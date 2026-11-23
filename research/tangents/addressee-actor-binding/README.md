# MHAC-T008 — Addressee / authorized-actor binding (synthetic prepass)

**Status:** exploratory, fictional contract and falsification exercise; not admitted into the accepted programme, source set or live registry. **Owner:** [issue #43](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/43). **Base:** accepted `main` `423649d18c54cbf90bf7bf79d49ba69b29f03848`.

## Question and independent falsifier

Can a correct source/event/action message be understood or accepted by the **wrong authorized actor**? The instrument deliberately keeps source identity, addressee, audience, authorization and response disjoint. It does not use or simulate actual voices, listeners, authentication, machinery or safety operations.

The 30 declared fictional scenarios include broadcast, ambiguous and group audience; two listeners; acoustic address-label metadata (not simulated audio); role handover and stale versions; missing/repaired acknowledgement; expired authority; absent audio and accessible fallback; wrong-first/correct-final actions and deadline overruns. The 31 attempted symbolic actions, including invalid attempts, are fictional **test input**. Truth labels were declared per case before comparing policies, then checked by an independent logical contract. This is not an empirical sample.

## Reproduce (Python 3.11+, standard library)

From repository root:

```sh
python research/tangents/addressee-actor-binding/actor_oracle.py --check
python research/tangents/addressee-actor-binding/actor_oracle.py --write
python research/tangents/addressee-actor-binding/actor_oracle.py --check
python -m unittest tests.test_mhac_t008 -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

`--check` independently regenerates all fixture and rule-result bytes, checks the committed `MANIFEST.json`, and checks the optional generated files if present. `--write` creates deterministic `FICTIONAL-TRACES.json` and `RESULTS.json` locally; these intentionally are **derived**, not accepted evidence records. A committed SHA-256 manifest fixes their expected identities and count. No random generator or external dependencies are used.

## Contents

- [ACTOR-CONTRACT.md](ACTOR-CONTRACT.md) — semantics, error truth and closed fields.
- [COMPARATORS.md](COMPARATORS.md) — five candidate policies, failure matrix, negative/null results.
- [SOURCES.md](SOURCES.md) — six primary/official source records and transfer caveats.
- [PROTOCOL-OUTLINE.md](PROTOCOL-OUTLINE.md) — unexecuted future human comparison, R020 gate.
- [DECISION-MEMO.md](DECISION-MEMO.md) — decisions, limitations, follow-up boundaries.
- [actor_oracle.py](actor_oracle.py), [MANIFEST.json](MANIFEST.json), [unit tests](../../../tests/test_mhac_t008.py) — reproducibility.

## Non-duplication and programme handoff

The independent outcome here is **wrong-actor attempted action despite source/event correctness**, not #30's broader failure taxonomy (PR #32), #33's repair lifecycle (PR #35), #34's source×event syntax (PR #37), #36's persistent-state policy, #38's polarity parsing (PR #39), #41's acoustic feature survival (PR #42), or #31's Bayesian alert decision (PR #40). No overlapping branch or shared artefact is changed.

R008/R011 may compare pragmatic audience designs and a simpler external-authorization account; R012/R013 could later consider actor/audience roles as candidate fields; R014 may use the separated outcome plan; R017 should test the inferential boundary. None is adopted by this PR. R005/R006 retains sole control of formal corpus identity/eligibility; Track E's human-to-human exclusion matters. R020 governs any actual participant experiment.

**AI disclosure:** generated and mechanically self-tested with GPT-6/connected GitHub and local Python on 2026-11-03 UTC; no independent human appraisal, human screening, human testing or peer review. Structural reproducibility cannot establish behavioural effectiveness.
