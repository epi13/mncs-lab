# RFC 0005 — Proof-Aware Introspection

- **Status:** Initial
- **Depends on:** RFCs 0001–0004

## Problem

MNCS includes proof/kernel concepts that should be intrinsic to interactive compilation rather than hidden behind batch compiler output. A serious interactive environment is also an unusually useful place to inspect compiler reasoning and generated artifacts.

## Decision

Make proof state and compiler artifacts queryable through structured introspection, with human-facing REPL commands layered on top.

Candidate views include:

- declared/inferred type;
- proof obligations;
- discharged/undischarged proof status;
- dependency graph;
- pre-optimization IR;
- optimized IR;
- backend lowering/assembly;
- definition generations/history;
- compilation/checking/execution timings;
- invalidation reasons.

## Invariants

1. Introspection must report compiler-owned state, not a lab-maintained imitation.
2. Proof results must identify the assumptions/generation under which they are valid.
3. A proof-inspection command must not silently alter committed semantics.
4. Human formatting must not be the only API; structured data should be available for tests, agents, IDEs, and other clients.
5. Security/capability boundaries apply to introspection output.

## Example interaction class

```text
> :type divide
> :proof divide
> :deps divide
> :ir divide
> :asm divide
```

These command spellings are illustrative, not normative.

## Pressure opportunity

If proof state cannot be queried incrementally without rerunning whole-program checks, that is compiler pressure to record, not a reason for the lab to infer proof status from text output.
