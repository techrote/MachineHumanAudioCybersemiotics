# The Rest That Arrives Too Late
## Syndrome privacy, recoverable omissions and the cost of immediate understanding

**Refs #290 · 24 November 2026 · synthetic mathematical and interpretive expedition.** AI-authored; no participants, empirical findings, accepted Track E/G claims, production privacy assurance or mathematical priority claim.

## 1. Archaeological premise

Draft [#283](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/c99142dabb330f5732b4e1af4cdbf82ce3eaacf9/research/expeditions/silence-buys-anonymity/README.md), §4, qualifies its sharp parity-privacy frontier: if the recipient knows the source parity, an erased bit may be reconstructed. The earlier theorem counts erased local symbols, not missing knowledge. This expedition takes that qualification seriously. It asks how much silence a source law can support, and whether the omitted information becomes known in time. The answer connects the privacy model to classical syndrome decoding, but introduces a distinct causal constraint on the *receiver*.

The accepted [X005 negative-space protocol](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/sound-of-nothing/NEGATIVE-SPACE-PROTOCOL.md), Receiver rule and Falsifiers, forbids inference of resolution merely from expired status, but admits a simpler reliable synchronous contract as a potential falsifier. A known algebraic source constraint supplies a precise example of what such a contract could mean. It does not make the transport erasure itself equivalent to semantic resolution.

Draft [#269](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/a46f7b2924517a378f6a12151740a430ce202c4a/research/expeditions/message-that-borrows-its-audience/README.md), §§1–3, studies missing/stale side-information bits under arbitrary broadcast encoders. Here the side information is instead a shared exact affine source law, the vocabulary is restricted, and the constraint is anonymity. Neither result substitutes for the other. The two can disagree on whether a given omission is cheap.

Main inspected at 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity, validation, X005 and the two pinned draft reports above (relevant sections). Search returned 86 open issue titles before #290; the PR-specific listing returned 68 open PRs. Search with is:pr was not trusted for counting because the connector returned issue results; separate PR listing used. Inspected #282 and #268 issue bodies and comments (none returned), #283 and #269 metadata, #283 exact-head Research integrity run (completed/success). Recent #284–#289 concern first-hit calibration, tuning and moment-null codes; no title-level duplication with this scope. This is a bounded reconciliation, not a substantive review of all open work. No prior draft is promoted to accepted scientific evidence. The core registry remains in progress.

## 2. Exact fixed-mask theorem

All arithmetic is over the binary field. H is an r-by-n matrix of columns h_i, b is a feasible syndrome, and the source X is uniform on the nonempty affine coset C={x:Hx=b}. The recipient index g belongs to an odd number G>=3 of groups. The source distribution is the same for every group. At each tick the encoder sees the source prefix and emits either an even-parity G-bit word or an explicit erasure at a fixed public position. E is a deterministic, source- and group-independent set of erased positions; K is its complement. On K, coordinate g must be exactly X_i, without exception. The recipient reads its own coordinate only, knows H,b,E and the tick boundaries, and may use source-law inference. The observer sees all emitted words and erasure positions but not X or g. Perfect group privacy means identical full transcript laws across g. It does not mean privacy of X itself.

**Theorem A.** A causal encoder with exact delivered coordinates and perfect group privacy exists if and only if b belongs to the column span of H_E. Exact eventual reconstruction by the recipient additionally requires the columns of H_E to be linearly independent.

Proof: let P be the projection of C onto K. It is a nonempty affine subspace; its uniform law follows from constant fiber sizes of a linear projection. Privacy forces a common transcript law. In this law each of the G coordinate rows is marginally uniform on P, since it is the actual delivered row for one possible recipient. With probability one all rows belong to P and their XOR is zero by the even-word restriction. For odd G, XOR of an odd number of elements of the affine coset P belongs to P itself. Thus zero belongs to P. Equivalently some x in C is supported on E, which holds exactly when b is in the span of H_E.

Conversely when zero belongs to P, P is a linear space. Before transmission, choose G-2 independent uniform fake rows from P. Assign them to groups other than g and a designated dependent group. At each delivered tick, set the actual row bit to the current X_i, each fake row bit to its preselected value, and the dependent bit to the XOR of the other G-1 bits. At each erased tick emit the fixed marker. The completed joint law is uniform over the zero-XOR tuples of G rows in P: any G-1 rows determine the remaining row, with every choice equally likely. It is the same for every g. This encoder is causal in the source, although it stores preselected synthetic rows and knows the block schedule. It does not need future actual bits. Computation, memory and law-distribution costs are not priced.

The delivered row satisfies H_E x_E=b+H_K x_K. For a feasible observed row, there is exactly one completion if and only if H_E has trivial kernel. Otherwise adding a nonzero kernel vector supported on E creates two distinct possible source blocks sharing the same observation. Uniformity makes both feasible with positive probability. This proves the two conditions.

**Minimum eventual erasure count.** The minimum is the weight of a minimum-weight vector z satisfying Hz=b, i.e. a coset leader. Any such minimum support is independent: if it contained a nonempty zero-XOR subset, deleting that subset would produce a smaller solution. Therefore the optimum for privacy alone also admits eventual exact reconstruction. For nonnegative weighted erasure costs the same result holds by choosing, among cost-optimal solutions, one with minimum cardinality. Zero-cost redundant columns can be removed without worsening cost.

An executable algorithm uses dynamic programming over reachable syndromes: start with the empty mask at syndrome zero; for each column compare the best existing mask for s with adding the current column to a mask for s XOR h_i. With rank R, there are at most 2^R syndromes; time O(n 2^R) in unit-cost syndrome operations, storage O(2^R) mask records. This is not a scalable general solver for large R.

## 3. Deadlines change the problem

For a fixed E, an erased bit i must be recovered no earlier than its source tick, with deadline d>=i. Let U_d=E union {j:j>d}; all indices in U_d are still unobserved directly. Then the exact criterion for determining X_i from the received prefix is

    h_i not in span {h_j : j in U_d, j != i}.

Necessity: if the column lies in the span, a kernel vector with its i-th coordinate one and support in U_d exists. Adding it to any source word produces an indistinguishable observed prefix but opposite target bit. Sufficiency: if no such vector exists, every pair of feasible completions has the same i-th bit. This also covers earlier inferred values; they are functions of the same prefix and provide no additional information. It yields an exact finite test for heterogeneous deadlines, not a claim that finding an optimal mask under arbitrary deadlines is polynomial.

**Theorem B.** For immediate recovery of all erased bits (d=i), define the rightmost pivot set B by scanning columns from n down to 1, taking a column iff it is not in the span of all later columns. These columns form a basis of the column space. Let S be the unique support representing b in this basis. The full feasible family of perfectly private, immediately recoverable fixed masks is

    S subset E subset B.

In particular S is the unique *minimum-cardinality* mask. It is not the only feasible mask.

Proof: every erased position must be a rightmost pivot. If h_i lies in the span of later columns then even knowing every earlier bit cannot distinguish two possibilities for X_i at its own tick. Conversely if all erasures are pivots, induct forward. Previously erased values have already been reconstructed. At an erased pivot the remaining unknown future columns cannot cancel h_i, so its bit is determined by the full earlier prefix, with no current symbol needed. All erased positions are thus immediately recoverable. By Theorem A the mask must span b, which in the independent pivot basis is equivalent to containing its unique support S.

The reverse basis and representation can be found by ordinary binary Gaussian elimination in polynomial time. The reference laboratory uses explicit span maps to keep the small-model logic transparent, rather than implementing that efficient elimination. The initial computational assertion that the entire immediate feasible family was a singleton failed on surplus pivot masks; the corrected statement above was then tested. This is a genuine self-falsification of an overstrong formulation, not an independent review.

## 4. Arbitrarily large separation and boundary failures

Take R>=1, n=R+1, b=(1,...,1), and H=[b | I_R]. The source is one fair bit z followed by R copies of its complement. Erasing tick one is perfectly private and suffices for eventual recovery, because h_1=b. No zero-erasure mask works, since b is nonzero. But this first column is not a rightmost pivot. The immediate optimum erases all R later ticks and delivers the first bit. The recipient then computes each missing bit before or at its deadline. The ratio of immediate to eventual erasure counts is R, and is as large as possible for a nonzero syndrome at rank R (the immediate cost is at most R, and the eventual cost is at least one).

| Rank | Eventual minimum | Immediate minimum | Minimum if one tick delay permitted |
| --- | ---: | ---: | ---: |
| 1 | 1 | 1 | 1 |
| 2 | 1 | 2 | 1 |
| 4 | 1 | 4 | 1 |
| 8 | 1 | 8 | 1 |
| 15 | 1 | 15 | 1 |

For the one-tick delay column, the first erased bit can be inferred as soon as the first complement arrives. The difference concerns scheduling and lawful knowledge, not transmission errors. It even reverses an intuitive engineering preference: immediate knowledge can require *more* omitted symbols here, because the permitted vocabulary and fixed-mask anonymity constrain which symbols may be sent.

A few boundaries prevent inappropriate generalization:

- With even G, all coordinates can simply repeat the current actual bit, so no mask is needed. With b=0, no erasures are needed even for odd G under the uniform source law.
- If uniformity is removed, the support criterion is insufficient. For H=0 and a single biased source bit with P(X=1)> (G-1)/G, a common even-word law cannot have all coordinate marginals equal to that bias (their expected sum is at most G-1). The support is linear but the required coupling does not exist.
- If an outside observer learns the actual source bit at a delivered tick where that bit is one, conditional perfect group privacy is impossible for odd G: a common conditional law would force all coordinates to equal one. Thus privacy must name the observer view; unconditional privacy cannot be repurposed as privacy given X.
- Adaptive masks, group-dependent masks, arbitrary cross-coordinate decoders, nonbinary codes, uncertain source laws, changing recipients and synchronization failures are outside the theorem. In particular an observer and recipient may have different accessible data, and the decoder might extract additional information from other rows if permitted. No impossibility is asserted for unrestricted schemes.
- If the recipient uses an incorrect parity law, a confident reconstruction may be wrong. The theorem assumes the law is exact; it provides no method for establishing that fact in an actual machine interface.

**Design hypothesis:** a missing-message ledger should record not only omission, but the law and version authorizing reconstruction, exact observed prefix, earliest provable reconstruction tick, required decision deadline, and whether the recipient actually has that law. If any prerequisite is absent, retain UNKNOWN rather than treating an inferred state as warranted. A useful falsifier is to remove one asserted source-law constraint or delay the confirming symbol past the deadline; the system must cease asserting the reconstructed value. No production layer is proposed.

**Artistic score:** four ticks with three parts, even-parity words only, source bit z then three complements. Score A: first tick marked rest, subsequent chords delivered; the first bit's meaning is recoverable only on the second tick. Score B: first chord delivered, three marked rests follow; all three missing bits are inferable at their own ticks. The score is a symbolic experiment, not rendered or evaluated auditory evidence. The rest marker must be distinct from the legal all-zero word.

**Fiction:** The clockmaker is told to omit nothing that the musician cannot immediately reconstruct. She prints a single note and three rests. A second clockmaker prints three notes and one rest, and is accused of withholding more information, although her printed score is longer. They have not disagreed about the notes. They have disagreed about when the performance is allowed to know them.

## 5. Source boundary, execution and disposition

Source comparison (AI, 24 November 2026; abstract/definition reading only). Berlekamp, McEliece and van Tilborg, 1978, *On the inherent intractability of certain coding problems*, IEEE Transactions on Information Theory 24(3), 384–386, [Caltech publisher-version repository record, Abstract](https://authors.library.caltech.edu/records/aw9vs-ann16), DOI 10.1109/TIT.1978.1055873: general linear decoding is established as NP-complete. [MathWorld, Syndrome Decoding Problem, opening definition](https://mathworld.wolfram.com/SyndromeDecodingProblem.html) identifies the minimum-weight syndrome problem and its link to nearest-codeword decoding. The equivalence in §2 is an application of this established problem, not a new decoding algorithm or priority claim. The deadline basis result is a self-contained finite argument using elementary linear algebra; no literature-wide search establishes novelty. No primary text beyond the abstract is claimed read. Source claims are separate from the toy mathematical proofs and proposed design.

Run from the repository root:

    node research/expeditions/rest-arrives-too-late/lab.js

Actual precommit execution in a V8 isolate: all binary matrices with 2 rows and 1–5 columns, and 3 rows and 1–4 columns, including repeated and zero columns and rank-deficient matrices. For each feasible syndrome, the oracle directly enumerates source words and every erasure mask, checking projection membership, injectivity, and whether observed-prefix fibers are single-valued for each omitted bit and deadline. Compare the minimum to the dynamic program, and the entire immediate feasible family to reverse pivots. A separate transcript enumeration implements the actual G=3 and G=5 sampler on selected small cases and compares exact group-conditioned mass counts. Counts overlap; they are not independent experiments.

| Activity | Count |
| --- | ---: |
| Matrices | 6,044 |
| Feasible affine cosets | 34,195 |
| Fixed masks | 583,636 |
| Direct deadline comparisons | 3,181,706 |
| Optimum checks | 68,390 |
| Group-law comparisons | 114 |
| Enumerated transcript draws | 33,452 |
| Rank-gap examples | 15 |
| Input refusals | 5 |

All assertions in the corrected lab passed. The proof covers arbitrary finite dimensions under its assumptions, while execution is bounded. One AI authored all mathematics and code; no external review, actual acoustic/participant evidence or full clean-checkout qualification. No modifications to frozen protocol, central manifests, other workers' branches or canonical claims. Remaining acceptance is substantive review and exact-head integrity CI. Keep this isolated work draft rather than advancing the core programme.

The recovered disagreement is not resolved by saying that silence is good or bad: a missing local report may be recoverable, but the time at which it becomes inferable is an independent property. Eventual knowledge cannot be credited against an earlier deadline.
