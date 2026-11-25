# The Dictionary That Survives Its Errors
## Noisy balanced-target optimality, peak vocabulary and minimum entropy

**Refs #454 · 25 November 2026 · mathematics and synthetic computation.** One ChatGPT GPT-6.2 agent; self-reviewed, not independently reviewed. No human observations, operational security assertion, accepted empirical finding or scholarly priority claim.

## Contents

1. Excavation — separate the error contract from the alphabet contract.
2. Model — define the same observable channel for utility and privacy.
3. Noisy minimax theorem — solve heterogeneous per-intervention budgets.
4. Alphabet rigidity — prove that every positive recovery advantage retains the exact dictionary cost.
5. Entropy frontier — calculate the sharp mean description-cost relaxation.
6. Exaptation — preserve disagreements and specify a falsifiable rendering contract.
7. Reproduction — record actual tests and acceptance boundaries.

## 1. Excavation

The actual draft [#403, The Receipt That Forgives a Collision](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/274f018579df3904366e596b4ba39398d30db598/research/expeditions/receipt-forgives-collision/README.md), §§2–5, allowed a separate conditional Bayes error budget on every pair-collapse edge, but optimized full-original guessing. [#427, The Receipt That Cannot Fit Its Dictionary](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/5158863f7f9b0d881a320c7678008bc04afbfa57/research/expeditions/receipt-cannot-fit-dictionary/README.md), §§2–5, instead required exact recovery and optimized the worst fixed balanced Boolean question, finding exponential alphabet cost. [#435, The Dictionary That Hides Its Missing Pages](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/dfdcdf848996c4ca0a7702f73881f62145c0eb30/research/expeditions/dictionary-missing-pages/README.md), Exact syndrome theorem and Instability sections, perturbed the privacy objective but retained exact recovery. None resolves the opposite perturbation: relax recovery and demand exact privacy optimality for that new utility contract.

The result is asymmetric. Relaxing the exact privacy score (as in #427/#435) can sharply reduce dictionary size. Relaxing recovery alone cannot reduce the minimum exact-optimal dictionary size at all, until all recovery advantage disappears. It CAN reduce minimum label entropy. These are different engineering resources.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866, refreshed before creating mhac-454/noisy-dictionary. Read AGENTS, RAG, programme, runbook, integrity, validation, foundations, accepted [X004 Quotient Guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md), and the three actual draft reports. First 100 returned open issue titles and first 100 open PR titles surveyed (not repository totals); targeted noisy dictionary issue/PR and branch searches returned no match. #434 scope and empty comments inspected; #435 exact-head Actions run 45526501547 completed successfully, not scientific validation. Created and read #454 scope and empty comments before branching. Draft predecessors are not accepted research findings.

## 2. Model (mathematics)

There are m groups, each with two equiprobable originals (i,+) and (i,-), N=2m. Take even m>=2 for the rigidity and entropy results. The encoder emits a finite random label J, before learning which pair-collapse action will occur. Action i identifies the two originals in group i and leaves all other originals unchanged. The authorized decoder observes the action, result and J; the external observer sees J alone. Actions do not depend on the original. No shared key or side channel. Use arbitrary finite stochastic channels, not only symmetric channels.

For positive-probability label j, write w_i(j)=P(i,+|j)+P(i,-|j), d_i(j)=P(i,+|j)-P(i,-|j), and p_j=P(J=j). Then sum_i w_i=1, |d_i|<=w_i, E w_i=1/m and E d_i=0. Define T_i=m E|d_i|. Direct binary Bayes decoding conditional on the actual collision in action i gives error (1-T_i)/2. This follows by summing min of the two joint endpoint/label probabilities and normalizing by 1/m. Outside the collapsed pair the decoder can recover with no error. The conditional error is a balanced average over the two colliding originals, not a worst-original guarantee.

Require conditional error <= eps_i in [0,1/2] separately for each action, and put t_i=1-2eps_i, a_i=t_i/m. Utility is exactly the constraint E|d_i|>=a_i. The adversary chooses one fixed balanced +/-1 target f on the 2m originals, observes J, and guesses its value. Its Bayes guessing probability is (1+E|E[f(X)|J]|)/2. Write V for the maximum over such f. This is a worst fixed target, not a target selected after observing J, and not whole-secret guessing. The target-specific objective is an instance of the established gain-function framework: Alvim, Chatzikokolakis, Palamidessi & Smith (2012), *Measuring Information Leakage Using Generalized Gain Functions*, DOI [10.1109/CSF.2012.26](https://doi.org/10.1109/CSF.2012.26), publisher abstract, §§III and III.C displayed text inspected 2026-11-25. We do not claim originality for Bayes vulnerability or gain functions.

## 3. Exact heterogeneous noisy minimax (mathematics)

For any nonnegative vector a define R(a)=2^(-m) sum over sign vectors z of |sum_i a_i z_i|.

**Theorem 1.** The exact minimum V under the utility contract is

    V*(eps_1,...,eps_m) = (1+R(a))/2.

Proof of lower bound: a group-balanced target chooses opposite signs within every pair, and thus is indexed by t in {-1,+1}^m. Averaging its posterior absolute bias over uniform independent t gives R(|d(j)|). Therefore 2V-1 >= E R(|d|) >= R(E|d|) >= R(a). The middle step is Jensen (R is convex). The last uses coordinate monotonicity on nonnegative inputs: conditioning on all signs except one replaces the average |B+c| and |B-c| by max(|B|,c), nondecreasing in c>=0.

Attainment: choose a uniform sign label z from the full cube, with posterior w_i=1/m, d_i=a_i z_i. Equivalently emit z given original (i,s) with probability 2^(-m)(1+s t_i z_i). These rows normalize, reproduce uniform prior, and exhaust every error budget. Every group-balanced target has absolute bias R(a). Any other globally balanced target has equally many all-plus and all-minus constant groups, so their contributions cancel pointwise because w_i is uniform. The remaining mixed groups give a partial independent signed sum; its expected absolute value cannot exceed R(a) by Jensen after adding the omitted zero-mean independent signs. Hence the upper bound is attained for the entire target family.

For equal eps, let t=1-2eps and c_m=binom(m,m/2)/2^m (even m). Then R(a)=t c_m, since E|sum of m independent fair signs|=m c_m (by summing binomial differences, or the two-coordinate identity below). Consequently

    V*(eps) = 1/2 + t c_m/2.

At eps=0 this recovers #427's score. At eps=1/2 a constant label attains chance guessing and chance recovery on every collapsed pair.

**Unequal allocations matter.** For fixed mean t_bar, R(t_i/m)>=t_bar c_m, strictly unless all t_i equal when m is even. To see strictness, average a over all permutations; the pointwise Jensen gaps for every sign vector are nonnegative. For a balanced sign vector, the signed sum of the permutation average is zero. Equality requires all permuted signed sums to vanish, hence every half-subset has identical mass; exchanging coordinates forces equality. This also covers zero coordinates. Thus an application imposing an unequal vector of error caps has a strictly higher optimum adversary score than an equal-cap contract of the same average.

Example, m=4:

| Conditional error caps | Mean cap | Best worst-target guessing |
| --- | ---: | ---: |
| (1/4,1/4,1/4,1/4) | 25% | 59.375% |
| (0,1/2,0,1/2) | 25% | 62.5% |
| (1/8,3/8,1/8,3/8) | 25% | 60.9375% |

The mean-only contract is weaker than an individual vector. Its optimal score equals the equal-cap optimum: average error constraint gives E sum |d|>=t_bar, so permutation convexity gives the lower bound and equal-cap witness attains it. A candidate accepted only under a mean cap need not honor the individual requirements. Neither optimum is an empirical listener error rate.

## 4. Exact alphabet rigidity at every positive recovery advantage (mathematics)

**Theorem 2.** For equal eps<1/2, the minimum number K of positive-probability observable labels attaining Theorem 1 is

    K = 2^(m-1), for even m>=4;
    K = 4, for m=2.

At eps=1/2 the minimum drops to one.

Necessity: equality in the previous lower bound requires E sum_i |d_i|=t and, by the strict permutation lemma applied pointwise, |d_i(j)|=b_j independent of i for each positive posterior. This follows from E R(|d|)>=c_m E sum_i |d_i|>=c_m t, and every gap is nonnegative. For b_j>0 define z_j by d_i(j)=b_j z_ji. Set beta_j=m p_j b_j. These effective contrast masses sum to t, are nonnegative, and beta_j<=p_j because m b_j<=sum_i w_i(j)=1. Zero-contrast labels do not contribute.

Since the average over group-balanced targets equals their maximum at optimality, every group-balanced target has that same score. With g(z)=|sum_i z_i|, this says sum_j beta_j g(u*z_j) is constant in u. On the binary cube, multiply this equality by product of u_i over a nonempty even subset S, then average. Substituting v=u*z_j yields the product of the Fourier coefficient ghat(S) and sum_j beta_j product of z_ji over S, equal to zero.

For S of size 2k, choose two coordinates of S and condition on the sum T of the remaining m-2 signs. The two-sign weighted average equals (|T+2|+|T-2|-2|T|)/4=1[T=0]. Conditional on T=0, the remaining signs are equally divided. The expected product of 2k-2 selected remaining signs is the coefficient of x^(2k-2) in (1-x^2)^((m-2)/2), divided by binom(m-2,2k-2), by permutation symmetry. Hence

    ghat(S)=c_(m-2) (-1)^(k-1) binom((m-2)/2,k-1)/binom(m-2,2k-2),

with c_0=1. It is nonzero. Odd coefficients vanish by global reversal. Fourier inversion (orthogonality of the cube characters) therefore forces the antipodally symmetrized effective contrast law to be uniform. Each antipodal pair must carry contrast mass t/2^(m-1)>0, so each needs at least one label. For m=2, E d_i=0 also forces the first moments of beta to vanish, and the second moment is zero from the audit. Inverting all four characters gives beta=t/4 on each of four sign vectors.

Sufficiency: for m>=4 retain just the sign vectors z satisfying z_1 z_2 z_3=+1, one per antipodal pair. Their uniform distribution has each coordinate unbiased (flip a constrained coordinate along with another constrained one; other coordinates can be flipped alone). For m=2 retain all four. Set beta_j=t/K and initially p_j=1/K; w_i=1/m and d_i=(t/m)z_ji. Then the prior is uniform and each conditional recovery error exactly eps. Every even function of z has the same mean as under the full cube. In particular all group-balanced targets attain the exact score; partial mixed-group sums for other balanced targets have no greater mean, just as in Theorem 1. Thus the lower bound is attained.

This proof does not require w_i to be uniform in every optimal channel; the necessity concerns the contrast d_i, not all posterior masses. The result holds for arbitrary finite stochastic channels and all real t in (0,1], however small. It does not assert the same lower bound for a nonzero tolerance on privacy optimality, for unbalanced targets, or for heterogeneous eps_i. This is a count of actually used observable labels, not dictionary storage complexity.

## 5. The sharp minimum entropy (mathematics)

Peak alphabet cost survives, but the label distribution can become highly skewed. Let K be as above, and define

    p_* = 1-t+t/K,
    H_min = -p_* log2(p_*) -(K-1)(t/K) log2(t/K).

**Theorem 3.** Among all channels attaining the equal-cap noisy optimum with t>0, the minimum Shannon entropy H(J) is exactly H_min. It is attained with K labels.

Lower bound: every required antipodal class (or each signed class for m=2) contains effective contrast mass t/K, so actual label mass in each class is at least t/K. Zero-contrast labels may be outside the classes. Any s<K labels can cover at most s classes; outside those labels at least (K-s)t/K mass must remain. Thus the sum of the s largest probabilities is at most 1-(K-s)t/K. For s>=K the bound is one. The vector (p_*,t/K,...,t/K,0,...) majorizes every feasible probability vector after padding with zeros. Shannon entropy is concave and symmetric, so majorization gives the lower bound (equivalently, transfers from a larger mass to a smaller one cannot reduce -sum p log p).

Witness: use Theorem 2's balanced orientation set, keep beta_j=t/K, but assign p_1=p_* and p_j=t/K for all other labels. Set w_i(j)=1/m and d_i(j)=beta_j z_ji/(m p_j). Since beta_j<=p_j, these are valid posterior distributions; their mixture is the uniform prior because the weighted sign mean is zero. The conditional channel is

    P(J=j | i,s)=p_j+s beta_j z_ji.

All rows sum to one, and the preceding recovery and target calculations depend on beta, not p separately. Constant-group contributions cancel with uniform w_i. All privacy and utility equalities therefore survive. The common label is less informative; the rare labels have deterministic pair recovery when they occur. No extra erasure label is necessary. For t=1 the law is uniform; for t tending to zero at fixed m, H_min tends to zero while the peak vocabulary stays fixed until t=0, where the constant channel becomes admissible.

For m=32, K=2^31. At 51% conditional authorized accuracy, t=.02, log2 K=31 bits, H_min approximately .76144 bits. At 75% accuracy, t=.5, H_min approximately 16.5 bits. At 100% accuracy, H_min=31 bits. These are marginal label entropy and log cardinality, not actual per-message physical lengths; entropy is an ideal asymptotic lossless description benchmark. An implementation with a strict single-token alphabet cap cannot infer feasibility from H_min alone. Serialization, coding delay, shared models, physical waveform faults and channel memory require separate contracts.

## 6. Exaptation and objections (interpretation / design hypothesis)

The accepted X004 deterministic quotient audit asks whether a declared decision is constant on a fibre. Here errors are deliberately allowed and the decision contract is statistical; its exact factorization cannot be silently reused. The earlier #403 optimizes a different target family and supplies a useful warning about worst versus mean action error, not this alphabet theorem. #435's instability result concerns a positive tolerance on the objective and cannot rescue exact attainment here.

A candidate auditory rendering qualification should report separately: (1) per-intervention conditional error and the prior used; (2) worst-target privacy score AND permissible optimization tolerance; (3) number of distinguishable observable labels; (4) marginal entropy and worst-case serialized duration; (5) errors induced by the actual acoustic observation rather than by the abstract label channel. A noisy waveform rendered after a receipt is a garbling of that channel; the same listener/observer model must be applied to its actual outputs. A small average description cost does not imply a small one-shot perceptual vocabulary. Conversely, if an application is content with approximate privacy optimality, it need not pay for exact rigidity. There is no blanket recommendation to maximize dictionary size or to accept recovery error.

Potential synthetic experiment: compare the concentrated witness with the uniform-probability witness at identical conditional recovery and balanced-target scores. Introduce explicit symbol confusions or a fixed alphabet cap, and evaluate the resulting channel end-to-end. The expected result is a testable computational prediction, not a claim that humans recognize either dictionary or prefer one. Human testing needs the existing gates; no actual listeners or waveform measurements are included.

Fictional miniature: a printer agrees to let the archivist be wrong almost half the time. The printer keeps the rare pages and makes the first page carry almost every visit. The dictionary has not become smaller; it has become less frequently opened. Only when the archivist accepts pure guessing can the printer remove the last rare page.

## 7. Reproduction and status

Run node lab.js in this directory (dependency-free). The executable tests actual integer-valued conditional channel rows, actual pair-collapse decoder fibres, and every balanced Boolean target on the small instances, rather than assuming the extremal Fourier formula. The laboratory also enumerates all denominator-two row laws with 2 and 3 labels for m=2, checking that feasible channels cannot attain the .625 optimum on that grid (best .75); this is a finite countercontrol, not the arbitrary-real lower-bound proof. Additional strict-equality tests enumerate integer contrast vectors, and prefix-sum tests enumerate class-mass vectors. The latter are combinatorial sanity checks, not exhaustive arbitrary-channel entropy optimization.

Development execution in the V8 tool environment passed: 16 constructive witnesses, 23,492 balanced-target evaluations, 1,875,014 target-label cells, 34,464 decoder cells, 4,368 contrast vectors, 266,304 sign sums, 1,377 small candidate channels (936 feasible), and 168 integer majorization vectors. Counts overlap; none is a human trial or an independent experiment. Native Node checkout and full repository validation not run. No central manifests, frozen protocol, canonical research records or other workers' branches changed. Draft/HOLD with Refs #454; no claim of closure or independent acceptance.

Revision criteria: a heterogeneous channel beating R(a), a positive-t exact optimum with fewer than K labels, an exact optimum with lower label entropy than the stated vector, or a direct finite decoder/target mismatch would require correction. No claim about approximate-optimal alphabet minima, heterogeneous rigidity, empirical auditory utility, or priority relative to the full information-theory literature.
