# R005 supplementary known-item remainder audit — 10 November 2026

This is a **dated, additive C8/C9 bibliographic navigation checkpoint**, not a newly executed OpenAlex/database harvest, complete citation chaining, or Track E screening.

The accepted [first 10-item recheck](../known-item-recheck-2026-11-10/OBSERVATIONS.json) addressed K02, K07, K29, K34, K38, K42, K44, K45, K52 and K53 from the historical 21 `not_located` references. This second pass addresses the **other 11**: **K04, K09, K12, K33, K35, K50, K54, K56, K64, K67 and K68**. Original 69-item benchmark outcomes **38 located / 10 possible / 21 not located** are deliberately unchanged. Neither batch has been recomputed against the large OpenAlex inventory.

[OBSERVATIONS.json](OBSERVATIONS.json) contains every exact web query, search mode, retained source locator, source type, verification level, limitations and issue-scoped R006 handoff. Ten candidates have a publisher/institution/conference/curated-index route. K50 only has a third-party item and a later secondary bibliography with a **page-range disagreement** (October 194–199 versus later citation 196–201); it is **provisional** and must not be accepted as independently verified publication identity. K54's historical DOI `0` is malformed: the 1997 Springer table of contents confirms the chapter, but a book-level DOI is not silently substituted for a chapter DOI. K56's historical topic queries already found a matching title; this is a validation route, not a newly found unique paper.

## Source hierarchy and what was actually read

- Publisher/primary programme: CHI 2013 for K04; Springer INTERACT '97 for K54; SAGE for K56, K64 and K67. Institutional or curated metadata: DBLP K09, PubMed K35, Edinburgh K68, Georgia Tech's indexed proceedings PDF title K12, contemporaneous ICAD programme K33.
- K50: third-party title/abstract and a conflicting later bibliography only. Independent original proceedings metadata remains needed.
- Georgia Tech proceedings/PDF routes for K12/K33 were discovered through indexing. **No PDF bytes or page images were inspected or hashed in this pass.** For other records, publisher/institutional metadata or abstract sections were read, not entire research reports.
- Exact output count is **11 targeted candidate-route assessments**, not 11 eligible publications, screened reports, studies, independent samples, complete production search hits or new primary experiments. No raw web-result payloads or response hashes were available; a later execution cannot exactly replay a search-provider ranking.

## Review and handoff

1. **R006**: check identity against all registered R005/R004/OpenAlex hits and source manifestations. Keep K50 pagination conflict and K54 malformed DOI unresolved. Check K56's already-found topic hits before creating a new source; check K64 against the 2006 ICAD spearcon conference paper before counting a distinct study/sample.
2. **R005**: highest-value outstanding coverage remains immutable **EQ1 continuation** (historically 4,200/9,368, date/title-sorted), then review and accepted-report backward chaining and incomplete venue/database channels. This audit does not change the frozen publication cutoff **2026-10-04** or the recorded 150-search/21,483-occurrence November snapshot.
3. **Integration shepherd**: verify the candidate URL/metadata claims and review the limited source-reading attestations before a guarded merge; retain this as a supplementary ledger without modifying common exports. Issue #5 and the R006 corpus gate stay **OPEN**.

No paid access, human reviewer action, participant work, source-paper redistribution or eligibility inference occurred. AI assistance is documented; structural tests are not independent bibliographic or empirical verification.
