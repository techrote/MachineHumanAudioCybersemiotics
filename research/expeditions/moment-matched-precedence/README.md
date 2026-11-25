# The Bell That Beats Its Own Ranking

**Date:** 2026-11-25. **Issue:** #610. **Base:** 495a98ca12bae467a507031f04931aa4254b1866.
**Status:** exploratory mathematical proofs and synthetic computational witnesses, pending independent critique. No Track E/G admission, human data, hearing claims, novelty priority, or canonical registry changes. AI-assisted single-agent derivation and checking.

## Question and observation contract

An instrument renders a random scalar amplitude index for each sign. Compare two independent draws, awarding half a win to a tie. Write W(p,q)=Pr(X>Y)+Pr(X=Y)/2. This is stochastic precedence, not an ordering of means, actual loudness, semantic urgency, or a causal claim. Every comparison uses the same distributions and no context mixture. Can moment qualification prevent a strict cycle A>B>C>A? Exactly how many common amplitude levels suffice to defeat any finite moment audit?

The distinct scope was selected after reviewing live main, instructions, 365 branch entries, 100 open issue and 100 open PR results, targeted searches, and issues #228, #554 and #240. #228 concerns scalar compression of given comparisons; #554 concerns context-mixture reversal; #240 already covers reversible Markov aggregation and was deliberately not duplicated. Prior #605 exact-head repository-integrity returned success. This investigation occupies only the new expedition directory.

## Sharp common-alphabet theorem

**Theorem.** For each integer k>=1, the smallest possible common alphabet size allowing three independent scalar laws with identical first k raw moments and strict cyclic tie-half precedence is k+3. The lower bound holds for arbitrary distinct real alphabet levels. The upper bound holds on consecutive integer levels; it even matches the moments of their uniform distribution. The common alphabet counts the union of allowable levels, not the number of positive masses in each law.

Let n be the alphabet size and K be the n by n matrix K[i,j]=sign(i-j), where the real levels are in ascending order. Then 2W(p,q)-1=p^T K q. K is skew-symmetric. Equality of moments through k, including the zeroth normalization, constrains p to an affine space of dimension max(0,n-k-1), by the Vandermonde rank. If n<=k+2, this dimension is at most one. In dimension zero all laws coincide. In dimension one every law can be written p0+t u. The comparison becomes (t_j-t_i) p0^T K u, because u^T K u=0. It either vanishes or orders all the t values monotonically, so no strict cycle of any length exists.

For the upper bound set d=k+1, n=d+2. Define u_i=(-1)^i binom(d,i) for i=0,...,d and u_(d+1)=0, and v_i=u_(i-1), taking out-of-range values to be zero. Each annihilates polynomials of degree <=k by the d-th finite difference identity (or differentiate (1-z)^d at z=1 and express powers via falling factorials). Let p0 be uniform. Since K times the all-ones vector has coordinates 2i-(n-1), both u and v have zero pairing with p0. This is where k>=1 is used.

The antisymmetric pairing is nonzero with a closed form:
u^T K v = sum_(i,j) u_i u_j sign(i-j-1)
= -sum_i u_i^2 - sum_i u_i u_(i-1)
= -binom(2d,d)+binom(2d,d-1)
= -Catalan(d).
The first equality uses the shifted support; subtract the zero form u^T K u. The sign changes only for i-j=0 or 1. The binomial sums follow from Vandermonde convolution.

Choose a positive epsilon sufficiently small that the following are nonnegative:
A=p0+epsilon v, B=p0+epsilon u, C=p0-epsilon(u+v).
They are normalized, match all k moments, and each directed edge A>B, B>C, C>A has
W=1/2+epsilon^2 Catalan(d)/2.
This is an exact balanced cycle, not a claimed optimum winning margin. Choosing epsilon=1/(n M), with M=max(-min u,-min v,max(u+v)), gives the explicit integer count vectors used in the laboratory. Increase M for strictly positive mass on every level.

**Concrete example k=3:** levels 0,...,5, counts per law 24:
| Level | A | B | C |
|---:|---:|---:|---:|
| 0 | 4 | 5 | 3 |
| 1 | 5 | 0 | 7 |
| 2 | 0 | 10 | 2 |
| 3 | 10 | 0 | 2 |
| 4 | 0 | 5 | 7 |
| 5 | 5 | 4 | 3 |

