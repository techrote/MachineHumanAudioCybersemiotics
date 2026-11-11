# Stevens 2009 R005: original Methods/Results section fingerprints (11 Nov 2026)

**Refs #5; source/identity handoff to R006 #6 and R004/Integration.** Frozen protocol v1 §§5, 6, 10–12; publication cutoff **2026-10-04**, unchanged. Source branch was created from main **5e01f3c39232a46238f5333cfa1d1519c0f8995f**. This is **not** a new publication, title/abstract screen, scientific admission, human reading or independent sample.

## Why this work, and the precise identity

Stevens, Brennan, Petocz and Howell (2009), *Designing informative warning signals: Effects of indicator type, modality, and task demand on recognition speed and accuracy*, *Advances in Cognitive Psychology* **5:84–90**, DOI [10.2478/v10053-008-0064-6](https://doi.org/10.2478/v10053-008-0064-6), PMCID [PMC2865004](https://pmc.ncbi.nlm.nih.gov/articles/PMC2865004/), PMID 20523852. The **Europe PMC JATS/NLM original-article XML** is not the publisher PDF edition.

Accepted original discovery occurrences are **one publication's multiple hits**, not three independent studies: representative `HIT-R005R-C1LOAD-EQ1-02138@2` (OpenAlex `W2022893852`), with `HIT-R005R-C1LOAD-EQ5-00403@2` and `HIT-R005R-C1RECOVERY-EQ7-00080@2` as further search occurrences. R006 source `SRC-R006-E-STEVENS-INFORMATIVE@1`.

The [previous original HTTP evidence](../stevens-2009-original-route-2026-11-10/OBSERVATIONS.json) came from public, unauthenticated [Europe PMC fullTextXML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2865004/fullTextXML): **10 November 2026 at 20:15:16.864Z**, HTTP 200, original **74,338 bytes**, SHA-256 **1390d7a4def94ad6b0926a5f1ae2608999f31713fb3ee5dad20b9e3fcc52658b**, source-reported CC BY 2.5 link. Those original response bytes were **not retained**. Their section-heading inventory, while reliable for locating Method and Results, could not establish fingerprints of full section text. No complete results reading or eligibility follows from heading presence.

## New bounded acquisition and source-reading boundary

The offline unit tests in `tests/test_r005_stevens2009_section_digest_20261111.py` reject incorrect DOI, abstract-only or truncated article, missing participant/stimulus/procedure and learning/test section boundaries, altered text hashes, and XML entity declarations while accepting ordinary JATS DOCTYPE headers. The only live request is a **single unauthenticated public GET on this exact branch's pull-request GitHub Actions run**. The original response (if received) is processed in memory and is never written to the public repository or to an artifact.

The machine obtains original HTTP Date/status, request/completion UTC, content type, actual response byte count and SHA-256. It parses the original article body and **walks complete top-level Method and Results sections**, including their nested paragraphs, returning reproducible `/article/body/sec[n]` locators, nested section headings, normalized full-section text SHA-256 and character/paragraph counts. The text fingerprint covers **actual original section content rather than only headings**. No paragraph text, participant-level data, table values, audio, statistics, effect estimates or full article bytes are published.

These are **machine-readable section-bound fingerprints, not human or independent assessor reading, peer review, performed semantic eligibility assessment, source manifestation, rights/retention approval, or numeric extraction**. A complete successful request must be proven by the actual `MHAC_R005_STEVENS_SECTION_PINS=` row in the CI log; green CI alone does not prove network access. A source/response error remains a precise recorded blocker, not evidence of absence of the paper.

## R006 / Integration gate and next action

**R004 / Integration:** Designate approved private custody and an actual rights/attribution basis for a new original Europe PMC XML copy. Retain that copy privately with original response timing and headers. Use the existing [offline XML attester](../scripts/attest_primary_xml.py) to bind its *actual* SHA-256 to a local receipt (never substitute a historical hash if bytes have changed). Register its source manifestation and controlled reading event using Integration's ownership of canonical source records, manifests and generated exports. The source's link to CC BY 2.5 is **licence metadata, not blanket self-authorization of retention**.

**R006 exclusively:** Use a proven retained manifestation and pinned original Methods/Results text to decide frozen E1–E6 eligibility and publication → study → experiment → independent-sample relationships. Stevens' author-reported 36-person main warning experiment and 40-person stimulus selection task are not automatically two independent admitted samples; cross-publication overlap with related Stevens/Petocz/Perry reporting remains `unknown` until established. Do not reinterpret modality/indicator conditions as separate samples. Existing nine TA (6 toward full text, 3 uncertain), FT (5 pending, 3 awaiting original, 1 exclude, 0 include), 0 admitted publications/studies/experiments/samples, Track E/G 0/0 remain unchanged.

**R005:** Search cutoff remains unchanged, and no SRCH/HIT or metadata-based empirical count is created by this source probe. If original-custody gate remains blocked, the next feasible independent priority is one immutable, single-invocation OpenAlex EQ1 adjacent-page/continuity verification **only when allowed by quota**, then ICAD/C9 coverage with original query and response evidence. The historical 4,200/9,368 checkpoint and 10/11 November 8-ID boundary overlap cannot be welded into a completed search; the 11 November page 45 HTTP 429 is a stop condition.

## Verification and status

```sh
python -m unittest discover -s tests
python tools/validate.py
python -m tools.build_record_fixtures --check
```

This document is a **pre-acquisition design and negative-control record**; an actual observed result, acquisition timestamp, hash and Actions link must be added only after reading the source-exact CI marker. Do not claim final-head qualification or merged-main CI until the actual final head and relevant checks are successful. R005/R006 and the owner-only custody/rights gate remain OPEN.
