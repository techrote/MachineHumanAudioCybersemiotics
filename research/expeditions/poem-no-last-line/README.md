# The Poem That Has No Last Line
*An expedition in enjambment, incompatible closures and interval-overlap synthesis.*

25 November 2026 · AI-assisted exploratory research and original artistic construction · Refs #572 · Draft/HOLD. Not a frozen-protocol extraction, selected evidence record, or human-subject result.

## The room whose walls do not end its sentences

A reader marks a poem with two pencils. One marks the line breaks; the other marks the completion of clauses. Neither pencil is redundant. A line may terminate while a phrase remains open, and a phrase may terminate while a line continues. Neither termination requires the acoustic signal to become silent.

Consider an original miniature:

> The machine keeps a record of the  
> door it has forgotten. The door keeps  
> a record of the machine.

The first line suspends an object; the second contains a grammatical ending and starts another sentence. Now distribute the same words across two lines, each a complete sentence. The words and their order are unchanged, but an editorial arrangement has disappeared. Do not claim a universal listener response: these are invitations to read differently.

The artistic proposal is to give a synthesizer two independently authored segmentations of one continuous event stream. Each segmentation determines its own envelope resets, accent markers, or slowly changing modulation identity. The cross-relations between the two become a third compositional domain. A boundary can be simultaneously a conclusion in one system and a continuation in another.

## Source encounters (not systematic review)

All links consulted on 25 November 2026 by an AI assistant; reading extents below. No human verification or claim of complete source coverage. Paraphrases only.

