# MHAC-T017 — threshold conformity decision-warrant falsifier

**Issue:** [#62](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/62) · **Base:** `423649d18c54cbf90bf7bf79d49ba69b29f03848` · **Status:** exploratory, fictional-only, independent review pending.

## Scope and Stage 0 decision

[Stage 0](STAGE0.md) returned **limited GO**: the proposed [project foundations](../../../docs/PROJECT_FOUNDATIONS.md) distinguish observation, estimate, hazard and speech purpose and allow an investigable future quantitative classification; **none is accepted as an existing production requirement**. The current [programme](../../../docs/PROGRAMME.md) leaves R012–R014 downstream of incomplete synthesis. We therefore test only whether a hypothetical spoken classification can be **unsupported even when the numeric value is correct**. We do not implement a device, calibrate instruments, authorize an action or amend the frozen protocol.

The novel boundary is **specification limit != operative acceptance rule != an authenticated upstream decision != spoken assertion**. Existing #31/#34/#36/#38/#41/#45/#47/#58/#60 and their PRs own nearby alert, event, language, acoustic and causal boundaries. [Model](CLAIM-MODEL.md) and [source audit](SOURCES.md) make this boundary falsifiable.

## Reproducible package

* `FICTIONAL-CASES.json`: 32 authored, explicitly **fictional** measurements with separate actual-world and authorized-claim labels, including 9 contrast families, adverse cases and a value-only null alternative.
* `oracle.py`: four predeclared symbolic speech-claim policies, deterministic scoring, no access to gold labels in rendering.
* `EXPECTED-COUNTS.json`: selected predeclared logical checks, not empirical rates.
* `MANIFEST.json`: immutable Git-object identity of original ledger and exact base.
* `COMPARISON.md`, `DECISION.md`, `PROTOCOL-SKETCH.md`: rival policies, interpretation, prospective-only human test, stop conditions.
* `tests/test_t017_threshold_decisions.py`: discovery tests for gold-label separation, selected mutations and case-by-case expectations.

From a checkout, run:

```sh
python -m unittest discover -s tests -p 'test_t017_threshold_decisions.py' -v
python research/tangents/threshold-decision-warrant/oracle.py
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

A passing synthetic oracle validates only the consistency of this fictional logical example. It does **not** validate wording, comprehension, accepted Track E/G evidence, metrological policy, human safety, thresholds, acoustic delivery, uncertainty distributions, real participant outcomes or action efficacy. The local repository clone was not accessible in this execution environment (GitHub DNS); GitHub-hosted CI, if run, is the authority for full-suite validation. Do not interpret absent checks as passing.

## Evidence and ownership

AI-assisted GPT-6 source inspection and scenario construction, 2026-11-05 UTC; no independent human screening or scientific review. Sources and access limits are recorded in [SOURCES](SOURCES.md). The six publications and guide are **leads/analogs**, not admitted live bibliography or selected evidence. No rights-restricted text is reproduced. The source ledger and test fixtures are outside canonical `research/registry`, programme JSON and frozen protocol. R005/R006 own any future formal empirical eligibility/screening. PR is reviewable research work only; issue remains open until real acceptance criteria and independent review.
