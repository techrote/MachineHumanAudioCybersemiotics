# R005 — Offline identity-overlap audit for the frozen EQ1 boundary (10 November 2026)

**Refs #5; downstream #6.** Source baseline `1daa81b078cda22f752c2f01da46da25370dab84` (accepted R006 eight-title/abstract main plus Integration's exact-byte attestation bridge). This is a **read-only, executable comparison of genuinely retained evidence**, not a new API request, complete EQ1 search, full-text reading, search-hit registration, eligibility decision or human screening. No existing R005, R006 or generated manifest is modified.

## Original retrievals, source class and lawful boundary

- **3 November 2026:** Frozen EQ1 query, OpenAlex C1 `title_and_abstract.search`, sorted by `publication_date:asc,display_name:asc`, with publication cutoff **2026-10-04**, historical `20261103-database-load-recovery/MANIFEST.json`: 4,200 distinct API IDs/occurrences in 21 successful 200-row pages, two preserved 429 attempts; provider reported 9,368 matches. Each archived gzip **metadata derivative** can be verified against its manifest compressed and uncompressed SHA-256. Original source response hashes are documented, but original raw responses and full abstract indexes are not retained publicly.
- **10 November 2026, HTTP Date 13:11:33/13:11:36 UTC:** [Original GitHub-runner retrieval, Actions #42822235351](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42822235351/job/129850397555) made two actual anonymous, public, unauthenticated OpenAlex metadata GETs at `per_page=100`, pages **42 and 43** with the unchanged Boolean filter, date cutoff and sort. Both returned HTTP 200; reported results **9,275**. The original response byte hashes and counts are pinned in [OBSERVATIONS.json](../eq1-boundary-2026-11-10/OBSERVATIONS.json). **The original November 10 response bodies were not retained**; their SHA-256 values are receipt claims, not independently rehashable blobs.
- This audit reads only those already retained artifacts, with no new network response or new access claim. Public bibliographic API metadata is used for lawful discovery. **No publisher article/full text/audio file or new primary study was accessed** by this audit. Reading extent: metadata rows and historical capture manifest, not article Methods/Results or participant-level evidence. No database export from ACM/IEEE/C7 is claimed.

## Exact observed boundary and interpretation

| Measure | Historical 3 Nov | Current observation 10 Nov |
|---|---:|---:|
| Provider-reported EQ1 total | 9,368 | 9,275 |
| Retained EQ1 works under this invocation | 4,200 | 200 observed, NOT registered |
| Page size | 200 | 100 |
| Anchor OpenAlex ID `W2520134007` | Historic sorted rank 4,200 | New observed rank **4,142** (page 42, row 42) |
| Original paper identity for anchor | Historical API work ID only | Same work ID; no primary-paper verification |
| Canonical new search occurrences | — | **0** |
| Study / experiment / independent sample admissions | — | **0 / 0 / 0** |

The provider total declined by **93**, and the same anchor has moved **58 ranked places earlier**. Those are distinct observations; **neither difference is a count of deleted papers, added papers, unique publications or participants**. Page 43 currently begins with `W2551005744`, DOI `10.1016/j.apergo.2016.11.002`, an unscreened title-level lead on auditory/tactile warnings in noise, *not* a canonical R006 inclusion.

The executable audit makes the additional, higher-value check against the **actual historical 4,200 stored work IDs**: for the 200 current rows it calculates how many already occur in that historical prefix, and how many are not in it. It checks immutable historical derivative hashes, page gaps/retries, unique IDs, equality of frozen Boolean filter, sort/cutoff, preserved HTTP receipt metadata and false screening claims. The historical prefix is the only safe comparator; lack of appearance in it **does not imply a globally new publication or search occurrence**.

The existing 10 November observation contains metadata row selections, not raw HTTP response bodies; this verifier cannot reconstruct or reauthenticate those exact original HTTP bytes or infer full historic query-set overlap outside the 200-row window. The outcome is **continuation unsafe**, not a guessed corrected search count.

## Reproduce offline on exact source

```sh
python3 research/searches/auditory/eq1-drift-audit-2026-11-10/audit.py
python3 research/searches/auditory/eq1-drift-audit-2026-11-10/audit.py --require-append-safe  # expected exit 2
python3 -m unittest tests.test_r005_eq1_immutable_overlap -v
python3 -m unittest discover -s tests
python3 tools/validate.py
python3 -m tools.build_record_fixtures --check
```

The script prints source-computed counts and refuses to certify that page 43 can be appended as historical hits 4,201–4,300. The negative controls reject changed cutoff, inconsistent provider totals, duplicate IDs, changed sort, artificial study/hit promotion and damaged historical hashes. Passing these engineering controls **does not** establish scientific eligibility.

## Downstream gate and exact owner handoff

**R006/Integration:** current baseline has eight first-pass title/abstract decisions (five proceed to full-text, three uncertain), **zero full-text inclusions, zero admitted studies/experiments/independent samples and no selected Track E/G corpus**. The newly audited `W2551005744` remains an **unscreened lead**, not a duplicated or selected source. Only R006 may link occurrence → publication → experiment → independent sample and apply frozen v1 E1–E6. Ask R006 to check already-registered discovery paths before proposing a new screening decision; this audit does not write its ledger. Integration owns shared indexes/exports and any guarded merge.

**Single high-leverage R004/Integration source action:** lawfully retain and privately register exact-byte original Becker 2025 (DOI `10.1145/3706066`) and Romeo 2025 (DOI `10.1145/3711938`) PDF instances, with capture UTC, byte SHA-256, rights/edition/reading scope, using the recently integrated R005 source-custody guard. Romeo 2023 IEEE original (DOI `10.1109/RO-MAN57019.2023.10309631`) separately remains unavailable; its Zenodo supplement cannot qualify as the primary report. R006 then alone makes source-based full-text decisions. This independent EQ1 reconciliation does not resolve that external original-source gate.

**Next bounded R005 retrieval:** when lawful API allowance and exact raw-response retention can be established, begin a **new complete EQ1 invocation**, not a splice from the old sorted prefix. Retain every new HTTP response securely, log real requests/retries, deduplicate against all prior R005 search-hit identities with R006 coordination, and only then register new canonical occurrences. C5 ICAD has an existing worker PR #122; do not duplicate it. The frozen 2026-10-04 publication cutoff and R005 #5/R006 #6 open state remain in force. R007/R008 are not selected-corpus-ready.
