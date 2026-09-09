# RFC 0006 — Language and Compiler Pressure Methodology

- **Status:** Initial
- **Depends on:** RFC 0001

## Problem

A pressure-testing repository can accidentally hide the most valuable result: evidence that the language/compiler cannot yet express or support a required workload. Host-language workarounds and ad hoc glue can make a prototype look successful while preventing the deficiency from being fixed at its proper layer.

## Decision

Maintain a grounded pressure registry under `pressure/` and distinguish language, compiler, and tooling ownership.

## Pressure classes

### Language pressure

The language/runtime/stdlib cannot express the needed behavior safely, efficiently, deterministically, or ergonomically.

### Compiler pressure

The language may be expressive enough, but the compiler lacks a required API, incremental behavior, proof query, dependency model, JIT capability, diagnostic distinction, artifact identity, or acceptable performance characteristic.

### Tooling pressure

The deficiency lies in harnesses, packaging, environment control, observability, or developer workflow rather than language semantics/compiler capability.

## Grounding requirements

A registry entry requires:

1. a real attempted workload;
2. observed behavior;
3. a minimal reproducer or exact experimental sequence;
4. expected semantics/capability;
5. impact assessment;
6. evidence;
7. likely owner or an explicit unresolved classification.

Speculative future difficulty is not a confirmed pressure entry.

## Severity guidance

- **blocker** — prevents a sound implementation of the targeted experiment;
- **major** — forces substantial semantic compromise, unsafe behavior, or dominant performance cost;
- **moderate** — meaningful workaround or ergonomic/performance burden;
- **minor** — localized friction with low correctness/performance impact.

## Workaround rule

A workaround must be visible and temporary. If host code substitutes for missing MNCS/compiler behavior, the relevant pressure entry must explain the substitution and what would allow its removal.

## Promotion workflow

```text
attempted workload
      ↓
grounded pressure entry + reproducer
      ↓
proposed language/compiler solution
      ↓
implementation in owning repository
      ↓
re-run original reproducer/workload
      ↓
verified resolution
      ↓
remove or shrink workaround in mncs-lab
```

Where the MNCS ecosystem uses broader multi-agent validation/promotion mechanisms, this repository should provide clean evidence suitable for that process rather than inventing a competing promotion system.
