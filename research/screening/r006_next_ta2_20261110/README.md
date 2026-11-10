# R006 — Source-led next empirical title/abstract tranche (10 November 2026)

**Refs #6 · R006-only Draft/HOLD pending Integration-owned serialization.**

Base accepted `main` at preparation: `7e2975466f5c3fb43eb7d099a879090bc5d24818` (the earlier six canonical TA decisions from #109 and #132 already accepted). Authored source-pinned original records at **2026-11-10T15:33:58.305Z** by **agent `gpt6-r006-ta-noise-urgency-20261110`** using the original SAGE publisher abstract and an indexed PubMed original-paper abstract via `web.run`. This was one AI first pass, **not** a human assessor, a separate later review, empirical extraction or corpus admission. Frozen v1 §§4, 6.2–6.4, 10, 11; search cutoff **2026-10-04** unchanged.

## Newly authored, source-pinned TA decisions

| Canonical screening/source | Primary publisher and exact edition | Actually accessed and disposition |
|---|---|---|
| `SCR-R006-SABIC-2021-NOISE-TA` → `SRC-R006-H-SABIC-UNDERSTANDING@1` | [Šabić, Chen & MacDonald, *Toward a Better Understanding of In-Vehicle Auditory Warnings and Background Noise*](https://journals.sagepub.com/doi/abs/10.1177/0018720819879311). DOI `10.1177/0018720819879311`; *Human Factors* **63(2), 312–335**, issue March **2021**, online **2019-10-08**. | Public original publisher **Abstract** (Objective–Application) verified via direct HTML retrieval. Search-index rendering additionally surfaced fragments labelled `Current Study`, `Experiment 1 > Method > Participants`, `General Discussion`, but direct publisher `/doi/full` fetch was **403**: these are discovery-only snippets, **not** qualified original full-text access. Includes simulated driving and three warning representations; **include to FT retrieval** under E1–E6. |
| `SCR-R006-ARRABITO-2004-URGENCY-TA` → `SRC-R006-F-ARRABITO-URGENCY@1` | [Arrabito, Mondor & Kent, *Judging the urgency of non-verbal auditory alarms: a case study*](https://www.tandfonline.com/doi/abs/10.1080/0014013042000193282). DOI `10.1080/0014013042000193282`; *Ergonomics* **47(8), 821–840**, **2004**. Publisher HTML online-post date 2007-02-20 differs from issue year; [PubMed 15204277](https://pubmed.ncbi.nlm.nih.gov/15204277/) establishes the 2004-06-22 issue and displays the original-paper abstract. | Direct Taylor & Francis publisher abstract/full route returned **403**; complete **PubMed-indexed original journal-paper Abstract** was read instead. Pilots/non-pilots judge urgency of five helicopter alarms; **include to FT retrieval** under E1–E6. No original publisher full text or PDF read. |

The R006 registry already verified both publication DOIs/metadata through Crossref on 6 November. No new source or search-hit identity was fabricated. `SRC-R006-H-SABIC-UNDERSTANDING@1` preserves `HIT-R005R-C1RECOVERY-EQ1-00046`. `SRC-R006-F-ARRABITO-URGENCY@1` preserves `HIT-R005R-C1LOAD-EQ1-01348`, `HIT-R005R-C1RECOVERY-EQ1-00109` and `HIT-R005R-C1RECOVERY-EQ2-00074`. Four discovery occurrences are four **hit paths**, not four studies.

**Scope and custody:** The SAGE original publisher abstract and Arrabito's PubMed-indexed original-paper abstract were read on **2026-11-10**, without authentication; Taylor & Francis directly returned **403** and Arrabito publisher HTML/complete paper could not be read. Original HTTP response `Date` timestamps and bytes were **not** captured. No article PDF, original HTML byte archive, SHA-256, audio, detailed tables/figures, complete Methods/Results or rights grant was obtained. Public readability does not establish permission to redistribute. The public SAGE abstract is retrievable; a separate SAGE full-article URL was **403 Forbidden** on direct browser retrieval on 10 November. An indexed search result contained apparent body passages, but these must **not** be represented as direct publisher article access or a completed full-text reading. The exact HTTP response Date was not captured. No canonical R006 FT gate is satisfied. A 2021 issue date is not a new post-cutoff article merely because the issue was after online-first publication. Publisher-reported two experiments (Šabić) have **not** been instantiated as independent EXP or SAMPLE records; any related first-author thesis, earlier warnings or participant overlap remains unadjudicated. No quantitative outcomes were extracted.

## Canonical gate arithmetic and Integration coordination

| Gate | Accepted main at base | R006-only authored in this Draft |
|---|---:|---:|
| TA decisions (3 include, 3 uncertain accepted) | 6 | +2 proposed `include`, not exported |
| Full-text exclusions / awaiting source / absent required FT | 1 / 1 / 4 | unchanged scientifically; prospective absent FT would rise to 6 after canonical serialization |
| FT inclusions | 0 | 0 |
| Admitted studies / experiments / samples | 0 / 0 / 0 | 0 / 0 / 0 |
| Selected Track E / G publications | 0 / 0 | 0 / 0 |

The **first four original TA decisions are already canonically accepted**; this work does not re-screen or overwrite them. Prior Edworthy/Nees first-pass decisions are also accepted. The R006 author did not edit `research/registry/generated/**`, common manifests, R004/R005 records, any other worker's branch, or the frozen protocol. The bounded `verify.py` and issue-specific tests check original source DOI/discovery pins, first AI registrar/time and falsified review/FT claims; they **do not validate a generated/export admission or freeze future scientific counts**.

**Integration-only handoff:** Independently review the SAGE publisher abstract, PubMed's original-journal-paper abstract and decision limits, compare the actual first-revision actor/date and verified source/hit pins, and reconstruct on a **separate Integration-owned branch** with `python tools/validate.py --write-exports` plus any affected records index/evidence-flow views. Run `python -m unittest discover -s tests -v`, `python tools/validate.py` (history/previous-ref as applicable), `python -m tools.build_record_fixtures --check`, issue-specific `verify.py`, exact-final-head PR Actions and merged-main push Actions. Do not overwrite this R006 author branch. It is expected that raw Draft source plus stale generated exports will **not** pass the repository validator; do not claim CI success or merge before reconciliation, approvals and exact-head verification. Close superseded Drafts only on an independently accepted replacement, not by deleting their source.

**R005/R004 handoff:** Retain and register lawful, version-stable original source bytes and reading scope where available. Highest-leverage already-open first-FT gates remain Becker 2025 `10.1145/3706066` and Romeo 2025 `10.1145/3711938`, with separate Romeo 2023 original IEEE article `10.1109/RO-MAN57019.2023.10309631`. The Šabić original-publisher **abstract** is available, but the direct full-article route returned 403; R005/source owners should seek a lawful archival author/publisher original and preserve actual bytes, edition/rights and source identity. Arrabito also needs lawful original FT; its directly consulted abstract was PubMed-indexed rather than the publisher's 403-protected page. Indexed article-looking web text alone does not qualify source custody. The R005 source-custody tool Draft #133 is independently owned by R005; do not edit it from R006.

**R006 alone** makes full-text E1–E6 and publication→study→experiment→sample identity decisions after source/reading qualification. Until full-text inclusions and sample overlap are resolved, R007/R008 have **zero selected Track E/G corpus** and neither issue can claim downstream corpus acceptance. #5/#6 stay open.

Reproduction (checker limited to authored TA, not scientific admission):

```bash
python research/screening/r006_next_ta2_20261110/verify.py
python -m unittest tests.test_r006_next_ta2_20261110 -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```
