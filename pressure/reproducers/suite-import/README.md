# Reproducer: LAB-PRESS-003 (missing suite import misreported)

Two files differing by exactly one line (`use mncs.test.suite;`):

- `nosuite.mncs` — imports only `mncs.test.assertions`;
- `withsuite.mncs` — additionally imports `mncs.test.suite`.

Place both under a `lab/` directory on `MNCS_LIBRARY_PATH` (module names
mirror the path) and run:

```bash
LIB="<libdir>:/path/to/mncs-test/native:/path/to/mncs-language/library"
MNCS_LIBRARY_PATH="$LIB" mncs test lab/nosuite.mncs --format text
MNCS_LIBRARY_PATH="$LIB" mncs test lab/withsuite.mncs --format text
```

Observed: `nosuite` fails with `native suite initializer did not return
SuiteSummary ... "execution target module does not match program"`;
`withsuite` reports `native mncs-test: PASS`. The module matches the
program in both cases; only the suite import differs.
