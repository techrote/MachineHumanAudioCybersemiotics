# The Witness That Needs a Polynomial

Refs #703 · 26 November 2026 · additive mathematical excursion, not canonical Track E/G evidence. One ChatGPT agent: source reading, proof development, exact JavaScript and Python computations. Independent critique outstanding. No human or physical acoustic measurements.

## Abstract

The previous expedition #698 asked what happens when two communication systems receive the same independent supplementary evidence. Here we characterize *existence* of a finite strictly positive catalyst for binary experiments whose likelihood ratios lie on a shared geometric grid. A polynomial of signed Bayes-hinge discrepancies must be strictly positive on the positive real axis. This criterion is necessary even for finite off-grid side evidence, and sufficient using a repeated fixed binary side channel. For a quadratic family we determine the exact minimum on-grid alphabet and log-likelihood span, and compare that custom-designed side alphabet with repeated binary evidence: the respective costs diverge as inverse square root and inverse first power of a margin parameter. This is an application of established positive-polynomial mathematics, not a priority claim about Pólya's theorem or the quadratic degree bound.

## The observation contract and the polynomial

An experiment E consists of two finite positive conditional probability rows e_+(i), e_-(i), each summing to one. One persistent binary state is shared by all instruments. Define

    H(z) = sum_i (e_+(i) - z e_-(i))_+
         - sum_j (f_+(j) - z f_-(j))_+, z>0.

