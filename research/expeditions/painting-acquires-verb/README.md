# The Painting That Acquires a Verb

Spatial scores, traversal and the composition of adjacency — exploratory expedition, 25 November 2026, issue #524.

**Status:** original artistic research and synthetic mathematics, not a frozen Track G/E finding, participant study or claim of novelty. AI-assisted source reading, writing and software self-review by ChatGPT; no independent reviewer. Accessed public HTML passages on 2026-11-25, not complete books or scores.

## The room before its sentence

A painter puts sixteen tiles on a table. A musician asks which is the first. The painter points to the table, not a tile.

A scanner turns the painting into a sentence. This does more than place things into time: it decides what comes immediately before what. The painted object has horizontal and vertical neighbours, while the sentence has a predecessor and successor. The scanner cannot preserve every spatial relation as immediate succession in one single visit to every tile. It can preserve the entire inventory nonetheless.

This is a deliberate distinction between a loss of immediate adjacency and a loss of information. A known invertible raster order can recover every cell. The absent adjacency has not been erased from the recoverable data; it has been displaced from the immediate temporal relation. A listener might reconstruct it, ignore it or invent other relations. None of those responses follows from the graph.

## Source encounters and tensions

1. **G. E. Lessing, Laocoon**, Ellen Frothingham translation, Boston: Roberts Brothers, 1890 edition, chapter XVI, printed pp. 91–94, opening argument and examples of Hebe assembling Juno's chariot and Agamemnon dressing. [Public text](https://classic-literature.net/gotthold-ephraim-lessing-1729-1781/laocoon-an-essay-upon-the-limits-of-painting-and-poetry-with-remarks-illustrative-of-various-points-in-the-history-of-an/). Read selected chapter passages and translator's preface. Lessing distinguishes the spatial arrangement of pictorial signs from the temporal succession of verbal signs, while conceding indirect representation across that distinction. His examples suggest an object can be represented through its construction rather than through an inventory. **Interpretation:** the sonification of an already assembled object might instead compose an itinerary of its becoming. Lessing's normative aesthetics is not a law of human perception, and music is not identical to his poetry.

