# The Melody That Misremembers Its Missing Note

**MHAC expedition #292 · 2026-11-24 · exploratory mathematics, not Track E or Track G acceptance**

## Question and boundary

Can a loss-tolerant auditory vocabulary use only pitch order rather than absolute pitch? Distinguish two choices: invariance to a strictly increasing transformation shared by every note of a packet, and recovery of a note that disappears. The first is a mathematical equivalence relation; the second is an inverse problem. We investigate how the quotient changes the posterior over source melodies.

A counterintuitive outcome is that a perfectly uniform distribution over original melodies produces a nonuniform posterior over reconstructions. A Bayesian decoder prefers a longer uninterrupted run of consecutive ranks at the deletion site. This preference comes from the multiplicity of ways to lose a note, not a prior preference for tunefulness.

No claim that listeners implement this decoder, that rank perception is exact, or that the code is useful in a safety-critical interface. Rank is a relational descriptor of a packet, not a globally meaningful pitch, and a consecutive rank run need not be a small physical frequency interval.

## Reconciliation and source ledger

The live default branch is main; observed base 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity, validation, foundations and experiment instructions. Inspected 50 recently updated issues and 50 open PR search results, first 100 branch results, and targeted permutation/rank searches. These are bounded observations, not a complete enumeration of all closed history. Nearby independent expeditions concern ordinal interpolation, acoustic quotation, timing, context-late coding, tuning and skill compatibility; no matching active rank-deletion branch was returned. Issue #292 owns only this fresh directory on mhac-292/ordinal-deletion. No live registry, canonical manifest, shared research conclusion or other branch changed. No dependency acceptance inferred from earlier expedition drafts.

Primary sources read by the same ChatGPT agent on this date, with passage-level rather than full-paper coverage:

