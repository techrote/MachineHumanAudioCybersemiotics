# Expected-loss comparator and conceptual alternatives — T002

This is a **normative, exact-probability, fictional model**. It is an intentionally economical competitor for subsequent R008/R011 analysis, not an assertion that humans use Bayes' rule or that the system can supply a calibrated prior.

## Model specification

Let H be a binary hazard with prespecified prior p. A detector emits A with sensitivity h = P(A|H) and false-alarm rate f = P(A|not H). Four joint masses are p*h, (1-p)*f, p*(1-h) and (1-p)*(1-f). PPV follows from the alert masses; P(H|silence) follows from the other two. Undefined posteriors for zero-probability observations are returned as JSON null, never assumed to mean safe.

For joint hazard mass x and non-hazard mass y, action causes false-action expected loss y*C_FP; ignoring causes miss expected loss x*C_FN. The optimal action for an observation is the lesser of the two, with 'ignore' breaking exact ties. Compliance is an explicit rival policy: act on every A, ignore silence. It is **not** an operationalization of trust; calling it trust would be a construct error.

## Verification model

An additional binary check has independently assigned sensitivity v_h, false-alarm rate v_f, and is conditionally independent of the alert given H. Its positive/negative joint masses are split by v_h/v_f. The oracle acts optimally after each check result. Verification incurs fixed per-event check cost C_check and hazard-weighted delay cost x*C_delay. The delay is an abstract monetary/utility proxy, not measured response time or hard-deadline censoring.

- 'bayes' chooses optimal action given the detector observation and no check.
- 'alarm_compliance' automatically follows the alarm signal.
- 'forced_verify' checks on every observed detector state, even when inferior.
- 'selective_verify' checks only when its **calculated** expected loss is lower than acting immediately.

By construction, a perfectly informed oracle's selective verification cannot exceed its no-check expected loss (absent rounding error), but a real human cannot be presumed to know these quantities. Under zero probability observations, the decision label is 'unobserved'; loss accounting contributes zero. The oracle does not authenticate alert sources, model correlated checks or distinguish status from user acknowledgements.

## Sensitivity and falsification

Rehearsal varies prevalence (.02, .2, .5), hit rate (.75, .95), false-alarm rate (.05, .35) and false-action cost (1, 3), with miss cost 5, verification h=.95/f=.05, check cost=.1 and hazard-weighted delay cost=.25: 24 exact cases. Three additional targeted adversarial examples deliberately vary checking quality/cost and compare simple policies. All parameter values were **invented for code qualification**, not fitted to a paper.

If cost-sensitive policy and event history account for human decisions, the additional communicative/semiotic framework must predict something independently discriminating: e.g. whether utterance structure affects *correct source attribution*, probability referent resolution, repair response or conditional-action meaning at matched posterior/cost/access. Such predictions belong in a preregistered design reviewed through #8/#11/#14, not a post-hoc explanation of an observed outcome. A pragmatic listener model may likewise outperform a simplistic Bayesian oracle if source-reliability history, meanings or common ground are causal. The competing accounts are **not** mutually exclusive and no philosophical account is statistically tested here.

## What the model does NOT predict

No acoustic detection, speech comprehension, perceived urgency, cross-cultural decoding, subjective trust, time-to-action, accessibility, calibrated probability estimates or real safety outcome is simulated. A good synthetic loss result cannot justify deployment. A simple ordinal trust measure cannot recover PPV or a decision criterion. Unknown prevalence, nonstationarity, source spoofing, stale status, dependence between verification and the primary detector, and multi-action utility are unresolved limitations.
