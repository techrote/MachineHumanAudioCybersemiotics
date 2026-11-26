# The Ornament That Holds the Note Still

**Refs #628 | 26 November 2026 | Original humanities, mathematical and artistic expedition.** Not selected Track E/G evidence, human evaluation, or an accepted design requirement.

A musician builds an instrument whose decorative branches are not connected to its loudspeaker. A visitor asks to remove them. The musician mutes their already silent output; nothing changes. The visitor then disconnects the branches from the mechanism. Two notes return. The visitor calls the result a simplification. The musician calls it a different instrument.

## Ornament and the jurisdiction of the frame

Owen Jones's *Grammar of Ornament* (1856), propositions 5–8 [S1], brings two apparently conflicting requirements into close proximity: decoration ought to be subordinate to construction, yet a well-formed design does not admit removals that leave it equally good. Propositions 14–15 also give colour an articulating role in distinguishing and developing form. Jones is not writing about feedback networks. His difficulty is interesting on its own terms: the distinction between construction and ornament does not entail a test of dispensability. A useful distinction for us is between a hierarchy of design decisions and a hierarchy of causal dependencies. They need not agree.

Loos's *Ornament und Verbrechen* [S2] makes an economic objection: the labour of carvers, turners and textile craftspeople is undervalued, and decorative fashions can make serviceable objects prematurely obsolete (printed pp. 282–285 of the 1962 edition, especially p. 282 following the page marker; online page /283). His argument embeds racist and evolutionary hierarchies (opening pp. 276–277), which we reject rather than translating into a ranking of cultures or tastes. The editor's note locates a 1910 lecture despite the text's 1908 heading. Neither chronology nor Loos's numerical labour assertions are relied upon here. His economic challenge deserves an answer independent of his historical ideology: making every ornament computationally expensive merely to claim it is essential would not be a defence of ornament, but a way of holding the user hostage.

Kant's *Critique of Judgment* §14, Akademie 5:226 [S3], distinguishes ornaments added externally from intrinsic constituents and argues that they contribute to taste through form rather than mere charm. The adjacent §15 explicitly distinguishes beauty from perfection and utility. Therefore our causal example cannot refute Kant: it can expose a problem with assuming that the audible extent of a computational object already defines its internal constituents. The aesthetic and mechanical questions have different domains.

Lisa van Sorge's 2025 article [S4, §3, paragraphs beginning with the narrow sense of parergon and ending with the discussion of supplementary work] reads Derrida as questioning the presumed boundary between the work and its frame. Her discussion of contemporary painterly practice also moves toward embodied framing, not a purely detachable physical border. That is the secondary encounter here; Derrida's complete *Truth in Painting* and Merleau-Ponty's primary works have not been read. Our own intervention is deliberately modest: can an interface label a component peripheral while placing it inside the very equations of a presented work? The border becomes an authoring decision rather than something we can infer from the audio mixer.

The musical warning comes from Colin Booth's 2014 abstract on single-note ornaments in the *Goldberg Variations* [S5]. He discusses C. P. E. Bach and Quantz's expectations of embellishments not fully specified in notation. The abstract also describes J. S. Bach's greater prescriptiveness in some movements. The full article was inaccessible; no claim about an individual variation's realization is made. The relevant possibility is that a competent musical practice can require material absent from a literal reading of the score. An unnotated gesture need not be an arbitrary addition.

### Interpretation: three acts of removal

There are three different tests one might perform on a musical component:

| Intervention | What changes? |
|---|---|
| Mute the observation channel | The observer does not directly receive that component. |
| Disconnect the component | The mechanism's governing equations change. |
| Rewrite the score or convention | What counts as a satisfactory performance can change. |

A synthesizer that calls all three Delete does not merely have an inelegant user interface. It makes certain musical questions impossible to pose separately. A sound artist ought to be free to use all three. In particular, a component can be causal but inaudible in isolation, audible but causally downstream, or aesthetically indispensable without being a necessary part of a specific DSP graph. The last category requires criticism, practice and judgment, not a matrix rank test.

A hypothetical museum of peripheral things would have two galleries. One contains detachable objects. The other contains objects whose removability is not yet known. The visitors have to specify which test of removal they mean before they can carry an object between galleries.

## Formal construction: a branch that prevents a note

Classical tuned mass absorbers provide direct engineering prior art [S6]. We borrow the forced harmonic response, not a claim of invention. Set primary mass and grounded stiffness to 1, primary grounded viscous damping gamma = 0.25, force amplitude F = 1, normalized angular frequency r (frequency in Hz divided by 200). Each branch j has mass m_j, spring k_j = m_j*t_j^2, optional coupling loss c_j, natural ratio t_j. X and Y_j denote complex displacement amplitudes. Define D = 1-r^2+i*gamma*r and K_j = k_j+i*c_j*r.

