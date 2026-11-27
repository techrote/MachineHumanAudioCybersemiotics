# The Sentence With a Waiting Room
## Copia, commentary and the time of elaboration

2026-11-27 · Issue #773 · exploratory humanities/art research and synthetic software oracle · Draft/HOLD

### A counterexample to the generous machine (original fiction)

A municipal organ has been asked to announce four things: a door has opened; a lift is absent; the east platform is occupied; the next departure is unconfirmed. For each statement its maker has composed a beautiful double. The double of the door has metallic overtones; the absent lift is accompanied by an elaborate little descent.

The organ begins. The listener is already walking when the organ completes its second double. The last statement will arrive, but not in time for the listener's decision.

The composer protests that the information is not missing from the composition. The attendant protests that the composition is not the decision's clock.

A third person proposes a waiting room for the doubles. The public announcement becomes austere. Later, the listener may enter the room and hear everything set aside. The room is not an archive of errors. It is a repertoire of things that could have been said, some of which deserve a different occasion.

The fiction illustrates the mismatch between completeness over an artifact and availability at a specified moment; it proves nothing about actual acoustic intelligibility.

### Three readings, and a disagreement

**Erasmus: source observation.** In *Colloquies*, volume I, hosted by CCEL, the latter part of the Profane Feast contains an interlude headed “The ARGUMENT” introducing rules of copia. Read the warning against ostentatious verbal variety through the example of a welcome letter, active/passive variation and negation (web extraction lines 588–647, accessed 2026-11-27). [English transcription](https://ccel.org/ccel/erasmus/colloquies1/colloquies1.xx.html). The dialogue insists on apt expression before variety and discusses grammatical and figurative alternatives. It also distinguishes the availability of a grammatical conversion from idiomatic suitability. The Latin text and modern critical apparatus were not collated; this is not a close reading of the whole De copia.

**Interpretation:** copia is not simply volubility. The store of forms can remain unspoken. The ability to make more than one sentence can give a speaker the power to select a more fitting sentence. A language model's ability to generate many paraphrases is not a reason to deliver all of them. Nor does repetition repair an initial misstatement.

**Queneau: source observation.** The New Directions description of Raymond Queneau's *Exercises in Style*, translated by Barbara Wright, identifies a mundane bus encounter and later meeting retold in ninety-nine styles. Read the product description below the translator credit, web lines 33–35, accessed 2026-11-27. [Publisher description](https://www.ndbooks.com/book/exercises-in-style/). This verifies the project and examples of its styles, not the linguistic content of each exercise. No complete book reading is claimed.

**Interpretation:** the incident is a pretext for making differences among literary forms available for inspection. Calling it “the same” is an invitation to compare, not a certificate of invariant pragmatic force. A police report, an overheard anecdote and a sonnet can bring different agents and relationships into focus even where their incident inventory agrees. A reader may enjoy exactly the divergence that an operational interface should avoid.

**Berio: source observation.** In the author note for *Chemins I* (1965), on *Sequenza II* (1963), Luciano Berio treats recomposition as analysis and commentary. The complete short note was read (web lines 48–58, accessed 2026-11-27). [Centro Studi Luciano Berio, author note](https://www.lucianoberio.org/nota-di-programma-op/chemins-i-authors-note/). The ensemble develops processes implicit in the solo part, sometimes apparently reversing the relation between commentary and original. The author note for *Chemins IV* (1975), lines 46–56, also read, discusses elaborating the oboe solo's latent polyphony around a persistent pitch. [Author note](https://www.lucianoberio.org/en/program-note-work/chemins-iv-authors-note/). No score analysis or recording audition is claimed.

**Interpretation:** commentary can change the function of original material. This is more powerful than decoration, and precisely why the formal model below is insufficient to represent Berio's practice. In an art instrument an elaboration may become the principal work. In an operational interface that same transformation may obscure whether a requested fact was delivered. Neither use is reducible to the other.

The three encounters are not evidence of historical influence among the authors, nor studies of acoustic communication. They are an AI-assisted comparative reading of specified passages. A fuller inquiry would collate the original Latin, French and musical scores and seek counterexamples.

### The musical waiting room (stipulated construction)

Four distinct anchors A B C D have a fixed order. Each owns exactly one distinct elaboration a b c d, which must follow its own anchor but may follow other anchors as well. Every tile occupies one identical time slot; no overlap, deletion, compression or preemption is allowed. A complete score uses each tile exactly once. Letters are artificial identities, not learned words; their stipulated relationships have no validated acoustic interpretation.

The two extreme arrangements are AaBbCcDd (immediate adjacency) and ABCDabcd (all anchors first). The former prioritizes juxtaposition; the latter prioritizes availability of anchors. Both preserve all eight tile identities and ownership.

A deadline vector d=(1,2,4,5) requires completion of anchors by those one-based slots. An anchor arriving in slot d is timely. The local score violates B, C and D deadlines; the bulletin is timely. A compromise ABaCDbcd completes the anchors exactly at the deadlines. It separates commentary a from its anchor by one intervening tile, b by three, c by two, d by two.

Define locality loss L as the total number of intervening tiles across all four pairs. Writing P for the sum of anchor positions, the sum of all positions is 36; the commentary-position sum is 36-P. Hence L=32-2P. This also reveals a limitation: the loss cannot distinguish the distribution of separation among pairs. Two schedules with the same anchor positions may have different individual delays and identical total loss. No empirical reason establishes that they matter equally. A weighted or maximum-delay objective could distinguish them.

Under the deadlines P <= 12, so L >= 8. ABaCDbcd attains the bound. There are 12 minimizers. With m paired tiles, fixed anchor order and no other constraints, L=2m^2-2P. A bijection with perfect matchings on 2m positions counts valid scores: choose an unordered perfect matching, label its pairs in increasing order of first position, designate first positions as anchors and second positions as comments. There are (2m-1)!! scores. This is elementary combinatorics, not a priority claim.

A feasible arrangement exists exactly when d_i >= i for every anchor i: necessity follows from fixed order, sufficiency from placing all anchors first. This says nothing about acceptable commentary lateness. Adding deadlines for comments, permitting overlap or requiring adjacency changes the model.

### Executed laboratory and original performance

[Python source](laboratory.py). Run from the expedition directory:

    python laboratory.py /tmp/copia-audio

Python 3.13.5 native execution completed twice. The program filters all 40,320 permutations and compares the 105 valid scores with independent recursive construction of the ordered-anchor/precedence grammar. It checks all 4,096 four-component deadline vectors in the range 1..8 against both enumerators and the feasibility criterion. Exact finite censuses, not estimates of human behaviour.

For d=(1,2,4,5), 54 of 105 scores satisfy the deadlines, with minimum locality loss 8 and 12 minimizers. Three original WAVs are generated, each 32,000 mono samples at 16 kHz, signed 16-bit PCM. Each anchor has a 250 ms sinusoidal tile; its commentary uses second and third harmonics under the same smooth envelope. All three scores are permutations of the same eight immutable tiles. The program reads back complete PCM and WAV metadata and renders twice to check identical SHA-256. Three distinct WAV hashes are required.

| Edition | Score | Anchor completion slots | L | Meets deadlines |
|---|---|---|---:|---|
| The seminar | AaBbCcDd | 1,3,5,7 | 0 | No |
| The bulletin | ABCDabcd | 1,2,3,4 | 12 | Yes |
| The waiting room | ABaCDbcd | 1,2,4,5 | 8 | Yes |

Observed runtime hashes:
- local.wav: bc98b038e1a6e7ab1d38644fd5405509995668e3ff0cbbfb1e0371ef93b9c9b8
- bulletin.wav: 4c2acb56c53264439c3c485b6ed1535f28acc78324b1dd8bbf8a598489e9fee1
- negotiated.wav: ad419b8cb1d0afe7c55c4e155694b8235cf5a32e13e8f77d8860ee174a458719

**Original performance instruction:** Listen to the seminar as chamber music. At its midpoint imagine the station attendant interrupting it. Listen to the bulletin as chamber music instead of an announcement. Finally, treat the negotiated version as a work in which some sounds must wait for their right to become meaningful. Exchange the instructions. A further movement consists of playing a commentary before its anchor, deliberately breaking the model and granting the commentary artistic anticipation. No listening test has been performed. There is no claim about recognition, latency benefits or accessibility.

### The second room: a commentary that becomes its own parent (speculative essay)

Suppose the waiting room is not FIFO. It contains not merely delayed doubles but an independently navigable musical space. A performer opens the commentary of A, finds that its harmony recalls C, and elects to elaborate that relationship. The commentary can itself generate a commentary. It acquires a provenance edge rather than a single fixed host. A musician may listen to descendants without replaying the ancestor. This creates a forest of possible developments rather than an endless compulsory recital.

Berio's author note suggests the more difficult inversion: an original is altered in its function by the apparent priority of commentary. If an elaboration becomes the principal statement in an artistic edition, the editor can explicitly promote it. In an evidential view, provenance must remain immutable. Promotion of a new work must not manufacture a new observed event. A branching musical library can distinguish an authored derivative, replay, reinterpretation and independently observed signal.

There is an objection to making the operational layer austere. A short fragment may be difficult to interpret without context. The division into anchor and optional commentary can be wrong. If a condition is needed to know whether A applies, it belongs to A's required bundle, not the waiting room. If the listener needs repetition or translation to obtain access, the material is not necessarily optional. The assumption of known symbolic identities cannot resolve these questions. The waiting room ought to include a way to challenge classification rather than merely postpone everything the composer labels surplus.

### Instrument proposal (not implemented firmware or VST)

**Copia Organ:** a sequencer with immutable source-event IDs, parent-linked elaborations and separate principal and commentary queues. Switch between adjacency, deadline-priority and explicitly negotiated scheduling. One XY axis controls commentary density, the other controls maximum attachment delay. A visual history exposes actual onset, completion, parent identity and pending material. Strict mode refuses an infeasible mandatory bundle rather than silently demoting a qualifier. Theatre mode permits composition unconstrained by operational ordering. Label the modes separately.

**VSTi:** deterministic MIDI-triggered bank, bounded queues, optional elaboration voice and per-event parent IDs. Avoid dynamic allocation in the audio callback. Test exact delivery against sample deadlines and block-boundary variation. No automatic text semantics or universal musical mapping assumed.

**VSTfx:** accept explicitly labelled events or stems; generate harmonic commentary on a separate output with selectable attachment delay, rather than infer semantics from arbitrary audio.

**CYD:** two views on a 320x240 screen: timeline for actual emitted events and grid of pending elaborations. Touch a parent to inspect or audition descendants. A separate artistic field allows navigation of the commentary forest.

**FM-1:** map one parent gesture to optional FM trajectories with a bounded commentary queue. Qualify scheduling independently of audio rendering and device timing.

### MHAC falsification and limits

A prospective experiment should use conventional textual controls: concise typed event table with necessary qualifiers, complete transcript, and recipient-initiated details panel. Compare with audio-only and optional redundant acoustic commentary. Deadlines must be independently specified, not tuned to favor audio. Randomize ordering, qualifiers, interruptions, prior code learning and whether allegedly optional material actually changes the correct action. Record complete-bundle accuracy by deadline, false action, correct abstention, comprehension, delay, workload and artistic preference separately. Measure the full bundle, not first-token delivery. A conventional details panel may solve the whole problem. No acoustic advantage, equivalent pragmatic force or human accessibility established.

Distinct from #246's codeword ornament/error protection, #366's abandoned syntax, #656's retrospective metric revision, #766's conserved local fragment inventory, and #279 scoped quotation: this construction holds the whole inventory fixed while allocating elaborations in time under completion deadlines. Overlap searches included Erasmus, copia, Queneau, Berio, paraphrase, ornament and commentary, and recent PR and issue titles; not a systematic novelty search.

### Checkpoint

AGENTS, RAG, programme, runbook, research integrity, validation and research README read from live main. Recent PR and active issue titles inspected. Issue #773 and empty comment list retrieved. New issue-scoped branch; only this README and laboratory.py. All verification by one AI-assisted run, not independent human review. Exact-head CI and mergedown review remain pending; preserve shared registry, manifests, other branches and frozen protocol. No core corpus acceptance, deployment, participant work, license grant or outreach.

### Afterword (original fiction)

The organ was praised for having spoken everything.

The attendant asked when.

The composer opened a second door.

Behind it were all the sentences the organ had been capable of saying, but had chosen not to say yet.
