# R006 / R004 empirical cross-lane: title–abstract screening tranche

Refs [#6](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/6) and the [R004 handoff](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/6#issuecomment-6151733443). Authority: [frozen E1–E6](../../protocol/PROTOCOL-v1.md#4-track-e-eligibility), [screening procedure](../../protocol/PROTOCOL-v1.md#62-screening-procedure), [research integrity](../../../docs/RESEARCH_INTEGRITY.md), and [live registry](../../registry/README.md).

## Scope and result

On 10 November 2026, one GPT-6 agent conducted a bounded first-pass title/abstract assessment of four already verified R004 publications surfaced for Track E. [DECISIONS.json](DECISIONS.json) contains source pins, explicit E1–E6 assessments, exact consulted abstract locations, reasons and access limits.

| Existing source / publication | First-stage decision | Main question |
|---|---|---|
| SRC-REL-BECKER-2025 — Becker et al. (2025) | **include for full-text assessment** | Robot's actionable spoken advice, natural vs mechanical voice, human advice-taking and response time; distinguish pre-study from main experiment |
| SRC-REL-ROMEO-2025 — Romeo et al. (2025) | **include for full-text assessment** | Robot voice and repair strategy in a collaborative maze task, with reported trust outcomes |
| SRC-REL-KUHNE-2020 — Kühne et al. (2020) | **uncertain; inspect full text** | Are isolated voice-rating clips actual machine-generated system messages under G01/E2? |
| SRC-REL-ROMEO-2023 — Romeo et al. (2023) | **uncertain; inspect full text** | Are video-presented robot voices actual system messages under G01/E2? |

Four title/abstract decisions: **two include, two uncertain, zero exclude**. No full-text decisions, empirical corpus inclusions, study/experiment/sample records or quantitative outcomes. These are four publications, not four independent studies. A decision of include at title/abstract means *proceed to full-text assessment*, not included in the final corpus.

## Consulted abstracts and provenance

The source IDs, titles and DOIs were checked against the accepted R004 source revision 1. The agent consulted only the **abstract sections** below for this pass; pages containing a full article were not fully read or hashed.

| Source | Actually consulted | R004 source access at base |
|---|---|---|
| Becker 2025 | [University of Surrey research portal](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Influence-of-Robots-Voice-Naturalness-on/991115568402346), Abstract; corroborating [ACM DOI](https://doi.org/10.1145/3706066) | abstract only; earlier ACM PDF refused |
| Romeo 2025 | [University of Manchester](https://research.manchester.ac.uk/en/publications/the-effect-of-voice-and-repair-strategy-on-trust-formation-and-re/), Abstract | abstract only; earlier ACM PDF refused |
| Kühne 2020 | [Frontiers original article](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2020.593732/full), Abstract | full text available; prior PDF hash not rechecked here |
| Romeo 2023 | [Heriot-Watt Research Portal](https://researchportal.hw.ac.uk/en/publications/putting-robots-in-context-challenging-the-influence-of-voice-and-/), Abstract | metadata only in R004; a public institutional abstract was newly consulted |

Romeo 2023's institutional page reports publication on 13 November 2023, while the R004 source uses the conference's 28 August 2023 start. This is a dated metadata discrepancy, not grounds to silently rewrite historical source records. All four works precede the 4 October 2026 frozen cutoff.

### Study/publication separation

Romeo 2023 and Romeo 2025 have **different verified DOIs and are distinct publications**. Their authors overlap, but their described tasks differ (video-based context/trust versus robot maze and repair). This does **not** establish independent participants or a shared study. Their study/sample overlap is recorded as **unknown pending full-report comparison**. Becker 2025 describes a pre-study and a main study, likewise not counted as two independent evidence units without methods/source appraisal.

## Registration and integration boundary

The decision JSON is a **noncanonical research handoff**, not an admitted mhac-records/1 screening record. The accepted research/registry/state.json does not register research/screening as a record root. The Integration & Research QA Shepherd owns that shared state and generated evidence views, so this branch does not change them. Its four decisions must not be counted in generated screening, study or corpus totals until reviewed, converted into source-pinned SCR records, registered and verified.

An integrator should source-review the specific G01/E2 uncertainty calls and the abstract evidence. Once accepted, use a coordinated screening record root; preserve first-stage decisions as title_abstract only, record the actual registration actor/time and reviewer status, and regenerate shared outputs in a serialized, tested integration. Never create a full-text decision from these abstract-only readings. Do not invent hashed PDF access, duplicate-independent human screening, study counts, or evidence-supported effect sizes.

After promotion: obtain lawful full methods/results for Becker and both Romeo publications; inspect Kühne's voice stimulus task; independently resolve pairwise study/sample identity; process remaining cross-lane R004 occurrence handoffs with R005 without rewriting its discovery history. The protocol's separate intra-agent title/abstract exclusion recheck will become relevant once exclusions exist.

## Verification and checkpoint

Specialized tests: python -m unittest tests.test_r006_r004_crosslane_screening -v

Full validation: python -m unittest discover -s tests -v; python tools/validate.py; python -m tools.build_record_fixtures --check

The tests reject source/DOI drift, unsupported decisive outcomes, invented full-text/study counts and unwarranted publication collapse. They do not establish scientific validity.

- Base accepted main: aae6776f73664d54d53371b9e5cf963a6a9f4ba8 (PR #86); recheck current head before merging.
- Branch: mhac-r006/crosslane-ta-screening-20261110.
- Current limits: one agent, source-published abstracts, no second screening pass or human adjudication; R005 and R006 remain open.
- Human action currently required: none. Lawful unavailable full texts may need a precise source-access gate later.
- **Disposition: Refs #6, partial only. Do not close #6 or claim #7–#9 dependency-ready.**
