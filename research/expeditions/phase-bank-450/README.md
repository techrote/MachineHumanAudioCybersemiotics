# The Quantizer That Borrows Its Neighbours' Phase

Refs #450. Synthetic mathematical expedition, 2026-11-25. Base: 495a98ca12bae467a507031f04931aa4254b1866. AI-generated research apparatus and self-review; no external review, hardware test, human trial, or evidence-register claim. No central/frozen files changed.

## Model and exact aggregation

Let M >= 2 be an integer modulus, n >= 1 the number of lanes, s_j in [0,M-1] their integer initial residues and a_t in [0,M] their common integer increment at each tick. Each lane emits the quotient bit b_j = floor((s_j+a_t)/M) and updates its residue to (s_j+a_t) mod M. All lanes share a clock, identical input and exactly observed, equally weighted carries. The state is not reset between ticks. Let C_t be the sum of increments through tick t, with C_0=0.

Compile s_j=floor(j*M/n), j=0,...,n-1. Repeated phases are allowed when n>M. The cumulative count of one lane is floor((C_t+s_j)/M), by telescoping its residue recursion. Write C_t=qM+r. For integer r, floor(j*M/n)>=M-r iff j>=ceil(n*(M-r)/M). Thus the number of extra carries is n-ceil(n*(M-r)/M)=floor(n*r/M). Therefore:

    sum_j floor((C_t+s_j)/M) = floor(n*C_t/M).

In particular the full bank exactly emulates a single integer accumulator with increment n*a_t and modulus M, whose quotient may exceed one. For every contiguous window with increment sum A, its emitted count is floor(n*C_end/M)-floor(n*C_start/M), either floor(n*A/M) or ceil(n*A/M). The absolute discrepancy from n*A/M is strictly less than one carry, independent of window length. Per-lane mean discrepancy is <1/n. Aligned phases, by contrast, may have absolute aggregate discrepancy arbitrarily close to n when M is large. This is an exact count statement, not a claim of an analog or broadband SNR improvement.

## Sharp fixed-erasure minimax theorem

Fix a window with A=qM+a, 0<=a<M. Every lane emits q plus a carry indicator for whether its starting residue lies in the circular interval of length a ending at M. Permit any e of the n lanes to be absent throughout that window, 0<=e<n. Let s=n-e. Consider all common rotations of the initial layout (reachable by admissible preceding input, e.g. one increment), all such fixed erasure subsets. For the residual count X after removing the baseline s*q:

    L=max(0,floor(n*a/M)-e)
    U=min(s,ceil(n*a/M))

These bounds are the best simultaneous achievable worst-case lower and upper endpoints over all layouts. For an arbitrary phase multiset, the total indicator count K averaged over the M rotations is n*a/M, because each lane belongs to the interval in exactly a rotations. Therefore some rotation has K<=floor(n*a/M), and some K>=ceil(n*a/M). At a given rotation the exact survivor endpoints are max(0,K-e) and min(s,K), obtained by deleting carriers or noncarriers first. This proves that no layout has a better lower or upper guarantee. The compiled layout's all-window identity gives K=floor(n*a/M) or ceil(n*a/M) at every rotation; averaging ensures both endpoints occur (or coincide). Thus the same layout attains both optimal endpoints simultaneously for every a,e, including a=0. Its sharp worst absolute residual discrepancy from s*a/M is max(s*a/M-L,U-s*a/M); subtracting s*q from all counts does not change the discrepancy. Also, for a fixed absent subset, the full bank discrepancy minus the e omitted lane discrepancies has absolute value <e+1 over every window. The exact bounds can be tighter.

This is a minimax claim over arbitrary common phase rotation and unknown fixed erasures, not a probability model or a claim about one particular constant-increment orbit, whose accessible rotations can be fewer. Exact erasure guarantees do not imply that missing channels can be identified.

## Exact contract for a family of increments

