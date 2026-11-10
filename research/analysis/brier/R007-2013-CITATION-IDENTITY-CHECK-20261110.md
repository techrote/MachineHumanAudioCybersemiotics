# R007 — 2013 internal citation-identity mismatch, source-bounded check

**10 November 2026 · Refs #7 · agent-only observation · not a selected-corpus extraction.**  
Base `main`: `0e7f9debc12e66fb75c132c6542b62041f67d53a`. Machine-readable [five-source-anchor ledger](../../extractions/brier/R007-2013-CITATION-IDENTITY-CHECK-20261110.json). This is a narrow follow-up to the **already merged** [R007 manifestation audit](R007-2003-2006-2013-MANIFESTATION-CHRONOLOGY-20261110.md); it does **not** repeat or replace the accepted chronology analysis.

## Source check and new finding

The [2013 *Integral Review* journal-hosted article](https://www.integral-review.org/documents/Brier%2C%20Cybersemiotics%2C%20Vol.%209%2C%20No.%202.pdf) has a **specific internal citation mismatch**:

- **Printed p. 223 / PDF index 3:** in discussing the foundational English monograph *Cybersemiotics: Why Information Is Not Enough*, the author supplies the parenthetic citation **(Brier, 2006)**.
- **Printed p. 259 / PDF index 39:** the reference list assigns **Brier (2006)** to *Informationsvidenskabsteori* (second edition, Danish), while the English monograph is **Brier (2008a)** (University of Toronto Press). That page does *not* identify the 2006 *Semiotica* article as the 2006 bibliography entry.
- **Printed p. 224 / PDF index 4:** the four-view star paragraph also uses **(Brier 2006)**. Its short-form citation, without an explicit title or DOI, is **not evidence** that Brier is citing the *Semiotica* article.

**Interpretation:** the p. 223 monograph/year combination is internally inconsistent. It is reasonable to suspect a year-reference error, but we cannot establish authorial intent, correct the original publication, or infer a direct source genealogy from this alone. The 2006 *Semiotica* article is a **distinct publication**, DOI [10.1515/SEM.2006.008](https://doi.org/10.1515/SEM.2006.008), not a proven version of either the English book or 2003 *tripleC* article. This concrete source-reference mismatch should be preserved when R006 reconciles publication identities and when R007 cites the 2013 argument.

## Independent manifestation/access check

| Manifestation | What was consulted in this pass | What is **not** verified |
|---|---|---|
| **2013 *Integral Review* 9(2), pp. 220–263** | Official journal-hosted PDF: rendered pages 223, 224, 259 and selected extracted text | Original bytes/SHA, whole-item reading, other figure sections |
| **2006 *Semiotica* 158, pp. 255–296** | [Current publisher page](https://www.degruyterbrill.com/document/doi/10.1515/SEM.2006.008/html): DOI, date, abstract and explicit **“not able to access this content”** message | Any article-body page, original PDF, 2003→2006 text equivalence |
| **2003 *tripleC* 1(1), pp. 71–94** | Selected rendered p. 81 in [CBS repository's publisher-version copy](https://research-api.cbs.dk/ws/portalfiles/portal/85720813/s_ren_brier_the_cybersemiotic_model_of_communication_publishersversion.pdf), which has an added cover | All pages, byte identity with the direct journal copy |

The 2003 *tripleC* **journal-hosted** PDF locates printed p.81 at zero-based PDF index **10**, whereas the **CBS rehosted PDF with a repository cover** places it at index **11**. Do not propagate PDF indices between manifestations. The previous R007 audit's journal-PDF mapping is not erroneous; it refers to a different physical file.

The 2006 publisher page currently exposes **abstract and metadata**, but refuses full article content. Earlier worker observations of HTTP 403 are retained as *earlier access attempts*; this run observed an explicit publisher access message through readable HTML, **not** a captured HTTP 403 status. The publisher abstract enumerates five levels, but is not a substitute for the 2006 text.

## Research disposition and precise unblock

The independently rendered 2013 pp.224/255 evidence in the accepted [R007 chronology memo](R007-2003-2006-2013-MANIFESTATION-CHRONOLOGY-20261110.md) continues to challenge a simple five-to-four replacement narrative, but **frozen protocol §10 bars promotion of this new un-hashed, tool-mediated reference check into a decisive locator-bound full-text extraction**. No original PDF bytes, SHA-256, complete 2008/2013 monograph, 2006 body, independent human review or selected R006 Track G corpus are available. No invented rights, eligibility, participant counts or review occurred.

**R006 handoff:** retain publication/manifestation distinctions; do not resolve “Brier (2006)” on 2013 pp. 223–224 to DOI `10.1515/SEM.2006.008` without direct primary provenance. **R008 handoff:** a citation label is not evidence of a chronological revision or independent theoretical development. **Integration:** source-review this bounded correction against original printed pp. 223, 224 and 259 and merge only after exact-head checks/approval.

**Smallest lawful missing-source action:** supply an authorized *Semiotica* 2006 full article manifestation, identified by DOI and exact issue/pages, plus the 2008 monograph (or clearly identified lawful printing) if whole-book claims are needed. Then hash locally, cite editions/pages and compare the texts. The primary-source gate remains **OPEN**, and R006 #6 / R007 #7 / R008 #8 remain open. No contact, purchase or permission assumption was made.
