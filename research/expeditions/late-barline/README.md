# The Barline That Arrives Late

*Retrospective metre, time-consciousness and the right to revise a score.*

2026-11-26 | [Issue #656](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/656) | Exploratory humanities/art lane; not a frozen-protocol evidence record. AI-assisted writing, source encounter, mathematical derivation, code and self-review by ChatGPT (GPT-6.2); no independent human review, participants, or claimed novel theorem.

## An opening that has two endings (original essay)

The drummer arrives six seconds after the organist. The organist has played the same high note every fourth pulse. The drummer plays a lower note every third pulse. The engraver immediately redraws the barlines of the opening, though no one has replayed it.

A second engraver refuses. She insists that the opening is in four and the new section is in three. A third annotates two concurrent grids. The three engravers agree perfectly about the recording's samples and disagree about the work's organisation.

The attractive mistake would be to treat the later accompaniment as a revelation of what the earlier sound really was. That is one possible authorial convention, but the opening has no obligation to belong to the same metre as its continuation. A change of interpretation, a change of metre, and the arrival of a competing metre are different musical propositions.

This is the useful distinction: the history of a performance can be immutable while its descriptions are not. A new description need not be a correction of an earlier error. It may be the product of a new relation between two materials. A listener who has already heard the ending is not obliged to hear the beginning as a first-time listener would. A recording can remain perfectly repeatable without the act of listening being repeatable in that stronger sense.

For MHAC, this matters because a machine's explanatory voice can also be produced after the events it describes. It might legitimately reclassify a previously recorded event given new observations. It must not silently claim that the new classification was known at the earlier time, or that the new evidence was already present. An instrument can make this distinction expressive before an interface makes it accountable.

## Source encounters and disagreements

Reading performed on 2026-11-26; each locator identifies the actual extent consulted. These are contextual encounters, not systematic-review inclusion decisions.

| Encounter | Access and locator | Source claim and interpretation |
|---|---|---|
| Dan Zahavi, *Edmund Husserl*, Stanford Encyclopedia of Philosophy (entry first published 8 Aug 2025) | [§4, Time- and self-consciousness](https://plato.stanford.edu/entries/husserl/#TimeSelfCons), especially the paragraphs using C, D, E and the distinction from episodic memory; online entry retrieved, selective section reading, no independent reading of Husserliana | The account distinguishes primal impression, retention and protention, with the temporal perspective of earlier notes changing as subsequent notes arrive. Interpretation: a musical past is not exhausted by an inventory of the earlier sounds. Retention is not a waveform buffer, a versioned database or an inference algorithm. |
| Christopher Hasty, *Meter as Rhythm*, twentieth anniversary edition (2020) | [ch. 7, Meter as Projection, pp. 113–126, DOI 10.1093/oso/9780190886912.003.0007](https://academic.oup.com/book/36981/chapter-abstract/322302023); indexed publisher abstract only; direct retrieval failed | Hasty treats the potential of a completed duration to condition its successor as central to metre. Interpretation: durations can furnish opportunities for subsequent events rather than merely occupy positions on a pre-existing grid. This is a challenge to our finite grid, not its philosophical warrant. |
| John Roeder (1998), review of Hasty, *Music Theory Online* 4(4) | [§§2.1–2.4](https://www.mtosmt.org/issues/mto.98.4.4/mto.98.4.4.roeder.html); retrieved HTML, selected paragraphs | Roeder describes Hasty's process account, including the role of Whitehead, and observes the awkwardness of using spatial diagrams to represent a theory concerned with temporal becoming. This secondary reading motivates the proposed instrument's irreversible live pass followed by optional retrospective views. |
| Justin London, *Hearing in Time*, 2nd ed. (2012) | [ch. 6, Meter-Rhythm Interactions II: Problems, pp. 99–109, DOI 10.1093/acprof:oso/9780199744374.003.0006](https://academic.oup.com/book/9899/chapter-abstract/157217076); indexed publisher abstract only; direct retrieval failed | London distinguishes metrical malleability from conflicts with an established metre, and discusses resetting period and phase. This is direct prior art for metric ambiguity. The book is not being claimed as evidence that these particular four synthetic recordings produce a specified experience. |
| Nicole Biamonte (2014), Formal Functions of Metric Dissonance in Rock Music, *Music Theory Online* 20(2) | [§§7.2–7.4, 7.6; opening example 10b discussed in §7.3](https://www.mtosmt.org/issues/mto.14.20.2/mto.14.20.2.biamonte.html); HTML retrieved, selected analytical text, musical excerpts not auditioned | Biamonte discusses openings retrospectively interpreted following later musical cues, including The Cars' Just What I Needed, and different forms of metric dissonance. The described phenomenon is existing compositional practice, not an MHAC discovery. Her example concerns displaced downbeats; our score explores changing grouping periods. |

Two philosophical cautions follow. First, Husserl's account addresses the structure of experiencing a temporal object, not the engineering of a delayed decision. Calling software's recent history its retention is metaphor, not an implementation of phenomenology. Second, Hasty's account questions the assumption that metre can be represented adequately as fixed marks on an axis. Our two grids are deliberately external, revisable notation; they do not pretend to be all that listening entails.

## A tiny apparatus of revision (formal construction)

Assume known equally spaced pulses, indexed 0 through N-1. Define a proposed downbeat flag G(p,a)[i] = 1 exactly when i mod p = a, and zero otherwise. The period p is a positive integer, phase a is a residue in 0..p-1. The flag is a label, not an amplitude measurement. A 3-pulse and a 4-pulse grid with phase zero coincide at pulses 0, 12, 24, ... .

Let L = lcm(p,q) and d = gcd(p,q). In one common period, the exact Hamming distance is

    D = L/p + L/q - 2 * I[(a-b) mod d = 0].

Proof: each grid has L/p or L/q ones; the Chinese remainder theorem gives one shared one in the common period if the phases agree modulo d, and none otherwise. The symmetric difference counts contested labels. For k complete common periods multiply D by k. Partial periods require direct counting.

For (3,0) and (4,0), D=5 in 12 pulses; D=10 in the 24-pulse opening of our score. These are ten annotation positions that differ, not ten mistakes made by a listener.

Now suppose the eventual author chooses either grid. Before that choice a notation system can mark each disputed position as the A interpretation, the B interpretation, or deferred. Common positions can be committed without disagreement. If exactly b disputed positions are deferred (0 <= b <= D), the other D-b have x A-supporting and D-b-x B-supporting flags. Worst-case revision count is max(x,D-b-x). It is minimized by balancing the two counts:

    minimum worst-case revisions = ceil((D-b)/2).

The lower bound follows from the sum of the two possible error counts; assigning half to each candidate, differing by at most one, attains it. If all committed labels must agree with a single coherent grid, the worst-case count instead equals D-b. A hybrid can reduce worst-case edits but is generally not a coherent musical metre. This makes a genuine design choice visible: locally robust annotations can be structurally inconsistent. The balanced solution is not a prescription for performance or human interpretation.

| Deferred disputed positions (24-pulse opening) | Worst-case revisions, free hybrid | Worst-case revisions, coherent provisional grid |
|---:|---:|---:|
| 0 | 5 | 10 |
| 2 | 4 | 8 |
| 4 | 3 | 6 |
| 6 | 2 | 4 |
| 8 | 1 | 2 |
| 10 | 0 | 0 |

All costs count only changed *committed* labels. Filling deferred labels still requires work. No cost for musical confusion, display clutter, physical latency, or human effort is assumed. The result is a simple two-hypothesis minimax construction, not a psychological theory.

The executable laboratory independently enumerates all phase pairs for periods 2–9 across one common cycle (1,936 cases), and all ternary assignments for 0–9 contested positions (29,524 assignments). The 24-pulse example is separately checked. The implementation exhausts the small assignment domain rather than generating only the proposed optimum. It does not estimate perception, solve arbitrary multi-grid optimisation, or infer metre from audio.

## Original performance score: Four Ways to Engrave a Beginning

Use a 250 ms pulse for 48 pulses. A fixed bright pluck begins each pulse: 330 Hz fundamental, a stronger 660 Hz partial at every fourth pulse, common gain and exponential decay. Its complete 12-second left-channel recording is the same for all four realizations. The right channel is silent for pulses 0–23. At pulse 24, choose one:

| Movement | Later voice | Proposed notation |
|---|---|---|
| I. The engraver in three | 110 Hz on every third pulse | Retrospectively draw the 3-grid across the entire recording. Retain the original 4-grid as a provisional annotation. |
| II. The engraver in four | 146.83 Hz every fourth pulse | Retain the 4-grid. |
| III. The engraver who leaves | No new voice | Leave the explanatory choice open. The left material is still accented in four; the absence of an authority cue does not prove perceptual ambiguity. |
| IV. The two engravers | Both later voices | Keep both grid annotations, or stipulate a local transition instead. Do not require one canonical resolution. |

All four recordings share exactly the first six seconds of stereo PCM. They have distinct complete PCM signals; the left channel remains identical throughout. The recordings do not reveal a uniquely correct interpretation. The later voice is an authored framing device, not a statistically fitted observation or an actual audience response.

Performance instruction: listen once without looking at a score. Then inspect the two proposed grids and replay. You may reject both, change metre at the entry, or describe the lower voice as a counter-rhythm. This is an invitation to artistic listening, not a recruited participant test.

A fifth movement need not be rendered: a conductor is given both possible endings on paper, while a second performer knows only the introduction. The first may anticipate a later entry; the second may not. The first is not a better witness of what the second knew at the time. In a live performance the audience could be given the conductor's score late, or never. The time at which annotation is made available becomes part of the score.

## Instrument exaptation: Retrospective Loom

Three independently persistent tracks: (1) immutable captured carrier and original event times; (2) proposed metric frames with phase, period, scope, issue time and version; (3) later contexts and explicit interpretive decisions. A live view shows the currently adopted frame, including its provisional status. A historical view reconstructs the annotations as of a selected knowledge time. A retrospective view overlays the latest interpretation on the unchanged carrier. An alternate view preserves conflicting grids instead of merging them.

Useful interactions: paint a barline grid across a recorded segment; pin provisional annotations; choose whether a later entry causes a local change, retrospective re-reading, or coexistence; mark undecided positions without deleting their pulse; show exact revision count; audition each context stem; optionally sonify only newly changed flags during replay. Never alter historical carrier bytes just to make a revised analysis sound inevitable.

The VSTi would synthesize the fixed pulse carrier and independently editable context voices. A VSTfx would accept an explicitly bounded captured loop and attach separate annotation/accent layers, with independent dry audition. A CYD interface could display stacked rows of pulse dots, with a scrubber selecting knowledge time versus performance time. The touch gesture moves a barline rather than a note. MIDI automation can drive future context changes; realtime audio cannot rewrite already emitted samples. None of these implementations is delivered here: only the offline generator and model.

Second rabbit hole: perhaps the score can preserve not only the alternative readings but the sequence of abandoned readings, making the act of editorial revision audible. For instance, replay committed downbeat additions in one timbre and removals in another. The listener might experience an editor's trajectory as music. But such a trajectory describes an annotation history, not the history of a listener's consciousness. The metaphor is productive precisely when the distinction survives.

## Operational counterargument and proposed experiment (not conducted)

This is adjacent to #224 (decipherability), #572 (overlapping partitions) and #562 (duration inference), but the pulse inventory here is known, and two authored annotation conventions can both remain viable. The question is the cost and provenance of a revised interpretation rather than recovery of a hidden token boundary or true duration. Conventional multi-version records and DAW arrangement views already supply much of the engineering machinery.

In a future synthetic study, compare a versioned annotation display, a latest-only display, and explicit plain text. Provide a common event history and later evidence that either changes the provisional interpretation or confirms it, with a fourth condition in which nothing resolves the uncertainty. Separate tasks: reconstruct what actually occurred; identify what was known at a particular earlier time; select the current interpretation; decide an allowed action. Record whether each version is distinguished, not whether the sonic device seems persuasive. Include a no-change control and a deliberately misleading retrospective display. Use an ordinary event log as a strong baseline. No participant recruitment or human trial is authorized by this record.

A counterhypothesis is that separate annotation layers merely add clutter. The complete historical log with timestamps may be more effective; late reinterpretation can be a compelling artistic event while remaining inappropriate for consequential live instructions. A warning or action status must never be silently retroactively changed or withheld for aesthetic effect. If new evidence warrants correction, issue a new version and preserve what was actually sent.

## Fiction: the engraver

The engraver asked the conductor whether the first measure had been three or four.

The conductor said that it was four until the other musicians arrived.

A philosopher said that this was impossible, since the first measure had already finished.

The engraver drew two barlines above the same note and dated them separately.

The composer bought the score, not because it had answered the philosopher, but because he could now compose the dates.

## Execution and handoff

Base: 495a98ca12bae467a507031f04931aa4254b1866. Branch mhac-656/late-barline. Live AGENTS, RAG, programme, runbook, research integrity, validation, freeze and workspace authorities reconciled; 50 recent PR titles, 35 open issue titles and targeted searches (including metric ambiguity, garden path, Husserl, anticipation, prosody and enjambment) inspected. Issues #224, #572 and #562 bodies read; new target #656 body and empty comments confirmed. Search coverage is bounded, not a claim of exhaustive novelty.

Run laboratory.py with Python 3.11+ from any working directory, without optimization flags. It writes four original stereo WAVs and a receipt beside the source. The recorded execution used Python 3.13.5. No third-party recording or source text is included. The mathematical and audio checks are local software qualification only. See [RECEIPT.md](RECEIPT.md) for exact hashes and scope.

No shared manifest, protocol, registry, evidence stage or other worker branch is modified. No production implementation, human study, review or scientific acceptance. Draft/HOLD for mergedown review and exact-head repository qualification; Refs #656 only.
