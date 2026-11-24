# The Equalizer That Cannot Please the Room

**Refs #304 — 2026-11-24.** Standalone formal/synthetic expedition. AI-assisted derivation, implementation and self-check by ChatGPT. Not a Track E/G finding, physical room test, perceptual result, accepted design contract or claim of mathematical priority.

## 1. A deliberately narrow model

At one frequency, each receiver has known complex transfer coefficient h_i. One source is multiplied by a shared arbitrary complex gain g. The target at every receiver is the same complex coefficient 1. Minimize

    R = min_g max_i |1 - h_i g|.

This measures coherent reconstruction error relative to a unit reference, not perceived loudness or quality. Silence (g=0) gives R<=1; "strict improvement" means improvement over this unit-error reference, not over bypass (g=1). A zero transfer fixes R=1 for all arrangements including that receiver. Assume all h_i nonzero otherwise. Each receiver has ideal gain c_i=1/h_i and weight w_i=|h_i|. The problem is the weighted Euclidean minimax center of the c_i: errors are w_i |g-c_i|.

Example: h=(1, exp(2pi i/3), exp(-2pi i/3)). All magnitudes equal 1. Each pair can be jointly corrected to error sqrt(3)/2; all three cannot achieve error below 1. Magnitude-only equalization is trivial (g=1), so this is explicitly a phase-sensitive target.

## 2. Proofs and counterexamples

**P1 — exact pair optimum.** The two feasible disks of target error t have centers c_i,c_j and radii t/w_i,t/w_j. Intersection iff their distance <= t(1/w_i+1/w_j). Thus the pair optimum is

    P_ij = |c_i-c_j|/(1/w_i+1/w_j)
         = |h_i-h_j|/(|h_i|+|h_j|).

It is attained at (w_i c_i+w_j c_j)/(w_i+w_j). A duplicate pair gives zero.

**P2 — three-point certificate and sharp ratio.** The objective squared is the maximum of convex quadratics F_i(g)=w_i^2 |g-c_i|^2. A minimizer exists (coercive); it is unique because subtracting min_i w_i^2 |g|^2 leaves a convex function. At the minimizer the convex hull of the active gradients contains zero: otherwise a separating direction decreases all active quadratics and, by continuity and finiteness, decreases the maximum. Conversely a convex combination of active gradients equalling zero implies global optimality by the supporting inequality for convex functions. A minimal convex representation of zero uses at most three vectors in R^2 (if more, an affine dependence permits removing one positive coefficient). The same minimizer and value hold for the corresponding subset.

Write P=max P_ij (zero for a single nonzero channel). Then

    P <= R <= min(1, 2 P / sqrt(3)).

For R>0 choose a minimal active gradient support. It cannot be a singleton (which would have zero gradient and R=0). The two-vector case has opposite directions. In the three-vector case their directions cannot lie in an open semicircle, because their convex hull contains zero; at least one smaller pair angle is >=120 degrees (order the three directions around the circle; gaps <=180 and one gap >=120). The vectors from g to the associated centers have those same pair angles (the gradients have opposite signs, positive rescalings). Their lengths are a=R/w_i and b=R/w_j. By cosine law

    |c_i-c_j|^2 >= a^2 + b^2 + ab >= 3(a+b)^2/4.

Hence P_ij >= sqrt(3) R/2. Zero transfers give the trivial R=P=1 if there are at least two receivers, with P defined as 1 for a zero singleton. The three roots of unity attain R=1, P=sqrt(3)/2, proving sharpness; identical h gives R=P=0. In particular, P<sqrt(3)/2 is sufficient for R<1, and the strict threshold cannot be increased.

