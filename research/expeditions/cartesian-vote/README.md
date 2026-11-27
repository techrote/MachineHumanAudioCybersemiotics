# The Chord That Recovers Its Vote

Refs #763, #759, #754 · 27 November 2026 · Exploratory mathematical DSP. One ChatGPT agent derived the results, inspected the source, implemented and checked both laboratories. No independent peer review, participant evidence, physical transmission or scientific-priority claim.

## Question and result

The complete #759 report leaves open whether unit-weight least absolute deviations (LAD) reaches the Hamming-distance limit on a complete Cartesian period of three or more coprime voices. Its arbitrary-index counterexample does not decide this question. The answer here is affirmative for *every* number of pairwise coprime periods. The proof does not use two-part graph cuts. Instead it converts the observation geometry into a biased Bernoulli product via conditional expectation, symmetrizes under permutations and solves a one-dimensional convex optimization. An independent-coordinate binary product supplies a contrasting strict failure even on a complete grid.

## Sharp concentration theorem

Let a real additive function on the full product of m finite coordinate sets of sizes p_i>=2 be

    h(x)=b+sum_i f_i(x_i).

Write P=product p_i, M=max p_i and d=P/M. All norms below are unnormalized sums unless marked as expectations. If

    2(1-1/M)^(m-1) >= 1,                         (1)

then

    ||h||_1 >= d ||h||_infinity.                   (2)

This is sharp: take the indicator of one residue in a largest coordinate, which is an admissible additive signal including the intercept. No restrictions on amplitude, relative signs or private shape are required.

Proof. Choose a maximum-absolute-value cell x*, divide by h(x*) (unless h=0, trivial), and henceforth h(x*)=1. Let X have independent uniform coordinates. Introduce independent Bernoulli variables Y_i with success probability 1/M. Couple each pair independently as follows: conditional on Y_i=1, X_i=x_i*; conditional on Y_i=0, give the target residue probability (1/p_i-1/M)/(1-1/M) and every other residue probability (1/p_i)/(1-1/M). These nonnegative probabilities sum to one; marginal X_i remains uniform.

By conditional Jensen,

    E|h(X)| >= E|E[h(X)|Y]|.

Because h is additive, the conditional expectation is an affine function of the binary variables, with value 1 at the all-success cell. Average this affine function over all coordinate permutations. The law of Y is exchangeable, so another application of Jensen cannot increase its expected absolute value. The resulting function has form 1-a J for some real a, with J the number of failed Bernoulli coordinates, distributed Binomial(m,1-1/M). It suffices to lower-bound

    F(a)=E|1-a J|.

F is convex and piecewise linear. At a=1/m its left derivative is -E[J], and its right derivative is 2m Pr(J=m)-E[J]. Since E[J]=m(1-1/M), the right derivative is nonnegative precisely under (1). Thus a=1/m is a minimizer and F(1/m)=1/M. Multiplying by P and restoring the original scaling proves (2).

Every set of pairwise coprime integers p_i>=2 satisfies (1). Among integers 2 through M, at most one even value can occur and there are floor((M-1)/2) odd values; hence m<=floor((M+1)/2). Bernoulli's inequality gives (1-1/M)^(m-1)>=1-(m-1)/M>1/2. For one component the same theorem is immediate. Coprimality is sufficient, not necessary: the theorem is for full Cartesian observations with arbitrary factor sizes satisfying (1). For coprime periods, CRT realizes exactly this product through one consecutive full period starting at any integer tick.

## Consequences: decoder optimality, sharp concentration and weights

By #759's full-grid distance proof, d is also the exact minimum Hamming weight of a nonzero additive signal. In fact (2) alone establishes the lower bound and the slice indicator attains it. For any set F of e cells, ||h_F||_1 <= e||h||_infinity. Consequently the largest possible fraction of total absolute amplitude carried by e cells is exactly min(e/d,1). Upper bound follows from (2); a largest-coordinate slice attains equality by selecting cells within its support.

Let E be a flagged erasure set of size f, F a disjoint arbitrary-error set of size e and G the remaining cells. Then

    ||h_G||_1 - ||h_F||_1 >= (d-f-2e)||h||_infinity.    (3)

