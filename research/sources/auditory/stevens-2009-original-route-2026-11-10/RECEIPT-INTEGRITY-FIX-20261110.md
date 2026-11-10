# R005 source-attestation integrity correction — 10 November 2026

Refs #5; source/custody handoff to #4 and #6. Base main: `099148afd0bab094c519a92e669a5f8c17ee7572`. Frozen search cutoff remains **2026-10-04**.

## Reproduced implementation gap

The accepted offline `attest_primary_xml.py` previously checked the private XML byte hash, DOI and PMCID, but `verify` did **not** compare the locally recomputed original `<body>`/`<back>` flags, section-title inventory or observed licence-link inventory against their saved receipt counterparts. Editing those receipt claims while retaining the original verified bytes could therefore still produce a successful verification result. The verifier also failed to reject missing/garbled operator-reported access evidence, source URL, edition, timestamp, or changed issue/search-hit pins.

This patch adds explicit comparison of **all locally source-derived fields**, validates presence/syntax/chronology of *operator-reported* source provenance and checks the fixed R005/R006 issue, frozen-cutoff and existing discovery hit identity. Three new unittest methods exercise falsified source-derived claims, missing/corrupt operator fields and noncanonical timestamps. No network call, source byte redistribution or scientific screening is introduced.

## The underlying original source (previously observed, not fetched in this run)

- Stevens, Brennan, Petocz and Howell (2009), *Designing informative warning signals*, DOI **10.2478/v10053-008-0064-6**, PMCID **PMC2865004**; existing R006 `SRC-R006-E-STEVENS-INFORMATIVE@1` and R005 `HIT-R005R-C1LOAD-EQ1-02138@2`.
- Original Europe PMC article XML endpoint: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2865004/fullTextXML
- Earlier R005 technical receipts: **2026-11-10T20:15:16.864Z** and **20:19:06.280Z**, two successful transient **74,338-byte** original XML responses with SHA-256 `1390d7a4def94ad6b0926a5f1ae2608999f31713fb3ee5dad20b9e3fcc52658b`. An XML licence link appeared to identify **CC BY 2.5**, but a legal retention decision and durable original-byte archive were **not** established.
- R006's distinct web-HTML Methods/Results preassessment concerned one author-reported **N=36** recognition task and a separate **N=40** stimulus-rating task; that HTML is **not** the hashed XML. Neither participant count is canonically admitted.

## Boundary and integration handoff

This is a negative-control correction to the **R005-owned offline attester**, **not** original source acquisition, an authenticated acquisition timestamp, proof of lawful storage, copyright clearance, human review or E1–E6 adjudication. The operator's original URL, edition, rights note and acquisition time remain **unverified assertions**, even when their format is checked. The receipt is not cryptographically signed; valid-looking provenance tampering still requires external audit.

**R004/Integration:** Approve private storage and rights basis, preserve an actual exact-byte original XML instance, independently verify acquisition/custody and register a truthful SRC manifestation; review this patch's source-only scope and final-head CI before guarded merge. **R006:** only after source manifestation and performed reading, decide frozen E1–E6 eligibility and study/experiment/sample overlap, without conflating 36 and 40 or inferring cross-publication independence. Integration alone updates shared registry exports.

At this checkpoint the nine accepted TA records remain nine; five FT pending, three awaiting text, one excluded, **zero included**; **0/0/0/0** admitted publications/studies/experiments/independent samples, selected Track E/G **0/0**. R007/R008 not selected-corpus-ready. No new EQ1, ICAD or C9 search run is claimed.

Run `python -m unittest tests.test_r005_primary_xml_attestation -v`, full unittest discovery, `python tools/validate.py`, and `python -m tools.build_record_fixtures --check` on the final source head. An exact-head CI success confirms code structure, **not scientific/rights admission**.
