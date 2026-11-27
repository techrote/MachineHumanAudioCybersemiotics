# The Courtier Who Rehearses His Effort

Exploratory expedition, 2026-11-27. Issue #761. AI-assisted original interpretation, synthetic construction and artistic score; not a Track G extraction or Track E finding. No human participation, independent human review, measured CPU performance or acoustic communication advantage.

## A court with two orchestras

A prince commissions an organ which can perform a difficult little tune without seeming to exert itself. The maker succeeds. The prince's successor instead commissions an organ which visibly labours on his behalf. The maker adds a percussion part. Neither sovereign has asked whether the percussion is connected to the machinery.

The instrument has acquired a second score: the presentation of its own production. Its silence about work can be beautiful, and its noise about work can be beautiful. Neither proves anything about the work.

Imagine that a musician composes three separate objects: a melody, the material conditions under which it can be produced, and a counterpoint describing those conditions. The first can remain fixed as the second changes. The third can expose the second, ignore it or invent an alternative. In a theatre these are legitimate independent arts; in an operational interface the third must not claim to be the second unless that claim is warranted.

This is a counterproposal to both the invisible computer and the computer which theatrically announces its busyness. The desirable property is not necessarily visible or invisible work, but a reliable distinction between an event and its representation.

## Source-located encounters

