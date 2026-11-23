# The Warning That Makes Itself False
## Performative calibration, prevented futures, and the distinction between truth and success

**Expedition #226 · 23 November 2026 · original mathematical/synthetic work and interpretive essay.** Not a Track E or G result, accepted design requirement, listening experiment, causal inference from real data, or claim of priority. AI-authored by one ChatGPT research agent. All numbers below are stipulated or exact consequences of the stated toy models.

## Contents

1. **Archaeology** — locate a limitation of earlier static distinctions and separate this work from active branches.
2. **Two meanings of a forecast** — specify a public forecast and a policy-indexed event law.
3. **Fixed points and boundary debt** — derive exact conditions, grid gap, cycles and counterexamples.
4. **The score that rewards the wrong number** — distinguish honest self-consistency, predictive score and welfare.
5. **Repair without magic** — examine randomized response, conditional claims, and identification failure.
6. **Qualification** — reproducible integer oracle and exact counts.
7. **Exaptation and objections** — propose a bounded forecast contract, with stopping conditions.
8. **Source notes and afterword** — locate prior work and preserve fiction as fiction.

## 1. Archaeology

Reconciled main at 495a98ca12bae467a507031f04931aa4254b1866, AGENTS.md, RAG.md, the programme, runbook and integrity rules; inspected open issue/PR inventory and branch listing. This work is isolated to this directory on mhac-226/performative-warning. No central manifests, research claims, protocols, human gates or other branches are changed. The issue had no comments at creation.

The main-branch intellectual sediment atlas, [QUOTIENT-GUARD.md](../intellectual-sediment/QUOTIENT-GUARD.md), establishes sufficiency relative to a declared finite decision vector. Its limitation explicitly admits that dynamic systems require stronger conditions. Its [SHADOW-SEDIMENT.md](../intellectual-sediment/SHADOW-SEDIMENT.md) traces the anti-collapse habit back to the early auditory research: validity versus persuasion, recognition versus action, and urgency versus delivery. The main-branch [absence type system](../sound-of-nothing/TYPE-SYSTEM.md) distinguishes acoustic cessation from event resolution. The [Chiastic Trap](../chiastic-trap/README.md) refuses to infer actual restitution from a symmetric sequence of signs.

There is an underdeveloped common premise: the world against which the sign is evaluated may be treated as given. A predictive utterance, however, can participate in producing the outcome that will later be used to evaluate its accuracy. This is not a refutation of the static quotient theorem. It is a counterexample to transferring its static assumptions without qualification.

Nonduplication crosswalk (issue/PR material is noncanonical unless separately accepted):

