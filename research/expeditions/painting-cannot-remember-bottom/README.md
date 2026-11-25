# The Painting That Cannot Remember Its Bottom
*Palimpsest, opaque composition and the aesthetics of selective excavation.*

25 November 2026 · MHAC #620 · exploratory humanities/art, not frozen Track G/E evidence.

## 1. The painting with two conservators

One conservator sees a finished portrait. Another sees a discarded architectural drawing beneath it. A third makes a new work by taking the radiograph itself as a score. These are not three increasingly accurate versions of the same task. The first encounters a presented work, the second reconstructs material evidence, the third authors a new presentation. A technological means of making a layer legible is not an instruction to prefer it.

Consider an instrument whose musical elements inhabit sheets of opaque rather than transparent notation. A sheet may cover a musical event without deleting it. Moving the sheet changes which event is heard, but not necessarily any of the sound sources. The composer might spend years on a hidden composition and never expose it. Another musician could be given the right to excavate the work without being given the right to rewrite it. This is an instrument with two distinct scores: a score of material and a score of access to material.

The metaphor has three dangers. Real palimpsests involve physical alteration and loss, not a perfectly preserved digital stack. Actual paintings do not necessarily contain discrete homogeneous layers or one total priority order. And what can be reconstructed from traces is not necessarily what the maker intended. The finite instrument below makes its layers perfectly distinct as a deliberate artistic restriction. It is not a model of heritage science.

## 2. Five source encounters and a counter-reading

All readings below were performed by one ChatGPT agent, 2026-11-25, from accessible HTML. Metadata and passage reading are bounded to the cited pages; no independent human checking or primary archival examination. Source text/images are not redistributed.

