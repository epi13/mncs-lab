# Tests

Tests should evolve with implementation and emphasize semantic/session safety, not merely command snapshots.

Expected coverage includes:

- fragment commit versus failure/incomplete behavior;
- persistent definitions and values;
- deterministic session generations;
- redefinition and dependent invalidation;
- stale-code prevention;
- type/layout lifetime safety;
- JIT publish/retire behavior;
- proof-state invalidation;
- structured introspection;
- recovery after malformed submissions;
- cold/warm incremental latency regressions.
