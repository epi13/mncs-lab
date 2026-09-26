# Experiments

Bounded investigations with typed definitions and digest-pinned records.
Read `docs/experiment-model.md` before adding one.

- `definitions/LAB-EXP-*.json` — question, hypothesis, revision-pinned
  subjects, variant codes, controls, evaluation rule. Refuses to run when
  the checkout differs from the pin.
- `records/LAB-EXP-*.json` — observations, integrity/standing witnesses,
  agreement analysis, tally, standing, conclusion, pressure links.
  Content digest covers everything except itself.
- `records/LAB-EXP-*.store.json` — Store publication sidecars (linkage
  only; record bytes are never mutated by publication).

Query with `scripts/lab_query.py` instead of grepping. Compact derived
evidence lives under `evidence/<EXP-ID>/`; full toolchain outputs stay in
tempdirs (reproducible by rerunning the definition).