**P3 — exact obstruction to any strict improvement.** R<1 iff zero is outside the convex hull of the h_i. If zero is inside, some probability weights lambda_i satisfy sum lambda_i h_i=0. Then the weighted average of |1-h_i g|^2 equals 1+|g|^2 sum lambda_i |h_i|^2 >=1. If outside, strict separation yields a complex direction v with Re(h_i v)>0 for all i; sufficiently small positive epsilon makes every |1-epsilon h_i v|^2<1. Thus an origin-containing triangle or antipodal pair suffices as a negative certificate (or a zero singleton). The integer obstruction function uses BigInt cross/dot tests; the Python checker uses independent exact integer convex hull construction.

**P4 — closed form for equal magnitudes.** Let all |h_i|=A>0 and let L be the width of a shortest closed circular arc containing their arguments. If L>=pi, P3 implies R=1. Otherwise the midpoint argument phi gives g=(cos(L/2)/A) exp(-i phi). The error at each receiver is no greater than sin(L/2), with equality at the arc endpoints; P1 for those endpoints gives the matching lower bound. Therefore R=sin(L/2) for L<pi. For the symmetric arrangement (1, exp(i theta), exp(-i theta)), 0<=theta<=pi, R=sin(theta) for theta<pi/2 and R=1 thereafter. The largest pair residual is sin(min(180 degrees, largest smaller pair separation)/2), with angles interpreted consistently.

## 3. Reusable solver and corrective-voice compiler

The mathematical candidate list is complete in exact arithmetic. Single active receivers give c_i. Two active receivers with opposing gradients give the pair center. If three are needed, either g=0, or u=1/g is equidistant from all three distinct h_i (divide |1-h_i g| by |g|); three distinct collinear h_i cannot have a finite equidistant u. Otherwise u is the circumcenter and g=1/u. A collinear triple of c_i needs at most two vectors for a gradient certificate. The implementation enumerates these cases, evaluates full-set feasible upper bounds and supplies a sparse dual probability vector giving a lower bound:

    min_g sum lambda_i |1-h_i g|^2
      = 1 - |sum lambda_i h_i|^2 / sum lambda_i |h_i|^2.

For numerical stability the implementation evaluates the weighted residual directly at the weighted mean rather than subtracting nearly equal scalars. In exact arithmetic, the upper and lower bounds coincide at the optimum. Barycentric weights mu of g in the support centers give lambda_i proportional to mu_i/w_i^2. Floating-point bounds are estimates, not rigorous interval certificates. Near-collinear triples can be skipped; a gap above 1e-8 is returned as unresolved. The input is bounded to 64 coefficients, components <=1e100, and normalized nonzero magnitude ratio >=1e-6 (scale >=1e-100). No arbitrary conditioning guarantee is made.

At threshold 0<t<1, each receiver constrains g to a closed disk. By the planar Helly theorem (or P2), a group meets a threshold iff each of its at-most-three-member subsets meets it. Build a hypergraph of forbidden subsets of size at most three. A partition into independent sets is a partition into separately correctable groups. Enumerate subsets with a bitmask DP, requiring each candidate part to include the first remaining element to remove ordering duplication. This is exponential (<=12 receivers). At a numerical boundary the compiler returns unresolved rather than manufacturing an exact classification. For the three roots of unity, all pairs meet t=0.9 but the whole triple fails: two independent gains are necessary and sufficient. At t=0.8 every pair fails, requiring three gains. At exact t=sqrt(3)/2, the numerical classifier deliberately declines a decision. A zero-transfer singleton cannot be repaired by partitioning.

The split is a hypothetical system with separately controllable, noninteracting groups. It does not create extra spatial degrees of freedom for a single loudspeaker. For a real acoustic deployment, cross-coupling, filter causality, broadband response, noise, model uncertainty, power limits and perceptual objectives need separate treatment.

## 4. Qualification and preserved negative cases

Run from this directory:

    node verify.mjs > results.rebuilt.txt
    python check_audio.py run

