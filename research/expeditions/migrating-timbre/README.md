# The Migrating Timbre
## A sorites for a synthesizer that keeps its name

**Refs #197 · 23 November 2026 · original humanities/formal/artistic expedition.** Not a Track E/G result, a perceptual study, or an accepted interface requirement.

A patch is modified a little every evening. Each morning its creator approves the change on the grounds that yesterday's sound is still recognisable in today's. Eventually the patch bears the original name but sounds radically different. Has anything gone wrong? That depends on what the name promised. A sound artist may have cultivated a lineage; an interface designer may have silently altered a sign.

## Contents

1. [Three philosophical lenses](#1-three-philosophical-lenses) — resemblance, tolerance and score identity.
2. [A finite witness](#2-a-finite-witness) — adjacency does not imply endpoint resemblance.
3. [Four kinds of continuity](#3-four-kinds-of-continuity) — local, anchored, path and institutional criteria.
4. [The stereo piece](#4-the-stereo-piece) — hear a parameter journey beside a frozen reference.
5. [The adaptive patch garden](#5-the-adaptive-patch-garden) — proposed instruments and interface boundaries.
6. [Objections and controls](#6-objections-and-controls) — cases where drift is desirable or harmless.
7. [The conservator of the ninth sound](#7-the-conservator-of-the-ninth-sound) — original speculative fiction.
8. [Source and execution boundary](#8-source-and-execution-boundary) — explicit reading and verification limits.

## 1. Three philosophical lenses

**Wittgenstein, primary text.** In *Philosophische Untersuchungen* §§65–69 [S1], the discussion begins with a demand for the essential common form of language games; §66 examines the shifting similarities among games. §67 uses the image of overlapping fibres: a thread need not contain one fibre running throughout its whole length. There is even a distinction between direct and indirect relatedness in the example of extensions of the concept of number. §68 permits drawing a boundary for a purpose without treating absence of a pre-existing boundary as a failure of ordinary use. This last point matters: the present project can allow open-ended artistic categories and nevertheless specify an exact boundary for a narrowly defined machine contract.

Do not turn these remarks into a theorem that all concepts are connected components of a graph. The fibres are a philosophical image; their relations are not defined by one distance function. Indeed Al Zoubi's 2016 article abstract [S2] explicitly contrasts overlap, sociohistorical extension, and a combined interpretation incorporating relations beyond similarity. That is a substantive warning against our own overly geometrical reading. The full argument was not inspected; the abstract establishes the author's stated interpretive position only.

**Sorites.** The SEP entry [S3, §2] describes the familiar situation in which a vague predicate applies at one end of a finite series but fails at the other, while successive items differ slightly. The apparent tolerance of the predicate creates the puzzle. Its contextualism discussion (§3.3.4) is particularly relevant: treating two values alike when considered together is not automatically a warrant to classify an endpoint independently of that comparison.

Our exact threshold relation is not itself a vague predicate. It is intentionally *crisp*, symmetric and nontransitive. It provides a countermodel to a particular inference from local approval to global identity, not a solution of the ancient paradox. An artist can accept every transition without inconsistency if the approval concerns transitions rather than the enduring membership of a fixed category.

**Goodman.** The SEP discussion of *Languages of Art* [S4, §4.3] describes Goodman's controversial score-compliance account of work identity: a performance can closely resemble another without instantiating the same notated work, while substantially different performances can comply with the same score. On that account aesthetic merit and work identity are distinct questions. The article also discusses objections to the sufficiency of score compliance. We have read the secondary discussion, not Goodman's entire book, and do not attribute our model to him. The narrow transfer is that similarity of realizations and satisfaction of a symbolic contract are independently specifiable.

These lenses resist an attractive but false unification. Wittgenstein's examples invite us to investigate plural relationships; sorites examines trouble with unrestricted tolerance; Goodman asks what warrants identity under a notation. None requires the others to be true.

## 2. A finite witness

Take the nine patches P = {0,1,...,8}, where i denotes a mixture of two oscillator waveforms with weights (8-i,i)/8. Define d(i,j) = |i-j|. This is a metric in parameter space; it is not a psychoacoustic measure. For radius r=1 define R(i,j) iff d(i,j) ≤ 1.

R(0,1) and R(1,2) hold, whereas R(0,2) fails. Thus R is reflexive and symmetric but not transitive. In the graph of admissible edges the full chain 0→1→...→8 is connected. Its endpoint distance is 8, its edge length at every step is 1, and its diameter is 8. The connected-component equivalence relation is therefore not identical to the original threshold relation. Single-link connectivity is a perfectly valid *different* category rule, not proof of universal pairwise resemblance.

The general bound follows by iterating the triangle inequality: for a path of n edges each of length at most r, the endpoint distance is at most nr. On the integer line the monotone chain attains this bound. In this bounded domain, it is also at most 8. Neither an infinite chain nor unbounded feature displacement is claimed.

A missing intermediate item matters. On {0,1,7,8}, the component of 0 is {0,1}, not the full domain. Adding intermediate patches may merge previously disconnected components; the endpoint distance has not changed. This is a useful model of *catalogue-dependent category assignment* rather than an empirical account of listeners.

## 3. Four kinds of continuity

For path x0,...,xn define:
- Local approval L: each adjacent distance ≤ r.
- Anchored approval A: each distance from x0 ≤ r.
- Travel budget B: sum of adjacent distances ≤ b.
- Declared identity I: all events satisfy a named contract; it can be a score, a fixed semantic label, a versioned lineage policy or another explicitly defined rule.

These are independent questions, not four measurements of the same metaphysical substance. The first three are computed in the lab; I is a design choice outside the metric. In particular, b ≤ r implies B ⇒ A and L by the triangle inequality, whereas A does not generally imply L (consider a two-sided excursion around an interior anchor). A small total endpoint displacement does not imply small travel.

With r=1, b=3, the following are exact expectations derived from the model, not listener data:

| Path | All local? | All anchored? | Endpoint | Max anchor | Travel | Within budget? |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 0…8 | yes | no | 8 | 8 | 8 | no |
| 0,1,2,3,2,1,0 | yes | no | 0 | 3 | 6 | no |
| 0,1,0,1 | yes | yes | 1 | 1 | 3 | yes |
| 0,1,8 | no | no | 8 | 8 | 8 | no |
| 0,0,0 | yes | yes | 0 | 0 | 0 | yes |

The closed excursion is crucial. A comparison restricted to the final patch would certify return; an accumulated budget would still record a journey. The two policies answer different questions, and neither should be presented as a universal definition of continuity.

## 4. The stereo piece

**Original artistic experiment.** In the left channel the patch migrates; in the right channel an anchor never moves. Each slot contains 4480 samples of tone and 640 samples of silence at 16 kHz. The two integer oscillators are triangles at 200 and 600 Hz. The mixture changes in eighths, with an integer fade of 160 samples at either end. The endpoint loses the 200 Hz component entirely, so changes in pitch as well as spectral character may be perceived: this is not a controlled timbre-only stimulus. The right channel is a reference, not a measured memory of the listener.

The score is called *The Migrating Timbre* in a deliberately broader artistic sense. The nine-slot outward journey lasts 2.88 seconds. Repeat it with headphones at a comfortable level, or inspect the waveforms; no claim is made that steps are indistinguishable, equally salient, pleasant, or perceived as the same sound. The control score returns to the anchor, while the one-jump score deliberately violates the chosen local radius.

From the repository root, run:

    python3 research/expeditions/migrating-timbre/lab.py --out build/migrating-timbre
    python3 -m unittest discover -s tests -p test_mhac_migrating_timbre_197.py -v

The generator writes five original stereo PCM WAVs and a machine-readable report with exact per-path distances, byte lengths and SHA-256 digests. No binary source, third-party melody, external synthesis library or human data is used.

## 5. The adaptive patch garden

Imagine a synthesizer preset browser that refuses to collapse identity into a single name. Instead it offers three different ways to retain an evolving sound:

**The lineage mode** records a parent edge for each accepted mutation. A musician can deliberately propagate a preset far from the seed. The identity is that of a lineage, not a timbre guarantee. One can fork the garden, compare branches, or discover remotely related patches. The graph of all acceptable adjacencies is not the same as the actual historical parent tree.

**The anchor mode** compares every proposed variation to a pinned reference. This may protect a narrowly specified parameter convention while permitting small changes. It does not establish that the sounds are perceptually recognisable or semantically safe. A better interface would show both the actual parameter changes and a clear declaration of which invariant it is preserving.

**The excursion mode** accumulates total movement and does not reset it merely because the current patch has returned. This can be used creatively as a compositional resource: each movement spends a budget, and the performer chooses whether to return home, branch, or rename. For exploratory art, travel is the material, not the error.

A more interesting future instrument could use a graph whose edges are multi-attribute contracts. One edge preserves envelope, another rhythmic pattern, another semantic role. A walk that switches edge types can lose every original attribute while each transition preserves *something*. A composer could compose these losses rather than simply interpolate a knob. Such a graph needs separate edge-type witnesses, otherwise an attractive path would imply a nonexistent invariant. This is a proposed exaptation, not implemented or validated here.

For an adaptive auditory interface, permit acoustic migration only as explicitly chosen policy. A fixed semantic codebook might retain the same intended role even as the acoustic feature vector changes, while the recipient's interpretation may not. That problem would need empirical measurement and an appropriate risk model. X004 corpus migration (#184) studies textual recurrence; T012 (#51) studies semantic reassignment across mixed codebook versions. Here the feature vectors migrate while the meaning assignment is intentionally outside the toy. X006 (#188) is about operational state restitution under a palindrome, whereas a path budget here detects parameter excursion even after an ordinary return. The joint-witness expedition (#195) is about quantifier scope, not metric nontransitivity.

## 6. Objections and controls

**A narrow metric can be irrelevant.** The chosen distance gives all adjacent parameter steps identical magnitude. Auditory discriminability need not obey that scale. Changing the representation (e.g. log frequency, loudness normalization, spectral distances, context-dependent masking) changes the graph. Metric proofs hold for the stated metric; they do not identify a preferred human similarity function. The synthesis is intentionally not loudness matched.

**Identity need not be protected.** A genre, family or tradition can be constituted by a lineage of changes rather than direct resemblance. An evolving artistic category is not a defective alarm code. The act of drawing a hard boundary can create exclusion or destroy an interesting process. It may be appropriate to allow a family's endpoint drift.

**No theorem of inevitability.** At radius zero only identical patches connect; restricted domains can separate families; repeated bounded movement can remain anchored; the constant path does not drift. The connected component can be small, and the path can return. A budget is conservative for backtracking and can penalize a harmless exploration; an endpoint anchor alone overlooks that journey. Use a rule whose failure corresponds to an actual problem.

**No inferential inversion.** If an interface keeps an exact symbolic meaning invariant, that neither proves its signal stayed identical nor that anyone understood it. Conversely an unchanged waveform does not prove its referent stayed invariant. Our laboratory cannot adjudicate either proposition.

An empirical extension would have to independently manipulate step size, order, anchor availability and comparison delay; collect pairwise versus endpoint similarity judgments and test for drift under controlled loudness, pitch and exposure. That is a research question, not an authorized participant protocol. A contrary result in which listeners consistently retain the anchor despite incremental drift would defeat a proposed perceptual anchoring effect without affecting the finite metric witness.

## 7. The conservator of the ninth sound

*Original fiction.*

The city had one surviving instrument and nine conservators. The first had replaced a reed; the second had changed a spring; the third had removed a bell nobody remembered hearing. Every conservator received the instrument from the preceding one and signed a certificate saying that the change was small.

When the last conservator died, the citizens asked the instrument to play the ancient call that once opened the city gates. It played a sound like a fine metal wire being pulled through a stone.

The gates did not open.

The historian said that the ancient instrument had survived, because every transfer was documented. The machinist said that it had failed, because its old function no longer held. A child said that the sound was beautiful. None had made a mistake about the thing they were judging.

The city commissioned a tenth conservator and gave her two rooms. In the first she could restore anything. In the second she could change anything. Her only obligation was to carry both sounds across the corridor and never file the certificates in the wrong cabinet.

## 8. Source and execution boundary

All source access occurred 23 November 2026 by one AI research agent. No independent human review, empirical screening, claims registry admission or external scholarly validation occurred. Sources below are linked, not reproduced; paraphrases are bounded to the inspected passages. The primary German passage was read via its online presentation; the secondary sources remain secondary. No source claims are offered about Brier or perception.

- **S1** Ludwig Wittgenstein, *Philosophische Untersuchungen*, [online German text](https://www.wittgensteinproject.org/w/index.php/Philosophische_Untersuchungen), §§65–68 and the surrounding §69 discussion as displayed in the [English excerpt with commentary](https://topologicalmedialab.net/xinwei/classes/readings/Wittgenstein/lw65-69c.htm). Primary author text in a web edition, and an attributed commentary/excerpt, respectively. No complete book reading or critical-edition collation.
- **S2** Odai Al Zoubi, “Wittgenstein and Family Concepts,” [Nordic Wittgenstein Review landing page](https://www.nordicwittgensteinreview.com/article/view/3384), abstract, 2016. Abstract only; the full article may qualify the interpretation.
- **S3** [Sorites Paradox](https://plato.stanford.edu/archives/spr2026/entries/sorites-paradox/), Stanford Encyclopedia of Philosophy, Spring 2026 archived version (substantive revision 26 August 2025), introduction, §2 and selected paragraph in §3.3.4 on pairwise consideration. Secondary overview; no assertion that the article endorses a graph interpretation.
- **S4** [Goodman's Aesthetics](https://plato.stanford.edu/entries/goodman-aesthetics/), Stanford Encyclopedia of Philosophy, substantive revision 9 August 2017, §4.3, especially its discussion of score compliance and objections. Secondary account locates *Languages of Art* (1976 edition), pp. 186, 210, 212; original pages not independently read.

Base main: f0927fbf4b20bef2a04b6e1220c7c78edda40e01. No canonical registry, shared protocol or programme state changed. The executable receipt is printed by the dedicated test in normal repository CI; actual run outcome must be checked rather than inferred from the presence of tests. The model, predictions and sound construction are original, synthetic and scoped; all empirical interpretation remains hypothetical.
