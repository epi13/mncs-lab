#!/usr/bin/env python3
"""Execute one Lab experiment definition (see src/mncs_lab/runner.py)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mncs_lab.common import REPO
from mncs_lab.runner import execute


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("definition", type=Path)
    parser.add_argument("--persist", action="store_true",
                        help="publish the record through the embedded Store")
    args = parser.parse_args()
    record = execute(
        args.definition,
        records_dir=REPO / "experiments" / "records",
        evidence_dir=REPO / "evidence",
        persist=args.persist,
    )
    print(f"record: {record}")


if __name__ == "__main__":
    main()
