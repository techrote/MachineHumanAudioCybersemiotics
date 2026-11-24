# The Mixer That Clips Silence

**Refs #312 · 24 November 2026 · AI-assisted original formal/synthetic expedition.**
Base inspected: 495a98ca12bae467a507031f04931aa4254b1866. No Track E/G evidence, production mixer, validated human interface or frozen-record change.

## Model and distinction

Each of n labelled leaves is an integer vector v_i in Z^d. Coordinates can be time samples, test scenarios or channels. One fixed unordered rooted full binary tree is shared by all coordinates, and each leaf occurs exactly once. No intermediate scaling, widening or duplication is allowed. Define exact subtree sums S(A) and their infinity norms w(A). The peak includes leaves and the root. For symmetric integer saturation at cap C, every input fits and each internal node computes componentwise clip_C(x+y). This is not wraparound or an asymmetric two's-complement range.

Three questions differ: can a tree avoid clipping, can a saturated tree produce the correct endpoint despite clipping, and do all saturated trees produce that endpoint? Exact endpoint is the ordinary vector sum, not a clipped target. A correct endpoint is not a certificate of clip-free evaluation.

Three leaves (1,1,-1), (1,-1,1), (-1,1,1) sum to (1,1,1). At cap 1 every possible first pair exceeds the cap at one coordinate; the remaining leaf is -1 there, so that coordinate finishes 0 rather than 1. All three coordinates are individually feasible under separately chosen sequential orders. This is a common-tree obstruction, not a scalar obstruction. In fact for scalar leaves, all partial sums can be kept within max(max_i |v_i|, |sum_i v_i|): when the current sum is nonzero choose an opposite-sign remaining term if possible. Its new absolute value cannot exceed the larger of the previous magnitude and the term magnitude. If no opposite-sign term remains, the rest is monotone to the final value. Zero admits either sign. This proof gives the scalar optimum.

## Exact compiler

For a singleton A, F(A)=w(A). Otherwise

    F(A) = max(w(A), min_{A=B disjoint-union D} max(F(B),F(D))).

Every binary tree induces such a root partition; conversely any partition and two optimal child trees give a tree. Induction proves equality. For left-deep trees constrain one child to be a singleton. Stored split choices reconstruct a witness. For a prescribed C, F(A)<=C is exactly the existence criterion for a clip-free tree. Time O(3^n + d*2^n) for free trees or O(n*2^n + d*2^n) sequential; memory O(d*2^n), ignoring integer bit length. No claim of polynomial-time scaling.

A separate endpoint recurrence uses Counter H_A over saturated vectors. For every unordered nonempty bipartition B,D and every x,y in H_B,H_D, add H_B[x]*H_D[y] to H_A[clip_C(x+y)]. Singletons have multiplicity one. By induction this counts each labelled unordered full binary tree exactly once, including repeated vector values as distinct labelled leaves. The total is (2n-3)!! (one-leaf case 1). This is not a probability distribution unless a separate uniform-tree sampling law is imposed. Explicit budget exhaustion throws BudgetExceeded, not UNSAT. Endpoint solver limited to ten leaves; peak solver to fourteen, also subject to the coordinate budget.

## Zero-sum family with unbounded required headroom

For every even n>=2, construct columns of n signs with exactly n/2 positive and n/2 negative entries. Keep one representative per global sign reversal (the first sign is positive). There are binomial(n-1,n/2-1) coordinates. Rows are leaves. Every leaf has norm 1; their total is identically zero.

For any subset A of size k, w(A)=min(k,n-k). Upper bound follows from unit entries and the zero total; for k<=n/2 a balanced column can be chosen positive on all of A, up to global sign. For k>n/2 use its complement. Thus every sequential order has peak n/2 because it visits every prefix size.

Claim: free binary trees have exact optimum m=ceil(n/3). For the lower bound descend from the root, which has size n>n-m, along any child of size >n-m until neither child exceeds n-m. The node cannot be a leaf and has at least n-m+1 leaves. If both children had fewer than m leaves, they would have at most 2(m-1) together, which is less than n-m+1. Therefore some child has size between m and n-m, so its norm is at least m. For the upper bound partition the leaves into three nonempty groups of size at most m (n=2 is immediate); build each group arbitrarily, merge two groups, then merge with the third at the root. All nodes within groups have size at most m, the two-group node has complement of size at most m, and the root is zero. This attains m.

