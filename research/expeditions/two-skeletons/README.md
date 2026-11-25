# The Score With Two Skeletons

Musical mereology, incompatible groupings, and the composition of joints.

**Status:** exploratory humanities/art and synthetic mathematics, 25 November 2026. Not a selected Track E/G finding, a Brier reconstruction, or a production feature. Single AI author and self-check (ChatGPT/GPT-6.2); no independent reviewer, participants, or human performance.

## 1. Essay: the joints are not the bones

A composer hands two editors the same sequence of six notes. One draws brackets around successive pairs. The other joins the second to the third, the fourth to the fifth, and the last to the first. Neither changes a note. Both insist that they have marked the composition's parts.

This is not yet an audible disagreement. It is a disagreement about what it would mean to change the piece together. When the editors distribute a little emphasis within their respective pairs, their two otherwise unobjectionable procedures interfere. They cannot decide which result is definitive without deciding whose organization acts last.

There is an attractive distinction between the identity of an event and the identity of a joint. A joint is not simply a mark saying that two notes belong together. It can be a permission to transfer something between them. The permission can be read as a musical resource, like an envelope or filter. One composer writes the notes; another writes the relations that can redistribute their dynamics.

An archival photograph of an assembled skeleton tells us rather little about the movements the joints permit. The musical counterpart is not anatomical science: it is an invitation to store relations separately from realized events. A dormant relation can be artistically important even before it is used. A recording of the original six-note motif could not determine which editable relation map its author kept in the sequencer.

Conversely, it would be a mistake to say that an audience cannot experience organization without an explicit relation map. Hearing the whole and its parts is not equivalent to accessing the sequencer's metadata. A listener may organize the sounds differently from either editor. Three separate questions must be asked: which events did the artist group, which events did the listener group, and which physical sources produced those events? The present instrument concerns only the first; it is not a source separator.

## 2. Source-located encounters and resistance

