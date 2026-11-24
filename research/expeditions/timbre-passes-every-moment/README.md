# The Timbre That Passes Every Moment

Exploratory mathematical and artistic research · 2026-11-24 · Refs #356

**Finding:** Any fixed finite list of spectral power moments can fail almost completely to identify the power above a specified frequency boundary. A true exclusion band around that boundary changes the problem substantially. On a symmetric support, the worst-case ambiguity of the hard threshold is unchanged by adding an even moment after an odd one.

This is an exploration of the geometry of lossy descriptors, not a claim about the performance of any listener, an auditory safety standard, or a new general moment theorem. The title means passing every moment in a chosen finite list, not equality of the entire infinite moment sequence.

## Contents

1. [Scope and provenance](#1-scope-provenance-and-reconciliation) — repository isolation and research status.
2. [Formal model](#2-formal-model-and-why-the-boundary-matters) — exact moment observations and minimax ambiguity.
3. [Constructive obstruction](#3-exact-constructive-obstruction-and-finite-grid-certificate) — rational witnesses, finite-grid optima and duality.
4. [Exclusion band](#4-a-true-exclusion-band-and-the-surprising-parity-plateau) — sharp low-order results and general repair bound.
5. [Experiments](#5-executed-computational-experiments) — exact census and independent numerical LP comparison.
6. [Acoustic witness](#6-original-acoustic-witness-and-synthesis-idea) — original PCM and the Boundary Organ concept.
7. [Cross-domain bridge](#7-intellectual-cross-domain-bridge-contrary-cases-and-sources) — implications, negative cases and source ledger.

## 1. Scope, provenance and reconciliation

- Base: main at 495a98ca12bae467a507031f04931aa4254b1866.
- Fresh branch mhac-356/timbre-passes-every-moment; scope is entirely this new expedition directory.
- Reconciliation inspected live AGENTS.md, README.md, RAG.md, docs/PROGRAMME.md, docs/AGENT_RUNBOOK.md, the integrity and validation guidance, the returned branch inventory (237 names), and the returned open issue/PR search pages (100 each, capped; not exhaustive). Existing #199 and its expedition README were read as adjacent sediment. Its homometric rhythms have identical whole power spectra; the present investigation concerns distinct power spectra with identical selected summaries. Searches for spectral moment, band energy and moment matching did not identify an already-owned equivalent package in the returned issue results. Previous expedition #349 was confirmed to have successful CI at its recorded head.
- No canonical manifest or programme-state edits, no shared worker branch changes. No implementation of operational MHAC policy is authorized or implied.
- Authoring, proofs, two computational implementations and self-review by the same AI agent. The two implementations are independent calculation paths, not independent reviewers. No human validation, priority claim, preregistration or peer review.

## 2. Formal model and why the boundary matters

Let x be a normalized frequency offset relative to a chosen threshold, with allowed support X within [-1,1]. A spectrum is a probability measure P on X obtained by normalizing nonnegative spectral *power* to unit total. We observe m_j(P)=integral x^j dP(x) for j=0,...,k, and wish to recover B(P)=P(x>0).

Define D_k(X) as the supremum of |B(P)-B(Q)| over equal-moment pairs. An affine change of frequency units preserves moment equality through order k. The result therefore also applies to raw physical-frequency moments of the corresponding orders. For nonzero variance it implies equality of the corresponding power-weighted central moments and standardized moments. It does not imply equality of magnitude-weighted descriptors, spectral envelope, harmonicity, phase, perception or every MFCC. Equal total physical power can be imposed independently of the normalization.

If P and Q have the same observed vector but different B, any deterministic estimate at that vector must err by at least half their gap in one world. In fact the optimal worst-case absolute error over all possible moment vectors is exactly D_k(X)/2: choose the midpoint of the infimum and supremum of B among compatible measures at each vector. This remains an infimum/supremum statement when an extremum is not attained. Randomization cannot improve worst-case expected absolute loss, since |z-a|+|z-b| >= |a-b| pointwise.

The mathematical difficulty is the jump in the function h(x)=1{x>0}. Low polynomial moments constrain smooth weighted averages, but that discontinuity can conceal a large transfer of mass across a very small distance. This is an exact identifiability issue, not a failure of a particular regression model.

## 3. Exact constructive obstruction and finite-grid certificate

For distinct nodes x_0,...,x_(k+1), let w_i=1/product_(j!=i)(x_i-x_j). Lagrange interpolation of x^r at these k+2 nodes, followed by comparing coefficients of x^(k+1), gives

    sum_i w_i x_i^r = 0   (0 <= r <= k)
    sum_i w_i x_i^(k+1) = 1.

Thus w has both positive and negative entries, with common absolute mass Z=sum_{w_i>0} w_i. Put P_i=max(w_i,0)/Z and Q_i=max(-w_i,0)/Z. These are probability measures with disjoint supports and equal moments through k, but unequal next moments. Their threshold gap is exactly

    |sum_{x_i>0} w_i| / Z.

For sorted nodes the signs of w alternate. For rational nodes the construction uses only rational operations. The code clears denominators and checks each signed moment exactly using BigInt; it checks the next moment is nonzero as a negative control.

**Near-complete ambiguity without an exclusion band.** Take two adjacent nodes -epsilon,+epsilon and k other fixed distinct nonzero nodes separated from 0, all within [-1,1]. As epsilon tends to zero, the two central weights have opposite signs and grow like reciprocal epsilon, with asymptotically equal magnitudes. All other weights stay bounded. Therefore one normalized measure concentrates at -epsilon and the other at +epsilon, and the gap tends to 1. This establishes D_k([-1,1])=1 for every finite k. For k>=1 a gap of exactly 1 is impossible: probability one above 0 gives strictly positive mean; probability zero above 0 gives nonpositive mean. The supremum is not a maximum. This is not a contradiction of compact-support moment determinacy for the *infinite* sequence.

**Exact finite-grid optimum.** For a finite grid X of n distinct points with n>=k+2, the largest possible gap is the maximum of the displayed rational expression over all (k+2)-element subsets. For n<=k+1, the moment system is injective by Vandermonde rank and the gap is zero.

Proof: differences d=P-Q are exactly the vectors with vanishing moments through k and l1 norm <=2. Conversely, normalize the positive and negative parts to equal masses <=1 and add the same nonnegative remainder to each to form P,Q. Maximize the linear functional h·d on this compact polytope (absolute value is redundant by sign symmetry). If the optimum is positive, an optimal extreme point is nonzero and has norm 2, since otherwise scaling gives a larger value. At a point with more than k+2 nonzero coordinates there exists a nonzero perturbation supported on these coordinates, preserving the k+1 moment constraints and the signed l1 equality. Sufficiently small positive and negative perturbations preserve all signs and feasibility, contradicting extremality. Fewer than k+2 nonzero coordinates cannot satisfy the vanishing moments nontrivially, by Vandermonde rank. On exactly k+2 nodes the nullspace is one-dimensional and spanned by w; scaling to norm 2 gives the constructed pair. The zero-optimum case is trivial.

The same finite-dimensional problem has the dual representation

    D_k(X) = 2 min_{degree(p)<=k} max_{x in X} |h(x)-p(x)|.

Indeed for any such p, h·d=(h-p)·d <=2||h-p||_infinity. Equality follows from finite-dimensional norm duality (distance to the polynomial evaluation subspace, dualized in l1), or linear programming duality. Consequently even an arbitrary nonlinear estimator cannot have a better global worst-case absolute error than the best polynomial estimator on that finite grid. This duality is established mathematics; see Han, Jiao and Weissman below for its analogous continuous formulation with their stated hypotheses. We do not invoke their continuity hypothesis for the discontinuous threshold on an interval.

**Equally spaced minimal grid:** take k+2 nodes equally spaced. The weights are proportional to (-1)^i times binomial(k+1,i), up to global sign. Their positive sum is 2^k in this scaling. The alternating partial-sum identity gives the threshold gap binomial(k,j-1)/2^k when the cut is before node j, 1<=j<=k+1. Its maximum is the central binomial coefficient divided by 2^k, asymptotic to sqrt(2/(pi*k)). This decay is specific to equal spacing on a minimal grid. The clustered-node result explains why extrapolating it to arbitrary grids is invalid.

## 4. A true exclusion band and the surprising parity plateau

Consider X_delta=[-1,-delta] union [delta,1], 0<delta<=1. The boundary has no allowed mass in (-delta,delta). The following bounds concern this mathematical support restriction, not a frequency-discrimination threshold in human hearing.

**Sharp low-order results:**

    D_1 = D_2 = (1-delta)/(1+delta).

For the upper bound use p(x)=1/2+x/(1+delta); its uniform error against h on X_delta is half the displayed expression. For 0<delta<1, the three nodes -1,-delta,+delta give a matching-mean witness attaining the bound (one measure sits at -delta, the other mixes -1 and +delta); delta=1 is immediate. Equality at degree two follows from the more general parity result below.

**Parity plateau.** On any symmetric support excluding 0, D_(2r)=D_(2r-1) for r>=1. If P,Q match through odd degree 2r-1, set P'=(P+R Q)/2 and Q'=(Q+R P)/2, with R reflection x->-x. All even moments of the new pair match automatically, while the odd moment differences are unchanged. Since h(-x)=1-h(x) on the support, the threshold difference is unchanged. Thus adding the next even moment cannot improve the global worst case. It can still improve bounds for particular observed moment vectors; this is a worst-case theorem, not a claim of general redundancy of variance or kurtosis.

**Sharp cubic and quartic result:**

    c = sqrt((1+delta+delta^2)/3)
    s = delta*(1+delta)
    t = 2*c^3
    D_3 = D_4 = (t-s)/(t+s).

For 0<delta<1, delta<c<1. Put b=2/(s+t) and q(x)=b[(1+delta+delta^2)x-x^3]. On the positive interval q has its unique interior maximum at c, and equal endpoint values bs; its value at c is bt. Hence q approximates sign(x) with uniform error E=(t-s)/(t+s) on X_delta (oddness supplies the negative interval). The polynomial p=(1+q)/2 bounds the threshold gap by E.

For attainability take any five consecutive nodes in the ordered list -1,-c,-delta,delta,c,1. The residual h-p equals plus or minus E/2 with alternating signs on those nodes. The signed barycentric weights of Section 3 also alternate, and annihilate the polynomial p; dividing by Z therefore makes the absolute threshold difference exactly E. This supplies a lower bound without any assumption about the existence of a minimax polynomial on a continuum. The parity theorem supplies D_4. At delta=1 the two-point support is determined by its mean and the displayed expression is zero.

**Higher-order constructive repair.** For the largest odd integer m<=k, let p_m(x) be the probability that a Binomial(m,(1+x)/2) random variable exceeds m/2. This is a degree-m polynomial in x. On x>=delta its error is at most the lower tail at (1+delta)/2, by monotonicity (couple Bernoulli trials with uniform random numbers). The reflected negative side has the same bound. Therefore

    D_k(X_delta) <= min(1, 2 sum_{j=0}^{(m-1)/2} binomial(m,j)
                         ((1+delta)/2)^j ((1-delta)/2)^(m-j)).

A simple exponential bound follows by applying Markov's inequality to exp(-u sum Y_i), where Y_i=+1 with probability (1+delta)/2 and -1 otherwise, and choosing exp(2u)=(1+delta)/(1-delta). The result is D_k <= min(1,2(1-delta^2)^(m/2)). At delta=1 use the exact two-point result. This bound is not generally sharp; it is an explicit certificate of convergence when the gap is genuine. For k=0 use D_0=1.

These two cases make a sharp qualitative distinction: increasing a finite number of moments alone cannot yield a uniform nontrivial guarantee on unrestricted support, but it can do so with a fixed positive exclusion band.

## 5. Executed computational experiments

Exact laboratory: laboratory.cjs (standalone Node-compatible code, core executed in JavaScript isolate and re-executed from fetched Git blob). Run from this directory:

    node laboratory.cjs moment-output

It writes a JSON receipt and eight generated WAV files. Native Node filesystem wrapper is not yet qualified here.

- Enumerated 79,932 minimal-support subsets across 8 symmetric integer grids (radius 8, exclusions g=1,...,8) and up to degree 8.
- Checked exact mass, moment cancellation and nonzero next moment for every constructed candidate, all exact subset-count identities, range, monotonicity, parity plateaus, sharp degree-1/2 values, and the binomial majority upper bounds.
- Checked the equally spaced formula for every cut through k=20 (231 cut checks).
- Checked 52 clustered-node examples across k=0,...,12 and M in {10,100,1000,10000}. For this family nodes are -1,+1,M,...,kM, then an implicit rescaling can put them in [-1,1]. The high-order convergence can be slow; at k=12 and M=10000 the gap is about 0.928931, not 1.

Independent calculation path: crosscheck.py, Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0. Run:

    python crosscheck.py crosscheck-output

It solves the original two-probability-vector LP, rather than enumerating signed circuits. All 60 finite-grid profile optima agreed with the exact census (largest absolute numerical difference 1.702e-13). It also checked the cubic formula for 7 exclusion ratios, degree 3 and 4 separately, on a 202-node base discretization augmented by the analytic extrema. All 14 comparisons agreed within 1e-8. This is numerical corroboration, not a replacement for the continuum proof. The exact source's receipt was reproduced byte-for-byte in the isolate; the fetched Python source blob matches the natively executed file. qualification.json records the execution environment, hashes, values and limits. The full native output can be regenerated; the committed qualification is a transcribed subset of that output with direct cross-comparison.

Representative exact finite-grid results (normalized radius 1; delta=g/8):

| g | degrees 1/2 | degrees 3/4 | degrees 5/6 | degrees 7/8 |
|---:|---:|---:|---:|---:|
| 1 | 7/9 | 7/13 | 83/225 | 493/1936 |
| 2 | 3/5 | 27/91 | 463/3025 | 227/2970 |
| 3 | 5/11 | 17/105 | 31/528 | 83/3575 |
| 4 | 1/3 | 3/35 | 71/2997 | 7/1287 |
| 5 | 3/13 | 1/27 | 1/143 | 0 |

As a contrast, for delta=1/2, the exact continuum cubic gap is about 0.0859546244, slightly greater than the discrete-grid value 3/35. A finite enumeration must not be mistaken for a continuum certificate.

## 6. Original acoustic witness and synthesis idea

Use the six physical frequencies 200,600,999,1001,1400,1800 Hz, centered on a declared 1000 Hz boundary. The signed cleared weights in ascending frequency order are

    -53333, 426666, -128000000, 128000000, -426666, 53333

with common mass 128479999. The positive and negative parts give equal first four raw moments and equal zeroth moment. Their ideal power above 1000 Hz is respectively 160267/160801 and 534/160801; the gap is 159733/160801 (approximately 99.336%).

A second witness replaces 999/1001 Hz with 900/1100 Hz. Its signed weights are -5,42,-128,128,-42,5, common mass 175. The above-boundary fractions are 19/25 and 6/25, a 52-percentage-point gap. This is a counterweight to the objection that the nearly complete example merely exploits an arbitrarily narrow division: larger separation diminishes but does not remove the failure of the descriptors.

Render each measure as a one-second sum of sinusoids with amplitudes proportional to square roots of its masses. Frequencies are exact integer DFT bins for a one-second rectangular frame. Orthogonality gives equal unquantized total power and the specified ideal moments. The renderers also create a second pair using only the components above 1000 Hz, with the same gains and no per-file normalization. This is an ideal component-selection demonstration, not a claim about a realizable brick-wall filter with zero latency.

Eight 8 kHz mono 16-bit PCM WAVs were generated in both implementations. No clipping. The near pair's native integer sample-energy sums are 216524487588 and 216524819764, a relative difference of roughly 1.5e-6 due to quantization. Its selected-component renderings have sums 215806422158 and 719018400. The wide pair's full renderings have sums 216521283800 and 216527441800. Quantized waveform spectra are not asserted to preserve the exact rational moments: exact equality is the ideal line-spectrum model; the measured PCM energies are separate finite-precision evidence. Native SHA-256 hashes and JS FNV-1a fingerprints are retained.

**Proposed instrument: The Boundary Organ.** Select a descriptor order, threshold and node set. Two hidden tone banks inhabit a common moment fiber. Move between them by mixing their power vectors (a convex interpolation preserving every retained moment), while converting powers to oscillator amplitudes with square roots. Independently audition the full sound or a threshold-selected stem. A listener may or may not notice timbre or pitch changes; the design makes the hidden power transfer explicit without predicting perception.

The instrument is a composition proposal, not implemented UI. The generated audio pairs are implemented witnesses. Never use them as alarm specifications or human experiments. Playback levels are user-controlled.

## 7. Intellectual cross-domain bridge, contrary cases and sources

**Interpretation:** A descriptor and a decision ask different questions. A moment vector is a compressed account of spectral mass; a threshold decision is a request about an event set. A perfectly accurate account of the former may fail to license the latter. The distinction is not that summary statistics are inherently misleading, but that their adequacy is relative to the question.

This links to empirical distribution assessment: moments of a bounded score can conceal the proportion exceeding a decision threshold, by exactly the same construction. It also suggests a semantics audit for sonification. If a machine declares a state using a compressed telemetry vector, its downstream decisions should be checked for variation over the corresponding admissible fiber; if the action is unstable, request a direct band measurement or express an unresolved interval. This is a design hypothesis, not a validated MHAC policy.

**Contrary cases and sediment:** A known finite support with enough moments is identifiable. A direct threshold statistic resolves this particular target without reconstructing the whole spectrum. Known support gaps and smooth band tapers permit polynomial approximation. A positive gap may be expensive or impossible to ensure physically; finite window leakage and spectral estimation error can destroy exact exclusion. The proof assumes exact spectral moments, and does not establish numerical conditioning, an acoustic recognition threshold, human pitch discrimination or listener equivalence. For a continuous target on a compact support, increasing polynomial order can uniformly reduce the approximation error; the hard discontinuity is essential to the unrestricted worst-case result. The parity plateau says nothing about particular fibers or nonsymmetric domains. The finite-grid oracle scales combinatorially, so use LP or polynomial approximation for larger instances.

**Primary source ledger (access 2026-11-24, selected passages only):**

- Jean-Paul Berrut and Lloyd N. Trefethen, *Barycentric Lagrange Interpolation*, SIAM Review 46(3), 501–517 (2004), DOI [10.1137/S0036144502417715](https://doi.org/10.1137/S0036144502417715). [Author-hosted PDF](https://people.maths.ox.ac.uk/trefethen/barycentric.pdf). Read Section 2, p. 502, especially Eq. (2.1), via text and PDF page image. Source establishes the interpolation expression used to obtain the weights. Moment-nullspace, threshold and synthesis arguments above are derived applications; no priority claim.
- Yanjun Han, Jiantao Jiao, Tsachy Weissman, *Local moment matching: A unified methodology for symmetric functional estimation and distribution estimation under Wasserstein distance*, COLT 2018, PMLR 75. [Proceedings PDF](https://proceedings.mlr.press/v75/han18b/han18b.pdf). Read abstract and Appendix B.1, Lemma 25 / Eq. (24), printed pp. 23–24; visually inspected p. 24. The authors identify an analogous duality for continuous target functions on their specified compact interval. This is established approximation/moment theory, not evidence of novelty of our finite-grid argument. We supply separate reasoning for a discontinuous target and symmetric union of intervals.
- Savvas Kazazis, Philippe Depalle and Stephen McAdams, *Interval and Ratio Scaling of Spectral Audio Descriptors*, Frontiers in Psychology 13, 835401 (2022), [DOI 10.3389/fpsyg.2022.835401](https://doi.org/10.3389/fpsyg.2022.835401), [open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC9007158/). Read abstract and Introduction passages defining centroid, spread and skewness, and the authors' qualification of interpreting physical predictors as perceptual magnitudes. Their stimulus and psychophysical results are not evidence for the present moment-collision pairs. Source motivates distinction between computed descriptor and experience; no claims based on unread methods or results tables.

No source files redistributed. No human or independent review. No mathematical novelty/priority established by this bounded source exploration.

## Fictional afterword — The certificate of brightness

A technician maintained a municipal instrument that announced the brightness of every incoming bell. Its report consisted of four impeccably computed numbers. An apprentice moved a narrow tone from just below the division to just above it, and altered three distant tones in compensation. The report remained unchanged.

The technician demanded a fifth number. The apprentice brought him two different bells.

Eventually the technician drew a small forbidden interval on the instrument's dial. It was the first time his certificate had specified what the world was not allowed to do.
