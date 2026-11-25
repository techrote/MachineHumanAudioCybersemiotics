# The Choir With No Original

**Exploratory expedition / interpretation and artistic construction; not selected empirical evidence.** 25 November 2026. [Issue #586](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/586).

## The manuscript as an instrument

A librarian brings four surviving scores to a rehearsal. Two contain a raised note at the same place. The editor calls it an error copied from an ancestor. A musician calls it a promising new phrase. The acoustician counts the two pitches. Each has inspected a different relationship. The editorial question concerns transmission; the musical question concerns what can be made from the differences; the acoustic count concerns simultaneous material. None licenses the others automatically.

A synthesizer could make a distinction between a **witness**, an independently situated version of a musical object, and an **edition**, a chosen construction from those witnesses. It would let an artist keep the disagreement intact instead of normalizing it into a canonical parameter value. More unusually, the instrument might deliberately change the relationships among surviving versions while conserving both the inventory of notes at every beat and the number of changed notes in every voice. A listener to the sum would receive precisely the same waveform; a listener to the separate voices would receive a different collection of melodies.

This is not an argument against critical editions. The ability to recover an earlier text can be valuable even when no one proposes that its earlier state is intrinsically superior. A performance can require a reliable score while an archive retains disputed readings. An instrument can make both modes available without collapsing them.

## Source encounters and their boundaries

All readings below are AI-assisted passage or abstract readings, checked 2026-11-25 by this assistant alone, not independent review. No source is promoted into the frozen empirical corpus.

- Philipp Roelli (ed.), *Handbook of Stemmatology: History, Methodology, Digital Approaches* (2020), [University of Vienna record](https://ucrisportal.univie.ac.at/en/publications/handbook-of-stemmatology-history-methodology-digital-approaches/), abstract; DOI 10.1515/9783110684384. **Source account:** the volume distinguishes the practical task of preparing an edition from the investigation of transmission and change. **Interpretation:** an inferred lineage and an editorially preferred realization are different outputs. Only institutional abstract/metadata read; not the full handbook. Heikkilä's chapter [Dealing with open textual traditions](https://researchportal.helsinki.fi/en/publications/dealing-with-open-textual-traditions/), pp. 254–272, is a useful follow-up; PDF request returned 403, so no chapter claim is made.
- Bernard Cerquiglini, *Éloge de la variante*, revised edition (April 2026), [Anacharsis publisher description](https://www.editions-anacharsis.com/Eloge-de-la-variante), paragraphs following edition statement. **Source account:** the description places variation in manuscript copying at the centre of a reconsideration of philology. **Interpretation:** a musical archive might treat divergence as material rather than merely noise. This is a publisher-level encounter, not a reading of the author's argument or a claim about all medieval traditions.
- TEI P5, v4.12.0, 28 July 2026, [ch. 13 Critical Apparatus](https://tei-c.org/release/doc/tei-p5-doc/en/html/TC.html), opening paragraphs and §§13.1–13.1.2. **Source account:** apparatus entries can retain readings from different witnesses, an optional base reading, and distinguish editorial conjecture from witness attestation; editorial grouping choices are not mechanically prescribed. **Exaptation:** retain separately the witness identity, the reading, its alignment and any newly generated reading. A new synthesis could be documented as an editorial conjecture rather than falsely attributed to an existing witness.
- Žanna Pärtlas, “Theoretical Approaches to Heterophony,” *Res Musica* 8 (2016), pp. 44–72, [PDF](https://resmusica.ee/wp-content/uploads/2017/04/rm8_2016_44-72_P%C3%A4rtlas.pdf), §1.2, printed pp. 49–50 (PDF indices 5–6; text and page images inspected). **Source account:** the author distinguishes traditions whose melodic variants are functionally equivalent from practices with differentiated main and accompanying voices. She questions what simultaneous variation means, including the possibility that no one part is a theme. **Interpretation:** a synth may permit several equally authoritative realizations without selecting a sounding original. This does not establish that any of the cultures discussed uses our binary model.
- John Napier (2006), “A 'Failed' Unison or Conscious Differentiation,” *International Review of the Aesthetics and Sociology of Music* 37(1), 85–108, [journal abstract](https://hrcak.srce.hr/en/32872). **Source account:** he emphasizes both musical and socio-musical processes and the limitations of transferring texture terminology across cultures. Abstract only. **Counterargument:** imposing a binary editor may obliterate the actual practice it purports to describe; the proposed apparatus is deliberately a new electronic construction, not ethnographic reconstruction.
- Milton T. Drott, FourgameteP v0.1.0, [R reference manual](https://search.r-project.org/CRAN/refmans/FourgameteP/html/FourgameteP.html), Description and Example. **Source account:** the four-gamete test relies on a model excluding repeated and reverse changes. The manual cites Hudson and Kaplan (1985); their original paper was not inspected. **Mathematical borrowing:** use incompatibility as a diagnostic of a deliberately restrictive genealogy, not as proof of borrowing. No biological or cultural evolutionary claim follows.

## Exact construction: four witnesses and six sites

Each site has two fixed realizations, 0 and 1. Four labelled voices A–D each play one of them at each site. Exactly two voices choose 1 at every site. The hypothetical root has all zeros; it is not a historically recovered score. We stipulate a rooted tree, no horizontal transfer, and at most one irreversible 0-to-1 change per site. The set of witnesses carrying 1 at a site must therefore form a clade: any two such sets are nested or disjoint. Conversely, a laminar family can be realized by nesting the sets in a rooted tree, adding singleton leaves and assigning each site's change at the edge into its clade (multiple changes may share an edge). Thus this is a necessary and sufficient compatibility criterion for this model.

Every balanced column is a two-element subset of four witnesses. Two columns are compatible exactly when their supports are equal or disjoint. There are three complementary split classes: AB|CD, AC|BD, AD|BC. Distinct classes cross, giving all four binary pairs across the four witnesses. Because the sets have equal size, the same split criterion also holds for the corresponding unrooted one-change character model. The root is still a modelling convention, not a privileged musical voice.

| Witness | One split class | Three split classes |
|---|---|---|
| A | 111000 | 111000 |
| B | 111000 | 100011 |
| C | 000111 | 010101 |
| D | 000111 | 001110 |

The second arrangement's columns are AB, AC, AD, CD, BD, BC. Every row has three 1s; every column has two 1s. The first has the same row and column totals. Note-by-note anonymous agreement does not determine genealogy. Nor does an identical sum determine the individual voices.

Let m be the number of sites and n1,n2,n3 the numbers using each split class. The incompatibility graph on sites is complete multipartite, with cross-class edges and no within-class edges. The exact incompatible-pair count is n1*n2+n1*n3+n2*n3. The maximum is floor(m*m/3), achieved by balancing the three counts (moving one site from a larger class to a smaller class increases the count when they differ by more than one). To retain a compatible subset of columns, keep the largest class. The minimum number of columns to **exclude from this analysis** is m-max(n1,n2,n3). Exclusion is an optional analytical operation, not an instruction to erase a score.

For six sites, the first arrangement has zero incompatible pairs and requires no exclusions; the second has twelve incompatible pairs and requires four exclusions. The three possible pairs of incompatible split classes do not count recombination events. A single event might affect several sites; repeated innovations might explain the same data. For example AB and AC can arise by a 0-to-1 change on the A+B clade at the first site, then two separate changes on A and C at the second site. This is a valid history once the one-change restriction is relaxed, with no borrowing whatsoever. Conversely borrowing can leave no detectable crossing. Compatibility does not certify actual descent.

## Executed finite apparatus

Run `node laboratory.cjs` to repeat the bounded tests and `node laboratory.cjs --wav` to produce eight individual stems and the common mix in choir-audio/. The pure computation was executed in an isolated JavaScript environment, not native Node. It examined all 6^6 = 46,656 labelled column arrangements, independently compared support crossing against explicit four-state observations, and exhaustively tested every subset of the six columns for compatibility. 839,817 assertions passed. There were 192 compatible configurations, 5,760 attaining twelve incompatible pairs, and 1,860 meeting the additional requirement that every witness has exactly three variant notes. Maximum-pair qualification covered the full family, not merely the equal-row subset. The two selected musical witnesses meet both margins and attain the two extrema.

Pair-count histogram: 0:192; 5:2304; 8:5760; 9:9600; 11:23040; 12:5760. Exclusion histogram: 0:192; 1:2304; 2:11520; 3:26880; 4:5760.

The synthesis function uses fixed integer PCM samples for each realization of each of six quarter-second slots. It tested 24,000 sample positions per mix at 16 kHz; the two sum arrays are exactly equal, the stem arrays differ, and the sums fit signed 16-bit samples. No WAV export was executed by the JavaScript sandbox, and no listener or physical audio was measured. The Node export branch has readback checks but remains to be executed natively. These are synthetic tests and an original artistic score, not human evidence. The mathematics is elementary set compatibility and a standard four-gamete construction; no priority is claimed.

## An editorial synthesizer

A **Variant Scriptorium** could contain a field of small waveform or melodic objects whose versions remain addressable rather than overwritten. At each site the author would be able to:
- edit the alternatives without changing their identities;
- choose witness paths through the alternatives and audition each complete path;
- show which differences can be explained by a stipulated genealogy;
- introduce local borrowing, independent parallel invention or reversion, retaining explicit event provenance rather than pretending the inferred tree is truth;
- compose a conjectural edition, keeping it distinct from the witnesses;
- use crossing pairs to trigger a second layer of resonance or FM without altering the principal mix.

The intriguing musical switch is between vertical agreement and horizontal coherence. The first compares simultaneous note inventories. The second concerns the particular paths through those inventories. In an oscillator bank, a designer might similarly preserve a framewise spectrum while changing how individual oscillator trajectories move through it. That is a proposed engineering direction, not a proof of invariance when phase, nonlinear mixing, envelopes, or history-dependent effects are present. Our exact invariance assumes additive, phase-reset, identically rendered slots.

The larger instrument should allow nonbinary choices, missing fragments, variant duration, explicit copying and unaligned witnesses. The choice of alignment is itself editorial. Forcing every sound into the same six columns would destroy musical features such as ornaments, shifts of pulse, and silence. The most interesting mode might be one in which there is no privileged base waveform; the named variants establish a temporary family and later split into unrelated works.

## A second rabbit hole: an editor who manufactures a witness

Imagine three versions of an object: 110, 101 and 011. A sitewise majority edition is 111, which is absent from the witnesses. It is not automatically wrong; it might be a useful reconstruction or new composition. It is wrong to label it as an observed witness. Duplicating the first copy a hundred times also changes the weight of that reading without adding a hundred independent origins. A future edition editor could keep documentary observations, source dependence, conjectural constructions, and approved operational revisions as separate objects. A version can be useful without having existed before.

For MHAC, distinguish the current authorized vocabulary from historical examples of it, and avoid generating a hybrid operational command by voting over fragments of incompatible versions. A proposed test uses explicitly versioned synthetic message schemas, comparing whole-version validation, independent fieldwise majority, and an explicit conflict/unknown outcome. Baselines are conventional schema checks and provenance logs. Outcomes: unauthorized hybrid acceptance, false rejection, correct conflict identification, and inspection effort; no human recruitment is authorized here. The failure case could be handled completely by conventional software versioning. Musical ambiguity is not an appropriate replacement for operational meaning.

## Speculative coda (fiction)

The archivist asked the choir to sing the original. Four singers produced a small chord. She asked for the original again and received the same chord. One singer had changed her entire tune.

The librarian hired a mathematician to reconstruct the genealogy. He returned three sheets of paper: on one, two monasteries had exchanged a leaf; on another, a scribe had made the same alteration twice; on the third, the editor had invented a useful ancestor.

The choir asked which sheet was the score.

The librarian put all three in the archive. At the concert she left the original's music stand vacant. It was not evidence that the original had never existed.

## Checkpoint and scope

Read live AGENTS, RAG, programme, runbook, integrity, validation, root and research README; main base 495a98ca12bae467a507031f04931aa4254b1866 at intake. Reviewed 70 recently updated open search results and 40 recent PR titles; targeted issue queries for heterophony, oral tradition, stemmatics, textual criticism, contamination, manuscript and variant/tradition returned no direct matching expedition. Earlier #358 rhythmic translation, #508 enharmonic translation, #530 temporal identity and #520 reversible stereo are adjacent but not this genealogical model; #51 version migration is an operational counterpart rather than displaced work. Search limitations: titles/indexed issue text are not a complete code corpus audit. New issue #586 created, comments empty on inspection. No shared files or canonical manifests altered. Exploratory lane only; no changes to frozen protocol, selected evidence, participant work or operational interface. AI-assisted original writing and software self-checks only; no independent reviewer, no full repository validation or CI result claimed here. Draft for integration review.