- Cheyne Homberger, *Counting Fixed-Length Permutation Patterns*, 2012, [publisher-hosted paper](https://combinatorialpress.com/article/ojac/vol7/Homberger_2012.pdf), pp. 2–6, especially Lemma 5, Corollary 8 (pp. 4–5), Proposition 12 (p. 6). Parsed text inspected; page images for pp. 4 and 6 checked. Established antecedents: deletion equivalence classes are consecutive runs; each shorter permutation has a constant number of one-step parents; the no-bond probability tends to exp(-2). The reconstruction count below is explicitly a reconstruction of Corollary 8, not a novelty claim.
- Ryan Gabrys, Eitan Yaakobi, Farzad Farnoud, Jehoshua Bruck, *Codes Correcting Erasures and Deletions for Rank Modulation*, ISIT 2014, [author-hosted paper](https://yaakobi.net.technion.ac.il/files/2015/04/39_Erasures_Deletions_Permutations_ISIT14.pdf), pp. 2759–2761, Definition 1, Lemma 4 and Corollary 5. First two page images and parsed passages checked. Distinguishes stable/unstable deletion and erasure, and relates unstable erasure to stable deletion via inverse permutations.
- Ryan Gabrys, Eitan Yaakobi, Farzad Farnoud, Frederic Sala, Jehoshua Bruck, Lara Dolecek, *Single-Deletion-Correcting Codes over Permutations*, ISIT 2014, [author-hosted paper](https://yaakobi.net.technion.ac.il/files/2015/04/40_Single_Deletion_Permutations_ISIT14.pdf), pp. 2764–2766, Definitions 1–3, Lemmas 2–3 and Theorem 1. First two page images checked, parsed proof continuation read. These authors derive deletion-correcting code bounds and constructions; this expedition does not compete with their code cardinality bounds.
- Bolin Wu et al., *Order-Optimal Systematic Permutation Codes for Correcting t Deletions*, [arXiv:2609.37578](https://arxiv.org/abs/2609.37578), dated 2026-09-29, abstract and introduction consulted as a recent discovery/comparator; no independent verification of its construction or priority. This preprint distinguishes symbol-invariant and permutation-invariant deletion; do not infer peer review.

Sources are external links and original paraphrases; no restricted source bytes reproduced. No full literature search, novelty priority, human validation or independent reviewer is claimed. The newer source falls within the project's date boundary but is not admitted to the frozen corpus by this side expedition.

## Model and exact posterior (proof)

Let P be uniform on permutations of 1,...,n; independently choose one deleted time slot J uniformly from 1,...,n. Let R=P[J] be its rank. The receiver observes Q, obtained by removing slot J and replacing all surviving values by ranks within the survivors. All pitches are distinct, all other events survive, the packet length n and exactly one deletion are known, and the receiver has no independent absolute-pitch or time-slot observations.

For a fixed observed q of length n-1, insertion at slot j with missing rank r means incrementing every surviving value >=r and inserting r at j. Each of the n² pairs (j,r) gives exactly one original event (p,j), and the forward transformation is inverse to this insertion. Thus conditional on q:

- Q is uniform over S_(n-1).
- J and R remain independent uniform random variables. Their joint entropy is 2 log2 n; q provides no information about either coordinate under this prior.
- The posterior of a distinct parent p equals m(p,q)/n², where m counts deletion positions of p yielding q. The posterior over parent events is uniform; the posterior over parent melodies need not be.

Call a bond a pair of adjacent entries differing by exactly one. Maximal consecutive runs partition a permutation, because two consecutive bonds cannot reverse direction without repeating a value. Homberger's Lemma 5 says two deletions yield the same q exactly when their positions are in one run. Here is a short reconstruction: deleting either entry of a bond and standardizing gives the same word. Conversely, suppose deletions at j<k yield the same q and p_j<p_k. Equality at position k-1 forces p_(k-1)=p_k-1, since deleting j subtracts one from p_k, and the alternative p_(k-1)=p_k is impossible. Replace k by k-1 and induct; descending is symmetric. Therefore each parent fiber is a single run, and its multiplicity equals that run length.

The number of distinct parents is n²-2(n-1) = (n-1)²+1, known from Homberger Corollary 8. For another proof, connect insertion events yielding the same parent when their deletion positions are adjacent. Each connected component is a path with m vertices and m-1 edges. For each adjacent slot pair j,j+1 and surviving rank q_j=k there are exactly two edges: create the ascending pair (k,k+1) or the descending pair (k+1,k) in the parent. All other entries are forced. Thus there are 2(n-1) edges and n² vertices in this forest. The component count follows.

**Posterior mode theorem (expedition derivation):** let L(q) be the longest consecutive run of q. The best exact-parent success probability given q is (L(q)+1)/n². Indeed, a parent fiber of size m≥2 shortens to a consecutive run of length m-1 in q, so m≤L(q)+1. Insert a new rank within, or at the appropriate end of, a longest run, extending it by one while preserving the standardization of all remaining ranks. This attains the bound. A parent mode need not have globally maximal smoothness, and multiple modes can tie. This is a likelihood effect localized to the deletion site, not a claim about global melodic aesthetics.

For q=123, p=1234 can produce q from four distinct deletions, p=1324 from two, p=4123 from one. Conditional probabilities are 4/16, 2/16 and 1/16. The best choice succeeds only 1/4 of the time, and guessing a particular deletion event succeeds 1/16 of the time. For q=132 the best parent succeeds 3/16. Both q's have ten candidate parents.

## Asymptotic and information consequences (proof)

For m=n-1, a uniformly random q has no bond with probability tending to exp(-2), established by Homberger Proposition 12 with Corollary 7. A consecutive monotone window of length l≥2 occurs in expectation W_l(m)=2(m-l+1)²(m-l)!/m!: choose its position, its smallest value, direction, and an arbitrary arrangement of the remaining m-l ranks. Hence P(L≥l)≤W_l(m). For l≥3 the ratio W_(l+1)/W_l=(m-l)/(m-l+1)²≤1/4, and W_3=O(1/m), so the sum of all tail probabilities for l≥3 tends to zero. Consequently E[L]→2-exp(-2), and

    optimal mean parent reconstruction probability ~ (3-exp(-2))/n².

Uniform guessing among distinct compatible parents has probability 1/((n-1)²+1) ~ 1/n². Optimal likelihood improves the asymptotic factor to about 2.865, but does not change the quadratic decay. Keeping either missing rank or slot yields probability 1/n, an order-of-growth improvement, not a constant-factor optimization.

An entropy identity follows from the same fibers. Let A_l(n) count maximal runs of length l in the parent and W_l(n) count consecutive windows. W_1=n, W_(n+1)=W_(n+2)=0. Since each maximal run of length r contributes max(r-l+1,0) windows, A_l=W_l-2W_(l+1)+W_(l+2). The conditional entropy of the original parent is

    H(P|Q) = 2 log2 n - (1/n) sum_l l log2(l) E[A_l(n)].

The subtraction is exactly the mean uncertainty about which deletion in a parent run occurred. It is not a coding overhead for a designed codebook. An exact closed-form expression results by substituting the expectation of W_l derived above. The laboratory verifies this against direct posterior summation. For n=8, H(P|Q)=5.5401993695 bits, whereas H(J,R|Q)=6 bits; even these different uncertain objects must not be conflated.

## Metadata and multiple deletions (proof and counterexample)

Single deletion, unrestricted uniform source, known n:

| Observation | Compatible distinct parents | Bayes success |
| --- | ---: | ---: |
| surviving order only | (n-1)²+1 | (L(q)+1)/n² |
| surviving order plus erased slot | n | 1/n |
| surviving order plus erased rank | n | 1/n |
| surviving order plus both | 1 | 1 |

The two middle rows are exact because a fixed slot and varying rank produces n distinct parents; similarly fixed rank and varying slot. They correspond to the stable/unstable distinction in the cited coding literature. For n=2 both middle observations have the same reconstruction performance as order alone.

Generalize to k known deletions, 1≤k<n, with uniform independent k-element deleted slot set I. Let R be the set of erased ranks. Conditional on q, the triple (I,R,bijection I→R) is uniform: every such triple uniquely reconstructs the parent by allocating the remaining rank values in the order dictated by q. Thus q is uniform, and I and R remain independent uniform subsets. With both sets known there are k! equally probable distinct parents. With only one set known there are binomial(n,k)·k! parents. With neither known there are binomial(n,k)²·k! equally likely *events*, not necessarily that many distinct parents.

**Negative result:** simply preserving both sets is insufficient for k>1. For n=4, erased positions {1,2}, erased ranks {3,4}, observed q=12, both 3412 and 4312 are compatible. The assignment is missing. Knowing the deleted position/rank pairing, not just marginal sets, would remove the ambiguity.

These are posterior results under uniform priors, not adversarial optimal code sizes. A constrained codebook, nonuniform note prior, pitch-dependent dropout, partial order errors or independent timing information changes the model. A single monotone transform preserving every rank is essential: time-varying warps may reverse orders and invalidate the observation itself.

## Computational qualification and score

Run from this directory using Node:

    node laboratory.mjs
    node metadata.mjs
    node laboratory.mjs /tmp/mhac-292-wavs

The first script builds every forward deletion event from all permutations for n=2..8, with a direct rank-count standardizer, and independently enumerates insertion events by observed q. Checks compare both event multiplicity maps, run partitions, round trips, candidate counts, one-coordinate cardinalities, posterior modes, run expectation and conditional entropy. All discrete counts exact within safe integers; log/entropy checks use tolerance 1e-9. Executed JavaScript core in a V8 environment; Node CLI/file-writing wrapper not executed here. The second script independently enumerates all deletion sets for n=2..7, k=1..min(3,n-1), testing all observation cells for their expected multiplicity.

| n | Parents per observation | Optimal parent success | One coordinate known | Mean conditional entropy (bits) |
| ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | 0.333333 | 0.333333 | 2.197160 |
| 4 | 10 | 0.208333 | 0.250000 | 3.176880 |
| 5 | 17 | 0.130000 | 0.200000 | 3.950812 |
| 6 | 26 | 0.088426 | 0.166667 | 4.575924 |
| 7 | 37 | 0.063946 | 0.142857 | 5.096118 |
| 8 | 50 | 0.048438 | 0.125000 | 5.540199 |

Single deletion: 46,232 original permutations; 5,913 observations; 362,878 forward and 362,878 inverse events; 282,240 distinct compatible parent-observation fibers. Multi-deletion: 350,416 events across 15 configurations (includes some single-deletion controls, so not a disjoint total). All assertions passed. See [single deletion receipt](execution.json), [metadata receipt](metadata-execution.json) and corresponding scripts. Enumeration and proofs are synthetic and were self-reviewed by one agent, not independently replicated by a human.

An original tiny PCM demonstration uses rank-dependent triangular tones, 8 kHz mono, 800 samples per note with edge ramps. From 1234 and 4123 delete the first note. The raw survivors 234 and 123 produce different WAV bytes; their canonical rank score 123 produces identical WAV bytes. Four arrays generated in memory, 4,844 bytes each; direct equality tests supplemented by FNV-1a fingerprints. This verifies a deterministic rendering collision introduced by rank canonicalization, not auditory equivalence of the original physical recordings. No audio classification or listener test.

**Speculative instrument: the Missing-Note Conservatory.** A performer enters a permutation of pitch ranks; a stochastic eraser removes notes; a second performer receives the rank-standardized melody, plus independently switchable time-slot and rank-set metadata. An accompanying instrument renders possible completions proportionally to their likelihood rather than substituting the highest-scoring one. The listener can request the missing coordinate or the full packet. This separates compositional uncertainty from the tendency to favor a plausible-looking reconstruction. A calibrated pitch bank and timing track would serve as independent reference channels, not decoration.

## Interpretation, implications and falsifiers

A sign invariant under a class of transformations preserves a selected relationship at the cost of refusing to distinguish members of the same equivalence class. Invariance is neither universal meaning nor noise immunity. A transformation that is desirable for timbral/pitch flexibility may erase metadata that would have repaired an omission. This echoes a central cybersemiotic question about which distinctions are available to an interpreter, without treating the mathematical rank model as Brier's theory or claiming a philosophical reduction.

For machine auditory messages, a packet receipt might separately report source pitch identifiers, event-slot identity, surviving ordinal pattern, transformation assumptions, deletion-count evidence, codebook version, and whether decoding returned a unique value, an explicit candidate set, or a refusal. An engineer must decide which identities matter; a repeated or plausible completion is not verified reception. For multiple deletions an ordered correspondence matters even when both sets are known. Do not turn a maximum posterior reconstruction into a statement of certainty.

Candidate hypothesis: retaining a separate temporal-slot channel improves exact message recovery when absolute pitch identification fails. The ideal model predicts an advantage; human performance may not, because synchronizing a slot, recognizing relative pitch, and maintaining attention consume resources. A test would compare rank-only, rank+slot, absolute-rank and full-packet-repeat interfaces at matched duration/training where possible. Define primary correct decoding and action including omissions, measure actual pitch discrimination and timing cue recognition, and reject the design if the metadata consumes more resources than it saves or induces confident erroneous action. No participant study, recruitment, or deployment authorized.

Contrary cases: an intact packet can be identified exactly within the rank-only model, even under arbitrary shared increasing transforms; a well-designed restricted deletion code can correct without explicit metadata (see coding literature); known absolute labels may be impractical or genuinely unavailable; when priors or fault mechanisms are known and nonuniform, a different MAP rule is appropriate. No claim of general smoothness preference in humans or all machine learning.

## Fiction (original, not evidence)

The conservatory's archivist received only the order of surviving notes. A lost scale came back as a longer scale, not because the archive loved scales but because a scale could have lost any of its steps and remained the same staircase. He recorded the reconstruction in pencil. When his successor inked it over, the archive acquired a taste it had never possessed.

## Checkpoint

Scope #292 exploratory sidecar. Source base as above. Artifacts: this report, two runnable JS laboratories, two execution receipts. Local core execution and self-critique complete. Remaining: independent mathematical critique, actual Node wrapper execution and full repository integrity CI on final head. Draft remains partial with Refs #292; no scientific or human-gate completion. No human action necessary for the synthetic experiment; any real listening study remains separately authorized.