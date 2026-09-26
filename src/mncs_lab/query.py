"""Bounded typed queries over Lab experiment records.

Future agents should not grep markdown or terminal logs to answer: what
experiments exist, what they evaluated, whether evidence is current, which
negative results block a path, or which experiment produced a pressure.
Every query here reads only ``experiments/records/LAB-EXP-*.json``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mncs_lab.common import REPO, subject_freshness

RECORDS = REPO / "experiments" / "records"


def is_record_path(path: Path) -> bool:
    """Publication sidecars live beside records but are not records."""
    return path.suffix == ".json" and not path.name.endswith(".store.json")


def all_records() -> list:
    records = []
    for path in sorted(RECORDS.glob("LAB-EXP-*.json")):
        if not is_record_path(path):
            continue
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def freshness(record: dict) -> str | None:
    return subject_freshness(record)


def summarize(record: dict) -> dict:
    return {
        "id": record["id"],
        "question": record.get("question"),
        "standing": record.get("standing", {}).get("value"),
        "tally": record.get("tally"),
        "freshness": freshness(record),
        "pressures": record.get("pressures", []),
    }


def cmd_list() -> None:
    for record in all_records():
        info = summarize(record)
        print(f"{info['id']} [{info['standing']}/{info['freshness']}] {info['question']}")


def cmd_show(exp_id: str) -> None:
    for record in all_records():
        if record["id"] == exp_id:
            print(json.dumps(record, indent=1))
            return
    raise SystemExit(f"unknown experiment: {exp_id}")


def cmd_by_subject(fragment: str) -> None:
    for record in all_records():
        subjects = [s.get("module", "") for s in record.get("subjects", [])]
        if any(fragment in s for s in subjects):
            info = summarize(record)
            print(f"{info['id']} [{info['standing']}/{info['freshness']}] {info['question']}")


def cmd_negatives() -> None:
    for record in all_records():
        if record.get("standing", {}).get("value") == "CONTRADICTED":
            info = summarize(record)
            print(f"{info['id']} [{info['freshness']}] {info['question']}")
            for case in record.get("agreement", {}).get("disagreements", []):
                print(f"  contradicted: {case}")


def cmd_inconclusive() -> None:
    for record in all_records():
        if record.get("standing", {}).get("value") in ("INCONCLUSIVE", "UNKNOWN"):
            info = summarize(record)
            print(f"{info['id']} [{info['standing']}/{info['freshness']}] {info['question']}")


def cmd_stale() -> None:
    for record in all_records():
        if freshness(record) == "stale":
            info = summarize(record)
            print(f"{info['id']} [{info['standing']}] {info['question']}")


def cmd_pressures() -> None:
    for record in all_records():
        for press in record.get("pressures", []):
            print(f"{record['id']}: {press}")


def main(argv: list) -> int:
    if not argv or argv[0] in ("list",):
        cmd_list()
    elif argv[0] == "show" and len(argv) == 2:
        cmd_show(argv[1])
    elif argv[0] == "by-subject" and len(argv) == 2:
        cmd_by_subject(argv[1])
    elif argv[0] == "negatives":
        cmd_negatives()
    elif argv[0] == "inconclusive":
        cmd_inconclusive()
    elif argv[0] == "stale":
        cmd_stale()
    elif argv[0] == "pressures":
        cmd_pressures()
    else:
        print("usage: lab_query.py list|show ID|by-subject FRAG|negatives|"
              "inconclusive|stale|pressures", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
