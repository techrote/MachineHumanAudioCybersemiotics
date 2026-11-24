# The Refrain That Exhausts Itself
*The impossibility of being novel forever, under an auditor's definition of novelty.*

## Status and reconciliation

2026-11-24; exploratory humanities/art research, issue #302. Base main 495a98ca12bae467a507031f04931aa4254b1866; its repository-integrity check was completed successfully. Read AGENTS, RAG, README, KICKOFF, programme, runbook, integrity, validation and research workspace instructions; reviewed 65 recent PRs and 50 open issue summaries, and inspected the accepted expedition directory. Read the newly scoped issue and its empty comment collection. Existing work on homometric rhythm (#200), temporal order (#261), gesture persistence (#271), and ordinal deletion (#293) is adjacent but does not ask this question. Owner's explicit expansive instruction permits a noncanonical expedition; it does not amend protocol v1, claim corpus completion or authorize human studies. No shared registries, manifests or other branches touched. AI-assisted research and self-check (GPT-6.2); no independent human review. Source reading extent specified below. Draft for integration review.

## 1. A small quarrel between two concepts of repetition

A museum acquires an instrument advertised as incapable of repeating itself. It contains only two notes. To prove the manufacturer's promise, the curator counts sequences of five notes and finds that none recurs until the thirty-second window. A visitor hears the lower note again in the first second. Both have interpreted the demonstration correctly; the dispute is over the unit that was allowed to repeat.

Gertrude Stein's 1934 Vassar lecture supplies a more radical challenge. In the passage preserved in Vassar's documentary chronology, she distinguishes repetition from insistence and questions whether repetition exists at all. Her examples move through recognizably recurring patterns of detective stories and newspaper criticism. The question is not whether a finite word is equal to another finite word; the occasion and emphasis of an utterance may make its return a new event. This is my interpretation of the passage, not an attribution of a combinatorial theory to Stein.

The finite instrument in this essay adopts a deliberately impoverished opposite position: equality of a fixed-length symbol window is all that counts as recurrence. In such a system it is possible to certify novelty by counting. This is a useful technical construction precisely because it excludes so much of what Stein is interested in. An invariant PCM sequence can be a new event in a different listening situation, while a never-before-emitted symbol word can be experienced as a banal reiteration of a genre.

Oulipo supplies a different relation between constraint and abundance. Its CMMP page describes Queneau's ten compatible fourteen-line sonnets; one independent choice at each line position gives 10^14 possible recombinations. The constraints are not an enemy of production but a construction of the field in which production can occur. It is tempting to confuse that count with artistic variety: one hundred trillion syntactically admissible poems need not have one hundred trillion distinguishable interpretations. Counting objects and counting experiences are different undertakings.

## 2. A score that refuses to repeat a phrase

Define a finite alphabet of k symbols and a context length n. A performer begins with a declared history of n-1 zeros. Each new symbol completes an n-symbol window. That window may never be repeated within a movement. There are E=k^n such windows. After at most E additions the rule must either be broken, reset, or enlarged. A cyclic score realizing every possible window exactly once exists: a de Bruijn cycle. In a graph with V=k^(n-1) vertices (contexts), the windows are directed edges, each joining its prefix to its suffix. Each vertex has k incoming and k outgoing edges. The desired score is an Euler circuit.

A small but important detail: the opening history is setup, not an extra scored window. For k=2,n=3, the emitted suffix 0100 is locally legal from history 00. It consumes 000,001,010,100 and returns to 00, where both outgoing edges are exhausted. The unused windows 011,101,110,111 are elsewhere. The instrument has exhausted its reachable novelty while half of its inventory is still untouched.

In contrast, the emitted suffix 01011100 from 00 consumes all eight windows exactly once. The ordering, not merely the inventory, determines whether novelty can be sustained. The finite graph does not model an audience's ability to recognize a phrase; it models the composer's declared symbol-equivalence rule.

## 3. An exact probability and a second type of musical refusal

A naive improviser chooses uniformly among currently unused outgoing edges, stopping when none remain. What is the probability of completing the whole score? Under exactly this policy, it is k^(1-n). Proof: a complete trail makes k,k-1,...,1 choices at each of V vertices, so every successful rooted trail has probability (k!)^(-V). The established count of de Bruijn cycles modulo rotation is (k!)^V/k^n (source S3 below). Each cycle visits the chosen root context exactly k times, corresponding to k distinct rooted rotations; there is no nontrivial periodicity because every n-window is unique. Multiplication gives k^(1-n). This is a derivation from established enumerative results, not a priority claim. It is not a probability of artistic success or a statement about human improvisation.

A completion guard can instead reject moves which leave the residual graph incapable of an Euler trail from the new current context back to the initial one. After any legal prefix the residual degree balance is automatically the required one; weak connectivity of the remaining non-isolated vertices to the current vertex, with the empty case closing at the root, is necessary and sufficient. Sufficiency follows by adjoining an edge from target to start if they differ, applying the Euler circuit criterion, then deleting the added edge. If current=start, the residual graph is already balanced. The guard therefore makes global completion possible after every permitted move. It does not guarantee a particular order or musical quality. It is a version of the familiar do-not-burn-bridges principle of Euler traversal.

The executable census recursively explores all legal histories, compares that connectivity predicate with actual exhaustive existence of a full continuation at each node, and verifies exact rational probability masses using integer weights. It also checks every lower-order cyclic window count on every complete score. Results (200,357 prefix visits, 257,124 assertions):

