# The Witness Who Cannot Count a Shared Silence

27 November 2026 — Concept Excavation continuation, #813 / #814. One GPT-6.2 assistant authored the original proofs and synthetic finite oracle. No independent review, human participants, physical tests, or claim of scientific priority. Not frozen Track E/G evidence.

## The anomaly

The earlier [multitype archive](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/455279729ac4dc4d574b13cc8e5129c2c176b00b/research/expeditions/repeated-witness/multitype/README.md) counts candidate originals from survivor words. This continuation asks a different question: even if we are given the actual original word, how many physical occurrences were never witnessed at all? Repetitions make agreement about this count surprisingly difficult. Two perfectly decoded identical symbol words do not necessarily correspond to the same event occurrences. Conversely two very different reports can collectively cover every occurrence.

Contract: a finite source word w of length N; h reports v_i, each assigned a subset of symbol types. A report is any order-preserving subsequence of its type projection (arbitrary local omissions). Report boundaries and type scopes are trusted. No insertions, substitutions, unknown source identity or timing evidence. An embedding is a strictly increasing tuple of source positions yielding the report. Each witness chooses its own embedding; no probability law is assumed. The invisible count U is N minus the size of their union. This includes structurally unobservable types; where every source type has an assigned monitor, U measures events not seen despite being in scope. An invisible event is not necessarily an upstream deletion.

## Source encounter

