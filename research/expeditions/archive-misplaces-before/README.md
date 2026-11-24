# The Archive That Misplaces Its Before

**MHAC expedition #348 | 2026-11-24 | additive, synthetic, noncanonical.**
Base observed: `495a98ca12bae467a507031f04931aa4254b1866`.
AI-assisted original derivations, source reading, and computational self-check by one GPT-6.2 agent; no independent human review or listening experiment.

## Abstract

A perfect archive of every overlapping local phrase can preserve all local event relationships while destroying the global order of the very same events. This is not just a failure of bigram statistics or an uncertainty about time reversal. In a finite model with distinct named events, the archive determines a collection of rigid clusters but can lose their permutation and the distribution of silent time between them. We derive the exact size of this equivalence class, including truncated boundary cases; a sharp horizon for total order invisibility; a sharp tradeoff between the number of hidden orders and the number of hidden complete histories; and precise comparison-query repair certificates. Two finite enumerators and an original PCM witness qualify the claims within their assumptions. No claim of mathematical priority.

## The puzzle and model

A clerk records all length-three windows of these two eleven-tick messages:

    00A00B00C00
    00C00B00A00

The count of each window is identical: exactly one of each of 00A, 0A0, A00, 00B, 0B0, B00, 00C, 0C0, C00. The first and last two symbols are also identical. Both histories contain all three named events exactly once. Their orders are opposite. All six permutations are possible.

Let w be a finite word of length n over 0 and m distinct nonzero named markers (each appearing once), with 1 <= k <= n and m >= 1. Zero is an ordinary specified idle token, not an unknown, a censored observation, or a claim that the physical machine did nothing. Observation H consists of the multiset of **all overlapping, oriented** k-factors, plus exact prefix and suffix of length k-1. The equivalent observation is the multiset of every factor of each length 1 through k: shorter counts follow by taking the suffixes of longer factors and adding the missing prefix. Conversely the difference between the shorter histogram and the suffix projection identifies that prefix (and similarly the suffix). At k=1 the boundary words are empty.

This is the established k-Abelian equivalence relation, not a new definition of it. The complete ordered list of windows would reconstruct the word; its multiset is the deliberately lossy part. No observations are randomly missing. Only the association of windows with absolute time is erased.

## Theorem A — exact rigid cluster decomposition, including boundaries

Construct an undirected graph on marker identities. Join two markers when they co-occur in any observed k-factor. Attach the signed offset from one to the other, read from the positions inside that factor. The actual word exists by assumption. Each marker is unique, so every reported offset is consistent.

**Necessity.** Two markers at positions i,j co-occur in at least one k-factor iff |i-j| < k: a window containing both fits inside the word because k <= n. Thus components are exactly maximal runs of successive markers separated by fewer than k ticks. Choose an arbitrary origin in each component and sum offsets along paths. The resulting coordinate of each marker is independent of path because the input has a realizing word. Translate the minimum coordinate to zero. This recovers an oriented, rigid substring C_i from first to last marker, including internal zeros. Let its span be L_i. The c components are distinguishable because their marker identities are disjoint.

If any marker occurs in the recorded prefix, its component is the leftmost cluster, and the exact leading zero count p is known by subtracting its recovered offset from its prefix position. A marker in the suffix similarly anchors the rightmost cluster and trailing zero count q. Let a,b be 0/1 indicating those anchors. Let r be c minus the number of **distinct** anchored clusters. If the same cluster is anchored twice, c=1 and r=0. Anchors can be extracted from the observation alone, not from the unknown original timeline.

Every internal gap has at least k-1 zeros. Any unanchored exterior gap also has at least k-1 zeros; otherwise a marker would appear in the corresponding boundary. Anchored exterior gaps have their measured exact lengths. There are g=c+1-a-b free gaps. Define

    s = n - sum_i L_i - (k-1)g - a*p - b*q

