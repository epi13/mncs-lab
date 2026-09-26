# Pressure Registry

Grounded findings from attempted Lab work. Each entry required an attempted
workload and reproducible evidence; speculative risks stay in RFCs and
experiment notes. Entry format follows `docs/language-pressure.md`.

Family-wide records live in the Commons pressure exchange; repo-local IDs
below are preserved there as `legacyIds`.

---

### LAB-PRESS-001 — No compiler session/incremental API; live REPL blocked

- **Category:** compiler
- **Severity:** blocker (for the interactive half of the Lab charter)
- **Status:** open
- **Observed in:** campaign survey + `mncs.lab.session` policy work
- **Owner candidate:** `mncs-compiler`
- **Commons record:** `MNCS-COMPILER-<filed at campaign end>` (legacyId `mncs-lab:LAB-PRESS-001`)

**Observed behavior**

`mncs-compiler` exposes no session concept: no create/define/commit/
publish/abandon API, and the `mncs` CLI offers only batch routes
(`compile`, `test`, `experiment run`, `call`, `observe`). The compiler's
own `kernel.mncs` states session inputs are out of scope. There is
therefore nothing for a REPL to hold a persistent definition, generation,
or JIT binding through.

**Minimal reproducer**

`pressure/reproducers/no-session-api/` holds the `mncs --help` command
surface (no session verbs) and the exact compiler-side exclusion quote.

**Expected behavior**

The smallest session API sketched in `docs/compiler-boundary.md`:
create/drop a session, analyze a fragment against prior state, commit a
generation, invalidate dependents, inspect artifacts — owned by the
compiler, driven by Lab policy.

**Impact**

Correctness: a host-side REPL loop over batch compilation would fake
persistence by rebuilding temporary programs — the failure mode
`docs/compiler-boundary.md` exists to forbid. The Lab deliberately does
not ship one.

**Current workaround**

`mncs.lab.session` encodes the fragment lifecycle, generation discipline,
and reset matrix as MNCS decision logic with Test proofs, so the policy
the missing API must satisfy is already specified and verified. The live
session itself is not faked.

**Evidence**

- `docs/compiler-boundary.md`, `docs/session-model.md`
- `mncs/lab/session.mncs`, `tests/lab/session_tests.mncs` (11 passing)
- reproducer directory (CLI surface + exclusion quote)

**Resolution / promotion notes**

Recorded here; family-wide declaration filed in the Commons exchange.

---

### LAB-PRESS-002 — `select()` poisons `experiment run` suites to UNKNOWN

- **Category:** language/compiler contract
- **Severity:** major
- **Status:** open, workaround in Lab kernels
- **Observed in:** LAB-EXP-001 subject preparation (`mncs.lab.variants`)
- **Owner candidate:** `mncs-language` (experiment contract vs frontend intent)
- **Commons record:** `MNCS-LANG-<filed at campaign end>` (legacyId `mncs-lab:LAB-PRESS-002`)

**Observed behavior**

Any `select(cond, a, b)` in a function executed via `mncs experiment run`
resolves every corpus case correctly yet reports suite status UNKNOWN with
`unresolved_reasons: ["compilation retained required unresolved
obligations"]`. The frontend attaches a `realization-branchless`
machine-intent requirement to each `select`; the experiment contract
(`bounded_execution_agreement`, `allow_unknown: false`) counts it as
required; no backend discharges it. `mncs.test`'s own `assertions.mncs`
uses `select` pervasively, so the framework's idiom and the experiment
contract disagree: identical semantics PASS under `mncs test` and go
UNKNOWN under `mncs experiment run`.

**Minimal reproducer**

`pressure/reproducers/select-unknown/`: one-branch kernel (PASS) beside
one-`select` kernel (UNKNOWN), same corpus shape, observed result excerpts.

**Expected behavior**

Either supported backends discharge the branchless-select requirement, or
the toolchain names `select` in the unresolved-obligation diagnostic, or
the contract documents that `select` is unavailable on the experiment
path. Silent all-cases-met UNKNOWN is the failure: it reads as an
execution problem while the cause is a source idiom.

**Impact**

Correctness/ergonomics: experiment authors writing idiomatic MNCS get
UNKNOWN suites with no pointer at the cause; Lab records would inherit
false UNKNOWNs. Safety: none (fail-closed direction), but evidence value
is destroyed.

**Current workaround**

`mncs.lab.variants` uses a plain-branch helper (`bump_on_difference`)
instead of `select`; the workaround is labeled at the use site. The
generic fold semantics are unchanged and still proven by `mncs test`.

**Evidence**

- reproducer directory; `mncs/lab/variants.mncs` use-site comment
- pre-fix result excerpts (UNKNOWN + `machine-intent` obligation ids);
  post-fix PASS on both backends

**Resolution / promotion notes**

Recorded here; family-wide declaration filed in the Commons exchange.

---

### LAB-PRESS-003 — Missing suite import misreported as module mismatch

- **Category:** tooling
- **Severity:** minor
- **Status:** open
- **Observed in:** Lab suite authoring (first `mncs test` probe)
- **Owner candidate:** `mncs-test`

**Observed behavior**

A test module importing `mncs.test.assertions` but not `mncs.test.suite`
fails with `native suite initializer did not return SuiteSummary ...
"execution target module does not match program"`. Nothing about the
module mismatches; the missing suite import is the entire cause. Adding
the single `use mncs.test.suite;` line turns the identical file PASS.

**Minimal reproducer**

`pressure/reproducers/suite-import/`: failing file, passing file (one
line differs), observed error text.

**Expected behavior**

Name the missing suite initializer import (or the unregistered suite)
instead of reporting a module mismatch.

**Impact**

Ergonomic only, but it cost a full confusion cycle on the first Lab suite
and will tax every new native-test author the same way.

**Current workaround**

Documented in `docs/experiment-model.md` authoring notes: every
test-bearing module must `use mncs.test.suite`.

**Evidence**

- reproducer directory with both files and observed outputs

**Resolution / promotion notes**

Repo-local; no Commons record (minor diagnostic wording, single owner).
