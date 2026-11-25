# The Choir That Cannot Share Its Reference

**MHAC expedition / issue #614 — 25 November 2026.** Synthetic mathematical investigation and original PCM specimens, not a selected Track E/G result. AI-assisted research, implementation and self-check by one ChatGPT agent. No independent human review, physical microphone experiment or listening study.

## Finding

Every individual complex coherence measurement can be admissible. Every simple closed measurement loop can be independently realizable. Nonetheless the complete collection can be impossible to realize with one shared reference. The reason is not binary signed-graph imbalance but incompatible constraints on an unmeasured complex inner product.

For two anchors A,B and k labelled relay paths R_j, the graph is K_{2,k}. Every simple cycle has four edges. We give an exact disk-intersection certificate for normalized complex Gram completion on this graph, an equal-strength phase-arc formula, a sharp interval in which every cycle can pass while the whole graph fails, and an optimal whole-relay deletion criterion. All are finite mathematical results under the stated observation contract.

## Observation contract and proof of the disk theorem

A, B, R_j are unit vectors in a common complex Hilbert space of unrestricted dimension; inner products are conjugate-linear in the first argument. Each receipt is p_j=<A,R_j>, q_j=<R_j,B>; both moduli are at most one. Relay labels bind the two edge measurements of a path. No relay-to-relay measurements are stipulated. Let z=<A,B> be unknown.

Projection onto R_j gives z=p_j q_j+<A_perp,B_perp>. Cauchy–Schwarz forces

    |z-p_j q_j| <= sqrt((1-|p_j|^2)(1-|q_j|^2)).

Call the closed disk with this center and radius D_j. Each disk lies in the unit disk: |p q|+sqrt((1-|p|²)(1-|q|²))<=1 by real two-vector Cauchy–Schwarz.

**Theorem 1 (exact):** a simultaneous completion exists iff the intersection of all D_j is nonempty.

Necessity follows above. For sufficiency, select any z in the intersection. Take A=e_0, B=z e_0+s e_1, s=sqrt(1-|z|²). For each relay take R_j=p_j e_0+v_j e_1+w_j e_{j+2}, where v_j=conj(q_j-conj(p_j) z)/s, w_j=sqrt(1-|p_j|²-|v_j|²). For s>0 the disk inequality, expanded and rearranged, is exactly the nonnegativity of the last radicand. Thus each vector is unit and realizes its two prescribed inner products. For s=0, the disk condition implies q_j=conj(p_j) z (the same expanded inequality gives a zero upper bound); choose v_j=0 and w_j=sqrt(1-|p_j|²). This produces a joint Gram matrix of rank at most k+2. The proof does not assume statistical independence of relay measurements.

A local phase convention multiplies each vector X by a unit phasor g_X. Then p'_j=conj(g_A)g_j p_j and q'_j=conj(g_j)g_B q_j. Each disk center rotates by the same conj(g_A)g_B, and its radius is unchanged. Global feasibility and maximum disk depth are gauge invariant. This does not mean the measured phase itself is zero.

**Theorem 2 (exact local audit order):** two-path audits suffice for each individual simple cycle; three-path audits suffice for global feasibility, even for unequal edge magnitudes. This follows from planar Helly. Self-contained argument: if a finite minimal empty family has m>=4 sets, select x_i in all sets except i for four distinct indices. Four points in the plane admit a Radon partition into two disjoint nonempty groups with intersecting convex hulls (use a nontrivial affine dependence, with positive and negative coefficients normalized separately). A point in both hulls belongs to every set: for each of the four indexed sets, at least one group excludes its exceptional point; all other sets contain all four points. Contradiction. Families of size one or two must also be checked if fewer than three relays exist. The equilateral witness below shows that order three is sharp.

## Equal-strength frontier and independent-cycle failure

Suppose |p_j|=|q_j|=rho in [0,1], and put theta_j=arg(p_j q_j) for rho>0. The disks have radius 1-rho² and centers rho² exp(i theta_j). At rho=0 all disks are the unit disk and phases are immaterial. Write W for the length of the shortest closed circular arc containing all phases (2*pi minus the largest gap in the sorted circular list; W=0 for one distinct phase). Let R be the minimum enclosing circle radius of the unit phasors. Then

    R = sin(W/2) if W <= pi; otherwise R = 1.
    rho_max = 1/sqrt(1+R).

Proof: if W<=pi the extreme phasors are 2 sin(W/2) apart; their midpoint disk of half that diameter contains the entire intervening arc, since its squared distance from the midpoint is maximized at the endpoints. If W>=pi, no open semicircle contains the phases. Any disk of radius less than one containing unit-circle points has nonzero center and those points all lie in the open semicircle facing that center: |u-c|²<1 implies Re(u conj(c))>|c|²/2. Thus the unit circle is optimal. Scaling by rho² establishes rho² R <=1-rho², hence the stated sharp frontier.

