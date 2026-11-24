# The Sentence That Changes Its Skeleton
*Anacoluthon, musical interruption and the afterlife of an abandoned phrase*

Exploratory expedition, 2026-11-24, [issue #366](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/366). Original interpretation and artistic research, not a selected Track E/G extraction, a protocol amendment, or a validated machine-warning design.

## Contents

1. [The unfinished sentence](#1-the-unfinished-sentence-is-not-necessarily-a-failed-sentence) — broken grammar versus successful redirection.
2. [Four ways to leave a phrase](#2-four-ways-to-leave-a-phrase) — interruption, resumption, revision and refunctioning.
3. [Historical detour](#3-historical-detour-a-musical-sentence-that-stops) — musical rhetoric and the counterposition from disfluency research.
4. [Finite construction and audio experiment](#4-a-finite-construction-and-a-small-audio-experiment) — invariant canonical phrase and distinguishable editorial histories.
5. [The Anacoluthon Console](#5-exaptation-the-anacoluthon-console) — design proposal and future falsification.
6. [Source notes and reconciliation](#6-source-notes-and-scope-reconciliation) — provenance, scope and limitations.

## 1. The unfinished sentence is not necessarily a failed sentence

A speaker begins: "When the last oscillator has—listen, the casing is singing." The initial subordinate clause does not receive its expected completion. The new imperative is not its grammatical continuation. Yet something has been accomplished: the speaker redirects attention from an explanation to a phenomenon. A fluent replacement ("Listen to the casing") might convey the request while erasing the change of direction.

This is an invented example of anacoluthon, not a transcript. The critical distinction is between a broken construction, an incorrect proposition and a deliberate change of communicative purpose. They may coincide but need not. The linguistic structure can fail to complete while the encounter succeeds.

The interesting musical equivalent would not be just a wrong note. It would be a phrase that begins under one organizing rule and whose continuation belongs to another. The listener might retain the first organization as an unfulfilled possibility even while following the second. That is an aesthetic hypothesis, not a demonstrated psychological mechanism.

Classical rhetoric is a useful corrective to the assumption that departures from smooth delivery are uniformly defects. Quintilian distinguishes a break employed for affect, hesitation or transition from a self-interruption that terminates before the usual ending but does not actually leave the construction unfinished (S1). In other words, a useful taxonomy already distinguishes what sounds discontinuous from what is structurally incomplete. Gildenhard's glossary supplies a more specific grammatical term, anacoluthon (S2). The categories overlap in some examples; they should not be treated as synonyms.

An instrument can simulate a broken sentence without simulating a worried person. It might also be a mistake to make a machine continually perform hesitation: a fictional rhetorical stance can be interesting in a composition without being informative in an interface.

## 2. Four ways to leave a phrase

| Operation | What the score specifies | What cannot be inferred |
| --- | --- | --- |
| Interrupt | A phrase stops before its anticipated completion | Why it stopped, or whether an error occurred |
| Resume | Material is continued under the original rule | Whether the listener maintained the first interpretation |
| Revise | A designated earlier fragment is superseded | Whether the listener heard the correction |
| Refunction | The superseded fragment becomes material in another layer | Whether the original interpretation disappears |

The last operation motivates this expedition. Call it **revision counterpoint**. The abandoned material no longer contributes to the canonical sequence but participates as accompaniment. Instead of treating a composer's failed attempt as disposable, retain it as the other voice of the composition.

There is an important distinction from an undo feature: an undo can restore a representation, but the earlier acoustic event is already part of the performance. This expedition does not propose making a withdrawn instruction actionable again. Its source material is entirely nonsemantic tones. For actual directives the existing #56 investigation handles irreversible action and uncertainty about receipt; #33 handles recipient-initiated repair. Neither lifecycle is being reimplemented here.

A repair may itself fail. An explicit repair marker may be missed or bind to the wrong fragment. Even when repair succeeds, the fact that it occurred can remain part of the listener's experience. Schegloff, Jefferson and Sacks distinguish the organization of conversational repair from a generic demand for perfect grammar (S3). Their abstract describes a preference for self-repair; that is not a requirement that a machine anthropomorphically apologize.

## 3. Historical detour: a musical sentence that stops

Leon W. Couch III analyzes notated interruption in Buxtehude's F-sharp-minor praeludium (S4). In his discussion, a general silence at measure 24 exemplifies aposiopesis, while later interruptions are discussed under abruptio. Couch locates these devices in the history of musica poetica, a tradition in which rhetorical ideas helped articulate musical composition. This is a secondary interpretation of the work, not independent analysis of the score or a claim to have read Burmeister's original treatise.

The interesting historical inversion: rhetoric and musical rhetoric often used discontinuity as part of persuasive expression. MHAC seeks intelligible nonhuman speech without dependence on simulated emotion. We can borrow the separation of structural functions without inheriting a code in which a particular interruption must stand for grief, fear or anger.

An unfinished musical gesture need not be a sign of malfunction. Conversely, an actual malfunction need not be a musical gesture. A listener cannot settle that distinction by waveform alone unless a communication convention and adequate contextual evidence make it available.

**Counterposition:** Brennan and Schober report four visual-selection experiments in which some spoken disfluencies helped listeners handle misleading information rather than merely interfering (S5). Their reported timing is relative to the target word; this is not an assertion of lower total instruction time. The abstract does not establish that electronic pips convey repair, nor does it cover our synthetic tones. The insight is a question generator: under what conditions does making a revision audible assist a listener, and when does it merely add cognitive work?

## 4. A finite construction and a small audio experiment

The score has two independent channels: a canonical lane L and an editorial lane R. Eight equal 300-ms slots are used in each recording. Slots 5–8 on L always contain 330, 392, 294, 220 Hz. The first four slots either contain silence or an abandoned two-tone motif. An 880-Hz tone in slot 3 on R is a stipulated editorial boundary; it is not assumed intuitively meaningful.

| Recording | L slots 1–4 | R slot 3 | R slots 5–8 |
| --- | --- | --- | --- |
| 01 clean | silence | silence | silence |
| 02 interrupt | 220, 277, rest, rest | silence | silence |
| 03 repair | 220, 277, rest, rest | 880 | silence |
| 04 revision A | 220, 277, rest, rest | 880 | 220, 277, 220, 277 |
| 05 revision B | 440, 349, rest, rest | 880 | 440, 349, 440, 349 |

Other R slots are silent. All material is original. These are scored discontinuities between complete enveloped notes, not literal mid-phoneme or mid-waveform cutoffs. The synthetic marker is not equivalent to a human hesitation or grammatical correction.

The canonical projection takes only the last four slots on L. It is intentionally many-to-one. For example, recordings 04 and 05 share exactly the same canonical projection and boundary signal, yet the editorial lane identifies different abandoned motifs within this artificial codebook. No decoder of the canonical suffix alone can recover which of these two motifs was abandoned. That follows directly from equality of the inputs to the decoder, and is a statement about digital samples rather than human interpretation.

A second distinction concerns scope: the unmarked sequence A; B could mean concatenate A and B, or discard A and retain B. The raw ordered symbols are identical. Without an independently established grammar, neither interpretation follows uniquely from those symbols. A revision marker does not generally settle scope either; a marker that means retract the last token differs from a marker that means retract the whole clause. This is a finite semantic counterexample, not a model of natural-language comprehension.

The standard-library renderer [render.py](render.py) produced five stereo 16-bit PCM WAVs at 24 kHz (57,600 frames per recording; duration 2.4 s). Qualification verified repeated PCM generation, sample bounds, reopened headers and exact sample payload, 28,800 identical final L frames across all conditions, and targeted intervention controls. The same-environment check does not assert bitwise portability across floating-point platforms. See [RECEIPTS.md](RECEIPTS.md). No physical playback or listener study was performed.

The interesting compositional result is not that the recordings sound alike. Their full waveforms are intentionally different. It is that an arrangement can preserve a strictly identical chosen canonical layer while making incompatible histories independently audible.

## 5. Exaptation: the Anacoluthon Console

Build a small performance instrument with a provisional phrase buffer, a committed phrase lane, a revision-boundary cue and an abandoned-material bus. A performer presses BEGIN, plays an incomplete figure, then chooses RESUME, REPLACE, or REFUNCTION. The final control transfers the old figure to an independently gated accompaniment lane, transposed or stretched but still traceable to its source phrase.

The instrument could expose:
- scope: note, phrase or section, shown explicitly rather than inferred from a generic undo;
- disposition: discard, retain as silent history, or refunction as accompaniment;
- persistence: finite time-to-live, decaying gain, manual release;
- editorial visibility: no cue, explicit arbitrary cue, or visible textual annotation;
- material transform: reverse, resample, filter, reharmonize; the original history remains distinguishable from the derived material.

The artistic objective is not to maximize the number of audible mistakes. It is to let the performer manipulate the relationship between a revision and the material revised. A careless design produces mere clutter. A useful one should allow the editorial layer to be muted, separately soloed and deliberately reintroduced.

**Hypothesis for a later, authorized noncritical interface study:** an explicit scope-bound correction annotation may help distinguish concatenation from replacement in unfamiliar synthetic messages. Compare (i) clean message, (ii) interruption without cue, (iii) interruption with an arbitrary trained cue, (iv) spoken or textual scope cue. Match message content and control cue duration, loudness, timing and training; collect final interpretation, recognition of the abandoned information, total completion time and false acceptance. A cue-only control should test whether participants are relying on the marker instead of the content. Reject the proposal if added cues confuse scope or impose excessive delay, or if simpler unambiguous phrasing performs as well. No human participants, alert deployment or adopted protocol in this expedition.

## 6. Source notes and scope reconciliation

All readings accessed 2026-11-24 by a single ChatGPT agent using public web pages. Access and reading extent listed below; no independent reviewer. Source claims are limited to the cited passages and abstracts; this is not a systematic literature review. No restricted full texts were copied into the repo.

| ID | Source and locator | Reading and claim boundary |
| --- | --- | --- |
| S1 | Quintilian, *Institutio Oratoria*, IX.2.54–57, [English HTML transcription](https://technorhetoric.net/stasis/2017/honeycutt/quintilian/9/chapter2.html) | Read §§54–57, not Latin original or entire book. §54 describes affect and hesitation; §55 transition; §57 distinguishes a related form of self-interruption. |
| S2 | Ingo Gildenhard, [Rhetorical Terms](https://dcc.dickinson.edu/es/cicero-verres/rhetorical-terms), Dickinson College Commentaries, entry “anacoluthon” | Read glossary entry, not whole commentary; grammatical discontinuity and mid-sentence change. |
| S3 | Emanuel A. Schegloff, Gail Jefferson, Harvey Sacks (1977), *The Preference for Self-Correction in the Organization of Repair in Conversation*, Language 53(2), 361–382, [publisher](https://doi.org/10.2307/413107), abstract; [ISCA media archive](https://www.conversationanalysis.org/schegloff-media-archive/preference-for-self-correction-in-repair-in-conversation-1977/) | Abstract and archive index only, not full conversation corpus or audio clips. Reports preference for self-repair; no quantified effect extracted. |
| S4 | Leon W. Couch III, [Musical Rhetoric in Three Praeludia of Dietrich Buxtehude](https://www.thediapason.com/content/musical-rhetoric-three-praeludia-dietrich-buxtehude), sections Joachim Burmeister (paragraph on aposiopesis) and Christoph Bernhard (paragraph on abruptio) | Read relevant HTML prose; not original treatise, score or diagrams. Secondary interpretive account; its birth/death year line for Burmeister is visibly inconsistent, so no biography copied. |
| S5 | Susan E. Brennan, Michael F. Schober (2001), *How Listeners Compensate for Disfluencies in Spontaneous Speech*, JML 44(2), 274–296, [DOI](https://doi.org/10.1006/jmla.2000.2753), [institutional abstract](https://researchconnect.suny.edu/en/publications/how-listeners-compensate-for-disfluencies-in-spontaneous-speech/) | Abstract only; source-reported comparison of fluent/disfluent selection instructions and pauses. No effect sizes, full methods appraisal, or transfer established. |

Reconciled live main at 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, README, programme, runbook, integrity and validation authorities read. Searched 100 requested recent PR results and 60 open issue results plus focused terms (anacoluthon, self-repair, false start, speech repair, palinode). No matching anacoluthon expedition found; not proof of global novelty. Read #33 and #56 complete issue bodies for overlap. The prior rest, aspect, genre and meter expeditions overlap with silence, contextual hearing, retrospective framing and recomposition respectively; this contribution isolates the artistic refunctioning of a fragment withdrawn from the canonical sequence. Issue #366 and its empty comment list were fetched before edits. No shared manifest, canonical registry, frozen protocol or prior branch changed. Draft intended for coordinated integration; local mechanical qualification does not substitute for repository CI.

The [original text score](SCORE.md) deliberately leaves the final question undecided: must a discarded phrase become accompaniment, or is its right to disappear equally important?
