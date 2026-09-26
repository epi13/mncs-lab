#!/usr/bin/env python3
"""Lab enforcement boundary (see src/mncs_lab/check.py)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mncs_lab.check import main
from mncs_lab.common import LabError

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (LabError, OSError, ValueError) as exc:
        print(f"lab_check FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
