# The Sentence That Ends by Refusing Its Ending

**MHAC independent expedition #786 — 2026-11-27 — speculative humanities, exact finite construction, original sound art.** Draft/HOLD; not an accepted Track E/G finding, a production design contract or a claim of mathematical priority.

## The instrument that refuses a cadence

A commission arrives for an organ with sixteen possible four-note phrases. The maker prepares every phrase, then constructs a second score which determines how much of each phrase can enter the room. Some phrases stop after one gesture. Others are allowed three. The performer must not supply the remainder even when it seems inevitable.

A conservator hears the curtailed concert and declares the organ damaged. The composer supplies two manuscripts: the repertoire and the interruptions. The conservator has been comparing the performed object against only one of its scores.

An unusual musical role follows: the performer who composes the right to stop. This need not be an editor who deletes notes from an already completed composition. It could be someone who places stopping conditions into a generative process before the event. Another performer may explore what those conditions leave unperformed. A third may refuse the premise that a stopped phrase is deficient. Each operation has a different relationship to the original score.

## Located readings (source claims, not empirical conclusions)

- Quintilian, *Institutio Oratoria*, IX.2.54–57, English transcription at [LacusCurtius](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Quintilian/Institutio_Oratoria/9B%2A.html), printed pp. 407–409. Read the complete relevant numbered passage. Section 54 discusses breaking off to suggest passion or scruple; 55 identifies a transitional use; 57 distinguishes an unfinished sentence from a rhetorically abbreviated but concluded speech. This is an account of rhetorical technique, not a physiological or listener experiment.
- Laurence Sterne, *The Life and Opinions of Tristram Shandy, Gentleman*, volume I, chapter XXXI, [original-text transcription at SparkNotes](https://www.sparknotes.com/lit/tristram/full-text/chapter-1xxxi/), chapter paragraphs beginning with the conversation about modesty and ending with the snapping of the father's pipe (web extraction lines 895–898). Read the entire short chapter body, not a critical edition; [Project Gutenberg 1079](https://www.gutenberg.org/cache/epub/1079/pg1079-images.html) indexed excerpt corroborated, direct retrieval returned 503. Sterne's narrator entertains whether Toby finished speaking, whether the pipe interrupted him, and whether the interruption was accidental or angry; he explicitly experiments with alternative completions. The uncertainty becomes the narrator's literary material.
- Thomas May, [LA Philharmonic programme note for György Kurtág's *Kafka Fragments*](https://www.laphil.com/works/kafka-fragments), paragraphs beginning with the collection of Kafka's notebooks/diaries/letters and the account of the forty pieces, continuing through the final description of minimal gestures (web lines 143–156). Read these passages. May describes a work formed from already fragmentary texts rather than a lost continuous original. The score, original texts and recordings were not inspected. This secondary account provides an artistic counterexample to the assumption that all fragments need reconstruction; it does not establish that Kurtág employed a stopping tree.
- Stanford EE274 [Kraft Inequality course notes](https://stanforddatacompressionclass.github.io/notes/lossless_iid/kraft_ineq_and_optimality.html), “Kraft Inequality & converse,” Theorem 1 and proof sketch, web lines 42–86. Read the relevant theorem and proof. Binary code leaves occupy disjoint descendant sets; equality holds when every full-depth leaf is covered. This is established mathematics, repurposed here, not a theory of linguistic meaning.

Access and reading actor: GPT-6.2 assistant using public web retrieval on 2026-11-27; no independent human review. No source text corpus copied. These are exploratory source notes outside the canonical registry.

## Interpretation: the punctuation that has several authors

Quintilian's difference between breaking off and ending early is more interesting than the classification of dashes. It suggests that two identical amounts of speech might differ in their status as completed acts. A short declaration can be complete; a long one can stop mid-commitment. Duration alone is a poor surrogate for closure.

Sterne complicates this with an external object. The pipe may have supplied the occasion for the rhetorical figure without its speaker intending to produce one. The narrator then adopts an interruption as an aesthetic operation. The resulting punctuation has at least three potential authors: speaker, interrupter, narrator. None is recoverable merely by inspecting the remaining letters. An instrument could assign these roles to independent processes: a generator, a cutter and a later editor. But the last should not silently invent an execution history.

Kurtág's fragments offer a needed objection. We need not posit a hidden complete text behind every fragment; a fragment can be a complete artistic encounter. The present laboratory deliberately does posit a finite repertoire behind its curtailed utterances. That limitation is an authored condition, not a universal model of art. A future instrument should allow standalone fragments that have no longer ancestor, side by side with fragments derived by cutting.

The design proposition is not that silence necessarily communicates. It is that the boundaries of a repertoire can become separately authored musical material. A selected termination can be meaningful in a known artistic convention while an unmarked channel loss remains epistemically unresolved. The word "aposiopesis" names an analogy; it cannot authenticate an interrupting mechanism.

## Exact construction: a frontier of endings

Let W be a uniform draw from all binary words of length D. Every bit selects the next node of a fixed phrase tree. A complete prefix frontier F is a set of terminal prefixes, none a prefix of another, covering all 2^D full words. It includes the root (empty prefix) as a legal extreme. For each W, perform the unique prefix P in F matching W.

For any terminal p of length l, the model has 2^(D-l) full descendants. Its probability is 2^(-l). The Kraft sum is exactly one. The mean emitted length E[l] therefore equals the Shannon entropy H(P) in bits, since -log2 Pr(P=p)=l. Conditional on p, the descendants remain uniform, so H(W|P)=D-E[l]. This identity is exact only under the uniform full-word prior and perfect knowledge of the prefix. It says nothing about human anticipation or musical pleasure.

A counterexample to confusing average and worst case: D=4. Frontier A = {00,01,10,11}. Frontier B = {0,100,101,110,111}. Both have mean length two and conditional entropy two bits. A always leaves four candidate words; B leaves eight on half the occasions and two on the others. Under a prior concentrated on 0000, conditional entropy is zero for both, while the emitted lengths are two and one respectively. Thus the duration/entropy identity is not robust to a changed prior.

### Sharp joint optimum for a fixed number of endings

For K terminal prefixes, 1 <= K <= 2^D, set h=floor(log2 K) and r=K-2^h. The balanced frontier has 2^h-r terminals at depth h and 2r at depth h+1: split r leaves of the complete depth-h tree (if r=0, no splits). Its mean length is h+r/2^h; worst remaining candidate count is 2^(D-h).

Proof of the worst-case bound: some leaf must have length <= h; otherwise Kraft sum <= K/2^(h+1) < 1. The balanced tree reaches the bound.

Proof of mean optimum: if a shallowest terminal has depth a and a deepest one depth b>=a+2, the deepest terminal has a terminal sibling. Split the shallow leaf and merge the deepest sibling pair. This preserves K and the depth cap, increases mean by 2^(-a)-2^(-(b-1))>0, and leaves a complete frontier. Any maximizer therefore has depths differing by at most one. Kraft equality and K then give the stated balanced depths and mean. This is an elementary exchange argument, not claimed novel.

The inverse-design instrument can choose a balanced frontier as a predictable control, then move away from it intentionally to concentrate ambiguity in selected territories. Maximizing information is not an aesthetic imperative. A one-note refusal with a large possible future might be much more interesting than a uniformly disclosed phrase.

## Executed finite census

Run from this directory: python laboratory.py audio

The recursive tree generator and an independent enumeration of all internal-node split masks agree at each D=0..4. The latter includes redundant masks below already stopped nodes; they are not unique frontiers.

| Depth | Unique frontiers | Decision masks |
|---:|---:|---:|
| 0 | 1 | 1 |
| 1 | 2 | 2 |
| 2 | 5 | 8 |
| 3 | 26 | 128 |
| 4 | 677 | 32768 |
| Total (across depths) | 711 | 32907 |

For every frontier, explicit full-word assignment checks exact coverage, subtree size, Kraft equality and the conditional-entropy identity by rational arithmetic. Every terminal count at every depth was checked against both optimum formulas. A and B are explicit equal-mean/different-worst witnesses. Complete and root-only controls are included in the census.

Native Python 3.13.5: PASS on two runs. The receipt SHA-256 was identical: 2e685e4f032fad99dc7acf50e8da97238b0096ca47f9f1739c43dd057666acbe. Tested laboratory Git blob: 975bf8be6f6416e01b01981593f8462a2726d715, retrieved from committed branch and matched. This is local isolated qualification, not full repository CI.

## Five studies for a missing cadence (original sound art)

Every full four-bit word is scheduled once, lexicographically, in a 750 ms slot. Its four nodes produce 150 ms windowed sinusoidal tiles; the last cell is rest. Pitch is a deterministic function of prefix depth and binary value; different nodes need not be treated as perceptually distinguishable. The full duration is 12 s in every edition.

1. Complete — all 64 scheduled note tiles.
2. Even cut — two tiles for each word; 32 scheduled tiles.
3. Uneven cut — one tile for the eight words starting 0, three for the eight starting 1; 32 scheduled tiles.
4. Even ghost — complementary scheduled material from study 2.
5. Uneven ghost — complementary scheduled material from study 3.

The two cut editions have the same total scheduled exposure and mean conditional ambiguity in the stipulated uniform model, but their rhythmic allocations differ. Exact samplewise addition of either cut with its corresponding ghost yields the complete edition. All five file hashes distinct; WAV metadata, payload readback, amplitude bound and same-runtime repeat hashes passed. 192000 mono frames per edition, signed 16-bit PCM at 16000 Hz. Audio files and receipt are generated, not committed binaries. No human listening study occurred. A ghost contains the supplied composer's original suffix, not an inferred missing signal.

Performance instruction: listen to the cut editions before their ghosts. Next, listen to the ghost as if it were the original. Finally, refuse to play the complete edition. Invent a standalone fragment that has no place in the tree. The last instruction deliberately exceeds the model.

## Exaptation: the Aposiopesis Organ

A playable instrument could let one hand draw stop leaves into a branching phrase atlas while the other triggers phrase generation. The choice of note and choice of how far to proceed are separate. A terminal expands into its two children on a tap; merging siblings reverses the operation. Mark the current node as an authored closure, pending continuation, accidental interruption or independent fragment; do not derive the label from elapsed silence. Preserve the generated path and stop authority separately.

VSTi: persistent node timbres, editable frontier, separate main and ghost buses, explicit standalone-fragment mode; use preallocated phrase events and schedule on the control thread. VSTfx: accept explicit segmentation and a supplied cut schedule; output a complementary bus rather than pretend to recover missing content. CYD: 320x240 tree explorer, select prefix via touch and independently modulate reveal speed and cutoff depth with XY; depth four needs only 31 nodes. FM-1: map tree edges to deterministic FM parameter trajectories and author termination/decay contracts without an automatic cadence.

A more radical composition could allow an evolving field of oscillator agents to end each other's phrases. Their cut policies would be a second spatial fabric. Pairwise influence and the authority to stop a voice must remain independent; a participant might compose the interruption without owning the interrupted material. This is a speculative artistic proposal, not qualified hardware or a real-time audio engine.

A useful conceptual inversion: the ghost bus can become the principal composition and the cut bus its commentary. Its ancestry is still legible. The system may then forget the tree by deliberate artistic fiat, but must distinguish that fiction from retained provenance.

## MHAC counterargument and proposed negative controls

A finite prefix tree is a poor model of open human utterances. The endpoint need not be selected before speaking, a listener need not share the repertoire, and the intention to break off may never be decided. Rhetorical figures do not supply a statistical prior. Distinguish terminal authority, complete delivery, intentional omission, accidental erasure, candidate continuations and independently verified facts.

A synthetic communication task could vary authorized stop vs transport interruption with matched received prefixes, and compare explicit typed end states, a full provenance ledger and optional learned acoustic cues. Include root-only, full delivery, skewed priors, incorrect cutoff metadata and essential qualification omitted as counterexamples. Correct continuation identification, false completion, abstention, latency, workload and artistic preference are separate outcomes. The strongest comparator is explicit scoped textual state plus a transport receipt; it may solve the whole problem. No acoustic advantage is demonstrated. No participant recruitment, external review or production safety claim is authorized.

## Fiction: the catalogue of endings

The conservator returned the repaired organ. It played all sixteen cadences.

The composer asked why the work had been removed.

The conservator displayed sixteen certificates of successful restoration.

The composer opened a different catalogue, in which the endings had been the works.

## Custody

Base main 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, README, research workspace, programme, runbook, integrity, validation and protocol index; checked forty recent PR and forty open issue search results plus targeted queries for aposiopesis, pruning, Kraft, prefix trees, fragments and neighbouring ideas. Read #187, #205 and #222 bodies: their focus is absence ambiguity, timing of choice and missing-content restoration, respectively; the present work concerns authored complete stopping frontiers and finite disclosure budgets. Enjambment #572 is an adjacent boundary investigation, not reimplemented. Search cannot establish exhaustive novelty.

New issue #786; exclusively additive README and laboratory in this directory. No shared registry, frozen protocol, manifest, generated aggregate or another worker's branch changed. One assistant performed source selection, derivation, implementation and native qualification; no independent human review. Draft/HOLD for integrator reconciliation, exact-head repository CI and review. No merge claimed.
