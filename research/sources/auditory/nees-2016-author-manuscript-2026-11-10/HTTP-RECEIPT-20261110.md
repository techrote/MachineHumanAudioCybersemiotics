# Nees 2016 author-manuscript original-byte access check — 10 November 2026

**Refs #5; R006 #6 and Integration handoff.** Base accepted main `fff3f79b2ce60eb6406c7d22cd1969ede1c39633`. Frozen v1 §§5, 6, 10–12; cutoff `2026-10-04`. This check attempts a new **direct original HTTP PDF response**, not a new paper, new search, screening decision, complete reading or sample.

## Exact target and existing authority

Nees, Helbein & Porter (2016), *Speech Auditory Alerts Promote Memory for Alerted Events in a Video-Simulated Self-Driving Car Ride*, `Human Factors` 58(3):416–426, DOI [10.1177/0018720816629279](https://doi.org/10.1177/0018720816629279). The [corresponding author's publicly accessible publications index](https://michaelanees.com/publications) links this [author-manuscript PDF](https://static1.squarespace.com/static/51bb699de4b0820e6e77849b/t/56d63bd2a3360c6369802fc3/1456880594996/Nees+et+al+Human+Factors+2016+author+preprint.pdf). Its own contradictory *submitted* / *accepted preprint* labels and **lack of demonstrated identity with SAGE VoR** were explicitly documented in [R005 original page observations](OBSERVATIONS.json), including manuscript Methods pp.10–14, Results pp.14–16 and selected Discussion pp.17–18. These are previous tool-mediated reading boundaries, **not** a reading performed by the present probe.

Existing canonical source `SRC-R006-NEES-2016-MEMORY@1`; original hit pins `HIT-R005R-C1LOAD-EQ1-04051@1`, `HIT-R005R-C1RECOVERY-EQ1-00329@1`, `HIT-R005R-C1RECOVERY-EQ6-00308@1`. These are discovery occurrences, not three publications or three samples.

## New executable receipt attempt

Issue-scoped `tests/test_r005_nees_http_probe_20261110.py` runs one public unauthenticated HTTP GET only when GitHub Actions executes the exact scoped PR-head branch. A deterministic local unit test never accesses the network. The runner prints `MHAC_R005_NEES2016=` followed by its **actual** received UTC, HTTP status and Date, Content-Type, final URL, bytes count and SHA-256, or the exact HTTP/transport/structural blocker. It checks PDF signature and EOF; **no claim that those checks authenticate document title, text, page count or publication equivalence**.

The test does not keep/commit the PDF, screenshots or participant data and never claims permission to redistribute. Public linked access permits navigation; independent legal retention/redistribution review is still required. Source bytes, if obtained, are ephemeral; SHA is a receipt for that specific acquired instance only. GitHub Actions job logs should be retained/referenced separately. This is an **acquisition checkpoint**, not a private custody completion or human-source review.

## Scientific and legal boundary

- R005: original source retrieval and identity **support only**; no new SRCH/HIT or study counting.
- R004/Integration: evaluate any actual original HTTP receipt; establish rights-appropriate durable private custody; check exact edition/DOI against PDF content before source manifestation registration. Existing `research/sources/auditory/scripts/attest_primary_pdf.py` handles a legitimately retained local PDF and refuses fake receipt data.
- R006: alone adjudicates full-text frozen E1–E6 and publication/experiment/sample identity. The 2016 author-manuscript describes one experiment with three between-subject arms; do not assume three independent samples. Source/reading and possible overlap remain unresolved without verified performed reading.
- Mainline source and R006 ledgers, common manifests and generated exports are not edited. No human or external assessor is represented.
- Search work: historical OpenAlex EQ1 prefix **4,200 / 9,368 reported on 3 Nov**, not complete and not resumable by blindly appending November pages because rank/count drift was shown by accepted #140. C5 ICAD has an existing owner Draft #122. The next independent R005 search task is a fresh response-captured EQ1 invocation when legally and technically available, otherwise C9 citation-chain retrieval.

## Tests, completion signal and limits

```sh
python3 -m unittest discover -s tests -p 'test_r005_nees_http_probe_20261110.py' -v
python3 -m unittest discover -s tests
python3 tools/validate.py
python3 -m tools.build_record_fixtures --check
```

Source receive/denial is to be verified from an actual exact-head GitHub Actions run and cannot be inferred from green tests. A successful source HTTP result still does not create a retained authenticated manifestation, full-text inclusion, admitted publication, experiment or sample. **R005 #5 and R006 #6 remain open; R007/R008 selected corpus remains unready.**
