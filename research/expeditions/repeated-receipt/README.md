# The Receipt That Needs Another Receipt

**Refs #480 · 25 November 2026 · exploratory mathematical and acoustic research.**
Base main: 495a98ca12bae467a507031f04931aa4254b1866. One ChatGPT agent, no independent human review, no participant data, no priority claim. This is not a canonical Track E/G finding or an accepted interface specification.

## The anomaly

Five possible machine conditions, exactly one true. Each acoustic report honestly names a set containing the true condition. A report may be regenerated from the same persistent state.

Two instruments have identical restricted binary statistical experiments and identical expected number of emitted tones (three). The burst instrument names either the true condition alone or all five conditions, each with probability 1/2. The balanced instrument always names the true condition and two uniformly selected false alternatives. For any specified rival, either instrument retains it with probability 1/2. Both are binary erasure experiments when the state universe is reduced to two alternatives: the outside labels can be reconstructed in distribution by a state-independent randomization.

But a succession of reports resolves the five-way uncertainty at different rates. The burst instrument needs two reports on average; the balanced instrument needs 19/5 = 3.8. They have the same expected number of surviving rivals after every number of independent reports. This is a difference in the geometry of uncertainty rather than mean uncertainty.

## Model and exact laws

Let m≥1 be the number of false candidates, so n=m+1. Conditional on true state i, draw K with law w on {0,...,m}; given K=k, choose a uniformly random k-subset R of the false candidates. Transmit {i}∪R. The law w is independent of i. Repetitions are independent conditional on the unchanged true state. Every received report is perfectly decoded. The posterior given the entire transcript is uniform on the intersection of the reports under a uniform prior: each consistent state's likelihood is the same product of w_k/binom(m,k).

Let J_t=|R_1∩...∩R_t|, with J_0=m. Define

    p_j = E[binom(K,j)]/binom(m,j), j=0,...,m.

In particular p_0=1 and p_1=p=E[K]/m. The probability that a specified j-subset survives t independent draws is p_j^t. Inclusion-exclusion, applied to the other m-l false labels, gives the exact histogram

    P(J_t=l)=binom(m,l) sum_{j=l}^m (-1)^(j-l) binom(m-l,j-l) p_j^t.

Thus E[J_t]=m p^t for every law with the same p. For the first singleton receipt time T=min{t:J_t=0},

    P(T>t)=sum_{j=1}^m (-1)^(j-1) binom(m,j) p_j^t,
    E[T]=sum_{j=1}^m (-1)^(j-1) binom(m,j)/(1-p_j),  p<1.

The second identity sums a finite inclusion-exclusion expression over t≥0; all its geometric series converge since p_j≤p for j≥1. For p=1 there is no identification. Posterior optimal guessing accuracy under uniform prior is

    V_t=E[1/(1+J_t)]
       =sum_{j=0}^m (-1)^j binom(m,j) p_j^t/(j+1).

For the latter formula integrate E[x^J] from x=0 to 1 and expand E[x^J]=sum_j binom(m,j)p_j^t(x-1)^j. A binary restricted receiver sees the rival excluded with probability 1-p and included with probability p; the full raw output on this restriction is equivalent to that binary erasure output by the uniform-subset conditional reinflation argument of #236. This extends to every finite independent repeated experiment on a two-state support. The completion-time disagreement only appears for more than two possible states.

## Sharp convex-order theorem

Fix integer bounds 0≤L≤U≤m and a mean μ in [L,U]. The balanced law B puts all probability on floor(μ) and ceil(μ), with the unique weights giving mean μ (one point if μ is integer). The endpoint law E puts probability (U-μ)/(U-L) on L and (μ-L)/(U-L) on U, or a point mass if L=U.

**Theorem:** for every horizon t and every convex real function f on the integer survivor counts,

    E[f(J_t^B)] ≤ E[f(J_t^w)] ≤ E[f(J_t^E)].

All three have the same mean. Both extrema are sharp and attained simultaneously for all horizons. This is convex order, not ordinary stochastic order.

**Proof.** Hold all but one draw fixed, with intersection S of size s. For a random ordering of the m labels, let X_k count elements of S among the first k. Its distribution is hypergeometric. Set g(k)=E[f(X_k)]. Let a,b be the indicator increments of positions k+1 and k+2. By exchangeability conditional on the first k positions,

    g(k+2)-2g(k+1)+g(k)
      = E[f(X_k+a+b)-f(X_k+a)-f(X_k+b)+f(X_k)] ≥ 0.