For received data equal to the true signal on G, the triangle inequality shows that every alternative with difference h has strictly greater LAD cost if 2e+f<d. The bound is uniform in error magnitudes and actual locations. At or above that boundary the slice witness can be split between two competing admissible signals after erasures, so no decoder can universally do better. This answers the previous open question: unweighted LAD, paired-contrast medians and information-theoretic decoding attain the same threshold on the full coprime Cartesian grid, despite their divergence on #759's incomplete schedule.

If good samples contain additional perturbations eta, the LAD cost difference is bounded below by the right side of (3) minus 2 sum_G |eta|. Hence every minimizer satisfies

    ||h||_infinity <= 2 sum_G |eta|/(d-f-2e).

This is a bound on the *complete predicted waveform*, including erased cells, not just observed residuals. A private contrast is a difference of two full-grid predictions and has error at most twice this bound. No probabilistic assumptions are used; the bound can be conservative for diffuse small noise.

The arbitrary-confidence extension is also sharp as a worst-case weight-range contract. Suppose every surviving weight is between w_min>0 and w_max=R w_min. The weighted good-minus-bad amplitude difference is at least

    w_min [d-f-(1+R)e] ||h||_infinity.

Thus d>f+(1+R)e suffices for universal recovery across all allowed weight assignments. For a sharp converse, use the slice indicator with f erasures and e false samples inside its support (up to the support size), assigning maximum weights to false cells and minimum weights to the remaining good cells. At equality the two candidate costs tie; below zero the false candidate is preferred. If erasures remove the entire support, identifiability already fails. This is a worst-case guarantee over weights, not a necessary condition for an individual fixed weight schedule. A weighted version of the stability bound replaces the numerator by twice the sum of weighted good perturbations and denominator by w_min[d-f-(1+R)e].

Example (3,5,7): P=105, d=15; seven errors or fourteen erasures are sharp. At e=5, f=2, strict robustness to arbitrary confidence assignment holds iff R<1.6. Unweighted observations have a margin of 3 in (3). Example (5,7,11,13,17): P=85085, d=5005; at most 2502 arbitrary errors on a complete period. These are synthetic model budgets, not physical error-rate estimates.

## Negative sediment: equal alphabets can lose the vote even on a full grid

The Bernoulli reduction is exact when all coordinate sizes equal M: take each coordinate's target indicator, use the symmetric affine function 1-a J, and attain the lower bound min_a F(a) itself. Thus the smallest possible unnormalized L1 mass among additive functions with value 1 at a fixed cell is

    P * min_{k=1,...,m} [ sum_{j=0}^m C(m,j)(M-1)^j |k-j| / (k M^m) ].

The breakpoints a=1/k suffice, since convex F is piecewise linear, decreases at a=0 and grows for sufficiently large a. The minimum equals d precisely when (1) holds. If (1) fails, the right derivative at 1/m is negative; a strict smaller norm is attained. This identifies the exact boundary of the sharp point-evaluation inequality for equal-level full products, not necessarily the exact LAD threshold in every failing profile.

| Levels M | Components m | P | d | Minimum mass at unit cell |
|---:|---:|---:|---:|---:|
| 2 | 3 | 8 | 4 | 3 |
| 2 | 6 | 64 | 32 | 20 |
| 3 | 3 | 27 | 9 | 8 |
| 4 | 4 | 256 | 64 | 54 |
| 5 | 4 | 625 | 125 | 125 |
| 7 | 4 | 2401 | 343 | 343 |

Failure of the pointwise bound by itself does not imply failure of LAD below half distance; a separate witness is needed. Take six independent binary coordinates, h(x)=3-sum_i x_i. Its absolute value inventory is:

| Absolute value | Number of cells |
|---:|---:|
| 3 | 2 |
| 2 | 12 |
| 1 | 30 |
| 0 | 20 |

Total absolute mass 60. Corrupt truth zero to h on the two extreme cells, all twelve magnitude-two cells and one magnitude-one cell, leaving every other cell at zero. This uses 15 errors, fewer than half the exact distance 32. The true signal costs 31; the competing admissible signal costs 29. Native LP attains 29. The full grid is identifiable and uniquely sparse-error correctable, yet unit-weight LAD fails.

