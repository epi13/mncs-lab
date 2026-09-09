# Roadmap

The roadmap is intentionally evidence-driven. Later phases should change when experiments invalidate early assumptions.

## Phase 0 — Foundation

- establish project boundaries and RFC discipline;
- define persistent session vocabulary;
- define pressure/evidence workflow;
- identify the minimum compiler capabilities required for the first executable experiment.

## Phase 1 — Minimal interactive execution

- accept a complete expression or definition fragment;
- compile through `mncs-compiler` rather than duplicating semantics;
- lower a supported subset through Cranelift JIT;
- execute and return a result;
- expose structured diagnostics and compilation timing.

Success means native interactive execution works for a deliberately small subset with an explicit boundary, not that the full language is supported.

## Phase 2 — Persistent sessions

- retain definitions and typed session metadata;
- support values whose lifetime extends across submissions;
- model imports/session namespaces;
- distinguish incomplete input from invalid input;
- define deterministic reset/drop behavior.

## Phase 3 — Redefinition and invalidation

- version definitions by generation;
- route replaceable calls through explicit bindings/dispatch;
- invalidate dependent compiler artifacts safely;
- retain or reject old values according to explicit type/layout lifetime rules;
- add history and restore experiments where sound.

## Phase 4 — Proof-aware introspection

- inspect inferred/declared types;
- expose proof obligations and proof status;
- inspect IR before/after optimization;
- inspect backend lowering/assembly;
- inspect dependency and invalidation graphs;
- expose compilation and execution measurements.

## Phase 5 — Serious REPL ergonomics

- multiline/incomplete fragment handling;
- history and session persistence experiments;
- structured completion/introspection hooks;
- benchmark/profile commands;
- error recovery that preserves unaffected session state.

## Phase 6 — Compiler-service integration

Evaluate whether the mature session API should be local-only, embedded, or usable through the broader compiler-service architecture so REPLs, IDEs, agents, tests, and other tools can share incremental compiler capabilities.

## Continuous objective — Pressure MNCS

Every phase should identify language/compiler limitations with minimal reproducers and evidence. Do not let host workarounds make missing capabilities invisible.
