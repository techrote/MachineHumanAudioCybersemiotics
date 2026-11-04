# MHAC-T005 — Continuous state × discrete event falsification

**Status:** exploratory, synthetic-only issue #36 prepass. No accepted Track E/G evidence, acoustic efficacy claim, production audio requirement, clinical safety claim or participant result. Prepared on 2026-11-04 by an AI research/engineering agent. The original trace/oracle seed was committed on 2026-11-03; this package completes its bounded issue handoff.

## Question and stop condition

Can a persistent auditory state display coexist with a separate time-critical event without causing incorrect interpretations of sound cessation or falsely reporting source recovery? The opposite outcome is admissible: a simple discrete warning with an inspectable visual state could be sufficient or preferable. **The code cannot answer auditory detectability, masking, comprehension or operator performance.** Stop before physical acoustic implementation or human testing until R012–R014 are actually ready and R020 is authorized.

## Contents and exact reproduction

- [SOURCES.md](SOURCES.md): study/report provenance, counterevidence, read/access limitations, and non-admission.
- [POLICIES.md](POLICIES.md): four candidate delivery policies, independent truth variables, case ledger and structural comparisons.
- [STATE-TRACES.json](STATE-TRACES.json): 25 invented cases with explicitly authored expected source truth, event due-ness and all-clear permissibility, not observed data.
- [replay.py](replay.py): deterministic Python 3.11+ symbolic oracle.
- [PROTOCOL-SKETCH.md](PROTOCOL-SKETCH.md): prospective experimental comparison, covariates, failure definitions, decision rules and gates.
- [DECISION-MEMO.md](DECISION-MEMO.md): conditional dispositions, implementation limits and lane ownership.
- [tests/test_continuous_state_events_t005.py](../../../tests/test_continuous_state_events_t005.py) and [tests/test_continuous_state_events_hardening.py](../../../tests/test_continuous_state_events_hardening.py): isolated regression and negative controls.

From repository root (stdlib only):

```sh
python research/tangents/continuous-state-events/replay.py
python -m unittest discover -s tests -p 'test_continuous_state_events*.py' -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

Existing replay prints PASS only for the encoded **logical fixtures**. Passing it cannot certify listening, independence of labels, event priority, real-world timestamps, hearing accessibility, or human action. Verify exact-head CI separately.

## Scope and related work

Uses a persistent-state × separate-event *policy interaction*, rather than duplicating #30 (masking/attention and warning failure), #33 (recipient repair), #34 (message composition), #41 (received cue separability), #47 (notification deadlines) or #49 (mode-dependent action permissions). Candidate *future* handoffs only: R008 comparisons, R009 appraisals after R005/R006 screening, R012 state semantics, R013 sound-policy hypotheses, R014 experiment design and R017 adversarial audit. The frozen 2026-10-04 Track E search cutoff and accepted schemas remain unchanged.

## Model restrictions

States are fictional and snapshots are supplied by an assumed authoritative source. The evaluator makes **no sound waveform, audibility, masking, attention, detection, latency, memory or physical-response model**. Both visual status and event visual presentation are idealized available channels. All four policies share the same event issuance rule, so their symbolic event-audio counts cannot demonstrate superiority or noninferiority. `ducked` is a declared playback input state and is not evidence about true acoustic energy.

The current fixture oracle additionally assumes source and event version integers belong to a jointly ordered synthetic revision domain in its `source.version >= event.version` guard. Real MHAC implementations may use independent version domains: **do not reuse that comparison without an explicit causal mapping and separate validation**. An independent-clock/sequence experiment is a potential failure of the current model, not a supported production policy. A conservative false-clear rejection here does not prove that every valid recovery is announced.

The first tranche of #36 is a **bounded prepass**, not complete human research; any synthetic invariants should be reviewed before integration. No files in the frozen protocol or live research registry are changed.
