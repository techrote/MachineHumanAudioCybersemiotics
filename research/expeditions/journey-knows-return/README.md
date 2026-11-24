# The Journey That Knows Its Return

Refs #396 · 2026-11-24 · Exploratory mathematical derivation, synthetic experiment, design conjecture and original score. Outside accepted Track E/G; no mathematical priority, empirical listener evidence, real clock calibration or production deployment claimed.

## Anomaly

Three clocks exchange messages around a ring. Each local timestamp difference is three units. One world has physical clockwise travel times (3,3,3); another has (2,5,2). The clocks' relative offsets differ, but all six directed timestamp differences remain three and each round-trip time remains six. Both clockwise totals equal nine. A receiver can know the total journey time exactly without knowing any leg exactly. This is not independent error cancellation by averaging; it is a deterministic gauge symmetry.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; root AGENTS, RAG, programme, runbook, integrity, validation and project foundations read; 257 branch names paginated, 100 recent open issue/PR search results and 100 open PR snapshots inspected, targeted searches for clock synchronization and one-way terminology. Prior #389 exact-head workflow returned completed/success. The #261 report on mhac-260/clock-that-cannot-shuffle investigates feasible event orderings given unrestricted offsets, not inference of the offsets from packet transit observations. The #229 report on mhac-228/staircase-cycle-debt minimizes uniform error of fitting antisymmetric comparisons; this expedition instead retains the complete feasible offset polytope and queries physical directed transit times. Both reports read in relevant passages; neither branch touched. No central artifacts or protocol modified.

## Model and exact pair interval

Let G be a finite connected undirected graph of available reciprocal links, with both directions observed separately. Local clocks have common unit rate, unknown constant origins x_i. For each directed edge i->j the measured timestamp difference is a_ij, physical transit time is l_ij >= 0, and

    a_ij = l_ij + x_j - x_i.

All exchange observations refer to the same static offsets; transmission/receipt timestamps are exact; holding times are excluded. This model does not assume reciprocity of the physical delays. Round-trip r_ij = a_ij+a_ji = l_ij+l_ji. Nonnegative r alone does not ensure feasibility around cycles.

Fix one origin x_0=0. Feasibility is precisely x_j-x_i <= a_ij for all arcs. A negative directed cycle refutes the transcript; otherwise shortest paths D(i,j) exist and x_j=D(0,j) is a feasible witness. Gauge translations change the origins but not differences. More generally if x is feasible, all l_ij are recovered as a_ij-(x_j-x_i). Conversely any compatible physical world has exactly this form. Hence the graph inequalities describe the whole observation fibre, not just a relaxation.

For any vertices u,v, the sharp interval of x_v-x_u is [-D(v,u), D(u,v)]. Each path gives an upper bound by summation. The upper endpoint is attained by x_j=D(u,j)-D(u,0), and the lower by the analogous potential rooted at v. Convexity attains every intermediate value. The argument also works for signed a_ij if there is no negative cycle.

For a directed walk P from u to v, the physical sum L(P) is A(P)-(x_v-x_u), with A(P) the sum of recorded differences along that walk. Thus

    L(P) in [A(P)-D(u,v), A(P)+D(v,u)].
    width(P) = D(u,v)+D(v,u).

This width depends on the endpoints and complete transcript, not on the length of the walk. A closed walk has width zero, including the ordinary reciprocal two-edge round trip. Subtract two walks with the same ordered endpoints: their physical difference is exactly their recorded difference, even if both totals are separately uncertain. A route may revisit edges, and the result still holds. It is not a claim that the physical end-to-end response time includes no processing delays.

Example with all a positive: in a triangle record a_AB=a_BC=a_CA=1 and reverse differences 9. Every reciprocal round-trip is 10. For A,B, D(A,B)=1, D(B,A)=2, hence the width of l_AB is 3 instead of the isolated-link width 10. A shortest two-hop return gives an informative inequality, without a new clock.

## The transport theorem: arbitrary linear delay queries

