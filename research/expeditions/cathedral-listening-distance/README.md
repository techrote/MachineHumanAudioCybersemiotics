# The Cathedral That Cannot Be Heard from One Distance

**Expedition #721 | 26 November 2026 | exploratory interpretation, original artistic construction and synthetic mathematics | Draft/HOLD**

Base: `495a98ca12bae467a507031f04931aa4254b1866`. One ChatGPT/GPT-6.2 agent performed source retrieval, interpretation, code authorship, native execution and self-review; no independent human review. This is not Track E/G selection, a protocol amendment, or a claim about measured auditory capacity.

## The listener at the wrong distance

Imagine a cathedral constructed of sixteen sounding stones. Eight sing and eight are silent. From the entrance its monitor plays a single tone. The pitch is entirely correct: exactly half of the stones sing. At the far end a second cathedral gives the same tone. Inside the first, eight contiguous stones sing; inside the second, every other stone sings. The two buildings require different journeys even though their inventories agree.

The monitor has not lied. It has made a choice about scale. The visitor who asks where the singing stones are is asking a different question from the visitor who asks how many there are. An artist could cultivate the moment when an apparently simple surface breaks into an elaborate interior. A machine interface should instead mark that distinction whenever it matters to a decision.

A musical instrument usually treats enlargement as a change in amplitude, duration or number of voices. Here enlargement is a change in the size of the objects about which it makes statements. The unit of composition is the listening distance. A visitor could perform a journey from the whole to the parts, return to the whole, then discover that another journey began with exactly the same sound.

## Source-located encounters

