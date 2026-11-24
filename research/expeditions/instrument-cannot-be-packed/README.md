# The Instrument That Cannot Be Packed

**Expedition #414 | 2026-11-24 | exploratory philosophy, art and synthetic mathematics.** Not a selected evidence record, a Brier reconstruction, or an approved operational design. AI-assisted research and self-check by ChatGPT GPT-6.2; no independent reviewer or participant. Base `495a98ca12bae467a507031f04931aa4254b1866`.

## A museum of detachable instruments

An auction catalogue lists a keyboard, a power supply and a processor. The instrument is sold, delivered and connected. It plays the old repertoire perfectly. Yet when a visitor speaks, the instrument no longer answers in the familiar way. The buyer asks for the missing effect. The seller sends a convolution impulse response. The visitor tries again. Nothing is quite right.

The fictional buyer has not simply lost a reverb preset. She has lost a reciprocal relationship: the keyboard affects something that can in turn affect it. The room is not only a destination for sound but potentially a second place from which an event can originate.

A musical instrument can be sold as a bounded commodity, demonstrated as an input/output device, conserved as a collection of parts and experienced as an arrangement of relations. None of these descriptions necessarily exhausts the others. The intriguing possibility is not merely a site-specific instrument, but a portable instrument whose identity depends on an explicitly transplantable coupling contract.

## Source-located encounters (bounded reading, 24 November 2026)

