# Reproducer: LAB-PRESS-001 (no compiler session API)

There is no executable failure to reproduce — the finding is an absence.
The evidence is the command surface and the compiler-side exclusion:

- `cli-surface.txt` — full `mncs --help` command list at
  `mncs-language 066897e`: batch routes only (`compile`, `test`,
  `experiment run`, `call`, `observe`, ...). No session verb exists.
- `compiler-exclusion.txt` — `mncs-compiler/src/compiler/kernel.mncs`:
  "No target, filesystem, session, cache, or scheduling inputs are
  relevant."

Together with `docs/compiler-boundary.md` (the API the Lab needs) and
`mncs/lab/session.mncs` (the policy already specified in MNCS), this is
the complete grounding: the policy exists and is proven, the machinery it
must drive does not.
