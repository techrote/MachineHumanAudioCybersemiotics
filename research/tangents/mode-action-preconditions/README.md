# MHAC-T011 — Mode-dependent action preconditions (exploratory)

**Issue:** [#49](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/49) · **Base:** `main` at `423649d18c54cbf90bf7bf79d49ba69b29f03848` · **Prepared:** 2026-11-04 UTC · **Status:** synthetic-only research, not accepted design or human evidence.

## Gate 0: applicability and non-duplication

A fictional desktop fabrication-workstation agent might ask an operator to `resume_job`: a coherent instruction in `paused`, but an incompatible instruction in `running`. `reset_preview` is valid in this **fictional** system only in `maintenance`; `ack_status` is mode-independent. These are *declared semantics*, not real device instructions, verified operating requirements or certified permissions. MHAC explicitly considers machine state and requested action, so the counterexample is relevant. **Gate result: proceed only with symbolic falsification.**

Accepted `main` has no completed R012 state model (R012 depends on still-open R011). [#34 / PR #37](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/37) concerns source/event composition; [#43 / PR #44](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/44) concerns authorized actors; [#47 / PR #48](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/48) concerns delivery freshness/deadlines; #36 concerns persistent status. This package **does not reproduce their grammar, identity infrastructure, scheduler or any canonical R012 state contract**. R005/R006 screening and study/sample identity remain incomplete, so scouting records cannot be counted as admitted Track E findings.

## Artifacts and reproduction

- `SOURCES.md`: six discovery-source identities, reading extent, counterpositions and dependence warnings.
- `MODE-CONTRACT.md`: independent fictional truth inputs, policies, assumptions and oracle limitations.
- `FICTIONAL-TRACES.tsv`: 30 authored, fictional source/event/actor/mode scenarios; no participants.
- `oracle.py`: deterministic stdlib action-validity falsifier with A/B/C/D and E no-action control.
- `MANIFEST.json`: SHA-256 of the precise TSV bytes and canonical result.
- `COMPARISON.md`, `DECISION.md`: disaggregated synthetic results and revision criteria.
- `PROTOCOL-SKETCH.md`: proposal only; R014/R020 gates intact.
- `tests/test_mode_action_t011.py`: 11 regression methods discoverable by repository CI.

From the repository root (Python 3.11+):

```sh
python research/tangents/mode-action-preconditions/oracle.py --check
python research/tangents/mode-action-preconditions/oracle.py
python -m unittest discover -s tests -p 'test_mode_action_t011.py' -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

The last three need the full repository; GitHub Actions is their authority for the published head. `--check` detects unchecked fixture/report changes, not scientific errors.

**No production code or actual audio, simulated listeners, participant evidence, real hazard, efficacy statistic, frozen-protocol amendment, external submission, source-evidence admission or adopted design is supplied.** AI-assisted (GPT-6, connected GitHub, public bibliographic/abstract sources and isolated Python unit tests, 2026-11-04); no independent human review. Restricted full texts were not reproduced.
