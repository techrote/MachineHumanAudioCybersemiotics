# The Message That Borrows Its Audience
## Context debt, missing knowledge, and the parity of a shared announcement

**Refs #268 · 24 November 2026 · original exploratory mathematics, interpretation and synthetic sound.** No Track E/G admission, empirical observation, production implementation or human validation. No mathematical priority asserted.

A public announcement need not contain all the propositions it conveys. Each recipient may bring different missing pieces. A single shared sound can therefore be sufficient for several incompatible-looking purposes. But if the announcer no longer knows which prior pieces remain available, the code can become expensive even when only one piece is missing anywhere in the entire audience.

## Contents

1. [Model](#1-model) — distinguish context loss, context uncertainty and corrupted context.
2. [Ring theorem](#2-ring-theorem) — exact cost with and without knowing the single erasure location.
3. [Complete audience theorem](#3-complete-audience-theorem) — a connection to Hamming geometry and stale context.
4. [Executable laboratory](#4-executable-laboratory) — exhaustive checks, independent fiber census and sound witness.
5. [Exaptation](#5-exaptation) — grounding, distributed software, an audience-dependent musical instrument and limits.
6. [Source and execution ledger](#6-source-and-execution-ledger) — exact reading extent, repository boundaries and reproducibility.
7. [Fictional afterword](#7-fictional-afterword) — the broadcast that had to learn its listeners.

## 1. Model

Let x be an arbitrary n-bit vector, with n >= 2. Receiver i demands x_i and initially has specified other coordinates. A sender observes x and broadcasts one noiseless fixed-length binary string E(x) of length L, common to all receivers. Each receiver must decode its own bit with zero error using only the broadcast, its receiver identity, and its local labelled side information. No receiver collaboration, new queries, free information about x, probabilistic prior, or message length variation is allowed. A declared code and mask policy are known in advance; an externally supplied erasure location in the known-location regime is not charged to L. Decoders can be arbitrary functions. All statements concern single-bit scalar messages, not asymptotic rates.

Four regimes:
- Nominal: all specified context bits correct.
- Announced erasure: exactly one directed side-information edge (i,j) is absent, the location is known to sender and receivers before choosing a code, and all other side information is correct.
- Unannounced detected erasure: zero or one directed edge globally is absent. Sender cannot tailor E to the location. Each recipient knows its own surviving labels and values, but not necessarily any other recipient's fault.
- Unannounced stale bit: zero or one side-information bit globally is wrong; neither sender nor recipient knows its location. No erasure mask is supplied.

The last two models are not the same as a corrupted broadcast. The broadcast is perfectly received throughout. All possible input vectors and permitted faults must work. Because each decoder is local, the globally-at-most-one condition imposes exactly the same decoder constraints as permitting one fault at *each* receiver independently. Every individual local fault has a witness in the globally bounded set; successful local decoding composes without any need to test simultaneous faults. This observation fails if fault identities are communicated or receivers collaborate.

A broadcast fiber is the set of x mapping to one codeword. No two states in a fiber may produce an identical local observation at a receiver whose requested bits differ. This elementary observation gives lower bounds for arbitrary deterministic encoders, not only linear ones. Conversely, if all fibers satisfy the constraint, table-lookup decoders exist. A fixed-length code needs at least the ceiling of log2(number of fibers) bits.

## 2. Ring theorem

Let n be even, n >= 4, and let each receiver know the bits of its two cyclic neighbors.

| Regime | Exact length |
|---|---:|
| Nominal | n/2 |
| Announced erasure | n/2 |
| Unannounced detected erasure | n-1 |
| Unannounced stale bit | n |

Proof of first two rows: fix the bits at all odd-numbered positions. Each even receiver's complete side information is then fixed, so its requested bit must be determined by the broadcast. There are 2^(n/2) even-bit assignments; they need different broadcasts. An erased edge cannot improve on the nominal optimum. For achievability, transmit pairwise XORs on one alternating perfect matching. Each receiver knows its matched neighbor and can recover its own bit. The cycle has two edge-disjoint alternating matchings; for any one announced missing directed edge, choose the matching not using its undirected edge. No extra payload bits are required. This says nothing about the cost of learning the fault or distributing the chosen matching.

For an unknown erasure, each receiver must be able to decode from either one of its neighbors. Even though at most one edge fails globally, all these decoder obligations are imposed on one E. Suppose x and y share E(x)=E(y) and agree at any vertex j. For a neighbor i of j, choose the allowed local erasure that removes i's other neighbor. The resulting local observations agree, so x_i=y_i. Continue around the connected cycle. Agreement at even one coordinate forces x=y; a fiber contains at most two states, and distinct states in it are complements. Therefore 2^n source vectors require at least 2^(n-1) broadcasts. Send the n-1 XORs along a spanning path: any known bit determines all others recursively. This achieves the bound. More generally, on any undirected graph where each non-isolated receiver is guaranteed one arbitrary correct labelled neighbor (and no other guaranteed side information), the exact cost is n-c, where c is the number of nontrivial connected components. In each such component at most a binary global complement remains; isolated vertices demand direct transmission. A spanning forest plus isolated raw bits achieves the bound.

For an unannounced stale bit, pick any distinct x,y and a receiver i where they differ. Its two side-information bits can differ in at most two positions; their binary radius-one Hamming balls intersect. A shared local observation is permitted in two separate worlds, each with at most one erroneous bit globally, so any shared broadcast would fail. Every fiber must be a singleton. Raw transmission attains n. This ring stale row is an analytical extension, not part of the executed ring census.

In particular a single known missing edge costs no extra broadcast bits, but uncertainty over where that same one edge may be missing almost doubles the cost for large rings. The ratio (n-1)/(n/2) tends to two. This is a minimax quantifier distinction, not a claim that the listener has lost half its memories.

## 3. Complete audience theorem

Now each receiver initially knows every bit except its own.

| Regime | Exact length |
|---|---:|
| Nominal | 1 |
| Announced erasure | 2 |
| Unannounced detected erasure | ceil(log2(n+1)) |
| Unannounced stale bit | 1+ceil(log2(n)) |

Nominal: one parity bit solves all requests; zero bits cannot distinguish two source states differing only in a receiver's target. Announced missing (i,j): fix all other n-2 bits. Receiver i has the same side information in all four assignments to (x_i,x_j), so E determines x_i, and then receiver j can recover x_j using that x_i. Four distinct broadcasts are necessary. Transmit x_i and the parity of the entire vector. Receiver i reads its bit directly; every other receiver has all its intended side information.

Unannounced detected erasure: two states differing in exactly one or two coordinates must have different broadcasts. Choose a differing receiver and erase the other differing coordinate, if any. Conversely if their Hamming distance is at least three, a differing receiver still has at least one differing known bit, so no confusion is possible. Thus a fiber is exactly a binary code of minimum distance at least three (singleton fibers allowed). Radius-one Hamming balls in a fiber are disjoint, each of size n+1, hence the fiber size is at most 2^n/(n+1). At least n+1 broadcasts are needed, including for nonlinear encoders. Let r=ceil(log2(n+1)); assign n distinct nonzero r-bit columns h_i (e.g. integers 1 through n). Send the XOR of h_i for each x_i=1. No nonzero difference of weight one or two can have zero syndrome, so the bound is attained. This reconstructs a classical parity-check construction, not a new coding-theory priority claim.

Unannounced stale bit: differing target i can be confused exactly when the two complete side vectors differ in at most two positions, because their radius-one balls intersect exactly then. Therefore fibers have minimum distance four. Puncture one coordinate from every member of a fiber: no two become equal and minimum distance is at least three. Disjoint radius-one balls in the (n-1)-cube now have n elements, so a fiber has size at most 2^(n-1)/n; at least 2n broadcasts are necessary. For r=ceil(log2 n), use the n distinct (r+1)-bit columns h_i=(1,binary(i)), i=0,...,n-1. A sum of one or three has leading parity bit one; a sum of two cannot vanish because labels are distinct. Thus every fiber has distance >=4, attaining the bound. Kim and No already establish the corresponding linear optimum (source S2); the elementary packing argument here also covers arbitrary deterministic fixed-length encoders. No literature-wide novelty claim is made.

The complete graph loses only one bit of payload efficiency when the location of a single erasure is announced, but its universal redundancy grows logarithmically with the audience size. The cost for stale bits is equal to the erasure cost when n is a power of two, and one bit greater otherwise. Thus even an intuitively more severe fault does not invariably increase the optimal integer payload length.

## 4. Executable laboratory

Run from this directory:
 
    node laboratory.js
    node laboratory.js ./generated-scores

The second command additionally writes four original WAV files. Neither generated WAVs nor copyrighted source texts are committed.

The core JavaScript function was actually executed in a tool isolate. It checked 2,073,360 local decoder observations: for every n=4,6,8,10 ring input and receiver, both the nominal, each announced erasure, and the universal erasure code; for every n=2,...,10 complete-graph input and receiver, also every single flipped-side-bit observation. A map keyed by (broadcast, surviving mask, received values) refuses conflicting target values. Each announced erasure is evaluated separately using the corresponding selected encoder. Counts include repeated observations in different states or scenarios; they are not independent empirical measurements.

A separate direct compatibility search enumerated 328,485 nonempty source subsets (candidate fibers) over complete graphs n=2,3,4 in three regimes, and the four-vertex ring in the nominal and universal erasure regimes. It checks every potentially conflicting pair using overlap of local observation sets, independent of the syndrome construction. Maximum fiber bounds matched the predicted fixed-length minima in all eleven cases. This is a check of the lower bound in small finite populations, not a general proof or independent reviewer.

Negative control: in the 4-ring, bits indexed 0 through 3, states A=0000 and B=(x_0,x_1,x_2,x_3)=(0,0,1,1) both yield (0,0) on matching (0,1),(2,3). If receiver 2 loses bit 3, its surviving bit 1 equals zero in both states, yet its target differs. The code that worked perfectly before now becomes unconditionally ambiguous for that observation. The universal path code yields (0,0,0) versus (0,1,0), allowing recovery.

**The Borrowed-Audience Organ:** two bits are rendered as two short square-wave pitches, zero at 250 Hz and one at 500 Hz, with 10 ms gaps between slots; 8 kHz mono PCM, fixed amplitude. The nominal pair of WAVs is byte-identical (3,244 bytes each); the robust pair is byte-distinct (4,844 bytes each). Reproduction identifiers and bytewise comparison are recorded in execution.json. The code uses distinct physical slots for bits: no claim that these particular frequencies are perceptually separable under a real acoustic channel. Node wrapper not executed in the isolate; the generated arrays were constructed in memory.

## 5. Exaptation

Clark's account of grounding (S3) treats collaborative understanding as a prerequisite of a joint project, adequate to its purposes. Our formal context is much narrower: labelled bits, not mutual belief, shared attention, situated understanding, authority, or pragmatics. The bridge is an interpretation: a compressed message is a function of both what the sender transmits and what the recipient can reliably supply. Grounding may be an active process for establishing those premises rather than a static codebook field.

Imagine a machine announcing parity over two machine states: a recipient who can inspect one state may recover the other. The acoustic payload does not uniquely denote a requested bit without that context. The same utterance may be locally unambiguous to several listeners, each using different correct background facts. A perfectly audible message can be semantically ambiguous after context loss even if no acoustic noise exists. This is not an endorsement of XOR-coded public safety alarms; it exposes an extreme dependence on recipient knowledge.

Candidate engineering receipt: requested propositions, recipient identity, labelled context prerequisites, source/version and freshness epochs, whether erasures are detected, where fault information is available and when, shared code identity, explicit decoding domain and fallback. A simulator can test loss, stale values, and unannounced context mismatch separately. In agentic software engineering, a delta patch, incremental build log or cached reference is meaningful only relative to an adequate baseline. Hash/epoch verification and a raw fallback may be cheaper than designing an opaque universal code. The theorem excludes the cost of obtaining that context, choosing a matching, version negotiation, feedback, actual audio transmission, cognitive load and authorization. Those costs may reverse any engineering preference.

Instrument speculation: a public parity melody accompanied by private, labelled pedal tones in headphones. Each performer hears the same melody but recovers a different target sequence from their private accompaniment. The conductor changes the network of side information between phrases. In a robust mode the public melody supplies redundancy; in a nominal mode its brevity becomes fragile. An artistic score could deliberately let a missing private tone turn a formerly determinate part into a set of possibilities. This is a proposed compositional interface, not a tested human decoder. A practical realization would need explicit beat alignment and synchronized context snapshots, a disclosed mapping and a way to refuse corrupted context.

Negative results: a known ring erasure can be handled at zero extra payload; stale and erased clique lengths sometimes coincide; the globally single-fault bound is no cheaper than local single-fault bounds under noncollaborative decoding; the bounds are not general for arbitrary directed graphs, noisy broadcasts, unequal messages, feedback, interactive speakers, variable-length codes, private randomization with tolerated errors or block-code rates. If messages are correlated, source restrictions can also remove ambiguity. Do not extrapolate one-bit counts to actual human memory or imply Brier endorses this model.

## 6. Source and execution ledger

Access and reading by one GPT-6.2 assistant, 24 November 2026; self-review and two computational methods, no subagents or human reviewers.

- S1: Bar-Yossef, Birk, Jayram, Kol (2011), *Index coding with side information*, IEEE Transactions on Information Theory 57(3), 1479–1494, DOI 10.1109/TIT.2010.2103753. [Author-affiliated abstract](https://research.ibm.com/publications/index-coding-with-side-information), [institutional metadata](https://cris.technion.ac.il/en/publications/index-coding-with-side-information/). Read abstract only: defines shared broadcast and graph-known context, reports results on minrank and acyclic induced-subgraph lower bound. No full-text reading claimed; proofs here are self-contained.
- S2: Jae-Won Kim and Jong-Seon No (2017 preprint), *Index Coding With Erroneous Side Information*, [arXiv:1703.09361v1](https://arxiv.org/abs/1703.09361), [PDF](https://arxiv.org/pdf/1703.09361). Read abstract, §II.B pp.4–5 on erroneous side information, §IV.B pp.18–20 on clique connection, Theorem 5(2), Proposition 2, and Remark 11 on p.20. Visually inspected PDF indices 18 and 19 (printed 19 and 20). The binary linear optimum for one stale bit and the distance-four parity-check connection are established in this source; our proof extends the lower-bound reasoning to arbitrary deterministic fixed-length fibers. The source allows a fault at each receiver; the local-observation argument in §1 reconciles the global fault constraint. Full paper not exhaustively read.
- S3: Herbert H. Clark (1996), *Using Language*, chapter 8, Grounding, pp.221–252, DOI 10.1017/CBO9780511620539.009. [Cambridge chapter summary](https://www.cambridge.org/core/books/abs/using-language/grounding/6753B41C95C651FE51A8B4B513A245E2). Read public summary only, especially its statements on grounding in relation to joint projects. Interpretive bridge only, not empirical evidence for coding claims. Full chapter not accessed.

Repository checkpoint: main resolved to 495a98ca12bae467a507031f04931aa4254b1866 (merged #198). Read root AGENTS, README, RAG, programme, runbook, research integrity, validation and research README; searched open issues and PRs and paged branch names, finding ongoing context-late privacy, erasure-resistant synchronization, causal counterpoint and other work. No duplicate of the specific announced-versus-unannounced single-context-erasure comparison identified by this title-level reconciliation. Did not claim to read every active PR in full. No nested AGENTS found at research/ or research/expeditions/. New #268 scope and empty comments read; only new directory on issue branch. No changes to frozen protocol, canonical registry, shared manifests or other workers. Local core checks passed; complete repository checkout/validation, Node CLI wrapper and exact final-head CI remain pending at authoring. Structural checks are not scientific acceptance.

## 7. Fictional afterword

The station sent a single note at noon. Every worker knew which of two switches their partner had left alone, so every worker understood the note differently and correctly.

One morning a window was shuttered. Nobody could tell the announcer which worker had lost the view. The engineer proposed a second note, then a third, then a little procession of notes.

A councillor objected: only one window was shut.

The engineer replied that the longer song was not about the window. It was about the announcer not knowing which window it was.

They tried the longer song. It worked, but it was not as beautiful. In the next building, they put the shutters on a separate circuit, and the song became short again.
