# The Mixture That Cannot Name Its Singers

Exploratory mathematics and synthetic composition · 2026-11-25 · Refs #440

**Result:** In a strictly positive additive band dictionary with at least (2k+1) available sources, the optimal number of measured bands for identifying a mixture of at most k active sources is (2k+2t+e), with t arbitrary band errors and e flagged erasures. Identifying that mixture against *all* nonnegative alternatives requires exactly one additional band. A positive binomial dictionary attains both bounds, even when the surviving bands are nonconsecutive. This is a model theorem, not a perceptual or safety claim.

## Contents
1. [Reconciliation](#1-scope-and-reconciliation) — isolated work and status.
2. [Channel](#2-the-channel-and-its-two-contracts) — definitions and examples.
3. [Sharp budgets](#3-sharp-band-budgets) — lower and upper proofs.
4. [Conditioning](#4-conditioning-and-the-cost-of-a-large-vocabulary) — exact near-collision and lower bound.
5. [Experiments](#5-executed-experiments-and-sound-witnesses) — reproducibility and PCM.
6. [Interpretation](#6-interpretation-negative-results-and-source-ledger) — application, prior art and limits.

## 1. Scope and reconciliation

Base main: 495a98ca12bae467a507031f04931aa4254b1866; branch mhac-440/mixture-cannot-name-singers; new issue #440 initially had no comments. Live AGENTS, README, RAG, programme, runbook, integrity, validation and project-foundations documents inspected; 279 branch names returned and 100 open issue / 100 PR search results (capped, not exhaustive). Four targeted searches for sparse mixture, polytope superposition, Radon and moment curve returned no issues. The earlier #356 report was inspected through its model and initial constructive proof; it concerns ambiguity of a particular spectral functional under moment compression rather than identification of sparse source mixtures. #420 concerns statistical dependence of voice activity, not additive observation of active sources. Exact-head workflow for previous expedition #429 at 07fb2f67a5a2cf26312699410f00152033cae843 returned completed/success.

This issue is a free-ranging additive expedition, not a revision of the frozen empirical protocol or a new canonical design claim. No shared manifests, other branches, source rights or programme status changed. One AI agent authored the proofs, source reading, two calculation methods and internal critique; neither method is independent peer review. Date of source reading 2026-11-25.

## 2. The channel and its two contracts

There are N known source templates (columns of D), each with B strictly positive entries summing to one. The underlying nonnegative vector w is nonzero. The received exact band vector is Dw. Unknown positive common gain is absorbed into w; the physical proportions are w/sum(w). No independent per-band gain is allowed. The channel erases up to e labelled coordinates and changes up to t other coordinates arbitrarily; the errors are not flagged. Assume N >= 2k+1 and k >= 1. A band is a scalar readout, not an independent auditory stream.

Trusted contract: the true and all competing vectors have at most k positive entries. Audit contract: the true vector has at most k positive entries, but the competing vector may be any nonnegative nonzero vector. The audit contract prevents a decoder from turning its own sparsity assumption into evidence of sparsity. It does not identify arbitrary dense inputs or prove that every dense input can be rejected without ambiguity with other dense inputs.

For a constructive dictionary use nodes 0 < u_1 < ... < u_N < 1 and

    D[j,i] = binom(B-1,j) u_i^j (1-u_i)^(B-1-j), j=0,...,B-1.

These are binomial probability masses, equivalently Bernstein basis evaluations. Each is strictly positive and the columns sum to one. A dictionary source can be a synthetic spectral-power receipt, not necessarily a separately radiated coherent pressure signal.

Example with k=2, nodes 1/6,2/6,3/6,4/6,5/6:
- Three bands: the two mixtures (1,0,3,0,0)/4 and (0,3,0,1,0)/4 both give (13/36,4/9,7/36).
- Four bands: the sparse mixture (0,4,0,4,0)/8 and dense mixture (1,0,6,0,1)/8 both give (1/6,1/3,1/3,1/6). Every at-most-two alternative to the sparse mixture is nevertheless excluded.
- Five bands: the latter pair gives different vectors. Dense world (139/1296,77/324,67/216,77/324,139/1296), sparse world (17/162,20/81,8/27,20/81,17/162). The discrepancy is small, not a listening-test result.

## 3. Sharp band budgets

**Theorem.** For the dictionary class above, N >= 2k+1, nonnegative integers t,e, the optimum B is 2k+2t+e under the trusted contract and 2k+1+2t+e under the audit contract. Optimum is among fixed scalar band dictionaries, not arbitrary interactive probes, nonlinear encoders or side information.

Two distinct possible exact vectors can share a received word iff their Hamming distance is at most 2t+e: erase up to e differing positions, split the remaining disagreements into two sets of size at most t, and choose the observation from one world on each set. Conversely, outside the erasures each disagreement must be charged to at least one error budget. Equalities are exact, not tolerance-based. A common gain may be chosen independently in each possible world because it is part of w.

**Lower bound, trusted.** If B-2t-e <= 2k-1, pick s=max(0,B-2t-e) bands. For s=0 any pair suffices. Otherwise normalize each restricted positive column by its sum; these are points in an affine space of dimension <= s-1 <= 2k-2. Among 2k+1 such points there are two disjoint subsets of at most k points with intersecting convex hulls. This is the affine van Kampen–Flores theorem (the k=1 case is simply coincident points). For completeness, embed into R^(2k-2) and perturb into general position. The affine dependence space for 2k+1 points in this dimension is a plane. A generic half-turn along its unit circle takes a coefficient vector to its negative, crossing one coordinate-zero line at a time (no pair can vanish by general position). At a generic direction the positive count plus negative count is 2k+1, so the half-turn must cross between k and k+1 positive entries. At that crossing there are k positive, k negative and one zero. Split and normalize the dependence. For the unperturbed configuration, take a convergent subsequence of the two convex combinations with the same disjoint supports; weights may become zero, but each side still sums to one. Undo column normalization to obtain positive mixtures on the retained rows; they coincide on those s rows and can differ on at most 2t+e others. Thus they are confusable.

**Lower bound, audit.** For s <= 2k, take 2k+1 normalized columns, which have an affine dependence. Its positive and negative supports are disjoint, nonempty, and the smaller contains at most k entries. Undo normalization. The same error/erasure construction proves impossibility. The lower bound relies on sufficiently many available sources; it does not cover small dictionaries with N <= 2k.

**Upper bound, trusted.** Put z_i=u_i/(1-u_i)>0. Removing positive row factors binom(B-1,j) and column factors (1-u_i)^(B-1) reduces every submatrix to powers z_i^j. Any square submatrix on increasing distinct rows and nodes is nonsingular: a nonzero polynomial consisting of at most r monomials has at most r-1 positive roots by Descartes' rule of signs. In fact the determinant is positive; on the connected domain 0<z_1<...<z_r it cannot change sign, and choosing z_i=R^i for large R gives the positive identity-permutation term uniquely dominant by the strict rearrangement inequality. A difference of two k-sparse mixtures has at most 2k nonzero entries. It cannot vanish on 2k distinct rows unless it is zero. Thus minimum Hamming separation is at least B-2k+1.

**Upper bound, audit.** Suppose two distinct vectors agree on >=2k+1 rows, with one vector k-sparse. Absorb positive column factors into their difference c. If all entries have one sign, positivity rules out any matching row. Otherwise c has a positive side of size s <= k (orient the difference to make the sparse vector positive). Choose 2s+1 of the matching row exponents. There is a nonzero linear combination g(z) of their monomials with double zeros at all s positive-side nodes: these are 2s homogeneous constraints on 2s+1 coefficients. Descartes' rule implies there are no other positive roots and these roots have multiplicity exactly two. Hence g has a constant nonzero sign away from those nodes. But agreement on the selected rows implies sum_i c_i g(z_i)=0, whereas all surviving negative terms have the same strict sign. Contradiction. Thus the audit distance is at least B-2k.

**Sharpness inside the construction.** For B>=2k choose any 2k-1 rows and 2k columns. The rectangular submatrix has a null vector made of signed maximal minors; these alternate signs, with k entries on each side. The pair agrees on exactly the selected rows, because an additional row makes an invertible square submatrix. The trusted distance is exactly B-2k+1. For B>=2k+1 use 2k rows and 2k+1 columns, yielding alternating signs with k and k+1 entries; the audit distance is exactly B-2k. These are actual witnesses for any chosen matching row set. At B=2k, the same alternating construction has an all-row sparse/dense collision.

For a given faulty transcript an exact but computationally expensive decoder enumerates erasure-compatible subsets of B-e-t unflagged bands and solves the appropriate nonnegative feasibility problem; for trusted recovery additionally enumerate supports. For audit recovery, retain only a sparse candidate with no other feasible nonnegative alternative. The theorem guarantees uniqueness when the stipulated true world is sparse. It does not assert efficient noisy decoding.

## 4. Conditioning and the cost of a large vocabulary

Exact Hamming distance disregards numerical magnitude. At the minimum trusted no-fault budget B=2k, let m=2k-1. Choose 2k consecutive nodes with spacing h in (0,1). The two mixtures formed from positive and negative coefficients of the m-th finite difference have equal unit mass, disjoint supports of k nodes, and weights proportional to binom(m,i)/2^(m-1). For each band, the difference is the m-th finite difference of a degree-m polynomial, so its absolute value is

    |delta_j| = binom(m,j) m! h^m / 2^(m-1).

Consequently total variation (half L1 distance) of the two *received* normalized band vectors is exactly m! h^m. The latent total variation is one. At k=3, h=0.01, the received distance is 1.2e-8. If each normalized receipt can undergo an L1 error of this magnitude, their midpoint is admissible for both. It is not an auditory JND or a bound on arbitrary physical noise.

A matching exponent lower bound holds for all pairs of k-sparse probability vectors in this dictionary with minimum node spacing h, B=2k. Let c=w-v and choose a largest |c_i| among its at most 2k nonzero entries. Form p(z)=product_{l in supp(c), l != i}(z-u_l), a degree <=m polynomial. On [0,1] the Bernstein coefficients of each factor have modulus <=1. The product coefficients are convex weighted averages of products of the constituent coefficients (by the Bernstein multiplication formula), and degree elevation preserves that bound. Thus p has Bernstein coefficients of modulus <=1 at degree m. Pairing them with D c yields exactly c_i p(u_i). Its magnitude is >= |c_i| h^m. Hence

    ||D(w-v)||_1 >= h^(2k-1) ||w-v||_1 / (2k).

The lower and constructive upper have the same exponent in h, not the same constant. For disjoint k-sparse unit-mass mixtures, received total variation lies at least h^m/(2k) from zero, and the explicit construction gives m! h^m. This rules out claiming that the finite-difference coefficient is the exact optimum for all grids. Overlapping supports can differ by arbitrarily small weights, so no positive universal support-identification margin without a minimum component mass. Arbitrary independent frequency-dependent gain, unknown templates, coherent interference cross terms, saturation, and unlabelled bands defeat assumptions rather than merely counting as an extra erasure.

## 5. Executed experiments and sound witnesses

The standard Node-format laboratory.cjs uses BigInt Bareiss determinants, exact cofactor null vectors and integer binomial columns. Executed core in a JS isolate with equivalent assertion adapter: 43,740 positive minors, 48,036 alternating cofactor witnesses, 343,086 row checks and 222,744 constructed error/erasure receipts across B=2..8 with nine source nodes; 15 finite-difference conditioning profiles and three literal collision profiles. All assertions passed. execution.json stores the receipt. Native Node CLI not claimed. This does not exhaust all possible real gain vectors; analytical proofs supply the universal conclusions.

A separate native Python Fraction/Gaussian-elimination implementation checked 1,703 minors on six nodes across B=2..6, all 15 conditioning profiles and the three collision profiles. It generated six one-second 8 kHz PCM16 mono files and two identical JSON receipts on repeat execution. Audio maps the normalized power vector to fixed-phase sinusoids at 300+200j Hz with a common taper and gain. The B=3 pair is byte-identical, as is the B=4 pair; B=5 differs. Files are generated demonstrations, not measurements, and the rendered waveform does not assert physical additivity of coherent sources. Use witness.py to regenerate, with witness.json retaining exact powers and SHA-256 fingerprints. No human listened as part of this work.

The proposed 'Mixture Organ' exposes a source bank, relative source gains, band count, adversarial band erasures and unknown-gain decoder. A performer can change a source combination while a limited-band observer's score remains identical. A second performer adds the audit band. A useful actual next experiment is constrained acoustic channel simulation with held-out frequency response, not listener recruitment or a production alarm deployment.

## 6. Interpretation, negative results and source ledger

Interpretation: recognizing an intended combination within a vocabulary is weaker than verifying that its underlying composition really belongs to that vocabulary. A decoder can be uniquely right *conditional on its trusted cap* while the evidence admits a denser impostor. The extra band repairs this specific logical gap, not all uncertainty. In machine-state audio, keep the source concurrency cap, whether it is independently warranted, measurement fault budget and numerical residual distinct in an uncertainty receipt. This is a design hypothesis; operational variables are false acceptance of out-of-contract dense mixtures, reconstruction error, dictionary spacing and channel mismatch. Reject or revise the hypothesis if the declared channel model fails in realistic measurement conditions, or if a controlled evaluation fails to support any claimed user benefit.

Source ancestry and contrary evidence (2026-11-25, AI passage reading, no human verification):
- Bogdanov and Matushkin, *Algebraic proofs of linear versions of the Conway–Gordon–Sachs theorem and the van Kampen–Flores theorem*, arXiv:1508.03185 (2015), https://arxiv.org/abs/1508.03185 . English abstract/theorem statement and rendered partial proof §2.1 inspected; main text Russian, not fully translated. The even-dimensional affine intersection theorem is established prior art. Our lower-bound proof is written out and does not depend on an unverified translation.
- Donoho and Tanner, *Sparse nonnegative solution of underdetermined linear equations by linear programming*, PNAS 102 (2005), 9446–9451, https://doi.org/10.1073/pnas.0502269102 . PubMed abstract and authors' corrected April 8, 2005 manuscript, https://people.maths.ox.ac.uk/tanner/papers/NonNegative-R5.pdf , printed pp. 2–4 (Theorem 1, §1.1, Corollaries 1.2–1.3; printed p.3 page image inspected). Their neighborliness and nonnegative uniqueness framework is direct prior art, including the connection to incomplete transforms. Their work is not a validation of the present auditory model; no priority claim for the mathematical ingredients or fault-budget extension.
- Bidet-Caulet and Bertrand, *Neurophysiological mechanisms involved in auditory perceptual organization*, Frontiers in Neuroscience (2009), https://doi.org/10.3389/neuro.01.025.2009 . HTML sections on simultaneous organization and conclusion inspected. This is a review, not a newly extracted empirical study. It describes context-dependent grouping involving onset and pitch continuity and warns against directly identifying recorded neural responses with conscious perception. This is contrary to treating band-vector decoding as a complete model of human source segregation. No claims about measured human performance of this dictionary.

Other negative results: exact fault distances do not establish numerical robustness; identifying a sparse world against dense impostors is not arbitrary dense recovery; component absence and low amplitude differ; increasing B changes the dictionary here, rather than merely appending a measurement to the original dictionary. A physical sound field may carry timing, phase, spatial or harmonic cues excluded from this channel. No canonical evidence promotion, no external review, no invented novelty or human result.

**Fiction (original):** A choirmaster gave the clerk a ledger of four columns. It could identify every permitted duet. One evening three singers submitted exactly the same ledger as two. The clerk had not made a mistake in his arithmetic. He had made a mistake in what he believed the arithmetic had licensed him to say. On the fifth column he wrote not a new singer's name, but the word *unless*.
