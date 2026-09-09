# RFC 0004 — Incremental Compilation and Redefinition

- **Status:** Initial
- **Depends on:** RFCs 0001–0003

## Problem

Interactive use requires small edits to compile against large accumulated session state without rebuilding everything. It also requires safe replacement of definitions while preserving unaffected state.

## Decision

Treat definitions and compiler artifacts as generation-addressed entities with explicit dependency relationships.

Redefinition creates a new logical definition generation. The old generation is not mutated into the new one.

```text
square#1  -> dependencies D1 -> code C1
square#2  -> dependencies D2 -> code C2  (current binding)
```

The compiler/session layer determines an invalidation set based on semantic dependencies, proof assumptions, type/layout dependencies, optimization dependencies, and backend binding strategy.

## Invariants

1. Redefinition is atomic at the committed-session boundary.
2. Unaffected definitions should remain reusable when their assumptions remain valid.
3. A stale compiled artifact must never execute under assumptions known to be invalid.
4. Type/layout changes receive stricter invalidation than body-only changes where required.
5. Proof dependencies participate in invalidation rather than being treated as comments.
6. Incremental compilation must produce semantics equivalent to a clean compilation of the same committed session state.

## Change classes to pressure

- body-only function replacement;
- signature change;
- constant/global change;
- type field/layout change;
- trait/interface/conformance change;
- import/module change;
- proof contract/precondition/postcondition change;
- optimization-relevant metadata change.

## History and restore

The lab may experiment with history/restore, but restoring a logical binding must not resurrect invalid runtime resources or violate current capability/lifetime rules. History is therefore not assumed to be a trivial pointer swap.

## Performance target philosophy

No fixed latency target is standardized yet. The lab should first measure cold versus warm cost, invalidation breadth, and scaling with session size, then use those results to pressure compiler architecture.
