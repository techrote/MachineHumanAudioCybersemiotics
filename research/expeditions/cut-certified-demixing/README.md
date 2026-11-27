# The Chord That Repairs a Lying Sample

Refs #754, #750, #211, #320 · 27 November 2026 · Exploratory mathematical DSP. One ChatGPT agent: source inspection, derivations, exact V8 experiment and native Python numerical cross-check. No independent peer review, physical transmission, human listening or novelty priority claimed.

## Observation contract: two periodic voices, corrupted samples

The local-clock study (#750) exposes the distinction between identifiability and numerical conditioning for sums of periodic signals. Here change the error model: a few indexed raw samples may have arbitrary amplitudes, including errors many orders of magnitude larger than the intended waveform. Ordinary least squares cannot supply a uniform exact recovery guarantee. We ask how much redundancy actually suffices.

After coherent parity demodulation, let y(t)=f(t mod p)+g(t mod q)+b+error(t), with known coprime integers 3<=p<q, arbitrary real zero-mean private shapes f,g, and unknown constant b. Sample indices are known. Missing observations are flagged erasures; up to e surviving observations can be changed arbitrarily. No unknown clock slip, time warp, independent alternating nuisance, third private period, or unmodeled component is covered.

Construct a bipartite observation multigraph on p+q vertices, with oriented edge (A[t mod p],B[t mod q]) per observed time. Represent noiseless observations as differences of vertex potentials theta_A-theta_B. A common shift of every potential is irrelevant. The zero-mean components and constant are uniquely obtained by f=theta_A-mean(theta_A), g=-theta_B+mean(theta_B), b=mean(theta_A)-mean(theta_B). Every potential assignment describes a permitted signal; coprimality means the full period graph is complete bipartite, so nonconstant potential differences yield distinct full signals.

The graph in #211 already establishes a cut certificate for distinguishing separately periodic symbolic streams. This is not a claim to rediscover it. The new observation is that the same graph supports actual additive real-valued demixing, with a convex decoder and a deterministic stability certificate, and a sharp closed-form prefix budget rather than the earlier generic oracle. #320 concerns bandlimited erasure amplification, a different signal class.

## Sharp corruption correction and a convex decoder

Let lambda be the smallest nontrivial cut cardinality, counting parallel edges, of the observed graph before erasures. The exact minimum number of differing observations between two distinct noiseless full signals is lambda. For any nonconstant potential perturbation h, choose a nonempty proper level set; every edge crossing it has a nonzero difference. Conversely an indicator potential of a minimizing cut produces precisely that many nonzero observations. Thus erasing f entries and arbitrarily corrupting e surviving ones is universally correctable iff lambda >= 2e+f+1. Necessity: erase up to f entries from a minimum cut witness, then split the remaining discrepancies between two received-world candidates; their error balls intersect if the remaining size is <=2e. Sufficiency follows from the Hamming triangle inequality.

But this is not just an abstract distance bound. Let B be the oriented incidence matrix, let z be observed data after erasure, and fit a potential by weighted least absolute deviations (LAD):

    minimize over theta, with theta[0]=0: sum_j w_j |z_j-(B theta)_j|.

Weights are positive. Fix an actual corruption support F (not known by the decoder), with surviving uncorrupted edges G. For every nontrivial vertex cut S put

    m(S) = sum_{j in cut(S) intersect G} w_j - sum_{j in cut(S) intersect F} w_j,
    delta = min_S m(S).

**Exact theorem:** this decoder uniquely recovers every true potential (modulo common shift) against every corruption on F iff delta>0.

Proof: for any perturbation h, define H=max(h)-min(h). Write |h_u-h_v| as the integral, over threshold levels a, of the indicator that (u,v) crosses {h>a}. Therefore

    sum_G w_j |(Bh)_j| - sum_F w_j |(Bh)_j| >= delta H.

This is a finite layer-cake/coarea identity, with no probability model. The inequality is sharp as a bound per unit range: take h equal to the indicator of a minimizing cut. By the triangle inequality, in the noiseless-good case the difference between the candidate LAD objective and the true objective is at least the expression on the left. If delta>0, every nonconstant candidate has strictly larger objective. If delta<=0, set z equal to the truth on G and to the truth plus Bh on F, with h the minimizing indicator. The competing potential then has objective no larger than the truth, defeating universal unique recovery. The criterion concerns an entire support contract, not identification of the actual error support.

For unit weights with at most e corruptions and f erasures, every surviving cut has signed margin at least lambda-f-2e. Hence unweighted LAD achieves the information-theoretically sharp correction threshold. No combinatorial search over outlier positions is required for the convex decoder. The margin for a fixed signed support can be computed by exhaustive cuts for small graphs; ordinary nonnegative-capacity min-cut algorithms cannot directly optimize arbitrary negative capacities.

For a universal weighted contract, order each pre-erasure cut's weights from largest to smallest. Worst-case loss of signed margin is twice the sum of its e largest weights plus the sum of its next f largest (truncate at the cut size). Proof: each corrupt edge reduces margin by 2w, each erased edge by w; exchange any incorrectly ordered assignments. A necessary and sufficient universal condition is that every cut's total weight strictly exceed this loss. In particular, weights expressing confidence are not automatically robust.

## A sharp prefix deadline for every pair of coprime periods

For p,q as above and n consecutive observations, the exact connectivity is

    lambda(n)=0                           n<p+q-1
    lambda(n)=max(1,floor(n/q))           n>=p+q-1.

Proof of initial threshold: the first q observations attach each B vertex once. The next p-1 edges, at times q,...,q+p-2, join A[i] to A[(i+q) mod p] through B[i] for i=0,...,p-2. These are all but one edge of the single cyclic permutation generated by q modulo p. Therefore the first p+q-1 observations form a spanning tree. Fewer observations cannot connect p+q vertices.

For d>=2, consider n=dq. Each B vertex has degree d, including repeats, hence lambda<=d. Restrict to the first p B residues (0,...,p-1). Relabel both sides by multiplication by the inverse of q modulo p. The core is a p-by-p bipartite circulant multigraph with shifts 0,...,d-1, reduced modulo p. Write d=kp+r, 0<=r<p. The core has k parallel copies of K(p,p) plus a simple r-shift graph. For r>=2, the r-shift graph is connected (shifts 0 and 1 suffice), regular of degree r and vertex-transitive: translations of both sides and swapping sides with sign reversal are automorphisms. By Mader's classical connected vertex-transitive graph theorem, its minimum cut is r. Each K(p,p) copy has minimum cut p. Thus their union has minimum cut at least kp+r. If r=0 use just the complete copies. If r=1, k>=1 since d>=2. Any minimum cut of K(p,p) isolates a single vertex for p>=3: when both sides split nontrivially the cut expression x(p-y)+(p-x)y is at least 2(p-1)>p, by minimizing on the rectangle 1<=x,y<=p-1; if one side is unsplit, equality p requires a singleton or its complement. Hence a core cut either crosses at least p+1 edges per complete copy (giving >=kp+1), or isolates a vertex and crosses the remaining matching once. In all cases the core is d-edge-connected. Every extra B vertex attaches by d edges, counting multiplicities, to core A vertices. A cut splitting the core already costs d; a cut leaving the core intact and separating any extra vertex also costs d. This proves lambda(dq)=d. For dq<=n<(d+1)q, monotonicity gives lambda>=d and at least one B vertex has degree d. The formula follows.

A shifted consecutive window only permutes residues, so the result is independent of start. In particular, if d=2e+f+1, the sharp number of raw scheduled positions is

    N_min = p+q-1 if d=1; d*q if d>=2.

This also minimizes the number of observations even if arbitrary indexed positions can be chosen, because connectivity needs p+q-1 edges for d=1, and every one of q right vertices must have at least d edges for d>=2. Consecutive sampling attains both lower bounds. It does not imply the same optimal elapsed time for a schedule that is allowed to skip ticks or repeated measurements at the same time. The theorem is restricted to coprime p,q with p>=3.

| Periods | Clean | 1 arbitrary error | 1 error + 2 erasures | 2 arbitrary errors |
|---|---:|---:|---:|---:|
| 3,5 | 7 | 15 | 25 | 25 |
| 5,7 | 11 | 21 | 35 | 35 |
| 7,11 | 17 | 33 | 55 | 55 |
| 11,17 | 27 | 51 | 85 | 85 |

At the one-short deadline the distance is exactly d-1, and a cut indicator gives two full signals that can produce the same received data under the allowed faults. This is not merely failure of LAD. The V8 laboratory validates 48 such explicit ball-intersection witnesses.

## Two independent reconstruction strategies and deterministic stability

LAD is a linear program (unrestricted anchored potentials, nonnegative absolute-residual variables). Suppose the good edges also contain bounded or arbitrary additive deviations eta, while the bad edges remain unrestricted. Using the triangle inequality on the good edges gives the objective gap lower bound delta*range(h)-2*sum_G w_j|eta_j|. Any minimizer therefore satisfies

    range(theta_hat-theta) <= 2 sum_G w_j |eta_j| / delta, provided delta>0.

An anchored coordinate error and the recovered centered private residue errors are each no larger than this range. The same bound applies to the reconstructed constant (difference of two side averages). This is a deterministic sufficient bound, not a stochastic variance estimate or generally sharp noisy error constant.

A second decoder does not solve a continuous optimization problem. In the surviving graph, find 2e+1 edge-disjoint paths from a reference vertex to each other vertex (unit undirected max flow and path decomposition). Existence follows from the surviving cut bound, or directly from max-flow/min-cut. Each signed path sum gives an estimate of the potential difference. A bad observation can contaminate at most one path in each collection. Hence a strict majority of path estimates is exactly correct in the gross-error-only model. Take their median. With absolute error <=epsilon on all good edges, every uncorrupted simple path estimate lies within its length times epsilon of the true potential. The median error is at most L*epsilon, where L is the maximum selected path length (<=p+q-1). This guarantee does not grow with the number of observations. It concerns the anchored potential; centering each private shape can at most double the coordinate-error bound. The path method uses no magnitude assumption on corrupted samples and no candidate search over their locations.

The independent native SciPy LP and V8 path decoder agree on the required correctness contract. Native comparison: 320 gross-error trials with deterministic random integer potentials in [-20,20], corruption magnitudes 1000..10000, four period pairs and four error/erasure contracts; all LAD fits recover the anchored potentials within 1e-6 (reported worst error rounds to zero at nine decimals). All 320 ordinary least-squares fits fail that tolerance. A further 320 trials add small uniform perturbations on good edges, all satisfying the derived range bound; maximum ratio of actual range to bound about 0.1191. These synthetic draws do not establish failure rates for real audio. In fact no linear decoder can be uniformly exact against one arbitrary unflagged additive corruption: exact cancellation of every single-coordinate perturbation forces all columns of its reconstruction matrix to be zero.

## Negative sediment: an observer can assign too much trust

In the (5,7) 21-sample fixture lambda=3, so one arbitrary corrupted sample can be corrected by unweighted LAD. Let truth be zero. Isolate the first B vertex, whose three incident samples carry the alternative signal -1. Corrupt just one of those three samples to -1. The true objective is 1 and the competing objective is 2 under unit weights.

Now weight the corrupted observation 3 and every other observation 1. The true objective becomes 3 and the alternative costs 2. The graph still has exactly the same cardinal connectivity and the error count is unchanged. The weighted receiver prefers the wrong signal. The native LP verifies this as well. This is not a claim that confidence weighting is always harmful; it establishes that its robust qualification must inspect cut weights, not only count samples.

Other limitations: a graph with many observations concentrated on the same residue pair may have zero connectivity. Arbitrary third-period components produce a hypergraph design rather than this incidence matrix; the two-level coarea proof does not extend automatically. Coherent cancellation, near-periodic drift, unflagged insertion/deletion, clipping and unknown periods are outside the model. The two-period contract is narrower than #750 and does not replace it. The clocked cubic population noise theorem and finite-window weighting remain different observation contracts. Sparse corruption is not equivalent to Gaussian noise. All recovered potentials require known coherent indices; no real-time VST, audio hardware test or human validation is delivered.

## Sources, replay and custody

- F. Blanchet-Sadri, D. Bal, G. Sisodia, *Graph Connectivity, Partial Words, and a Theorem of Fine and Wilf*, Information and Computation 206(5), 676–693 (2008), https://doi.org/10.1016/j.ic.2007.11.007 . Read author-hosted preprint https://msuweb.montclair.edu/~bald/files/finewilf.pdf abstract/introduction and Section 4, printed preprint page 9, Definition 4.2 and Figure 1; page image inspected. Their graph has sample positions as vertices, unlike the residue-incidence graph used here. Established ancestry for periodicity under missing data, not attribution of the LAD theorem to them.
- A. C. Burgess, R. D. Luther, D. A. Pike, *The edge-connectivity of vertex-transitive hypergraphs*, Journal of Graph Theory 105(2), 252–259 (2024 issue, first published 2023-09-29), https://doi.org/10.1002/jgt.23035 . Read accessible Introduction and Theorem 1 (classical Mader result as restated by the authors), also the abstract's restriction on hypergraph extensions. Mader's original paper not read. Theorem 1 is the established graph result used in the core argument, not a new result here.
- X. Jiang, L.-H. Lim, Y. Yao, Y. Ye, *Statistical ranking and combinatorial Hodge theory*, Mathematical Programming 127, 203–244 (2011), https://doi.org/10.1007/s10107-010-0419-x . Publisher abstract read, not full paper. Its edge-flow viewpoint and gradient least-squares reconstruction motivate the cross-domain analogy to inconsistent rankings. No attribution of the cut theorem or priority.
- Reuse of MHAC #211 acknowledged explicitly (full report read). #750 report and issue read; #320 issue read for scope distinction. No claim of literature novelty or independent scientific review.

Replay: [laboratory.cjs](laboratory.cjs) runs in Node-compatible JS without dependencies; exact integer computations executed twice in V8, including fetched committed source, byte-identical [execution.json](execution.json). 3258 prefix/cut profiles, 1638 independent flow checks, 48 sharp ambiguity constructions, 960 exact median decodes, 960 bounded-noise checks, 960 integer coarea checks, 800 weighted coarea checks. No failed final assertions. Native [native.py](native.py) uses Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, run with OPENBLAS_NUM_THREADS=1; two identical local receipts, committed source blob ac3239a9e87793fed4844f5669c0d36edc92e8c6 and corrected [native-execution.json](native-execution.json) blob d46d8886456e1fb69171a3ac80c4839d4dafa8b5 match local Git hash-object. The initial copied native receipt contained one transcribed row value; corrected against the actual native blob before qualification. Numerical LP is an independent formulation, not independent review. Exact proof is separate from numerical execution.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; root AGENTS, README, RAG, programme, runbook, integrity and validation inspected; nested research/AGENTS and research/expeditions/AGENTS absent. 439 branch entries paginated, 50 recent issue results and 50 actual open PR results, targeted Fine-Wilf, edge-connectivity, periodic erasure and LAD searches. Predecessor #751 draft exact head 9a6388c5e6dc1624e1d8b4b296c209d6f7b30200 workflow 45924883224 completed success. #750 and #754 comments empty. Native git ls-remote failed DNS, so no repository-wide native checks claimed. Additive scoped branch only; Draft/HOLD for critique/integrator, no shared paths or canonical stage changes.

Interpretation: an acoustic observer need not know which statement lies if enough independent routes establish each relationship. The cut exposes the weakest possible partition of testimony. Unlike an elapsed-time counter, it identifies a specific structural vulnerability. An Observatory prototype could display the weakest cut, fault contract and robust decoder disagreement; test whether this aids actual understanding separately. This is a design hypothesis. Conventional graph theory, coding distance and convex optimization explain the results; no incremental cybersemiotic explanation established.

Fiction: a clerk gives each witness a number of votes in proportion to his confidence. The apprentice draws a line separating two groups of witnesses and finds that one trusted witness can outweigh every other statement crossing it. She does not ask him to speak more softly. She changes the rules of the vote.
