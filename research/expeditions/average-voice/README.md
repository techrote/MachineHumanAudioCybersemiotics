# The Average Voice That Nobody Has
## Calibration debt, the sound of disagreement, and the limits of consensus

**Refs #220 · 23 November 2026 · mathematical reconstruction, synthetic computation, design conjecture and fiction.** Not a Track E/G inclusion, original-theorem priority claim, participant study or production contract.

### The anomaly and its ancestry

A committee of machines each reports a probability of the same binary event on the same reference population. Every machine is exactly calibrated: among cases where it says 0.6, the event occurs 60% of the time. It is tempting to average the voices and assume that the new voice inherits this property. It generally does not. More perversely, the average may improve squared-error accuracy even while destroying calibration. One number can become better in one sense and worse in another.

This is established forecast-combination theory, not a new discovery. Ranjan and Gneiting, *Combining probability forecasts*, JRSS B 72(1), 71–91 (2010), DOI [10.1111/j.1467-9868.2009.00726.x](https://doi.org/10.1111/j.1467-9868.2009.00726.x), publisher abstract at [Wiley](https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-9868.2009.00726.x), explicitly identifies noncalibration and reduced sharpness of nontrivial fixed linear combinations of calibrated binary forecasts. The University of Washington [2008 technical report listing](https://stat.uw.edu/research/tech-reports/combining-probability-forecasts) corroborates the abstract. Metadata and visible abstracts inspected on 2026-11-23 via public search retrieval; direct full publisher and university page fetches failed. Full text, theorem details, empirical cases and beta-pool performance are not claimed read or reproduced. The algebra below is independently worked out from the definitions; its quantitative bound may have existing antecedents and no priority claim is made.

Reconciled main 495a98ca12bae467a507031f04931aa4254b1866, root instructions/RAG/programme/runbook/integrity/validation, recent issue/PR lists and branch listing. T002 [#31](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/31) separates alarm predictive validity, recipient trust and action thresholds; its actual decision model at open [#40](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/40), head 9f7505fc03368cc915e6fc506ad63e452db2a95f, uses a detector posterior and expected-loss comparator, not a consensus theorem. [#193](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/193) concerns false corroboration, [#209](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/209) context-late compression (actual report inspected), [#218](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/218) joint disclosure (issue/PR titles inspected). This expedition concerns calibration of the reported probability itself, not alarm design, provenance independence, code synthesis or secrecy. No other worker's files changed.

### Exact results: three separate debts

Let Y be binary, X_i be probabilistic forecasts in [0,1], all defined on the same probability space, and w_i strictly positive **fixed** weights summing to one. Assume E[Y|X_i]=X_i for every i. Define P=sum w_i X_i, Q=E[Y|P], J=E[Y|X_1,...,X_m], mu=E[Y], and

- D = E[sum w_i (X_i-P)^2], within-case forecast disagreement.
- C = E[(Q-P)^2], squared calibration defect of the pool.
- B(F) = E[(Y-F)^2], binary Brier loss (one-event convention).

**Identity 1 — noncalibration and a lower bound.** Calibration of each input implies E[X_i]=mu and E[Y X_i]=E[X_i^2]. Since E[P]=mu,

E[P(Y-P)] = sum w_i E[X_i^2] - E[P^2] = D.

Conditioning on P replaces Y with Q. Also E[Q-P]=0, hence Cov(P,Q-P)=D. Cauchy–Schwarz therefore gives

**C Var(P) >= D^2.**

If Var(P)>0, C >= D^2/Var(P). If Var(P)=0, the covariance identity forces D=0; every positively weighted input equals P almost surely and C=0. More generally C=0 iff D=0 under the stated assumptions. Equality in the bound occurs iff Q-P is a scalar multiple of P-mu almost surely (for nonzero variance), so the bound can be exact but is not a general calibration estimator. The slope of the population linear regression of Y on nonconstant P is 1+D/Var(P), not necessarily a pointwise correction curve. A slope above one does not mean every forecast lies too close to 0.5. Recalibration Q depends on the joint distribution; do not treat this lower bound as a trained calibrator.

**Identity 2 — score improvement despite calibration loss.** The pointwise variance decomposition

sum w_i (Y-X_i)^2 = (Y-P)^2 + sum w_i (X_i-P)^2

gives B(P)=sum w_i B(X_i)-D. This identity requires no calibration and holds pointwise for convex weights, even variable ones. A fixed pool beats the weighted mean input Brier loss whenever D>0, but not necessarily the best input. Separately, conditional expectation gives B(P)-B(Q)=C. These are different comparisons: improvement against the average member and loss against a recalibrated version of the pool are not contradictory.

**Identity 3 — lost information.** Because P is a function of the full vector, E[J|P]=Q and B(Q)-B(J)=E[(J-Q)^2]. Even a perfectly recalibrated single number may throw away predictive information available in the ensemble. Neither disagreement nor this information loss establishes source independence; no such premise was required anywhere.

These identities refer to population expectations, not estimated binwise errors from finite samples with continuous scores. A finite empirical analogue must address calibration uncertainty, sample splitting and shift.

### Three witnesses, one negative control

All rows below are equally weighted fictional worlds. Values are exact.

| Case | Y | X | Z | P | Q |
|---|---|---|---|---|---|
| Three-row improvement | 1,0,0 | 1/2,1/2,0 | 1/2,0,1/2 | 1/2,1/4,1/4 | 1,0,0 |
| Six-row alias | 1,1,0,0,0,0 | 1/4,1/2,1/4,1/4,1/4,1/2 | 1/4,1,1/4,1/4,1/4,0 | 1/4,3/4,1/4,1/4,1/4,1/4 | 1/5,1,1/5,1/5,1/5,1/5 |

First case: both inputs have Brier loss 1/6, the pool 1/8. D=1/24, Var(P)=1/72 and C=1/8, saturating the lower bound. The pool beats **both** inputs but is not calibrated. Its recalibrated value perfectly predicts this particular fictional population. This is not a test-set result. A strict-bound case with Y=(1,0,0), X=(1/2,1/2,0), Z=(1,0,0) has C=1/24 and D=1/24; the latter alone does not specify C.

Second case: the full-vector J=(1/4,1,1/4,1/4,1/4,0). A pooled quarter can conceal either a calibrated joint quarter or joint zero; B(Q)-B(J)=1/120. Correcting the average does not restore the missing distinction. The witness does not assert that variance or disagreement alone is universally sufficient for recovering J.

Negative controls: identical calibrated inputs preserve calibration. With an imperfect pair consisting of constants 0 and 1 on a balanced population, the mean 1/2 is calibrated despite maximal disagreement. With calibrated but distinct inputs, an independent fair selector choosing one input in each case gives a calibrated mixture (condition on selector, then on selected value), even though the weights are variable and can be zero. The fixed positive weight theorem cannot be applied to arbitrary adaptive weighting; the selector example does not establish calibration for arbitrary adaptive interior weights. Also, fixed weights do not require statistical independence.

### Exhaustive laboratory

The standard-library oracle represents probabilities as exact integers on a grid of size 2*lcm(1,...,n). Enumerate every set partition of n labelled rows using restricted growth strings. For each prevalence k/n, fix one binary outcome vector with k leading ones. Each partition gives a forecast equal to the event frequency in each cell, guaranteeing calibration; every calibrated forecast on these rows is represented by at least its value partition. Use unordered partition pairs with replacement, including identical partitions. Distinct partitions can produce identical forecasts; multiplicities retained. We do not weight by the number of outcome permutations or deduplicate forecast vectors, and the cases are not independent datasets or a probability distribution over forecasting methods.

An independently written JavaScript enumeration executed in this research session, with exact integer operations on the n<=6 grid (no numerical tolerance), checked the Brier identity, the squared-defect bound and the zero-defect equivalence. The Python implementation additionally asserts the conditional projection identities. Observed JavaScript counts:

| Rows | Partition pairs across prevalence levels | Distinct forecasts | Pool beats both | Strict lower bound | Joint-vector gain |
|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 0 | 0 | 0 | 0 |
| 2 | 9 | 1 | 0 | 0 | 0 |
| 3 | 60 | 18 | 2 | 8 | 0 |
| 4 | 600 | 280 | 62 | 202 | 0 |
| 5 | 8,268 | 4,876 | 1,340 | 4,568 | 0 |
| 6 | 144,942 | 96,712 | 31,066 | 89,409 | 292 |

Within this census joint-vector gain first occurs at n=6; no universal minimality beyond the stated equal-weight binary finite-population model is implied. Reproduction from root: `python3 research/expeditions/average-voice/oracle.py`. The independent JavaScript computation and Python source are from the same agent; this is independent implementation, not independent scholarly review. Repository checks and Python execution status belong to the PR record, not an inferred pass.

### Exaptation: machine consensus without anthropomorphism

A consensus utterance may be useful as a point forecast yet no longer support the same interpretation as its inputs. Treat "average of model reports" as a different contract from "estimated event probability calibrated against reference population R." Retain upstream event definition, horizon, population, weights and constituent estimates when needed, not merely a confident voice or a declaration of agreement. A recalibrator would require out-of-sample evidence on the actual deployment distribution. Never convert model agreement into a probability without evidence, infer independence from the number of models, or turn a Brier improvement into an assertion of safe decisions. Under a known loss function the required action depends on the posterior and decision cost; calibration alone does not establish utility or communication effectiveness.

The six-row example shows the limit of a scalar summary, in the spirit of X004's quotient guard. Preserve the vector if joint conditional distinctions earn their cost; if it is known that J=Q, the vector is unnecessary for this specific squared-loss prediction. Neither maximal retention nor maximal compression is a universal rule.

A speculative instrument, *The Calibration Carillon*: each source has a pitch proportional to its probability; the mean has its own pitch; an optional disagreement voice uses within-case variance rather than treating loudness as confidence. Equal means with different constituent pairs can yield identical mean-only scores, distinct multi-voice scores. The mapping is arbitrary art, not a claim about consonance, perception, accessibility or efficient encoding. A future experiment might ask whether a separately labelled spread helps a recipient recover source disagreement without confusing it with event risk; this is a hypothesis, not participant evidence.

### Afterword — fiction

At the observatory every bell was individually honest. One rang for half the storms and half the dry afternoons of its appointed category; another divided the sky differently. The conductor tuned them into a single impeccable average. The new bell was more accurate in its squared errors than either parent, yet its quarter-tones did not mean a quarter of the storms.

The astronomer asked whether it was a probability or a chord. The conductor answered that the two had the same pitch.

The next morning the astronomer kept both bells, not because plurality was sacred, but because the one note could not say which bells had sounded.

### Disposition

Formal identities under fixed-weight population assumptions; synthetic finite census; abstract-level source attribution; design conjecture and fictional afterword clearly separated. No empirical effect sizes, human response data, original theorem priority, publication or core programme acceptance. AI assistance: one ChatGPT agent, GitHub connector, public source search, independent JavaScript enumeration and Python implementation; no external reviewer or participant. Frozen protocol, canonical records and human gates unchanged.