- **National Gallery, “Studying Raphael: x-ray examination”** ([institutional article](https://www.nationalgallery.org.uk/research/publications/studying-raphael/studying-raphael-x-ray-examination)). Read opening paragraphs and the entire section “Pentimenti in Raphael's work.” The museum reports that X-rays in 1969 revealed a major change to the background of the Julius II portrait; paint cross-sections informed a colour reconstruction. In this particular case, the alterations helped reassess authenticity. Interpretation: a mark can be evidence of revision rather than an error in the final work. Caution: the diagram of the earlier background is an analytical construction, not an independent surviving painting.
- **Walters Art Museum, “With X-Ray Florescence Imaging, New Ability to Read Previously Unknown Mathematical Treatises in Archimedes Palimpsest,” 24 May 2005** ([institutional release](https://thewalters.org/news/archimedes-palimpsest-imaging/)). Read paragraphs beginning “The Archimedes Palimpsest contains seven” through “This month.” The institution describes reuse of parchment, recovery using multispectral imaging, and XRF exposing ink beneath a later forged icon. The press release is a contemporary report, not an independently replicated imaging evaluation or current completeness statement. Interpretation: changing the measurement apparatus can change which text is accessible without changing the manuscript. No analogy to perfect digital retention is warranted.
- **Julie Mehretu, “To Be Felt as Much as Read,” interview with Susan Sollins, October 2008, published May 2013** ([Art21](https://art21.org/read/julie-mehretu-to-be-felt-as-much-as-read/)). Read the answers to the opening question about revealing underpinnings, the question about watercolours, the follow-up about hope, and the question about transparency. Mehretu describes deliberately making architectural sources difficult to disentangle, sanding away colour, and the resulting work becoming complete. Her account relates these choices to historical erasure and political concerns; the present toy is not an equivalent of those concerns. Counter-reading: successful excavation may destroy the aesthetic condition the artist wanted. Obscurity can be intentional.
- **R. John Williams, interview by Lisa Prevost, “A fresh impression of Freud's ‘mystic writing-pad’,” 9 February 2024** ([Yale News](https://news.yale.edu/2024/02/09/fresh-impression-freuds-mystic-writing-pad)). Read the opening account and answers about the assumption that the pad was a toy and its marketing. Williams argues that a writing surface may participate in thinking rather than merely depict an already formed thought. His interview traces the device's commercial context; the underlying Representations article was not read. The Freudian analogy is encountered through this interview, not accepted as psychological evidence. Interpretation: an excavation interface participates in composition, not merely in playback.
- **John Cage, Fontana Mix (1958)** ([publisher programme note](https://www.wisemusicclassical.com/work/69276/)). Read the complete programme note. Transparent sheets and a grid are superimposed; measurements of intersections contribute to performance instructions. This is substantial prior art for independently manipulable score layers. The actual published score was not inspected and this expedition is not a realization of Cage's piece. Our construction instead uses opaque masks and gives each time cell one winning layer.

A commonplace engineering counterexample is audio ducking: Adobe's [Premiere help, “Automatically duck audio,” updated 10 November 2026](https://helpx.adobe.com/premiere/desktop/add-audio-effects/adjust-volume-and-levels/automatically-duck-audio.html), opening description, documents attenuating background material when foreground speech is detected. Priority gates, mute/solo and compositing already exist. No novelty for DSP is claimed. The proposed contribution is a score editor in which the *choice of permitted excavation* is first-class.

## 3. Formal construction: an opaque listening apparatus

Let Q be n known distinguishable layers and let pi be a strict total order, from uppermost to lowermost. A probe is any nonempty subset S of Q, fixed in advance or chosen adaptively. The response w(S) is the first element of pi in S. An empty mask produces a designated silence but contributes no information. Layer identity is read exactly, not inferred from noisy audio. All layer inventories are known; order is the only unknown. A probe changes the audition mask, not the order or the stored material. It may represent a time cell in a score. Nothing here assumes acoustic masking or a psychoacoustic winner-take-all law.

For a fixed family of probes, create a directed constraint w(S) -> x for every other x in S. The set of compatible orders is exactly the set of topological sorts of this graph: every order consistent with these edges reproduces each winner, and every matching winner imposes those edges. Graph edges say priority, not historical precedence.

**Instance-specific theorem.** Given the true order, its responses uniquely determine it if and only if each consecutive pair (a,b) in that order is witnessed by some probe containing both with winner a.

Sufficiency: the consecutive edges form the entire chain, so its linear extension is unique. Necessity: if consecutive a,b lack such a witness, swap them. No probe containing neither or just one changes winner; a probe containing both either has a still-higher winner or would have witnessed the missing edge. All responses stay unchanged. Since every probe has only one winner, it can witness at most one consecutive pair. Thus n-1 probes are necessary for uniqueness on even a single instance.

**Universal nonadaptive theorem.** A fixed probe family distinguishes every possible order if and only if it contains every exact two-element subset. Sufficiency: pair probes reveal every comparison. Necessity: place any missing pair at the bottom of the true order and swap them. Every probe containing both and at least one additional element is won by a higher element; no other probe can distinguish the swap. Hence the optimum fixed universal family has n(n-1)/2 probes. Singletons, repeats and the empty mask do not improve this bound.

**Adaptive theorem.** The worst-case number of probes is exactly n-1. Query all layers, remove the winner from the next audition mask, repeat until one layer remains. The last identity follows from the known inventory. The transcript's masks do not add information independent of the responses for a deterministic strategy; the preceding instance-specific lower bound still applies to the realized sequence. These are simple combinatorial results, not a claim of mathematical priority.

Example: A>B>C>D and A>B>D>C have identical winners A,B,A,A,A,B on masks ABCD, BCD, ABC, ABD, AB, BCD. Their difference is exposed by CD. An artist can swap those bottom layers without modifying the principal performance. An excavator can reveal the difference by a new audition. The artist and excavator now have separate musical instruments.

The exhaustive oracle enumerates all families of distinct masks of size >=2 for n=2,3,4, independently compares response fibres with the certificate and universal pair condition, and tests adaptive peeling. Repeated masks are represented in the explicit audio witness but do not enlarge the finite family enumeration. It also includes an empty-mask control and an underdetermined case. See laboratory.py and RECEIPT.md. The oracle is a software check of this stipulated model, not empirical work.

## 4. Interpretive essay: an excavation is not an undo

There are four different ways to make a sound disappear. One can delete its data. One can set its gain to zero. One can exclude it from an audition. Or one can admit it to an audition but allow a higher-priority sound to cover it. These may share a silent output while establishing different possibilities for subsequent composition. In a conventional DAW they are often represented by separate editing, mute, solo and routing operations. The proposed instrument deliberately makes them legible as different relations.

Imagine a composer painting an enormous field of grains. Underneath it are several earlier field recordings, each cut into the same temporal cells. The composer writes a moving brush that makes parts of the upper layer transparent. A second artist writes a brush that can inspect lower layers but cannot change their order. A third performs the emergent foreground as a musical phrase. The work is neither the stack alone nor a single rendering: it includes a vocabulary of possible excavations.

There is a tension between the conservator and the musician. The conservator may want the smallest set of inspections that distinguishes all admissible hidden orders. The musician might want the opposite: a long and slow series of examinations, some redundant, others deliberately unable to settle the question. The mathematically optimal strategy could be aesthetically banal. Six pairwise examinations might become a richer counterpoint than three peeling operations. A probe with many layers might serve as a repeated refrain even when it contributes nothing new. This does not make an inefficient diagnostic better for real diagnosis.

The lower layers are not necessarily earlier drafts. The artist can reorder newly created and old material without pretending that priority reflects chronology. This is a decisive difference from a recovered manuscript and from #516's local deletion chronology. One could even create a bottom layer after the final performance and intentionally never hear it. It is not a recovered original; it is a counterfactual underpainting.

There is also a right not to excavate. A performer may want to keep an audible sketch without preserving every rejected attempt. A digital palimpsest whose “erase” operation secretly retained everything would be a bad privacy interface. Separate reversible concealment from explicit destructive removal, and state what backups remain. A performance may conceal a layer from an audience without restricting an authorized editor; that is not a security mechanism.

The model's starkest limitation is that its exact identity responses do not model listening. Real voices may share frequency, timbre and phase; a nonlinear or mixed signal can carry information about more than one source. Some materials are intentionally blended. A partial-opacity mode could become musically fertile but would require a different model: alpha-compositing with distinguishable stems, headroom, spectral overlap and state transitions. The present theorem must not be applied to that mode.

### Exaptation: the Pentimento Loom

An instrument prototype could hold a 2-D time-frequency grid of labelled oscillator or grain layers. Each cell supplies a mask and a priority list; only the uppermost eligible voice is audible in hard-opacity mode. The layer order is a non-destructive editing dimension independent of pitch, phase and timbre. An audition sequencer reads through masks; a separate inspector displays all source states and distinguishes concealed material from deleted material.

Candidate controls: occlusion brush; local or global priority order; layer aperture; independent mask transport; pairwise comparison audition; adaptive peeling; surface lock; dry/bypass; optional safe crossfade when changing winners. A VSTi can use internally generated layer voices; a VSTfx can use explicitly routed input stems with a bounded number of layers and no hidden audio recording. A continuous crossfade extension must report when two layers sound together and no longer claim the hard winner-only guarantee. A realtime implementation would preallocate masks/voices, interpolate gain safely, and never allocate or lock on its audio callback.

Interesting research direction: a composer defines multiple protected surface performances and asks which priority permutations remain compatible with all of them. Moving within a compatible fibre permits dramatic hidden changes without altering any protected rendering. A second composer authors a new mask sequence to expose a chosen difference. This is a collaborative game between an underpainter and an excavator, rather than a generic mixer. It can also become a spatial installation with movable acoustic apertures (simulated routing, not actual physical masking).

### Operational boundary for MHAC

Priority-suppressed machine cues do not establish that their underlying conditions are absent. Compare an ordinary priority queue with an explicit pending-condition panel, a permitted secondary inspection channel and a full log. Measure mistaken absence attribution, recovery of pending conditions, query count and time; distinguish simulated decoder success from human task performance. Counterhypothesis: explicit structured status is sufficient and the acoustic layer metaphor adds only cognitive load. The design must never conceal urgent operational warnings as a game. No empirical communication advantage, safety validation, or consent to participant work is asserted.

## 5. Speculative afterword: the second exhibition

*The conservator announced that the painting contained a city.*

*The painter replied that the city was under the portrait because it had been built afterwards.*

*At the first exhibition the gallery displayed the portrait. At the second it exhibited six small windows through which visitors could inspect different portions of the city.*

*An architect declared the sixth window unnecessary.*

*The composer kept it. Every time it opened, a bell sounded that had been absent from the first five.*

*The catalogue did not call the bell a discovery. It was a new performance of an old possibility.*

---

Reconciliation: live AGENTS, README, RAG, PROGRAMME, AGENT_RUNBOOK, RESEARCH_INTEGRITY and VALIDATION read before editing. Recent 50 PR titles, 35 open issue titles and targeted overlap searches inspected. #516 records deletion scars, #348 recovers local-factor chronology, #524 addresses spatial traversal, #606 surface state and #612 sampling units. This expedition examines selective winner-only audition of a known retained layer set; it neither infers deletion chronology nor reconstructs a lost carrier. #620 was created and its body/comments reread; fresh issue-scoped branch from main. No canonical manifest, frozen protocol, or concurrent work is changed. Native qualification applies only to the standalone renderer/oracle. Draft/HOLD for mergedown review; no human testing, rights grant or research-stage advancement.
