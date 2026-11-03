# Synthetic rehearsal and negative controls — T002

All cases and numbers are **fictional mathematical examples**. No human response, source prevalence, model calibration or warning effectiveness has been observed. Values are normalized loss units per interval, not probabilities of harm or medical risk.

## Reproduce and check

From repo root:

    python research/tangents/epistemic-calibration/rehearsal.py --json
    python -m unittest tests.test_epistemic_calibration_t002 -v

The deterministic JSON has schema marker mhac-t002-synthetic-v1 and exactly 24 ordered grid cases. The simulation has no random seed because it performs finite exact joint-probability arithmetic, not Monte Carlo sampling. Nine tests cover normalization, basic policy dominance, false-trust counterexample, verification benefit/harm, zero-probability observations, extreme priors, invalid input and deterministic tie handling.

## Three explicitly negative/countervailing cases

| Invented case | Parameters (H prior, hit, false-alarm, C_miss, C_false_action; check) | Expected loss: compliance / Bayes / forced check / selective check | Meaning only within model |
|---|---|---|---|
| Blindly following low-validity alerts | .02, .75, .35, 5, 3; defaults | 1.054 / .100 / .1302 / .0981 | PPV=.041899441 despite detector hit=.75. Acting on every alert is costly; 'higher trust helps' is not a universal law. |
| Accurate free checking | .2, .8, .2, 8, 2; check h=.99/f=.01, fixed/delay=0 | .640 / .640 / .032 / .032 | Verification can improve action selection when it adds highly diagnostic, costless information. |
| Time-critical check burden | .5, .8, .1, 8, 1; check h=.9/f=.1, fixed=.5, delay=2 | .850 / .500 / 1.675 / .500 | Forced checking is worse under fictional delay cost; an adaptive oracle correctly avoids it. |

These are calculated counterexamples, not observations of 'trust', checking behaviour, alarm fatigue or human decisions. In particular, the model cannot identify measured decision latency or deadline exceedance; such outcomes belong to a future authorized study.

## Follow-on stress tests, not executed

Independent verification assumptions must be relaxed for correlated sensors, shared provenance, stale data, degraded checks, non-binary states, unequal timeliness, unknown likelihoods and failure of the detector itself. Hard deadlines require action time and censoring rather than a smooth delay-loss approximation. Spoken/nonspeech/text channels need actual comprehension and accessibility measures; substituting a presentation label into this model would fabricate an effect.
