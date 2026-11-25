# The Duet That Cannot Bind Its Syllables

**Expedition #514 — 2026-11-25.** Synthetic mathematical research and original digital synthesis; not canonical Track E/G evidence, a priority claim, or a human study.

## The anomaly: every syllable arrives, but the sentences do not

Two synchronized anonymous transmitters each send a binary message of m fields. Each field is rendered with one of two tones. A perfect receiver observes exactly how many of each tone occurred in that slot, not which transmitter emitted it. With exactly two transmitters, this is equivalent to observing the integer sum of the two bits, coordinate by coordinate. Zero and two identify both bits; one identifies the unordered pair {0,1}.

For instance, the unordered pair of messages {0000,1111} and {1010,0101} yield the same four observations (1,1,1,1). This remains true even with perfect component recognition. Global interchange of the two senders is an intended equivalence, not a decoding error. Interchanging their bits at only some coordinates is not.

We allow both transmitters to generate an additional bit by XORing a prescribed subset of their own fields, then send that bit concurrently in a supplementary slot. The receiver again observes an integer sum. The additional slot is a **new encoded statement**, not a function of the previous aggregate. It requires cooperation, agreement on the query mask and a stable pair of messages. No receiver-only manipulation of the original mono mixture creates that missing evidence.

## Exact fibres and the cost of changing the question

Let D be the set of coordinates whose raw sum is one, s its size. Outside D both messages are fixed. On D, the first sender can choose any orientation vector x and the other has its complement. For s>=1, global exchange pairs all 2^s vectors without fixed points. Thus the fibre cardinality is exactly 2^(s-1); for s=0 it is one.

A parity mask r is informative exactly when its intersection with D has even size. Odd intersection makes the two parity bits opposite, so their sum is always one. Even intersection makes them equal; their sum is zero or two, disclosing one binary equation in x, after subtracting the known XOR contribution outside D. Every even-weight vector on D is available as a mask. These equations live in the dual of the quotient by global exchange.

For s>=2, the exact number of noiseless supplementary queries, when D is known first, is s-1. The lower bound is the fibre cardinality and the fact that every query has at most two possible responses within it, even with sequential adaptation. The upper bound compares a chosen anchor coordinate in D with each other coordinate in D. For s<=1 no supplementary query is necessary.

This is not a bound on the number of human-recognizable syllables or physical sources.

## A graph that reconstructs the duet

For weight-two parity probes, only pairs entirely inside D are informative. Represent each such probe by an edge (allow parallel edges, i.e. repeated queries). Its receipt gives the relative orientation of the endpoints. The orientation is determined up to global complement precisely when this graph is connected. More generally, if its component count is c, exactly 2^(c-1) unordered candidate pairs remain, for s>=1. Within a component propagation fixes every relative bit; each component can independently flip.

Compare two candidate source pairs in the same raw fibre, written as {a,b} and {c,d}. Put u=a XOR c and v=a XOR d. Then u and v are nonzero, disjoint masks, and u XOR v is D. The two candidates differ in their supplementary integer sums at row r exactly when both parities r·u and r·v equal one (dot products over F2). To see this, the first pair's bits are p and p XOR (r·D). If r·D is odd both sums are one. Otherwise each sum is twice one bit, and the change is nonzero exactly when r·u=1, which then implies r·v=1.

Hence the exact Hamming distance is the number of rows crossing the partition in parity:

    delta_R(u,v) = count{r in R: parity(r AND u)=parity(r AND v)=1}.

For pair-local rows this is precisely the number of edges crossing the cut of D into the supports of u and v. A dictionary correcting t arbitrary supplementary symbol substitutions and e flagged erasures is equivalent to a minimum cut of at least q=2t+e+1. The raw fields are assumed reliable. The standard distance proof: two receipts at distance at most 2t+e can be made identical by erasing up to e differing coordinates and splitting the rest between the two substitution budgets; larger distance precludes this.

For fixed D, noiseless pair-local probes need s-1 edges (tree). One erasure needs s edges (cycle, including two parallel edges for s=2). One error needs exactly ceil(3s/2) edges. Necessity: all vertex degrees at least three. Sufficiency: take a cycle and add ceil(s/2) antipodal chords joining i to i+floor(s/2) modulo s for i=0,...,ceil(s/2)-1. Every vertex touches at least one such chord. Any cut with at least four cycle edges already passes. A cut crossing just two cycle edges has a shorter side that is a consecutive arc of at most floor(s/2) vertices; the antipodal chord incident on any of those vertices leaves that arc. Thus all cuts have size at least three. This includes s=2, with parallel edges.

