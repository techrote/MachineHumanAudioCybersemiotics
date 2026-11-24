# The Window That Forgets Its Boundary

**Exploratory mathematical expedition, 24 November 2026.** Issue [#324](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/324). Synthetic analysis, not a frozen-protocol finding. One GPT-6.2 research agent authored the proofs, source notes and two computational laboratories; no independent human review, participant data, or claim of mathematical priority.

## Abstract

A circular log retains sums of contiguous time windows, not the original samples. It may retain enough measurements to cover every sample, connect every endpoint, and even contain a cycle, yet fail to identify the total of the original signal. The missing object is the winding of a cycle of labelled interval endpoints. We give exact rank, target observability, repair, erasure-distance and integer-lattice certificates. The last exposes a curious converse: a square invertible measurement system with no redundant real-valued equations may still detect single-unit corruptions because its integer image is a proper sublattice. An original PCM witness turns observational ambiguity into a score.

## Model and a four-sample anomaly

Let N>=2, x=(x_0,...,x_{N-1}) be real-valued periodic samples, and T=sum(x). An observation (i,l), 0<=i<N, 1<=l<N, reports the exact sum of the l samples starting at i, with wraparound. Its labels are retained, erasures are known, and the period and origin are fixed. This can model nonnegative energy or event-count envelopes, signed measurements, and additive resource accounting. It does not assert that arbitrary speech or audio waveforms can be reconstructed from energy.

Consider the following entirely positive integer profiles:

* A=(2,2,2,2), total 8.
* B=(2,3,1,3), total 9.

| Start | Length | Included samples | A | B |
|---:|---:|---|---:|---:|
| 1 | 2 | 1,2 | 4 | 4 |
| 2 | 2 | 2,3 | 4 | 4 |
| 0 | 3 | 0,1,2 | 6 | 6 |
| 2 | 3 | 2,3,0 | 6 | 6 |

Every sample is covered. There are four windows for four unknowns. Their endpoint graph is connected, with a cycle. Still the reported data agree. The difference (0,1,-1,1) is invisible and changes the total by one. Replace only (1,2) with its complementary interval (3,2): the endpoint multigraph, window count, length multiset and full sample coverage are unchanged. The new measurements become (4,4,6,6) and (5,4,6,6). The new system is invertible, not merely able to discriminate these two witnesses.

## Exact rank via winding

Define prefix coordinates p_0=0 and p_i=sum(x_j for j<i), for 1<=i<N. The coordinates (p_1,...,p_{N-1},T) are in bijection with x, including over the integers. For interval e=(i,l), put j=(i+l) mod N and w=floor((i+l)/N), either zero or one. The measurement is

    y_e = p_j - p_i + w T.

Treat e as an oriented edge from i to j with integer gain w; traversing backward negates both gain and measurement. Keep parallel edges distinct. Let c count connected components of the underlying undirected graph, including isolated vertices, and let b=1 if some closed walk has nonzero signed gain sum, else b=0. The gain sum is its winding about the period boundary: the signed lengths telescope modulo N. Changing the chosen origin changes individual gains but not cycle gains.

**Theorem 1 (proved).** The real observation matrix A has rank N-c+b, hence nullity c-b. With an independent exact total measurement appended, rank is N-c+1 and nullity c-1.

Proof: choose a spanning forest. Its equations in prefix coordinates express each vertex potential in terms of its component root potential, a known forest path sum, and a multiple of T. The root in the component of vertex zero is fixed; c-1 other root offsets remain free. Summing any closed walk gives sum(y)=T sum(w), since the prefix differences telescope. If any winding is nonzero it fixes T; otherwise all cycles cancel T and no equation can constrain it. Conversely a choice of T and the remaining root offsets satisfying the cycle equations extends along the forest to a solution of all edges. For the homogeneous system, this leaves exactly c-1+(1-b)=c-b free parameters. Appending T fixes the last scalar if necessary. QED.

Consequences: all real samples identifiable iff connected AND b=1; known total reduces that criterion to connectivity. Total alone identifiable iff b=1, even if the graph is disconnected. A tree cannot reveal the total. A graph with many cycles can still be balanced (all windings zero). In the example the original cycle has winding zero; after complement replacement the cycle 3→1→2→0→3 has gain 1 and measured signed sum y_newfirst-y_fourth+y_second+y_third, which recovers 8 or 9 exactly.

An explicit algorithm builds a forest, transports signed gains and compares every remaining edge with its forest prediction. For noiseless consistent data, any nonzero residual gain gives T by dividing the corresponding residual observation by the gain. Zero-gain residual observations must be zero; different nonzero-gain ratios must agree. These are consistency certificates, not a noisy estimator. Once T is fixed, tree propagation gives p and adjacent differences give x. O(N+|E|) graph operations suffice; exact rational bit complexity is a separate matter. The supplied reconstruction routine uses small exact-representable integers and the Number type for ratios, while the rank oracle uses BigInt; arbitrary rational arithmetic is not implemented.

## Which questions survive, and how to repair

**Theorem 2 (proved).** An unmeasured target interval e=(i,l) is identifiable from consistent real data iff its endpoints lie in the same connected component and either T is identifiable/known or its gain agrees with the transported forest gain between them.

Proof: distinct component offsets can vary independently and change a cross-component difference. Within one component they cancel. Write the homogeneous forest potential as p_i=a_C-h_i T, where h_j-h_i=w on each forest edge. The target becomes (a_D-a_C)+(w-h_j+h_i)T. If C=D, the only residual degree of freedom is the coefficient of T; it vanishes precisely under the stated condition. QED. This is a target certificate, not a blanket assertion that all samples must be recovered before any useful question can be answered.

**Theorem 3 (proved).** If the available pool of additional intervals is capable of full identification together with current data, exactly c-b new scalar measurements suffice and are necessary (c-1 if T already known). Each new row raises rank by at most one. A greedy addition of any rank-increasing available row terminates at full rank because otherwise the available pool would lie in the current span. The graph interpretation: a connecting edge removes a component degree of freedom, while the first winding cycle removes the total degree of freedom. When balanced and a window exists, its complement alone reveals the total by summing the two measurements. That need not recover all individual samples. Costs, access constraints and noise can invalidate an unweighted greedy selection policy; the theorem is about minimum count under the stated availability condition.

## Exact fault distance

For an injective observation map on the known-total affine space, define D as the minimum number of unequal observed coordinates between distinct profiles of that total. In homogeneous coordinates T=0, the observed differences are simply p_j-p_i. Hence D equals the edge connectivity (minimum nontrivial cut size) of the endpoint multigraph: any nonconstant p has at least all the edges across a nontrivial level-set cut in its support, and choosing p as the indicator of a minimum-cut side attains the lower bound. Subtract a constant to enforce p_0=0. A sufficiently large positive baseline makes the witnesses strictly positive.

Thus e detected erasures and t arbitrary erroneous scalar observations are guaranteed uniquely correctable when 2t+e<D. Conversely if 2t+e>=D, one can erase part of a minimum-distance witness difference and split the remaining disagreements across two error budgets, defeating unique decoding (subject to physically meaningful budgets). This is an exact code distance, not a stability bound under small additive noise. For a single length l with gcd(N,l)=1, the endpoint graph is one cycle (two parallel edges for N=2). Known total gives D=2. Unknown total gives D=1 because the N by N real matrix is invertible: any one-coordinate measurement perturbation is realizable.

**Theorem 4 (proved).** For the complete proper-interval family (every start, every length 1..N-1), the known-total distance is 2(N-1). Without total metadata it is min(2(N-1),N(N-1)/2), equal to the known-total value for N>=4.

Proof: the endpoint graph has two parallel edges per unordered pair, so any nonconstant homogeneous zero-total p has support at least 2s(N-s)>=2(N-1) across a cut of size s; a singleton cut attains it. For nonzero total difference, complementary windows have differences summing to that total. At least one entry per disjoint complementary pair is nonzero, giving N(N-1)/2. For N>=4 this bound is at least 2(N-1), and the zero-total witness attains it. For N=2 or 3, a unit impulse changes exactly sum_{l=1}^{N-1} l=N(N-1)/2 measurements and attains the lower bound. QED.

The full-family bound depends on retaining complements; merely accumulating many windows does not prove this distance.

## Integer arithmetic: redundancy without a redundant equation

Now restrict x to integers (e.g. event counts, not arbitrary audio amplitudes). Suppose the endpoint graph is connected and has nonzero winding. Let g be the gcd of the absolute nonzero windings of its fundamental cycles.

**Theorem 5 (proved).** The index of the integer observation lattice A Z^N within the integer points of its real column space is g. Equivalently the N nonzero Smith invariant factors are N-1 ones and g.

Proof: the prefix/total coordinate transform is unimodular over Z, with inverse x_i=p_{i+1}-p_i for i<N-1 and x_{N-1}=T-p_{N-1}. For a spanning tree, its reduced oriented incidence matrix has determinant ±1, as follows inductively by expanding at a leaf distinct from root zero. Integral row operations eliminate the prefix entries from every other row, leaving its cycle gain in the total column. Integral column operations remove the tree rows' total coefficients. The resulting block has an (N-1)-identity and one remaining column of signed fundamental cycle gains. Euclidean row operations reduce this column to g followed by zeros. All operations are invertible over Z, proving the Smith and index assertions. QED.

For all starts of a single length l coprime to N, the unique directed cycle winds l times; |det A|=l. An integer measurement vector admits an integer solution iff the sum of its entries is divisible by l. Necessity follows because every sample occurs in exactly l windows; sufficiency follows from the tree/cycle equations: integer T and integer y give integer p. For l>1 a single ±1 error in an integer measurement is always detectable even with N measurements for N unknowns. A single error of size l passes that divisibility check; detection is not correction. Positivity can impose extra constraints. The real-valued model has no such arithmetic protection.

Example N=5,l=2: x=(2,3,4,5,6), y=(5,7,9,11,8), sum=40, T=20. Changing any one reading by +1 makes sum=41; an exact real solution exists but no integer solution does. This is a physically interpretable consistency test for count telemetry, not a claim that audio quantization noise follows this model.

## Executed computational investigation

Two dependency-free JavaScript laboratories were executed as pure functions in the V8 tool environment. Reproduce locally with Node using the commands below (the native Node CLI wrapper was not itself run in this environment).

    node research/expeditions/window-forgets-boundary/laboratory.cjs
    node research/expeditions/window-forgets-boundary/arithmetic.cjs

The first enumerates every subset of all starts of each one- or two-length family for N=2..6, and all subsets of the full family at N=4. It compares graph rank and rank with appended total against fraction-free BigInt elimination on actual interval indicator rows. The count is family/subset instances; different families can contain identical subsets. It reconstructs a deterministic sample profile whenever possible and checks greedy repair on every 31st mask. It independently enumerates erasure thresholds for the full family at N=2..4.

| Check | Count |
|---|---:|
| Family/subset instances | 52,548 |
| Exact rank comparisons | 105,096 |
| Connected but balanced instances | 5,925 |
| Connected, balanced and fully covered | 3,514 |
| Successful reconstructions | 56,917 |
| Greedy minimum-count repair checks | 1,726 |

| Period | Unknown-total distance | Known-total distance |
|---:|---:|---:|
| 2 | 1 | 2 |
| 3 | 3 | 4 |
| 4 | 6 | 6 |

The arithmetic laboratory independently computes signed-gain gcds by breadth-first transport and compares to gcds of maximal minors via exact Bareiss determinants. For N=2..4 it checks all full-family subsets, including direct row-rank tests for each possible target. It checks every coprime (N,l) through N=15 and both signs of unit error at every measurement index.

| Check | Count |
|---|---:|
| Distinct maximal minors evaluated | 516 |
| Connected full-rank subset/index checks | 3,626 |
| Target observability checks | 49,544 |
| Coprime-length determinant checks | 71 |
| Single-unit error checks | 1,468 |

For N=4 among full-rank subsets, 3,529 have index 1, 56 index 2 and one index 3. All assertions passed. These finite counts are not probabilities of failures in real instruments, nor independent review. The receipts record the actual execution; the rank and determinant computations concern exact small integer matrices, not measured physical signals.

## Original PCM witness and speculative instrument

The laboratory renders original 8-kHz mono 16-bit PCM arrays, with a 100-ms sine tone per scalar, frequency 180+20*s Hz for value s and short linear fades. The latent profiles, public window sums and repaired window sums each produce two arrays. Equality is checked directly; FNV-1a is only a reproduction identifier.

| Score | A | B |
|---|---|---|
| Latent | ec0cff95 | 287878c4 |
| Public | e4871959 | e4871959 |
| Complement-repaired | e4871959 | 34e5584a |

All arrays are 6,444 bytes. The public recordings are byte-identical, while replacing a single window separates them. The waveforms are generated in memory, not asserted to be heard or perceptually validated.

**Design hypothesis:** a circular interval organ could treat a repeating latent amplitude/event sequence as a private score, and an arrangement of labelled listening windows as public voices. Moving a window's boundary changes the graph; substituting a complement preserves its endpoints but changes its winding. A performer can choose to expose the total, connect disconnected voices, or intentionally sustain ambiguity. The display could distinguish rank, target identifiability and integer consistency. This is an instrument proposal, not production TTS, not a claim that hearing is linear interval integration.

## Interpretation, negative sediment and transfer

The word “coverage” can refer to whether each sample appears in a window, whether the endpoint graph is connected, or whether the observation operator has full rank. These are different statements. A count of stored metrics is not a certificate of what those metrics can distinguish. A telemetry summarizer may keep every time segment represented and still hide a cumulative event total; a diagnostic request for a complementary window can reveal what another overlapping window cannot.

An analogy to semiotic context: the same relational endpoints can support distinct cumulative histories, and the oriented path between those endpoints is part of the sign's specification. This is not a reduction of linguistic understanding or Brier's theory to graph theory. Prior MHAC excursions into exact clock constraints, phase winding, erased samples and spatial aliasing motivate the question, but no earlier draft is treated as accepted empirical evidence.

Negative cases: with a known total and connected endpoints the rank ambiguity vanishes; with disconnection a nonzero winding can recover total but not necessarily individuals; nonnegative profiles on the boundary may uniquely identify despite real rank deficiency, whereas strict positivity permits sufficiently small nullspace perturbations; unknown labels, aperiodic boundaries, overlapping nonrectangular weights, quantized/noisy reports, nonlinear peak summaries and actual RMS of signed signals are different models. The code does not infer an underlying waveform from its power envelope. Real invertibility does not certify numerical conditioning. Unit-error detection in the integer model is not robust error correction or a probabilistic guarantee. An open direction is optimal noisy repair using path lengths, cycle winding and measurement covariance.

## Source ledger and integrity

- Tibor Jordán, Viktória E. Kaszanitzky, Shin-ichi Tanigawa, “Gain-Sparsity and Symmetry-Forced Rigidity in the Plane,” Discrete & Computational Geometry 55 (2016), 314–372, [DOI](https://doi.org/10.1007/s00454-015-9755-1). Open publisher HTML; read introduction and relevant §2.1–2.2 passages, especially Proposition 2.2 and Lemma 2.3, on forest switching and cycle balance. These support established gain-graph ancestry; the interval-measurement application and proofs here are reconstructed independently from the defined model. Entire paper not read.
- Andrea C. Burgess, Robert D. Luther, David A. Pike, “The edge-connectivity of vertex-transitive hypergraphs,” Journal of Graph Theory 105(2), 252–259 (2024; online 29 September 2023), [DOI](https://doi.org/10.1002/jgt.23035). Open publisher HTML; read abstract and §1 including Theorem 1. Establishes edge-connectivity terminology and reports Mader's classic vertex-transitive graph result. That theorem is not needed for the complete-family proof, which directly counts cuts; no hypergraph result transferred.
- [Windowed Moving Average Filters](https://blog.mbedded.ninja/programming/signal-processing/digital-filters/windowed-moving-average-filters/), technical tutorial, frequency-response section encountered in search; discovery only, not primary evidence or an authority for the proofs. Conventional rectangular filtering is a related signal-processing representation. No source text copied.
- All access/reading and computations by the same AI agent on 24 November 2026. No external review, auditory trial, participant evidence, source-corpus promotion, or claim of priority. The Smith reduction is given in full rather than relying on an unverified historical attribution.

Repository reconciliation: main inspected at 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity, validation and research workspace read; latest open issue/PR titles and branch search inspected; dedicated issue created and body/comments read, branch uniqueness checked. Prior #317 exact-head workflow returned success, but its draft/independent-review status was not altered. Only this issue's expedition directory is changed; no frozen records or manifests. Full repository CI and independent critique remain gates before integration.

## Fiction: the circular station

The night clerk inherited a clock without a midnight. Every accountant reported what happened between two hands. The accounts overlapped, and there was not one hour without a witness. Nevertheless two days of different length fitted the same accounts.

The apprentice did not add another accountant. She asked one to report the other way round the clock.

The clerk looked at the ledger. There were still four accounts.

*It was the first time one of them had completed the day.*
