# The Alphabet of Tomorrow
## The irreversibility of a perfectly adequate summary

**Refs #209 · 23 November 2026 · finite mathematical model and critical synthesis.** Not a Track E/G result, human listening study, production requirement or priority claim.

## Contents

1. Archaeology — preserve the disagreement over compression scope.
2. Exact model — encoder, decoder and feasibility conditions.
3. Two-tone vocabulary — graph coloring and unbounded alphabet growth.
4. Higher-order obstruction — when pairwise compatibility fails.
5. Exaptation — future questions and archival limits.
6. Laboratory — methods, controls and execution evidence.
7. Afterword — original fictional reflection.
8. Disposition — falsifiers and claim boundaries.

### 1. Archaeology: the disagreement worth keeping

At main 495a98ca12bae467a507031f04931aa4254b1866, X004's QUOTIENT-GUARD.md gives a precise criterion for a fixed decision vector: the outcome must be constant on each representation fibre. Its conclusion is not to preserve every distinction, but to retain distinctions that earn their cost. The open #201 goes further: with a set of acceptable actions, a common action may eliminate the need for clarification. These are constructive challenges to the repository's anti-collapse rhetoric. Yet both are conditioned on a declared decision problem. A summary may be sufficient on Tuesday and irreversibly inadequate on Wednesday.

The neglected issue is **when the use of a sign is determined**. In a future-dependent archive, a distinction may have no present decision value yet be indispensable to a future reader. This is not a reason to retain everything everywhere; it is a reason to make the scope of compression explicit.

Read against main's X006 (surface return need not restore state) and X005 (absence is not a determinate observation), the archive creates another kind of asymmetry: the encoder must commit before the decoder's question is available. #203 changes the state through observation; we instead stipulate immutable states and a non-interactive code. #205 concerns trace-equivalent choice menus, not static side-information encoding. #195 exposes joint-witness failure; its related logical lesson reappears here as a higher-order obstruction, not a new marginal-bound theorem. #207 studies actual transformation order; there are no transitions here.

The live issue and PR lists were inspected before carving this separate scope; the named open expeditions remain unmodified. R001–R020, the frozen protocol, selected evidence, and the human gates remain untouched.

### 2. Exact model: three different obligations

Let X be a nonempty finite state set, C a finite set of possible decision contexts, and S(c) a subset of X describing which states can occur with context c. In each feasible pair (x,c), declare a nonempty finite action set A(x,c). For a pair outside the support there is no constraint. An empty action set at a feasible pair is an infeasible specification, not a harmless missing value. In the laboratory null means outside support; empty arrays are rejected.

A deterministic encoder q:X→{1,...,k} sees x but not c. A decoder d(q(x),c) sees the code symbol and c, not x. The obligation is d(q(x),c) ∈ A(x,c) for every feasible pair. The encoder knows the entire stipulated family C and its support beforehand, not which context is actually selected. There are no probabilities, sequence codes, interaction, side channels, erasure recovery, or human perception assumptions.

**Proposition.** A code is valid iff for every code fibre B and every context c with B ∩ S(c) nonempty, the intersection of A(x,c) over x in B ∩ S(c) is nonempty.

Necessity: the decoder has one answer for the same symbol and context and that answer must belong to each allowed set. Sufficiency: choose one element of every nonempty intersection and tabulate it. Empty support cells need no answer. The finite model is closed; an unstipulated world or later context is not covered.

The proposition yields three useful distinctions:

- Context-known encoding: the encoder can choose a different mapping for each c. Its alphabet can be reused.
- Context-late encoding: one fixed mapping must serve all c. Different decoders are allowed.
- Unknown-family encoding: the code must work for decision contexts not yet specified. This is a stronger obligation, not supplied by either previous result.

For singleton action sets and full support in every context, this reduces to grouping states with identical decision vectors (X004). With restricted support, pairs can be grouped even when their answers would differ in a context that cannot jointly occur. This distinction is essential: unavailable contexts are not fabricated negative observations.

### 3. The two-tone vocabulary that needs eight tones

For singleton outputs define an undirected graph G on X. Join u and v iff a feasible context admits both and requires different answers for them. By the proposition a valid code fibre is an independent set; the minimum alphabet is the chromatic number χ(G). The full proof is elementary: an edge prohibits a common symbol, and any proper coloring guarantees that jointly feasible states of the same color cannot disagree in a context.

