# RFC 0002 — Persistent Interactive Session Model

- **Status:** Initial
- **Depends on:** RFC 0001

## Problem

A capable REPL cannot be modeled well as repeated isolated whole-program compilations. Definitions, imports, proof results, runtime values, generated code, and diagnostics have distinct lifetimes that may span many submissions.

## Decision

Model interactive use around an explicit long-lived session with committed logical generations.

A session contains separable state classes:

- source/submission state;
- semantic state;
- proof state;
- compiler artifacts;
- runtime values/resources;
- JIT code/data generations;
- observability/evidence metadata.

A submitted fragment is analyzed before it is committed. Incomplete or invalid fragments do not advance the semantic generation.

```text
session G
   + submission
       ├─ incomplete -> continuation requested, remain G
       ├─ invalid    -> diagnostics, remain G
       └─ valid      -> candidate
                          ├─ inspect -> remain G
                          └─ commit  -> G+1
```

## Session invariants

1. Failed submissions must not partially mutate committed semantic state.
2. A committed generation identifies the semantic assumptions under which artifacts are valid.
3. Runtime and JIT lifetimes must be explicit and need not equal source-history lifetime.
4. Teardown must release owned runtime/JIT resources deterministically where the runtime permits.
5. Type redefinition must never reinterpret existing values implicitly.
6. Proof results must be invalidated when assumptions they depend on change.

## Persistent values

Values may outlive the fragment that created them, but only under defined lifetime/type-generation rules. The initial policy to test is that a value retains the identity of the type/layout generation that created it; incompatible type redefinition does not mutate that identity.

## Reset semantics

The lab should not hide all reset behavior behind one ambiguous operation. Experiments should distinguish at least:

- command/source-history clearing;
- semantic namespace reset;
- runtime value/resource drop;
- JIT retirement;
- complete session destruction.

## Failure behavior

A compiler crash, proof failure, JIT publication failure, or runtime trap must not leave the session claiming a committed generation that was never atomically established.

## Open questions

- whether session generations are global or can form subgraphs/branches;
- whether values can be explicitly migrated across type generations;
- whether session snapshots become persistent artifacts;
- which state can be shared by concurrent clients safely.
