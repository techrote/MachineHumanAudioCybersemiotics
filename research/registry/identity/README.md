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

## Batch E provenance reconciliation — 6 November 2026

The [bibliography subplan](R006-REFERENCE-E-PLAN-20261106.json) partitions all ten
cases deferred by [DOI batch E](R006-DOI-E-PLAN-20261106.json): eight bibliography
occurrences plus two mixed OpenAlex records. The [eight-citation ledger](R006-REFERENCE-E-20261106.json)
and [two-record publisher adjudication](R006-E-FINAL-20261106.json) resolve all ten.
The full batch now accounts for 62 occurrences and sixteen publication identities,
including the distinct journal report; this is not an independent-study count.

### Bibliography witnesses

The [fresh PDF receipt](R006-REFERENCE-E-WITNESSES-20261106.json) records one HTTP
200 Nees accepted manuscript whose bytes match the retained SHA-256 exactly.
Four selected citation pages were rendered and visually inspected:

| Cited publication | File / printed page | Occurrences |
| --- | ---: | ---: |
| Bonebright and Nees, earcons and passage comprehension | 44 / 44 | 2 |
| Jeon and Walker, Spindex | 46 / 46 | 2 |
| Sun and Jeon, Lyricon | 50 / 50 | 2 |
| Walker and Kogan, mobile-phone menus | 51 / 51 | 2 |

Original export hashes, ordinals, outcome letters, literal text and doubled DOI
resolver prefix remain intact. The four original `RL-NL` model-rendered entries
receive identity corroboration only: three have truncated titles, while Bonebright's
title is complete. The shared engine's historical
`corroborated_model_abbreviations` counter counts all four `RL-NL` entries; it does
not mean all four titles are truncated. No faithful original-preprint transcription
or manuscript-version equivalence is asserted. The four cited targets remain
`metadata_only`; only these bibliography citations were read. The review PDF and
renders are not committed.

### Mixed conference and journal metadata

The [fixed adjudication plan](R006-E-FINAL-PLAN-20261106.json) records why the two
longer-title occurrences cannot simply link to the conference source. A fresh
[Crossref derivative with subtitle](metadata/20261106-e-jeon-subtitle.json) has the
same original-response hash as batch E's earlier capture: its selected-field
export omitted the separately deposited subtitle. Adding that subtitle explains
the longer title (with an explicit straight/curly quotation-mark comparison),
but not the conflicting venue, year and pages.

