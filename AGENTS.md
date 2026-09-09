# AGENTS.md — mncs-lab

## Mission

Use a real interactive execution environment to discover what MNCS and `mncs-compiler` need for persistent compilation, JIT execution, proof-aware interaction, introspection, and rapid incremental development.

## Current phase

Architecture-first bootstrap. The RFCs describe starting contracts and hypotheses; they do **not** imply a working REPL, JIT runtime, persistent heap, or incremental compiler API already exists.

## Repository boundary

`mncs-lab` owns experimental interaction policy, prototypes, session UX, comparative experiments, and evidence.

It must not become a second implementation of parsing, type checking, proof semantics, IR, optimization, or backend lowering. Reusable compiler mechanisms belong in `mncs-compiler` once validated.

## Implementation policy

- Prefer MNCS-language for lab logic when the language can express the requirement correctly.
- Do not hide core semantics in Rust, Python, C, or another host language simply because MNCS or the compiler is missing a feature.
- If a host workaround is unavoidable, keep it narrow, label it, and record the underlying pressure.
- Cranelift is the first JIT target, not the semantic definition of interactive MNCS.
- Avoid changing `mncs-language` or `mncs-compiler` from this repository unless a task explicitly spans repositories. Default lab work should discover pressure and record it here.

## Pressure discipline

Read `docs/language-pressure.md` and RFC 0006 before recording gaps.

A pressure entry must be grounded in an attempted workload and include:

1. observed limitation;
2. minimal reproducer or concrete call sequence;
3. expected behavior;
4. current workaround, if any;
5. correctness/safety consequences;
6. performance/ergonomic consequences;
7. suspected ownership (`mncs-language`, `mncs-compiler`, tooling, or unresolved);
8. evidence links.

Do not pre-populate speculative gaps as confirmed deficiencies.

## Experimental discipline

Experiments should answer a specific question, record setup and outcome, and avoid turning temporary prototypes into architectural commitments without RFC review.

Important measurements include:

- cold and warm fragment compilation latency;
- incremental invalidation scope;
- JIT finalization/link latency;
- dispatch/redefinition overhead;
- code and session memory growth;
- proof/checking latency;
- diagnostic recovery after malformed/incomplete fragments;
- state retention/reclamation behavior.

## Safety and correctness

Interactive execution increases the importance of lifetime, stale-code, capability, and invalidation safety. Treat dangling JIT references, stale proof assumptions, invalidated type layouts, capability leaks, and use-after-redefinition behavior as correctness/security issues, not merely REPL inconveniences.
