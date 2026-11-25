# The Chord That Loses Its Pun
*Enharmonic ambiguity, poetic translation and the composition of equivalence.*

Exploratory humanities/art expedition, 2026-11-25; AI-authored and self-checked, no independent human reviewer. Not a finding in the frozen MHAC review, not a reconstruction of Brier, not a participant experiment.

## The translator's damaged hinge

A publisher buys a score containing a chord that can be interpreted as four different beginnings. The next edition is translated into another tuning. All four beginnings survive. But they no longer occupy the same sound.

The publisher has preserved the four grammatical possibilities and lost their coincidence. A second translator preserves the coincidence by using a single pitch collection for all four interpretations, but three of the newly named structures no longer conform to the target tuning's chosen interval grammar. A third invents a different chord with a comparable capacity for ambiguity. Who has translated the work?

This is not a question about which tuning is correct. It is a question about the object of fidelity. An instrument can make a distinction available, suppress it, or leave it latent until a subsequent gesture. A change of medium can alter that choice before any note is composed.

## Reading encounters (located claims, not a systematic review)

- **Roman Jakobson**, “On Linguistic Aspects of Translation” (1959), closing paragraphs in the English text reproduced in Simona Clerici's 2011 bilingual thesis, posted 2014: [text](https://www.trad.it/roman-jakobson-on-linguistic-aspects-of-translation-language-and-culture/). Read the English opening and closing passages; the Italian translation and full original edition were not independently collated. His example of the Italian translator/betrayer proverb distinguishes conveying its propositional content from carrying across its sound resemblance. His proposed creative transposition opens a possibility beyond word-for-word fidelity. It is his theoretical position, not a universal impossibility theorem.
- **Kristian Olesen Toft**, “Derrida and the exemplarity of literature,” *Orbis Litterarum* 79(1), 108–128, first published 24 August 2023, [DOI](https://doi.org/10.1111/oli.12421), §1 “This, for example,” opening discussion of Jakobson (citing Jakobson 1959, 128–131). Read those paragraphs. Toft challenges the clean separation of cognitive translation from poetic translation because even slight dependence on grammatical form complicates the distinction. This is an important objection to carving the world into unambiguous engineering and ambiguous art.
- **Bryn Hughes**, “Chromatic Modulation,” *Open Music Theory*, [chapter](https://viva.pressbooks.pub/openmusictheory/chapter/reinterpreting-augmented-sixth-chords/), section “Reinterpreting Diminished-Seventh Chords,” examples 14–15 and adjoining text. Read explanatory text, not the embedded scores/audio. Hughes explains the four possible root interpretations of a symmetric diminished-seventh chord and describes Beethoven's reinterpretation of a pitch collection between G minor and E minor. This is substantial existing musical practice, not an invention of this expedition.
- **Jonathan Wild**, “Genus, Species and Mode in Vicentino’s 31-tone Compositional Theory,” *Music Theory Online* 20(2), 2014, [article](https://mtosmt.org/issues/mto.14.20.2/mto.14.20.2.wild.php), paragraph 24 and abstract. Read the accessible text around the discussion of dividing whole tones and the archicembalo; no historical audio or primary treatise verification. Wild argues that the layout of keys informs Vicentino's theory of enharmonic subdivision. This is a historical reminder that available distinctions are partly material. The 31 equal divisions used below are a modern stipulated arithmetic model, not a reconstruction of Vicentino's particular tuning or genera.
- **Guangxu Zhao**, “Translating the Iconicity of Classical Chinese Poetry and its Significance for the Development of Digital Poetry and Digital Humanities,” 9 April 2026, pp. 117–133, [chapter](https://doi.org/10.1007/978-981-95-8844-2_6), §6.3, paragraphs discussing Xu Bing's *Book from the Sky* and John Cayley. Read these paragraphs and abstract. The discussion considers preserving the relation between apparent legibility and unreadability by creating different pseudo-writing in another script, rather than mechanically copying marks. This is the author's account of a proposed translation, not evidence that it succeeds with readers. It suggests our third translator may preserve the work's organizing tension by inventing a different sound-object.

## Interpretation: three fidelities

The pun is not simply two meanings attached to a sound. In the present construction, it is a relation between two distinct symbolic derivations that yield one pitch-class collection. Retuning is analogous to translating the shared material condition, not to translating a linguistic meaning. The analogy fails if we identify pitches with words, harmonic functions with propositions, or a mathematical collision with a listener's experience of wit.

There are at least three independent preservation objectives: (a) keep the spelled intervals and the four root labels; (b) keep the physical coincidence of the resulting pitch-class sets; (c) keep the artistic capacity for surprise. The first two can conflict under a specified rendering. The third is not a formal observable and might survive even when both others fail. It could be more compelling to hear a seemingly identical chord slowly reveal a small seam than to have it remain perfectly invariant.

A translator might also add ambiguity where none previously existed. The tuning is then not a neutral delivery channel but an editor of what distinctions can be performed. Nothing here establishes that equal temperament is inferior to meantone or that either tuning is culturally universal.

## Exact construction: a hinge with four leaves

Let N be the number of equal octave divisions, g a chosen fifth in steps, and s = (-3g) mod N the minor-third spelling derived by moving three fifths backwards. All pitches are modulo N. Let L=N/gcd(N,s) be the orbit length of the step s. Define the m-note collection A_r={(r+i)s mod N: 0<=i<m}, with 1<=m<=L. Root labels r here are indexes along the minor-third orbit, not absolute frequency or evidence of tonal function.

The map j -> js mod N is injective on Z_L. Consequently, for 0<=k<L, the intersection of A_0 with A_k has exactly
max(0,m-k) + max(0,m-(L-k))
members. Proof: rotate the interval [0,m-1] by k on Z_L; its nonwrapped portion and wrapped portion give the two disjoint intersection counts. In particular for m<L the only shift within this orbit preserving the entire set is zero; for m=L all L shifts preserve it. There are L distinct root-shifted sets in the proper-interval case and one in the full-orbit case. These are standard cyclic group arguments. They are not new mathematics.

For the four-note construction the stipulated fifths give:

| N | g | s | L | Four root candidates, distinct pitch sets | A_0 to A_1 substitutions |
|---:|---:|---:|---:|---:|---:|
| 12 | 7 | 3 | 4 | 1 | 0 |
| 19 | 11 | 5 | 19 | 4 | 1 |
| 31 | 18 | 8 | 31 | 4 | 1 |
| 24 | 14 | 6 | 4 | 1 | 0 |

In 19 and 31 divisions, the four candidate collections share progressively fewer pitches with the first: 4, 3, 2, 1. To advance from A_r to A_(r+1), preserve three pitches and replace rs with (r+4)s. For these two tunings the replacement is one tuning step upward in pitch-class space (1200/N cents), since 4s=N+1. If the same octave placement is chosen, this is a small single-voice motion, not a jump of an octave. Actual voice-leading distance depends on register. Four such replacements transpose the entire original collection by one step; in the 12/24 controls the sets remain identical. The 24 case defeats a naive claim that increased resolution alone must destroy the symmetry. In 16 divisions a four-step quarter-octave stack also has the symmetry, but it need not represent the same chosen fifth-derived interval.

This is a counterexample to preserving both these exact symbolic interval spellings and their full acoustic pitch-class coincidence under these particular tuning maps. It is not an impossibility result for all musical translations. No claim of human perceptual distinguishability, exact waveform equality across different voicings, or tonal function in microtonal harmony is made.

## Experiment and receipt

Run node oracle.cjs. It enumerates N=2..32, s=1..N-1, all lengths m<=L and every orbit shift k. Direct set intersection is compared against the formula, and counts of stabilizing shifts are checked. The four example tunings are checked independently. Executed the same function in a JavaScript isolate on 2026-11-25: 185742 shift cases, 388268 assertions passed. Native Node, entire repository tests and CI were not run in that execution. The function has no external dependencies. No measurement or human listening test was conducted.

## Exaptation: the Equivocation Oscillator

A prototype could keep a spelling coordinate distinct from its rendered pitch: fifth-chain index, octave, voice identity, articulation, tuning map. An ambiguity inspector groups derivations yielding the same target pitch-class multiset. A composer chooses a root interpretation without automatically retriggering notes; on changing tuning, a collision-split event can optionally retune the one replaced oscillator while holding the others. A split bus could drive a timbral difference even if the principal pitches remain equal. A convergence mode could restore equality with explicit retuning, and a reconstruction mode could search different pitch materials with the desired orbit/stabilizer size. Ordinary microtonal keyboards and MIDI pitch per note already make much of this technically possible; the proposed novelty is the explicit authoring of symbolic coincidence and its dissolution, not microtonality itself.

Do not use a generic pitch-class hash as proof of waveform identity: octave, phase, articulation, timbre, voice identity and effects are separate. For a first prototype, use a four-voice offline synth with explicit tuning presets, phase-continuous glide and independent audition. Retuning should not modify archived symbolic identities. Avoid interpreting a particular interval as a universally understood sign.

## The interface question and its rival

A machine might translate an informational vocabulary between acoustic realizations. A mapping that preserves all individual message identities might not preserve similarities, contrasts or context-dependent equivalences. Conversely an intentional artistic ambiguity may be unacceptable for an operational message. Separate the requirements, and do not use this pitch-class model to justify ambiguity in operational instructions. A future synthetic comparison could examine whether an explicit map of which cues merge and split improves operator predictions of how a renderer changes; compare to ordinary per-cue inspection, with complete binding accuracy and inspection time as outcomes. No participant work is authorized here. Conventional codebook tests may suffice; if they do, there is no special explanatory contribution from cybersemiotics.

## Reconciliation and boundaries

Read live AGENTS, RAG, README, programme, runbook, integrity and human-gates documents; recent 70 PR titles and 60 open issue results; targeted searches for pun, zeugma, polysemy, homophony, translation, enharmonic, temperament, tuning, pivot chord and diminished. #286 studies sequential tuning drift and resets; #358 rhythmic translation; #178 observational aliasing; #471 contingency rules. Here the object is static tuning-dependent symmetry and deliberate artistic preservation or destruction of a collision, with sequential motion as a performance consequence. Search is bounded, not a proof of novelty. Base main 495a98ca12bae467a507031f04931aa4254b1866. Only this expedition directory is owned. No protocol, claim register, shared index, licensing, external outreach or human gate changes. Draft review, not central acceptance.

See [SCORE.md](SCORE.md) for an original performance instruction and [oracle.cjs](oracle.cjs) for the exact finite model.
