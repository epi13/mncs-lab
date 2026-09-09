# Compiler Boundary

## Principle

The REPL should be a first-class client of `mncs-compiler`, not a fork of compiler semantics.

The lab may pressure an API conceptually similar to:

```text
create_session(config) -> session
analyze_fragment(session, source) -> fragment_result
commit_fragment(session, fragment_result) -> generation
lower(session, artifact, backend) -> lowered_artifact
publish_jit(session, lowered_artifact) -> executable_binding
inspect(session, subject, view) -> structured_artifact
invalidate(session, change) -> invalidation_set
drop_session(session)
```

The names and exact granularity are deliberately non-normative. The requirement is that the compiler own semantic truth while the lab owns interactive policy.

## Why this boundary matters

If the lab owns its own symbol/type/proof model, every REPL feature becomes a second compiler feature that can diverge. If the compiler instead exposes only whole-program batch compilation, every interactive experiment must fake persistence by rebuilding temporary programs.

The lab exists to discover the smallest middle layer that supports interactive clients without forcing REPL-specific UX into the compiler core.

## Graduation rule

A mechanism should move toward `mncs-compiler` when it is:

1. required by more than one plausible compiler client;
2. semantically independent of a particular REPL command/UX choice;
3. covered by deterministic tests;
4. clear about invalidation and lifetime behavior;
5. compatible with the proof/type ownership model;
6. shown by evidence to be useful enough to justify API stability.
