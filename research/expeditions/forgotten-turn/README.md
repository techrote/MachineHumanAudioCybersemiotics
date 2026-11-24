# The Turn That the Samples Forgot

Synthetic expedition, 2026-11-24, Refs #272. Base 495a98ca12bae467a507031f04931aa4254b1866. AI-assisted mathematical derivation, implementation and self-check by ChatGPT; no human review, participants, live empirical records or claim of priority. This folder alone is owned by the expedition.

## Contents

1. [Phase is not winding](#1-model-phase-is-not-winding) — define exact observations and the hidden signed lifts.
2. [Exact winding range](#2-exact-winding-range-multiplicity-and-minimax-lift) — derive range, multiplicities and optimal common slew.
3. [Fractional probes](#3-a-second-instrument-fractional-probes-as-a-residue-code) — plan minimum-cardinality diagnostic sampling with bounded phase error.
4. [Topological obstruction](#4-a-topological-obstruction-to-hiding-the-difference) — distinguish continuous morphs from sample equality.
5. [Reproduction](#5-reproduction-and-evidence) — executable checks, audio receipt and limitations.
6. [Provenance](#6-provenance-and-exaptation-boundaries) — source access and explicitly conditional applications.

## 1. Model: phase is not winding

Take M integer ticks per turn, N cyclic observations p_i in [0,M-1], with p_N=p_0. Observations are exact modulo M. Each edge i lasts one normalized interval and admits a signed net lift d_i bounded by |d_i|<=B_i. A continuous lift with instantaneous slew at most B_i exists for every admissible d_i (linear interpolation suffices); conversely integrating such a bound implies the net constraint. Arbitrary admissible paths need not be linear and may reverse within edges. Multiplicity below counts integer edge-increment vectors, not continuous trajectories or probabilities. All edges, including closure, are part of the model.

For M=16 and p=[0,6,12,2,8,14,4,10], every edge residue is 6. Constant signed increments 6, -10 and 22 give respectively +3, -5 and +11 turns around the full eight-edge ring. The recorded observations are identical. This is a constructive form of ordinary aliasing, extended here to independently constrained nonuniform increments.

## 2. Exact winding range, multiplicity and minimax lift

Let r_i=(p_{i+1}-p_i) mod M, chosen in [0,M-1]. Every admissible increment is r_i+M k_i where k_i is an integer in [l_i,h_i], with l_i=ceil((-B_i-r_i)/M) and h_i=floor((B_i-r_i)/M). If any interval is empty the observations and budgets are inconsistent. Otherwise W0=sum(r_i)/M is integral by telescoping modulo M. The full winding W=W0+sum(k_i) ranges from W0+sum(l_i) to W0+sum(h_i). Every intervening integer is attained: start with all lower endpoints and spend a requested excess greedily across the independent intervals. This proves necessity, sufficiency and the witness construction. The range and witness take O(N) arithmetic steps; no enumeration.

The polynomial product of (1+x+...+x^(h_i-l_i)) over edges gives the multiplicity at exponent W-W_min, by independent choices. Sliding-window convolution computes exact BigInt coefficients. A configurable cumulative cell budget refuses the histogram without forfeiting the exact feasible range. Counts are not calibrated probabilities. Unique feasible winding means all edge intervals are singletons, but does not identify the continuous between-sample path.

Under a common budget B, attainable target windings expand monotonically as B increases. Integer bisection plus the witness construction gives the least common slew bound. Implementation caps M at 10^6, N at 4096 and B at 10^9; outside supported budget is not impossibility over unbounded integers. Within those caps sums and division bounds are safe JS Number integer arithmetic, and combinatorial counts use BigInt.

For the eight-edge example, B=6 or 7 forces W=3; B=10 admits all W=-5..3; B=22 admits W=-5..11, with 6561 increment vectors. Budget 22 on edges 0 and 4 only, and 6 elsewhere, admits W=1..5 with counts 1,2,3,2,1. At M=16, observations [0,8] and budgets [8,8], exact antipodal ties allow windings -1,0,1; do not silently choose the positive or negative branch. General flat family: N identical observations and B=KM have (2K+1)^N lifts, all W=-NK..NK.

## 3. A second instrument: fractional probes as a residue code

This extension assumes an exactly affine lifted phase on the edge, with exact anchor observations and known duration. Let a=p_i, r=r_i and k in a contiguous integer interval [l,h] of width w=h-l+1. A phase probe at fraction 1/q of the interval (integer q>=2) returns, in units of 1/q tick, the residue

    y=(q*a+r+M*k) mod (q*M).

Distinct k modulo q give a regular q-point constellation. Any bounded circular phase error strictly smaller than M/(2q) physical ticks permits unique decoding of k mod q; implementation takes integer measured numerator and integer error numerator e with 2e<M. Equality is not guaranteed: halfway between two neighbouring constellation points is compatible with both.

For multiple probes, two integers give identical residue signatures iff their difference is divisible by every denominator, equivalently their least common multiple L. A contiguous interval of width w is identified iff L>=w. If L<w, l and l+L collide. This is the elementary generalized Chinese remainder uniqueness principle. It does not require pairwise coprimality. No error correction across wrongly decoded residues is promised.

Breadth-first search over attainable LCM states gives a minimum-cardinality subset of an allowed denominator catalogue. Denominators already used need not be tracked: any q dividing the current LCM adds no information, and all other q remain available. The first state reaching L>=w is optimal. An exhausted state budget is distinct from a complete search proving impossibility. Denominators are bounded by 64 and width by 10^6 in this implementation. The decoder intersects congruences by bounded direct enumeration and distinguishes zero, one or multiple candidates.

A single noiseless arbitrary phase probe at fraction 1/w separates all w candidates equally (w>1). Any w points on a circle of circumference M have minimum separation at most M/w by summing consecutive gaps; thus this probe also optimizes worst-case single-probe circular separation. Its guaranteed error radius is strictly less than M/(2w), sharp over arbitrary circular observation errors. Multiple probes can trade additional measurements for much larger per-measurement error margins. For M=120, w=41:

| Largest permitted denominator | Minimum probes | Example denominators | LCM | Sufficient common error radius, strictly below |
|---:|---:|---|---:|---:|
| 4 | impossible | none | - | - |
| 5 | 3 | 3,4,5 | 60 | 12 ticks |
| 7 | 2 | 6,7 | 42 | 60/7 ticks |
| 41 | 1 | 41 | 41 | 60/41 ticks |

The 3-probe and 2-probe designs are minimum cardinality for the stated catalogues; lower denominator caps express error robustness. The guaranteed radii are sufficient for separate residue decoding, not a claim of globally optimal joint decoding under every possible noise model. Nested dyadic probes restricted to q=2,4,8 cannot identify 100 candidates because their LCM is only 8. A more general rational probe j/q with coprime numerator gives the same congruence information and is not needed here.

Critical falsifier: without affine motion, two paths with anchors zero and a zero midpoint can differ by one complete turn. One remains zero; another remains zero on the first half and rotates once on the second half at normalized slew 2M. Both obey B=2M. Thus midpoint probing does not identify winding merely from a slew bound; do not use the residue decoder on arbitrary trajectories, drifting clocks, noisy anchors or unknown phase dynamics. Timing errors and noise in anchor/residue estimates are not modelled.

## 4. A topological obstruction to hiding the difference

Suppose the two periodic unit-complex curves exp(3 i theta) and exp(11 i theta) are endpoints of a continuous complex-valued morph F(theta,t), periodic in theta for every t. If F never vanishes, F/|F| is a homotopy of circle maps, so winding is constant: on the parameter rectangle the phase lift is continuous and its endpoint difference divided by 2 pi is a continuous integer as t varies. But 3 != 11, a contradiction. Every such morph must contain a zero. Linear complex crossfade realizes this: cancellation requires equal weights t=1/2 and exp(8 i theta)=-1, exactly eight distinct points in one full period. In contrast the phase-offset morph exp(i*(3 theta+t phi)) has equal winding and never vanishes. Finite sampled plots can miss zeros; the theorem concerns continuous nonvanishing interpolation with periodic boundary conditions. It is not a statement about human hearing, arbitrary real audio or the number of zeros in all possible morphs.

## 5. Reproduction and evidence

Run from this directory with Node supporting ES modules and BigInt (native Node entry point pending):

    node verify.mjs > /tmp/forgotten-turn.txt
    diff -u results.synthetic.txt /tmp/forgotten-turn.txt
    node verify-probe.mjs > /tmp/forgotten-probe.txt
    diff -u probe-results.synthetic.txt /tmp/forgotten-probe.txt
    python3 render.py run

The JS core and direct brute-force oracle executed in V8, then were fetched back from GitHub and rerun after removing only module boundary statements and replacing the final console output with return. Both resulting receipts matched committed bytes exactly. Tests: 4454 lift cases (including 550 deterministic nonuniform cases), 12135 target-count and witness checks, 2750 minimax checks with independent bounded increment enumeration, 155 flat-family checks; 12800 fractional-probe plans compared with exhaustive subsets and explicit residue signatures, 32835 bounded-error observations, 3240 residue-system recoveries. A 3^80 count exercises arbitrary precision. Budget refusal, antipodal tie, impossible and inconsistent cases retained.

Python stdlib audio renderer executed locally twice; exact WAV and manifest bytes agreed. Tested Git blob identities for renderer and manifest are 556cf1fa5db819309786de5e93774d3bd5235a7c and 52191a4b7c86092454263e39fa5ac86c8c4722d8. A two-second stereo 16-kHz PCM16 render uses 150 and 550 Hz with identical common endpoint fades, an integer phase lookup table, and 400-Hz anchor sampling. All 800 anchor sample pairs match exactly; all 800 midpoint sample pairs differ. 31199 of 32000 full-rate PCM pairs differ. This is a synthetic equality counterexample and original audio, not human listener evidence. Real PCM is only a projection of the underlying complex phasor; the lift theorem uses exact phase observations, not phase inferred from these real samples. WAV generated locally, not committed; regenerate from the renderer. Cross-platform last-bit waveform equality is not guaranteed by floating-point sine.

All result receipts use .synthetic.txt rather than registered JSON records. No protocol amendment, central record, participant evidence, shared manifest, production code or license change. Network DNS from local container prevented clone; repository-wide native checks and independent reviewer remain pending. GitHub repository CI is structural, not a substitute for executing the expedition verifiers.

## 6. Provenance and exaptation boundaries

Accessed 2026-11-24 by ChatGPT via web. No source text copied into the repository; no paid or restricted materials used. The mathematical results above are derived explicitly here and should be treated as small applications/rediscoveries of familiar mathematics, not priority claims.

- University of Maryland, [Aliasing and Digitization](https://www.physics.umd.edu/hep/drew/fourier/aliasing_digitization.html), HTML section Aliasing, read the sampling equation and frequency discussion. Context for sinusoid aliasing, not a source for the new bounded-edge tool.
- Sound Open Firmware, [Phase Vocoder Architecture](https://thesofproject.github.io/latest/developer_guides/firmware/phase_vocoder.html), HTML Phase Unwrapping Arithmetic section excerpt and architecture overview. Context for circular phase tracking; no claim that this toy improves SOF.
- Allen Hatcher, [Algebraic Topology chapter index](https://pi.math.cornell.edu/~hatcher/AT/ATchapters.html), 2002 book bibliographic pointer, chapters 1 and 2; index accessed, book not close-read. The winding argument above is supplied independently.
- [Chinese Remainder Theorem, solution for not coprime moduli](https://gh.cp-algorithms.com/main/algebra/chinese-remainder-theorem.html), HTML section excerpt accessed; background on LCM and inconsistent residues. Derivation above proves the needed uniqueness directly.
- Li Xiao, Xiang-Gen Xia and Yu-Ping Wang, [Exact and Robust Reconstructions of Integer Vectors Based on Multidimensional Chinese Remainder Theorem (MD-CRT)](https://arxiv.org/abs/2002.00087), 2020 preprint abstract inspected only. Explicitly mentions phase unwrapping and sub-Nyquist frequency estimation. This is a novelty-overlap lead, not a primary-text review or evidence for a superior estimator.

Candidate transfers: a winding-aware gesture editor, phase-continuity diagnostics for oscillator morphs, a probe planner for deliberately restricted constant-rate encoders, and adversarial tests of sampled agent trajectories. The code cannot infer arbitrary hidden histories; bounded net motion, continuous motion, and affine motion are distinct assumptions. Next falsifiers: correlated anchor uncertainty, timing jitter, joint decoding without separate residue certainty, nonaffine motion with bounded acceleration, and sample-budget optimization under these broader models. None are solved by this expedition.
