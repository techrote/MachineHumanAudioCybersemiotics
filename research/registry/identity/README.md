# R006 publication-identity ledger

[Issue #6](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/6) · [Protocol §6](../../protocol/PROTOCOL-v1.md#6-screening-identity-retrieval-and-extraction) · [Record contract](../../../schemas/README.md)

## Bounded completed work

The [Hermann 2008 tranche](R006-HERMANN-2008.json) links three preserved R005
occurrences to the existing R004 source `SRC-REL-HERMANN-2008` revision 1,
*Taxonomy and Definitions for Sonification and Auditory Display*. Every returned
URL is exactly the source's already verified ICAD PDF URL. No fuzzy title match,
new source record, eligibility decision or inference about participants is used.

| Preserved occurrence | New revision | Disposition |
|---|---:|---|
| `HIT-R005-IW6-07` | 2 | Resolved to the existing source; representative within this tranche. |
| `HIT-R005-IW9-08` | 2 | Duplicate occurrence of `HIT-R005-IW6-07@2`; discovery path retained. |
| `HIT-R005-C5LIST-0644` | 2 | Duplicate occurrence of `HIT-R005-IW6-07@2`; listing ordinal retained. |

The representative's query started at 02:12:33 UTC on 13 October 2026, before
IW9 at 02:12:35 and the directory listing at 06:23:58. This is an ordering within
these three occurrences, not a claim of first discovery across the programme.
The exact search references, original ordinals, input/output revision hashes,
actual resolution time and agent identity are in the JSON ledger and its
[CSV view](R006-HERMANN-2008.csv).

The existing source's PDF hash and metadata-verification status are inherited
from R004. This task compared repository records; it did not retrieve or read
the paper again. Source access, reading extent, rights and scientific claims
remain as previously recorded. The new assistance record describes that narrow
scope and explicitly identifies the same-agent review limitation.

## What this does not complete

Three occurrences now resolve to one existing publication. They do not create
three publications, three studies or three independent samples. Other search
occurrences remain outside this tranche, and unresolved discovery is still
unresolved. Nothing here includes or excludes Hermann's paper under Track E or
selects it for Track G close reading.

Issue #6 remains open for the broader publication reconciliation, actual
screening and retrieval decisions, study/experiment/sample ledger, verification
passes, selected corpus snapshot and residual-bias assessment. Downstream issues
#7–#9 do not acquire a completed corpus gate from these identity links. A PR
containing this tranche must use `Refs #6`, not a closing keyword.

## Exact-identifier review queue — 6 November 2026

The read-only `python -m tools.identity_queue` command validates the live registry
and proposes unresolved occurrences whose explicit DOI or normalized resource URL
matches an active, non-alias source's verified identifier. It preserves latest
hit/source revision pins, original search pins and ordinals. Ambiguous sources or
conflicted source metadata/identifiers receive `conflict_review`; nothing is
resolved automatically. It does not use titles, infer a DOI from a publisher path,
collapse URL query order or make transitive identity links.

The [dated queue](R006-IDENTITY-QUEUE-20261106.json) was generated from accepted
main `423649d18c54cbf90bf7bf79d49ba69b29f03848`: **22,494 unresolved occurrences,
30 candidate occurrences, 22,464 unmatched occurrences, zero conflict-review
occurrences**. These counts span all registered search lanes, including pilot and
theoretical discovery; they are not a Track E flow or independent-publication
count. The queue includes a SHA-256 of all ordered input records and history.
It is a dated checkpoint, not a perpetually current generated registry export.

To reproduce from that unchanged canonical registry:

```sh
mkdir -p build
python -m tools.identity_queue > build/identity-queue.json
cmp build/identity-queue.json research/registry/identity/R006-IDENTITY-QUEUE-20261106.json
python -m unittest tests.test_identity_queue -v
```

Next, review each candidate's original occurrence/export and the pinned source's
identifier provenance. Resource equality may identify a shared landing page;
it is not publication identity by itself. If warranted, create a bounded,
append-only resolution tranche using the Hermann builder as a worked example,
retaining every discovery path and recording the actual verification performed.
Unmatched candidates need separate identity work; no title-only screening or
source reading is inferred from this queue.

AI disclosure: Codex/GPT-6 prepared the tool, nine fictional regression tests and
the dated queue on 6 November 2026. Verification is local registry comparison and
software self-review; no fresh paper retrieval, human adjudication, independent
scientific review, eligibility decision or new canonical evidence was performed.
Issue #6 and the corpus gate remain open.

## DOI/title adjudication — 6 November 2026

The [fixed twelve-occurrence tranche](R006-DOI-TRANCHE-20261106.json) advances
the earlier candidate queue into recorded publication identity. Each occurrence's
explicit DOI and full title agree with the retained export at its original
ordinal and the existing source's verified Crossref metadata. Export manifests,
compressed public OpenAlex pages and decompressed payload hashes were checked;
the ledger records exact file/item locators and revision hashes.

| Existing publication | Newly linked duplicate occurrences | Existing representative |
|---|---:|---|
| Blattner et al. (1989), *Earcons and Icons* | 6 | `HIT-R004-LK-BLATTNER-1989-01@1` |
| Edworthy et al. (1991), *Relationship between Warning Sound Parameters and Perceived Urgency* | 4 | `HIT-R004-LK-EDWORTHY-1991-01@1` |
| Hellier et al. (1993), *Quantifying and Predicting the Effects of Different Warning Parameters on Perceived Urgency* | 2 | `HIT-R004-LK-HELLIER-1993-01@1` |

All twelve original revisions remain intact; new revision 2 links each occurrence
to its already resolved R004 representative. The two crossed R004 lookup hits
are resolved to the actual returned publication, independently of the lookup's
query name. The separate abstract-only record returned by the Blattner lookup
has DOI `10.1145/67880.1046599` and is **not** collapsed into the full article's
`10.1207/s15327051hci0401_1` identity. Source records and their access/reading states
are unchanged.

This reduces all-lane unresolved occurrences from **22,494 to 22,482** and leaves
**18** of the original 30 queue candidates unresolved. These are discovery-level
counts, not Track E flow counts or independent studies. No source, screening,
study or sample records were created. The older queue is retained as a historical
input, not overwritten to look current.

```sh
python research/registry/identity/scripts/build_r006_doi_tranche.py --check
python -m unittest tests.test_screening_doi_tranche -v
python tools/validate.py
python -m tools.identity_queue > build/identity-queue-current.json
```

The builder reproduces a fixed scope and preserves later canonical revisions;
frozen ledger drift stops it before writes. It does not admit new candidates.
Next work is adjudication of the remaining 18 candidates, followed by broader
publication reconciliation and actual protocol-governed screening. Issue #6 and
the corpus gate remain open; #7–#9 do not gain a completed corpus prerequisite.

AI disclosure: one Codex/GPT-6 agent performed metadata comparison, software
self-review and nine adverse-input/history tests on 6 November 2026. No fresh
online source retrieval or paper reading, independent human adjudication,
scientific acceptance or participant evaluation occurred. Original private API
responses were not re-inspected; public OpenAlex metadata derivatives and the
preserved Crossref/bibliographic exports were checked. These support the bounded
identity decision, not empirical extraction or study independence.

## Remaining explicit-DOI batch — 6 November 2026

The [ten-occurrence ledger](R006-REMAINING-DOIS-20261106.json) resolves the
remaining explicit-DOI matches in the original 30-candidate queue. Full titles
were compared after case and whitespace normalization only; punctuation, words
and digits were retained. Each DOI/title pair agrees with its original export
ordinal and the accepted source's verified metadata. Source verification is
inherited from the pinned accepted record, not a new paper reading.

| Existing publication | Occurrences | Disposition |
|---|---:|---|
| Nees and Liebman (2023), published review | 4 | Duplicates of `HIT-R002-PA6-02@1` |
| Edworthy, *Medical audible alarms: a review* | 2 | One representative at revision 2; one duplicate |
| McFarlane et al. (2020), sleep-inertia review | 2 | One representative at revision 2; one duplicate |
| Murphy (2006), *A Semiotic Approach to the Design of Non-speech Sounds* | 1 | Duplicate of existing R004 occurrence |
| Gaver (1986), *Auditory Icons* | 1 | Duplicate of existing R004 occurrence |

The first fixed occurrence for Edworthy and McFarlane becomes the representative
within this batch; no claim of first global discovery is made. Nees's published
version stays `SRC-NOV-NEES-LIEBMAN-2023`; its accepted manuscript remains a
distinct source. No version alias or publication-family claim is introduced.
Edworthy's original OpenAlex date `2012-10-26` and the bibliographic issue year
`2013` remain untouched; the accepted source separately records online-first
`2012-10-25`. Identity agreement does not resolve that one-day metadata discrepancy
or justify overwriting the issue year.

All ten original discovery revisions and original search paths/ordinals remain
intact. Retained export manifests, compressed OpenAlex pages and decompressed
payload hashes were checked, alongside the bibliography's source-page/entry
locators. The ledger preserves input/output revision hashes and exact source
pins. Public metadata derivatives were checked; private raw API responses and
article texts were not re-read.

All-lane unresolved discovery falls **22,482 → 22,472**. **Eight URL-only
candidates** remain from the original queue; **22,464** other unresolved
occurrences still have no exact match proposed by that queue. These are
occurrence-level bookkeeping counts, not a selected Track E corpus or independent
studies. Two representatives and eight duplicates create no new sources,
screening decisions, studies or samples. Issue #6 and its corpus gate remain open.

```sh
python research/registry/identity/scripts/build_r006_remaining_dois.py --check
python -m unittest tests.test_screening_remaining_dois -v
python tools/validate.py
```

Next, adjudicate the eight URL-only candidates against their retained discovery
exports and publication-specific resource provenance; a shared URL alone is not
proof of publication identity. Broader publication reconciliation, actual
screening, study/sample relationships and corpus selection remain necessary.
AI assistance: one Codex/GPT-6 agent, 6 November 2026, metadata comparison,
software self-review and ten regression tests. No fresh online retrieval,
independent human adjudication or scientific acceptance is claimed.

## URL-resource batch and original queue completion — 6 November 2026

The [eight-occurrence ledger](R006-URL-TRANCHE-20261106.json) adjudicates the
remaining URL-only matches from the original 30-candidate queue. Exact returned
URLs, original query, run, result ordinal and raw result label were checked in
the hash-bound discovery exports. Each URL equals an accepted source revision's
verified **publication-specific resource**, with its recorded metadata and
identifier provenance pinned in the ledger. This inherits the accepted source
verification; no current URL availability or fresh page/PDF reading is claimed.

| Existing publication resource | Occurrences | Disposition |
|---|---:|---|
| Edworthy review, PMC article `PMC3628049` | 3 | Duplicates of its existing DOI-resolved occurrence |
| Brier (2011), Signs article `26864` | 1 | Duplicate of `HIT-R003-B04-06@1` |
| Nees/Liebman published review, Lafayette record `gx41mk40g` | 1 | Duplicate of `HIT-R002-PA6-02@1` |
| Ruskin et al. report, ROSA P `dot/59041` PDF | 3 | One representative at revision 2; two duplicates |

Several original labels are merely hostnames (`pmc.ncbi.nlm.nih.gov`,
`tidsskrift.dk`, `ldr.lafayette.edu`). These remain unchanged and are not promoted
to bibliographic titles. The publication link rests on the exact resource and
its accepted verification provenance, not an inferred title or same-host match.
The shorter Ruskin result title is also retained; no title correction or version
alias is introduced. Pilot records retain their original search references and
pilot status. Brier's abstract-only access state and every other source's
access/reading/rights assertions remain unchanged.

All-lane unresolved discovery falls **22,472 → 22,464**. The original fixed queue
is now fully adjudicated: **12 + 10 + 8 = 30 occurrences**, spanning ten existing
source IDs. Its historical snapshot stays intact. Re-running the current exact
identifier queue returns **zero candidates and 22,464 unmatched unresolved
occurrences**. This completes a bounded identity queue, not issue #6, the corpus
gate or programme-level deduplication. No source, eligibility decision, study or
sample was created, and independent-publication/sample counts are not inferred.

```sh
python research/registry/identity/scripts/build_r006_url_tranche.py --check
python -m unittest tests.test_screening_url_tranche -v
python tools/validate.py
python -m tools.identity_queue > build/identity-queue-current.json
```

Next work must expand beyond exact matches to the currently registered verified
identifiers: inventory unresolved DOI/metadata groups and preserve contrary
identifiers, then adjudicate new publication identities in bounded batches under
protocol §6. Do not automatically merge titles, publication versions or studies.
Actual eligibility screening, study/sample relationships, the selected corpus
and bias assessment remain outstanding. Issue #6 stays open; #7–#9 do not gain a
completed corpus prerequisite from these identity decisions.

AI disclosure: one Codex/GPT-6 agent, 6 November 2026, local metadata comparison,
software self-review and ten regression tests. No new online retrieval, source
reading, independent human adjudication or scientific acceptance occurred.

## New publication identities from recurring DOI groups — 6 November 2026

The [fixed plan](R006-NEW-DOI-PLAN-20261106.json) and
[adjudication ledger](R006-NEW-PUBLICATIONS-20261106.json) extend identity work
beyond already registered verified sources. Fresh Crossref single-work HTTP 200
responses supplied bibliographic identity metadata for five explicit DOIs. The
retained [metadata derivatives](metadata/) contain title, authors, dates and
publication fields, request URL/time and original-response SHA-256. Abstracts and
unrelated fields were omitted, and original raw response bytes are not committed.
No article or abstract was read, and no article availability or licence is inferred.

| New metadata-only source | DOI | Resolved occurrences |
|---|---|---:|
| Walker et al., *Spearcons (Speech-Based Earcons) Improve Navigation Performance in Advanced Auditory Menus* | `10.1177/0018720812450587` | 6 |
| Edworthy and Stanton, *A user-centred approach… 1. Methodology* | `10.1080/00140139508925267` | 6 |
| Garzonis et al., *Auditory icon and earcon mobile service notifications* | `10.1145/1518701.1518932` | 7 |
| Perry et al., *Cough Once for Danger…* | `10.1518/001872007x249929` | 4 |
| Blattner et al., *Earcons and Icons… (Abstract only)* | `10.1145/67880.1046599` | 6 |

Each selected occurrence's explicit DOI and full title agree with the retained
OpenAlex, Crossref or original web-search export and the fresh metadata. Hashes,
ordinals and work IDs were checked. The pilot Walker result includes the full
title followed by authors; its raw label and pilot discovery path are retained.
Five representatives and 24 duplicates preserve every original discovery revision.
The five new source records have verified **metadata**, `metadata_only` access,
unknown article-reuse rights, no manifestations, and no article-reading claim.
These five publication identities do not establish five independent studies.

Dates remain separate assertions. The source `publication_date` explicitly uses
Crossref's `published-print` field when supplied; the ledger and captures also
retain `issued` and `published-online`. Walker is online/issued in July 2012 and
print in February 2013. Edworthy's record reports print/issued November 1995 and
online March 2007. Perry's retained OpenAlex date differs from Crossref's date
fields. No original discovery date is rewritten, and no dates are interpreted as
new empirical-study dates. The abstract-only Blattner DOI stays distinct from the
full article DOI `10.1207/s15327051hci0401_1`; no alias, publication-family or
sample-overlap judgment is added.

**Seven reference-list occurrences are deferred**, listed explicitly in the plan
and ledger. Their rendered/extracted references require a separate provenance
check; they were not silently accepted from matching DOI text. The earlier
original 30-candidate queue remains a historical completed batch. This new batch
reduces all-lane unresolved occurrences **22,464 → 22,435**. No eligibility,
screening, study, sample, claim or design records are created; issue #6 and the
corpus gate remain open.

```sh
python research/registry/identity/scripts/build_r006_new_publications.py --check
python -m unittest tests.test_screening_new_publications -v
python tools/validate.py
```

The builder is offline and reuses the fixed captures, not fresh API responses.
Its ledger stops drift before canonical writes and preserves later revisions.
Re-querying Crossref may return changed metadata; retain a new dated capture and
explicit correction rather than overwriting these frozen inputs.
Next: verify the seven deferred reference-list occurrences, then continue bounded
new DOI-group identity batches. Actual screening and study/sample reconciliation
remain separate obligations.

AI disclosure: one Codex/GPT-6 agent performed fresh bibliographic retrieval,
metadata comparison, software self-review and twelve regression tests on
6 November 2026. No independent human adjudication, source-content appraisal,
empirical extraction or scientific acceptance occurred.

## Deferred bibliography identities — 6 November 2026

The [seven-occurrence ledger](R006-REFERENCE-TRANCHE-20261106.json) resolves the
seven reference-list cases deferred by the new-publication batch. The
[source witness receipt](R006-REFERENCE-WITNESSES-20261106.json) records three
fresh HTTP 200 PDF retrievals, all matching the retained original SHA-256 exactly,
and five citation witnesses checked in rendered reference pages.

| Source bibliography inspected | File pages checked | Cited publication identity |
|---|---|---|
| Nees/Liebman accepted manuscript | 36, 49, 51 | Edworthy/Stanton methodology; Perry aviation warnings; Walker spearcons |
| FRA *In-Vehicle Auditory Alerts Literature Review* | 41–42, printed 33–34 | Walker citation spans the page break |
| Ruskin et al. *ATC Signaling Systems* report | 71 | Perry citation, matching retained line/coordinate provenance |

Original export hashes, list/entry ordinals, explicit DOI, full title or declared
short-title prefix, and existing resolved representative were checked. For the
two `RL-NL` model-rendered abbreviated occurrences, a matching full citation in
the hash-matched Nees accepted manuscript supplies **corroboration of the cited
publication identity**. It does not prove faithful transcription of the original
preprint/Academia page, restore omitted text or establish equivalence of review
versions. Original labels, abbreviations and model-render provenance remain in
the old revisions and new verification limits. Outcome-letter prefixes remain
literal discovery text; no result interpretation or independent-evidence count
is inferred. The original partial search statuses are unchanged.

All seven become duplicates of existing publication representatives; no new
source record is created. Target source records remain `metadata_only`: the
cited target articles were not retrieved or read. Inspection was limited to the
selected bibliography citations in the three containing reviews/reports, not
whole-report reading or empirical extraction. Original source states, rights,
source-version distinctions and all discovery revisions remain intact.

All-lane unresolved discovery falls **22,435 → 22,428**. The five-publication
batch now accounts for **29 + 7 = 36** resolved occurrences, with no remaining
exact-identifier candidates for currently registered verified sources. This
closes that bounded identity tranche, not issue #6 or the corpus gate. The
remaining unresolved DOI groups, eligibility screening, study/sample identities,
selected corpus and bias assessment still require work.

```sh
python research/registry/identity/scripts/build_r006_reference_tranche.py --check
python -m unittest tests.test_screening_reference_tranche -v
python tools/validate.py
```

The offline builder reproduces the fixed receipt/ledger and canonical revision
prefixes; it does not re-download PDFs or prove the recorded visual observations.
To repeat the source check, retrieve the receipt's exact URLs, require the same
SHA-256, then inspect its file-page locators. Changed bytes require a new dated
provenance/correction decision. Source PDFs and rendered pages were used locally
and are not committed; the receipt retains exact hashes, URLs and reading extent.
Next: continue bounded new-publication admission from remaining DOI groups, then
perform actual protocol-governed screening without treating metadata identity as
eligibility or sample independence.

AI disclosure: one Codex/GPT-6 agent performed retrieval, bibliography inspection,
metadata comparison, software self-review and ten regression tests on
6 November 2026. No independent human adjudication or scientific acceptance is
claimed. Source-reading extent is logged in the performed assistance record and
receipt; no complete source reading is asserted.

## DOI batch B and reusable admission profiles — 6 November 2026

The [batch B plan](R006-DOI-B-PLAN-20261106.json) and
[ledger](R006-DOI-B-20261106.json) add five metadata-only publication identities
from fresh Crossref bibliographic captures and resolve 23 retained occurrences.
Nine reference-list occurrences are explicitly deferred for source-provenance
checks. Original hit revisions, titles, dates and search paths remain intact.

| Publication identity | DOI | Resolved occurrences |
|---|---|---:|
| Alseid/Rigas, avatar-based e-learning audio cues | `10.1109/dese.2011.34` | 5 |
| Suh et al., Korean auditory-menu spearcons | `10.1177/1071181312561390` | 5 |
| Hofmann et al., in-car SDS notifications | `10.1007/978-3-319-21834-2_11` | 4 |
| Edworthy et al., learning medical alarm sets | `10.1016/j.apergo.2013.10.003` | 4 |
| Petocz et al., warning signal–referent relations | `10.1037/1076-898x.14.2.165` | 5 |

The Hofmann record is a **book chapter**, as reported by Crossref, and is not
silently typed as an article. Print/online/issued dates remain separate in the
captures and ledger. All five sources have verified metadata, `metadata_only`
access, unknown article-reuse rights, no manifestations and no reading claim.
Original article/chapter content, abstracts and empirical results were not read.
An initial metadata request returned HTTP 429; missing captures were retried
sequentially after local implementation work. Only successful HTTP 200 captures
are admitted. The initial failed response bytes/request time were not retained;
the plan records this limitation rather than inventing a precise retry history.

The admission engine now accepts explicit fixed-batch profiles. Its original
default invocation still reproduces the previous five-source/29-occurrence
ledger and canonical prefixes **exactly**. Batch B is a small profile, not a copy
of the full builder. Each configured batch must supply its own task/provenance
narrative and exact expected counts. Duplicate IDs/DOIs, repeated or overlapping
selected/deferred occurrences, sources without qualified occurrence evidence and
unreviewed publication types are rejected before writes. Profiles do not mutate
the original default configuration or expand source scope automatically.

```sh
python research/registry/identity/scripts/build_r006_new_publications.py --check
python research/registry/identity/scripts/build_r006_doi_batch_b.py --check
python -m unittest tests.test_screening_doi_batch_b -v
python tools/validate.py
```

All-lane unresolved discovery decreases **22,428 → 22,405**: five representatives
and 18 duplicates. Nine exact-identifier candidates remain for separately checked
reference-list provenance. No eligibility, screening, study, sample, claim or
design records are created. Publication metadata does not establish independent
studies or corpus readiness. Issue #6 and the corpus gate remain open.
Next: verify the nine deferred references, then reuse fixed profiles for further
new-publication batches while preserving version and sample distinctions.

AI disclosure: one Codex/GPT-6 agent, 6 November 2026, fresh bibliographic metadata
retrieval, retained-export comparison, software self-review and thirteen batch/
profile regression tests. No independent human adjudication, source-content
appraisal or scientific acceptance occurred.

## Batch B deferred references — 6 November 2026

The [nine-occurrence ledger](R006-REFERENCE-B-20261106.json) resolves all nine
reference-list cases deferred by DOI batch B. A fresh HTTP 200 retrieval of the
Nees/Liebman accepted manuscript matches the retained original SHA-256 exactly.
The [witness receipt](R006-REFERENCE-B-WITNESSES-20261106.json) records the request,
bytes/hash, five visually inspected citation witnesses and reading limits.

| Cited publication | Nees AM file/printed page | Occurrences resolved |
|---|---:|---:|
| Alseid/Rigas (2011), avatar-based e-learning | 43 | 2 |
| Edworthy et al. (2014), learning medical alarm sets | 44 | 2 |
| Hofmann et al. (2016), in-car SDS chapter | 46 | 2 |
| Suh et al. (2012), Korean auditory menus | 50 | 2 |
| Petocz et al. (2008), warning signal–referent relations | 40 | 1 |

Original export hashes, reference ordinals, full titles or explicitly abbreviated
title prefixes, DOI suffixes and existing resolved representatives were checked.
Four older `RL-NL` model-rendered short entries receive **publication-identity
corroboration** from the full accepted-manuscript citations. This does not prove
faithful transcription of the original preprint/Academia source or equivalence
of review versions. All original wording, outcome-letter prefixes, dates,
search states and discovery revisions are preserved. In particular, the doubled
`https://doi.org/` prefix in the Edworthy citation remains unchanged; the explicit
DOI suffix agrees with the accepted publication metadata.

All nine become duplicates of existing representatives. The five target sources
remain `metadata_only`, with no new reading/access/rights state or manifestation.
Only the selected bibliography citations in the containing review were checked;
no target article or chapter, whole review, empirical result or eligibility
criterion was read/applied. No source, screening, study or sample record is added.

The bibliography builder now accepts complete fixed profiles, including their
own scope, actor, assistance narrative and exact counts. Duplicate receipt keys,
missing witnesses and count disagreement fail before writes. The original
seven-reference ledger and canonical prefixes still reproduce **exactly**; the
new profile does not mutate the original defaults. Offline checks reproduce the
recorded observations, not the visual inspection itself. Rechecking requires
retrieving the receipt URL, matching the SHA-256 and inspecting the page locators;
changed bytes require a new provenance decision. PDF/renders are not committed.

```sh
python research/registry/identity/scripts/build_r006_reference_tranche.py --check
python research/registry/identity/scripts/build_r006_reference_batch_b.py --check
python -m unittest tests.test_screening_reference_batch_b -v
python tools/validate.py
```

All-lane unresolved discovery falls **22,405 → 22,396**. Batch B now accounts for
**23 + 9 = 32 occurrences** across five publication identities. The current exact
identifier queue has zero candidates; 22,396 unmatched unresolved occurrences
remain. This completes batch B's bounded identity work, not issue #6 or the
corpus gate. Next: admit further DOI-group identities in bounded profiles, then
perform protocol-governed eligibility and study/sample reconciliation. No
completed corpus prerequisite is asserted for #7–#9.

AI disclosure: one Codex/GPT-6 agent, 6 November 2026, fresh same-byte PDF
retrieval, five citation-page inspections, retained-export/metadata comparison,
software self-review and thirteen new profile/provenance regression tests. No
independent human adjudication or scientific acceptance occurred.

## DOI batch C — 6 November 2026

The [fixed plan](R006-DOI-C-PLAN-20261106.json) and
[ledger](R006-DOI-C-20261106.json) add nine metadata-only publication identities
and resolve 38 retained DOI/full-title occurrences. Ten sequential Crossref
single-work requests returned HTTP 200; selected bibliographic derivatives,
request times/URLs and original-response hashes are retained. Abstracts and
target article/chapter texts were not read. Selection for this bounded identity
batch used recurring DOI groups and auditory warning/interface topic labels,
not eligibility, results or outcome direction; it is not exhaustive sampling.

| Publication identity | Resolved occurrences | Deferred occurrences |
|---|---:|---:|
| Graham (1999), collision-avoidance auditory icons | 3 | 3 |
| Sanderson et al. (2009), anesthesiology displays | 6 | 0 |
| Nees et al. (2016), alerted-event memory | 3 | 3 |
| Bellettiere et al. (2014), behavioral-intervention warnings | 5 | 1 |
| Tislar et al. (2018), auditory-display learnability | 3 | 3 |
| Amer/Johnson (2018), computing-event cues | 3 | 3 |
| Brewster (1997), telephone interfaces, **chapter** | 5 | 0 |
| Gygi/Shafiro (2010), environmental-sound design, **chapter** | 5 | 0 |
| Edworthy et al. (2011), alarm-set heterogeneity | 5 | 0 |

Full titles and explicit DOIs agree under case/whitespace normalization only
with fresh Crossref metadata and the hash-bound retained exports. Original
export/page hashes, payload hashes, ordinals and work IDs were checked. Nine
representatives and 29 duplicates preserve every discovery revision. No competing
source with these DOI assertions or exact normalized titles was found in the
existing source records. This is publication identity, not study independence.

Twelve bibliography occurrences and one ICAD-series occurrence remain deferred
because their export formats need a separate provenance check. The ICAD entry
is a venue listing, not a reference-list entry. The dated plan distinguishes it.
The tenth group, Wilcox's alarm-signals article, is **not admitted**: Crossref's
title contains literal HTML and escaped-newline markup and disagrees with all six plain
retained discovery titles under the current comparison. The capture/hash, title,
six original hit pins and reason remain in the plan. No silent tag stripping,
canonical source or occurrence resolution is introduced. A separate reviewed
representation/identity decision is needed; this is not an eligibility exclusion.
The profile checks the retained unadmitted capture's hash before building.

All nine sources remain `metadata_only`, with unknown reuse rights, no
manifestations, family/sample links or reading claims. Both chapters retain their
publication type. Dates stay separate assertions: Sanderson's discovery date
`2009-10-31` remains alongside Crossref's print/issued `2009-12`; Graham's print
1999 and online 2010 assertions remain distinct; Nees's February online/issued
and May print dates are retained. No discovery metadata is harmonized or rewritten.

```sh
python research/registry/identity/scripts/build_r006_doi_batch_c.py --check
python -m unittest tests.test_screening_doi_batch_c -v
python tools/validate.py
python -m tools.identity_queue > build/identity-queue-current.json
```

This small fixed profile reuses the existing builder without changing its
original or batch B outputs. Offline reproduction uses the retained captures,
not new API responses. Frozen ledger disagreement stops canonical writes.
Re-querying may return changed metadata; retain new dated provenance rather than
overwriting these inputs. Original raw Crossref responses are not committed.

All-lane unresolved discovery falls **22,396 → 22,358**. The current exact-identifier
queue has **13 candidates**, zero conflicts and **22,345 unmatched unresolved**
occurrences; the six Wilcox cases remain among the unmatched occurrences. These
are occurrence counts, not a selected corpus. No eligibility, screening, study,
sample, empirical claim or design records are created. Issue #6 and the corpus
gate stay open. Next: separately verify the 13 bibliography/venue cases and the
HTML-marked title representation, then continue bounded identity admission and
protocol-governed screening without inferring study/sample independence.

AI disclosure: one Codex/GPT-6 agent, 6 November 2026, fresh bibliographic metadata
retrieval, retained-export comparison, software self-review and eleven new
regression tests. No independent human adjudication, target-source reading or
scientific acceptance occurred.

## Batch C bibliography provenance — 6 November 2026

The [subplan](R006-REFERENCE-C-PLAN-20261106.json) and
[twelve-occurrence ledger](R006-REFERENCE-C-20261106.json) resolve the twelve
bibliography cases deferred by DOI batch C. The [witness receipt](R006-REFERENCE-C-WITNESSES-20261106.json)
records three fresh HTTP 200 PDF retrievals matching the retained original bytes,
with eight selected citation witnesses checked on rendered bibliography pages.

| Containing source inspected | File pages | Printed pages | Target identities |
|---|---|---|---|
| Nees/Liebman accepted manuscript | 33, 43, 45, 49, 51 | Same | Amer (general and meta-analysis bibliographies), Graham, Nees, Tislar |
| FRA auditory-alert literature review | 36, 40 | 28, 32 | Graham, Nees |
| Totland process-industry alarm thesis | 42 | 42 | Bellettiere |

Totland's previously retained temporary download alias returned HTTP 404.
The stable public OpenFile endpoint supplied a fresh anonymous alias returning
the same 821,130-byte PDF. The receipt retains the stable filelink URL, success
status/hash and actual alias-fetch time; temporary alias/redirect URLs are omitted.
The failed response bytes and precise request time were not retained. The initial
batch receipt was interrupted by the expired alias; the successful Nees/FRA
retrievals recorded here were repeated afterward. No earlier request times or
access permissions are invented, and no access restriction was bypassed.

Every original export/hash/ordinal, citation title and DOI, source/page locator
and existing representative was checked. Totland's coordinate-bearing reference
export remains unchanged, with occurrence ID, PDF/printed page and line boxes
available at the pinned export locator. Four older `RL-NL` model-rendered short
entries receive publication-identity **corroboration** from full Nees AM citations.
This does not establish faithful original-preprint transcription, review-version
equivalence or empirical findings. Original outcome letters, wording, discovery
paths/dates, partial search states and all revisions remain intact.

All twelve become duplicates of existing representatives across five publication
identities. Target source records remain `metadata_only`: no target article or
whole review/report/thesis was read, and no source access/rights/reading state,
source alias, screening decision, study or sample is introduced. Only the eight
selected bibliography citations were inspected; neighbouring page text is not
accepted evidence for unrelated claims.

The subplan hash-pins its parent DOI plan and partitions its thirteen deferred
entries into twelve checked cases plus **one remaining ICAD-series venue case**.
Missing or duplicated partition entries and changed parent bytes fail before
writes. The Totland case explicitly uses the coordinate-bearing reference format;
unreviewed export labels now fail rather than falling through that branch. Both
older reference-batch ledgers and canonical prefixes still reproduce exactly.
Historical DOI-batch tests check the original deferral and that batch's output
inventory, allowing later canonical revisions; append-only history validation
continues to guard those later resolutions.

```sh
python research/registry/identity/scripts/build_r006_reference_batch_c.py --check
python research/registry/identity/scripts/build_r006_reference_tranche.py --check
python research/registry/identity/scripts/build_r006_reference_batch_b.py --check
python -m unittest tests.test_screening_reference_batch_c -v
python tools/validate.py
```

All-lane unresolved discovery falls **22,358 → 22,346**. Batch C now accounts for
**38 + 12 = 50 resolved occurrences** of its 57 reviewed occurrence assertions.
One venue-listing case and all six Wilcox HTML-title cases remain unresolved;
the current exact-identifier queue has one candidate, zero conflicts and 22,345
unmatched unresolved occurrences. This closes the bibliography subplan, not issue
#6, the corpus gate or programme deduplication. Next: review the ICAD venue export
and the title representation separately, then continue bounded identity work and
actual protocol-governed screening without inferring study/sample independence.

The offline builder reproduces the recorded observations, not the visual check
itself. Rechecking requires matching the receipt's hashes and inspecting its page
locators; changed bytes require new provenance. Source PDFs/renders are not
committed. AI assistance: one Codex/GPT-6 agent, 6 November 2026, public retrieval,
eight citation-page inspections, retained-export/metadata comparison, software
self-review and fourteen new regression tests. No independent human adjudication
or scientific acceptance occurred.

## Batch C venue and title-presentation completion — 6 November 2026

The [fixed residual plan](R006-C-FINAL-PLAN-20261106.json) and
[seven-occurrence ledger](R006-C-FINAL-20261106.json) resolve the one venue case
and six Wilcox occurrences left after the bibliography subplan. Fresh Crossref,
PubMed and Georgia Tech identity requests all returned HTTP 200. Selected
bibliographic derivatives retain URLs, times and original-response hashes;
original response bytes are not committed.

**Wilcox's title representation is an explicit, fixed decision.** The raw
Crossref title contains exact italic tags and an actual **U+000A line feed**,
which JSON displays as an escaped newline. It is not a two-character literal
backslash followed by `n`. The dated raw title is preserved in the original and
fresh captures. The [presentation derivative](metadata/20261106-c-final-wilcox-presentation.json)
removes only the exact italic-tag strings and collapses whitespace for this DOI
and exact raw title. It preserves every word, punctuation and the space before
the colon in the retained display label. PubMed corroborates DOI, author, year,
volume and issue; its title has a colon without that space and a trailing period.
The publisher PDF's bibliographic header was also exposed through web search.
No generic HTML stripping, fuzzy matching or title-based source alias is added.
Unknown tags, literal backslash-n text and corroborating DOI disagreement fail.

Six Wilcox hits now link to new `SRC-R006-WILCOX-2011-ALARMS`: one representative
and five duplicates. Their original OpenAlex hashes/payloads, ordinals, work IDs,
DOIs and full labels were checked. The original 2011-07-01 discovery date remains
alongside the Crossref print date 2011-07. The raw title and title decision remain
distinct from the canonical display string; the old deferral is not rewritten.

**The ICAD venue case is publication-specific.** Original manifest ordinal 1072,
repository UUID, full title, five authors, issued date, DOI and literal discovery
text agree with the hash-matched compressed API page and its exact JSON pointer
(`/objects/80/`), plus fresh Georgia Tech metadata. It becomes a duplicate of the
existing Tislar representative, with original source revision 1 pinned. No venue
listing or same-host URL is accepted from title similarity alone.

**Actual source-text exposure is recorded separately.** Wilcox's publisher PDF
header and first-page excerpts (printed p.284) appeared through web search; the
new source records `partial_text`, not full-text availability or complete reading.
Those excerpts were not a contiguous page/article reading, appraised evidence or
an extraction, and the tool's rendered search response was not retained as source
bytes. During original venue-metadata inspection, Tislar's embedded abstract was
exposed. A new source revision records `abstract_only` and that limitation. Only
access observations and metadata evidence change; material publication identity,
manifestations, rights, original revisions and old source pins stay intact. No
formal reading record, full-paper reading, eligibility decision, study, sample or
empirical claim is created. The fresh selected-field derivatives omit abstracts.

```sh
python research/registry/identity/scripts/build_r006_batch_c_final.py --check
python -m unittest tests.test_screening_batch_c_final -v
python tools/validate.py
python -m tools.identity_queue > build/identity-queue-current.json
```

The bounded builder composes the existing DOI/title checker with the reviewed
venue format and source-access observations. A frozen ledger mismatch stops all
canonical writes. Both historical batch C ledgers/prefixes still reproduce;
source-observation tests allow later revisions while checking their original
pinned assertions. Fifteen new tests cover exact presentation, contradictory
metadata, wrong venue identity/DOI/text, scope drift, immutable discovery and
truthful access extent. No generic source-matching rule or research gate is relaxed.

All-lane unresolved discovery falls **22,346 → 22,339**. Batch C's bounded scope
is complete: **38 + 12 + 7 = 57 occurrences** across ten publication identities,
without an independent-study count. The current exact-identifier queue has zero
candidates/conflicts and 22,339 unmatched unresolved occurrences. Issue #6 and
the corpus gate remain open for broader identity work, actual protocol-governed
screening, study/sample overlap, selection and bias assessment. Next: further
bounded DOI-group admission, preserving these access/reading limits.

AI disclosure: one Codex/GPT-6 agent, 6 November 2026, primary/index metadata and
retained-export verification, record-specific presentation decision, disclosed
incidental source-text exposure, software self-review and fifteen regression
tests. No independent human adjudication or scientific acceptance occurred.

## DOI batch D — 6 November 2026

The [fixed plan](R006-DOI-D-PLAN-20261106.json) and
[ledger](R006-DOI-D-20261106.json) admit fifteen metadata-only publication
identities and resolve 67 retained DOI/full-title occurrences. Fifteen sequential
Crossref single-work requests returned HTTP 200. Selected bibliographic
derivatives retain request URLs/times and original-response hashes. Abstracts
and article/chapter texts were not read; original raw responses are not committed.

| Publication title from metadata | Type | Resolved | Deferred |
|---|---|---:|---:|
| Earcons and Icons: An Experimental Study | chapter | 5 | 0 |
| A Study of Auditory Warning Signals for the Design Guidelines of Man-Machine Interfaces | chapter | 5 | 0 |
| Ergonomics and Anaesthesia: Auditory Alarm Signals in the Operating Room | chapter | 5 | 0 |
| Learning auditory warnings: The effects of sound type, verbal labelling and imagery on the identification of alarm sounds | article | 5 | 0 |
| Meaning From Environmental Sounds: Types of Signal-Referent Relations and Their Effect on Recognizing Auditory Icons. | article | 5 | 0 |
| Menu Navigation With In-Vehicle Technologies: Auditory Menu Cues Improve Dual Task Performance, Preference, and Workload | article | 2 | 3 |
| Composing alarms: considering the musical aspects of auditory alarm design | article | 5 | 0 |
| Employing auditory icons to support virtual lecturers in e-learning interfaces | conference paper | 5 | 0 |
| Exploring Melodic Structure to Increase Heterogeneity of Auditory Alarm Sets in Medical Devices | article | 5 | 0 |
| An evaluation of earcons for use in auditory human-computer interfaces | conference paper | 2 | 3 |
| A Comparative Usability Study on the Use of Auditory Icons to Support Virtual Lecturers in E-Learning Interfaces | article | 5 | 0 |
| Learning and Retention of Associations Between Auditory Icons and Denotative Referents: Implications for the Design of Auditory Warnings | article | 5 | 0 |
| A New Class of Auditory Warning Signals for Complex Systems: Auditory Icons | article | 3 | 2 |
| Acquisition, Response, and Error Rates With Three Suites of Collision Warning Sounds | conference paper | 5 | 0 |
| Designing Effective Alarm Sounds | article | 5 | 0 |

The source batch was selected from recurring DOI groups with auditory-warning/
interface topic labels and five occurrences per group, not from result direction,
statistical significance, open-access status or eligibility. All **75 occurrences**
are accounted for: 67 checked and eight bibliography cases explicitly deferred.
There are no silently discarded candidate groups. This is bounded identity
prioritization, not exhaustive source selection or corpus acceptance.

Every admitted occurrence's explicit DOI and full title agree between the fresh
metadata and the original export under case/whitespace normalization only.
Original manifest/page hashes, payload hashes, ordinals and work IDs were checked.
No competing existing source DOI assertion or exact normalized source title was
found across source-record histories. Fifteen representatives and 52 duplicates
preserve all old revisions, literal metadata, search paths and discovery dates.
Eight references in the FRA, Nees, Ruskin and Totland exports require separate
bibliography provenance checks; none is inferred resolved from DOI text alone.

All fifteen sources have verified metadata, `metadata_only` access, unknown reuse
rights, no manifestations, family/sample links or reading claims. Crossref records
Leimann, Nakatani and McIntyre as **book chapters**. The original Nakatani OpenAlex
`conference-paper` label remains literal discovery metadata; registration and
index type assertions are not silently overwritten. Jeon's original OpenAlex date
`2014-05-30`, Crossref online/issued `2014-10-22` and print `2015-01-02` remain
distinct. The source date explicitly uses the reported print field; identity does
not adjudicate those date differences or establish an independent study.

```sh
python research/registry/identity/scripts/build_r006_doi_batch_d.py --check
python -m unittest tests.test_screening_doi_batch_d -v
python tools/validate.py
python -m tools.identity_queue > build/identity-queue-current.json
```

This thin fixed profile reuses the existing admission engine with exact counts
and its own task/provenance narrative. No shared matcher or research gate is
changed. Frozen ledger disagreement stops canonical writes, and older outputs
retain their historical prefixes. Re-querying may return changed metadata;
retain a new dated capture and correction instead of overwriting these inputs.
The registry and retrieval-map summaries now describe the accumulated identity
batches and separate access observations rather than only the first Hermann case.

All-lane unresolved discovery falls **22,339 → 22,272**. The current exact-identifier
queue has eight candidates, zero conflicts and 22,264 unmatched unresolved
occurrences. No eligibility, screening, study, sample, empirical claim or design
record is created. Existing limited access/reading observations remain unchanged.
Issue #6 and the corpus gate stay open. Next: separately verify the eight deferred
bibliography cases, then continue bounded identity admission and actual
protocol-governed screening with study/sample reconciliation.

AI disclosure: one Codex/GPT-6 agent, 6 November 2026, fresh bibliographic metadata
retrieval, retained-export comparison, software self-review and nine regression
tests. No new target-source reading, independent human adjudication or scientific
acceptance occurred.

## Bibliography batch D — 6 November 2026

The [eight-occurrence ledger](R006-REFERENCE-D-20261106.json) completes the
bibliography work deferred by [DOI batch D](R006-DOI-D-20261106.json). All eight
occurrences now point to existing representatives of three publications (Belz,
Jeon and Brewster). Together, the two batches resolve 75 occurrences to fifteen
publication identities; those identities are not independent studies.

The [fresh retrieval and witness receipt](R006-REFERENCE-D-WITNESSES-20261106.json)
records four HTTP 200 PDFs with hashes identical to the original retained files.
Six selected bibliography citations were visually checked:

| Containing PDF | File pages | Printed pages | Cited publication |
| --- | --- | --- | --- |
| Nees accepted manuscript | 44, 46 | 44, 46 | Brewster; Jeon |
| FRA review | 34, 38 | 26, 30 | Belz; Jeon |
| Ruskin report | 57 | 57 | Brewster |
| Totland thesis | 42 | 42 | Belz |

Original discovery fields, export hashes, ordinals, citation text and coordinate
locators remain intact. The two older `RL-NL` short titles receive publication
identity corroboration from the accepted manuscript, not faithful original
preprint transcription or review-version equivalence. Ruskin reference 018 and
Totland reference 003 retain their original page and line boxes.

Inspection covered only those six citations. No cited target article or whole
containing report was read. All three target publications remain `metadata_only`;
no source access, rights, screening decision, study or sample records were changed.
The PDFs and renders are not committed. A fresh anonymous Totland OpenFile alias
was used; only its stable public endpoint and retrieval provenance are retained.

Reproduce and check:

```bash
python research/registry/identity/scripts/build_r006_reference_batch_d.py --check
python -m unittest tests.test_screening_reference_batch_d -v
python tools/validate.py
python -m tools.identity_queue
```

The dated all-lane queue falls from 22,272 to 22,264 unresolved occurrences, with
zero exact candidates or conflicts and 22,264 unmatched. This finishes this fixed
batch, not issue #6, programme deduplication or the corpus gate. Further identity
admission and actual eligibility screening remain open.

AI assistance: one Codex/GPT-6 agent performed retrieval, six citation inspections,
retained-export comparison, software self-review and ten regression tests. These
checks do not constitute independent human adjudication or scientific validation.

## DOI batch E — 6 November 2026

The [fixed plan](R006-DOI-E-PLAN-20261106.json) and
[identity ledger](R006-DOI-E-20261106.json) add fifteen metadata-only publication
records and resolve 52 original DOI/full-title occurrences (fifteen
representatives and 37 duplicates). Fifteen sequential Crossref single-work
requests returned HTTP 200; selected bibliographic derivatives retain actual
request URLs/times and original-response hashes. Abstracts and article/chapter
texts were not read; raw responses are not committed.

| Publication title from metadata | Type | Resolved | Deferred |
| --- | --- | ---: | ---: |
| The effect of a cross-trial shift of auditory warning signals on the sequential foreperiod effect | article | 5 | 0 |
| Designing informative warning signals: Effects of indicator type, modality, and task demand on recognition speed and accuracy | article | 5 | 0 |
| Most earcons do not interfere with spoken passage comprehension | article | 2 | 2 |
| Testing New Alarms for Medical Electrical Equipment | chapter | 4 | 0 |
| Lyricon (Lyrics + Earcons) Improves Identification of Auditory Cues | chapter | 2 | 2 |
| Designing and Deploying Meaningful Auditory Alarms for Control Systems | chapter | 4 | 0 |
| Spearcon Performance and Preference for Auditory Menus on a Mobile Phone | chapter | 2 | 2 |
| Tailoring reveals information requirements: the case of anaesthesia alarms | article | 4 | 0 |
| Reaction Time and Glance Behavior of Visually Distracted Drivers to an Imminent Forward Collision as a Function of Training, Auditory Warning, and Gender | article | 4 | 0 |
| Synchronized walking cadence for TUG in perturbed environments: Using Earcon or Tacton cues? | conference paper | 4 | 0 |
| Auditory menus are not just spoken visual menus | conference paper | 2 | 2 |
| Spindex (Speech Index) Improves Auditory Menu Acceptance and Navigation Performance | article | 2 | 2 |
| Spearcon Sequences for Monitoring Multiple Patients: Laboratory Investigation Comparing Two Auditory Display Designs | article | 4 | 0 |
| The Relationship between Task Performance, Reaction Time, and Perceived Urgency in Nonverbal Auditory Warnings | article | 4 | 0 |
| Pilot Interactions with Alarm Systems in the Cockpit | article | 4 | 0 |

The batch prioritizes recurring DOI groups with auditory warning/interface topic
labels and four or five unresolved occurrences each. Recurrence and topic labels
are work ordering, not eligibility, result-direction or quality judgments. All
62 occurrences are accounted for: 52 checked and ten deferred; no candidate group
was silently discarded. The eight older bibliography entries need separate
source/export verification. Two additional OpenAlex occurrences use the same DOI
as the shorter Jeon menu title, but a longer title, different work ID and date:

| Retained OpenAlex work | Original title/date assertion | Disposition |
| --- | --- | --- |
| W2130765441 | Auditory menus are not just spoken visual menus; 2010-04-10 | Two exact full-title/DOI matches admitted |
| W1492156475 | Auditory Menus Are Not Just Spoken Visual Menus: A Case Study of “Unavailable” Menu Items; 2012-08-27 | Two occurrences deferred for title/version provenance review |

Crossref reports the shorter title and 2010-04-10. Shared DOI text does not
establish that the longer title/date assertion is equivalent, wrong, a version,
or an independent publication. No alias or family link is inferred. A negative
test confirms that attempting to admit those longer-title records fails even
with the same DOI and adjusted batch counts.

Admitted titles agree under case/whitespace normalization only. Original export
and page hashes, decompressed payload hashes, ordinals and work IDs were checked.
No competing existing source DOI assertion or exact normalized source title was
found across source-record histories. Discovery text, dates and type labels stay
unchanged. Crossref classifies Wee, Sun, Sousa and Walker as book chapters, while
several original index records call them conference papers. Bonebright's source
date uses reported print 2009-04; original discovery/online 2008-05-02 remains
visible. Li's print date is 2019-03 and online/issued date 2018-09-27. Identity
matching does not adjudicate these date/type distinctions.

All fifteen sources have verified metadata, `metadata_only` access, unknown
rights, no manifestations, reading claims or family/sample links. No eligibility,
study, sample, extraction or corpus decision is created. Existing source reading
and access observations remain unchanged.

```sh
python research/registry/identity/scripts/build_r006_doi_batch_e.py --check
python -m unittest tests.test_screening_doi_batch_e -v
python tools/validate.py
python -m tools.identity_queue
```

The thin fixed profile reuses the existing admission engine; no shared matcher or
research gate changed. Frozen ledger disagreement stops writes, and old canonical
revision prefixes remain reproducible. Re-querying requires a new observation,
not replacement of these retained captures.

The dated all-lane unresolved count falls **22,264 → 22,212**. The exact identifier
queue has ten candidates, zero conflicts and 22,202 unmatched. Issue #6 and the
corpus gate remain open. Next: check the eight deferred bibliography citations
and reconcile the two discordant Jeon title/work-ID occurrences before any link;
continue bounded identity work and actual protocol-governed screening separately.

AI assistance: one Codex/GPT-6 agent performed bibliographic retrieval,
retained-export comparison, software self-review and eleven regression tests.
No independent human adjudication, target-source reading or scientific
acceptance is claimed.

## Reproduction of the original Hermann tranche

From the repository root:

```sh
python research/registry/identity/scripts/build_r006_hermann.py --check
python -m unittest tests.test_screening_identity tests.test_screening_integrity tests.test_screening_hermann_tranche
python tools/validate.py --write-exports
python tools/validate.py
```

The builder uses fixed original revision pins and the ledger's recorded time.
Rebuilding preserves later canonical revisions. It never expands the tranche to
new candidates, reads a source or makes screening decisions. Shared registry
exports are regenerated by the integrator after incorporating the current R005
search work.

The [infrastructure self-review](REVIEW-R006-INFRASTRUCTURE.md) records compatibility
checks, two additional DOI-integrity findings and the limits of the review.