- **Susanna Lindberg (2019), “Being with Technique–Technique as being-with: The technological communities of Gilbert Simondon,” Continental Philosophy Review 52, 299–310.** [Open article](https://link.springer.com/article/10.1007/s11007-019-09466-9), numbered argument (2), paragraphs beginning “Thirdly” and “Simondon calls”, notes 35–41; also argument (4), critique of human technicality. Passage-level secondary reading. Lindberg presents associated milieu as the technical-natural setting constituted through technical operation and distinguishes an indispensable milieu from an ensemble. Her discussion of a concert hall is her illustration, not Simondon's own turbine example. Her critique complicates a merely machine-centred account of technical relations. No independent full reading of Simondon's book.
- **Nicolas Collins (1990), liner notes for Alvin Lucier, I am sitting in a room.** [DRAM notes](https://www.dramonline.org/albums/alvin-lucier-i-am-sitting-in-a-room/notes), paragraphs beginning “The performer proceeds”, “By the end of the piece” and “The pieces could have been performed live”; signed March 14, 1990. Passage reading, including the score excerpt and interview quotation as transmitted by Collins. Collins describes iterative re-recording and emphasizes the interaction of Lucier's particular vocal material with his room, rather than treating the result as a complete room spectrum. His interpretation of the speech rhythm is a reading of the artwork, not a clinical claim about stuttering.
- **David Tudor, Rainforest IV (1973).** [Getty Research Institute account of 2001 realization](https://www.getty.edu/research/tools/guides_bibliographies/david_tudor/av/rainforest.html), paragraphs following the video credit and artist statement. Institutional description and excerpt of artist testimony read; video not viewed. Driven resonant sculptures become instrumental emitters, with materials chosen for their physical characteristics and visitors free to move among them. This is a precedent for relocating instrumentality into things commonly classified as surroundings; it does not establish that the objects form reciprocal feedback loops.
- **Agostino Di Scipio (2003), “Sound is the interface: from interactive to ecosystemic signal processing,” Organised Sound 8(3), 269–277.** [Publisher abstract and metadata](https://www.cambridge.org/core/journals/organised-sound/article/abs/sound-is-the-interface-from-interactive-to-ecosystemic-signal-processing/46F00028C75A53AF050A0B1E4BB5AE70); abstract-level primary reading. The author proposes interaction as interdependency among DSP, surroundings and other components, with behaviour emerging through contact with the performance environment. The title and abstract make ecosystemic composition clear prior art, not a novelty claimed here. The full paper was not independently read or appraised.
- **Dario Sanfilippo and Luca Spanedda (2026), “The realisation of Di Scipio's Audible Ecosystemics n.2: strengths and challenges in the interpretation and notation of machine-independent computer music.”** [Zenodo version 1](https://zenodo.org/records/18898899), Description, paragraphs 1–4, published 7 March 2026. Abstract/description only. The authors report reimplementation of the Kyma-based work in Faust and point to the importance of faithfully interpreting processing objects for recursive behaviour. No evaluation of their tests or reproduction of their system here.

These encounters are not interchangeable. A resonating sculpture, an iterated recording and a continually interacting environment have different temporal and causal structures. Simondon's associated milieu has a stronger philosophical sense than the presence of a feedback path. The mathematical construction below is deliberately much weaker: it does not demonstrate individuation, autopoiesis, subjectivity, or a common essence of these works.

## A second entrance to the instrument (original construction)

Let x be an internal state, y an environmental state with an independently fixed calibration, u a keyboard input and v an environmental injection. All are dimensionless synthetic quantities. Begin at x=y=0 and update synchronously:

    x[t+1] = a*x[t] + b*y[t] + u[t]
    y[t+1] = c*x[t] + d*y[t] + v[t]

The observed keyboard output is x, not the sum x+y. No real microphone, room, physical energy, or acoustic transfer function is represented. For two systems with equal a,d and equal product bc, elimination of y gives

    x[t+2] = (a+d)*x[t+1] + (bc-ad)*x[t]
             + u[t+1] - d*u[t] + b*v[t].

Thus for v=0, the complete keyboard input/output map is identical, for every input sequence, not merely for an impulse. The initial values x[0]=0 and x[1]=u[0] are equal, and induction gives the result. But an independently calibrated environmental unit impulse v[0]=1 yields x[2]=b. It separates all distinct positive factorizations of the product.

Example: a=d=1/4. A has b=1/8,c=1/2; B has b=1/2,c=1/8. Each product is 1/16, each has maximum row sum 3/4, each is stable (the eigenvalues are 1/2 and 0). A sends more into its environment; B receives more from its environment. They have identical keyboard responses and different environmental responses. Their full state-space models are related by rescaling y. That is not a loophole but an important limit: without a common calibrated environmental coordinate or input, the individual b and c values are not identifiable. The distinction is operational only relative to the fixed second port.

One could even replay a convolution of u with the keyboard impulse response to reproduce the one-port output exactly, but this would not supply the second input or reconstruct the environment. A successful emulation of a single interface is not a demonstration that every interface is preserved.

### Executed finite checks

Run `node oracle.cjs` in this directory. The dependency-free JavaScript laboratory uses BigInt with a common denominator 8^t; the exact checks compare the simultaneous recurrence with independently eliminated scalar recurrence. The finite grid enumerates a,d in {0,1,2,3}/8 and b,c in {1,...,5}/8, with each row sum at most 7/8. Group by a,d,bc, compare all unordered distinct pairs. Verify arbitrary signed fixture input and impulse input, calibrated environmental separation and environmental scaling. An additional 243 signed five-tick keyboard sequences test A/B.

Results: 361 systems; 164 distinct same-product pairs; 1831 counted trajectories in the grid and exhaustive-sequence checks (excluding the four displayed witness traces); 12319 passing assertions. Exact witness x values from tick 0 through 6:

| input | t0 | t1 | t2 | t3 | t4 | t5 | t6 |
|---|---|---|---|---|---|---|---|
| keyboard A or B | 0 | 1 | 0.25 | 0.125 | 0.0625 | 0.03125 | 0.015625 |
| environmental A | 0 | 0 | 0.125 | 0.0625 | 0.03125 | 0.015625 | 0.0078125 |
| environmental B | 0 | 0 | 0.5 | 0.25 | 0.125 | 0.0625 | 0.03125 |

This is standard linear-system algebra applied to a deliberately constrained example, not a claim of mathematical originality. A linear model with positive stable coupling is not a model of the historical artworks, human listening or real acoustic feedback. Physical acoustics may be nonlinear, multichannel, time-varying and unobservable. Calibrated probes can be intrusive; an instrument must not secretly conscript a room's occupants into measurement.

## The instrument as a contract of reciprocal exposure (interpretation)

I propose treating the external relation as an authored part of the instrument, rather than an unexamined dependency. Four independently addressable operations are worth distinguishing: **send** (what the instrument contributes to its milieu), **receive** (what the milieu contributes to the instrument), **substitute** (which aspects of that milieu may be simulated), and **detach** (what can be played when the relationship is unavailable or declined). A convolution preset can be an excellent substitute for one response without being a substitute for every way of participating.

There is a temptation to equate larger coupling with greater openness. A device that hears everything might be intrusive rather than receptive. A person might want to hear the instrument without becoming part of its control loop. Conversely an artist might intentionally compose a situation in which a physical environment remains indispensable, and decline the premise that all works ought to be portable. The correct response is not to insist on interchangeable rooms, but to make the choice intelligible to performers.

A studio instrument could expose two independently editable ports, loop memory, a documented environmental calibration, a virtual substitute, and a separate optional environment-monitor voice. The same keyboard response could be conserved while the response to the second musician is transformed. In a large procedural synthesizer, thousands of oscillator agents might share virtual environmental cells, writing into and reading from them with independently programmable strengths. A cell would be a persistent field, not just a reverb applied after synthesis. Stability, saturation and update order would be first-class software parameters; no physical feedback hardware is required or tested.

## MHAC handoff and negative cases

The one-port example is not the received-feature separability question in #41 (T007), which concerns transformations after source-side rendering. Here the milieu also has a return path, including an independently specified external input. Earlier expeditions on acoustic withdrawal (#342), service compensation (#374), directional cost (#406), and blind convolution, switched dynamics and closed-loop phase are neighbouring but different in purpose. This expedition does not extend their formal guarantees or change their artifacts.

A prospective synthetic interface evaluation could use a fixed keyboard trace and an independent calibrated environmental input. Compare (i) outgoing-only tests, (ii) outgoing plus calibrated environmental probes, and (iii) an explicit statement that a return channel is absent. Outcomes: identification of the available causal route, discrimination of the two synthetic systems, incorrect attributions of origin, and interruption burden. Include mismatched calibration, disabled port, additive background and unknown input as negative controls. Failure of a calibrated test is not evidence of a perceptual or semantic failure without a separate study. Conventional system identification is sufficient for the mathematical result; no cybersemiotic vocabulary improves it by itself.

No live sound capture, device control, participants, or required alerts are involved. A future interface should not infer consent from environmental input, should disclose capture and allow independent disconnect, and should keep essential notifications independent of experimental coupling. The no-participant, nonproduction limits remain.

## Expedition checkpoint

Read live AGENTS, RAG, programme, runbook, integrity, validation and research workspace authorities; checked main repository-integrity success, 100 recent PR titles, 70 open issue search results, targeted Simondon/Umwelt/associated milieu/acoustic feedback/room/affordance searches, and the full #41 issue. New #414 body and empty comments checked before editing. The frozen protocol, source registry, shared manifest and other workers' branches are untouched. Scope is additive exploratory writing, a text score and exact executable fixture. Draft for integrator review; no scientific acceptance, human review or full repository validation claimed. See [score](SCORE.md) and [oracle](oracle.cjs).