If either increment vanishes the expression is zero; otherwise it is the second forward difference of f. Hence g is discretely convex. The piecewise-linear convex interpolation of g gives Jensen's lower bound at μ, attained by B. The secant through L,U gives the upper bound, attained by E. Condition on the other draws, replace the chosen draw by the appropriate extremal law, and repeat one draw at a time; independence ensures the conditioning does not change its law. This proves the theorem.

Take f(j)=1[j=0], a discretely convex function, and f(j)=1/(1+j), also convex. The endpoint law maximizes singleton coverage and posterior guessing accuracy; the balanced law minimizes both. Take f(j)=log(1+j), concave: the directions reverse for expected posterior entropy. Integrating the completion tails gives extremal mean completion times. In the unrestricted case E has endpoints 0,m; J_t equals m with probability p^t and zero otherwise, so E[T]=1/(1-p), P(T≤t)=1-p^t, and V_t=1-m p^t/(m+1). This matches the elementary bound P(T>t)≥p^t from any single false candidate.

The peak/floor formulation is relevant when an acoustic packet cannot have arbitrary polyphony. It says exactly which list-size variability is valuable under these assumptions. It does not assert that peak-heavy chords are perceptually easier. If a listener's required action is to name a shortlist of size l>1, the payoff min(1,l/(1+j)) need not be convex. Do not generalize the ordering to all decisions.

### Adaptive extension (analytical, not separately enumerated)

Permit a history-dependent choice of w at each round, but require conditional on true state and past reports that the same bounds and mean apply and that the false subset is uniform given its size. The fixed extreme strategies still optimize every terminal convex survivor-count payoff. Backward induction: the value of a fixed extreme strategy with r future draws, as a function of current survivor count s, is convex because conditional on the independent future intersection size it is the expectation of f of a hypergeometric count, convex in s by the same increment argument. One-step optimization of this value therefore again selects the same extremal law. This also works for a predetermined varying sequence of per-round bounds and means, selecting the corresponding extrema at each round. Posterior uniformity for adaptive policies requires the choice law to be the same function of public history for every consistent true state; if policy selection leaks additional state information the posterior formula does not automatically apply.

### Completion scales

For fixed p in (0,1), the worst exchangeable iid law's mean T grows as log base 1/p of m plus a bounded additive term as m grows. Proof: under B, the variance of K is at most the binomial variance at the same mean, by the one-dimensional convex-order argument. Thus p_2≤p² (for m≥2), and distinct survivor indicators have nonpositive covariance after independent draws. Var(J_t)≤E[J_t]=a=m p^t. The second-moment bound gives P(J_t>0)≥a/(1+a); the union bound gives P(J_t>0)≤min(1,a). Sum both bounds over t≥0. Splitting at floor(log base 1/p of m), the lower deficit before that index and upper excess after it are bounded geometric series depending only on p. In contrast the unrestricted endpoint mean remains 1/(1-p) for all m. This is a logarithmic disparity under identical pairwise experiments and identical expected per-report list sizes.

At p=1/2, the exact computation yields:

| False candidates m | Balanced mean T | Endpoint mean T | Balanced unique after 4 reports | Endpoint unique after 4 reports |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 3 | 2 | 0.875 | 0.9375 |
| 4 | 3.8 | 2 | 0.754629 | 0.9375 |
| 8 | 4.656835 | 2 | 0.557583 | 0.9375 |
| 16 | 5.535030 | 2 | 0.303569 | 0.9375 |
| 32 | 6.455572 | 2 | 0.089867 | 0.9375 |
| 64 | 7.405157 | 2 | 0.007870 | 0.9375 |

Decimals are truncated or exact; see execution.json for rational means. With fixed per-report duration, cumulative expected tone appearances up to the first singleton equal (1+μ) E[T] by the independent-draw stopping identity: the event T≥t depends only on previous reports, so each report's expected cost conditional on its being sent is still 1+μ. This is a modeled count, not acoustic energy or workload.

## A descendant of the parity museum

The earlier #236 report studies equivalence on every proper state support in one observation. It proves that two symmetric per-subset likelihood profiles differ by an alternating sequence if their proper restrictions agree. We reuse that proof, and investigate repeated convergence rather than re-claiming it.

For m false labels, equality of all proper restrictions means p_j agrees for j<m; only p_m, the full-set probability, may differ. The intersection channel after t reports remains symmetric and its corresponding moments are p_j^t. Thus the difference of its survivor histograms at l is

    (-1)^(m-l) binom(m,l) (a^t-b^t),

