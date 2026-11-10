# R005 → R006 primary-source access recovery — Becker et al. (2025)

**Refs #5; handoff to #6.** Access observed 10 November 2026; ledger assembled at the timestamp in [BECKER-2025.json](BECKER-2025.json). Branch base: `d3348fba38f01500a134593f9b64b268d62392af`. Frozen publication cutoff: **2026-10-04**.

## Result: the missing source-text gate has a lawful route

The previously [unresolved R006 Becker full-text gate](../../../screening/r006_fulltext_e2_review_20261110/DECISIONS.json) can now be re-examined. The University of Hamburg author bibliography [entry 928](https://wtmbib.informatik.uni-hamburg.de/Basilic/publis/928/) links an [author-hosted article PDF](https://www2.informatik.uni-hamburg.de/wtm/publications/2025/BBCKOAGSFW25/3706066.pdf), **Becker et al., *Influence of Robots’ Voice Naturalness on Trust and Compliance*, ACM Transactions on Human-Robot Interaction 14(2), article 29 (2025), pp. 29:1–29:25, DOI [10.1145/3706066](https://doi.org/10.1145/3706066)**. The PDF's first page states the CC BY 4.0 licence. An institutional [Surrey record](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Influence-of-Robots-Voice-Naturalness-on/991115568402346) corroborates the publication identity, but its abstract alone was the earlier R006 reading basis.

The web PDF reader supplied article text; selected rendered **PDF pages 8, 9, 24 and 25** (zero-based indices 7, 8, 23, 24, corresponding to printed 29:8, 29:9, 29:24, 29:25) were inspected as page images. Another image-render attempt returned HTTP 403, without invalidating the successfully rendered pages. Direct DOI web opening also returned 403; the institutional route succeeded. A separate attempted runtime download failed, so **original PDF bytes and SHA-256 have not been verified**. The ledger stores the actual record-assembly UTC timestamp, explicitly **not** a guessed HTTP retrieval timestamp. This is tool-mediated primary PDF reading with partial visual verification, not a locally byte-verified source file or complete audio review.

## Evidence changing R006's decisions

| Source location | Primary-text observation | Scientific consequence to test |
|---|---|---|
| §3.2, printed 29:5; §3.7, 29:8 | Online pre-study compares six voice samples for suitability; 62 completed and 2 were omitted after a control question, leaving 60 analysed | Voice-suitability ratings alone are not necessarily G01/E2 system messages |
| §§3.3–3.4, 29:6–29:7; Appendix E, Table E1, 29:24 | Main Battleship interaction has robot status reports, action recommendations, accept/reject choices and repair speech | Concrete E2 evidence exists for the **main interaction**, pending R006 adjudication |
| §§3.6–3.7, 29:8–29:9 | 73 completed main experiment, 5 excluded for technical reasons, 68 analysed, equally allocated to two voice conditions; 9 advice events per person | 68 analysed people, **not** 612 independent people or nine independent samples per participant |
| §3.7, printed 29:8 | Authors explicitly exclude pre-study participants from main-study participation | Direct **author-reported within-publication nonoverlap** between the 60 analysed pre-study participants and 68 analysed main participants; identities not externally verified |
| §3.4, printed 29:8 | Eight people participated in a distinct setup pilot before the main study | Pilot people cannot be counted again without determining participant overlap and eligibility |
| §3.4, 29:7 and Appendix E, Table E1, 29:24 | Robot uses gestures, facial expressions and 76 spoken lines with emotional/repair wording | No inference that the study isolates an emotion-free voice or demonstrates a unique acoustical effect |

All numbers above are **author-reported method counts, not independent MHAC admissions or new empirical measurements**. The sampled voice files were not opened or listened to. The robot's voice conditions also differ in voice identity and treatment, so E3/causal appraisal require care. The research protocol's single-agent status, source-manifest verification and independent scientific-review gaps remain.

## Existing occurrence provenance and correct ownership

The DOI was already represented as `SRC-REL-BECKER-2025@1` in R004 and as `HIT-R004-G06-03@1`, `HIT-R004-G06-04@1` and `HIT-R004-LK3-VOICE-NATURALNESS-TRUST-01@1`. This tranche adds **zero** `SRCH`, `HIT`, `SCR`, `STUDY` or `SAMPLE` records. Source navigation through a web search is **C8 only**, not completion of a formal ACM DL search, a new OpenAlex response or production C9 chaining. The pilot `HIT-R002-PA3-04` is an additional pre-existing metadata route; it has not been silently adjudicated.

**R006 handoff:** independently inspect the now-available Becker primary PDF, decide the full-text `awaiting_text` disposition and E2 per experimental phase, decide how to represent the explicit pre-study/main nonoverlap while leaving the separate pilot unresolved, and register scientifically justified first-stage records without fictitious reviewer identities. Preserve actual screening actor/time. Do not promote this R005 access memo into a canonical R006 full-text decision.

**Integration Shepherd handoff:** review this disjoint R005 source-access file, its source locators and negative tests; after acceptance, notify R006 that the Becker full-text access block is reduced. **Only Integration** coordinates manifests/index/exports and guarded merges. No shared registry state or R004/R006 file was changed here.

## Reproducibility and remaining coverage

Read [the structured ledger](BECKER-2025.json) for query strings, URLs, dated extent, reading modes, source-ID/hit-ID pins, specific page-image outcomes and limitation flags. Run `python -m unittest tests.test_r005_becker_primary_20261110 -v`, full `python -m unittest discover -s tests -v`, `python tools/validate.py`, and `python -m tools.build_record_fixtures --check` against the **final branch head**. CI checks structural coherence, not manuscript truth.

R005's frozen EQ1 remains at the last dated **4,200 / 9,368** sorted-prefix checkpoint; no new query execution or live quota estimate is claimed. Remaining priority after this R006 source handoff: the 2023 Romeo primary manuscript/supplement versus 2025 pilot comparison, then legitimate immutable EQ1 continuation or EQ8/ICAD chain coverage if lawful network/API access permits. **Issues #5 and #6 stay open; no selected #7–#9 corpus is claimed.**