2. **John Cage, Fontana Mix (1958).** [Publisher catalogue, Programme Note](https://www.wisemusicclassical.com/work/69276/), paragraphs beginning with the work's indeterminacy and describing the layered sheets. Read catalogue description, not original performance instructions. A geometric arrangement of transparent sheets provides measurements from which a performer constructs time brackets and actions. **Interpretation:** an intermediate instrument for reading a drawing can itself be authored. The proposed grid scanner is not a reconstruction of Cage's procedure.

3. **David Gutkin, Unsettling the Score: Experiments in Notation, Part II**, Pew Center, 17 October 2013. [Essay](https://www.pewcenterarts.org/post/unsettling-score-experiments-notation-part-ii), paragraphs discussing example 8 and Wittgenstein. Secondary account of Cornelius Cardew's Treatise; consulted selected paragraphs, not Cardew's handbook. Gutkin describes a score without fixed sonic assignments that nevertheless has an intended governing role. **Counterargument:** choosing an interpretation does not mean the graphic object has become arbitrary decoration. A traversal instrument should expose constraints that remain authoritative even as reading changes.

4. **Agostino Di Scipio, UPIC**, Centre Iannis Xenakis dictionary, 13 July 2023. [Entry](https://www.iannis-xenakis.org/en/dictionary-upic/), paragraphs describing wavetable drawing, control signals, micro/macro time and the trial-and-error requirement. Read these selected passages. Drawn curves can supply waveform samples or modulation signals, with duration assigned separately. Di Scipio explicitly cautions that formal identity between drawing and sound does not guarantee musical sense. This is substantial existing prior art for graphics-driven synthesis. **Design implication:** the separate traversal layer should remain inspectable rather than be marketed as a new discovery of graphic synthesis.

5. **The vOICe Training Manual**, last update 24 November 2018, [§2 Image to sound mapping principles](https://www.seeingwithsound.com/manual/The_vOICe_Training_Manual.htm). Read §2 opening rules. Its established convention scans successive columns, maps elevation to pitch, brightness to amplitude, and provides lateral panning. **Counterargument:** stable mappings can support a learned task; continual artistic reordering may undermine it. The proposed single-cell sequential renderer is different from this simultaneous-column mapping and does not claim accessibility benefit.

6. **Giles Hamilton-Fletcher and Kevin C. Chan**, Auditory Scene Analysis Principles Improve Image Reconstruction Abilities of Novice Vision-to-Audio Sensory Substitution Users, EMBC 2021, pp. 5868–5871, [doi:10.1109/EMBC46164.2021.9630296](https://pmc.ncbi.nlm.nih.gov/articles/PMC9352562/). Read apparatus, procedure and textual results; figures and full statistical analysis not independently appraised. Authors report differences in reconstruction performance across sonification styles and a relationship with musical experience. **Limit:** neither their experiments nor our grid model compare the three traversal modes here. This is a discovery note, not an empirical evidence extraction or a generalized accessibility claim.

## Interpretation: a second author

The painting's author determines the tiles, positions and relationships. The traversal author selects a route and therefore makes some spatial relationships salient as consecutive events. A third author chooses how those events are sounded. These authors can be the same person, but their work is different.

The analogy to rhetoric is ordering rather than persuasion itself: a sentence that introduces A before B and another that introduces B before A can present the same inventory while making different juxtapositions. The order of reading can become an editorial decision even if no underlying facts are altered.

The opposite aesthetic is possible. A raster scan jumps from the end of one row to the start of the next. Those spatially distant tiles become temporal neighbours. Rather than remove the seam, a composer could amplify it. The apparent defect becomes a deliberate cut. A local path is not necessarily a better composition.

## Exact synthetic model

For an n-by-n square grid with four-neighbour edges, E has 2n(n-1) edges. A single serial traversal that visits each cell exactly once has n²-1 transitions, including at most n²-1 distinct true grid edges. It must omit at least (n-1)² grid edges from immediate temporal adjacency. This bound is attained by a Hamiltonian snake. A row-major raster additionally creates n-1 non-neighbour jumps, covering n(n-1) true edges.

A horizontal snake includes every horizontal edge, plus n-1 vertical connectors. Transposing it yields a vertical snake including every vertical edge plus n-1 horizontal connectors. Their union is E, with 2(n-1) shared edges. Two separate passes therefore suffice to present every undirected grid edge as immediate succession; one cannot for n>=2. This is only a minimum under the stipulated no-repeat-per-pass, serial, open-path contract. Repeated visits, simultaneous dyads or another observation relation change the problem. Pass boundaries are not grid transitions; in the concatenated audio there is an explicit conceptual boundary at four seconds, not an extra audited edge.

For 4x4: 24 grid edges; raster 12 genuine / 3 nonlocal / 12 omitted; either snake 15 genuine / 0 nonlocal / 9 omitted; two snakes 24 distinct genuine with six repeated. The maximum single-pass edge fraction is (n+1)/(2n), approaching one half. The count alone says nothing about which omitted edges matter. All 552 directed Hamiltonian paths of the 4x4 grid have 15 true transitions but their ordered content differs. Reversal is counted separately; no symmetry quotient.

An especially useful negative control: if every tile has the same acoustic parameter, every scan's PCM can be identical despite different positional transitions. Even in the supplied field, some pitches recur. Edge coverage is a property of the score's cell identities, not a claim that the listener can identify those cells from audio.

## Exaptation: the Itinerary Synthesizer

Keep a persistent drawable field of oscillator cells and an independently editable traversal layer. A path can select a single cell's pitch, waveform, envelope or FM routing, while the field stays unchanged. Provide explicit open/closed path and revisit policies; do not silently count a jump between passes as a spatial relationship. Compute the true-edge coverage and nonlocal seams as visual overlays. Optional seam resonators could render the skipped spatial relationships as a second contrapuntal voice. Allow a deliberate nonlocal cut rather than classifying it as an error.

A stronger design uses simultaneous paths with independent speeds and directions over a shared field. Their encounters and avoided regions can influence granular density or bounded modulation. The field is not necessarily a map of time; an artist chooses when it becomes one. A first prototype could remain a 4x4 or 16x16 editor with fixed envelopes and an explicit path list. Do not make a perceptual claim until the listening task and mapping are specified.

For MHAC, a neutral toy experiment might ask which of two adjacent cells differ in a static matrix. Compare a fixed invertible raster with a task-prioritized traversal and with direct pair presentation; hold total exposure or report its difference, record correct relation identification, ordering errors, learning and response time. Counterbalance paths and layouts. If direct pair presentation wins, accept it. A metric of adjacency coverage cannot itself establish usability, urgency or action accuracy. In an operational interface a stable mapping or explicit labels may be preferable; artistic surprise is not a safety feature.

## Art and qualification

See [original score](SCORE.md) and [native Python laboratory](laboratory.py). Standard library only; run with Python 3.11+ to produce four original mono WAVs (16 kHz, 16 bit). Tested locally: grid contracts for sizes 2–32; exhaustive directed Hamiltonian path census for n=2,3,4; repeated PCM, bounded samples, WAV header and payload readback. See [receipt](RECEIPT.md). No claim of human listening or independent review. The WAV files are generated rather than committed; no third-party music is used.

## Reconciliation and boundaries

Base 495a98ca12bae467a507031f04931aa4254b1866. Read live AGENTS, RAG, programme, runbook, integrity, validation and research README; target #524 and its empty comment list. Default main, 70 recent PR titles and 60 open issue titles inspected. Targeted issue searches for ekphrasis, graphic score, spatial traversal, Laocoön, scan path, intermedia and sonification painting returned no close humanities expedition; scan path hits #452 and #442 concern grammar/measurement. The earlier Two Skeletons (#444) concerns intersecting group-level edits, and Chord Loses Its Pun (#508) concerns tuning-dependent equivalence; neither is this traversal construction. These are bounded searches, not proof of originality. New branch only; frozen protocol, registry and shared manifests untouched. Draft integration review; no canonical findings or full repository qualification claimed.