## Arbitrary parity and nonadaptive coding

For known D and arbitrary masks, all informative rows implement binary linear forms on k=s-1 anchor-relative coordinates. A fixed dictionary of length n is a binary linear encoding of k bits (plus known offsets) and must have minimum distance at least q. Uninformative rows cannot help. One arbitrary error requires exactly n=k+r where r is the least integer with 2^r >= k+r+1. Lower bound: disjoint binary Hamming spheres of radius one around the 2^k receipts; restricting received symbols to the two valid ones suffices. Construction: choose k distinct nonzero non-unit columns of length r and append the r unit columns to form a parity check matrix. Its kernel has dimension k and distance at least three, and can be expressed systematically. Every resulting linear form is an even mask on D, so its integer sum is a valid query. The laboratory constructs and checks these masks.

These fault budgets are for dictionaries selected after observing D but fixed before supplementary faults. We do not establish optimal adaptive protocols in which the next query depends on a potentially corrupted response.

## Universal dictionaries: a quadratic-to-linear transition

Now require one predetermined supplementary dictionary to work for every possible raw fibre. Every nonempty disjoint pair u,v is realizable: compare {0,u XOR v} with {u,v}. Consequently the exact universal requirement is

    min_{u,v nonzero, u AND v=0} delta_R(u,v) >= q.

For weight-two masks, choose u and v each of size one. Only the edge joining their two vertices is informative. Every pair therefore needs q copies, so the exact universal pair-local budget is q*m*(m-1)/2; the complete multigraph attains it for all larger cuts. This is very different from the s-1 tree available after the disagreement set is known.

The unrestricted universal problem at q=1 is equivalent to a classical binary intersecting linear code. Append the raw identity rows to the supplementary parity matrix R. Two nonzero input vectors whose supports overlap already have overlapping output supports in the systematic positions. Two nonzero input vectors with disjoint supports must have a shared nonzero supplementary coordinate; this is precisely the criterion above. Conversely any systematic intersecting code supplies such a dictionary. A general binary linear code of dimension m can be put in systematic form by a change of generator basis and coordinate permutation. Thus the optimum supplemental length equals the minimum length of a binary intersecting code of dimension m minus m. This is an established coding problem, not a newly named class. For q>1 the criterion is a restricted multiplicity condition on disjoint systematic inputs because raw coordinates are assumed fault-free; it is not the same as a fully q-intersecting code.

For q=1 a universal linear-size existence bound follows from random rows. There are P=(3^m-2*2^m+1)/2 unordered nonzero disjoint pairs, because each coordinate may belong to either mask or neither, excluding empty masks and dividing by two. For any such pair, a uniformly random binary row has independent unbiased parities, and succeeds with probability 1/4. Thus the probability of any uncovered pair after n independent rows is at most P*(3/4)^n. Any integer n for which this is strictly less than one yields a universal dictionary. This is O(m); repeating it q times suffices for fixed q. It is not an exact finite optimum or a practical efficient decoder. A row-weight cap W>=2 restores a necessary lower bound of ceil(q*C(m,2)/C(W,2)) by counting size-two disagreement sets; covering those sets alone does not guarantee larger cuts.

An elementary lower bound for arbitrary masks follows from intersecting codes: restriction to the support of any nonzero codeword must be injective on the entire code, otherwise a nonzero word would be disjoint from it. Hence the support size is at least m. For universal no-fault identification, the augmented systematic code has minimum distance at least m; the Singleton bound gives total length at least 2m-1. A sharper bound may be obtained from known binary-code bounds. The exact universal length is not solved here for general m.

## An exact three-field fault frontier and a finite census

With m=3 the useful masks are the three edges and the all-three mask. Let their multiplicities be x,y,z,w respectively. Size-two disagreement sets require x+w, y+w, z+w >= q. Size-three disagreement sets require x+y, x+z, y+z >= q. Those are all possibilities. Writing S=x+y+z, we have S>=3q/2 and S>=3(q-w). Therefore S+w>=2q, and equality requires w=q/2 and S=3q/2. For odd q, integer w makes equality impossible. The construction x=y=z=ceil(q/2), w=floor(q/2) meets every requirement and attains the lower bound. The exact answer is 2q+(q mod 2). For two fields, exactly q copies of their pair are necessary and sufficient.

