# Pressure Registry

No confirmed pressure entries yet. This repository is at the architecture bootstrap stage.

Add entries only after an attempted workload demonstrates a concrete deficiency.

## Entry template

### LAB-PRESS-XXX — Short title

- **Category:** language | compiler | tooling | unresolved
- **Severity:** blocker | major | moderate | minor
- **Status:** open | workaround | proposed | fixed | verified
- **Observed in:** experiment/test/commit reference
- **Owner candidate:** `mncs-language` | `mncs-compiler` | `mncs-lab` | other

**Observed behavior**

Describe what actually happened.

**Minimal reproducer**

Link a file under `pressure/reproducers/` or provide the exact command/API sequence.

**Expected behavior**

State the capability or semantics required by the workload.

**Impact**

Describe correctness, safety, performance, and ergonomic consequences.

**Current workaround**

Document any temporary workaround and why it must not become hidden canonical behavior.

**Evidence**

Link tests, traces, diagnostics, timings, or compiler artifacts.

**Resolution / promotion notes**

Record the proposed language/compiler change and later verification evidence.
