# The Tune That Changes Its Allegiance

**Expedition #705 | 26 November 2026 | Exploratory humanities / artistic research | Draft for mergedown**

## Contents

- 1 — The anthem: speculative fiction about inherited musical associations.
- 2 — Source encounters: contrafactum, prosody and limits of the reading.
- 3 — Accent budget: exact counterexample and generalized bound.
- 4 — Six ceremonies: original performance score.
- 5 — Qualification: executed mathematical and PCM checks.
- 6 — Design proposals: instruments and controlled experiment.

## 1. The anthem of the gate (original speculative essay)

The city replaces its gatekeeper with a singing machine. The machine has only one tune. The city has several governments. Each government purchases a new set of words, but the instrument maker has guaranteed that the tune will remain unchanged.

At the opening ceremony the children recognize the melody before the first sentence is complete. The minister believes that this establishes continuity. The locksmith believes that it establishes a liability: the same tune once accompanied the opening of the gate, and now it accompanies its closure.

The tune is not a liar. It has not asserted anything on its own. Yet its history might contribute to the way an audience receives the words. To erase the melody's associations by decree would confuse the design of an interface with control over an interpreter's experience.

The interesting instrument is not a semantic synthesizer which claims to put an objectively correct meaning in a melody. It is a workshop for refitting inherited forms. A tune possesses a skeleton of pitches and times; a text possesses its own possibilities of articulation; a community supplies associations that neither score contains exhaustively. The workshop keeps these three domains separate.

Imagine a concert in which the operator can hear the score that would have been convenient for another text, but the singer cannot. The operator may transfer an accent to satisfy one speaker, knowing that the same change will remove a support from another. The original song is never recovered as an unqualified authority. Its persistence is a material constraint, not an ethical argument.

## 2. Source encounters and their boundaries

All reading below was by one AI assistant on 2026-11-26; no independent human screening, historical reconstruction, or empirical evidence appraisal. This is a non-systematic expedition, not a change to the frozen cutoff or evidence registry.