where a,b are the two full-set probabilities. In particular the absolute singleton coverage gap equals |a^t-b^t| and the absolute posterior guessing gap equals |a^t-b^t|/(m+1). The pure parity pair has a=1/A,b=0 with A=2^(m-1), so the gap decays as A^(-t). Their local statistical equivalence persists at every horizon even as the global gap shrinks.

**Sharp deadline gap across all locally equivalent symmetric pairs.** For m≥2, orient a=b+δ. By the alternating per-subset difference from #236, each of the two profiles contains a parity component of mass Aδ and shares a common nonnegative remainder of mass 1-Aδ. The lower full-set probability b is entirely from the common remainder. Hence 0≤δ≤1/A and b≤1-Aδ. For fixed δ, the gap is maximized at b=1-Aδ, realized by placing the common remainder entirely on the full set. The optimized gap at t=1 is 1/A. At integer t>1 maximize

    [1-(A-1)δ]^t - [1-Aδ]^t.

Differentiation gives a unique interior maximum: write r=((A-1)/A)^(1/(t-1)). The ratio b/a decreases strictly from 1 to 0 as δ goes from 0 to 1/A; the derivative changes from positive to negative at b/a=r. Substitution gives

    max gap = (1-r^t)/(A-(A-1)r)^t.

This is an analytic result, not included in the exact census except for the pure parity special case. The extremizers depend on t; for every fixed pair with a<1 the gap tends to zero. Yet the optimized gap across channel pairs tends to (1/A)(1-1/A)^(A-1) as t→∞. A convergence theorem for each fixed channel is not a uniform convergence theorem across arbitrarily uninformative channels. At m=2 the limiting worst gap is 1/4. No general asymmetric-channel optimum is claimed.

## Negative sediment and interpretive bridge

- **Replay:** draw R once and repeat that identical set forever. Its one-round experiment and each time marginal are identical to fresh iid drawing. Under replay J_t=K for all t≥1 and a non-singleton first report never resolves. A fixed K>0 therefore makes T infinite almost surely; if P(K>0)>0, the unconditional mean T is infinite. Repetition count and number of independent evidence-generating events must not be conflated.
- **Nonexchangeable false alternatives:** use the seven nonzero binary 3-vectors as false labels. Choose a uniformly random line {a,b,a XOR b}, a≠b. Each label is included with probability 3/7 and every report retains three false labels. Every pair of lines intersects, so P(T≤2)=0; for the uniform three-of-seven balanced law it is binom(4,3)/binom(7,3)=4/35. The balanced extremum requires exchangeability, not merely equal binary retention probabilities and a fixed list size. Verified in witness.py.
- **Nonuniform priors:** intersection remains a sufficient statistic in the symmetric iid model, but posterior mass is proportional to the original prior on that intersection. The uniform-prior guessing formula is not portable unchanged.
- **Changing truth, false exclusions, masking and uncertain decoding** invalidate the simple intersection contract. An incorrect exclusion is irreversible unless explicit revision semantics restore it. Zero posterior support is a strong claim that requires a trustworthy exclusion mechanism.

The communication question is not simply whether repeated messages have been received, but whether they have narrowed the admissible world set. #193 (provenance plurality/false corroboration) is conceptually adjacent; this expedition deliberately studies a fixed single truth and a precisely specified stochastic exclusion mechanism rather than source provenance in general. The coupon-collector analogy identifies each excluded alternative as a collected coupon; the information-bearing event is collecting the final missing rival.

A proposed receipt would distinguish generation ID, observation/diagnosis epoch, truth-persistence assumption, permitted dependence model, report set, cumulative candidate set, and newly excluded labels. A repeated rendering should not automatically increment an evidence counter. A fresh report may also exclude nothing new. This is a design hypothesis, not empirical validation or a claim about Brier's doctrine.

## Original sound construction

The Receipt Organ assigns five fixed tones (200, 300, 400, 500, 600 Hz) to five candidate conditions A–E. The true condition is A. Three original deterministic four-chord scores use 300 ms tapered tones and 100 ms gaps, fixed per-tone gain:

| Score | Four report sets | Cumulative surviving counts |
| --- | --- | --- |
| Burst | A, ABCDE, A, ABCDE | 1,1,1,1 |
| Balanced | ABC, ABD, ADE, ACE | 3,2,1,1 |
| Replay | ABC, ABC, ABC, ABC | 3,3,3,3 |

