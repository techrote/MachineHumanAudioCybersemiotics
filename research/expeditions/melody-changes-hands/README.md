# The Melody That Changes Hands

Expedition #530, 2026-11-25. Original mathematical derivations and synthetic digital audio. Not canonical Track E/G evidence, a claim of mathematical priority, or a human study.

## The anomaly: a perfectly observed sound need not identify its owner

The previous duet and four-singer expeditions (#514 and #522) concern simultaneous anonymous semantic fields. This expedition changes the observation axis to time. A machine announces its continuous state by pitch, and a receiver obtains the exact unordered pitch population at each of two instants. Even if every pitch is measured correctly, it may not know which machine changed state.

Two machines may appear to glide through each other, or approach and retreat. With equal source waveforms and matching phase at their meeting, both assignments can produce the exact same mono recording. This is not merely an inability of a chosen decoder. It is an observation-level collision.

## Mathematical contract

There are n persistent labelled sources, initially at strictly ordered real values x_1 < ... < x_n, and at the next observation the strictly ordered anonymous values y_1 < ... < y_n are known. A common maximum displacement v >= 0 is enforced: source i can end at y_j iff |x_i-y_j| <= v. For a time separation T and a speed bound V, v=VT. Values can be pitch, log-frequency or another one-dimensional state, but the metric and units must be fixed first.

An assignment is a permutation p mapping each initial rank i to its final rank p(i). No births, deaths, duplicate endpoint values, acceleration constraints, source-specific limits, measurement errors or other distinguishing cues are allowed. Intermediate trajectories may be arbitrary continuous V-Lipschitz paths; any feasible endpoint assignment can be realized by straight interpolation. Initial rank labels are already known. An identity receipt for i is the final rank p(i), not an unverified extra pitch measurement. The sender or trusted provenance mechanism must supply this relation.

## Exact identifiability and possible meetings

The sorted assignment p(i)=i is feasible iff any assignment is feasible. Proof: an inversion in a matching can be uncrossed without increasing its maximum distance. If i<j and p(i)>p(j), the two cross distances bounded by v imply the two corresponding straight-order distances are also bounded by v, by comparing the ordered endpoints. Repeated inversion removal proves the assertion. Equivalently the least feasible displacement is max_i |x_i-y_i|.

Assume feasibility. A distinct assignment exists iff some adjacent sorted pair can be exchanged:

    |x_i-y_(i+1)| <= v and |x_(i+1)-y_i| <= v.

Necessity: any nonidentity permutation crosses a rank cut in both directions. Choose a cut between i and i+1. A permitted edge from a row at or below i to a column above i, together with the permitted diagonal edge, implies the edge from i to i+1 by ordered interval containment. The reverse crossing analogously permits i+1 to i. Sufficiency: transpose that adjacent pair.

For two ranks i<j define their swap threshold

    C_ij = max(|x_i-y_j|, |x_j-y_i|)
         = |(x_i+x_j-y_i-y_j)/2| + ((x_j-x_i)+(y_j-y_i))/2.

This exposes two separate terms: movement of the midpoint and the combined half-widths. Gap alone is not an exact test. With x=(0,2), y=(2,4), v=2, each pair has gap 2 but the swap threshold is 4. The first ambiguous displacement, for n>=2, is max(max_i |x_i-y_i|, min_i C_(i,i+1)).

The same pair threshold determines whether two sources following the sorted assignment could meet somewhere during the interval. If they meet, exchange their paths after the meeting: the new V-Lipschitz paths realize the swapped endpoints. Conversely, straight interpolations realizing the swapped endpoints must cross by continuity; exchange their tails there to obtain sorted paths that meet. Thus a unique endpoint assignment excludes every possible intermediate meeting under this speed-only model. An ambiguous endpoint assignment does not establish that a meeting actually occurred. The model allows a cusp in velocity; an acceleration bound can invalidate this splice argument.

## Two identity contracts

A common mistake is to find a small set of identity receipts proving a particular predicted assignment and then claim that those same receipts identify every possible assignment.

For an arbitrary feasible proposed matching p, create an undirected swap graph G_p on the initial ranks. Join i,j when exchanging p(i),p(j) is itself feasible. A set of authenticated identity receipts certifies p exactly iff it is a vertex cover of G_p, assuming the returned values agree with p.

Proof: if an uncovered edge exists its transposition gives another matching with all the same receipts. Conversely, remove anchored rows and their matched columns. If any alternative remains, the union of the two matchings contains an alternating cycle. A shortest directed alternating cycle has length two (two rows and two columns): the permitted bipartite graph has interval neighborhoods on the ordered columns, also after deletion. In any longer simple bipartite cycle, take its smallest column c; its two incident cycle rows each connect to a different other cycle column. The row reaching the farther one must also contain the nearer one, giving a chord. In a shortest directed cycle of the matching-relative arcs (row i can take p(j)), that chord is a non-successor arc and closes a shorter cycle. Thus a two-row swap survives, contradicting the cover. This proof also works for an arbitrary subset of unanchored rows.

For the sorted hypothesis the graph is especially simple. If i<j<k and i,k are adjacent in G_identity, every pair inside that index interval is adjacent: the two extreme cross edges and diagonal feasibility imply the intermediate cross edges. Hence the graph has a proper interval ordering. Maximum independent set is obtained by repeatedly retaining the first available vertex and removing its right neighbors. Exchange proof: if an optimum starts later, replace its first vertex by the earliest available one; the interval property guarantees that later independent vertices remain non-neighbors. Recurse. The complement of this independent set is a minimum sorted-hypothesis certificate. With monotone neighbor endpoints, a two-pointer scan of the ordered coordinates constructs it without enumerating matchings.

Now define U as the union of G_p over ALL feasible p. Predetermined identity receipts identify every assignment iff they cover U. Necessity follows from any witnessed swap; sufficiency follows by applying the preceding cycle argument to any actual p. To build U without enumerating all permutations, for every pair of rows and pair of distinct columns in their common neighborhood, remove those two rows and two columns and test whether the remaining ordered matching is feasible. If yes, both assignments of the two rows to those columns are feasible. This finite algorithm is polynomial; the minimum vertex-cover optimization on U is not assumed to admit the sorted greedy proof for arbitrary snapshots.

Counterexample: x=y=(0,1,2,3), v=2. The sorted swap graph contains all pairs except (1,4) in one-based indexing. Two receipts at ranks 2 and 3 certify the sorted hypothesis. Yet the zero-based assignments (1,0,3,2) and (2,0,3,1) both return 0 and 3 at those anchored rows. The universal graph is complete, and three receipts are necessary. An efficient certificate for a prediction is not an equally efficient universal decoder.

## Sharp worst-case receipt budgets

Suppose both snapshots have consecutive gaps at least s>0. Write a=v/s. Among feasible pairs of snapshots, let C be the maximum of the minimum number of receipts certifying the sorted hypothesis, and Umax the maximum of the minimum fixed receipts identifying every assignment. Then

    C = n - ceil(n/(floor(a)+1)),
    Umax = n - ceil(n/max(1,floor(2*a))).

These are sharp integer budgets for all n>=1 and all real a>=0, not estimates of the number of auditory syllables.

Upper bounds: a sorted swap between ranks i,j requires (j-i)s <= v by the combined-width formula. The sorted graph is contained in the floor(a)-th power of a path. Retain every floor(a)+1-th rank as unanchored. For a universal swap, both rows must reach both of two distinct final columns. Their separation plus the two columns' separation cannot exceed 2v, so (j-i+1)s <= 2v. Thus U is contained in the (floor(2a)-1)-th path power if floor(2a)>=1; otherwise it has no edges. Retain every max(1,floor(2a))-th rank. The complements yield the asserted budgets.

Attainment: rescale to s=1. For the sorted contract take x_i=y_i=i (zero-based). All and only swaps with rank distance <=k=floor(a) are feasible. For a graph with every pair at index distance less than L joined, an independent set has at most ceil(n/L) vertices and this is attained by spacing them L apart.

For the universal contract, if a<1 sorted feasibility already implies uniqueness. Otherwise write a=k+f, k>=1, 0<=f<1. Take x_i=i and y_i=i for f<1/2, or y_i=i-1/2 for f>=1/2. Permitted rank offsets are respectively [-k,k] and [-k,k+1]. Let h=0 or 1 indicate the second case. A row pair at distance d<=k can swap under the sorted assignment. For k<d<=2k+h-1, use intermediate column indices A=j-k and B=A+1. They lie inside the common reachable set of rows i and j. Start with the sorted assignment, transpose i with A and j with B (omit the latter when B=j). The two transpositions are disjoint and their displacements permitted. Rows i and j now own A and B; exchanging these two destinations is also permitted. Thus every such pair is an edge of U. The resulting graph is exactly the path power with L=2k+h=floor(2a). Both upper bounds are therefore attained. If L exceeds n, all vertices are mutually adjacent and n-1 receipts suffice and are necessary.

This proves a sampling condition: if VT<s, both contracts require zero supplementary identity receipts. Equality is unsafe: a pair can exchange. On the other hand the threshold is worst-case, not necessary for uniqueness of a specific snapshot pair.

## Faulted identity receipts and temporal debt

If a fixed receipt schedule queries source i exactly w_i times, each receipt being a complete final-rank symbol, then the minimum Hamming distance of the resulting code over distinct feasible assignments is exactly

    D = min_(i,j in U) (w_i+w_j).

If U has no edges, only one assignment exists and no receipts are necessary. Otherwise an edge witnesses a pair of assignments differing in exactly those two rows, giving the upper bound. For any two distinct assignments, remove the rows where they agree, then use the alternating-cycle argument to find a swap within the remaining rows. Their Hamming distance is at least that edge weight. Consequently t arbitrary symbol substitutions and e flagged erasures can be corrected iff every edge sum is at least 2t+e+1. The same weighted criterion with G_p is the distance from the proposed matching to its closest competitor, not a universal fault guarantee. This is a reliable-baseline, independent-symbol corruption contract; a single common source failure affecting all repeated receipts is not modeled.

Across multiple frames with known initial labels and no extra dynamical restrictions, the number of entire labelled endpoint histories is the product of the numbers of local feasible permutations. Terminal identity uncertainty is instead the set of ordered products of those permutations; it need not equal the product cardinality or the subgroup generated by their union. Example with v=1: snapshots (0,1,3), (0,1,2), (-1,1,2). Only ranks 1/2 can swap in the first interval; only ranks 2/3 in the second. There are four possible histories and four terminal permutations, not the six suggested by connectivity of the union of the swap graphs. Temporal order is substantive. No multi-frame optimal adaptive interrogation theorem is asserted.

A stronger negative example shows why the one-dimensional restriction is essential. In the plane, take an equilateral triangle of initial points on the unit circle and final points rotated by 60 degrees. Permit displacement at most 1. Each row reaches exactly its two adjacent final points (distance 1; opposite distance 2). The bipartite graph is a chordless six-cycle with two perfect matchings and no feasible two-row swap. The swap-cover criterion fails in that geometry. Additional timbre, position and velocity features cannot be silently collapsed into one coordinate.

## Executable qualification and acoustic witness

Run from this expedition directory:

    node laboratory.cjs
    python witness.py

The JavaScript census enumerates ordered point sets on the integer grid 0..6, n=2..5, v=0..4; every feasible permutation and every possible anchor subset is examined. It separately verifies the sorted greedy cover and the sharp universal path-power bound. Total: 16,660 snapshot/displacement cases, 10,596 feasible cases, 86,686 feasible assignments and 304,472 anchor-subset classification checks. In 3,302 feasible cases the minimum universal receipt budget exceeds the sorted certificate budget. The maximum gap in this bounded grid is two receipts. Sixty uniform profiles (n=2..7 and ten half-step displacement ratios) produce 1,120 exact edge tests and attain both formulas.

The native Python 3.13.5 implementation instead compares literal pairs of feasible permutations, extracts their changed rows and groups actual receipt tuples. Across 3,400 snapshot/displacement cases it performs 40,169 assertions counted as receipt classifications and weighted-distance checks. Its full receipt reproduces byte-for-byte across two executions; source and receipt Git blob hashes match the local files. These are different computational methods by the same agent, not independent scientific review. The uniform path-power proof is analytical; the finite census is a falsification attempt, not its replacement.

The Python script also generates four one-second 8 kHz PCM16 WAV files in results/. Start with two phase-continuous glides, 400→600 Hz and 600→400 Hz, with respective phase laws (cycles) 400t+100t^2 and 600t-100t^2. At t=1/2, both frequencies are 500 Hz and their phases differ by exactly 50 cycles. Swap the two suffixes at sample 4000, producing a second pair of phase-continuous sources that bounce instead of cross. Both pairs use the same common envelope. Integer samples are added without clipping. Their mono WAVs are byte-identical (SHA-256 in qualification.json); their two source-resolved stereo WAVs differ. This is a literal exact digital collision, not a model of independent room propagation or a claim about whether human listeners hear bouncing. The source rendering is deliberately phase aligned, not a claim that arbitrary source mixtures admit an exact splice. Generated binaries are not committed; the generator and hashes are.

A possible performance interface would let a composer specify labelled frequency trajectories, select crossing or bouncing continuations at eligible meeting points, and expose selected identity receipts using an independent tagged channel. The renderer and exact census are implemented; live performance controls and any perceptual trial are not.

## Sources, interpretation and limitations

- Werman, Peleg, Melter and Kong, *Bipartite graph matching for points on a line or a circle*, Journal of Algorithms 7(2), 277–284 (1986), DOI https://doi.org/10.1016/0196-6774(86)90009-X . Read institutional metadata and abstract at https://cris.huji.ac.il/en/publications/bipartite-graph-matching-for-points-on-a-line-or-a-circle/ ; full article not inspected. Established matching-on-a-line context, not authority for the local minimax receipt proof.
- McPherson, Ciocca and Bregman, *Organization in audition by similarity in rate of change: Evidence from tracking individual frequency glides in mixtures*, Perception & Psychophysics 55(3), 269–278 (1994), DOI https://doi.org/10.3758/BF03207598 . Publisher PDF consulted at https://link.springer.com/content/pdf/10.3758/BF03207598.pdf ; read abstract/introduction, General Method, Experiment 3 and 4 discussion, General Discussion (printed pp. 269–271, 275–278); original page images 269, 277, 278 inspected. Authors report that different glide rates can facilitate tracking through a crossing, with frequency proximity competing. They explicitly consider symmetry as a rival explanation on p. 278. This is evidence about their stimuli and task, not validation of the proposed mathematical receiver.
- Kuroda, Nakajima and Eguchi, *Illusory continuity without sufficient sound energy to fill a temporal gap: Examples of crossing glide tones*, JEP: Human Perception and Performance 38(5), 1254–1267 (2012), DOI https://doi.org/10.1037/a0026629 . Institutional abstract and metadata read at https://kyushu-u.elsevierpure.com/en/publications/illusory-continuity-without-sufficient-sound-energy-to-fill-a-tem/ ; full text not inspected. Reported gap-transfer perception depends on relative levels. This is a contrary constraint on treating perceptual continuity as direct proof of the underlying source's persistence.
- Internal ancestry: #514 issue, comments and report, and #523 PR/report inspected. Their static anonymous field binding differs from this temporal matching contract. Markov/lumpability direction was abandoned after finding #240. Searches for trajectory matching, crossing identity, tracking and permutation did not reveal a directly equivalent active expedition; bounded overlap search, not a literature novelty guarantee.

Interpretation: continuous-looking sound is not necessarily continuous identity. A receiver can report a pitch trajectory conditional on its order-preservation hypothesis without possessing evidence that the hypothesis is true. The design implication for MHAC is to distinguish observed value, inferred track, authenticated source and stale/ambiguous association. An anchor is new evidence, not a more confident rendering of the same mono signal. An experimental hypothesis is that explicitly tagged identity receipts near ambiguous transitions would reduce attribution errors compared with untagged continuity; compare against timbre, spatial and trajectory-rate cues and match exposure/attention costs. No human, clinical, device-control or Brier-specific validation follows.

Reconciliation: base main 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity and validation; 325 branch entries, 100 recent open issues, 100 open PR snapshots, targeted duplicate searches, #530 body and empty comments. #523 exact-head workflow 45579823069 completed successfully. Native checkout attempted and failed DNS resolution. Only new issue-scoped files; no other branches or canonical records changed. Same ChatGPT agent performed source inspection, proof, implementation and checks on 2026-11-25. Independent critique and exact-head full repository validation are not claimed; draft and Refs-only until those acceptance conditions are met.

Fictional afterword: Two machines approached one note. On the far side, the clerk continued to write their names in ascending order. The technician asked which machine had changed its mind. The clerk had recorded every pitch correctly, but no name had crossed the meeting.