where absent p,q terms mean zero. This is the nonnegative surplus idle time. If g=0, realizability forces s=0.

**Sufficiency.** Arrange the unanchored components in any order, respecting the anchored ends. Give each free gap k-1 zeros plus a nonnegative share of s; fixed gaps keep their exact values. No k-factor can meet two clusters. For each cluster, the multiset of windows meeting it is determined by its rigid shape and the available boundary padding (full padding except for an anchored end, where its exact length is fixed). Shifting it or adding zeros between clusters cannot change these windows. The all-zero window count is the fixed total n-k+1 minus the total number of windows meeting clusters. The endpoints are unchanged. Thus every arrangement just described has exactly H, and the necessity argument excludes every other arrangement.

**Exact count.** Since the free clusters have distinct marker sets, different orders and gap compositions yield different words. Stars and bars yields

    |[w]_k| = r! * binom(s+g-1,g-1)   (g >= 1)
    |[w]_k| = r!                     (g = 0, s = 0)

There are precisely r! distinct named-event orders; all share the same number of admissible timing placements. The no-anchor case is especially simple:

    |[w]_k| = c! * binom(s+c,c)
    s = n - sum_i L_i - (c+1)(k-1).

Full reconstruction holds iff this count equals one. Chronology alone is identified iff r <= 1. A connected marker graph does not in general identify absolute timing: the single rigid cluster can slide between unanchored ends.

This is a restricted explicit factorization of the general k-Abelian class-count problem, not an alternative claim to the general directed-matrix-tree/BEST formula in Karhumäki et al. (2017).

## Theorem B — sharp horizon for completely hidden order

For m >= 2 unique named events, all m! orders can coexist in one k-Abelian class iff

    n >= (m+1)k - 1.

Necessity: a marker in a boundary word has fixed ordinal rank among the named markers, preventing all permutations. Any co-occurring pair has fixed relative order, also preventing all permutations. Hence all clusters must be singletons with both ends unanchored. The minimal word contains m markers and (m+1)(k-1) zeros. Sufficiency: place k-1 zeros at both ends and between each marker, distribute any extra zeros among the gaps, and permute markers arbitrarily. At threshold there are exactly m! realizations. At larger n the class contains m! * binom(n-(m+1)k+1+m,m) words.

This is a sharp statement about **named-event order**, not the older general shortest collision at length 2k. That latter result already appears in Karhumäki, Saarela and Zamboni (2013), Lemma 2.4 and its following paragraph. It can also be seen from the shared endpoints covering all but at most one position when n<=2k-1; the remaining symbol is then fixed by unigram counts. At 2k a singleton marker can move one position within zeros. Losing its exact time is easier than losing the order of distinct events.

## Theorem C — more order ambiguity need not mean more total ambiguity

Fix m,n,k >= 2 in the fully padded population and require exactly c clusters. For feasible c in 1..m let

    S_c = n-m-(c+1)(k-1)
    F_c = (S_c+c)! / S_c!

where feasibility is S_c >= 0. Each cluster span is at least its number of markers, so total span is at least m. Theorem A is increasing in s for fixed c, hence F_c is an upper bound. Attain it by distributing the m markers into c nonempty contiguous clusters, using no internal zeros, then separating/padding them by k-1 zeros. (k>=2 ensures adjacent markers belong to the same cluster.) The global maximum is max over feasible c. For k=1 the only possible c is m.

At m=3, k=4, n=15:

| Cluster count | Maximum compatible words | Distinct event orders |
|---:|---:|---:|
| 1 | 7 | 1 |
| 2 | 20 | 2 |
| 3 | 6 | 6 |

A one-cluster word can slide through six excess zero ticks. Three separate events consume all available padding, leaving only permutation ambiguity. Two clusters permit both ambiguity types simultaneously and maximize the class. At n=12 only c=1,2 are feasible; the corresponding maxima are 4 and 2. In the independent bounded census, the largest feasible c failed to maximize total ambiguity in 12 of 136 profiles.