The frequency-domain equations are

    (D + sum K_j) X - sum K_j Y_j = F
    -K_j X + (K_j - m_j r^2) Y_j = 0

Away from zeros in the branch diagonal, elimination yields

    X = F / (D + sum (K_j - K_j^2/(K_j - m_j r^2))).

At r = t_j for a lossless branch, its equation reduces to -k_j X = 0, hence X = 0. If exactly one branch has zero diagonal, other branch responses are zero, and Y_j = -F/k_j. The direct-output channel can be completely silent although that branch has nonzero displacement. Positive grounded damping at the primary does not change this implication; it is relative damping in the tuned coupling that generally lifts this zero. Russell's page describes the classical undamped case and broadly cautions about damping; our equations specify which damping is being varied, rather than applying the warning indiscriminately.

This argument also works for any finite number of distinct lossless tuned branches. Their locations are specified by the spring-to-mass ratios, not by a fixed equal spacing. Coincident lossless branches at their tuning yield a singular system with nonunique individual amplitudes; the renderer explicitly rejects that case. No transient or physical stability result follows from a phasor identity.

Two branches are attached in our score, with masses 1/4 and tuning ratios 1 and 3/2. At 200 Hz, the first branch displacement is -4 and primary displacement is zero. At 300 Hz the second is -16/9 and primary displacement is zero. With no branches, the primary displacement magnitude at 200 Hz is 4. A physically meaningful unit is not claimed: these are nondimensional synthetic equations.

Notice what an audio-output mute does: it does not enter the equations at all. Disconnecting a branch changes the matrix. In a conventional linear system the reduced transfer function already embodies the branch's effects; an efficient DSP implementation can therefore realize the same input/output law without simulating every hidden mass. The purpose of the explicit branch is to expose a different musical interface and an optional diagnostic observation. It is not required to claim novel filtering.

### Counterarguments and controls

- An arbitrary post-filter can make the primary output silent at chosen frequencies with no explicit oscillating side branch. A notch is not proof of this mechanism. The two-channel witness is an explicit model output, not a proof of physical provenance.
- Detuning moves the ideal zero; adding relative branch loss generally fills it. Both controls are rendered. No claim of zero at finite-duration excitation is made: the audio deliberately resynthesizes independent stationary phasors with fades.
- Primary damping is not branch damping. Confusing the two would misrepresent the mathematics.
- Ornament can simply be ornamental. A harmless additive flourish, freely removable, needs no justification through causal importance. Nor is maximal entanglement a desirable interface objective.
- Removing any sound need not alter a listener's inferred phrase or an institution's definition of the work. Conversely a small change can be aesthetically decisive. Neither is tested here.

## Original performance: Five notes and two missing pillars

The score uses five half-second slots at 160, 200, 240, 300 and 340 Hz. Each slot independently renders the real part of its stationary displacement times a sinusoidal carrier with 20 ms fades. A single gain across all recordings is determined by the largest primary or summed branch phasor magnitude, without per-file normalization. This is not physical time-domain simulation or perceptually matched audio.

I. **The unadorned room:** bare primary.
II. **The decorated room:** two lossless tuned branches, primary output only. Slots 2 and 4 disappear exactly in PCM.
III. **The displaced pillars:** branches tuned at 220 and 320 Hz; the original silent slots return.
IV. **The soft joints:** original tuning, relative damping 0.05 in each coupling; the zeros lift.
V. **The conservator's stethoscope:** primary left, summed branch displacement right. At the two missing notes the right channel sounds and left is exactly zero. This is a diagnostic stereo representation, not the acoustic radiation of a physical object.

Run from this directory: python laboratory.py --out audio. Five WAV files at 16 kHz, 16-bit, 40,000 frames each; first four mono, last stereo. No third-party musical material or participants. The direct matrix solver checks the elimination formula over five configurations and 201 frequencies each. The native receipt records errors and hashes; self-check only, no independent review. Do not use Python's -O flag, which removes assertions. Exact sample claims apply to the recorded outputs, not to all platforms' floating-point rounding.

## Instrument exaptation: the Parergon Organ

A sound painter could create modal structures with three independent brushes: a coupling brush paints reciprocal resonator connections; a radiation brush selects what enters the loudspeaker mix; and a score brush determines which frequencies or events excite the resulting structure. A branch may be painted as a decorative frieze on a display while changing the sound of the building. The display ought to make that relationship discoverable rather than deceive the player. The most interesting control is not resonance amount, but whether a branch is only hidden from observation or actually taken out of the network.

A VSTfx could offer a conventional notch-bank implementation with a separate stationary response inspector and explicit branch audition. A VSTi could instead use damped modal dynamics and MIDI excitation. Both would need bounded real-time processing, safe gain, sample-rate-aware integration, state migration and click-free parameter changes. Dynamic frequency retuning requires a real-time design and fresh stability tests; none has been implemented. A CYD interface could show a primary spine, side branches, connection switches and independent audition levels; no hardware work here. A patch format can mark each output tap and each coupling separately.

