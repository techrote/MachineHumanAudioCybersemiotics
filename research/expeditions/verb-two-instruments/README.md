# The Verb That Has Two Instruments
## Zeugma, coupled gestures and the composition of reachable states

2026-11-26 | Exploratory humanities/art expedition | Refs #636 | Draft/HOLD

**Proposition (artistic, not empirical):** compose an instrument's verbs rather than only its voices. A single gesture can act on unlike musical objects, each interpreting the gesture in its own way. The artist can choose whether the resulting conjunction is a productive constraint, a temporary obstacle, or an inadmissible coupling.

### Contents

- [I. A word with two occupations](#i-a-word-with-two-occupations) — the rhetorical analogy and artistic premise.
- [II. Source encounters and reading limits](#ii-source-encounters-and-reading-limits) — prior art and limits of interpretation.
- [III. The exact toy model](#iii-the-exact-toy-model) — joint reachability and minimum trim cost.
- [IV. Artistic score](#iv-artistic-score-counsel-and-tea-three-hearings) — three original stereo movements.
- [V. Native qualification](#v-native-qualification-and-reproducibility) — oracle results and audio receipts.
- [VI. Exaptation](#vi-exaptation-the-yoke-loom) — instrument architecture and counterargument.
- [VII. MHAC boundary](#vii-mhac-boundary-and-second-rabbit-hole) — operational implications and speculative miniature.
- [VIII. Reconciliation](#viii-reconciliation-and-delivery-boundary) — provenance, scope and review status.

### I. A word with two occupations

In Pope's court, counsel and tea share a verb. This small syntactic economy is also an encounter between registers of activity. The listener supplies different meanings for the same occurrence of the word. The rhetorical effect is not simply a saving of syllables: duplicating the verb would preserve many of the sentence's facts but alter its architecture.

Consider an original miniature: "The organist raised the pitch and the congregation's suspicions." The sentence is not a specification for a device that raises suspicions. The interesting relation is that the same sign is engaged in two quite different operations. The two objects are not interchangeable, and there is no common numerical unit in which their changes are commensurable.

Now construct a knob labelled ADVANCE. One branch advances a four-step pitch collection. Another advances a six-step modulation-rate collection. The pitch and the rate remain independent objects with independent meanings; the performer has yoked their transitions. Unlike a metaphor that changes the description of an existing apparatus, this is an authored executable relationship.

It may be tempting to identify an instrument by its sound-producing inventory: four pitches, six rates. But two instruments with that same inventory can offer different conjunctions. A performer may discover that every pitch and every rate is individually accessible, yet that some apparently ordinary combinations cannot be played. The limitation is not in either vocabulary: it is in the grammar that joins them.

### II. Source encounters and reading limits

All readings below were checked by one AI agent on 2026-11-26. No human review or Track E/G inclusion is claimed; no restricted source files are retained.

- **Alexander Pope, The Rape of the Lock, Canto III, lines 1–16 (especially 7–8), Eighteenth-Century Poetry Archive:** https://www.eighteenthcenturypoetry.org/works/o3695-w0010.shtml . Primary text transcription, Canto III passage (archive page contains other cantos); the opening joins taking counsel and taking tea. Interpretation: a shared verb places political affairs and social ritual in proximity. This is a reading of the passage, not a claim about all readers or an exhaustive account of Pope's satire.
- **Sara Mack, “The Single Supplie”: Some Observations on Zeugma with Particular Reference to Vergil, Ramus 9(2), 1980, 101–111, DOI 10.1017/S0048671X00005403:** https://doi.org/10.1017/S0048671X00005403 . Cambridge publisher extract, opening paragraphs only, not the full article. Mack highlights disagreement over the term and proposes a convention emphasizing incongruous yoking. The online publication date is 2014, not the original issue year. Our usage follows the incongruous shared-governor sense; it is not a universal taxonomy of syllepsis or zeugma.
- **Andy Hunt, Marcelo M. Wanderley, Matthew Paradis, The importance of parameter mapping in electronic instrument design, NIME 2002, pp. 88–93, DOI 10.5281/zenodo.1176424:** https://nime.org/proceedings/2002/nime2002_088.pdf . Read PDF pages 0–2 through the informal observation and mapping-test sections; page images of 0–1 inspected. The accidental theremin anecdote describes a wiring error that made continuous hand movement necessary to sound; the later slider example uses cross-coupling. The authors argue that changing the mapping changes the instrument's character. This is direct prior art for the artistic premise, not evidence that our particular modular mapping is effective. Their informal examples and reported comparative tests are not an appraisal of population-level effects; order, gesture energy and cross-coupling are potential confounds (authors discuss factors in the later comparison).
- **Thor Magnusson, Designing Constraints: Composing and Performing with Digital Musical Systems, Computer Music Journal 34(4), 2010, 62–73, DOI 10.1162/COMJ_a_00026:** https://users.sussex.ac.uk/~thm21/thor/pdfs/Magnusson_DesigningConstraints.pdf . Retrieved text of printed pp. 62–63, opening and Constraints section beginning; page-image attempts returned 404; no figure-dependent claims made. The author argues that delimiting a gestural/compositional possibility space can support creative exploration. This theoretical argument is not a guarantee that any particular restriction is useful. The instrument might instead impede the player, and the constraint itself may be creatively exhausted.
- **Mathematical background:** generalized Chinese remainder theorem (two-congruence case), https://a-warded.org/open-book/university-number-theory/lesson-16 , section 7. Consulted accessible lesson text; elementary independent proof below, not a claim of mathematical novelty.

A crucial distinction: zeugma is a linguistic relation, many-to-many mapping is an engineering practice, and modular reachability is mathematics. The former is an inspiration for authoring the latter, not its causal explanation or proof.

### III. The exact toy model

Let A and B have m and n cyclic indices, respectively, both at least 2. Initially the state is (0,s), with s an integer offset modulo n. An ordinary shared gesture increments both indices by one modulo their respective cycle lengths; reversing it decrements both. No other operations exist until explicitly enabled. Sounding an index does not itself change state. Each pair has two independently defined rendering functions.

After t shared increments the pair is (t mod m, (t+s) mod n). Put d=gcd(m,n), L=lcm(m,n)=mn/d. The exact return period is L because simultaneous return requires t divisible by both m and n. The invariant (b-a-s) modulo d vanishes, since subtracting the two congruences cancels t. Conversely any target satisfying that congruence is reachable: writing t=a+mk gives m k congruent to b-s-a modulo n. Divide through by d; m/d and n/d are coprime, so m/d has a modular inverse and a solution exists. The reachable pairs constitute exactly one of d disjoint orbits, each with L states. The fraction of the Cartesian vocabulary available is 1/d. For coprime m,n every pair occurs, despite the shared gesture.

**Important limit:** full eventual reachability is not independent control. The next ordinary move always changes both indices. Nor is eventual reachability a deadline guarantee: from a specified origin the first forward visit to a target may be L-1 steps away. If the gesture is a continuously traversed physical knob rather than an unbounded integer encoder, the range and traversal costs must be separately modeled. The digital indices are arbitrary, not human perceptual units.

Now introduce a second verb, TRIM, which increments or decrements only B by one. Count trim operations, and treat any number of shared gestures as free for this particular objective. If r=(b-a-s) mod d in 0..d-1, the minimum number of trims to reach the target is min(r,d-r). Each trim moves the residue by one around a d-cycle; the circular distance is a lower bound. Performing those trims reaches the required orbit, after which the congruence proof supplies shared steps. This bound ignores elapsed time and number of ordinary gestures; it is not a shortest-time plan.

The number of states reachable with at most q trims is L*min(d,2q+1), because the residue ball contains that many disjoint orbits. Thus one trim unlocks all 24 states for m=4,n=6, while one trim cannot unlock every state for m=8,n=12 (d=4). The target (0,2) from offset zero needs two trims. For d=1 the trim has no value for eventual coverage, although it may change the traversal cost.

Examples:
- 4 x 6: 12 of 24 states, 2 orbits, one trim can reach the other.
- 5 x 6: 30 of 30 states, one orbit, no trim required for coverage.
- 8 x 12: 24 of 96 states, 4 orbits, one trim covers at most 72, two cover all 96.
- 6 x 9: 18 of 54 states, 3 orbits, one signed trim covers all residues.

The mathematics is an elementary application of congruences and a circular quotient graph. It proves properties of this stipulated instrument only, not properties of figurative language, human dexterity or musical preference.

### IV. Artistic score: Counsel and Tea, three hearings

Four pitches (196, 220, 261.6256, 293.6648 Hz) occupy the left channel. Six modulation rates (3, 6, 9, 12, 15, 18 Hz) act on a fixed 392 Hz sine in the right channel. Each event is 250 ms with fixed attack/release; phase resets at each event. These are deliberately differentiated synthesis registers, not a claim of perceptual orthogonality. A listener may choose either channel or both.

I. **Counsel.** Start (0,0); advance through 12 pairs twice. The even residue class is the entire permitted repertoire.

II. **Tea.** Start (0,1); traverse the other orbit twice. The marginal inventory and counts remain unchanged, but every conjunction differs as a set from I.

III. **A second verb.** Traverse the even orbit once; at the return boundary apply a single B-only trim and traverse the odd orbit once. The two registers retain the same inventories and total occurrence counts as I and II. Now every one of the 24 pair states occurs exactly once. In all three movements the entire left-channel sample sequence is identical. The right-channel order changes; it is not necessarily perceptually separable.

For a live interpretation: ask a performer to reach (0,1) from (0,0) with shared advances alone. Permit the attempt to fail, or the performer to decline. Then expose the second verb. Alternatively withhold it entirely and treat the unreachable conjunction as a deliberate exclusion. No attempt to persuade the listener that a missing pair is inherently meaningful.

The score's plot is a change in the grammar of gestures, not a change in the available oscillator parameters. An ordinary arpeggiator and cyclic sequencers could realize all three; the proposed difference is exposing the grammar, the unreachable states and explicit release gestures as things a composer edits.

### V. Native qualification and reproducibility

Run from this directory: python laboratory.py audio

Standard-library Python 3.13.5 executed locally, without optimization flags. The independent 0–1 BFS oracle treats ordinary moves as zero cost and signed B-only trims as cost one. Across all 121 ordered modulus pairs m,n=2..12, 265 distinct offset-class cases and 15,415 target comparisons passed. Each target comparison checks both exact trim distance and zero-cost orbit membership; orbit sizes and union coverage are separately checked. Negative controls: (0,1) unreachable in zero-offset 4x6; (0,2) in zero-offset 8x12 requires two trims.

Three generated stereo PCM WAVs (16 kHz, 16-bit, 96,000 frames each) passed deterministic payload re-render, amplitude bound, WAV format/readback, distinct payload checks and exact identical left-channel extraction. Pair coverage 12,12,24 respectively. SHA-256:
- even.wav: 7aca08e412dd5f9d19ae57385e0aad02e4e88b2b2981422b172b9c7d5d6ae42d
- odd.wav: 812bbd4a5dce2f5a24b5b5399bb597ec1235af38b3a8d86697916ecc890fd13d
- release.wav: 3b55fcc414b14ff106a0e95f73037a565ad4ea308f90732a269ea560b80846b0

The locally executed laboratory.py Git blob is 7eb14eb39374bcc6dfa05f24d0062cd97d171f40; fetched branch source matched. WAV bytes are regenerated rather than added to Git. No listening experiment, real-time host test, independent human review or cross-platform byte identity guarantee. Full repository validation has not been executed locally.

### VI. Exaptation: the Yoke Loom

The instrument's authoring surface could contain three layers: objects, verbs and exceptions. Objects have their own state spaces and synthesis maps. A verb applies a declared transition to each of a set of objects. Exceptions introduce an alternate gesture, not an automatic correction of artistic intent.

A compact CYD screen could display a reachable-state grid, two cyclic wheels, a shared step encoder/touch gesture, and a guarded B-only trim. The firmware must make the current mode and the effects of a step visible. A VSTi could assign one macro gesture to a pitch-class sequence and a separate timbral sequence; VSTfx could yoke a delay tap selector to a resonator-bank selector, with independent trim as an optional articulation. The real-time versions need bounded state and click-free transitions, and should leave bypass and dry audio outside the experimental mapping. No plugin or firmware built here.

The more ambitious instrument uses many independently rotating domains. The shared orbit has length lcm of their lengths, versus the product inventory; all pairwise congruences are necessary for a joint target, and the generalized CRT makes them sufficient under the unit-step model. Large products can make a one-dimensional traversal astonishingly slow even when no combination is forbidden. An interactive implementation should compute compatibility rather than enumerate astronomical joint spaces. A new question arises with several partial-scope verbs: which small set of additional gestures makes the entire state graph connected, and at what temporal cost? The current two-domain lab does not solve that design problem.

**Counterargument and revision criterion:** the coupling might be a nuisance disguised as rhetoric. A separate pitch and rate knob could be more expressive in practice, especially for time-critical targeting. The artist should be able to compare a shared verb, independent knobs, and shared-plus-trim with matched sound engines. A future authorized study could compare target accuracy, time, learnability and freely chosen creative exploration; the latter should not be reduced to number of distinct states. If a conventional independent mapping dominates the relevant tasks, retain the yoke only as an optional compositional device. No participants were recruited or studied.

### VII. MHAC boundary and second rabbit hole

A machine announcing a scalar quantity may tempt a designer to have one acoustic gesture mean both increasing urgency and decreasing certainty. The fact that both dimensions are separately measurable does not imply that all valid joint states are expressible by that gesture, or that listeners interpret the fields correctly. Before mapping, enumerate valid joint state requirements and check whether the control or code actually reaches them. Do not confuse control reachability (this expedition), waveform distinguishability, perceptual separation and correct semantic/action interpretation (#45). A conventional explicit field list or spoken serialization may be the better interface. The shared verb is an artistic constraint, not an endorsed operational communications contract.

There is an opposite rhetorical gesture: give every object its own verb, thereby removing the surprising conjunction. An instrument might deliberately alternate between those grammatical regimes. A release gesture is then a change of syntax, not an extra note. The most interesting point may be the moment when a musician discovers that a previously unavailable note was always in the instrument, but its partner was not permitted to accompany it.

*Speculative miniature:* The clerk was ordered to lower the blind and the price. The machine lowered the blind precisely six centimetres. The clerk asked what it had done to the price. It showed him a second dial; the dial was tied to the first with a piece of string. He cut the string. The shop was still dark. For the first time, the two things could be lowered separately.

### VIII. Reconciliation and delivery boundary

Read main AGENTS, RAG, PROGRAMME, AGENT_RUNBOOK, RESEARCH_INTEGRITY, VALIDATION and research README; compared live main at 495a98ca12bae467a507031f04931aa4254b1866. Inspected 55 recent PR and 35 open issue search results, targeted overlap searches (zeugma/syllepsis/one gesture/Chinese remainder/congruence/parameter mapping etc.) and the scopes of #350 (competing pitch equivalences), #422 (metaphor/executable affordances), and #45 (semantic crosstalk). These are adjacent rather than identical to joint gesture reachability. Search coverage is bounded; no assertion of exhaustive novelty. New issue #636 read back with no comments at creation. Fresh issue branch, additive directory only. Original research programme remains in progress and its frozen protocol and evidence registries untouched. One AI agent, no independent human review. Draft/HOLD pending integration review and exact-final-head checks; no human action required for this exploratory packet itself. No licence grant, external outreach, deployment or change to other workers' branches.
