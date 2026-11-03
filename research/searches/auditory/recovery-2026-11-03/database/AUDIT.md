# Database channel availability and query audit

Date: 2026-11-03. Actor: ChatGPT, GPT-6 Astra Pro, delegated database-channel audit.
This is an AI-assisted technical check, not human search review. The [first-probe
manifest](probe-manifest.json) and [family-count manifest](count-manifest.json)
retain exact URLs, timestamps, HTTP outcomes, response filenames and SHA-256
digests. They are feasibility probes, not completed production searches.

## Observed availability

Both services responded successfully to unauthenticated requests. OpenAlex
returned HTTP 200 for the exact frozen EQ4 Boolean expression in
`title_and_abstract.search`, with the frozen `2026-10-04` cutoff. Its parsed-query
metadata retained the alternatives inside each block and the conjunction between
blocks. Crossref returned HTTP 200 for a bibliographic metadata query. No account,
key, purchase or privileged access was used.

The eight frozen OpenAlex query families each returned HTTP 200. An additional
EQ4 request with `page=2&per_page=1` also succeeded. These are current observations;
the preserved October refusal/rate-limit records remain accurate for their dates.

| Query | Reported matches | Pages at 100 | Pages at 200 |
|---|---:|---:|---:|
| EQ1 | 9,368 | 94 | 47 |
| EQ2 | 556 | 6 | 3 |
| EQ3 | 76 | 1 | 1 |
| EQ4 | 585 | 6 | 3 |
| EQ5 | 2,112 | 22 | 11 |
| EQ6 | 537 | 6 | 3 |
| EQ7 | 153 | 2 | 1 |
| EQ8 | 4,652 | 47 | 24 |
| Total query occurrences/pages | 18,039 | 184 | 93 |

These counts overlap across queries and are not a count of distinct publications,
eligible reports, studies or participants. The totals are service metadata at the
probe times, not guarantees that the index remains static during retrieval.

## OpenAlex execution constraints

