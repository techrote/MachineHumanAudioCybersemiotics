# R006 — G01/E2 full-text eligibility review (10 November 2026)

Refs [#6](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/6). This is a **separate, provisional second-stage research handoff**, building on [the admitted first-pass four-publication handoff](../r006_r004_crosslane_20261110/README.md); it is **not** a canonical `SCR` record, selected corpus, validated numerical extraction or second independent screening.

## Purpose and decision surface

Protocol v1 §4 requires all E1–E6. The G01 message definition requires **technical-system or task state information or an action request**. Merely manipulating recorded/artificial voices in a listening study does not establish this. In contrast, a wizarded robot that actually issues navigational recommendations can qualify as a machine-to-human message because the presented utterance is from the task system; wizarding is a study design/appraisal issue rather than an automatic audio-message exclusion.

| Source (accepted R004 identity) | Proposed full-text disposition | Evidence boundary |
|---|---|---|
| **Kühne et al. 2020**, `SRC-REL-KUHNE-2020@1` | **Exclude provisionally**, E-NOT-MACHINE-MESSAGE | Publisher HTML Methods: 15 interview-derived audio clips in a first-impressions voice/speaker-rating survey, not an operational system-state or requested-action message. This needs a later, separately recorded exclusion verification pass under protocol §6.2. |
| **Romeo et al. 2025**, `SRC-REL-ROMEO-2025@1` | **Include provisionally** | Publisher-version institutional PDF text §§2.1–2.4 supports a robot message in a maze task, two voice conditions, three repair strategies and task/trust outcomes. The web reader did not yield source PDF bytes or page-image checking. |
| **Becker et al. 2025**, `SRC-REL-BECKER-2025@1` | **Await full report** | ACM indexed excerpt and institutional abstract distinguish voice-selection and robot-advice experiments, but DOI full-text access returned HTTP 403. Indexed excerpts are not a complete PDF or full-text screening. |

The [structured ledger](DECISIONS.json) gives the six-rule assessments, exact article/section locators, tested access routes, source-revision pins, agent identity, uncertainty and next actions. Do not interpret `include` as evidence of an accepted independent empirical study or meta-analytic effect.

## Primary material actually consulted

- [Kühne, Fischer and Zhou (2020), Frontiers full HTML](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2020.593732/full): **Materials and Methods → Participants, Design, Audio Stimuli, Procedure**, plus Abstract and portions of Results. Online survey sample described as 95 adults. Stimuli are selections from robot interviews in Watson, Sophia and human voice forms; voice attributes are rated independently of a live system/task communication loop. No PDF bytes or original publisher PDF hash were checked in this run.
- [Romeo et al. (2025), institutional publisher-version PDF](https://researchportal.hw.ac.uk/files/147098646/3711938.pdf): web-reader **text** from paper §§1.4, 2.1–2.4 and 3, in the article's printed 33:5 onward pagination. Pilot: 50 Prolific online video raters. Main maze experiment: 60 participants, six between-person voice×repair conditions, spoken junction instructions and recommendations, logged choice and trust outcomes. **No PDF bytes retained/hashed and attempted page-image screenshot refused HTTP 403.** Therefore no exact figure/table transcriptions, numeric data extraction or formal appraisal is authorized from this pass.
- [Becker et al. (2025), ACM article DOI](https://doi.org/10.1145/3706066) and [Surrey institutional abstract](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Influence-of-Robots-Voice-Naturalness-on/991115568402346): DOI page refused HTTP 403 for direct full reading. Search-indexed ACM article text describes a voice-selection pre-study and a robot advice game, but **full-text status remains awaiting verified material**.

Source URLs and access are dated observations. No original full-text PDFs are copied to the public repository. Source identity and previously accepted manifestation metadata were not rewritten or silently upgraded.

## Independent-unit boundary and integration

**One publication is not necessarily one study and two reported experiments are not automatically independent samples.** Romeo 2025's pilot and main trial have differing recruitment routes (Prolific versus campus) and designs, but no participant-linkage verification was completed. Romeo 2023 and 2025 have distinct DOIs; the cross-publication overlap check remains open. Becker's two reported experiments likewise require actual methods and sample provenance. This tranche records **zero canonical study, experiment or sample records, and zero eligible evidence-map inclusions**.

For integration, source-review both provisional decisions; obtain a separately dated later pass for the Kühne exclusion; read and verify full report/bytes for proper numerical extraction; then coordinate with the Integration Shepherd to register a screening record root, append title–abstract precedents and valid full-text `SCR` records, generate aggregates and run graph/CI history validation. No unverified human second screener is implied.

## Verification, risks and handoff

- Specialized: `python -m unittest tests.test_r006_e2_fulltext -v`.
- Repository: `python -m unittest discover -s tests -v`; `python tools/validate.py`; `python -m tools.build_record_fixtures --check`.
- Tests check the provenance, DOI pins, source revision, staged uncertainty, duplicate-independent-sample guard and count drift. They cannot prove the scientific interpretation.
- **Issue #6 remains open**; the paper corpus, exclusion verification, participant identity, #5 coverage and #7–#9 dependencies remain unfulfilled. Frozen cutoff stays **2026-10-04**; no amendment.
- **Scope:** exclusively `research/screening/r006_fulltext_e2_review_20261110/**` plus one issue-specific test file. No common manifest, current registry, R005 records, other branches or generated indexes modified.
- **AI assistance:** GPT-6 single-agent interpretation of public publisher HTML, a web-parsed institutional PDF and publisher abstract/index; no human adjudication, peer review, participant observation or independent model pass. The PDF page-image request failed; this limits confidence but does not turn observed text into unobserved data.

**Checkpoint:** Base `06cad54301d34b699b95b8e8f45bb547bbebf233`. Next: qualify the exact scientific interpretations and second-pass E2 exclusion, seek complete Becker text, cross-check Romeo 2023/2025 participant/method boundaries, and let the integrator register canonical records. No ordinary management action is required from the owner.
