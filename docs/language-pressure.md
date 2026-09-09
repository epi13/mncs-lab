# Language and Compiler Pressure

## Purpose

`mncs-lab` should expose deficiencies instead of normalizing workarounds. Interactive compilation is expected to pressure language, compiler, runtime, and tooling behavior that batch workloads may not reveal.

## Pressure categories

### Language

Examples include missing expressivity around lifetimes, dynamic/native calls, FFI, effects, concurrency, reflection, values with session lifetime, or standard-library/runtime facilities.

### Compiler

Examples include missing incremental session APIs, inability to compile fragments, coarse invalidation, non-queryable proof state, backend/JIT limitations, unstable artifact identity, insufficient diagnostics, or unacceptable incremental latency.

### Tooling

Examples include harness gaps, environment limitations, poor evidence capture, or packaging/developer workflow deficiencies.

## Grounding rule

Do not create a registry item simply because a future feature might be difficult. A confirmed pressure item requires an attempted workload and evidence.

## Required record

Each confirmed entry should contain:

- ID and short title;
- category and severity;
- status;
- observed behavior;
- minimal reproducer or exact experimental sequence;
- expected/desired semantics;
- safety/correctness impact;
- performance/ergonomic impact;
- current workaround, if any;
- likely owning repository;
- evidence links;
- promotion/resolution notes.

See RFC 0006 and `pressure/registry.md`.
