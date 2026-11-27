# The Film That Keeps Every Cut
## Montage, higher-order context and the right to edit a musical neighbourhood

Exploratory humanities/art expedition, 2026-11-27. Refs #765. AI-authored research notes, interpretation, mathematical construction and original synthetic score; no independent human review. Outside frozen Tracks E/G, no promotion into the canonical corpus or claims.

## An editor's affidavit (original essay)

An editor comes to court carrying seven fragments of film. The judge asks whether she has removed a shot. No. Changed its length? No. Manufactured a new image? No. Changed the inventory of cuts? No. The judge acquits the film of having been edited.

The projectionist plays it. A recurring image of a motionless door appears between two images of the same room, then between different rooms, then between two images of the second room. In another version, the same door always occurs between different rooms. The judge's inventory is still correct. The film has changed.

The unit of editorial authorship is not necessarily the object or even the pair of objects. It may be the passage through a relation. A door is not merely next to a room; it mediates a particular passage between two rooms. The distinction matters to a composer working with immutable samples: the exact same sample may participate in recurrence, contrast, transition, interruption or a deliberately unfulfilled expectation.

There is no universal dictionary translating these formal roles into human experience. A door in a film can be a room divider, the promise of a return, a prohibition, or simply part of a set. The editor may design a context, not decree the spectator's inference.

## Source encounters and their limits