Let c_ij be arbitrary real coefficients on observed directed arcs, and define Q=sum c_ij*l_ij. Set K=sum c_ij*a_ij and b_v=sum incoming c - sum outgoing c (signed net demand). Then Q=K-b dot x; sum b=0. Define T_D(b) as the minimum cost of transporting mass b^- to b^+ using directed shortest-path costs D(i,j). Mass need not total one; zero mass costs zero.

**Theorem:** Q has sharp interval

    [K-T_D(b), K+T_D(-b)]
    width = T_D(b)+T_D(-b).

Proof: maximize b dot x under x_j-x_i <= a_ij. Fix one gauge, or leave it free since b sums to zero. The finite LP is feasible and bounded modulo gauge. Its dual has nonnegative arc flows f_ij with net inflow b and objective sum a_ij*f_ij. By LP strong duality the optimum is attained and equal. Decompose each feasible flow into directed source-to-sink paths and cycles; removing cycles cannot increase cost (no negative cycle); replacing each path by a shortest path cannot increase cost. The resulting mass coupling costs at least T_D(b). Conversely expand a minimizing coupling along shortest paths, obtaining a feasible flow of the same cost. This proves equality. Apply the same reasoning to -b for the other endpoint; convexity gives all interior values. For signed a, D may be negative, but the directed LP and no-negative-cycle argument still work. It is not necessarily a metric transport problem until the symmetric case below.

An equivalent statement: only the divergence b of the query determines its uncertainty. A purely circulatory query (b=0) is exact, regardless of the individual transit ambiguities. Two different queries with equal divergence have the same width and differ by a known constant. With strictly positive delays in some compatible world, the feasible offset region contains an open neighborhood modulo gauge, so conversely only b=0 is invariant. Boundary-only feasible worlds can have further invariant queries; do not mistake that sufficient condition for universal necessity.

A stronger local characterization: put u~v iff D(u,v)+D(v,u)=0. This means their offset difference is constant in every feasible world; it is an equivalence relation. An arc inequality is universally tight iff its reverse-distance lower bound meets its upper bound, which also makes the endpoints equivalent. Average, over every inequality that is not universally tight, a feasible witness with strict slack on that inequality (if none, take any feasible witness). At that average all non-forced inequalities have positive slack simultaneously. One may perturb the origin of each equivalence class independently by sufficiently small amounts, keeping forced equalities. Therefore Q is invariant iff the sum of b over every equivalence class is zero. This last characterization is analytical; the census below does not exhaustively check the equivalence-class criterion.

## Sharp worst-case guarantee using only round-trip lengths

Hold the undirected link round-trip lengths r_e >=0 fixed. Let R be their shortest-path pseudometric (zero-length components may be contracted). For each query divergence b define W_R(b) as the symmetric transport cost from b^- to b^+. Across all feasible timestamp transcripts with these round trips,

    max width(Q) = W_R(b).

Proof: take any two feasible origins x,y for the same transcript. For every edge, the difference z=x-y satisfies |z_j-z_i| <= a_ij+a_ji=r_e. Thus z is 1-Lipschitz for R. Every feasible transport plan gives |b dot z| <= its cost by telescoping; minimizing gives width <= W_R(b). For equality choose the symmetric transcript a_ij=a_ji=r_e/2. Its feasible set is the half-sized Lipschitz ball, centrally symmetric. Therefore its width is exactly the maximum b dot z on the entire Lipschitz ball, equal to W_R(b) by finite LP duality (or the preceding theorem, since D=R/2 and symmetric transport costs agree under reversal). This is a worst-case information statement, not a probability distribution over delays. The midpoint of the exact scalar interval is the minimax absolute-error estimate, with worst-case error half the width. Independently chosen midpoints for multiple queries need not have a common offset witness.

On a tree there is a unique undirected path between nodes. For each edge e remove it, and choose either resulting vertex component S_e. A transport plan must ship at least |sum_{v in S_e} b_v| net mass across that edge; the unique signed flow with divergence b achieves all these edge totals simultaneously, decomposing into paths with no cancellation. Therefore

    W_R(b)=sum_e r_e * |sum_{v in S_e} b_v|.

