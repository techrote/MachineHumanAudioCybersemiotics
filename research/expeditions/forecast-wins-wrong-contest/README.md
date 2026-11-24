# The Forecast That Wins the Wrong Contest
## Sharp moment-to-decision bounds for a calibrated binary forecast

**Refs #330 · 24 November 2026 · mathematical/synthetic expedition, one ChatGPT GPT-6.2 author and self-review.** No empirical auditory findings, production privacy guarantee, priority claim or Track E/G acceptance.

## 1. Excavation and challenge

[Draft #323](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/de0b34e21bbf6185525e174026023b528af7414d/research/expeditions/forecast-hides-arrival/README.md), §§2–4, shows two previews with identical hard classification accuracy and different optimal privacy. Its example has unequal Brier loss; it explicitly refuses to discredit proper scoring. That refusal is sound, but leaves a sharper question: can equally calibrated forecasts with identical Brier loss still have different downstream utility? Can *better* Brier loss even reverse the downstream preference?

[Draft #237](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/0bd86578cc7dd27ce6ec176ab04c631b8f9e4a7d/research/expeditions/museum-of-unasked-questions/README.md), §§2–4, uses posterior conditional expectation under garbling to distinguish statistical equivalence from restricted decision performance. Its three-state shortlist reversal is different from our binary calibrated-score reversal. [Draft #285](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/285), first-hit theorem and repeat-exposure identity, shows that a score certificate may change meaning under selection of the population. Here the population is held fixed throughout; only the distribution of legitimate conditional probabilities varies. [Draft #253](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/253), equal-margin counterexample, keeps entire marginal histograms fixed while changing pairing. Here the histogram itself changes while its first two moments remain fixed. Do not conflate these different information losses.

Reconciled main at 495a98ca12bae467a507031f04931aa4254b1866; read AGENTS, RAG, programme, runbook, integrity and validation. Reviewed first 100 returned open issue titles (search cap), all 88 returned open PR titles, and targeted #323, #237, #285, #253 arguments; no exhaustive branch review claimed. #322 issue and comments read; no comments. #323 exact-head integrity run 45385283920 completed successfully; it remains a draft, not a scientific acceptance. New #330 issue/comment scope isolates this directory. Core empirical and theoretical corpus work remains gated.

## 2. The sharp moment region

Let H be a finite calibrated posterior probability for a fixed binary outcome Y: P(Y=1|H)=H. Let its mean a=E H, variance v=Var H, with known support [l,u] contained in [0,1]. Let L be the mean over the lowest half of its probability mass, splitting any atom at the median. Define d=a-L, the half-spread. The upper-half mean is a+d. Put m0=min(a-l,u-a), M=max(a-l,u-a).

**Theorem.** For any l<=a<=u, the complete feasible region of (d,v) is

    0 <= d <= m0,
    d^2 <= v <= M*d.

Consequently, at fixed feasible v, if M>0 the exact possible spread interval is

    v/M <= d <= min(sqrt(v),m0).

For constant support or degenerate prior, both d and v are zero. This theorem concerns a probability law, not a finite-sample estimate.

**Proof of bounds.** Affine normalization reduces to [0,1]; reflect if a<1/2. The half means give the support bound. Split H into equally probable lower and upper halves (randomly split an atom if necessary). Conditional variance decomposition gives v>=d^2. Take a separating median m. On the lower half x^2<=m*x, and on the upper half x^2<=(1+m)*x-m. Taking the two half expectations gives

    E H^2 <= (a+d)/2 + m*(a-1/2).

Since a>=1/2 and m<=a+d, this is <=a*(a+d), hence v<=a*d. Reflection gives v<= (1-a)*d when a<=1/2. Undo normalization: spread scales by u-l, variance by its square, so v<=M*d.

**Attainment of the entire region.** On normalized support with a>=1/2, take the minimum-variance law H=a-d or a+d with equal probability. For the maximum-variance law use H=0 with probability d/(a+d), otherwise H=a+d. (If a+d=0 use the constant law.) Since d<=a, at most half the mass is at zero; both laws have mean a and upper-half mean a+d. Their variances are d^2 and a*d. Both are supported below or at a+d, with at least half their mass at a+d. Mix these laws with any mixing probability to obtain every intermediate variance while preserving the upper-half mean and hence d. Reflect and rescale to cover all other supports. At most three distinct posterior values are needed. Every such law is a legitimate finite preview: sample its cell, then sample Y as Bernoulli(H); the resulting prior is a and the posterior is exactly H. Real weights are permitted in this mathematical construction; the laboratory uses bounded integer ratios.

An equivalent identity is d=min_m E|H-m|, attained at any median. Indeed, the two half masses cancel the terms in m and leave half the difference of their means. Thus d is a centered absolute-deviation functional, not the standard deviation.

## 3. Exact implications for the earlier privacy model

For a calibrated posterior, expected binary Brier loss B=E[(Y-H)^2]=E[H(1-H)]=a(1-a)-v. This follows by conditioning on H; it is the calibrated case of the established resolution decomposition. Here the expectation is conditional on X1=0 in #323, not a score on an unspecified full population. All forecasts in this report are genuine posteriors; an arbitrary uncalibrated numeric predictor need not obey the identity.

In #323's fair-initial, two-tick, three-recipient even-parity model with other transition probability 1/2 and hidden exogenous preview, the sharp optimal worst-pair total variation is

    delta(d)=max(0,(3*(a-d)-2)/8).

Holding the prior, calibrated Brier loss and support fixed therefore gives the exact envelope

    delta_best  = max(0,(3*(a-min(sqrt(v),m0))-2)/8),
    delta_worst = max(0,(3*(a-v/M)-2)/8),

with constant laws treated directly. Every intermediate value is attained because the full feasible region above is attainable. These are bounds on the optimized encoder for a specified forecast, not on an arbitrary deployed policy or a public forecast.

If a<=2/3 no preview is necessary. Otherwise write c=a-2/3. If c>m0 no cue respecting the support can achieve zero leakage. If 0<c<=m0, then perfect privacy is *possible for some* forecast at the given variance exactly when v>=c^2; it is *guaranteed feasible for every* calibrated forecast of that variance and support exactly when v>=M*c. The two thresholds generally differ.

At a=5/6 and support [1/2,1], c=1/6, M=1/3, so the possibility threshold is v=1/36 and the universal feasibility threshold v=1/18. The latter is the maximum variance under that support. With unrestricted [0,1], the universal threshold is 5/36, again the maximum. A score threshold cannot be interpreted as sufficient merely because one witness achieves privacy there.

## 4. Two counterexamples and a non-counterexample

All rows below have exact calibration, mean 5/6, and Bayes hard accuracy 5/6: they can always guess one (ties at 1/2 may be resolved as one). The following conditional probability laws are rational.

| Forecast | Posterior values (probabilities) | Variance | Brier loss | Lower-half mean | Optimal TV |
| --- | --- | ---: | ---: | ---: | ---: |
| Constant | 5/6 (1) | 0 | 5/36 | 5/6 | 1/16 |
| A | 2/3 (1/2), 1 (1/2) | 1/36 | 1/9 | 2/3 | 0 |
| B | 1/2 (1/5), 11/12 (4/5) | 1/36 | 1/9 | 3/4 | 1/32 |
| C | 1/2 (3/13), 14/15 (10/13) | 1/30 | 19/180 | 11/15 | 1/40 |

A and B have identical calibrated Brier loss and hard accuracy yet distinct optimal privacy, attaining opposite endpoints of the support-constrained envelope at variance 1/36. C has *strictly better* Brier loss than A, yet positive rather than zero optimal privacy. The source prior, timing, vocabulary, observer and utility constraints are held fixed. These are not calibration failures.

**Non-counterexample to Blackwell dominance.** If H' comes from state-independent garbling of the experiment generating H, then H'=E[H|garbled observation]. Jensen gives Var H'<=Var H, and for every fixed m, E|H'-m|<=E|H-m|. Minimizing over m yields d'<=d. Hence a more informative experiment in this order cannot worsen optimal privacy in the model. A and C are incomparable: C has greater variance but smaller d; neither direction of garbling is possible. A and B are also incomparable: equal variance under garbling would force identical posterior laws by conditional variance, contrary to their distributions. Proper scoring of a truthful probability and universal ordering of information channels are different objectives.

## 5. Exaptation and boundaries

**Interpretation/design hypothesis:** the portfolio's task-relative distinction should enter the actual forecast-evaluation specification. A calibrated scoring metric measures a legitimate property; it need not suffice to establish another procedure's performance. A score receipt should specify the population, target, law of the legitimate posterior, support, information access and downstream decision. For a lower-tail objective retain the weighted quantile curve or at least the applicable integral, not only the mean/variance. Test an equal-metric pair and a ranking reversal before accepting a universal claim. On an empirical sample, report uncertainty of both the score and tail estimate; this exact theorem does not supply confidence intervals or certify calibration. The prior #285 exposure-versus-case distinction remains separately relevant: a change of sampling unit is not required for this reversal but can introduce another defect.

No production score or privacy infrastructure is proposed. A Brier ranking remains appropriate for its own expected quadratic prediction objective. An experiment dominating another in the full Blackwell sense cannot show this reversal. A different observer (including one seeing the realized forecast), alphabet or source process needs a separate analysis. Unrestricted words including 111 permit anonymous direct repetition, a negative control inherited from #323. An uncertain source law or mistaken calibration invalidates the numerical inference from score to variance. Do not hide operational logs or reinterpret an actual warning merely to improve this synthetic privacy metric.

**Original unrendered symbolic score (artistic):** A and B both use an identical sustained note for the predicted bit. A's backstage dial alternates equally between 2/3 and 1; B's dwells briefly at 1/2 and longer at 11/12. The accompanist chooses the first chord by the lower-half mass, not by the sustained note. C wins the printed quadratic contest but loses the accompanist's contest. No listening experiment or measured audio.

**Fiction:** Three weather oracles enter a competition. The jury congratulates C for its smaller squared errors. The stage manager hires A because the orchestra must reorganize itself before the weather arrives. The jury demands a recount. The manager asks whether the competition's rules mentioned an orchestra.

## 6. Qualification and source comparison

Run `node lab.js` in this directory. The exact bounded-integer V8 execution returned:

| Activity | Count |
| --- | ---: |
| Sorted equal-weight posterior histograms (denominators 1..12, even population 2..8) | 350,957 |
| Constructed rational extremal/intermediate laws including reflection | 131,472 |
| Affine support checks | 131,472 |
| Variance inequality checks | 1,227,810 |
| Median absolute-deviation checks | 613,905 |
| Direct binary-joint Brier identities | 613,905 |
| Named comparative controls / input refusals | 10 / 6 |

The direct oracle sums the lower half of sorted mass and the first two moments, computes expected loss from binary joint counts, and checks the median identity separately. The construction tests all mixture grid points, not only endpoints. Counts overlap and are not independent experiments. Analytic proof supplies the continuous result. Native Node and clean full-repository validation were not executed in this environment; exact-head integrity and substantive review remain open. No independent human reviewer is claimed.

**Source reading and limits:** Allan H. Murphy (1973), [A New Vector Partition of the Probability Score](https://doi.org/10.1175/1520-0450(1973)012%3C0595:ANVPOT%3E2.0.CO;2), J. Applied Meteorology 12, 595–600, publisher abstract read 24 November 2026: the uncertainty/reliability/resolution partition is established prior art; no primary full-text reconstruction claimed. Stefan Siegert (2017), [Simplifying and generalising Murphy's Brier score decomposition](https://doi.org/10.1002/qj.2985), QJRMS 143, 1178–1183, publisher abstract read, supports the decomposition context. Alexander A. Gushchin and Dmitriy A. Borzykh (2017), [Integrated quantile functions: properties and applications](https://doi.org/10.15559/17-VMSTA88), Modern Stochastics 4, 285–314, targeted open HTML reading of Theorem 5(i) and Proposition 2, describes convex-order and binary-experiment comparison using quantile functions. Our fixed-median moment region is derived directly; the source supports the established surrounding mathematical framework, not an attribution of our particular bound or a priority claim. No literature-wide novelty audit.

Disposition: additive two-file expedition only, fresh issue branch, no canonical/shared changes. Refs #330 until exact-head integrity, review and normal integration. The core disagreement is preserved: optimal forecasting under one proper scoring rule is neither universal decision optimality nor proof of an invalid scoring rule.
