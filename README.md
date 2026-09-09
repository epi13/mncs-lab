# mncs-lab

Experimental interactive environment for MNCS, focused on REPL design, Cranelift JIT execution, persistent compiler sessions, incremental compilation, proof-aware execution, runtime state, compiler introspection, and other interactive language/compiler experiments.

> **Status:** architecture-first bootstrap. This repository currently defines the laboratory boundary, experimental contracts, initial RFCs, and language/compiler pressure workflow. It does not yet claim a working REPL or JIT runtime.

## Why this exists

Batch compilation is only one way to use a language. MNCS also needs a place to pressure the compiler as a long-lived interactive system: accept fragments, retain semantic state, compile quickly, execute native code, redefine symbols, inspect proof obligations and IR, and recover cleanly from incomplete or invalid input.

`mncs-lab` exists to explore those requirements without prematurely making every experiment a permanent `mncs-compiler` API or language feature.

The intended relationship is:

```text
mncs-language
     │
     ▼
mncs-compiler
  ├─ parsing / semantics
  ├─ proof kernel
  ├─ IR + optimization
  ├─ backend lowering
  └─ incremental/session capabilities
           │
           ▼
       mncs-lab
  ├─ REPL experiments
  ├─ Cranelift JIT sessions
  ├─ persistent definitions/state
  ├─ introspection surfaces
  ├─ benchmark/profiling probes
  └─ language/compiler pressure evidence
```

The lab should discover and validate useful compiler capabilities. Stable, generally reusable mechanisms may later graduate into `mncs-compiler`; experimental policy and interaction design should remain here until that boundary is clear.

## Founding principles

1. **The REPL is a compiler client, not a second compiler.** Parsing, typing, proof checking, IR semantics, and lowering belong to compiler-owned mechanisms.
2. **Interactive compilation is first-class.** A session is not modeled as repeatedly compiling isolated temporary programs.
3. **State must be explicit.** Definitions, values, proof state, imports, generated code, and invalidation relationships need observable lifetimes and generations.
4. **Redefinition must not depend on unsafe code mutation.** New generations should replace bindings through explicit indirection/versioning semantics.
5. **Proof and introspection are part of the experience.** Interactive execution should make it easy to inspect types, proof obligations, IR, lowering, assembly, dependencies, and compilation costs.
6. **Cranelift JIT is the first native interactive backend target, not the only possible execution model.** The architecture must not make Cranelift semantics canonical MNCS semantics.
7. **Experiments must produce evidence.** Successful and failed approaches should leave behind reproducible results rather than only implementation churn.
8. **Language/compiler gaps are recorded, not hidden.** When MNCS or the compiler cannot express a required interactive behavior safely or efficiently, record the pressure explicitly.

## Initial experimental questions

- What is the smallest compiler session API capable of supporting a serious REPL?
- Which semantic state must persist between fragments?
- How should incomplete fragments differ from invalid programs diagnostically?
- How should symbol redefinition and dependency invalidation work?
- How should JIT-generated code reference definitions that may later be replaced?
- How do values and heap objects outlive the fragment that created them?
- What proof state is session-scoped versus definition-scoped?
- Which compiler artifacts should be inspectable (`type`, proof, IR, optimized IR, assembly, dependency graph, timings)?
- How cheaply can the compiler compile a small change after a large session history?
- Which capabilities belong permanently in `mncs-compiler`, and which should remain interaction policy in `mncs-lab`?

## Repository layout

```text
.
├── AGENTS.md
├── CONTRIBUTING.md
├── ROADMAP.md
├── SECURITY.md
├── docs/
│   ├── architecture.md
│   ├── compiler-boundary.md
│   ├── interactive-surface.md
│   ├── language-pressure.md
│   └── session-model.md
├── rfcs/
│   ├── README.md
│   ├── 0001-project-charter-and-boundaries.md
│   ├── 0002-persistent-interactive-session-model.md
│   ├── 0003-cranelift-jit-execution.md
│   ├── 0004-incremental-compilation-and-redefinition.md
│   ├── 0005-proof-aware-introspection.md
│   └── 0006-language-and-compiler-pressure-methodology.md
├── pressure/
│   ├── README.md
│   ├── registry.md
│   └── reproducers/
├── experiments/
│   └── README.md
├── evidence/
│   └── README.md
├── src/
│   └── README.md
└── tests/
    └── README.md
```

## RFC map

| RFC | Topic |
|---|---|
| [0001](rfcs/0001-project-charter-and-boundaries.md) | Project charter, scope, and ecosystem boundaries |
| [0002](rfcs/0002-persistent-interactive-session-model.md) | Persistent interactive compiler/session model |
| [0003](rfcs/0003-cranelift-jit-execution.md) | Cranelift JIT execution and code lifetime |
| [0004](rfcs/0004-incremental-compilation-and-redefinition.md) | Incremental fragments, redefinition, generations, and invalidation |
| [0005](rfcs/0005-proof-aware-introspection.md) | Proof-aware execution and compiler introspection |
| [0006](rfcs/0006-language-and-compiler-pressure-methodology.md) | Language/compiler pressure evidence and promotion workflow |

These RFCs establish starting hypotheses and invariants. Experimental evidence is expected to amend or replace details.

## Language and compiler pressure

`mncs-lab` is intentionally a pressure test for both `mncs-language` and `mncs-compiler`.

When a required behavior cannot be expressed safely, efficiently, deterministically, or ergonomically, record it under `pressure/` instead of silently moving semantics into a host-language workaround. Pressure entries should distinguish:

- **language pressure** — syntax, type system, ownership/lifetimes, effects, concurrency, FFI, reflection, runtime, or standard-library deficiency;
- **compiler pressure** — incremental APIs, symbol management, proof state, dependency invalidation, backend/JIT support, diagnostics, artifact inspection, or performance deficiency;
- **tooling pressure** — developer workflow, test harness, observability, packaging, or environment limitation.

Speculative risks belong in RFCs or experiment notes. `pressure/registry.md` should contain only grounded findings from attempted work with reproducible evidence.

## Expected interactive surface

The exact syntax is experimental, but the lab should eventually pressure capabilities in this family:

```text
> let x = 12
> square(x)
144

> :type square
> :proof square
> :ir square
> :asm square
> :deps square
> :bench square(x)
> :history square
> :pressure
```

These examples describe desired interaction classes, not implemented commands.

## Implementation policy

The intended implementation is **MNCS-language first** wherever the language can express the requirement correctly. Cranelift integration and compiler/session mechanisms may initially require work in `mncs-compiler`; do not duplicate compiler semantics inside this repository merely to make a demo work.

Host-language bootstrap code is acceptable only when clearly bounded, labeled, and backed by a pressure entry if it substitutes for a missing MNCS/compiler capability.

## License

Apache-2.0. See `LICENSE`.
