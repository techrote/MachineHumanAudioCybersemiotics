# The Machine That Borrows Its Body

Foley, audiovisual contracts and fictional causality — exploratory expedition #556, 25 November 2026. Draft/HOLD; not part of the frozen evidence registry.

## Contents

1. Essay — fictional bodies for an invariant sound.
2. Source encounters — film sound, ecology and audiovisual timing.
3. Relations — provenance, depiction, alignment and causality.
4. Apparatus — reproducible audiovisual score and qualification.
5. Exaptation — creative instrument and falsifiable interface questions.
6. Reconciliation — overlap checks and outstanding gates.

## 1. Essay: a machine without a surface

Imagine a machine whose sound is entirely synthetic. Its display shows a brass lever moving downwards whenever a short resonant impact sounds. Next it displays a ball landing on a plate. Nothing in the audio renderer changes. Eventually the display goes blank, but the impacts continue.

The machine has not acquired three physical bodies. It has acquired three possible fictional explanations for the same sound.

A Foley performer does not need to manufacture the depicted event. They manufacture material that can participate in its depiction. This is a valuable artistic distinction: resemblance, synchrony and causality may coincide in a finished film without having been identical throughout its making. A footstep can be faithful to a character's gait without being a recording of that character's foot. There is no contradiction if the work is a fiction and the relation is appropriately understood.

A machine interface is not necessarily a fiction, however. Its users may need to distinguish a recorded physical event from a generated announcement. The same strategies that make a fictional world coherent can produce inappropriate causal implications if presented as evidence of a real event. An elegant animated impact is not a second independent witness to the event reported by a synthetic impact sound.

I propose **body scoring**: independent authoring of the visible action through which an otherwise fixed acoustic object is presented. Instead of composing the noise of a lever, the artist composes a lever for a noise. The body can subsequently be replaced, delayed, partially removed or left unspecified.

This is not an argument that the source of a sound never matters. If the sound actually records a physical event, that provenance may be indispensable. Nor is it an argument that all visual substitutions are persuasive. A stubborn, conspicuously unsuitable sound may be the most interesting composition.

## 2. Source-located encounters

All sources below were consulted by a single AI research worker on 2026-11-25. Access/reading extent is recorded separately from interpretation; no independent reviewer or participant evidence.

