# MHAC-T006 — Action polarity and contrastive guidance (exploratory)

**Refs [#38](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/38).** Bounded formal research prepass. **All 47 scenarios and their expected results are invented**, not participant data, acoustics or safety outcomes. Accepted `main` base: `423649d18c54cbf90bf7bf79d49ba69b29f03848`, 3 November 2026 UTC.

## Question and scope

Does the operator scope of a truthful negative instruction, factual negative, positive requirement or contrastive correction survive field binding, expiration and version changes? Would context make a complex instruction easier to understand, or merely longer? A symbolic truth oracle can falsify **logical mismatches** only; it cannot adjudicate the second question. This package is not an adopted message grammar or voice engine.

## Reproducible artifacts

- [SOURCES.md](SOURCES.md): identities, exact publisher/abstract locators, uncertainty, access and contradictory evidence for S58–S62.
- [OPERATORS.md](OPERATORS.md): typed truth model, operator grammar, non-equivalence, unknown and all-clear guards.
- [SCENARIOS.json](SCENARIOS.json): 47 explicitly fictional positive and negative test cases, with authored expectations.
- [oracle.py](oracle.py) and [test_oracle.py](test_oracle.py): deterministic standard-library checker and regression tests; [adapter](../../../tests/test_action_polarity_t006.py) supports CI discovery.
- [COMPARATORS.md](COMPARATORS.md): direct, negated, contrastive, factual and accessible alternative policies.
- [PROTOCOL-SKETCH.md](PROTOCOL-SKETCH.md): unregistered, unexecuted prospective human comparison.
- [DECISION-MEMO.md](DECISION-MEMO.md): bounded decisions for positive, null, adverse and inconclusive evidence.

Run from root using Python 3.11+:

```sh
python -m unittest discover -s research/tangents/action-polarity -p test_oracle.py -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

A test status of `accept` means that an invented text proposition is consistent with invented authoritative truth. The fixture count is **not an empirical denominator**. No acoustic cues or real commands are generated.

## Research boundaries and disclosure

Track E search cutoff is frozen at **2026-10-04**, and protocol v1 internally frozen 2026-10-13. R005/R006 alone own formal inclusion and report/sample identity. R008/R011 own theory, R012 state model, R013 hypotheses and R014 experiment preparation. Separate issues #30/#31/#33/#34/#36 retain masking, uncertainty, repair, composition and persistent-state ownership. #19/#20 remain genuinely human-gated. No live registry, selected corpus, frozen method, real participant or production system is modified.

**AI provenance:** one GPT-6 agent, connected GitHub and public primary PubMed/Oxford/Springer/Frontiers webpages accessed 2026-11-03 UTC. Abstract or stated selected publisher-HTML sections were checked; no independent human review, exhaustive licensed reading, ethics approval or empirical validation.