A two-relay cycle is feasible iff |sin((theta_i-theta_j)/2)| <= (1-rho²)/rho² for rho>0. Its closure phase is theta_i-theta_j up to orientation. For phases 0, 120, 240 degrees, all three two-relay cycles pass at rho=18/25=.72: their pairwise center distances are sqrt(3)*324/625, less than twice the common radius 301/625. But the three centers sum to zero and have common modulus 324/625. For any z, the average squared distance to the centers is |z|²+(324/625)², strictly larger than (301/625)². No common z exists. Every simple cycle is individually valid; no single realization exists. At rho=.7 all three do share a realization with z=0.

**Theorem 3 (sharp false-pass band):** for arbitrary finite equal-strength phase dictionaries, a pairwise audit can pass while global completion fails exactly for some phase dictionary at

    1/sqrt(2) < rho <= 1/sqrt(1+sqrt(3)/2)
    (approximately .70710678 < rho <= .73205081).

Below or at the lower endpoint every phase dictionary is feasible (z=0). If W<=pi, the extreme pair determines R, so pairwise checks suffice. Otherwise the origin is in the convex hull of the unit phasors (separation by an open semicircle would contradict W>pi). Triangulate the convex hull; a triangle or diameter contains the origin. For a triangle containing the origin, its three successive circular gaps are each <=pi and sum to 2*pi; at least one gap is >=2*pi/3, so a pair is separated by chord length at least sqrt(3). A diameter has an even larger separation. Pairwise success therefore forces the upper endpoint inequality. The equilateral triple attains that upper bound and fails globally everywhere above the lower bound. These are existence bounds, not the frequency of failure for real-world data.

## Repair and conditioning

**Theorem 4 (maximum consistent subset):** for equal strength rho>1/sqrt(2), let W_max=2 arcsin((1-rho²)/rho²). The maximum number of paths that can remain without changing their receipts equals the largest number of phase points (counting multiplicity) in a closed circular arc of width W_max. Below or at 1/sqrt(2), retain all. This follows directly from Theorem 3's preceding enclosing-arc formula. Sort phases, duplicate with a 2*pi offset, and sweep with two monotone pointers. Time O(k log k), space O(k). Do not count any relay twice. The laboratory compares the returned count against literal disk-arrangement depth. The choice is not necessarily unique; excluded relays are not proven faulty.

For unequal magnitudes, maximizing retained paths equals maximum disk depth. Enumerate all centers and pairwise boundary intersection points (including tangencies), count how many disks contain each, and choose a maximum. Why these candidates suffice: take a nonempty intersection of a maximum-cardinality subfamily. If a zero-radius disk occurs, its center works. Otherwise the intersection is compact and convex. If its boundary is one complete circle, the corresponding disk and its center are contained in every other disk. If its boundary changes circles, an intersection point is available; if the intersection degenerates to a point it is a tangency or multiple-boundary point. Identical circles can be grouped, retaining multiplicities. This yields O(k³) time and O(1) streaming candidate space beyond the input. The code uses a numerical tolerance and is not an exact-arithmetic computational geometry kernel.

Uniform radial attenuation is another distinct repair: multiply every specified edge by rho_max/rho if infeasible. This is optimal among uniform radial attenuations preserving phases, not among arbitrary edits. For feasible equal-strength receipts, the maximum attainable smallest eigenvalue over all full Gram completions is exactly

    eta_max = 1-rho/rho_max.

For 0<=eta<1, G>=eta I and unit diagonal iff G=eta I+(1-eta)H with H a unit-diagonal PSD matrix. The specified off-diagonal magnitudes of H become rho/(1-eta), and its phases are unchanged. The feasibility theorem applies. For rho=0, G=I attains eta=1. At the frontier the spectral margin is zero. For the equilateral rho=.7 example eta_max=1-.7 sqrt(2), about .01005. This is an exact conditioning margin, not a noise-probability or perceptual claim.

## Source lineage, comparisons and limits

