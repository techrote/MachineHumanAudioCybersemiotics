# R005 — bounded EQ1 same-invocation adjacency check (11 November 2026)

**Refs #5; R006 #6 and Integration handoff.** Owner priority: primary-source custody and corpus decisions take precedence over this search continuity check. Authentic Stevens 2009 article bytes are **not** retained in approved private custody, and Romeo 2023's six-page IEEE report remains unread. Neither issue is closed by this experiment.

## Purpose and source lineage

OpenAlex C1 frozen EQ1 `title_and_abstract.search`, **publication cutoff 2026-10-04**. The [accepted raw page-44 observation](../eq1-pages44-47-20261111/OBSERVATIONS.json) is the exact as-run URL authority: same query blocks, cutoff, date/title ascending sort, `per_page=100`, bibliographic `select`. This proposal changes only `page=44` to `page=45`, makes two adjacent requests in **one invocation** if the first succeeds, and stops on the first HTTP failure. It never pastes or joins distinct dated provider snapshots.

A prior [cross-run comparison](../eq1-crossrun-boundary-20261111/README.md) proved that eight OpenAlex work IDs at 10-Nov page-43 positions 93–100 recur at 11-Nov page-44 positions 1–8, while the provider total changed 9,275 to 9,280. Page 45 of that later invocation returned **429**. Accordingly neither the old 4,200-item sorted prefix nor the 11-Nov page-44 response certifies completion.

## What this exact-scoped PR executes

`tests/test_r005_eq1_single_snapshot_20261111.py` includes fail-closed offline query preservation, wrong-page/date, overlapping-ID and count-drift negatives. The initial one-off bounded live acquisition was enabled **only** in GitHub Actions PR CI on head branch `mhac-r005/eq1-single-snapshot-20261111-0615`, and is now disabled by committed `ATTEMPTED.json`. The original HTTP response for each successful page is represented as gzipped base64 chunks in the Actions job log, with source URL, response content hash, receipt time/header, ordered work IDs and reported total. The job may instead emit `MHAC_R005_EQ1_SINGLE_BLOCKER` and stop without disguising 429 as success.

**Result:** The original HTTP acquisition did run and actual response bytes were reconstructed, pinned and committed in this R005-only tranche, subject to final-head offline qualification. A successful unit test alone is not network evidence or a completed production search. A source query that returns HTTP 429 is an *observed access limit*, not an inferred empty result set. Do not rerun a rejected page in a loop or bypass any API quota.


## Executed original-source acquisition — 11 November 2026, 06:21 UTC

**The planned one-shot public OpenAlex acquisition actually succeeded.** [PR-head GitHub Actions job 130361702053](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42971784143/job/130361702053) at original probe head `7bf423379444193d9b98010d065df6e43983fc22` made two unauthenticated public C1 HTTPS GET requests without credentials, quota circumvention or paid database access.

| Original HTTP result | Page 44 | Page 45 |
|---|---|---|
| UTC request start | 2026-11-11T06:21:02.340Z | 2026-11-11T06:21:04.562Z |
| UTC received | 2026-11-11T06:21:03.361Z | 2026-11-11T06:21:05.145Z |
| HTTP status / provider Date | 200 / 06:21:03 GMT | 200 / 06:21:05 GMT |
| Raw JSON bytes | 39,477 | 38,861 |
| Raw JSON SHA-256 | `402efcd0b63bf66a3d599338acea8d58ce05c38393574bce2b9b4e8493bd1ef9` | `f217415a50a241d14a89b51f8a9ab82806580eb5fd27e42a9695d8e5941488b8` |
| Deterministic gzip bytes | 8,441 | 8,224 |
| Gzip SHA-256 | `13e688843b5911635af8aba51a199c42f25c5c05cdeb4a9bcccc675b02cfa4d5` | `fd119c9fc0467d37613180f85b84aa32b48e511fc45288bff8f353d40d2c527d` |
| Provider total / page work IDs | 9,280 / 100 | 9,280 / 100 |

The **entire original HTTP response bodies are now retained as byte-verifiable gzip** in `page-44.json.gz` and `page-45.json.gz`, reconstructed from the actual GitHub Actions base64 chunks without altering the original JSON. [OBSERVATIONS.json](OBSERVATIONS.json) records exact as-run URL, HTTP dates, complete ordered work IDs, content hashes, file hashes and custody boundaries. [ATTEMPTED.json](ATTEMPTED.json) disables subsequent live source requests on this branch; offline CI replays the retained originals.

**Measured boundary:** page 44 and page 45 were fetched in this same invocation with identical provider counts (9,280), and each contains 100 unique work IDs; **zero work IDs occur in both pages**. This verifies a *bounded local adjacency pair*, not stability across historical invocations, complete EQ1 search coverage or 200 newly distinct publications. The previously observed page-43→44 eight-ID cross-run overlap remains unreconciled for a complete contiguous harvest. A page-45 HTTP 429 in the *earlier* invocation is historical and is not erased by the later successful response.

## Verification and scientific status

Run `python -m unittest tests.test_r005_eq1_single_snapshot_20261111 -v` to replay both original JSON bodies, verify original and gzip SHA-256/byte sizes, frozen query/cutoff, 100 ordered work IDs per page, identical provider counts and zero adjacent-page overlap. Negative tests reject synthetic identity collision, count drift, changed dates and modified payload hashes. The complete repository suite, history-aware validator and fixture check are mandatory for the final head.

**R006/Integration handoff:** The returned records are only unscreened metadata and have **not** been registered as canonical `search_hit` records or promoted to publications/experiments/samples; no R006 screening was conducted. Publication/study/experiment/sample identity and E1–E6 eligibility remain exclusively R006-owned; Integration must review source fidelity and generated-manifest impact before guarded merge. The canonical pre-existing R006 ledger remains nine TA decisions (six to FT, three uncertain), FT five pending/three awaiting/one excluded/**zero included**, admitted publications/studies/experiments/samples **0/0/0/0**, selected E/G **0/0**. These are the unchanged accepted baseline, not new admissions.

The higher-priority unresolved primary-source action remains **owner authorization for private, rights-compliant, durable retention of authentic Stevens 2009 XML**, followed by actual source manifestation and source-pinned semantic reading through R004/Integration and R006 final adjudication. Romeo 2023's original IEEE full text also remains absent. C1 page continuity alone does not close #5 or #6, unblock #7/#8 or establish human assessment.

## Claim and handoff boundary

- **R006:** No added eligible publication, independent experiment/cohort or new title/abstract decision. A discovery ID is not an independent empirical sample. R006 alone owns DOI/publication identity, E1–E6 screening and full-text status changes.
- **Integration:** No changes here to shared index, hit records or generated selection exports. Accept only source-exact responses, hashes, and candid partial status. Review any cross-page duplicate or moving-total evidence before considering separate noncanonical metadata occurrence registration.
- **R004/Integration original-source gate:** An approved private durable destination and rights/attribution/retention basis for authentic Stevens 2009 Europe PMC XML remains necessary. Actual original bytes, custody receipt, source-pinned semantic assessment and any R006 eligibility transition remain absent. Romeo 2023 original IEEE text remains inaccessible from previously checked publisher/institutional routes.

No external human reviewer, publisher subscription, novel database export, abstract/full article or audio assessment, new empirical statistic or corpus admission is claimed. Model-assisted source/integrity checks are not independent scientific review. Full repository and exact-final-head CI are required; independent Integration review and guarded merge remain necessary, so this partial PR remains Draft/HOLD.
