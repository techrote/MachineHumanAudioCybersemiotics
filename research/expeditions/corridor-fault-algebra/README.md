# The Corridor That Cannot Name Its Break

Expedition #584 — 25 November 2026. Original mathematical derivations, synthetic enumeration and symbolic receipt sonification. Not canonical Track E/G evidence, a claim of scientific priority, or a human experiment.

## 1. The question

Consider a finite tree of signal conduits. Every leaf is an accessible terminal; every internal vertex has degree at least three. A fault is a unit change on an edge, with at most one change per edge. Assume stable faults during measurement, known baseline, known tree unless explicitly relaxed, exact terminal-to-terminal receipts, and no alternative propagation route.

The same physical fault configuration is observed by three distinct abstract instruments:

- **Additive:** report the number of affected edges along the path.
- **Boolean outage:** report whether at least one affected edge occurs.
- **Parity:** report whether the count is odd.

The three are models, not interchangeable descriptions of a microphone. Additive excess delay, saturating loss indication, and ideal binary phase inversion are possible analogies with different physical assumptions.

At a three-arm junction, order the terminal pairs AB, AC, BC. Faults on arms A and B give additive (2,1,1), outage (1,1,1), parity (0,1,1). Faults on arms A and C give (1,2,1), (1,1,1), (1,0,1). Faults on all three arms give zero parity everywhere, exactly as no fault at all.

The anomaly is not measurement noise. The algebra of the receipt has removed a distinction.

## 2. Exact full-boundary identification frontiers

Let L be the number of leaves, I the number of internal vertices, m=L+I-1 the number of edges, and delta the minimum internal degree. Assume L>=3. Let k be the maximum permitted number of faults, and include the healthy state.

**Theorem A (additive).** All real edge changes, including signed values, are uniquely determined by all leaf-pair path sums.

Proof. For a pendant edge ending at leaf a, choose b,c in two other branches of its internal endpoint. Its value is (d(a,b)+d(a,c)-d(b,c))/2. For an internal edge uv, choose a,b in two distinct branches at u away from v, and c,d in two distinct branches at v away from u. Its value is (d(a,c)+d(b,d)-d(a,b)-d(c,d))/2. Each expression cancels all other edges. This is the usual additive-tree limb/quartet algebra; positivity is not needed when topology is given. In particular all binary fault sets are distinct. At least m scalar linear receipts are necessary for universal real-valued recovery, and m independent rows exist because the full matrix has rank m. The result does not claim identification of arbitrary unknown topology with zero or signed lengths.

**Theorem B (parity).** There are exactly 2^(L-1) possible complete records, each with exactly 2^I distinct binary fault sets. The sharp universal sparsity bound is k <= floor((delta-1)/2).

Proof. Over GF(2), assign a potential at a chosen root, then propagate across edges by XOR with the edge fault bit. A path's parity is the XOR of its endpoint potentials. Every leaf potential vector is attainable, and simultaneous complement has no effect. The kernel consists of edge boundaries of internal-vertex subsets: normalize the common leaf potential to zero and choose the internal potentials freely. This proves the fibre count. For a nonempty set S of internal vertices, its boundary size equals the sum of degrees in S minus twice the number of induced edges. The induced subgraph is a forest, hence the boundary size is at least (delta-2)|S|+2, and therefore at least delta. A singleton of minimum degree attains delta. Thus the kernel's minimum nonzero weight is exactly delta. Two fault sets of size at most k have symmetric difference of size at most 2k; they cannot collide if 2k<delta. Conversely partition the delta edges incident to a minimum-degree internal vertex into two groups as equally as possible. Their symmetric difference is a kernel vector; both groups have size at most ceil(delta/2). This attains the obstruction.

**Theorem C (Boolean outage).** The sharp universal sparsity bound is k <= delta-2.

Proof. The zero receipts describe exactly the partition of leaves into connected components of the forest after faulty edges are removed. If at most delta-2 edges are removed, every internal vertex still has residual degree at least two. Each resulting tree component is consequently the minimal subtree spanning its original leaves (including singleton leaf components). Indeed all degree-one endpoints of a nonsingleton component must be original leaves; each edge lies on a path between two of these endpoints. There cannot be a singleton internal component. The observed leaf partition uniquely specifies those minimal subtrees and hence the removed edges. At delta-1 faults, choose an internal vertex of degree delta, cut all but one incident edge, and vary the one retained edge. In each case the leaf partition consists of the same delta groups originally incident to the vertex. The assignment of the vertex to one group has disappeared. This gives delta different fault sets with identical observations.

Comparison:

| Minimum internal degree | Max guaranteed parity faults | Max guaranteed Boolean faults | Additive |
|---:|---:|---:|---|
| 3 | 1 | 1 | all |
| 4 | 1 | 2 | all |
| 5 | 2 | 3 | all |
| 6 | 2 | 4 | all |
| 9 | 4 | 7 | all |

