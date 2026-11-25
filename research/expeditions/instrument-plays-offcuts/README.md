# The Instrument That Plays Its Offcuts

**Expedition #548 · 25 November 2026 · exploratory humanities/art, not frozen Track E/G evidence.**

## Contents

1. [The workshop](#1-the-workshop-has-two-outputs) — residual material as a second creative domain.
2. [Source encounters](#2-source-encounters) — historically situated art and design readings.
3. [Exact construction](#3-exact-construction-the-offcut-is-a-constrained-complement) — the finite clipping ambiguity.
4. [Sound construction](#4-native-sound-construction) — executable audio witness.
5. [Second workshop](#5-the-second-workshop-a-playable-instrument) — Offcut Loom proposal.
6. [Transfer and limits](#6-transfer-and-limits) — competing explanations and scope.
7. [Reconciliation](#7-reconciliation-and-qualification) — repository and verification receipt.

## 1. The workshop has two outputs

A carpenter cuts a shape out of a sheet. The client buys the shape; a second artist buys the sheet around it. Neither gets a derivative illustration of the other's object. They acquire complementary objects whose relation is a consequence of the cut.

Suppose an electronic musician uses a digital operation that discards something. A limiter, a spectral mask, a gate, a rounding operation: each has its own specific account of what is retained and what is not. Can the discarded component become a second instrument, while the principal operation remains unaltered? Instead of asking a composer to make a new sound from scratch, give them a *right to collect* from a process already taking place.

The word waste describes a destination, not an intrinsic property of a sample. Yet it would be equally reductive to declare all waste precious: the artist must have the option to discard it. The distinction between remainder and residue is useful here. A remainder is something left by a defined operation; a residue is what an artist or investigator elects to keep. The distinction is stipulated for this essay, not a dictionary claim.

## 2. Source encounters

All accessed 2026-11-25 by this AI assistant; web reading of the listed passages only. No independent reviewer, participant study, reproduction of source artworks, or complete book reading. Museum descriptions are secondary curatorial accounts, not substitutes for artists' statements.

- **Kurt Schwitters, Merz Picture 32 A. The Cherry Picture (1921).** [MoMA collection record, object 27.1954](https://www.moma.org/collection/works/33356), medium and the interpretive passage beginning with the collected scraps. The work incorporates disparate printed and physical material onto a pre-existing painted substrate; the curatorial account notes an ordering grid. [MoMA Dada audio transcript](https://www.moma.org/audio/playlist/198/2638), Umland and Dickerman's remarks, provides historical framing concerning postwar fragmentation. Interpretation: collecting surplus is not enough; assemblage entails ordering, juxtaposition and new relations. The historical rupture is not equivalent to a digital clipping error.
- **El Anatsui, Dusasa II (2007).** [Met collection record, 2008.121](https://www.metmuseum.org/art/collection/search/495553), introductory three paragraphs and medium. The museum describes repurposed bottle closures formed and joined with copper wire, connecting the work to textiles and consumer culture; the title is associated with collective production. Interpretation: a new object can preserve the significance of an earlier material without reproducing its former use. The labor, histories and cultural situatedness of this sculpture cannot be reduced to a lossless transform; do not claim the audio experiment reproduces them.
- **John Cage, An Autobiographical Statement (1990; first printed 1991).** [John Cage Trust](https://johncage.org/cage-autobiographical-statement), paragraphs beginning with his assistance to Fischinger, his reservations about communication, and the preparation of a piano at Cornish for Syvilla Fort. Cage retrospectively links changes to the instrument with practical constraints of space; he also rejects an account of musical purpose founded solely on communication because audience responses differed from his intentions. Interpretation: a technical impediment can become the material of a composition. His account is retrospective testimony, not evidence of an acoustically universal meaning or a demonstration of priority.
- **Grandmaster Flash's Technics SL-1200 MK2.** [Smithsonian object nmah_1301251](https://www.si.edu/object/nmah_1301251), Object Details / Description; indexed collection text read, direct alternative museum URL returned HTTP 500. [Marked record nmah_1301249](https://americanhistory.si.edu/collections/object/nmah_1301249), indexed Description (Brief), reports physical marks and use in scratching; direct retrieval failed. Interpretation: playback apparatus and its material can become performance apparatus. Hip-hop history is not explained by the mere availability of a mechanical affordance, nor is it synonymous with Cage's practice.
- **Alan Dix, Designing for Appropriation (HCI 2007, pp. 1–4, DOI 10.14236/ewic/hci2007.53).** [Author's web summary](https://www.alandix.com/academic/papers/HCI2007-appropriation/), Abstract and Guidelines for Appropriation: provide visibility, expose intentions, support not control, plugability and configuration. Summary read at passage level; not the final PDF. The possibility of designing to permit unanticipated uses is distinct from predicting those uses. Interpretation: an exposed diagnostic tap can be creatively useful even if its original engineering purpose was not musical. Counterpoint: an interface that exposes everything can burden a user or make essential constraints obscure.

## 3. Exact construction: the offcut is a constrained complement

For integer samples x with |x| <= 2T, define y = clip(x,-T,T) and e = x-y. Then x = y+e exactly. If |y| < T, e=0. If y=+T then 0<=e<=T, and if y=-T then -T<=e<=0. Conversely every such pair (y,e) gives an admissible input x and clips to y.

For a fixed length-N output with k samples at the two clipping boundaries, its preimage has (T+1)^k members: choose each admissible residual independently at boundary samples, and nowhere else. Thus a primary signal with no saturated samples has a unique input in this model. A primary signal entirely at the boundary has the maximum ambiguity. These are sample-grid counts, not estimates of real waveform distributions or a new result in signal processing.

For T=4 and N=4, exhaustive enumeration of 17^4 = 83,521 input tuples yields 9^4 = 6,561 output tuples. Every individual fiber size agrees with the formula; maximum size 625. Native Python checks the reconstruction and sign/support invariants on every input. Boundary equality is included even if actual excess is zero. This is a lossless decomposition only when both outputs are retained unmodified and represented with adequate numerical headroom.

**Interpretation:** the principal signal dictates the places at which the second performer may sound. This is not independent polyphony; it is a score for an asymmetric collaboration. A sustained saturated plateau is a window for composing the offcut. A fully interior signal is an instruction to the second voice to remain silent. Removing the restriction by processing the offcut creates a new work; it no longer certifies the original input.

A useful opposition: an engineer might treat the residual as an error to minimize, an artist as material to cultivate. Neither definition changes the algebra. Do not turn this into a claim that all error is art or that error-free engineering is undesirable.

## 4. Native sound construction

Run `python3 laboratory.py` to generate six original mono PCM WAVs, four seconds each at 16 kHz, and a receipt. Two input signals share an identical clipped eight-note carrier. One has residual magnitude modulated at 3 Hz, the other at 37 Hz. Residuals are sign-constrained by the carrier and zero off its saturated support. This is deliberate constructive synthesis, not an analysis of an ordinary commercial limiter. The first and second input files differ; the principal files are byte-identical; the offcut files differ. Sample-wise recombination of principal and offcut equals the original input. Readback, bounds, and same-environment rerender were checked. No listening trial, listening quality ranking, cross-platform hash reproducibility or physical limiter behavior is claimed.

A frequency-domain variant would use an explicitly defined complementary mask, preserving a dry path and reporting phase/delay alignment. Stateful gain reduction would require a sample-aligned reference; casually subtracting a delayed wet signal from an undelayed dry signal is not an isolated record of the gain reduction. The toy avoids such ambiguities by defining an instantaneous integer map.

## 5. The second workshop: a playable instrument

**Offcut Loom** (proposed): a two-bus processor with explicit audition of dry, accepted, and rejected components, and a separate creative bus derived from the latter. The performer controls threshold, mapping of magnitude/sign into other oscillators, delay and grain capture, and whether the rejected material is discarded. Use conservative output levels and finite feedback gains. A reconstruction mode must be exact or declare the error; artistic processing and gain normalization break that mode and must be marked as such.

A second stage could process the first offcut. For any sequence of exact decompositions x_i = x_(i+1) + e_i, telescoping gives x_0 = x_n + sum(e_i). This is arithmetic, not conservation of acoustic energy: component energies need not add. The hierarchy could become a sample library of the successive decisions of a signal chain. Alternatively, choose a process that discards residuals permanently. Do not secretly preserve discarded data under the promise of removal.

The most interesting UI may not be a graph of the waveform. It may be a pair of equally visible meters and a routing surface: the user can send a rejected part to a resonator, a rhythm generator, or nowhere. A performer can then make the main path sound deliberately plain while the other path carries its own intricate articulation. Ordinary difference routing, waveshaping, parallel processing and digital null tests already provide most of this machinery. The possible contribution is a compositional interface rather than a new DSP primitive. If a two-track DAW patch makes the same experiment easy, use that rather than build a plugin.

## 6. Transfer and limits

MHAC might investigate a diagnostic side channel that exposes why a renderer suppressed an otherwise eligible representation. A safe toy comparison could compare an ordinary event list, explicit omission metadata and optional residual audition under identical state/event fixtures. Outcomes: identification of omitted event identity, mistaken interpretation of diagnostic sounds as live actions, extra inspection time. The acoustic residual of clipping is not necessarily evidence of a semantic omission; the two models must not be conflated. The main operational channel must remain correct and sufficient. No new alert policy, participant work, or production deployment is proposed.

The analogy with sculpture ends where the model begins. The integer complement is exactly defined, its source history mostly known, and its possibilities finite. Discarded material in human art has histories and meanings that cannot be represented by that complement. Conversely, the mathematics establishes no aesthetic virtue. A composer may find the untreated remainder tedious.

## 7. Reconciliation and qualification

Read live AGENTS.md, RAG.md, README.md, research/README.md, docs/PROGRAMME.md, docs/AGENT_RUNBOOK.md, docs/RESEARCH_INTEGRITY.md and docs/VALIDATION.md. Reconciled 60 recent PR titles, 40 open issue titles and targeted searches (appropriation, prepared piano, turntable, byproduct, seamful, residual synthesis, clipping residual, null test, feedback, Simondon). Read issue #548 and its empty comments. Base main 495a98ca12bae467a507031f04931aa4254b1866. Existing #270 addresses skill compatibility/appropriation, #516 retained deletion chronology, #484 balanced saturation, #477 hysteresis; this work concerns a complementary contemporaneous signal, not a historical scar or dynamic saturation convergence. Search is bounded; no exhaustive novelty claim. Explicit current expedition instruction permits the parallel exploratory lane, not advancement of the frozen foundational corpus. Fresh issue branch, additive isolated directory, no shared records changed.

AI-assisted author and verifier: ChatGPT, single assistant, 2026-11-25. Native Python executed locally; no independent external review. Full repository checks and integration review remain pending. Draft/HOLD. See [score](SCORE.md) and [execution receipt](RECEIPT.md).
