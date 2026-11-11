# C9 Romeo 2025 → 2023 direct citation and voice-context source routes — 11 November 2026

**Refs #5; R006 #6 handoff only.** Frozen v1 §5.1 C9 backward citation chaining using C8 public-web navigation; 2026-10-04 publication cutoff remains unchanged. Base `2a5c480daa5f0ade8f0d76df66cf499174c60fa1`. Detailed observations are in [OBSERVATIONS.json](OBSERVATIONS.json).

## Highest-value primary-source/identity finding

The Chalmers-hosted publisher-layout **Romeo et al. 2025**, ACM *Transactions on Human-Robot Interaction* **14(2), Article 33**, DOI **10.1145/3711938**, visibly cites **[61] Romeo et al. 2023** as prior robot-voice/trust literature in **§1.3, printed p.33:4 (PDF page index 4)**; the exact 2023 bibliographic reference appears in **References [61], printed p.33:20 (PDF index 20)**. Both page images were actually inspected. The separate **2023 IEEE RO-MAN, pp.2045–2050**, DOI **10.1109/RO-MAN57019.2023.10309631**, was cross-identified at Heriot-Watt and Chalmers institutional HTML landing pages. The Heriot-Watt public page reports two video-based online studies at abstract level only. No original 2023 IEEE 6-page full text was retrieved or read.

These sources establish **two distinct publications and an actual citation connection, not two independent participant samples**, not duplication, and not a reliable claim of shared stimulus/participant identity. The 2023 Zenodo DOI **10.5281/zenodo.8042317** contains script supplements, not the missing original article or audible stimuli. R006 alone can adjudicate E1–E6 and study/experiment/sample relations.

## Three additional targeted C9 acquisition routes

The same visibly inspected parent reference pages provide **[74]** Torre/Goslin/White 2020, DOI `10.1016/j.chb.2019.106215` (Newcastle accepted-version link; labelled CC BY-NC-ND); **[75]** Torre/Goslin/White/Zanatto 2018, DOI `10.1145/3183654.3183691` (Newcastle accepted manuscript, reuse deferred to ACM); **[76]** Torre/Latupeirissa/McGinn 2020, DOI `10.1109/RO-MAN47096.2020.9223449` (TCD TARA openAccess item with linked PDF and item-level CC BY-SA). Original candidate PDFs were not opened; access labels and links are **routes**, not proof of acquired full texts. No eligibility or distinct-study conclusion follows. These are focused citation-chain leads rather than another false-alarm themed paper.

## Exact provenance and reproducibility

- Parent article: https://research.chalmers.se/publication/546010/file/546010_Fulltext.pdf — actual **PDF screenshot** inspection at indices 4, 20, 21; corresponding printed pages 33:4, 33:20, 33:21. Cover sheet not used as an acquisition timestamp; no stable original-PDF hash or retained file.
- Romeo 2023 institutional metadata: https://researchportal.hw.ac.uk/en/publications/putting-robots-in-context-challenging-the-influence-of-voice-and-/ and https://research.chalmers.se/en/publication/539223
- Supplement (different artifact): https://zenodo.org/records/8042317
- Candidate repository pages: https://eprints.ncl.ac.uk/263737 ; https://eprints.ncl.ac.uk/257694 ; https://www.tara.tcd.ie/items/f47eb94c-e26d-4d33-9d6d-50e4652e8a31
- Actual C8 search strings, author/source/edition identities, candidate keys and reading boundaries are serialized in `OBSERVATIONS.json`. Observer clock checkpoint **2026-11-11T04:12:28.365Z**, measured after searches; it is **not** the request timestamps, HTTP Date or cached Chalmers wrapper date.
- The web service returned rendered search excerpts/pages and PDF page images **without lossless original HTTP bodies, per-request server dates, query response IDs or original-body hashes**. No API export, complete search-result response, original article file, audio or private storage was captured. The committed JSON and its Git blob SHA preserve the researcher's *observation record*, not transport bytes. Candidate keys `C9-ROMEO2025-REF061/074/075/076` are **not** `HIT-` IDs or deduplicated publications.

**Integrity:** No external outreach, login, purchase, original PDF redistribution, human assessor, canonical screening, new `HIT` entries, experimental N, source manifestation, or selected corpus. The 2025 article's displayed CC BY-NC-SA 4.0, Newcastle item-rights notices and TARA item access labels must not be interpreted as an owner-approved private storage policy. The historical 150 search records / 21,483 occurrences and the canonical R006 state remain unchanged.

## Verification and next gate

Run `python -m unittest tests.test_r005_c9_romeo_voice_lineage_20261111`, then repository-wide unit tests, `python tools/validate.py`, and `python -m tools.build_record_fixtures --check`. Unit tests protect metadata relationships, DOI/edition, review-claim limits, noncanonical hit status and missing raw-response/custody evidence; they cannot verify the source scientifically.

**Handoff to R006:** Preserve separate publication identifiers for Romeo 2023 and 2025, note direct Ref [61] connection and distinct 2023 supplement, verify full original 2023 publisher text before claims about methods, participant or stimulus overlap, and treat three additional references as unscreened deduplication routes.

**Handoff to Integration/R004:** No shared manifest edits. The decisive owner action remains choosing an approved private, rights-compliant retention destination for authentic Stevens 2009 Europe PMC XML (DOI 10.2478/v10053-008-0064-6; PMCID PMC2865004); actually retain, hash and register genuine original bytes and reading provenance. Then R006 may make source-pinned full-text decisions. Otherwise continue authorized C9/legitimate EQ1 remainder attempts. R005 and R006 stay OPEN; R007/R008 not selected-corpus-ready.

**Publisher full-text access recheck (2026-11-11 04:18:33Z observer-clock checkpoint):** Direct web-renderer opening of `https://ieeexplore.ieee.org/document/10309631` returned a JavaScript-disabled/bot-verification interstitial, not the article. Original request HTTP code, exact acquisition time and original response bytes were not supplied; no subscription login, payment or bypass was attempted. [dblp's record](https://dblp.dagstuhl.de/rec/conf/ro-man/RomeoTMCL23.html) explicitly marks access `closed`; its generic optional Unpaywall button is **not evidence of an actually retrieved lawful PDF**. The R006 `awaiting_text` blocker remains. The session's observable failure is a verification interstitial, not proof that the article is universally unavailable.
