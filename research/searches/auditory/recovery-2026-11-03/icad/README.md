# ICAD C5 listing recovery — 3 November 2026

The public Georgia Tech ICAD series index was retrieved to its advertised end:
**1,269 distinct repository items across 13 pages**. The [manifest](MANIFEST.json)
contains one outcome for every issue-date year 1992–2026, exact executed URLs,
retrieval start and finish times, retained raw-response paths and SHA-256 hashes,
and source metadata for every returned item. [The access log](access.jsonl)
also preserves failed requests. This was an AI-assisted metadata retrieval by a
ChatGPT GPT-6 Astra Pro subagent, with no human verification.

## What the recovery adds

The [official proceedings page](https://icad.org/proceedings/) links the
[Georgia Tech series](https://repository.gatech.edu/entities/series/6cb90d00-3311-4767-954d-415c9341a358).
Its public HTML was server-rendered on this attempt and exposed the public
listing API. Enumerating that API recovered titles, authors where supplied,
issue dates, identifiers and other metadata, including years beyond the earlier
legacy archive. This is a venue-specific listing, not an OpenAlex, Crossref,
ACM or other bibliographic-database search.

Each API response's advertised total and page number were checked. Retrieval
returned all 1,269 advertised items without repeated repository IDs. Two
requests with optional thumbnail embedding timed out; requests for the same
pages without that optional embedding succeeded. The exact variants are logged.
No pagination results were fabricated or reconstructed from search snippets.

The prior **780 filename occurrences** remain in the unchanged October export.
They must remain discoverable alongside these records: the two inventories
overlap and neither should silently replace the other. The legacy archive has,
for example, 38 filename entries for 2000, while the series index returns 27
items with a 2000 issue date. Different inventory units, metadata errors and
deposit gaps need item-level reconciliation in R006.

## Year coverage and limits

| Issue-date year | Returned repository items |
|---|---:|
| 1992 | 0 |
| 1993 | 0 |
| 1994 | 35 |
| 1995 | 0 |
| 1996 | 28 |
| 1997 | 20 |
| 1998 | 31 |
| 1999 | 0 |
| 2000 | 27 |
| 2001 | 46 |
| 2002 | 66 |
| 2003 | 72 |
| 2004 | 60 |
| 2005 | 73 |
| 2006 | 51 |
| 2007 | 77 |
| 2008 | 57 |
| 2009 | 43 |
| 2010 | 55 |
| 2011 | 45 |
| 2012 | 53 |
| 2013 | 40 |
| 2014 | 56 |
| 2015 | 63 |
| 2016 | 34 |
| 2017 | 33 |
| 2018 | 30 |
| 2019 | 52 |
| 2020 | 0 |
| 2021 | 36 |
| 2022 | 15 |
| 2023 | 24 |
| 2024 | 22 |
| 2025 | 24 |
| 2026 | 1 |
| **Total** | **1,269** |

These are **issue-date metadata years**, not inferred conference years, unique
publications or eligible studies. The sole 2026 item is titled *Companion Book of
the AM.ICAD 2025* and has `dc.date.issued = 2026-07`; the discrepancy is preserved.
The source index mixes individual papers, whole proceedings and ancillary media.
No eligibility, independent-sample or reading decision follows from a listing.

The [official conference history](https://icad.org/conferences/) lists conferences
in 1992 and 2026. Their absence from corresponding conference-specific item
coverage remains a gap. The current 2026 conference link redirected to
`https://interactive-sonification.org/icad2026/` and returned HTTP 503; the response
and timestamp are retained. Zero items for 1993, 1995, 1999 and 2020 also do not
establish that no relevant material exists. The official history omits annual
conference entries for those years and includes an undated ICAD/ASA/EAA workshop.

The baseline cut-off remains **4 October 2026**. Eligibility of full dates and
ambiguous year-only dates belongs to screening, including any items deposited
after the cut-off. No source text, methods, statistics or outcome was read in
this batch. Metadata rights are supplied as CC0 for 26 records and absent for
the other 1,243; no blanket licence was inferred. The public proceedings page
describes the proceedings repository as CC BY-NC 4.0 and copyright remaining
with authors. Only public metadata/index responses are retained here, not paper
PDFs or book texts.

## Reproduction

From the repository root:

```sh
python research/searches/auditory/recovery-2026-11-03/icad/build_r005_icad.py --check
```

The command verifies every retained page hash, advertised total, page number,
per-page result count, unique repository identity and generated manifest. Run
without `--check` to regenerate the manifest. `fetch_r005_icad.py` records a
specified public URL and output filename; replaying a live request can return
different metadata and must be retained as a new dated batch, never overwrite
this evidence.

The 13 successful raw API pages are the reproducible listing authority. Retained
API and HTML responses are stored with **lossless deterministic gzip** (zero
timestamp and empty embedded filename). [STORAGE.json](STORAGE.json) maps every
original capture path to its `stored_path`, `storage_bytes` and `storage_sha256`,
and separately records the exact decompressed `payload_bytes` and
`payload_sha256`. Decompression restores the original captured bytes; compression
does not remove or rewrite metadata. Original access-log paths, URLs, timestamps
and response hashes remain capture observations and resolve through that mapping.
The manifest's page records identify the compressed storage objects and their
payload hashes. The builder checks both hash layers before parsing the payload.

The HTML responses preserve the official source routes and history. The manifest's
per-item JSON pointers locate the original metadata. R006 should retain all
discovery paths, reconcile legacy filenames with repository identities, and
seek texts only for candidates under the frozen eligibility rules.