Every edge has W=295/576 (about 51.2153%). The first three raw moments are those of the discrete uniform law: 5/2, 55/6, 75/2. A common positive affine transformation (including shifting to amplitudes 1,...,6) preserves moment equality and precedence. The construction can have small margins; finite-sample detection may require many trials.

## Arbitrary relational dictionaries

**Theorem.** For t>=2 alternatives and k>=1, every prescribed tournament on t vertices can be realized by independent scalar laws sharing their first k raw moments, with equal absolute tie-half winning margins, on (t-1)(k+3) consecutive levels. More generally any rational skew comparison matrix is realizable up to a common positive scaling around 1/2.

Partition the alphabet into t-1 consecutive blocks, each of length k+3. In block b (b=0,...,t-2), put perturbation v in law b, s[b,i] u in law i>b, and zero in earlier laws, where s[b,i]=+1 if b is to beat i, otherwise -1. Add each concatenated perturbation times epsilon to the shared uniform law. Every block has zero moments through k even after translation (binomial expansion). Cross-block skew pairings vanish: all indices in one block precede those in the other and each perturbation has zero mass. The shared uniform base pairs to zero by zeroth and first moment matching. For i<j the only nonzero term is block i, where v^T K (s[i,j] u)=s[i,j] Catalan(d); earlier blocks pair multiples of u with u, later ones include zero. This proves the equal-margin claim and the weighted extension by replacing signs with desired rational coefficients and shrinking epsilon to preserve nonnegativity. The bound on alphabet size is sufficient, not claimed optimal for t>3.

This is a constructive mathematical separation of absolute statistics and relational comparisons. A finite moment receipt can certify all alternatives alike while an arbitrarily complex directed comparison relation persists underneath.

## Averaging changes the question

Taking r independent draws from each law and comparing their averages preserves equality of the first k moments: expand the power of the sum by the multinomial theorem; independence factors every monomial into matching moments. Yet W may change its sign, even when every moment in the audit remains equal.

For the k=3 example the signed count differences for A>B, B>C, C>A after one draw are (14,14,14), with W-1/2 equal to those numbers divided by 1152. For two draws they are (-2626,-378,-378) divided by 663552. Thus the entire cycle reverses; after three draws the signs are (+,-,-), which is transitive. At five draws all are negative again. These are exact convolution counts, not asymptotic extrapolation. The 120-profile census in execution.json records all signs for k=1..10 and r=1..12. No conjecture about eventual orientation is established.

**Tie-free extension.** Add independent identically distributed continuous jitter supported on (-eta,eta) with eta<1/2 to each integer observation. Differences of distinct levels preserve sign, while equal-level draws resolve symmetrically with probability 1/2. Moments still match by binomial expansion. Thus the single-draw phenomenon does not depend on explicit tie rules. For a fixed finite maximum r, eta<1/(2r) also preserves sum comparisons at every horizon through r. This is a sufficient condition, not a claim about arbitrary noise or unlimited averaging.

**Negative controls.** On n<=k+1 levels the moment vector determines the entire law. On n=k+2 levels a hidden degree of freedom remains but cannot produce a strict cycle. Equality of all moments on a common compact interval also forces equality in law by polynomial approximation of continuous functions, unlike every finite audit. This is not first-order stochastic dominance: dominance would give a consistent ordering of increasing expected utilities. Replacing W by E[g(X)]-E[g(Y)] for a fixed g produces transitive comparisons by definition, but changes the operational question. Dependence between X and Y invalidates the independent-product comparison formula.

## Reproduction and exact checks

Run:

    node research/expeditions/moment-matched-precedence/laboratory.cjs

Compare stdout with execution.json. The script uses exact BigInt count arithmetic, literal double sums as a separate check of cumulative comparisons, binomial coefficients, literal convolutions, and finite composition enumeration. Actual executed results:

