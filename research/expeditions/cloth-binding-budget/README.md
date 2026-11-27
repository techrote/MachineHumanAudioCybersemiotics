# The Cloth That Counts Every Thread but Cannot Hold a Phrase

**Expedition #782 — 27 November 2026 — exploratory / Draft-HOLD.**
Original AI-assisted writing and synthetic construction, not a selected evidence record, textile simulation, human study or scientific acceptance claim.

## An invented commission

The municipality commissioned an organ with sixteen voices. Its patron specified equality: each voice should be audible for exactly half the performance. The maker supplied two scores. In one, every voice was repeatedly interrupted. In the other, each occupied long passages, alternately disappearing and returning. The patron's accountant certified both. The performers asked for a second specification: how long could a voice remain continuously in the foreground, and how long could it be excluded?

A weaver was invited. Instead of a new inventory of sounds, she supplied a card of over-and-under decisions. The organ was made to play its warp from one side and its weft from another. The two sides were not interchangeable; a row's continuing presence meant a column's absence at that crossing. The object to compose was no longer the voice but its successive relationships with other voices.

This is an original fiction. It makes no claim about equal political participation or the actual mechanics of cloth.

## Source-located encounters

- **Anni Albers, [The Pliable Plane: Textiles in Architecture](https://www.albersfoundation.org/alberses/teaching/anni-albers/the-pliable-plane-textiles-in-architecture), Perspecta 4 (1957).** Foundation transcription, opening two paragraphs beginning with the contrast between architecture and textiles and continuing into linkage versus fusion. Albers identifies a shared mode of construction from parts retaining their identities. Read the opening selected passage, not the entire essay or original facsimile. Interpretation: a synthesizer might link voices without reducing them to a fused identity. The analogy is productive precisely because an audio mix does not normally retain separately recoverable source identities.
- **Albers, [On Weaving](https://www.albersfoundation.org/alberses/teaching/anni-albers/on-weaving), October 1963 lecture transcript.** Read the paragraphs beginning “To save time”, “These examples show you”, “Though we have gained”, and “Embedded in the process”, through the discussion of visible and invisible textile qualities. She contrasts the range of hand practice with the narrower range of mechanized production, links crossing to textile form, and distinguishes surface appearance from properties needing separate descriptions. These are her arguments, not measured engineering findings; the historical chronology and absent slides were not verified. Interpretation: an instrument's internal compositional affordances need not be visible in the surface picture or apparent in a summary of its output.
- **Ada Lovelace, notes to Menabrea, [Sketch of the Analytical Engine](https://www.fourmilab.ch/babbage/sketch.html), 1843, Note A.** Fourmilab transcription, paragraphs beginning “The operating mechanism can even be thrown into action” and “The distinctive characteristic of the Analytical Engine”. Both the proposed application to musical relationships and the comparison with Jacquard pattern control were read directly. These are conditional conceptual arguments, not proof that the Engine created music. The card can prescribe an operation rather than be an image of the resulting object. Interpretation: let a graphical draft prescribe a temporal musical relation instead of merely mapping image brightness to pitch.
- **Ann Lane Hedlund, Beyond the Loom (1990), [University of Colorado Museum glossary](https://cumuseum-archive.colorado.edu/Exhibits/ThreeCultures/glossary.html).** Read entries warp, weft, weave/plain, weave/twill and warp float pattern. The glossary explicitly scopes its definitions to the collections concerned. It establishes the ordinary distinction between alternating crossings and longer floats; it does not establish physical stability from binary counts. Note especially that the glossary's technical definition of balanced weave concerns yarn size and spacing, not a binary half-count. Our 'balanced draft' is a separate mathematical convention.

Access: public HTML transcriptions, selected passages read 2026-11-27 by the writing agent; no restricted source copied, no human independent reading. These encounters are contextual rather than additions to the frozen empirical corpus. No priority or direct influence between the authors is claimed.

## Essay: an instrument composed out of obligations

A piano key usually opens a voice. A woven instrument instead places every voice at a crossing. At each crossing something comes into the foreground and something else passes behind. The decision is mutual, but its consequences need not be simultaneous in the eventual score: the score might read across rows or down columns. The material object can be turned ninety degrees without rewriting its individual crossing decisions.

Lovelace's comparison of calculation and weaving is often attractive because of the cards: an arrangement of marks is able to govern an arrangement of material. Albers makes another aspect of the metaphor available. The structure and the means of its production are themselves a medium, not just a conduit for a pre-existing picture. A synthetic score could therefore specify how a texture holds together rather than describe an image of what it should become. The difference is comparable to drawing a curtain and writing the rules according to which a curtain changes.

What if the composer is responsible for continuity rather than timbre? Give two performers the same oscillators and the same total durations of exposure. One distributes those durations as brief alternating glimpses. The other lets them cohere into extended phrases. In an ordinary piano roll their works are obviously different. In a report consisting of total active time per voice they are identical. Both reports can be entirely correct.

The loom makes the ambiguity explicit through two independently useful constraints. A maximum float limits a thread's uninterrupted occupancy (or absence, for the other side). A switch budget limits the total number of interruptions. Neither is a universal artistic virtue. A long tone could be a valuable refusal to change; a short interruption could be a desirable articulation. A perfectly alternating score can be oppressive to sustained melody, and a very smooth one can conceal a voice for too long.

A machine whose only measure of generosity is the total duration of access may be generous in aggregate while making a particular encounter unusable. Conversely, a machine measuring only the frequency of changes may mistake a restless surface for a rich distribution of opportunities. The model below isolates this tension. It is not a model of justice, textile strength, attention or intelligibility.

## Exact synthetic construction

Let n=2m, and let a binary n-by-n cyclic draft have exactly m ones in every row and column. One marks a row voice on the foreground side; zero marks the corresponding column voice on the foreground side. For each of its 2n lines count changes between consecutive bits, including the wrap. Define F as the greatest same-bit run across all lines, and B as the sum of all line changes.

For a cap L with 1 <= L <= m, every line has r positive runs of each bit, so its change count is 2r. Since m copies of each bit must fit into those runs, r >= ceil(m/L). Therefore B >= 4n ceil(m/L).

This bound is attained simultaneously for all rows and columns: partition m into r positive lengths no greater than L (use L repeatedly and a final remainder), alternate equal-length 1 and 0 runs, and form the circulant draft G[i,j]=w[(i+j) mod n]. Every row and column is a rotation of the same balanced word. Thus the lower bound is sharp for the stipulated toroidal binary model.

There is a plateau. At n=8, caps 2 and 3 both allow a minimum B=64, yet the respective witnesses 11001100 and 11100010 distribute continuous exposure differently. Cap 1 requires 128 changes; cap 4 requires 32. This is an exact switch count, not CPU work, physical binding force or an auditory judgment. The two plateau witnesses have the same exposure counts and same change counts, but distinct run-duration distributions.

A useful dual design question: if a per-line switch limit permits at most r runs of each bit, the smallest possible worst same-bit run is ceil(m/r), attained by balanced partitions and the same circulant construction. This statement is analytical; the implementation qualifies the forward cap formulation. No theorem priority claimed.

## Executed laboratory and artistic score

Run `python laboratory.py audio` with Python 3.11+ and no dependencies. Native Python 3.13.5 executed the final source twice, with identical WAVs and receipts. The first attempted construction partitioned runs evenly, making cap 3 accidentally identical to cap 2. The distinct-recording assertion refused that trial; the final construction deliberately uses the longest permissible first run and remainder. This retains optimality and exposes the plateau musically.

- All 65,536 labelled 4x4 binary drafts screened; 90 have exactly two ones in each row and column. Their (F,B) census: (1,32):2; (2,16):16; (2,20):32; (2,24):40.
- All 4,706 balanced binary words of even lengths 2 through 14 examined. Longest cyclic runs were cross-checked by independent direct constant-window search. All 28 admissible length/cap combinations matched the sharp bound and constructive matrix witness. Three out-of-domain inputs refused.
- Four 8x8 circulant draft examples rendered, words 10101010, 11001100, 11100010, 11110000. Left: eight row voices gated by 1. Right: eight column voices gated by 0. All voices are continuously phased sine oscillators; ten-millisecond ramps at actual gate transitions and outer recording boundaries. Each channel has four scheduled active voices per slot, and every voice is scheduled on for 16 of 32 slots. The two scans are separate projections, not an assertion of physical simultaneous threading. 140 ms per slot, four cycles, 71,680 stereo frames at 16 kHz, signed 16-bit PCM. All headers, sample bounds, full PCM readback and four distinct WAV hashes checked.
- Audio receipt generated locally, not a canonical registry record. Final hash prefixes: cap 1 bd3308d095d3, cap 2 d739facf8c2c, cap 3 f542825178da, cap 4 6da6a205b431. Same-runtime repeat execution matched byte for byte; cross-platform floating-point identity not established.

**Performance instructions:** Listen to the four recordings without a picture. Then examine the draft. Listen to the middle two again as a pair of works with the same number of interruptions, not as two estimates of the same sound. In a fifth unwritten movement, allow a thread to exceed its prescribed cap whenever its absence would destroy a phrase. Record the exception separately rather than pretend the constraint has survived.

No human listening, physical weaving, DSP latency or hardware qualification occurred. Output RMS and perceived loudness are not conserved by this model. Voice exposure is symbolic gate duration, not a listening result.

## Second rabbit hole: a cloth with a right to turn over

Imagine an instrument that does not discard the inaudible voices. They continue to phase, accumulate modulation, and form a second independently audible fabric. Turning the score over reveals the other side; rotating it changes the traversal order. A performer could modify one crossing and immediately hear which side lost a gesture and which side acquired it.

The metaphor can be developed without conflating concealment with erasure. If hidden oscillators continue to evolve, their state must be advanced even while absent from a bus. If frozen, they resume from a retained state. If erased, no later return is implied. Three different contracts could sound identical on the visible side for a while. The future instrument ought to expose those differences explicitly.

A practical extension is to separate maximum audible run from maximum inaudible run, to allow weighted or unequal exposure, and to make the costs of switching dependent on actual envelopes. The simple circulant construction is not automatically optimal under those conditions. Another experiment: prescribe individual row and column run caps and identify infeasible collections despite equal total counts. A small exact solver can compare repairs before designing a live editor.

## Exaptation and research handoff

- **Binding Organ (VSTi):** persistent oscillator identities, editable over/under draft, independently scannable row and column buses, cap and switch inspector, transition-preserving variants. A first product should be a small fixed grid with deterministic gates, explicit note-on/off semantics and a crossfade at draft replacement. Keep sustained and reset phase policies separate.
- **Selvedge (VSTfx):** explicitly supplied stems or two input buses gated according to complementary draft decisions. Separate dry reference; do not claim arbitrary mixed-signal separation. A future soft-mask extension would require actual overlap and summed-gain testing.
- **CYD Thread Atlas:** 8x8 touch editor, X/Y scan position, cap slider, row/column counts, cyclic run highlights, independent monitor selection. A brush toggles a 2x2 checkerboard to preserve marginals; it must still inspect run caps because count conservation alone does not preserve them. This is a proposed firmware interaction, not shipped hardware.
- **FM-1:** prospective patch scheduler using runs to control sustained carrier/FM gestures and changes to control articulations. No device integration assumed.

The next most useful artifact is a playable, preallocated bounded-grid editor with deterministic tests for phase continuation, wrap transitions, exact gate counts, refusal of invalid drafts and click-free editing. Record actual callback costs rather than extrapolating from the offline renderer.

For MHAC operational communication, aggregate exposure, maximum silent gap, uninterrupted availability of a complete message, and transition count must be distinguished. A future synthetic comparison should hold total opportunities constant while varying gap and fragmentation, using a plain timestamped typed ledger as the strongest comparator. Test complete-bundle recovery by deadline, false action, abstention, and workload separately; reject an acoustic layer if it provides no added value. Equal exposure is not sufficient for successful communication. No acoustic benefit demonstrated.

## Counterargument and checkpoint

A binary draft is not a cloth. It excludes thread tension, elasticity, friction, deformation, material histories, skill, labor, cultural specificity and the economic institutions behind weaving. Treating the textile metaphor as a data visualization alone repeats the very reduction that Albers's concern for the material process helps challenge. Nor does a cap prove that a human perceives a phrase. The artist may choose to reject the cap altogether. The model remains useful as a deliberately narrow compositional constraint and adversarial counterexample.

Live AGENTS, README, RAG, programme, runbook, integrity and validation authorities reconciled; main base 495a98ca12bae467a507031f04931aa4254b1866. Reviewed 40 recent PR titles and 25 active issue titles, plus targeted issue searches for weaving, loom, Jacquard, Albers, textile, float, tapestry, braid, Goodman and abandoned directions on reversal/memory. No matching weaving-specific issue returned in those bounded searches; not exhaustive novelty proof. Existing Crossing Loom (#549/#557), Offcut Loom (#574/#580), Frottage (#746) and Copia (#773) are related but focus on identity crossings, residual synthesis, observation kernels and commentary scheduling rather than this cyclic run cap. No canonical records or shared manifests touched. Only this directory on mhac-x782/cloth-binding-budget is owned. One AI writing/implementation agent; no subagents or external review. Native standalone tests passed; full repository tests/CI and independent mergedown acceptance remain separate. Refs #782; do not close or merge on this record alone.
