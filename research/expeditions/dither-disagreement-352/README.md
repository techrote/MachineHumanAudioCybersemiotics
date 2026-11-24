# The Dither That Has to Disagree
## Fair correlated rounding, moving defects and exact temporal debt

Refs #352 · 24 November 2026 · synthetic mathematical / artistic expedition. No Track E/G admission, participant data, perception claim, production DSP guarantee or priority claim.

### Model

Each of n channels has an ideal value of one half of an LSB. The rounding word x is binary; every channel must have mean 1/2. A signed simple graph specifies local pair contracts: edge (u,v,p) wants x_u XOR x_v = p. For p=1 the sum must be exactly one LSB; for p=0 the difference must be zero. Each failed edge has absolute residual one LSB. This is a model of a shared rounding operation, not a claim about conventional additive dither or a white-noise process. No unequal fractional inputs, temporal signal variation, overload or real converter noise is modeled.

Independent unbiased rounding violates each edge with probability 1/2. Common threshold rounding satisfies all p=0 edges but fails all p=1 edges. Correlated rounding can do better, yet the local constraints need not admit a common word. A parity-inconsistent cycle is the simplest obstruction: XORing all edge demands yields 1, while XORing all actual edge parities yields 0.

### Exact fair compiler and certificate

Let A_{s,e} be one if word s satisfies edge e, otherwise zero. Complementing every bit leaves A unchanged. Thus any distribution on complement representatives can be symmetrized without changing edge success probabilities, while ensuring exactly unbiased channel marginals.

Let alpha be the largest achievable minimum edge success probability, and let r=1-alpha be the minimum worst-edge failure probability. The fractional cover LP minimizes sum(c_s) subject to c>=0 and A^T c>=1. Its dual maximizes sum(w_e) subject to w>=0 and A w<=1. Since every edge can be satisfied by some word, the cover exists; its optimum C is finite and positive. Scaling an admissible distribution by the reciprocal of its minimum success produces a feasible cover; normalizing a cover gives a distribution with success at least 1/C. Consequently alpha=1/C. This is the fractional cut-cover invariant for all p=1, with a signed-constraint generalization here.

The rational simplex solves the dual with slack basis and Bland's smallest-index entering/leaving tie rule. Its objective slack coefficients recover a cover. It emits a distribution P and an edge weight vector W, both nonnegative and normalized. The independently callable verifier checks every edge has P-success >= alpha and every word has W-weighted success <= alpha. These are exact matching lower and upper bounds: for any competing distribution, the minimum edge success cannot exceed its W-weighted success, which cannot exceed alpha. A numerical LP is not needed to validate this certificate.

For balanced finite periods the compiler pairs each representative with its complement. If the distribution has common denominator D this gives a period of 2D; it is a feasible realization, not a general shortest-period optimizer. The solver accepts simple graphs of 2..8 vertices, no empty edge set or duplicate edges, and has a pivot budget. The certificate verifier is intended for rational arguments, not arbitrary untrusted deserialized data. The algorithm is exponential in vertices and not a real-time allocator.

### The moving defect theorem

For any simple signed cycle of length n>=3 whose edge parities XOR to 1:

* Every word must fail at least one edge, so the worst-edge failure probability is >=1/n.
* Choose a starting word satisfying the first n-1 edges; the closing edge fails. Flip vertices in cyclic order 0,1,...,n-1 and repeat. Each flip toggles exactly the old failed edge and its next neighbor, moving the unique defect around the cycle. After n flips the entire word is complemented; after 2n it returns.
* Every channel is one in exactly n of the 2n recorded frames. Each edge fails twice, so the lower bound 1/n is attained.
* In any exactly balanced period T, two channel columns each contain T/2 ones. Their Hamming distance is T-2 times their common-one count, hence even. Both same-parity and opposite-parity failure counts are therefore even. At the optimum every edge has T/n failures (the sum must be at least T and each count at most T/n). Thus T/n is a positive even integer: T>=2n.
* Any cyclic schedule with exactly balanced channels flips each channel at least twice. The moving defect achieves the minimum total 2n flips and the minimum possible nonzero peak of one flip per transition, including the wraparound. It simultaneously attains optimal fairness, period, total switching and peak switching for this cycle family.

This applies to an ordinary odd cycle (all p=1) and to an even cycle with an odd number of opposite-parity demands. For a consistent cycle all constraints can instead be satisfied simultaneously, with a word and complement giving a balanced period of two frames. In general the cycle lower bound need not be tight: the all-opposite K5 has at most six satisfied edges of ten per word, and averaging all balanced cuts attains defect 2/5, greater than the triangle lower bound 1/3.

A further general necessary period bound: if the rational optimum worst-edge failure is a/b in lowest terms, at least one edge of an optimal schedule attains it. Its count aT/b and T must both be even. Therefore T is a multiple of 2b (if b is odd, T even forces this; if b is even, a odd and count even force it). This is necessary, not proved sufficient outside the cycle construction.

