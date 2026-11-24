# The Receipt That Cannot Retire Its Debt
## Closed-horizon causal compression, multicolour thresholds and the value of termination

**Refs #362 · 24 November 2026 · finite mathematics and synthetic qualification.** AI-authored and self-reviewed by ChatGPT GPT-6.2. No participant data, acoustic performance, adopted production policy, accepted Track E/G finding or mathematical priority claim.

## 1. Excavation and disagreement

[The Receipt That Needs a Wider Second Tick (#355)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/24e2500e7d0926aae5dcfa67c703c68c24cb38d3/research/expeditions/receipt-wider-second-tick/README.md), §§3–5, proves a two-tick peak-alphabet obstruction for a pentagon collision graph, expressly leaving longer streaming horizons unresolved. Its paired-digit pipeline can use a flush tick. The gap is whether a long finite stream with unrestricted decoding delay, but no flush and a narrow alphabet, can eventually extinguish earlier ambiguity. It cannot under the following conditions. This strengthens the closed-horizon result without claiming the open-ended one-tick streaming problem is solved.

[The Receipt That Cannot Share a Drawer (#347)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/486498ef2fafa1f1bf1ae1b75e70b586d068d269/research/expeditions/receipt-cannot-share-drawer/README.md) treats incompatible action bundles; here each tick independently selects an intervention, with full Cartesian support, not a common action or an indivisible cross-tick bundle. Its selective-admission and randomized-refusal objectives are not our zero-error objective. The older [Undo That Needs a Forecast (#339)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64/research/expeditions/undo-needs-forecast/README.md) separates historical information from physical restoration; that separation remains indispensable. The negative result is not a recommendation for universal logging or against delaying a decision.

Reconciliation: fetched live main 495a98ca12bae467a507031f04931aa4254b1866 and AGENTS, RAG, programme, runbook, integrity and validation. Reviewed 100 returned open issue titles and 100 returned open PR titles (capped results, not exhaustive counts); searched specifically for flush/receipt issues and matching new branch, none returned. Read the exact #355 and #347 reports, verified #355 is open draft at its stated head and its workflow run 45426919736 succeeded. New issue #362 body and zero comments verified. Other recent scopes involve passive routing, spectral moments and rhythmic translation; no overlapping file edited. Core corpus remains in progress; this expedition cannot advance its acceptance.

## 2. Model and propagation lemma (mathematics)

Use #355's finite nonempty origin set X, intervention maps f_a:X→Y, decoder observation (a,f_a(x)) and source-only deterministic causal tags e_t(x_1,...,x_t). All origin sequences and intervention sequences are allowed independently in the sense of support. The encoder sees the source prefix, not intervention identities/results, and has no future preview. Let G connect two distinct origins if some action merges them. At t, two different source prefixes are confusable iff each coordinate is equal or adjacent in G; that is the strong graph power G^⊠t. A tag prefix fibre is the set of source prefixes producing that particular tag transcript. It carries debt if it contains an edge of G^⊠t, so that the receiver could see identical observations and tags for different origins. This is an existential ambiguity over legal observations, not uncertainty in every actual observation.

Let c=χ(G), d=χ(K2⊠G). The latter is precisely the two-fold chromatic number of G: the two copies of each vertex require two distinct colours, and adjacent original vertices require disjoint pairs. Conversely any assignment of such pairs colours the product. We have c+1≤d≤2c: delete any one colour from a d-colour two-fold assignment and choose one of the remaining colours per vertex; using two disjoint copies of a scalar colouring gives the upper bound. For edgeless G debt never exists.

**Propagation lemma.** If a tag prefix fibre carries debt and the next tick admits a new arbitrary original while the available tag alphabet B is smaller than d, at least one extended tag fibre still carries debt.

Proof: choose confusable distinct prefixes u,v with identical tags. Restrict next origins to {u,v}×X. The induced confusability graph is exactly K2⊠G, since u and v are adjacent and all continuations are admissible. A next-tag function eliminating all debt would properly colour this subgraph with B colours. Impossible for B<d. Therefore some distinct adjacent extended prefixes have the same new tag. This proof does not assume the ambiguity remains about the same historical coordinate, and the witness may change with the tick. One cannot infer that all input trajectories remain ambiguous, or that one fixed pair of origins survives forever.

## 3. Closed-horizon theorem and exact suffix factorization (mathematics)

**Theorem.** Fix any finite horizon n≥1 with exactly n source-bearing slots, no extra flush and full exact recovery required by the last slot. If every slot has c≤B_t<d, every feasible causal encoder is already prefix-decodable at every tick. Its minimum distinct terminal transcripts is exactly c^n, independent of the permitted intermediate reconstruction delay.

Proof: terminal debt is forbidden by zero error. Apply the contrapositive of the lemma backward for slots n,n-1,...,2. Every earlier tag fibre is independent. For each reachable tag prefix, fix an actual source prefix within its fibre. Across all possible next origins the new tags must properly colour a copy of G, since the earlier origins and observations can be held identical. Thus each reachable tag prefix has at least c distinct children, and children of different prefixes are distinct transcripts. Induct from the empty prefix to obtain c^n. A memoryless scalar optimal colouring attains the bound and all deadlines. If any B_t<c, the entire narrow closed horizon is infeasible: that slot cannot colour even the fixed-prefix copy of G. This is a statement about distinct transcripts, not expected length, occupancy, physical energy or entropy.

**Suffix factorization.** More generally let the first s slots have arbitrary caps and all n−s later source-bearing slots have c≤B_t<d. Write T_s for the optimum of the first s slots when full recovery is required by s and there are no other intermediate deadlines. Then T_n=T_s c^(n−s) (with infeasible propagating). Backward propagation forces prefix validity from s onward; the same branching argument applies to every reachable transcript at s. Conversely concatenate a valid optimal closed prefix code and scalar colours thereafter. Thus a narrow suffix cannot rescue an unclosed prefix. A wide earlier slot can already retire debt, and the theorem does not deny this possibility. If some suffix cap<c, infeasible as above.

The threshold d is sharp for the *local* debt question: given exactly two confusable past prefixes in one fibre, a d-colour product code retires all ambiguity on the next source-bearing tick. This does not mean every larger fibre can be retired with d or that all graphs exhibit global block-coding savings.

**Pentagon:** for C5, c=3 and d=5. The lower bound d≥5 follows because each colour can appear at most twice among five vertices in a two-fold colouring, while ten assignments are required; the five pairs {i,i+2} modulo 5 for cyclically indexed vertices give a valid witness: adjacent vertices receive disjoint pairs, including wrap-around. The pair code q(x,y)=(x+2y) mod 5 is proper on C5⊠C5 by the difference argument in #355. Hence any length n closed stream of peak 3 or 4 has optimum 3^n, even if the decoder is forbidden to act until the last tick. If caps are (3,5,3,...,3), the optimum is 5·3^(n−2) for n≥2, by #355's pair code and the suffix theorem.

## 4. A single flush changes the exponential cost (mathematics)

For even n, append one source-free slot of peak three. At tick 1 emit a constant. At ticks 2j and 2j+1 emit the two base-three digits of q(x_(2j−1),x_(2j)), using leading zero padding. Each pair is recoverable by tick 2j+1; the first member waits two ticks and the second one. No future source input is used. The last slot carries no fresh origin. This yields exactly 5^(n/2) distinct complete tag transcripts. It is optimal: the tags must properly colour C5^⊠n, which has 5^n vertices and independence number at most 5^(n/2), using the established pentagon Shannon capacity √5 (Lovász 1979). Thus every colour class covers at most that many origins. The pair code attains the lower bound. The same proof applies to the unconstrained offline block alphabet, not to the narrow closed causal schedule.

| Origins n | Closed, peak 3 | One flush, peak 3 | Closed/flush |
| ---: | ---: | ---: | ---: |
| 2 | 9 | 5 | 1.8 |
| 4 | 81 | 25 | 3.24 |
| 8 | 6561 | 625 | 10.4976 |
| 16 | 43046721 | 390625 | 110.19960576 |

The ratio is (9/5)^(n/2). The logarithmic transcript count per origin changes from log2(3) to log2(5)/2 (approximately 1.585 to 1.161). Physical fixed ternary slots actually increase from n to n+1; no claim of reduced occupied time or actual transmitted binary length. A downstream entropy or variable-length coder requires its own assumptions and timing qualification.

**General pipeline:** let k≥1, B≥c and B≥2, M=χ(G^⊠k), and d_k=max(1,ceil(log_B M)). Since M≤c^k≤B^k, d_k≤k. For n a positive multiple of k, emit each block colour as d_k padded base-B digits starting at its last arrival. Blocks do not overlap. Use d_k−1 final source-free slots and fixed fillers elsewhere. Maximum reconstruction delay k+d_k−2, and exactly M^(n/k) complete transcripts. It need not be globally optimal among all length-n codes; it realizes the chosen block code. For edgeless G a constant tag is enough. This separates peak alphabet from block size, latency, and termination permission. B and d_k refer to reliable abstract symbols, not actual audio distinguishability.

## 5. Countercontrols, exaptation and unresolved question

- **Changed support:** if x2=x1 is guaranteed, the first tag may be constant and the second a scalar colour, using three transcripts with no flush for C5. The product subgraph assumed by the propagation proof does not exist. The law is known and exact, not a guess about the next state.
- **Changed capacity:** the five-symbol second slot genuinely retires debt; the impossibility is not about delay alone.
- **Changed arrivals:** a flush slot has one fixed dummy origin rather than a new arbitrary one. Its extension graph is the old fibre, not K2⊠G; the debt argument fails for a good reason.
- **Changed target:** accepting a common satisfactory remedy instead of exact reconstruction can erase the need to distinguish histories. Actual restoration requires controllability, separate from information.
- **Open horizon:** the theorem says an ambiguity somewhere persists at every later finite prefix, not that an infinite causal code cannot keep shifting its debt while satisfying finite per-item deadlines. In particular the uniform one-tick-delay infinite-stream optimum at peak three remains unresolved. Do not generalize this finite proof into a claim about such streams.
- **Stop protocol:** a producer permitted to stop after any source-bearing slot, without a flush, must have prefix-valid receipts if the stop can occur there. A promise to eventually finish an endless pipeline does not meet that contract. Announcing that the next slot is the last cannot cure debt under the same full-support narrow extension.

Interpretive/design hypothesis: distinguish a **shutdown contract** from a steady-state throughput contract. A snapshot, audio notification system or agentic recovery ledger may appear efficient by moving outstanding distinctions to the next transaction. Audit the source-bearing last tick separately from a source-free drain. Falsifier: choose an ambiguous prefix pair sharing decoder observations, extend each by every possible new original, and test whether the next tag separates the K2⊠G subgraph. Refuse closure if it does not. Record whether interruption, crash, or abrupt cancellation actually permits a drain. This is an audit idea, not a mandate to retain more user history, introduce buffering or change production architecture.

Artistic score (symbolic): for four originals, the narrow closed score sends four scalar tags. The flush score begins with a fixed tag, sends the pair digits across ticks 2–3 and 4–5. Hold the fifth beat open as a coda with no new original. If a new original is admitted during that beat, the coda has changed function. No rendered audio, listener evaluation or aesthetic preference is asserted.

Fiction: the museum's final customer arrives with a new object while the archivist is trying to close the day's register. The accountant counts the register's pages and declares the archive efficient. The archivist counts the unanswered distinctions. A final blank appointment is not another customer.

## 6. Evidence and reproducibility

Source comparison, single AI reader, accessed 2026-11-24: H. S. Witsenhausen, *The zero-error side information problem and chromatic numbers*, IEEE TIT 22(5), 592–593 (1976), DOI 10.1109/TIT.1976.1055607, publisher abstract at https://ieeexplore.ieee.org/document/1055607/ inspected (graph colouring and possible block savings when decoder alone has side information). L. Lovász, *On the Shannon capacity of a graph*, IEEE TIT 25(1), 1–7 (1979), DOI 10.1109/TIT.1979.1055985, publisher abstract at https://ieeexplore.ieee.org/abstract/document/1055985/ inspected (pentagon capacity). Full texts and comprehensive novelty search not performed. Two-fold colouring is defined and its relationship proved directly above; no claim of priority. No source excerpts committed. The asymptotic lower bound invokes Lovász's established theorem rather than purporting to derive it from finite enumeration.

Run `node lab.js` in this directory. The exact finite oracle builds causal tag-fibre partitions without assuming the propagation theorem, computes the terminal chromatic cost with exact search, and checks the narrow closed frontier for labelled graphs up to three vertices over horizons up to three. It separately tests the two-fold colouring threshold on every labelled simple graph with one to five vertices; the direct intervention maps verify product adjacency and the four-origin flush witness against every action vector at the two deadlines. Causality is checked against every unseen continuation for that fixture. The repeated-origin support control is checked directly. Counts from the precommit JavaScript runtime:

| Check | Count |
| --- | ---: |
| Labelled graphs | 1099 |
| Independent multicolour threshold tests | 2198 |
| Direct graph entries | 6586 |
| Finite optimal-frontier comparisons | 111 |
| Enumerated policy partitions | 27983 |
| Colour-search nodes | 70738 |
| Direct streaming decoder checks | 837000 |
| Unseen-suffix invariance checks | 1250 |

Overlapping synthetic checks, not independent experiments. Both proof and oracle share one author. The full general theorem is analytical, not inferred from this census. No native Node or full checkout validation performed; exact-head CI and substantive review required. Keep issue open, Refs #362, with disjoint report and lab only. No central records modified.
