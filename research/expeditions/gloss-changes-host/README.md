# The Gloss That Changes Its Host

**MHAC exploratory expedition #709 — 26 November 2026.** Original speculative essay, elementary finite construction, and performance score. Outside the frozen Track E/G corpus and all promoted claims. AI-assisted research and implementation by one ChatGPT agent; no independent human review.

## A manuscript for two identical bells

A copyist adds a small warning beside the second occurrence of a bell in a score. The next edition moves its phrases and replaces one of the notes around each bell. A computer is asked to restore the warning. It finds a perfectly matching quotation in the new edition. Unfortunately it belongs to the other bell.

The interesting failure is not lost text. The marginal inscription survives word for word, the melody survives almost entirely, and an exact textual match exists. The relationship between inscription and host has changed.

Imagine an instrument whose composer can move a commentary between passages, rather than merely change the contents of the commentary. What was originally written to the first bell becomes audible beside its successor, its imitation, or its antagonist. A musician might deliberately compose these migrations. A curator, by contrast, might need to preserve the old attachment or mark it as uncertain.

I propose an independent musical parameter: **the persistence policy of an annotation**. Does it follow an event's identity, its location, a recognizable motif, the passage's function, or the annotator's changing intention? These are distinct commitments. In a digital system an identity may be explicitly assigned and maintained, but no identifier tells us on its own whether the old advice still makes sense after an edit.

A warning could remain correctly attached to a passage whose difficulty has disappeared. A newly relevant warning could be assigned to another passage with complete artistic justification. A perfectly faithful reattachment and a useful reinterpretation are not synonyms.

## Source encounters (not a systematic review)

