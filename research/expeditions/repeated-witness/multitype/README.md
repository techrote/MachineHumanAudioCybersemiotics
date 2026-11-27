# The Archive That Counts Its Missing Notes Without Hearing Their Order

27 November 2026 — Concept Excavation, additive continuation of #813 / #814, pinned predecessor [751be8060338b4caf4847797730b760d7831de02](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/751be8060338b4caf4847797730b760d7831de02/research/expeditions/repeated-witness/README.md). Original derivations and synthetic qualification by one GPT-6.2 assistant. No independent review, participant data, physical validation, or novelty priority asserted. Not part of the frozen Track E/G corpus.

## An unexpected invariance

The previous report counted possible originals when only one symbol type is deleted upstream. Now let any number of types disappear. The receiver knows the entire surviving word v, and the original count vector c. The count vector s of v is known, and k=c-s is the nonnegative vector of missing counts. Write m=sum(s), t=sum(k), N=m+t. All words with composition c are permitted histories; deletions preserve order, and there are no substitutions or extra constraints.

It is natural to suspect a clustered surviving phrase such as AABB would have a different number of possible originals from ABAB. In fact, when the missing inventory is fixed, **the number of distinct compatible histories depends only on the histogram of the surviving word, not on its order.** The identities of those histories do depend on order. Their likelihoods can also depend on order. The proof below separates these three resources.

## Source encounter

