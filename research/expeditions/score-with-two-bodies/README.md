# The Score With Two Bodies

*Scordatura, embodied notation, and the incompatible fidelities of musical translation.*

**Status:** exploratory expedition; synthetic construction and original art; not a frozen-protocol source extraction or a finding about human perception. Refs #692. AI-assisted research/writing/implementation by ChatGPT, 2026-11-26; no independent human review.

## The rehearsal that survives the instrument

Imagine a musician rehearsing a piece on an instrument whose strings are subsequently retuned. A conservator retains the recording; a choreographer retains the hand's journey; an engineer retains the mapping from keys to sounds. The conservator and choreographer can both identify a faithful performance, yet disagree over which one is faithful.

The hand is not merely the delivery system of the melody. It is itself capable of possessing a score. The act of translating a work between instruments can preserve the one at the expense of the other. More radically, an instrument can make the disagreement its musical material.

This is not a universal claim about notation. Conventional scores can specify gestures, and tablatures can supply tuning information. We deliberately separate two incomplete projections of a performance so that their differences can be composed.

### Reading encounters (all checked 2026-11-26 by the same assistant)

| Source / access | Locator and source claim | Interpretation or limit |
|---|---|---|
| ABC Classic, [Biber Rosary Sonatas](https://www.abc.net.au/listen/classic/read-and-watch/listening-guide/1000-years-of-classical-music-bibers-rosary-sonatas/10025008), 26 Nov 2018; public HTML, selected passages read | Under “Biber's Rosary Sonatas”, paragraphs beginning “A distinguishing feature” and “Only the first Sonata”: altered string tunings and notation for the player's actions can yield notes different from the written pitches. | Mediated account, not direct analysis of Biber's manuscript or recordings. Retuning also affects resonance; our grid omits this. |
| Martin Kaltenecker, [Matières sonores. Grand entretien avec Helmut Lachenmann](https://www.ensembleintercontemporain.com/fr/2014/09/matieres-sonores-entretien-avec-helmut-lachenmann-compositeur/), 30 Sep 2014; French interview, selected passages read | Reply to “Avez-vous expérimenté ce genre de chocs…” discusses the energy involved in producing sound and unforeseen expressivity in interpretation. Reply about rehearsal discusses willingness to be temporarily unskilled and learn. | Primary interview, not a complete analysis of his compositions. My English paraphrase. The model makes an artificial cue for action; it does not instantiate instrumental musique concrète. |
| Mei-Chen Lu, [Resources and Riches: Dance Notation Bureau](https://www.dancenotation.org/theory-bulletin-board/resources-and-riches-dance-notation-bureau/), 2011 web post of 2009 article, public HTML, selected passages read | Opening paragraph beginning “Labanotation scores function”; “Dance Notation Bureau History”, paragraph on expansion to complete production package: movement notation supports staging but supplementary production information also matters. | Institutional historical account; no dance score or performance independently inspected. A body score is not necessarily a self-sufficient record. |
| Michael R. Kearney, [The Phenomenology of the Pipe Organ](https://journals.library.ualberta.ca/pandpr/index.php/pandpr/article/download/29432/21449/77964), Phenomenology & Practice 15(2), 2020, 24–38; extracted PDF opening read, page-image retrieval failed | p. 24, abstract and introduction, including mediated quotation of Merleau-Ponty (2012, p. 146): an experienced organist adapting to an unfamiliar instrument illustrates habit as embodied engagement rather than memorized coordinates. | Merleau-Ponty's original book not independently verified. His example is philosophical, not measured learning-time evidence. Our discrete distance is not bodily effort or a phenomenological model. |
| [Optimization for Guitar Fingering on Single Notes](https://cir.nii.ac.jp/crid/1390001204604232320), IEEJ Transactions on Electronics, Information and Systems 124(7), 1396–1403, 2004, DOI 10.1541/ieejeiss.124.1396 | Indexed English abstract explicitly describes Manhattan-distance fingering costs and dynamic programming; direct article and CiNii open failed. | Substantial prior art for optimization of fingering. Author metadata and full article not independently verified. No algorithmic novelty claimed. |

The encounter with Merleau-Ponty poses a useful objection: converting an instrument into coordinates and calculating a minimal path could be precisely what an experienced player does NOT do. A numerical score of motion is a description we have chosen, not a theory of skilful performance. Lachenmann's practice poses another objection: the resistance of an action might be aesthetically desired. An easier passage is not always a better passage.

## The Tablature Loom: a finite construction

Use an imaginary three-row, five-column instrument. An action is a pair (s,f) with row s in 0..2, column f in 0..4. The rows have original offsets (0,3,6) and retuned offsets (0,4,6). Pitch is a semitone index relative to 220 Hz: P_t(s,f)=t[s]+f. No chords, pressure, string mechanics, physical effort or continuous motion are modelled.

The authored score is ((0,4),(1,3)) repeated three times. Its sounding pitch indices are (4,6) repeated three times. Literal transfer of the action score to the retuned mapping instead produces (4,7) repeated three times. Retuning changes the second note, not the first; it is not an ordinary whole-phrase transposition.

Define E as the number of note slots where the translated action differs from the original. Define M as the sum of 2*absolute row change + absolute column change over adjacent actions; initial and final travel are excluded. These weights are arbitrary composition conventions, NOT ergonomic measurements.

For an exact pitch-preserving translation, the action at every slot must lie in the target inverse image of the corresponding source pitch. We retain minimum M for each exact E, then eliminate dominated pairs. One path per pair is retained, choosing lexicographic ties; we do not enumerate every optimal path in the returned frontier.

| Transfer | Pitch mismatch count | Changed action slots | Motion cost |
|---|---:|---:|---:|
| Original body | 0 | 0 | 15 |
| Literal retune | 3 | 0 | 15 |
| Minimum edits | 0 | 3 | 20 |
| Alternative | 0 | 4 | 16 |
| Alternative | 0 | 5 | 12 |
| Minimum motion | 0 | 6 | 10 |

The last four rows form the exact nondominated frontier in the stipulated pitch-preserving domain. They are not a joint three-objective frontier with pitch mismatches allowed. Three edits are necessary because the original second action has changed pitch and occurs three times. They are sufficient because the retuned middle row at column two produces the desired pitch. The least-edit route costs more travel than the original. The least-motion route is a complete rewrite.

For a fixed old action sequence x, the recurrence uses state (last action a, exact edit count e). At each next pitch-compatible action b, add the motion distance d(a,b) and increment e by the indicator of b differing from x at this slot. Retain only the least-cost path (lexicographic tie-break) for each state. Future incremental costs depend only on the last action and edit count, so discarded paths cannot improve a later result in this model. An empty inverse image correctly yields no feasible translation.

### Native qualification and controls

Run `python laboratory.py audio` from this directory using Python 3.11+. The program compares the DP frontier against exhaustive enumeration over all 3,616 old action scores of lengths 0 through 3 (11,155 target candidate paths visited), then independently enumerates all 64 target paths for the six-event exemplar. It checks exact nondominated costs, unreachable pitch refusal, empty score, identical-map zero-edit preservation, rerender determinism, amplitudes, WAV header/readback and left/right PCM equality controls.

Actual run: Python 3.13.5, PASS. All six WAVs are 16 kHz stereo 16-bit PCM, 24,000 frames (1.5 s). Executed source Git blob 9d7838536cdab7ccfb60e84477e2807d3328ff22. The uploaded branch copy was independently fetched and its blob ID matched. Machine-readable receipt and audio generated on demand; neither is a canonical evidence record.

The tests verify a bounded finite implementation. Brute force shares pitch and motion functions with the DP; an explicit known frontier and audio invariants help check errors but this is not independent external implementation or peer review. No physical instrument or listener trial took place.

## Original artistic score — Six dances for an absent hand

Render the sounding melody on the left using a sine oscillator and an identical squared-sine envelope for every event. On the right, a separate invented coordinate instrument sings 500+180*s+35*f Hz. Both use fixed common gains. The right channel does not simulate physical finger noises; it is a deliberately artificial notation of action.

I. Original: the body and the melody introduce themselves.
II. Literal retune: the body remembers the old dance; the melody does not.
III. Minimum edits: the melody survives; three gestures change and travel increases.
IV. Four edits: the translator begins moving the earlier gestures as well.
V. Five edits: most of the choreography has been replaced.
VI. Minimum motion: the same melody is now performed by a different route entirely.

The first two right-channel PCM streams are exactly equal. The original and all four pitch-preserving translations have exactly equal left-channel PCM streams. All six complete stereo streams differ. This constructs an audible counterpoint of independent fidelities rather than measuring natural cue perception.

Listen to left alone, right alone, and stereo. Those are instructions for an artistic exercise, not a claim about anyone's actual experience. The listener may find the added coordinate channel ugly or gratuitous; that is an acceptable artistic response.

### Second rabbit hole: the pianist's foreign body

Imagine a score distributed to three performers, each supplied with a different mapping between gesture and sound. An audience hears their three exact-pitch translations as unison. The performers are dancing three different dances.

Now designate one musician as the master of gestures rather than pitch. The others follow her movements, producing harmonically divergent music. The ensemble can switch between coordinated action and coordinated sound, introducing an orthogonal musical mode that is neither conventional harmony nor conventional rhythm.

A further possibility is to compose the mapping itself as an automation lane. When the mapping changes, some gestures become acoustically transformed, others remain fixed, and some requested pitches disappear. A composer's decision to preserve a phrase can cause a sudden change of movement; their decision to preserve a movement can cause a sudden change of harmony.

This offers a choreography for nonhuman synthesizer agents without attributing a human body schema to them. The agents have action maps, not necessarily bodies, sensations, skill or intentions.

## Exaptation and falsification

**Tablature Loom VSTi:** a step sequencer maintaining independent action and pitch lanes, editable maps and a selectable translation frontier. Provide literal-transfer, preserve-pitch, minimize-edits and minimize-motion modes. Report unavailable targets rather than substituting pitches silently. Recompute bounded paths off the audio thread; publish immutable plans at explicit step boundaries. MIDI output and the coordinate sonification should be independently routed. No plugin implemented here.

**Scordatura Field CYD:** a 3x5 touch surface with editable row offsets and a second view of pitch identity. Record a gesture sequence and switch the map without deleting the source sequence. A frontier knob permits the performer to choose among translated paths. The two views could also serve as independent XY modulation routes. No device build or hardware qualification here.

**Body Double VSTfx:** record control gestures accompanying audio or MIDI. Preserve the original control trace and regenerate a separately declared mapping, instead of claiming to reconstruct gestures from an arbitrary recording. The inverse problem is not solved by this expedition.

**Research hypothesis (unvalidated):** an explicit mode distinction between replaying an original action sequence and reproducing its original effect may reduce confusion when a virtual device's control mapping changes. A synthetic study should compare action-only, effect-only, explicit mapping/version labels, text, and optional acoustic cues. Measure action reconstruction, effect reconstruction and appropriate choices independently. Include unreachable requests and equal-output/different-action cases. Ordinary explicit text or a table may outperform sound; no acoustic benefit is established.

Do not infer a machine's exact internal action trace from an acoustically equivalent output; do not infer safe execution or authority from a musical mapping. Operational controls must retain their actual state/version and explicit authorization independently of the artistic demonstration.

## A short fiction: The rehearsal room

The conservator asked the dancer to reproduce the song. The dancer did so with her left hand. The conservator objected that the right hand had made the recording.

At the second rehearsal she used her right hand. The conservator objected to the notes.

At the third rehearsal a second musician sang the notes while the dancer repeated her first movement.

The conservator asked which of them was the original.

The technician turned down the monitor and offered him two scores.

---

Reconciliation: live main base 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, research README, integrity and validation read. Recent 40 PR and 30 open issue titles inspected, with targeted searches for tablature, fingering, choreography, embodiment, voice leading and destructive observation. Earlier destructive observation #203 made that direction unsuitable for a new expedition; #540 concerns hocket, not retuning. #636 and #678 are neighbouring gesture/capability topics by title, not verified exhaustive non-overlap. Search indexing is incomplete. Scope only this directory. Owner instruction to prefer additive expeditions and the separate concurrent mergedown lane take precedence over automatic landing; draft/HOLD pending exact-head review and CI. No shared manifest, protocol, canonical claim registry or existing worker file modified.
