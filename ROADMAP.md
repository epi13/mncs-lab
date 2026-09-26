# Roadmap

Evidence-driven as before; this revision records what the native
realization campaign established and what remains genuinely blocked.

## Phase 0 — Foundation

Done (bootstrap commit): boundaries, RFCs, session vocabulary,
pressure/evidence workflow, minimum compiler capabilities identified.

## Phase 1 — Minimal interactive execution (RESOLVED AS POLICY, BLOCKED AS MACHINERY)

The Lab can accept, classify, and dispose fragments — as MNCS decision
logic (`mncs.lab.session`, proven by 11 native tests). It cannot execute
an interactive session because no compiler session API exists
(LAB-PRESS-001). Deliberately not faked: a host loop over batch
compilation would violate the compiler boundary. This phase reopens when
the compiler owns sessions; the policy it must satisfy is already written
and proven.

## Phase 2 — Persistent sessions (BLOCKED, specified)

Generations, value/type lifetimes, reset taxonomy: specified in
`mncs.lab.session` + `docs/session-model.md`. Executable once Phase 1's
machinery lands.

## Phase 3 — Redefinition and invalidation (BLOCKED, specified)

Generation discipline (`generation_ok`: successor-only, no skips/replays)
is specified and proven. Dependent invalidation awaits compiler machinery.

## Phase 4 — Proof-aware introspection (OPEN)

Unstarted as Lab surface. Introspection commands (`:type`, `:proof`,
`:ir`, ...) remain policy classes in `docs/interactive-surface.md`, not
implemented commands. No shadow compiler will be built to fake them.

## Phase 5 — REPL ergonomics (OPEN, behind Phase 1)

Multiline handling, history UX, completion hooks, benchmark display, error
recovery: design stays in RFCs until sessions execute.

## Phase 6 — Compiler-service integration (OPEN)

Evaluate shared incremental capabilities once a session API exists to
share.

## Realized instead: native experiment layer (DONE)

Not on the original roadmap, now the Lab's core: typed definitions,
MNCS comparison/outcome semantics, Test proofs, canonical execution,
digest-pinned records, Store publication, bounded queries, pressure
generation. LAB-EXP-001/002 green across three backends.

## Near-term follow-ups (no v2, same architecture)

- Forge Provider-Protocol speaker for `lab_run` definitions (Forge owns
  orchestration; Lab needs a declared provider voice, not its own).
- Cross-record relations via Lineage once experiment bindings exist in
  the provenance graph (records already carry exact digests).
- Session machinery the moment LAB-PRESS-001 moves; policy is ready.
- Retire `select()` workaround in kernels when LAB-PRESS-002 resolves
  (use-site labeled; Commons record filed).

## Continuous objective — Pressure MNCS (ACTIVE)

LAB-PRESS-001 (blocker), LAB-PRESS-002 (major), LAB-PRESS-003 (minor)
filed this campaign with reproducers; 001/002 escalated to Commons.