| Identity | Publisher / registration evidence | Retained index assertions |
| --- | --- | --- |
| Existing CHI EA 2010 conference report | ACM DOI `10.1145/1753846.1753978`; 2010-04-10; pp.3319–3324; base title plus subtitle | Short-title OpenAlex W2130765441 remains linked to the conference source |
| New AES 2012 journal report | [AES item 16362](https://aes.org/publications/elibrary/elibrary-page/?id=16362); 2012-07-06; volume 60(7/8), pp.505–518; same full title and four authors | W1492156475 contains the AES item URL, volume/pages and all four authors, but also the conference DOI, 2012-08-27 date and `conference-paper` type |

The [publisher metadata derivative](metadata/20261106-e-jeon-aes2012.json) retains
HTTP 200, actual retrieval time, raw HTML hash and selected bibliographic
`citation_*` fields. Two occurrences resolve to the new
`SRC-R006-E-JEON-2012-AES` (one representative, one duplicate). Their original
conference DOI assertions are preserved as discovery provenance and explicitly
rejected as journal identifiers. Only the verified publisher URL identifies the
new source; no journal DOI was verified, which does not establish that none exists.
Original index dates/types are preserved rather than silently corrected.

The existing conference source and its representative remain unchanged. Separate
publication records do not establish different studies or independent participants.
Potential conference/journal overlap is explicitly unadjudicated in the ledger;
no source alias, family link, study or sample record is created.

The AES publisher abstract was exposed through web search and is logged as
`abstract_only`, without appraisal or numerical extraction. An incidental
third-party abstract fragment is separately disclosed with its uncertain report
association. No article PDF, methods/results section or complete paper was read;
no abstract text or raw HTML is committed. The four bibliography targets remain
metadata-only, and the conference source receives no transferred journal reading.

```sh
python research/registry/identity/scripts/build_r006_reference_batch_e.py --check
python research/registry/identity/scripts/build_r006_batch_e_final.py --check
python -m unittest tests.test_screening_reference_batch_e tests.test_screening_batch_e_final -v
python tools/validate.py
python -m tools.identity_queue
```

The first profile reuses the frozen bibliography engine. The second builder is
record-specific and requires publisher venue/pages/authors, the original AES
location and exact retained page/payload/ordinal/work-ID provenance. It does not
weaken the generic matcher or treat DOI equality as enough. Negative tests reject
publisher-page/DOI disagreement, changed subtitle, altered index bibliography,
missing parent cases, failed retrieval/hash mismatch and frozen-ledger drift.

The dated all-lane unresolved count falls **22,212 → 22,202**, with zero exact
candidates or conflicts and 22,202 unmatched occurrences. This finishes batch E's
fixed identity scope, not issue #6, screening, study/sample reconciliation or the
corpus gate. No eligibility decision changed. Further identity work and actual
protocol-governed screening remain open.

AI assistance: one Codex/GPT-6 agent performed fresh PDF/metadata retrieval, four
visual citation checks, publisher-versus-index adjudication, software self-review
and 21 regression tests. These checks are not independent human screening,
scientific validation or empirical acceptance.

## DOI batch F — 6 November 2026

The [fixed plan](R006-DOI-F-PLAN-20261106.json) and
[ledger](R006-DOI-F-20261106.json) add twenty metadata-only publication records
and resolve sixty retained occurrences (twenty representatives and forty
duplicates). Twenty sequential Crossref single-work requests returned HTTP 200.
Selected bibliographic derivatives retain actual request URLs/times,
original-response hashes, declared subtitle fields when present, and separate
issued/online/print assertions. No abstract or article/chapter text was read;
raw responses are not committed.

| Publication title from metadata | Crossref type | Resolved | Deferred |
| --- | --- | ---: | ---: |
| Standardization of Interface Design for Medical Devices: International Electrotechnical Commission and International Organization for Standardization Medical Alarm Systems | journal-article | 5 | 0 |
| Enhanced Auditory Menu Cues on a Mobile Phone Improve Time-Shared Performance of a Driving-Like Dual Task | journal-article | 2 | 2 |
| Space Station Freedom Aural Toxic Alarm Development | journal-article | 4 | 0 |
| Can 3-D Auditory Warnings Enhance Helicopter Cockpit Safety? | journal-article | 2 | 2 |
| Auditory Alarms in Intensive Care | book-chapter | 4 | 0 |
| Earcons as a Method of Providing Navigational Cues in a Menu Hierarchy | book-chapter | 2 | 1 |
| A Review of Design Guidelines for Clinical Auditory Alarms | book-chapter | 3 | 0 |
| The design and implementation of non-verbal auditory warnings | journal-article | 3 | 0 |
| Designing acoustic and non-acoustic parameters of synthesized speech warnings to control perceived urgency | journal-article | 3 | 0 |
| Improving auditory alarms: Reducing perceived annoyance with musical timbre (a randomized trial) | journal-article | 3 | 0 |
| Loudness interacts with semantics in auditory warnings to impact rear-end collisions | journal-article | 2 | 1 |
| On using psychophysical techniques to achieve urgency mapping in auditory warnings | journal-article | 3 | 0 |
| Using auditory streaming to reduce disruption to serial memory by extraneous auditory warnings. | journal-article | 3 | 0 |
| Judging the urgency of nonvocal auditory warning signals: Perceptual and cognitive processes. | journal-article | 3 | 0 |
| Designing urgency into auditory warnings using pitch, speed and loudness | journal-article | 3 | 0 |
| Localizable auditory warning pulses | journal-article | 3 | 0 |
| Judging the urgency of non-verbal auditory alarms: a case study | journal-article | 3 | 0 |
| A psychophysiological evaluation of the perceived urgency of auditory warning signals | journal-article | 3 | 0 |
| Effects of Synthesized Voice Warning Parameters on Perceived Urgency | journal-article | 3 | 0 |
| The Perceived Urgency of Speech Warnings: Semantics versus Acoustics | journal-article | 3 | 0 |

The batch prioritizes twenty recurring DOI groups with three, four or five
unresolved occurrences each and auditory warning/interface topic labels.
Recurrence and topic labels order identity work; they do not establish eligibility,
quality, preferred cue families or result direction. All 66 occurrences are
accounted for: sixty checked and six explicitly deferred, with no discarded
candidate groups in this fixed plan.

Each admitted occurrence's explicit DOI and full title agree with its original
export and fresh registration metadata under case/whitespace normalization only.
Original manifest/page hashes, decompressed payload hashes, ordinals and work IDs
were checked. No competing source DOI assertion or exactly normalized title was
found across existing source histories. Original discovery fields, dates and
index type labels remain intact. Subtitle capture is more complete than the
older selected-field format; it does not authorize title expansion or fuzzy
matching.

Crossref classifies Welch, Brewster and Vieira as book chapters. Several other
records are registered as `journal-article` within HFES proceedings containers;
registration type is not a final report-type or eligibility judgment. Jang's
source date uses reported print 2007-03, while original OpenAlex 2006-12-30
remains unchanged. Other print/online/issued assertions likewise stay separate.
Catchpole's original index first-author string says Ken C. while the fresh
registration reports Ken R; both remain literal assertions in their respective
records. Identity checking does not silently reconcile author initials.

Six bibliography occurrences need separate source/export verification: Baldwin
in the FRA PDF list, Haas and Moskovitch in the original model-rendered and
accepted-manuscript lists, and Brewster in the coordinate-bearing Ruskin export.
DOI/full-title registration alone does not resolve their page/transcription
provenance. They remain unresolved in this batch.

All twenty sources have verified bibliographic metadata, `metadata_only` access,
unknown reuse rights, no manifestations, reading claims or family/sample links.
No eligibility, study, sample, empirical extraction or completed corpus is created.
Existing source access/reading observations remain unchanged.

```sh
python research/registry/identity/scripts/build_r006_doi_batch_f.py --check
python -m unittest tests.test_screening_doi_batch_f -v
python tools/validate.py
python -m tools.identity_queue
```

The fixed profile reuses the existing admission engine; no shared matcher or
research gate changed. Frozen ledger disagreement stops writes, and historical
canonical revision prefixes remain reproducible. A changed future metadata
response requires a new observation, not replacement of these captures.

The dated all-lane unresolved count falls **22,202 → 22,142**, with six exact
candidates, zero conflicts and 22,136 unmatched occurrences. Issue #6 and the
corpus gate stay open. Next: verify the six bibliography cases separately,
continue bounded identity admission and undertake actual protocol-governed
screening and study/sample reconciliation.

AI assistance: one Codex/GPT-6 agent performed bibliographic retrieval,
retained-export comparison, software self-review and ten regression tests.
No independent human adjudication, target-source reading or scientific
acceptance is claimed.

## Bibliography batch F — 6 November 2026

The [six-occurrence ledger](R006-REFERENCE-F-20261106.json) completes the
bibliography cases deferred by [DOI batch F](R006-DOI-F-20261106.json).
All six occurrences link to existing representatives of four publications:
Baldwin and May, Haas, Moskovitch and colleagues, and Brewster and colleagues.
Together, the two batches resolve 66 occurrences to twenty publication
identities. These are not independent-study or sample counts.

The [fresh retrieval and witness receipt](R006-REFERENCE-F-WITNESSES-20261106.json)
records three HTTP 200 PDFs with hashes identical to the retained originals.
Four selected bibliography citations were visually checked:

| Containing PDF | File pages | Printed pages | Cited publication |
| --- | --- | --- | --- |
| Nees accepted manuscript | 45, 48 | 45, 48 | Haas; Moskovitch and colleagues |
| FRA review | 34 | 26 | Baldwin and May |
| Ruskin report | 57 | 57 | Brewster and colleagues |

Original discovery fields, export hashes, ordinals, literal citation text and
outcome letters remain intact. The two older `RL-NL` short entries receive
publication-identity corroboration from the accepted manuscript, not faithful
original-preprint transcription or review-version equivalence. Ruskin reference
019 retains its original page and coordinate-bearing citation lines.

Inspection covered only those four citations. No cited target article or whole
containing review/report was read. All four target sources remain `metadata_only`;
no source access, rights, eligibility decisions, studies or samples changed.
Source PDFs and renders are not committed. The fixed
[batch F profile](scripts/build_r006_reference_batch_f.py) uses the existing
reference engine, verifies its complete deferred scope and reproduces all output
revision hashes without replacing historical input revisions.

```bash
python research/registry/identity/scripts/build_r006_reference_batch_f.py --check
python -m unittest tests.test_screening_reference_batch_f -v
python tools/validate.py
python -m tools.identity_queue
```

The dated all-lane queue falls from 22,142 to 22,136 unresolved occurrences:
zero exact candidates, zero conflicts and 22,136 unmatched. This completes the
fixed batch F identity scope; broader issue #6 reconciliation, eligibility,
study/sample overlap, corpus selection and residual-bias assessment remain open.
The R005 coverage gaps and downstream #7–#9 corpus gates remain explicit.

AI assistance: one Codex/GPT-6 agent performed retrieval, four citation
inspections, retained-export comparison, software self-review and ten regression
tests. These checks are not independent human adjudication or scientific
validation. No protocol amendment or scientific acceptance is asserted.

## DOI batch G — 6 November 2026

The [fixed twenty-group plan](R006-DOI-G-PLAN-20261106.json) and
[nineteen-publication ledger](R006-DOI-G-20261106.json) add nineteen metadata-only
source records and resolve 51 occurrences (nineteen representatives and 32
duplicates). Twenty sequential Crossref single-work requests returned HTTP 200.
Selected bibliographic derivatives retain actual URLs/times, original-response
hashes, subtitle fields and separate issued/online/print assertions. Raw responses,
abstracts and article text are not committed; no abstract or article was read.

| Publication title from metadata | Crossref type | Resolved | Deferred |
| --- | --- | ---: | ---: |
| The impact of concurrent linguistic tasks on participants’ identification of spearcons | journal-article | 2 | 1 |
| Recommendation of New Medical Alarms Based on Audibility, Identifiability, and Detectability in a Randomized, Simulation-Based Study | journal-article | 2 | 1 |
| Enhanced auditory menu cues improve dual task performance and are preferred with in-vehicle technologies | proceedings-article | 2 | 1 |
| An RSS-feed auditory aggregator using earcons | proceedings-article | 3 | 0 |
| Graded auditory warnings during in-vehicle use | proceedings-article | 2 | 1 |
| Speech Tactons Improve Speech Warnings for Drivers | proceedings-article | 3 | 0 |
| An Initial Investigation into Non-visual Code Structure Overview Through Speech, Non-speech and Spearcons | proceedings-article | 1 | 2 |
| The Impact of Intonation and Valence on Objective and Subjective Attention Capture by Auditory Alarms | journal-article | 3 | 0 |
| Do Learned Alarm Sounds Interfere With Working Memory? | journal-article | 3 | 0 |
| A Methodology for Selecting Auditory Icons for Use in Commercial Motor Vehicles | journal-article | 3 | 0 |
| Auditory Warnings in the Medical Work Domain: An Overview of Critical Issues | journal-article | 3 | 0 |
| Auditory Alarms: From Alerting to Informing | journal-article | 3 | 0 |
| Representative Auditory Warning Signals: Methodological Considerations for Their Development and Selection | journal-article | 3 | 0 |
| Perceived Urgency in Speech Warnings | journal-article | 3 | 0 |
| Using Psychophysics to Design Speech Warnings | journal-article | 3 | 0 |
| Connoted Hazard of Voiced Warning Signal Words: An Examination of Auditory Components | journal-article | 3 | 0 |
| Natural Warning Sounds in Safety Critical Human-Machine Systems -A Cognitive Engineering Approach | journal-article | 3 | 0 |
| Obtaining Objective Measurements of Operator Performance with Auditory Alarms | journal-article | 3 | 0 |
| Measuring Perceived Urgency to Create Safe Auditory Warnings | journal-article | 3 | 0 |

The fixed scope contains sixty occurrences across twenty recurring DOI groups,
each with three occurrences. Auditory warning/interface topic labels and
recurrence prioritize identity work; they do not establish eligibility, quality,
preferred result direction or study independence. Other recurring groups remain
unadjudicated, not excluded. All sixty fixed occurrences are accounted for:
51 resolved, six bibliography cases deferred, and three correction-related cases
not admitted. No candidate was silently replaced after verification.

Each admitted occurrence's explicit DOI and full title agrees with the retained
original export and fresh registration under case/whitespace comparison only.
Original export/page hashes, decompressed payload hashes, ordinals and work IDs
were checked. No competing DOI assertion or exactly normalized title was found
in existing source histories. Original discovery text, dates and index type labels
remain intact. Five ACM proceedings articles retain conference-paper type;
HFES entries registered as journal-article are not given a final report-type or
eligibility judgment from registration type alone.

Davidson's source date uses reported print 2019-11 while original OpenAlex
2019-08-14 remains literal; Ljungberg and Lacherez likewise retain separate print
and index-date assertions. Fagerlönn's main registration title and deposited
subtitle are retained separately. The subtitle is not inserted into the source's
main title or used to rewrite discovery text. Author-name expansions and initials
from the two services likewise remain their respective assertions.

Six bibliography occurrences need separate citation/provenance verification:
Davidson and Bennett in Nees general references; Jeon and Fagerlönn in the FRA
PDF-derived list; and Hutchinson in the original model-rendered and accepted-
manuscript included lists. These remain unresolved in this batch. No source PDF
retrieval, full-citation corroboration or review-version equivalence is inferred.

### Correction-related hold

The retained [Ferreira registration derivative](metadata/20261106-g-ferreira-erp.json)
for `10.1371/journal.pone.0281680` contains a `relation.correction` entry naming
`10.1371/journal.pone.0295826`. Its three discovery occurrences remain unresolved;
no Ferreira source or hit revisions are created. This records registration
metadata, not a reading or adjudication of the correction notice, a retraction,
publication invalidity or an eligibility exclusion. Next: retrieve the correction
registration and lawful publisher notice, inspect its exact scope, and record the
original/correction identities and consequences explicitly before admission.

The shared admission engine now rejects nonempty `relation` or `update-to`
metadata even when the capture hash and DOI/title match. This makes the existing
manual deferral policy fail closed during reconstruction. A separate reviewed
correction/relation path is necessary; fields cannot simply be dropped to admit
a record. Fictional adverse-input tests cover both fields with matching artifact
hashes. Existing frozen batches remain reproducible.

All nineteen admitted sources have verified bibliographic metadata,
`metadata_only` access, unknown reuse rights, no manifestations or family/sample
links. No eligibility, study, sample, empirical extraction, completed corpus or
#7–#9 analysis acceptance is created. The R005 coverage gaps remain open.

```sh
python research/registry/identity/scripts/build_r006_doi_batch_g.py --check
python -m unittest tests.test_screening_doi_batch_g -v
python tools/validate.py
python -m tools.identity_queue
```

The dated all-lane unresolved count falls **22,136 → 22,085**: six exact
candidates, zero conflicts and 22,079 unmatched occurrences. The three held
Ferreira occurrences belong to the unmatched residual, not to a screened-out
category. Issue #6 and the corpus gate remain open for broader identity,
protocol-governed screening, study/sample reconciliation and bias assessment.

AI assistance: one Codex/GPT-6 agent performed metadata retrieval, retained-export
comparison, implementation, software self-review and fourteen regression tests.
These are not independent human adjudication or scientific validation. No
protocol amendment or human gate satisfaction is asserted.

## Bibliography batch G — 6 November 2026

The [six-occurrence ledger](R006-REFERENCE-G-20261106.json) resolves all
bibliography cases deferred by [DOI batch G](R006-DOI-G-20261106.json).
Six occurrences now point to existing representatives of five publications:
Bennett, Davidson, Hutchinson, Fagerlönn and Jeon. Across the two tranches,
57 occurrences link to nineteen publication identities. The separate three-
occurrence Ferreira correction-related hold remains unresolved; the original
sixty-occurrence plan is not declared fully resolved.

The [fresh retrieval and citation receipt](R006-REFERENCE-G-WITNESSES-20261106.json)
records two HTTP 200 PDFs with hashes identical to the retained originals.
Five selected citations were visually checked:

| Containing PDF / section | File pages | Printed pages | Cited publication |
| --- | --- | --- | --- |
| Nees accepted manuscript, general references | 33, 35 | 33, 35 | Bennett; Davidson |
| Nees accepted manuscript, included list | 46 | 46 | Hutchinson |
| FRA review | 36, 37 | 28, 29 | Fagerlönn; Jeon |

Original discovery text, export hashes, ordinals, citation locators and outcome
letters remain intact. The two general references retain original references 6
and 21 and their exact page assertions. Fagerlönn's full subtitle remains in its
original citation without expanding the target source's main title. Jeon's
original single-page `91` assertion is retained rather than rewritten from the
registration's page range. Hutchinson's older `RL-NL` abbreviated title receives
publication-identity corroboration from the accepted manuscript, not faithful
original-preprint transcription or review-version equivalence.

Inspection covered only those five citations; no cited target article or whole
containing review/report was read. All five existing target sources remain
`metadata_only`, with unchanged access/rights and no study/sample links. No new
source, eligibility decision, empirical extraction, correction adjudication or
completed corpus is created. PDFs and renders are not committed. The fixed
[batch G profile](scripts/build_r006_reference_batch_g.py) reuses the existing
reference engine and reproduces its complete deferred scope and canonical output
prefixes; no shared engine or frozen protocol changed in this tranche.

```bash
python research/registry/identity/scripts/build_r006_reference_batch_g.py --check
python -m unittest tests.test_screening_reference_batch_g -v
python tools/validate.py
python -m tools.identity_queue
```

The dated all-lane queue falls from 22,085 to 22,079 unresolved occurrences:
zero exact candidates, zero conflicts and 22,079 unmatched. The three held
Ferreira occurrences stay in that unmatched residual pending explicit correction
review. Broader issue #6 identity reconciliation, actual screening, study/sample
overlap, selected corpus and bias assessment remain open, alongside the R005
coverage gaps and downstream #7–#9 corpus gates.

AI assistance: one Codex/GPT-6 agent performed fresh retrieval, five citation
inspections, retained-export comparison, software self-review and twelve
regression tests. These checks are not independent human adjudication or
scientific validation. No human gate satisfaction or protocol amendment is
asserted.

## Ferreira correction-aware identity review — 6 November 2026

The [fixed correction-review plan](R006-FERREIRA-CORRECTION-PLAN-20261106.json)
and [ledger](R006-FERREIRA-CORRECTION-20261106.json) resolve the three
Ferreira occurrences held by batch G. They create one representative and two
duplicate links to `SRC-R006-G-FERREIRA-ERP`, first registered with validity
`corrected` and access `metadata_only`. A separate source,
`SRC-R006-G-FERREIRA-CORRECTION`, records the publisher's correction notice and
links `correction_of` the original. They are distinct publications, never two
independent experiments or samples and never source aliases.

Two fresh Crossref single-work requests returned HTTP 200. The original's
`relation.correction` names notice DOI `10.1371/journal.pone.0295826`; the
notice's publisher `update-to` identifies original DOI
`10.1371/journal.pone.0281680` as its correction target. The full author names
agree, although the original registration splits the first author's family name
as `Ribeiro Ferreira` and the notice registration uses `Ferreira`. Both literal
registration assertions are retained. Original publication date 16 February
2023 and notice date 7 December 2023 remain distinct.

The [publisher reading receipt](R006-FERREIRA-CORRECTION-WITNESS-20261106.json)
records the freshly retrieved one-page PDF, exact URL/time/hash, rendered-image
inspection and paragraph locators. The full correction notice, its original-paper
reference and copyright sidebar were read. It identifies three changes:

| Publisher notice locator | Stated change |
| --- | --- |
| PDF p.1, paragraph 1 | Guilherme Campos replaces Alberto Crego as corresponding author. |
| PDF p.1, paragraph 2 | Three omitted affiliations are added for Guilherme Campos. |
| PDF p.1, paragraph 3 | Additional partial FCT funding through UIDB/00127/2020 is acknowledged. |

This is the notice's stated scope. The original article, abstract, methods and
results were not retrieved or read, and no empirical-result effect assessment was
performed. The source's corrected flag records a known publisher correction; it
does not certify unaffected results or study validity. The notice's full-item
reading applies only to its one-page manifestation. Its explicit Creative Commons
Attribution redistribution terms are recorded only for the notice, with no licence
version inferred; original-paper rights remain unknown. PDFs, HTML, renders,
raw registration responses and contact details are not committed.

The initial noncanonical PDF request using `type=print` returned 404; the actual
publisher-linked `type=printable` route returned 200. No source-unavailability
claim is made from the failed route. The fixed
[correction-aware builder](scripts/build_r006_ferreira_correction.py) checks
reciprocal registration identities, title/author/date context, the inspected
publisher witness, the complete three-case parent hold and separate notice
occurrence, export/page/payload hashes, DOI/full titles and work IDs. It preserves every original hit
revision and discovery field. The ordinary metadata admission engine's relation/
update guard is unchanged; this separate path does not discard those fields.

Registration of the notice exposed an additional retained exact-DOI candidate,
`HIT-R005R-C1RECOVERY-EQ1-00705`. Its full correction title, explicit notice DOI,
original ordinal 705, date 2023-12-07, `erratum` type label and OpenAlex work ID
were checked against the retained export and current registration. It now resolves
to the correction source as its own representative, never as a duplicate of the
original paper. Four occurrences are resolved in this review: the three held
original-paper occurrences and this separate notice occurrence.

Because the original source did not previously exist locally, its first revision
already records the correction. No fictional earlier active revision, amendment
or downstream invalidation event is fabricated. Future source changes still need
ordinary append-only correction handling. Notice content belongs in future
funding/conflict appraisal when actual empirical reading occurs; no eligibility,
study/sample, appraisal or selected corpus is created here.

```bash
python research/registry/identity/scripts/build_r006_ferreira_correction.py --check
python -m unittest tests.test_screening_ferreira_correction -v
python tools/validate.py
python -m tools.identity_queue
```

The dated all-lane unresolved count falls **22,079 → 22,075**, with zero exact
candidates/conflicts and 22,075 unmatched. Batch G's sixty original discovery
occurrences now link to twenty cited publication identities; its correction
notice is an additional linked source with its own separately retained discovery
occurrence; it is not another study.
This completes only that fixed identity scope. Issue #6 remains open for broader
identity, actual eligibility, overlap, corpus snapshot and bias assessment;
R005 coverage and the #7–#9 corpus gates remain incomplete.

AI assistance: one Codex/GPT-6 agent performed retrieval, full notice reading,
identity review, implementation and software self-review, with eighteen regression
tests. No independent human adjudication, peer review, original-paper reading,
scientific validation or human-gate satisfaction is asserted.

## DOI batch H — 6 November 2026

The [fixed twelve-group plan](R006-DOI-H-PLAN-20261106.json) and
[ledger](R006-DOI-H-20261106.json) add twelve metadata-only publication records
and resolve 25 occurrences (twelve representatives and thirteen duplicates).
Twelve sequential Crossref single-work requests returned HTTP 200. Selected
bibliographic derivatives retain actual request URLs/times, response hashes,
subtitle fields and separate issued/online/print assertions. Raw responses,
abstracts and article/chapter text are not committed or read.

| Publication title from metadata | Crossref type | Resolved | Deferred |
| --- | --- | ---: | ---: |
| Semantic congruency of auditory warnings | journal-article | 1 | 2 |
| Auditory icons, earcons, and displays: Information and expression through sound | book-chapter | 3 | 0 |
| Recognition of Car Warnings | proceedings-article | 1 | 2 |
| Using a Sequence of Earcons to Monitor Multiple Simulated Patients | journal-article | 2 | 1 |
| Toward a Better Understanding of In-Vehicle Auditory Warnings and Background Noise | journal-article | 1 | 2 |
| Multimodal Warnings: Curve-Warning Design | journal-article | 1 | 2 |
| Urgency mapping in auditory warning signals | book-chapter | 3 | 0 |
| Are Melodic Medical Equipment Alarms Easily Learned? | journal-article | 3 | 0 |
| Manual 3D Control of an Assistive Robotic Manipulator Using Alpha Rhythms and an Auditory Menu: A Proof-of-Concept | journal-article | 3 | 0 |
| Ergonomic Design of Voice Warning Sounds Used in Utility Helicopter | journal-article | 3 | 0 |
| Listen Out! Behavioural and Subjective Responses to Verbal Warnings | journal-article | 2 | 0 |
| Evaluation of earcons for portable digital electronic products considering perceptual user characteristics | journal-article | 2 | 0 |

The fixed scope contains 34 occurrences across twelve DOI groups, with two or
three occurrences each. Auditory warning/interface topic labels and recurrence
prioritize identity work, not eligibility, quality or result direction. Other
recurring groups remain unadjudicated rather than excluded. All 34 occurrences
are accounted for: 25 resolved, nine deferred, zero discarded or substituted
candidate groups.

Each admitted occurrence's explicit DOI and full registration title agrees with
its original retained export under case/whitespace normalization only. Export,
page and decompressed payload hashes, original ordinals and work IDs were checked.
Twenty-three OpenAlex rows also agree in volume/issue/page fields wherever both
services supply them; historical index flags are not a fresh retraction search.
No competing existing source DOI assertion or exactly normalized title was found.
Captured relation/update fields were empty; this is not a comprehensive correction
or retraction search. The ordinary engine's relation/update guard remains active.

Two Roginska/Edworthy sources retain chapter type; Sabic's recognition paper
retains conference-paper type. HFES registration as journal-article is not a final
report-type decision. The two R004 Crossref lookup occurrences returned Edworthy's
1994 chapter at ordinal 3, although their query labels name 1991 and 1993 targets.
Those labels, search pins and discovery strings are preserved; a query target does
not determine the identity or year of every returned result.

Isherwood's source date uses reported print 2017-07-03, while original OpenAlex
2016-09-21 remains literal. Sabic's journal paper similarly keeps print 2021-03
separate from index 2019-10-08 and its captured online date. Park's and Roginska's
name spellings and all other author/date assertions remain as reported by their
respective services. No discovery text is harmonized to fresh registration.

Nine bibliography cases remain unresolved: Isherwood, both Sabic papers and
Neurauter in the original model-rendered/accepted-manuscript included lists, plus
Hickling in Ruskin reference 073. They need citation/source-provenance review.
The recognition paper's registered main title, *Recognition of Car Warnings*,
and deposited subtitle, *An Analysis of Various Alert Types*, remain separate.
Its model-rendered title includes a truncated subtitle; verifying that
presentation requires an explicit subtitle-aware comparison, not a relaxation
of the full-title matcher or an inferred review-version alias.

All twelve sources remain `metadata_only`, with unknown reuse rights, no
manifestations and no family/sample links. No eligibility, study, sample,
empirical extraction, correction adjudication, completed corpus or downstream
#7–#9 acceptance is created. No full-text availability or reading is inferred from
metadata, and the R005 coverage gaps remain open.

```sh
python research/registry/identity/scripts/build_r006_doi_batch_h.py --check
python -m unittest tests.test_screening_doi_batch_h -v
python tools/validate.py
python -m tools.identity_queue
```

The dated all-lane unresolved count falls **22,075 → 22,050**: nine exact
candidates, zero conflicts and 22,041 unmatched. These are all-lane discovery
counts, not an empirical flow or independent-study count. Issue #6 and the corpus
gate remain open for broader identity, actual protocol-governed screening,
study/sample reconciliation and bias assessment.

AI assistance: one Codex/GPT-6 agent performed metadata retrieval, retained-export
comparison, software self-review and twelve regression tests. No independent
human adjudication, target-source reading, scientific validation, protocol
amendment or human-gate satisfaction is asserted.

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
