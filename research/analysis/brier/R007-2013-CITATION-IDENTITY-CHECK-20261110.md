# R007 — 2013 Brier reference identity: corrected primary-page audit

**10 November 2026 · Refs #7 · AI-assisted source verification · preparatory, not selected-corpus reading.** Original PR base: `0e7f9debc12e66fb75c132c6542b62041f67d53a`. This revises the existing [source-critical draft](../../extractions/brier/R007-2013-CITATION-IDENTITY-CHECK-20261110.json) after the [Integration source review](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/113#pullrequestreview-5839761772). It does not create an additional comparator paper.

## Decisive primary-page findings and chronology

- [Brier, *Integral Review* 9(2), 2013](https://www.integral-review.org/documents/Brier%2C%20Cybersemiotics%2C%20Vol.%209%2C%20No.%202.pdf), **printed p.223 / zero-based PDF page 3**: the article calls *Cybersemiotics: Why Information Is Not Enough* a foundational English-language book and cites **(Brier, 2006)**. This is an **ambiguous intended manifestation**, *not proof of a mistaken 2008 book year*. There is a genuine 2006 English thesis with substantially the same title.
- **Printed p.259 / PDF page 39**: its bibliography maps **Brier (2006)** to Danish second-edition *Informationsvidenskabsteori*, maps **Brier (2008a)** to the UTP English book, and **does not include the 2006 English thesis** as a separate entry. This is a reproducible internal reference mismatch/incomplete bibliography; its authorial cause is not recoverable from the citation alone.
- **Printed p.224 / PDF page 4**: the four-view star discussion cites **(Brier 2006)**, but the abbreviated date does not resolve any specific 2006 manifestation, and especially not DOI `10.1515/SEM.2006.008`.
- **Printed p.255 / PDF page 35**: the same 2013 article enumerates **five ontological levels**. Its **four knowledge perspectives** on p.224 are not shown to replace the five levels chronologically. They are distinct conceptual dimensions in the same publication; treating them as 2003 five → 2013 four would be a demonstrable reading error.
- [Brier, *tripleC* 1(1), 2003](https://www.triple-c.at/index.php/tripleC/article/view/6/708), DOI [10.31269/triplec.v1i1.6](https://doi.org/10.31269/triplec.v1i1.6), **printed p.81 / journal PDF page 10**: the five-level scheme already appears here. A [CBS rehost with a cover](https://research-api.cbs.dk/ws/portalfiles/portal/85720813/s_ren_brier_the_cybersemiotic_model_of_communication_publishersversion.pdf) places the same printed p.81 at PDF page 11. PDF indexes cannot be transferred across these two file manifestations.

These are selected *rendered page* checks, not complete-article or monograph close readings, nor independently hash-bound source files.

## Four distinct candidate publication identities

| Identity | Provenance and exact boundary | Not verified |
|---|---|---|
| **2006 English CBS thesis**, *Cybersemiotics: Why information is not enough* | [CBS institutional catalogue](https://research.cbs.dk/en/publications/cybersemiotics-why-information-is-not-enough/): doctoral thesis, English, Frederiksberg, 544 pages, ISBN `8759399864`; **metadata only** | Thesis PDF, chapters/pages, equivalence to UTP book, intentional use of p.223 citation |
| **2006 Danish textbook**, *Informationsvidenskabsteori*, 2nd ed. | [Danish national library catalogue](https://bibliotek.dk/materiale/informationsvidenskabsteori_soeren-brier/work-of%3A870970-basis%3A25661370) confirms 2006 Samfundslitteratur second edition (distinct from 2005 first); 2013 article **bibliography p.259** cites it | Original Danish book text/pages, translation relationship |
| **2006 *Semiotica* 158**, *The cybersemiotic model of communication* | [De Gruyter publisher](https://www.degruyterbrill.com/document/doi/10.1515/SEM.2006.008/html), DOI `10.1515/SEM.2006.008`, pp.255–296, publisher **abstract/metadata only** | Original paper body/PDF, comparison to 2003 article, use as 2013 citation target |
| **2008 English UTP book**, *Cybersemiotics: Why Information Is Not Enough!* | [CBS book catalogue](https://research.cbs.dk/en/publications/cybersemiotics-why-information-is-not-enough-2/): 477 pages, ISBN `9780802092205`, eISBN `9781442687813`; **metadata only** | Whole-book text, specific printing, textual relationship to 2006 thesis |

[Brier's dated CV, printed p.1](https://nordicsemiotics.org/wp-content/uploads/CV-engelsk-to-sider-BRIER.pdf) describes the 2008 book as an **improved version** and reports a 2010 edition with minor changes. This is **author-reported edition history**, not source-body textual comparison. Its wording about a Danish 2006 dissertation also requires caution; it does not override CBS's specific English-language catalogue record.

## Access, provenance and fail-closed decision

Source pages were inspected via public web PDF page rendering and accessible institutional/publisher HTML on **2026-11-10**. No original PDF bytes, local SHA-256, HTTP receipt headers or precise retrieval timestamp were retained. `source_file_sha256=null`, `independent_human_review=false`, `full_item_read=false`, and `canonical_track_g_admission=false` are intentional. The *Semiotica* publisher explicitly states **article content cannot currently be accessed**; no article-body page, PDF comparison or paywall bypass is asserted.

**R006 (exclusive selection authority):** preserve at least four publication-level identities; do not use shared year, title, wording or the 2013 shorthand as a DOI/ISBN equivalence rule. The 2006 thesis is a candidate for lawful source retrieval and possible future Track G consideration, **not an admitted record**. **R008:** maintain five levels versus four views as a documented, source-located counterexample to a simplistic revision chronology; no new comparator study is justified. **Integration:** review this corrected existing PR's final head and exact-source evidence before a guarded merge. No R005/R006/shared registry or export edits belong to this branch.

**Remaining gate:** obtain lawful original body files (2006 *Semiotica* paper, 2006 thesis and a specifically identified UTP book printing, as available), compute SHA-256 from actual bytes in a trusted environment, document exact text/passages read and compare the editions. Frozen v1 §10 and R006 corpus selection remain open. **R006 #6 / R007 #7 / R008 #8 remain OPEN**; absence of sources cannot be replaced by model agreement.
