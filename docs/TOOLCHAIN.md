# MNCS toolchain pin

Lab executes real MNCS through the canonical toolchain; it never invents
its own. Three identities (never conflate them):

1. **Source toolchain revision** (compiler+executor source):
   `epi13/mncs-language`
   `066897e97a8499a25ea33611d47cc7a4fcdc2b48`
   (full immutable SHA — all Lab kernel corpora PASS on the wasm and
   bytecode backends with this revision; EXP-002 additionally covers the
   Cranelift adapter).
2. **Executor release:** `toolchain/mncs-executor-066897e`
   (`mncs-executor-linux-x86_64`), published from `mncs-harness`. Lab
   consumes the family's pinned distribution instead of publishing a
   second executor binary.
3. **Executor digest:**
   `sha256:4387bae352b68020a83edbbb312794522a76c9f618cc7548a8f68384c63ecb40`
   (release bytes; verified before use by
   `scripts/fetch_mncs_executor.py`).

## Executor resolution order

1. `MNCS_EXECUTOR` environment variable (explicit file path).
2. `mncs-executor` found on `PATH`.
3. A sibling `mncs-language` checkout build
   (`../mncs-language/target/{release,debug}/mncs`, developers only).
4. Otherwise fail closed pointing at `scripts/fetch_mncs_executor.py`.

The runner and the check boundary never download anything by themselves.

## Native Test framework resolution

`mncs test` suites resolve `mncs.test.*` through `MNCS_LIBRARY_PATH`,
assembled by `mncs_lab.library_path()`:

1. this repository root (Lab kernels and suites);
2. `../mncs-test/native` (native assertions/suite semantics);
3. `../mncs-language/library` (standard library).

Every test-bearing module must `use mncs.test.suite` (see LAB-PRESS-003);
module names mirror file paths relative to a library root.
