# R005 → R006: Nees 2016 primary author-manuscript route (10 November 2026)

**Refs #5; handoff to #6 and Integration.** Base main `b22f9bb6c0f7c8873f6b449c775c35af89ba2585`. Frozen protocol v1 §§4–6, 10–12; **publication cutoff remains 2026-10-04**. This is a new lawful *publicly accessible original author-manuscript reading route*, not a new publication or a version-of-record copy, and **not a performed R006 eligibility decision**.

## What actually became accessible

The [corresponding author's publications list](https://michaelanees.com/publications), 2016 journal entry, directly links *PDF* [#35](https://static1.squarespace.com/static/51bb699de4b0820e6e77849b/t/56d63bd2a3360c6369802fc3/1456880594996/Nees+et+al+Human+Factors+2016+author+preprint.pdf). The public PDF renderer opened a **29-page author-hosted manuscript**, and selected page images were visually inspected. Its own title page says *submitted for consideration*; the internal cover note calls this the *authors' accepted preprint version* and directs readers to the journal version. Those statements are recorded together, not silently equated with each other or with the published text.

**Publication identity:** Michael A. Nees, Benji Helbein, Anna Porter, “Speech Auditory Alerts Promote Memory for Alerted Events in a Video-Simulated Self-Driving Car Ride”; DOI [10.1177/0018720816629279](https://doi.org/10.1177/0018720816629279). The independent [SAGE publisher page](https://journals.sagepub.com/doi/10.1177/0018720816629279) reports *Human Factors* **58(3), 416–426**, online first 2016-02-16 (May 2016 issue), and restricted full report. **Do not carry author-manuscript PDF page numbers into the SAGE version of record.**

**Access extent / timestamp:** Public web-rendered author PDF at 2026-11-10 UTC; a clock checkpoint was taken at **18:08:37 UTC after navigation**, *not* original HTTP Date or exact acquisition time. PDF p.1 title page, p.3 abstract, selected original Methods **manuscript pp.10–14**, Table 1 **p.11**, selected Results **pp.14–16** including Table 2, and selected discussion/limits **pp.17–18** were inspected via text renderer. Visual page inspection was performed for original PDF page indices **9, 10, 13, 14** (printed manuscript pp.10, 11, 14, 15). This **does not certify a complete 29-page read**, appendices, precise journal text, publisher PDF bytes or audio playback. Specific locators are in [OBSERVATIONS.json](OBSERVATIONS.json).

**Access and rights:** The author openly links to the file, so public reading through that route succeeded without purchase, login or bypass. No explicit repository licence or redistribution/private-copying grant was found or certified. The tool did not expose raw original response, HTTP headers or binary bytes. **No SHA-256, exact-byte identity, receipt, retained source or lawful archival permission is claimed.** Subsequent authorized acquisition must record its own receipt; it may differ from this renderer instance.

## Source-bounded Methods finding — identity, not admissions

| Question for R006 | Observed author-manuscript evidence | Locator |
|---|---|---|
| Human participant eligibility (E1) | Authors report **90 recruited**, five excluded, **85 analysed** | Method > Participants, manuscript p.10, lines 118–126; visually checked |
| Audio manipulation (E2/E3) | **Three between-subject conditions:** visual text, auditory icons, spoken alerts; same driving scenarios across conditions | pp.9–12; Table 1 p.11 visually checked |
| Tasks and outcomes (E4) | Alert training/recognition followed by three routine-driving videos, visual word-search secondary task, free recall, annoyance/usefulness/confidence and NASA-TLX | Method > Procedure, pp.13–14; Results pp.14–16 |
| Design (E5) | Described as **one experiment**, not three studies; author reports analysed condition sizes **30 visual / 28 icons / 27 speech** | Method p.10; assignment/procedure p.13 |
| Date (E6) | The journal's publication dates precede frozen cutoff | SAGE publisher record |
| Generalization caution | The paper studies memory during routine video-simulated automated driving, **not actual emergency control response** | Discussion/limitations pp.17–18, selected passages |

All numerical figures above are **author reports found in a selected original manuscript**, not MHAC independently measured outcomes, accepted synthesis data, cohort verification or additional `SAMPLE` objects. The author describes a single recruitment/experiment distributed across three between-subject conditions. R006 must still examine possible repeated reporting/overlap and decide whether to include one publication under the frozen criteria after a properly source-registered reading. The fact that the author's manuscript exists **does not automatically satisfy** the remaining canonical full-text provenance requirements.

## Preserve old discovery and canonical screening state

Existing R006 source `SRC-R006-NEES-2016-MEMORY@1` and TA record `SCR-R006-NEES-2016-MEMORY-TA@1` remain unchanged. Existing retrieval pins are `HIT-R005R-C1LOAD-EQ1-04051@1`, `HIT-R005R-C1RECOVERY-EQ1-00329@1`, and `HIT-R005R-C1RECOVERY-EQ6-00308@1`. **No new SRCH/HIT, publication, EXP or SAMPLE record.** One publisher DOI and its author-preprint manifestation are **not** independent publications.

As of the last verified #142 merged-main checkpoint: **8 canonical TA first passes, 1 FT exclusion, 1 awaiting text, 3 provisional FT pending, 3 missing FT decisions (Edworthy 2014, Arrabito 2004, Nees 2016), 0 FT inclusions, 0 admitted publications/studies/experiments/independent samples, 0 selected E/G**. These are dated baseline counts, not a claim about concurrent future main changes.

## R006 / Integration handoff and next external gate

**R004/Integration source custodian:** attempt authorized private retention of this precise 29-page author-manuscript file. Capture real final URL, UTC, raw bytes/hash, source edition, access basis and explicit retention rights; if rights are insufficient, record the precise blocker. This is a different manifestation from the SAGE journal version: do not transfer its page numbers or its checksum to a publisher copy. Use accepted [private attestation tool](../scripts/attest_primary_pdf.py) without putting the PDF on public GitHub. R004/Integration owns source revisions and common exports.

**R006:** decide whether this source suffices for a frozen-v1 full-text assessment once its manifestation/reading evidence is legitimately bound. Resolve one-publication/one-experiment/three-arm identity and any shared participants against existing reports. A pending/uncertain state is preferable to an unsupported include. No human second reader, external review or accepted scientific sample has been created.

**R005:** after this direct source route is supplied, continue unfilled EQ1 via a new immutable response-captured acquisition **when authorized API access actually works**; do not splice November pages into the shifted 3 November prefix. C5 ICAD 2026 is separately owned by active Draft #122; do not duplicate it. C9 chaining is not complete; neither a new database export nor a complete search is claimed here.

The matching [OBSERVATIONS.json](OBSERVATIONS.json) gives the machine-readable version/reading limits. Tests in `tests/test_r005_nees_manuscript_20261110.py` fail closed if the route is misreported as a version of record, licensed/byte-hashed source, R006 include, independent cohort or new search hit. They verify bookkeeping only, **not source authenticity or scientific validity**.

Check: `python -m unittest discover -s tests -p 'test_r005_nees_manuscript_20261110.py' -v`; then full tests, `python tools/validate.py`, `python -m tools.build_record_fixtures --check`. Integration owns exact-head qualification and merges; leave #5/#6 open.
