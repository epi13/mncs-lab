# Lab Experiment Model

## What Lab is

`mncs-lab` is the controlled-investigation layer for MNCS itself. It owns
**experiments**: typed, reproducible investigations with a hypothesis, exact
subjects at exact revisions, controlled variants, structured observations,
and a conclusion that preserves the distinction between what was
hypothesized, what was executed, what was observed, and what was concluded.

An experiment asks something. A test checks something. Lab never confuses
the two: experiments *invoke* tests (via `mncs-test`) and *compare*
observations, but the hypothesis/observation/conclusion record is Lab's own.

## What Lab owns

- experiment definitions (`experiments/definitions/LAB-EXP-*.json`):
  question, hypothesis with predicted standing, subjects pinned to exact
  revisions and source digests, variant dimension codes, controls,
  evaluation rule;
- comparison semantics (`mncs/lab/variants.mncs`): variant integrity —
  exactly the intended dimension differs between variants;
- outcome semantics (`mncs/lab/outcome.mncs`): the hypothesis-standing
  algebra (SUPPORTED / CONTRADICTED / INCONCLUSIVE / UNKNOWN) with
  combination that can only weaken a claim;
- session interaction policy (`mncs/lab/session.mncs`): fragment
  lifecycle, generation discipline, reset matrix — the policy a future
  compiler session API must satisfy (see LAB-PRESS-001);
- execution of definitions (`scripts/lab_run.py` → `src/mncs_lab/`):
  subject admission, integrity/standing witnesses executed in MNCS,
  digest-pinned records;
- pressure generation with reproducers (`pressure/`).

## What Lab does not own

| Concern | Owner | Lab relationship |
|---|---|---|
| planning, questions, evidence obligations | RAVEL | a RAVEL question may motivate an experiment; the record links back |
| execution orchestration, admission, resources | Forge | Lab runs definitions through canonical toolchain commands; a Provider-Protocol speaker is roadmap, not a second orchestrator |
| assertion and suite semantics | `mncs-test` | Lab suites are `test` declarations using `mncs.test.*`; Lab proves no private assertion machinery |
| diagnosis of failures | Debug | failed runs keep structured evidence (definition, variant, inputs, expected/actual, execution identity) for Debug |
| integration environments | `mncs-harness` | Lab consumes environment capability; it does not manage lifecycles |
| bounded execution substrate | Fabric / runtime | `experiment run` and `mncs test` are the execution paths |
| persistence authority | Store / Commons | records are content-addressed Store objects; pressures file to the Commons exchange |
| machine telemetry | System Monitor | Lab references resource observations; it monitors nothing |
| provenance graph | Lineage | records carry exact revision/source digests Lineage can bind |

## The canonical pipeline

```text
hypothesis/question
  -> experiment definition (typed, revision-pinned)
  -> subject admission (every variant green on its own corpus, else abort)
  -> execution (canonical toolchain: experiment run / mncs test)
  -> observations (per-variant, per-case: met, executed, returned digest)
  -> variant-integrity witness (controlled4 in MNCS; failure -> INCONCLUSIVE)
  -> agreement analysis (byte-compared returned values)
  -> standing rule -> classify witness (mncs.lab.outcome in MNCS)
  -> digest-pinned record (+ optional Store publication sidecar)
  -> pressure linkage where a gap was exposed
```

Two MNCS executions guard every record: the integrity witness and the
standing witness. If MNCS disagrees with the recorded conclusion, the run
fails closed instead of writing the record.

## Subjects must be green first

A comparison subject that fails on its own corpus cannot produce agreement
evidence: uniform failure across variants would masquerade as agreement.
The runner therefore aborts when any variant observation is not PASS with
zero unmet cases. Kernel correctness is Test's job (the `mncs test`
suites); the experiment measures cross-variant agreement only.

## Standing semantics

- SUPPORTED — every compared case agrees across variants, nothing unknown.
- CONTRADICTED — at least one case disagrees (a negative result: preserved,
  queryable, and linked so the path is not retried blindly).
- INCONCLUSIVE — the comparison could not answer (e.g. variant integrity
  failed). Never a FAIL; never support.
- UNKNOWN — execution or evidence was incomplete. Never support, never
  failure.

Combination order (in `mncs.lab.outcome`): CONTRADICTED dominates
INCONCLUSIVE dominates UNKNOWN dominates SUPPORTED. Zero observations is
UNKNOWN, never vacuous support.

## Reproducibility

A record pins: definition digest, subject revisions + source digests,
corpus digests, toolchain (executor path/version, language revision, lab
revision, library path), per-observation result digests, witness digests.
Definitions refuse to run when the checkout revision or source bytes differ
from the pin: a historical result must not silently become evidence for a
different revision. Freshness is queryable (`lab_query.py stale`); stale
records remain valid history, not current evidence.

## Queryability

`scripts/lab_query.py list | show ID | by-subject FRAG | negatives |
inconclusive | stale | pressures` — all answered from records, never from
prose or logs.

## Adding an experiment

1. Write the definition (`experiments/definitions/LAB-EXP-NNN.json`);
   pin subject revisions to the current clean HEAD and source digests to
   current bytes (`python3 -c` sha256 or the runner's error message, which
   reports both).
2. Run `python3 scripts/lab_run.py experiments/definitions/LAB-EXP-NNN.json`.
3. On green witnesses the record lands in `experiments/records/` with
   compact evidence under `evidence/LAB-EXP-NNN/`.
4. Optionally `--persist` to publish through the embedded Store (sidecar
   `experiments/records/LAB-EXP-NNN.store.json`; the record bytes are
   never mutated by publication).
5. Link genuine gaps from `pressure/registry.md` (grounded entries with
   reproducers only).

## Test authoring notes

Every test-bearing module must `use mncs.test.suite` alongside
`mncs.test.assertions`, or the runner reports a misleading module-mismatch
error (LAB-PRESS-003). Module names mirror file paths relative to a
`MNCS_LIBRARY_PATH` root. Corpus-called functions take flat
boolean/finite/integer arguments only; keep records and arrays inside
module-internal helpers. Avoid `select()` in functions executed via
`experiment run` — use plain branches (LAB-PRESS-002).
