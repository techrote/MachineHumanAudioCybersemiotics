# R006 — Nees 2016 original-author manuscript: eligibility preflight (10 November 2026)

**Disposition: `pending`, NOT included or counted.** Refs #6. Source base [`51a399bbe4138c52b7da4840ff6d9a6b7ed9b874`](https://github.com/techrote/MachineHumanAudioCybersemiotics/commit/51a399bbe4138c52b7da4840ff6d9a6b7ed9b874). R005 author [Draft #144](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/144) remains a distinct, unmerged source-provenance proposal. R006 has not modified that branch, R005 records, shared manifests or exports.

## Exact edition and accessed original text

Nees, M. A., Helbein, B. and Porter, A. (2016), *Speech Auditory Alerts Promote Memory for Alerted Events in a Video-Simulated Self-Driving Car Ride*, *Human Factors* 58(3), 416–426. [Publisher DOI 10.1177/0018720816629279](https://doi.org/10.1177/0018720816629279); first online 16 February 2016, issue May 2016. The [corresponding-author publication listing](https://michaelanees.com/publications) links a [29-page author-hosted PDF](https://static1.squarespace.com/static/51bb699de4b0820e6e77849b/t/56d63bd2a3360c6369802fc3/1456880594996/Nees+et+al+Human+Factors+2016+author+preprint.pdf). Its title leaf says **submitted**; the publishing route also calls it a preprint. Neither identity nor exact-byte equivalence with the SAGE version of record is established.

A GPT-6 agent re-examined the author manuscript via the public PDF text renderer and inspected screenshots of PDF indices **9, 10, 13 and 14** on 10 November 2026. The consulted original ranges were the title and abstract, Introduction and study objectives, **Methods printed pp. 10–14** (participants, Table 1 alerts, three conditions, procedure and response tasks), **Results pp. 14–16**, and selected Discussion/limitations **pp. 17–18**. The complete manuscript was not certified read; no audio was played. No original HTTP response bytes, headers, acquired-at timestamp, current PDF SHA-256, retained binary, reuse grant, or independent human assessor was obtained. Decision recorded **18:29:32 UTC**, not presented as an HTTP acquisition time.

This is *tool-mediated original-document reading*, not a hashed-source numerical extraction, verified raw-source custody, publisher VoR equivalence, or actual participant dataset access. The author manuscript is useful scientific reading evidence but is not a substitute for exact-byte provenance where required.

## Frozen Track E E1–E6 decision matrix

| Rule | Source evidence inspected | Current assessment |
|---|---|---|
| **E1 Human participants** | Manuscript Method, printed p. 10: recruitment and analysis exclusions of human student drivers | Provisionally supported |
| **E2 Machine audio message** | Table 1 and Alert conditions, pp. 11–12: speech TTS and auditory icons convey low fuel, hazards, weather and other system/road status | Provisionally supported; not mere ambient audio |
| **E3 Comparison** | pp. 9–13: three randomized between-subject arms — visual text, auditory icons and speech | Provisionally supported |
| **E4 Eligible outcome** | pp. 13–16: recall of alerted events, perceived effort/workload, annoyance and ratings of usefulness/confidence | Provisionally supported |
| **E5 Primary method/results** | Original Methods and Results visible in author manuscript; one described experiment | Provisionally supported |
| **E6 Published before cutoff** | Original SAGE publication 2016-02-16, well before frozen **2026-10-04** | Supported |

**Participant identity is not multiply admitted.** The manuscript reports 90 recruited, five excluded and 85 analysed, across arms 30 visual / 28 auditory icons / 27 speech. These are authors' claims, not extracted canonical numbers. One described experimental participant cohort, three between-subject conditions, three videos, and several dependent outcomes do **not** constitute three independent studies or samples. Whether the 2016 author manuscript has extensions or shares participants with other reports remains open.

## Why no full-text `include` has been serialized

The frozen [protocol §6.3 and §10](../../protocol/PROTOCOL-v1.md) explicitly permit **tool-mediated reading for eligibility screening and overlap mapping**, while barring numeric extraction, quotation and decisive scientific claims without a hashed manifestation. However, current [`tools/record_graph.py`](../../../tools/record_graph.py) requires every full-text `include` or `exclude` to cite a performed `assistance` reading. The reading requires a manifestation ID and coordinate ranges within the registered source; `SRC-R006-NEES-2016-MEMORY@1` has `access_status=metadata_only` and `manifestations=[]`. A fabricated reading, SHA-256, or human second pass would be invalid.

This is a **narrow implementation-vs-method gate requiring Integration adjudication**, not a finding that Nees fails E1–E6. The current record is `SCR-R006-NEES-2016-MEMORY-FT@1`, `pending`, based on exact prior `SCR-R006-NEES-2016-MEMORY-TA@1` (`uncertain`) and source revision 1.

Integration has two lawful technical routes, neither authorized or performed by R006:

1. **Source custody route (no validator change):** review R005 #144, obtain and privately register lawful *exact bytes* of the specified edition via R004/Integration, then create truthful source-manifestation/reading evidence and independently audit R006's E1–E6 conclusion; never commit rights-restricted original PDFs. Any numerical extraction separately requires actual authenticated byte/locator evidence.
2. **Protocol-faithful screening route (shared schema/validator decision):** if §10's tool-mediated screen-in exception is retained as intended, add an explicitly attributed, non-manifestation *eligibility-only* verification mechanism. Check exact original-document route, consulted section bounds, reviewer identity and no second assessor. Reject its use for numerical extraction, source quotations, full-item reading or outcome claims. This must be Integration-owned with new validator/negative tests; R006 must not silently relax `FALSE_FULL_TEXT_SCREENING` or invent AIDs.

A human second assessor is **not mandatory** for the v1 screening procedure: §6.2 specifies intra-agent rechecks and disclosure, not fictional independent dual-human screening. No actual human performed a screen here.

## Delta and tests

| Live R006 metric | Accepted main | This proposal if integrated |
|---|---:|---:|
| Title/abstract decisions | 8 | 8 |
| Full-text exclusions | 1 | 1 |
| Full-text `awaiting_text` | 1 | 1 |
| Full-text `pending` | 3 | **4** |
| Required full-text decisions missing | 3 | **2** (Edworthy 2014, Arrabito 2004) |
| Full-text includes | 0 | **0** |
| Admitted publications/studies/experiments/samples | 0 / 0 / 0 / 0 | **0 / 0 / 0 / 0** |
| Selected Track E / G | 0 / 0 | **0 / 0** |

The new regression tests assert frozen identity/DOI, valid predecessor, AI attribution and non-admission, and reject invented final decisions, source revision pins and adverse title/abstract transitions.

R006-owned scoped check: `python -m unittest discover -s tests -p 'test_r006_nees_manuscript_ft_20261110.py' -v`.

**Integration handoff:** source-review the actual manuscript and #144 independently; copy/reconcile only the R006 source-scoped record on its own branch; regenerate Integration-owned `records-index`/`evidence-flow` with `python tools/validate.py --write-exports`; run full unittest, `python tools/validate.py`, `python -m tools.build_record_fixtures --check`, exact-final-head CI and merged-main CI. Source-relative CI failure from a stale generated export is **not** qualification. Owner access action only if original bytes cannot be obtained lawfully in the Integration context.

**R007/R008:** no selected Track G publication and no R006-ready theory/empirical corpus; no evidence synthesis or outcome figures are authorized by this source check.