The second rabbit hole is the ornamental feedback economy: paint where an otherwise inaudible node changes many neighbours, then compare that with a surface of equally numerous audible but downstream nodes. An artwork might offer two different modes of abundance. The costly one involves genuinely coupled resources; the cheap one draws a visually dense interface over a small stable filter. Loos's economic objection returns, but now as an explicit choice rather than a universal ban. A performer can decide whether the expensive machinery is worth its additional intervention affordances.

For MHAC, a disabled decorative layer should have an explicit contract: output muted, processing suspended, or coupling removed. A toy interface study could test whether users predict the effect of mute/disconnect in a nonconsequential sandbox, comparing ordinary routing labels with graph visualization. Outcome: prediction correctness, correction time and false assumptions about the disabled state. Conventional signal-flow documentation may outperform sonification. No operational warning should be vulnerable to this artistic coupling, and no real control or safety claims follow.

### Original fiction: the apprentice

The apprentice brought a plain instrument into the gallery. Its case had two empty alcoves.

The curator filled them with carved objects and asked the apprentice to play. Two notes disappeared.

He removed the carvings. The notes returned.

A critic declared the carvings essential and asked the apprentice to make a third. The apprentice refused. She had not promised that every useful silence must be purchased with an ornament.

## Source and repository boundary

All access on 26 November 2026 by one ChatGPT research agent, source locators and metadata observed at the listed web presentations, no independent human verification. The following are passage-level except S5 (indexed abstract only); no complete books or primary Derrida text claimed.

- S1 Owen Jones, *The Grammar of Ornament*, 1856, general propositions 5–8 and 14–15. [Reading Design transcription](https://www.readingdesign.org/grammar-of-ornament). Primary text in online presentation, no edition collation.
- S2 Adolf Loos, *Ornament und Verbrechen*, in *Sämtliche Schriften*, vol. 1, Franz Glück ed., Herold, 1962, pp. 276–288; selected opening and labour paragraphs and editorial note. [German transcription](https://de.wikisource.org/wiki/Ornament_und_Verbrechen), [individual labour page](https://de.wikisource.org/wiki/Seite:Loos_S%C3%A4mtliche_Schriften.pdf/283). German text read, paraphrase by agent; no scan collation.
- S3 Immanuel Kant, *Kritik der Urteilskraft*, §14–15, Akademie 5:226–227. [Mouseia German text and parallel English presentation](https://en.mouseia.org/texts/kant-judgment/part-13), German passage consulted; Gutenberg direct retrieval failed (503). No translation authority inferred from Mouseia.
- S4 Lisa van Sorge, “Painting as an embodied act of framing: Toward a phenomenological aesthetics with Merleau-Ponty and Derrida,” *Continental Philosophy Review* 58 (2025), 469–489. [DOI 10.1007/s11007-025-09694-2](https://link.springer.com/article/10.1007/s11007-025-09694-2), abstract, introduction and §3 discussion of parergon, especially notes 37–45. Secondary reading of Derrida and Merleau-Ponty.
- S5 Colin Booth, “Bach’s use of the single-note ornament in the Goldberg Variations,” *Early Music* 42(2), 259–272 (2014). [DOI 10.1093/em/cau030](https://academic.oup.com/em/article-abstract/42/2/259/526229), indexed publisher abstract; direct full retrieval failed. Lead, not detailed primary musical analysis.
- S6 Daniel A. Russell, Penn State, [The Dynamic Vibration Absorber](https://www.acs.psu.edu/drussell/Demos/absorber/DynamicAbsorber.html), section “The Classical Undamped Tuned Dynamic Absorber” and text accompanying frequency-response plots, web version updated 2025. Educational secondary engineering account; cited Den Hartog book and original 1928 paper not independently read. No source figures reproduced.

Live main inspected at 495a98ca12bae467a507031f04931aa4254b1866. AGENTS, RAG, programme, runbook, integrity and validation authorities read, 55 recent PRs and 40 open issues inspected, targeted issue searches for ornament, decorative, parergon, frame, embellishment, Loos, scaffolding, antiresonance, absorber, Fano, resonator. #246's body and comments checked: it fixes protected semantic classes and permits ornaments within them. Here a peripheral component changes the mechanism rather than supplying within-class variation. #388/#526 concern graph-resonator observability/cospectrality; #532 concerns paratext; #620 concerns winner-only priority occlusion. Overlap search is bounded and not a novelty proof. New issue #628 read, no comments at intake. No shared files or accepted corpus changed. Draft for mergedown review; local laboratory checks do not establish full repository CI or human acceptance.
