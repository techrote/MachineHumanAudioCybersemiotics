# Auditory-lane search inventory — MHAC-R005

[Coverage memo](../../sources/auditory/README.md) · [Recovery checkpoint](recovery-2026-11-03/README.md) · [Protocol §5](../../protocol/PROTOCOL-v1.md#5-track-e-sources-and-searches)

The auditory inventory contains **150 search records and 21,483 discovery occurrences** from 13 October and 3 November 2026. The cutoff stays **2026-10-04**. Seven frozen OpenAlex families have complete runs; EQ1 is partial. Search, corpus and scientific acceptance remain distinct.

| Path | Contents |
|---|---|
| [Original web export](exports/AUDITORY-WEBSEARCH-2026-10-13.json) | Exact October queries, ordered results, references and access outcomes |
| [Original access ledger](exports/ACCESS-LEDGER-R005-2026-10-13.csv) | Retrieval attempts and historical restrictions |
| [Known-item table](exports/KNOWN-ITEM-CHECK-R005.csv) | 69 entries: 38 located, 10 possible, 21 not located; not a November recall estimate |
| [OpenAlex exports](exports/openalex/) | Three invocation manifests and 93 gzip response artifacts, including errors |
| [Database audit](recovery-2026-11-03/database/AUDIT.md) | Access, exact semantics, retries, quota stop and verified counts |
| [ICAD recovery](recovery-2026-11-03/icad/README.md) | 1,269 available series items, year outcomes and lossless response storage |
| [Reference recovery](recovery-2026-11-03/references/README.md) | Nees–Liebman general references (85), sleep-inertia bibliography (91), version checks and navigation |
| [Three-review recovery](recovery-2026-11-03/reviews/README.md) | Totland (47), Edworthy (80), Ruskin et al. (185), with exact locators |
| [Search records](records/) / [occurrences](records/hits/) | Original R005 and new R005R records; every discovery path retained |

The earlier 2,244 occurrences are not replaced. Repeated queries, reference-list retrievals and within-provider duplicates are preserved. Identity adjudication belongs to R006 and must append decisions with provenance.

## Offline reproduction

From the repository root:

```sh
python3 research/sources/auditory/scripts/build_r005_recovery_records.py --check
python3 research/searches/auditory/recovery-2026-11-03/database/summarize_runs.py
python3 research/searches/auditory/recovery-2026-11-03/icad/build_r005_icad.py --check
python3 tools/validate.py
```

The recovery builder checks gzip container and decoded payload hashes. Its check mode verifies original revisions without overwriting later identity decisions. PDF extraction additionally needs matching lawful private source files; each reference directory documents inputs. Public bibliographic exports and hit records remain usable without those files. The [October builder](../../sources/auditory/scripts/build_r005_records.py) describes the historical capture; do not use it to replace later revisions.

## Remaining work

EQ1 continuation, remaining review/included-report chaining, forward citations, missing database exports, ICAD venue gaps, identity adjudication, actual screening and primary-text retrieval remain explicit. No corpus freeze, inclusion decision, independent-study count or numerical synthesis is declared.