- Lev Kuleshov, account of creative geography, quoted in David B. Clarke, [The Bathos of Distance](https://youareheregeography.wordpress.com/the-montage-effect/framing-geographies-of-montage/the-bathos-of-distance/), opening paragraphs, which locate Kuleshov's recollection at 1974 edition pp. 51–52. Clarke reproduces a passage about filming the characters and a pole in separate places and joining them by editing. Consulted the opening web passage on 2026-11-27; not the 1974 book itself. This is a mediated historical account, not a verified original experiment. Interpretation: editing can author a shared space without having recorded that space as such.
- Barratt, Rédei, Innes-Ker & van de Weijer (2016), [Does the Kuleshov Effect Really Exist?](https://doi.org/10.1177/0301006616638595), Perception 45(8), 847–874. Read institutional abstract via [CBS](https://research.cbs.dk/da/publications/does-the-kuleshov-effect-really-exist-revisiting-a-classic-film-e-2/). The authors report context-aligned category choices and dimensional judgments but not the expected differences in eye-tracking measures across emotional conditions. No full report appraisal. The old experiment's status should not be upgraded from film legend on this basis.
- Baranowski & Hecht (2017; online 2016-12-05), [The Auditory Kuleshov Effect](https://doi.org/10.1177/0301006616682754), Perception 46(5), publisher abstract. Music accompanying film material influenced emotional judgments of facial expressions in their task. Full text restricted; only abstract read. This is an audiovisual result, not a pure-audio result or a demonstration of operational communication.
- Szaszkó & Loebus (2026), [Context shapes evaluation of emotional valence, not emotional categorization](https://doi.org/10.1177/20416695251410119), i-Perception 17(2), 1–13. Publisher HTML abstract, Introduction and Results/Discussion paragraphs on explicit categorization consulted. Under a design that removed cinematic continuity and required an explicit context evaluation, the authors report valence effects but no significant context effect on discrete facial-emotion categorization. They propose continuity as a possible explanatory difference. Not a proof of no categorical effects generally; no full appraisal. This contrary result is essential: a context effect on an evaluation is not necessarily a change of category. Their Introduction also discusses the lost original film and inadequate procedural record.
- Christophe Levaux (2017), [The Forgotten History of Repetitive Audio Technologies](https://doi.org/10.1017/S1355771817000097), Organised Sound 22(2), 187–194, Abstract and §§1–3 opening paragraphs, publisher HTML. Levaux recounts the familiar history of Schaeffer's use of locked grooves and spliced loops, and contests the implied priority of postwar electronic music studios by tracing earlier technologies. Schaeffer's own 1952 text not inspected. Interpretation: repetition makes a sound fragment manipulable as an object, while montage reintroduces new relations among such objects. This does not equate reduced listening with a digital sample.

All encounters are selective reading notes, not systematic review or source extraction. No human evidence collected, no meta-analysis, no claim of acoustic superiority. The original Kuleshov film was not viewed. No third-party media included.

## Exact symbolic experiment: the montage organ

Take two finite scores with explicit non-cyclic boundaries:

    I   A X A X B X B
    II  A X B X A X B

Both contain two A, two B, three X, start at A and end at B. Their directed adjacent-pair counts are AX=2, XA=1, XB=2, BX=1. But the X-centred triples are:

    I   AXA, AXB, BXB
    II  AXB, BXA, AXB

Thus I contains two returns through X and one crossing; II contains three crossings. Return/crossing are our stipulated symbolic definitions, not claims about what is heard. The full ordered PCM is distinguishable: the indistinguishability is strictly about the inventory of local cuts, not the recordings.

Formally a receipt records first and last symbols plus a multiset of overlapping directed 2-grams. The initial symbol and edge destination counts determine all unigram counts. Any compatible score is a directed Euler trail on the multigraph of these counts, though counting permutations of indistinguishable edges would overcount distinct words. No graph-theoretic novelty claimed.

A larger family hides the distinction at any selected order k >= 2. Let Q consist of k-1 repetitions of X; let a permutation of m distinct symbols not equal X be p1,...,pm. Construct

    Q p1 Q p2 Q ... pm Q.

Every length-k window contains exactly one non-X symbol (consecutive markers are k positions apart). Each marker occurs once in each of k possible offsets. Therefore the length-k histogram does not depend on permutation, and the shared prefix/suffix Q are fixed. All shorter histograms also agree: length-j counts can be recovered from the prefix of each k-window plus the final k-j start positions, which lie in the fixed suffix. Length-(k+1) windows that contain two markers are precisely pi Q p(i+1). Their ordered pairs recover the directed path of distinct markers; its start is the unique marker with no incoming edge, then each successor is unique. Thus all m! permutations have distinct length-(k+1) receipts while sharing every lower-order receipt through k. This is an explicit family, not a claim that all possible equivalent words have that size or that perception follows k-gram order.

The peculiar artistic opportunity is to choose a scale at which a musical editing operation is invisible to an inspector. One editor can conserve the inventory of samples, another can conserve the inventory of transitions, a third can conserve every three-note motif. A fourth changes what happens at the next scale. None need introduce an original sample.

## Executed qualification and sound work

Run Python 3.11+ (standard library, do not use -O):

    python laboratory.py montage-audio

Native Python 3.13.5 executed twice; recursive byte comparison of generated outputs matched. Exact local Git blob 2dcb05a08e77e917c756523ea7e92cacbe9b1319. The script enumerates all ternary words of lengths 1–9 (29,523 words). For each endpoint/pair receipt, it groups the actual words, asserts common unigram inventory, and counts whether distinct triple receipts occur. At length 9: 2,784 pair receipt classes, 2,295 with differing triple histograms, containing 19,092 of the 19,683 words; largest pair class 36 words. At length 4: 75 receipts, six with differing triples, containing twelve words. These are finite exhaustive census counts, not estimates of musical practice.

The construction is checked on all 3,488 permutations across k=2–5, m=2–6. The test checks all orders through k, fixed endpoints and factorial distinguishability at k+1. Reversal of I is a directed-pair negative control. The explicit I/II pair collision and differing triple receipts are checked. No independent third-party implementation or repository-wide validation claimed.

Five WAVs are rendered: clustered and alternating (2.1 seconds each); third_order_i and third_order_ii (3.3 seconds each, from k=3 and three markers); isolated_x (0.3 seconds). Each symbol uses an immutable 300 ms tile at 16 kHz mono signed PCM16: A 196 Hz, B 523 Hz, C 247 Hz, X 330 Hz, each with fixed envelope and second harmonic. Every occurrence exactly matches its tile, all five hashes differ, headers/amplitude/readback passed, and same-runtime rerendering is identical. The first two use identical multiset of directed pairs; the latter two use identical multiset through order three. No physical listening or perception experiment.

Performance instruction (original): listen to X alone. Listen to I as though X were a place that keeps returning; listen to II as though X were an interstice. Then exchange these instructions. The score does not compel these readings. Next perform the third-order pair while refusing to alter any triple inventory. In a final unwritten movement, use actual recorded sounds with cuts that cannot be made seamless. Let the cut itself acquire a voice.

## Instrument design and possible experiment (unvalidated)

A Montage Organ VSTi could use pre-rendered or authored tiles, a directed transition graph with remaining multiplicities, and a route editor constrained to valid trails. A small exact search could list alternative trails for bounded patch sizes. A real-time implementation would need off-audio-thread solving and bounded queues. A CYD touchscreen could draw crossings and returns through a repeated tile; horizontal motion selects the preserved context order, vertical motion selects an alternate realization. A VSTfx could perform explicitly segmented input, never pretending to infer reliable source identity from arbitrary mixed sound. FM-1 could use fixed parameter gestures as tiles. These are design candidates, not implemented plugins.

A second performer could play the difference between two triple inventories while a first performer retains the original transition histogram. Another could deliberately make local transition statistics an unreliable forecast of global musical structure. A live composer may instead prefer to break the constraint and record when it is broken.

MHAC relevance: summaries of events, transitions or k-grams cannot in general certify a complete event history. A system reporting a correct transition histogram could still omit which earlier event and later event belonged to the same middle occurrence. Consider an explicit event identity and scope ledger as the strongest ordinary-text comparator. Synthetic tests should cross actual sequence, displayed context and presentation order independently; ask for exact event associations, action decisions, confidence and abstention separately, and also measure affect judgments separately. Falsify any claim that adding acoustic motifs improves associations against the typed event table. No claim of benefit, emotion-free perception, or suitability for live control.

Counterargument: a film is not an alphabet. Repeated shots may carry history, rhythm, bodies, memory and material discontinuities. Equal token counts cannot prove equal experiential transitions. A histogram is not a cinematographer. This construction takes local equality seriously so that artists can experiment with it, not to replace the work with its formal inventory.

## Afterword (fiction)

The censor counted every doorway. The editor preserved every doorway. A visitor crossed the building and returned to a place that had not been there before. The censor's certificate was correct; its interpretation was not.

## Repository checkpoint

Base main 495a98ca12bae467a507031f04931aa4254b1866. AGENTS, README, RAG, programme, runbook, integrity and validation read. Forty recent PR titles, 25 active issue titles and targeted searches (montage, Kuleshov, Warburg, bigram, trigram, Euler, adjacency, editing, context window) consulted. Nearest issue bodies #524 (spatial traversal), #672 (faceted classification), #183 (causal order), #696 (retention) inspected; distinct here is preservation of all directed local transition counts with higher-order variation. New issue #765 read back; no comments. No existing branch matched montage in branch search. Only this directory is owned. No canonical manifests, frozen protocol, live evidence, other branches or rights changes. Draft/HOLD pending exact-head checks and integrator review; full repository tests not run locally. No independent human review, participant work, or required human action at this exploratory stage.
