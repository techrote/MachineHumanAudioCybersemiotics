# R005 — bounded EQ1 same-invocation adjacency check (11 November 2026)

**Refs #5; R006 #6 and Integration handoff.** Owner priority: primary-source custody and corpus decisions take precedence over this search continuity check. Authentic Stevens 2009 article bytes are **not** retained in approved private custody, and Romeo 2023's six-page IEEE report remains unread. Neither issue is closed by this experiment.

## Purpose and source lineage

OpenAlex C1 frozen EQ1 `title_and_abstract.search`, **publication cutoff 2026-10-04**. The [accepted raw page-44 observation](../eq1-pages44-47-20261111/OBSERVATIONS.json) is the exact as-run URL authority: same query blocks, cutoff, date/title ascending sort, `per_page=100`, bibliographic `select`. This proposal changes only `page=44` to `page=45`, makes two adjacent requests in **one invocation** if the first succeeds, and stops on the first HTTP failure. It never pastes or joins distinct dated provider snapshots.

A prior [cross-run comparison](../eq1-crossrun-boundary-20261111/README.md) proved that eight OpenAlex work IDs at 10-Nov page-43 positions 93–100 recur at 11-Nov page-44 positions 1–8, while the provider total changed 9,275 to 9,280. Page 45 of that later invocation returned **429**. Accordingly neither the old 4,200-item sorted prefix nor the 11-Nov page-44 response certifies completion.

## What this exact-scoped PR executes

`tests/test_r005_eq1_single_snapshot_20261111.py` includes fail-closed offline query preservation, wrong-page/date, overlapping-ID and count-drift negatives. One bounded live acquisition is enabled **only** in GitHub Actions PR CI on head branch `mhac-r005/eq1-single-snapshot-20261111-0615`, and disabled after this directory receives `ATTEMPTED.json`. The original HTTP response for each successful page is represented as gzipped base64 chunks in the Actions job log, with source URL, response content hash, receipt time/header, ordered work IDs and reported total. The job may instead emit `MHAC_R005_EQ1_SINGLE_BLOCKER` and stop without disguising 429 as success.

**Important:** A source acquisition must actually run, and any genuine returned bytes must be reconstructed, verified and added in an R005-owned follow-up commit before claiming immutable repository retention. A successful unit test alone is not network evidence or a completed production search. A source query that returns HTTP 429 is an *observed access limit*, not an inferred empty result set. Do not rerun a rejected page in a loop or bypass any API quota.

## Claim and handoff boundary

- **R006:** No added eligible publication, independent experiment/cohort or new title/abstract decision. A discovery ID is not an independent empirical sample. R006 alone owns DOI/publication identity, E1–E6 screening and full-text status changes.
- **Integration:** No changes here to shared index, hit records or generated selection exports. Accept only source-exact responses, hashes, and candid partial status. Review any cross-page duplicate or moving-total evidence before considering separate noncanonical metadata occurrence registration.
- **R004/Integration original-source gate:** An approved private durable destination and rights/attribution/retention basis for authentic Stevens 2009 Europe PMC XML remains necessary. Actual original bytes, custody receipt, source-pinned semantic assessment and any R006 eligibility transition remain absent. Romeo 2023 original IEEE text remains inaccessible from previously checked publisher/institutional routes.

No external human reviewer, publisher subscription, novel database export, abstract/full article or audio assessment, new empirical statistic or corpus admission is claimed. Model-assisted source/integrity checks are not independent scientific review. Full repository and exact-final-head CI are required, then independent Integration review and guarded merge; a partial PR remains Draft/HOLD.
