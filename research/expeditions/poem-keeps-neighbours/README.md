# The Poem That Keeps Every Neighbour

**2026-11-26 | Issue [#646](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/646) | exploratory humanities/art; not frozen Track E/G evidence.**

## The cabinet of conjunctions — interpretation

A poet is asked to make a second poem using exactly the letters of her first. The archivist is dissatisfied: a letter has lost its neighbour. She accepts a new commission, to retain not only every letter but the exact number of appearances of every consecutive pair. The archivist puts the resulting poems into the same drawer. A musician notices that they do not tell their stories in the same order.

An anagram can be an agreement about what shall remain invariant, not an agreement about what the work means. Why should the inventory consist of isolated things? We might instead demand the conservation of encounters. This shifts authorship from the choice of nouns to the ordering of their conjunctions. The important question is not how to recover an original, but how many other works can inhabit the same local description.

The proposed instrument, the **Conjunction Loom**, gives a composer a finite stock of directional transitions. A composition consumes this stock in a single continuous walk. Two compositions may share the same individual pitches, the same directional intervals with named endpoints, the same first and last pitch, and the same duration, without sharing their longer gestures. Their local grammar is the same in an exact bookkeeping sense, not in the sense of a language's complete syntax.

## Source encounters (single AI reader, 2026-11-26)

- Oulipo, [Anagramme](https://oulipo.net/fr/contraintes/anagramme), two definition paragraphs following the navigation (French, read in full). An anagrammatic poem keeps a letter inventory across successive lines. Interpretation: conservation can be chosen at another scale than letters.
- Oulipo, [Eodermdrome](https://oulipo.net/contraintes/eodermdrome), definition, example and two closing extension sentences (French, read in full). Five letters occupy a pentagon and a route visits each side and diagonal once, yielding an eleven-letter line; other units, including whole words and lines, are permitted. This is particularly close direct literary prior art: a complete undirected five-vertex graph has ten edges. It does not require the same directed pairs. The present work explicitly distinguishes orientation and multiplicity, and composes higher-order switching inside a fixed directed ledger. No literary priority claimed.
- Ciarán Ryan, [Cut ups](https://www.briongysin.com/cut-ups/), heading 'What is the cut up technique?' and the two preceding descriptive paragraphs, plus the history section opening. Ryan reproduces a passage from William Burroughs's 'The Cut-Up Method of Brion Gysin' (1961/1978 as labelled by the site). This is a mediated primary excerpt, not the original edition or complete essay. Its four-section reassembly provides an artistic contrast: the cut-up generally permits changed seams; a transition anagram deliberately conserves them. The site's later divinatory interpretations are not accepted as evidence of prediction.
- Minghui Jiang, James Anderson, Joel Gillespie and Martin Mayne, [uShuffle](https://doi.org/10.1186/1471-2105-9-192), BMC Bioinformatics 9, 192 (2008), abstract; Background, 'Methods for random sequence generation', 'The Euler algorithm preserves exact k-let counts'; Implementation, 'Directed multigraph' and 'Correspondence between permutations and Eulerian walks'. These web-text passages were read; no independent reproduction of their general uniform sampler. The paper explains exact k-let conservation by Eulerian walks and contrasts it with ordinary Markov generation that preserves counts only in expectation. This is established computational prior art, not an argument that music and genetic sequences share biological properties.
- François Pachet and Pierre Roy, [Markov Constraints: Steerable Generation of Markov Sequences](https://www.francoispachet.fr/markov-constraints-steerable-generation-of-markov-sequences/), Constraints 16(2), 148–172 (2011), DOI [10.1007/s10601-010-9101-4](https://doi.org/10.1007/s10601-010-9101-4). Author-hosted 'About the paper' and abstract read, not full article. Their constrained generation already addresses musical sequence control beyond simple greedy Markov selection. Our finite exact-inventory example is not a substitute for their general constraint machinery.

Reading scope: targeted primary descriptions, one mediated excerpt, technical article sections and an abstract. This is a small opportunistic research expedition, not an exhaustive literature review or a novelty assessment. No quotations from protected works are reproduced here.

## A finite grammar — exact construction

Let A be a home note, B and C two contrasting excursions. Each excursion leaves A for one of the other notes and returns to A. For a word w with b occurrences of B and c occurrences of C define S(w)=A w1 A w2 A ... w(b+c) A.

Every such score has b+c+1 A tokens, b B tokens and c C tokens. Its only directed pairs are AB and BA, each b times, and AC and CA, each c times. The converse holds: any score starting at A with exactly that transition ledger has this form, since neither B nor C has another outgoing edge. Therefore the number of distinct scores is binom(b+c,b), without counting indistinguishable parallel edge labels as distinct scores.

Define T(w) as the number of times consecutive excursions differ. This is exactly the combined count of BAC and CAB triples in S(w). For positive b,c the minimum is 1 and the maximum is min(b+c-1,2 min(b,c)). The lower bound follows because both letters must occur. For the upper bound, each minority letter can supply at most two change boundaries; alternating until the minority is exhausted attains the bound (when counts are equal the final boundary limit is one smaller).

The distribution is also exact. Define C(n,r)=binom(n-1,r-1) for 1 <= r <= n, zero otherwise (positive n only). For t switches let r=t+1 runs, h=ceil(r/2), l=floor(r/2). The number of words with t switches is
N(b,c,t)=C(b,h)C(c,l)+C(b,l)C(c,h).
A word beginning with B has h nonempty B runs and l C runs; a word beginning with C reverses them. Counting positive integer compositions gives the formula. Thus there are 12,870 possible scores in the balanced eight-excursion-per-type case, all with exactly the same directed transition ledger, but ranging from one to fifteen switches.

All such scores also receive the same likelihood under any fixed homogeneous first-order Markov model, conditional on the initial A: the likelihood is the product of the same transition probabilities with the same exponents. A zero transition probability makes all these scores impossible under that model, not distinguishable. Time-varying or higher-order models need not agree. Neither equal likelihood nor equal inventory means equal human perception.

## The pentagon — a second rabbit hole

The Oulipian example supplies a challenge richer than alternating excursions: visit all ten undirected edges of K5 exactly once, starting at a designated vertex 0. The executable enumerates 528 oriented rooted traversals. Rotations and reversals have not been quotiented out. Orient each edge instead from i to (i+1) mod 5 or (i+2) mod 5; this regular directed tournament has two outgoing and two incoming edges at every vertex. There are 22 rooted directed traversals using each arc exactly once. These 22 have identical directed bigram ledgers. The smaller number compares two distinct constraint families, not a universal ratio. The results are direct exhaustive software enumeration, not a claim to a novel graph theorem.

The eodermdrome is an interesting counterargument to the archivist: the prescribed network can be the work, with the particular reading only one performance. But there is no obligation to elevate the network above its realization. A performer may decide that a particular walk is the composition and that its alternatives are separate works.

## Original score — Three letters from the same cabinet

Use three pitches A=196 Hz, B=293.6648 Hz, C=392 Hz, a 200-ms slot per token, a softly tapered attack/release and an additive fundamental plus second harmonic. Play each expanded score as a separate 6.6-second miniature, without normalizing recordings independently.

| Movement | Excursions (insert A before, between and after) | Switches |
|---|---|---:|
| I. The rooms | BBBBBBBBCCCCCCCC | 1 |
| II. The alternating corridors | BBCCBBCCBBCCBBCC | 7 |
| III. The revolving door | BCBCBCBCBCBCBCBC | 15 |

Repeat I with its two blocks reversed. The archival description remains unaltered; the direction of the long gesture changes. In a live performance let a second performer hear only the A notes and announce the moments at which the next excursion differs from the last. They may instead decline to annotate. Do not treat their observations as a formal test of perception.

The renderer generates I–III only, with identical phase-reset note samples and fixed gain. It does not generate a biological process, linguistic meaning, or an actual diagnostic voice. See the execution receipt. The scores preserve slot inventories and slot-edge counts; these do not establish equality of continuous waveform spectra or arbitrary acoustic descriptors.

## Instrument construction and research questions — proposed, not implemented

The Conjunction Loom VSTi could expose a directed adjacency matrix whose cells hold remaining transition tokens. A performer drags a path through the nodes, with the instrument decrementing the chosen directed edge. A completion inspector should distinguish a locally legal move from one that strands unused edges: the residual directed graph must admit an Euler trail from the current node to the intended terminal node. A feasible-next-note filter, a manually overridable rehearsal mode and explicit failure/undo states would be preferable to a generator silently repairing the performance. In the simple excursion case, positive composition counts could guide exact sampling conditioned on a desired switch total. The general uniform Eulerian sampler is available in prior art; this laboratory does not implement it.

A Conjunction Loom effect could operate on explicit user-authored slices rather than silently inferring a segmentation. Its source-buffer inventory, transition ledger, and rendered order should be separate editable artifacts. A compact CYD interface could display a five-node pentagon with remaining directional arcs, an independent row of longer motifs, and a physical stop/reset. A larger instrument might hold several simultaneous ledgers at different orders. It should visibly identify when an added constraint makes completion impossible. Arbitrary changes of granularity can alter what is conserved.

A composer may choose a different relationship: retain an invariant but deliberately conceal which invariant it is. The audience then has a puzzle rather than an explanation. An artist may also choose no invariant at all; mathematical equality is not a requirement for aesthetic value.

Counterarguments: the exact ledger may produce tedious music, phase-reset slots remove natural articulation, and perceptual salience is not the same as a symbolic switch count. A conventional pattern sequencer may provide a more usable instrument. A future artistic test should compare ordinary shuffle, exact transition shuffle and hand composition, with ratings of perceived grouping and creative control separate from objective counts. The current apparatus contains a deliberately small set of pitches and no human results.

For MHAC operations, an inventory of local messages or ordered adjacent pairs does not necessarily specify a complete action history. Test a synthetic diagnostic task with exact pair-matched traces and different global event orders, measuring ordering reconstruction and correct actions separately. Compare to explicit ordered event records and text. A conventional authenticated ordered log may solve the entire practical problem. Do not infer action correctness, user understanding, urgency or semantic equivalence from an acoustic feature ledger, and do not use this artwork to replace operational event validation.

## Afterword — the cabinet (original speculative prose)

The archivist said the second song had all its neighbours. The singer pointed at the far door. At the first concert she had arrived there once; at the second she had gone there and back seven times. The archivist replied that no encounter had been lost.

She asked him to show her the place where he kept the journeys. He opened a drawer containing four sorts of ticket.

She took the tickets to a composer. He made a road out of the backs of the tickets and asked her to walk it. At the end she put all the tickets back into the same drawer. The drawer was indeed unchanged.

## Reconciliation and boundary

Live main base: 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS.md, RAG.md, programme, runbook, research integrity, validation and research workspace; no expedition-local AGENTS found. Checked 50 recent PR and 40 open issue results plus targeted searches (anagram, Eulerian, bigram, Oulipo, homometric, forbidden transitions, other candidate topics). Read issue bodies #302 (de Bruijn trail feasibility and novelty, especially close), #494 (collateral exceptions), #524 (spatial serialization), #199 (circular autocorrelation collision). This expedition is narrower: enumerate conserved first-order inventories with exact distribution of a freely authored second-order gesture; distinguish the literary pentagon's undirected and directed variants. Related work remains related, not evidence of novelty. #646 read back with no comments at intake.

One AI agent performed reading, implementation, native Python execution and self-review; no subagent or independent human reviewer. No frozen protocol, registry, shared manifest, production command, external outreach or participant activity changed. Draft/HOLD pending integrator review and exact-head repository qualification. See [laboratory](laboratory.py) and [receipt](RECEIPT.md).
