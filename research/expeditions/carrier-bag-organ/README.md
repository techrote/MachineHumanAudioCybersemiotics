# The Score That Does Not Know It Is Being Recorded

**Expedition:** Carrier Bag Organ · 2026-11-26 · [issue #731](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/731)  
**Status:** exploratory interpretation, original artistic research and a qualified synthetic renderer; not selected empirical evidence, a scientific conclusion, or a production instrument.

## A room instead of an arrow

Imagine an instrument maker asked to compose the soundtrack to a settlement on a moon. She is given four channels: a pump, a greenhouse, a clock that has lost its face, and a person doing some work for which nobody has yet invented a word. The film director requests a climax at exactly twelve seconds. The instrument maker declines to make the pump responsible for the climax. She also declines to make it stop pumping when the soundtrack ends.

There are at least three clocks: the clock of the settlement, the clock of the recording, and the clock of the editor. The last two can coincide without being identical to the first.

The familiar electronic-music arrangement window is extremely good at representing an object that has a beginning, middle and end. That is a useful affordance, not a mistake. But a second kind of object could be a collection of processes whose relations continue while a listener comes and goes. Its exported recording is a finite edition of that collection. The edition is not the extent of its world.

The principal proposition of this expedition is that the boundary of an observation should be available as compositional material without necessarily becoming a boundary of the observed process.

## Four encounters, and one precedent

**Le Guin — literary interpretation.** In "The Carrier Bag Theory of Fiction" (1986), the passages moving from the novel-as-container to continuing process, and then from heroic technology to science fiction, offer a critique of narrative organized around conquest or resolution. [Text transcription](https://hackneybooks.co.uk/books/479/831/CarrierBagFiction.html), paragraphs beginning "I differ with all of this", "One relationship among elements", and "If, however, one avoids". Read the accessible essay in this unpaginated transcription; a critical print edition and the anthropological works invoked were not checked. The opening prehistoric subsistence claims are not evidence used here. The literary argument concerns gendered exclusions and whose activities count as a story; reducing it to a technique for infinite loops would lose that argument.

An original interpretation: the vessel might be the synthesizer's project file, holding disparate processes in relation, rather than a score describing their arrival at a final destination. A work may contain conflict without making every participant subordinate to its resolution.

**Anna Lowenhaupt Tsing — source claim and interpretation.** [Publisher-hosted excerpt from The Mushroom at the End of the World](https://press.princeton.edu/ideas/a-look-inside-the-mushroom-at-the-end-of-the-world), 14 June 2021, from the passages beginning "The concept of assemblage is helpful" through the discussion of agriculture and supply chains. Read this excerpt, especially the discussion of simultaneous temporal projects and unplanned coordination. The full book and underlying ethnographic evidence were not appraised. Tsing invokes polyphony to explain a method of noticing distinct lifeways and their interactions. The reverse analogy is interesting: could a musical patch be constructed so that the listener must discover its different temporalities rather than being led along a single principal line? Her argument about ecology and political economy is not evidence that an oscillator is a living or social agent.

**Pauline Oliveros — artistic practice.** [Center for Deep Listening, Deep Listening](https://www.deeplistening.rpi.edu/deep-listening/), indexed full passage under "Pauline Oliveros on Deep Listening", excerpt from "Quantum Listening: From Practice to Theory (To Practice Practice)", December 1999. Direct page retrieval returned 502; the indexed passage was available, including Oliveros's discussion of broad and focused listening. [About the Center](https://www.deeplistening.rpi.edu/about-us/) supplies institutional context. No original workshop participation or independent verification of claimed benefits occurred. The listener might enter and leave a field of sounds, choosing where to direct attention. This differs from composing a field that automatically directs attention on the listener's behalf.

**Christian Wolff — contingent performance.** [Interview with James Saunders](https://www.james-saunders.com/interview-with-christian-wolff/), conducted 22 November 2004–15 April 2005; published in The Ashgate Research Companion to Experimental Music (2009), pp. 359–368. Read the first interview exchange, especially the answer about the 1957 two-piano work with Frederic Rzewski: a shared temporal scaffolding contained individually chosen material, and performers' choices influenced one another. This is a useful contrast rather than an identical precedent: that piece explicitly starts and finishes together. The Carrier Bag Organ instead separates the local material from the observation deadline. The present software does not reproduce Wolff's interpersonal responsiveness or a live human ensemble.

**Brian Eno — technical and artistic precedent.** [Smithsonian Magazine, Music for Airports Soothes the Savage Passenger](https://www.smithsonianmag.com/arts-culture/music-for-airports-soothes-the-savage-passenger-116079759/), passage introducing and reproducing the album liner notes; [MusicRadar analysis](https://www.musicradar.com/artists/the-album-was-played-in-laguardia-airport-for-a-brief-period-in-1980-but-travellers-said-it-induced-unease-and-sounded-like-funeral-music-a-music-professor-breaks-down-brian-enos-ambient-1-music-for-airports), background section. Consulted these secondary presentations, not an original physical album or the recordings. Ambient practice and asynchronous tape loops are clear prior art for sustained musical environments; no novelty claim about looping, open forms or ambient music follows from this expedition. The specific design question is the explicit distinction between an output window, a world clock and an editorial ending, with auditable PCM consequences.

## A proposed distinction between three kinds of ending

| Operation | What ends | What need not end |
|---|---|---|
| Stop recording | The capture interval | The synthetic process |
| Perform an ending | An authored sequence or envelope | Other local activities |
| Terminate a process | Its execution | Other processes or the archive |

An ordinary transport button can intentionally combine all three. The proposed instrument exposes them independently. A DAW plugin should still respect the host's transport, resource limits and user expectations; it should not clandestinely continue recording or computing when stopped. Continued time can mean a deterministic virtual clock or explicit saved state rather than perpetual background work.

The recorder is not necessarily a narrator. A fade is not necessarily a state transition. A clip ending is not a receipt that the event represented by the clip has resolved.

## Constructed laboratory: a room of four local rhythms

The original [laboratory](laboratory.py) generates four oscillator voices with local periods of 2.3, 3.7, 5.1 and 7.3 seconds. Each cycles through its own small pitch inventory and finite envelope; offsets allow activities already in progress at the first sample. A fifth, invented 311 Hz voice is modulated by the product of two of the envelope values. It appears only during a specific conjunction of activities. This is a compositional relation, not a physical intermodulation model or simulation of living agency.

Each stereo sample is computed at an absolute integer sample index. In the implemented model there is no hidden mutable state; no voice knows the requested export duration. There is no peak normalization using the entire export, no post-window phase reset, and no default closing fade. For a fixed configuration, define F(n) as the quantized stereo frame and W(a,b) as the sequence of frames for a <= n < b. Then W(a,c) = W(a,b) concatenated with W(b,c), for 0 <= a <= b <= c. The identity is immediate from the definition, not novel mathematics. It supplies a testable contract. A conventional endpoint-dependent envelope is a constructive negative control: it can intentionally violate the contract without changing the underlying F.

This is a very narrow example. A persistent stateful DSP engine would require an initial state, deterministic event stream and exact checkpoint/replay policy, or a capture buffer. A true feedback process generally cannot be evaluated at an arbitrary offset simply by supplying the sample index. A wall clock is not required; a virtual sample index is sufficient. Edits, quantization changes, nondeterministic scheduling, cross-runtime differences, and changes in configuration invalidate unrestricted equality claims.

### Executed self-qualification

Run with Python 3.11+ and the standard library: `python laboratory.py`. Output is generated under the script's local audio directory. No external audio material, dependencies, devices or participants.

Native Python 3.13.5 run and repeat on 2026-11-26: PASS. All generated receipts including file hashes matched on rerender. Exact stereo frame checks: 192,000 frames of 12-second export match the start of the 24-second export; 192,000 frames of independently rendered interval [7,19) seconds match the corresponding long-export slice; 32 seeded short windows match; empty/invalid intervals handled; editorial ending preserves the first ten seconds but changes the tail and ends at zero; ablation changes only the equal-channel encounter contribution, and has zero difference outside the stipulated overlap. WAV headers, complete PCM readback, amplitude bounds and distinct full-file hashes checked.

| File stem | Frames at 16 kHz | Peak absolute PCM | SHA-256 |
|---|---:|---:|---|
| room-24 | 384000 | 4241 | a9dd4bb26ca72c2b0189fc1148ccc06e0a0ecd088fe1179450638ace0dfb543e |
| room-12 | 192000 | 4062 | 183bea089dad15aea6e944442db77aceed8799d42ed703a1362be15bb3750b16 |
| window-7-to-19 | 192000 | 3780 | 67953595798fce02b864474df6f45a440e6fbabafedd1afd4c33a9d3f562efb8 |
| editorial-ending | 192000 | 4062 | 5daa4a5caf44af41d5fce833ae54a9c5b7572dd69e036e4fa3c4529c900be7df |
| without-encounter | 192000 | 3458 | 3881da8a0dbf4d45e052ad3f4061bdeecca055c1808ba1c2daca6fe826516778 |

These are same-runtime software observations; they do not establish human perceptions, aesthetic quality or portability of the exact hashes across mathematical libraries. No listening experiment, perceptual rating, participant recruitment, firmware or VST implementation took place. The source blob read back from the repository matches the locally executed Git blob 1cf4ea0c9b96a5d68251e924c3825af29de76808.

### Original performance instructions: Three doors and an editor

1. Hear Room for twelve seconds. When the recording ends, write down one activity you imagine continuing.
2. Hear the twenty-four-second edition. Do not attempt to reconcile the note you wrote with every subsequent sound.
3. Enter at the seventh second. Treat this entrance as a door, not a first event.
4. Hear the twelve-second editorial edition with the closing fade. Consider whether the apparent ending belongs to the room or to its presentation.
5. Hear the edition without the encounter voice. Listen for a relationship rather than a missing protagonist.
6. In a live performance, give each musician a recurring local task, and let the audience choose when to leave. If a performer ends a task, the others need not end theirs. An audience member may request an explicitly labelled coda; the coda is an optional collective performance, not proof that the prior processes reached completion.

These are artistic invitations, not instructions to participants in a research study. The digital files contain abrupt window boundaries by design. A practical player may apply a very short monitor-only de-click ramp; an invariant capture must remain available separately.

## The next rabbit hole: a collection that cannot be curated by loudness

A container does not guarantee hospitality. A bag may be designed for one kind of object; a mixture may mask a quiet signal. The artist's desire to remove a principal voice can itself become a new imposed hierarchy. Equal amplitude does not mean equal attention, equal audible salience or equitable participation.

There is a productive disagreement between making a quiet voice intelligible and making its volume compete with everything else. One future design could reserve a listener-controlled private monitor, indexed by local activity, instead of boosting that voice in the public mix. The monitor is an observation operation. A separate "remove process" control is an intervention. In a coupled patch these may have different effects: muting the monitor of a voice need not stop it driving the encounter oscillator. Conversely, disconnecting the modulation edge may leave the voice audible but remove its influence.

The repertoire of possible relations is more interesting than a global fairness score. Let a process support, interfere with, ignore, or coexist with a neighbour. Let the connection itself be an editable object. Do not require every neighbour to interact. Do not infer cooperative behaviour merely from simultaneous sound. The particular histories of these relations could be saved as a composition, rather than collapsing them into a single protagonist's trajectory.

## Instrument exaptation

| Candidate | Mechanism and acceptance boundary |
|---|---|
| Carrier Bag Organ (VSTi) | Local-clock motif bank with explicit world, transport and clip coordinates, static headroom, optional encounter buses. First native check: exact chunked versus continuous render at a fixed configuration; host stop must release resources as specified. |
| Window / Coda (VSTfx) | Capture given audio into bounded buffers; separate raw capture, monitor-only smoothing and explicit presentation fade. Cannot recover material outside the recorded window. |
| Settlement (CYD) | Touch landscape with locally cycling populations, independently painted clocks and selective monitor. At first, no global beat or global end; explicit freeze/save and restore. Requires actual embedded performance qualification. |
| Carrier patch (FM-1) | Candidate local clocks driving FM ratio, envelope and modulation changes. Clock coordination remains independently editable. Hardware limits and firmware feasibility unknown here. |

A richer version could replace the fixed pitches with patch-local deterministic random streams, variable-duration tasks, nested communities, and explicit causal edges. The sample clock would continue as a coordinate, not as a common aesthetic beat. A local event count might be a better editing address than global time. Changing a voice's future should not retroactively change a saved edition. State snapshots must record pending events and modulation state; raw capture and reproducible reconstruction must not be conflated.

## MHAC implications and critical boundary

Operational systems can have numerous simultaneous lifecycles. A request completed, one warning cleared or a recording stopped does not establish that other obligations have ended. A concise interface should not invent a global completion merely to close the musical phrase. Conversely, urgent tasks must not become subordinate to an artistically open-ended interface.

Testable candidate: a synthetic event-log task contains several independent obligations and explicit clear events. Compare a conventional textual state table, serial notifications, and optionally an audio presentation with independent scoped lifecycles. Vary the observation interval independently of real clear events. Measure false global-clear decisions, correctly identified outstanding obligations, action selection, abstention, latency and workload. Include an explicit text baseline that simply lists all active obligations, and a negative control with matching closure sounds on two different underlying states. The straightforward state table may completely solve the problem. No acoustic benefit has been demonstrated. This is not a change to the frozen protocol or a finding about Brier.

## Speculative coda

The settlement's archive contained twelve seconds of the pump.

The historian labelled the thirteenth second "after the pump."

The greenhouse refused the classification.

A technician made three buttons: CLOSE THE WINDOW, END THE SONG, STOP THE PUMP.

The first two were installed in the theatre. The third stayed in the machine room.

## Provenance and handoff

AI-assisted research, original writing, implementation and software self-check by ChatGPT on 2026-11-26. No independent human reviewer, coauthor, license grant or empirical validation. Source locators and access limits are given above. Repository authorities AGENTS.md, README.md, RAG.md, docs/PROGRAMME.md, docs/AGENT_RUNBOOK.md, docs/RESEARCH_INTEGRITY.md and docs/VALIDATION.md were consulted. Base main: 495a98ca12bae467a507031f04931aa4254b1866. Reviewed 40 recent PR titles and 30 active issue titles; targeted issue searches for carrier bag, Le Guin, assemblage, refrain, nonteleological, intervention, solo and interruption. No carrier-bag title/search match was returned; not a comprehensive novelty audit. Distinguish existing #548 (offcuts), #238 (coalition-dependent attribution), #388 (graph intervention), #456 (interrupted dialogue), #657 (retrospective metre) and #721 (observation scale) from this explicit capture-window versus process-ending contract. No changes to canonical records, protocols, manifests or other workers' files. Draft/HOLD until mergedown review and exact-head repository checks. Full repository validation not run locally.
