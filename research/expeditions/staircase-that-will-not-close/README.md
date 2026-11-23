# The Staircase That Will Not Close

**Refs #228 · 2026-11-23 · mathematical reconstruction, exact synthetic computation, original audio, design conjecture and fiction.** Not a Track E/G inclusion, a human study, a psychophysical mapping, or a priority claim.

## The anomaly: a number that cannot be a place

A committee of machines is asked to rank alternatives. Each pair receives a signed comparison magnitude. The orchestrator wants to collapse the comparisons into one score per alternative and report differences between those scores. Suppose a comparison says that moving from A to B should increase a score by one unit; B to C should likewise increase it by one, C to D by one, and D to A by one. Walking the stairs returns to the same labelled floor but four units higher.

The issue is not merely that a majority can cycle. Even unanimous transitive ordinal preferences can give nonadditive comparison magnitudes. We need to distinguish three questions: is the order representable, are the numerical differences representable, and how much numerical distortion is unavoidable under a specified representation?

**Reconciliation:** observed main at 495a98ca12bae467a507031f04931aa4254b1866. Read root instructions, RAG, programme, runbook, integrity, validation and recent open issues/PRs/branches; inspected issue #191 (binary parity relations), #220 and its actual average-voice report (calibration debt), #226 (performative prediction). These remain separate: binary satisfiability is not real-valued approximation, forecast calibration is not ordinal ranking, and no outcome intervention is modelled here. Created fresh issue #228 and branch mhac-228/staircase-cycle-debt; all artifacts are additive, no canonical records or other branches changed.

## Source boundary and research lineage

