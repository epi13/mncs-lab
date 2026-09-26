"""Execute one Lab experiment definition end to end.

Pipeline (host boundary only; semantics stay in MNCS):

  definition
  -> subject admission (every variant observation must be green on its own
     corpus, otherwise the run aborts: a comparison subject that fails
     everywhere cannot produce agreement evidence)
  -> variant-integrity witness (controlled4 over each variant pair, executed
     in MNCS; failure forces INCONCLUSIVE, never a silent proceed)
  -> cross-variant agreement analysis (byte comparison of returned values)
  -> standing rule -> classify witness (the tally is classified by
     mncs.lab.outcome in MNCS; the run fails closed if MNCS disagrees)
  -> digest-pinned record (+ optional Store publication sidecar)
"""

from __future__ import annotations

import datetime
import json
import tempfile
from pathlib import Path

from .common import (
    REPO,
    LabError,
    canonical_bytes,
    digest_bytes,
    digest_file,
    digest_record,
    find_executor,
    git_dirty,
    git_head,
    library_path,
    run,
)

BACKENDS = {
    "mncs-portable-wasm-mvp": "wasm",
    "mncs-research-bytecode": "bytecode",
    "mncs-cranelift": "cranelift",
}

DEFINITION_SCHEMA = "mncs-lab.experiment-definition/1"
RECORD_SCHEMA = "mncs-lab.experiment-record/1"


def load_definition(path: Path) -> dict:
    definition = json.loads(path.read_text(encoding="utf-8"))
    if definition.get("schema_version") != DEFINITION_SCHEMA:
        raise LabError(f"{path}: unsupported schema {definition.get('schema_version')}")
    for key in ("id", "question", "hypothesis", "subjects", "variants",
                "intended_dimension", "controls", "corpora", "evaluation_rule"):
        if key not in definition:
            raise LabError(f"{path}: definition missing {key!r}")
    return definition


def check_subjects(definition: dict) -> dict:
    """Reproducibility gate: pinned revisions must match clean checkouts."""
    state = {}
    for subject in definition["subjects"]:
        repo = REPO.parent / subject["repo"] if subject["repo"] != "mncs-lab" else REPO
        head = git_head(repo)
        dirty = git_dirty(repo)
        source = REPO / subject["source"]
        if not source.is_file():
            raise LabError(f"missing subject source: {source}")
        actual_digest = digest_file(source)
        state[subject["module"]] = {
            "head": head, "dirty": dirty, "source_digest": actual_digest,
        }
        if head != subject["revision"]:
            raise LabError(
                f"{subject['module']}: checkout {head} != pinned {subject['revision']} "
                "(a historical result must not silently become evidence for another revision)"
            )
        if dirty:
            raise LabError(f"{subject['module']}: tracked tree is dirty; commit first")
        if actual_digest != subject["source_digest"]:
            raise LabError(f"{subject['module']}: source digest drift vs definition")
    return state


def run_corpus(executor: str, source: Path, backend: str, corpus: Path,
               out_dir: Path) -> dict:
    completed = run([executor, "experiment", "run", str(source),
                     "--backend", backend, "--corpus", str(corpus),
                     "--output-dir", str(out_dir)])
    result_file = out_dir / "result.json"
    if completed.returncode != 0 or not result_file.is_file():
        raise LabError(
            f"experiment run failed for {source.name}/{backend}:\n"
            f"{completed.stderr[-2000:]}"
        )
    return json.loads(result_file.read_text(encoding="utf-8"))


def observe_case(case: dict) -> dict:
    returned = case.get("returned", [])
    return {
        "met": bool(case.get("expectation_met")),
        "executed": case.get("status") == "returned",
        "returned_digest": digest_bytes(canonical_bytes(returned)),
    }


def witness_corpus(module: str, function: str, args: list, expected: list) -> dict:
    return {
        "schema_version": "0.1",
        "name": "lab-witness",
        "cases": [{
            "id": "witness",
            "request": {
                "schema_version": "0.1",
                "target": {"module": module, "function": function},
                "arguments": args,
                "step_budget": 1024,
            },
            "expected": expected,
        }],
    }