- 32 moment-matched balanced cycle profiles (k=1..32).
- 120 repeated-aggregation profiles (k=1..10, r=1..12); moment identities and three literal pair comparisons each.
- 3,294 labelled tournament constructions (every orientation on 2..5 vertices for k=1..3), 31,950 exact directed-pair margin checks.
- 5,976 small-alphabet count profiles, 5,891 moment fibres, 37 distinct triple checks; both equally spaced and nonuniform levels; all forbidden strict cycles absent.
- Zero assertion failures. These finite checks corroborate but do not replace the analytic proofs.

A separately executed native Python witness used Fraction comparisons, direct convolution via count maps and literal enumeration of all 24-by-24 and 576-by-576 face pairs for the k=3 one- and two-draw witnesses. 128 profiles and 487 counted checks completed. Three original 1.92-second mono PCM16 banks use the same integer tapered 400 Hz pulse, amplitudes 1..6 and 24 slots per bank. Each has exactly 192330120164 squared integer PCM sample units. They are sonifications of count vectors, not human stimuli qualification. Native execution JSON and all audio bytes reproduced on a second run. Native files are local supplemental artifacts, not committed in this PR. Native full repository checkout failed with DNS resolution for github.com; full repository test suite not locally run. Same-agent computational checks are not independent peer review.

## Source ledger and contrary constraints

- Injo Hur and Yeansu Kim (2021), *Possible Probability and Irreducibility of Balanced Nontransitive Dice*, [doi:10.1155/2021/6648248](https://doi.org/10.1155/2021/6648248). Publisher HTML, abstract, introduction, definitions 1–4 and remark 1 read. They investigate balanced cycles for disjoint sets of equally likely die faces, unlike the shared amplitude alphabet here. Their winning-margin conjecture is not used or claimed resolved.
- A. N. Yakusheva (2026), *Nontransitive Dice with Equal Means and Variances*, Doklady Mathematics 113, 111–119, [doi:10.1134/S1064562426700134](https://doi.org/10.1134/S1064562426700134), published 20 October 2026. Publisher metadata and abstract read; full paper subscription-only and not inspected. Direct prior overlap: equal mean/variance nontransitivity and effect of one versus two tosses. This is important contrary novelty evidence. No claim that our general-k threshold or construction is absent from the literature.
- Sah and Sawhney (2023 preprint), [The intransitive dice kernel](https://arxiv.org/abs/2302.11293). Abstract read; HTML retrieval failed. Its skew-operator treatment is mathematical ancestry, not a source for the specific finite-difference theorem. No result from its unread proof is used.
- Buhler, Graham and Hales (2018), *Maximally Nontransitive Dice*, American Mathematical Monthly 125, 387–399, [JSTOR](https://www.jstor.org/stable/48663319). Abstract read: changing the number of rolls can realize different comparison outcomes. This precludes claiming discovery of aggregation-dependent ranking in general.

No full literature priority audit. All theorem statements above follow from displayed derivations, not from presumed source endorsement. AI agent performed this reading and verification; no human validation. No reproduced third-party source bytes or licensing decisions.

## Interpretation, design hypothesis, fiction

A scalar instantaneous observable need not induce a scalar ranking of its distributions. An auditory vocabulary designer may equalize mean amplitude, RMS energy and even several higher moments without equalizing paired precedence. A receiving system that takes one exemplar versus an average of two might reverse a comparison without violating any of those audit receipts.

Design hypothesis: for an application whose decision actually uses paired stochastic comparisons, qualify the full pairwise comparison matrix and explicitly bind its sampling horizon, tie policy, gain, dependence and task to the receipt. Compare against direct expected-cost ranking, deterministic codes and full distributional comparisons. Falsifier: if the target action uses expected utility or calibrated deterministic features rather than pairwise wins, the cycle may be operationally irrelevant. Equal digital energy is not equal perceptual loudness; no acoustic semantic or user benefit established. Conventional stochastic precedence explains the effect without requiring cybersemiotic theory.

Speculative instrument: three banks of equal-energy pulses, a dial for the number of independent draws per comparison, and a three-edge score voice displaying the resultant win direction. The count kernel and offline audio bank exist; the live instrument and listener evaluation do not.

Fiction: the clerk checks the bells' averages, then their variations, then their skew. They agree. The apprentice pairs them and finds a circle. She asks each bell to ring twice. The circle reverses. The clerk had calibrated each bell, not the contest.