| Alphabet | Context length | Max windows | Full trails | Naive success |
|---:|---:|---:|---:|---:|
| 2 | 2 | 4 | 2 | 2/4 (50%) |
| 2 | 3 | 8 | 4 | 4/16 (25%) |
| 2 | 4 | 16 | 32 | 32/256 (12.5%) |
| 2 | 5 | 32 | 4096 | 4096/65536 (6.25%) |
| 3 | 2 | 9 | 72 | 72/216 (33.333333333333336%) |

Run `node lab.js`; `results.json` contains the actual full census, including terminal lengths and weights. Each terminal weight uses common denominator D=(k!)^V; no simulated random numbers are needed. Exhaustive verification is bounded to these five configurations; the proof gives the broader exact result. No claim of physical audio or human testing.

The first mode refuses to repeat. The second mode sometimes refuses a currently novel event in order to preserve the ability to be novel later. That is a distinct kind of rest: the composer is not forbidden to repeat because the event is old; the composer is forbidden to innovate because the event would foreclose future innovation.

## 4. Novelty is not independent of repetition

For a cyclic order-n de Bruijn score, every m-symbol window (1 <= m <= n) occurs exactly k^(n-m) times: each shorter word is the prefix of exactly that many n-words. In the binary order-five score there are 32 unique five-windows, but each four-window appears twice, each three-window four times, each two-window eight times, each symbol sixteen times. Maximal formal novelty at one scale imposes repetition at every shorter scale. A composer cannot demand complete order-five coverage and simultaneous order-four uniqueness. Changing the definition of novelty changes the constraint, not the sound itself.

Counterposition: Margulis's book On Repeat treats repetition as fundamental to musical experience, and her chapter on technologically exact repetition contrasts musical and verbal memory. The relistenings chapter takes repeated exposure and enjoyment seriously. Here the available evidence was restricted to publisher abstracts; full text retrieval failed. These positions challenge the artistic desirability of the no-repeat rule; they do not establish a preference for any of our synthetic scores. A refrain is sometimes a technology for learning what the first occurrence was. A refusal to repeat may deny the listener a chance to recognize what is being varied.

An anti-repetition interface can therefore become coercive when its designer chooses the comparison window for everyone. Consider two counterexamples to treating its rule as good design. A novice requests the same motif again to study it; a novelty guard refuses an important rehearsal operation. An alarm repeats an unresolved request; a novelty guard suppresses a useful signal because it has no model of resolution. The audit horizon should be selectable for art, and protocol semantics must take precedence over a novelty policy in operational contexts.

## 5. Exaptation: the Exhaustion Organ

Proposed instrument, not implemented hardware. Three layers: a fixed note engine, an editable equivalence/window definition, and a history ledger with residual-graph reachability. In Local mode any unused window is allowed; in Complete mode only extendible moves are allowed; in Forget mode a performer can deliberately reset the ledger, with an audible marker. The interface exposes four different quantities: used windows, unused windows, currently legal edges, and edges that retain a full continuation. Display both immediate and strategic options. Do not label a move aesthetically wrong merely because it is blocked by Complete mode.

An artist could play the comparison scale itself: while the melody continues, one performer lengthens the window used to decide whether it is new. This requires reconstructing the ledger from the actual retained symbol history, not pretending that old hashes can be reinterpreted. If the necessary past is missing, the interface must mark the new audit as partial. A second performer can change the equivalence relation (pitch class rather than pitch, rhythm rather than pitch); again the historic ledger must be recomputed or explicitly reset. A third can audition the unavailable windows as a separate voice. The shadow orchestra consists of the things a history has made impossible to play under its chosen rule.

Potential MHAC use: repeated notifications must be assessed against unresolved obligations and semantic state, not merely acoustic hashes. A candidate experiment would compare a listener's ability to reconstruct which alerts remain unresolved under exact repeats, ornamented repeats, and a versioned novelty policy. Predefine recognition, action accuracy, missed alerts, response time and perceived fatigue; distinguish repeated exposure from semantic state change. Real participant work requires the existing human gate. Do not infer from the graph that listeners prefer diversity or that suppressing repetition is safe.

## Source locators and limits

- S1 — Vassar College, A Documentary Chronicle, 10 November 1934, paragraphs 1–3, including the excerpt beginning with the question of repetition. https://chronology.vassarspaces.net/1934-11-10-stein-lecture/ . Read the complete chronology entry via web text; excerpt of Stein's lecture supplied via the college newspaper, not the complete 1935 essay or a checked critical edition.
- S2 — Oulipo, CMMP, explanatory paragraphs on ten sonnets, fourteen independent line choices and structural compatibility, https://oulipo.net/fr/contraintes/cmmp . Read the relevant explanation, original French; paraphrase and interpretation in English. No source sonnets reproduced.
- S3 — De Bruijn Sequences and Universal Cycles, “A graph model and Euler cycles,” paragraphs on line graphs and Eulerian property, and “Finding an Euler cycle,” paragraph following Fleury algorithm step 3 giving the cycle count, https://debruijnsequence.org/db/graph . Read relevant sections via web text; technical exposition, not the original 1946 paper. Established theorem used as a premise.
- S4 — Elizabeth Hellmuth Margulis, On Repeat: How Music Plays the Mind, Oxford University Press (online publication 2013), chapter 4 abstract, pp. 75–94, https://doi.org/10.1093/acprof:oso/9780199990825.003.0004 ; chapter 5 abstract, pp. 95–116, https://doi.org/10.1093/acprof:oso/9780199990825.003.0005 . Publisher abstract surfaced in search results; direct page retrieval returned an error. No chapter-level claims beyond abstract content, no empirical effect sizes asserted.

All sources consulted 2026-11-24; web-mediated reading, no retained source bytes/hashes. The essay's analogy, design and fiction are exploratory, not selected protocol evidence. The finite calculation is exact within its assumptions; it establishes neither artistic value nor a psychological law. See SCORE.md for original artistic work.
