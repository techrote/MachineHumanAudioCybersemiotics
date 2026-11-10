# R006 — Šabić 2021 publisher-original HTML full-text preassessment

Refs #6. Prepared 2026-11-10T17:35:44.912Z against accepted main `a7301d37b8077d2105072d543c567b37f6949bdc`. **Original SAGE publisher article selected sections were rendered by a web intermediary; no source bytes or canonical reading manifestation were captured.** The source-backed canonical `full_text=pending` record is a workflow checkpoint, not a scientific inclusion.

## Original publication, identity, and exactly accessed material

- Edin Šabić, Jing Chen, Justin A. MacDonald. “Toward a Better Understanding of In-Vehicle Auditory Warnings and Background Noise,” *Human Factors* 63(2), 312–335 (March 2021), DOI [10.1177/0018720819879311](https://doi.org/10.1177/0018720819879311); [SAGE original publisher HTML](https://journals.sagepub.com/doi/10.1177/0018720819879311), marked **Available access** and first published online **8 October 2019**. Do not confuse the online date, journal issue date and this retrieval.
- Previously accepted `SRC-R006-H-SABIC-UNDERSTANDING@1` (Crossref identity) and `SCR-R006-SABIC-2021-NOISE-TA@1`; original discovery `HIT-R005R-C1RECOVERY-EQ1-00046@1`. This single DOI is **one publication**, irrespective of how many experiments/outputs it reports.
- Tool-rendered selected publisher HTML spans: **Abstract**, **The Current Study**, **Experiment 1 > Method > Experiment design / Participants / Stimuli / Procedure**, selected **Experiment 1 Results/Discussion**, **Experiment 2 > Method > Participants / Apparatus, stimuli, experiment design, and procedure**, selected **Experiment 2 Results**, **General Discussion > Limitations**. SAGE web tool visible line anchors approximately Experiment 1 Methods **91–137**, Experiment 2 Methods **285–292**, Discussion **428–450**. These are **intermediary line anchors, not original publisher page or byte offsets**.
- Retrieval/reading observation: 2026-11-10T17:35:44.912Z UTC (agent decision recording, **not** an origin-server HTTP `Date`); original HTTP response-body hash, native HTML/PDF bytes, original PDF page coordinates, redistribution permission, and source-file preservation **unavailable**. This document paraphrases selected passages rather than redistributing article text. Rights stay `unknown`.

## Frozen v1 E1–E6 provisional review

| Rule | Publisher passage | Tentative assessment |
|---|---|---|
| E1 human participants | Both Experiment 1 and Experiment 2 > Method > Participants | Yes, author-described participants |
| E2 system message G01 | Experiment 1 > Stimuli; Procedure | Simulated in-vehicle status/safety warnings, not ambient noise alone |
| E3 audio comparison | Experiment 1 > Experiment design; Experiment 2 > Method | TTS vs spearcon vs auditory icon; noise blocks; second experiment adds prewarning tone |
| E4 measured outcomes | Experiment 1/2 Results | Recognition, latency, urgency, effort; no values extracted |
| E5 primary empirical report | Both experiments' Methods and Results | Yes, methods and outcomes present |
| E6 publication by cutoff | Publisher article first-online and issue dates | Yes, before 2026-10-04 |

The article describes Experiment 1 with **60 participants** and Experiment 2 with **60 new participants** in their respective Participants sections. These are **author-reported sample descriptions, not new canonical SAMPLE or EXP objects**, participant-level independence evidence or 120 verified independent people. This manuscript says it draws on the first author's master's thesis; possible thesis/publication reuse remains an **unresolved cross-report identity question**.

## Canonical disposition and exact owner actions

`SCR-R006-SABIC-2021-NOISE-FT@1` is **pending**, with a real agent actor, source@1/TA@1 predecessor, `reading_refs=[]`, `review_refs=[]`. No source revision, rights acceptance, human screen, numerical extraction, or experiment/sample was registered. Historical TA decisions were not repeated or rewritten. Source correction/version changes must trigger requalification, not silent promotion.

**R006/R005 handoff:** Investigate whether SAGE's **publisher HTML** can be lawfully retained privately in exact original form (URI, raw response SHA-256, real response/acquisition UTC, rights, HTML anchors and edition); obtain an original PDF separately only if permitted. R006 source owner then registers the actual source manifestation and performed reading assistance pin, re-screens E1–E6 and tests thesis/experiment/cohort overlap. Do not treat the live publisher HTML view as a hashed manuscript instance, and do not invent a human second assessor. R005 owns search history; Integration alone updates shared generated `records-index` and `evidence-flow` and performs guarded merge.

**Expected gate if this pending record is integrated:** TA remains **8** (5 include/3 uncertain). FT becomes **1 exclude / 1 awaiting / 3 pending / 3 missing / 0 include**. Canonically admitted publications, studies, experiments and independent samples stay **0**, selected Track E/G **0/0**. #5/#6 remain open, R007/R008 not selected-corpus-ready.

## Reproduction

```sh
python -m unittest tests.test_r006_sabic_sage_ft_20261110 -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

Adding the canonical pending decision makes Integration-owned generated views stale: **a normal validator/CI failure is expected until Integration recreates the exports on its own branch** using `python tools/validate.py --write-exports`. Neither this R006 branch nor an early partial test can be declared exact-final-head clean on that basis. Scientific admission is still zero, regardless of mechanical validation.
