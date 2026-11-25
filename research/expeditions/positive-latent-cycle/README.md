# The Duet That Needs More Parents Than Modes
## Positive latent mixtures, cycle supports and tensor amplification

Issue [#618](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/618); base 495a98ca12bae467a507031f04931aa4254b1866; 2026-11-25. Additive synthetic expedition, outside frozen Tracks E/G. AI-assisted mathematical derivation, implementation and self-check; no independent review, human listening evidence, causal identification or priority claim.

## Anomaly and observation contract

Two separated generators emit symbols X and Y in Z/nZ. Each symbol is locally uniform, but the only permitted pairs are y=x or y=x+1 modulo n. The target P is uniform on these 2n cells. A shared selector Z chooses a product law p_z(x)q_z(y), with weight lambda_z. Private randomness is otherwise independent. No post-selection or communication between the two emitters is allowed. A "parent" below means a selector value, not a causal mechanism.

For n=4 the target table, multiplied by 8, is

```
1 1 0 0
0 1 1 0
0 0 1 1
1 0 0 1
```

It has ordinary real rank three, yet four selector values are necessary. Positive mixture cannot use cancellation to remove forbidden pairs. This is a probabilistic generation constraint, not a claim that a linear audio synthesizer cannot play the scores.

## Exact theorem: rank, entropy and repetition

For n>=3, let P_d=P^(tensor d), the joint law of d independent target pairs, grouped into two length-d words. Set N=n^d. Then

* real rank = (n-1)^d for even n, n^d for odd n;
* nonnegative rank = n^d, for either parity;
* minimum H(Z) and minimum I((X,Y);Z) among exact finite conditional-independence auxiliaries = d log2(n);
* I(X;Y)=d log2(n/2), one bit per coordinate below the common-information budget.

Proof: (I+cyclic shift)x=0 implies x_(i+1)=-x_i; this has a one-dimensional kernel for even n and zero kernel for odd n. Real rank multiplies under tensor products (reduce each factor by invertible row and column operations to its rank normal form).

The support bipartite graph is a single 2n-cycle. A nonempty product rectangle has at most two cells because the graph has no 4-cycle and every vertex has degree two. Every support rectangle in P_d projects to a support rectangle in each coordinate; the original rectangle is contained in their Cartesian product, hence has at most 2^d cells. The entire support has (2n)^d cells. Nonnegative components cannot cancel leakage, so at least n^d are required. The row-selector construction attains the bound: choose X uniformly and choose each Y-coordinate as X or X+1 independently.

Any component weight is at most 2^d/(2n)^d=1/n^d because its mass cannot exceed the target mass of its support. Thus H(Z)>=log2(n^d). Also H(X,Y|Z)<=d, while H(X,Y)=d log2(2n), proving the mutual-information bound; the row-selector attains both. The ordinary mutual information follows from uniform margins and H(Y|X)=d. The general uniform-support Wyner bound has explicit prior overlap with Bruno and Vaccaro, Sec. IV-A Lemma 7 (see ledger).

At the minimum cardinality, all rectangles must be disjoint maximal rectangles, each component has weight 1/n^d, and each is uniform on its rectangle. A maximal rectangle is the product of coordinate stars (two cells at a shared row or column). For d=1, disjoint stars covering the 2n-cycle correspond to perfect matchings of the cyclic list of edges. There are exactly two: all row-stars or all column-stars (choosing one adjacent pair forces the next pair). This is a precise *non-identifiability* result, not proof of direction. At d>1 there are mixed tilings: choose X in coordinate 1, then, depending on that value, select either row or column in coordinate 2. Thus the two base explanations do not exhaust the repeated case.

For n=4,d=6, real rank is 729 and nonnegative rank 4096. Their ratio (4/3)^d grows exponentially.

## Exact zero-leakage approximation and a general robustness bound

Use total variation TV(P,Q)=max_A |P(A)-Q(A)| = 1/2 sum |P-Q|. If Q uses at most k>=1 positive components and no forbidden pair has positive probability, its support covers at most k 2^d cells. Hence

TV(P_d,Q)>=max(0,1-k/n^d).

This is sharp, without a marginal constraint: choose k distinct target rows (or all rows if k>=N) and renormalize the target on their support. Missing combinations are not equivalent to forbidden combinations.

If forbidden mass ell=Q(S^c) is permitted, with S=target support, the following weaker but explicit bound holds:

TV(P_d,Q) >= max(ell, 0, 1-k/n^d-d sqrt(2 ell)).

Proof: for a product component with forbidden probability eps, each coordinate's forbidden probability eps_i<=eps. Write p,q for that coordinate's row and column marginals. For independent X,X'~p and Y~q, Jensen's inequality gives (1-eps_i)^2 <= E_Y[p(N(Y))^2]. The latter is at most a+(1-a) max(q), a=sum p_x^2: two different rows share at most one neighbor. Consequently (1-max p)(1-max q)<=2 eps_i, since a<=max p. One side has a coordinate value with mass at least 1-sqrt(2 eps). Fix that side in each coordinate and restrict the other to its permitted neighbors; this defines an allowed rectangle R. The probability of S outside R is at most d sqrt(2 eps) by the union bound. Form the union U of the k rectangles. Its target mass is at most k/n^d, whereas Q(S outside U)<=d sum lambda_z sqrt(2 eps_z)<=d sqrt(2 ell). Apply the TV event bound to S outside U, and separately to S^c. This does not assert optimality under leakage or a dimension-uniform asymptotic estimate.

## Stronger single-coordinate frontier with both margins held exactly uniform

Let Q have uniform marginals on n>=3 symbols and at most k components, 2<=k<=n. Then

**Q(S^c) >= (1-k/n)^2, hence TV(P,Q) >= (1-k/n)^2.**

The bound is sharp when k divides n (including k=n, where the exact row-selector works).

Proof of a capped bilinear lemma. For one component of weight lambda>0 set t=n lambda, x_i=t p_i, y_i=t q_i. The marginal constraints force 0<=x_i,y_i<=1 and both sums equal t. The weighted allowed mass is F/(nt), where F=sum_i x_i(y_i+y_(i+1)). Maximizing F over the two capped simplices can be done at a vertex in each, by linear maximization in one vector at a time. A vertex has m=floor(t) ones and at most one fractional value r=t-m. The exact maximum is

```
Fmax(t)= t^2                          (0<t<=1)
         2t-1                         (1<=t<=n-1)
         2t-1+(t-(n-1))^2             (n-1<=t<=n).
```

For t<=1, concentration on one allowed pair attains t^2. For 1<=t<n-1, the full coordinates induce a proper subgraph of the 2n-cycle and have at most 2m-1 edges; the total occupied vertices induce at most 2m+1 edges. Remaining edge weights are at most r. Thus F<=2m-1+2r. Equality is attained by full rows 0..m-1, full columns 1..m, fractional row m and fractional column 0 (omit fraction when zero). For t in (n-1,n), all coordinates are occupied. If the fractional row and column are adjacent, their incident edges give 2n-3 full-full, two full-fractional, one fractional-fractional; otherwise 2n-4 full-full and four full-fractional. The first arrangement wins by (1-r)^2. Endpoints follow directly.

Write f(t)=Fmax(t)/t, f(0)=0. For t0=n/k in [1,n/2], the line L(t)=2-2/t0+t/t0^2 majorizes f on [0,n]: on [1,n-1] it is the tangent to the concave function 2-1/t; on [0,1] it dominates the line t at both endpoints; on [n-1,n] f is convex (f=t+2-2(n-1)+((n-1)^2-1)/t), and L dominates at n-1 and at n, where L(n)>=2=f(n). Pad with zero weights if needed. Since sum t_z=n, sum allowed mass <= sum L(t_z)/n = 2k/n-(k/n)^2. Subtract from one.

Attainment: if n=k t, t integer>=2, partition rows into consecutive t-blocks and columns into the same blocks shifted cyclically by one. Give each component weight 1/k and sample its row and column independently and uniformly within its assigned blocks. Each block contains 2t-1 allowed cells out of t^2. Both margins are uniform. Every occupied allowed cell has mass 1/(nt)<=1/(2n), so TV equals forbidden mass, exactly (1-k/n)^2. For k=n use row-stars. For k=1 the unique uniform-margin product law is the full uniform square, with TV=1-2/n; the k>=2 formula must not be extrapolated to it. Sharpness for nondivisor k is not established.

Example n=8: four parents can retain both single-channel histograms exactly while emitting forbidden pairs with probability 1/4. One parent emits forbidden pairs with probability 3/4. Zero-leakage four-parent approximation without uniform margins instead has TV 1/2. The improvement under leakage is not free: it changes which pairings can ever occur.

## Apparatus, experiments and negative sediment

Run the standalone exact integer census with `node laboratory.cjs`. It enumerates all nonempty row subsets to find common columns, computes real rank by fraction-free BigInt elimination, enumerates capped simplex vertices (integer scaled) and their products, exhausts base star-tiling masks, and verifies uniform-margin block witnesses. The retained execution is a bounded computational check, not the universal proof.

JavaScript execution: 10 rectangle/rank profiles (including 4^2 rows), 225 capped profiles, 352911 literal vertex pair checks, 7 tiling profiles, 103 divisor constructions, all assertions passed.

A native Python cross-check enumerated capped vertices by combinations and evaluated column sums, and used literal set intersections for six rectangle profiles. 180 capped profiles, 82158 vertex pair checks. Three 64-slot stereo specimens at n=8: target, four-parent block and one-parent uniform. Each channel has eight instances of each of eight frequency symbols, but forbidden pair counts are 0, 16, 48. The WAV renderer uses 8 kHz PCM16, 640-sample tapered tones at 250+50i Hz, deterministic shuffle, and matched-template decoding from actual PCM. All 192 slots decoded correctly, both margins verified. Two native executions reproduced receipt and WAV fingerprints. These are original symbolic test fixtures, not human stimuli or empirical evidence. Native source/receipt retained separately with the delivered package.

Negative results: real rank is not a latent state count; identical marginals do not certify joint support; arbitrary signed weights are not probability mixtures; leakage can improve numerical TV when hard support is relaxed; minimum exact decompositions are not unique. The strong bound needs both uniform margins; general tensor leakage bound is weaker. Post-selection could generate the target from independent uniform emissions simply by rejecting invalid pairs, but changes the contract and acceptance probability. A common selector model does not establish real causal parenthood. Finite sample marginals and forbidden counts do not establish true population zeros.

## Source ledger and comparison

* Fiorini, Kaibel, Pashkovich and Theis, [Combinatorial Bounds on Nonnegative Rank and Extended Formulations](https://arxiv.org/abs/1111.0444), 2011 preprint metadata; read introduction, especially support rectangle argument. It supplies established ancestry of the nonnegative-rank lower bound, not a new discovery by this expedition.
* Chee, Le and Ta, [On the Asymptotic Nonnegative Rank of Matrices and its Applications in Information Theory](https://arxiv.org/abs/2308.07187), 2023 preprint; read Sec. 1, 1.1 tensor definition and 1.2 common information. General nonnegative rank is not multiplicative, making the cycle family's exact multiplicativity a special case.
* Bruno and Vaccaro, [Wyner's Common Information and the Common Entropy are NP-Hard to Compute](https://arxiv.org/html/2610.15402v2), revised 24 Nov 2026; read abstract, Sec. I and I-A, Sec. IV-A Definition 3 and Lemmas 7-9. Direct overlap: their general uniform-support criterion already gives our Wyner information equality once the maximum rectangle is known. The exact capped-marginal leakage frontier, minimum-tiling rigidity and finite robustness bound are the scoped derivations here. No claim of priority or exhaustive novelty search. Sources are HTML passages, not whole-paper readings; no source images required for these text arguments.

All source reading and derivation by one AI agent on 25 Nov 2026. No source text republished. Conventional matrix theory and information theory suffice; no additional explanatory contribution from cybersemiotics has been established. Earlier repository #360 studies passive routing rather than product mixtures; #514 anonymous binding and #614 shared references provide adjacent motivations. No new canonical empirical or theoretical record.

## Exaptation and fiction

Design hypothesis: a two-field acoustic grammar (e.g. source and permissible action) should separately qualify marginal symbol frequencies, joint validity, the shared selection mechanism, and allowed leakage. Compare a direct joint lookup (no independent-generator constraint), independent field synthesis with a selector, and rejection sampling. Measure invalid conjunctions, TV, shared bits and rejection latency before any human study. The hypothesis is not that these symbols possess inherent meaning or that the listener performs nonnegative factorization.

Fiction: the clerk inventories both singers separately and hears every note equally often. He hires a smaller committee to coordinate the duets. Their individual ledgers remain perfect, but the committee begins to authorize forbidden pairings. A negative coefficient could erase those pairings on paper; it cannot take back an emitted pair.

## Checkpoint

Fresh branch mhac-618/positive-latent-cycle; additive files only, no shared canonical manifests. Scope #618. Standalone tests pass; full repository CI and independent mathematical review not asserted. Draft PR with Refs #618, left for review and integrator, consistent with ongoing parallel exploratory work. No human action required for next computational review.
