"""Shared host-boundary helpers for mncs-lab.

Host code in this package owns only legitimate process/filesystem
concerns: locating the executor, invoking it, hashing bytes, reading git
state, and moving JSON records. All experiment semantics (standing
combination, variant integrity, session policy) live in MNCS under
``mncs/lab/`` and are proven by ``mncs test`` suites. Nothing here
reimplements them.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

LANGUAGE_REVISION_FILE = "docs/TOOLCHAIN.md"  # records the pinned revision, not the mechanism

STANDING_CODES = {"SUPPORTED": 0, "CONTRADICTED": 1, "INCONCLUSIVE": 2, "UNKNOWN": 3}
CODE_STANDINGS = {v: k for k, v in STANDING_CODES.items()}


class LabError(RuntimeError):
    pass


def canonical_bytes(record: dict) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def digest_record(record: dict) -> str:
    """Content digest of a record excluding its own ``record_digest`` field."""
    clone = {k: v for k, v in record.items() if k != "record_digest"}
    return digest_bytes(canonical_bytes(clone))


def find_executor() -> str:
    """Resolve the mncs compiler/executor binary (host boundary).

    Order: MNCS_EXECUTOR env, mncs-executor on PATH, sibling
    mncs-language checkout builds (release preferred). Fail closed.
    """
    override = os.environ.get("MNCS_EXECUTOR")
    if override:
        return override
    found = shutil.which("mncs-executor")
    if found:
        return found
    for profile in ("release", "debug"):
        sibling = REPO.parent / "mncs-language" / "target" / profile / "mncs"
        if sibling.is_file():
            return str(sibling)
    raise LabError(
        "no MNCS executor found: set MNCS_EXECUTOR, put mncs-executor on PATH "
        "(python3 scripts/fetch_mncs_executor.py), or check out mncs-language "
        "next to mncs-lab and build it"
    )


def library_path() -> str:
    """MNCS_LIBRARY_PATH roots for Lab suites: repo root first, then the
    native Test framework and the language library from the sibling
    checkouts. Fail closed when a sibling is missing."""
    roots = [
        REPO,
        REPO.parent / "mncs-test" / "native",
        REPO.parent / "mncs-language" / "library",
    ]
    missing = [str(r) for r in roots if not r.is_dir()]
    if missing:
        raise LabError(f"missing MNCS library roots: {missing}")
    return os.pathsep.join(str(r) for r in roots)


def git_head(repo: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return completed.stdout.strip()


def git_dirty(repo: Path) -> bool:
    completed = subprocess.run(
        ["git", "-C", str(repo), "status", "--short"],
        capture_output=True, text=True, check=True,
    )
    tracked = [line for line in completed.stdout.splitlines()
               if not line.startswith("??")]
    return bool(tracked)


def run(args: list, *, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                             check=False)
