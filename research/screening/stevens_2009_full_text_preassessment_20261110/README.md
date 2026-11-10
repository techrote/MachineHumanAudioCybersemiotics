# R006 — Stevens et al. 2009 original-full-text eligibility preassessment (10 November 2026)

Refs [#6](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/6). **Canonical full-text decision remains `pending`; this document is not a study admission.**

## Original source and actual reading

- **Publication**: Stevens, C. J., Brennan, D., Petocz, A., & Howell, C. (2009), *Designing informative warning signals: Effects of indicator type, modality, and task demand on recognition speed and accuracy*. *Advances in Cognitive Psychology* 5:84–90 (2009-05-04), DOI `10.2478/v10053-008-0064-6`, PMID 20523852, PMCID PMC2865004. Original full-body article at <https://pmc.ncbi.nlm.nih.gov/articles/PMC2865004/>.
- **R006 actual tool-mediated reading**: 2026-11-10, executed by GPT-6 through web.run. Opened primary-source original PMC HTML after finding indexed article. Read introduction/aim/design, complete presented **Method > Participants, Stimuli, Equipment, Procedure**, **Results** including displayed Tables 3–5, **Discussion**, and identifying references. Web-rendered HTML has line ranges 85–118 (intro/aim), 119–123 (participants), 124–157 (stimuli and Tables 1–2), 158–167 (equipment/procedure), 168–217 (results/Tables 3–5), and 218–239 (discussion). These are web intermediary *line locators*, not permanent page or publisher-PDF anchors. Raw web response, HTTP receipt, source-specific SHA, sound files and screenshots were **not** obtained by this R006 agent. This is not a claimed complete paper/HTML manifestation capture.
- **Separate R005 original XML receipt**: R005 integrated PR [#154](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/154), original Europe PMC XML endpoint <https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2865004/fullTextXML>, HTTP 200 at 2026-11-10 20:15:16.864Z and 20:19:06.280Z, each **74,338 bytes**, SHA-256 `1390d7a4def94ad6b0926a5f1ae2608999f31713fb3ee5dad20b9e3fcc52658b`. Those are R005 **ephemeral XML responses**. This R006 reading was via PMC HTML, not the same bytes; do not claim byte equivalence or assign the XML hash to this reading. No durably retained canonical original-text manifestation exists yet.
- **Licence**: PMC article copyright note states Creative Commons Attribution; this is a published source statement, not an R006 permission decision about source storage or audio.
- **Registry**: `SRC-R006-E-STEVENS-INFORMATIVE@1` currently metadata-only, no manifestations; representative original hit `HIT-R005R-C1LOAD-EQ1-02138@2`; `SCR-R006-STEVENS-2009-WARNING-TA@1` includes to full-text assessment. This updates the **existing** `SCR-R006-STEVENS-2009-WARNING-FT` to revision 2, still `pending`, with agent attribution; no new publication, hit, STUDY, EXP or SAMPLE.

## Frozen Track E checks (eligibility only)

| Rule | Original-body evidence, distinct from any numerical extraction | Status |
|---|---|---|
| E1 human | Method > Participants: original authors report 36 adults, with 18 receiving auditory and 18 visual warning sets | Source supports |
| E2 machine-issued audio | Method > Stimuli: computer-delivered one-second natural/symbolic auditory warning indicators for critical aviation events; not interpersonal speech | Source supports |
| E3 comparison | Aim/design and Procedure: 2×2×2 modality × indicator × workload; repeated natural/symbolic and low/high conditions | Source supports |
| E4 outcome | Results and Tables 4–5: warning-recognition accuracy and reaction times across learning and dual-task phases | Source supports |
| E5 primary empirical report | Original Method, Procedure, Results present | Source supports |
| E6 cutoff | Journal issue/date 2009, before frozen 2026-10-04 | Source supports |

**Identity and denominator caution:** Method > Stimuli says a separate N=40 association-rating/stimulus-selection task preceded the original warning-recognition experiment. It must not be added to, conflated with, or silently counted as a second admitted sample inside the N=36 main experiment. The 18 auditory and 18 visual groups are experimental arms, and natural/symbolic warning tests are within-person conditions. This paper contrasts Perry et al. (2007) but says nothing sufficient to certify disjoint participant pools across publications. Mark cross-report overlap `unknown` pending original primary-method comparison.

The main article reports qualitative source findings and numerical tables, but **no numerical result, effect size or sample record has been extracted/admitted**. The web-intermediary reading is permitted for bounded eligibility checking by frozen protocol §10, not for numerical extraction or decisive synthesis.

## Exact gate and Integration action

- Frozen protocol §6.2 does **not** require an independent second human screener; any AI recheck is correlated, not human verification.
- Current `tools/record_graph.py` rejects a full-text final `include`/`exclude` without a *performed* `assistance` reading reference attached to the source. The source has no registered manifestation, and R006 has no truthful AID to attach; **retain `pending`** until an admissible source-bound reading exists. Do not manufacture a manifestation, digest, timestamp or reviewer.
- **One Integration-owned action:** lawfully retain and attest a precise *original* Europe PMC XML instance (or independently verified publisher HTML/PDF), document its edition, access time, DOI, licence/rights and byte digest, and register a canonical `SRC` manifestation in the appropriate source lane. Notify R006 of the new exact `SRC@rev` with original content available for re-reading. Then R006 can perform genuine source-pinned E1–E6 judgement and decide whether to transition `pending` to `include`. Reconcile any participant overlap before admitting study/sample identities.
- Integration must regenerate `research/registry/generated/records-index.json` and `evidence-flow.json` using `python tools/validate.py --write-exports` after copying any R006 canonical record revision; full history-aware suite, fixture check, exact-final-head and merged-main CI are required. R006 owns neither shared manifest nor exports.
- All R006 counts remain 9 title/abstract, 5 pending FT, 3 awaiting original, 1 FT exclusion, **0 FT included**, **0** admitted studies/experiments/samples and **0** selected Track E/G. R007/R008 are not corpus-ready.

This source-backed work is AI-assisted (GPT-6; web intermediary), not independent human screening. Do not merge as scientific acceptance without Integration provenance review.