- **Michel Chion, Audio-Vision, audiovisual contract.** [Edited excerpt at FilmSound.org](https://www.filmsound.org/chion/av-contr.htm), heading and two paragraphs immediately before the attribution. Chion characterizes the sound-image relationship as an accepted representational pact, with each channel altering the experience of the other. Access: edited excerpt, not the complete book or a verified page of the print edition. Interpretation: a body can be authored as part of a sound's presentation rather than discovered in its physical provenance. Do not elevate this to a universal perceptual law.
- **ACMI, Foley Sound.** [Museum educational resource](https://www.acmi.net.au/education/school-program-and-resources/foley-sound/), section Discover Foley sound, first three prose paragraphs after the embedded video. The museum explains synchronized post-production effects produced using ordinary objects. Access: selected HTML text, video not watched. Interpretation: depicted and recording-source materials need not coincide.
- **Daniel Urban (2019), What exactly is Foley Art?** [SCHIRN magazine, 30 July 2019](https://www.schirn.de/en/schirnmag/foley-art-sounds-art-in-films-big-orchestra-big-orchestra-2019-context-en/), section A Foley artist's studio is rather like an older child's play den, especially the paragraph beginning with cinematic versus real sounds and giving starch and coconut-shell examples. Read selected article passages, not the embedded documentary. This is arts journalism and an account of craft, not controlled evidence that these effects persuade everyone. The article's broader history and perceptual generalizations are not independently verified here.
- **Geoffrey Cox (2017), There Must Be a Poetry of Sound That None of Us Knows…, Organised Sound 22(2), 172–186.** [DOI](https://doi.org/10.1017/S1355771817000085), sections 1 and 5.1–5.2. Cox situates early British documentary sound alongside musique concrète and discusses the 1928 Soviet directors' argument for audiovisual counterpoint. Access: selected publisher HTML sections, not the original manifesto or films. His introduction explicitly avoids a simple direct-influence story. Interpretation: noncoincidence can be the aesthetic purpose, not a synchronization fault.
- **William W. Gaver (1993), What in the World Do We Hear?, Ecological Psychology 5(1).** [Institutional publication record](https://researchportal.northumbria.ac.uk/en/publications/what-in-the-world-do-we-hear-an-ecological-approach-to-auditory-e/), abstract; publisher retrieval returned 403. Gaver organizes everyday listening around audible events and material interactions. Counterposition: a sound may constrain its plausible depictions through physical information. A body-scoring editor cannot assume acoustic material is arbitrarily interchangeable.
- **Jean Vroomen and Beatrice de Gelder (2004), Temporal ventriloquism: sound modulates the flash-lag effect, JEP:HPP 30(3), 513–518.** [PubMed record](https://pubmed.ncbi.nlm.nih.gov/15161383/), abstract, Experiments 1 and 2. Reports changes in a visual timing illusion with nearby sound and varied sound timing. Abstract only; methods and effect sizes not independently appraised. The study does not establish the timing tolerance for this artwork, attribution to a mechanical source, or machine-interface effectiveness. The ±300 ms editor range is artistic, not derived from a perceptual threshold.

## 3. Four independent relations

| Relation | Question | Apparatus example |
|---|---|---|
| Material provenance | What physically or computationally generated the signal? | Deterministic synthetic impact generator |
| Depicted event | What occurrence does the scene portray? | Lever, sphere or shutter motion |
| Presentation alignment | Which events are authored to coincide? | Independently scheduled visual contact markers |
| Actual causal relation | Did the depicted event generate the audio? | No; both are driven by a score, with separate rendering |

A fifth relation, the listener's attribution, remains unmeasured. It must not be inferred from the four authored relations.

The original soundtrack uses six onset times in seconds: 0.75, 1.50, 2.50, 3.25, 4.50, 5.25. Every body except the absent body presents a visual action at those times plus the selected lag, excluding an optional omitted contact. Let A be the fixed onset set and V be the resulting visual schedule. For zero lag and no omission, A=V. This equality does not imply that either schedule causes the other: the implementation uses a common authored schedule. At nonzero lag or with omission, the audio buffer remains unchanged.

The counterexample is deliberately mundane. Synchronous output is insufficient evidence of independent physical corroboration when both channels share a renderer or data source. Conversely, noncoincidence does not prove a hardware fault: intentionally asynchronous art, real propagation delays, distinct sampling clocks and display latency are alternatives.

## 4. Executable artistic apparatus

Save [index.html](index.html) locally and open in a current desktop browser. No build, server, third-party assets or network are required. Play initiates a single 6.5-second audio buffer; Stop cancels it. Select lever, ball, shutter or absent body; vary visual lag from −300 to +300 ms; optionally omit a contact. Restart applies the selection. The WAV export saves the invariant mono soundtrack.

The stage is deliberately abstract. Contact times are intended animation maxima, not sensor measurements. The small timeline exposes the scheduled discrepancy; it is not an independent clock or proof of actual device latency. Browser audio/display timing has not been measured. The abstract stage and its timing tracks were visually inspected in headless Chromium screenshots. Sound is two damped sinusoids and short deterministic noise bursts, not a physical model of any depicted object.

The model was run in a JavaScript execution environment prior to commit: 156,000 mono PCM frames at 24 kHz, peak integer magnitude 15,704, 50,042 nonzero samples, word-wise FNV-style checksum 8c880489 (noncryptographic, not a WAV hash). 262,425 assertions passed: repeat generation, silence outside scheduled support, contact count/order/range across 140 scenes, amplitude and malformed scene rejection. The same model is embedded in the HTML; a Node reproduction script [check.cjs](check.cjs) extracts it. Native Node v22.16.0 reproduced the exact result using the two Git-blob-matched files. Headless Chromium 144.0.7559.96 exercised all four bodies, stop/restart, natural completion and four WAV exports; all exports were byte-identical and their PCM headers passed Python wave readback. The browser was muted, and no physical latency or auditory experience was measured. See [RECEIPT.md](RECEIPT.md). The 140 scenes are four modes × five representative offsets × seven omission settings, not the full slider domain or independent human observations.

## 5. Exaptation and rival explanations

A body-score instrument could support independent sound and animated contact tracks, interchangeable material skins, gesture-to-envelope mappings and a visible link mode (shared score versus physical event). In artistic mode, an oscillator might borrow the motion of a virtual hinge until the performer detaches them. A whole orchestra could share a single sound palette while their visible bodies follow mutually incompatible fictional mechanical lives.

In an operational MHAC interface the direction is different. Do not use invented motion as evidence of physical activity. Separate measured event, declared machine state, synthesized representation and optional illustration. A shared underlying event ID establishes software lineage, not independent verification. Actual instrumentation and its limitations determine what can be asserted. The body score is not a replacement for ordinary status text, event logs or device feedback.

Future research question: does a depicted causal action change a viewer's attribution of a fixed synthetic sound relative to sound-only, correctly labelled animation and unrelated animation? A separate condition would present explicitly independent evidence rather than a common renderer. Assess event identification, provenance discrimination, confidence calibration and task costs; use benign fictional scenes only unless an approved protocol authorizes more. Counterbalance order, measure output timing, and avoid collecting participants in this expedition. An ordinary explicit label may outperform all animations. Gaver's account offers a competing hypothesis that material acoustics restrict reinterpretation; a null result or dominance of the sound itself would be informative.

The prior-art subtraction is substantial: film sound, Foley, audiovisual installation and ordinary animation timelines already provide the mechanisms. The contribution is an artistic authoring proposal and a scoped question about representational provenance, not a new theory of multisensory integration.

## 6. Reconciliation, limitations and handoff

Read live AGENTS, README, RAG, programme, runbook, integrity and validation; inspected 65 requested recent PR results (60 returned) and 40 open issue search results. Base main 495a98ca12bae467a507031f04931aa4254b1866. Initial palindrome/chiasmus direction abandoned after #188 and #340 overlap; meter direction abandoned after #382. Targeted searches for Foley, Chion, synchresis, acousmatic listening and source bonding found #230 as closest source-allocation predecessor. Read #230, #471 and #530 issue bodies and comments. Their formal targets differ: additive partition, cue response and anonymous temporal association respectively. This project instead varies depicted bodies with one fixed waveform, and does not claim a new association theorem. #548 concerns discarded signals, not fictional depiction. New issue #556 and its comments were checked before writing.

Five files in this isolated directory; no canonical records, manifests, licenses or protocol changes. [SCORE.md](SCORE.md) is original unperformed artistic material. AI authored the apparatus and source notes, performed the reported finite checks and self-review. No independent reviewer, physical listening, full repository validation, CI or empirical effects are asserted. Draft for integration; no merge until exact-head checks and review requirements are met.