- [Academy of American Poets, “Enjambment”](https://poets.org/glossary/enjambment), definition and opening history: a clause or sentence can run across a poetic line ending. This is an ordinary descriptive point, not a claim that all poetry requires enjambment or that all line breaks produce pauses.
- Dongho Cha, [“Sense-Making Sound: Agamben, Longenbach, and the Question of Poetic Meaning”](https://www.researchgate.net/publication/265875687_Sense-Making_Sound_Agamben_Longenbach_and_the_Question_of_Poetic_Meaning), Philosophy and Literature 38(1), 276–281 (2014), DOI 10.1353/phl.2014.0001. Accessible abstract/preview paragraphs discussing Agamben's pp. 110–115 and Longenbach; full article unavailable in this view. Cha presents Agamben's difficulty with the final verse: the possibility of continuing across a line break is exhausted at the end. This expedition has NOT read Agamben's complete primary essay. The philosophical objection is an interpretative starting point, not a premise of the graph theorem.
- Kayvan Tahmasebian and Rebecca Ruth Gould, [“Translating Line Breaks: A View from Persian Poetics”](https://soas-repository.worktribe.com/output/331518), Comparative Literature 75(3), 373–391 (2023), DOI 10.1215/00104124-10475471. [Accessible author-hosted text](https://www.academia.edu/107036175/Translating_Line_Breaks_A_View_from_Persian_Poetics_Comparative_Literature_2023_With_Kayvan_Tahmasebian), opening pp. 373–375, including “Line Breaks from Classical to Modern Persian Poetics”; metadata checked against SOAS. The authors distinguish the classical metrically regulated Persian line from modernist transformations of both visual and aural form; they caution against equating distinct Persian free-verse traditions with English or French categories. A line is not merely a metronomic interval. Our model deliberately abstracts from language-specific forms and does not translate Persian prosody.
- Ruth Koops van 't Jagt, John Hoeks, Gillis Dorleijn and Petra Hendriks, [“Look before you leap”](https://research.rug.nl/en/publications/look-before-you-leap-how-enjambment-affects-the-processing-of-poe/), Scientific Study of Literature 4(1), 3–24 (2014), DOI 10.1075/ssol.4.1.01jag. Institutional abstract, not full methods or statistics. Authors distinguish prospective (syntactically incomplete) and retrospective (syntactically complete) enjambment and report reading-pattern differences in two eye-tracking experiments. This is a study of visual reading, not proof of an auditory effect. Our predetermined cut lists cannot represent retrospective reinterpretation without an additional changing parse state.
- [Open Music Theory, “Metrical Dissonance”](https://viva.pressbooks.pub/openmusictheory/chapter/metrical-dissonance/), opening definitions, “Grouping dissonance,” examples 4–8 and “Grouping dissonance via ostinati” consulted as text; musical examples not auditioned. Existing metrical displacement and grouping dissonance already describe independently organized rhythmic layers. The 3-against-4 example and its realignment are prior art. Our four-against-four offset witness is displacement, not a newly discovered kind of rhythm.

## Formal construction: open versus cyclic boundaries

Fix a sequence of n positive unit slots. On an open interval, A and B are arbitrary sets of interior cuts, each inducing contiguous nonempty blocks. Let p and q be the respective block counts; c = |A intersection B|. On a circle, A and B are nonempty subsets of the n boundary positions; a single cut makes one full-circle block with a named start.

Build a bipartite **multigraph**: a vertex for each block of either partition, an edge for every maximal atomic interval between successive union cuts, with weight equal to its length. Parallel edges are retained: two different atomic intervals can join the same two blocks, especially when the partitions have only one cut each. Edge identities and their traversal order are separate from the weight vector.

Open: E = p + q - 1 - c, V = p + q, components = c + 1. Hence E - V + components = 0; the graph is a forest. Consecutive atomic intervals share a block at single cuts and share none at common cuts. A block cannot cross a common cut, so these are exactly the connected components.

Cyclic: E = p + q - c, V = p + q, components = max(1,c). If c > 0, the graph is a forest; if c = 0, the graph is connected and unicyclic, including a two-edge multigraph cycle when applicable. If c > 0, open the circle at any shared cut, keeping the named block identities; the other c-1 common cuts separate the resulting linear component runs. This also covers a single full-circle block with a named start. If c = 0 the chain wraps around, sharing at least one vertex across each successive pair of atomic intervals.

A second result follows from the weighted degree constraints. Given the overlap topology and each block's total duration, a forest's edge weights are unique: a leaf determines its single edge, which can be subtracted from its neighbour's total, recursively. Consistency and positivity remain necessary. In the unicyclic case, peel all leaves; the remaining bipartite cycle has even length. Alternately add and subtract delta to its edge weights. All block totals stay unchanged. The difference of any two solutions must vanish on peeled edges and alternate on the cycle, so this is the complete one-dimensional real ambiguity (for positive weights, there is an open interval of allowed delta around any solution). For positive integer weights, delta may range from 1 - min(plus-edge weights) through min(minus-edge weights) - 1 inclusive. This interval may contain only zero.

Witness: eight pulses, A cuts at 0 and 4, B cuts at x and x+4 for x=1,2,3. Every block is four pulses. Each of the four A/B block pairings occurs, with overlaps x, 4-x, x, 4-x in temporal order starting at pulse zero. Same weighted degree sequence, different overlaps. At x=0 the common-cut topology changes to two disconnected single edges. This is not ambiguity if the observer also knows all timestamps or relative phase. Even in the forest case it is the weights, not every possible temporal history, that are uniquely recovered given topology and totals.

The elementary graph and linear-algebra results are applied here as a compositional construction; no mathematical priority claimed. The topology is not a scientific model of syntax, perception, emotion, or poetry.

## An artistic interpretation: an ending as a boundary condition

There is a temptation to think of the last line as a physical catastrophe: if a phrase is unfinished when the last line ends, the work has failed to close. But an electronic score can loop. In the disjoint cyclic construction there is no common cut anywhere. Every local articulation is crossed by another segmentation. A performer can choose a final fade while refusing to promote that fade into a common structural conclusion.

The mathematics says only that the overlap graph has a cycle, not that the experience of tension persists. An ordinary repeated figure could be perceptually tedious. A listener might hear only one layer, invent a third, or ignore both. And a finite performance necessarily ends in some practical sense. The loop is a metaphorical reply to a philosophical problem, not a solution to Agamben.

There is also an aesthetic counterargument: coincident closures can be extraordinarily expressive. The proposed instrument should not maximize disagreement; it should let a composer choose when independent structures touch. A single common cut can remove the graph cycle while leaving every other boundary displaced. The most interesting moment may be the synchronization that happens after a long period of nonalignment.

## Exaptation: the Enjambment Loom

A small synthesis instrument can expose a common pulse/event carrier, two editable boundary lanes and an overlap inspector. Distinct local envelopes operate over their respective blocks; each intersection has its own modulation amount and can drive a resonator. Changing one boundary modifies which block-pair relationships exist and their durations, rather than merely changing the note sequence.

- Carrier: persistent ordered notes or spectral cells. Separate note duration from block duration.
- Line and phrase brushes: cut/rejoin each lane independently; select open or cyclic mode; show explicit termination separately from grouping.
- Intersection voice: one oscillator or FM route per atomic overlap; distinguish parallel edges. Audition it separately; do not interpret its amplitude as measured tension.
- Cycle dial: when the topology has no shared cut, use alternating overlap-duration changes within the positive interval. With fixed block lengths, reflow timing; if the timing order cannot be maintained, reject the requested edit. The four-pulse displacement witness is realizable directly as phase offset; arbitrary nonnegative matrix solutions are not automatically temporal scores.
- Closure switch: insert a common cut (or align existing cuts), inspect changed topology and deliberately reconfigure or release old modulation state.
- Retrospective parser (future): editable provisional and revised segmentations; preserve the difference between boundary asserted, inferred, revised, and explicitly ended. Do not conflate this with an actual language parser.

Engineering precedent includes ordinary DAW loop phase, polymetric sequencers, independent envelope retriggering, and MIDI articulation. The creative contribution is the explicit composition of intersection relationships and a topology-sensitive editing control.

For MHAC, a renderer could preserve message membership while presenting a different acoustic grouping. A study might compare aligned cues, misaligned groups with separately identified boundary markers, and conventional explicit labels/direct presentation. Fix event identities and total exposure where feasible; vary marker identity, duration and placement independently. Measure scope attribution and revision errors, response time, and confidence. Counterhypothesis: explicit labels dominate, or grouping marks distract. The eye-tracking research does not validate audio transfer; no participant activity authorized. Do not use artistic ambiguity to encode consequential commands. Ordinary framing and explicit scope metadata may suffice without cybersemiotics.

## Qualification and checkpoint

Oracle: 21,845 open and 86,368 cyclic marked partition pairs for n=1..8 (108,213 exhaustive cases); five additional witnesses/controls. It checks edge count, components, cycle rank, positive durations, independent per-slot degree totals, leaf reconstruction, alternating kernel and allowable integer shifts. 99,386 forest cases and 8,832 unicycle cases include the five additional witnesses/controls. Of the latter, 4,156 admit a nonzero integer shift in the tested representation. 1,367,618 checks passed in the JavaScript execution environment. This count is software checks, not independent experiments. Native Node execution and repository-wide validation were not performed in that environment. The separate native Python audio demonstration generated five six-second WAVs; see [receipt](RECEIPT.md) and [renderer](render.py).

Repository reconciliation: read AGENTS, README, RAG, programme, runbook, integrity and validation; main pinned at 495a98ca12bae467a507031f04931aa4254b1866. Read issue #572 and empty comment list. Reviewed 65 recent PR titles, 45 open issue titles, targeted searches for enjambment, line break, phrase boundary, phrasing, grouping, punctuation, caesura, prosody, metrical and earlier alternatives. No direct title match for enjambment or caesura; #334 perceptual framing and #444 mereology/group edits are adjacent; recent #532 closure concerns matching concurrent lifetimes, not overlap partition topology. Search is not a proof of novelty. Additive expedition only; no canonical evidence, shared manifest, frozen protocol or other worker files changed. No full CI, external review, or participant validation claimed. Keep Draft/HOLD pending integration.