def int_arg(value: int) -> dict:
    return {"integer": {"value": value, "type": {"bits": 64, "signed": False}}}


def finite_arg(module: str, enum: str, variant: str, discriminant: int) -> dict:
    return {"finite": {
        "type_identity": f"mncs:0.2:finite-type:{module}::{enum}",
        "variant_identity": f"mncs:0.2:finite-variant:{module}::{enum}::{variant}",
        "discriminant": discriminant}}


def run_witness(executor: str, source: Path, backend: str, corpus_doc: dict,
                workdir: Path) -> dict:
    corpus_file = workdir / "witness-corpus.json"
    corpus_file.write_text(json.dumps(corpus_doc, indent=1), encoding="utf-8")
    out = workdir / "witness-out"
    out.mkdir(exist_ok=True)
    result = run_corpus(executor, source, backend, corpus_file, out)
    case = result["cases"][0]
    return {
        "met": bool(case.get("expectation_met")),
        "status": result.get("status"),
        "corpus_digest": digest_bytes(canonical_bytes(corpus_doc)),
        "result_digest": digest_bytes(canonical_bytes(result.get("cases", []))),
    }


def execute(definition_path: Path, *, records_dir: Path,
            evidence_dir: Path, persist: bool = False,
            store_path: Path | None = None) -> Path:
    definition = load_definition(definition_path)
    exp_id = definition["id"]
    executor = find_executor()
    version = run([executor, "--version"], timeout=60)
    check_subjects(definition)
    intended = int(definition["intended_dimension"])
    variants = definition["variants"]

    corpora = {k: REPO / v for k, v in definition["corpora"].items()}
    for name, path in corpora.items():
        if not path.is_file():
            raise LabError(f"missing corpus for {name}: {path}")
    sources = {s["module"]: REPO / s["source"] for s in definition["subjects"]}

    with tempfile.TemporaryDirectory(prefix="lab-exp-") as tmp:
        workdir = Path(tmp)
        observations = []
        per_kernel_cases: dict[str, dict[str, dict[str, dict]]] = {}
        for variant in variants:
            backend = variant["backend"]
            for module, corpus in corpora.items():
                result = run_corpus(executor, sources[module], backend, corpus,
                                    workdir / f"{variant['id']}-{module}")
                cases = {c.get("case_id"): c for c in result.get("cases", [])}
                detail = {cid: observe_case(c) for cid, c in cases.items()}
                unmet = sorted(cid for cid, o in detail.items() if not o["met"])
                unexecuted = sorted(cid for cid, o in detail.items() if not o["executed"])
                observations.append({
                    "variant": variant["id"],
                    "backend": backend,
                    "kernel": module,
                    "status": result.get("status"),
                    "cases_total": len(detail),
                    "cases_met": sum(1 for o in detail.values() if o["met"]),
                    "unmet": unmet,
                    "unexecuted": unexecuted,
                    "result_digest": digest_bytes(canonical_bytes(result.get("cases", []))),
                })
                per_kernel_cases.setdefault(module, {})[variant["id"]] = detail
                if result.get("status") != "PASS" or unmet:
                    raise LabError(
                        f"subject admission failed: {module}/{variant['id']} "
                        f"status={result.get('status')} unmet={unmet} "
                        f"unresolved={result.get('unresolved_reasons')}"
                    )

        # Variant integrity: every non-baseline variant must form a
        # controlled pair with the baseline along the intended dimension.
        baseline = variants[0]
        integrity_witnesses = []
        integrity_ok = True
        variants_source = sources["mncs.lab.variants"]
        for variant in variants[1:]:
            args = [int_arg(intended)]
            args += [int_arg(c) for c in baseline["codes"]]
            args += [int_arg(c) for c in variant["codes"]]
            corpus_doc = witness_corpus(
                "mncs.lab.variants", "controlled4", args, [{"boolean": {"value": True}}])
            witness = run_witness(executor, variants_source, baseline["backend"],
                                  corpus_doc, workdir / f"integrity-{variant['id']}")
            witness["pair"] = [baseline["id"], variant["id"]]
            integrity_witnesses.append(witness)
            integrity_ok = integrity_ok and witness["met"]
        if not integrity_ok:
            raise LabError(f"variant integrity witness failed: {integrity_witnesses}")

        # Agreement: same case, same returned bytes, across every variant.
        agreements: list[str] = []
        disagreements: list[str] = []
        unknowns: list[str] = []
        for module, by_variant in per_kernel_cases.items():
            case_ids = set()
            for detail in by_variant.values():
                case_ids.update(detail)
            for cid in sorted(case_ids):
                per_variant = {v: by_variant[v].get(cid) for v in
                               [x["id"] for x in variants]}
                if any(o is None or not o["executed"] for o in per_variant.values()):
                    unknowns.append(f"{module}::{cid}")
                elif len({o["returned_digest"] for o in per_variant.values()}) == 1:
                    agreements.append(f"{module}::{cid}")
                else:
                    disagreements.append(f"{module}::{cid}")

        tally = {
            "supported": len(agreements),
            "contradicted": len(disagreements),
            "inconclusive": 0,
            "unknown": len(unknowns),
        }
        if disagreements:
            standing = "CONTRADICTED"
        elif unknowns:
            standing = "UNKNOWN"
        else:
            standing = "SUPPORTED"

        # Standing witness: mncs.lab.outcome classifies the observed tally;
        # the recorded conclusion must match MNCS, else fail closed.
        outcome_source = sources["mncs.lab.outcome"]
        standing_index = {"SUPPORTED": 0, "CONTRADICTED": 1,
                          "INCONCLUSIVE": 2, "UNKNOWN": 3}[standing]
        corpus_doc = witness_corpus(
            "mncs.lab.outcome", "classify",
            [int_arg(tally["supported"]), int_arg(tally["contradicted"]),
             int_arg(tally["inconclusive"]), int_arg(tally["unknown"])],
            [finite_arg("mncs.lab.outcome", "Standing", standing, standing_index)])
        standing_witness = run_witness(executor, outcome_source,
                                       baseline["backend"], corpus_doc,
                                       workdir / "standing")
        if not standing_witness["met"]:
            raise LabError(
                f"standing witness rejected: tally {tally} did not classify "
                f"as {standing} in MNCS")

        record = {
            "schema_version": RECORD_SCHEMA,
            "id": exp_id,
            "definition_digest": digest_bytes(canonical_bytes(definition)),
            "executed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "question": definition["question"],
            "hypothesis": definition["hypothesis"],
            "toolchain": {
                "executor": executor,
                "executor_version": (version.stdout.strip() or version.stderr.strip()),
                "language_revision": git_head(REPO.parent / "mncs-language"),
                "lab_revision": git_head(REPO),
                "library_path": library_path(),
            },
            "subjects": definition["subjects"],
            "variants": variants,
            "controls": definition["controls"],
            "observations": observations,
            "variant_integrity": {"ok": True, "witnesses": integrity_witnesses},
            "agreement": {
                "compared": len(agreements) + len(disagreements) + len(unknowns),
                "agreements": agreements,
                "disagreements": disagreements,
                "unknowns": unknowns,
            },
            "tally": tally,
            "standing": {
                "value": standing,
                "code": standing_index,
                "witness": standing_witness,
            },
            "conclusion": definition["evaluation_rule"],
            "pressures": definition.get("pressures", []),
            "evidence": [f"evidence/{exp_id}/observations.json"],
        }
        record["record_digest"] = digest_record(record)

        records_dir.mkdir(parents=True, exist_ok=True)
        record_path = records_dir / f"{exp_id}.json"
        record_path.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")

        compact = {
            "record": exp_id,
            "record_digest": record["record_digest"],
            "observations": [
                {k: o[k] for k in ("variant", "kernel", "status", "cases_total",
                                   "cases_met", "unmet", "result_digest")}
                for o in observations
            ],
            "agreement": record["agreement"],
        }
        exp_evidence = evidence_dir / exp_id
        exp_evidence.mkdir(parents=True, exist_ok=True)
        (exp_evidence / "observations.json").write_text(
            json.dumps(compact, indent=1) + "\n", encoding="utf-8")

    if persist:
        from .store_link import publish_record
        publish_record(record_path, store_path=store_path)

    return record_path
