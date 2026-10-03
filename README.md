# mncs-lab

<!-- MNCS:generated:begin -->
<!-- MNCS:generated:end -->

Controlled investigations over MNCS behavior, realized as a current MNCS
application: typed experiment definitions, MNCS-native comparison and
outcome semantics, Test-proven kernels, canonical execution, digest-pinned
records, and grounded language/compiler pressure with reproducers.

> **Status:** realized native slice. Lab defines experiments in JSON,
> implements their semantics in MNCS (`mncs/lab/`), proves them with
> `mncs test` suites, executes them through the canonical toolchain,
> classifies outcomes in MNCS, and persists digest-pinned records
> (optionally as Store objects). Two backend-comparison experiments are
> green across portable-WASM, research-bytecode, and Cranelift.

## Why this exists

Batch compilation is only one way to pressure a language. MNCS also needs
a place that asks controlled questions — do these backends agree? does
this hypothesis survive contact with execution? — with exact subjects at
exact revisions, and that keeps the answer reproducible after the code
moves on. `mncs-lab` is that place.

The intended relationship is:

```text
question (RAVEL obligation, RFC, or open investigation)
     │
     ▼
mncs-lab experiment definition
     │  subjects @ exact revisions, controlled variants, corpora
     ▼
canonical execution (mncs experiment run / mncs test — Forge/Fabric paths)
     │
     ▼
structured observations -> mncs.lab comparison/outcome semantics
     │
     ├─ test propositions evaluated by mncs-test (Lab asserts nothing itself)
     ├─ records persisted (files + optional Store objects)
     ├─ Debug receives structured failure evidence
     └─ gaps persist as pressures with reproducers
```

## Founding principles (kept from the bootstrap)

1. **Experiments are typed records, not scripts plus prose.** The system
   can reason about what was attempted: hypothesis, subjects, variants,
   observations, conclusion.
2. **Hypothesis is not result.** A contradicted hypothesis is preserved
   evidence, never rewritten history.
3. **INCONCLUSIVE is not FAIL; UNKNOWN is not PASS.** Incomplete evidence
   never becomes false certainty in either direction.
4. **Subjects must be green first.** A comparison subject that fails on
   its own corpus aborts the run; uniform failure is not agreement.
5. **Classification executes in MNCS.** Every record carries two MNCS
   witnesses (variant integrity, standing); disagreement fails the run
   closed instead of writing the record.
6. **The REPL is a compiler client, not a second compiler** — and until
   the compiler owns sessions, Lab ships policy, not a fake session.
7. **Cranelift is a comparison subject, not canonical semantics.**
8. **Gaps are recorded, not hidden.** Host code that substitutes for a
   missing capability is labeled and linked to a pressure entry.

## Recovered intent and classification

Historical Lab (RFCs 0001–0006, `docs/`) set out to be an interactive
compiler-session laboratory: REPL policy, JIT sessions, generations,
proof-aware introspection, pressure. Against today's architecture:

- **Enduring, now realized:** experiment discipline
  (question/hypothesis/setup/criteria/evidence/conclusion), pressure
  workflow with reproducers, generation discipline and state lifetimes as
  MNCS policy, interaction-policy-vs-mechanism split, negative-result
  preservation.
- **Migrated to canonical owners:** parsing/typing/proof/IR/lowering
  (compiler, never Lab's), assertion semantics (`mncs-test`), execution
  orchestration (Forge), persistence authority (Store/Commons), machine
  telemetry (System Monitor), provenance graph (Lineage).
- **Retained as specified-but-blocked policy:** the live interactive
  session. `mncs.lab.session` proves the lifecycle/generation/reset
  policy in MNCS today; executing it awaits a compiler session API
  (LAB-PRESS-001). Lab does not fake persistence by recompiling fragments.
- **Discarded:** general notebook ambitions, remote multi-tenant
  execution, Cranelift-as-semantics (all explicit non-goals in
  `docs/architecture.md`).

## Repository layout

```text
.
├── mncs/lab/                  # MNCS-native semantics (the canonical Lab)
│   ├── outcome.mncs           # hypothesis-standing algebra
│   ├── variants.mncs          # controlled-comparison (variant integrity)
│   └── session.mncs           # interactive-session policy (no live session yet)
├── tests/lab/                 # mncs test suites proving the kernels (31 tests)
├── tests/test_lab.py          # host-side record/rule/query tests (10 tests)
├── corpora/                   # executable kernel corpora (generator-built, drift-gated)
├── experiments/
│   ├── definitions/           # typed experiment definitions (revision-pinned)
│   └── records/               # digest-pinned records + Store sidecars
├── evidence/                  # compact per-run observation summaries
├── scripts/                   # lab_run / lab_check / lab_query + builders/fetch
├── src/mncs_lab/              # host boundary (process/filesystem only, no semantics)
├── pressure/
│   ├── registry.md            # grounded entries (LAB-PRESS-001/002/003)
│   ├── reproducers/           # minimal reproducers per entry
│   └── commons-drafts/        # exact Commons filing inputs (filed: see registry)
├── docs/
│   ├── experiment-model.md    # the canonical pipeline (start here)
│   ├── TOOLCHAIN.md           # pinned executor + library resolution
│   ├── architecture.md        # original boundary architecture (still current)
│   ├── session-model.md       # session vocabulary (realized as mncs.lab.session)
│   ├── compiler-boundary.md   # the API Lab pressures for (LAB-PRESS-001)
│   ├── interactive-surface.md # command classes (policy, not implemented surface)
│   └── language-pressure.md   # pressure categories and grounding rule
├── rfcs/                      # 0001-0006 starting hypotheses (session half still open)
└── ROADMAP.md                 # evidence-driven phases with current status
```

## Quick start

```bash
# Resolve the toolchain (explicit, digest-verified) or use a sibling checkout.
python3 scripts/fetch_mncs_executor.py --dest ~/.local/bin/mncs-executor

# Enforcement boundary: corpora sync + native suites + record integrity.
python3 scripts/lab_check.py

# Execute an experiment definition end to end.
python3 scripts/lab_run.py experiments/definitions/LAB-EXP-001.json

# Query prior work instead of repeating it.
python3 scripts/lab_query.py list
python3 scripts/lab_query.py by-subject mncs.lab.variants
python3 scripts/lab_query.py negatives
```

## Current experiments

| ID | Question | Standing |
|---|---|---|
| LAB-EXP-001 | Do portable-WASM and research-bytecode agree on Lab kernels? | SUPPORTED (42/42) |
| LAB-EXP-002 | Does the Cranelift adapter agree with the WASM baseline? | SUPPORTED (42/42) |

## Pressures

Repo-local grounded entries in `pressure/registry.md` with reproducers;
family-wide declarations in the Commons exchange:

- LAB-PRESS-001 → `MNCS-COMPILER-40CF32855108` (blocker, open): no
  compiler session API; live REPL honestly absent.
- LAB-PRESS-002 → `MNCS-LANG-BD5D650AC9D8` (major, open): `select()`
  turns green experiment suites UNKNOWN; Lab kernels use branches.
- LAB-PRESS-003 (minor, open, repo-local): missing suite import
  misreported as a module mismatch.

## What host code remains and why

`src/mncs_lab/` and `scripts/` own process/filesystem effects only:
locating the executor, invoking it, hashing bytes, reading git state,
writing records, Store publication, bounded queries. Semantics
(combination order, controlled pairs, lifecycle, classification) live in
MNCS and are proven by Test; the host never reimplements them.

## License

Apache-2.0. See `LICENSE`.