This is an independently addressable six-coordinate Cartesian grid, not six copies of a period-two oscillator sampled on a single clock. Those six oscillator residue coordinates would be perfectly dependent, not Cartesian. Do not transfer this negative result to a coprime cyclic acquisition or confuse an independent multichannel address with a single time index.

## Computational witness and source ledger

Replay `node laboratory.cjs` for the dependency-free exact tests. BigInt evaluates 930 binomial profiles (271 satisfying the sufficient coprime dimension bound), 6561 exhaustive ternary anchored-coefficient assignments on the (2,3,5) grid, 328 seeded integer profiles across six coprime grids, six sharp slice witnesses and the binary strict-failure witness. Committed source retrieved and executed in V8; output exactly matches execution.json. The full-grid tests are finite cross-checks, not the general proof. Committed source blob 108142af57e1c7bbbf103e6111fbd3073bbbf42a and receipt 072c647fdc185af9ede8fb6b338b96245af206fa.

Replay `python native.py` for the separately formulated sparse linear programs. Nine actual full-grid LP minima (not the binomial reduction) and 60 deterministic corruption/erasure recovery trials; maximum parameter error rounded to 1e-9, all within 1e-6 tolerance. The 64-cell binary witness gives actual optimum 29. Native Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0; two runs produced byte-identical receipts. Committed source blob 2a7bd712aeefa34ce7dda68bbabfb413bc9185f1 and receipt 1a334ae0e0cbd2263bb2e2e244f1ebdb0fb29be1 match the locally executed files. These are same-agent different formulations, not independent review.

Primary literature: E. Candès and T. Tao, *Decoding by Linear Programming*, IEEE Transactions on Information Theory 51(12), 4203–4215 (2005), DOI 10.1109/TIT.2005.858979. Public publisher-author record https://authors.library.caltech.edu/records/pxr5b-3zf41 and preprint v1 https://arxiv.org/pdf/math/0502327. Read abstract, §§1.1–1.3, equations (1.1)–(1.6), inspected original printed page 4 (PDF index 3). The general relation between sparse-error correction, annihilation and convex absolute-residual minimization is established prior art. The particular product thinning, symmetrization, sharp concentration and binary counterexample are present derivations; scientific priority unassessed. Search for exact related affine biased product inequalities did not produce a decisive primary source in this bounded pass. This is not a novelty audit.

Repository: main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, README, RAG, programme, runbook, integrity and validation inspected. Nested research/AGENTS and research/expeditions/AGENTS absent. Paginated branch search returned 444 entries at inspection, 30 recent issue and 30 recent PR results inspected; targeted searches for Cartesian LAD and periodic concentration. Full predecessor #759 report, issue, comments and PR #760 inspected; exact-head workflow 45936113445 succeeded. Fresh #763 issue body and comments inspected, isolated branch based on main. Native git ls-remote blocked by DNS, so no full native repository validation claimed. Draft/HOLD for critique and integrator as stipulated by #763; no canonical records or other workers' branches changed.

## Interpretation and design hypothesis

The acoustic model reveals an unexpected relationship between combinatorial diversity and decoder reliability. Adding more components does not necessarily defeat convex decoding: with coprime periods the number of independent coordinates remains small relative to the largest alphabet and the entire Cartesian grid prevents excessive amplitude concentration. By contrast, repeated small alphabets can admit concentrated extreme values even though every combination has been sampled. This is an algebraic result, not a theory of human testimony.

An Observatory receiver should distinguish full-grid completeness, period independence, sharp concentration, weighted confidence and actual sample faults. A playable comparison can switch between the 105-cell coprime case, the incomplete #759 schedule and the six-binary independent address case. The existing median decoder remains attractive for low complexity; the LAD result supplies a cross-check and a stable optimization alternative, not a reason to replace it. Actual streaming latency, partial-period optimal schedules, physical acoustic transmission and human use remain unqualified. Conventional probability, convex analysis and coding theory suffice for all demonstrated results; no incremental explanatory value of cybersemiotics has been established.

Fiction: the clerk restores every missing page of his ledger. His apprentice notices that the votes now become reliable, not because the witnesses are more truthful, but because the possible combinations have finally been represented. In a second ledger with six binary witnesses, even complete representation does not rescue the vote. She keeps both ledgers.
