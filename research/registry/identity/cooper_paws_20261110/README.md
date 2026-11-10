# R006 — Cooper PAWS publication / phase / participant identity

Refs #6. Noncanonical **source-backed identity adjudication**, 10 November 2026. Base accepted main `d3348fba38f01500a134593f9b64b268d62392af`; reviewer: one GPT-6 AI-assisted source pass, **no human screening or independent human review**. Full structured observations: [EVIDENCE.json](EVIDENCE.json). Validation: `python research/registry/identity/cooper_paws_20261110/validate.py` and `python -m unittest tests.test_r006_cooper_paws_20261110 -v`.

## Decisive result

The shared PAWS programme occurs in **three distinct reports**, not three automatically independent experiments or participant samples:

| Report | Verified source extent | Phases described |
|---|---|---|
| [Cooper et al., OJAKM 2020](https://www.iiakm.org/ojakm/articles/2020/Volume8_2/OJAKM_Volume8_2pp107-121.pdf) (DOI 10.36965/OJAKM.2020.8(2)107-121) | Journal landing-page abstract and printed pp. 110–111 PDF/text + page images | One phase of **32 expert reviewers**, surveyed April 2020 |
| [Cooper doctoral dissertation, 2020](https://nsuworks.nova.edu/gscis_etd/1121/) | Repository abstract only; full-text link rejected (HTTP 403 in browser) | **32 experts**, **5 pilot users**, **205 later app users** |
| [Cooper et al., *Heads-up!*, 2021](https://scholars.nova.edu/en/publications/heads-up-an-alert-and-warning-system-for-phishing-emails/) (DOI 10.1108/OCJ-03-2021-0006) | University abstract only; direct final PDF link rejected (HTTP 403 in browser) | **32 experts**, development/pilot, **205 later app users** |

The repeated phase counts and project/author/design details support **probable report reuse**, especially for 32 expert ratings and 205 end-user trials. They **do not prove** identical participant identities without comparing the full reports. The five-person pilot number is stated in the dissertation abstract only; it must not be silently attributed to the 2021 article as a directly verified value.

### Scientific and eligibility distinction

The 2020 OJAKM panel judged *prospective* audio/visual/haptic warning features; a design-rating study is not automatically an E2/E3 qualifying experiment in machine-generated messages. The thesis and 2021 paper discuss audio/visual warnings versus no warning, but the complete methods and participant overlap remain unchecked. All three receive **`uncertain` / not-canonical** rather than forged full-text eligibility decisions. There is **no independent-sample count** from this comparison. This matters especially because R005's [Zhang 2024 contrary-source discovery](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/6#issuecomment-6759664824) cites both Cooper journal publications; they should not be pooled as independent samples without adjudication.

### Provenance and reproduction

The 2020 publisher PDF was reached and screenshot-checked at printed pp.110–111 (PDF file pages 4–5, zero-based indices 3–4); the institution-hosted dissertation and 2021 publication abstracts were examined separately. No original PDF bytes or SHA-256 were obtained, no whole-report reading of any of the three items, no outside peer review and no participant-level data. HTTP 403 is a browser retrieval result, not a conclusion that no lawful access exists. These are source observations and conservative identity hypotheses, not an R009 quantitative synthesis.

The ledger's exact source URLs, locators, evidence limits, three phase links, uncertainty states, frozen cutoff and zero-admission assertions are fail-closed checked by `validate.py`. Negative tests challenge mistaken DOI aliases, 32-person triple counting, 205-person duplication, PDF hash invention, premature full-text/screening promotion and fabricated second reviewer.

## Handoff and next gate

**R006 + Integration:** review the three original full-text manuscripts, reconcile project cohort dates, recruitment and apparatus; separately classify 2020 expert design survey versus 2021 end-user experiment against frozen E1–E6; then create genuinely dated, agent-attributed canonical SCR and STUDY/SAMPLE records with shared manifest/exports only when appropriate. **R005 owns search-history and hit matching.** R007–R009 have no selected corpus from this tranche. Do not replace the prior [four-title/abstract admission bridge](../../../screening/r006_scr_admission_bridge_20261110/) or pretend its missing manifest gate is resolved.

**Status: R006 #6 OPEN; no new canonical SCR, STUDY, SAMPLE, selected report, independent participant count, or completed search channel.**
