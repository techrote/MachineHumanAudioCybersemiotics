# The Keyboard That Can Play Every Duet But Not the Trio

*Prepared piano, compound affordances, and composition of the unplayable.*

Exploratory humanities/art lane, 2026-11-27. Refs #752. AI-assisted original notes and synthetic software, not a selected empirical study, an accepted Brier reconstruction, a human review, or evidence of improved communication.

## A theatre with a spare musician (original fiction)

Four notes live behind four keys. A, B and C share two musicians, either of whom can play any of those three notes. D has the services of two different musicians. The patron tests every key and every duet. All work. The patron writes that the instrument has four-note polyphony.

When the composer requests ABC, one musician remains idle. Another is unable to help. Neither is trained in those notes. A vacant chair does not solve the problem.

The composer asks the instrument maker not to repair it immediately. She wants to write a piece that makes the instrument's impossibilities audible. A second performer will edit the affiliations of the musicians during the performance; the pitch identities and their individual sounds must remain intact. A chord that was once impossible becomes a new musical event without the addition of a new note.

The maker has composed a possibility, not a sound.

## Source encounters and disagreement

- John Cage, [How the Piano Came to be Prepared](https://www.data-johncage.org/prepared_piano_essay.cfm), author retrospective first written 1972, revised web edition hosted by the John Cage Trust. Read the complete short essay, especially paragraphs beginning "The Cornish Theatre", "Having decided", and "When I first". Cage explains the practical stage-space problem posed by Syvilla Fort's dance, experiments with objects on the strings, and the eventual realization that his prepared sounds varied across instruments and performers. The artistic problem shifted from writing for a given instrument to changing its material constitution. This is Cage's retrospective account, not an independently verified chronology. His racialized shorthand about musical suitability is not a premise adopted here; the practical constraints and technique are the relevant historical claim.
- Dominic Murcott, [Tomorrow's Music On Yesterday's Machines](https://mtosmt.org/issues/mto.14.20.1/mto.14.20.1.murcott.html), Music Theory Online 20(1), March 2014, introduction [1] and text of [4]–[9]. Murcott describes the specific Ampico reproducing instruments employed by Conlon Nancarrow, their split dynamic control, hammer alterations and damping. The instrument enlarged some temporal possibilities while imposing its own organization of dynamics and material attack. The text, not the audio/video examples, was examined. His curator's account also treats authentic reproduction as a situated problem; the full article was not read.
- Whitney Museum, [High Pressure Repairs: Restoring the Player Piano for Conlon Nancarrow](https://whitney.org/whitney-stories/preparing-the-player-piano), 27 June 2015, paragraphs beginning "Finding such a machine", "Nancarrow customized" and "Though many". Institutional report and attributed technician statements, article body read. Restoration exposed tempo, release and pneumatic limitations. This is contextual support for the specificity of mechanisms, not experimental evidence for the allocation model.
- William W. Gaver, [Technology Affordances](https://doi.org/10.1145/108844.108856), CHI 1991, pp. 79–84; author's [public text](https://www.researchgate.net/publication/221518931_Technology_Affordances), abstract and opening of Introduction. Gaver distinguishes action possibilities from their perceptibility and discusses compound affordances organized in time or space. Only these portions were read. The allocation construction below is a deliberately narrower model of compound capability; it does not operationalize ecological perception or bodily affordances as a whole.
- Indian Statistical Institute, Discrete Mathematics course notes, [§6.1 Hall's marriage theorem and SDR](https://www.isibang.ac.in/~d.yogesh/Course_Notes/DM1/Ch6.S1.html), Definition 6.1, Theorem 6.2 and its proof read. Established matching theory supplies the mathematical model. No mathematical priority is claimed.

All source accesses 2026-11-27 by the same AI research worker. No independent human verification. No source copies or third-party audio retained.

**Interpretation:** Cage's preparation changes the relationship between gesture and sounding material. Nancarrow's mechanism changes the space of performances that a particular player can execute. Gaver invites the question of whether such possibilities can be perceived. Our proposed preparation is a different one: change the relationships among simultaneous gestures without changing their individual sonic realizations.

This distinction is not a historical claim about Cage's pianos. It treats his decision to alter the instrument rather than accept its limitations as an invitation to compose a new kind of constraint.

A counterposition: a piano is not simply a set of independent resources. Its resonance, mechanical interaction, bodily affordances and unstable material behaviour cannot be preserved by a binary compatibility matrix. Precisely those irregularities may be what make prepared piano interesting. The digital model should be considered a new instrument rather than a theory or simulation of the original one.

## A preparation of permissions (exact finite construction)

Notes are A=220, B=277, C=330, D=440 Hz. There are four interchangeable-in-sound but independently occupied ports. A note may occupy a permitted port for one simultaneous chord; no port serves two notes in that chord.

| Note | Limited preparation | Expanded preparation |
|---|---|---|
| A | 1, 2 | 1, 2 |
| B | 1, 2 | 1, 2 |
| C | 1, 2 | 1, 2, 3 |
| D | 3, 4 | 3, 4 |

All six unordered pairs work in both. In the limited preparation ABC cannot be assigned, because its three notes have just two eligible ports. D's extra port cannot help. Other triples work. In the expanded preparation every subset works: allocate A to 1, B to 2, C to 3 and D to 4.

Even exact recordings of all single notes and pairs do not identify the difference, given port-invariant rendering. A three-note probe distinguishes these two preparations. Neither the waveform nor the visible count of ports establishes joint capability. This is an authored equivalence, not an empirical statement about synthesizer hardware.

For a chord Q, let N(S) be the union of eligible ports for S, where S ranges over subsets of Q. By Hall's theorem, Q is feasible iff every S has at least |S| neighbours. Define deficiency D(Q) = max over S of (|S| - |N(S)|), including the empty set. Then maximum matching cardinality equals |Q| - D(Q).

Proof: for any S, at least |S|-|N(S)| of its notes must remain unmatched. Conversely append D(Q) dummy ports, each eligible for every requested note. Every nonempty S now satisfies Hall's condition, so a full matching exists in the augmented graph. Remove the dummy ports: at least |Q|-D(Q) original assignments remain. The bound is attained. This proves a maximum number of notes, not an ordering or a musically preferred omission.

The example generalizes: take k+1 notes sharing k ports, and a separate note with two different ports. Every subset of at most k notes can be assigned, but the first k+1 notes cannot coexist, even though there are enough total ports. Therefore no fixed test of k-note capability establishes arbitrary polyphony. The number of notes and allowed routes are finite and fixed for the duration of each test.

**Further derived result, not separately executed:** resilience to any e arbitrary port erasures for a nonempty Q requires |N(S)| >= |S|+e for every nonempty subset S of Q. Sufficiency follows because at most e neighbours vanish. Necessity follows by erasing as many as possible, up to e, from a violating S. This is for known erasures, not incorrect outputs or reallocation delays. A composer can invert the objective: intentionally remove a small group of ports to release an authored obstruction.

## Executed synthetic census and score

Run `python laboratory.py` from this directory using Python 3.11+ (tested locally with 3.13.5, without optimization). It writes original mono signed 16-bit PCM files at 16 kHz and a JSON receipt into its local audio directory. Audio output is not committed; source is sufficient to regenerate it. Do not run with assertions disabled. 

Every labelled binary adjacency graph with three ports and either three or four notes is enumerated, including disconnected and empty cases. For every chord, explicit partial assignment enumeration is compared against the independent subset-deficiency calculation.

| Notes | Graphs | Graph/chord cases | All solos and pairs feasible | Of these, at least one impossible triple |
|---:|---:|---:|---:|---:|
| 3 | 512 | 4096 | 286 | 39 |
| 4 | 4096 | 65536 | 1696 | 687 |

All 69,632 cases passed. These are counts over labelled graphs, not incidence estimates for real instruments. The four-port example is separately checked.

Five original editions:
- Duets limited and duets expanded: AB, AC, AD, BC, BD, CD; each half a second. The two WAVs are byte-identical.
- Trio refused: D, silence, silence, D.
- Trio serialized: D, AB, C, D.
- Trio expanded: D, ABC, silence, D.

Each event lasts 0.5 s; a sine-squared envelope shapes a fundamental plus a second harmonic. Port identity is deliberately excluded from the signal map. The rejected raw ABC render is independently tested to raise before writing. Refusal is represented by a separately authored silent slot, not successful playback. Serialization has changed the timing contract and is not equivalent to the full chord. Both refusal and serialization should have explicit labels in a real operational interface.

The native run checked complete WAV payload readback, parameters, sample bounds via signed conversion and equality of duet hashes. A common recording is not a common capability. The render is a synthetic oscillator score, not a sample of an actual piano. No listeners were tested.

## The second rabbit hole: a score for the instrument maker (speculative art)

A performer plays a sequence of chords on the ordinary keys. A second performer operates a graph editor that determines which voices can perform them. The second performer may change connections only during designated interludes. A third performer reads out the rejected chords, not as errors but as the score of a different instrument.

A request for an impossible chord yields several permissible artistic choices:
- explicitly withhold it;
- audition all largest feasible fragments in succession;
- negotiate a new preparation;
- play a delayed realization;
- perform the missing-note identities with an independent resonator, without claiming they were successfully allocated.

The rule is that the audience's score may say what the sound cannot say. The silent event is not an admission of success, and the sound of an impossible chord on a separate bus is not its realization on the original instrument.

A useful contrast: a designer might want predictable capability. An artist might want fragile capability and make a precise constellation of forbidden chords the identity of a patch. Neither preference can be inferred from the mathematics.

## Exaptation and proposed instrument

Prepared Keyboard VSTi: a small oscillator bank with editable note-to-voice compatibility, fixed integer polyphony and selectable matching policies. Retain stable requested note IDs, current assignments, unallocated identities and optional refusal/repair bus. Initially perform allocation outside the audio callback and publish immutable bounded snapshots; real-time transitions, note-off identity, tails, latency and voice stealing require separate tests. No runtime implementation is claimed.

CYD: a 4x4 touch matrix of note/port connections plus an XY performance surface. One axis biases desired chord size, the other chooses an explicitly named repair policy. A hold gesture locks currently sounding notes while proposed changes are auditioned in a separate monitor. A graph editor should show actual assignments and an obstructing subset, not just a generic polyphony number.

FM-1: prospective patch-level mapping of notes or modulation gestures to a limited set of independent carriers; demonstrate contention symbolically before making any assumption about device resources. A general graph-based constraint synthesizer could make its own topology a playable parameter.

MHAC communication hypothesis: individual capability acknowledgements do not license a joint action. Compare an explicit textual allocation table, pairwise availability reports, and a proposed obstruction cue carrying the set of affected actions and shortfall. Vary requested concurrency and known resource outages independently; score exact whole-bundle selection, unnecessary refusal, incorrect implied availability, workload and time. Keep cue comprehension separate from actual task execution. Conventional resource reservation and structured textual errors may solve the complete engineering problem. No acoustic advantage is established.

## Reconciliation and boundaries

Read live AGENTS, README, RAG, programme, runbook, integrity and validation instructions; 45 recent PR titles, 30 active issue titles, targeted issue searches (prepared piano, affordances, matching, polyphony, scordatura, zeugma, reversibility and alternatives). Related issue bodies #636 (shared-step reachability), #692 (retuning and gesture translation), #346 (action-bundle receipt obstructions) consulted. This construction is specifically a matching-constrained voice allocation with identical duet renders and a hidden triple obstruction, not a claim that compound incompatibility is new to MHAC. Search indexing limits absolute novelty claims. New target #752 body and empty comments retrieved. Base 495a98ca12bae467a507031f04931aa4254b1866. Work exclusively in this directory. Keep Draft/HOLD per issue scope and independent integration workflow; no frozen protocol, registry, shared manifest, production firmware or participant changes. Full repository CI, integration and independent review are not claimed by this local experiment.

*The patron tested every pair of musicians. The composer requested three. The empty chair remained empty. The maker drew one new line. The piece began.*
