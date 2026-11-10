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


## Actual original HTTP result — 21:11 UTC, 10 November 2026

**Direct source acquisition succeeded**, recorded independently of the public web reader's prior rendering. Exact PR-head [GitHub Actions #42902552982 / job #130132051244](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42902552982/job/130132051244) emitted the full `MHAC_R005_NEES2016=` receipt, now preserved verbatim in [HTTP-RECEIPT.json](HTTP-RECEIPT.json).

| Observed field | Actual PR-head runner result |
|---|---|
| UTC HTTP response opened | `2026-11-10T21:11:25.026+00:00` |
| UTC read completed | `2026-11-10T21:11:25.033+00:00` |
| HTTP Date | `Tue, 10 Nov 2026 21:11:25 GMT` |
| Status / MIME | **200** / `application/pdf` |
| Received original PDF bytes | **851,943** |
| PDF header | `%PDF-1.3` |
| SHA-256 over received original bytes | `012398a1a81c923c413454d7993e474e7389149b8e4199e2f8241cb35cbc3cfe` |
| Requested and final URL | Exact author-hosted Squarespace PDF link above; no changed final URL |
| Structural checks | `%PDF-` prefix and `%%EOF` in trailing 4 KiB |

This is an **actual acquisition SHA-256 for one ephemeral HTTP instance**, not an invented original file, archival copy, SAGE VoR checksum, full 29-page semantic read, audio access or copyright/retention approval. No PDF source bytes were persisted. The owner-facing next action has narrowed: R004/Integration must obtain this exact **edition** lawfully into retention-appropriate private custody, independently compare with the original rendered manuscript (including title page), retain its *own* actual download hash/UTC, verify rights and register a manifestation; subsequent downloads may legitimately differ from the present digest. R006 then performs source-bound full-text reading and E1–E6/participant-overlap adjudication. There is still **no human second reviewer** and **no new admitted study/experiment/sample**.

The first exact-head job reported **983 unit tests, four skips, PASS**, plus history-aware repository validator and deterministic fixtures passing. These are software checks only; the final PR head with committed receipt and anti-promotion tests requires a fresh independent check.
