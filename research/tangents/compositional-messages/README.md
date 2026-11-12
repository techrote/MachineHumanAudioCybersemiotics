# MHAC-T004 — Held-out compositional messages: exploratory prepass

**Refs [#34](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/34).** Issue-scoped candidate protocol, not an adopted design contract. Initial accepted `main` base: `423649d18c54cbf90bf7bf79d49ba69b29f03848` (2026-11-03). This subtree is deliberately separate from R005/R006 formal source/identity records and R012–R014 accepted outputs.

## Precise question

Can an auditory interface represent a previously untrained, *legal* `source × event` combination without inducing listener field misbinding, incorrect action or intolerable attention/deadline cost? A syntactically composable code is not evidence that any person can hear or comprehend it.

**Three different problems:** within-message source/event composition; independent concurrent alarms (#30); perceived interpretation and timely action (#13/#14). The fictional model checks only the first problem's **labelled symbol consistency** and event-ID/version safeguards. It cannot model hearing, acoustic masking, auditory scene segregation, semantics, user behaviour, latency or safety.

## Artifacts and rerun

- [SOURCE-IDENTITIES.md](SOURCE-IDENTITIES.md): provenance, access/read extent, contradictory observations and report identity concerns.
- [ABSTRACT-GRAMMAR.md](ABSTRACT-GRAMMAR.md): fictional codebook, constraints, field binding, held-out sets and negative cases.
- [COMPARATORS.md](COMPARATORS.md): four mechanisms without manufactured human scores.
- [PROTOCOL-SKETCH.md](PROTOCOL-SKETCH.md): future **unexecuted**, human-gated comparative design.
- [DECISION-MEMO.md](DECISION-MEMO.md): negative/null/positive decision logic and handoffs.
- [SYNTHETIC-CASES.json](SYNTHETIC-CASES.json): 24 explicitly invented scenarios.
- [protocol.py](protocol.py), [test_protocol.py](test_protocol.py): standard-library deterministic oracle/negative tests.
- [repository test adapter](../../../tests/test_compositional_messages_t004.py): integrates with ordinary test discovery.

Commands from the repository root:

```sh
python -m unittest discover -s research/tangents/compositional-messages -p test_protocol.py -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

Local isolated tests are a **synthetic code check**, not participant evidence. CI results must be checked on the exact proposed PR head, and the full-repository validation is not claimed to have run locally in an unavailable checkout.

## Programme/protocol boundary

The frozen empirical search cutoff is **2026-10-04**. This 2026-11-03 public-web primary-source check is exploratory source identification and **does not retrospectively update or complete Track E**. R005 owns retrieval; R006 owns publication/study/sample mapping and screening; R008/R011 own theory comparison; R012–R014 own accepted semantic, auditory and experimental contracts. No evidence record has been added to the live manifest. All token mappings and grammar restrictions are provisional conventions; there is no claim that Brier endorses this grammar, or that deliberately non-human sound is affect-neutral. R020 alone authorizes actual participant work after genuine human gates.

**AI/work disclosure:** single GPT-6 agent; connected GitHub, public Glasgow repository and PubMed metadata/abstracts on 2026-11-03; no independent human review, full-text study appraisal, recruitment or experiment.
