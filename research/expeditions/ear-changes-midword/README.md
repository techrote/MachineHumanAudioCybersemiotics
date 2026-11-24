# The Ear That Changes Midword

Exploratory MHAC expedition #316, 24 November 2026. **Formal derivations and synthetic computation only.** No Track E/G admission, production auditory decoder, participant finding, peer review, claim of mathematical priority or evidence of human parity perception.

## Question and provenance

A receiver can observe a different attribute of a symbol at different moments. Is a code qualified against every fixed observer necessarily qualified against a changing observer? If the observer identity is supplied to the decoder, does that repair the problem? The anomaly is that even *perfectly recorded* observer changes can destroy all zero-error communication for an entire range of word lengths.

Reconciled main at 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity and validation. Reviewed recent open issues/PRs and branch search; #309, #311, #313 and #315 are separate draft branches; #309 exact-head workflow succeeded, which is not scientific acceptance. Target issue #316 was freshly created and had no comments. Search for rank-metric and receiver-switching issues did not find this particular model. #268 treats different private side-information sets, #309 spatial phase distance, #314 temporal anonymity, and #51 mixed codebook versions; none is used as an accepted premise. This expedition owns only its new directory. Main is deliberately not modified. Open issues and existing worker branches are not claimed to be exhaustively reviewed for scientific content; the nonduplication search is bounded.

## Model

Let d >= 2, T >= 1 and s >= 0 be integers. A message is a length-T word X of column vectors x_t in F_2^d, or a d-by-T binary matrix. At tick t the receiver sees one bit y_t = a_t^T x_t, where a_t is any nonzero vector in F_2^d. The trajectory a is allowed at most s changes between successive ticks. Initially the entire trajectory is known to the decoder, but not to the encoder. A deterministic block code C is valid if for every permitted trajectory, the map X -> y is injective on C. The channel is noiseless, synchronized, noninteractive, and all nonzero linear functionals are available to the adversary; no prior on messages or observer trajectories is required.

The quantifier is important: for a fixed pair of different words, a single legal trajectory witnessing equal output is enough to invalidate the code. The two candidate messages must be compared under the SAME trajectory in the known-observer model. This is not an assertion that an actual listener chooses an adversarial trajectory, or that human ears implement XOR. A binary projection is a deliberately stylized software observation/feature-extraction operation.

## Fixed observers: exact baseline

For s=0, words X and Z are confusable iff some nonzero a annihilates every column of X-Z, equivalently rank(X-Z) < d. This is full-distance rank-metric coding, a known setting. If T<d, every pair is confusable, hence the maximum message count M(d,T,0)=1. If T>=d, M(d,T,0)=2^T: one fixed nonzero a gives the upper bound. For achievability, regard each row as the coordinate vector of an element of the field F_(2^T). Fix d linearly independent field elements b_1,...,b_d. Encode each field element m as the d rows m*b_i. A difference of distinct messages multiplies every b_i by a nonzero field element, preserving their independence. The resulting difference matrix has rank d. This is a self-contained maximum-distance field-multiplication construction, not a novelty claim about MRD codes.

## Exact switch cost: a rank segmentation certificate

For a given nonzero difference word W, a trajectory hides it iff each maximal constant-observer run is a contiguous block whose columns lie in a proper subspace of F_2^d. Indeed a nonzero annihilator exists iff the column span has rank < d. Conversely, choose an annihilator for each such block and concatenate the choices. Adjacent identical choices can be merged, so the number of switches is no larger than the number of block boundaries.

Let B(W) be the minimum number of nonempty contiguous rank-deficient blocks covering W. The minimum switch count needed to hide W is exactly B(W)-1. The two directions above prove equality: every hiding path induces such a cover, and every cover yields a hiding path. This also handles the zero difference (one block). For d>=2 a single column never spans, so a cover always exists.

Greedy algorithm: take the longest initial rank-deficient block, then repeat on the remaining suffix. This minimizes B. Given any minimum cover, its first cut lies no later than the greedy cut. Extend its first block to the greedy cut, discard swallowed blocks, and truncate at most one remaining block; truncation cannot increase rank. The resulting cover has no more blocks. Induct on the suffix. Thus the simple streaming greedy algorithm is an exact pairwise refusal oracle, not a heuristic.

