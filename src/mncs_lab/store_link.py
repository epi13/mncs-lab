"""Durable experiment records through the canonical embedded Store.

The checked-in JSON record under ``experiments/records/`` stays the
reviewable source. Publication stores the exact same bytes as a
content-addressed Store object (schema ``mncs-lab.experiment-record/1``,
identity = experiment id) and writes a sidecar with the linkage. The
record itself is never mutated by publication, so its digest keeps
covering exactly what was executed.

Same identity + different bytes is an IDENTITY_CONFLICT in Store, which
is the desired behavior: a record id must not silently become evidence
for different bytes. Same bytes republished is DUPLICATE and verifies.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from .common import REPO, LabError, digest_record

DOMAIN_SCHEMA = b"mncs-lab.experiment-record/1"


def default_store_path() -> Path:
    configured = os.environ.get("MNCS_LAB_STORE")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".local" / "share" / "mncs-lab" / "store"


def _store_module():
    root = Path(os.environ.get("MNCS_STORE_PYTHON",
                               str(REPO.parent / "mncs-store" / "python")))
    if not root.is_dir():
        raise LabError("sibling mncs-store checkout missing; cannot persist")
    sys.path.insert(0, str(root))
    try:
        from mncs_store.embedded import EmbeddedStore
    finally:
        sys.path.pop(0)
    return EmbeddedStore


def publish_record(record_path: Path, *, store_path: Path | None = None) -> Path:
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if digest_record(record) != record.get("record_digest"):
        raise LabError(f"{record_path}: digest mismatch; refusing to persist")
    payload = json.dumps(
        {k: v for k, v in record.items()},
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    descriptor = json.dumps({
        "schema": "mncs-lab.experiment-record/1",
        "record": record["id"],
        "record_digest": record["record_digest"],
    }, sort_keys=True).encode("utf-8")

    EmbeddedStore = _store_module()
    store = EmbeddedStore(store_path or default_store_path())
    try:
        current = store.current_generation
        result = store.put_bound_object(
            domain_schema=DOMAIN_SCHEMA,
            domain_identity=record["id"].encode("utf-8"),
            descriptor=descriptor,
            payload=payload,
            expected_generation=current,
        )
        if not result.committed:
            raise LabError(f"store publication not committed: {result.code}")
        stored = store.get_bound_object(DOMAIN_SCHEMA, record["id"].encode("utf-8"))
        if stored.payload != payload:
            raise LabError("store round-trip payload mismatch")
        sidecar = {
            "record": record["id"],
            "record_digest": record["record_digest"],
            "store": str(store.path),
            "generation": result.generation,
            "logical_id": result.logical_id.hex(),
            "content_id": result.content_id.hex(),
            "binding_id": result.binding_id.hex(),
            "commit_code": str(result.code),
        }
        sidecar_path = record_path.with_suffix(".store.json")
        sidecar_path.write_text(json.dumps(sidecar, indent=1) + "\n", encoding="utf-8")
        return sidecar_path
    finally:
        store.close()


def verify_record(record_path: Path, *, store_path: Path | None = None) -> dict:
    """Verify a publication sidecar against Store. Returns the sidecar."""
    sidecar_path = record_path.with_suffix(".store.json")
    if not sidecar_path.is_file():
        raise LabError(f"no store sidecar for {record_path.name}")
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if sidecar.get("record_digest") != record.get("record_digest"):
        raise LabError(f"{record_path.name}: sidecar digest != record digest")
    EmbeddedStore = _store_module()
    store = EmbeddedStore(store_path or default_store_path())
    try:
        stored = store.get_bound_object(DOMAIN_SCHEMA, record["id"].encode("utf-8"))
        payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if stored.payload != payload:
            raise LabError(f"{record_path.name}: store payload drift")
        if stored.content_id.hex() != sidecar.get("content_id"):
            raise LabError(f"{record_path.name}: store content id drift")
    finally:
        store.close()
    return sidecar