Interpretation: temporal segmentation can exchange location uncertainty for order uncertainty. One scalar ambiguity measure cannot tell an archivist which question remains answerable.

## Theorem D — the price of asking for 'before'

After Theorem A, let r unanchored clusters remain. A truthful pair comparison asks which of two named clusters precedes the other. An arbitrary marker from each suffices because clusters do not interleave.

* **Certificate for one realized order:** exactly r-1 comparisons are necessary and sufficient when r>=1. Every adjacent pair in that order must be compared: otherwise swapping those adjacent items changes no observed pair result and remains consistent with H. Comparing all adjacent pairs supplies the transitive chain.
* **Nonadaptive worst-case identification:** all binom(r,2) comparisons are necessary and sufficient. Any omitted pair can occur adjacent in some permitted permutation, giving the preceding counterexample. A set of comparisons fixed before seeing results cannot exploit the unknown order.
* **Adaptive identification:** any binary decision tree has worst depth >= ceil(log2(r!)); inserting items into a sorted list by binary search has worst depth <= sum_{j=2}^r ceil(log2 j). These are bounds, not a claim that insertion is always optimal. Exhaustive insertion tests cover r=2..8.
* **Unrestricted fixed-length receipt:** the exact minimum bit length to identify the order is ceil(log2(r!)); for a full timed word it is ceil(log2(|[w]_k|)). Encode the rank in a canonical enumeration to attain the bound. These are ideal combinatorial bit counts; physical framing, sender knowledge, trust and transmission errors cost extra.
* **Forced reconstruction without further observations:** if all r! orders are equally possible, any chosen deterministic order has expected Kendall inversion loss binom(r,2)/2. More strongly, this is the minimax expected loss for randomized reconstructions against an unknown true order: averaging over uniform truth gives the lower bound, and uniform random output gives that loss against every truth. A deterministic reconstruction has worst loss binom(r,2) against its reversal. None of these statements supplies a natural prior for real machines.

A chronology certificate is not necessarily a causal certificate. This formal order is sequence position, with no causal law inferred from it.

## Computational receipts and reproducibility

From this expedition directory, with Node.js:

    node laboratory.cjs /tmp/archive-before
    node frontier.cjs

The first command writes an execution JSON and four WAV files; the second prints the separate frontier receipt. Compare the JSON to the committed receipts. The computational cores were run in the available V8 JavaScript execution environment (not a native Node subprocess); the first was fetched from commit 5322df0a9be2f92702f767f59fb70d9370e40a46 and re-executed with byte-identical JSON. The Node filesystem wrapper is provided but has not been exercised here. No external dependencies, random seeds, time-based output or empirical data.

| Check | Actual count |
|---|---:|
| Word/length/horizon instances (m=1..4, n<=11, k<=5) | 112,310 |
| Histogram/boundary equivalence classes | 63,867 |
| Padded instances / classes | 32,290 / 1,531 |
| Boundary-anchored classes | 62,336 |
| Classes permitting all orders, m>=2 | 48 |
| Largest class in main census | 7,920 |
| Explicit threshold witnesses, m=2..6, k=1..7 | 6,104 |
| Nonadaptive query sets (r=2..5) | 1,098 |
| Individual order/query-set checks | 124,468 |
| Unique order certificates in that census | 7,886 |
| Insertion-sort orders tested (r=2..8) | 46,232 |
| Independent padded frontier words (m<=4,n<=15,k=2..5) | 86,854 |
| Frontier groups / profiles | 7,010 / 136 |
| Final assertion failures | 0 |

The first enumeration generates words by selecting positions and permuting labels, then groups their actual histograms. It independently recovers cluster shapes and anchors solely from window co-occurrence offsets and endpoint words; compares that descriptor with a direct scan of the original; and checks group and order cardinality. The second implementation sorts literal windows and measures maxima by actual cluster count, rather than using the first descriptor function. They are separate algorithms by the same agent, not independent peer review. The comparison census groups orders by their actual answer transcripts, not just by the theorem's adjacency condition.

