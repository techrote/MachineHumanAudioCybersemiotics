# R006 — Romeo 2023/2025: publication, procedure, stimulus and sample boundaries

Refs [#6](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/6). Base `aaffdd541b761f55e701d084717ef49e4e4083ea`, 10 November 2026. Authority: [frozen protocol §4 and §§6.2–6.4](../../../protocol/PROTOCOL-v1.md), existing [R004 title/abstract screening](../../../screening/r006_r004_crosslane_20261110/DECISIONS.json), and [R006 provisional full-text assessment](../../../screening/r006_fulltext_e2_review_20261110/DECISIONS.json).

## Material research distinction

Two independently DOI-identified **publications** describe at least four **candidate experimental procedures**, but neither the four procedures nor their participant counts establish four distinct studies or four independent samples. This source-limited analysis therefore records **zero newly adjudicated independent samples and zero canonical screening records**. See [EVIDENCE.json](EVIDENCE.json) for typed candidate units, exact source routes, local access limitations and still-open questions. A verified article DOI is not a confirmed study or sample identity.

| Source | Procedure supported by consulted material | Reported participants | Identity/admissibility status |
|---|---|---|---|
| Romeo et al., RO-MAN 2023, DOI [10.1109/RO-MAN57019.2023.10309631](https://doi.org/10.1109/RO-MAN57019.2023.10309631) | OS1, general-context video trust survey | **Not verified** | E2 and participant identity unresolved |
| Same 2023 publication | OS2, task-specific corn-maze navigation video; scripts listed by authors in Zenodo supplement | **Not verified** | E2 and participant identity unresolved |
| Romeo et al., ACM THRI 2025, DOI [10.1145/3711938](https://doi.org/10.1145/3711938) | Online six-video repair-selection pilot, Pepper over corn-maze scene, Prolific | **50 reported** | E2 plausible; pilot outcomes not automatically a separate eligible study |
| Same 2025 publication | In-person robot navigation, two voices × three repair strategies, ten participants per condition | **60 reported** | Provisional E2 inclusion from earlier R006; sample independence unadjudicated |

**Potential stimulus—not sample—overlap:** the 2023 authors' [Zenodo description](https://zenodo.org/records/8042317) identifies utterance scripts from OS1 and a corn-maze navigation video from OS2. The 2025 article describes Pepper-over-corn-maze videos in its online pilot (§2.1). Similar subject matter and overlapping authors raise a **specific testable reuse question**. No common recording, script identity or reused participants are established. The 2025 paper also cites the 2023 publication as reference [61], which establishes awareness, not extension, shared study or duplicate data.

The 2025 study's six conditions and multiple navigation decisions are **not six independent samples or independent participants per trial**. The article describes 60 recruited people, with ten people in each between-person arm (§2.2). Its separate 50-person pilot cannot simply be added to 60 to report an accepted R006 sample N=110.

## Actual source inspection and access limitations

- [Heriot-Watt 2023 institutional record](https://researchportal.hw.ac.uk/en/publications/putting-robots-in-context-challenging-the-influence-of-voice-and-/): publication/DOI, abstract describing *two video-based online studies*, and conference details examined. **No 2023 manuscript full text read.**
- [Author-linked Zenodo record 8042317](https://zenodo.org/records/8042317): **description and file listing only**, including the declared OS1/OS2 utterance-script PDF; the attempted web PDF fetch failed and its bytes/contents were **not read or hashed**. A repository-supplied MD5 listing is not our own file verification.
- [2025 institutional publisher-version PDF](https://researchportal.hw.ac.uk/files/147098646/3711938.pdf): web-extracted **selected text** from §§2, 2.1–2.4 (online pilot, in-person task/recruitment/assignment) and the reference list [61]. A rendered-page screenshot request returned HTTP 403. **No PDF bytes retained, no local SHA-256, no verified tables/figures or numerical outcome extraction.** Reported participant figures are source descriptions, not an empirical extraction.
- Existing accepted R004 source pins: `SRC-REL-ROMEO-2023@1` (verified DOI, metadata only in original record) and `SRC-REL-ROMEO-2025@1` (verified DOI, abstract-only in original record). This tranche does **not** mutate those historical source/access records.

The 2023 university record's 13 November 2023 publication date differs from R004's 28 August 2023 conference-start date; this is a metadata distinction, not permission to replace historical source revisions. All materials predate the frozen **4 October 2026** cut-off. No source, human reviewer, participant, eligibility or copyright permission is invented.

## Reproducibility and explicit negative controls

`python research/registry/identity/romeo_pair_20261110/validate.py` reads the accepted R004 source files and the new JSON and checks pinned DOI identities, unchanged source revisions, observed reading limits, four candidate procedures, **no claims of independent participants or study counts**, and absence of canonical admission. A newer/corrected source revision fails closed until re-reviewed.

`python -m unittest tests.test_r006_romeo_pair_20261110 -v` tests source collision, unsupported sample/stimulus independence, improper abstract-to-full-text promotion, invented human review, conference-to-journal merging, source-correction invalidation and noncanonical count inflation. Altered records in those tests are **deliberately synthetic in-memory negatives**, not live evidence.

No research manifest, generated view, R005 occurrence, R004 source, source byte or outside lane is edited. Structural CI cannot establish research validity. No second human screening or source-file hash audit took place.

## Next adjudication and downstream handoff

**Highest-value next evidence:** read the lawful 2023 main text and author-deposited OS1/OS2 scripts, and directly compare the 2023 OS2 corn-maze prompts/recordings with the 2025 pilot stimuli. Then check source-specific recruitment, collection dates, explicit overlap and eligibility of each procedure (especially whether OS1/OS2 satisfy G01/E2). Only afterward determine whether there are distinct studies, shared materials or participant samples. If no participant overlap evidence exists, preserve `unknown`; do not manufacture an independence relationship.

The Integration Shepherd owns canonical TA/full-text SCR admission, updated source manifestations, common manifest/index refresh, downstream count reconciliation and guarded merges. This tranche does **not** change the earlier four first-pass decisions, register a source, create a STUDY/SAMPLE, select a #7–#9 corpus or close #6. R005 #5's coverage gap also remains open. Human action currently required: **none**; lawful access shortfall is recorded for subsequent retrieval.
