# Session Model

## Session identity

A session is a long-lived compilation and execution context. It has explicit identity, configuration, generations, and teardown semantics.

A submission is not automatically a generation. A fragment may parse incompletely, fail semantics/proof checking, or be inspected without being committed.

```text
submission
   │
   ├─ incomplete -> request continuation, no semantic commit
   ├─ invalid    -> diagnostics, no semantic commit
   └─ valid      -> analyzable candidate
                     │
                     ├─ inspect only
                     └─ commit -> new session generation
```

## Generations

Committed changes create monotonically ordered logical generations. A generation identifies the semantic world against which compiled artifacts and proof results are valid.

Generated machine code may have a different physical lifetime from the logical definition it implements. The session must not equate "new definition" with "overwrite old executable bytes."

## Values and type lifetime

A persistent value created in generation `G` may remain usable after later generations only when its representation and capabilities remain valid under explicit rules. Redefining a type must not silently reinterpret existing objects.

Candidate policies to test include:

- old values remain tied to their original type-generation identity;
- incompatible redefinition blocks affected bindings;
- explicit migration creates new values;
- session reset/reclamation drops unreachable generations safely.

## Reset and teardown

The lab should distinguish:

- clearing source/command history;
- clearing semantic definitions;
- dropping runtime values/resources;
- retiring JIT code;
- destroying the entire compiler session.

A single opaque `reset` should not hide materially different safety behavior.
