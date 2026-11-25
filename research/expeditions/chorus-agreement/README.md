# The Chorus That Agrees Without Knowing Its Note

MHAC expedition #492 — 2026-11-25. Original finite-model mathematics, synthetic experiments and composition. AI-assisted exploratory work, not Track E/G evidence, production control, empirical validation or a priority claim.

## Scope and predecessor reconciliation

The initial thought was to investigate deletion-resistant reset words. Repository searches for automata and reset deletion located #232 and its draft PR #233; their full report already proves the one-omission construction and two-omission impossibility for the Cerny family. Duplicating that result would add nothing. This expedition instead separates **agreement conditional on a shared corrupted history** from **agreement across independent corrupted histories**, adds a pair-automaton compiler and a sharp all-budget result, and generalizes the fault model to arbitrary symbol insertions and substitutions. The predecessor remains unchanged; no dependency on its unmerged files is necessary. #203 concerns destructive observation rather than open-loop control.

Reconciled main at 495a98ca12bae467a507031f04931aa4254b1866; read AGENTS.md, RAG.md, programme, runbook, integrity, validation and experiments instructions. Inspected 306 branch entries (one repeated across pages), 100 recent open issues and 100 recent open PRs, targeted issue searches, predecessor issue/comments and report. PR #481 prior expedition exact-head run 45549638481 succeeded. The new path is issue-scoped; no canonical manifest, frozen records or another worker's branch is edited.

## Two quantifier orders

Let Q be a nonempty finite state set and each letter a total deterministic map. An issued word w has a set E_d(w) of realizations after up to d specified symbol edits, including zero edits. No feedback, timing effects or probabilities are assumed.

- Shared-history reset: for every v in E_d(w), |Qv|=1. The final state may depend on v.
- Common-target reset: |union over v in E_d(w) of Qv|=1. All initial states and all separate realizations end in the same state.

In the first contract all copies receive the same actual word, not merely the same intended word. Independent errors need the second contract for universal agreement. Even two individually reset copies need not agree. Neither condition reconstructs a prior state or error history.

**Theorem (shared-history existence).** For any finite d and alphabet of complete maps, shared-history reset under at most d arbitrary deletions, insertions and substitutions exists if and only if ordinary synchronization exists. Necessity follows from the no-edit realization. For sufficiency take any ordinary reset word u and issue d+1 contiguous copies. Each edit can spoil at most one original block (insertion at a block boundary spoils neither). At least one block occurs intact in every realization. Once that block maps Q to a singleton, every subsequent total map preserves rank one. Thus the length is at most (d+1)|u|. This argument does not certify the common target; trailing edits may move the singleton.

## Exact pair-automaton search

Let P be all unordered pairs of distinct states. A map acts on each pair; a pair that merges is discarded forever. Define P_j(w) as the set of still-distinct pairs attainable after w with at most j omissions and a shared realization. Then P_j(empty)=P and

    P_j(wa) = a(P_j(w)) union P_(j-1)(w),

where negative-index sets are empty, and the image discards merged pairs. Induction on the last command proves the equality. Shared-history reset iff P_d is empty: if any realization has rank >1, some initial pair survives that realization. Conversely a surviving pair certifies rank >1.

For common-target reset use S_j(w), the union of single-state images, initialized to Q. The same nested update without pair deletion applies. Acceptance is |S_d|=1. Joint search tracks both tuples and can optimize duration at a specified residual terminal-set size. Both are exact BFS because successor states depend only on the tuple; a queue exhaustion is a proof of impossibility in the finite search space, whereas a cap exit is not.

For n states and d omissions the pair tuple universe is at most (d+2)^(n choose 2), since each pair has a first membership level or is absent. This is an exponential algorithm, not a universal efficient compiler. The pair representation is nevertheless much smaller than retaining every possible image subset per realization. Shared edit search could extend the same recurrence with substitution and insertion closure; the implemented pair BFS specifically handles omissions.

For common-target search with mixed unit edits, let f_a(S) denote letter image. For each appended a and j=0..d compute T_j from the preceding tuple S:

    T_j = f_a(S_j)
          union S_(j-1)
          union all f_b(S_(j-1))
          union all f_b(T_(j-1)).

At j=0 only the first term is present. These terms are respectively execution, deletion, substitution (including a harmless duplicate), and insertion after the current prefix. Any edit alignment can be decomposed by its final source symbol and any terminal insertions; the recurrence is exact. Insertions before the first command cannot enlarge the initial Q. This is a symbol edit budget, not a physical-channel timing or burst model.

## Three states: sharp shared-history length for every omission budget

Consider C3 with a:0→1→2→0 and b:2→0, fixing 0 and 1. The predecessor #232 proves common-target impossibility for d>=2, and supplies a nine-letter one-loss common-target word W=baababaab. Here we prove the distinct sharp shared-history length

    L_shared(d) = 4(d+1), for every integer d>=0.

Upper bound: (baab)^(d+1), since baab is an ordinary reset and at least one copy is intact.

