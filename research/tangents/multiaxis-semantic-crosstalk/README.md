# MHAC-T009 — multiaxis acoustic-semantic crosstalk (synthetic prepass)

**Refs [issue #45](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/45).** Isolated exploratory counterexample package. No accepted empirical claim, production sound grammar or listener data.

- [SOURCES.md](SOURCES.md): seven source identities, extent, positive/negative reports, R005/R006 non-adoption.
- [TRUTH-FIELDS.md](TRUTH-FIELDS.md) and [CASES.json](CASES.json): 27 crossed fictional truth tuples plus 3 unknowns with action/addressee controls.
- [MAPPINGS.json](MAPPINGS.json) and [COMPARATORS.md](COMPARATORS.md): one fused scalar, naïve independent descriptors, candidate independent descriptors and serial field policy.
- [analyze.py](analyze.py), [RESULTS.md](RESULTS.md) and [tests/test_t009_multiaxis.py](../../../tests/test_t009_multiaxis.py): deterministic exact-collision oracle, polarity checks, negative tests and reported outcomes.
- [PROTOCOL-SKETCH.md](PROTOCOL-SKETCH.md) and [DECISION.md](DECISION.md): proposed separate human semantic/action endpoints and conditional negative/null/positive outcomes.

Reproduce from repository root:

\`\`\`sh
python research/tangents/multiaxis-semantic-crosstalk/analyze.py
python -m unittest discover -s tests -p 'test_t009_multiaxis.py' -v
python -m unittest discover -s tests
python -m tools.validate
\`\`\`

Only the first two commands were locally rehearsed before publication. GitHub CI controls the full repository set. The exact model counts are specification-dependent; these should **not** be converted into perception, confusion, action, training, safety, or accessibility metrics.

Research is bounded by frozen MHAC protocol v1 and [evidence integrity](../../../docs/RESEARCH_INTEGRITY.md). Future human listening is separately gated by #20. Source scouting is not selected Track E evidence; [R005/R006](../../../research/sources/auditory/README.md) retain screening and identity authority.