## The Window Archive Organ — executable synthetic composition

Use silence for zero and three distinguishable square-wave pitches (A=200, B=300, C=400 Hz), with 320 samples per slot at 8 kHz, 16-bit mono PCM. The archive renderer sorts each observed length-three fragment lexicographically and concatenates it, preserving multiplicity. This is an intentionally order-erasing score, not a claim that listeners naturally hear bag-of-windows statistics.

| WAV | Bytes | FNV-1a32 (diagnostic, not cryptographic) |
|---|---:|---|
| chronology_a | 7,084 | 485924d1 |
| chronology_b | 7,084 | 491dccd1 |
| archive_a | 17,324 | 07bf9411 |
| archive_b | 17,324 | 07bf9411 |

The chronological WAVs are distinct. The archive WAVs were compared directly and are byte-identical. The filenames are generated locally by the script; no binary files are required in this PR.

Speculative instrument: the composer chooses a local phrase inventory, then plays with cluster order, inter-cluster idle-time allocations and the window horizon. One performer hears the reconstructed archive, a second hears one realization, a third can request a specific pair's precedence. At higher horizons, clusters fuse; at lower horizons, previously fixed chronology becomes playable. Rather than choosing a single canonical reconstruction, an interface could permit the listener to audition several admissible scores or display the residual order/timing ambiguity. No listener discrimination, preference, workload, or training claim follows from exact sample identity.

## Source ledger and cross-domain bridge

Read 2026-11-24 via public web by the same AI agent. Metadata and selected passages verified, not whole-work critical reviews. These are expedition context, not canonical Track E/G admission or a change to the protocol cutoff.

