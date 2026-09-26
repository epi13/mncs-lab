"""Host-side tests for the Lab record machinery.

These cover what Python owns: record digest stability, the standing rule
the checker enforces, corpus determinism, and query filters. Experiment
semantics themselves are proven in MNCS (tests/lab/*_tests.mncs); nothing
here reimplements them. Nothing here needs an executor.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mncs_lab.check import standing_for
from mncs_lab.common import canonical_bytes, digest_bytes, digest_record
from mncs_lab.runner import analyze_agreement, standing_for_tally


def test_standing_rule_matches_mncs_lattice() -> None:
    assert standing_for({"contradicted": 1}, True) == "CONTRADICTED"
    assert standing_for({"contradicted": 0, "unknown": 2}, True) == "UNKNOWN"
    assert standing_for({"contradicted": 0, "unknown": 0}, True) == "SUPPORTED"
    assert standing_for({"contradicted": 5, "unknown": 5}, True) == "CONTRADICTED"
    assert standing_for({"contradicted": 0, "unknown": 0}, False) == "INCONCLUSIVE"


def test_record_digest_ignores_itself() -> None:
    record = {"schema_version": "x", "id": "LAB-EXP-000", "tally": {"a": 1}}
    first = digest_record(record)
    record["record_digest"] = first
    assert digest_record(record) == first


def test_canonical_bytes_are_stable() -> None:
    left = {"b": [1, 2], "a": {"y": True, "x": None}}
    right = {"a": {"x": None, "y": True}, "b": [1, 2]}
    assert digest_bytes(canonical_bytes(left)) == digest_bytes(canonical_bytes(right))


def test_corpus_generator_is_deterministic() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import build_lab_corpora

    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        build_lab_corpora.build(Path(first))
        build_lab_corpora.build(Path(second))
        for name, _, _ in build_lab_corpora.KERNELS:
            left = (Path(first) / f"lab-{name}-corpus.json").read_text()
            right = (Path(second) / f"lab-{name}-corpus.json").read_text()
            assert left == right
            pinned = Path(__file__).resolve().parents[1] / "corpora" / f"lab-{name}-corpus.json"
            assert left == pinned.read_text(), f"corpus drift: {name}"


def _obs(met: bool = True, executed: bool = True, digest: str = "d") -> dict:
    return {"met": met, "executed": executed, "returned_digest": digest}


def test_agreement_supports_identical_returns() -> None:
    per_kernel = {"m": {"a": {"c1": _obs(digest="d1")},
                        "b": {"c1": _obs(digest="d1")}}}
    analysis = analyze_agreement(per_kernel, ["a", "b"])
    assert analysis["agreements"] == ["m::c1"]
    assert analysis["tally"]["supported"] == 1
    assert standing_for_tally(analysis["tally"]) == "SUPPORTED"


def test_disagreement_contradicts_and_is_preserved() -> None:
    # The negative-result path: a differing observation contradicts the
    # hypothesis and must survive as CONTRADICTED, never collapse.
    per_kernel = {"m": {"a": {"c1": _obs(digest="d1")},
                        "b": {"c1": _obs(digest="d2")}}}
    analysis = analyze_agreement(per_kernel, ["a", "b"])
    assert analysis["disagreements"] == ["m::c1"]
    assert analysis["tally"]["contradicted"] == 1
    assert standing_for_tally(analysis["tally"]) == "CONTRADICTED"


def test_unexecuted_case_is_unknown_not_support() -> None:
    per_kernel = {"m": {"a": {"c1": _obs()},
                        "b": {"c1": _obs(executed=False)}}}
    analysis = analyze_agreement(per_kernel, ["a", "b"])
    assert analysis["unknowns"] == ["m::c1"]
    assert standing_for_tally(analysis["tally"]) == "UNKNOWN"


def test_contradiction_dominates_unknown() -> None:
    assert standing_for_tally({"contradicted": 1, "unknown": 3}) == "CONTRADICTED"


def test_query_filters() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from mncs_lab import query

    supported = {"id": "LAB-EXP-901", "question": "q",
                 "standing": {"value": "SUPPORTED"},
                 "tally": {}, "subjects": [], "pressures": []}
    contradicted = {"id": "LAB-EXP-902", "question": "q",
                    "standing": {"value": "CONTRADICTED"},
                    "tally": {}, "subjects": [],
                    "pressures": [],
                    "agreement": {"disagreements": ["m::c"]}}
    assert query.summarize(supported)["standing"] == "SUPPORTED"
    assert query.summarize(contradicted)["id"] == "LAB-EXP-902"


def test_sidecars_are_not_records() -> None:
    from mncs_lab.query import is_record_path

    assert is_record_path(Path("experiments/records/LAB-EXP-001.json"))
    assert not is_record_path(Path("experiments/records/LAB-EXP-001.store.json"))


def test_subject_freshness_levels() -> None:
    from mncs_lab.common import REPO, digest_file, git_head, subject_freshness

    head = git_head(REPO)
    source = "mncs/lab/outcome.mncs"
    current = {"subjects": [{"repo": "mncs-lab", "source": source,
                             "revision": head, "source_digest": digest_file(REPO / source)}]}
    assert subject_freshness(current) == "current"
    moved = {"subjects": [{"repo": "mncs-lab", "source": source,
                           "revision": "0" * 40, "source_digest": digest_file(REPO / source)}]}
    assert subject_freshness(moved) == "current-content"
    changed = {"subjects": [{"repo": "mncs-lab", "source": source,
                             "revision": head, "source_digest": "sha256:dead"}]}
    assert subject_freshness(changed) == "stale"
