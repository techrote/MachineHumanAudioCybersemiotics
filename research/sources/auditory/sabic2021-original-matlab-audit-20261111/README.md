# R005 → R006: Šabić 2021 original stimulus-normalization code audit

**Refs #5; R006 #6 and Integration handoff.** Model-assisted source-code and publisher-original selected-section reading on 11 November 2026; frozen v1 and 2026-10-04 cutoff unchanged. This is a primary-method **fidelity challenge**, not an empirical replication, recording of source custody, article eligibility decision, or new study/sample.

## Pinned original sources and access

- Publication: Šabić, Chen and MacDonald, *Toward a Better Understanding of In-Vehicle Auditory Warnings and Background Noise*, *Human Factors* 63(2), 312–335 (2021), DOI **10.1177/0018720819879311**, first online 2019-10-08. Original [SAGE HTML](https://journals.sagepub.com/doi/10.1177/0018720819879311), consulted sections **The Current Study; Experiment 1 > Method > Stimuli; Experiment 2 > Method > Apparatus, stimuli, experiment design and procedure**. The publisher's Experiment 1 Stimuli text links to the author's GitHub account and states a MATLAB RMS-normalization script was used (tool-rendered HTML lines 103–126).
- Original author-hosted [Human-Factors-2019 README](https://github.com/Edin-Sabic/Human-Factors-2019/blob/e5f8bf29ad225fa15d8969db40ce2b03b4295821/README.md) explicitly identifies its MATLAB script with this paper. [Exact script at commit e5f8bf29](https://github.com/Edin-Sabic/Human-Factors-2019/blob/e5f8bf29ad225fa15d8969db40ce2b03b4295821/RMS%20Standardization), Git blob SHA-1 **3ff7a5d2da362cc2d3d332432c9d41b3606b628e**. Entire short code file inspected through read-only public GitHub file API. The external repository was NOT modified.
- Access recorded as AI-assisted, unauthenticated public web/GitHub source reading on **2026-11-11**. UTC inspection-clock checkpoint **12:17:30Z** is **not** an origin HTTP Date or precise GitHub response-received time. No original HTML response bytes, GitHub HTTP response-body SHA-256, original WAV files, playback, reproduction of authors' measurements, or publisher edition equivalence attested. The third-party repo declares no licence in GitHub metadata; no source code is republished here.

## Exact source-code inconsistency

The first loop (source lines **8–26**) iterates 29 times but line **13** fixes the read expression to file **1.wav** every time. The loop stores the peak of this same RMS-normalized file in all 29 slots (line 23), and uses their maximum as a supposed global peak scale (line 29). In contrast, the second loop at line **35** reads each indexed filename, then normalizes and divides by the fixed first-file-derived scale (lines 38–45).

**Consequence, conditional:** the script as published cannot guarantee its stated all-file peak bound. A second file with a higher RMS-normalized peak than file 1 can produce computed samples exceeding absolute unity before the writer. Whether any **actual** authors' recordings had this relationship, whether this exact version was executed in the experiment, how MATLAB handled out-of-range samples, and whether participant outcomes were affected are **unknown**. The main point is reproducibility of the intended processing, not an assertion that the paper's results are wrong.

**Synthetic counterexample only:** samples for file 1 `[1, -1]` give RMS=1, normalized peak=1; file 2 `[1, 0, 0, 0]` gives RMS=0.5, normalized peak=2. The first loop's scale remains 1 and the second loop's file-2 computed peak becomes 2. These artificial arrays are mathematics, not measured study stimuli. The issue-scoped test demonstrates this while explicitly forbidding source/admission promotion.

## R006 / Integration precise decision boundary

- Existing publication/source `SRC-R006-H-SABIC-UNDERSTANDING@1`; previously registered hit `HIT-R005R-C1RECOVERY-EQ1-00046@1`. The 2021 paper describes **two experiments**, but its author-linked code is not another paper, experiment, new dataset, or proof of independent samples. The paper itself reports a new participant set for Experiment 2; cross-report thesis and earlier conference-participant overlap remains undecided. R006 retains sole E1–E6 and sample/experiment adjudication.
- The publisher article selected Methods text is accessible, but original publisher HTML response bytes, source-rights approval, retained manifestation and matched R006 reading are absent. The newly discovered code does **not** clear R006's canonical `pending` FT disposition. It helps R006/Integration define a concrete stimulus-provenance check before later numeric extraction or claims about equal RMS/peak matching.
- **Stevens external HOLD remains:** no owner-approved non-public retention directory plus real approving actor, UTC time, and applicable CC BY 2.5 attribution/retention basis. Merged R005 private-XML capture tool can act only after this legitimate authorization; the historical 74,338-byte Europe PMC JATS response is ephemeral and not a retained original. No attempt was made to generate an approval file.
- Current canonical nine-record snapshot: **TA 9; FT 5 pending / 3 awaiting_text / 1 excluded / 0 included; admitted publication/study/experiment/sample 0/0/0/0**. No changes to R006 source/decision shards, indexes, generated exports, or frozen protocol.

## Reproduction and scientific guard

`OBSERVATIONS.json` binds the original publisher DOI and Methods section, the author's own repository README, the exact commit/blob and inspected line numbers. To inspect later, fetch the **commit-pinned** script and compare lines 10–13 with lines 32–35; do not rely on `master` remaining unchanged. The included test performs synthetic math only and checks that the record remains non-empirical/non-admitting.

```sh
python -m unittest discover -s tests -p 'test_r005_sabic_author_normalization_20261111.py' -v
python -m unittest discover -s tests
python tools/validate.py
python -m tools.build_record_fixtures --check
```

**Integration handoff:** independently source-review the pinned code, the SAGE link in the Method/Stimuli text and the synthetic counterexample, run exact-final-head CI. Use `Refs #5`; keep R006 scientific HOLD and issue #5/#6 open. Do not assign human review or licence approval to this model-assisted audit.
