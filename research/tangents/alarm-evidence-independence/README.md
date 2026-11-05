# MHAC-T015 — Alarm evidence independence (exploratory)

**Issue:** [#58](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/58) · **Base:** [accepted `main` 423649d1](https://github.com/techrote/MachineHumanAudioCybersemiotics/commit/423649d18c54cbf90bf7bf79d49ba69b29f03848) · **Classification:** fictional source/evidence-dependence falsifier, **not** Track E/G evidence.

## Stage 0 — conditional GO, not an adopted interface

The accepted [R012 issue #12](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/12) requires multiple sources, conflicting estimates, interruption and message lifecycle, but remains dependent on the uncompleted synthesis. [R013 #13](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/13) contemplates message prioritisation, source attribution and fallback but does **not** authorize a particular audio policy. There is **no production multi-alarm deployment contract**.

One bounded fictional printer/workshop application is nonetheless defensible: a pressure limit sensor is relayed through two separately audible annunciators while a genuinely independent overheat signal also requires an action. Another is one source reporting two urgent tasks. Under either scenario a recipient, scheduler or future message-policy experiment could mistake audible plurality for independent evidence, or suppress an independent obligation. Whether listeners actually do so is unknown.

Ownership/dedup checked on 2026-11-05 UTC:

| Existing work | Actual boundary | Missing here |
|---|---|---|
| [#30 / PR #32](../../../../../../issues/30) | Masking, recognition and timely-action failure taxonomy | Common upstream observation versus distinct observation |
| [#31 / PR #40](../../../../../../issues/31) | Alert validity and decision criteria | Cross-alert common-cause dependence |
| [#34 / PR #37](../../../../../../issues/34) | Within-message source/event grammar | Cross-message observation lineage |
| [#36 / PR #53](../../../../../../issues/36) | Continuous state, events and recovery | False corroboration and duplicate suppression |
| [#41 / PR #42](../../../../../../issues/41), [#45 / PR #46](../../../../../../issues/45) | Received waveform and multiaxis cue discrimination | Perceptual distinguishability does not imply evidence independence |
| [#43 / PR #44](../../../../../../issues/43) | Actor/addressee authority | Two independent alert obligations under one audible source |

All seven associated PR scopes were inspected by the connected GitHub interface. None implements the paired **same-upstream-versus-verified-independent** oracle and **false-corroboration-versus-omitted-obligation** comparison. [PR #57](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/57) is a separate, existing instruction-retraction falsifier and is not modified. Thus **limited GO** for fictional research only. If subsequent source review shows these conditions already covered, this package should be rejected as duplicate without promoting another design contract.

## Reproduction

From repository root with Python 3.11+:

```sh
python research/tangents/alarm-evidence-independence/oracle.py --check
python -m unittest discover -s tests -p "test_t015_alarm_evidence_independence.py" -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

`--check` verifies the hand-labelled fictional fixture, an independently **programmed but same-agent** JavaScript numerical expectation ledger, and SHA-256 hashes. The normal CI performs the last three commands; run it on the **exact final head** after PR creation. Structural green CI cannot establish study eligibility, real source truth, human perception, hearing accessibility, safety or science acceptance.

## Artifact inventory and boundaries

- [SOURCES.md](SOURCES.md): seven publisher/open-primary source records, opposing results and access limits; these are **not** admitted studies.
- [TRUTH-CONTRACT.md](TRUTH-CONTRACT.md): idealized and explicitly limited inputs, gold labels and key invariants.
- [FICTIONAL-CASES.json](FICTIONAL-CASES.json): **40 pre-authored two-message cases**, 20 explicitly marked negative/control, with separate world/actor/deadline truth and expected obligations.
- [oracle.py](oracle.py): four competing deterministic comparators A/B/C/D, no sound generation or physical action.
- [EXPECTED-METRICS.json](EXPECTED-METRICS.json): separately computed JS shadow arithmetic; **not** independent human validation.
- [COMPARISON.md](COMPARISON.md), [DECISION.md](DECISION.md), [PROTOCOL-SKETCH.md](PROTOCOL-SKETCH.md): transparent trade-offs, counterpositions, hypotheses and R008/R012–R014 handoff.
- [SHA256SUMS](SHA256SUMS) and [repository-discoverable tests](../../../tests/test_t015_alarm_evidence_independence.py) (see exact repository root path `tests/test_t015_alarm_evidence_independence.py`).

**No edits** to frozen protocol, accepted source registry, record schemas, `main`, scout branch, existing issues/PRs, study selection or participants. No synthetic voice persona is assumed; `cue_identity` is a symbolic identifier only. No new safety requirement is asserted. This artifact is an investigation of design **possibility**, not a proof of a listener bias.

**AI provenance:** GPT-6 agent prepared this bounded synthetic comparison and source audit on 2026-11-05, using connected GitHub source/PR retrieval and public publisher/open-text pages. Source verification is not an independent human review; synthetic case labels are authored, not blind human annotations.