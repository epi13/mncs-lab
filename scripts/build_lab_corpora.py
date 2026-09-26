#!/usr/bin/env python3
"""Build (or verify) the Lab kernel execution corpora.

For every kernel in KERNELS, emits ``corpora/lab-<name>-corpus.json``: a
fixed set of executable cases over the kernel's corpus entry points with
exact finite/integer/boolean identities. ``--verify`` rebuilds into a temp
dir and fails if any rebuilt corpus differs from the checked-in one
(source/corpus drift gate for CI).

Only value shapes the ``experiment run`` boundary is known to transport
are used: ``finite`` (enums), ``integer`` (u64/i64 scalars), ``boolean``.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CORPUS_DIR = REPO / "corpora"

OUTCOME = "mncs.lab.outcome"
VARIANTS = "mncs.lab.variants"
SESSION = "mncs.lab.session"


def finite(module: str, enum: str, variant: str, discriminant: int) -> dict:
    return {
        "finite": {
            "type_identity": f"mncs:0.2:finite-type:{module}::{enum}",
            "variant_identity": f"mncs:0.2:finite-variant:{module}::{enum}::{variant}",
            "discriminant": discriminant,
        }
    }


def integer(value: int, *, signed: bool = False) -> dict:
    return {"integer": {"value": value, "type": {"bits": 64, "signed": signed}}}


def boolean(value: bool) -> dict:
    return {"boolean": {"value": value}}


def case(cid: str, module: str, function: str, args: list, expected: list) -> dict:
    return {
        "id": cid,
        "request": {
            "schema_version": "0.1",
            "target": {"module": module, "function": function},
            "arguments": args,
            "step_budget": 1024,
        },
        "expected": expected,
    }


STANDING = ("SUPPORTED", "CONTRADICTED", "INCONCLUSIVE", "UNKNOWN")


def st(variant: str) -> dict:
    return finite(OUTCOME, "Standing", variant, STANDING.index(variant))


def outcome_cases() -> list:
    cases = [
        case("comb-ss", OUTCOME, "combine", [st("SUPPORTED"), st("SUPPORTED")], [st("SUPPORTED")]),
        case("comb-sc", OUTCOME, "combine", [st("SUPPORTED"), st("CONTRADICTED")], [st("CONTRADICTED")]),
        case("comb-cs", OUTCOME, "combine", [st("CONTRADICTED"), st("SUPPORTED")], [st("CONTRADICTED")]),
        case("comb-iu", OUTCOME, "combine", [st("INCONCLUSIVE"), st("UNKNOWN")], [st("INCONCLUSIVE")]),
        case("comb-uu", OUTCOME, "combine", [st("UNKNOWN"), st("UNKNOWN")], [st("UNKNOWN")]),
        case("comb-is", OUTCOME, "combine", [st("INCONCLUSIVE"), st("SUPPORTED")], [st("INCONCLUSIVE")]),
        case("cls-support", OUTCOME, "classify",
             [integer(3), integer(0), integer(0), integer(0)], [st("SUPPORTED")]),
        case("cls-vacuous", OUTCOME, "classify",
             [integer(0), integer(0), integer(0), integer(0)], [st("UNKNOWN")]),
        case("cls-contra", OUTCOME, "classify",
             [integer(1), integer(1), integer(1), integer(1)], [st("CONTRADICTED")]),
        case("cls-inconclusive", OUTCOME, "classify",
             [integer(2), integer(0), integer(2), integer(3)], [st("INCONCLUSIVE")]),
        case("cls-unknown", OUTCOME, "classify",
             [integer(2), integer(0), integer(0), integer(1)], [st("UNKNOWN")]),
        case("code-s", OUTCOME, "standing_code", [st("SUPPORTED")], [integer(0)]),
        case("code-c", OUTCOME, "standing_code", [st("CONTRADICTED")], [integer(1)]),
        case("code-i", OUTCOME, "standing_code", [st("INCONCLUSIVE")], [integer(2)]),
        case("code-u", OUTCOME, "standing_code", [st("UNKNOWN")], [integer(3)]),
        case("decided-s", OUTCOME, "is_decided", [st("SUPPORTED")], [boolean(True)]),
        case("decided-i", OUTCOME, "is_decided", [st("INCONCLUSIVE")], [boolean(False)]),
    ]
    return cases


def variant_cases() -> list:
    return [
        case("diff-same", VARIANTS, "diff4",
             [integer(7)] * 4 + [integer(7)] * 4, [integer(0)]),
        case("diff-one", VARIANTS, "diff4",
             [integer(1), integer(2), integer(3), integer(4),
              integer(1), integer(9), integer(3), integer(4)], [integer(1)]),
        case("diff-four", VARIANTS, "diff4",
             [integer(1), integer(2), integer(3), integer(4),
              integer(5), integer(6), integer(7), integer(8)], [integer(4)]),
        case("ctrl-ok", VARIANTS, "controlled4",
             [integer(1),
              integer(1), integer(2), integer(3), integer(4),
              integer(1), integer(9), integer(3), integer(4)], [boolean(True)]),
        case("ctrl-ok-zero", VARIANTS, "controlled4",
             [integer(0),
              integer(1), integer(2), integer(3), integer(4),
              integer(8), integer(2), integer(3), integer(4)], [boolean(True)]),
        case("ctrl-same", VARIANTS, "controlled4",
             [integer(1),
              integer(1), integer(2), integer(3), integer(4),
              integer(1), integer(2), integer(3), integer(4)], [boolean(False)]),
        case("ctrl-double", VARIANTS, "controlled4",
             [integer(1),
              integer(1), integer(2), integer(3), integer(4),
              integer(1), integer(9), integer(9), integer(4)], [boolean(False)]),
        case("ctrl-wrong-dim", VARIANTS, "controlled4",
             [integer(2),
              integer(1), integer(2), integer(3), integer(4),
              integer(8), integer(2), integer(3), integer(4)], [boolean(False)]),
    ]


SUBMISSION = ("INCOMPLETE", "INVALID", "VALID")
DISPOSITION = ("COMMIT", "INSPECT_ONLY", "REJECT")
SCOPE = ("HISTORY", "DEFINITIONS", "VALUES", "CODE", "ALL")
STATE = ("SOURCE", "SEMANTIC", "PROOF", "ARTIFACT", "RUNTIME", "JIT", "OBSERVABILITY")


def sub(variant: str) -> dict:
    return finite(SESSION, "Submission", variant, SUBMISSION.index(variant))


def disp(variant: str) -> dict:
    return finite(SESSION, "Disposition", variant, DISPOSITION.index(variant))


def scope(variant: str) -> dict:
    return finite(SESSION, "ResetScope", variant, SCOPE.index(variant))


def state(variant: str) -> dict:
    return finite(SESSION, "StateClass", variant, STATE.index(variant))


def session_cases() -> list:
    return [
        case("frag-incomplete", SESSION, "classify_fragment",
             [boolean(False), boolean(False)], [sub("INCOMPLETE")]),
        case("frag-incomplete-valid", SESSION, "classify_fragment",
             [boolean(False), boolean(True)], [sub("INCOMPLETE")]),
        case("frag-invalid", SESSION, "classify_fragment",
             [boolean(True), boolean(False)], [sub("INVALID")]),
        case("frag-valid", SESSION, "classify_fragment",
             [boolean(True), boolean(True)], [sub("VALID")]),
        case("disp-reject-incomplete", SESSION, "dispose",
             [sub("INCOMPLETE"), boolean(False)], [disp("REJECT")]),
        case("disp-reject-invalid", SESSION, "dispose",
             [sub("INVALID"), boolean(True)], [disp("REJECT")]),
        case("disp-inspect", SESSION, "dispose",
             [sub("VALID"), boolean(True)], [disp("INSPECT_ONLY")]),
        case("disp-commit", SESSION, "dispose",
             [sub("VALID"), boolean(False)], [disp("COMMIT")]),
        case("gen-ok", SESSION, "generation_ok",
             [integer(5), integer(6)], [boolean(True)]),
        case("gen-stay", SESSION, "generation_ok",
             [integer(5), integer(5)], [boolean(False)]),
        case("gen-skip", SESSION, "generation_ok",
             [integer(5), integer(7)], [boolean(False)]),
        case("reset-history-source", SESSION, "reset_clears",
             [scope("HISTORY"), state("SOURCE")], [boolean(True)]),
        case("reset-history-runtime", SESSION, "reset_clears",
             [scope("HISTORY"), state("RUNTIME")], [boolean(False)]),
        case("reset-definitions-proof", SESSION, "reset_clears",
             [scope("DEFINITIONS"), state("PROOF")], [boolean(True)]),
        case("reset-code-artifact", SESSION, "reset_clears",
             [scope("CODE"), state("ARTIFACT")], [boolean(False)]),
        case("reset-all-observability", SESSION, "reset_clears",
             [scope("ALL"), state("OBSERVABILITY")], [boolean(True)]),
        case("reset-values-jit", SESSION, "reset_clears",
             [scope("VALUES"), state("JIT")], [boolean(False)]),
    ]


KERNELS = (
    ("outcome", OUTCOME, outcome_cases),
    ("variant", VARIANTS, variant_cases),
    ("session", SESSION, session_cases),
)


def build(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    built = {}
    for name, module, fn in KERNELS:
        doc = {"schema_version": "0.1", "name": f"lab-{name}", "cases": fn()}
        (out_dir / f"lab-{name}-corpus.json").write_text(
            json.dumps(doc, indent=1) + "\n", encoding="utf-8"
        )
        built[name] = len(doc["cases"])
    return built


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        with tempfile.TemporaryDirectory(prefix="lab-corpora-") as tmp:
            build(Path(tmp))
            for name, _, _ in KERNELS:
                fresh = (Path(tmp) / f"lab-{name}-corpus.json").read_text()
                pinned = (CORPUS_DIR / f"lab-{name}-corpus.json").read_text()
                if fresh != pinned:
                    raise SystemExit(f"corpus drift: corpora/lab-{name}-corpus.json")
        print("corpora in sync")
    else:
        print(build(CORPUS_DIR))


if __name__ == "__main__":
    main()
