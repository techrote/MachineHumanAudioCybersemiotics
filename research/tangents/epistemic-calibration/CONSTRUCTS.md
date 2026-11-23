# Construct separation and identifiability — T002

All examples in this package are **fictional policy variables** rather than observed population estimates. The words 'certainty', 'reliability', 'urgency', 'confidence' and 'trust' are not interchangeable.

| Quantity | Operational meaning | What cannot be inferred from it |
|---|---|---|
| H (world hazard) | Binary state actually present/absent within a toy event interval | Its prior from the voice or from perceived urgency |
| prevalence p | P(H), prespecified base rate for a time/task population | Universal incident frequency |
| detector hit h | P(alert given H), sensitivity/true-positive rate | P(H given alert), or message provenance |
| false-alarm rate f | P(alert given not H), false-positive rate | A listener's false-action rate |
| PPV | P(H given alert) = ph / [ph + (1-p)f] | Intrinsic message quality independent of prevalence |
| negative-alert posterior | P(H given silence) | Proof of all-clear, knowledge of detector status, or authorization to act |
| upstream alert trigger | Observed emitted alarm vs no alarm under h,f | Source event truth or verified communication receipt |
| message stated probability | Explicit proposition, interval, or words like 'possibly' | Automatically calibrated to PPV without audited reference class |
| source provenance/freshness | Identified, authenticated, current source/event version | Entailed by perceived familiarity or vocal naturalness |
| deadline | Remaining interval before useful action | Acoustic urgency impression |
| miss cost | Expected loss when hazard exists but action omitted | Subjective listener fear |
| false-action cost | Expected loss when action taken without hazard | Loss of all types of action (model deliberately simplified) |
| verification accuracy | Additional check's sensitivity and false-alarm rate | Independent information unless conditional independence holds |
| check/latency cost | Fixed checking burden + hazard-weighted cost of delayed action | Empirically measured workload or time-to-action |
| decision criterion | Rule mapping posterior and costs to an action | Discriminability, d-prime, or comprehension |
| trust / credibility | Subjective assessment of system/source | Actual behavioural compliance or correctness |
| estimated probability | Participant's reported P(H given evidence) | Guaranteed calibration; scoring requires truthful labels and prespecified bins/scoring rule |
| correct action | Action appropriate to true state and task cost | Merely noticing, recognizing a melody or expressing trust |

The toy threshold for acting, with only two actions and zero base action cost, is p(H given observation) > C_false_action / (C_false_action + C_miss). At equality the oracle chooses ignore. This is a decision rule, not a prescriptive alarm-standard recommendation. Differential action severity, reversible actions, partial observability, correlated samples, dynamically changing p and source freshness are not represented.

## Non-identifiability and confounding

A change in response rate can arise from prior/prevalence learning, detector trust, alarm salience, sensory detection, perceived urgency, spoken-number comprehension, pragmatic interpretation, verification access, workload or consequence asymmetry. A single overall 'trust score' or reaction-time mean cannot identify these mechanisms. Detection sensitivity (d-prime), response criterion, confidence, calibration and trust require distinct observations and instruments. Gaussian equal-variance SDT is not assumed by the discrete Bernoulli oracle.

For an actual listener experiment, hearing variation, assistive processing, language proficiency, numeric literacy, prior experience, device loudness, fatigue, sequence effects, false-alarm history and concurrent task demands are potential effect modifiers, not grounds for exclusion without justification. Audio-only and visual-only comparators must preserve accessibility alternatives.

## Required data separation

A real-data record would need item-by-item source state, alert state, correct action, correct-source identity, emission and presentation times, available check evidence, recipient detection and confidence, actual response, elapsed time/censoring, and separately administered ratings. No such records have been collected under this tangent.
