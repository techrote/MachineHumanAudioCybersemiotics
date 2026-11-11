# R005 — original-response EQ1 pages 45–47, single invocation (11 November 2026)

**Refs #5; R006 #6 / Integration handoff.** Base accepted main `ece75ff89d3668a3ebea12a186e5329cfb05e7fe`, original acquisition source head `cac89849f27c4d02c3aa92df3437d954d4e31d0b`. Frozen protocol v1, unchanged publication cutoff **2026-10-04**. This adds *metadata discovery provenance*, not eligible publications, independent experiments, audio listening, human assessment or corpus selection.

## Actual original source and lawful access

On **11 November 2026**, GitHub Actions [source acquisition job](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42978112350/job/130381869391) performed exactly three **unauthenticated public HTTPS GETs** to the OpenAlex C1 works API in one bounded invocation, with no paid account, credential, bypass or retry. The complete source URLs, provider HTTP Date, original request/receive UTC, raw-response SHA-256/length, deterministic gzip SHA-256/length and ordered 100 work IDs per page are pinned in [OBSERVATIONS.json](OBSERVATIONS.json). Original HTTP JSON entity bytes are preserved losslessly in `page-{45,46,47}.json.gz` reconstructed from actual source-log base64 chunks. A committed [one-shot guard](ATTEMPTED.json) prevents repeat live requests on this branch.

| Page | Received UTC | HTTP | Original bytes | SHA-256 original JSON | Provider total / work IDs |
|---|---|---|---:|---|---|
| 45 | 2026-11-11T07:15:17.077+00:00 | 200 | 38861 | `7fb8dbd73e30552841db83e32fb298df957792df88a75ed8b7d0c283734055a4` | 9280 / 100 |
| 46 | 2026-11-11T07:15:19.111+00:00 | 200 | 38053 | `5d25235feb33c01439fd76033903d8d252117a307c1be58a8871d38d0de1d2c0` | 9280 / 100 |
| 47 | 2026-11-11T07:15:20.982+00:00 | 200 | 38978 | `99ddab5df4a9504e60817ac026596e01eeec869f44a2a909af35037babe7c2a7` | 9280 / 100 |

## Reconciliation and limitations

All three pages have the same provider total **9,280**, each has 100 unique work IDs and **no adjacent-page overlap**, hence 300 different **metadata work identifiers within this invocation**. The page-45 ordered 100-ID vector is exactly the same as the separately acquired 06:21 UTC page 45 on accepted main; **the raw JSON SHA-256 differs**. This verifies that one anchor's ordered identity remained stable across these two distinct requests, **not** that other pages or the entire prefix remained stable. The earlier 10→11 November **eight-ID page-43/44 cross-invocation overlap** persists, so EQ1 is **not** a completed contiguous search. No original primary article texts, article PDFs, recordings or abstracts were read: the `select` fields are bibliographic metadata only. No new canonical R006 `search_hit` or TA/FT records were registered.

The parent four-candidate TA tranche was already canonical through #109; the historically accepted R006 gate remains **9 TA, 5 FT pending / 3 awaiting_text / 1 excluded / 0 included, 0/0/0/0 publications/studies/experiments/independent samples admitted, Track E/G 0/0**. New eligible records **0**, title/abstract and full-text decisions **0**, human assessors **0**. Distinct work IDs are not distinct eligible publications, human samples or independent studies.

**Owner/R004/Integration gate:** approved private durable source-retention location and lawful rights/attribution basis for authentic Stevens 2009 Europe PMC XML, followed by actual retained-byte SHA-256 and source manifestation. The prior 74,338-byte original response hash is not custody. Romeo 2023 original IEEE report remains unavailable. **R006 alone** may resolve DOI/publication identity, E1–E6 and publication→experiment→sample relations after qualifying source evidence. Integration alone owns shared manifest/selection/export changes and guarded merge.

## Reproduction and state

```sh
python -m unittest tests.test_r005_eq1_45to47_20261111 tests.test_r005_eq1_45to47_replay_20261111 -v
python -m unittest discover -s tests
python tools/validate.py
python -m tools.build_record_fixtures --check
```

The source-branch test has a genuine HTTP acquisition marker but **never reruns while ATTEMPTED.json exists**. The offline checker verifies original gzip/raw bytes and hashes, URLs, cutoff, ordered hits, no overlap and conservative nonadmission flags, with synthetic negative controls. Exact final-head CI and independent Integration review are required before merge; structural CI is not scientific validation.

**Next highest-value R005 gap:** continue bounded EQ1 only after a fresh source/authority and quota reconciliation; ICAD venue-year and complete review/included-report citation chains remain incomplete. Do not concatenate distinct dated snapshots or count metadata as experiments.
