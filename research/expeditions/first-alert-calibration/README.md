# The Alarm That Chooses Its Own Evidence

**Issue #545 · 2026-11-25 · exploratory mathematics and synthetic apparatus.** No participant data, empirical corpus admission, scientific-priority claim or production alert policy. Single ChatGPT research agent; no independent reviewer.

## The anomaly

An instrument can report exactly calibrated probabilities at every scheduled tick, yet an alarm triggered by the first high reading can be grossly miscalibrated. The timing of the alarm is itself evidence. This differs from repeated independent evidence in #480 and persistence-filtered counts in #458: here the truth is one fixed event, and the full joint law of each individual score and truth is preserved. It is an additive mathematical extension beside #31, not a modification of its existing correlated-check task.

Consider equally probable truth classes Y=0 and Y=1, each with four equiprobable labelled worlds. At each of four ticks, three true worlds and one false world receive score 3/4; the remainder receive 1/4. Every score is exactly calibrated at every tick. In instrument A the high-score worlds are unchanged. In B the same three true worlds remain high but the one false world rotates through all four. Both have identical snapshot reliability tables and Brier scores, but first-alert precision is 3/4 versus 3/7. Every first alert after tick one in B is false. The schedule is a joint distribution, not a device that has access to the hidden truth at runtime.

## Exact sharp bounds

Let Y be a fixed binary outcome with prior pi in (0,1), S_t a score, H_t the event S_t >= h, and H the union over t=1,...,n. Define a_t=P(H_t|Y=1), b_t=P(H_t|Y=0). Let l_a=max a_t, u_a=min(1,sum a_t), and similarly l_b,u_b. Write F(a,b)=pi*a/(pi*a+(1-pi)*b) whenever the denominator is positive.

**Theorem 1.** Given all per-tick joint laws of (Y,S_t), the sharp endpoints of P(Y=1|H) are F(l_a,u_b) and F(u_a,l_b). Assume an alert is possible. If one entire class has zero high probability, the nonempty alert precision is identically zero or one, respectively.

Proof: the union probability within each class is at least the maximum marginal probability and at most the sum capped at one. F increases in a and decreases in b. Both endpoints are realized by coupling separately conditional on Y. For the lower union endpoint use nested intervals [0,p_t) on a uniform unit interval. For the upper endpoint place consecutive arcs of lengths p_t on a unit circle; their union has measure min(1,sum p_t). Having chosen the high/low indicator, sample the original conditional score distribution in the corresponding region, preserving every supplied (Y,S_t) law. Mix endpoint couplings if intermediate union probabilities are desired. The construction proves sharpness, not merely an inequality. Finite rational marginals admit finite labelled-atom versions.

**Theorem 2 (horizon penalty).** If every snapshot alert has precision at least h, then every nonempty first-alert population has precision at least h/(h+n(1-h)). Here h is in (0,1). For the stronger requirement of exact snapshot calibration, the same bound is attainable at every prior pi<h.

Proof: snapshot precision implies (1-pi)b_t <= pi*a_t*(1-h)/h. Therefore (1-pi)P(H|Y=0) <= n*pi*P(H|Y=1)*(1-h)/h. Divide by total alert mass. To attain equality choose a positive a small enough that b=pi*a*(1-h)/((1-pi)*h) satisfies n*b<=1; nest identical true high sets and use disjoint false high sets. Emit h on high sets and the Bayes posterior pi*(1-a)/(pi*(1-a)+(1-pi)*(1-b)) on low sets. That posterior is below h when pi<h, as follows from averaging it with h to obtain pi. Thus both score values are exactly calibrated.

For prior 1/10 and 100 ticks, take 100 equiprobable worlds within each class. At every tick 81 true worlds and one false world score 9/10; everyone else scores 19/910. Rotate the false singleton and keep the true set fixed. First-alert precision becomes 9/109 (~8.26%). Every tick has precisely the same joint truth/score distribution. After the first tick, every newly triggered alarm is false. This is not a claim about any operational alarm system.

