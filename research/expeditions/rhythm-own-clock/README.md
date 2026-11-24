# The Rhythm That Becomes Its Own Clock

Refs #404 · 2026-11-24 · Exploratory mathematics, synthetic experiment, proposed design and original fiction. AI-authored and self-checked by ChatGPT; no human or independent scientific review, priority claim, empirical listener result, production deployment or accepted Track E/G record.

## Anomaly: expression or distortion?

A four-gap score (1,1,1,1) and a geometric ritardando (1,2,4,8) can arrive as exactly the same gap sequence. The second instrument experiences an index-dependent multiplicative time warp (1,1/2,1/4,1/8), while the first does not. Both are compatible with the same observed rhythm. A tempo-invariant code might legitimately suppress overall tempo; a drift-invariant code also suppresses intended geometric acceleration or deceleration. Its expressive vocabulary must change accordingly.

Reconciliation: main at 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity, validation and project foundations read. 261 branch names paginated; 100 recent open issue and 100 recent open PR search results inspected; targeted tempo/drift, curvature, Chebyshev and rhythm-ratio searches inspected (limited search, not proof of absence). New issue #404 read in full, no comments at creation. Prior #397 exact-head workflow completed successfully. Read the relevant passages of #288 on additive polynomial-baseline cancellation by bipolar pulse blocks, #400 on rigid periodic scheduling and #396 on constant clock-offset uncertainty. #288 is especially close in its use of finite differences, but that work controls a signed probe against additive nuisance; this expedition studies positive duration codewords, nonlinear multiplicative distortion transformed into log coordinates, unknown drift as a quotient, and robust discrimination under errors. #400 addresses fixed-event concurrency, not decoding. No other worker branch or central manifest touched.

## Channel, equivalence and exact distance

Let a nominal word consist of n positive, individually indexed inter-onset intervals d_i, i=0,...,n-1. Use x_i=log(d_i/d_ref) for a fixed positive reference duration. Choose natural logs for numerical examples; another base just rescales all log quantities.

An observed log interval is

    y_i = x_i + q(i) + noise_i,

where q is an arbitrary real polynomial of degree at most p (a nuisance specific to this transmission) and |noise_i| <= eps independently on each correctly received coordinate. p=0 is unknown overall tempo, p=1 permits geometrically varying multiplicative factors across interval indices. This is not a claim that physical clock skew usually has this form. Assume known symbol indices, complete segmentation and no constraint on actual received duration, nuisance slope, or polynomial coefficients. In particular an affine log nuisance is not affine drift of physical timestamps.

For a surviving index set I, define the quotient radius

    E_p(z;I) = min_{q in P_p} max_{i in I} |z_i-q(i)|,

with zero for the empty set. The minimizer exists because the sampled polynomial space is a closed finite-dimensional linear subspace. If I has at most p+1 distinct indices, every vector interpolates and E_p=0.

