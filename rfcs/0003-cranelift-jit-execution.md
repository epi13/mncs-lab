# RFC 0003 — Cranelift JIT Execution

- **Status:** Initial
- **Depends on:** RFCs 0001–0002

## Problem

Interactive MNCS needs low-latency native execution. Cranelift is already an MNCS backend direction and is suited to fast code generation, but a REPL adds code lifetime, symbol replacement, linking, and stale-reference concerns that batch output does not expose.

## Decision

Use Cranelift JIT as the first native interactive execution target while keeping MNCS semantics and compiler IR backend-neutral.

The intended flow is:

```text
committed/analyzable MNCS fragment
        ↓
compiler-owned semantic/proof checks
        ↓
compiler IR
        ↓
Cranelift lowering
        ↓
JIT code/data generation
        ↓
publish executable binding
        ↓
invoke through session runtime
```

## Invariants

1. Machine code is published only after required semantic/proof checks succeed.
2. Executable code is never treated as the canonical representation of a definition.
3. Redefinition should publish a new generation rather than patch arbitrary old machine code in place.
4. Retired JIT code must remain alive while any valid call/value may still reference it, or such references must be redirected safely.
5. W^X / executable-memory protections must follow platform-safe practices.
6. Native symbol/FFI exposure must obey MNCS capability and safety rules rather than making all host symbols implicitly reachable.

## Binding model hypothesis

Replaceable user-visible definitions should resolve through a stable logical binding/dispatch layer:

```text
foo -> logical binding slot
       ├─ foo#1 -> JIT generation A
       ├─ foo#2 -> JIT generation B
       └─ foo#3 -> JIT generation C (current)
```

Exact indirection mechanisms are experimental. Direct calls may be possible when dependencies are immutable for the lifetime of the caller; replaceable dependencies require invalidation/recompile or safe indirection.

## Measurements

Experiments should record:

- lowering/finalization latency;
- call dispatch overhead;
- code memory growth;
- reclamation behavior;
- cost of recompiling dependent callers versus indirection;
- target/platform differences.

## Alternatives

An interpreter or bytecode backend may later provide complementary behavior, especially for portability or debugging, but Cranelift JIT is the first native path to pressure.