The lab separately computes min-plus dynamic programming directly over observer identities. On each new symbol it retains the least number of changes reaching each compatible nonzero a; stay costs zero, switch costs one. This independent procedure does not compute spans. The two were compared on every word in the declared census.

## Sharp onset of communication

Write T0=(s+1)(d-1)+1. Then:

* If T<T0, M(d,T,s)=1.
* At T=T0, M(d,T,s)=2^d.
* If T>=T0, M(d,T,s)<=2^(T-s(d-1)).

Proof of impossibility: split any difference into at most s+1 blocks of length at most d-1. Every block has deficient rank, hence a hiding trajectory exists. This applies to arbitrary, including nonlinear, codebooks. In particular, switching freely between ticks (s>=T-1) destroys all zero-error communication for d>=2, even though every reading is one exact bit and its identity is known.

Proof of the cardinality upper bound: fix a nonzero projection a on the final L=T-s(d-1) ticks. If two codewords yield the same L-bit suffix under a, hide their difference on each of the s preceding blocks of length d-1 by selecting an annihilator, then use a on the suffix. There are at most s changes, so injectivity of the suffix map is necessary. Its range has size 2^L. At onset L=d.

Proof of attainability at onset: identify column vectors with F_(2^d), choose a binary basis e_1,...,e_d, and transmit x_t=m*e_(1+((t-1) mod d)) for each m in F_(2^d). For distinct m, the difference in every consecutive d-column window is a basis. Among at most s+1 constant-observer runs covering T0 ticks, at least one must contain d consecutive ticks. No nonzero projection annihilates that window, so all pairs are distinguished. The construction remains valid for longer T by continuing the periodic basis. These are exact binary-vector statements. The same proof works with a finite field of q elements by replacing 2 with q; the executable census is binary only.

A sharper onset characterization: at T0, every valid pair must have full rank on each of the s+1 designated d-column windows beginning at indices 1+j(d-1) for j=0,...,s. Necessity follows by allocating the remaining ticks to s blocks of length d-1. Sufficiency follows because these windows have disjoint sets of internal boundaries; hiding the pair needs at least one switch inside each. These windows overlap at endpoints, not at their internal boundaries.

For d=2, two ticks suffice for a four-message fixed-observer code. One change makes every two-tick code trivial. Three ticks restore a four-message code, with periodic basis [1,2,1]. At d=8 and s=3 the onset is 29 ticks, rather than 8. This is an exact latency cost of a worst-case guarantee, not a proposed auditory response time.

## The extra tick that will not behave: exact nonlinear census

The preceding upper bound is tempting to interpret as universally attainable. It is not.

For d=2, represent each column by a number 0..3 (binary coordinates); integer word encodings use the earliest column in the least significant two bits. Make a Cayley graph on all 4^T words, adjacent iff greedy minimum hiding switches > s. A valid code is a clique. Translate any clique by one of its words to include the zero word; this preserves every difference and eliminates no possible size. The exact search then only needs the neighbors of zero.

| T | s | Cardinality upper bound | Exact maximum | Nonzero neighbors of zero |
|---:|---:|---:|---:|---:|
| 2 | 0 | 4 | 4 | 6 |
| 3 | 1 | 4 | 4 | 12 |
| 4 | 1 | 8 | 8 | 108 |
| 4 | 2 | 4 | 4 | 24 |
| 5 | 2 | 8 | **5** | 264 |
| 5 | 3 | 4 | 4 | 48 |
| 6 | 3 | 8 | **4** | 624 |

The search builds adjacency from admissible XOR differences. Each candidate coloring partitions the remaining vertices into independent sets, hence bounds clique-extension size. Recursive branching includes or excludes vertices and prunes only when the coloring upper bound cannot beat the incumbent. All returned cliques are independently verified by enumerating all actual permitted trajectories, checking injectivity (not just rank or a claimed optimality certificate).

