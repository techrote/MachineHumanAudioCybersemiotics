# R006 — Two next-priority primary-abstract screening candidates (10 November 2026)

**Refs #6. Two source-pinned canonical TA SCR files are now AUTHORED ON THIS DRAFT BRANCH but NOT serialized into accepted-main indexes/exports or merged.** No full-text eligibility, study, sample, selected Track E/G publication or human second screening is claimed. Original first-pass proposal is preserved in DECISIONS.json; a later same-agent E1 conservatism adjustment is disclosed below. This tranche follows the already admitted four TA records on accepted base `f2f9a13a70d38ab50e038ce08f34724c5a08918e`; none of those records is re-created. The current four-case FT gate is deliberately untouched.

## Source-backed first pass

| Existing verified publication | Original text actually accessed 10 Nov | Frozen v1 E1–E6 first pass | Next admission boundary |
|---|---|---|---|
| Edworthy et al. (2014), DOI [10.1016/j.apergo.2013.10.003](https://doi.org/10.1016/j.apergo.2013.10.003) | [University of Plymouth institutional publication Abstract](https://researchportal.plymouth.ac.uk/en/publications/learning-three-sets-of-alarms-for-the-same-medical-functions-a-pe/) (not complete article); PubMed PMID 24209498 crosscheck | **include to FT**: humans learn three representations of function-mapped equipment alarms; alarm identification/learnability tested | Exact full-text retrieval and sample design, source-manifest pin, canonical TA and export |
| Nees, Helbein & Porter (2016), DOI [10.1177/0018720816629279](https://doi.org/10.1177/0018720816629279) | [SAGE original publisher displayed Abstract](https://journals.sagepub.com/doi/10.1177/0018720816629279), sections Objective–Application; SAGE identifies full paper as **restricted access**; PubMed PMID 26884437 crosscheck | **include to FT**: vehicle-status speech/earcon-type alerts vs visual control, with event memory and subjective outcomes; human N not verified from abstract | Lawful report retrieval, source-manifest pin and complete methods review; no extraction/count yet |

The original web pages were consulted without authentication on 10 November 2026. **No HTTP response timestamp, original PDF bytes/digest, video/audio playback, complete Methods or numeric effect extraction were obtained.** The recorded `2026-11-10T14:30:04Z` is the executing agent's decision/checkpoint time, not the original publisher HTTP Date. Access permission for publicly displayed abstract text is distinct from reproduction rights to the article. External pages may change; no raw response snapshot is claimed.

Both items were already registered as **distinct verified-DOI publications** by R006 on 6 November, with immutable R005 search-hit IDs preserved in each source's revision-1 basis. The multiple EQ1/EQ5/EQ6 discovery occurrences are **not** participant groups or multiple experiments. `DECISIONS.json` records exact source pins, original-abstract locators, E1–E6 and scoped human/agent provenance. No R005 files, R004 manifestations, accepted-main original four SCRs, shared generated exports or protocol were modified. **Two NEW R006-owned canonical TA SCR files were authored later in the same run and remain blocked from merge until Integration regenerates shared exports.**

## Distinct admission tasks

1. **R006 scientific review:** confirm first-pass E1–E6 using the displayed original abstracts, and resolve any discovery ambiguity. Consider the Nees E1 report provisional on the abstract; retain uncertainty if the reviewer cannot substantiate a human test. Do not assert complete full-text eligibility or study/sample independence from abstract summaries.
2. **Integration registrar only:** review the two newly authored canonical title/abstract `SCR` files pinned to existing publications, retaining their actual registrar actor and time; do not backdate to original preparation. Independently assess the E1 caveat below. Regenerate records-index and evidence-flow under shared ownership, run `python tools/validate.py`, `python -m tools.build_record_fixtures --check`, full unittest, scope checker and exact-head/push CI. Earlier #109 registrar was **not** the screener of this pair.
3. **R005/source owners:** pursue lawful full texts and version-stable hashed manifestations if obtainable. A restricted publisher article is not excluded for access. R006 may then perform source-pinned full-text screening. Exclusions require the protocol's separate later AI recheck; frozen v1 requires **no invented human second assessor**.
4. **Existing four-case gate:** Becker 2025 and Romeo 2025 still lack permanently registered original-file manifestations (the Chalmers Romeo URL has byte variability); Romeo 2023 still lacks original IEEE full text despite the verified Zenodo scripts. Kühne 2020's existing FT E2 exclusion and reading AID remain unchanged. Do not double count the four original TAs.

## Reproduction

```sh
python research/screening/r006_next_ta_20261110/check.py
python -m unittest tests.test_r006_next_ta_20261110 -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

The checker only validates this **prepared** packet against canonical publication identity/hit provenance; it is not a substitute for exported corpus admission or actual full-text/source assessment. Two R006-owned canonical SCR additions now require Integration's serialized generated exports. Current unmodified generated views are EXPECTED STALE on this Draft and **full repository validator is not yet expected to pass**. Only a new integration PR/commit with regenerated index and evidence-flow, verified exact-head CI and merged-main CI can claim canonical admission. **R007/R008 remain not selected-corpus-ready.**

## Same-run canonical registration checkpoint (14:33:37 UTC)

After the noncanonical 14:30:04 UTC first-pass packet, this GPT-6 R006 registrar authored **two new canonical TA record files** in `research/screening/records/` with actual AI actor/time, original abstracts and source identity pins. Edworthy remains `include` to FT only. Nees was conservatively changed to `uncertain` because the publicly displayed SAGE abstract did not explicitly verify human participant N or assignment; this is a **same-agent correction**, not a second pass or human adjudication. Both decisions proceed to lawful full-text retrieval under §6.2. They are not accepted on main, and no study/sample/extraction is created.

The prepared 14:30 first-pass packet remains historically explicit (original Nees proposal `include`); `post_preparation_registration` records the later change rather than rewriting it. Run `python -c "from research.screening.r006_next_ta_20261110.check import verify_authored_scrs; print(verify_authored_scrs())"` only in environments where that import resolves; the unit tests load the checker by file path. **Actual mainline export/test gate is with Integration**, not the branch's preparation validator. Shared files remain unchanged by this worker.
