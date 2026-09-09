# Architecture

## Role of the lab

`mncs-lab` is the experimental client of interactive compiler capabilities. It is deliberately separated from `mncs-compiler` so interaction policy can change rapidly without making each experiment a compiler contract.

```text
source fragment
     │
     ▼
interaction layer (mncs-lab)
     │  classify fragment / session command
     ▼
compiler session boundary
     ├─ parse / recover
     ├─ semantic analysis
     ├─ proof obligations
     ├─ dependency analysis
     ├─ IR generation
     └─ backend lowering
              │
              ▼
        Cranelift JIT target
              │
              ▼
       executable generation
              │
              ▼
         session runtime
```

## State classes

A useful interactive session is expected to contain several distinct classes of state:

- **source state** — submitted fragments and source identities;
- **semantic state** — symbols, types, imports, constraints, dependencies;
- **proof state** — obligations, discharged evidence, invalidation links;
- **compiler artifact state** — IR, optimized IR, lowered functions, diagnostics;
- **runtime state** — values, heap/session objects, resources;
- **JIT state** — executable generations, data objects, dispatch bindings;
- **observability state** — timings, counters, pressure/evidence references.

These should not be collapsed into one opaque REPL context because their invalidation and lifetime rules differ.

## Stable mechanism versus experimental policy

Candidate compiler mechanisms:

- create/drop an incremental compilation session;
- submit/analyze a fragment against prior session state;
- query structured symbols/types/proofs/dependencies;
- lower selected artifacts to a backend;
- publish a definition generation;
- invalidate/recompute dependents;
- expose stable diagnostic and artifact identifiers.

Candidate lab policy:

- command syntax (`:type`, `:ir`, etc.);
- history presentation;
- when to auto-print values;
- redefinition UX;
- benchmarking display;
- experiment toggles;
- session persistence UX.

The lab should make this distinction visible in code and docs.

## Non-goals

`mncs-lab` should not become:

- the canonical parser/type checker/proof kernel;
- a replacement for `mncs-compiler`;
- a general notebook application before session semantics are sound;
- a remote multi-tenant execution service by default;
- a requirement that all MNCS backends support interactive JIT semantics.
