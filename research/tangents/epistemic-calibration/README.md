# MHAC-T002: epistemic calibration and consequential action

**Status: exploratory synthetic research package, refs #31.** This is a bounded comparison of alert validity, information checking and costly decisions. It is NOT an accepted empirical finding, a language/voice evaluation, a source screening decision, an R012 state model, an authorized human pilot or an amendment to the frozen R002 protocol.

## Question and boundaries

When can a listener's willingness to act on a familiar or convincing alarm increase expected harm, and when does independent checking reduce harm versus impose a costly delay? The attached fully fictional calculation shows that both situations are mathematically possible. It does not estimate how listeners behave, whether speech is trustworthy, or whether this is a deployed alarm policy.

Separate source truth, detection accuracy, prior prevalence, alert predictive value, stated message certainty, consequence, deadline, recipient interpretation, trust and action. The model is deliberately indifferent to auditory signal form. A richer cybersemiotic account must propose incremental, prospective predictions over a simpler expected-loss account before claiming explanatory leverage.

## Files and authority

- [SOURCE-BASIS.md](SOURCE-BASIS.md): four primary bibliographic identities, observed reading extent, contradictory evidence and unsatisfied eligibility gates.
- [CONSTRUCTS.md](CONSTRUCTS.md): distinct variables, conditioning and confounders.
- [DECISION-MODEL.md](DECISION-MODEL.md): reproducible exact-probability rules and non-equivalent philosophical accounts.
- [SYNTHETIC-REHEARSAL.md](SYNTHETIC-REHEARSAL.md): prescribed fictional grid and negative cases.
- [PROTOCOL-SKETCH.md](PROTOCOL-SKETCH.md): a proposed, **not executed**, prospective human comparison with R020 gate.
- [DECISION-MEMO.md](DECISION-MEMO.md): positive, negative, null and contradictory interpretation and handoffs.
- [rehearsal.py](rehearsal.py): standalone standard-library model.
- [test_epistemic_calibration_t002.py](../../../tests/test_epistemic_calibration_t002.py): ten isolated invariant tests.

## Reproduction

From repository root, Python 3.11+ and no paid APIs:

    python research/tangents/epistemic-calibration/rehearsal.py --json > /tmp/mhac-t002-fictional.json
    python -m unittest tests.test_epistemic_calibration_t002 -v
    python -m unittest discover -s tests -v
    python tools/validate.py
    python -m tools.build_record_fixtures --check

The JSON schema marker is mhac-t002-synthetic-v1. Generated results are ephemeral, deterministic, marked synthetic and **not** written to the registry, evidence extraction or empirical corpus. Codes and source notes were authored and checked by an AI agent on 2026-11-03; this is not independent human verification.

## Acceptance boundary

Tested invariants and full CI can establish implementation consistency, not scientific validity. Formal Track E inclusion requires R005/R006 identity, access, screening and appraisal; cross-domain theory requires the corresponding Track G authority. R014 must review any experiment proposal. R020 requires real participant and ethics authorization; no study was run. Main, frozen protocol, accepted schemas, R005/R006 and other tangent packages remain untouched.
