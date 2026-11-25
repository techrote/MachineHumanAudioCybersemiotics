# The Filter That Needs Its Lost Bits

Refs #462. Exploratory, synthetic-only mathematics and artistic apparatus. No formal Track E/G claim, corpus change, listening result or production requirement.

## Contract and usage

A ring of N binary input cells x is transformed by t synchronous steps of D=I+S over GF(2), where S rotates a word one position toward increasing cell indices. The receiver knows the complete exact transformed word y=D^t x and some **original** input bits at preselected distinct physical positions ("pilots"). Up to e pilots can be erased, with the missing positions known. The question is the minimum number of pilots needed to recover every x for every such erasure. No output erasures, bit substitutions, unknown rotation or lossy audio channel are modelled. Index 0 is the least significant bit.

```sh
node verify.cjs
python independent.py
```

The CommonJS module exports params(n,t), evolve(n,t,x), compile(n,t,e), decode(n,t,y,observations). Words are BigInt; n=1..512, t=0..1e9, e=0..n. Compile returns status ok plus physical pilot positions, dimension, distance, minimum, or status impossible. Decode accepts distinct [index,0|1] pairs; returns unique with x, ambiguous, or inconsistent. The decoder is Gaussian elimination on the full system, not an erasure-correction claim for unknown bit flips. Evolution uses binary powers of D via Frobenius, requiring logarithmically many rotations in t. The compiler does not enumerate states; decoder uses a dense bit matrix.

Example: compile(8,3,2) returns seven pilots; compile(8,3,4) is impossible. Decode with any up-to-two pilot losses recovers the source when the complete output is correct.

## Sharp budget

Let P be the largest power of two dividing N, d=min(t,P), r=e+1. When d>0 let p be the largest power of two not exceeding d. The kernel dimension is d and its minimum nonzero Hamming weight is N/p. If d=0, no pilots are required, regardless of e. Otherwise recovery is impossible when r>N/p. For feasible cases the exact optimal number is

- r=1: d.
- d=p or r even: rp.
- p<d<2p, r odd and r>=3: rp+p-b, where b is the smallest power of two at least 2p-d.

In particular one-erasure recovery requires precisely 2p pilots, where feasible. Even required distance r has a simple packing solution; odd r can require a positive surcharge. N=8,t=3,e=2 gives p=2,b=1 and a minimum of seven, not six. N=8,t=3,e=1 gives four. At N=16,t=7,e=2, the minimum is fifteen; at N=16,t=5,e=2 the minimum is twelve. The count is for distinct input positions, not repeatedly transmitting one position over multiple channels.

## Proof of dimension and distance

Represent the ring as GF(2)[z]/(z^N+1), where D multiplies by z+1. Write N=P*m with m odd. Since z^m+1 has a simple root at 1 and z^N+1=(z^m+1)^P, the greatest common divisor of (z+1)^t and z^N+1 is (z+1)^d. A polynomial representative lies in the kernel iff it is divisible by (z^N+1)/(z+1)^d; this gives dimension d. If d=0 the operator is identity (t=0). For d>0 the kernel equals ker D^d.

Let Q be the smallest power of two at least d. Q divides P and N. Since D^Q=I+S^Q and d<=Q, every kernel word is periodic with period Q (not necessarily least period). Conversely a repeated Q-word is killed by D^d exactly when the Q-word is divisible by (z+1)^(Q-d). Thus the problem reduces to a repeated short code.

If d=p, every p-bit block is admissible, so minimum nonzero weight is N/p. Otherwise Q=2p. Write a Q-word as two p-bit halves a,c. As z^p=1 modulo (z+1)^(Q-d), membership is equivalent to the pair sum w=a+c being divisible by (z+1)^(Q-d) in the length-p ring. This is the kernel of D^(d-p) there. In particular (a,a) is always allowed; no singleton Q-word is allowed since Q-d>0. The minimum weight on Q is therefore exactly two, and repeating gives N/p.

## Proof of the optimal pilot budget

Distinct inputs with the same output differ by a nonzero kernel word. A set of pilots tolerates e arbitrary erasures iff the minimum Hamming weight of any nonzero kernel word restricted to the pilot positions is at least r. Even the complete set cannot exceed N/p; this proves the feasibility threshold. For r=1 the rank lower bound is d. The first d consecutive physical positions suffice: a kernel difference that is zero there must be zero everywhere, by the monic binary recurrence D^d k=0 with both endpoint coefficients one. (If d=N the full input is selected.)

For d=p, kernel words repeat an arbitrary p-word. Every residue class modulo p must have at least r observed physical positions, and choosing exactly r is sufficient.

For p<d<2p use Q=2p. Let A_i,C_i be the counts of selected physical pilots in residues i and i+p modulo Q. Each count is at most N/Q. The kernel contains a word supported on just that pair of residues, so A_i+C_i>=r for every i. Moreover for a nonzero allowed pair-sum w, the least observed weight among words giving that w is sum_{i in supp(w)} min(A_i,C_i): at each active pair pick the cheaper side and at inactive pairs pick neither. Hence these pair and pair-sum inequalities are necessary and sufficient.