Important negative result: two binary instruments are not equally informative. Parity is a linear observation but can be worse for sparse identification than a nonlinear Boolean observation. Neither globally dominates the other: the three-arm example above distinguishes two faults by parity but not outage; healthy versus three faults is distinguishable by outage but not parity.

## 3. Unknown topology: the graph of questions

For one fault, all three instruments reduce to the same binary leaf split (or the all-zero healthy state). Relax known topology: permit every reduced tree on the same labelled leaves. Every nontrivial split is realizable as a single edge of some such tree: a singleton is a pendant split, and a nonsingleton split can be realized by two junctions joined by an edge.

A fixed collection of leaf-pair probes defines a graph G on the terminal labels, counting repeats as parallel edges. For a split encoded by binary leaf labels x modulo global complement, the receipt on uv is x_u XOR x_v.

**Theorem D.** For c connected components of G, every attainable receipt has exactly 2^(c-1) compatible split classes, including the healthy class when applicable. The minimum Hamming distance between all split-class records is the minimum edge-cut size lambda(G), taking zero for disconnected graphs.

Proof. Each component permits one independent complement. Two vectors produce different receipts exactly on edges crossing their symmetric difference, and every nontrivial cut occurs as such a difference. The result is the binary cut code of G, the same mathematical structure as the pairwise binding receipts of [#514](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/514), applied here to a topology-unknown path instrument. This is an explicit reuse of established mathematics, not a new coding theorem.

Therefore n-1 probes are necessary and sufficient without faults, even adaptively: there are 2^(n-1) possible answers and each probe returns one bit. For q=2t+e+1, the exact robustness requirement is lambda(G)>=q. For simple probe graphs and 2<=q<=n-1, the sharp budget is ceil(nq/2). Degree counting gives the lower bound, and the classical q-connected Harary graph attains it because edge connectivity is at least vertex connectivity. For q=1 use any spanning tree. Repeated receipt faults, not physical conduit faults, are counted in t,e. No formula for q>=n is asserted here.

Unknown topology does not mean physical identification: the decoded split is a boundary partition, not the location of the actual edge, its length, or its realization. Degree-two segments cannot be distinguished by leaf paths even if their topology is supplied.

**Known-star contrast.** With n leaves, a fixed single-fault dictionary needs exactly ceil(2n/3) probes for n>=3. Its probe graph cannot have an isolated vertex (uncovered arm) or a component of size two (identical endpoint signatures). All components of size at least three suffice. Forest components of sizes 3, 4, or 5 give the sharp construction. This is a star special case of separating-covering path systems; the lower bound follows from at most floor(n/3) components. For unknown topology the same disconnected dictionary conceals a split. Example: probes AB, BC, DE, EF distinguish every arm on a six-leaf star but completely miss an internal edge separating ABC from DEF.

For a known star, adaptive probing requires exactly floor(n/2)+1 in the worst case for n>=3. Query disjoint leaf pairs until a positive result, then test one of those endpoints against a guaranteed healthy outside leaf. If n is odd, the leftover singleton can be tested against a previously certified healthy endpoint. Lower bound: the all-zero transcript must cover every leaf, so at least ceil(n/2) probes. For even n, achieving n/2 on that transcript requires disjoint pairs; a positive on the final pair leaves its two endpoints indistinguishable without one more query. This proof includes the no-fault state and assumes a single fault at most.

## 4. A second anomaly: the same probe graph can be perfect for one algebra and singular for another

Return to the known star, now permitting arbitrary real additive arm changes. Probe uv reports x_u+x_v. The homogeneous equations say x_u=-x_v on every probe edge. On each connected bipartite component they permit exactly one free alternating amplitude; an odd cycle forces that amplitude to zero. This includes an isolated vertex as a bipartite component with one empty colour class.

**Theorem E.** Full real-valued reconstruction is possible exactly when every probe component is nonbipartite; nullity equals the number of bipartite components. In particular a connected spanning tree, optimal for topology-unknown single-fault split identification, is singular for unrestricted additive arm recovery. A triangle plus one attachment per remaining leaf uses n probes and attains the minimum n for real recovery.

For binary additive arm faults there is a sharper partial-observation result. In a connected bipartite component with colour classes A and B, the only possible nonzero difference between two binary states alternates +1/-1, forcing one state to have exactly A faulty and the other exactly B faulty within that component. For a nonbipartite component the difference must vanish. It follows that the exact first ambiguous sparsity cap is the minimum of max(|A|,|B|) over bipartite components; if none exist, no ambiguity occurs. To attain it, leave all other components healthy and choose the two colour classes. To prove the lower bound, any distinct colliding states differ on at least one whole bipartite component.

A connected six-terminal path has colour classes of sizes three and three. It identifies all binary additive states of at most two faults, but confuses the alternating triples. A six-terminal star-shaped probe graph has colour classes of sizes one and five; it identifies up to four faults, even though both dictionaries contain five probes and both are singular over the reals. The difference is not a matter of number of probes alone.

## 5. Computational witnesses and interpretation

Run the two standalone JavaScript files with Node:

    node laboratory.cjs
    node star-laboratory.cjs

The first enumerates all labelled reduced trees on 4–6 vertices using Prüfer sequences, plus four larger stars. Literal unique paths are traversed, then all binary edge-fault states are evaluated for the three receipt algebras. It additionally enumerates every simple probe graph on 3–5 terminals and compares every pair of literal split receipts. The executed counts are in [execution.json](execution.json): 109 trees, 4,144 fault sets, 1,096 probe graphs and 124,720 split-pair comparisons. All assertions passed. The second examines the same 1,096 probe graphs and 33,856 binary star states, checks the colour-class threshold, and finds 553 graphs with no bipartite component, 543 with at least one, and 217 connected bipartite graphs with exactly one nonsingleton fibre. All assertions passed.

A separate native Python implementation (delivered alongside this expedition in the conversation) reproduced the first census twice with byte-identical receipts, including the exact same tree and split counts. It also generated six original 0.75-second, 8 kHz mono PCM16 symbolic sonifications, with each 0/1/2 represented by a common tapered 250/500/750 Hz pulse. The three-arm A+B and A+C faults produce byte-identical outage WAVs, but different additive and parity WAVs. The renderer is not a wave-propagation model. No perceptual discrimination, device performance, or human evidence is established. All tests and proofs are same-agent work, not independent peer review.

Practical hypothesis: an auditory diagnostic interface should label its observable, not just its conclusion. A count, a saturating alert and a phase sign encode distinct fault algebras even when each sounds like a reliable report. A test could compare them under matched duration, energy, timing, topology uncertainty, and task cost, including explicit abstention for non-identifiable cases. The arithmetic itself already explains the anomaly; a cybersemiotic interpretation would need to add testable value beyond that model.

Negative sediment: degree-two vertices are permanently aliased under leaf-only paths; unknown or varying topology changes the estimand; simultaneous physical wave propagation, phase coherence, attenuation, time-varying faults, alternative routes, and common-mode receipt corruption are outside the model. Binary parity and OR are not mutually reconstructible in general. Exact identification with unrestricted real changes says nothing about ill-conditioned partial measurement or analog noise. No canonical manifests or experiment approvals are changed.

## Source and reconciliation ledger

- Arrepol, Asenjo, Astete, Cartes, Gajardo, Henríquez, Opazo, Sanhueza-Matamala and Thraves Caro, [Separating path systems in trees](https://arxiv.org/abs/2306.00843), arXiv v1, 1 June 2023. Read introduction and relevant theorem/construction passages, visually inspected printed pp. 4–5 (PDF indices 3–4): Theorem 3.3, Definition 4.1, Lemma 4.3, Definition 4.4. Established path-separation ancestry, not a priority claim. The paper allows general path endpoints; the present leaf-only restriction is explicit.
- Harary, [The Maximum Connectivity of a Graph](https://doi.org/10.1073/pnas.48.7.1142), PNAS 48 (1962), 1142–1146. Bibliographic record verified via PubMed; original proof not read. The construction/existence statement was checked against [NetworkX documentation](https://networkx.org/documentation/networkx-3.4.1/reference/generated/networkx.generators.harary_graph.hkn_harary_graph.html) and the [MathWorld Harary graph entry](https://mathworld.wolfram.com/HararyGraph.html). This is a clearly attributed classical dependency, not an independently derived graph-connectivity theorem.
- [Phylogenetics beyond biology](https://link.springer.com/article/10.1007/s12064-018-0264-7), distance-based phylogenetics passage: leaf path sums and four-point condition. Passage-level discovery only; PMC retrieval returned a challenge. The additive reconstruction formulas above are proved directly, not claimed as novel.
- Repository: inspected AGENTS, RAG, programme, runbook, integrity and validation; 352 branch entries, 100 recent open issue results, 100 open PR results and targeted searches for tree metrics, network tomography, phylogenetics and related notions. Checked excerpts of #514 and #538, and created new isolated issue #584. Base main SHA 495a98ca12bae467a507031f04931aa4254b1866. Issue read back with no comments at creation. The previous centroid/parity title search did not identify a publication; no recovery claim is made. No shared files modified.
- Verification agent: ChatGPT, GPT-6.2, 2026-11-25; source reading, derivations, executable checks and self-review. Full repository qualification and independent critique are outstanding at authoring. Not a scientific priority assertion, human gate or external endorsement.

Fictional coda: A clerk sounds a note through each corridor. The bell says that every route is broken. The apprentice replaces the bell with a clock and the clock counts two breaks on one route. The building had not changed; the question had.