Construct a family from any finite simple graph: for each edge {u,v}, create a context in which precisely u,v are feasible, requiring different singleton answers low/high. Every nonempty context requires just two symbols if known to the encoder. Yet the minimum fixed code is χ(G), not two in general. For the complete graph on n vertices, every pair has its own distinguishing context, so no two states can share a symbol and exactly n are necessary. This establishes an unbounded alphabet ratio n/2 for n≥2, with the cost of a growing family of n(n−1)/2 restricted contexts. It is **not** a claim about arbitrary binary questions under a fixed number of contexts.

On a five-vertex path the fixed alphabet has two symbols. Add only the closing edge to make a five-cycle and it requires three: alternating two colors along the path forces the last and first to coincide, violating the new edge. A three-color witness is {0,2}, {1,3}, {4}. There is no pairwise contradiction in the individual contexts, just a conflict in reusing the same encoding. Removing the closing context restores two colors, a negative control.

The important prior result is H. S. Witsenhausen, *The zero-error side information problem and chromatic numbers*, IEEE Transactions on Information Theory 22(5), 592–593 (1976), DOI 10.1109/TIT.1976.1055607. The publisher abstract exposed in search describes the graph-coloring equivalence when receiver side information is unavailable to the transmitter, including possible savings from block coding. The direct publisher page then returned a robot-verification barrier; full text was not inspected. See https://ieeexplore.ieee.org/document/1055607/ and metadata confirmation at https://cir.nii.ac.jp/crid/1360011145655997184 . The present finite proof is our own exposition of an established type of result, not a claim to have invented it.

A modern primary mathematical treatment, *Side Information Design in Zero-Error Coding for Computing*, Entropy 26(4), 338 (2024), https://www.mdpi.com/1099-4300/26/4/338 , was inspected at §3.1, Definition 4, equations (7)–(8), Definition 5 and the opening line of Theorem 1's proof. Its characteristic graph captures shared compatible side information and conflicting function values. The article's asymptotic entropy/rate optimization and encoder-side information are broader than our fixed-length, single-use cardinality model. We borrow the contrast, not the rate theorem or any empirical inference. Orlitsky and Roche, *Coding for computing*, IEEE TIT 47(3), 903–917 (2001), DOI 10.1109/18.915643, identified via metadata and abstract at https://www.researchgate.net/publication/3080348_Coding_for_computing ; full text not read, not needed for the proof.

### 4. Why a graph can itself discard the crucial distinction

Set-valued actions change the obstruction. Let one context contain three states with allowed sets {a,b}, {b,c}, {a,c}. Every pair intersects, yet all three have empty intersection. A graph recording only incompatible pairs contains no edges and falsely permits a one-symbol code. Two suffice: group states 0,1 with answer b and state 2 with answer a. This is the finite set-theoretic joint-witness problem, now applied to reusable symbol assignment.

In general, let a hyperedge be an inclusion-minimal subset B that fails the proposition. Valid fibres contain no hyperedge. This follows because invalidity is upward closed: adding more constraints cannot make an empty intersection nonempty. Every invalid finite set contains a minimal invalid subset, and any set containing one is invalid. Thus the exact problem is weak hypergraph coloring: no hyperedge may be monochromatic. No pair graph suffices in general.

If all allowed actions are drawn from a vocabulary of m symbols, an empty intersection can be certified by at most m states: for each action choose a state in the same context that excludes it. The union of these selected states excludes the full vocabulary. The bound is sharp for m≥2: state i allows every action except i. Every proper subset of these m states leaves at least one action available. Therefore arbitrarily large *minimal* forbidden groups exist as the action vocabulary grows. This is an elementary finite construction, not a claim of a novel hypergraph theorem.

Countercontrols: singleton action sets reduce to pair obstructions; a universal common action eliminates all conflicts; disconnected context supports can allow symbol reuse across disjoint domains. A larger alphabet does not automatically preserve aesthetics, utility, statistical calibration, or future questions not in the model.

### 5. The limit of exaptation: unknown questions and a hypothetical instrument