The JS receipt is in results.synthetic.txt. The independent Python receipt is in audio.synthetic.txt. All 2,024 triples and 10,626 quadruples of the 24 nonzero points of the integer square [-2,2]^2 were evaluated; 7,810 prohibit strict improvement, including 3,264 with every pair strictly improvable. The exact Python monotone-chain hull census independently reproduced these counts (triples: 784 blocked, 360 pairwise-only; quadruples: 7,026 blocked, 2,904 pairwise-only). Counts are labelled mathematical populations, not samples of rooms.

500 seeded random continuous cases and three controls additionally tested. The independent algorithm in JS uses binary search on disk intersection; a feasible intersection contains a disk center or pair boundary crossing (coincident/contained disks can be ignored until a limiting boundary remains). 2,527 oracle comparisons gave max difference 9.999e-12; max observed primal-dual gap 4.441e-16. The solver's primal and sparse dual are replayed. 85 partition checks include 80 brute force assignments and five targeted examples. Negative cases: equal phase (no obstruction), zero transfer, exact threshold (unresolved), all magnitude responses identical yet coherent target obstructed, independent gain groups not equivalent to one common gain. No proof from simulation alone.

The source was executed as functions in the V8 tool runtime, not a native Node clean-checkout run. Python 3 was executed locally twice with matching receipts and byte-identical WAVs. A native repository checkout was attempted but GitHub DNS was unavailable in the container; connector writes and fetches succeeded. Python blob identity was compared to the locally executed file. Repository CI and independent review are not yet established. No protocol, registry, shared manifest, central test suite or live research record changes.

Two 1.8 s stereo PCM16, 16 kHz files are reproducible with the renderer: same-magnitude.wav (left all aligned; right phase-shifted roots; common scale), split-residual.wav (left residual under shared g=0; right residual under two independent gains). Each 0.6 s block represents a receiver in sequence, using a distinct carrier for legibility; this is a time-expanded illustration of a single-frequency coefficient problem, not a room impulse response. The middle block of the split residual is identically zero in right-channel PCM. No claim of audibility, human preference or physical room efficacy.

## 5. Provenance and exaptation

- Yoichi Haneda, Shoji Makino, Yutaka Kaneda, 1997, "Multiple-point equalization of room transfer functions by using common acoustical poles," IEEE Transactions on Speech and Audio Processing 5(4), 325–333, DOI [10.1109/89.593306](https://doi.org/10.1109/89.593306). Read the institutional abstract at [Waseda research portal](https://waseda.elsevierpure.com/en/publications/multiple-point-equalization-of-room-transfer-functions-by-using-c/) on 2026-11-24, not a complete paper appraisal. Motivation only: multi-point compensation is established. Their method and measurements are not this experiment.
- Cagdas Tuna et al., 2022, "Data-driven local average room transfer function estimation for multi-point equalization," JASA, DOI [10.1121/10.0016592](https://doi.org/10.1121/10.0016592), [PubMed abstract, PMID 36586844](https://pubmed.ncbi.nlm.nih.gov/36586844/), read 2026-11-24. Context only; no transfer of their empirical conclusions to this toy.
- Classical Helly theorem, [statement](https://en.wikipedia.org/wiki/Helly%27s_theorem), read statement 2026-11-24 (secondary source, not priority research). Convex optimization background reference: Boyd and Vandenberghe, [Convex Optimization (2004)](https://web.stanford.edu/~boyd/cvxbook/); landing page inspected only. P1–P4 are self-contained derivations here, not attributed novel results.
- Original code, generated audio and synthetic data; no external audio or licensed source text incorporated. No exhaustive literature/priority search was performed. No new license grant.

Potential exaptations: phase-sensitive oscillator correction, calibration of a shared complex control across independently modelled loads, test generators for pairwise-only qualification, and a conflict-hypergraph compiler for minimum numbers of control voices. In agentic communication the analogy is that every pair of receivers can admit a common correction while no common correction satisfies all. This is a mathematical analogy, not evidence about people, semantics or social agreement.
