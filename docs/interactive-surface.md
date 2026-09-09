# Interactive Surface

The command surface is experimental. These classes exist to guide pressure tests, not to freeze syntax.

## Language submissions

- expressions;
- declarations/definitions;
- multiline constructs;
- imports/module references;
- eventually async/concurrent and system-facing constructs.

## Introspection

Candidate commands:

```text
:type <subject>
:proof <subject>
:ir <subject>
:ir-opt <subject>
:asm <subject>
:deps <subject>
:history <subject>
:timing <subject>
```

## Execution tooling

Candidate commands:

```text
:bench <expression>
:profile <expression>
:backend cranelift
:reset
:session
:pressure
```

## Structured output

The underlying compiler/lab interfaces should prefer structured artifacts over scraping human-formatted text. A terminal REPL can render those structures for people; agents, IDEs, tests, and notebooks may consume them differently.