- Una McIlvenna, *The Power of Music: the Significance of Contrafactum in Execution Ballads*, Past & Present 229(1), 47–89 (2015), [Kent repository](https://kar.kent.ac.uk/54888/), Abstract, complete three-sentence abstract read; full article not retrieved. McIlvenna investigates the role of familiar tunes in framing news and accounts of punishment. Her later chapter, *The Significance of Contrafactum, or, How Melody Made Meaning*, in *Singing the News of Death* (2022), pp. 49–88, [publisher-indexed abstract](https://doi.org/10.1093/oso/9780197551851.003.0002), explicitly addresses the associations contributed by earlier songs. Direct publisher retrieval failed; indexed abstract only. These are author claims, not independently verified reconstructions of particular ballads. **Interpretation:** a borrowed tune can be more than economical packaging; it may supply a remembered context for the new words. The fictional gate is not an example from her historical corpus.
- Stefano Milonia and Matteo Mazzamurro, *Temporal networks of ‘Contrafacta’ in the first three troubadour generations*, Digital Scholarship in the Humanities 38(1), 240–256, online 2022, [Warwick repository](https://wrap.warwick.ac.uk/id/eprint/167218/), Abstract (all three paragraphs read), doi:10.1093/llc/fqac018. The authors model relations between lyricists through temporally annotated directed melody-borrowing edges. **Interpretation:** the same borrowing graph rendered without its dates may conceal the direction in which an association became available. Their nodes are authors' corpora, not acoustic signals, and their network is not the one below. No source data or centrality results independently assessed.
- Eron Smith, *Prosodic Dissonance*, Music Theory Online 30(2), June 2024, [HTML article](https://www.mtosmt.org/issues/mto.24.30.2/mto.24.30.2.smith.php), abstract and §§1.1–1.11 read; audio examples not auditioned. Smith treats clashes between linguistic and musical prosody as heterogeneous, context-dependent phenomena; §§1.4–1.6 note the multiple cues associated with stress, and §§1.7–1.9 discuss interactions across speech and song. **Interpretation:** an accent conflict is potentially an artistic resource, not merely a bad setting to correct. The gain-only accents below do not model the full set of cues or determine how a human will hear the lines.
- Kevin M. Ryan, *Syllable weight and natural duration in textsetting popular music in English*, English Language & Linguistics 26(3), 559–582 (2022), [publisher-indexed abstract](https://doi.org/10.1017/S1360674322000156). The author argues for distinguishing continuous natural duration from categorical weight in text setting, and for considering perceptual centres. Abstract only, no corpus or statistics inspected. **Counterposition to the fixture:** equal-duration cells and binary gain labels deliberately discard relevant linguistic variables.

These encounters do not establish a universal prosodic code. Familiarity may be absent, conflicting, learned in a different order, or deliberately resisted. No Brier endorsement is implied.

## 3. The accent budget (exact finite construction)

One six-cell instrumental melody is shared by four original text cards. Capitals mark **prescribed theatrical emphasis**, not measured or inevitable English stress. Every cell is one syllable and has identical duration; no speech is synthesized.

| Card | Cells 1–6 | Requested accent positions (1-based) |
|---|---|---|
| Keeper | KEEP / it / in / LET / it / rest | 1, 4 |
| Closure | the / GATE / is / still / LOCKED / now | 2, 5 |
| Opening | the / GATE / is / un / LOCKED / now | 2, 5 |
| Light | in / the / DARK / in / the / LIGHT | 3, 6 |

Opening and Closure are alternative asserted states of the same imagined gate, not commands or authorization. They have different words but identical authored accent requests. The three distinct request sets partition the six slots. The fixture uses six pitches (220, 275, 330, 294, 247, 220 Hz), each a quarter second, with 0.55 or 0.20 gain and a smooth envelope. Pitch contour and rhythmic grid are fixed; amplitude is the only changing synthesis control.

A score S contains exactly b accented positions. For request group G_i, define hits h_i = |S intersect G_i|. A reading is admitted in this game if h_i >= 1; extra accents are not penalized by that predicate. This is deliberately a weak compositional contract, not an intelligibility test. Full alignment instead requires S = G_i at budget 2.

With budget 2, each pair of distinct request groups has four mutually admissible scores (pick one of two positions from each). Yet no score admits all three groups: at least three distinct slots are necessary. This is a counterexample to interpreting separate pairwise compatibility as a simultaneous global guarantee. Raising budget to 3 yields eight all-admitting scores, one position from each pair. None fully aligns with any original two-accent template.

Generalization: let r disjoint groups each have s slots and cover the whole score. Any b-element accent mask distributes exactly b hits across groups. Its least hit count cannot exceed floor(b/r). Distribute b accents as evenly as possible, assigning floor(b/r) to every group and one additional hit to b mod r groups. Since 0 <= b <= rs this fits capacities, proving max_S min_i h_i = floor(b/r). For a threshold q in 0..s the global minimum budget is rq. A pair requires only 2q. No historical or perceptual premise is used in the proof; the mathematics is elementary pigeonhole reasoning.

A distinct claim concerns identity. The renderer is a function of the accent mask and fixed pitches, not text. Opening and Closure therefore yield identical PCM. A carrier-only decoder cannot identify which text card was assigned when those two cards are the only equiprobable possibilities: its maximum accuracy is one half under this restricted observation model. This says nothing about a listener who actually hears the words, observes the gate, or knows a different prior.

## 4. Original performance instruction: Six ceremonies for the same gate

1. Keeper: play the two accents at cells 1 and 4 while a reader performs its card.
2. Closure: replace accents with cells 2 and 5, then read the Closure card.
3. Opening: repeat the exact instrumental recording while the reader substitutes the Opening card. Neither tape nor oscillator acknowledges the change.
4. Light: select cells 3 and 6; use the Light card.
5. The negotiators: play accents at 1 and 2; let Keeper and Closure alternate. Light receives no requested accent. Then replace either negotiator with Light and repeat the negotiation with an appropriate new mask.
6. The new constitution: use accents at 1, 2 and 3. All three distinct requests receive one accent, but none receives its entire original pattern. Perform the three cards successively without reprogramming the accompaniment.

The recordings are instrumental carriers for the score, not performed recitations. The last movement's extra accent is not necessarily aesthetically worse. A further performance could retain an obsolete accent as an audible trace of the previous card, intentionally leaving the old allegiance in the music. Do not present the reader's changing words as information decoded from the instrumental audio.

## 5. Executed synthetic qualification

Run `python laboratory.py output-directory` with Python 3.11+ (standard library). Native Python 3.13.5 execution on 2026-11-26 passed: 5,036 masks across 63 group-size/budget cases, exact agreement with the proved max-min bound for r=2..4 and s=1..3. The specific three-group oracle verified [4,4,4] pair counts, zero simultaneous budget-2 solutions and eight budget-3 solutions. Six WAVs, 24,000 mono PCM frames each at 16 kHz, five unique SHA-256 values; the two gate recordings have the identical WAV SHA-256 f0476671884dbb955d52d15b7128b1aa50af46ae7c5dffaf3c3b050d3e89e2b8. Deterministic rerender, bounds, header and complete PCM readback, and out-of-range accent refusal passed. No human listening or speech production test. Local tested source Git blob be672a3871e1d5e18e3e663a333183f5773c6f58.

## 6. Design and experiment proposals (not implementation)

- **Contrafact Loom VSTi:** preserve a MIDI motif lane; attach multiple text or gesture tracks with explicitly edited prominence preferences. A budgeted accent router offers exact, pairwise, max-min, and intentional-conflict modes. Precompute small mask choices on control thread, pass an immutable pattern to the audio callback. Preserve the old track's accents on a second voice if desired. Report which preferences are unsatisfied without implying they are human needs.
- **Borrowed Tongue VSTfx:** take an incoming audio phrase, annotate boundaries manually, apply an envelope sequence without changing the source clip. Preserve dry playback and reveal the applied envelope. No claim to identify words or automatically infer stress.
- **CYD / FM-1:** a six-column, three-row accent matrix; XY controls accent budget and balance; display request coverage alongside the sound, not as a proxy for semantic success. A compact integer mask solver can enumerate 64 masks at the control rate; hardware feasibility untested.
- **Temporal provenance:** label a reused motif with its originating track, subsequent assigned contexts and versioned association graph. Permit concurrent contradictory artistic associations. An optional counter-melody performs unsatisfied accent requests.
- **MHAC test:** teach a fictional message vocabulary to authorized participants only after the actual human gate. Factor same vs changed melody, same vs contradictory explicit words, familiar vs unfamiliar motif, and congruent vs incongruent authored accents. Counterbalance exposure order and prior training; include explicit text-only and speech-only baselines, no-word carriers as a negative control, and independent task-state ground truth. Measure lexical recognition, state identification, action choice, confidence and latency separately. A text panel may entirely solve the operational problem. No advantage or confusion rate established.

A larger score with overlapping requests could have a different bound; a weighted or continuous accent budget is a different model. Global compatibility does not follow from the pairwise results, but neither does the example establish that all real message sets have this problem.

**Counterargument:** A familiar tune may be useful precisely because it acquires a new meaning, and prosodic clashes may be witty, expressive or memorable. Preserving the old text's accent map is not always desirable. The artistic control is the option to conserve, transfer or contradict it. Revise the operational hypothesis if ordinary explicit words dominate every tested condition, or if the specific mappings do not affect interpretation.

## Reconciliation and checkpoint

Base inspected: 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity and validation; reviewed recent 35 PR and 30 open issue titles, searched issue corpus for contrafactum, parody, accent, prosody, syllable and alternative topics. Closest leads: #382 (retrospective accent/metrical role), #514 (polyphonic syllable binding), #177 (affective feedback), #701 (poetic recurrence), #668 (delegated assertion). Distinction: text replacement on fixed melody, separately stipulated emphasis preferences, simultaneous resource feasibility rather than metric inference or role authentication. This is bounded overlap screening, not a novelty claim. Alternative tuning and homometry directions were abandoned after finding #286/#508 and #199. No shared manifest, protocol, canonical records or other worker's branch touched. No external human review, participant data, external submission, production firmware or licence grant. One ChatGPT assistant performed source reading, writing, code and native execution. No additional workers claimed. Independent review and exact-head CI remain required before landing; retain open issue and draft PR for integrator.
