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

## Reproduction and review

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