For q=1 the exact universal optima in dimensions two through five were computed by exhaustive subset search over all nonzero masks of weight at least two. A duplicate mask cannot help at distance one, and weight-zero/one masks never cover a disjoint pair. For each candidate mask, store a bitset of covered pairs. Enumerate subsets in increasing size; skip branches whose remaining union cannot cover the target or whose new mask adds nothing. The former is a certificate of insufficiency, the latter can only remove redundant rows from a putatively minimal witness. No floating-point solver is involved.

| Fields | Disjoint pairs | Candidate masks | Exact supplementary optimum | Pair-local optimum | Witness (integer bit masks, bit 0 first) |
|---:|---:|---:|---:|---:|---|
| 2 | 1 | 1 | 1 | 1 | 3 |
| 3 | 6 | 4 | 3 | 3 | 3,5,6 |
| 4 | 25 | 11 | 5 | 6 | 3,5,10,12,15 |
| 5 | 90 | 26 | 8 | 10 | 3,5,9,18,20,26,28,31 |

These numbers agree between the native Python implementation and a separately executed JavaScript enumeration of the cut-cover search. Both are same-agent computations, not independent review. The Python implementation additionally verifies literal unordered-pair receipt collisions rather than merely the cut criterion.

## Reproduce and listen

Run from this directory with Python 3.11+:

    python laboratory.py
    python laboratory.py --audio-dir results

The second invocation produces six original 8 kHz PCM16 recordings and the JSON receipt on stdout. Two runs under Python 3.13.5 yielded identical JSON bytes, including audio hashes, on this environment. Floating sine evaluation and rounding are not promised bit-identical across arbitrary platforms; the collision equality holds within any consistent integer-pulse renderer. No third-party sound samples are used. The audio is deliberately kept as a generated artifact rather than repository binary content.

The raw mono pair has four slots of 200 ms, each containing two aligned tones of 250 and 500 Hz. Compare the source allocation {0000,1111} to {1010,0101} (bit 0 first). Their raw mono PCM files are byte-identical; the separately rendered stereo stems differ. Appending the optimal five-row universal dictionary for four fields produces extra sums (0,0,0,0,0) versus (2,0,0,2,0). These longer mono recordings differ. The synthesis exposes the exact same algebraic relation as the proofs, using fixed phase and integer addition with no clipping.

Native receipt: 360 raw fibres, 833 literal pair-distance comparisons, 2,066 complete row-subset equivalence checks, 8,166 graph cut checks, 8,166 Hamming cut checks, and 70,342 bounded three-field multiplicity profiles. The no-fault optimizer visited 732,786 nodes in total. All assertions passed. The qualification JSON gives each optimum and witness plus literal audio hashes. The script and receipt are standalone; the repository validator is a separate check.

## Where the metaphor breaks

The relation to semiotics is an interpretation: a sign can communicate its component inventory completely yet fail to communicate which components belong together. A grammar is not only a list of recognizable tokens; it also needs recoverable relations. The same applies to concurrent machine status reports such as source/event binding. The parity rows are explicit relational receipts, not an intrinsic language of hearing.

Negative results and restrictions:

- An unordered pair of messages is not the identity of either physical sender. Even perfect supplementary parity cannot label the pair; an independent source-specific anchor is required.
- The all-fields parity alone fails for larger disagreement sets: when s is odd it is always uninformative; when s is even it supplies at most one bit. Covering every pair of coordinates is not sufficient if the available masks are arbitrary; e.g. one all-fields mask covers every two-element disagreement set yet fails on triples.
- Recomputing any deterministic function of the raw sum cannot resolve a raw collision. The transmitters, not just the receiver, must supply the new information.
- A third anonymous sender changes the fibre and the parity algebra; no extension to three or more is claimed.
- No synchronization, source liveness, phase coherence, raw-error correction, room-acoustic or independent-source physical model is provided. Unequal source gains and distinctive timbres may supply additional information but are excluded here.
- Predictable melodic continuity may help perceptual grouping but is a prior, not an authenticated historical allocation. Human binding, learning effort, interference, timing and accessibility would need authorized evaluation. No safety or alarm-design recommendation follows.

Design hypothesis: a two-source toy receiver could return the full candidate pair set, a graph of established binding relations, and an explicit distinction between anonymous pair recovery and authenticated sender identity. Compare raw parallel motifs, local parity witnesses, arbitrary parity witnesses and a serialized source-labelled baseline under matched payload and duration. Test correctness, latency and mistaken source assignment separately. An offline algorithm can exhaust all candidates for small m; a real human interface may find parity unintuitive. Negative or null transfer is a useful possible outcome.