The five-message witness at T=5,s=2 is [0,958,633,479,103]. An additional increasing-index exhaustive search builds its graph using the observer DP, not rank; it uses NO coloring or optimality heuristic, and checks whether five pairwise-compatible neighbors of zero exist. It examined 22,624 recursive nodes and refused a six-word clique. Thus the 5-versus-8 gap is not a failed heuristic search. A separate Python implementation of the greedy/coloring method executed locally and reproduced all seven maxima; the committed CJS implementation additionally includes the independent DP-based refusal. This remains a bounded computational result, not a closed-form formula for arbitrary T and s.

There is a genuine nonlinear advantage here. Every binary linear or affine code has power-of-two cardinality, so in the five-message case such a code can contain at most four words. Four are achievable by padding the onset construction. The fifth symbol is a 25% increase in alphabet cardinality; it does NOT permit transmission of three independent binary bits in one block. The exact cardinality frontier away from onset remains open in this expedition. The T=6,s=3 case also refuses the attractive conjecture that merely appending one tick always improves cardinality.

## The observer identity is itself information

Now remove the trajectory metadata, even when the observer never changes (s=0). The decoder must distinguish the sets of possible outputs for different words, not merely compare outputs under a shared observer.

For a d-by-T matrix X of rank r, its set of possible outputs under nonzero a is the image of the map a -> a^T X: if r=d it contains all 2^d-1 nonzero vectors of its row space and no zero; if r<d, it also contains zero. At most one rank-deficient word can therefore appear in a valid code. Full-rank words consume disjoint sets of 2^d-1 nonzero outputs. Consequently for T>=d,

M_hidden(d,T,0) <= 1 + floor((2^T-1)/(2^d-1)).

For T<d, all words are rank-deficient and the maximum is one. If d divides T, the displayed bound is sharp: identify F_2^T with the k=T/d-dimensional vector space over F_(2^d). Its one-dimensional field subspaces partition all nonzero vectors, each into a set of size 2^d-1. Choose a binary basis for each of these d-dimensional subspaces and use it as the rows of a word; include the all-zero word. The output sets are disjoint and exhaust the binary output alphabet. This is the familiar finite-geometric spread construction applied to this observer model; no priority claim. For other T the upper bound is not claimed sharp.

At T=d the observer-known maximum 2^d falls to exactly 2 if its identity is withheld. The hidden-observer maximum at d=2,T=10 is 342, versus 1024 with metadata. The lab explicitly constructs and tests five GF(4) spreads, covering every output for T=2,4,6,8,10. This is a different problem from privacy: the receiver is trying to infer the message, not conceal identity from an adversary. With switching and hidden metadata, the known-path guarantee cannot automatically be reused; the exact general frontier is not resolved here.

## Reproduction and acoustic score

Run from this directory with Node:

    node laboratory.cjs
    node laboratory.cjs --out /path/to/new/output-directory

The first command prints the deterministic JSON receipt; the second also writes six original mono 8 kHz 16-bit PCM WAVs. The receipt records every exact search and witness. V8 core was actually run, not merely generated. Native Node filesystem wrapper and full repository checks were not exercised in that core execution.

- 124,828 complete difference words: d=2,T=1..8 and d=3,T=1..5, greedy versus direct observer DP.
- Seven exact nonlinear clique searches, with actual-path verification; separate six-word refusal for the five-message optimum.
- 25 onset constructions (d=2..6,s=0..4), 13,330 pairwise checks against both oracles.
- Five hidden-observer spread constructions.
- Six PCM arrays, direct equality/inequality assertions as well as FNV-1a fingerprints. FNV is a reproducibility label, not a cryptographic proof.

The sound mapping is deliberately mechanical: bit 0 -> 200 Hz square-wave event, bit 1 -> 400 Hz, each 100 ms with integer attack/release. Two source words [0,0] and [1,2] differ under any fixed nonzero projection, but under the legal switching trajectory [2,1] their emitted bit sequences are both 00. With the extra basis column, [0,0,0] and [1,2,1] differ under the chosen [2,1,1] trajectory (000 versus 001), and the onset theorem guarantees distinction under every legal one-switch trajectory. Fixed, switched and repaired WAV pairs are rendered and compared. The audible rendering is of the *projected* bits, not a claim that the raw two-dimensional symbols acoustically sound like parity.

