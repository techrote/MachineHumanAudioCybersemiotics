# MHAC-T016 — Observation, causal warrant and intervention authority

**Status:** exploratory source-critical, synthetic-only falsification. **Issue:** [#60](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/60). Accepted base: `423649d18c54cbf90bf7bf79d49ba69b29f03848` (2026-11-05 UTC inspection).

## Stage 0 — NARROW GO, not a production requirement

The [proposed foundations](../../../docs/PROJECT_FOUNDATIONS.md) contain a hypothetical printer with a *suspected* filament obstruction, and R012 #12 explicitly differentiates observation and diagnosis. This supports a **fictional diagnosis-claim test**, not accepted design authority. Inspection of active #31/PR40 (uncertainty/validity), #34/PR37 (field grammar), #36/PR53 (status/event), #43/PR44 (actor), #49/PR50 (mode permission), #54/PR55 (presupposition), #56/PR57 (retraction), and #58/PR59 (alarm-source lineage) found **no same-case oracle requiring independent warrant for a named fault cause and separately for a remedy**. All cover adjacent mechanisms; none of those PRs has landed in main. Do not reimplement their machinery here. If those PRs or later R012 work cover this exact distinction, this tangent should be retired as duplicated.

**Unique counterexample:** low extrusion is accurately observed while both feed-path blockage and nozzle obstruction remain plausible. An unsupported diagnosis can be *factually lucky* but still unwarranted by evidence. Conversely, a fictional independently discriminating test may justify naming the cause while leaving a proposed intervention ineffective, unauthorized or too late. This is a closed-world epistemic contract for falsification, not real machine diagnosis.

## Artifact inventory and commands

- [SOURCES.md](SOURCES.md): seven source identities, accessible passage levels, limitations and contrary findings.
- [WARRANT-LADDER.md](WARRANT-LADDER.md): independent observation → explanation → intervention → authority distinctions.
- [FICTIONAL-CASES.json](FICTIONAL-CASES.json): 32 separately labelled cases, with hidden ground truth, including eight families and negative controls.
- [oracle.py](oracle.py): four predeclared comparators and disaggregated accounting (standard library).
- [MANIFEST.json](MANIFEST.json): immutable Git-blob identity for the labelled cases.
- [COMPARISON.md](COMPARISON.md), [PROTOCOL-SKETCH.md](PROTOCOL-SKETCH.md), [DECISION.md](DECISION.md): measures, future gates and bounded decision consequences.
- [repository-discovered tests](../../../tests/test_t016_causal_warrant.py): label integrity, falsifiers, null controls, no oracle leakage and tampering checks.

Run `python research/tangents/causal-claim-warrant/oracle.py`, `python -m unittest discover -s tests -v`, `python tools/validate.py`, and `python -m tools.build_record_fixtures --check`.

**Evidence classification:** all cases and policy outcomes are invented logical examples. Source claims are attributed and limited to the tasks the publications actually studied. No synthetic count estimates listener comprehension, time, safety, effectiveness, real device error, or a cybersemiotic advantage. The empirical Track E cutoff of 2026-10-04 remains frozen; #5/#6 exclusively own formal selection and sample identity. No source, claim or schema has been added to the accepted registry.

**AI disclosure:** GPT-6 authored this source analysis and synthetic method using public publisher/institutional pages and connected GitHub on 2026-11-05 UTC. No independent human appraisal, preregistration, participant work, machine validation or publication is claimed.