The current [paging documentation](https://help.openalex.org/api/paging/) permits
basic pagination through 10,000 results. All observed family counts fit below that
limit. It recommends page size 100; size 200 remains accepted as deprecated legacy
behavior. Cursor continuation after the first page requires a free key. A switch
from cursor to documented basic pages preserves query content and field scope; it
does not remove a Boolean term or alter eligibility.

The [authentication documentation](https://help.openalex.org/api/authentication/)
describes a shared anonymous budget and a one-request-per-second limit for Boolean
queries containing more than five operators. Each successful probe reported
`cost_usd: 0.001`. The first response showed 990 of 1,000 credits remaining; after
ten requests the last showed 900. At the observed rate, a fresh complete harvest
would need 93 requests even at legacy page size 200, exceeding the remaining 90
request-equivalents. Other clients sharing the IP can further reduce availability.

The [search documentation](https://help.openalex.org/api/searching/) supports
uppercase Boolean operators and quoted phrases. The existing scoped filter is
deprecated but still works; replacing it with unscoped `search` would broaden to
full text and keywords and must not be done silently. Keep the frozen title and
abstract scope and date limit.

## Crossref scope limit

Crossref is usable for metadata and DOI identity checks. Its [staff explanation of
REST queries](https://community.crossref.org/t/advanced-set-boolean-operators/4596)
states that Boolean operators are unsupported, and corrects the earlier claim that
multiword queries are a simple OR: the match threshold is 20% of query words.
Consequently, pasting EQ1–EQ8 into `query` or `query.bibliographic` cannot be called
an equivalent Boolean search. Preserve C2 as a metadata channel, and record the
unsupported exact-search capability separately from network availability.

## Executable recommendation

Use basic pagination with the unchanged frozen filters, immutable response files,
and an append-only run directory. Fetch smaller families first, then EQ8 and EQ1;
record incomplete families explicitly if service access ends. For each family,
require stable reported totals, no repeated work IDs and a retrieved unique-ID
count equal to the reported total before calling the run complete. Preserve error
responses, stop on authentication or budget limits, and make incomplete status a
nonzero process outcome. Never relabel a first page, missing final page, or changed
count as complete.

Retain bibliographic identity, date, authors, language, location/rights metadata and
reference IDs for downstream work. OpenAlex's [work-attribute
documentation](https://help.openalex.org/data/works/attributes/) says abstracts are
supplied as inverted indexes for legal reasons. Do not automatically republish
reconstructed abstract text or full-source bytes merely because the API returns
them. Abstract metadata is neither a complete primary text nor a numerical
extraction authority.

The probes alone establish no production-search completion, eligibility decision
or source reading. The later execution work is recorded below.

## Execution and storage addendum

The repaired harvester keeps each invocation separately under
`research/searches/auditory/exports/openalex/`; every directory has its own
`MANIFEST.json` using schema `mhac-r005-openalex-harvest/2`. The
[execution summary](database-execution-summary.json) reconciles all retained
occurrences and distinguishes them from distinct API work IDs. The generating
[verification script](summarize_runs.py) verifies retained-file and payload hashes
and refuses mismatched occurrence counts. It makes no screening decisions.

The first production run used the provider's default relevance ordering. Its
duplicate-ID guard detected repeats across pages, leaving affected families
partial. Subsequent runs use the documented
[`publication_date:asc,display_name:asc` sorting](https://help.openalex.org/api/sorting/).
This changes order only, leaving every frozen concept and the cutoff unchanged;
the absence of duplicates is checked instead of assumed. The old occurrences
remain in their original run, including repeats. They must not be silently
replaced or counted as independently sampled evidence.

Public pages are gzip-compressed metadata derivatives with an empty gzip filename
and modification time zero. Each page binds compressed bytes (`sha256`, `bytes`),
decompressed derivative bytes (`payload_sha256`, `payload_bytes`), and original
response bytes (`raw_sha256`, `raw_bytes`). Abstract indexes remain in a private
local cache, identified only by relative cache keys; public pages omit them.
Sensitive URL query parameters are stripped if present. Prior uncompressed
derivatives were checked against their original hashes and compressed losslessly;
every stored gzip roundtrip was verified before the redundant JSON was removed.
No prior page needed URL redaction.

A later 429 explicitly described temporary elevated cluster load and supplied
`Retry-After: 11`; it did not establish exhausted daily budget. Its response is
preserved. The harvester now permits at most two retries per page only for that
explicit temporary-load response, respecting waits of at most 30 seconds. Each
attempt receives a different immutable filename and stays in the manifest.
Authentication and daily-budget refusals are not retried. Count drift, repeated
IDs, truncated pages and transport errors remain explicit failures. An incomplete
invocation exits with code 2. Tests use synthetic responses, never invented live
research records.

## Final observed execution result

Execution stopped at the observed anonymous daily-budget boundary on
2026-11-03T01:06:18Z, without an additional refused request. The final response
reported zero remaining credits. Seven families have a complete run with stable
service count and exactly matching distinct IDs:

| Family | Complete run matches | Complete execution directory |
|---|---:|---|
| EQ2 | 556 | `20261103-database-recovery` |
| EQ3 | 76 | `20261103-database-recovery` |
| EQ4 | 585 | `20261103-database-sort-recovery` |
| EQ5 | 2,112 | `20261103-database-load-recovery` |
| EQ6 | 537 | `20261103-database-recovery` |
| EQ7 | 153 | `20261103-database-recovery` |
| EQ8 | 4,652 | `20261103-database-load-recovery` |

EQ1 remains incomplete: its final sorted run retained 4,200 unique IDs out of the
reported 9,368. The earlier relevance-ordered attempt retained 1,000 occurrences
with 998 unique IDs; its overlap with the sorted attempt remains visible in the
exports and summary. A prefix of a sorted list is not a random sample. No remaining
record may be treated as excluded simply because this search could not retrieve it.

The three runs together retain **17,456 occurrences and 11,898 distinct API work
IDs**, including retry-run overlap and the repeated IDs in failed pages. These
totals must not be compared with the initial 18,039 query-occurrence estimate as a
percentage of corpus coverage: reruns repeat earlier results and families overlap.
There are 93 compressed response artifacts, including retained error attempts,
totalling 16,701,569 bytes. These are search/metadata artifacts, not primary study
readings. The full channel and issue acceptance remain the integrator's decision;
this audit does not assert completed MHAC-R005 or MHAC-R006.