Burst and balanced both emit A four times and each rival twice, with twelve total voice appearances. They have different peak polyphony and resolve at different times. Replay does not have equal finite-score marginals; it illustrates one realization of a persistent reused draw. These are selected demonstration scores, not random trials or independent perceptual judgments. Generated audio: 1.6 s each, 8 kHz mono PCM16; the source and SHA-256 receipts allow regeneration. No binary audio or third-party source text is committed.

Potential playable instrument: let performers choose list-size dispersion, replay/fresh mode, candidate count and peak limit. Render the full reports in one channel and their cumulative intersection in another. Add an explicit revision gesture to investigate how erroneous exclusions could be repaired; that extension is not implemented here.

**Fiction:** The clerk asked the same oracle four times. On the fifth page he finally drew two boxes, one for the sound he had heard and one for the alternative it had removed. The oracle had not learned to speak less. The clerk had learned to count a different thing.

## Computational evidence and source ledger

Run `node laboratory.cjs` for the exact BigInt census; the laboratory function executed in a V8 environment and was serialized to the committed source with a CLI wrapper. The wrapper itself was not executed in that environment. The core uses exact labelled-mask intersection propagation and separately computes binomial inversion.

| Check | Actual count |
| --- | ---: |
| Denominator-four profiles, m=1..6 | 461 |
| Exact histogram comparisons, horizons 1..5 | 2,305 |
| Histogram cells | 13,855 |
| Stop-loss convex-order inequalities, full and observed-support bounds | 55,420 |
| Profiles with restricted peak/floor | 378 |
| Mean identity checks | 2,305 |
| Posterior accuracy inequalities | 4,610 |

Run `python witness.py results` for the separately implemented rational hypergeometric size chain and the original sound rendering. Native Python executed twice and both complete receipts were byte-identical. It checked 500 histograms, 5,032 convex-order inequalities, 252 parity histogram cells and the Fano counterexample. Source and receipt blob hashes were checked against local native execution. These are same-agent cross-checks, not independent peer review. Adaptive and optimized deadline-gap proofs have no separate exhaustive qualification here.

Sources read on 25 November 2026:

- Wolfgang Stadje, “The collector's problem with group drawings,” *Advances in Applied Probability* 22(4), 866–882 (1990), DOI https://doi.org/10.2307/1427566. Publisher abstract and bibliographic metadata inspected: fixed-size uniform group drawing, count and collection-time problems. Full text not accessed; no claim about the paper's exact formulas or priority beyond the abstract.
- Carina Betken and Christoph Thäle, “Approaching the coupon collector’s problem with group drawings via Stein’s method,” *Journal of Applied Probability* 60(4), 1352–1366 (2023), DOI https://doi.org/10.1017/jpr.2023.6. Publisher HTML abstract, §1 and beginning of §2 inspected. The authors study fluctuations of the number of uncollected types under fixed-size uniform group drawing and summarize random-package-size antecedents. Their asymptotic results are not used to establish our convex-order proof. No exhaustive literature novelty search claimed.
- Aumyo Hassan and Sarah J. Barber, “The effects of repetition frequency on the illusory truth effect,” *Cognitive Research: Principles and Implications* 6, 38 (2021), DOI https://doi.org/10.1186/s41235-021-00301-5. Publisher abstract and significance statement inspected. They report experiments where perceived truth increases with repeated exposure, with diminishing increments. This is a contrary motivation against treating human belief updates as the ideal set-intersection decoder, not evidence for this acoustic design or a complete appraisal of the study.
- MHAC #236, *The Museum of Unasked Questions*, report on its own branch inspected, not presumed accepted. The exact one-shot restriction and parity argument is prior repository work. The present work is explicitly an extension in time, not a replacement. #193 was identified by issue search; no close reading of its deliverables claimed.

No source texts copied. All derivations are original in this report as expositions, without claims of publication priority. Synthetic counts, mathematical proof, interpretive proposal and fiction are distinct.

Reconciliation: root AGENTS, README, RAG, programme, runbook, research integrity, validation and foundations read; nested research AGENTS paths returned 404; branch pagination and recent open issue/PR search completed; targeted searches on Blackwell, subset channels and repetition identified #236 and #193. Preceding #469 exact-head CI successful (run 45542338245). Native Git checkout failed DNS resolution; no full repository validation claimed. Only this fresh issue-scoped path changed. Keep draft/open pending review and exact-head checks; no main merge or canonical registry change.
