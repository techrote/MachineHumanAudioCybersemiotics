# R005 targeted known-item recovery — 10 November 2026

This is an **additive, source-navigation audit**, not a correction to the October 69-item benchmark, an OpenAlex continuation, or Track E eligibility. The original benchmark recorded 38 located, 10 possible and 21 not located. A new exact-title/author/DOI web-search pass located **10 bibliographic candidate routes among those 21 historically unlocated entries** (K02, K07, K29, K34, K38, K42, K44, K45, K52, K53). The historical scores remain unchanged. One match (K29) has conflicting secondary metadata and must not be silently promoted to a unique publication identity.

[OBSERVATIONS.json](OBSERVATIONS.json) records, per historical K identifier: the exact query, fast/slow web mode, source URL, authority type, extent actually inspected, DOI provenance, uncertainty, and onward R006 requirements. The source material ranges from publisher abstracts to a bibliographic index or first-author publication list. Public links to PDFs were found for K42, K45 and K53, but their bytes were **not** downloaded, hashed or fully read by this run. No full-text screening, human verification, included-study assessment, extraction or outcomes are claimed.

## Limits and reproduction

The web tool provides result pages/snippets but no lossless search-response export. This batch therefore **must not be registered as a complete v1 C1/C2 search-run** or counted as exhaustive web recall; it is a dated supplement with exact recorded queries and stable source locators. Re-execution of the same query at a different date may return different rankings. Source claims are restricted to bibliographic metadata and directly visible access text. No content from restricted articles or copyrighted PDFs is redistributed.

Direct OpenAlex/Crossref API access from the container failed with name-resolution errors on 10 Nov 2026. This is a **current-environment route observation**, not evidence that those services are globally unavailable, quota-exhausted today, or that the previously complete EQ2–EQ8 runs regressed. The old EQ1 sorted partial 4,200/9,368 remains unresolved.

## Actionable handoff

- **R005**: if a network-enabled worker can access C1, continue **only** the remaining EQ1 sorted paging in a new immutable invocation, preserving all prior attempts; then compare against these located K items and the existing source/hit registry.
- **R006**: reconcile these ten candidate source routes against existing DOI/URL and manifestation records, preserving occurrence provenance and testing publication-vs-study-vs-sample overlap. For K29, compare publisher DOI metadata with institutional and third-party presentations before choosing identity; do not classify this audit as a screening decision.
- **Integration shepherd**: incorporate qualified source/hit/search records and regenerate shared indexes only after actual export- and record-schema validation; do not treat this supplement alone as #5 or #6 completion.

The unchanged 2026-10-04 publication cutoff, frozen protocol, human gates and incomplete search/channel coverage remain binding.

## Check

Run `python -m unittest tests.test_r005_known_item_recheck_20261110 -v` from the repository root to assert that the ten IDs were genuinely previously `not_located`, that the links/query evidence is present, and that no observation claims full-text, independent study or screening acceptance. This is integrity checking, not verification of remote page content.