Fiction: Two singers enter a room. The clerk hears every syllable and copies them in two columns. The composer swaps half the syllables between singers and the clerk hears exactly the same song. On the next page the singers each add a word that depends on two of their own earlier words. The clerk can now reconstruct the two sentences. He still cannot say which singer spoke either sentence.

## Source and repository ledger

Read live AGENTS.md, README.md, RAG.md, docs/PROGRAMME.md, docs/AGENT_RUNBOOK.md, docs/RESEARCH_INTEGRITY.md, docs/VALIDATION.md, and research/protocol/README.md. Main base 495a98ca12bae467a507031f04931aa4254b1866. Reconciled 317 branch entries and 100 recent open issue and 100 open PR results. Targeted searches for adder, intersecting codes, parity, unlabelled, source attribution and binding; no exact adder/intersecting-code issue surfaced. Read issue #230, #34, #502 and their comment collections; inspected #230 and #502 reports. #230 assumes a balanced ownership assignment to disjoint events and a labelled membership query; here both senders speak every slot and the supplement is an anonymous sum of their XORs. #34 is an empirical/protocol tangent on compositional field binding, not an implemented acoustic adder. #502 studies pair interference for a specific waveform family rather than sender-wise parity of two messages. Distinction is bounded by inspected records, not an exhaustive novelty claim. Created #514, fetched its body and empty comment collection, and created a fresh branch at main. Only new expedition files are changed in this PR.

Preceding #503's exact-head CI failed at repository Markdown validation (mathematical multiplication mistaken for a local link with target -1). Its unit tests passed. Verified unchanged prior head before repairing that one expression on its own earlier expedition branch, not another worker's branch; correction head 68b97f540044b81214413ae33188b9aea9d252ea. Follow-up CI was in progress when inspected. Native repository checkout could not resolve github.com; connector publication and standalone native execution were available. Full repository tests are not claimed locally.

Sources inspected by one AI agent on 2026-11-25; no external reviewer or participants:

- Cohen, G. D. and Lempel, A. (1985), *Linear intersecting codes*, Discrete Mathematics 56(1), 35–43, https://doi.org/10.1016/0012-365X(85)90190-6. Bibliographic identity cross-checked with DBLP and MaRDI. Publisher DOI retrieval failed; text transcription at https://www.academia.edu/27247308/Linear_intersecting_codes inspected Definition 1, Proposition 1 and Corollary 1, printed pp. 35–36. It defines intersecting codes and gives support-size bounds by injective coordinate restriction. OCR quality limits access; the proofs used here are self-contained and not dependent on uncertain symbols. No original page images retrieved from this HTML transcription.
- Balogh, J.; Nguyen, T.; Östergård, P. R. J.; White, E. P.; Wigal, M. C. (2025 revision), *Improving Uniquely Decodable Codes in Binary Adder Channels*, arXiv:2312.11723v2, https://arxiv.org/html/2312.11723v2. Read Abstract and §1 including the distinction between separately labelled constituent codes and same-code binary Sidon sets. This is direct ancestry for the integer-sum model, not validation of the specific reliable-systematic-coordinate fault model. The paper's unequal-constituent constructions are not claimed as our own or reproduced here.
- Bendixen, A. (2014), *Predictability effects in auditory scene analysis: a review*, Frontiers in Neuroscience 8:60, https://doi.org/10.3389/fnins.2014.00060. Read publisher text on concurrent versus sequential grouping, similarity, continuity and the later discussion of bistability and predictability. It provides contrary constraints: grouping can use several physical and contextual cues and can change despite unchanged stimuli; strict predictability is not necessary. Review-level source, not a selected empirical study or evidence that parity receipts benefit listeners.

Formal statements above are derived within the explicit mathematical model. The finite census is computational evidence. Sonifications are synthetic demonstrations. The human-interface transfer is a design hypothesis; the closing scene is fiction. No claim of scientific priority, Brier endorsement, human validation or completed canonical research stage.

## Remaining acceptance

Standalone reproducibility is established; independent mathematical critique, full exact-head repository validation and integration acceptance remain pending. Leave this as a scoped Refs-only draft. A general universal optimum, intermediate mask-weight/fault bounds, labelled identity anchors and raw-slot noise remain open. Do not alter shared manifests or treat these files as canonical evidence.
