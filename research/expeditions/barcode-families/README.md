# The Choir That Keeps Its Barcode but Loses Its Families

**Refs #624 · 25 November 2026 · exploratory mathematical and artistic research.** Not a Track E/G result, a validated auditory interface, a participant experiment, or a claim of scientific priority. One AI research agent wrote and checked this work; no independent human critique.

## An archive of weddings without names

A conservator keeps the dates of every union between families, but erases the identities of those who joined. The archive records the exact number of remaining families at each date. It cannot tell a visitor who belongs with whom.

This is a useful failure mode for an acoustic dictionary audited using an anonymous multiscale clustering summary. A faithful barcode is not a faithful labelled hierarchy. We investigate the cost of recovering the missing relationships, rather than treating the barcode as defective for doing its own job.

## Contract and ancestry

Fix n >= 3 labelled leaves and a trusted strictly increasing list of positive heights h_1,...,h_(n-1). At each height exactly two existing blocks merge; all leaves are present at height zero. A pair receipt reports the height at which its two labelled leaves first share a block. Distances form a binary ultrametric. The ordinary unreduced degree-zero barcode has one infinite interval and one interval [0,h_i) for each merge, regardless of which blocks merge. It does not carry labels. The reduced barcode omits the infinite interval. This is a deliberately restricted equal-birth barcode, not the generic distinct-birth function model in S2.

The dendrogram-ultrametric correspondence is established mathematics (S1, Theorem 9). The non-injectivity of the barcode map is established too (S2, section 2 and abstract; S3, abstract). This expedition supplies self-contained receipt-budget and fault-distance arguments for the restricted equal-birth, distinct-merge model. Related phylogenetic query models already have quasilinear algorithms (S4–S5). Neither the general ambiguity nor adaptive tree reconstruction is claimed as a novel field.

The number of labelled hierarchies in this barcode fibre is

    product_{j=2}^n binom(j,2) = n! (n-1)! / 2^(n-1).

At each stage choose an unordered pair of current blocks; no choice is undone or forgotten because all merge heights are distinct. The distance matrix determines every partition, so distinct histories cannot represent the same matrix. For eight labels the common barcode is compatible with 1,587,600 hierarchies.

