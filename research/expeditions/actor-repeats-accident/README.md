# The Actor Who Repeats the Accident
## Theatrical fidelity, cue-contingent synthesis and the ethics of the rehearsed reply

Expedition #735 · 2026-11-26 · AI-assisted exploratory writing, not a selected source extraction, empirical finding, completed protocol work, or peer-reviewed result.

## An opening scene (original fiction)

A theatrical clock plays a little melody every evening at the moment a dancer enters the stage. The dancer once misses her entrance. The clock plays anyway. A second clock, fitted with a sensor, remains silent. A third clock waits for the dancer and moves its melody a little later. At the next rehearsal all three perform the same score perfectly. The director asks which is the best actor. The technician asks what the director means by a score.

The first clock has a relation to the theatre's time. The second has a relation to an event but preserves the theatre's rhythm when possible. The third has a relation to an interval between two events. The three relations are not different degrees of musicality; they are distinct commitments. A clock that faithfully repeats the scene may fail to participate in it. Conversely, a clock that responds may destroy a precisely composed interruption.

The issue is not that a machine should have an inner life. It is that its observable reply may be a trace of several very different contracts. The artistic opportunity is to perform the contract itself.

## Source encounters (located and limited)

- Horace, *Ars Poetica*, lines 99–113, A. S. Kline translation (2005), [section AP:73–118](https://www.poetryintranslation.com/PITBR/Latin/HoraceArsPoetica.php). Read this section's surrounding passage on genre, expressive decorum and grief. Horace presents appropriate expression and the speaker's inward condition as relevant to moving a spectator. The text is a poetic prescription, not contemporary experimental evidence. Other translations can emphasize display rather than felt emotion; no original Latin critical edition collated.
- Denis Diderot, *Paradoxe sur le comédien*, Assézat and Tourneux ed., Garnier (1875), vol. VIII, pp. 361–423, [French transcription](https://fr.wikisource.org/wiki/Paradoxe_sur_le_com%C3%A9dien). Selected passages read in French, not the entire dialogue or facsimile. Locate the first interlocutor's paragraphs beginning “Ce qui me confirme dans mon opinion”, “Au lieu que le comédien qui jouera de réflexion”, the Clairon rehearsal discussion, and “Réfléchissez un moment sur ce qu’on appelle au théâtre être vrai.” The interlocutor contrasts variable feeling-led playing with repeatable, studied construction of an ideal model. Crucially, the passage beginning “C’est ici le lieu de vous parler de l’influence perfide d’un médiocre partenaire” and the next paragraphs make the ensemble and the accommodation of a partner relevant to the model. Do not collapse this staged debate into a theorem about emotions. The digitized transcription has not been independently checked against the print edition.
- Heinrich von Kleist, *On the Marionette Theatre* (1810), Idris Parry translation, [Southern Cross Review transcription](https://southerncrossreview.org/9/kleist.htm). Read the opening mechanism discussion (paragraphs about centre of gravity, free-moving limbs and the operator's sensitivity), and concluding bear/fencing and grace passages. The dancer in the dialogue suggests a simple control of the puppet can organize complex motion; the conclusion places grace at two imagined extremes of consciousness. The bear story is a literary episode, not verified animal behavior. The narrator's objections and the theological ending caution against treating it as a control-engineering paper.
- Robert Rowe, *Interactive Music Systems* (1993), [chapter 1 author-hosted text](https://wp.nyu.edu/robert_rowe/text/interactive-music-systems-1993/chapter-1-interactive-music-systems/), indexed passages on score-driven/performance-driven and instrument/player paradigms and score following. Search-index excerpt consulted; direct retrieval returned 502. Substantial prior art, not a full reading. No priority is claimed for reactive accompaniment or the score-following distinction.

These sources disagree fruitfully. Horace's concern is the effect of fitting expression. Diderot's dialogue shifts attention towards the repeatable fabrication of that expression, yet it also asks how the performance survives the other actor. Kleist imagines graceful movement arising from constraints without elaborate self-monitoring. Neither author needs to be recruited as an advocate of modern machine speech. A model of a machine's control structure is not a model of theatrical subjectivity.

## Interpretation — the three loyalties of the actor

A recorded note can preserve its place in a score, its relation to another event, or its evidential authority. These are three different objects of fidelity. The first is not necessarily more objective than the second: both are measurable once their reference is specified. The third is not guaranteed by either.

The Diderotian ideal model is not a PCM recording. It is something the actor constructs, studies and can exceed through practice. A rigid playback algorithm is an intentionally crude caricature, useful only as a contrasting instrument behavior. The passage on the partner prevents us from reading Diderot as advocating deafness to context. Likewise, Kleist's puppet is not an autonomous dancer: its center is guided by a performer. Delegating motion to the material does not remove artistry. It redistributes it.

A composer might author an apparently indifferent response, allowing a late partner to collide with a perfectly measured beat. Another might make responsiveness itself audible. A third could deliberately repeat an impossible duet in which one performer remembers the absent partner. These are artistically viable under different declared rules. In a machine status interface, however, a prerecorded response must not be represented as evidence of an event that did not occur.

## Finite score and executable contract (synthetic)

Four cue slots have nominal ticks 4, 12, 20, 28. Tick = 125 ms; intended reply delay L = 3 ticks. Each slot has a known identity and a cue displacement d in {-2,-1,0,1,2}, or no cue. A missing cue is known by closure of the slot's acceptance window at nominal +2. The model does not recognize cues in audio; slot-labelled symbolic input is supplied.

Four policies:
- clock: play at t+3 even if the cue is missing;
- gated score (k=0): play at t+3 only if cue present;
- compromise (k=1): play at t+3+clamp(d,-1,1) only if cue present;
- partner (k=2): play at t+d+3 only if cue present.

These are offline schedulers, but their present-cue replies are always at least one tick after their actual cue. A streaming version can calculate the reply once its slot-tagged cue arrives, suppress a missing gated slot, and requires a bounded delivery delay. There is no guarantee for arbitrary jitter, missing slot identity, event duplication or late deliveries. The oracle refuses displacement outside its contract. No claim about real-time implementation is made.

For each present cue and a reply r, absolute fidelity cost A=|r-(t+3)| and relational fidelity cost R=|r-(t+d+3)|. The triangle inequality gives A+R >= |d|. Equality holds precisely between the two desired times, including endpoints. For any nonzero d, zero cost on both dimensions is impossible. A clipped correction lies between them; for fixed d its errors are min(k,|d|) and max(0,|d|-k). This is elementary geometry, not new mathematics. For zero displacement all policies coincide. For an absent cue a phantom reply is counted separately; for a present but unanswered cue an omission would be counted separately. Timing costs are intentionally not computed for absent cues and never treat omission as a successful timing outcome.

The census covers all 6^4=1,296 labelled histories; each of four policies is checked on each (5,184 policy evaluations). Aggregate absolute/relative/phantom/omitted costs:

| Policy | Absolute ticks | Relational ticks | Phantom replies | Omitted present cues |
|---|---:|---:|---:|---:|
| clock | 0 | 5184 | 864 | 0 |
| gated score | 0 | 5184 | 0 | 0 |
| compromise | 3456 | 1728 | 0 | 0 |
| partner | 5184 | 0 | 0 | 0 |

Counts are finite census totals, not estimated frequencies in a population. There are 4,320 present cue occurrences and 864 absent ones. The clock's ghost reply is an intentional negative control, not a failure if it is independently labelled an autonomous part. Gating dominates clock for the stipulated reply contract, but cannot by itself maintain the relative delay under displacement. The three gated strategies offer selected Pareto points; not a census of every possible scheduler or objective. No human listening, perception, emotion, causation-in-the-world or communication advantage is claimed.

## Sound art — Five rehearsals for an empty stage

Run `python laboratory.py audio` with Python 3.10+ (standard library, no inputs required). Original 4.5-second stereo PCM works, 16 kHz, 16-bit; left is cue, right reply. Note pitches distinguish the four slots, envelopes are authored. The nominal version is sample-identical for all four policies. The perturbed score is (+2, absent, -2, +1); all four perturbed left channels are identical; right changes. Recordings: rehearsal, clock, gated, compromise, responsive. Read receipt.json for hashes and exact timings.

Actual local qualification: Python 3.13.5, two executions; generated audio and receipt files compared byte for byte, no differences. WAV headers and PCM readback validated. Nominal render equality, perturbed left equality and four distinct perturbed stereo renders passed; all census assertions passed. Source Git blob 751832fa35b4f1c3a04e2ea14f1795e21e344423. Same-runtime determinism only; no cross-platform bitwise guarantee.

Performance instructions: listen to rehearsal once. Listen to clock twice, first as an accompaniment, then as a purported response to the left. Notice the missing second cue in all perturbed versions. The clock's right-channel note is not a mistake in its own score, but it would be a false reply if the label said it acknowledged a received cue. Listen to the gated score, then the compromise, then the partner. Finally reverse the roles of the two ears in your imagination, without pretending that a reply caused an earlier cue. These are compositional instructions, not results from listeners.

## Instrument construction and research questions (proposed)

The Rehearsal Theatre could be an event sequencer with a score clock and a cue clock. Each track would retain the nominal event, actual event, accepted deadline, reply provenance and a correction budget. An independent ghost bus could perform missed cues explicitly as imagined continuations; it must never be conflated with acknowledgements. A VSTi could take MIDI note-ons on a cue bus, offer per-voice phase loyalty and export an event ledger. A VSTfx could operate on explicit host MIDI or supplied transient annotations; automatic onset detection is a separate problem. A CYD XY interface could use horizontal position for clock loyalty and vertical position for voice density, with touch triggering a local cue. A live engine needs bounded queues, host sample timestamps, transport/seek behavior, timeout policy and deterministic event identities; none are implemented here.

Artistic research: the musician might assign clock loyalty to one oscillator population and partner loyalty to another. A touch gesture that shifts the common cue then produces a spatially distributed canon. A third population plays only the unperformed alternatives. A different experiment would deliberately make the cues themselves responses, introducing actual feedback and possibly unstable timing; the present nonrecursive model supplies no stability claims. An instrument should disclose whether a performer is listening, replaying, or inventing a counterpart to silence.

Operational hypothesis: users may interpret a well-timed motif as proof that a machine received an event when its controller actually played an autonomous scheduled part. Compare text-only timestamp/receipt tables, absolute playback with explicit provenance, gated replies and cue-relative replies. Include absent, late, duplicated, wrongly scoped and stale cues, and a conventional explicit acknowledgment baseline. Measure source attribution, actual event reconstruction, false acknowledgment, action selection, abstention, workload and latency separately. A simple typed event receipt may solve the entire operational problem. No participant recruitment or test is authorized or performed. Evidence to overturn the hypothesis would include no difference in source attribution under equivalent explicit labels or a strong negative effect from extra audio.

Counterargument: the clock's indifference may be precisely the theatre's point. A responsive instrument can become aesthetically servile. Neither ideal is universal. The aim is not to decide between Horace and Diderot with a timing equation but to provide a stage on which rival obligations can coexist. Do not equate mathematical fidelity with affect, consciousness or grace.

## Checkpoint

Live AGENTS, RAG, programme, runbook, research integrity and research/root README consulted; target issue body and zero comments fetched; main base 495a98ca12bae467a507031f04931aa4254b1866; forty recent PR titles, thirty open issues and targeted overlap searches reviewed. Simondon/associated milieu already #414, anacoluthon #366, paratext #532, sorites #197, rehearsal #214 (higher-order knowledge), instrument memory #270 and graph/open-loop work #191/#232 are adjacent but different. Searches for Diderot, Kleist, marionette and Stanislavski returned no issue hits; no guarantee of global novelty. Own only this expedition directory; do not edit shared manifests, accepted evidence or frozen protocols. New branch and draft PR for independent mergedown; no automatic closure or merge. Source notes and synthetic results are not canonical findings. No independent human or agent reviewer. No human action required for this scoped exploratory artifact.

*The clock was applauded for repeating the scene exactly. The dancer had been absent for three nights. In the programme the technician changed one word: accompaniment, not reply.*