- Immanuel Kant, *Critique of Judgement*, J. H. Bernard translation, [digital transcription](https://library.wrkhrs.co/texts/kant-critique-of-judgement/kant-critique-of-judgement.html), §26, printed pp. 111–113, especially the paragraphs distinguishing successive apprehension and aesthetic comprehension and the examples of viewing pyramids and entering St Peter's. Selected passage read; not the entire book or German original. Kant distinguishes accumulating parts from grasping a magnitude together; the distance examples motivate the artistic zoom here. Crucial caveat: he subsequently excludes purposive buildings as exemplary instances of a *pure* judgement of the sublime. The cathedral instrument is thus a deliberate departure, not an implementation of Kantian aesthetics. The numerical cost below is not a model of transcendental imagination.
- Edmund Burke, *A Philosophical Inquiry into the Origin of our Ideas of the Sublime and Beautiful*, [Jack Lynch's edited selections](https://www.jacklynch.net/Texts/sublime.html), Part IV §§10–11, paragraphs 4.10.1 and 4.11.1. Relevant paragraphs read. Burke gives uniform recurrence and the expectation of successive sounds a role in his account of an artificial infinite. His eighteenth-century physiological explanation is not imported as contemporary auditory science; the artistic borrowing is the tension between sameness and apparent magnitude. No attempt to induce distress or loudness is part of this score.
- Benoît Gibson, [Stochastic Music](https://www.iannis-xenakis.org/en/stochastic-music/), 18 October 2023, opening discussion and paragraphs on *Analogique A*. Selected institutional dictionary text read; Xenakis's primary 1992 book and the recordings were not examined. Gibson describes composing sonic populations using distributional properties rather than treating each voice as a continuous independent melody. This provides relevant artistic precedent for composing at the aggregate level.
- Christopher Ford, [interview with György Ligeti](https://www.theguardian.com/music/2016/feb/02/from-the-classical-archive-gyorgy-ligeti-interveiw-1974), originally 7 May 1974, republished 2 February 2016; paragraphs on micropolyphony and the *Requiem* performance instructions. Selected primary interview passages read. Ligeti describes densely woven polyphony as a means to create a collective colour; he also stresses the importance of the details generating it. No scores or recordings were inspected. This is the useful contrary position: an aggregate's expressive identity may depend on its internal construction even when individual components cannot be isolated by ear.

**Interpretation:** Burke's uniformity and Ligeti's intricate surface need not produce the same kind of magnitude. The composer's distinction is not between information and noise, but between what has been articulated at one scale and what has been withheld at another. A consciously coarse composition could make a fine structure inaccessible to the audience while leaving it available to the performer. Conversely, a composition could make the audience hear every individual detail while refusing to supply a privileged view of the whole.

**Counterargument:** An overview is not necessarily deficient; it may be the proper artistic object. Conversely a complete inventory need not produce aesthetic comprehension. The distance metaphor does not establish that listening behaves like geometrical vision. There is no measured sublime, measured recognition threshold, or claim that auditory zoom is preferable to ordinary diagrams.

## Finite construction: a dyadic listening atlas

Let N=2^h, and let x be N ordered binary cells. They are authored synthesis states, not participant data. At depth d, divide the line into 2^d consecutive blocks of width w=N/2^d and publish the ordered counts c_j of active cells in each block.

The exact number of detailed arrangements compatible with that receipt is

    A = product_j binomial(w,c_j).

Proof: each block has exactly binomial(w,c_j) distinct binary strings, and disjoint blocks can be filled independently. The formula assumes the precise partition, cell count, binary alphabet and truthful exact counts. Overlapping queries, correlations, noisy observations and other priors are outside this model.

An especially useful contrast uses N=16 and total K=8:

| Array | Root receipt | Half receipts | Quarter receipts | Full detail |
|---|---|---|---|---|
| C: 1111111100000000 | 8 | 8,0 | 4,4,0,0 | C |
| S: 1010101010101010 | 8 | 4,4 | 2,2,2,2 | S |
| T: 0101010101010101 | 8 | 4,4 | 2,2,2,2 | T |

At root all three are compatible with 12,870 possible arrays. For C, the half receipts identify the whole array (1 possibility). For S and T, the half receipts leave 4,900 possibilities and quarters leave 1,296; at pairs there are 256 possibilities. At leaf depth every array is uniquely identified. Equal spatial resolution does not yield equal recoverability: homogeneous regions carry different reconstruction costs from mixed ones.

### A score for the cost of approaching

Given the root count for free, a particular adaptive decoder asks for the count of the left child of every mixed internal node, deriving the right count by subtraction. It never queries a homogeneous node because its descendants are already known. Its additional query count Q is precisely the number of mixed internal nodes.

For total K, the sharp extremes for this algorithm are:

    Q_min = sum_{d=0}^{h-1} [K mod (N/2^d) != 0]
    Q_max = sum_{d=0}^{h-1} min(2^d,K,N-K).

Minimum proof: at a level with block size w, if K is not divisible by w, at least one block must be mixed. A prefix of K ones followed by zeros simultaneously achieves the bound at every level.

Maximum proof: each mixed block needs one zero and one one, and there are 2^d blocks. Write m=min(K,N-K). Place the m minority cells at the bit-reversed indices of the integers 0 through m-1 in h-bit representation. At depth d their block indices are the reversed low d bits of those integers, so they occupy min(2^d,m) blocks. Since m<=N/2, no aligned pair contains two minority cells. Every occupied internal block therefore also contains a majority cell. This attains every level bound simultaneously. The uniform cases m=0 give Q=0.

For K=N/2, these extremes are 1 and N-1. Thus the same correct overview count can describe an interior whose reconstruction under this protocol takes one additional count or fifteen (at N=16). No universal optimality over arbitrary questions, alternative encodings, count response bit costs, or noisy transmission is claimed. The algorithm knows the root total and N; those metadata are not free in an actual protocol.

An artistic instrument could use Q as a rhythmic structure rather than treat it as a deficit: the clustered cathedral has a very short tour, whereas the dispersed cathedral unfolds into a long branching score. A different metric, e.g. total query bits, would produce a different composition.

### Executed synthetic checks

Python 3.13.5, standard library only. Run `python laboratory.py --out audio`. Exhaustive enumeration covered 65,812 binary arrays of lengths 2,4,8,16. Every array was reconstructed; every query count equalled the independently counted mixed nodes; every depth's observed receipt multiplicity equalled the product formula; every population count's empirical extrema equalled both analytical bounds. The half-count extrema were 1–1, 1–3, 1–7, 1–15 respectively. The renderer verified repeated PCM equality, amplitude bounds, WAV metadata, full readback and the two specified collisions. The executed source Git blob was `8716ef79be1ca60461c338ffe838883769ba96af`. This is native synthetic execution, not independent review, scientific validation, or complete repository CI.

## Original score: Three interiors from one doorway

Each movement lasts four seconds. Map every block's fraction K/w to a sine oscillator at 220+440*K/w Hz, with a short attack and release. One cell per block occupies an equal share of the fixed duration. This is an arbitrary explicit sonification, not a simulation of a cathedral, acoustic propagation, or loudness perception.

1. Cluster overview, spread overview: identical four-second 440 Hz tones.
2. Cluster detail: eight high cells followed by eight low cells.
3. Spread detail: alternating high and low cells.
4. Spread quarter and shifted quarter: four identical 440 Hz cells; these two files are identical.
5. Shifted detail: the opposite alternation.

Seven files, five distinct full WAV hashes, 64,000 mono 16-bit samples per file at 16 kHz. The two specified equalities and three distinct detailed hashes passed. Generated WAVs and machine-readable receipts are produced by the committed source, not stored as canonical records. No human listening occurred.

**Performance instruction:** first hear the two overviews without labels, then switch between their detail versions. Hear the two quarter movements, then the opposing alternating sequences. Finally choose one scale and perform only that scale, treating the other as an unavailable score. The listener is not obliged to admire the detail or the overview. Any feeling of disappointment, anticipation or magnitude belongs to a possible performance, not this execution receipt.

## The listening-distance organ

A possible VSTi would maintain a large spatial population of independently editable oscillator states, a persistent hierarchy of partitions, and independent voices for aggregates and children. The player could zoom without changing the underlying population. An aggregate voice need not be the physical sum of its children; this implementation's density-to-pitch mapping explicitly is not. A dual-bus mode could preserve a physical mixture alongside the abstract receipt, so a performer can contrast them.

A VSTfx variant would require declared input events or stems and could use time-block summaries to construct a new accompaniment, independently auditioning the dry source. It must not pretend a block's summary reconstructs arbitrary source audio. A CYD XY interface could dedicate horizontal position to region and vertical position to partition depth; taps could expand a mixed block or fold it back. An FM-1 experiment could map levels to modulation lanes and design a deliberate tension between overview and resolved detail. These are design candidates; no firmware or plugin was implemented or qualified.

A further artistic rabbit hole: compose two landscapes that preserve the same receipts until an authored depth, then branch into entirely different performances. A musician could design the distance at which a secret first becomes available. The secret need not be a message; it could be another musical form. A second musician could alter the distribution of detail while preserving the score heard by a performer who remains at a particular depth.

### Operational transfer and falsification

An exact aggregate state need not support a local operational decision. A synthetic machine-monitor task could compare overview-only counts, explicit ordered block tables, adaptive count drill-down, and the same metadata with optional audio. Use identical underlying arrays and predeclared tasks: total count, local region identification, reconstruction and selecting an action contingent on a particular cell. Include homogeneous and alternating cases, equal aggregate/different local action controls, and fixed time/bandwidth costs. Keep correct decisions, abstention, latency, query overhead and confidence separate. A textual tree may be sufficient. Human testing requires the programme's real gates. No communication advantage is asserted.

## Reconciliation and disposition

Read live AGENTS, README, RAG, programme, runbook, research-integrity and validation documents. Inspected 40 recent PR titles and 30 open issue results; targeted issue searches covered sublime, multiscale, granularity, zoom, density, hierarchical and aggregation. Earlier alternatives in apostrophe, prosopopoeia and acousmatic attribution were rejected due to #602, #668, #230. The related #450 concerns pulse-density aggregation and erasure, #240 coarse-grained Markov dependence, and #717 relative role organization; this proposal concerns dyadic partition receipt multiplicity and the cost of selective count refinement, not those mechanisms. Title/search-level overlap checking is bounded, not an exhaustive novelty audit. New issue #721 was created and its comments were empty at intake.

Additive files only: this essay and laboratory.py. No protocol, canonical claims, shared manifests, stage status, other repositories, participant records or licenses modified. PR must stay Draft/HOLD pending independent mergedown qualification and actual required checks. Next action: read exact committed artifacts, inspect CI and review; no human action required at this exploratory stage.

*The architect announced that all sixteen stones were represented. The visitor asked where the eight singing stones were. The architect played the doorway again. The visitor did not ask for a louder door.*
