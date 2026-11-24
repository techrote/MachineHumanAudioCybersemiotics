# The Mask That Cannot Survive Its Own Playback

Refs #368 · 24 November 2026 · original formal/synthetic expedition, not Track E/G evidence or an accepted interface specification.

## Model and scope

For a real cyclic vector x of length n >= 3, analyze each overlapping pair (x_i,x_(i+1)) into two coefficients (x_i+x_(i+1))/2 and (x_i-x_(i+1))/2. Write the analysis matrix A; every sample occurs in two windows, so A^T A=I. P=A A^T is the orthogonal projection onto realizable coefficient vectors. For real diagonal gain D, the requested coefficients are D A x; playback A^T D A x is always possible, but reanalysis yields P D A x, not necessarily the requested coefficients. Define leakage B=(I-P)D A. Distinguish this coefficient-space discrepancy from waveform reconstruction error or subjective quality.

## General certificate

For any finite real Parseval frame A and real diagonal D=diag(d), E=||B||_F^2 is half the squared Frobenius norm of [P,D]. Proof: decompose coefficient space into range(P) and its orthogonal complement. In this basis the commutator consists of two mutually transposed off-diagonal blocks with opposite signs; B is the lower-left block applied to an isometry onto range(P). Entrywise [P,D]_ij=P_ij(d_j-d_i), hence

    E = sum_(i<j) P_ij^2 (d_i-d_j)^2.

Universal consistency E=0 holds iff gains are constant on connected components of the graph whose edges have P_ij != 0. This is a Dirichlet energy; anchored least-squares gain design is a graph harmonic extension, by the quadratic first-order equations at free vertices. No priority claim.

For the cycle frame, adjacent windows have four cross-coefficient overlaps of magnitude 1/4; signs in a window are mutually orthogonal, and nonadjacent windows are disjoint. Thus with window mean m_i and half-splitting s_i between its two gains,

    E = (1/4) sum_i (m_i-m_(i+1))^2 + (1/2) sum_i s_i^2.

The graph is connected. A nonconstant mask cannot survive playback for *every* input.

## Anchor compiler and sharp optima

Restrict to tied gains g_i for the plus/minus coefficients of each window. Window inverse gives two copies of each sample, scaled by the preceding and following window gains. Synthesis averages those copies, and each vertex's coefficient residual has total squared norm x_i^2 (g_i-g_(i-1))^2/4. Equivalently B^T B is diagonal with these squared jump weights (verified via basis vectors). Therefore

    E = (1/4) sum_i (g_i-g_(i-1))^2
    ||B||_2 = (1/2) max_i |g_i-g_(i-1)|.

Given any nonempty set of distinct anchored windows, split the cycle into arcs between consecutive anchors. A real-valued linear ramp on each arc minimizes both objectives: Cauchy-Schwarz bounds the squared jump sum by delta^2/L, and the largest absolute jump is at least |delta|/L. A one-anchor cycle admits a constant solution. Even allowing untied *real* gains on unanchored windows cannot improve either optimum: the energy formula penalizes splitting, and the diagonal of B^T B for arbitrary real paired gains is ((m_i-m_(i-1))^2+s_i^2+s_(i-1)^2)/4, as follows by expanding A^T D^2 A-(A^T D A)^2. The operator norm squared is at least its largest diagonal. Tied ramps attain both lower bounds.

For integer tied gains, let an arc have L steps and signed endpoint difference delta, with |delta|=Lq+r, 0<=r<L. Any integer jump list with this sum can be improved in squared sum by moving one tick from a larger jump to a smaller jump whenever their difference exceeds one. Therefore the optimal squared jump sum is (L-r)q^2+r(q+1)^2; the minimum maximum absolute jump is ceil(|delta|/L). Both bounds are achieved by the floor-interpolated ramp used by compile(). Arc independence gives global optima. This is an exact integer result for tied gains; we do not claim integer untied optimality.

Two opposite anchors 0 and M on a cycle of 2L windows: hard step E=M^2/2, ||B||_2=M/2. Real ramp E=M^2/(2L), ||B||_2=M/(2L), a factor L reduction in both (note E is squared Frobenius, not Frobenius norm). For integer ticks with normalized gains g/M, once L>=M both optimal costs plateau: E=1/(2M), ||B||_2=1/(2M). Increasing window count alone cannot remove finite-resolution leakage. This is a precision floor for a specified anchor contrast, not a general bound on all DSP.

## Falsifiers and preserved limits

- Signal-specific consistency need not imply universal consistency. With gains [0,0,1,1] and x=[0,1,0,0], both windows containing the active sample agree; residual is zero. With x=[1,0,0,0], they disagree.
- Constant gains are an exact positive control. Non-overlapping orthonormal analysis (P=I) allows arbitrary gains without leakage; redundancy topology matters.
- Playback always produces a valid waveform and projected coefficients. The obstruction is only to satisfying the requested coefficient vector exactly. A different optimization objective, e.g. preserving an input waveform or subjective quality, need not prefer the ramp.
- The toy uses a cyclic two-point real frame, not a validated STFT mask optimizer. No listening effects, intelligibility, hardware or human claims. No empirical population.

## Artifacts, qualification and provenance

Run node verify.cjs in this directory for the deterministic census; node is not required by the repository's core validator. Run python render.py for two locally generated 2-second stereo 16 kHz PCM16 files, using the same scale in both channels. The first renders the actual difference of the two local copies for constant x, repeated as a 64-sample periodic signal. The second plays synthesized cosines with the hard/ramp masks. A shared 20 ms endpoint taper is applied; the artistic periodic embedding is not a listening experiment. WAV bytes are not committed; the source and hashes suffice to regenerate them. Original synthetic source only.

Executed in a JavaScript V8 sandbox: 7,290 exhaustive independent-gain basis-vector comparisons, 3,267 tied-gain Gram checks, 80 anchor configurations with 32,520 enumerated candidates, five refusal cases, and signal-specific negative/positive controls. Exact integer/dyadic computations in the bounded census. Python rendering twice produced identical SHA-256 outputs. No claim of independent human review; one AI agent authored and checked the work.

Reconciliation: base 495a98ca12bae467a507031f04931aa4254b1866 on main. Read repository authority docs, searched recent issues and PRs and overlap terms STFT, spectrogram, overlap-add, projection and magnitude. Found related but different work on hidden projection dimensions (#178), switched observers (#316), commutators (#207), and all-pass magnitude (#256). Search is not proof of novelty. Issue-scoped branch and files only. Local Git remote lookup failed DNS; full repository validation and native Node checkout not run. No central data, manifest, protocol or accepted claims changed.

Background metadata/abstract inspected 24 November 2026: Daniel W. Griffin and Jae S. Lim, "Signal estimation from modified short-time Fourier transform", IEEE TASSP 32(2), 236–243 (1984), DOI https://doi.org/10.1109/TASSP.1984.1164317, publisher abstract: least-squared mismatch between modified STFT and STFT of a reconstructed signal. Abstract only, no full-text priority audit. This provides context for modified-transform consistency; all results above are self-contained derivations for the toy.

Potential exaptations: graph-aware mask authoring, consistency budgets in redundant feature editors, local patch reconciliation in overlapping procedural tiles, and a synthesizer in which intentionally impossible local requests generate a discrepancy waveform. These are design hypotheses, not evidence of efficacy.