- Xiaoye Jiang, Lek-Heng Lim, Yuan Yao and Yinyu Ye, *Statistical ranking and combinatorial Hodge theory*, arXiv:0811.1067, [public primary text](https://arxiv.org/abs/0811.1067), abstract, §1 (especially edge flows, gradient, curl and harmonic components), §2.3 Definition 2.3, §5.2 Theorem 5.2 and opening of §6. These selected passages were inspected on 2026-11-23, not the entire paper. The authors treat pairwise comparisons as edge flows and distinguish globally representable score differences from cyclic residuals; they discuss L2 and L1 objectives. This expedition's L-infinity objective is a separate choice, not a claimed consequence of their numerical experiments or a novel ranking theorem. Their local-versus-global exact-consistency distinction is particularly relevant to our sparse-square control.
- Richard M. Karp, *A characterization of the minimum cycle mean in a digraph*, Discrete Mathematics 23 (1978), 309–311, [DOI 10.1016/0012-365X(78)90011-0](https://doi.org/10.1016/0012-365X(78)90011-0); [1977 Berkeley technical report metadata](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1977/29121.html) and [DBLP bibliographic record](https://dblp.org/rec/journals/dm/Karp78.html). Metadata verified, not a claimed full-text reading. Cycle mean is established mathematical machinery. The elementary derivation below stands on its own; no claim that Karp discussed this communication application.
- [Stanford Encyclopedia of Philosophy, Social Choice Theory](https://plato.stanford.edu/entries/social-choice/), substantive revision 2022, §1.1 (Condorcet paradox) and §3.5 / §5.1 selected passages on majority choice and aggregation. Secondary source, not Condorcet's 1785 text. It gives the classic cycle of three individually transitive preferences; the four-candidate numerical construction below is explicit and separately verified.

These sources anchor the mathematical genealogy, not human listening or decision evidence. No assertion of priority; the maximum-cycle-mean formula is a standard type of difference-constraint result. The original work here is the bounded MHAC construction, census, controls, representation critique and sound design.

## The exact model and theorem

Let G be a finite simple undirected comparison graph. Each observed edge u,v has an antisymmetric real target w(u,v) = -w(v,u). A scalar score s assigns one number to each vertex. We explicitly choose the model that target w(u,v) should equal s(v)-s(u), and the objective

D = min_s max_observed_edges |w(u,v) - (s(v)-s(u))|.

Missing comparisons remain absent, not zero. A zero-weight observed comparison is an equality target. Disconnected components are permitted; scores have independent additive gauges. Empty graphs have D=0. The target need not be a probability or a utility; the additive cardinal model is a convention under test.

**Theorem (exact uniform distortion):** D equals the maximum absolute mean weight over simple directed cycles, including zero-valued two-arc reverse cycles; take zero when there is no cycle. A cycle C of length k gives

D >= |sum_C w| / k.

Proof of lower bound: sum all k fitted differences around C. They telescope to zero. The magnitude of the target sum cannot exceed k times the worst error. This proves every cycle bound.

Proof of attainability: let d be the maximum mean over oriented cycles (symmetry under reversal gives the absolute form). Replace each directed arc weight w by w-d. Every directed cycle has nonpositive total; closed walks decompose into simple cycles, so every closed walk is also nonpositive. Add a conceptual super-source with a zero-weight arc to every vertex. Define s(v) as the maximum total weight of any path ending at v, including the zero-length path. Removing a nonpositive closed subwalk cannot lower a path's weight, so the maximum is finite and attained by a simple path with at most |V|-1 edges. Appending an arc shows s(v) >= s(u)+w(u,v)-d. Applying the same inequality to the reverse arc gives s(v) <= s(u)+w(u,v)+d. Thus every edge error is at most d. With the lower bound, D=d. No uniqueness is implied.

The returned cycle is a dual lower-bound certificate; the returned potential is a primal upper-bound certificate. They are checkable independently. A nonzero certificate locates a representation mismatch, not the wrong witness or a source to suppress.

For integer targets, a maximizing cycle mean is rational with denominator no greater than its length. The exact oracle scales the potential by that denominator and uses integer path relaxation. It enumerates cycles (factorial worst case) for small graphs; it is not a scalable implementation of Karp's algorithm. Its separate synchronous Bellman–Ford feasibility check searches all candidate fractions on the bounded four-vertex census. Runtime arithmetic is exact within the declared input limits.

**Ordinal distinction.** If all strictly positive edges are oriented from lower to higher, an ordinal score respecting those strict comparisons exists iff that directed graph is acyclic (topological sorting). Here zero-weight edges do not impose ordinal equality; if ties must be preserved, contract equality components and check the resulting directed graph separately. An ordinal ranking may exist even when D>0. For example, w(A,B)=w(B,C)=w(A,C)=1 is unanimous in direction yet cannot fit three unit differences; D=1/3. Conversely a tree always fits all numerical targets exactly, even if its comparisons are unreliable. D is not a truth, quality, calibration or consensus metric.

## A sharper anomaly: unanimity and cyclic majority can incur the same maximal debt

Suppose every comparison is taken from the same N complete strict rankings of n alternatives, with equal ballot weight. Set normalized w(u,v) = (votes preferring v to u minus votes preferring u to v)/N. All weights lie in [-1,1].

For any simple cycle of k>=3 vertices, each individual strict ranking must oppose at least one of the k orientations and support at least one. Its signed sum along the cycle is therefore between -(k-2) and k-2. Averaging preserves the bound:

|sum_C w|/k <= 1 - 2/k <= 1 - 2/n.

Two distinct constructions attain D=1-2/n for every n>=3:

- **Unanimity:** every ballot has the same order. A loop following n-1 successive preferred directions and then reversing the last comparison has total n-2. All ordinal directions are consistent.
- **Cyclic rotations:** n voters rank the n cyclic rotations of one fixed order. Along the reverse-label cyclic route in our sign convention, each edge is supported by n-1 voters and opposed by one. Each edge margin is (n-2)/n. The majority relation contains a strict directed cycle.

So **the maximal possible uniform cardinal fitting error can be identical in a perfectly unanimous panel and a genuinely cyclic one**. For n=4 both normalized debts are 1/2. The fitted scores in our construction differ: one is ordered, the other entirely tied. Calling D a measure of disagreement between people or agents would be a category error. The normalization bound assumes the same complete panel (or common nonnegative normalized ballot weights). It need not hold for edge-dependent respondent subsets, arbitrary independent pairwise judgements or different scales. A four-edge square with every oriented target +1 has D=1, but cannot arise from the same complete panel.

Triangle diagnostics are also insufficient quantitatively: for the four-vertex cyclic rotations, the maximum triangle mean is 1/3 but the four-cycle mean is 1/2. On complete graphs, zero triangle curl is equivalent to exact representability; this does **not** imply maximum triangle mean equals optimal uniform distortion. On sparse graphs even the zero test fails: the square with no diagonals has no triangles and D=1. This is an exact negative control.

## Computational experiments

The experiments were executed on 2026-11-23 in a JavaScript runtime, using the same pure function definitions committed to the two Node scripts. No external dependency, random sample, solver tolerance or human data was involved. The optional Node file-writing adapter was not executed in this session. See [RESULTS.md](RESULTS.md) and [PANEL-RESULTS.md](PANEL-RESULTS.md) for exact machine-produced receipts.

**Census A.** On four labelled vertices enumerate all 4^6=4,096 possible simple comparison graphs. Each unordered pair has one of four states: absent, -1, 0, +1. For every graph compare the cycle-mean oracle with a separate exact rational threshold feasibility search by synchronous Bellman–Ford relaxation. All 4,096 agree. The complete observed graph subpopulation has 3^6=729 cases.

| Result | All graphs | Complete graphs |
|---|---:|---:|
| Cases | 4,096 | 729 |
| Nonzero uniform debt | 3,056 | 714 |
| Strict positive-edge directed cycle | 488 | 186 |
| Nonzero debt but no strict directed cycle | 2,568 | 528 |
| Triangle-only bound strictly too low | 576 | 162 |
| Zero triangle bound but positive debt | 186 | 0 |

These are counts of labelled edge states, not prevalence estimates. The code includes disconnected, exact gradient, sparse square, tree, malformed input, and 3–8 vertex sharp same-panel controls. The Bellman–Ford cross-check is algorithmically distinct but implemented and executed by the same research agent, not an independent reviewer.

**Census B.** Enumerate all multisets of four complete strict rankings of four labelled alternatives: 24 possible rankings and C(27,4)=17,550 equally counted multisets. This is not uniform sampling of labelled voters; different multiset multiplicities would change population frequencies. Use an independent explicit enumeration of all triangles and four-cycles. Margins are exact integers prior to division by four. Debt is represented as integer multiples of 1/48.

| Normalized D | No strict majority cycle | Strict majority cycle |
|---:|---:|---:|
| 0 | 1,068 | 0 |
| 1/6 | 6,912 | 0 |
| 1/4 | 2,400 | 0 |
| 1/3 | 5,040 | 0 |
| 3/8 | 1,920 | 0 |
| 1/2 | 204 | 6 |

All 210 maximally distorted panels include just six with strict majority cycles. This census exposes the difference between a strict-order contradiction and a cardinal compression mismatch under one deliberately chosen objective. No claim about real panels follows. Ties in majority comparisons are ignored for strict cycle detection; a tied relation is not necessarily a consistent weak order.

Reproduction from this directory (Node.js, no package installation):

```sh
node oracle.js
node panel_and_audio.js
node panel_and_audio.js ./generated
```

The last command writes two generated WAVs; binary files are not required in the repository.

## Instrument, application and fictional afterword

**Original synthetic instrument — The Unclosed Staircase.** On one stereo channel a walker integrates the requested comparison increments as additive Hz steps. On the other it follows the fitted global score potential, returning to its initial frequency when the path closes. The acoustic mapping is an authored representation, not a psychoacoustic claim about perceived interval equality. Each note is 0.2 seconds, 16 kHz stereo, 16-bit PCM, integer triangle oscillator with a short envelope. The two generated one-second PCM WAV byte arrays were constructed in memory: 64,044 bytes each; regression FNV-1a checksums in the receipt. No listening test or claim of perceptual efficacy.

| Profile | Local interval integration (Hz) | Global scalar fit (Hz) |
|---|---|---|
| Four rotations | 400, 440, 480, 520, 560 | 400, 400, 400, 400, 400 |
| Unanimous | 400, 320, 400, 480, 560 | 400, 280, 320, 360, 400 |

Both left paths end 160 Hz above their starting frequency and both right paths return. Their internal shapes differ. A closure tone alone cannot tell whether the panel was unanimous or cyclic. The scores use the exact four-voter raw margins and corresponding optimal potential; the choice of 20 Hz per unit is arbitrary. In a log-pitch variant one could encode comparison differences in cents instead; this would change the acoustic scale, not the telescoping argument.

**Design conjecture:** a multi-agent comparison record should retain alternatives, edge direction, original magnitude and scale, comparison population/provenance, strict ordinal cycle witness if any, uniform-error witness if relevant, and the chosen projection objective. Treat a forced scalar score as an explicitly lossy representation, rather than a hidden default. A useful decision may require no cardinal reconstruction; ordinal ranking, Kemeny optimization, partial ordering, outranking, and retaining a graph can be more appropriate. Kemeny disagreement is not this L-infinity distortion. One scalar is perfectly adequate when the task requires only an authorized order or the input is already a gradient. A high residual can simply diagnose the wrong encoding convention; changing the target to rank distances would make a unanimous ranking exactly representable. A low residual is not evidence for independence, truth, or calibration.

**Fiction — The Staircase That Will Not Close.** In the municipal archive, each corridor had been measured by a different clerk. All four measurements were correct according to their individual ledgers. The architect did not accuse any of them of fraud; instead, she asked whether a floor-number was the right sort of object to carry their measurements. She commissioned two instruments. One played the corridors as they had been described, the other played the building as it could be built. At the entrance they sounded the same. At the exit, one was still ascending.

*The committee had agreed on every direction. It had not agreed to inhabit a number line.*

No participant study, device implementation, evidence-stage promotion or human validation is asserted. Further work: independent review of proof and arithmetic, exact-head repository checks, and only if warranted an explicit design evaluation of graph-versus-scalar reports.
