"""Lab enforcement boundary: integrity gates for CI and developers.

Checks (fail closed, nonzero exit on integrity breakage):

1. corpora in sync with the generator (drift gate);
2. all three ``mncs test`` suites PASS on the canonical toolchain;
3. every record validates: schema keys, content digest, standing matches
   the tally rule, tally matches the recorded agreement lists, witness
   flags are met, referenced files exist with matching digests;
4. Store round-trip for every record carrying a publication sidecar.

Freshness (record revision vs current checkout) is REPORTED, never a
failure: a stale record is historical evidence, not broken evidence.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mncs_lab.common import (
    REPO,
    LabError,
    digest_record,
    find_executor,
    git_head,
    library_path,
)
from mncs_lab.store_link import verify_record

SUITES = (
    "tests/lab/outcome_tests.mncs",
    "tests/lab/variant_tests.mncs",
    "tests/lab/session_tests.mncs",
)

STANDING_RULE_ORDER = ("CONTRADICTED", "UNKNOWN", "SUPPORTED")


def check_corpora() -> None:
    sys.path.insert(0, str(REPO / "scripts"))
    import build_lab_corpora
    with tempfile.TemporaryDirectory(prefix="lab-corpora-check-") as tmp:
        out = Path(tmp)
        build_lab_corpora.build(out)
        for name, _, _ in build_lab_corpora.KERNELS:
            fresh = (out / f"lab-{name}-corpus.json").read_text()
            pinned = (REPO / "corpora" / f"lab-{name}-corpus.json").read_text()
            if fresh != pinned:
                raise LabError(f"corpus drift: corpora/lab-{name}-corpus.json "
                               "(regenerate with scripts/build_lab_corpora.py)")


def check_suites(executor: str) -> dict:
    import os
    env = dict(os.environ, MNCS_LIBRARY_PATH=library_path())
    results = {}
    for suite in SUITES:
        completed = subprocess_run(
            [executor, "test", str(REPO / suite), "--format", "json"], env)
        try:
            doc = json.loads(completed.stdout)
        except json.JSONDecodeError:
            raise LabError(f"{suite}: unparseable test output:\n{completed.stderr[-1500:]}")
        summary = doc.get("summary", {})
        ok = doc.get("classification") == "passed" and summary.get("failed", 1) == 0
        results[suite] = {"ok": ok, "summary": summary}
        if not ok:
            raise LabError(f"{suite}: suite not green: {summary}")
    return results


def subprocess_run(args: list, env: dict):
    return subprocess.run(args, capture_output=True, text=True, timeout=600,
                             env=env, check=False)


def standing_for(tally: dict, integrity_ok: bool) -> str:
    if not integrity_ok:
        return "INCONCLUSIVE"
    if tally.get("contradicted", 0) > 0:
        return "CONTRADICTED"
    if tally.get("unknown", 0) > 0:
        return "UNKNOWN"
    return "SUPPORTED"


def check_record(path: Path) -> dict:
    record = json.loads(path.read_text(encoding="utf-8"))
    if digest_record(record) != record.get("record_digest"):
        raise LabError(f"{path.name}: record digest mismatch")
    for key in ("id", "definition_digest", "question", "hypothesis", "toolchain",
                "subjects", "variants", "observations", "variant_integrity",
                "agreement", "tally", "standing", "evidence"):
        if key not in record:
            raise LabError(f"{path.name}: record missing {key!r}")

    agreement = record["agreement"]
    tally = record["tally"]
    if tally["supported"] != len(agreement["agreements"]):
        raise LabError(f"{path.name}: tally.supported != agreements")
    if tally["contradicted"] != len(agreement["disagreements"]):
        raise LabError(f"{path.name}: tally.contradicted != disagreements")
    if tally["unknown"] != len(agreement["unknowns"]):
        raise LabError(f"{path.name}: tally.unknown != unknowns")
    if tally.get("inconclusive", 0) != 0:
        raise LabError(f"{path.name}: nonzero inconclusive tally without lineage")

    integrity_ok = bool(record["variant_integrity"].get("ok"))
    for witness in record["variant_integrity"].get("witnesses", []):
        if not witness.get("met"):
            raise LabError(f"{path.name}: variant integrity witness unmet")
    expected = standing_for(tally, integrity_ok)
    if record["standing"]["value"] != expected:
        raise LabError(f"{path.name}: standing {record['standing']['value']} "
                       f"!= rule {expected}")
    if not record["standing"].get("witness", {}).get("met"):
        raise LabError(f"{path.name}: standing witness unmet")

    for subject in record["subjects"]:
        source = REPO / subject["source"]
        if not source.is_file():
            raise LabError(f"{path.name}: subject source missing: {source}")
    for rel in record.get("evidence", []):
        if not (REPO / rel).is_file():
            raise LabError(f"{path.name}: evidence missing: {rel}")
    for press in record.get("pressures", []):
        if not (REPO / press).is_file():
            raise LabError(f"{path.name}: pressure link missing: {press}")

    try:
        current = git_head(REPO)
    except (OSError, ValueError, subprocess.CalledProcessError):
        current = None
    fresh = all(s.get("revision") == current for s in record["subjects"]
                if s.get("repo") == "mncs-lab") if current else None
    return {"id": record["id"], "standing": record["standing"]["value"],
            "fresh": fresh}


def main() -> int:
    executor = find_executor()
    print(f"executor: {executor}")
    check_corpora()
    print("corpora in sync")
    suites = check_suites(executor)
    for suite, result in suites.items():
        print(f"{suite}: {result['summary']}")
    records_dir = REPO / "experiments" / "records"
    records = sorted(records_dir.glob("LAB-EXP-*.json"))
    if not records:
        print("no experiment records yet")
    for path in records:
        info = check_record(path)
        print(f"{path.name}: standing={info['standing']} fresh={info['fresh']}")
        sidecar = path.with_suffix(".store.json")
        if sidecar.is_file():
            verify_record(path)
            print(f"{path.name}: store round-trip ok")
    print("lab boundary green")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LabError as exc:
        print(f"lab_check FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
