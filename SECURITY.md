# Security

`mncs-lab` executes dynamically compiled code and therefore crosses security boundaries that a batch-only prototype may avoid.

Security-sensitive findings include:

- use-after-free or stale pointers into retired JIT code/data;
- execution of code that no longer satisfies current proof/type assumptions;
- invalidation failures after type/layout redefinition;
- capability escalation across session submissions;
- unsafe FFI/native symbol exposure;
- executable-memory permission mistakes;
- session state leakage between users/processes;
- malformed compiler artifacts causing memory corruption;
- proof/introspection output exposing data outside the current capability boundary.

Do not publish exploitable details before the relevant implementation has been assessed. During the architecture-only phase, record security assumptions directly in RFCs and tests as implementation begins.
