# The Receipt That Cannot Share a Drawer
## Action-bundle obstruction hypergraphs, arbitrary compatibility depth, and selective historical recovery

**Refs #346 · 24 November 2026 · original finite mathematical/synthetic expedition. AI-authored and self-reviewed by ChatGPT GPT-6.2.** Not Track E/G evidence, an auditory experiment, a production undo mechanism, or a priority claim. No independent human review.

## Contents

1. Excavation — reconcile a neglected quantifier in the previous receipt report.
2. Representation theorem — turn arbitrary higher-order action obstructions into matching interventions.
3. Sharp costs — show unbounded preview requirements despite fixed origin-graph complexity.
4. Selective recovery — distinguish random admission, refusal, and reconstruction error.
5. Exaptation and refusals — propose a bounded audit, not a new ontology or production mandate.
6. Laboratory and provenance — give exact finite checks and reading limits.

## 1. Excavation

The main [X004 quotient guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md) says that a representation may collapse distinctions whenever the declared downstream decision is constant on its fibres. This is a useful antidote to MHAC's tendency to accumulate distinctions. [#209/#210 The Alphabet of Tomorrow](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/38ec85c218a43474164530c4efa9227ab276872b/research/expeditions/alphabet-of-tomorrow/README.md) adds state-side set-valued admissibility: a code class requires one action acceptable to all compatible origins. [#195/#196 The Choir That Cannot Meet](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/e53a2a4d397d225e49c0c7e265b582390798fdb9/research/expeditions/choir-that-cannot-meet/README.md) provides a different obstruction, nonidentifiability of a common witness from proper marginals.