Indeed on a tree the width equals this expression for EVERY feasible transcript with those round trips: oriented edge differences can vary independently in their respective intervals, and there are no cycle consistency constraints beyond the reciprocal pairs. On a cyclic graph shortest-path alternatives can shrink uncertainty, or an entire class may become exactly determined by directional data. The bound uses all round-trip lengths but is a bound on the fibre conditional on the full timestamps, not an estimate based only on round trips with the timestamp differences discarded.

Example of aggregate cancellation: along A-B-C-D, each link has r=10. The sum of A->B, B->C and C->D delays has worst width 30. Add a direct A-D measurement with round-trip 2; the same three-leg sum now has worst width 2, while the round trips on all three original legs remain unchanged. A closed walk around these four vertices has width zero. If instead the three forward legs have alternating coefficients (+1,-1,+1), divergence is no longer concentrated at the two endpoints; the new shortcut alone need not remove the uncertainty of the interior nodes. The relevant object is the query's mass imbalance, not its number of terms.

Exact relative calibration between two nodes can be inserted as a zero-round-trip artificial constraint edge carrying the known offset and its negative (this is a mathematical constraint, not a physical zero-delay transmission). In the worst-case Lipschitz formula this contracts the calibrated relationship. With all physical round trips positive and consistent exact relative calibrations, a query is guaranteed exact for every feasible transcript precisely when its net demand is zero in each calibrated connected component. Calibration of a spanning tree is sufficient for every query; fewer calibrations may suffice for a particular query. This observation requires the calibration constraints themselves to remain valid over the whole observation window.

## Qualification

[Laboratory](laboratory.cjs) and [execution receipt](execution.json). One AI agent wrote both the calculation and proof. The core was actually executed in a V8 isolate, not a native Node process. It enumerates every nonnegative directed measurement profile on a triangle and three-edge path with integer arc values 0..2, plus 256 deterministic seeded four-node cyclic profiles (including symmetric cases). Duplicate profiles, if any, count as executions, not independent samples.

For integer arc weights the rooted feasible polytope has integer vertices: at a vertex the tight equality graph must connect every node to the root (otherwise one component could be perturbed); each origin is a sum of integer tight edge weights. A bounded linear objective therefore attains its extrema at integer points. The exhaustive oracle enumerates all integer origins within valid pair bounds and filters by original arc inequalities. The distinct transport oracle uses Floyd–Warshall and literal unit-mass assignment enumeration; integer mass couplings have integral optimal plans by the standard transportation-polytope integrality property. The query family is nonzero integer b in [-2,2]^n, sum zero and positive mass at most four.

| Actual computation | Count |
|---|---:|
| Executed profiles | 1,714 |
| Feasible integer origin vectors | 30,232 |
| Pair interval comparisons | 11,052 |
| Strictly improved directed upper bounds | 948 |
| Linear query extrema comparisons | 95,862 |
| Strict improvement over round-trip worst bound | 8,632 |
| Exact queries with positive round-trip-only worst bound | 1,008 |
| Symmetric profiles (all query widths attain round-trip bound) | 118 |
| Assertion failures | 0 |

These counts are deterministic synthetic results, not incidence estimates. The direct oracle uses shortest-path bounds for its search box; original constraints filter feasible points. The proof of the box and integrality is part of the analytical argument, not an independent empirical result. Negative-weight transcripts and arbitrary real coefficients are handled by the proof but not by the census. Disconnected networks would require independent gauges and per-component mass balance. The complete native repository checkout failed at DNS resolution for github.com; native Node CLI and full repository checks are not claimed.

Run from repository root:

    node research/expeditions/journey-knows-return/laboratory.cjs build/journey-knows-return

The optional native filesystem adapter emits the four WAV files and the receipt to stdout; the core generated their byte arrays and fingerprints, but that adapter has not yet been exercised here.

## Original score: The Return Organ

Three markers (A/B/C plus return to A) are voiced as different integer square-wave pitches, with the next attack delayed by the modeled transit time (100 ms per unit). The renderer uses a tapered envelope, 8 kHz mono PCM16. All files are 15,724 bytes. Physical world A has three equal intervals; physical world B has intervals 2,5,2. Their final marker occurs at the same time. Both public receipts have the same three recorded intervals.