So a zero-output, unit-input mixer can require arbitrarily large intermediate range even under optimal scheduling. The dimension increases combinatorially with n, so this is not an unboundedness claim at fixed dimension. The improvement of the free tree over sequential ordering is real but bounded (ratio at most 1.5 for this family).

For n=4 the leaves are (1,1,1), (1,-1,-1), (-1,1,-1), (-1,-1,1). Every pair has norm 2. Under C=1 all trees clip, but the three balanced pair-pair trees return exactly zero: their pair sums are negatives and symmetric saturation is odd. The twelve unbalanced trees return signed unit residuals. The executable census verifies multiplicities. This is the central falsifier: even perfect output nulling can conceal mandatory internal clipping.

## Synthetic qualification and audio

Run `python verify.py` (without -O) in this directory, Python standard library only. The independent direct oracle enumerates labelled trees through combinations and replays each exact and saturated tree, rather than merging endpoint states; it independently exhausts permutations for the sequential comparison. This is algorithmic cross-checking by the same agent, not independent human review. Census includes all multisets of n=2..6 leaves from the eight 3-D sign corners whose final norm is <=1. Duplicates are distinct labels in tree counts. 204 configurations, 39,364 tree topologies replayed in both arithmetic modes and 35,096 sequential permutations. All comparisons passed. 146 admit a clip-free tree, 26 more admit the correct endpoint only through clipping, 32 admit no correct endpoint at cap 1. Four have all endpoints correct. No free-tree advantage in that restricted census; the separate balanced family first shows a strict advantage at n=6. Family checked through n=12. Refusals for invalid coordinates, duplicate leaves, inadequate input cap and exhausted budget were checked.

The executable creates run/results.synthetic.txt (full histograms for selected witnesses, per-population counts and WAV manifest) and two original stereo PCM16 files. three-voices.wav compares exact versus saturated addition of the three-leaf example. silence-that-clips.wav compares balanced and sequential trees on the four-leaf zero-sum example, both saturated. A time block per vector coordinate uses a common enveloped integer carrier times the corresponding leaf sign. Cap=12000, sample rate=16000, 19200 frames per file. These are actual sample-by-sample arithmetic demonstrations, not human listening data. In the second file the left channel is identically zero, the right has 4143 nonzero samples. The first file also has 4143 differing sample pairs. Both runs produced identical file hashes on Python 3.13.5 in this environment; cross-platform transcendental rounding is not promised. Generated binary files are not committed; the renderer and compact receipt are. No human subjects.

## Provenance, exaptations and boundaries

[Arm CMSIS-DSP v1.14.3, Vector Addition, arm_add_q15, Scaling and Overflow Behavior](https://arm-software.github.io/CMSIS-DSP/v1.14.3/group__BasicAdd.html), retrieved visible documentation section on 2026-11-24, establishes that the concrete library uses saturating vector addition; its asymmetric range differs from our symmetric model. [Imre Bárány, A matrix version of the Steinitz lemma, 2024, abstract](https://discovery.ucl.ac.uk/id/eprint/10191140/), DOI 10.1515/crelle-2024-0008, retrieved repository metadata and abstract only, places the sequential zero-sum rearrangement problem in established Steinitz theory. No full-paper reading or mathematical priority is claimed. The binary-tree recurrence, family proof and audio are self-contained constructions in this expedition, not a novelty claim about the literature.

Possible applications: offline headroom optimization for small fixed-point audio graphs; shared summation order across test samples or channels; synthetic DSP fixtures to distinguish true zero from clipping-induced cancellation; mixed-precision accumulator planning; testing whether a reducer's correct final result hides forbidden intermediate states. No guarantee for arbitrary future signals, bounded-width overflow during the solver, fixed dimension, noncommutative operations, or hardware with other rounding/saturation policies. Wide accumulation, summing each coordinate separately, or adaptive reassociation changes the problem and may remove the obstruction. Treat these as engineering hypotheses, not validated transfer.

One ChatGPT agent produced the proof, Python implementation, local tests and synthetic audio. Locally tested source blobs match committed Git blob identities. Full repository checkout was blocked by DNS in the execution container; repository-wide validation and independent review pending. No frozen record edited. Draft review requested.