Xi Chen, Anindya De, Chin Ho Lee, Rocco A. Servedio and Sandip Sinha, [Approximate Trace Reconstruction from a Single Trace](https://arxiv.org/abs/2211.03292), arXiv:2211.03292v1, 7 Nov 2022; later SODA 2023, DOI 10.1137/1.9781611977554.ch27. Read introduction and first part of section 1.1, printed pp.1–2; inspected original PDF images indices 1 and 2. The authors define independent random deletion traces and use longest common subsequence as their approximate reconstruction accuracy measure. Their probabilistic reconstruction problem is not our deterministic embedding-provenance problem; no sample-complexity claim borrowed.

David Sankoff, [Matching sequences under deletion-insertion constraints](https://pubmed.ncbi.nlm.nih.gov/4500555/), PNAS 69(1), 4–6 (1972), DOI 10.1073/pnas.69.1.4: bibliographic record and abstract inspected. This concerns longest common subsequences under positional deletion/insertion constraints. Full article retrieval via PMC encountered a browser challenge; full text not read. Our constraint is instead a lower quota on matched types induced by original composition. Standard alignment and dynamic programming are not claimed as original.

## Fixed source: an interval theorem and an exact polynomial

For a feasible report tuple, the set of possible invisible counts is always a consecutive integer interval, for any number of witnesses and any fixed scopes.

Proof. The embedding graph of a single report is connected under moves that change one retained position while retaining the order and symbol identities. To reach the lexicographically earliest greedy embedding, move the first position to its greedy position, then the second, and so forth. Each new position is no later than the old one, greater than the previously fixed position, and strictly before the next still unchanged position. This works also for an empty report. The product of these connected graphs is connected. One move removes at most one position from the union and adds at most one, so U changes by at most one. A path between embeddings minimizing and maximizing U must visit every intervening integer. If any report is impossible, the support is empty, not an interval of positive length.

To find both endpoints and more, count labeled embedding tuples by U using a polynomial P(z). Scan w left to right, maintaining a prefix length p_i per report. At source position t choose any subset S of reports whose next desired letter equals w_t and whose scope admits it. Advance those prefixes; the empty subset contributes a factor z and the others contribute 1. At the end accept precisely complete prefixes. The coefficient of z^u counts exactly the labeled embedding tuples with invisible count u: each tuple specifies a unique sequence of subsets, and vice versa. Coefficients are not posterior probabilities without a sampling model.

The direct memoized polynomial recurrence costs at most O(N^2 2^h h product_i (|v_i|+1)) arithmetic operations and O(N^2 product_i (|v_i|+1)) coefficient storage, ignoring integer bit lengths and input/key storage. Only extrema can instead be computed with min/max recurrence, omitting the polynomial factor. The implementation is an oracle for short phrases, not realtime qualified.

Example w=ABA, reports A and BA. Independent greedy matches select positions 1 and (2,3) respectively: U=0. But choosing the last A for the first report gives U=1. Both embeddings are legal; the actual histogram is ["1","1","0","0"] (coefficients ordered from zero). Greedy matching determines feasibility, not joint occurrence coverage. With the same source and reports AB, AB, both must select the first A and B; U=1 is forced, although the histogram alone would allow the two A occurrences to be covered.

## Unknown source, known composition: the exact two-witness quota theorem

Now only the source composition c is known. Let a,b be the two report count vectors and u,v their actual words. Reject out-of-scope reports or a_i>c_i or b_i>c_i. In any pair of embeddings, shared positions induce an order-preserving matching of identical letters in u and v (a common subsequence, with specified indices). If m_i matches of type i occur, their union uses a_i+b_i-m_i original positions of that type. Consequently the necessary quotas are

    q_i = max(0, a_i+b_i-c_i).

These quotas are sufficient in the following constructive sense. Given any common-subsequence alignment with m_i >= q_i, merge the two words around the aligned letters, interleaving unmatched runs in any order consistent with each report. Each matched pair is one position; unmatched letters get distinct positions. This merged word has exactly a+b-m as its composition. Append all remaining symbols of c in any order, observing none of them. Both embeddings now exist in one source of composition c. This works for heterogeneous type scopes because omitted eligible events are allowed and out-of-scope events do not enter reports.

Thus feasibility is equivalent to existence of a common subsequence meeting every quota. Let M be the maximum length of any such common subsequence; if no such subsequence exists, report inconsistency. From a maximal alignment remove arbitrary matches of any type with surplus above quota until all quotas become exact. Each removal preserves the alignment order and feasibility and decreases the total number of matches by one. All possible match totals therefore form the interval from sum(q) through M. Inclusion-exclusion gives the exact invisible-count interval:

    U_min = N - |u| - |v| + sum(q)
          = sum_i max(0,c_i-a_i-b_i)
    U_max = N - |u| - |v| + M.

In particular the lower endpoint ignores the surviving order **conditional on feasibility and allowing every source of the stated composition**. The upper endpoint and feasibility depend on order. Unlike the fixed-source theorem this result is only for two reports; it does not require any stochastic independence assumption. Type-specific unavoidable invisibility at the lower endpoint is attained simultaneously.

Algorithm: a quota-constrained LCS recurrence on indices (i,j) and a vector of remaining nonnegative quotas. Skip either next letter, or if they match, advance both indices, lower that type's quota by one (floor zero), and add one to the objective. At exhaustion return zero if all quotas are met, negative infinity otherwise. This gives M with O(|u||v| qdim product_i(q_i+1)) time allowing vector copying, and O(|u||v| product_i(q_i+1)) cached states (qdim = alphabet size; key storage and bit complexity excluded). Classical scalar LCS cannot replace this recurrence.

Sharp example: u=AAAB, v=BAAA; source inventory six As and one B. An ordinary LCS has length 3 (AAA), but B must be shared because only one B exists. No A match can coexist with that B match. Hence M=1, not 3. The true invisible interval is {0}: the source AAABAAA is fully covered. Naive use of ordinary LCS would permit two invisible events that are actually impossible. The quota arises from resource accounting, not from a change to the definition of sequence similarity.

## Three witnesses: pairwise consistency does not compose

Given one A, one B and one C, the reports AB, BC and CA are each complete observations of their assigned pair. Every pair of reports is feasible (e.g. ABC for AB/BC, CAB for AB/CA, BCA for BC/CA), but all three are jointly impossible: A precedes B precedes C precedes A. The oracle exhausts all six source permutations and finds zero joint histories. This remains a useful caution even when pairwise overlap intervals are exact. It is not proof of dishonest testimony or which witness is faulty. A general unknown-source many-witness solution needs joint alignment, not independently chosen pairwise matchings.

## Hidden loss is not its cause

If a common upstream deletion set D is followed by arbitrary local omissions, every element of D must be invisible to all observers. Conversely any subset of the invisible positions of a compatible embedding tuple may be declared upstream-deleted, with all remaining omissions assigned to local paths. Thus with no further causal constraints, even knowing w, the possible upstream deletion counts are exactly 0 through U_max. This counts structural blind spots if they are allowed as upstream deletions too; restrict the source alphabet to types covered by at least one observer for a meaningful all-observer-loss interpretation.

Under a *different* contract that forbids simultaneous local omission of an in-scope event by all its assigned observers, with all types covered, the upstream count equals U. These two contracts cannot be interchanged. For the first, even if U_min>0, the minimum inferred upstream deletion count is still zero. No physical independence, inferred probability or sensor fault attribution follows from this deterministic model. A calibrated stochastic model, independently observed source identity, event-specific tags, or additional fault-domain evidence might change the conclusion.

Design hypothesis: an Observatory receipt inspector should retain both symbolic history support and occurrence coverage bounds. For each proposed source display possible unseen counts separately from possible shared upstream causes; use a scoped joint alignment oracle for small fixtures and return inconsistency instead of choosing a culprit. Conventional combinatorics and alignment explain the derivations; no incremental cybersemiotic mechanism or human validation established.

## Executed qualification

Run `node laboratory.cjs`. Exact BigInt polynomial counts compared with independent enumeration of every eligible retained mask tuple. For every binary source through length six and all pairs of distinct survivor strings with replacement: 41219 fixed two-stream cases. For every ternary source through length four and three partial monitors AB, BC, AC: 10567 cases. Total labeled embedding tuples counted in these tests: 322214. Nontrivial fixed-source support intervals: 18410. Every polynomial coefficient, total tuple count and interval property checked.

Aggregate the independently enumerated binary fixed-source supports by composition; for every individually possible ordered pair of reports at every binary composition through length six compare with the quota-LCS formula, including incompatible pairs: 16600 cases, 4680 inconsistent, 40 feasible cases where unconstrained LCS overestimates the upper endpoint. Additional explicit seven-event quota counterexample and ternary pairwise/joint inconsistency checked. No assertion failures. These tests supplement the proofs, not replace them; they do not establish large-scale performance or physical applicability.

## Continuation checkpoint

Live main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity and validation inspected. Recent 30 PR and issue results, 472 branch entries, issue #813 and #815, comments and predecessor reports reconciled. Target #814 on mhac-813/repeated-witness at 455279729ac4dc4d574b13cc8e5129c2c176b00b, exact workflow 46065300767 success; Humanities #816 on mhac-815/score-teaches-exception at b87e2d9e0628c169d35964fcf32015792097495a, exact workflow 46065481904 success. Previous checkpoints and live refs agree; no observed in-flight changes, although internal execution of another agent cannot be observed directly. Only this fresh additive subdirectory under existing #813 scope is changed; no duplicate issue or PR, no merge, no canonical manifests, no external repository, hardware, publication or participant access. Guarded non-force ref update from pinned parent. Full repository suite pending actual new-head CI, independent critique outstanding.

Concept Excavation advanced #813/#814: next explore joint constrained alignment under hierarchical fault domains, or move to a different conceptual question. Humanities Drift preserved #815/#816: advance next, with the exception-marking or a fresh humanities thread.

*Fiction: Two listeners return with a note named A. The archivist can count the notes on their paper, but the paper has no serial numbers. She leaves a space for the possibility that neither listener heard the same A.*
