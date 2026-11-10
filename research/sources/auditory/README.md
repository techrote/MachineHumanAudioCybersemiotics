# Auditory evidence search — MHAC-R005 coverage memo

[Search inventory](../../searches/auditory/README.md) · [Recovery checkpoint](../../searches/auditory/recovery-2026-11-03/README.md) · [Protocol §5](../../protocol/PROTOCOL-v1.md#5-track-e-sources-and-searches) · [Duplicate candidates](DUPLICATE-CANDIDATES.md)

**Coverage remains limited and Track E is not complete.** The 3 November 2026 recovery executed the frozen OpenAlex searches: seven query families have complete runs; broad EQ1 remains partial at the observed anonymous daily-budget boundary. The available ICAD series index and five additional review bibliography sections were recovered. Retrieval counts are not included-study or independent-sample counts.

The cutoff remains **2026-10-04**, although recovery occurred on **2026-11-03**. No frozen concept block, language rule or eligibility criterion changed. The older 13 October observations are preserved, including access failures, abbreviated reference lists and subsequent manifestation-based corrections. The old statement that no bibliographic database was searched describes the October fallback only.

## Inventory and reproducibility

| Retained layer | Search records | Occurrences | Meaning |
|---|---:|---:|---|
| Preserved 13 October branch | 128 | 2,244 | Web routes, known-item lookups, 780 ICAD filenames, original and manifestation-based reference lists |
| Three OpenAlex invocations | 15 | 17,456 | Includes two planned families skipped after an earlier family's access failure; every actual retrieval remains separate |
| Georgia Tech ICAD series | 1 | 1,269 | Distinct repository items, including proceedings and media |
| C9 known-item navigation | 1 | 26 | Combined web-tool batch; no query-specific total or pagination |
| Five new bibliography sections | 5 | 488 | 85 + 91 + 47 + 80 + 185 ordered references |
| **Auditory-lane total** | **150** | **21,483** | Discovery occurrences; overlap and eligibility remain for R006 |

The [database summary](../../searches/auditory/recovery-2026-11-03/database/database-execution-summary.json) verifies **11,898 distinct OpenAlex work IDs** across all three invocations. A service ID is not automatically a verified publication identity. Neither occurrence nor ID counts measure scientific coverage or study independence.

The [recovery builder](scripts/build_r005_recovery_records.py) verifies response hashes, decompressed payload hashes, per-run counts and ordered registration. It refuses conflicting history and preserves later revisions. Retained metadata permits offline re-registration without querying a changing index. Private PDFs and original API abstract indexes are not republished; derivatives identify original hashes and retrieval routes. A new online fetch is a new observation, not reproduction of historical bytes.

## Channel outcomes and impact

| Channel | Actual outcome | Consequence / next action |
|---|---|---|
| **C1 OpenAlex** | EQ2–EQ8 each have a complete run; EQ1 partial. [Audit](../../searches/auditory/recovery-2026-11-03/database/AUDIT.md). | Broad retrieval is incomplete. The final EQ1 prefix is sorted by date/title, not randomly sampled. Continue in a new immutable invocation when allowance permits and reconcile overlap. |
| **C2 Crossref** | Current metadata probe succeeded; its API does not implement the frozen Boolean title/abstract semantics. | Available for DOI/metadata checking; no equivalent EQ1–EQ8 execution claimed. October refusal remains historically true. |
| **C3 ACM DL** | No owner-run database export supplied; original access gap retained. | HCI coverage relies on other channels. ACM web results are not an ACM database search. |
| **C4 IEEE Xplore** | No owner-run database export supplied; access gap retained. | Engineering and warning-system coverage remains uncertain. |
| **C5 ICAD** | All 13 available Georgia Tech series pages enumerated, with issued-year outcomes for 1992–2026. [Manifest](../../searches/auditory/recovery-2026-11-03/icad/MANIFEST.json). | Index completion does not establish venue completion. 1992 is absent; the 2026 bin is a 2025 companion book issued in 2026, and the actual 2026 route returned 503. Empty bins do not prove no conference occurred. |
| **C6 SAGE / T&F** | Publisher database searches unexecuted; explicit access gaps retained. | Human-factors coverage relies on OpenAlex, references and web routes. |
| **C7 PsycINFO / WoS / Scopus** | Subscription searches unexecuted; no supplied exports. | Psychology, citation-index and non-English coverage remain uncertain. |
| **C8 web search** | October W1–W9, extended W1 and seven translated W1 queries retained; no pagination. | Supplementary discovery only; ranking and recall unknown. |
| **C9 chaining** | Original Nees–Liebman included-list and FRA bibliography retained; five additional sections recovered. | Backward chaining remains for other EQ8 reviews and subsequently included reports. Forward chaining has not run; C1 budget is exhausted. C9 is not complete. |
| **C10 grey literature** | October report/thesis searches retained; new thesis/report bibliographies recovered. | Purposive transport, defence and thesis routes do not establish exhaustive grey coverage. |

The [historical database gate](../../protocol/gates/HG-R002-DATABASE-ACCESS.md) records the earlier owner-access request. Successful API access does not constitute a human authorization record or remove remaining channel and quota gaps.

## OpenAlex query execution

| Frozen family | Complete matching records, or retained subset | Status |
|---|---:|---|
| EQ1 broad cue-family recall | Final sorted run 4,200 / 9,368 reported; 4,549 distinct IDs across attempts | **Partial** |
| EQ2 urgency, hazard and severity | 556 / 556 | Complete run |
| EQ3 voice, human likeness and affect | 76 / 76 | Complete run |
| EQ4 uncertainty | 585 / 585 | Complete run |
| EQ5 learning and retention | 2,112 / 2,112 | Complete run |
| EQ6 monitoring sonification | 537 / 537 | Complete run |
| EQ7 interruption and workload | 153 / 153 | Complete run |
| EQ8 existing reviews | 4,652 / 4,652 | Complete run; references not all chained |

Default relevance paging exposed duplicate IDs; affected runs remain partial even where raw counts equal the service total. Sorted recovery preserves every frozen term and field scope. Completion requires stable reported totals and equal distinct-ID counts. Separate attempts are never overwritten. Bounded temporary-load retries follow observed Retry-After values. The final run stopped at **2026-11-03T01:06:18Z**, when the response reported zero credits; no quota or authentication workaround was used.

October negative/null-oriented W9 probes, grey routes and non-English translations remain in the [original export](../../searches/auditory/exports/AUDITORY-WEBSEARCH-2026-10-13.json). Database searches have no language, type or open-access filter. This does not establish exhaustive null-result or non-English coverage. The [A7 date-derived inventory](../../searches/auditory/recovery-2026-11-03/database/A7-INVENTORY.json) retains 5,404 occurrences (4,029 distinct OpenAlex IDs) dated 2021-04-01–2026-10-04 across all query families. It is an offline subset of existing metadata, not a new executed query or complete cue-family update search; it inherits EQ1's incomplete retrieval. No dates were missing in this retained subset calculation.

## Review bibliographies and version identity

| Source / section | Verified range or boundary | Occurrences |
|---|---|---:|
| Nees–Liebman original tool-rendered included list | Discovery rendering without hash-bound page coordinates; truncation preserved | 68 |
| Nees–Liebman 52-page accepted manuscript, included list | October manifestation-bound export; replaces the rendering for fidelity checks | 69 |
| FRA 2022 bibliography | Original tool list and PDF-derived list; deliberately retained as separate occurrences | 115 + 115 |
| Nees–Liebman accepted manuscript, general references | PDF pp. 33–42; distinct from its included-list section | 85 |
| McFarlane et al. 2020 sleep-inertia review | PDF pp. 14–18 | 91 |
| Totland 2021 process-industry thesis | Printed/PDF pp. 42–47 | 47 |
| Edworthy 2013 medical audible-alarm review | PDF pp. 5–6 / printed pp. 588–589; references 1–80 | 80 |
| Ruskin, Corvin and Rice 2020 ATC report | Printed/PDF pp. 55–79; repository author order differs and is preserved | 185 |

November source files were lawfully obtained and inspected for identity and bibliography boundaries. This is **selected-range reading**, not empirical extraction. Hashes, access outcomes and locators are in [reference recovery](../../searches/auditory/recovery-2026-11-03/references/README.md) and [review recovery](../../searches/auditory/recovery-2026-11-03/reviews/README.md). The FRA reacquisition matches its October hash and is not another bibliography run.

**Version reconciliation:** `SRC-NOV-NEES-LIEBMAN-2023-PREPRINT` describes the older 47-page 9.8.22 manuscript. The recovered 52-page accepted manuscript is separately registered as `SRC-AUD-NEES-LIEBMAN-2023-AM`, SHA256 `5585a4d7d64d84edaef80ab322863a273152e85eac572da4bbeec245540e2fbf`. Historical `SRCH-R005-RLNLAM` identifies these later bytes in its boundary although its basis pin points to the older source. That historical pin does not establish manifestation equivalence and must not transfer page numbers. New family links distinguish both manuscripts and the Version of Record.

Reviews provide discovery paths, never duplicate primary observations. [Sixteen historical publication/sample-overlap flags](DUPLICATE-CANDIDATES.md) remain unadjudicated, including Walker conference/journal spearcon reports, Garzonis and Warnock thesis/article families, and rail-crossing alert reports. Shared authors, titles or paradigms justify inspection; they do not prove shared or independent samples.

## Known-item check and residual bias

The corrected October [known-item table](../../searches/auditory/exports/KNOWN-ITEM-CHECK-R005.csv) has **69 entries: 38 located, 10 possible and 21 not located**. It evaluates earlier web routes and has not been recomputed against the enlarged corpus. A title match does not establish eligibility, text access or independence.

Residual biases include incomplete EQ1 retrieval, missing publisher/subscription channels, repository-year gaps, selective web indexing, limited non-English discovery and unfinished chaining. The date-sorted EQ1 prefix may overrepresent earlier work. Repository dates and item types require screening; an issued year does not establish the conference year or cutoff eligibility. Absence from this inventory never establishes absence of a relevant study.

No item was excluded in recovery. Inaccessible reports remain candidates; unavailable full text must become `awaiting_text`, not exclusion. Primary-text requests follow actual title/abstract screening. No methods, outcomes or numerical estimates are inferred from snippets or bibliographies.

## Stopping, dependency reconciliation and handoff

This is a **checkpoint**, not Track E completion. Current API allowance is exhausted and inaccessible channels retain gaps. Protocol §11 also requires deduplication, resolved screening or awaiting text, and complete backward chaining; those conditions remain unmet. No target paper count is a stopping rule.

Issue #6 depends on #5, while protocol §11's global search-completion rule includes work owned by #6. The safe staging is to land R005 search evidence and bounded R006 infrastructure/identity work as partial PRs, keep both issues open, and defer the completed corpus and dependent #7–#9 acceptance. This explicitly records the dependency tension without silently relaxing either contract.

| Work | Actual state |
|---|---|
| Occurrence preservation | All retained production exports registered; original branch history retained |
| Frozen families | Seven complete C1 families; EQ1 partial; other database gaps explicit |
| Venue coverage | Available ICAD series enumerated; venue-year gaps remain |
| Identity, eligibility and studies (#6) | Pending; no selected corpus or included primary studies declared by R005 |
| Brier/theory/empirical analysis (#7–#9) | Dependency gates remain; discovery counts establish no analysis readiness |
| Final refresh (#17) | Use actual later refresh date and retain original cutoff and observations |

Recovery used ChatGPT (GPT-6 Astra Pro), Python, public HTTPS, web search and Poppler. The integrator, database and ICAD/review agents divided source batches; another AI pass checked bibliography boundaries. These are correlated checks, not independent human screening, librarian review, external scholarly review or participant validation. Structural CI verifies integrity and reproduction, not scientific truth.

## Targeted known-item navigation — 10 November 2026

A supplementary, **non-database** C8/C9 recheck located ten bibliographic candidate routes among the 21 entries historically marked `not_located` in October's 69-entry known-item benchmark: K02, K07, K29, K34, K38, K42, K44, K45, K52 and K53. The dated [observation ledger](../../searches/auditory/known-item-recheck-2026-11-10/OBSERVATIONS.json) and [reproduction limitations](../../searches/auditory/known-item-recheck-2026-11-10/README.md) retain exact queries, stable source locators, access extent and an unresolved DOI/author rendering conflict for K29. These routes are **candidates for R006 reconciliation**, not new independently adjudicated publications or studies.

The historical 38 located / 10 possible / 21 not located counts have **not** been revised or recomputed over OpenAlex and the newer discovery layers. This web batch has no lossless source-result export, unique hit count or verified PDF source hashes and must not be described as completed C1, C2 or other subscription database queries. Direct API access from this execution environment encountered DNS errors; that does not change the historical 3 November OpenAlex results, nor does it establish a new OpenAlex quota observation. EQ1, review chaining, access and eligibility remain incomplete.


## Remaining historical known-item navigation — 10 November 2026

A second additive [R005 C8/C9 reference audit](../../searches/auditory/known-item-remainder-2026-11-10/README.md) targeted the **11 historically `not_located` entries not covered by the earlier 10-item pass**: K04, K09, K12, K33, K35, K50, K54, K56, K64, K67, K68. The [observation ledger](../../searches/auditory/known-item-remainder-2026-11-10/OBSERVATIONS.json) documents bibliographic and source-navigation routes, including a **provisional K50 page-range conflict** and the malformed K54 DOI. Ten have original publisher/institutional/conference or curated-index support; K50 is weaker third-party navigation. PDF title search previews do not constitute full-text reading.

**These are candidates only.** The original 69-item baseline remains 38 located / 10 possible / 21 not located, with both later supplements kept separate; no revised empirical recall score, new C1/C2 database run, successful EQ1 continuation, source hash, complete report retrieval, R006 eligibility, participant sample or corpus freeze is asserted. Highest-value next work is the immutable EQ1 remainder and review/included-report citation chaining, with the frozen publication cutoff unchanged at 2026-10-04. Issue #5 remains open.

## Focused construction-safety review chaining — 10 November 2026

One supplementary **C9 backward-citation navigation** examined the 2022 Dang et al. [construction-auditory-safety review](https://pmc.ncbi.nlm.nih.gov/articles/PMC9740817/) (DOI 10.3390/s22239135). Five selectively chosen reference routes (#33, #38, #39, #101, #102) were cross-read against publisher, PubMed, university or conference metadata. The [dated observation ledger](../../searches/auditory/c9-construction-review-2026-11-10/OBSERVATIONS.json) and [bounded methods/handoff](../../searches/auditory/c9-construction-review-2026-11-10/README.md) preserve stable locators, possible transport context, and deliberate non-auditory comparator cases.

This is a **partial review-to-reference route**, not the full review bibliography or finished EQ8 review chaining. It adds **zero canonical search-run/hit records and zero screened/included studies**: original totals, October baseline, R006 identity authority and frozen 2026-10-04 cutoff remain unchanged. Citation numbers may refer to existing R005 occurrences; R006 must deduplicate before screening. The first priority remains lawful EQ1 completion (4,200/9,368 last sorted run); this C9 tranche is an independent feasible route while the OpenAlex API cannot be reached from the current environment. No source PDF/response hashes, full empirical reading, human verification or citation-chain completeness are claimed.


## Cyber-warning auditory-alert contrary case — 10 November 2026

The [C8 cyber-warning negative-case shard](../../searches/auditory/c8-cyberwarning-negative-2026-11-10/README.md) source-navigated two publisher-readable empirical papers (Zhang, Berger & Chen 2024; Datta et al. 2021) and a separate publisher-abstract-only expert-judgement comparator (Cooper et al. 2020). The [provenance ledger](../../searches/auditory/c8-cyberwarning-negative-2026-11-10/OBSERVATIONS.json) pins exact web-search queries and source sections. Zhang already appears as an unresolved EQ1 record `HIT-R005R-C1RECOVERY-EQ1-00611`, so this is **not** a new discovery hit or independent study.

A useful contrary caution for later screening is that the 2024 source reports an earcon hit-rate advantage over short speech but also higher false alarms in both audio arms versus no audio, with no significant across-condition discrimination (d-prime) result; faster responses do not by themselves establish improved safety. Datta reports different recognition and intended-action measures, and Cooper's expert preferences are not comparable end-user performance. Results remain **author-reported, selected publisher HTML/abstract readings**, not R009 empirical extraction, accepted evidence, figure/PDF verification or human review. Three bibliographic routes were examined with zero changes to the historical 150/21,483 search/occurrence baseline, 69-item known-item table, R006 eligibility, independent samples, or the frozen cutoff. EQ1 remains partially retrieved at 4,200/9,368; other channel and C9 gaps remain.
