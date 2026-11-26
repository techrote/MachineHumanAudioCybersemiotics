# The Orchestra That Cannot Agree on Its Foreground

**MHAC humanities expedition · 2026-11-26 · #717 · Draft/HOLD**

## Abstract

A picture may remain unchanged while the perceived figure changes. A musical
mixture may be interpreted at several levels of organization. What would an
instrument look like if its performer composed those organizational choices
instead of the material itself? This essay proposes an intentionally simplified
two-role score, qualified by exhaustive symbolic enumeration and accompanied by
an original reversible stereo composition. It does not claim that listeners
hear the authored roles, or that the construction models perceptual bistability.

## Source-located encounters

- Wagemans et al. (2012), *A century of Gestalt psychology in visual perception:
  I. Perceptual grouping and figure-ground organization*, Psychological Bulletin
  138(6), 1172–1217, [DOI](https://doi.org/10.1037/a0029333).
  Institutional abstract and indexed section 5.1 consulted; direct PMC opening
  encountered a CAPTCHA. The review distinguishes grouping from figure-ground
  organization and discusses border ownership. The latter is useful here as a
  conceptual prompt: a relationship can be organized without adding a new object.
  Neither the full review nor Rubin's original thesis was read.
- Escher in Het Paleis, [Development II](https://www.escherinhetpaleis.nl/en/escher-today/development-ii),
  17 October 2020, opening paragraph. Museum commentary on tessellation as
  material for metamorphoses and cycles, not only an isolated pattern.
  Read the opening text, not the original artwork at exhibition resolution.
  This suggests a compositional process that repeatedly exchanges the roles
  of material and context; that suggestion is ours, not an account of Escher's
  intentions.
- Pressnitzer, Suied and Shamma (2011), [Auditory scene analysis: the sweet
  music of ambiguity](https://doi.org/10.3389/fnhum.2011.00158), Frontiers in
  Human Neuroscience 5:158. Abstract, 'Auditory Bistability' (opening
  paragraphs), and 'Some Musical Illustrations' (opening paragraphs) read on
  publisher website. They discuss reports of changing stream organization for
  repeated tones, and distinguish physical sound sources from musical
  percepts. The review's underlying studies and sound demonstrations were
  not independently checked. Stream segregation is not identical to
  figure-ground reversal; our artificial role assignment is neither.
- Huron (2016), *Voice Leading*, chapter 13, [Hierarchical Streams](https://doi.org/10.7551/mitpress/9780262034852.003.0013),
  pp. 163–172, indexed publisher abstract only (direct chapter retrieval
  failed). The chapter distinguishes multiple levels of organization,
  including intermediate textural streams. This is a counterweight to the
  proposed binary grammar: actual musical layering need not be two-valued.
- Harary (1953), [On the notion of balance of a signed graph](https://doi.org/10.1307/mmj/1028989917),
  Michigan Mathematical Journal 2(2), metadata only. Harary and Kabell (1981),
  [Counting balanced signed graphs using marked graphs](https://www.cambridge.org/core/journals/proceedings-of-the-edinburgh-mathematical-society/article/counting-balanced-signed-graphs-using-marked-graphs/4FC857BB402340C68D4694FC2D046231),
  extract consulted, defines balance by positive cycle products.
  The section 'Harary’s Balance Theorem' of
  [Negative (and positive) circles in signed graphs: A problem collection](https://www.tandfonline.com/doi/full/10.1016/j.akcej.2018.01.011)
  was consulted via indexed passage. This is established graph theory, not
  new mathematics. The application to an authored role score is interpretive.

Access/verification: one AI-assisted reading pass on 2026-11-26. Sources are
discovery and interpretive notes outside the frozen systematic review; no
screening, independent human verification or full-text appraisal is claimed.
No source audio or images are redistributed.

## Interpretive essay — The foreground is not a property of a note

Imagine an orchestra consisting of six stationary musicians. Their parts are
complete; nobody is permitted to change a note. Two conductors arrive. One
describes a particular cello phrase as the main material, the other hears it
as a support for the oboe. The archive records both descriptions, but insists
that the musicians have not changed.

This is not a dispute about which instrument is playing. Nor is it necessarily
a dispute about the presence of a sound. It concerns a relationship between
the sound and an organizing activity. The most radical conductor might
perform no notes at all, only change the organization of the other musicians'
notes.

The grammar developed here treats foreground and ground as names of two
routing buses. They are not psychological categories. A musician authors
relationships: two motifs must occupy the same bus, or they must occupy
different buses. They can leave the choice of absolute role open. Two islands
of relationships can be reversed independently. When islands are joined, one
degree of freedom disappears, not necessarily any note.

One can compose an entire movement in which no absolute role is specified.
Then an anchor is introduced. The anchor is tiny; its consequences can be
large, because it determines the organization of a whole connected component.
A contradictory anchor does not make the music impossible; it makes this
particular score of relationships impossible. The underlying mixture is still
playable. The artist may choose to perform that refusal separately.

There is a political temptation here: to describe the background as oppressed
and the foreground as powerful. Resist making that a law. A bass foundation
may be more structurally consequential than a conspicuous solo. A participant
may prefer to withdraw from attention. This binary model is a toy for
composition, not an ontology of listening or society.

## Formal construction and proof

Let each of n persistent sound stems have role x_i in {0,1}. An edge (i,j,p)
requires x_i XOR x_j = p, with 0=same and 1=opposite. An anchor fixes x_i
to an explicitly supplied value. Edges are undirected and simple.

If a cycle has odd XOR sum, adding its equations produces 0=1, so no assignment
exists. Otherwise choose a root per connected component and propagate relative
parities along paths. Path independence follows because every cycle has even
XOR. Every assignment on that component is determined by its root bit.

An anchor fixes the root bit after accounting for its relative parity.
Conflicting anchor-implied root bits make the whole system unsatisfiable.
If all constraints are consistent and u components have no anchors, there are
exactly 2**u labelled assignments. Isolated vertices count as components.
No claim that these assignments are equally probable human interpretations.

An unanchored connected graph has two labelled solutions, even if it contains
a thousand edges. An anchor resolves the choice; more consistent relative
edges within that component do not. A bridge joining two previously unanchored
components halves their joint assignment count. A cycle-closing edge either
adds no information or introduces a contradiction.

A further design corollary, derived rather than separately enumerated here:
with a fixed consistent graph and reliable anchors on distinct vertices,
surviving any e arbitrary anchor erasures while retaining unique recovery
requires at least e+1 anchors per component. If a component has <= e,
all its anchors can disappear. If every component has > e, at least one
survives in each. Components smaller than e+1 make the guarantee impossible.
This assumes erasure locations known, not erroneous anchor values or graph edits.

The oracle tests all simple graphs with absent/same/opposite edges for n=1..5;
all absent/0/1 anchor patterns for n=1..4 and no anchors for n=5. Independent
brute force enumerates binary assignments; propagation counts them without
enumeration. Native execution: 59,809 graph configurations, 118,857
graph/anchor cases, every count agrees. Negative controls: odd opposite triangle
and inconsistent anchors on a same-role edge return zero. No novelty claim.

## Original artistic score — Four interiors of one orchestra

Six additive oscillator stems at 110, 165, 220, 277, 330, 440 Hz. Each has
a distinct rhythmic phase and one of three envelope rates. The common gain
and window are fixed. Component A: 0 opposite 1, 1 same 2. Component B:
3 opposite 4, 4 opposite 5. Four admissible assignments:

| Roles (0 left; 1 right) | Left stems | Right stems |
|---|---|---|
| 011010 | 0,3,5 | 1,2,4 |
| 011101 | 0,4 | 1,2,3,5 |
| 100010 | 1,2,3,5 | 0,4 |
| 100101 | 1,2,4 | 0,3,5 |

Render with Python 3.11+ stdlib: run laboratory.py in its directory. It writes
four 4-second stereo WAVs and one dry mono WAV under audio/. Files have
64,000 frames, 16 kHz, signed 16-bit PCM. Every stereo L+R sample equals
the corresponding dry mono sample exactly (integer sum, not a claim about
physical loudspeaker summation). All five WAV hashes are distinct and two
same-runtime renders agree byte-for-byte; cross-platform bit-exactness not
established. Readback and amplitude checks passed. Generated audio and receipt
are supplied as a local package, not committed. No listening trial or decoder.

Performance instructions: listen first to the dry mix; then to the four
stereo versions in either order. Next audition each channel separately.
Finally imagine the role name changing without routing changing. That last
movement exists in the score rather than the sound. Ask whether a name is
sufficient to create an audible foreground; do not assume an answer.

## Instrument proposals and experimental questions

**Reversible Organ (VSTi):** persistent oscillator bank; separate authored
role graph; component reversal, anchor automation, explicit contradiction
state. Keep a dry invariant-sum monitor; optional unequal role gains are
a separate effect and break that invariant. Apply graph changes off the
audio thread and swap immutable routing snapshots at buffer boundaries.

**Border Chorus (VSTfx):** operate on explicitly provided multichannel stems,
not claim to extract arbitrary sources from a mono mix. Two role buses, a
dry monitor, and a difference monitor for auditioning reorganizations. Smooth
role changes via complementary crossfades so that the total gain per stem
remains one; verify real arithmetic tolerance and clipping independently.

**Figure Field (CYD):** touch surface of oscillator territories. Tap an anchor,
draw same/opposite edges, or flip a connected component. Color denotes
authored role, not measured salience. A contradiction gets an explicit
non-audio status plus optional musical material. For FM-1, a small patch
sequencer could use the same parity grammar to select modulation groups.
No plugin or hardware implementation is claimed.

**MHAC hypothesis:** relative role information and absolute operational
role are distinct. A machine may specify that two states have opposite
priority without specifying which one has higher priority. Unlike the
binary model, real priority can be multilevel, contextual or incomparable.
A future benchmark should compare explicit textual anchors, relative-only
graphs, full tables and optional sonification, with erased anchors,
contradictory edges and changed context. Measure role reconstruction,
operational decisions, abstention, confidence and latency separately.
Conventional tables may solve the operational problem; no communication
benefit has been demonstrated. No participant activity authorized or performed.

## Speculative coda — A room with two acoustics

The conductor turned towards the window. The orchestra continued playing.

The archivist asked whether the first violin was still the foreground.

The conductor pointed at a small bassoon part.

The engineer announced that the signal was unchanged. The poet said that the
room had acquired another window.

Both of them were describing the same room; neither had measured the window.

## Reconciliation and limits

Base: 495a98ca12bae467a507031f04931aa4254b1866. Read live AGENTS, RAG,
programme, runbook, integrity, validation, research and protocol indexes,
new issue #717 and its empty comment list. Reviewed 40 recent PR titles
and 30 active issue titles. Targeted searches for figure-ground, Rubin,
bistability, auditory streaming, Gestalt and bipartite revealed #444
(mereological grouping), #600 (semantic geometry), #58 (alarm corroboration)
and adjacent #524 (spatial traversal). These are different from a signed
role-graph score; this is a bounded overlap search, not a novelty audit.
Earlier directions concerning quotation and ekphrasis were set aside after
finding #278/#460 and #524/#668. No canonical records, registry, protocol,
manifests or existing files modified. AI assisted research, proof,
implementation and self-check; no independent review. Draft for mergedown
qualification per issue scope and concurrent-worker boundary. Full repository
CI and acceptance not asserted.