For even r choose A_i=C_i=r/2. Every nonzero w has weight at least two, as Q-d>0. This gives the lower bound rp with equality.

For odd r=2h+1>=3, every pair costing exactly r has min(A_i,C_i)<=h; call such a pair cheap. A weight-two pair-sum w supported on i,j is allowed iff (z+1)^(Q-d) divides z^i+z^j. For i!=j, its multiplicity at z=1 is the largest power of two dividing |i-j|, by factoring the odd exponent after Frobenius. Equivalently i,j are congruent modulo b=ceilPowerOfTwo(Q-d). Thus two cheap pairs in the same residue class violate distance r. At most b of the p pairs can cost r; the other p-b must cost at least r+1. This yields rp+p-b.

Construct exactly one cheap pair per class (indices 0..b-1), with counts h,h+1, and make all other counts h+1,h+1. Pair words meet the bound; weight-two pair sums have at least one high pair so cost at least r. Pair sums with weight at least three have cost at least 3h>=2h+1. No singleton pair sums exist. The construction fits the available repeats because r<=N/p=2N/Q and r is odd, so h+1<=N/Q. This attains the bound. The separate r=1 case is essential.

## Negative cases and experiments

- Cardinality alone is not enough. N=8,t=3, observing positions 0,4,1 leaves ambiguity even without erasures, despite three pilots equalling the kernel dimension.
- Six pilots at N=8,t=3 do not guarantee two erasures. Example set 0,1,2,3,6,7, erased 0 and 1: kernel word 0x33 is invisible. Seven pilots omitting only 4 suffice. This is a strict surcharge beyond the pair-support packing lower bound.
- A singleton output at t=1 is inconsistent with every input. Decoder refuses it.
- A single impulse at N=16 dies at t=16; at N=17, t=16 leaves two ones. One extra zero cell can change the entire future. A different boundary condition or update rule is outside the proof.
- For t>=P no additional dimension is lost, although the output may continue evolving. A complete transformed word must be known; unknown bit substitutions or observation errors invalidate the stated guarantee.
- Original stereo PCM16 pulse sonifications: shared-future.wav follows 0x96 and 0xa5 on N=8 through t=0..3, yielding identical final 0x55. one-extra-cell.wav compares impulse evolution on N=16 versus 17 through t=16, padding the shorter frame with one silent slot. Both use a shared 440 Hz envelope/pulse mapping at 16 kHz and no separate normalization. Renderer generates WAVs locally; source plus hashes are committed rather than large binaries. Audio is an arbitrary artistic rendering, not a validated human code, filter listening test or evidence of cognition.

## Verification and provenance

V8 execution of original compiler and test functions: 52 ring/depth combinations (N=1..12, t=0..P+1), 39,790 transitions against iterative single-step XOR, 39,790 exhaustive physical pilot subsets, 408 erasure contracts (264 feasible and reconstructed with one deterministic input and erasure choice each, 144 impossible), 872 nonzero kernel members, three strict odd-distance surcharges and five invalid-input refusals. For every feasible contract all kernel words are checked against the compiled mask, covering every allowed erasure subset logically. The exhaustive budget oracle computes minimum restricted Hamming weight for every candidate mask, not the compiler formula.

Separate native Python 3.13.5 direct-cell oracle reproduces all census totals (264 is the number of feasible contracts, not native decoder runs). Two consecutive renders reproduced both WAV hashes, PCM peaks below clipping. JS tests ran in V8, not native Node CLI. Local git ls-remote failed DNS resolution for github.com; full native repository qualification unavailable. Native Python source and result blob identities verified against GitHub. Independent human review pending.

Background: Stephen Wolfram, *A New Kind of Science*, chapter 6 section 4 note (a), p.951, [Additive cellular automata in finite regions](https://www.wolframscience.com/nks/notes-6-4--additive-cellular-automata-in-finite-regions/), public HTML note text checked 2026-11-25, explicitly gives the cyclic Rule 60 polynomial representation and Frobenius relation; refers to Martin, Odlyzko and Wolfram's earlier analysis. This is background for established algebra, not a source of the pilot-budget theorem. Mathematical derivation here is self-contained, no priority claim or systematic novelty search. No source figures, text extracts or third-party audio copied. AI-assisted original code, mathematics, and synthetic verification; no external peer review.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; README, AGENTS, RAG, programme, runbook, integrity and validation reviewed; recent open PR/issue titles and targeted Rule 60/cyclic XOR/repeated-root searches and branch-name search inspected. No matching pilot optimizer located, not exhaustive. Scope is entirely new files under research/expeditions/xor-pilot-462. Prior median scheduler expedition differs (nonlinear majority endpoints, not linear cyclic difference kernels). No change to frozen records or shared manifests. Potential exaptation: binary rhythmic transformations with retained audit bits, constrained reversible debugging, cellular rule regression, synthetic tests of the difference between uncertainty dimension and fault-tolerant observation cost. These are prospective transfers, not tested products or Brier-derived predictions.
