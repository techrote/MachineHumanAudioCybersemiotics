# The Clock That Cannot Keep Four Friends

Refs #801, #796/#797, #792/#793. Exploratory mathematics and synthetic software, 27 November 2026. One ChatGPT agent; no independent mathematical review, scientific-priority claim, physical transmission or human data. Outside frozen Track E/G. No canonical evidence changed.

## Contract and question

An indexed pilot x of length N+K-1 yields K consecutive candidate phase words x_s(t)=x(t+s), t=0,...,N-1, s=0,...,K-1. The scalar alphabet is the ordered grid {0,...,q-1}. The channel is a fixed unknown strictly monotone function with either polarity; different competing phase explanations may have different functions. We use exact equality and ordering, not Euclidean distance, and coherent indices. The preceding plateau-limited reduction (#796) permits the same conclusions for q effective levels if the physical grid has at least (q-1)B+1 positions, where each unknown monotone plateau contains at most B complete-grid levels, using guard spacing B.

For two phase words, form the q by q contingency matrix W counting paired symbols. Their maximum compatible-subset cardinality L(W) is the largest mass of a chain of cells strictly increasing in row and strictly increasing OR strictly decreasing in column, with the entire mass of each selected cell allowed. This is precisely maximum agreement under two legal channel maps: matching output levels must be strictly ordered in both axes (up to reversal); conversely a finite ordered matching can be extended by interpolation to strictly monotone relabelings. Define L(x) as the maximum L(W) over phase pairs and L*(N,K,q) as its minimum over pilots. The sharp Hamming discrimination distance is N-L(x); universal correction is exactly 2e+f<N-L(x) with e arbitrary substitutions and f flagged erasures.

The predecessor found a ten-symbol ternary pilot for N=8,K=3 with L=2. Can it be repeated? Can more phase hypotheses coexist at the same relative distance? This is a packing problem, not a mere pairwise separation problem.

## General alphabet: a sharp two-phase chain-cover theorem

For q>=2, partition the square grid into the diagonals j-i=k for k=-(q-2),...,(q-2), and the final decreasing pair {(0,q-1),(q-1,0)}. These 2q-2 disjoint chains cover every cell. The sum of their masses is N, so one chain has mass at least ceil(N/(2q-2)). This applies to any pair, not just shifted words, and therefore

    L*(N,K,q) >= ceil(N/(2q-2)).

It is sharp in relative terms for K=2. Give every perimeter cell of the square grid unit mass and every interior cell zero. Any strict monotone chain contains at most two perimeter cells: a boundary cell lies in the first/last row or first/last column, and hence must be an endpoint of that chain. A chain containing two boundary cells exists. Total mass is 4q-4 and maximum chain mass is exactly 2.

This pair distribution is realizable by an overlapping cyclic pilot, not merely two independent words. Make a directed graph with q vertices and one edge a->b for each perimeter cell. The graph is symmetric, balanced, and connected (each vertex communicates with 0). An Euler tour uses every edge exactly once. Emit its successive source labels. Cyclic adjacent-pair counts equal the desired matrix. Thus for N a positive multiple of 4q-4, K=2, L*=N/(2q-2). The constructive laboratory certifies every q=2..32. It does not assert this lower bound is sharp for K>2 or every N.

## The multi-phase ternary packing theorem

Fix K>=2, q=3, and let H=K(K-1). Then the exact asymptotic ambiguity fraction for genuinely overlapping shifted pilots is

    lim_(N->infinity) L*(N,K,3)/N = lambda_K,

    lambda_K = 1/4                         for K=2,3,4,
             = 4/15                        for K=5,
             = [(K-j)(K-j-1)/2+j(j-1)]/H  for K>=6,
               j=floor((K+1)/3).

Every finite pilot satisfies L(x)>=ceil(N lambda_K). No assertion of finite achievability for all N is made. In particular the best possible relative distance approaches 2/3 as K tends to infinity, after taking the fixed-K large-N limit. Do not exchange these limits or infer a positive code rate.

**Lower bound (proof).** The maximum chain functional is convex: it is the maximum of finitely many linear chain-mass functions. It is also invariant to transposition and independently reversing either axis. Average the normalized W matrices over all ordered distinct phase pairs, and over independent reversals of their row and column labels. The resulting symmetric matrix has the form

    a b a
    b c b
    a b a

and its largest chain mass is max(2a+c,2b). Indeed the two full diagonal chains have weight 2a+c, the side-to-side chains have weight 2b, and all other chains have mass at most max(2a+c,2b), since a+b <= max(2a,2b). By convexity this maximum cannot exceed L(x)/N.

At each observation t let J be the number of candidate phase words whose symbol is the middle level 1. Among H ordered distinct pairs, J(J-1) are both middle, J(K-J) are middle/nonmiddle in a fixed orientation, and (K-J)(K-J-1) are both nonmiddle. Averaging reversals divides the latter among four corners and the middle/nonmiddle among two side cells per orientation. Hence

    A_j = [(K-j)(K-j-1)/2+j(j-1)]/H
    B_j = j(K-j)/H

and 2a+c=E[A_J], 2b=E[B_J], where expectation is just an average over observation indices. Therefore

    L(x)/N >= max(E[A_J],E[B_J]).

For K<=4 the universal chain cover gives 1/4. The distribution J=1 with probability K/4, J=0 otherwise, has E[A]=E[B]=1/4, so the relaxation is exact.

For K=5 the six possible occupancy values satisfy 2H A_j+H B_j>=16 (substitution gives a quadratic minimized at j=1,2). Therefore max(E[A],E[B])>=(2E[A]+E[B])/3>=16/(3H)=4/15. The distribution P(J=1)=1/3, P(J=2)=2/3 attains equality in both objectives. In particular a fifth candidate phase is incompatible with the old 1/4 ambiguity fraction even in an unconstrained, nonoverlapping codebook.

For K>=6 the numerator of A_j is a convex quadratic with real minimizer (2K+1)/6. The integer j=floor((K+1)/3) is a minimizer (choosing the lower in a tie). At this j, A_j>=B_j: writing K=3h,3h+1,3h+2 respectively, H(A-B) is h(h-2), h(h-1), h^2-h-1. These are nonnegative in the indicated K>=6 range. Thus A_j is a lower bound for every distribution and a point mass at j attains the relaxation. Dividing by N and taking the ceiling yields the finite lower bound. All arithmetic here is exact.

**Achievability by actual overlapping pilots (proof).** For any of the rational optimal occupancy distributions above, choose an exchangeable random K-tuple: first choose J, then uniformly choose which J coordinates are middle, and assign independent equiprobable 0/2 values to the rest. Its pair distribution for every pair of distinct coordinates is exactly the symmetric matrix with chain mass lambda_K. This is a finite rational distribution; represent it by a multiset of M words of length K with integer multiplicities. Concatenate each word repeated R times into a length N=MRK cyclic pilot. If each block were independently continued periodically at its boundary, all K-phase contingency matrices would have exactly the specified ideal counts: any two offsets differ modulo K, and the exchangeable inventory gives the same pair law at every rotation. Actual overlapping windows differ only at the final K-1 starting positions of each block, at most M(K-1) ticks. Changing one paired observation changes any chain mass by at most one. Hence

    N lambda_K <= L(x) <= N lambda_K+M(K-1).

The finite multiset depends on K, not R. For any sufficiently large requested N choose R=floor(N/(MK)), take the cyclic pilot above and extend by fewer than MK extra observation positions (and K-1 lookahead ticks). This changes L by at most MK. Therefore the upper excess is bounded for fixed K independently of N; the lower bound and the limit agree. The construction is an existence proof and an exact executable compiler for small K, not an efficient universal implementation. The length and memory requirements of the inventory can grow exponentially with K.

Some exact fractions:

| K | Optimal asymptotic L/N | Optimal asymptotic (N-L)/N |
|---:|---:|---:|
| 2–4 | 1/4 | 3/4 |
| 5 | 4/15 | 11/15 |
| 6 | 4/15 | 11/15 |
| 7–8 | 2/7 | 5/7 |
| 9 | 7/24 | 17/24 |
| 10 | 3/10 | 7/10 |
| 12 | 10/33 | 23/33 |
| K->infinity | 1/3 | 2/3 |

The K=5 obstruction is important: individual pairs can all in principle use the perimeter optimum, but requiring them to come from one family creates occupancy constraints. The lower bound is analogous to Plotkin-style finite-alphabet distance packing, with an order-orbit metric instead of ordinary Hamming equality.

## Exact short cyclic solutions

For K=3, the preceding ternary witness already consists of one eight-symbol cycle plus two lookahead symbols. Every lag one and two has the eight noncenter cells exactly once. A different eight-symbol cycle works for all K<=4:

    1 0 0 2 1 2 2 0

Every lag 1,2,3 has this exact matrix:

    1 1 1
    1 0 1
    1 1 1

Each phase-pair agreement is 2, so N=8,K=4,d=6 is globally optimal, and repetition gives N=8R,L=2R,d=6R. Universal exact correction holds when 2e+f<6R. In contrast a fifth phase forces L>=ceil(32/15)=3 at N=8. This does not prove that 3 is attainable at that length. The old four-phase cycle cannot be used for an unrestricted offset vocabulary; shifts separated by the cycle length alias.

For K=5, a more elaborate cyclic design attains the exact new bound, not just its asymptotic limit. Take all length-five ternary words with one middle symbol (80 words), once each, and those with two middle symbols (80 words), twice each. Use them as directed edges from their first four symbols to their last four, with multiplicity, in a de Bruijn-type graph. The graph is balanced because the weights depend only on symbol occupancy, and an actual Euler traversal in the laboratory uses all 240 edges. We do not infer connectedness from balance alone: the program verifies full traversal and independently re-counts every cyclic length-five window, finding the required 160 distinct windows at precisely their prescribed multiplicities. Emit the source word's first symbol along the tour. For each of the ten distinct phase pairs, the actual pair matrix is

    24 32 24
    32 16 32
    24 32 24

Its largest chain mass is max(24+16+24,32+32)=64. Consequently N=240,K=5,L=64,d=176 is globally optimal. A repeat of the 240-tick cycle gives equality for every multiple of 240. The full emitted cycle is in execution.json. We make no minimal-cycle-length claim.

The 8-tick cycle and 240-tick cycle therefore supply exact finite pilots, while the block construction establishes the general limit. Repetition guarantees robustness in this indexed fault contract, not freedom from periodic ambiguity beyond the stipulated K consecutive offsets.

## Executable qualification and negative sediment

Run node laboratory.cjs from this directory. It uses integer-valued JavaScript arithmetic within the safe integer range for the actual fixtures. It executes:
- 99 exact occupancy profiles K=2..100 with lower/upper certificates checked against each possible occupancy; the large-K proof above is not based on extrapolating those tests.
- 31 disjoint chain-cover and Euler perimeter checks q=2..32.
- All six four-phase and ten five-phase contingency matrices plus the full 240-window edge multiplicity certificate.
- Nine genuine overlapping block profiles K=6,7,8 and R=1,4,16. For example K=6,N=23040 gives L=6224 vs exact lower 6144; K=8,N=229376 gives L=66208 vs lower 65536. They satisfy the boundary allowance, but are not asserted globally finite-optimal.
- 300 seeded weighted-chain comparisons against independent exhaustive subset-mask enumeration.
- 120 seeded synthetic candidate-list decodes: 60 for N=8,K=4 with e=2,f=1; 60 for N=240,K=5 with e=80,f=15. The exact candidate set is the unique injected phase in every trial. The latter uses effective budget 175 just below distance 176. The fixed monotonic output maps vary in polarity and gaps. The injected substitutions are particular large outliers, not an exhaustive test of fault values; universality comes from the distance proof.
- Zero assertion failures. Committed JavaScript and JSON were retrieved, executed again in V8, and the resulting receipt matched byte-for-byte.

The reference decoder uses a weighted chain DP on the transmitted level versus the observed value rank. This is the strict specialization of #796, not a new production decoder. It tests both relative orientations, ignores flagged erasures, and retains all phases with at least N-f-e compatible positions. It is a synthetic oracle, not a real-time VST. No physical channel test, calibration measurement, output noise floor or human validation was performed.

Negative results: pair-optimal geometry is not necessarily jointly attainable; at five candidates the optimal fraction changes strictly. A larger candidate vocabulary is not free. The guard-level reduction preserves the exact ordinal contract, not Euclidean noise margins; the channel may still compress all outputs arbitrarily closely. Equality-based detection in analog noise and unknown indexing remain distinct problems. Large K inventory growth makes the generic construction unattractive for embedded deployment. A smaller exact periodic design for K>=6 and finite-length optima outside the certified multiples remain open. The two-phase perimeter theorem does not settle arbitrary-q multi-phase packing.

## Source ledger and interpretation

Read on 27 November 2026 by the same agent:
- De Bruijn Sequence and Universal Cycle Constructions, "A graph model and Euler cycles", https://debruijnsequence.org/db/graph . HTML graph definitions and Hierholzer algorithm steps read, including its discussion of the edge-to-cycle representation. Established technique used here with restricted, weighted edge sets; the ordinary full de Bruijn result is not a proof of connectedness for a restricted graph.
- Atri Rudra, Nathan Russell and Atri Rudra (lecture/scribe roles as printed), *Error Correcting Codes: Combinatorics, Algorithms and Applications*, Lecture 16, "Plotkin Bound", 2 October 2007, https://cse.buffalo.edu/faculty/atri/courses/coding-theory/lectures/lect16.pdf . Three-page extracted text read, printed page 1 visually checked, Theorem 1.1 and proof on page 3 inspected. This is a teaching source for classical packing context, not Plotkin's original paper; its distance is ordinary Hamming, not order-orbit agreement. No priority inference made.
- Repository predecessor #796/#797 complete report, issue/comments, PR and exact-head workflow 46003239805 (completed success) read. The previous plateau-reduction and chain definitions are inputs, not canonical accepted human evidence.

Interpretation: an observer can support four alternative alignments whose pairwise distinctions are protected by the same small alphabet, but introducing a fifth forces a redistribution of those distinctions. This resembles a constraint on a vocabulary of competing interpretations; it is not a theorem of human semantics. Conventional coding theory, convex averaging and finite graph theory account for all demonstrated results; no extra explanatory contribution from cybersemiotics is established (Brier subtraction). Scientific priority for the particular formulas is unassessed.

Design hypothesis: a receiver inspector can expose not just the pairwise margin but the unavoidable degradation as its phase vocabulary expands. The short 8-tick cycle can be used in a synthetic four-phase reference experiment, with guard spacing determined by a separately established plateau bound. Test a real channel separately for stable monotonicity, ties, dense noise, spectral occupancy and index errors. No acoustic performance or listener preference follows from the combinatorial proof.

Checkpoint: base main 495a98ca12bae467a507031f04931aa4254b1866; branch mhac-801/phase-packing. Read AGENTS, RAG, programme, runbook, integrity, validation, experiments and human gates; nested research/AGENTS and research/expeditions/AGENTS absent. Reconciled 464 branch entries, 30 recent issue and PR entries, targeted ordinal/asymptotic/chain searches, predecessor #796/#797 and its exact-head checks, new issue #801 body and empty comments. Scope confined to this directory; no canonical manifests or other workers' branches modified. Draft/HOLD pending independent critique and exact-final-head repository checks; full native repository validation not performed. No human gate for synthetic research.

Fiction: The clock keeps four friends whose accounts can coexist in the same narrow ledger. A fifth arrives, carrying no new alphabet. The clerk discovers that the ledger has room for every pair in isolation, but not for all their promises together.
