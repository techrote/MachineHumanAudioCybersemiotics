# Pilot searches — MHAC-R002

[Pilot report](../../protocol/PILOT_REPORT.md) · [Protocol §5](../../protocol/PROTOCOL-v1.md#5-track-e-sources-and-searches)

**Pilot and discovery runs only.** These are not production searches, and the only channel that worked was a general web search engine. They cannot support any coverage claim.

| Path | Content |
|---|---|
| [exports/PILOT-WEBSEARCH-2026-10-13.json](exports/PILOT-WEBSEARCH-2026-10-13.json) | Every web-search run in R002 (31 runs, four batches) with each returned title and URL exactly as received. |
| [exports/ACCESS-LEDGER-2026-10-13.csv](exports/ACCESS-LEDGER-2026-10-13.csv) | Every fetch, download, API and browser attempt, with outcome and what was obtained. |
| [records/](records/) | One `search_run` record per run (`SRCH-R002-*`), status `partial` because the engine exposes no pagination or totals, and one `search_hit` record per returned occurrence (`HIT-R002-*`). |

Every returned occurrence has a `search_hit` record (`HIT-R002-*`). Occurrences are `resolved` only where the agent actually opened that URL or the URL carries the publication's DOI, arXiv identifier or ISBN; all others stay `unresolved`. Production runs for #3/#4/#5 belong in their own lane directories under `research/searches/`.
