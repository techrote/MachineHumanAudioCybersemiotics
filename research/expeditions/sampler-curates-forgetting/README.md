# The Sampler That Curates Its Forgetting

*An expedition into readymades, soundscape, admission scores and the topology of finite memory.*

26 November 2026 · Issue #696 · Exploratory humanities/art and synthetic mathematics, outside frozen Track E/G. No new empirical claim or production requirement.

## An essay: the museum with an insufficient tape

A curator installs an apparatus in a room. It can remember half the sounds that pass through it. Another curator arrives with the same apparatus and the same amount of storage, but uses it differently: the first keeps a single continuous passage; the second retains a series of isolated instants. The first can play a little history. The second can play a little geography of time. Neither is a neutral witness.

The readymade makes designation rather than manufacture an available artistic operation. But the acoustic readymade has a peculiarity: its object is not simply waiting in a shop. Its possible boundaries are moving. To designate an event after its appearance, one must have retained something of its appearance. A button marked KEEP is also, implicitly, a boundary between the parts of the world eligible for later reconsideration and those that are not.

Consider a sampler whose keyboard does not trigger sounds. Instead, the keyboard grants sounds the right to become replayable. Its player composes an **admission score**: not a sequence of notes but a sequence of permissions. The source can continue uninterrupted while the score of its future availability develops independently.

This is not equivalent to a mute switch. A muted sound can be retained and played later. An excluded sound in an honestly bounded archive cannot be recovered from that archive. Nor does the absence of a recording indicate an absence of sound. Silence as a compositional element and missing material as a condition of knowledge should remain separate.

A museum might deliberately preserve the quiet spaces between incidents instead of the incidents themselves. A recording of two consecutive gestures can contain a relationship that neither gesture contains separately. This does not mean the relationship is necessarily causal, or even perceptually recognized. But an editor choosing isolated samples has relinquished one means of examining that relationship.

The most interesting musical control may therefore be the topology of the holes: their number, length, and relation to the surviving fragments. A long hole may feel like a missing scene; many small holes may produce a rhythm. Those are artistic proposals, not measured responses.

## Source encounters and disagreement

All consulted on 26 November 2026 by the same AI assistant; no independent review, primary work audition or new participant observation. Locators below indicate actual reading extent.

