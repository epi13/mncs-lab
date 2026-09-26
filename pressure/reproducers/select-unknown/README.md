# Reproducer: LAB-PRESS-002 (`select` poisons `experiment run`)

Two kernels with identical semantics over identical corpus shapes:

- `select_kernel.mncs` + `select-corpus.json` — one `select(flag, 1, 0)`;
- `branch_kernel.mncs` + `branch-corpus.json` — the same choice as a
  plain `if` branch.

Run (from this directory, `mncs` = pinned Lab toolchain):

```bash
mncs experiment run select_kernel.mncs --backend mncs-portable-wasm-mvp \
  --corpus select-corpus.json --output-dir /tmp/repro-select
mncs experiment run branch_kernel.mncs --backend mncs-portable-wasm-mvp \
  --corpus branch-corpus.json --output-dir /tmp/repro-branch
```

Observed at `mncs-language 066897e`:

- select variant: both cases execute and meet expectations, suite status
  `UNKNOWN`, `unresolved_reasons:
  ["compilation retained required unresolved obligations"]`, with
  `mncs:0.2:obligation:body:machine-intent:*` entries (frontend
  `realization-branchless` requirement, one per `select`).
- branch variant: suite status `PASS`, no unresolved obligations.

Nothing about the modules differs except the choice idiom. The toolchain
names neither `select` nor branchlessness anywhere in the failure output.