The false-to-true odds of the alert population can thus be n times the permitted snapshot odds. At fixed h the lower bound tends to zero as n increases; the construction can depend on n. It is not a statement that every fixed process deteriorates.

## Even auditing all proper temporal subsets can miss the defect

For n>=2, let true-class high histories be all ones with probability 3/4, else all zeros. In the false class, mix half mass at the zero word and half uniform on either the even-parity or odd-parity binary words of length n. Any proper projection of the parity classes is uniform because at least one omitted bit can flip to satisfy the required parity. Thus even and odd instruments have identical joint laws of Y and any proper subset of scores. Each high bit has conditional probabilities 3/4 versus 1/4, so with prior 1/2 the score alphabet {1/4,3/4} is calibrated.

False-class union probabilities are (1-2^(1-n))/2 versus 1/2. The corresponding first-alert precisions are (3/4)/(3/4+(1-2^(1-n))/2) and 3/5. At n=3 these are 2/3 versus 3/5, despite identical truth-labelled pairwise laws. This is a temporal parity trade, related to #236/#522, but now its consequence is selection-induced calibration ambiguity. The gap of this particular construction shrinks with n; it does not establish a universal large discrepancy under all proper-projection audits.

## History-aware repair and a second obstruction

Let F_t be an increasing information filtration, and P_t=E[Y|F_t]. If tau is the first threshold crossing by tick n (or no alert), {tau=t} belongs to F_t. Summing E[Y*1_{tau=t}]=E[P_t*1_{tau=t}] over t gives E[Y|alert]=E[P_tau|alert]>=h. More generally, conditional on the emitted posterior, the selected alert population is calibrated. The same identity holds when conditioning on any additional F_t-measurable selection event. This is a simple stopped conditional-expectation argument, not a frequentist confidence sequence or a certificate that an estimated posterior is correct.

In the rotating example, a late first crossing reveals Y=0 exactly: the history-conditioned posterior is zero, unlike the snapshot score of 3/4 or 9/10. A repair must change the estimate using the previous evidence, not just change its acoustic rendering.

Even genuine posterior sequences with the same snapshot distributions need not have the same alarm workload. Consider P1=1/4 or 3/4 with equal probability. At the next tick P2 is 0,1/2,1. Two conditional transition matrices, with rows in P1 order and columns in P2 order, are:

    A = [[2,2,0],[1,0,3]] / 4
    B = [[3,0,1],[0,2,2]] / 4

In either case sample Y conditional on the whole path as Bernoulli(P2). Each row has conditional expectation P1; both are genuine history-conditioned posterior processes. Their P2 marginal is (3,2,3)/8 and their P1 marginal is identical. At threshold 3/4, ever-alert probability is 1/2 versus 5/8, with precision 3/4 versus 4/5. So the repair guarantees a precision floor, not an alarm-count prediction. This is an elementary instance of dependence-sensitive path observables.

If pi<=h, the posterior contract also implies P(H)<=pi/h and P(H,Y=0)<=(1-h)*pi/h by summing the stopped posterior identity and using P(H,Y=1)<=pi. Both are sharp: reveal h with probability pi/h and zero otherwise at the first tick, with Y drawn accordingly. For pi>h these bounds may be weaker than trivial bounds. No claim of a bound on P(H|Y=0) independent of prior is made.

## Exaptation: the first-alert organ

A score stream and its trigger policy are different communication objects. A synthetic instrument can render high and low scores as two fixed-frequency pulses. For each possible world, compare a raw snapshot stream, a first-only alert stream, and a history-conditioned posterior stream. For the four-tick population, true worlds 0..2 have high-high-high-high and world 3 has low-low-low-low in both models. In A false world 0 is high-high-high-high and the other three are always low. In B false world j has a single high at tick j. Individual tick histograms are identical. The first-only scores are not: A has four alerts across eight equally weighted worlds, B seven.

