# Contributing to mncs-lab

`mncs-lab` is an experimental repository, but experiments still need disciplined evidence so successful ideas can graduate into the MNCS compiler without carrying accidental assumptions with them.

## Before changing architecture

Read:

- `README.md`
- `docs/architecture.md`
- `docs/compiler-boundary.md`
- `docs/session-model.md`
- the relevant RFCs under `rfcs/`

Changes to session identity, state lifetime, redefinition, JIT binding, proof semantics, invalidation, or compiler/lab ownership should update an RFC or add a new one.

## Preferred change shape

1. State the experimental question or problem.
2. Identify the relevant invariant/RFC.
3. Add the smallest useful experiment or test.
4. Measure and record the result under `evidence/` when appropriate.
5. Record grounded language/compiler pressure under `pressure/`.
6. Promote only validated reusable mechanisms into compiler-facing proposals.

## What belongs here

Good fits:

- REPL interaction experiments;
- persistent session behavior;
- Cranelift JIT experiments using compiler-owned lowering;
- symbol generation/redefinition policies;
- proof/introspection UX;
- latency, memory, invalidation, and dispatch measurements;
- pressure reproducers.

Poor fits:

- a parallel parser/type checker;
- a second proof kernel;
- canonical IR semantics duplicated from `mncs-compiler`;
- unrelated application features;
- silent host-language implementations that bypass missing MNCS/compiler capabilities.

## Pull requests

PRs should distinguish clearly between:

- architecture/design only;
- executable experiment;
- validated behavior;
- compiler/language pressure;
- functionality that is actually implemented versus proposed.