The recent [#338/#339 The Undo That Needs a Forecast](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64/research/expeditions/undo-needs-forecast/README.md) has a surprisingly fertile orphan: its 30-state, five-action counterexample disproves the product law for bundled actions. But it leaves unclear how complicated the obstruction can become. Does knowing the origin collision graph, maximum fibre size, and all pairwise action-compatibility results give any bound on required preview? Can checking triples, or arbitrarily many actions at a time, repair the problem? This expedition answers no, and identifies the exact combinatorial object that is missing.

These are not the same hypergraphs as in #210: there the vertices are original states and hyperedges constrain the choice of a decoder output. Here the vertices are interventions and hyperedges constrain sharing a single *receipt function* before the intervention. All decoder targets here are singleton exact origins. The new obstruction therefore exists without ambiguity of acceptable remedies. The report does not repeat #195's marginal-count theorem or #339's pair-collapse proof.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866 checked twice; AGENTS, RAG, programme, runbook, integrity, validation and opening protocol scope read. Inspected 100 returned open issue titles (search limit; not a complete census), 96 returned open PR titles, searched branches for "bundle" (none returned) and issues for hypergraph overlap. Read #338 issue and empty comments, #339 exact report and lab; #339 exact-head integrity run 45404877221 succeeded. Read #195 body/comments and linked report; #209 body and #210 report through the higher-order section. New #346 issue and empty comments checked before creating fresh branch. The canonical programme is not complete; this is an isolated parallel exploratory lane. No changes to other workers, shared records or frozen methods.

## 2. Representation theorem (mathematics)

Let A be a finite nonempty set of interventions, X finite original states, f_a:X→X each intervention. The writer knows x and a deterministic preview class h(a) in {1,...,k}, but not necessarily a. The decoder sees a, the exact result f_a(x), and a binary historical tag e_h(x). Every origin/action combination is permitted; receipt and final observation are exact, and the scheduler knows the action before writing the receipt. No physical restoration is asserted.

For each a let its collision graph have an edge between distinct originals with equal f_a values. Restrict to actions whose nontrivial fibres all have size two, so each collision graph is a matching. A set S of actions is *compatible* if a single binary receipt works for every action in S. As in #339, this is equivalent to bipartiteness of the union of their collision graphs: assign opposite tags to every collided pair; conversely a valid tag assignment is a two-colouring. An empty class is allowed.

Define H as the hypergraph with vertices A and edges the inclusion-minimal incompatible action sets. Then compatible sets are exactly those containing no hyperedge. A weak hypergraph colouring means no hyperedge is monochromatic. The minimum preview alphabet is exactly the weak chromatic number of H: partition A into compatible classes, equivalently assign a colour to every action without making any hyperedge monochromatic. This is a partition of whole actions, not of individual state collision edges.

**Theorem 1 (representation).** For matching interventions, every minimal incompatible action set has size at least three. Conversely every finite hypergraph with edges of size at least three can be represented by such interventions, with compatible sets exactly its independent sets. If at least one hyperedge exists, the union origin graph has chromatic number exactly three. In particular, if the given hypergraph is an antichain of subsets, it is precisely the hypergraph of minimal incompatible action sets.

Proof of necessity: a single matching is bipartite. The union of two matchings is also bipartite: shared edges form isolated edge components, and every nontrivial cycle among distinct edges alternates action colours, hence has even length. Therefore no singleton or pair can be a minimal incompatible set.

Constructive converse: for every hyperedge T of cardinality s, create its own disjoint simple cycle of odd length l=s if s is odd, l=s+1 if s is even. List each of the s actions on consecutive cycle edges once. If s is even (thus at least four), append a repeat of the second action as the last edge. The repeat is not adjacent to its original occurrence, including across the cyclic boundary. Every action's assigned edges form a matching in this block. For an action a and its edges (u,v), define f_a(v)=u and f_a(u)=u, leaving all unassigned vertices fixed. Blocks are disjoint, so this is an actual map with fibres of size at most two, even when a appears in many blocks.

All cycle edges survive in the union for S iff T⊆S. A proper subset of the edges of a simple cycle is a forest and hence bipartite; the complete odd cycle is not. Across disjoint blocks the union is bipartite iff no T is contained in S. This proves the representation and the correspondence of safe sets. Each odd cycle is three-colourable (alternate two colours on all but the final vertex, give that vertex the third), and any complete odd cycle needs at least three. If there are no hyperedges, take one identity state; one receipt symbol suffices.

This realizes the entire arbitrary higher-order obstruction, not just a family of isolated triangle counterexamples. It is an elementary constructive reduction to established weak hypergraph colouring, not a new definition of colouring or a literature-wide originality claim. The laboratory additionally constructs actual maps and derives their fibres rather than testing only the intended cycle adjacency.

## 3. Sharp preview cost and compatibility depth (mathematics)

For n≥t+1, t≥2, choose all (t+1)-subsets of n actions as hyperedges. Use one disjoint odd cycle per such subset, as above. Then every collection of at most t actions shares a binary receipt; **every** collection of t+1 or more fails. Thus the exact preview alphabet is

    k_min = ceil(n/t).

Lower bound: each of k classes covers at most t actions. Upper bound: arbitrarily partition the n actions into groups of at most t. The associated binary receipt exists for each group. The number of origin states in this explicit construction is l * binomial(n,t+1), where l is the least odd integer ≥t+1. This can be large; no claim of state-minimality is made.

| Actions n | Compatibility checked through t | Origin states in construction | Minimum hints | Fixed preview bits |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 2 | 30 | 3 | 2 |
| 8 | 2 | 168 | 4 | 2 |
| 8 | 3 | 350 | 3 | 2 |
| 10 | 4 | 1260 | 3 | 2 |
| 100 | 2 | 485100 | 50 | 6 |

The first row recovers the #339 example. Fix t=2 and increase n: the maximum action fibre remains two and the union origin chromatic number remains three, yet k_min grows without bound. For any fixed audit depth t, one can pass all tests at or below that depth and still require arbitrarily many preview classes. This is not a hidden contradiction in an individual action; it is a failure of reusing a *single* tag function across too many whole actions. A complete audit can use the odd cycle's set of action labels as a checkable incompatibility witness.

The separation makes a practical trade-off visible. With a binary tag, the preview channel needs ceil(log2 ceil(n/t)) fixed bits in these families. With three tag symbols (two bits in fixed binary storage), a single receipt function works for *all* actions and needs no preview. An extra stored bit removes the entire growing preview burden. In this constructed family, retaining a third distinction can be more economical than designing an increasingly complicated context-selection protocol. This is an argument against universal maximal compression, not for universal larger logging.

Different hypergraphs with identical origin-graph chromatic numbers and the same pairwise results can have different global costs. The seven lines of the Fano plane, encoded as seven disjoint triangles (21 origins), require three preview classes; deleting any one action makes two classes sufficient (exact finite oracle below). The complete triple family on seven actions (105 origins) needs four classes. Both have origin chromatic number three and all pairs compatible. The two models need not have the same origin graph or state count; the claim concerns the coarse summary, not indistinguishability of their complete graphs.

If a worker is allowed to route *each collision edge* separately, a three-colouring of origins gives two binary digit functions, and each edge can use one separating digit. This does not solve the problem when one hint must serve the whole action, nor does it authorize splitting an actual atomic operation. The guarantee changes when the granularity of authorization changes.

## 4. Selective admission rather than approximate reconstruction (mathematics)

Permit a scheduler to decline an entire action before committing a receipt. On admission, recovery must be exact for every original; refusal is explicit and does not count as successful recovery. A refusal flag is a separate resource and is not silently encoded as one of the k successful hints. No claims about action-specific conditional errors are made.

For a given schedule seed, the admitted set must be k-colourable in H. Define F_k to be the family of such subsets. Any probability distribution pi over F_k, drawn independently of the actual action, can be used: announce refusal if the action is not in the sampled subset; otherwise use a fixed compatible partition of that subset. The scheduler knows the seed and actual action. Since the writer/decoder can share the seed or a trusted equivalent schedule identifier, both know the selected tag scheme. The seed/storage/channel cost is excluded from the specified hint budget and must be accounted for in any application. For a fixed action selected before the seed, its success probability is sum of pi(S) over S containing the action.

The exact minimax success is

    V_k = max_pi min_a sum_{S∈F_k:a∈S} pi(S).

Equivalently V_k=1/tau_k, where tau_k is the minimum total nonnegative weight on F_k with covering weight at least one at each action. Proof: any distribution of worst coverage v>0 scales by 1/v to give a fractional cover, so v≤1/tau_k. Normalize any minimum fractional cover to a distribution to attain 1/tau_k. Since singletons are compatible, a cover exists for k≥1. For k=1 this is precisely the usual fractional weak hypergraph colouring formulation; for k>1 it is a fractional covering by k-colourable sets, not an assertion that multiplying the single-colour optimum is always tight.

For the complete uniform family of Section 3, each admitted set contains at most min(n,kt) actions, so the average success over uniformly chosen actions cannot exceed min(1,kt/n), and worst success is no higher than the average. Draw a uniformly random subset of exactly min(n,kt) actions, partition into groups of size ≤t, and use its exact tag functions. Every fixed action is included with probability min(1,kt/n), attaining the bound:

    V_k = min(1, kt/n).

For the Fano example with two hints, every six-action deletion subset is compatible with two classes and the full set is not. Uniform deletion attains 6/7 and the same cardinality argument proves optimality. These are exact admission probabilities, not expected decoder error or coverage of human recipients.

Adversarial timing changes this result. If the action is selected after seeing the realized admission set, every seed with an omitted action permits forced refusal. Unless full admission is possible, the worst adaptive admission probability is zero. This extends the timing distinction from #339 without conflating refusal with a guessed reconstruction. Private random tie-breaking does not fix an admitted action whose tag function is not valid; a policy permitting errors for some origins is a different optimization problem.

## 5. Exaptation, limits, and an artistic witness

**Interpretive proposal, not a deployed contract:** supplement the X004 quotient guard with an action-family audit when a history tag must be committed prospectively. Retain the actual action IDs and their collision fibres, a declared target (origin vs acceptable remedy), the admissible scheduling granularity, tag alphabet, hint arrival, and a safe partition or an odd-cycle certificate labeled by whole actions. Validate each proposed class by constructing its *union* graph and attempting a common receipt. Pairwise green checks alone cannot qualify the partition. On general matching actions, every minimal incompatible set corresponds to the label set of some odd cycle, minimal under inclusion among all such label sets: an incompatible union contains an odd cycle, and if the labels used were a proper subset of the minimal set, that subset would already fail. A discovered cycle therefore gives a witness; its label set need not be minimal unless minimized. Removing one action's labels from that witness may not repair the entire graph, because another cycle can survive.

Counterargument: a complete origin-recovery audit may be unnecessary if all colliding origins permit a common remedy, as #210 emphasizes. Even in the uniform hard family, three symbols can remove the preview problem. If the action is known before writing the receipt, two symbols suffice. If the action itself is unknown even to the decoder, cross-action ambiguities change the graph. If the actual permitted origin/action support is restricted, derive collision edges from that support instead. If a retained snapshot already provides the needed distinctions, new receipt fields are redundant. No argument here establishes an operational restoration path, replay safety, human interpretability, or a universal policy for logging.

**Concrete falsification fixture:** let each action operate on several disjoint state pairs at once. Supply a purported one-bit recovery tag and one preview class for three mutually pairwise-compatible actions. Produce their labelled odd cycle and two actual origins with identical decoder input for at least one action. Do not accept “each action has a valid tag” as evidence that the *same* tag works for the whole class. Separately qualify that the actual authorized actuator can restore a valid target. No automatic mutation of canonical schemas is proposed.

**Artistic, unrendered original score:** Seven percussionists each carry a reversible-looking two-tone marking instruction. Each line of the Fano plane is a separate three-note loop; the three percussionists named by that line each merge one adjacent pair of notes. Each performer can mark their own merged pair with alternating light/dark timbre. Any two can agree on a common alternation across all loops. But a globally shared two-colour timbre pattern would have to alternate around a complete triangle. Use three cue classes, or introduce a third timbre. This is a symbolic score; no listening trial or acoustic reconstruction is claimed.

**Fiction:** The archive purchases one binary drawer for every pair of incompatible memories. Each pair passes its inspection. A conservator asks where the instructions for changing five memories together should go. The librarian splits the instruction into pieces and distributes them among drawers. The conservator refuses: the instruction is a single operation. The librarian offers a larger drawer. Both are correct about a different budget.

## 6. Laboratory and provenance

Run `node lab.js` in this directory. The dependency-free JavaScript lab validates inputs, constructs intervention maps, reconstructs collision edges from their actual fibres, checks a three-colour witness, uses a BFS binary-tag oracle on each action subset, and verifies direct (post-action state, tag) injectivity. On failures it confirms a complete odd cycle of actual collision pairs. Exact subset partition dynamic programming is cross-checked by enumerating colour assignments. The uniform families include odd and even hyperedge cardinalities, the latter requiring a repeated action label on a nonadjacent edge. Five malformed-input controls refuse. The lab deliberately caps action count at eight; the proof, not the census, handles arbitrary finite n.

First execution and replay of fetched committed lab at 407c275bd86e461114ba387904506f31702e7a5b (same AI author, JavaScript runtime, not independent review):

| Activity | Count |
| --- | ---: |
| Constructed hypergraph families | 1128 |
| Actual matching interventions | 5650 |
| Action subset feasibility checks | 37784 |
| Direct decoder-input checks | 1226512 |
| Odd-cycle collision certificates | 12103 |
| Explicit colour assignments | 304244 |
| Uniform selective-admission budgets | 133 |
| Exact seeded action coverage checks | 889 |
| Malformed-input refusals | 5 |

All assertions passed in both executions. Counts overlap; no empirical data or independent experiments. Native Node execution and complete checkout validation not performed here. Full exact-final-head repository CI and substantive review remain pending at report creation. The Fano-plane result is confirmed by the direct finite census, not inferred from a picture. The proof is independently readable but not independently reviewed.

Source comparison, access 2026-11-24: H. S. Witsenhausen, *The zero-error side information problem and chromatic numbers*, IEEE TIT 22(5), 592–593 (1976), DOI 10.1109/TIT.1976.1055607. Metadata inspected at https://cir.nii.ac.jp/crid/1360011145655997184 and the abstract as reproduced at https://scispace.com/papers/the-zero-error-side-information-problem-and-chromatic-1h6d5rr1n2 ; original full text not read. This confirms the established fixed-symbol graph-colouring antecedent, not the action-side reduction. Danila D. Cherkashin, *About maximal number of edges in hypergraph-clique with chromatic number 3*, arXiv:1107.1869 (2011), https://arxiv.org/abs/1107.1869 ; inspected the author abstract's opening definition of weak chromatic number only. This is a terminological comparator, not evidence of priority for our construction. Schaefer 1978 publisher abstract was also inspected at https://doi.org/10.1145/800133.804350 but does not expose the relevant hardness proof; no standalone complexity theorem is claimed here. No full-text novelty audit performed.

Disposition: preserve this as a mathematical obstruction and testable exaptation in a fresh issue branch, Refs #346 only. No canonical status changes, no protocols amended, no shared manifest updates, no production mechanism, no human recruitment. Exact-head checks and review required before integration.