Lower bound: ordinary reset words of C3 are exactly those containing two consecutive b occurrences separated by a run of a's of length 2 modulo 3. Before the first b, rotations preserve all initial pairs. After that b every remaining pair is {0,1}. A rotation run moves it around the three pairs; the next b merges it iff its length is 2 modulo 3, otherwise returns the survivor to {0,1}. Without such a gap at least one pair remains distinct.

Call a b-to-b gap bad if it has length 2 mod 3. Partition the bad gaps into maximal consecutive chains, where a chain of r gaps has r+1 bounding b's and at least 2r a's. Pair consecutive bad gaps in each chain. Delete their shared b: the merged a-run length is 1 mod 3, removing two bad gaps at once without modifying their other neighbours. For an odd leftover gap delete one of its a's, which changes its length to 1 mod 3. The chain costs ceil(r/2) deletions and occupies at least 3r+1 symbols. For every r>=1, 4 ceil(r/2)<=3r+1 (equality for r=1). Distinct chains have disjoint bounding symbols, as they are separated by at least one good gap. Summing costs shows every word of length L can be made nonreset with at most floor(L/4) omissions. In particular every L<4(d+1) fails the d-shared contract. QED.

This proof explains why the simple repeat strategy is length-optimal for C3, but not generally for larger Cerny automata. E.g. C4 d=2 has a 23-command shared reset, versus 27 by three ordinary blocks; the exact BFS confirms this. No general larger-n formula is claimed.

### Residual ambiguity as a separate resource

For C3 and d>=2, a shared-reset word can reduce the terminal uncertainty to exactly two states, but never one (predecessor impossibility). A constructive upper bound for simultaneously requiring shared reset and |S_d|<=2 is

    (baab)^(d-1) W b^(d-1), length 5d+4.

If some ordinary block remains intact the rank is one. If all d-1 blocks are spoiled, W has at most one omission, so rank one still follows. There are d consecutive b's at the very end (W includes its final b). Unless all are omitted, final states lie in {0,1}. If all d are omitted, all preceding commands execute; W's nominal state immediately before its final b is 0, so the outcome still lies in {0,1}. At least two outcomes must occur by #232. For d=1, the same construction reduces to W. For d=0 ordinary reset suffices.

The joint native BFS establishes 5d+4 as the optimal length for d=2..10, not a proof of optimality for every d. The shortest shared reset allows all three terminal states in this bounded census; reducing ambiguity to two takes extra commands. A noiseless fixed-length terminal receipt identifying one of two states needs one bit; identifying one of three needs two. This is an elementary information count, not a claim about auditory bit rates or the reliability of the receipt. Without observation, the remaining ambiguity is real.

## Terminal insertion obstruction and the sink-size plateau

**Theorem (common target under insertions).** Assume at least one arbitrary terminal insertion is allowed. A common-target robust reset under any finite positive mixed-edit budget exists iff the automaton is ordinarily synchronizing and possesses a state fixed by every letter.

Necessity: no-edit realizations imply ordinary reset. Let q be the target. Append any single letter to the no-edit word; its image must still be q. Thus q is a common fixed point. Sufficiency: every ordinary reset word necessarily resets to that fixed point, because an initial copy starting there never leaves. Repeat the reset word d+1 times. At least one block survives, and all subsequent commands, inserted or otherwise, fix q. The theorem is specific to unflagged arbitrary tail insertion, not a claim about deletions alone or a channel that authenticates the endpoint.

More generally, assume the DFA is synchronizing and its unique sink strongly connected component has size s. Uniqueness follows since an ordinary reset maps every closed sink SCC to the same state, so two disjoint sink SCCs are impossible. Every state reaches the sink. Define M_d as the minimum, over all issued words, of the union size of terminal states under at most d mixed edits.

    min(d+1,s) <= M_d <= s.
    In particular M_d=s for d>=s-1.

Proof of lower bound: choose one no-edit terminal state q. The allowed terminal insertions include every word of length at most d, so S_d includes the directed reachability ball of radius d about q. This ball grows by at least one state per radius until closed; if it is closed it contains the unique sink, hence has size at least s. The lower bound follows. Upper: extend an ordinary reset word to a target in the sink, then repeat it d+1 times. Once any intact block enters the sink, no subsequent letters can leave it. This upper bound simultaneously attains shared-history reset. No inserted-symbol probability or equilibrium assumption is needed.

The bound can be tight at intermediate budgets too: take an n-state cyclic advance and a constant reset to 0. Repeating the reset d+1 times guarantees at least one intact reset, after which at most d arbitrary inserted/substituted advances occur. The reachable outcomes are exactly the first min(d+1,n) cyclic states. This example has s=n. General intermediate-budget optimum is not asserted.

For a strongly connected synchronizing automaton the high-budget plateau equals the entire state set: every individual realization can be perfectly reset while the aggregate terminal uncertainty is as large as before. Adding a genuine absorbing state or a protected terminal receipt changes the contract; mere repetition does not fix the obstruction.

## Results and independent-method checks