* Baldassarre Castiglione, *The Book of the Courtier*, first published 1528; Leonard Eckstein Opdycke translation, 1901, [Project Gutenberg edition 67799](https://gutenberg.org/ebooks/67799), Book I section 26, printed pp. 35–36. The [indexed primary passage](https://www.gutenberg.org/cache/epub/67799/pg67799-images.html) describes a cultivated nonchalance that hides the making of graceful action, including rhetorical artifice. Section 40's indexed dialogue also contains a dispute about whether artful concealment is deceit. Edition metadata verified; direct full-page retrieval returned HTTP 503, so these are passage-level indexed reading notes, not complete close reading. Interpretation: grace is a social relationship in which visible ease suggests hidden mastery; it is not literally an algorithmic cost metric. The court is a historically unequal setting, not a normative template for software.
* Matthew Chalmers and Areti Galani, [Seamful interweaving](https://eprints.gla.ac.uk/3457/), DIS 2004, pp. 243–252, DOI 10.1145/1013115.1013149. Institutional metadata and complete abstract read. The authors argue that heterogeneous media can be used fluidly while their differences remain perceptible, and criticise disappearance as a sufficient design ideal. Interpretation: one can retain a musical seam without forcing every listener to attend to it. Full paper appraisal outstanding.
* Gina Emerson and Hauke Egermann, [Gesture-sound causality from the audience's perspective](https://eprints.whiterose.ac.uk/id/eprint/108925/), 2018, pp. 96–109, DOI 10.1037/aca0000114. Institutional abstract read. The authors report a video manipulation study in which reduced gesture-sound correspondence affected ratings of certain digital instrument performances. They propose increased understanding as an explanation. This is a reported finding, not an independently appraised empirical result. It neither establishes that computational telemetry improves art nor that visible gesture proves actual computation.
* Ryan W. Buell and Michael I. Norton, [The Labor Illusion](https://pubsonline.informs.org/doi/abs/10.1287/mnsc.1110.1376), Management Science 57(9), 2011, pp. 1564–1579, DOI 10.1287/mnsc.1110.1376. Publisher metadata and abstract read. The authors report that signalling service effort can increase perceived value even for identical results, in simulated travel and dating services. This is a particularly productive counterposition to Castiglione. Neither transfer to audio nor an ethical license to manufacture latency follows. Full experimental appraisal outstanding.
* Demand paging precedent: [Belady's optimality theorem](https://algorithm.tamnd.com/belady-optimality/), statement and exchange-argument summary, secondary exposition; [Tetzlaff and Flynn, A Comparison of Page Replacement Algorithms](https://research.ibm.com/publications/a-comparison-of-page-replacement-algorithms), 1992, institutional abstract. The established farthest-next-use rule is an offline optimum for unit-cost demand paging. The original 1966 article and formal historical proof were not read. No mathematical priority claimed; an independent finite dynamic programme below checks the rule within the stipulated census.

These sources do not speak with one voice. Castiglione's courtier makes effort disappear; the service interface makes effort available to inference; the digital instrument may depend on a spectator's causal understanding; the seamful design argument allows fluidity and perceptible differences to coexist. The tension is a useful artistic subject rather than an empirical synthesis.

## Finite construction: the Sprezzatura Organ

Three immutable oscillator tiles A/B/C have pitches 220/277/330 Hz, 4,000 samples each at 16 kHz. A request produces the tile; the cache initially contains nothing, holds two tiles, and constructs a tile only on a miss. No prefetch, bypass or recomputation on hits. Replacing a resident tile costs no additional counted build. Output is a concatenation of unchanged tiles.

LRU evicts the least recently requested tile. FUTURE evicts the resident whose next request is farthest away (never-used-again last). FUTURE has the complete score in advance: it is not a realizable online oracle for improvisation. The independent dynamic programme explores each legal eviction. Its value at each state is zero at the end, the successor value on a hit, or one plus the least successor value among legal insertions on a miss.

A small impossibility: after ABC, a demand cache of capacity two must contain C and one of A or B. Before the fourth request an online deterministic policy cannot know whether ABCA or ABCB will occur. At least one continuation requires four builds, although both sequences admit a three-build offline execution. This is a statement about the stipulated demand-cache model, not human foresight. Randomization cannot guarantee the offline optimum on both continuations either. A prearranged composition and an improvised composition may therefore sound identical on one realized trajectory while possessing genuinely different information conditions.

The laboratory exhaustively enumerates all nonempty strings of length 1 through 7 over ABC: 3,279 sequences. The farthest-future rule matches the dynamic-programming optimum in every case. LRU constructs 10,923 tiles in aggregate; FUTURE constructs 9,819, with 1,038 sequences showing a strict gap and a maximum per-sequence gap of two. These are finite unweighted census totals, not workload estimates or timing benchmarks.

## Three performances of one accomplishment

Run from this directory: `python laboratory.py audio`. The three original stereo WAVs use 16 kHz signed 16-bit PCM, 48,000 frames, three seconds. All play ABCABCABCABC on the left. The right channel places a short 880 Hz pulse at each represented tile-build event, aligned to its requested note (not its measured wall-clock completion).

* lru.wav: 12 actual builds, 12 truthful markers.
* future.wav: 7 actual builds, 7 truthful markers.
* theatre.wav: 7 actual builds, 12 markers, 5 markers falsely suggesting builds if interpreted under the telemetry convention.

The third movement is explicitly a fictional theatrical layer. It is not a proposed deceptive interface. Its whole WAV is byte-identical to the first despite their different build histories. The principal PCM channel is identical across all three. The renderer instruments actual calls to the tile constructor rather than assigning a workload number after rendering. Marker synthesis and memory operations are excluded from that count; there is no inference about elapsed time, energy, labour, latency, or human effort.

Local Python 3.13.5: two runs passed the exhaustive oracle, call-trace, negative-control, amplitude, WAV-header and complete PCM readback assertions; SHA-256 equality on rerender verified for all outputs and JSON receipt. Source Git blob locally computed: 09cdd4069726b568b78be83b710ec2857e715917. No external listening experiment. Generated audio and receipt are reproducible local deliverables, not canonical corpus records.

Performance score: listen to the two identical recordings as different theatrical scenes, with their provenance labels visible. Listen to FUTURE. Imagine a musician whose instrument's real work is audible only through a second percussionist. Give that percussionist the liberty to compose fiction, but require the programme to distinguish fiction from observation.

## The second rabbit hole: the virtuoso cache

Consider a performance with two instrumentalists. One makes choices by manipulating a limited-memory tile store; the other improvises requests. The first tries to remember what will be requested, and the second may cooperate or confound the memory. A third musician plays only evictions. Their score is no longer about whether a machine is efficient but what kinds of expectation the performers construct together.

A cache miss might generate a rich grain cloud while a hit produces its dry tile. This artistic extension would destroy principal-output invariance if mixed into the dry bus, so keep a separate monitor. In a fixed score, changing replacement policy could produce polymetric percussion with the same pitch sequence. In a live score, predictions could become a fourth voice, with errors explicitly labelled as such. The instrument should expose the difference between observed events and anticipated events, just as an acoustic duet distinguishes a rehearsal from an encounter.

A VSTi could implement persistent, bounded immutable tile caching with an event queue, a dry bus and a trace-percussion bus. A VSTfx could take explicitly supplied block identities and independently sonify recomputation, cache invalidation or replay; do not infer these events from arbitrary incoming audio. CYD could present a three-by-two tile memory with touch requests, retention policies and separately selectable actual/fictional accompaniment; FM-1 could map real patch-generation events to an optional modulation lane. All are future designs, not completed software or hardware. Real audio callback implementation needs preallocated storage, bounded costs, asynchronous construction and explicit deadline/fallback semantics; this offline renderer makes none of those guarantees.

The deeper question is whether an interface can be gracious without pretending to have laboured. In an operational MHAC experiment, compare a plain result, a typed receipt, a truthful event sonification and a labelled fictional counterpoint, with actual workload and result correctness independently varied. Measure identification of cache reuse, actual verification status, false inference, workload, latency and artistic preference separately. A cache hit does not itself establish freshness or independent verification; identities and invalidation rules must be checked. Ordinary textual receipts could fully solve the operational problem. No user experiment is authorized here.

Counterargument: labour cannot be reduced to a count of operations. The actual human work of building the instrument, supplying data and maintaining infrastructure disappears from our model. The pulse on a build may become yet another seductive proxy. The cache cannot demonstrate the meaning of grace, and the courtier cannot prove a paging theorem. Their juxtaposition is a compositional construction. Its testable engineering lesson is only that invariant output and an unbound presentation do not identify internal execution.

## Reconciliation and delivery boundary

Live AGENTS, RAG, programme, runbook, integrity, validation, protocol index and research workspace consulted on 2026-11-27. Reviewed 40 recent PR titles, 30 active issue titles and targeted searches. Hysteresis (#364, #424), identity/authenticity (#471), tuning comma (#286) and palimpsest (#620) were set aside as occupied. Searches for sprezzatura, Castiglione, seamful and Belady returned no issue matches; cache and effort searches exposed adjacent engineering work, not this specific artistic combination. Search is bounded and not proof of novelty. Scope is new issue #761, whose body and empty comments were fetched; starting main SHA 495a98ca12bae467a507031f04931aa4254b1866. No canonical dependencies promoted. Prior #756/#758 explores source-scoped editions, not workload representation; #471 is adjacent causal performance research. Independent mergedown must evaluate overlap, source access limits and exact-head CI. No other repo, protocol, evidence manifest or shared aggregate changed.

*The prince asked the organ why it had worked so hard.*

*The organist pointed to the percussionist.*

*The percussionist pointed to the programme.*

*The programme had two columns: what happened, and what was played.*
