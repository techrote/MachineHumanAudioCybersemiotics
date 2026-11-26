# The Forecast That Visits Every Door

**Refs #682 · 26 November 2026 · additive mathematics and synthetic acoustic specimens.** One ChatGPT GPT-6.2 research agent. Not canonical Track E/G evidence, operational alert qualification, human validation or scientific priority.

## Contents

1. Excavation — a stopped-posterior repair that does not repair workload.
2. Sharp horizon theorem — exact supremum at a fixed prior and threshold.
3. Constructive proof — four-value rational posterior laws with matching snapshots.
4. Exact two-tick fibre — sharp extrema and acoustic inventory.
5. Negative sediment — nonattainment, guard bands, scope and practical alternatives.
6. Qualification — executable checks, source reading and integration disposition.

## 1. Excavation

[Issue #545](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/545) and its full [first-alert report](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/mhac-545/first-alert-calibration/research/expeditions/first-alert-calibration/README.md), section “History-aware repair and a second obstruction,” correctly distinguish snapshot calibration from a genuine posterior under an increasing filtration. They also exhibit two coherent posterior paths with identical snapshot distributions but workload 1/2 versus 5/8 at threshold 3/4. This expedition resolves the extent of that second obstruction across arbitrary finite horizons. It is not a claim that history-aware calibration fails. The full [#330 report](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/mhac-330/forecast-wins-wrong-contest/research/expeditions/forecast-wins-wrong-contest/README.md), sections 2–4, separately changes posterior marginal distributions while retaining Brier loss; here the entire marginal is fixed at every reporting tick. #676 similarly motivates target-specific telemetry, but concerns moments of a single latency distribution.

Consider a fixed binary outcome Y, prior pi, filtration F_t, and P_t=E[Y|F_t] for t=0,...,N with P_0=pi. A first-only alarm triggers at the first reporting tick t in 1,...,N at which P_t >= tau, where 0<tau<1. Tick zero is not a reporting tick. There is no intervention changing Y and no censoring of the analytical posterior path after a trigger. Compare two systems with the same law of P_t for each t, not necessarily the same joint temporal law. Since each is a genuine posterior, their joint laws of (P_t,Y) also agree: P(P_t in B,Y=1)=E[P_t 1_{P_t in B}]. Thus every snapshot calibration table, Brier score, proper score with finite expectation, threshold confusion matrix and expected total count of above-threshold ticks agrees. The fraction of episodes needing at least one first-only notification need not agree.

The established surrounding discipline is martingale optimal transport, especially lookback payoffs. Our contribution is a self-contained elementary workload supremum over matched marginal families, a small exact attaining family for a specified two-tick marginal fibre, and a synthetic acoustic transfer; not a general solution of the prescribed-marginal lookback problem.

## 2. Sharp horizon theorem

**Theorem.** For N>=2 and fixed 0<pi<=tau<1, the supremum over pairs of coherent posterior systems with identical one-time laws of the absolute difference in the probability of at least one threshold alert is

    (pi/tau) * (1 - 1/N).

It is not attained. For N=1 or pi=0 the difference is zero. The construction uses just four possible posterior values at reporting ticks (0,a,b,1). Arbitrary real priors and thresholds are allowed; rational parameters give exact finite probability tables.

**Upper bound.** Write H_t={P_t>=tau}, h_t=P(H_t), m=max h_t, U=max of the two union probabilities, V=min. Both systems have the same h_t. Then V>=m and U<=sum h_t<=N*m. If T denotes the first reporting hit, the bounded stopped conditional expectation identity is E[Y 1_{hit}]=E[P_T 1_{hit}]>=tau*U. Consequently U<=pi/tau. Hence

    U - V <= U - m <= (1-1/N)*U <= (1-1/N)*pi/tau.

This also clarifies why correctly calibrated first alarms remain calibrated: for every first-hit score value x, the conditional truth frequency is x, provided the hit and score are measured in the forecast filtration. No claim of calibration is made for estimated posteriors or an outcome-dependent selector outside the filtration.

**Strictness.** Equality at positive pi and N>=2 requires every h_t=U/N>0, with all H_t pairwise disjoint almost surely in the larger-union system. But if P(H_t)>0, martingale coherence implies P(H_t intersect H_{t+1})>0: otherwise E[P_{t+1}|H_t]<tau while E[P_t|H_t]>=tau. This contradicts disjointness. Therefore no pair attains the displayed supremum under this inclusive threshold contract.

For pi>tau, the elementary upper bound 1-1/N remains valid, but the fixed-prior sharp bound is not claimed here. If the prior itself triggers an alarm, the workload contract changes completely.

## 3. Construction: the stable and rotating doors

Choose a small delta>0 with a=tau-delta>0 and b=tau+(N-1)*delta<1, so ((N-1)*a+b)/N=tau. Set

    r=min(a/b,(1-b)/(1-a)), c=pi/tau.

With probability 1-c use the constant-zero path. Otherwise choose a uniform labelled cohort j in {1,...,N}. At tick 1, its posterior is b for cohort 1, a for the others. The stable system intends b only in cohort 1 throughout. The rotating system intends b only in cohort t at tick t. For either intended schedule, a surviving cohort whose current value is x in {a,b} and next intended value is y in {a,b} transitions as follows:

    y with probability r
    1 with probability x-r*y
    0 with probability 1-r-x+r*y.

The latter two states absorb. The definition of r guarantees nonnegative probabilities for every x,y; their sum is one and their conditional expectation is x. The initial mean is c*tau=pi. Even in the filtration that includes the cohort identity after tick one, the process is a martingale. Drawing Y conditionally Bernoulli(P_N) gives a joint probability space with P_t=E[Y|F_t]. This is a law construction, not a machine secretly consulting Y to decide which score to emit.

Each active cohort survives t-1 steps with probability r^(t-1); their masses are equal. At each time the marginal of P_t is exactly

| Value | Probability |
| --- | --- |
| 0 | 1-c+c*(1-tau)*(1-r^(t-1)) |
| a | c*(N-1)/N*r^(t-1) |
| b | c/N*r^(t-1) |
| 1 | c*tau*(1-r^(t-1)) |

The endpoint probabilities follow by conservation of mass and mean. Hence both systems agree on all snapshot laws and their truth-labelled versions. All expected repeat counts agree too.

In the stable system, cohort 1 triggers immediately; the other cohorts trigger only if absorbed at 1. The exact workload is

    V_stable=c/N+c*(N-1)/N*a*(1-r^(N-1)).

Every cohort that survives until tick N in the rotating system has visited its own high tick. Therefore V_rotating>=c*r^(N-1) and V_rotating<=c. As delta tends to zero, r tends to one, V_stable tends to c/N and V_rotating tends to c. This proves sharpness. At delta=0 both near-threshold symbols collapse onto the inclusive boundary, so substituting zero into the limiting description is invalid.

**Interpretation.** Correct belief formation and correct instantaneous prediction metrics do not identify episode-level demand for human attention. The missing object is the dependence between successive legitimate forecasts, not an error in their semantics or calibration.

## 4. Exact two-tick fibre and rendered score

A second construction supplies attained sharp bounds for a specific matched finite marginal pair. Let integer m>=2, a=(m-1)/(2m), b=(m+1)/(2m), e=1/(m+1), v=1/2-e. P_1 takes a,b equally. P_2 takes 0,a,b,1 with probabilities e,v,v,e. Threshold is 1/2. Let the row for P_1=a be joint mass vector x, so sum x=1/2, weighted mean sum y_i*x_i=a/2 and 0<=x_i<=column_i. The row for b is its complement; it automatically has correct mean.

Let h=x_b+x_1. The first-only workload is 1/2+h. Filling the entire lower half gives mean a*v, below the required a/2 by a*e. Replacing h lower-half mass with upper-half mass increases the weighted mean by at most h, hence h>=a*e. Conversely the high mass alone contributes at least b*h to the mean, hence h<=a/(2*b)=v. Both endpoints are attained by the following low rows:

    minimum: (e-a*e, v, 0, a*e)
    maximum: (e, 0, v, 0).

Thus the exact fibre workload interval is [1/2+a*e, 1/2+v], and its width is (m-1)^2/(2*m*(m+1)). Every intermediate value is obtained by mixing the rows. This is sharper than merely demonstrating two counterexamples.

For m=9 the two full joint tables are integer inventories over 90 episodes:

| Model, first value | 0 | 4/9 | 5/9 | 1 |
| --- | ---: | ---: | ---: | ---: |
| Minimum, 4/9 | 5 | 36 | 0 | 4 |
| Minimum, 5/9 | 4 | 0 | 36 | 5 |
| Maximum, 4/9 | 9 | 0 | 36 | 0 |
| Maximum, 5/9 | 0 | 36 | 0 | 9 |

Both first-tick marginals are (45,45)/90, and both second-tick marginals are (9,36,36,9)/90. Minimum workload is 49/90 (54.444%); maximum is 81/90 (90%). The precision of first-only alerts is 29/49 and 5/9 respectively, both above 1/2; true-alert mass is 29/90 and 45/90 respectively. Those last quantities are population expectations of Y drawn conditional on the final posterior, not counts of measured people or actual truth samples.

The original synthetic audio specimens stable.wav and crossing.wav are generated by laboratory.py. Four posterior values map to 300,500,700,900 Hz. Two consecutive 50 ms notes represent one episode; each inventory has 90 episodes (9 seconds, 8 kHz mono PCM16). The score inventories are exact, shuffled with seed 682; the final binary Y is not encoded. Matched-template decoding from actual integer PCM recovers 360/360 frames. This is digital fixture validation, not physical transmission or listening evidence. A proposed first-only rendering would sound an additional notification only on the first high symbol in each episode. Do not confuse 90 rendered episodes with 90 statistical samples or a human evaluation.

## 5. Negative sediment and practical transfer

**Guard-band bound (not claimed sharp).** If every reporting tick avoids (tau-delta,tau+delta), with 0<delta<min(tau,1-tau), and high means at least tau+delta, the martingale constraint implies

    P(H_{t+1}|F_t) >= kappa = 2*delta/(1-tau+delta) on H_t.

Indeed the next forecast is at most tau-delta if low and at most 1 if high. Its conditional mean is at least tau+delta. Since each new hit after tick 1 must have been low at the immediately preceding tick,

    U <= h_1 + sum_{t=2..N} [h_t-P(H_t intersect H_{t-1})]
      <= [N-(N-1)*kappa]*m.

With B=N-(N-1)*kappa and U<=min(1,pi/(tau+delta)), the workload difference is bounded above by (1-1/B)*min(1,pi/(tau+delta)). This analytic bound is retained as a qualified guard-band control; exact sharpness and a dedicated computational census are outstanding. A guard band must be a real restriction of posterior support, not deletion or renaming of inconvenient observations. Fixed quantization, minimum reporting probability margins, and finite transition alphabets can preclude the limiting construction. A constant marginal distribution at two successive ticks forces equality of those two genuine posteriors almost surely by the variance identity; marginal drift is essential to the construction.

**Candidate MHAC design hypothesis:** retain event identity, prior, explicit threshold and equality convention, reporting horizon, full posterior trace or sufficient path-dependent first-hit counts, and the distinction between first-only and repeat policy. A first-only alarm workload receipt should report the episode denominator, first-hit distribution and outcome-linked counts. If traces are unavailable but finite marginal distributions are supplied, one can use an exact finite martingale-transport linear program with a variable per possible path: nonnegative masses, marginal constraints, and each prefix's next-mean constraint. The linear objective is total mass of hit paths. A two-tick row vertex enumerator is implemented here, not a scalable multistep optimizer. Directly logging first-hit flags is the simplest baseline and needs no such reconstruction. Do not infer an unmeasured workload or safety outcome from an ordinary score certificate.

If truth changes in time, action alters truth, the threshold adapts to undisclosed evidence, the score is an estimate rather than the true conditional probability, or recording stops on alert, the stated model no longer applies automatically. No claim about listener understanding, alarm fatigue, appropriate action, operational safety, or Brier/cybersemiotics endorsement follows. Conventional probability and transport geometry explain the proof; cybersemiotic interpretation remains an unvalidated design hypothesis. The fiction below is not evidence.

## 6. Qualification and source ledger

Run: python laboratory.py (Python standard library, no downloads). It writes execution.json and the two WAV files beside the script. The exact Fraction path oracle constructs literal absorbing paths and checks the Bernoulli outcome mass for every positive prefix, compares full truth-labelled one-time joint laws, verifies the stopped-posterior identity and stable formula, and checks the sharp global bound. The exact independent-of-formula row vertex oracle fixes all but two entries at their capacity endpoints and solves the two remaining equality constraints; every vertex of the bounded polytope is included (degenerate vertices may repeat). Counts are overlapping computational checks, not independent trials.

| Check | Count |
| --- | ---: |
| Paired cohort profiles (N=2..12, thresholds 1/4,1/2,3/4; prior fraction 1/3 or 1; three delta scales) | 198 |
| Positive-prefix identities across all audits | 76,686 |
| Two-tick exact fibres m=2..100 | 99 |
| Feasible vertex instances (duplicates permitted) | 891 |
| Decoded PCM frames | 360/360 |
| Assertion failures | 0 |

Two native repetitions gave identical JSON and WAV hashes. Source blob dbdbc873b464904f2bf29a392b36ab0b24cdd512 matches the locally executed Python file; execution receipt blob feb056a564b19f8ddc6595cabb1e2f35128e76a3. Numerical example values in JSON are float display conversions of exact rational calculations. No independent reviewer.

**Sources, access and comparison (26 November 2026, same agent):**

- Mathias Beiglböck and Nicolas Juillet, *On a problem of optimal transport under marginal martingale constraints*, Annals of Probability 44 (2016), DOI [10.1214/14-AOP966](https://doi.org/10.1214/14-AOP966), [arXiv:1208.1509](https://arxiv.org/abs/1208.1509). Read retrieved HTML introduction section 1.1, equations (1)–(2) and surrounding martingale coupling definition, including convex-order feasibility. This is the established framework, not an attribution of the particular fixed-prior workload supremum.
- Pierre Henry-Labordère, Jan Obłój, Peter Spoida, Nizar Touzi, *The maximum maximum of a martingale with given n marginals*, Annals of Applied Probability 26 (2016), 1–44, DOI [10.1214/14-AAP1084](https://doi.org/10.1214/14-AAP1084), [arXiv:1203.6877](https://arxiv.org/abs/1203.6877). Read retrieved preprint HTML (April 2013 version) introduction and section 2.3 through equation (2.4); journal abstract and metadata viewed. This directly precedes the general question of extrema of martingale maxima with prescribed marginals, in a continuous-time setting. We restrict to reporting-tick maxima and optimize the separation across shared marginal families, rather than claim a new general prescribed-marginal theory. No full-paper read or literature-wide priority audit.
- [#545](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/545) report and [#330](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/330) report read in full, both issues and comments inspected (none). The former cites Wilkinson and Ferro on calibrated sequences; a fresh retrieval of arXiv:2606.31621 failed in this run, so it is an inherited lead only, not a directly reverified source.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866; read AGENTS, RAG, programme, runbook, integrity and validation; examined 401 returned branch entries, 100 recent open issues, 100 open PR results, and targeted search queries including martingale, optional stopping, proper scoring and calibration. Prior #677 exact-head workflow 45795536661 completed successfully. Native full checkout failed DNS resolution. New branch mhac-682/posterior-doorways, additive files only; no shared canonical manifests or other worker branches edited. Draft/Refs pending independent substantive review and exact-head repository qualification. The synthetic work does not discharge core corpus gates.

*Fiction:* The clerk certified that every doorway had the same number of visitors each hour. In one building the same visitor returned to the same doorway; in the other, each visitor reached a different doorway before leaving. The apprentice was asked to count the visitors who had ever entered. The hourly ledger had no column for them.