Suppose the future decoder may ask any binary singleton-valued question on X. Any noninjective encoding merges u,v; choose a later question assigning distinct answers to them. No decoder repairs that collision without more information. Conversely an injective encoder can answer any future question if the question and its semantics are supplied. Thus universal future-question support is equivalent to preserving state identity in this model. No probabilistic risk or archival privacy is included.

But if future questions are known to fall into a restricted family, a smaller alphabet may be valid. The right choice depends on the purpose of the object:

- For an irreversible sound-only event summary, version the supported question family and distinguish unsupported questions from confidently answerable ones.
- For a live interface with accessible source state, transmit only what the current operation needs; do not confuse the lossy interface sign with the archived record.
- For a patch librarian or procedural authoring tool, store an immutable optional source or versioned recipe separately from the convenient display label when genuinely justified. This is a hypothetical design option, not a requirement. Data retention has cost, privacy and rights implications; more data is not automatically better.
- For an artistic instrument, exploit rather than eliminate ambiguous signs: a five-cycle score could admit local two-note interpretations while an invariant code needs three pitches. The formal analogy requires exact known contexts and reliable token decoding; real pitch identity and perceived ambiguity would need separate testing. No sound file or listener result is asserted.

An adversarial reading of X004 and #201 is therefore not that they are mistaken. Their fixed-decision claims remain intact. The conflict is between two different design goods: minimal present communication and retained capacity for future interpretation. Calling one of them universally optimal would silently change the decision problem.

### 6. Laboratory and execution boundary

Run node lab.js from this directory (no dependencies). The exact search enumerates unlabeled partitions with canonical state order, discarding a partial group when its action intersection becomes empty. A valid complete grouping with fewer symbols replaces the singleton incumbent. The search can prune when group count is at least the incumbent because adding states cannot reduce existing group count. Independently, the brute checker enumerates all labeled assignments at increasing alphabet sizes and explicitly searches the allowed action union for an admissible answer for each occupied context/symbol cell. This is an independent algorithm within the same implementation session, not an independent reviewer. Cap: ten states, exponential search, no performance claim.

Actual execution of the exact JavaScript functions before serializing them into lab.js (commit 9fd2e301f9b8fb5cd8c20f975f7acdf3e2dc1ce8) returned:

| Test family | Comparisons |
| --- | ---: |
| All labeled simple graphs on 1–5 vertices | 1,099 |
| All ordered triples of nonempty subsets of a three-action alphabet | 343 |
| All ordered pairs of partial-support binary-action contexts on three states | 4,096 |
| Total exact optimum comparisons | 5,538 |

Named outputs: five-cycle 3, five-path 2, complete graphs K1–K8 give 1–8, three-way obstruction 2 with only minimal forbidden group [0,1,2], all-compatible control 1. Invalid arrays, duplicate actions and non-array actions refused. All listed checks passed in the same tool execution. No external human review or full repository CI is implied. The accompanying Python bridge reruns the JavaScript test on systems with Node installed; it skips explicitly otherwise.

### 7. Speculative afterword — The curator's second question

The first exhibition had one question: was the thing warm or cold? Its curator assigned two tones. The archive grew. A second visitor asked whether it had once been alive; a third whether it belonged to the collection or merely passed through. The old score was impeccable under its original contract. No missing note could be found, because the missing distinctions had never been notes.

The curator could have kept every object, which would have displaced the visitors, or kept none, which would have displaced the questions. Instead she appended a small inscription to each score: *These are the questions this object can still answer.* The inscription was not a solution to the loss. It was the beginning of an honest relationship with it.

This is original fiction, not a historical event, philosophical source claim or evidence of human responses to sound.

### 8. Disposition and falsifiers

A future counterexample within the exact declared model would invalidate the theorem or implementation, depending on which fails. Changed support, unreliable symbol perception, nonstationarity, adaptive interaction, costs and mixed authority are different problems. Do not infer that a feasible action is safe or authorized in a real system. Do not infer that retaining full state identity means retaining private information indefinitely. No measured benefits of the proposed interface, scientific priority, or Brier-specific contribution are established. A formal source-aware tangent and small audit tool are sufficient; defer a production coding system unless a real use case earns its complexity.

AI-assisted work: GPT-6.2 ChatGPT, GitHub repository reads/writes, web source inspection and executable JavaScript comparison, 23 November 2026. One implementation/review session; no independent human or subagent review. No third-party source text redistributed.
