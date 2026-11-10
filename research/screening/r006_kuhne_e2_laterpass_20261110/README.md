# R006 Kühne 2020 — later-pass E2 eligibility re-examination (2026-11-10)

**Refs #6. Noncanonical source-screening audit; not an accepted corpus exclusion.** Base main: `df6b1135b4a363acfc2f66101d8ea83b14b11475`. This is a separate later GPT-6 review after the first provisional full-text pass in `research/screening/r006_fulltext_e2_review_20261110/`; it was **not blinded**, and it is neither a new human screener nor a PDF-hash verification.

## Re-examined source and method

Kühne, Fischer & Zhou (2020), [Frontiers Neurorobotics DOI 10.3389/fnbot.2020.593732](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2020.593732/full), matched to repository source `SRC-REL-KUHNE-2020@1`. The publisher's **Materials and Methods > Design, Audio Stimuli, Voice Rating Measures and Procedure** were consulted in rendered HTML, with direct source-locator text checks. The listed R004 PDF manifestation/hash is **inherited bibliographic metadata**, not reverified local bytes in this pass. No audio or figures were checked.

The article compares voices (IBM Watson synthetic, Sophia humanoid and a human speaker) using interview-derived sentence excerpts. The listening task instructs participants to rate first impressions/voice and speaker properties. These are genuine human voice-perception outcomes and satisfy E1, E3, E4, E5 and E6 at this source-reading scope. But **E2 fails**: G01 requires communication of the technical system's/task's state or a task-action request. A recorded/synthesised speech sample is not automatically a system message.

## Adversarial checks on the E2 distinction

- **Apparent imperative:** the interview-derived social-media invitation sounds like a request, but is presented to participants as a decontextualized clip to rate, not an instruction from an operational interface.
- **Apparent system description:** a robot-persona line about helping and not tiring is not information about a currently monitored machine condition. Its truth was not established or tested.
- **Manipulated synthetic voice:** technological generation and between-voice comparison meet the audio-property component of E3 but do not independently establish G01/E2.

Result: the later pass **corroborates the provisional full-text exclusion `E-NOT-MACHINE-MESSAGE`**, not exclusion on listener preference, affect direction or significance. Preserve this source in Track G as voice-humanlikeness/attributed-affect context. This is a reinterpretation of task semantics, **not** an empirical finding about superior voices or a new primary sample.

## Verification, limits and registration route

`RECHECK.json` records exact locator-level observations, three potential counterexamples, the frozen date cut-off, source/revision pins, model-assisted provenance, earlier evidence and zero admission counters. This later pass occurs after the source was considered in the accepted first/full-text R006 files; the previous decision was visible and the model class is the same. Thus it supports the protocol §6.2 **separate later re-examination process**, but cannot be called blinded, independent human adjudication or a canonical screening record.

**Current canonical additions: SCR 0; STUDY 0; SAMPLE 0; selected studies 0.** No R005 search records, R004 source data, shared state manifest or generated exports were edited. The formal R006 gate stays open.

The Integration Shepherd should source-review the E2 decision and actor history; after serialized first-stage registration from the existing four-candidate bridge, add a correctly ordered source-pinned full-text exclusion if it agrees and register this recheck honestly as later single-agent verification. Never replace an earlier decision with a newly invented historical timestamp. A new source revision, contradictory stimulus context or discovered task instruction reopens this classification. R006 still needs full corpus reconciliation, unretrieved text, verification sampling and source-family/sample adjudication; R007–R009 have no selected corpus from this tranche.

**No independent human review, participant work or numerical extraction.** Source consulted: publisher HTML selected sections, 2026-11-10T05:32:44.143Z; original PDF bytes not collected. Negative tests in `tests/test_r006_kuhne_e2_laterpass.py` protect against false E2 promotion, sample counting, reviewer spoofing, source changes and claims that this registered a complete corpus.