This extends the question of labelled resemblance posed by [The Migrating Timbre (#197)](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/197), but differs from that landed work: here the underlying distances really are ultrametric, transitivity holds at every scale, and the loss occurs when labels are removed from the summary. The earlier essay explicitly warned that connected-component identity and direct resemblance are different. Here even the complete *counts* of connected components fail to identify them.

## Exact fixed-dictionary theorem

Write M = binom(n,2). A predetermined dictionary of distinct pair receipts identifies every compatible hierarchy if and only if at most one of the M pairs is absent. Thus the exact fault-free nonadaptive budget is M-1.

**Lower bound, with explicit witnesses for every choice of two absent pairs.**

If the absent pairs share a vertex, rename them AB and AC. On the first three leaves, one history merges AB at h_1 and then ABC at h_2; another merges AC at h_1 and then ABC at h_2. BC has height h_2 in both. Attach all remaining leaves in the same order at the later heights. Exactly AB and AC change.

If the absent pairs are disjoint, rename them AB and CD. Merge AB at h_1 and CD at h_2 in one history; reverse those two merge heights in the other. Merge the two resulting blocks at h_3 and attach any remaining leaves identically. Exactly AB and CD change. This case requires n >= 4, automatically satisfied for disjoint pairs.

Both constructions even preserve the complete unordered pair-distance histogram. Thus knowing that extra histogram cannot improve the worst-case predetermined budget.

**Upper bound.** Suppose two compatible matrices differ only on AB, with values s < t. For every other leaf C the two observed distances AC and BC must coincide: if unequal, the ultrametric inequality forces AB to equal their larger value in both matrices. Their common value must be at least t. It must in fact exceed t, since three mutually equal distances would require a multifurcation or two merges at one height, forbidden by the contract. Consequently AB is a two-leaf cherry in both histories. Its own merge height appears nowhere else among the pair distances. The common observations contain all the other merge heights; the trusted list supplies the unique missing height. Contradiction.

A direct finite decoder enumerates all ranked binary hierarchies, retains those agreeing with the observations, and returns a result only for a singleton fibre. The proof also suggests a faster repair of one absent receipt: if AC and BC differ for any C, take the larger; otherwise check which height is missing from the entire set of retained receipts. If no height is missing and all AC=BC, admissibility must be checked; under the valid binary contract AB must be a cherry in this case, so this situation cannot occur. The proof concerns valid inputs; the decoder must reject inconsistent inputs rather than fill arbitrary gaps.

## Exact whole-receipt fault distance and budget

Permit repetitions. Assign nonnegative integer multiplicity w_e to each pair e, and let w_(1) <= w_(2) be the two smallest multiplicities. The encoded record is the concatenation of the repeated exact pair receipts, and distance is the number of disagreeing complete receipts.

    D = w_(1) + w_(2).

The upper-bound proof above shows that distinct histories differ on at least two coordinates, giving the lower bound. The two explicit witnesses for every choice of absent pair prove equality, including zero multiplicities.

For t substitutions and e flagged erasures, unique correction of every compatible history is possible exactly when D >= 2t+e+1. Sufficiency follows from the triangle inequality after deletion; necessity follows by erasing up to e differing coordinates and distributing the remaining differing coordinates between the two candidate records so each is at most t substitutions away. This is ordinary finite-code distance, not a Gaussian sample-noise guarantee. The list of heights, leaf identities and receipt locations are assumed trustworthy.

For required distance D0, the minimum total number of predetermined receipts is

    B(D0) = D0 + (M-2) ceil(D0/2).

Indeed w_(2) >= ceil(D0/2) and sum w >= w_(1)+w_(2)+(M-2)w_(2). Equality is obtained by choosing w_(1)=floor(D0/2) and all remaining weights equal to ceil(D0/2).

Special cases: no errors or erasures needs M-1 receipts; one flagged erasure needs M; one arbitrary substitution needs 2M-1. For n=8 these are 27, 28 and 55. One complete distance matrix is an erasure-correcting code but not a one-substitution-correcting code. Adding one extra copy of a single strategically chosen pair cannot fix this: there are still two least-protected pairs. Fixed fault distance and adaptive fault correction are different questions.

## Adaptive discovery versus targeted verification

The quadratic fixed budget is not a lower bound for adaptive queries.

Maintain the exact ultrametric on m already inserted leaves. Its induced binary tree still has distinct internal heights, even though some full-tree heights may not yet appear. To insert x, descend the larger child at every branch of the existing tree until reaching a representative leaf r. Query H = d(x,r).

For every existing y with d(r,y) != H, the ultrametric inequality forces d(x,y)=max(H,d(r,y)). The only unresolved leaves have d(r,y)=H. If that set is nonempty it is precisely the opposite child of a node on the heavy path, and therefore contains at most floor(m/2) leaves. Recurse on that induced subtree. A representative for each recursion is chosen from the largest-child descent in the current unresolved subtree, not from arbitrary leaves.

This recovers all distances involving x using at most 1+floor(log2 m) queries. Thus insertion of all n leaves uses at most

    Q(n) = sum_{m=1}^{n-1} (1+floor(log2 m)) = O(n log n).

No trusted barcode is needed for this algorithm, only the strict binary exact-distance assumption. It does not estimate a noisy dendrogram. It is a query-complexity upper bound; this straightforward implementation scans known matrices and is not claimed to have quasilinear total computation. We do not claim the exact optimal adaptive budget. On n=3, for example, knowing the barcode can save the final comparison in some cases.

A third contract is targeted verification of a *specified* candidate tree. For each merge except the final merge, choose one pair crossing its two child blocks, and report its height. These n-2 receipts suffice given the trusted barcode: the edges observed at the first k heights form a forest with n-k components equal to the candidate blocks. Any compatible tree must contain these blocks in its own partition and have exactly n-k blocks, so equality is forced. After the penultimate merge, the final two blocks must merge. This is a sufficient candidate-specific certificate, not a universal fixed query set or a claim of minimality for every candidate. A verifier must not accept a certificate generated from an untrusted proposed tree without checking actual receipts.

For 8 labels: fixed universal 27, adaptive upper bound 17, candidate-specific verification 6. These are different information contracts. The comparison is not a claim that a verifier can find the correct six pairs in advance without knowing the candidate.

## An unusually strong negative control: two identical inventories

Take eight labels A–H and the four two-leaf cherries AB, CD, EF, GH at heights 1, 2, 3, 4 respectively. In hierarchy I, join AB+CD at 5, EF+GH at 6. In hierarchy II, join AB+EF at 5, CD+GH at 6. Both join the two four-leaf blocks at 7.

Both possess:
- exactly the same barcode and even the same anonymous cluster-size multiset at every threshold;
- the same complete unordered pair-distance histogram: heights 1–4 occur once each, heights 5–6 four times each, height 7 sixteen times;
- the same per-label nearest-neighbour distance and nearest-neighbour identity.

Yet sixteen labelled pair distances differ. The two are not merely relabelled distance spaces: each cherry is identifiable from its unique internal distance and the associations among those cherries differ. At the intermediate threshold 5, the question whether A and C share a family receives opposite answers.

If the trusted heights are absent, the single-erasure theorem itself fails: three labels can have distances (AB,AC,BC)=(1,3,3) or (2,3,3), differing in just one pair. If the model is generalized to arbitrary metrics with the same single-linkage barcode, one can change a non-minimum-spanning-tree distance without changing the barcode. Thus the fixed-dictionary theorem is not a general persistent-homology theorem or a claim about arbitrary Euclidean sound banks.

## The Family Organ: equal-energy acoustic realizations

An exact ultrametric can itself be represented by Euclidean waveform distances. Give each edge from parent height p to child height c an orthogonal feature coordinate with squared amplitude (p^2-c^2)/2. A leaf has that amplitude on each coordinate along its root-to-leaf path and zero elsewhere. All leaf energies telescope to h_root^2/2. The squared distance of two leaves telescopes along their two paths below the least common ancestor to h_LCA^2. This gives an exact equal-energy embedding with at most 2n-2 coordinates (not a minimal-dimension claim).

The native witness renders these coordinates as orthogonal sinusoids at 200+40j Hz, with 250 ms per label, 8 kHz mono PCM16, a common coefficient gain of 1000, no normalization between symbols. The two original 2-second banks are labelled by their fixed playback order A,...,H. Each of the 56 within-bank pair distances was recomputed directly from decoded samples. The maximum absolute squared-distance error was 0.001453580000003285, and maximum absolute normalized energy error was 0.0007642399999987504, in coefficient units. Exact abstract energy is 24.5. The digital approximations are not exact integer equality; no loudness, timbre-only, physical propagation or perceptual claim follows.

The generator is [witness.py](witness.py). The waveform hashes and exact target pair matrices are retained in [native-execution.json](native-execution.json). Audio is generated on demand rather than committing binary specimens. This artistic instrument can be imagined as two choirs whose anonymous similarity profiles are invariant while a performer exchanges family memberships. A second performer asks labelled pair questions; a third chooses which questions are missing or corrupted. A live instrument is not implemented.

## Execution, limitations and disposition

Run from this directory with Node.js or Python 3.11+:

    node laboratory.cjs
    python3 witness.py

The JavaScript [laboratory](laboratory.cjs) enumerates merge histories for n=3..6, reconstructs each using literal oracle answers, checks every one-omission projection and finds a collision for every two-omission dictionary. It also checks weighted distances by pair enumeration for 45 deterministic weight profiles across n=3..5. The executed [receipt](execution.json) reports 2,901 histories, 42,417 one-omission projections, 168 two-omission dictionaries, zero assertion failures. Worst observed insertion-query counts for n=3..6 are 3,5,8,11, equal to the stated algorithm bounds.

The native implementation generates matrices independently by enforcing the ultrametric triple rule and requiring all n-1 distinct levels, not by simulating merges. It enumerated 201 matrices for n=3..5 and compared 16,266 unordered matrix pairs, finding every two-coordinate support and no one-coordinate support. Python 3.13.5 executed twice; the receipt and both WAVs were byte-identical in the repeated run. The committed witness source blob was verified against the executed native file. The JSON receipt is a serialization of the native output. The JavaScript code and receipt were committed from the executed function. These are distinct same-agent calculation methods, not independent review.

A practical receiver might use a hierarchy summary for aggregate quality control and reserve labelled pair receipts for disputed semantic relationships. Compare against directly sending the merge log (only n-1 labelled block unions); that can be far cheaper if the source is trusted. The pair-only lower bound does not constrain direct merge reports, arbitrary binary questions, or a richer observable. Treating the barcode as a codeword about its own relationships, or assuming listeners use ultrametric similarity, would be an unjustified transfer. Conventional combinatorics and graph geometry explain these findings without an additional cybersemiotic principle. No Brier endorsement, participant data, clinical claim, or research priority.

Reconciliation: governing AGENTS, RAG, programme, runbook, integrity and validation documents read; 372 branch entries and 100 recent open issue and PR results inspected; searches for ultrametric, dendrogram, barcode, merge tree and related terms did not locate a matching issue. Earlier #197 essay was inspected; prior PR #619 exact-head workflow returned completed/success. New issue #624 had no comments at readback. Base 495a98ca12bae467a507031f04931aa4254b1866. Fresh branch owns only this directory. Native full checkout failed DNS resolution; full repository integrity tests were not run locally. Draft for independent critique and integration, no changes to canonical manifests or stage declarations.

## Source ledger

Accessed 25 November 2026 by the same AI research agent, as exploratory comparators outside the frozen corpus, not systematic literature screening. No restricted source text copied.

- S1 Gunnar Carlsson and Facundo Mémoli, “Characterization, Stability and Convergence of Hierarchical Clustering Methods”, JMLR 11 (2010), 1425–1470, [publisher paper](https://www.jmlr.org/papers/v11/carlsson10a.html), [PDF](https://jmlr.csail.mit.edu/papers/volume11/carlsson10a/carlsson10a.pdf). Read Theorem 9 and §§3.3.1–3.3.3 extracts; checked printed pages 1439–1440 (PDF indices 14–15) visually, including Figure 9. Establishes the correspondence; not a source for the new receipt-budget proofs.
- S2 David Beers and Jacob Leygonie, “The fiber of persistent homology for trees”, Journal of Applied and Computational Topology 9, article 22 (2025), [DOI and open full text](https://doi.org/10.1007/s41468-025-00213-z). Read abstract, section 2 factorization passage and section 6 generic-barcode proposition/corollary excerpts in publisher HTML; not the entire article. Their setting is continuous functions on geometric trees and generic barcodes, unlike the equal-birth finite contract here.
- S3 David Beers and Gillian Grindstaff, “Intrinsic Bottleneck Distance for Merge Trees”, [arXiv:2509.02755](https://arxiv.org/abs/2509.02755), 2025 preprint. Abstract only: explicitly distinguishes ordinary barcode and merge-tree metrics and reports a relationship for intrinsic metrics. No inference from its uninspected proof.
- S4 Ehsan Emamjomeh-Zadeh and David Kempe, “Adaptive Hierarchical Clustering Using Ordinal Queries”, SODA 2018, 415–429, [publisher abstract](https://doi.org/10.1137/1.9781611975031.28). Abstract only; queries are relative closest pairs of triples rather than exact merge heights.
- S5 “Tight Distance Query Reconstruction for Trees and Graphs Without Long Induced Cycles”, [publisher text](https://onlinelibrary.wiley.com/doi/10.1002/rsa.70017), section 4.4.4 excerpt. Consulted the discussion of phylogenetic leaf-distance query complexity; no full reading. This is prior quasilinear reconstruction work, not evidence for optimality of our bound under a fixed trusted barcode.

## Fiction: The second archive

The clerk counted seven marriages and received a flawless audit. The apprentice asked whether two children belonged to the same household. He opened the ledger and found seven dates.

She visited the houses instead.

The dates had not lied; the names had never been entered.
