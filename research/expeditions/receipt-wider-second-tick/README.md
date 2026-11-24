# The Receipt That Needs a Wider Second Tick
## Block compression, causal peak budgets and a five-state historical archive

**Refs #354 · 24 November 2026 · finite mathematical/synthetic expedition.** AI-authored and self-reviewed by ChatGPT GPT-6.2. No empirical participant, auditory perception, physical undo, production requirement, accepted Track E/G finding or priority claim.

## Contents

1. Excavation — recover an explicitly deferred question from #210.
2. Model — separate historical recovery from receipt timing.
3. Exact frontier — prove the two-tick causal partition theorem.
4. Pentagon — derive the sharp peak-capacity and preview separation.
5. Countercontrols — change support and latency without changing the alphabet.
6. Exaptation and evidence — define a bounded audit, source limits and tests.

## 1. Excavation

[The Alphabet of Tomorrow (#210)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/38ec85c218a43474164530c4efa9227ab276872b/research/expeditions/alphabet-of-tomorrow/README.md), §§2–3, expressly excludes sequence coding but notes Witsenhausen's block-coding savings. This is an orphaned research direction. [The Undo That Needs a Forecast (#339)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64/research/expeditions/undo-needs-forecast/README.md) makes the context a later-known intervention; [The Receipt That Cannot Share a Drawer (#347)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/486498ef2fafa1f1bf1ae1b75e70b586d068d269/research/expeditions/receipt-cannot-share-drawer/README.md), §§2–4, preserves indivisible action bundles and separates historical receipt storage from advance hints. Neither answers whether several origins can share a cheaper temporal receipt. [The Rest That Arrives Too Late (#291)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/6dab50fb3685bbed534f017ca6259a29ac6e9304/research/expeditions/rest-arrives-too-late/README.md), §1, distinguishes eventual from deadline-constrained reconstruction; [The Mask That Borrows Tomorrow (#315)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/c0349ccf1c308c1e0bdf4c3a747d51fbff7b814d/research/expeditions/mask-borrows-tomorrow/README.md) distinguishes causal from retrospective encoding in a different privacy model.

The tempting inference is that permitting a small recovery delay lets an instrument use an efficient offline block code without changing its physical vocabulary. That inference is false for a stipulated two-tick contract. Delay, preview and instantaneous capacity are separate resources. This is not the previous anonymity theorem or the action-obstruction hypergraph: no anonymity or preview of the actual action is supplied here.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866 confirmed twice; AGENTS, RAG, programme, runbook, integrity, validation read. Reviewed 100 returned open issue titles and 100 open PR titles (search limits, not exhaustive counts); used the PR-specific endpoint because the generic is:pr issue search returned issue records. Searched for block/chromatic and receipt/deadline overlap and pentagon branches (none returned). Read #210 exact report, #347 exact report and lab, #346 body and comments (none), relevant #291 report passage; #347 exact-head run 45415571255 completed successfully. The recent #349/#351/#353 concern chronology, pitch equivalence and rounding; not the same scope. New #354 body and comments checked before branching. The core registry remains in progress. No other branch, shared manifest or protocol is edited.

## 2. Model (mathematics)

Let X be a finite set of possible originals. At each tick an independently selectable intervention a maps X to a result f_a(x). Every origin and every intervention is allowed. Independence here means full Cartesian *support*, not a stochastic independence assumption; there are no probabilities. The encoder sees the original x before the intervention but never its identity or result. The decoder knows the actual intervention and its exact result. Its target is exact origin, not merely an acceptable remedy.

Define G on X by adjacency of distinct origins u,v iff some intervention merges them. A valid one-tick tag is exactly a proper colouring of G. For a stream of n origins, every tuple of intervention identities is admissible. The combined collision graph is the strong power G^⊠n: two distinct words are confusable precisely if in every coordinate their entries are equal or adjacent. Necessity follows by observing the same action/result in every coordinate. Sufficiency follows by choosing a merging action independently wherever entries differ, and any action at equal coordinates. Thus a complete block tag needs χ(G^⊠n) values.

The two-tick encoder sends e1(x) at tick 1 and e2(x,y) at tick 2; each message is a single reliably distinguishable symbol at a known boundary. It may keep x in memory but has no preview of y at tick 1. The second function may depend on the first tag (which is already a deterministic function of x). The decoder has both observations by tick 2. The first tag alphabet has at most A values, the second at most B. A fixed first symbol has cost one possible value, not necessarily zero physical duration. A terminal transcript is an ordered pair of tag values. Its distinct count T is a cardinality objective, not an expected code length, acoustic bandwidth, bit rate or energy measurement. We treat fixed slot timing and alphabet caps as exogenous.

Compare (i) offline block encoding, (ii) zero-delay recovery of each origin, (iii) causal encoding with both originals recoverable by the end of the second tick. The latter grants a one-tick delay for the first original and no delay for the second. It excludes later flush slots.

## 3. Exact causal frontier (mathematics)

**Theorem.** For arbitrary finite G and the stipulated full independent intervention support, let P be a partition of X into nonempty first-tag fibres F. Put c(F)=χ(G[F] ⊠ G), where G[F] is the induced graph. A two-tick causal code with caps A,B exists iff some partition satisfies |P|≤A and max_F c(F)≤B. Its optimal terminal transcript count is

    T*(A,B) = min_{P: |P|≤A, max c(F)≤B} sum_{F∈P} c(F),

with no feasible code if the minimum is over an empty set.

Proof: the first tag is a deterministic function of x, hence partitions X. Conditional on that tag, the possible originals are exactly F×X. The combined collision graph on these is G[F]⊠G. The remaining tag must properly colour it, and no first-tag class can use fewer c(F) distinct second values. Tags can be reused across different first values because the decoder retains the first symbol. This establishes the cap and sum lower bounds. Conversely choose a proper colouring for each class, identify classes at tick 1, and emit the appropriate colouring value at tick 2. Each decoder-input fibre then contains at most one origin pair. Reuse a common second alphabet of size max c(F). This attains the stated sum. No assumption that the first tag itself decodes x is required.

Zero delay gives a different theorem: with per-tick side information and no source preview the minimum number of distinct terminal transcripts over n ticks is χ(G)^n. For a fixed actual origin prefix, adjacent possible next originals must have different current tags, since some next action/result is shared and all prior observations can be identical. There must therefore be at least χ(G) distinct outgoing tag prefixes. Starting at the root and choosing one actual prefix representative for every distinct reachable tag prefix gives at least χ(G) extensions per node until depth n. Their parents are disjoint prefixes, so induction gives the bound. Sending a scalar optimal colouring each tick attains it. This lower bound survives dependence of later tag functions on earlier originals and is not just a restriction to memoryless encoders. It relies on full support and on the decoder having no future observations at the earlier deadline.

## 4. The five-state separation (mathematics)

Take X={0,1,2,3,4}; there are five possible pair-collapse interventions, one per edge of the cycle C5. Each maps one endpoint to the other, leaving all other states fixed. Thus the scalar collision graph is C5, whose chromatic number is three (an odd cycle is not bipartite, and tags 0,1,0,1,2 work).

A two-origin block has an explicit five-tag code

    q(x,y) = (x+2y) mod 5.

For distinct confusable pairs the coordinate differences belong to {0,±1} modulo five, and cannot yield Δx+2Δy=0 modulo five unless both vanish. Hence q is valid. For a lower bound, restrict the first coordinate to any adjacent pair of originals. In the resulting ten-vertex K2⊠C5, an independent class projects injectively to an independent subset of C5 (if second coordinates coincide or are adjacent, distinct vertices conflict). Such a subset contains at most two elements. Therefore at least five tags are required. This proves exact χ(C5⊠C5)=5.

Now calculate c(F) for each first-tag fibre. If F is independent, G[F]⊠G is a disjoint union of copies of C5 and c(F)=3. If F contains an edge, it contains the ten-vertex subgraph just described and needs at least five; the five-tag global colouring restricted to it attains five. Thus c(F)=3 or 5, with no intermediate possibilities.

| First-slot cap A | Second-slot cap B | Optimal T |
| --- | --- | --- |
| Any A≥1 | B≤2 | Infeasible |
| A≤2 | 3≤B≤4 | Infeasible |
| A≥3 | 3≤B≤4 | 9 |
| Any A≥1 | B≥5 | 5 |

The middle rows follow because B<5 forces every first fibre independent, requiring at least three first colours. For B≥5 a constant first tag and q at tick 2 achieve five, and the offline lower bound prevents anything smaller. If the first tag is required to be nonconstant and B≥5, the optimum is eight: any partition into two classes has at least one class containing an edge, so costs at least 5+3; the partition {0,2}, {1,3,4} attains it. Three or more classes cost at least nine. These statements refer to the two-slot horizon only.

**Counterexample:** with the same caps A=B=3, an offline encoder can express q by two base-three digits, using five distinct transcripts. Its first digit depends on y, so it has future preview. A strictly causal encoder cannot use this saving even if its decoder can wait until tick 2: it requires nine transcripts. The offline code exists but is not a valid implementation under these peak limits. Allowing B=5 restores five transcripts with no future preview, because the full block can be encoded after y arrives.

A further established asymptotic connection: the pentagon's Shannon capacity is √5 (Lovász 1979). Thus α(C5^⊠n)≤5^(n/2); since there are 5^n vertices, χ(C5^⊠n)≥5^(n/2). Pair the coordinates and use q independently in every pair to attain equality for even n. Hence the offline logarithmic alphabet cost per origin for even n is log2(5)/2, versus log2(3) at zero delay. For odd n append a scalar tag; no odd-block exact formula is asserted. This is the familiar graph-capacity phenomenon, not a claimed new result. Our bounded causal peak characterization isolates a different implementation constraint. Logarithms here are log-cardinality in bits, not actual per-slot fixed-length binary allocations.

## 5. Countercontrols: different support and different time (mathematics)

**Shared intervention is not independent intervention.** Suppose a single action is applied to both origins, rather than two independently selectable actions. The graph is now smaller. Every action on {u,v} merges the four origins {u,v}² into the same output pair, requiring at least four tags. The following four-tag matrix (row x, column y) works:

    0 2 1 0 1
    3 1 2 1 0
    0 3 0 2 1
    1 0 3 1 0
    3 1 0 3 2

For each action on an edge {i,i+1}, modulo five, the four entries of its 2×2 collapsed submatrix are distinct. The other nontrivial fibres consist of two cells on the same row or column with indices i,i+1; every cyclic adjacent entry in each row and column differs. Therefore the matrix meets all decoder fibres and four is exact. The lab independently derives the graph from actual maps, finds a four-colour witness and checks every decoder input. It removes 80 directed adjacency entries relative to independent actions (40 undirected edges). This is a negative control against silently multiplying the same context into independent contexts.

**Another tick changes the peak result.** If the first of each pair can wait two ticks and the second one tick, a ternary stream can realize the five-tag pair scheme without preview: at tick 2 emit floor(q/3), at tick 3 emit q mod 3, at ticks 4 and 5 do the same for the next pair, and so on. Tick 1 is fixed; an even-length finite stream needs one flush tick. With known framing, each pair has five distinct joint transcripts and each slot uses at most three symbols. This is an explicit causal construction; it does not solve the general infinite-stream problem with uniformly one-tick delay and peak three. The exact infeasibility above concerns a closed two-slot horizon, not all pipelined systems.

If only an acceptable remedy rather than exact origin is needed, #210's set-valued decoder can reduce these requirements, possibly to one symbol. If the encoder can see the intervention, it can simply label its at-most-two origin fibre; if it can write later to the same record without loss or trust cost, the receipt timing changes. If a snapshot or independent source already exists, the tag may be redundant. None of the graph results establishes control of a physical actuator or validates retaining sensitive history.

## 6. Exaptation, provenance, laboratory

**Design hypothesis, not an adopted contract:** audit a prospective receipt encoder against a tuple of origin/action support, source-arrival time, encoder-visible inputs, decoder-visible side information, recovery deadline, maximum alphabet per slot, total transcript count and final flush permission. A block-code witness should not qualify a bounded stream without a realizable schedule. Falsification fixture: freeze first input x and all permitted past inputs, vary y; any changed first tag violates no-preview. Separately, force first and second slots to three symbols, require both originals by tick 2, and attempt to fit five transcripts. Supply an adjacent first-fibre pair or a scalar three-colour certificate to expose the contradiction. Do not prescribe larger vocabularies or delayed action without an actual application cost model.

**Source comparison (access 2026-11-24, single AI author):** H. S. Witsenhausen, *The zero-error side information problem and chromatic numbers*, IEEE TIT 22(5), 592–593 (1976), DOI 10.1109/TIT.1976.1055607, publisher abstract at https://ieeexplore.ieee.org/document/1055607/ inspected: it explicitly distinguishes encoder side-information access and possible block savings. L. Lovász, *On the Shannon capacity of a graph*, IEEE TIT 25(1), 1–7 (1979), DOI 10.1109/TIT.1979.1055985, publisher abstract at https://ieeexplore.ieee.org/abstract/document/1055985/ inspected: pentagon capacity √5. Y. Kaspi and N. Merhav, *Zero-Delay and Causal Single-User and Multi-User Lossy Source Coding with Decoder Side Information*, arXiv:1301.0079 (2013), https://arxiv.org/abs/1301.0079, abstract inspected as a contrary/broader framing: sequential encoding and decoding, instantaneous codes and average distortion. Their objectives are not our fixed two-slot cardinality/cap model; no theorem equivalence inferred. Full papers and comprehensive novelty review not performed. The elementary finite proofs above are supplied rather than resting on source abstracts. No third-party article text committed.

**Artistic score, symbolic only:** Five possible original notes 0–4; a second event is drawn from the same set. A mechanical transformation may collapse a neighbouring pair, and the restorer receives its identity and result. Give a three-timbre instrument a two-tick performance deadline. It plays the scalar tag 0,1,0,1,2 at each onset. A five-timbre instrument waits through the first onset and plays the block colour at the second. A three-timbre instrument with an extra tick can play the two ternary digits instead. The performance is a formal analogy; no acoustic render, intelligibility or aesthetic superiority asserted.

**Fiction:** The archive purchases a narrow pipe because its new two-note notation needs only five symbols across two events. At the second event the archivist discovers that the five-way distinction must all travel through one opening. She can widen the pipe, delay the delivery, or go back to the old notation. She cannot change yesterday's message by citing an efficient score written tomorrow.

**Computational qualification:** Run node lab.js. The dependency-free lab constructs actual interventions, enumerates decoder observations, derives graph edges independently of the formula, performs exact DSATUR-style colour search (all colours up to the first feasible cardinality, symmetry breaking only on unused labels), enumerates all 31 nonempty first fibres and all 52 set partitions, and checks direct decoder injectivity for every chosen branch witness. It additionally verifies the shared-action control and future-preview witness for base-three digits. Executed the exact function before committing, then replayed fetched code at 972a6bfda28d0f9fad8c29c634650e670a20562e in a JavaScript runtime.

| Check | Count/result |
| --- | ---: |
| Direct graph vs strong-product entries | 625 |
| Exact colour search nodes | 2606 |
| Direct decoder-input checks | 11375 |
| Partition-cap comparisons | 1560 |
| Nonempty first fibres | 31 |
| First partitions | 52 |
| Shared-action minimum | 4 |
| Shared-action removed directed adjacencies | 80 |
| First-origin values with offline preview witness | 5 |

Both executions returned identical results. Counts overlap and are synthetic checks, not independent experiments. The oracle and proofs share one author. Native Node and full checkout validation not performed in this session; exact-final-head CI and substantive independent review remain required. No mathematical priority, empirical calibration or universal compression mandate claimed. Keep issue and PR open pending review; no edits outside the two isolated expedition files.
