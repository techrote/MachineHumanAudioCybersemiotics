# R006 — Becker (2025) phase-resolved E2 eligibility check

**Status:** source-limited, noncanonical, AI-assisted review, 10 November 2026. **Refs #6.** This is not a second human screen, a full-item reading claim, a numerical extraction or an accepted publication/study/sample record. Frozen search cutoff: **4 October 2026**.

## Material and version

Becker et al., *Influence of Robots' Voice Naturalness on Trust and Compliance*, *ACM Transactions on Human-Robot Interaction* **14(2), Article 29 (2025)**, DOI [10.1145/3706066](https://doi.org/10.1145/3706066), retained as `SRC-REL-BECKER-2025@1`. The accepted R004 source has a verified DOI and an **abstract-only** access declaration; that old historical access record was not rewritten.

The author-hosted [published PDF](https://www2.informatik.uni-hamburg.de/wtm/publications/2025/BBCKOAGSFW25/3706066.pdf) was consulted via web-extracted PDF text from the abstract, §§3.1–3.7 and Appendices C–E. Printed pages **29:8 and 29:24** were inspected visually in the PDF rendering, including the participant statement and Appendix E's speech examples. Text and images for other sections were not exhaustively reviewed. Original PDF bytes/SHA-256 were **not locally acquired or verified**; audio stimuli were not heard. The source's printed first page declares CC BY 4.0. Exact current Git blob for the existing source registry file is pinned in `RECHECK.json`; that is **not** a PDF hash.

This complements R005 [Draft PR #106](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/106), which establishes lawful publication access and reports phase sizes. This R006 check instead independently applies frozen protocol **E1–E6** at the *procedure* level. It does not incorporate, edit or pre-empt #106's branch.

## Eligibility distinction

| Procedure in one publication | E2 / G01 machine-message question | Bounded disposition |
|---|---|---|
| Online six-voice pre-study, 60 analysed | Samples rated for voice characteristics and prospective suitability, not received as actionable operational system messages (§3.2, printed 29:5) | **Provisional E2 no** for a standalone Track E experiment; included as methodological context |
| Eight-person setup pilot | Robot speech and game comprehension reported, but comparative design, complete outcomes and participant overlap insufficient (§3.4, printed 29:8) | **Uncertain**; never count as an independent study/sample |
| In-person robot-assisted Battleship, 68 analysed | Spoken live status, advice, repair and task instructions; two randomized voice arms, same utterance and gesture/expression repertoire (§§3.1, 3.3–3.7; Appendix E) | **Provisional E1–E6 yes** for the main procedure, conditioned on source-review and registration |

This matters because an article's **publication-level title/abstract include** to full-text assessment does not imply that all of its constituent procedures satisfy E2. The pre-study's voice suitability results cannot be silently pooled as if they are task-action responses. Likewise, no claim that the main task is an isolated voice-only causal manipulation is warranted: the interaction includes visual display, gestures, facial expressions and expressive speech, even where the two groups share the same nonvoice repertoire.

**Participant relationship:** §3.7, printed p. 29:8 explicitly says pre-study participants were excluded from main-study recruitment. This is an author-reported **nonoverlap**, not inspection of individual identities. The separate eight-person setup pilot's overlap with either group remains unknown. Nine advice events within one participant are repeated measures, not nine independent people. Analysed `n=60` and `n=68` are author-reported, **not** canonical MHAC SAMPLE counts.

## Admission and falsification gates

`RECHECK.json` records the source pin, access/reading limits, per-phase criteria and disjoint/unknown overlap; `tests/test_r006_becker_phase_e2_20261110.py` has one positive and eleven adverse checks for accidental source drift, DOI substitutions, invented source bytes, human verification, premature screening, E2 promotion and study/sample inflation. These are structural controls, not external scientific validation.

Before any **canonical full-text SCR**: the Integration Shepherd must finish serializing the four already prepared authentic **title/abstract** SCR records on an exact checkout, including shared manifest and deterministic exports, and run graph/history + exact-final-head CI. Then R006 must record a separately dated actual full-text decision with correct actor, evidence/reading extent and source pins. A later-pass exclusion recheck remains required for full-text exclusions. If the author-hosted PDF manifestation is revised or the R004 source record changes, review the findings rather than silently lifting this note into accepted status.

There are **zero canonical SCR/STUDY/EXPERIMENT/SAMPLE admissions in this shard**. Issues #5 and #6 remain scientifically incomplete, and the selected #7–#9 corpus is not ready. A successful Python unit test would only verify that this stated bounded audit did not drift.

**Reproduction on a complete checkout**:

```sh
python -m unittest tests.test_r006_becker_phase_e2_20261110 -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```
