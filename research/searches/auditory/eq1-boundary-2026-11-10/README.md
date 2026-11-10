# R005 — EQ1 frozen-query boundary recheck, 10 November 2026

**Refs #5; read-only source discovery support for #6.** This is a new OpenAlex C1 observation against frozen protocol v1, **not** a historical export extension, completed EQ1 search, eligibility decision, source full-text reading or selected study/sample. Source branch was created from accepted main `085a0760294c23b8f128a028e2c377b35571c8c6`. The existing 150 search records and 21,483 discovery occurrences are unchanged.

## Why this recheck matters

The 3 November sorted EQ1 retrieval ended after 4,200 records of 9,368 reported, with registered boundary `HIT-R005R-C1LOAD-EQ1-04200` = OpenAlex `W2520134007` (2016-09-01). [Current OpenAlex API authentication documentation](https://help.openalex.org/api/authentication/) now states a 100-record maximum per page, unlike the historical 200-record legacy size. Resuming with page 22 at the old size cannot be assumed valid. The read-only test used the exact existing `query_families()["EQ1"]` expression from `research/protocol/PROTOCOL-v1.md`, `title_and_abstract.search`, `to_publication_date:2026-10-04`, `sort=publication_date:asc,display_name:asc` and **`per_page=100`**, at pages **42 and 43**. It deliberately did not substitute general search or shift the cutoff.

## Original HTTP receipt and actual outcome

[PR-branch Actions #42822235351, job #129850397555](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42822235351/job/129850397555) executed on **2026-11-10**, source commit `554541af7488b7f91d0fa22334026a63aa14b4ab`; both unauthenticated OpenAlex API GETs returned **HTTP 200**, 100 result entries with distinct OpenAlex IDs per page. The full URLs, HTTP Date, request/completion UTC, raw-byte hashes, bibliographic IDs/DOIs/dates/titles and access limits are preserved verbatim in [OBSERVATIONS.json](OBSERVATIONS.json). The response bodies were checked and hashed but were **not** archived; the committed 200-record table is a derived metadata selection with no reconstructed abstracts. The original response itself cannot be byte-for-byte regenerated from the derivative.

| Page | UTC HTTP Date | Raw bytes | SHA-256 | Current provider total |
|---|---|---:|---|---:|
| 42 | 2026-11-10 13:11:33 | 1,076,658 | `99a557eac990811a3270faf7fb83f6723b9a797f35d821ae610d11f8ecda277a` | 9,275 |
| 43 | 2026-11-10 13:11:36 | 1,017,746 | `7f17c8eb666c0f2d2bf52f6c336bd3748d173a6b2ff73e769f1b976ac587a4c8` | 9,275 |

**Decisive discrepancy:** The provider now reports **9,275, not 9,368** (−93). Page 42's last ID was `W4244593129` (dated 2016-11-14), **not** the historic 4,200th ID `W2520134007` (dated 2016-09-01). Thus page 43 cannot simply be appended as occurrences 4,201–4,300; the live index, search result set or sorting boundaries shifted. The 200 returned rows are *observations*, not 200 verified new publications nor independently eligible studies.

A potentially relevant hit in the new page 43 is OpenAlex `W2551005744`, *Effects of auditory and tactile warning on response to visual hazards under a noisy environment*, DOI `10.1016/j.apergo.2016.11.002`. This is an **unscreened discovery lead**; publication identity, source-text availability, protocol eligibility and duplicates require R006 assessment. It must not silently enter the selected corpus.

## Research-integrity boundaries and handoff

- **R005:** Preserve these true source-page receipts; perform overlap reconciliation against the original 4,200 sorted IDs and other discovery routes before registering any new `SRCH`/`HIT` records or changing coverage counts. A new stable complete EQ1 invocation, with explicit index-drift handling and immutable exported pages, is preferable to calling page 43 a continuation. Seven other OpenAlex families are already complete and should not be harvested again without an explicit reason.
- **R006:** No new canonical title/abstract or full-text decision, study, experiment, sample or Track E/G selection is asserted. R006 alone decides eligibility and publication versus experiment versus independent-sample identity. The existing four-candidate gate remains four TA, one FT exclusion, one FT awaiting text, two FT decisions absent, zero FT inclusion and zero selected studies/samples, subject to live canonical re-verification.
- **R004 / Integration:** Exact-byte Becker and Romeo 2025 original-PDF manifestation registration remains the dominant R006 full-text dependency; Romeo 2023 has a verified Zenodo *supplement* but lacks the original IEEE report. Integration exclusively owns shared manifests, generated exports, guarded merge and downstream count recalculation.
- **Verification boundary:** The live GitHub Actions run proves that these HTTP bytes were received and that the test/validator/fixtures passed on the first source head; it does not establish lawful redistribution of full papers, physical audio inspection, independent human screening, completeness, source eligibility or scientific validity. Public, no-login OpenAlex metadata access was used. No API key, credential, paid access or external review was involved.

No original API response bytes, abstract inverted indexes, third-party full paper or audio stimuli were committed. `Refs #5` until the search/access gate is accepted.