For each requested a, constant aggregate count across every rotation requires n*a/M to be an integer (average argument). For a collection A, the condition is equivalent to n being a multiple of M/gcd(M,A...). The same compiled layout attains exactness for every such increment whenever that condition holds. Hence M/gcd(M,A...) is the minimum lane count. This holds even under arbitrary temporal ordering of the specified common increments. It does not require exactness in each individual lane. With M=64, A={8,24,40}, eight lanes suffice; including increment 1 requires 64 lanes.

## Executable negative cases and audio

With M=8, four phases [0,2,4,6] and common increment 2, one lane carries every tick. A moving erasure that deletes precisely that lane produces zero observed carries forever, whereas deleting a noncarrier gives one forever. Both use the same erasure count of one but accrue linear discrepancy from the nominal survivor expectation 3/4 per tick. The fixed-set bound cannot apply to arbitrary per-tick changing subsets. The per-tick endpoints still apply. Unequal input increments [7,1,0,0] from these phases give no carries, unlike shared [2,2,2,2], despite equal summed input. State perturbations, clock mismatch, saturation rather than modulo, unequal weights, and analog mismatch are outside the model.

Run from this directory with Python 3.13.5 (standard library only):

    python verify.py run > results.synthetic.json

The direct membership oracle enumerates 6,420 multisets for M=2..8, n=1..6, checks 236,643 layout/residue/erasure cases, explicitly enumerates survivor subsets in 3,391 smaller cases, checks 45,003 layout/residue constant-contract conditions (implication when constant), and simulates 205,920 windows of seeded variable streams. These are distinct categories of checks, not independent human reviews. The JSON and two WAVs reproduced byte-for-byte on two executions. Native repository checkout was attempted but DNS resolution failed; standalone tests are not full-repo qualification.

Audio uses 64 residue positions, eight lanes, shared increment 24, 16 kHz, two seconds. Aligned vs staggered renders raw count error relative to 3, divided by 8, with a common PCM scale of 12000. Right is exactly zero. Fixed vs moving loss renders absolute cumulative discrepancy from 21/8 carries per tick as the amplitude of an original 440 Hz sinusoid, scaled by the sample rate and capped at unity. Fixed loss final discrepancy is zero, moving loss -20,000 carries. WAV peaks (absolute PCM): first 7500/0, second 1/12000. No clipping. The latter is an artistic mapping of accumulated mathematical debt, not a direct physical output of the quantizer, nor evidence about hearing or communication.

## Provenance and exaptation

The accumulator is a classical first-order carry/PDM primitive, and evenly distributed floor sequences are related to balanced mechanical words. Background, not a priority claim or a systematic literature review:
- https://en.wikipedia.org/wiki/Pulse-density_modulation (Algorithm, discovery-level background).
- Gabriele Fici, On the Structure of Bispecial Sturmian Words, arXiv:1311.4904 (abstract consulted for balanced words/Christoffel context): https://arxiv.org/abs/1311.4904 .
- Ingrid Daubechies and Rayan Saab, A Deterministic Analysis of Decimation for Sigma-Delta Quantization of Bandlimited Functions, arXiv:1506.00179 (abstract consulted; adjacent quantization/decimation context, not evidence for these formulas): https://arxiv.org/abs/1506.00179 .

The proofs above are self-contained; no novelty priority claim. Live intake checked the repository README, agent instructions, RAG, programme, runbook, recent open issue inventory and targeted issue keyword searches (pulse density, sigma-delta, accumulator, quantizer, balanced words, interleaved, error feedback). No duplicate surfaced; coverage not exhaustive.

Potential transfers: staggered pulse-density banks for digital instruments; bounded-discrepancy event delivery to simulation workers; multiplexed equal-weight counters; fault-tolerant emission schedules; acoustic encodings whose residual indicates violations of a shared clock/input or fixed-erasure assumption. A deliberately moving erasure could serve as a compositional control that breaks the bounded-debt contract. Hardware duty cycle, timing, analog reconstruction, spectral shaping and listening claims require separate qualification. The count discrepancy objective is not a universal optimum for spectrum, noise, or perceptual outcome.
