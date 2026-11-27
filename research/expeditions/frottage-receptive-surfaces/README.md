# The Rubbing That Writes Its Own Score

*Receptive instruments, frottage, voice figures and the manufacture of musical surfaces.*

Status: independent exploratory artistic research, 27 November 2026. Refs #746. Not canonical Track E/G evidence, not an empirical result, not a physical model of contact acoustics. AI-assisted reading, interpretation, implementation and self-review; no human reviewer or participant.

## A receptive instrument — original essay

Imagine a museum commissioning a composer to perform a wall. The composer receives three implements: a pin, a short horizontal bar and a square of felt. None can record the wall as such. The pin visits isolated places; the bar brings neighbours into a joint event; the felt averages a small territory. The same wall becomes three scores. The museum asks which is the authentic recording. The composer supplies an inventory of implements instead.

There is an ordinary distinction between an instrument and the material it plays. But the wall, the scanning implement, the trajectory and the conversion from a reading to a note are all necessary to produce this work. An instrument designed primarily to receive may still be highly authored. Selecting what can count as a musical object is a form of composition.

A rubbing is interesting because its surface was not originally designed as a score. A grain, ridge, screw, scar or weathered joint can become notation without anyone requiring the original maker to have composed music. This is not the discovery of latent music in a scientific sense: it is an act of artistic adoption. Nor is the work exclusively attributable to the person who performs it. The contingent material constrains what can happen, without needing to be treated as a conscious collaborator.

There is a danger in calling such a machine neutral. Its field of reception is already an editorial decision. A smooth brush may remove a whole class of differences; a sharp brush may reveal a different class. A machine could give a completely repeatable response to a surface and nevertheless fail to distinguish it from another surface. In art this is productive: a sculptor might make several objects that share one musical reading and diverge when touched by another implement.

The proposed **Frottage Organ** is therefore not primarily a picture-to-audio converter. It is an instrument for composing the relationship between a surface and its reader. The read head, not only the surface, is an authored musical object.

## Source-located encounters

All accessed 27 November 2026 by the assistant via web retrieval. Sources are selective, not a systematic review. No restricted images or full texts are reproduced. Reading levels and attribution are separated below.