- **Alejandro G. Di Rienzo (2026), Musical Mereology**, Pacific Philosophical Quarterly 107(2), 58–73, [DOI](https://doi.org/10.1111/papq.70013). Publisher HTML, abstract, §1, opening of §2, ending of §4.1, §4.2 and §5 read; published 27 April 2026. Di Rienzo builds different parthood relations from the successive and simultaneous combination of sound-event types. His conclusion reports departures from classical decomposition and fusion principles. The distinction between types and event tokens is explicit; the article does not offer my graph-edit theory. The discussion of tremolo in §2 is particularly suggestive: granularity can depend on the question under consideration. Our event identities are fixed tokens, a different ontological choice. I did not check the complete axiom system or appendix proofs.
- **James Tenney with Larry Polansky (1980), Temporal Gestalt Perception in Music**, Journal of Music Theory 24(2), 205–241, [author-hosted scan](https://eamusic.dartmouth.edu/~larry/published_articles/temporalhighquality.pdf). Introduction and beginning of §1, printed pp. 205–208, read in extracted text; printed pp. 205–206 also checked visually. They describe hierarchically organized temporal units and discuss the difficulties of making similarity and proximity operational across multiple varying parameters. Their restriction to a tractable perceptual model is instructive. A hierarchy of contiguous time spans, however, cannot simply be identified with my arbitrary pairings of note tokens. This distinction is why I call them edit skeletons rather than perceptual gestalts. No wholesale reconstruction of the paper claimed.
- **Daniel Pressnitzer and Jean-Michel Hupé (2006), Temporal dynamics of auditory and visual bistability reveal common principles of perceptual organization**, Current Biology 16(13), 1351–1357, [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/16824924/), DOI 10.1016/j.cub.2006.05.054. Authors report perceptual alternation with invariant ambiguous auditory stimuli and compare it with visual alternation. The abstract also notes the absence of cross-modal correlation for subject-specific biases. This is a reason not to assume a unified mechanism. Abstract only; no effect-size extraction.
- **Susan Denham, Kinga Gyimesi, Gábor Stefanics and István Winkler (2013), Perceptual bistability in auditory streaming: how much do stimulus features matter?**, Learning & Perception 5(S2), 73–100, [institutional repository abstract](https://real.mtak.hu/5718/), DOI 10.1556/LP.5.2013.Suppl2.6. The authors report transitions among two or more organizations and distinguish the initial percept from later ones. Abstract only. This is a useful corrective to treating auditory organization as a binary switch or stable personality parameter.
- **Stephen McAdams (2024), Processes of auditory organization during music listening**, in Perception and Cognition of Music: The Sorbonne Lectures, pp. 12–43, [publisher abstract](https://doi.org/10.1093/oso/9780198939177.003.0002). Discusses concurrent versus sequential grouping, and relationships among grouping cues and musical textures. Abstract only. It underscores that a pairing model omits both simultaneous grouping and the dependence of timbre and rhythm on organization.

All source metadata and indicated passages were checked by the same AI author using public web access on the expedition date. No source was independently human-verified. Only original paraphrase and links are retained. These are exploratory readings, not systematic review extractions. Di Rienzo's paper happens to predate the frozen programme cutoff, but this note does not amend the programme's corpus.

**Interpretation:** Di Rienzo motivates plural parthood, Tenney/Polansky motivate the operationalization of relations, and streaming research motivates the distinction between invariant stimuli and changing organization. None entails the following averaging model. The mathematical construction is my deliberately small design object, not a derivation of a theory of musical ontology.

**Counterargument:** a graph of editable pairs need not describe any genuine musical part. It may be nothing more than a modulation graph. That objection is correct if the system is judged as a metaphysical theory. The instrument still affords a way to compose relations. If familiar DAW automation groups or an ordinary modulation matrix deliver every useful affordance, no new terminology or architecture is required.

## 3. Exact construction: two perfectly innocent edits

Fix an even number of distinct events. Each has a scalar emphasis value. A skeleton P is a perfect matching: each event belongs to exactly one unordered pair. A second skeleton Q is another perfect matching. Each edit replaces the two values of every pair by their arithmetic mean, simultaneously. No timing, pitch, order or membership changes. This is an offline, complete-score operation, not a causal real-time algorithm.

Represent matchings by fixed-point-free involutions p and q on event IDs. If S_p acts by (S_p x)_i = x_{p(i)}, the averaging operator is A_p = (I + S_p)/2. Each A_p is idempotent, preserves the sum and preserves the initial min/max bounds. The sum is a mathematical scalar budget, NOT audio energy or loudness.

The commutator is (A_q A_p - A_p A_q) = (S_q S_p - S_p S_q)/4. Since distinct permutation matrices differ on at least one basis vector, the averages commute on every input iff the partner permutations commute.

Overlay the two matchings as a two-colour multigraph; shared pairs are doubled edges (size 2 components). All other connected components are alternating even cycles. On a cycle of length 2k, applying the two partner permutations in opposite orders walks two edges in opposite directions. The endpoints coincide iff the cycle length divides four. Therefore:

**The two group edits commute on every score exactly when every component of their overlay has size 2 or 4.** A cycle of length 6 or more supplies a basis-vector witness. This is elementary permutation/projection algebra, not a mathematical priority claim. Particular inputs (e.g. a constant vector) can hide noncommutation even when the operators fail the criterion.

The smallest failing score has six events. With one-based IDs, let P = (12)(34)(56), Q = (23)(45)(61). Start with emphasis at event 1 alone. P then Q gives (1,1,1,0,0,1)/4; Q then P gives (1,1,0,0,1,1)/4. Both outcomes have the same multiset of values. A census of gains cannot distinguish them. Event 3 versus 5 carries the audible contrast in the supplied render.

A four-event negative control P=(12)(34), Q=(23)(41) has different skeletons but commutes; both orders give the global mean. Merely crossing two grouping maps is insufficient to obtain order dependence.

A second observation (deductive, not a listening result): repeated alternating full-strength pair averages erase differences within each connected component in the limit. Each mean is an orthogonal projection, so it cannot increase the squared norm after subtracting each component's conserved mean; equality occurs only when the corresponding pairing already agrees. On the mean-zero subspace the product is strictly norm-decreasing on the unit sphere, as equality would imply agreement on every edge and hence zero. Compactness gives a contraction factor below one. Therefore the asymptotic score is the same componentwise average for either repeated order, although finite trajectories differ. The artist has a reason to stop, change weights, or reintroduce emphasis before the joints disappear into uniformity.

### Executed oracle

Run: node oracle.cjs. Pure JS function executed in the current tool runtime before writing the identical function to the repository. Independent basis-vector integer propagation uses a factor of two per averaging step, so the two-step denominator is exactly four. No float tolerance is used. Both orders are compared against permutation composition and component sizes for every ordered matching pair.

| Events | Matchings | Ordered pairs | Commuting pairs | Basis comparisons |
|---:|---:|---:|---:|---:|
|2|1|1|1|2|
|4|3|9|9|36|
|6|15|225|105|1350|
|8|105|11025|2625|88200|

Totals: 11,260 ordered pairs, 89,588 basis comparisons, 190,437 successful assertions, including the explicit six-event witness. Enumeration only up to eight events; the algebraic argument is general. No implication for actual listener groupings.

## 4. Artistic research: the second skeleton is a second composer

[Performance instructions](SCORE.md) and [renderer](render.py) are complementary. The three 12-second, original mono PCM studies use exactly the same pitch and timing sequence; the stored scalar emphasis changes. Render with Python 3: python render.py. Each note retains a low base gain so all six remain audible in principle; no audibility or preference finding claimed. Eight repetitions make the differing accents available for exploration.

I am especially interested in the moment before an edit. The two skeletons are present in the instrument but absent from the sound. A score can be plural before it sounds plural. An artist might intentionally preserve this plurality instead of flattening the project into a single mixer group tree.

The most useful compositional act may not be the operation that changes a note. It may be deciding which events must share a change. If a performer makes one note bright, another performer can choose whether that brightness belongs to its neighbour in time, its counterpart in a repeating motif, or its distant relative in pitch. This is a compositional redistribution of dependency, not a claim that listeners hear a new voice.

## 5. Exaptation: the multi-skeleton sequencer

Prototype proposal: immutable event IDs (not positions), independently named grouping maps, typed group operators, order-aware action preview and versioned non-destructive edit history. For the first implementation, restrict group maps to equal-sized pairs and gain edits to simple averaging; later allow general partitions, transfer operators and separately authored grouping proposals. The user must be able to inspect and reject each map.

A practical editor would contain a piano roll and two coloured bracket layers. Each operation can be applied to one layer, or to an explicitly ordered stack. A commutator preview shows the event-wise delta between the two orders on the current score, separately from an all-input commutation check. If the delta is zero, it is important to distinguish a compatible pair of maps from a special score concealing incompatibility. Repeated averaging's tendency to erase emphasis should be inspectable, not sold as emergent intelligence.

For procedural sound art, route the same operation into filter cutoff, granular density or FM depth. Constrain units and bounds at each mapping. Distinguish authored groups from any computational estimate of auditory streams; a listener's perception is not available merely by examining the graph. A possible generative piece alternates edits on several evolving pairings, occasionally injecting new accents. Composers modify edges rather than writing a melody anew. In contrast to a normal group mixer, the membership can cross other groupings and operations can be deliberately noncommuting.

MHAC transfer hypothesis: a message may contain overlapping author-defined bundles (e.g. an action bundle and a diagnostic bundle). Two group-level transformations that individually preserve a stipulated scalar total can produce different results depending on order. A future *synthetic* interface evaluation could compare ordered previews, current-output-only previews and explicit grouping diagrams. Measure identification of affected IDs, order prediction, reversal errors, and inspection burden. Include commuting maps and constant-score counterexamples. No protected action, uncertainty, or urgency field should actually be averaged by this toy model. An existing typed transaction or DAG editor might solve the entire operational problem, in which case the musical concept can remain an artistic technique.

**Revision criteria:** abandon the new interface vocabulary if existing grouping/automation tools suffice; reject the claim of useful order previews if they do not improve prediction or merely burden inspection; do not infer auditory multistability from playback of these files.

### Speculative fiction — the conservator's two skeletons

The museum had two drawings of the same animal. On the first, every bone was joined to its neighbour; on the second, the joints connected bones from different ends of the body. The conservator could not decide which to hang beside the cabinet. The skeleton in the cabinet was still.

She commissioned a musician to make the two drawings disagree. The musician did not move a bone. She distributed six small lamps, then connected the lamps according to the first drawing. A second musician connected them according to the other. Where the first had lit a shoulder, the second lit a foot. Both were obeying the museum's instructions.

The conservator requested that the lamps be left connected until the disagreement ended. They gradually all became equally bright.

She ordered a new label: THE AGREEMENT OF THE LAMPS DOES NOT CERTIFY THE DRAWING.

The musician asked for a switch with which to interrupt the agreement. The museum called this a failure of restoration. She called it a movement.

### Checkpoint

Scope: #444, additive exploratory record only. Base main 495a98ca12bae467a507031f04931aa4254b1866; branch mhac-444/two-skeletons. Read AGENTS, RAG, programme, runbook, research integrity and validation, README, #444 and comments, 100 recent PR titles and 70 open issue results; searched streaming, bistability, figure/ground, auditory scene, mereology and grouping/partition. #230 studies hidden source attribution: here source and event IDs are known and multiple deliberately authored edit maps operate on them. The earlier score/metric-role work does not establish the edit commutator studied here. Concurrent work includes Freeze Socket implementation; no shared files touched. No full checkout or full repository test run in this environment. Draft, Refs only, not a canonical finding. Keep generated WAVs outside the repo; render.py and the receipts record the executable original art.
