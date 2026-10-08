# MHAC-R002 — chunk 1C1 portable audit packet

**PARTIAL: comparator identity and access reconciliation are complete; the primary-text overlap audit is not.** No novelty, methodological compliance, accepted protocol freeze or whole-workflow completion is claimed.

## Read the result

| Artifact | Purpose |
|---|---|
| [CHECKPOINT.md](CHECKPOINT.md) | Assessed pin, actual status, source-access limit and continuation facts. |
| [Comparator reading/access record](readings/NEES_LIEBMAN_2023.md) | Verified identity; exact access and reading limits. |
| [Overlap matrix](matrices/OVERLAP_MATRIX.md) / [CSV](matrices/OVERLAP_MATRIX.csv) | All six original RQs; title-level overlap separated from unassessed substantive coverage. |
| [Coverage and unknowns](matrices/COVERAGE_UNKNOWNS.md) / [CSV](matrices/COVERAGE_UNKNOWNS.csv) | Fourteen scope/method fields and the primary passages still needed. |
| [Redundancy and candidate questions](findings/REDUNDANCY_AND_CANDIDATES.md) | Conditional duplication objection and two falsifiable candidate questions, not verified gaps. |
| [Next comparison inputs](findings/NEXT_COMPARISON_INPUTS.md) | Exact missing Nees–Liebman text and the later de Souza comparison question; no successor prompt. |
| [Entry reconciliation](findings/ENTRY_RECONCILIATION.md) | Actual restored packets, narrow authority refresh and preserved 1B decisions. |

## Evidence and provenance

[Source/authority manifest](SOURCE_AUTHORITY_MANIFEST.csv), [comparator metadata](readings/COMPARATOR_IDENTITY.json), [access ledger](provenance/ACCESS_LEDGER.csv), [access budget](provenance/ACCESS_BUDGET.json), [reading coverage](provenance/READING_COVERAGE.md), [remote refresh](provenance/REMOTE_REFRESH.json), [assistance/limits](provenance/ASSISTANCE_AND_LIMITS.json), [commands/results](logs/COMMANDS_AND_RESULTS.md), and [content review](logs/CONTENT_REVIEW.md).

## Prior packet identities and reuse

The unchanged [final 1B ZIP](inputs/MHAC_R002_chunk1B_packet_2026-10-04.zip) and [original receipt](inputs/MHAC_R002_chunk1B_archive_verification.json) are included. That ZIP already contains the unchanged original 1A ZIP and receipt. Both original packets were independently verified this turn; [hash/inventory results](provenance/INPUT_HASH_VERIFICATION.json) and [identity comparisons](provenance/INPUT_IDENTITY_CHECK.json) are preserved.

Five exact CSV copies provide direct access to the [1A RQ map](prior_material/1A/matrices/RQ_METHOD_MATRIX.csv), [1A record availability](prior_material/1A/matrices/RECORD_AVAILABILITY.csv), [1B source decisions](prior_material/1B/matrices/SOURCE_TO_DECISION.csv), [1B deferred queue](prior_material/1B/matrices/DEFERRED_GUIDANCE.csv), and [1B reading coverage](prior_material/1B/provenance/READING_COVERAGE.csv). Their [copy identities](provenance/PRIOR_COPY_IDENTITIES.json) match their original archive members. Full adaptation/open-question notes remain in the original 1B archive context; extract that archive before following its local Markdown links.

## Offline packet verification

With standard-library Python, from this packet directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python scripts/verify_packet.py .
```

The verifier checks [SHA256SUMS](SHA256SUMS), inventory, readable JSON/CSV/Python, local Markdown targets, declared-scope consistency, the embedded 1B archive and nested 1A hashes, and prior-copy equality. It does not execute repository tests, validate a research schema, assess scientific truth or infer full-text reading. The external archive-verification receipt pins the final ZIP and records all member checks without a recursive self-hash.

## Safety and scope

No external full texts, article screenshots, search-preview article content, credentials, unrelated author contact/profile information or private-repository material are included. No remote write or humagent update occurred. This is original preparatory analysis, not a new research registry, a complete Git tree, primary-study extraction, publication or proof of novelty. Keep this whole packet for continuation; do not depend on the originating workspace surviving.