Daniella Bar-Lev, Tuvi Etzion and Eitan Yaakobi, [On the Size of Balls and Anticodes of Small Diameter Under the Fixed-Length Levenshtein Metric](https://yaakobi.net.technion.ac.il/files/2024/02/77_Levenshtein_Ball_IT23.pdf), IEEE Transactions on Information Theory 69(4), April 2023, printed p.2325, Section II, Definition 1 and equation (2). Read the extracted relevant passage and visually inspected PDF page index 1 on 27 November 2026. The paper reports the classical Levenshtein formula for the size of an insertion sphere, independent of the central word at a given length and alphabet size, and contrasts it with deletion sphere sizes. It is not a study of human listening. The multivariate refinement below is derived directly, not asserted as new to the literature. Original Levenshtein paper not read in this run. No reproduction of the article committed.

Daniella Bar-Lev, Omer Sabary, Yotam Gershon and Eitan Yaakobi, [The Intersection of Insertion and Deletion Balls](https://www.itsoc.org/archive/itw2021.org/paper/intersection-insertion-and-deletion-balls), ITW 2021, event page abstract inspected. It treats an insertion ball intersecting a deletion ball; this report's multiple deletion witnesses instead give intersections of insertion spheres with fixed composition. Full paper not read. Relevant related work, not evidence of this report's specific claims.

## Exact multivariate count

Let x_a be commuting formal variables for each alphabet symbol a, and X=sum_a x_a. Define H(s,k) as the number of original words containing v as a subsequence and having composition s+k.

Greedily match v from left to right against an original w. Each next match of a symbol a is preceded by a possibly empty unmatched word not containing a. After the final match the unmatched suffix is unrestricted. This decomposition is unique: every gap excludes the symbol about to be greedily matched, so no earlier match could have been chosen. Conversely arbitrary such gaps interleaved with the letters of v give a compatible original, and greedy matching recovers precisely those gaps.

An unrestricted gap has multivariate generating series 1/(1-X), because its words of length j have total monomial weight X^j. A gap excluding a has series 1/(1-X+x_a). Multiplying all gap inventories counts original words once, with the missing inventory encoded by the exponents.

Thus the exact formula is

    H(s,k) = [x^k] (1-X)^(-1) product_a (1-X+x_a)^(-s_a).

All factors are formal power series, not convergence assumptions. Their commutativity proves the claimed order invariance. For any two surviving words of identical composition a constructive bijection reorders their greedy gaps along with their corresponding matched symbols (match repeated symbols by their ranks); the final suffix is unchanged. Its inverse reorders them back.

When only one type a is missing, set all other variables to zero. The coefficient reduces to (1-x_a)^(-(1+m-s_a)), giving binomial(m-s_a+k_a,k_a), precisely the preceding theorem. When no composition constraint is imposed, substitute every x_a=z: the coefficient becomes [z^t](1-qz)^(-1)(1-(q-1)z)^(-m). Equivalently the ordinary insertion sphere has sum_{i=0}^t binomial(m+t,i)(q-1)^i words: under a uniformly drawn length-N word the greedy matcher succeeds after at least m matches, each step before completion has success probability 1/q; continue artificial Bernoulli trials after completion to obtain the binomial tail. This recovers the standard scalar formula, rather than claiming to discover it.

For surviving ABCABC the exact counts for missing inventories (1,1,1), (2,2,2), (3,3,3), (5,5,5) are 172, 10,203, 392,486 and 334,787,664. These are formal combinatorial counts, not probabilities of acoustic loss.

## Support is not a posterior

Define E(w,v) as the number of index embeddings of v in w. It counts deletion masks, not distinct possible originals. Double count pairs (w, embedding): choose the m retained positions among N, place v there, and fill the remaining positions with any permutation of the missing inventory k. Therefore

    sum_w E(w,v) = binomial(N,m) multinomial(k).

Under an explicitly assumed uniform prior over words with composition c, and a uniform deletion mask of exactly t positions independent of the word, the posterior of w given v is E(w,v) divided by that sum. The same posterior results if the mask is selected uniformly conditional on the missing type counts (the number of such masks depends only on c and k). These are illustrative stochastic models, not an assumed physical channel.

Example: original counts (3,3), surviving counts (2,2). Every one of the six possible surviving words has exactly ten compatible originals and total embedding mass 30. But AABB has embedding histogram {1:4,3:4,5:1,9:1}, while ABAB has {1:1,2:4,4:4,5:1}. The most likely original has posterior 9/30 for AABB and 5/30 for ABAB. Thus equal support size does not establish equal posterior concentration, and an embedding count is not a candidate count. No uniform probability assumption is needed for the earlier support theorem.

## Multiple fault domains: the order returns

If two streams v and u come from the same original through independently possible deletion masks, and neither has other errors, the compatible set is the intersection of their composition-restricted insertion spheres. This is not the same as two copies of one damaged stream; nor does the deterministic model assume stochastic independence.

Use a product of greedy prefix matchers. State (r,p_1,...,p_h) holds remaining type counts and the length of each matched prefix. For each type a with r_a>0, append a, decrement r_a, and advance every matcher whose next desired symbol is a. Sum the successor counts. At zero remaining counts accept only if all matchers completed. Each path spells one distinct original; greedy matching accepts exactly the words containing all survivor strings. The algorithm is exact with upper bound O(q h product_a(c_a+1) product_i(|v_i|+1)) time and O(product_a(c_a+1) product_i(|v_i|+1)) cached states (excluding input/key storage). State growth is still exponential in the number of streams or alphabet size. One stream can instead use the coefficient formula.

For original counts (3,3), each length-four balanced witness permits ten histories. The intersections AABB/AABB, AABB/ABAB, AABB/BABA, AABB/BBAA have sizes 10,6,4,0. In the last case the two reports cannot both be deletion-only observations of an original with those counts; no decoder should silently choose a history. Conversely, two reports with the same histograms may provide complementary evidence. The one-stream order invariance does not extend to intersections.

## Executed qualification and negative sediment

Run node laboratory.cjs from this directory. It uses exact BigInt arithmetic for coefficient convolution, embedding counts and the product automaton. Exhaustive distinct-word enumeration compares the three formulations for 10,974 single-stream cases over every ternary original composition through length seven and all feasible surviving words, including empty. Double-counting identity checked on the same 10,974 cases. One-type reduction checked 4,908 times. Two-stream automaton cross-checked with brute enumeration on 20,868 cases (all balanced binary pairs in the displayed example plus all unordered pairs with replacement of single-deletion survivors over every ternary composition through length six). Larger coefficient-only results recorded separately; they were not exhaustively enumerated. All assertions passed in V8. execution.json is the actual deterministic output. This is same-agent verification; full repository test suite and independent critique not performed in this run.

A support count says how many alternatives are possible, not which is true or how a listener distributes belief. The posterior example depends on the stipulated uniform prior and mask selection. Shared upstream loss, exact deletion masks, independent physical paths, substitutions, changing inventories, signal timing, and perceptual event recognition must not be conflated. Duplicating a single damaged stream does not change the deterministic support. If original counts are unbounded there can be infinitely many compatible histories (over a nonempty alphabet); a finite cap permits summing the coefficient over the admissible count vectors. A zero intersection is an inconsistency under the contract, not proof of dishonesty or an identifiable culprit.

Design hypothesis: expose a distinction between compatible-history count, embedding mass, and provenance-aware intersection in a receipt inspector. Preserve the actual survivor order even if the count can be computed from its histogram, because complementary witnesses need order. Conventional word combinatorics, finite automata and Bayesian inference explain the result; no incremental cybersemiotic mechanism or human validation established.

## Continuation checkpoint

Live main base 495a98ca12bae467a507031f04931aa4254b1866. Re-read AGENTS, RAG, programme, runbook, integrity and validation. Inspected 30 recent issues, 30 PR results, 472 branch entries, #813 issue/comments, #814 discussion, exact predecessor report, #492 and #707 scope and targeted searches for shared deletion and subsequence/multiplicity. #814 head 751be8060338b4caf4847797730b760d7831de02 had successful workflow 46044283699; #816 head 73a3f92f7bbe3e671665547eebe60a4bed9727b1 successful workflow 46052567709. Both were open Draft/HOLD. Previous run checkpoint and completed CI and unchanged #814 branch indicate no observed in-flight changes; internal execution of other agents cannot be directly observed. The additive multitype subdirectory extends the existing #813 candidate, without modifying its prior files or opening a duplicate PR. No canonical manifests, external repository, hardware, external publication or merge. Recheck exact new head CI and independent critique before acceptance.

Concept Excavation advanced #813/#814, next consider partial-type projections with unequal per-stream missing inventories, or alternative composition priors. Humanities Drift preserved #815/#816 at the exact head above; rotate to humanities next, exploring institutional exceptions or genuinely different threads.

*Fiction: The archivist discovers that two surviving phrases have the same number of possible pasts. She cannot exchange them in the ledger: when the second witness arrives, their pasts intersect differently.*