The likelihood ratio is e_+/e_-. At prior 1/(1+z) the optimal state-classification accuracy difference is H(z)/(1+z). The binary Blackwell criterion is H(z)>=0 everywhere (see #694 and #698; equivalently convex order of likelihood-ratio laws under the minus state). Both H tails vanish because the conditional rows sum to one. H is continuous and piecewise linear in z, with knots among the likelihood ratios of E,F.

Assume all ratios in both instruments belong to {lambda q^k : k integer}, q>1, lambda>0. Set h_k=H(lambda q^k). If all h_k vanish the instruments are equivalent; this is a separate trivial case. Otherwise translate the index so that the first nonzero h is h_0 and the last h_d. Absorb the translation into lambda. Define P(x)=sum_(k=0)^d h_k x^k.

A side experiment R has likelihood ratios s q^j, with weights w_j=Pr(R=j | +). Merge outputs with identical ratios and translate so the first index is zero. For any positive coefficients c_j (zero coefficients simply mean absent symbols), let

    w_j = c_j / sum c_j,
    s = sum_j w_j q^(-j),
    Pr(R=j | -) = w_j q^(-j) / s.

This normalizes both rows; the side likelihood ratio is indeed s q^j. Every finite common-grid side can be represented this way. Write C(x)=sum c_j x^j.

By conditional independence, the compound hinge is

    H_R(z) = sum_j w_j H(z/(s q^j)).

All its knots are on the shifted grid lambda s q^k. At those knots it equals the coefficient of x^k in P*C divided by sum c_j. Since it is linear between knots and zero outside, we have an exact equivalence:

    E x R dominates F x R  iff  every coefficient of P*C is nonnegative.

A candidate catalyst therefore has a finite exact certificate. The common observation does not have to be intrinsically more informative than both primary instruments. Its *shape* matters. The criterion is for dominance when both sides retain the SAME side experiment, not just simulation of an old, weaker target.

## Existence, including a nonlattice impossibility theorem

**Theorem.** For nonzero H on the declared grid, a finite strictly positive common-side experiment exists (even allowing arbitrary off-grid likelihood ratios) iff P(x)>0 for every real x>0. Whenever one exists, a finite common-grid catalyst exists. In fact, repeated independent reads of a single fixed binary side suffice.

Sufficiency: if P is positive on (0,infinity), its first and last coefficients are positive by the trimming convention. The homogeneous form p(u,v)=sum h_k u^k v^(d-k) is positive on the closed standard one-simplex (including endpoints). Pólya's theorem gives N such that (u+v)^N p has positive coefficients. Thus C=(1+x)^N works. The fixed two-output side has plus row [1/2,1/2] and minus row [q/(q+1),1/(q+1)]; its two likelihood ratios have spacing factor q. After N iid reads the sufficient count statistic has plus weights binomial(N,j)/2^N and shifted grid ratios, so C is precisely its multiplier. Pólya here is a classical theorem; Powers–Reznick supply an explicit sufficient exponent, discussed below.

Necessity beyond the grid: let phi(z) be the piecewise linear hat with knots q^-1,1,q and values 0,1,0, zero elsewhere. By interpolation,

    H(z) = sum_k h_k phi(z/(lambda q^k)).

For real t, set J(t)=integral_0^infty phi(z) z^(t-1) dz, finite and strictly positive. A change of variable gives the Mellin identity

    integral H(z) z^(t-1) dz = J(t) lambda^t P(q^t).

For ANY finite positive side R with likelihood ratios L_j and plus weights w_j, the integral of H_R equals this expression times sum_j w_j L_j^t, a strictly positive factor. If P has a negative value at x>0, choose t=log_q x; a nonnegative H_R is impossible. If P has a positive-real zero, the integral vanishes at its corresponding t. A continuous nonnegative H_R must then vanish everywhere. But P is nonzero, hence at some other real t the integral is nonzero, a contradiction. This proves strict positivity is necessary even for off-grid finite positive catalysts. Uninformative H=0 is separately equivalent, and perfect revelation (zero conditional probabilities) is outside the assumptions: it makes the two compound experiments equivalent regardless of P.

This is a geometric-grid specialization of the broad catalytic comparison problem from Mu et al., not a replacement for their general theory. It gives a concrete polynomial compiler and removes a genericity assumption within this restricted grid class by direct proof. In particular a root exactly on the positive axis is a genuine obstruction, not a numerical near-failure.

**Quantitative established bound.** With d=degree P, lambda_min=min_(0<=t<=1) p(t,1-t)>0, L=max_k |h_k|/binom(d,k), Powers–Reznick Theorem 1 gives strict coefficient positivity for N>d(d-1)L/(2 lambda_min)-d (take N>=0; degrees 0,1 are immediate). This is a sufficient repeated-read bound, not generally the minimum alphabet or exponent. We use their theorem rather than presenting it as ours. Our executable exact quadratic recurrence avoids numerical positivity testing.

## A quadratic family and exact costs

Choose P_a(x)=1-a x+x², 0<a<2. There are positive real zeros at a>=2, so there is no finite positive catalyst there. For 0<a<2 define theta=acos(a/2), in (0,pi/2), and m=ceil(pi/theta)-2.

**Sharp lattice span and alphabet.** Every on-grid successful catalyst must have index span at least m and at least m+1 distinct likelihood ratios. Both bounds are attained by

    c_j = sin((j+1)theta)/sin(theta), j=0,...,m.

Proof of span: the polynomial product P_a C has nonnegative coefficients and vanishes at exp(i theta). If its degree D satisfies D theta<pi, the vectors exp(ik theta), 0<=k<=D, lie in an open half-plane through zero after a rotation. Their nonnegative combination cannot vanish. Thus deg C>=ceil(pi/theta)-2. The quadratic minimum degree has established antecedents (Dancs; Motzkin–Strauss; Kepka–Korbelar Theorem 2.2).

Proof of construction: c_-1=0,c_0=1,c_(j+1)=a c_j-c_(j-1). The coefficients through c_m are positive, and the next c_(m+1)<=0. Then P_a C has coefficients 1 at zero, 0 at indices 1..m, -c_(m+1) at m+1, and c_m at m+2. They are all nonnegative.

Proof of alphabet lower bound: for any candidate c with c_0>0, coefficient nonnegativity requires c_1>=a c_0 and c_j>=a c_(j-1)-c_(j-2) (treat missing coefficients as zero). Compare successive ratios to those of the positive sine recurrence b. Inductively c_j/c_(j-1)>=b_j/b_(j-1)>0 for 1<=j<=m, because a-1/r is increasing in positive r. Hence every one of the first m+1 coefficients must be positive, even if gaps are allowed later. No smaller alphabet can work. The constructed polynomial therefore minimizes both distinct ratio count and span for this fixed q grid. It does not minimize entropy, human learning burden, or acquisition cost under every possible side-instrument model.

**Exact repeated binary read budget.** Fix the binary side from the existence proof; after N reads C=(1+x)^N. Write delta=2-a and D=N+2. The coefficient of x^k in P_a C, divided by binom(D,k), is

    1 - (a+2) k(D-k)/(D(D-1)).

The minimum occurs at the central integer(s). For even D the condition is delta D>=4; for odd D it is delta(D+1)>=4. The smallest D>=2 satisfying either is 2 ceil(2/delta)-1, so

    N_min = 2 ceil(2/delta)-3.

This is the weak nonnegativity version needed for Blackwell dominance; Powers–Reznick p.2 already discuss the corresponding strict positivity problem for this same quadratic. The polynomial product can have zero coefficients and still certify dominance. Further reads preserve the certificate by multiplication by 1+x.

As delta tends to zero, theta~sqrt(delta), so the custom distinct alphabet size m+1~pi/sqrt(delta), whereas the repeated binary side needs N~4/delta independent reads and N+1 distinct count receipts. These are different resource contracts, not a comparison of two identical physical hardware costs.

| a | Minimal lattice alphabet | Minimum fixed binary reads |
| --- | ---: | ---: |
| 1 | 2 | 1 |
| 6/5 | 3 | 3 |
| 3/2 | 4 | 5 |
| 8/5 | 4 | 7 |
| 9/5 | 6 | 17 |
| 19/10 | 9 | 37 |
| 39/20 | 14 | 77 |

**Off-grid lower bound, not a sharp classification.** For a finite arbitrary side with K distinct ratios, take samples of H_R on a geometric grid aligned with one of those ratios. The hat representation above expresses the sampled sequence as P_a times an effective nonnegative polynomial (up to positive normalization and a monomial translation). Each side ratio contributes the samples of a shifted hat to this multiplier: at most two consecutive nonzero entries, or exactly one for an aligned ratio. Therefore the multiplier has at most 2K-1 nonzero coefficients, but must have at least m+1. Thus K>=ceil((m+2)/2). If the grid aligns the smallest side ratio, all effective indices lie between 0 and ceil(W) where W=log_q(L_max/L_min); the span result gives ceil(W)>=m, hence W>m-1. The exact off-grid minimal alphabet/span remain open. We do not equate an off-grid lower bound with a fixed-grid optimum.

## Realizing the polynomial as actual positive channels

A sign pattern alone is not automatically a legal probability channel. Construct the piecewise linear H_raw at knots (1/4,1/2,1,2,4) with values (0,1,-a,1,0), zero outside. Its slope jumps are

    [4, -(6+2a), 3(a+1), -(a+3/2), 1/2].

They sum to zero and their first moments sum to zero. Positive and negative parts have common mass M0=15/2+3a and common weighted mass M1=6+3a. Normalize the positive and negative slopes by M0 to obtain the two minus rows; multiply by their respective raw knots and normalize by M1 to obtain the plus rows. Both probability rows in each instrument sum to one. The resulting likelihood ratios equal raw knots multiplied by M0/M1, so the actual hinge is H_raw(z M1/M0)/M1. This constructs legal channels for all positive a, including the forbidden a>=2 controls. Every output probability is strictly positive.

For a=3/2, the exact rows (plus,minus) are

    E: [2/21, 5/7, 4/21]; [1/3, 5/8, 1/24].
    F: [3/7, 4/7];       [3/4, 1/4].
    R: [8/33,12/33,10/33,3/33]; [64/135,48/135,20/135,3/135].

E and F are incomparable because the hinge has both signs. The side multiplier is [1,3/2,5/4,3/8], and its product with [1,-3/2,1] is [1,0,0,0,11/16,3/8]. Hence E x R dominates F x R for every Bayesian decision, not merely fair-prior classification. The compound experiment has zero hinge at several knots but is not equivalent; the positive coefficients survive. Dropping the last side coefficient (and renormalizing correctly) fails. A five-read fixed binary side works, whereas four reads fail. The exact laboratory confirms both, across hundreds of rational a values.

## Synthetic acoustic specimens and negative sediment

The native script renders the two conditional rows of R at a=3/2 as separate deterministic shuffled PCM16 mono files, at 8 kHz, 400 samples/frame. Tones at 300,500,700,900 Hz encode four side outcomes; conditional counts are [8,12,10,3] (33 frames, 1.65 s) and [64,48,20,3] (135 frames, 6.75 s). All 168 frames are matched-template decoded from actual PCM. The state labels are file-level, not audible truth channels. These are conditional inventories of the *side* experiment, not full compound inventories or sampled physical channels. Unequal file length reflects minimal exact row denominators, not an empirical state prior. Files regenerate with the script; the repository does not commit WAV binaries.

A prospective instrument could let a performer move through positive, nearly singular and impossible polynomial margin regimes, then switch between a tailored side alphabet and a fixed repeated-read policy. It would sonify the cost of making evidence comparable. A receiver must actually know and use the conditional joint experiment; arbitrary pitch assignments have no universal semantic meaning. This is a design hypothesis, not empirical guidance. A simpler baseline is a direct decision-specific qualification with no extra observations, or direct garbling checks when the full channels are known.

Negative findings: finite positive side evidence cannot fix the zero margin P(1)=0 at a=2, even off-grid. A perfect-revelation limit is not the same contract. Repeating an already drawn symbol is not iid and cannot realize the binomial multiplier. Discarding the entire side receipt returns the original incomparable primary channels. Strictly more informative side evidence is not a monotone certificate (see #698). Exact dominance says nothing about finite listener effort, temporal cost, estimation error or physical decode reliability. Conventional probability, interpolation and polynomial algebra explain the result; no additional explanatory contribution from cybersemiotics is established.

Fiction: a clerk keeps adding honest witnesses to two contradictory ledgers. The apprentice stops counting witnesses and begins arranging the distribution of their testimony. At the critical margin, no finite arrangement can settle the discrepancy.

## Sources, qualification and disposition

- Mu, Pomatto, Strack & Tamuz, *From Blackwell Dominance in Large Samples to Rényi Divergences and Back Again*, Econometrica 89(1), 475–506 (2021), DOI https://doi.org/10.3982/ECTA17548. Publisher metadata and abstract inspected; arXiv v5 https://arxiv.org/pdf/1906.02838 printed pp.4–5 (product experiment, posterior criterion) and p.12 (Proposition 4 and surrounding catalyst passage) inspected, including images of pp.5 and 12. Their catalyst-existence result is prior art; #698 recorded a distinct issue with the post-Proposition-4 sentence, not a rejection of the theorem.
- Victoria Powers and Bruce Reznick, *A new bound for Pólya's Theorem with applications to polynomials positive on polyhedra*, J. Pure Appl. Algebra 164(1–2), 221–229 (2001), DOI https://doi.org/10.1016/S0022-4049(00)00155-9. Author-hosted manuscript https://reznick.web.illinois.edu/11200.pdf dated 12 January 2000: printed pp.1–3, Theorem 1, quadratic example and coefficient derivation (1)–(4); page images pp.1–2 inspected. Their bound and quadratic antecedent are explicitly credited.
- Tomas Kepka and Miroslav Korbelar, *The lowest-degree polynomials with non-negative coefficients*, arXiv:1210.6868 (2012), https://arxiv.org/abs/1210.6868 and author archive https://archive.math.muni.cz/project/ecc/ECC_papers/Korbelar_Nonlinear_new.pdf ; abstract and pp.1–3, Theorems 1.2 and 2.2, p.3 image inspected. The quadratic degree result and positive-multiple theorem are established; Dancs, Motzkin–Strauss and Harnos cited there, not separately read. Our grid-to-channel reduction, Mellin obstruction and explicit resource interpretation are scoped derivations; no exhaustive novelty or erratum search.
- Internal ancestry: complete #698 report and issue, empty comments; #694 report through bounded decision theorem inspected. #699 exact head f936d795db6e79592b3854848da3e49af357d080, Actions run 45843555482 success. Both are draft research, not accepted empirical evidence.
- Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, README, RAG, programme, runbook, integrity, validation, protocol overview and foundations read. 412 branch entries and 60 recent open issues and PRs each reconciled; targeted searches for catalyst polynomial and Bernstein. New #703 read back with empty comments. No other branch or shared manifest changed.
- Execute node laboratory.cjs and python witness.py from this directory. The exact JS implementation was executed twice from retrieved committed source under a V8 CommonJS assertion adapter (not native Node); 399 rational profiles, 2,910 exact convolution/hinge knot equalities, 414 negative controls and 798 exact binomial endpoint checks. Receipt reproduced byte-for-byte. The native Python 3.13.5 script independently uses closed-form channel rows and literal products of the primary and sufficient side tables: 323 profiles, 10,932 distinct-knot visits, 646 negative controls and 168 decoded audio frames. It ran twice with identical receipt and WAV hashes; committed Python and receipt blobs match local Git hashes. These are different methods by the same agent, not independent peer review. See [laboratory.cjs](laboratory.cjs), [execution.json](execution.json), [witness.py](witness.py), [native-execution.json](native-execution.json).
- Native repository access failed at git ls-remote with DNS resolution error; full local suite not run. Exact final-head CI and independent critique must be assessed separately. Draft scoped contribution for designated integrator; no canonical evidence or release status changed.
