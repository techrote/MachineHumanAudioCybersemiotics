# MHAC-T012 — codebook migration and longitudinal binding falsifier

**EXPLORATORY · SYMBOLIC ONLY · NOT ACCEPTED TRACK E/G · NO PARTICIPANTS · NOT SAFETY CERTIFIED.**

Issue [#51](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/51). Base accepted `main`: `423649d18c54cbf90bf7bf79d49ba69b29f03848`. The [limited-go applicability and duplicate gate](GATE.md) precedes this isolated synthetic specification. See [source-appraisal limitations](SOURCES.md). No production learned-audio dictionary, verified source authority, accepted R012 state model or R013 audio hypotheses exist yet.

Research hypothesis: **codebook versioning of cue→referent and referent→priority/action can matter even when the audio token is unchanged**. Acoustic retuning without a semantic change is a separate case whose *actual human recognition transfer is unknown*. Compare deliberate baseline policies and preserve non-audio/no-version counterexamples.

Only fictional, manually scripted event/source/action truth is used. The symbolic oracle must never generate ground truth from the tested decoding policy. Event time/version, message replay/rollback, cue asset identity, codebook version, receiver legend version, exact referent, priority, action, expiry, revoked/resolved status, external authority and unknown are distinct.

**Reproduction (Python ≥3.11, stdlib):**
```sh
python -m unittest discover -s tests -p 'test_t012_codebook.py' -v
python research/tangents/codebook-migration/oracle.py --check
python tools/validate.py
python -m tools.build_record_fixtures --check
```

All numeric times, deadline thresholds, event configurations, symbolic acoustic hashes and comparator strategies are fictional. No waveforms or actual user response, training/learning outcome, distress/annoyance, correct perceived first action or intervention safety are generated. CI only qualifies structural integrity.

**Ownership:** only this directory and the T012-specific test file. [Proposed downstream study and decision memo](DECISION.md) are future human-gated hypotheses, not changes to programme issue contracts.