### Aggregate versus local guarantees

For a triangle with L leaves attached to one vertex, all opposite-parity, every word must fail at least one triangle edge. Choosing any maximum cut of the triangle and setting leaves opposite the center attains exactly one failed edge per frame. The optimal average defect across edges is 1/(L+3). But the optimal maximum edge defect remains 1/3, by the triangle bound and rotating the single defect with the leaves following the center. The ratio is (L+3)/3 and unbounded as L grows. Global averages can conceal local persistent faults.

A seven-cycle fixed-defect schedule alternating a word and its complement has exactly one failed edge per frame, all at the same location, and 98 total flips over 14 frames. The moving defect has the same aggregate failure count, but failures are spread evenly and it uses 14 total flips, peak one. This is not a universal switching advantage over all fixed-defect schedules: grouping seven copies of the word followed by seven copies of its complement also uses 14 flips, but with peak seven and persistent spatial unfairness. Switching cost, peak cost, fairness and spectral behavior are distinct objectives. No claim that the period produces white or inaudible noise.

### Synthetic qualification

Run from this directory:

    python dither.py
    python verify.py --out run

The core uses only Python standard library. The second command additionally requires SciPy for the independent floating-point primal probability LP. Local execution: Python 3.13.5, SciPy 1.17.0. All 756 nonempty labeled signed graphs of sizes 2..4 were exactly certified and replayed as balanced periods. Defect histogram: 416 zero; 316 at 1/3; 24 at 1/4. The second LP checks all those and all 1,023 nonempty all-opposite labeled graphs on five vertices (1,779 total, maximum numerical gap 2.22e-16). These are finite enumerations, not prevalence estimates. All 1,020 frustrated sign patterns on cycles of lengths 3..10 reproduce the theorem's exact counts, and a separate balanced-column enumeration proves the claimed period boundary for all signed frustrated cycles of lengths 3 and 4 (44 cases). The triangle with five leaves is an explicit additional case. The floating-point LP is a separate formulation, not independent human review.

### Sound and transfer

The original 1.4-second stereo PCM16 WAVs at 16 kHz are generated by verify.py. Every block corresponds to one rounding word; its signed sum residual is multiplied by an integer triangular carrier with a fixed edge-dependent period and taper. Both channels use the same scale. In target-edge.wav the left channel repeatedly fails one selected edge, while the right fails it in only two of fourteen blocks. In walking-defect.wav all edge residuals are embedded in different carriers, so the fixed failure repeats at one pitch and the moving failure traverses the bank. This is an artistic linear-style embedding with integer truncation, not measured hardware audio or a perceptual comparison. No third-party audio or participant data. Both WAVs and the receipt reproduced byte-for-byte locally; binary WAVs are generated on demand and not committed. See results.synthetic.txt for hashes.

Potential exaptations: graph-aware coordinated quantization of static control buses; a modular synth in which incompatible pair contracts generate moving residual tones; scheduling conflicting symbolic contracts with equal marginal duty; testing fairness of quantized multichannel transformations; periodic actuator scheduling where the switching metric actually corresponds to cost. Actual DSP performance, spectral shaping, timing, dynamic fractional input, weighted constraints and hardware safety require separate qualification. The moving defect is an exact cycle construction, not a general graph switching optimizer.

### Provenance and boundaries

Source access by one AI agent on 24 November 2026:
- Robert Šámal, [Cubical coloring -- fractional covering by cuts and semidefinite programming](https://arxiv.org/abs/0911.2589), arXiv abstract inspected. It introduces the fractional covering by cuts invariant. No full-text or priority audit.
- José Neto and Walid Ben-Ameur, [On fractional cut covers](https://doi.org/10.1016/j.dam.2019.03.020), Discrete Applied Mathematics 265 (2019), 168–181. Institutional abstract and metadata inspected, not the full article. It describes fractional weights on cuts covering every edge.
- Gandhi, Khuller, Parthasarathy and Srinivasan, [Dependent rounding and its applications to approximation algorithms](https://doi.org/10.1145/1147954.1147956), JACM 53(3), 324–360 (2006). Institutional abstract and metadata inspected. Its bipartite edge-variable model differs from the present vertex-variable signed constraints.

The proofs above are self-contained derivations for the defined model. No novelty priority, human interpretation, or equivalence to a full dither theory is asserted. The source abstracts are context only, not empirical evidence. Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866; recent issues/PRs and searches for rounding, max-cut and discrepancy inspected. #264 concerns quantized dynamical attractors, #216 exclusive pulse slots, #312 mixer headroom, and #296 phase cycling; this folder concerns fair half-LSB pair constraints. No shared records or frozen protocol edits. Repository-wide clean checkout blocked by DNS; local dedicated verification passed. Scope remains Draft pending further review and repository integrity CI.