* Juhani Karhumäki, Aleksi Saarela and Luca Q. Zamboni, *On a generalization of Abelian equivalence and complexity of infinite words*, arXiv:1301.5104v1 (2013), [preprint](https://arxiv.org/pdf/1301.5104). Read Definition 2.1, Lemma 2.3, Lemma 2.4 and its sharpness paragraph (PDF indices 3–5, visually inspected indices 4 and 5), and Lemma 2.12 (PDF index 8, text). This establishes the equivalence and earliest general collisions; the distinct-event specialization and repair arguments here are separate derivations.
* Juhani Karhumäki, Svetlana Puzynina, Michaël Rao and Markus A. Whiteland, *On cardinalities of k-abelian equivalence classes*, Theoretical Computer Science 658 (2017), 190–204, DOI 10.1016/j.tcs.2016.06.010; [author preprint](https://arxiv.org/abs/1605.03319). Read abstract, introduction and §§2, 4.1–4.3 as rendered text, notably Corollary 4.3 and Proposition 4.7 proof. This gives a general class-count method via directed multigraph Euler trails. The specialized cluster formula does not claim priority or supersede that result. Full paper not audited.
* Pavel A. Pevzner, Haixu Tang and Michael S. Waterman, *An Eulerian path approach to DNA fragment assembly*, PNAS 98(17), 9748–9753 (2001), [publisher](https://www.pnas.org/doi/10.1073/pnas.171285098), DOI 10.1073/pnas.171285098. Read abstract/introduction and Eulerian Superpaths text (latter also accessed through a public article mirror; printed pp. 9750–9751). The authors retain information about which short fragments share a longer sequencing read to resolve repeat-induced assembly ambiguity. This is a mechanistic analogy to retaining a targeted chronology receipt, not a statement that their sequencing problem reduces to unique event labels. No numerical sequencing performance claims are transferred.

The graph of k-1 contexts with k-factors as directed edges is the familiar de Bruijn multigraph. A word realizes an Euler trail. Here the repeated idle context allows excursions representing separate clusters to be permuted, and unused all-zero loops can be redistributed. Genome assembly's longer-read constraints suggest a design pattern: preserve *relationships among observations*, not simply more instances of observations already represented.

A linguistic analogy is a dossier containing every local collocation but no document chronology. A perfect record of local phrasing cannot justify which separated statement came first. This analogy says nothing about the full semantics of natural language, for which unique names, exact discrete time, fixed tokenization and a single idle symbol are exceptionally restrictive.

## Negative sediment and scope limits

* Repeated marker identities defeat the signed-offset reconstruction: `0010100` and `0100010` are 2-Abelian equivalent, but a label 1 is not a unique event. This is a negative control, not an application of Theorem A.
* Omitting boundaries AND shorter counts changes the observation: `010` and `101` have the same bigram histogram but different unigram counts. A raw k-spectrum alone need not be k-Abelian equivalence.
* More event clusters can reduce the number of admissible histories at fixed duration (Theorem C); do not optimize a single ambiguity score blindly.
* Order comparisons do not resolve silent gap allocation. Knowing every marker is present does not verify its timestamp or action lifecycle.
* The model is finite, linear, exact and symbolically noiseless. Circular words, approximate histogram matching, unknown marker identity, unknown boundaries, unequal tick lengths and multiple simultaneous events require other models. No extension to arbitrary real audio is proved.
* A sorted fragment score actively discards chronology; an uninterrupted recording or time-stamped ordered windows do not suffer this particular loss. Human perception is not the stipulated histogram operator.
* No source claims that chronology implies causality; the independent earlier #183/#260 problems concern causal DAGs and clock offsets. #340 concerns stationary reversal, #302 constrained novelty; this expedition does not modify them.

## Candidate engineering exaptation (unvalidated)

An archival or machine-communication receipt should distinguish local factor counts, event identity, observed ordering relations, timing anchors, and unallocated gap duration. Where a decision requires a specific before/after relationship, ask whether that relation is invariant across the observation's equivalence class; if not, request the least costly additional witness allowed by the application. A chronological chain of adjacent clusters can certify a realized order, but selecting that chain without knowing the order is a distinct acquisition problem.

No implementation authority, real safety claim or participant validation follows. A falsification experiment could compare explicit timestamp receipts against local-texture summaries on synthetic diagnosis questions, then separately study comprehension under an authorized human protocol. The exact mathematics can specify the ground truth for that later study, not its outcome.

## Fiction — The clerk's archive

The archive of the town clock contained every three seconds of its history. It was the most meticulous archive in the district. Each fragment had been counted, indexed, and copied without error.

When the water rose, the clerk produced a complete record of the opening of a gate, the sounding of a bell and the closing of a valve. The magistrate asked which had happened first.

The clerk brought the indexes again, this time in alphabetical order.

The apprentice examined the silence between the entries and asked how long the silence had been. The clerk could account for every second, but not for which silence owned it.

The archive was not missing a single sound. It was missing a place to put the word *before*.

## Repository reconciliation and remaining gates

Read live root instructions, RAG, programme, runbook, integrity, validation and project foundations; inspected the 212 open issue/PR records (100+100+12), 97 open PRs, and 233 branches (100+100+33) at the pre-write snapshot, with main at the above SHA. Read issues #183, #260, #340 and searched issue text for de Bruijn overlap (only #302 returned). The #348 issue was created afresh; its comment list was empty on readback. Prior #341 exact-head Actions run 45407549020 was successful; this does not qualify #348. No active branch or canonical manifest modified. The accepted programme still has open corpus and analysis gates; this expedition is not a substitute for them.

Only this directory is owned by the expedition. Independent critique, native Node filesystem CLI run, full repository CI and integrator landing remain separate acceptance steps. The branch stays a draft with Refs #348 until those are evaluated. No human action is needed for the computational core. No authorization for human testing or production control implied.