- British Library, [Add MS 8091, Gospel of St John with glosses](https://searcharchives.bl.uk/catalog/032-002029098), catalogue record, **Scope & Content**, **Contents**, **Date Range**. Read these fields on 2026-11-26. The early twelfth-century manuscript includes commentary beside and between lines of biblical text; the catalogue also connects the present codex to a larger earlier manuscript via foliation. No folio images or Latin transcription were read. Interpretation: a text can be physically distributed across several layers, and evidence of an earlier ordering need not be identical with present placement. This is not a claim that medieval scribes used the proposed algorithm.
- Emily Payne and Floris Schuiling (2017), [The Textility of Marking: Performers’ Annotations as Indicators of the Creative Process in Performance](https://doi.org/10.1093/ml/gcx055), Music & Letters 98(3), 438–464. [Accepted version](https://eprints.whiterose.ac.uk/id/eprint/113067/1/Main%20Document%20v2.3.pdf), abstract, selected passages of Case study 1, accepted manuscript internal pp. 13, 16–18 (pagination flagged as incorrect for the version of record; PDF index 16 visually inspected, corresponding to printed 16). The authors describe fingering reminders and graphic reinterpretations in rehearsals on a less familiar basset clarinet, treating marks as part of creative and bodily engagement. The authors' observations are theirs, not ours. Figures and complete article not examined; publisher abstract corroborated bibliographic identity. Interpretation: musical annotations can be temporary aids, not permanent attributes of notes. Mechanical relocation cannot decide when a reminder has ceased to be useful.
- W3C, [Web Annotation Data Model](https://www.w3.org/TR/annotation-model/), Recommendation, 23 February 2017, §1, §§4.2.4–4.2.5. Read relevant paragraphs. The standard separates body and target; quote selectors retain selected text with surrounding context, and position selectors use offsets. It explicitly allows multiple matches for a quote selector and notes the fragility of positional selectors under editing. This is direct technical prior art, not a new annotation standard. Our single-choice experimental exact policy is deliberately narrower than W3C's multi-target handling.
- A.J. Brush and David Bargeron (2001), [Robustly Anchoring Annotations Using Keywords](https://www.microsoft.com/en-us/research/publication/robustly-anchoring-annotations-using-keywords/), MSR-TR-2001-107, November 2001, publisher-hosted abstract. The authors describe tracking distinguishing nearby words through document revision, motivated by their user studies. The report body, experiments and algorithm were not inspected; no quantitative performance claims imported. Their prior art makes it especially important not to present context matching as a new invention.

All reading by the same agent. Metadata and passages inspected as stated; no independent translation, source fidelity review, participant access, external contact or rights grant. Only original analysis and ordinary bibliographic references retained.

### Interpretive disagreement

The library catalogue reconstructs an object through surviving physical clues. The performer may need an annotation precisely while a gesture is unfamiliar, and may later remove it. The web standard represents associations in a transferable form. The engineer attempts to move a mark through a changed document. None of these activities fixes a universally correct definition of what the mark is for.

The gloss is not necessarily subordinate to a final text. It can be an instrument for changing the text's performance. A copied fingering reminder might teach the wrong movement on a retuned instrument; a wrong musical attachment could be a deliberate compositional device. The software must distinguish historical attachment from a decision to adopt the mark elsewhere.

## Exact synthetic model: two hosts, one annotation

Two persistent identities A (annotated) and B (unannotated) each carry a binary context of length n. These represent authored musical cells, not acoustic features inferred from recordings. Both contexts are distinct initially, with Hamming separation d. The central event to which the gloss is attached is identical in both phrases.

A revision substitutes at most t bits independently in each context; both events survive exactly once. The revised fragments may be reordered; persistent IDs and edit history are hidden. There are no insertions, deletions, copies, merges or pitch recognition errors. The task is to restore the attachment to A. This is identity tracking under stipulated provenance, not semantic relevance or a model of human reading.

Four policies:
- Exact: select a unique fragment matching A's old context exactly, else abstain.
- Nearest: select a unique fragment minimizing Hamming distance from A's context, else abstain.
- Bounded: select a unique fragment compatible with A's context and t, else abstain.
- Joint: retain both old contexts, admit the two possible bijections only if every assigned fragment is within t of its old context, then select A only when exactly one bijection is admitted.

Example with one permitted edit: old A=00000, B=10000; revised slots X=01000, Y=00000. The unique exact match is Y, but it descends from B. Nearest also selects Y. Both are compatible with A, so bounded abstains. Joint assigns X to A and Y to B, because X is two edits from B. Identical carrier quotation is insufficient even for a unique match.

Now old A=00000, B=11000; revised X=10000, Y=01000. Each observation lies one edit from both old contexts. Both possible histories satisfy the same contract and yield exactly the same revised contents. Joint abstains. No content-only deterministic decision is guaranteed to recover the hidden identity on both histories.

### Counting the price of keeping the other context

Write H(A,t) for the Hamming ball around A. Its volume V=sum(k=0..t) binomial(n,k). Define I=|H(A,t) intersect H(B,t)|. The experiment counts every pair of independently revised contexts x in H(A,t), y in H(B,t), and both possible display orders. These are labelled worlds, not distinct observed arrays and not an empirical probability distribution.

There are W=2 V^2 worlds. Bounded abstains iff y is also within the old A ball, giving 2VI abstentions. Joint abstains iff both fragments belong to the intersection, giving 2I^2 abstentions. Both policies never select the wrong identity under the stipulated bound, because the true assignment is always admitted. Joint ambiguity is a subset of bounded ambiguity.

The intersection is nonempty exactly when d <= 2t: the triangle inequality proves necessity; splitting the differing coordinates between the two centres proves sufficiency. Thus d > 2t guarantees unique attachment, even for anchor-only bounded matching. At d <= 2t, a common midpoint can occupy both fragments or both feasible assignments can be exchanged, so no universally correct forced selector exists. This is ordinary Hamming-ball geometry, not a new coding-theory theorem.

Under uniform counting of worlds, bounded abstention fraction is I/V and joint is (I/V)^2. No statistical inference about real edits follows. The strict improvement when 0<I<V is purchased by retaining a record of the *other* fragment. Information about what the gloss was not attached to can help preserve where it was attached.

The exact policy gives a false unique match in 2(V-1) worlds if d<=t; the distractor can become A while A changes away from its old context. Otherwise there are no such false exact matches in this model. Nearest has no special identity authority simply because a distance is smaller.

| n=5, t=1, d=1 | Correct | Wrong | Abstain |
|---|---:|---:|---:|
| Exact | 10 | 10 | 52 |
| Nearest | 50 | 10 | 12 |
| Bounded | 48 | 0 | 24 |
| Joint | 64 | 0 | 8 |

At d=2, t=1, V=6 and I=2 also, but nearest gives 52 correct, 0 wrong, 20 abstentions. At d=3, t=1, I=0; both bounded and joint are uniquely correct in all 72 worlds. Exact still abstains in 60.

**Limits:** a violated edit budget can break the guarantee; the negative control replaces both original contexts 000 and 111 by each other's content, exceeding t=1. A unique bounded match is then wrong. Persistent identifiers and a verified edit map, when legitimately available, solve the narrower tracking problem without pattern matching. They do not solve whether an annotation should still apply. General many-fragment assignment needs explicit handling of insertion, deletion and duplication, not a forced permutation. Nothing here is a perceptual or linguistic model.

## Original score: Six Rebindings of a Marginal Bell

For two electronic musicians. A performs the principal score in the left channel: five equal cells of 220 Hz (0) or 330 Hz (1), followed by a 440 Hz bell, then a 200 ms rest before the second phrase. Every cell lasts 200 ms. B performs the marginal gloss on the right channel: 660 then 880 Hz, each 100 ms, simultaneous with the bell it is attached to. All events have squared-sine envelopes; B may withhold the gloss entirely. The marker has no natural semantic interpretation.

| Movement | Principal fragments | Gloss location |
|---|---|---|
| I. Ink | 00000 / 10000 | First bell |
| II. Exact quotation | 01000 / 00000 | Second bell (false attachment in the stipulated history) |
| III. Remembering the other | 01000 / 00000 | First bell (unique joint solution) |
| IV. The first possible history | 10000 / 01000 | First bell |
| V. The second possible history | 10000 / 01000 | Second bell |
| VI. Unassigned | 10000 / 01000 | None |

In IV–VI the stipulated originals are 00000 and 11000. The first two versions enact alternative possible histories, not validated guesses. The third is an abstention. During live performance, a curator may display both possible histories on paper without performing either gloss. In a second run, a poet may explicitly choose the wrong attachment as an artistic act. Label it adoption rather than recovery.

Rendered offline using render.py; all six recordings are original 16 kHz stereo PCM16, 41,600 frames, 2.6 seconds. II and III have identical left PCM and different right PCM. IV, V, VI share identical left PCM; VI has no right-channel sound. No recording contains human speech or evidence of a listener's understanding. The accompanying WAVs are generated locally rather than added as binary repository objects.

### Second rabbit hole: the annotation that acquires a biography

Suppose a score annotation has an expiry predicate. A reminder about an unfamiliar key becomes inactive after the gesture is learned, but retains its original historical address. A second performer can borrow the reminder and author a new attachment. A third can turn it into a theme in its own right.

The histories form separate tracks: original address, current candidate addresses, explicit editorial adoption, applicability and performed output. An annotation can become an autonomous musical object without falsifying its original history. This is a design construction; no learning or human-like intention is attributed to a software oscillator.

An alternative artistic policy: when multiple hosts are admissible, play a separate gloss for each, perhaps with conflicting pitches or timbres; make unresolved relation audible rather than resolving it. In a concert, the ambiguity itself can be the score. In an operational interface, playing all possible targets as if authorized would be unsafe; display them as candidates and require appropriate verification.

## Exaptation and proposed next experiments

**Marginalia Organ (VSTi):** a persistent event/phrase sequencer with a separate annotation layer, immutable event IDs, explicit reattachment policies (identity, position, content, joint compatibility, free adoption) and independently routable gloss voices. Record revision and source/target IDs outside the audio callback. Use bounded buffers, immutable prepared snapshots and MIDI/event rendering; do not perform graph allocation on the audio thread. Provide an orphan tray, a candidate inspector and explicit audition of alternative histories.

**Gloss Fold (VSTfx):** a bounded granular processor over supplied DAW audio with user-authored segment IDs and context tags. Annotations can trigger a resonator or independently routed modulation, not assert hidden semantics. Reorder or revise segments and audition competing mapping policies. Dry audio and metadata remain separate. No automatic claim to recover actual historical identity from arbitrary audio.

**CYD Margin Field:** a 320x240 touchscreen instrument where the upper lane contains six cells per phrase, the lower lane shows gloss attachment. Touch edits context; XY moves between deliberately selected policies and musical gloss timbre. A dashed candidate link is not an accepted target. A persistent ID lock and a deliberate adoption control avoid silently changing the attachment. Firmware feasibility and usability untested.

**MHAC operational research hypothesis:** revision-aware evidence annotations could reduce wrong-target actions compared with automatic nearest matching. Test only synthetic versioned logs initially: substitute, reorder, duplicate, delete, and independently change applicability. Compare identity/verified revision mapping, ordinary textual candidate tables, local context, joint assignments, and optional acoustic candidate markers. Measure wrong-target selections, abstentions, correct recovery, task time and applicability judgments separately. Balance repeated contexts and edit histories; retain impossible histories as controls. The strong nonacoustic baseline may eliminate the problem. No communication benefit demonstrated.

### Counterargument

The artistic gloss need not stay attached at all. A transferred ornament may reveal something previously unavailable. The assumption that an event has a stable identity is itself a choice made by an editor. An artist may declare that an imitation inherits every annotation, while an archive retains the original relation. A score with no identifiable ancestry may still be a complete work. The instrument should expose this disagreement, not impose a universally correct ontology.

### Afterword (original fiction)

The librarian brought the old score to the organist. The pencil marks had been copied in ink.

“Here is everything the previous organist learned.”

The organist played the wrong bell and heard a beautiful ornament.

“Here is something she did not learn.”

The librarian opened two catalogue entries, one for an inscription and one for its migration.

## Reproduction and checkpoint

Run node laboratory.cjs (standard JS, no dependencies), and python render.py ./audio (Python 3.11+). The finite oracle was executed in a V8 tool isolate: 83 parameter cases, 23,708 labelled worlds, 94,832 policy checks; all assertions passed. Includes out-of-bound and swapped-history controls. Native Python 3.13.5 renderer passed deterministic rerendering, amplitude, WAV header, PCM readback, channel invariance and distinct-hash assertions for six files. Native repository-wide tests and independent review were not run here.

Live intake: base 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, research integrity, validation and research README; 35 recent PR and 30 active issue titles examined. Targeted title/content searches for marginalia, annotation, anchor, gloss, revision, quotation, paratext, gift, reciprocity, open form and related directions. #532 addresses return from digression; #471 cue-binding repertoire equivalence; #668 speaking-role attribution; #620 selective layer excavation. The present mechanism instead relocates a relationship after bounded content edits and compares knowledge of one context against both. Search is non-exhaustive, no novelty claim. Recent #706 verified open draft. #709 scope and empty comments checked before branch creation.

Only research/expeditions/gloss-changes-host/ is owned here. No shared manifests, canonical claims, frozen protocol, external review, real-device control or participant work. Draft/HOLD per issue for independent mergedown; do not mark accepted solely from local execution. Pending exact-head CI and integrator review.