Proposed protocol fields: event identity, score definition, conditioning history, observation epoch, alert policy/version, first-crossing flag, actual posterior scope, empirical policy-level precision (when measured), and separate consequence/action fields. Do not describe score-conditioned probability as an unconditional alarm reliability or collapse it with urgency. A prospective synthetic interface comparison would hold score sequence, cue mapping and duration fixed and contrast snapshot versus history-conditioned annotations. Real users, perceived trust and action appropriateness are untested; #20 governs participant work.

Negative sediment: repeat alarms, changing outcomes, actions that influence truth, unknown censoring, extra hidden information available to the trigger, stale estimates and model drift require different contracts. Counting only audible alarms can hide the non-alert denominator. A posterior can be correct for the wrong event definition. Repeated single-event forecasts are not independent validation samples; testing statistical calibration over many events is another problem. A Bayesian posterior is not an e-value. There is no human advantage or safety certification here.

## Source ledger and reproducibility

- Thomas Wilkinson and Christopher Ferro, *Calibrated Probability Forecast Sequences and Measure-Valued Martingales*, preprint 30 June 2026, [arXiv:2606.31621](https://arxiv.org/abs/2606.31621). Read retrieved text Introduction and section 2, especially Definitions 2.1–2.3, Proposition 2.4 and following remarks, on 25 November 2026. Authors distinguish isolated calibration from fixed-event history-conditioned calibration; Proposition 2.4 includes terminal truth consistency, not merely a martingale of scores. Some display equations absent from text extraction; PDF and direct HTML routes failed. Not a full-paper review; no priority assertion adopted. The stopped binary-posterior argument above is self-contained.
- Sebastian Arnold, Alexander Henzi, Johanna F. Ziegel, *Sequentially valid tests for forecast calibration*, [arXiv:2109.11761](https://arxiv.org/abs/2109.11761), retrieved preprint text dated November 8, 2021, section 1; journal DOI [10.1214/22-AOAS1697](https://doi.org/10.1214/22-AOAS1697). Read introduction passages about sequential testing and optional stopping; journal DOI retrieval failed. This paper addresses sequential statistical evaluation of forecasts (including PIT tests), not the precise within-event first-alert PPV theorem. It is a methodological counterposition to treating ordinary snapshot evaluation as enough, not a validation of our toy model.
- Related MHAC records: [#31](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/31) and its correlation-scope comment were read in full; [#480](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/480), [#458](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/458), [#236](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/236), [#522](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/522) are adjacent expedition leads, not external evidence. No canonical corpus or shared manifest edited.

Reproduce with `node laboratory.cjs`. Exact integer enumeration (counts remain within safe integer range) checks all labelled set schedules with up to four atoms per class and four times, extrema and all intervening integer union sizes, paired endpoint precision inequalities, all proper projections of parity examples through n=10, literal first-alert examples, and the posterior coupling rows. The execution receipt records 74,954 schedules, 1,270 marginal profiles, 1,928,000 paired endpoint comparisons and 86,525 projection cell comparisons, all passed. This is bounded same-agent computational qualification, not independent proof review. Scope is exploratory; formal evidence protocol remains unchanged.

Reconciliation: base main 495a98ca12bae467a507031f04931aa4254b1866, 332 branch entries and 100 recent open issues / 100 open PR results, targeted searches for martingale, optional stopping, first passage, confidence threshold and running maximum; read AGENTS, RAG, programme, runbook, integrity, validation, experiments and #31/comments. Previous own expedition #539 exact-head workflow 45598528842 succeeded. New issue-owned branch only. Keep draft pending integrator review; no shared aggregation or merge here.

*Fiction:* the clerk had checked each bell against the truth. The apprentice checked the first bell against all the bells that had not rung. It was the silence before it that changed what it meant.
