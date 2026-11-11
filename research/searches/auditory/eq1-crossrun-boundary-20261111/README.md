# R005 EQ1 cross-run boundary reconciliation — 11 November 2026

**Refs #5; handoff to R006 #6 and the Integration Shepherd.** Frozen protocol v1, EQ1 OpenAlex C1 `title_and_abstract.search`, literature cutoff **2026-10-04** unchanged. This is a new *offline cross-run integrity finding* from already accepted original response/manifest evidence, **not** an additional database search, publisher-text reading, screening decision or eligible publication.

## Source-exact provenance and result

| Accepted source | Invocation and source boundary | Immutable pin |
|---|---|---|
| [10 Nov page-42/43 observation](../eq1-boundary-2026-11-10/OBSERVATIONS.json) | OpenAlex public anonymous API, 10 Nov 2026 around 13:11 UTC; HTTP 200; pages 42/43, 100 results each; reported total **9,275** | Git blob SHA-1 `443d3702bda94cb4fcd0cbfeda8b92354ec8b381` |
| [11 Nov page-44 original-response evidence](../eq1-pages44-47-20261111/OBSERVATIONS.json) | 11 Nov 2026 00:15:58.579–00:16:00.107 UTC; HTTP 200; 100 results; reported total **9,280** | Git blob SHA-1 `b61a018a7ec8888811e918611e55ebd584bb8fdf`; original 39,478-byte JSON SHA-256 `24e4a8c62087b489ea9e038c8ca22cfa8d8b07ba93e0152c9d8ec19114d4103b` |

The [original 11 Nov HTTP acquisition log](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42929964491/job/130225913549) and compressed original response in the accepted page-44 directory are the acquisition evidence. This run re-analysed their accepted records; **no new HTTP request or original-response byte capture** occurred. The two invocations have identical EQ1 concept filter, cutoff, page size and publication-date/title sort. The newer response reduces output columns only.

**Measured boundary failure:** The **last eight** OpenAlex work IDs of the 10 Nov page 43 (positions **93–100**) are exactly the **first eight** work IDs of the 11 Nov page 44 (positions **1–8**). No page-42 ID occurs on page 44. Thus concatenating page 44 with the earlier snapshot would introduce **at least eight duplicate discovery occurrences**. The other **92** page-44 IDs were absent from just pages 42/43; their uniqueness against older pages, identity with publications, study eligibility and sample independence remain **unverified**. A changed reported total (9,275 to 9,280) establishes cross-run drift, but not its mechanism: index updates, tie-order changes and other causes have not been distinguished.

The same 11 Nov invocation received **HTTP 429** when requesting page 45 at 00:16:01.308 UTC; pages 46–47 were not attempted. The historical sorted 4,200/9,368 checkpoint is a separate dated incomplete invocation. **Do not label any concatenation a contiguous completed EQ1 run, register 92 new publications or infer empirical counts from this metadata.**

The full eight work identifiers, date annotations, position pairs, source SHA pins and conservative gates are serialised in [OBSERVATIONS.json](OBSERVATIONS.json). Reproduction uses no network:

```sh
python research/searches/auditory/eq1-crossrun-boundary-20261111/check_boundary.py
python -m unittest tests.test_r005_eq1_crossrun_boundary_20261111 -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

The checker verifies Git-blob pins, original response hash metadata, exact frozen query/cutoff, 100 unique identifiers per page, cross-run overlap positions, retained 429 and explicit nonadmission declarations. Eight regression methods challenge tampering, query/sort changes, fabricated page uniqueness, rate-limit erasure and count drift.

## Scientific boundary and handoff

**R006:** Original four canonical title/abstract candidates (Becker 2025, Romeo 2025, Kühne 2020 and Romeo 2023) are already recorded on main. No R006 records were changed here. The latest previously verified ledger had nine TA decisions (six to full-text and three uncertain), FT five pending/three awaiting/one excluded/**zero included**, and **zero admitted publications, studies, experiments or independent samples**. These are dated accepted baseline figures, not new screening. Publication–experiment–participant identity and eligibility remain exclusively R006's responsibility.

**R004 / Integration:** Source custody still blocks final Stevens/Becker/Romeo full-text admission: a real, rights-compliant, durably stored original article manifestation and source-pinned actual reading are required. The original Romeo 2023 IEEE article (DOI `10.1109/RO-MAN57019.2023.10309631`, pp.2045–2050) remains unavailable for full-text reading; its Zenodo v1 `10.5281/zenodo.8042317` script supplement is a separate file, not a substitute. Do not invent access or a rights decision. Independently review this overlap evidence before any shared search-hit registration, keep count aggregates untouched, and admit no studies from discovery metadata.

**R005:** The next highest-value feasible search action after lawful quota recovery is a *single-snapshot, adjacent-page, raw-response-backed EQ1 boundary check* with stable or explicitly divergent totals and IDs. Check old/new overlap and continuity before allocating hit IDs or attempting the next bounded page. If the live provider again returns 429, stop without looping. Work on original-article custody and remaining real C9/ICAD coverage if the API is unavailable.

No human or independent second assessor, original-article methods/results reading, new DOI resolution or stimulus/audio listening is claimed. Structural tests are only provenance integrity checks; they are not scientific validation.
