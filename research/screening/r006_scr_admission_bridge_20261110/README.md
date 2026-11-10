# R006 — guarded title/abstract SCR admission bridge (10 November 2026)

Refs [#6](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/6). This is **not an accepted corpus or a canonical screening registry update**. It addresses the implementation gap between the two accepted, noncanonical first/second-stage source-review ledgers and `mhac-records/1` registration. It does **not** perform an additional independent screen.

## Inputs, decisions and bounded outcome

The admission bridge consumes the exact on-main source-pinned first-pass
[`DECISIONS.json`](../r006_r004_crosslane_20261110/DECISIONS.json) and checks the distinct
[full-text handoff](../r006_fulltext_e2_review_20261110/DECISIONS.json). Four publication records are pinned at
revision 1 in `research/sources/related/records/`, using their individually verified DOI fields.

| Publication | Title/abstract candidate | Full-text / further gate |
|---|---|---|
| Becker 2025, `SRC-REL-BECKER-2025@1` | `include` to full-text queue | `awaiting_text` in the noncanonical follow-up; no article PDF checked |
| Romeo 2025, `SRC-REL-ROMEO-2025@1` | `include` to full-text queue | Provisional `include` in second handoff; requires controlled reading/manifestation and review before a canonical full-text `SCR` |
| Kühne 2020, `SRC-REL-KUHNE-2020@1` | `uncertain` to full-text queue | Provisional E2 exclusion after publisher HTML, **not final** until the protocol §6.2 later pass |
| Romeo 2023, `SRC-REL-ROMEO-2023@1` | `uncertain` to full-text queue | Full 2023 paper not read in this tranche; study/sample overlap with 2025 unknown |

Only the four **title/abstract** v1 candidates can be generated. No full-text
`include`/`exclude` is emitted: `reading_refs`/`review_refs` remain empty,
the 2023 paper is not screened by extrapolating from 2025, and no accepted study,
experiment, sample, independent evidence unit or numerical finding is created.
The frozen evidence cut-off remains 2026-10-04.

## What the bridge verifies

[`build_candidates.py`](build_candidates.py) checks provenance, agent type, fixed
E1–E6 assessment, source ID/revision/DOI, actual abstract-only access and
the two ledgers' nonadmission statuses. It generates an in-memory, schema-checked
record with `kind=screening`, `stage=title_abstract`, `track=empirical`,
`synthetic=false`, exact source pin, unpromoted decision and explicit
single-agent provenance. A record's revision timestamp and actor ID must be
provided by the person/agent **actually performing registration**; the bridge
does not invent past timestamps or independent human screeners.

From the repository root:

```sh
python research/screening/r006_scr_admission_bridge_20261110/build_candidates.py
python -m unittest tests.test_r006_scr_admission_bridge -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

For the integrator **after scientific acceptance of the first-pass source
judgments**, the bridge can emit one reviewable record to stdout:

```sh
python research/screening/r006_scr_admission_bridge_20261110/build_candidates.py \
  --at ACTUAL-YYYY-MM-DDTHH:MM:SSZ --actor-id ACTUAL-AGENT-ID \
  --record SCR-R006-REL-ROMEO-2025-TA
```

Do **not** use this command to claim that the emitted record is admitted. The
integrator must select a canonical `research/screening/records` root, revise the
manifest under `research/registry/state.json`, write each record under its exact
ID filename, run graph/record tests, build/verify generated exports, compare
append-only history, satisfy actual exact-head PR checks and verify merged main.
Changes to `state.json` and exports are intentionally absent here.

### Scientific caution / newly checked supplementary route

[Zenodo record 8042317](https://zenodo.org/records/8042317) is a public,
author-attributed **2023 supplementary-material listing** (`ROMAN2023_Ila_Marta.pdf`),
which describes scripts of robot utterances for the general-context study and
corn-maze navigation video. The listing is a relevant lawful retrieval lead
for G01/E2 and source comparison, **not a full-text reading of the supplement
or main IEEE paper**; its PDF download was not successfully opened/hashed in
this run. The 2023 proceedings [Heriot-Watt record](https://researchportal.hw.ac.uk/en/publications/putting-robots-in-context-challenging-the-influence-of-voice-and-/)
and 2025 article [Heriot-Watt record](https://researchportal.hw.ac.uk/en/publications/the-effect-of-voice-and-repair-strategy-on-trust-formation-and-re/)
identify distinct publications/DOIs and qualitatively different study contexts.
They do not establish independent participant samples. No DOI alias or
`STUDY`/`SAMPLE` record is justified on these observations alone.

## Negative controls, integration and stop condition

[`tests/test_r006_scr_admission_bridge.py`](../../../tests/test_r006_scr_admission_bridge.py)
guards against silently changed decisions, source/DOI drift, duplicate records,
E2 promotions, claimed PDF hashing, sample-count inflation, altered cutoff,
human-review spoofing and unqualified timestamps. The test's fixed time and
actor are explicitly test-only and never admitted as research records.

This tranche uses only R006-owned screening files plus one issue-scoped test.
Neither the frozen protocol, R005 hits, R004 source records, common manifest
nor generated registry exports are modified. Its artifacts are suitable for
integrator review, **not acceptance of #6**. R005 search completion, the eventual
full-text/verification work, all-lane deduplication and the corpus snapshot
remain outstanding. R007–R009 are not dependency-ready.

**Next highest-value action:** integrator review and serialized canonical
admission of the four title/abstract outcomes, followed by independently
verified full-text and publication-to-study-to-sample reconciliation. Preserve
Kühne's separately dated exclusion recheck requirement. Actual human
review/permissions: none received or requested. AI assistance: one GPT-6 agent,
public metadata and accepted on-main source ledgers; no new participant data,
external scholarly review or independently verified study outcomes.
