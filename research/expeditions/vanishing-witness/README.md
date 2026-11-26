# The Witness That Must Sometimes Disappear

Issue #707; 26 November 2026. Exploratory mathematics, synthetic acoustic specimens and a design hypothesis, not accepted empirical research. Refs #703 and #698 (draft ancestors, no merge dependency). All reasoning and computation by one ChatGPT agent. No independent human review.

## Contents
- [Contract and anomaly](#contract-and-anomaly) — exactly known versus uncertain state-blind erasure.
- [Reduction to a lattice](#reduction-to-a-lattice) — exact finite LP despite unrestricted finite side alphabets.
- [Known rate: sharp optimum](#known-rate-sharp-optimum) — a catalyst that works at exactly one erasure rate.
- [Uniform interval: sharp optimum](#uniform-interval-sharp-optimum) — robust design and an all-alphabet dual certificate.
- [Countercontrols and implications](#countercontrols-and-implications) — nonmonotonicity, hidden between-knot failures and limitations.
- [Sources and qualification](#sources-and-qualification) — reading extent, reproducibility, disposition.

## Contract and anomaly

In #703, a positive polynomial with signed coefficients encoded the difference between the binary experiments E and F. Here we ask how much independent erasure a supplementary instrument can tolerate. Fix the same primary tables (each column is one output, rows are + and -):
    
    E+: 2/21, 5/7, 4/21     E-: 1/3, 5/8, 1/24
    F+: 3/7, 4/7            F-: 3/4, 1/4

For any side channel R with finite alphabet and strictly positive conditional output probabilities, observe the primary report unchanged and independently acquire R conditional on the same binary state. With probability e, independently of both reports and the state, replace the entire side report by a distinct, flagged erasure symbol. This symbol has likelihood ratio 1. Denote this experiment R_e. There is no loss of the primary report; no corrupted symbol is mistaken for a valid report. The two receivers have the same observation contract. e=1 returns the original incomparable channels.

The two problems are different:
- Known rate: maximize e for which SOME R satisfies E x R_e >= F x R_e in the Blackwell order.
- Uniform interval: maximize rho for which ONE R satisfies that comparison at every e in [0,rho]. Each comparison concerns optimal Bayesian decisions; the receiver knows the conditional experiment. State-blind erasure does not change the posterior given the flagged/retained report.

Results (proved below): known-rate maximum 14/39 = 35.8974%; uniform-interval maximum 10973/78500 = 13.9783%. Both are global over arbitrary finite strictly positive side experiments, not only geometric-grid side experiments. Moreover one optimal known-rate instrument qualifies ONLY at e=14/39; reducing its erasures also destroys the comparison. This is not a claim that less information increases either individual instrument's optimal reward.

## Reduction to a lattice

For finite binary channels define H(z)=sum_y(E+_y-z E-_y)_+ - sum_y(F+_y-z F-_y)_+. This is a piecewise linear function. Blackwell dominance holds exactly when H>=0 everywhere: at a prior p=1/(1+z) the classification-accuracy difference is p H(z), and the hinge functions plus affine terms generate the finite piecewise-linear convex decision envelopes. Equivalently use the Blackwell posterior convex-order characterization (source below).

Direct substitution yields knots z=(2/7,4/7,8/7,16/7,32/7), values (0,1,-3/2,1,0)*2/21. H vanishes outside those knots. Write q=2, lambda=4/7, and a=3/2. The same reduction holds for any q>1 and any primary hinge piecewise linear with knots on lambda*q^k and zero outside its finite knot interval.

For side likelihood L=R+/R- and plus probability w, its contribution to the compound hinge is w H(z/L). Suppose q^j <= L <= q^(j+1). Split that plus mass between adjacent lattice ratios q^j and q^(j+1) using weights w*alpha and w*(1-alpha), where

    alpha = (1/L - q^(-j-1))/(q^(-j)-q^(-j-1)).

The total minus mass is unchanged, because the inverse likelihood is interpolated exactly. Thus both state rows remain normalized and nonnegative; discard zero mass outputs. This is an actual refinement: retaining the original symbol labels and forgetting which split occurred recovers R. At each original lattice test z=lambda*q^k, H(z/L) is exactly its linear interpolation between H(z/q^j) and H(z/q^(j+1)). Thus all original grid receipts remain exactly equal. The rounded compound has all its knots on the grid, so if the original compound qualifies, the rounded one qualifies. This is only a one-way implication, not a generic preservation result for more informative side channels. The rounding fixes a neutral ratio and is linear in the side masses, hence commutes with any state-blind flagged erasure. It therefore works simultaneously for every e.

For q=2, let c_j be the plus probability at ratio 2^j of the FINAL (erasure-included) side channel. The minus probability is 2^(-j)c_j. Finite support, c>=0, sum c=1 and sum 2^(-j)c_j=1 are required. Then

    (Dc)_j = c_(j-1) - (3/2)c_j + c_(j+1)
    H_compound(lambda*2^(j+1)) = (2/21)(Dc)_j.

The condition is Dc>=0 at every integer j. An e-erasure side channel exists exactly when c_0>=e: subtract e at index zero and divide all remaining plus/minus masses by 1-e to obtain the underlying channel. For a fixed interval, c is the final side at rho; the two endpoint conditions Dc>=0 and D(c-rho*delta_0)>=0 suffice by affinity of the compound hinge in e. No interior rate checks are required for a proof.

This gives finite linear programs if the permissible ratio range is [q^-B,q^B]. Even with arbitrary off-grid ratios inside this range, rounding cannot leave the range. The finite LP optimum is therefore exact for the original unrestricted-within-box problem. Without any bound on the ratios the global upper certificates below apply to every finite support, eliminating any extrapolation from a truncated LP.

## Known rate: sharp optimum

Feasible final side channel c:
    
| j | -1 | 0 | 1 | 2 |
|---|---:|---:|---:|---:|
| Plus counts /39 | 9 | 14 | 12 | 4 |
| Minus counts /39 | 18 | 14 | 6 | 1 |

Each row sums to one; Dc>=0 (direct exact arithmetic). e=14/39 takes all the neutral mass as erasure. The underlying R has plus row (9,12,4)/25 and minus row (18,6,1)/25; ratios 1/2,2,4.

Global dual proof: put g_0=22/39, g_1=8/39, g_j=0 elsewhere. Let l=2/13 and m=8/39. Pointwise for every integer j,

    indicator(j=0) <= l + m*2^(-j) - (Dg)_j.

Check j=-1,0,1,2 directly; outside those indices Dg=0 and both l,m positive. Multiplying by c_j and summing, using D symmetric under finite sums and g>=0, Dc>=0, gives c_0 <= l+m=14/39. Since any off-grid qualifying channel rounds to such a c without losing the erasure mass, the bound is global. Every rate from 0 through 14/39 is feasible if one is allowed to redesign the underlying R by subtracting the desired neutral mass from the same final c. This does NOT mean the same R works at all those rates.

For the displayed optimal R, at any e=t the constraints at j=1 and 0 require respectively

    (Dc)_1 = (39t-14)/25 >= 0
    (Dc)_0 = (42-117t)/50 >= 0.

Both hold only at t=14/39. At t=0 the hinge difference at z=16/7 is -4/75 (classification accuracy difference -28/1725 at prior 7/23). Therefore erasure genuinely enables the comparison. At t>14/39 it fails again. R_e is strictly less informative than R, since R_e is a nontrivial state-blind erasure and R informative. This is a direct additional counterexample to the upward-closure sentence after Proposition 4 in the preprint discussed in #698; Proposition 4 itself is not contradicted.

## Uniform interval: sharp optimum

The final side at rho=10973/78500 has plus numerators over 78500:

| j | -3 | -2 | -1 | 0 | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| c_j numerator | 3144 | 4716 | 3930 | 12152 | 14298 | 20268 | 16104 | 3888 |

Its minus numerators are the same times 2^(-j); both rows normalize. Subtract 10973 at j=0, then divide by 67527 to obtain the underlying side's plus row (with minus row scaled by 2^(-j)). In particular the underlying neutral mass is 1179/67527. All entries strictly positive. Dc and D(c-rho*delta_0) are nonnegative. The endpoint proof qualifies every rate in [0,rho]; above rho the j=0 coefficient becomes negative for this R.

The global dual certificate is as follows. Use two nonnegative finite sequences g0,g1 with nonzero entries shown, all others zero.

| j | g0 | g1 |
|---|---:|---:|
| -3 | 3639/39250 | 0 |
| -2 | 449/1570 | 0 |
| -1 | 0 | 3761/7850 |
| 0 | 22509/39250 | 0 |
| 1 | 0 | 4089/7850 |
| 2 | 109/314 | 0 |
| 3 | 5449/39250 | 0 |

Let l=10893/78500, m=4/3925. Direct substitution verifies D(g0+g1)_j <= l + m*2^(-j) for j=-4 through 4; outside D=0 and l,m>0. Also (Dg1)_0=1. For any feasible endpoint pair,

    sum_j c_j D(g0+g1)_j
    = sum_j g0_j (Dc)_j + sum_j g1_j [D(c-rho*delta_0)]_j + rho*(Dg1)_0
    >= rho.

The pointwise bound and two normalization constraints upper bound this same sum by l+m=10973/78500. Equality is attained by the exhibited c. Rounding reduces arbitrary off-grid side channels to feasible lattice candidates at both endpoints, so this is again an all-finite-positive-side optimum. This argument does not rely on floating-point LP dual multipliers: those suggested the rational coefficients, which are checked pointwise exactly.

Numerical finite-box LP search with B=1..12 suggested the certificates. B=1 infeasible, B=2 gives known optimum 14/39 and robust optimum about 0.073276; B=3 gives robust about 0.135686; B>=4 reaches global robust optimum. Finite-box values below global saturation are numerical findings, not separately claimed exact optima. The finite-box experiment computes literal primary hinge values, independently of the convolution recurrence.

## Countercontrols and implications

An off-grid side channel can agree at all original grid receipts and still fail between them. Merge the last two outputs of the known-rate final table, obtaining plus (9,14,16)/39, minus (18,14,7)/39. Its last ratio 16/7 is off-grid. Rounding restores the original table and hence preserves every original grid receipt. But the actual compound hinge is -8/273 at z=128/49. This is a negative control against treating sampled-grid success as a qualification of the original off-grid instrument. The LP theorem concerns existence by controlled refinement, not testing an unmodified arbitrary side.

Information loss is not necessarily detrimental to a *comparative ranking*, though the individual receiver can never improve its optimal value merely by garbling its own evidence. The erasure-enabled comparison may rely on different decisions in the erasure and retained branches. Requiring dominance conditional on every flag would be impossible here for any positive erasure probability, because the erased branch contains only E or F, which are incomparable. The guarantee is on the complete experiment before the flag is observed; it is not a per-erasure-event guarantee.

Interpretation for MHAC: a common contextual audio cue may affect not just the ability to decode a primary report but which of two report vocabularies is preferable. A synthetic Observatory component could accept a primary pair, an admissible likelihood-ratio box and an erasure interval, solve the LP and produce explicit counterexamples at failed priors. Preserve the distinction between known rate, unknown-but-bounded rate and state- or message-dependent dropout; the last violates the model. Physical loss, unflagged corruption, correlated reports, feedback, actual listening performance and temporal cost are not modeled. Direct retention of the full channel table and explicit qualification of the actual operating modes remain simpler baselines.

Synthetic sound: the known-rate final side table is represented as two separate conditional score inventories, 39 50-ms frames each. Carriers 350,550,750,950 Hz correspond to ratios 1/2,1 (erasure),2,4. The flagged erasure is deliberately a *present* distinct symbol, not absence of sound. The state is a file label. No natural meaning, human perceptual equivalence, physical transmission or empirical dropout is asserted. Exact counts and matched-template decoding test digital realization only.

Fiction: the clerk employs a witness whose testimony only settles the dispute when the witness occasionally fails to arrive. He replaces the witness with a perfectly punctual version; the dispute returns. The apprentice writes a new ledger heading: 'Which absence was promised?'

## Sources and qualification

- Mu, Pomatto, Strack & Tamuz, *From Blackwell Dominance in Large Samples to Renyi Divergences and Back Again*, Econometrica 89(1), 475–506, DOI https://doi.org/10.3982/ECTA17548. Caltech record https://authors.library.caltech.edu/records/x70d0-23195 (metadata, abstract, two listed versions inspected); published PDF download redirected and failed. ArXiv v5 https://arxiv.org/pdf/1906.02838, printed pp.4–5 (product experiments and posterior convex order, Eq.1), p.12 (Proposition 4 and following paragraph), Appendix G opening inspected; original page images pp.5 and 12 checked. Prior art: catalytic experiments and convex order. The new exact erasure thresholds and lattice-splitting proof are our scoped derivations, not an exhaustive novelty claim. The post-Proposition-4 passage is still only assessed against the inspected preprint, not journal wording.
- MIT OCW, *Principles of Digital Communication II*, Spring 2005, Lecture 23, transcript excerpt on state-independent flagged erasures: https://mitocw.ups.edu.ec/courses/electrical-engineering-and-computer-science/6-451-principles-of-digital-communication-ii-spring-2005/video-lectures/lecture-23-lattice-and-trellis-codes/ . Retrieved excerpt inspected; full-page opening timed out. Used only as background to the familiar erasure model, not a source for catalytic bounds.
- Internal #703 complete report retrieved on mhac-703/polynomial-witness; issue and empty comments read. #704 head 055e810aae201a9a5b87b9c7d5f4f469728a9001, Actions 45852176171 completed success. #698 is cited as internal ancestry, not newly reviewed in full this run. Main base 495a98ca12bae467a507031f04931aa4254b1866. AGENTS, README, RAG, programme, runbook, research integrity, validation, protocol overview, project foundations read. Nested AGENTS in research and research/expeditions not found. 414 branch entries traversed, 60 recent issue search results and 30 actual open PRs examined (search_issues returned same issue set for is:pr, so used dedicated PR listing); targeted catalyst/erasure search returned no overlap. New #707 read back, zero comments. Fresh branch, no shared manifests. Native git ls-remote failed DNS; full local repository suite not run.
- [laboratory.cjs](laboratory.cjs) executed in V8 code-mode, 6532 exact rational assertions, 1576 literal compound knots, 2448 off-grid rounding knot identities across 144 valid profiles, 39 singleton-rate and 101 robust interval checks. See [execution.json](execution.json). Separate native Python formulation solved 24 numerical LP profiles and verified the literal off-grid failure and endpoint comparisons in exact rational arithmetic, plus decoded 78/78 frames. Same agent, not independent peer review. Conventional probability theory, interpolation and linear programming explain the findings; no additional explanatory contribution from cybersemiotics established. No canonical evidence changes. Independent critique and exact-head repository checks remain required for landing.