Run Node on laboratory.cjs and compare the printed JSON to execution.json. The core function was actually evaluated in the available V8 tool runtime; the committed source is its serialized function plus a Node output wrapper. Native Python 3.13.5 executes witness.py and generates witness.json and two stereo WAVs. The native receipt reproduced byte-for-byte; committed source and receipt blobs match local hashes (321c371c10fda23ce8915f0a3ffbc7ee368a1a31, c5f00db7168b277029fae61359dd267da028a4e8). WAV hashes are in that receipt; binaries are generated locally rather than committed.

| n | labelled binary total-map pairs | ordinarily synchronizing | common-target robust to one mixed edit | ordinary but not common-target robust |
|---:|---:|---:|---:|---:|
| 2 | 16 | 12 | 6 | 6 |
| 3 | 729 | 549 | 165 | 384 |

These counts enumerate ordered pairs including repeated letters; not isomorphism classes, observed devices or sampling estimates. For all 561 synchronizing cases the constructed repeated-block word with d=n-1 was checked to attain exactly the sink-state set under mixed edits. This qualifies the high-budget result, not every intermediate d.

Other checks: 140,805 direct deletion comparisons (both pair and union outputs), 11,175 direct one-edit union comparisons, 65,535 constructive bad-gap deletion witnesses for all C3 binary words through length 15, and 6,141 native Python direct deletion comparisons through length 10 and budgets 0..2. The native joint search exhausted its reachable graph for d=0..10, including impossible common-target cases. All assertions passed. V8 Cerny census covers n=2..6, with different explicitly recorded budget limits. No incomplete search is counted as an impossibility. No independent external reviewer.

Repository checkout was attempted with git ls-remote; DNS could not resolve github.com in the native container. Connector reads and writes succeeded. Full native repository tests were not run; exact-head repository CI is a separate structural gate, not mathematical qualification. The source code and receipts are synthetic expedition artifacts and do not alter registry state.

## Source ledger, interpretation and negative sediment

- M. V. Volkov, Synchronization of finite automata, Russian Mathematical Surveys 77(5), 819–891 (2022), DOI 10.4213/rm10005, https://www.mathnet.ru/eng/rm10005 . HTML section 1.2 definition, C4 example and ideal property (Lemma 1.1) inspected; no claim of complete reading. The source establishes the ordinary-reset context. The shared-edit, C3 sharp and sink plateau proofs above are our model-specific derivations, not attributed to Volkov.
- A. Kisielewicz, J. Kowalski, M. Szykuła, Computing the shortest reset words of synchronizing automata, Journal of Combinatorial Optimization 29, 88–124 (2015), DOI 10.1007/s10878-013-9682-0, https://link.springer.com/article/10.1007/s10878-013-9682-0 . Abstract, introduction and Theorem 1 proof inspected in HTML; their ordinary-reset search is a methodological comparator, not a proof of the fault results here.
- J. Y. Halpern and Y. Moses, Knowledge and Common Knowledge in a Distributed Environment, JACM 37(3), 549–587 (1990), DOI 10.1145/79147.79161, https://research.ibm.com/publications/knowledge-and-common-knowledge-in-a-distributed-environment ; institutional abstract only, metadata cross-checked at Weizmann institutional record. This motivates distinguishing a group property from knowledge of it. Our quantifier distinction is not their formal common-knowledge theorem, and we do not claim to solve distributed consensus.
- Prior MHAC #232 / #233, full report inspected, is decisive for the Cerny common-target ceiling and one-loss construction. The earlier idea of redoing it was rejected. Targeted external searches did not establish priority for these extensions; no priority claim.

Interpretation: a score can enforce unanimity without establishing the pitch on which the performers agree. The same issued score is not necessarily the same executed score. Acoustic agreement, known final state and common knowledge of the final state are three separate obligations. A common-mode failure model may create coordination even when individual terminal states remain uncertain; independent loss can destroy that coordination.

Proposed experiment: two stateful synths, independently controlled omission masks, and a third optional receipt channel naming the actual terminal state. Compare shared fault patterns with independent ones while holding each marginal fault count fixed. The generator here produces only deterministic examples, not randomized human experiments. Human understanding, causal attribution, and the value of the additional receipt remain untested. No device safety claims.

The two stereo compositions render 13 slots (1.3 seconds) at 8 kHz PCM16, using 220/330/440 Hz for states 0/1/2. The left instrument starts at 0, the right at 2. In the shared score both execute (baab)^3 and end at 0. In the independent score the right instrument misses the penultimate rotation and ends at 1; the left ends at 0. Every permitted shared history of up to two omissions resets, but the recordings demonstrate distinct endpoint agreement when histories differ. Frequencies are arbitrary artistic mappings, not established meanings. No source material copied or license assigned.

**Fiction:** A conductor writes a cadence guaranteed to bring the choir together. The same page reaches two halls, but a single mark is smudged in only one. Both halls finish in unison. The conductor receives two different notes. The guarantee was not wrong; its quantifier was missing from the programme.

Draft checkpoint: analytical proofs, bounded computational qualification, reproducible scores delivered. Independent mathematical critique, exact-head structural CI and native repository-wide testing remain distinct outstanding gates. Refs #492, no closure claim.