A performance instrument proposal: two original melodic coordinate streams controlled by a performer, a second performer selecting one of the three parity readouts, a third operating a decoder supplied with (or deliberately deprived of) the selector trajectory. Two source phrases can collapse to the same emitted melody; extend the phrase or constrain selector changes to recover the distinction. A gallery could expose competing messages in the decoder's current fiber rather than silently choosing one. A robust five-symbol alphabet with only two coordinate streams and five ticks gives an unexpected repertoire beyond binary linear construction. The score generator exists; the performance interface, listener learning, aesthetic preference and usability are untested hypotheses.

## Interpretation, contrary cases and source ledger

Interpretation: qualification against each fixed observation channel does not imply qualification against all sequences assembled from those channels. An asynchronous observer may change its feature projection, attention policy or software parsing mode midword. In an engineered system the metadata can identify the channel yet the information destroyed by switching is still destroyed. Conversely, if a receiver really can observe all coordinates simultaneously or the sender knows the entire trajectory in advance, the bound need not apply. With known trajectory at the encoder, each tick can encode one arbitrary bit by choosing a vector with the required projection, so 2^T is achievable even with arbitrary switching. This is a useful positive control.

A candidate "observer continuity receipt" should retain the message/codebook identity, observation operators, synchrony model, maximum allowed state transitions, whether the selector history is available at encode/decode time, minimum pairwise hiding-switch certificate, and independently validated codebook cardinality. Real acoustic operators, imperfect classification, noisy readouts, resynchronization, feedback, probabilistic errors, restricted observer sets, nonbinary semantic costs, and switching within symbol windows are all outside this theorem. No extrapolation to human attention, cognitive disability or Brier's position is made. The model's observer alphabet is exhaustive nonzero linear maps; a smaller set may avoid the impossibility. A finite-field multiplication construction is not a claim that a human could learn the associated motifs.

Sources accessed on 2026-11-24 by one AI research agent, web HTML full-text access at cited passage level. No entire-book or independent human reading asserted.

1. Alessandro Neri and Ferdinando Zullo, *Rank-metric codes over arbitrary fields: Bounds and constructions*, arXiv:2601.15464v1, 21 Jan 2026, [HTML](https://arxiv.org/html/2601.15464v1). Read introduction, §1.1 definition 1.1, §1.2 theorem 1.8/proof and §1.3 theorems 1.16–1.17. Source supports known rank-distance definition, Singleton-style bound and finite-field attainability; the specific elementary fixed-observer construction above is independently proved. Survey traces Delsarte 1978 and Gabidulin's later work; original historical articles not read in this run.
2. Sergey Loyka and Charalambos D. Charalambous, *A General Formula for Compound Channel Capacity*, arXiv:1604.01434v1, 5 Apr 2016, [HTML](https://arxiv.org/html/1604.01434v1), introduction and §II Channel Model (especially the distinction between constant/varying states and augmentation of output by receiver CSI). Their setting permits stochastic channels and vanishing error; this expedition instead uses finite deterministic zero-error guarantees and a bounded switch count. No capacity theorem is imported from their paper.

The sharp onset, segmentation theorem and finite census are deductions under the declared model. The spread and rank-metric ancestry is acknowledged. No exhaustive novelty search or independent expert validation was performed. The formal results do not alter MHAC's frozen corpus or empirical research status.

## Fiction — The three ears of a customs house

The customs house had three interpreters. One listened to the left flute, one the right, and the third to whether their notes differed. Each interpreter alone could certify every permitted declaration. One winter the interpreters began sharing shifts, so the first half of a declaration sometimes reached one desk and the second another. The ledger faithfully recorded every transfer. Nevertheless two declarations acquired the same entry.

The director suspected a lost stamp. The apprentice drew two columns on the ledger and added one more beat to every declaration. Later, when two transfers were allowed, he discovered that five declarations could survive where his neat binary filing system allowed four, but his promised eight would not fit.

The house kept the extra beat. It also kept the names of its interpreters.

*The record of a change of ear was not the information that the ear had failed to hear.*