The observation sets for two words x and x' intersect iff

    E_p(x-x';I) <= 2 eps.

Necessity: subtract compatible observations and bound the difference of their errors by 2 eps. Sufficiency: if z=q+r with |r| <=2 eps, use nuisance 0 and -q (or q and 0 with the appropriate sign) to make the noiseless received difference r, then use errors -r/2 and +r/2 to meet at the midpoint. More explicitly, take x with nuisance 0 and x' with nuisance q; the difference is r. The criterion is exact including the equality boundary. The quotient norm is a metric on the equivalence classes, not on the original scores. For p=0 it is half the range of z; the doubled distance is the logarithmic spread of the ratios, the positive-cone projective metric. No assumption about human perception is used.

## Sparse witness theorem

For a set J of p+2 distinct sample indices define

    w_i(J) = 1 / product_{j in J, j != i}(i-j).

Then

    E_p(z;I) = max_{J subset I, |J|=p+2}
                  |sum_{i in J} w_i(J) z_i| / sum_{i in J}|w_i(J)|.

The empty maximum is zero. Thus a pair of arbitrarily long words is separated by bounded polynomial nuisance precisely when a certificate supported on at most p+2 coordinates exceeds the applicable error threshold.

Proof: by finite LP duality (or normed-space separation), distance to the sampled polynomial subspace equals the maximum of z dot v over sum |v_i| <=1 and sum v_i i^k=0 for k=0,...,p. The dual is feasible and compact; the primal is feasible and has an attained finite optimum. Each nonzero extreme point has support at most p+2: otherwise on its support there is a nonzero direction satisfying the p+1 moment equations and one signed l1 equality. Small positive and negative moves in that direction preserve signs, moments and l1, contradicting extremality. Every nonzero annihilator has support at least p+2 by Vandermonde rank. On p+2 nodes the annihilator is one-dimensional, with the displayed weights, as follows by taking the leading coefficient in the degree-(p+1) Lagrange interpolation formula for monomials of degree at most p. Normalizing l1 and allowing both signs yields the maximum. If the sampled polynomial subspace fills the space, the dual is just zero. This is classical uniform-approximation duality applied to the channel; the sparse contrast formula is not claimed as a new approximation-theory theorem.

For affine drift p=1, a triple i<j<k suffices:

    E_1(z;I) = max_{i<j<k in I}
      |z_j - ((k-j)z_i+(j-i)z_k)/(k-i)| / 2.

A constant or monotonic geometric trend disappears from this statistic, but a change in log curvature does not. The denominator is essential: an adjacent second difference has radius |z_{i+2}-2z_{i+1}+z_i|/4. Testing only adjacent triples is not equivalent to testing every triple.

Independent affine feasibility formulation: a radius R is possible iff the intervals

    [(z_j-z_i-2R)/(j-i), (z_j-z_i+2R)/(j-i)]

over all i<j have nonempty intersection. For a slope in the intersection, the adjusted values z_i-bi have range at most 2R; choose the intercept as their midrange. This proves necessity and sufficiency and provides a direct O(n^2) rational test. The alternative optimization oracle minimizes the adjusted-value range over slopes at pair intersections. The range is convex piecewise linear, coercive for at least two distinct indices, and attains a minimum at a breakpoint or on a flat segment ending there.

## Why local drift tests can hide a global difference

For all n>=3 and every real z with |z_{i+2}-2z_{i+1}+z_i|<=kappa,

    E_1(z;all) <= kappa floor((n-1)^2/4)/4.

The bound is sharp, and is exactly floor((n-1)^2/4) times the maximum allowed adjacent-triple certificate kappa/4.

Proof: restrict to any i<j<k. Subtract the endpoint chord, obtaining h with h_i=h_k=0 and the same second differences. The barrier g_l = kappa(l-i)(k-l)/2 has second difference -kappa. h-g is discrete convex because its second difference is >=0, and with zero endpoints it is <=0. h+g is discrete concave and >=0. Hence |h_j|<=kappa(j-i)(k-j)/2. Divide by two for the triple radius, maximize the product under j-i+k-j<=n-1, obtaining the asserted bound. Equality for the constant-second-difference sequence z_l=kappa l(l-1)/2 at endpoints and a middle index. The finite census confirms both signs and arbitrary bounded integer curvature fixtures, not just that single example.

For n=7, z=(0,0,1,3,6,10,15) has adjacent radius 1/4 but full radius 9/4, witnessed by (0,3,6). For a realistic-scale illustration multiply by any positive factor, e.g. 0.01; the factor nine is unchanged. A diagnostic that declares two scores equivalent merely because every local curvature residual fits independently can therefore give a false certificate. Each local fit was free to use a different nuisance line; the actual channel uses a single nuisance line over the entire word. A growing gap between local and global guarantees is an information issue, not numerical instability of the exact arithmetic.

## Errors, erasures and curvature alphabets

Allow at most t unflagged arbitrary coordinate replacements per received word and at most e flagged erased coordinates, with indices retained. Set m=max(0,n-2t-e). A pair is confusable iff

    min_{I subset all, |I|=m} E_p(x-x';I) <= 2 eps.

Necessity: erase the flagged positions and the union of both worlds' corrupt positions. At least m indices remain; choose any m. Sufficiency: start with a common feasible observation on such an I. Outside I, designate at most e erasures and split the remaining positions into two sets of size at most t each. On the first set use the second world's clean observation; on the second use the first world's clean observation, while the other world uses a permitted replacement. If m=0 and 2t+e>=n, choose only enough errors/erasures to cover n. This argument relies on arbitrary replacements and a common erased-index pattern. It does not cover unmarked pulse deletion that merges two intervals, spurious onsets, insertions, or index errors.

In particular n>=p+2+2t+e is necessary for even two messages to be distinguishable. At eps=0 it is sufficient when a nontrivial continuous alphabet is available: take words whose difference has degree exactly p+1, which cannot coincide with a degree-p polynomial on p+2 distinct indices. A sufficiently small positive eps preserves separation for a fixed finite pair. An arbitrary specified eps may be too large for a bounded alphabet.

For p=1 consider the one-dimensional curvature family: a word's log intervals are represented modulo affine terms by s i^2. Allow nominal dynamic range L>0, i.e. each score has some representative in [0,L]^n. Write P(n)=floor((n-1)^2/4). The admissible s values are exactly [-L/P(n),L/P(n)] for n>=3. In fact the quadratic minus the endpoint chord has range P(n), and its best affine residual norm is P(n)/2 by the triple formula. A representative within the log cube exists iff |s|P(n)<=L (center the best residual in that cube). This bounds relative nominal intervals by exp(L), not absolute playback length.

For any surviving index set I of m>=3, the exact radius of i^2 is

    (1/2) max_{j in I}(j-min I)(max I-j).

The maximizing triple can use the extreme indices, since enlarging both endpoint distances can only increase the nonnegative product. The minimum over all m-element subsets is P(m)/2: the median-by-rank index has distance at least floor((m-1)/2) and ceil((m-1)/2) from the two ends, because indices are distinct integers; consecutive indices attain that bound. Thus in the quadratic family the worst fault distance is

    |s-s'| P(m)/2.

A robust alphabet must separate s values by strictly more than 4 eps/P(m). For eps>0, m>=3, the exact maximal cardinality IN THIS FAMILY is

    C_quad = max(1, ceil(L P(m)/(2 eps P(n)))).

Proof of scalar packing: in an interval of length A, k points separated by >B require (k-1)B<A; conversely choose equal spacing A/(k-1)>B for k>=2. The ceiling, not floor-plus-one, handles equality correctly. For m<=2 all words are confusable; for eps=0 and m>=3 the continuous family admits arbitrarily many distinct words (not a finite digital throughput claim). This formula is not an upper bound on nonquadratic codebooks when n>3. At n=3, the affine quotient is one-dimensional, so it is the unrestricted optimum.

Example n=12, L=1, eps=1/40: no faults gives 20 words within the family; 1 substitution gives 14; 2 substitutions 8; 3 substitutions 4; 4 substitutions 2; 5 substitutions leaves two guaranteed clean common coordinates and gives 1. The uncertainty is a worst-case condition; it is not an expected error rate.

## General codebook geometry and unresolved packing

For n>p+1, the quotient dimension is q=n-p-1. The projection of the log cube [0,L]^n onto the quotient is exactly the norm ball of radius L/2, because constants belong to the nuisance space and the minimum uniform norm is attained. For no faults and eps>0, disjoint open balls of radius eps around separated words lie within the ball of radius L/2+eps. Lebesgue volume in the q-dimensional quotient scales as the q-th power of radius, giving

    C <= floor((1+L/(2eps))^q).

A maximum-cardinality strict-separated code exists as a finite integer cardinality (packing bound); its closed balls of radius 2eps cover the admissible ball, since otherwise one more point could be added. This gives C >= max(1, ceil((L/(4eps))^q)). These are generic volume bounds, often not tight. No general optimal packing theorem is claimed. When n=p+2 the quotient is one-dimensional: the exact fault-free optimum is max(1,ceil(L/(2eps))) for every p. One erased coordinate destroys all distinction in this minimum-length case. A higher-order nuisance model discards more expressive dimensions; its value must be measured against the distortion actually expected.

## Qualification and reproducibility

- [laboratory.cjs](laboratory.cjs) is standard-library JavaScript; run node laboratory.cjs. Its actual core ran in a V8 isolate, not native Node. [execution.json](execution.json) contains counts: 9,840 full words in {-1,0,1} through length eight; 55,986 subset radius comparisons through length six; 19,648 exact feasibility checks at the predicted optimum and (when positive) strictly below it; 9,840 bounded-curvature sequences through length ten; 65,528 quadratic subset checks through n=15; 130 minimum-over-subsets checks; 62,052 adversarial profiles and 492,684 subset feasibility comparisons. All passed. Exactness here means safe-range integer products and rational pairs, not arbitrary precision outside the tested range. The adversarial census compares subset radii against direct slope feasibility, not every literal corruption transcript; the general two-world replacement argument is a proof, not a claim of exhaustive transcript enumeration.
- [crosscheck.py](crosscheck.py) compares rational Vandermonde contrasts with a direct numerical linear programme (SciPy HiGHS) at degrees 0,1,2,3, 120 deterministic seeded cases each. Python 3.13.5, SciPy 1.17.0; all 480 passed, max absolute discrepancy 6.039613253960852e-14; [crosscheck.json](crosscheck.json). NumPy/SciPy are optional for this cross-check, not new canonical dependencies. This is an algorithmic cross-check by the same agent, not independent review. No population frequency is inferred from synthetic fixtures.
- [witness.py](witness.py) is standard-library native Python 3.13.5 and generated five original mono PCM16 WAVs at 8 kHz. [audio.json](audio.json) retains full SHA-256 and onset sample indices. Run python witness.py from this directory; the generated files live in results/ (not committed as binary assets). Nominal-flat and nominal-ramp differ, observed-flat and observed-ramp are byte-identical, and curvature differs from the flat receipt. The renderer directly synthesizes the specified observed intervals, not a physical resampling or noisy sensor simulation. Pulse width is fixed for the illustrative score; no claims of full waveform time-warp invariance, perceptual equivalence or human decoding. The audio is original and no externally sourced recordings are included.

Repository-wide tests were not run locally: git ls-remote failed with DNS resolution for github.com; connector writes are separate. Native Node wrapper execution and independent critique remain outstanding, along with exact-head repository CI at opening. Draft is intentionally held for review and no main merge or scientific stage acceptance is claimed.

## Sources, ancestry and limits

Read 2026-11-24 by this agent:

* D. V. Gorbachev, V. I. Ivanov and S. Yu. Tikhonov, *Chebyshev systems and Sturm oscillation theory for discrete polynomials*, [arXiv:2501.02358v2](https://arxiv.org/abs/2501.02358v2). PDF version footer 19 Aug 2026; document date 21 Aug 2026. Relevant §1.1, printed pp.2–4, especially Theorems 1.3/1.4 and Corollary 1.5; p.4 page image inspected. This gives established discrete approximation/alternation ancestry, not a claim that the paper studies auditory codes. No whole-paper reading claimed. Self-contained duality proof above instead of reproducing their proof.
* B. H. Repp, J. London, P. E. Keller, *Perception-production relationships and phase correction in synchronization with two-interval rhythms*, Psychological Research 75(3), 227–242 (2011), [DOI 10.1007/s00426-010-0301-8](https://doi.org/10.1007/s00426-010-0301-8). [Institutional author-publication abstract](https://researchers.westernsydney.edu.au/en/publications/perception-production-relationships-and-phase-correction-in-synch/) read, Abstract paragraphs on ratio-dependent biases. The authors report biases dependent on interval ratios in their experiments; this is a contrary lead against a generic perceptual log-error assumption. Abstract only: no appraisal, participant-level analysis, import of threshold or general inference. Not promoted to the frozen evidence registry.

The mathematical propositions are conditional on the defined channel. An auditory listener may perceive overall rate, rate change, absolute time, phrase grouping, pitch, pulse width and context; removing these cues is a design choice, not a universal auditory invariant. Real-time tempo drift may be constrained, time-dependent, tied to physical timestamps or correlated across intervals. A finite nuisance bound can make previously confusable words separable. Independent log error is multiplicative duration error; additive onset timestamp error instead induces correlated adjacent interval errors. A missing pulse is not a flagged coordinate erasure. A fixed nominal duration range does not bound actual playback time under unrestricted tempo nuisance. Additional observation of the nuisance, calibration pilots, or a separate synchronized clock can restore lost information. No human validation, semantic universality, claim that Brier endorsed the model, or result about perceived emotion.

## Interpretive and artistic sediment

A rhythm language must decide whether acceleration is an utterance, a defect in transmission, or an admissible reinterpretation. Invariance cannot preserve a semantic distinction that it identifies as nuisance. A proposed "curvature organ" would play the nominal score, a drift-transformed version and sparse diagnostic contrasts. A performer manipulates curvature while a second manipulates the affine nuisance; each can hear the same public receipt even as the nominal score changes. The proof suggests a refusal rule: if the intended message pair has no fault-robust separating contrast, refuse to present it as unambiguous. The actual human usefulness of such an interface is untested.

Potential falsification programme: compare fixed-tempo versus unknown-tempo versus controlled geometric-warp conditions; compare full triple fit with adjacent-only decisions; vary relative and additive timing errors separately; test missed-onset behavior, response time, comprehensibility and confusion matrices only under authorized study arrangements. Reject the proposed channel if actual errors are not adequately modeled by its bounds, and do not infer a human effect from the synthetic files.

**Original fiction.** A conductor wrote a gradual slowing into a machine's score. The transmission engineer had just installed a perfect correction for gradual slowing. Every beat arrived on time. The conductor asked where the instruction had gone. The engineer said the machine had preserved everything that counted as rhythm. On the next page the conductor wrote a curve that the engineer could no longer straighten.
