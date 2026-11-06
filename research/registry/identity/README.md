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