- Max Ernst, *The Fugitive (L'Évadé)*, 1926, [MoMA Learning](https://www.moma.org/momaorg/shared/flattened_pages/moma_learning/max-ernst-levade/), object description and paragraphs following the title, plus [MoMA Natural History collection label](https://www.moma.org/collection/works/10056), 2017 gallery label. Read museum text, not Ernst's original 1948 account cited by the museum. The museum describes rubbings of varied materials subsequently elaborated by Ernst into fantastical imagery. The source establishes the technique and artistic practice, not the truth of a theory of the unconscious. Interpretation: the source texture can initiate an artwork without dictating its finished identity.
- Tom Richards, [The Oramics Machine](https://www.daphneoram.org/oramicsmachine/), opening section “Oram’s ‘drawn sound’ synthesis and sequencing system,” and [Science Museum Group object 2010-68](https://collection.sciencemuseumgroup.org.uk/objects/co8188395/oramics-machine-synthesizer), description and Details. Read those passages, not Oram's own technical notebooks. The museum distinguishes painted glass waveform slides for sound generation from parallel film strips for control. Interpretation: the drawing, its scanner and the control grammar are distinct compositional surfaces. The present virtual stencil is not a reconstruction of Oramics.
- Will Montgomery, [Quiet storms: Toshiya Tsunoda](https://www.thewire.co.uk/in-writing/essays/quiet-storms_toshiya-tsunoda), *The Wire*, issue 323, January 2011. Read interview passages from the description of the early archive through Tsunoda's discussion of field, space and orientation, and the Maguchi Bay example. Tsunoda describes attaching contact microphones to structures and the importance of the observer's relationship to a place. His proposed explanation for the bay's vibration is his account, not independently verified here. No recordings auditioned. Interpretation: a measurement can become an artwork partly through its disclosed conditions of acquisition. Do not equate contact microphones, texture measurements and virtual averages.
- Margaret Watts Hughes, *Visible Sound — Voice-Figures*, Century Magazine 42, pp. 37–44 (1891), [MIT-hosted 2014 transcription](https://web.mit.edu/redingtn/www/netadv/SP20140310.html), attributed text from the apparatus description to the closing paragraphs, especially the paragraph beginning “It may perhaps be worth pointing out” and the following discussion of adhesion. Read the attributed transcription, not the original magazine page images. Hughes describes an elastic membrane, powders, liquids and coloured impressions on glass. She explicitly discusses how direction and speed of motion affect spiral marks, and how adhesion participates in other figures. Her statements about what the impressions accurately record and her natural-theological interpretation remain historical author claims, not validated measurements here.
- Rob Mullender, “Divine agency: Bringing to light the voice figures of Margaret Watts-Hughes,” *SoundEffects* 8(1), 122–139 (2019), [journal abstract and references](https://www.soundeffects.dk/article/view/115031). Abstract and bibliographic references only. Particularly relevant counterpoint: the complex voice figures challenge a straightforward attempt to recover sound from a visual artifact. No full-text appraisal or reconstruction claimed.

## A formal construction — the footprint's blind family

Let an n-by-n array X be indexed modulo n in both directions. The virtual head is linear and its reading is exact; this is a toy field of scalar heights, not simulated friction or measured vibration. At every possible starting cell, record:

- P: X[r,c] (point);
- H: X[r,c]+X[r,c+1] (horizontal pair);
- V: X[r,c]+X[r+1,c] (vertical pair);
- S: the sum of all four cells in the 2-by-2 square.

For even n, any column-alternating field (-1)^c a[r] is invisible to H and S; any row-alternating field (-1)^r b[c] is invisible to V and S. Their intersection is the one-dimensional checkerboard family. Each family has dimension n; their sum has dimension 2n-1.

This is exactly the nullity of S over the reals: the cyclic one-dimensional adjacent-sum operator A=I+shift has kernel dimension one for even n (the recurrence x[i+1]=-x[i]), rank n-1. S applies A on both axes, so its rank is (n-1)^2 and its nullity is n^2-(n-1)^2=2n-1. For odd n the recurrence forces x=0, so A and S are invertible. Equivalently, for an odd cycle, one may solve the adjacent sums by an alternating sum of the equations and then reconstruct the rest.

If both H and V readings agree for two surfaces, the difference alternates in both directions, so it equals k*(-1)^(r+c). For even n, a single point reading determines k, and for odd n k is already zero. An exact binary surface (values 0 or 1) admits a nonzero checkerboard difference only if both competing surfaces are the two complementary checkerboards: all positive-difference sites must switch 0 to 1 and all negative sites 1 to 0. Thus H+V leaves exactly one two-member binary fibre for even n and no ambiguity otherwise.

This is an elementary separable linear-operator observation, not mathematical novelty. It assumes every shifted stencil value is delivered with known registration and without noise. No claim about finite noisy precision, a single trajectory with gaps, arbitrary boundaries, or perceptual decoding follows.

A second way to compose the surface is to author a difference in the nullspace. This is not cryptography: the other instruments can disclose the difference, and side information may do so even without them. It is a deliberately shared score with several possible material realizations.

## Executed synthetic laboratory

Run with Python 3.11+ standard library:

```sh
python laboratory.py audio
```

Exhaustive binary enumeration, all 16 + 512 + 65536 = 66064 fields, confirms the exact collision counts:

| n | Head(s) | Distinct receipts | Largest fibre | Surfaces with ambiguous receipt |
|---:|---|---:|---:|---:|
| 2 | Square | 5 | 6 | 14 |
| 2 | H+V | 15 | 2 | 2 |
| 2 | H+V+anchor | 16 | 1 | 0 |
| 3 | Square / H+V / H+V+anchor (each) | 512 | 1 | 0 |
| 4 | Square | 36317 | 30 | 42806 |
| 4 | H+V | 65535 | 2 | 2 |
| 4 | H+V+anchor | 65536 | 1 | 0 |

The count of ambiguous surfaces weights each non-singleton fibre by its size; the largest fibre is a count of distinct binary arrays, not a geometric dimension. No human probability distribution is implied. Exhaustive census checks odd-width recovery, paired-head distinct count and anchored injectivity. Square, paired and point scan differences are asserted on the multilevel audio fixtures.

### Six studies for a borrowed wall

Three 8x8 toroidal surfaces: A has a diagonal three-cell-wide ridge on a base level 3; B adds a signed checkerboard; C adds signed alternating columns. All values are between 2 and 5. A, B and C have equal square receipts and equal H receipts. A and B have equal V receipts; C differs. A and B differ at point level.

Read each head's entire field in row-major order. Each reading is mapped to a 100 ms tile at 16 kHz, mono signed 16-bit PCM. Frequency = 180 + 480 times (sum / (6 * footprint area)) Hz, with a raised sine-squared envelope and a small inharmonic partial. The mapping is authored, not a physical acoustic law. Each study lasts 6.4 seconds.

| Edition | Source/head | Interpretation |
|---|---|---|
| Square A | A / square | First impression |
| Square B | B / square | A different surface, the exact same impression |
| Vertical A | A / V | A narrower implement |
| Vertical C | C / V | Alternating columns reappear |
| Point A | A / P | Individual texture |
| Point B | B / P | Checker modulation reappears |

Two native Python 3.13.5 runs passed; all generated files and receipts were byte-identical across same-runtime reruns. Each WAV header, full PCM readback, bounded amplitude, expected equality/inequality and per-tile rerender were checked. Five distinct complete WAV hashes among six editions. Square A/B SHA-256: 34cfd41cd4e5ffb7acd78c53626cc1ee670b87720644a7b5b0e471dbae88799c. These are original synthesized miniatures, not recorded rubbings. No human hearing test or accessibility evaluation.

Performance instruction: audition the two square recordings without their labels. There is no acoustic difference to discover. Then compare the two point recordings. Imagine a sculptor altering a wall so that the square recording is unchanged but a different head reveals a private score. Finally choose your own path through the surface rather than the supplied raster order.

## The reverse rabbit hole — a print that cannot give back its singer

Watts Hughes's voice figures complicate the apparent symmetry between sound and shape. A singer can produce an image, and an image can be used to produce a sound. The second operation need not invert the first. A beautiful flower in pigment may have participated in the acoustics without being a complete audio record.

Consider an installation with two tables. On the first, a singer produces a mark. On the second, a performer reads it with a stylus and supplies a new sound. The resulting sound writes another mark. The exhibition is a chain of adoptions rather than a chain of recoveries. A provenance label may state the specific operations in the chain without claiming that any returned sound is the singer's historical voice.

A possible digital experiment uses independent write and read kernels on a bounded persistent field, with successive translations, decay and saturation. It must declare clipping, stability and exact state history if it is to support replay. The present model has no feedback or writing dynamics. In a later artistic instrument the write kernel could be driven by an envelope follower, the read kernel by XY position, and a retained dry input available separately. A system that converges to a repetitive fixed point is not inherently less artistic, but a system intended to reveal historic information must distinguish a new realization from recovery.

## Exaptation and counterarguments

The Frottage Organ VSTi would separate editable texture, read head, scan trajectory, scan clock and pitch/timbre mapping. Initial prototype: 32x32 bounded scalar field, XY cursor, selectable 1x1/1x2/2x1/2x2 stencils, row-major or free path, interpolation toggle, independently audible reading and raw point reference, preset and gesture export, bounded interpolation and deterministic offline render tests. The musical object would be an authored field and a performance path rather than a fixed note sequence.

A VSTfx **Second Impression** could turn supplied event amplitudes into a texture and read them with alternative kernels; it would not imply inverse reconstruction of the original input. CYD **Grain Atlas** could use a touch cursor with a visible head footprint, coarse/pair/point audition, color-coded latent fields and explicit export of the scan history. FM-1 **Rubbing Ratio** could map local height to carrier pitch and the difference of two readings to an FM ratio or depth. These are proposed implementations only, not qualified products.

For MHAC operational design the practical distinction is between a true report of a specified measurement and a true report of the underlying state. A sensor can be correct and still blind to structured changes. A future synthetic benchmark can cross known footprint, path coverage, exact or rounded readings, and target decision (aggregate vs cell-specific). Include complete state tables and explicit sensor metadata as baselines. Measure correct decisions, abstention, false identity, latency, coverage and interpretive burden separately. No advantage for acoustic presentation established.

Counterargument: calling a material a collaborator may erase the actual labour that made it, or attach agency to a deterministic input. Do not convert this metaphor into an ontology. A physical rubbing is not necessarily linear or registered; real contact, friction, resonances, pressure and materials matter. Virtual texture scanning also lacks the resistance and contingency that make physical frottage interesting. These differences motivate instrument experiments rather than validation by analogy. A conventional visual matrix and known measurement kernel solve the narrow synthetic inference problem.

### Original afterword: the catalogue of implements

The conservator asked for the song of the wall.

The musician placed a square of felt upon the table.

The conservator asked for another wall.

The musician exchanged the wall and kept the recording.

A visitor borrowed a needle.

The museum made a new catalogue entry, not for a second recording of the wall, but for a different manner of touching it.

## Reconciliation and delivery boundary

Read current root AGENTS, README, research README, RAG, PROGRAMME, AGENT_RUNBOOK, RESEARCH_INTEGRITY and VALIDATION; no nested expedition instructions found at research/expeditions/AGENTS.md. Recent 40 PR titles and 30 active issue titles surveyed. Targeted issue searches for frottage, Oram, contact microphone, optical sound, raster, eidophone, cymatics and stencil yielded no earlier direct match in returned results. Abandoned restoration/patina and instrument resistance because of #222/#374/#406/#606. The existing directional tomography #690 concerns channel identification by prior/curvature sweeps; this expedition instead studies local spatial footprint cancellation and musical adoption. Search coverage is bounded, not an originality guarantee. New issue #746 was created and its empty comment list checked. The user-requested exploratory scope is disjoint from frozen protocol and canonical source registry. Fresh branch from live main, only two additive files; no shared manifests or protected state changed. Full repo checks and independent review outstanding; retain draft for mergedown qualification. No new licensing or human gates asserted.
