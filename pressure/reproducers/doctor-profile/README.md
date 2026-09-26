# Reproducer: LAB-PRESS-004 (Doctor profile registry lags 0.18)

`mncs-doctor doctor` reports `DOC102 unknown profile 0.18` on every
0.18 source file, failing `header-health`, `version-drift`, and
`migration-availability` — including on `mncs-test`'s own canonical
self-suite, which the real toolchain executes with PASS.

- `mncs-lab.txt` — 10 files, all DOC102 (this repo: kernels, suites,
  reproducers).
- `mncs-test.txt` — 17 files incl. `tests/self_suite.mncs`, all DOC102.
- `mncs-harness.txt` — 15 files at profile 0.16: header-health PASS
  (control: Doctor knows 0.16, not 0.18).

The compiler at `mncs-language 066897e` compiles, tests, and executes
0.18 (with language-owned `test` declarations since 0.17) without
objection. The skew is Doctor-side: its profile registry predates the
profiles the family already canonicalized. Downgrading Lab sources to
0.16 would forfeit `test` declarations — the wrong direction.