* Carilli, Nikolic, Thyagarajan and Gale-Sides (2018), "H I 21-cm Cosmology and the Bispectrum: Closure Diagnostics in Massively Redundant Interferometric Arrays", Radio Science 53, 845–865, DOI https://doi.org/10.1029/2018RS006537. Read publisher HTML introduction and section 3 equations (7)–(10) with accompanying text, 2026-11-25. Antenna-based separable phase terms cancel from closed-loop products; introduction also identifies nonclosing effects. Astronomy is a mathematical bridge, not evidence for auditory communication. General instrumental noise need not have separable gauge form.
* Sagar Silva Pratapsi, João Gouveia, Leonardo Novo, Ernesto F. Galvão, "Elementary characterization of Bargmann invariants", Phys. Rev. A 112, 042421 (2025), DOI https://doi.org/10.1103/hsnv-wpt3. Read publisher abstract and arXiv:2506.17132v3 HTML https://arxiv.org/html/2506.17132v3, definitions (2)–(4), Theorem 1/proof, Corollary 2 and boundary parametrization (14). The regular-polygon characterization of cycle products is already established and is not a novel result of this expedition. Our question is simultaneous completion of many cycles sharing two unmeasured anchors, not realizability of an individual cyclic product. In particular the four-cycle local limit is consistent with the known polygon result.
* Grone, Johnson, Sá, Wolkowicz (1984), "Positive definite completions of partial Hermitian matrices", Linear Algebra and its Applications 58, 109–124, DOI https://doi.org/10.1016/0024-3795(84)90207-6. Publisher abstract inspected, not full proof. Chordal completion gives the general mathematical setting. Our explicit common-anchor construction handles semidefinite/degenerate cases and does not rely on the source's positive-definite theorem.
* Repo #191, The Frustrated Choir: complete issue body read (no comments). Binary relations require exact parity balance; nonzero closure phase here can be perfectly admissible when magnitudes are less than one. Repo #384, The Knob That Returns With a Phase: complete issue body read (no comments). Operator holonomy is not Gram completion. Targeted live issue searches for Bargmann, closure phase, correlation matrix, Gram/phase and frustration did not reveal a duplicate of this specific relay problem. Scientific priority not claimed; no exhaustive literature search.

Negative sediment: pairwise-valid does not mean jointly realizable; nonzero loop phase does not itself imply inconsistency; even strong normalized coherence is not source identity. The disk proof presumes a common ensemble, window, frequency-feature basis, shared anchor definitions and normalized inner products. Pairwise windows with changing anchors, missing samples, independently renormalized populations or nonlinear metrics can give valid but non-comparable edge reports. A failed completion does not identify the culprit, establish deception or prove a physical impossibility outside the model. The feasible matrix is generally nonunique. A fixed low-dimensional synthesizer can have stricter constraints. Human listening, perceived timbre and interpretive adequacy are untested. Ordinary linear algebra and geometry explain the phenomenon without additional cybersemiotic assumptions.

Design hypothesis (unvalidated): an MHAC diagnostic could carry the reference/ensemble identity, normalized complex receipt, model residual and a small inconsistent subset separately. A receiver should distinguish "each loop can be explained" from "one explanation fits all loops." Compare with a conventional full Gram check and plain symbolic receipt, not merely a sonified inconsistency. A speculative instrument would let a performer move the phase disks, another adjust coherence strength, and a third choose which paths to retain; the musical material is loss of shared-reference compatibility rather than individual detuning.

## Reproducibility and repository checkpoint

Base main 495a98ca12bae467a507031f04931aa4254b1866. Fresh branch mhac-614/shared-reference-coherence. Scope only this directory; no shared manifests or canonical Track E/G records modified. Reconciled root instructions, RAG, programme, runbook, research integrity, validation guidance, 100 recent open issue results, 100 open PR results and 367 branch entries. PR #611's exact-head workflow 45698903254 was successful. The new issue body and comments were fetched before editing. Full native checkout failed with DNS resolution; no full repository test pass claimed.

Run from this directory:

    python laboratory.py

Python 3.13.5 native, standard library only. Exhaustively tested 2,509 distinct subsets of one through six points of a 12-phase grid, at eight strengths (20,072 profiles). Arc feasibility and optimal retained count matched literal disk-center/boundary intersection enumeration throughout; eight pairwise false passes were observed on this grid. Separately sampled 600 unequal-magnitude profiles with fixed seed 614, checked 8,011 triple intersections and 600 gauge transformations, and constructed 10,876 feasible Gram witnesses. These are finite floating-point checks, not mathematical proofs; analytic claims above have separate proofs. No independent agent or human review.

Four original half-second 8 kHz PCM16 files are generated into results/ (not committed binaries): common.wav contains A,B,R1,R2,R3 simultaneously at rho=.7; local-1-2.wav, local-1-3.wav, local-2-3.wav each contain A,B and the respective two relays at rho=.72. The latter are three separate common-reference realizations, with differing anchor correlations; they cannot be concatenated as if one shared five-vector state. All use integer-cycle sinusoidal bases with complex coefficients and fixed per-bank gain, not recordings of physical microphone coherence. PCM is read back and demodulated at the known carrier frequencies, then normalized to compute complex Gram errors (max 0.0000259491). No listening validation or equal perceived loudness. Two native executions produced identical receipts and WAV SHA-256 values. Source blob b16590a5f0d01185ae3c00e11e7bfd37232c729d matches the native executed source. See execution.json for full receipt.

Disposition: draft, open issue, review/CI pending. No scientific priority claim, no promotion into accepted evidence or external submissions.