| Score | FNV-1a fingerprint |
|---|---|
| Physical A | 676fa25a |
| Physical B | ea77db5a |
| Receipt A | 676fa25a |
| Receipt B | 676fa25a |

Direct byte equality/inequality checked, not just fingerprints. The score is an original synthetic illustration, not a recording of a network or a human discrimination study. A future performance instrument could let musicians distribute changes in clock origins across the vertices, hearing the physical route transform while the receipt remains unchanged. A separate control could add calibrated edges, shrinking the admissible performance space without changing the fixed observed score. No production renderer or listener experiment authorized.

## Source ledger and interpretation

- D. Mills, J. Martin (ed.), J. Burbank, W. Kasch, RFC 5905, June 2010, [NTPv4 specification](https://datatracker.ietf.org/doc/rfc5905/), §8 printed pp. 28–29, timestamp arithmetic around the four-timestamp equations. HTML passage inspected. The standard computes a half-difference offset estimate and a round-trip delay. Our static nonnegative-delay model makes the asymmetry assumption explicit; it is not a description of all NTP filtering, frequency discipline or clock precision handling.
- J. Lundelius and N. Lynch, *An Upper and Lower Bound for Clock Synchronization*, Information and Control 62 (1984), 190–204, [author-hosted paper](https://groups.csail.mit.edu/tds/papers/Lynch/ic84.pdf), p.190 abstract and introduction inspected, including page image 0. Established impossibility of exact synchronization under bounded delivery uncertainty even with perfect rates. Their distributed synchronization bound and our conditional scalar query widths are different objectives; no claim of strengthening their result. Remaining proof sections not read for this expedition.
- C. Villani, *Topics in Optimal Transportation*, AMS Graduate Studies in Mathematics 58 (2003), [university-hosted text](https://www.math.ucla.edu/~wgangbo/Cedric-Villani.pdf), printed p.34 §1.2.1 Thm 1.14 and p.35 Cor. 1.16, extracted text inspected. Page-image retrieval failed due to source size; no visual verification claimed. Established Kantorovich–Rubinstein duality; our proof uses finite LP and explicitly connects physical-delay queries to its symmetric case. Not a full-book reading.
- Repository comparison: #260/#261 and #228/#229, actual reports read in bounded passages as above. These are prior exploratory AI artifacts, not independently validated publications.

The mathematical results are self-contained derivations using established machinery. No novelty priority search was sufficient to assert an original theorem in clock synchronization or optimal transport. Source check and same-agent computation performed by ChatGPT on 2026-11-24; no human independent review, empirical validation, source corpus admission or protocol change.

**Design conjecture:** a machine announcing elapsed-time claims should distinguish a gauge-invariant result, a bounded scalar result and a fully reconstructed timing history. A receipt could contain the observation interval, clock-rate assumption, graph, original directed measurements, known relative calibrations, query divergence and its sharp interval. It should not treat individually reported error bars as independent. This is a candidate epistemic contract for later scrutiny, not an approved MHAC interface.

**Countercases and transfer limits:** drifting clocks, packet-specific variable delays, correlated lower bounds, clock discontinuities, unobserved processing time, path changes and quantization demand new constraints or a new model. Repeating an identical static observation does not shrink its fibre; new independent constraints can. A single external absolute reference fixes a global origin but does not alone determine relative origins. Physical simultaneous arrivals need a shared temporal frame. The result does not establish how humans interpret time, sound or meaning. An empirical future test would compare comprehension of exact totals versus independently uncertain components; it is not performed.

**Fiction:** The messenger arrived back at the tower exactly at nine. The clerk asked him how long each road had taken. He answered that the three village clocks had all agreed on three. The clerk wrote nine in ink and the three threes in pencil. The messenger was puzzled. The clerk explained: the ink belonged to the journey, the pencil to the clocks.

## Disposition

Isolated additive issue #396 branch only. Draft/HOLD until exact-head repository checks, native reproduction and substantive review. No merge, manifest update, human gate or canonical promotion. The next useful critique is to independently test the signed-arc and zero-distance-class extensions; no new worker is presumed to have performed it.
