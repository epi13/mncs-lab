# RFC 0001 — Project Charter and Boundaries

- **Status:** Initial
- **Scope:** `mncs-lab`

## Problem

MNCS needs an interactive environment capable of pressuring the language and compiler under workloads that batch compilation does not exercise well: long-lived semantic state, native JIT execution, redefinition, incremental invalidation, proof inspection, and rapid compile/execute cycles.

Embedding every exploratory interaction directly into `mncs-compiler` would make unstable UX and experimental policy part of the compiler too early. Building a completely standalone REPL would risk duplicating compiler semantics.

## Decision

Create `mncs-lab` as an experimental interactive environment and compiler client.

`mncs-lab` owns:

- REPL and interaction experiments;
- session UX and policy;
- Cranelift JIT integration experiments through compiler-owned lowering;
- persistent-state experiments;
- introspection/benchmark/profiling interaction design;
- evidence capture;
- language/compiler pressure discovery.

`mncs-compiler` should ultimately own reusable semantic mechanisms needed by multiple clients, including parsing, typing, proof checking, IR, lowering, dependency information, and stable incremental/session primitives.

## Invariants

1. The lab must not become a second canonical compiler.
2. MNCS semantics must not depend on Cranelift-specific behavior.
3. Experimental policy should remain separable from reusable compiler mechanisms.
4. Host-language workarounds must not hide missing MNCS/compiler capabilities.
5. Claims of support require executable evidence.

## Ecosystem boundary

```text
mncs-language  -> language semantics and expressivity
mncs-compiler  -> canonical compiler/proof/backend mechanisms
mncs-lab       -> interactive experimentation and evidence
```

Future clients such as IDEs, agents, notebooks, tests, and compiler services may reuse compiler session mechanisms discovered here without inheriting the lab's terminal UX.

## Non-goals

- defining a second parser/type system/proof kernel;
- making a notebook product before session semantics are sound;
- making interactive execution mandatory for every backend;
- building a remote untrusted execution service in the initial architecture.

## Alternatives rejected

### Put the REPL directly in `mncs-compiler`

Rejected as the sole architecture because interaction policy is expected to change rapidly and should not force premature compiler API commitments.

### Make `mncs-lab` fully standalone

Rejected because it would encourage semantic duplication and divergence.

## Pressure expectation

The lab is explicitly expected to find missing capabilities. Confirmed deficiencies must be recorded using RFC 0006 rather than treated as reasons to bypass the compiler boundary silently.