- **Marcel Duchamp / MoMA Learning, "Marcel Duchamp and the Readymade."** [Institutional account](https://www.moma.org/momaorg/shared/flattened_pages/moma_learning/themes/dada/marcel-duchamp-and-the-readymade/), main paragraphs beginning with Duchamp as a Dada pioneer and ending with the distinction from retinal art, plus notes 1–3. The account describes selecting ordinary manufactured objects, designating them as art and assigning titles; it reports aesthetic indifference as one criterion. The 1946 Sweeney interview (MoMA Bulletin 13, nos. 4/5, p. 20) and the 1961 assemblage symposium are cited there, not independently read here. Interpretation: an admission instrument could intentionally reject interestingness as a selection criterion. This is not a claim about all Duchamp works or the origin of sampling.
- **John Cage / MoMA, "There Will Never Be Silence: Scoring John Cage's 4′33″," 2013–14.** [Exhibition description](https://www.moma.org/calendar/exhibitions/1386), opening three prose paragraphs and the surviving score's caption. The museum characterizes the three movements by the absence of deliberate sound production by the performer and the availability of surrounding sounds. [Score commentary](https://www.moma.org/slideshows/24/389), indexed text under the 1952/53 proportional notation, describes vertical lines measuring durations. The original score image and recordings were not inspected. Interpretation: temporal framing can be a performable act distinct from sound generation. Cage's work does not entail recording or finite storage; that is this expedition's departure.
- **Luc Ferrari, Presque rien (N° 1) ou Le lever du jour au bord de la mer (1967–1970).** [IRCAM work entry](https://brahms.ircam.fr/en/work/presque-rien-%28n-1%29-ou-le-lever-du-jour-au-bord-de-la-mer), general information, fixed-sound designation and the complete short French program note attributed to Ferrari. Ferrari characterizes the piece as a representation of a fishing village awakening, with abstract sounds removed. The note supplies authorial intention, not an independent verification of documentary fidelity. [IRCAM workcourse](https://ressources.ircam.fr/fr/composer/luc-ferrari/workcourse), indexed paragraph beginning "Ce fut la même chose avec Presque rien N° 1", describes recomposition of recorded environmental material. The full workcourse and recording were not accessed. Interpretation: seemingly documentary sound can be deliberately assembled; do not claim an unedited record.
- **Barry Truax, "Soundscape Composition."** [Author's SFU page](https://www.sfu.ca/~truax/scomp.html), opening definition, principles and range of approaches. Truax describes minimal selection and unobtrusive editing at one end of a continuum, and more transformed work at the other; contextual associations and recognizable source material matter in his account. **"Soundscape Composition as Global Music: Electroacoustic music as soundscape," Organised Sound 13(2), 103–109 (2008).** [Author-hosted text](https://www.sfu.ca/sonic-studio/WSPDatabase/AnalysisDVD/WSP/OS7.html), abstract, §§I–III through the Pendlerdrøm example; [publisher abstract](https://www.cambridge.org/core/journals/organised-sound/article/abs/soundscape-composition-as-global-music-electroacoustic-music-as-soundscape/115CA3A7867A41FB86F0A0D493E00E49). Truax describes a composition that moves between an evoked train journey and transformed material associated with daydreaming, and challenges the cliché of music as universal language. Neither the recording nor a complete reading of the article was undertaken. His contextual orientation is substantial artistic precedent and an objection to treating each tile as interchangeable.

Duchamp's reported indifference pulls against a soundscape composer's attention to an environment's particularity. Cage's performed temporal bracket does not require Ferrari's fixed record. These differences should be preserved, rather than collapsed into a common claim that all sound is music. The proposed sampler occupies the gap: a deliberately partial record of a source and an instrument for designing that partiality.

## Exact construction: how many neighbours survive?

Let n >= 3 equally long frames form a labelled cycle, with 0 < m < n retained frames. The source is known in the toy model, but the future requested adjacent pair is unknown when the mask is chosen. No reconstruction from neighbouring frames, compression, or semantic inference is permitted. The wrap edge is a modelling convention, not a claim that a real recording's end neighbours its beginning.

Let r be the number of maximal retained runs, counting across the wrap. Each nonempty run of length l contributes l-1 fully retained directed adjacent pairs, so:

- both endpoints available: B = m-r;
- exactly one endpoint available: X = 2r (one edge at either run boundary);
- at least one available: T = B+X = m+r;
- neither available: Z = n-m-r.

Consequently B+T = 2m. At fixed retention budget every additional island buys exactly one newly touched query and costs one complete query. All integer r from 1 through min(m,n-m) are feasible: partition m retained and n-m missing positions into r positive run lengths each, then alternate them. The two metrics count available original frames, not semantic accuracy or listener utility. If the objective instead asks for a single uniformly selected frame, every mask with m retained frames is equivalent.

Number of labelled masks with r runs:
N(n,m,r) = (n/r) * C(m-1,r-1) * C(n-m-1,r-1).
To prove, mark one of the r retained-run starts, choose its labelled position (n possibilities), and choose ordered positive compositions of retained and missing lengths (the two binomial factors). Each unmarked mask is counted r times. No assumption of uniform run counts is made. For n=12, m=6, the counts for r=1..6 are 12, 150, 400, 300, 60, 2, summing to C(12,6)=924.

Uniformly rotating any fixed mask makes the success probability for every precommitted edge exactly B/n for complete access and T/n for partial-or-complete access. This is optimal worst-edge probability within policies restricted to that run count: the mean over all fixed edges is the same for any such policy, and the minimum cannot exceed the mean. Rotation attains equality for both. This does not protect against an adversary who sees the realized mask before choosing a query, and it does not preserve an externally distinguished origin. For a live stream with endpoints, the boundary accounting changes. For arbitrary variable-duration clips, equal frame count need not mean equal storage.

| Twelve-frame score | Retained | Runs | Both | Touch | Neither |
|---|---:|---:|---:|---:|---:|
| 111111000000 | 6 | 1 | 5 | 7 | 5 |
| 110011001100 | 6 | 3 | 3 | 9 | 3 |
| 101010101010 | 6 | 6 | 0 | 12 | 0 |

The alternating archive can produce at least a fragment of every adjacent query while never producing a complete one. The danger in calling either system a better recorder lies in quietly changing what a successful query means.

This is elementary cycle combinatorics, not mathematical novelty, and no relation to actual acoustic perception is proven.

## Original listening score: Three Curators at the Factory

The full source is an invented six-second acoustic miniature, rendered as twelve half-second tiles. Low oscillators evoke machinery, whistles vary across tiles, deterministic noise and ticks provide texture. Each tile has short boundary ramps; these are part of the original source, not capture processing. No real factory, microphone or environmental observation is involved.

1. **The room:** all twelve tiles.
2. **The historian:** six consecutive tiles, then a three-second missing interval.
3. **The island keeper:** three separated two-tile passages.
4. **The collector:** every other tile, no original adjacent pair fully available.

Keep the six-second timeline in all four renderings; omitted frames are replaced by zero PCM, not joined, inferred, or classified as original silence. Read the masks alongside the audio. Retained samples are bit-identical to the full source. All partial renderings contain the same number of original frames, not necessarily the same total energy.

Performance extension (unimplemented): play a compacted audition, removing gaps; then restore the original time coordinates. New adjacent sounds in a compacted version are editorial joins. Compose a separate join voice that identifies them, and mute that voice when ambiguity is desired in art. In an operational record, keep the original index ledger regardless of audition. The music need not explain itself continually; the archive should remain inspectable.

The artist's responsibilities are not exhausted by storing a mask. An actual environment contains other people's activity; selecting, retaining and publishing recordings are separate acts. This prototype does not record people, ask for permission or justify ambient surveillance. A real capture implementation would require explicit local opt-in, bounded volatile storage, visible capture state and separate publication controls.

## Exaptation: the Admission Organ

The proposed VSTfx operates on supplied DAW audio, not an always-on microphone. A preallocated circular ring stores a bounded region, with an independently programmable retention mask and a pinned source timeline. Quantize capture in musical time or fixed samples; declare which. Write only into preallocated storage on the audio callback, send immutable capture descriptions to a non-real-time editor; do not allocate or write files on the callback. Preview modes: original, gap-preserving, compacted and join-audited. Distinguish eviction, intentional omission and observed silence. Avoid promising complete recall after eviction.

A CYD version could use a 12-cell touch ring and audition a synthetic oscillator field; a large XY surface paints run density and source position, with a separately adjustable memory budget. An FM-1 experiment could use a generated stream of simple motifs (subject to real hardware capabilities), not a microphone assumption. A VSTi could generate a persistent synthetic environment with two performers: one controls the source population, the other edits the retention topology. None of these real-time implementations is delivered here.

An alternative experiment: several small samplers hear the same source but independently compose their selection masks. Their union might reconstruct a complete history none individually possesses, or leave shared blind spots. This introduces a new compositional question about the relations between archives rather than within a single archive. Do not infer independence from separate file names. A negative control duplicates a sampler's mask and therefore adds no coverage. This is a future design question, not a result here.

For MHAC, compare complete-query availability, touched-query availability and correctly reconstructed joint event states on explicitly synthetic logs. Baselines: contiguous archive, periodic archive, random rotations, full log, and text-only interval/omission ledger. A second condition introduces genuine observed silent frames alongside missing frames. Test whether a recipient incorrectly treats zero-filled gaps as actual silence; do not replace operational warnings with an artistic masking policy. An ordinary coverage map could be better than any acoustic annotation. No acoustic communication benefit or empirical effectiveness has been established.

## Execution and handoff

- Reconciliation: AGENTS, RAG, programme, runbook, integrity, validation, protocol index, research README; 40 recent PR titles, 30 open issue results and targeted searches. Read issue bodies #548 (clipping/offcuts), #205 (branching continuation), #656 (revision of metrical annotations); #672 is faceted indexing of persistent objects. Here the actual original inventory is partially unavailable and the future query is an adjacent pair. Abandoned palimpsest (#620) and tuning drift (#286, #508) as overlapping. Search is bounded, not an exhaustive novelty review.
- Base: 495a98ca12bae467a507031f04931aa4254b1866. Issue #696. Only this expedition's directory is owned.
- Run: python laboratory.py audio (Python 3.11+; executed on 3.13.5). Native PASS: 131,036 nontrivial labelled masks for n=3..16; direct edge classification, run counts and multiplicity formula; all twelve labelled rotations of each exemplar checked against every edge. Deterministic synthetic rendering, four distinct WAV hashes, bounds, PCM format/readback and exact retained-tile equality passed. Local script Git blob 1f15bab5ff880ff54993e93f4e185ce04b2de1e9.
- Audio: 16 kHz mono signed 16-bit PCM, 96,000 frames per WAV, 48,000 original frames per partial capture. Renderer writes a machine-readable receipt and four WAVs to the specified local output directory; audio binaries not committed. Native script qualification is not repository CI.
- AI-authored original essay, source encounter notes, proof, self-audit and renderer. No other agent or human reviewer, no listening trial, no canonical research promotion. Draft/HOLD for integrator review and exact-head repository qualification. Preserve shared manifests, frozen protocol, other branches and live evidence. No changes to permissions, license or production code.

## Speculative afterword

*The museum purchased a device that remembered every second sound. Its curator was praised for having a sample of every conversation.*

*When asked what the conversations had been about, the device presented every second word.*

*The curator arranged them in a row.*

*The archivist asked for the spaces.*

*They had already been sold.*