| Related record | Distinction preserved here |
|---|---|
| [T002 #31](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/31) | Alert validity versus recipient decision; here the published probability itself changes the outcome law. |
| [T016 #60](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/60) | Observation versus diagnosis and remedy authority; here even a stipulated, perfectly known causal response can defeat unconditional forecast consistency. |
| [T018 #177](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/177) | The main-branch toy feedback mathematics concerns pressure/accommodation/failure gain; no affect variable is needed here. |
| [#203](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/203) | Destructive diagnostic queries change the observed state; this model is not trying to identify the initial state, but to forecast a future event after the forecast is heard. |
| [#220 / PR #221](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/221) | Fixed-weight pooling may destroy calibration across a fixed population; here a single public forecast can lack a fixed point because it changes the population law. |
| [#209](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/209), [#218](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/218) | Context-late code sufficiency and joint disclosure concern representation/observation; here the representation is an input to the outcome mechanism. |

The strongest bridge is between MHAC's epistemic calibration and the causal discipline of its action/repair studies. The dispute is real: a warning may help prevent an undesirable event yet be badly scored as a prediction of the world after action. Conversely, a system can make its forecasts predictively excellent by inducing undesirable events. Do not dissolve that conflict by redefining every warning as correct.

## 2. Two meanings of a forecast

Stipulate a binary future outcome Y, where 1 denotes an undesirable event in a fictional system. Let u = Pr(Y=1 | do(A=0)) and v = Pr(Y=1 | do(A=1)). These are **given model parameters**, not estimates from observational data. Assume the publication influences Y only through the stipulated action A, and that the population/other conditions stay fixed across counterfactual regimes.

A public forecast q in [0,1] is interpreted as the unconditional probability of the outcome under the policy it induces. A deterministic recipient policy is:

    A(q) = 0 if q < t, otherwise 1, with 0 < t <= 1.

The induced risk is R(q)=u if q<t, otherwise v. Self-consistency of the public probability requires q=R(q). This is a one-shot fixed point in a fully specified model, not a statement that every finite sample should have exactly that observed frequency. It is stronger than matching the grand mean across a heterogeneous collection of announcements.

If q instead means the event probability **in the absence of intervention**, q=u can be correct by stipulation even when the action is triggered and the realized event law is v. That is a different estimand. Saying the former while scoring the latter is not a harmless change of labels.

## 3. Fixed points and boundary debt

**Exact result.** Every fixed point belongs to {u,v}. The candidate u is valid iff u<t; the candidate v is valid iff v>=t. Thus:

| Condition | Fixed points | Interpretation |
| --- | --- | --- |
| u<t, v<t | u only | Both regimes are below threshold; untreated report is consistent. |
| u>=t, v>=t | v only | Both regimes are at/above threshold; treated report is consistent. |
| u<t<=v | u and v | Positive feedback can support two different consistent futures. |
| v<t<=u | none | Prevention crosses the trigger: the forecast that triggers treatment contradicts the risk after treatment. |

The proof is substitution in the two branches. All four cases are possible; prevention alone (v<u) does not imply impossibility. At equality t the action is 1, so the strict/weak inequalities matter.

With u=0.8, v=0.2, t=0.5, publishing 0.8 triggers treatment and gives risk 0.2. Publishing 0.2 avoids treatment and gives risk 0.8. Neither is an unconditional forecast consistent with this publication policy. A report of 0.5 triggers treatment and is also inconsistent. No deterministic public probability in the continuous interval is fixed.

**Discrete sharp gap.** Restrict q,u,v,t to integers on a common denominator N, with t represented by integer T in [1,N]. Below T the nearest report to U is a=min(U,T-1); at/above T the nearest report to V is b=max(V,T). The exact minimum absolute calibration residual is

    min(|U-a|, |V-b|)/N.

The branch domains are integer intervals, so these clamped endpoints minimize distance, and comparing them gives the global minimum. For no-fixed-point models this is min(U-T+1,T-V)/N. With N=10 and (U,V,T)=(8,2,5), the minimum is 0.3.

Continuous caution: for v<t<=u, the infimum is min(u-t,t-v). The untreated branch is open at t, so its boundary infimum need not be attained. If u=t and v<t, the infimum is zero although a fixed point does not exist; arbitrarily small residual is not proof of self-consistency. On the ten-point grid (5,2,5), the smallest residual is 0.1.

**Exact retraining dynamics.** The stylized retraining update q_(k+1)=R(q_k) moves into {u,v} after one update. In the no-fixed-point region it alternates u,v forever. Outside that region it reaches a fixed point in at most two updates (the two-fixed case retains whichever basin the initial report entered). This says nothing about empirical convergence of gradient descent, finite-sample learning, delayed reactions, or systems with changing policies.

A misleading validation result follows. In the alternating two-cycle with equal exposure to each report, the grand mean of the forecasts equals the grand mean of the event probabilities: (u+v)/2. Yet the conditional mean outcome at report u is v, and at report v it is u. Squared reliability defect is (u-v)^2. For 0.8 and 0.2, the mean is 0.5 on both sides and the defect is 0.36. Equal exposure is part of the construction; noisy samples need not exhibit exact equality. Calibration-in-the-large is not report-wise calibration.

## 4. The score that rewards the wrong number

For a Bernoulli event of risk r the expected binary Brier loss of a report q is

    L(q,r) = r(1-q)^2 + (1-r)q^2
           = r(1-r) + (q-r)^2.

For fixed r, strict propriety selects q=r. But in this model the first term is itself a function of the report. The two branchwise optima on the grid remain the nearest admissible points a and b, since the within-branch variance term is constant. Comparing their full losses need not select a fixed point, even when a fixed point exists.

Example: u=0.29, v=0, t=0.30, grid hundredths.

- q=0.29 is the unique fixed point: action 0; expected Brier loss 0.2059.
- q=0.30 induces action 1 and an event probability of zero. Its expected Brier loss is 0.09.
- Every q<0.30 has expected loss at least 0.2059, and every q>=0.30 has loss at least 0.09. Thus the unique score minimizer is q=0.30, **not** the honest unconditional fixed point.

This is an elementary discrete instance of the published performative-scoring problem, not a new scoring theorem (S2 below). It does not mean the score is intrinsically defective. The fixed-distribution conditions that give it its usual interpretation do not hold across the two policies.

There is also a converse ethical problem. For u=0.2, v=0.9, t=0.5, both 0.2 and 0.9 are fixed points. Their expected losses are 0.16 and 0.09, respectively. The lower loss rewards a worse event rate in the stipulated adverse-event model. Calibration is compatible with bad outcomes. An optimizing system would need a separate objective for action costs, outcome severity and authority. A truthful probability is not automatically a recommendation. The binary threshold policy is an invented mechanism, not a prescription.

## 5. Repair without magic

**Smooth response control.** Replace the threshold by a stipulated randomized action, Pr(A=1 | q)=q, where q is public and the realized action is not yet known. Now R(q)=(1-q)u+qv, an affine function. A fixed point is

    q* = u/(1+u-v).

For u,v in [0,1] the denominator is positive and the root is in [0,1], except at u=0,v=1 where every q is fixed. For the preventive example q*=0.5. This changes the intervention mechanism, rather than solving the original threshold problem. A real intervention must not be randomized merely to improve forecast self-consistency. If the action is already observed, a forecast of its resulting risk is a different conditional forecast.

More generally, any continuous map of [0,1] into itself has a fixed point by the intermediate value theorem applied to R(q)-q. Continuity cannot be presumed for people, rules, or software operating with hard thresholds. A fixed point need not attract retraining; e.g. u=1,v=0 in the smooth model gives R(q)=1-q, whose nonfixed starting points cycle.

**Policy-indexed communication.** The two utterances "Without action, the model estimates 80%" and "With the specified action, the model estimates 20%" have different truth conditions. In this stipulated model both are correct, independently of the threshold consistency of a single unconditional utterance. A decision system could select a policy using causal risk estimates plus cost/authority constraints, and then report the resulting policy-indexed risk separately. This is not a proof that conditioning on arbitrary observed actions is enough to remove performativity, nor a guarantee of proper incentives for reporting both counterfactuals. S3 explicitly warns that even making a target forecast-invariant does not automatically establish incentive-compatible elicitation.

**Counterfactual nonidentification.** If every deployment performs action 1 and the observed outcome law is Bernoulli(0.2), this is compatible with all of the following stipulated counterfactual models:

| u (untreated) | v (treated) | Risk reduction u-v |
| --- | --- | --- |
| 0.8 | 0.2 | 0.6 |
| 0.2 | 0.2 | 0 |
| 0.1 | 0.2 | -0.1 |

Under fixed action 1 all three yield the same distribution of observed outcomes, even with arbitrarily many independent draws. Thus a successful post-warning outcome does not establish what would have happened without warning; neither does a failed prediction establish that prevention worked. Evidence about the alternative policy requires an identification design or defensible additional assumptions. The listed probabilities are not real intervention estimates.

## 6. Qualification

[lab.js](lab.js) uses bounded safe-integer arithmetic, with N capped at 1,000. Loss numerator is computed using N^3 as common denominator. The closed-form branch solution is compared against explicit enumeration of every possible public report, using the unexpanded Bernoulli loss expression in the enumeration. It independently enumerates initial retraining states and verifies the rational smooth-root identity.

Run from repository root:

    node research/expeditions/warning-that-makes-itself-false/lab.js

Actually executed on 23 November 2026: the same JavaScript function body committed in lab.js ran in the tool's V8 JavaScript isolate before publication (one author; no independent human review). No random data, package installation or external numerical library.

| Check | Count/result |
| --- | ---: |
| All models with N=1..20, U,V=0..N, T=1..N | 50,050 |
| All initial grid reports for retraining check | 863,786 |
| No-fixed-point models (two-cycle) | 8,855 |
| Two-fixed-point models | 8,855 |
| Models with at least one fixed point but no Brier minimizer among fixed points | 2,800 |
| Smooth response root identities / degenerate cases | 50,050 |
| Named scenario checks | 5 passed |
| Malformed input refusals | 5 passed |

Counts describe the enumerated grid family, not frequencies of phenomena in deployed systems; grids repeat rational models at different denominators. The implementation and brute-force cross-check share one author, response function and runtime. The proofs are elementary and explicitly given above; test counts do not establish a general causal theory. Node execution on GitHub and repository CI are not claimed at this checkpoint.

## 7. Exaptation and objections

A minimal **forecast-target contract** for a future synthetic interface test might carry:

    target: adverse_event_by_horizon
    estimand: under_no_action | under_named_policy | under_fixed_action
    publication_policy_id: ...
    audience_response_assumption: ...
    forecast_time: ...
    horizon: ...
    estimate: ...
    action_taken: observed | unknown
    outcome: observed | pending | unavailable
    evaluation_target: matching_estimand_only
    evidence_for_alternative_policy: ... | unknown

No field gives itself causal authority. A claim of intervention efficacy requires evidence beyond this schema. The contract should be optional to the extent that a simpler interface establishes the same estimand. It is a candidate for research, not a proposal to force verbose spoken metadata into every alert. An interface might render only the currently relevant probability while keeping the model assumptions inspectable. A listener experiment would need to compare interpretation, timely action, and misunderstanding of counterfactual statements; no such experiment took place.

Adversarial objections and revision criteria:

- A normal status message about an already observed past fact is not a forecast. This result does not establish a paradox for truthful state reporting.
- A recipient may ignore the message. In the exogenous control u=v there is exactly one fixed point R(q)=u; conventional scoring applies in the stipulated population.
- If the response policy depends on a different forecast, multiple messages, history, or hidden variables, the two-branch map is insufficient; derive the actual joint mechanism.
- If the threshold never lies between the two risks, no prevention cycle follows. Positive feedback can give multiple equilibria; prevention can give a single equilibrium. Do not label all effective warnings self-defeating.
- If one only cares about reducing the event rate and action is costless, a constant action may be preferable to a public forecasting game. This would be a legitimate negative result for the proposed interface mechanism.
- A good Brier score may be valuable within a fixed deployment regime. Comparing it across endogenous policies without accounting for changed event law answers a different question.
- A counterfactual statement may be speculative, false, or unidentified. Adding "without intervention" does not validate it.
- There is no evidence here that humans interpret all probability statements as unconditional, or that nonhuman vocal delivery prevents confusion.
- The term "warning that makes itself false" is a title: probabilistic reports are not ordinary truth-valued event predictions. A single nonoccurrence does not falsify an 80% forecast. The mathematical failure is lack of distributional self-consistency.
- A model-derived forecast and a warning are different speech acts, but real utterances can perform multiple functions. The conceptual classification is not a universal linguistic ontology.

**Candidate test:** hold event horizon, intervention and causal model fixed; vary the displayed estimand and whether the recipient knows the policy. Test symbolic evaluators against known causal regimes first; only after existing human gates are satisfied consider whether human listeners distinguish baseline risk, treated risk and actual outcome. Stop if the real task does not contain an actionable forecast whose publication plausibly changes its target.

## 8. Source notes and afterword

Read extent, 23 November 2026: publisher landing-page abstracts of S1, S2, S3; metadata on those pages. No full-text proofs, figures, supplementary material, datasets or human listening studies were reviewed. These are primary author abstracts for intellectual ancestry, not empirical inclusions in MHAC. No copied source files or new license.

- **S1.** Juan Perdomo, Tijana Zrnic, Celestine Mendler-Dünner, Moritz Hardt (2020), *Performative Prediction*, ICML, PMLR 119:7599–7609. [Publisher abstract](https://proceedings.mlr.press/v119/perdomo20a.html). The authors define performativity as predictions influencing their targets and describe performative stability relative to resulting future outcomes. The threshold fixed-point calculation here is a separate elementary illustration, not an extraction of their convergence theorem.
- **S2.** Caspar Oesterheld, Johannes Treutlein, Emery Cooper, Rubi Hudson (2023), *Incentivizing Honest Performative Predictions with Proper Scoring Rules*, UAI, PMLR 216:1564–1574. [Publisher abstract](https://proceedings.mlr.press/v216/oesterheld23a.html). The authors report that expected-score maximizing forecasts generally fail to match post-report beliefs in performative settings. The exact grid example in §4 is our stipulated construction; no mathematical novelty is claimed.
- **S3.** Philip Boeken, Onno Zoeter, Joris M. Mooij (2025), *Conditional Forecasts and Proper Scoring Rules for Reliable and Accurate Performative Predictions*, NeurIPS 38. [Publisher abstract](https://proceedings.neurips.cc/paper_files/paper/2025/hash/17da6ad7f0821c9b62a9116ff9c1cf1b-Abstract-Conference.html). Authors describe forecast-invariance through appropriate conditioning and limits of ordinary scoring rules; their sufficient conditions are not reconstructed here. This is a particularly important counterposition to any claim that labeling a conditional forecast solves the problem.

### Fictional afterword: The Bureau of Unhappened Things

The city installed an organ that played the likelihood of rain in the square.

A high note caused the awnings to unfold. Under the awnings, the square remained dry. Every morning the adjudicator compared the note with the dryness of the stones and marked the organ unreliable. Its tuner lowered the note. The awnings remained folded. The square became wet.

The organ was not predicting rain in the atmosphere. It was predicting wet stones, which the city had once considered a more useful thing to know. Nobody had thought the name of the predicted thing would become a part of its weather.

A second instrument was commissioned. It had two voices, one for the uncovered square and one for the covered square. The adjudicator demanded to hear which was real. Both, said the tuner, if you understand the conditions. Neither, said the philosopher, until you have justified the model.

The maintenance department asked a different question: which roof should we open?

The city's archives preserved all three requests, and for the first time the organ could be right without anyone agreeing on what it was for.

*Fictional illustration only. No listening or cultural claim.*

---

**Disposition:** scoped additive expedition, review and exact-head CI pending. The strongest useful disagreement is not whether predictions ought to be true. It is whether a communicative act is being evaluated as a description, an intervention, or both, and whether the observer has specified the world in which that evaluation takes place.
