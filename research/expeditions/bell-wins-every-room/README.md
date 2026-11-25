# The Bell That Wins in Every Room and Loses the Building

**Issue #554 · 25 November 2026 · exploratory mathematics and original synthetic score.** One ChatGPT research agent; no external or independent review, no participant data, no canonical evidence promotion or scientific priority claim.

## The anomaly

Two auditory warning policies are evaluated in two contexts. In this invented fixture:

| Context | A correct / trials | B correct / trials | A minus B |
|---|---:|---:|---:|
| Easy | 9/10 | 24/30 | +10 percentage points |
| Hard | 6/30 | 1/10 | +10 percentage points |
| Pooled | 15/40 | 25/40 | -25 percentage points |

A is better in every context and worse in the pooled report. With a common 50:50 context distribution, A has 55% and B 45%. Neither statistic is dishonest; the denominators answer different questions. Simpson reversal is established mathematics, not a discovery here. The expedition asks how much reversal can be hidden by context mixture, and how many audible context tags are sufficient to preserve the entire arithmetic audit.

This connects #545's policy-conditioned alert precision to a different problem: different evaluation populations for different interfaces. It also supplies a mathematical appendix to #36's warning against misleading averages over contradictory tasks, without taking over that work. Not a claim about actual continuous sonification.

## Sharp reversal bounds

Assume finitely many contexts, strictly positive probability vectors p and q for policies A and B, success probabilities a_i and b_i, and a known uniform local margin d in [0,1]: a_i >= b_i+d. Define A=sum p_i a_i, B=sum q_i b_i, and TV(p,q)=sum |p_i-q_i|/2.

**Theorem 1.** The sharp lower bound on A-B is d-(1-d)TV(p,q). A strict reversal is possible if and only if TV > d/(1-d) for d<1; at equality a tie is possible but not strict reversal. In particular d>=1/2 precludes strict reversal.

Proof: A-B >= d+sum (p_i-q_i)b_i; each b_i is in [0,1-d]. Choose b_i=1-d on q_i>p_i and zero on the others; put a_i=b_i+d. This attains the stated lower bound. With heterogeneous known margins d_i the same proof gives the sharp bound sum p_i d_i - sum max(q_i-p_i,0)(1-d_i). The upper endpoint is not asserted to be symmetric under an at-least-margin constraint. If the local margins are required to be exactly d, the upper endpoint is d+(1-d)TV.

A common context distribution eliminates the arithmetic reversal; it does not establish which distribution should be used for a causal or operational decision.

**Theorem 2 (baseline-conditioned frontier).** For d<1, if the observed pooled baseline B=beta is known, set s=beta/(1-d), necessarily in [0,1]. Let R_i=p_i/q_i and define L(s) as the minimum of sum p_i z_i over 0<=z_i<=1 with sum q_i z_i=s. The exact minimum possible A is d+(1-d)L(s). Its maximum is 1, attainable at a_i=1 and b_i=beta. Every intervening A is achievable by mixing feasible vectors while keeping B fixed.

To calculate L, order the contexts by increasing R_i. Fill the required q-mass s starting at the lowest ratio, allowing a fractional last context. The exchange argument is elementary: move q-mass from a used higher-ratio context to an incompletely filled lower-ratio one; the objective cannot increase. L is a continuous piecewise-linear convex curve connecting (0,0) and (1,1). Put b=(1-d)z and a=b+d for the attaining witness. Strict reversal at the specified B is possible precisely when d+(1-d)L(s)<beta. The worst over all beta recovers Theorem 1 because max(s-L(s))=TV.

This is the lower concentration curve for the two context laws, the reflected counterpart of the optimal likelihood-ratio ROC. The standard curve and likelihood-ratio ordering are not new. The audio-policy interpretation and explicit tag-budget question are the scope of this expedition.

## Lossless and lossy context tags

A deterministic tag partitions context indices into nonempty groups. Write p_G and q_G for their sums and Rbar_G=p_G/q_G. Under q this is the conditional expectation of R given the tag. Let L_C be the lower concentration curve of the grouped probabilities. It is the exact frontier when the hypothetical baseline z is restricted to being constant within each group, and thus L_C>=L. This restriction is a mathematical comparison of audit resolution, not an assertion that pooled success rates preserve a fine-context local margin.

**Theorem 3 (lossless tags).** The entire baseline-conditioned frontier is preserved if and only if every group consists of contexts with identical likelihood ratio. The minimum tag alphabet is therefore the number of distinct ratios p_i/q_i (for positive weights).

Proof: define H(t)=sum q_i max(t-R_i,0). Then
    L(s)=sup_t {t*s-H(t)},   H(t)=sup_{0<=s<=1} {t*s-L(s)}.
For the first formula, the expression is a lower bound from subtracting a multiplier times the mass constraint, and a threshold equal to the marginal filled ratio attains equality. The reverse identity follows by filling exactly all ratios below t. The analogous expressions apply to grouped H_C and L_C. Jensen gives H>=H_C. If any group contains unequal ratios, a threshold strictly between its minimum and maximum produces a strict Jensen gap in that group; other groups cannot cancel it. Consequently its H and hence its L are different. Conversely equal ratios preserve H identically.

**Theorem 4 (exact worst error).** Let E=max over s in [0,1] of L_C(s)-L(s). Then
    E = max_t [H(t)-H_C(t)].
Both directions follow by comparing the two suprema in each conjugacy relation: a uniform epsilon bound in either domain gives the same epsilon bound in the other. The maxima can be evaluated at the finite breakpoints (cumulative q-masses for L; original and grouped ratios for H); outside the common ratio range the hinge gap vanishes. The maximum upward distortion of the minimum-A frontier is exactly (1-d)E.

For the integrated gap, write R' for an independent draw from the q-weighted ratio distribution and similarly for Rbar'. Direct trapezoidal integration gives
    integral_0^1 L(s) ds = 1/2 - E|R-R'|/4.
For ordered atoms with masses w_i and slopes r_i, the difference between half the mean and the area is half the sum over i<j of w_i w_j(r_j-r_i). Hence the area gap equals one quarter of the difference in the two Gini mean differences. This identity is the familiar concentration-curve/Gini relationship in finite form; its use to score tag alphabets is an engineering proposal.

**A two-tag trap.** Take p=(1,2,3,4)/10, q=(1,1,1,1)/4 and d=1/10. Tag all R<=1 together and the remaining contexts together. TV remains exactly 1/5 because no positive and negative p_i-q_i are cancelled. But at s=1/4 the original L is 1/10 and grouped L_C is 3/20. The actual witness b=(9/10,0,0,0), a=b+d gives B=9/40, A=19/100, gap -7/200. The restricted coarse model gives minimum A=47/200, a positive gap of 1/100. In the actual pooled first tag the A success rate is 2/5 and B is 9/20, so the original local guarantee does not survive grouping. This is a deliberate negative fixture: preserving TV does not preserve the baseline-specific frontier, and imposing an unjustified coarse local advantage could exclude a real reversal. The grouped curve is not a conservative bound when the actual baseline can vary inside groups.

## The tag compiler and its failed greedy intuition

Suppose tags must be contiguous blocks in likelihood-ratio order. For a block G, let c_G be its hinge deficit evaluated at its mean Rbar_G:
    c_G = sum_{i in G} q_i max(Rbar_G-R_i,0)
        = (1/2) sum_{i in G} q_i |R_i-Rbar_G|.
Below the block's smallest ratio or above its largest the deficit is zero. It increases up to the mean and decreases after it: below the mean the grouped hinge is zero; above it the grouped hinge has slope q_G, while the fine hinge has slope no greater than q_G. Ordered disjoint blocks have disjoint interior ratio ranges; even if endpoints tie their deficits are zero at those endpoints. Therefore E=max_G c_G.

For an ordered prefix ending at j, define D(k,j) as the smallest achievable maximum block cost with exactly k blocks. D(0,0)=0, all other impossible states infinity. Then
    D(k,j) = min_{k-1 <= i < j} max(D(k-1,i), c_{i+1,...,j}).
This is a complete exact minimax compiler for contiguous tags (O(k*m^2) transitions after precomputing block costs; naive cost precomputation O(m^3)). It is not the general optimum.

I initially conjectured that optimal tags could always be taken contiguous. **False even without ratio ties.** The native rational search supplies p=(1,1,3,5)/10 and q=(6,1,2,1)/10, with strictly increasing ratios 1/6,1,3/2,5. Here are all seven two-group partitions, numbered from 0:

| Groups | Worst vertical loss E |
|---|---:|
| 012 / 3 | 7/30 |
| 013 / 2 | 17/40 |
| 01 / 23 | 7/30 |
| 023 / 1 | 1/2 |
| 02 / 13 | **1/5** |
| 03 / 12 | 29/70 |
| 0 / 123 | 11/40 |

The best unrestricted deterministic two-tag alphabet interleaves the ordered ratios. The best contiguous alphabet loses 7/30, versus 1/5. Both are exact. This is not a counterexample to likelihood-ratio threshold testing, which optimizes a single decision at a specified mass budget; it is a counterexample to restricting a reusable finite partition for a uniform vertical-loss objective. Fractional splitting of contexts and randomized tags are separate problems; no claim about their optimum.

The JavaScript census found 194 cases (profile and tag-budget combinations) in which arbitrary partitions outperformed contiguous partitions under a fixed stable tie ordering. The first such case contained tied ratios; do not interpret that count as 194 strict-ratio counterexamples. The native search above explicitly excludes ties and demonstrates a genuine failure.

## Synthetic score and methodological consequences

The renderer produces four 6-second mono PCM16 files (8 kHz), derived from the first table. Forty equal slots per policy. Each contains a context tone (300 Hz easy, 600 Hz hard, or silence in the untagged version) followed by an outcome tone (800 Hz correct, 400 Hz incorrect). The exact counts are 15 vs 25 successes overall, but the context-conditioned rates favor A in both rooms. The score is deterministic and ordered by context; it is neither a trial randomization nor an actual auditory experiment. Tagged and untagged energy differ; do not interpret this as a controlled listening comparison. In a future matched-energy experiment replace silence with a neutral context token, randomize trial order, preserve provenance and compare explicit tags versus a pooled summary. No listening benefit is predicted as fact.

Suggested evaluation receipt: policy/version, outcome definition, context identity or tag, context denominators by policy, conditional outcome counts, common target-population weights, pooled and standardized estimates, uncertainty and missingness. A tag compiler is an optional analysis aid, not a replacement for the underlying records. Report whether comparisons are descriptive, standardized or causal; avoid collapsing accuracy, action completion, latency and workload. The arithmetic assumes fixed known context laws and exact probabilities; sampled estimates require uncertainty treatment. Unobserved confounding, post-policy contexts, missing support, outcome-dependent sampling, estimated weights and selection can defeat causal interpretation. A ratio class can be sufficient for this binary distribution-pair audit yet discard meaning relevant to another comparison or listener. Positivity is stipulated; zero-weight contexts need separate treatment. No accepted MHAC design or canonical record is changed.

## Sources, qualification and handoff

- Judea Pearl, *Understanding Simpson's Paradox*, UCLA technical report R-414, December 2013, subsequently American Statistician 68(1), 8–13 (2014), DOI [10.1080/00031305.2014.876829](https://doi.org/10.1080/00031305.2014.876829). [Author-hosted report](https://ftp.cs.ucla.edu/pub/stat_ser/r414.pdf): read sections 1, 2.1 and opening of 2.2; inspected the printed page 4 image (PDF index 3) on 25 November 2026. Pearl distinguishes arithmetic reversal from causal surprise and states a causal sure-thing condition when the subpopulation distribution is unchanged. His warning that the proper aggregation depends on causal structure is a contrary constraint on naive stratification, not evidence for a cue design.
- Mauro Gasparini and Lidia Sacchetto, *On the definition of a concentration function relevant to the ROC curve*, METRON 78, 271–277 (2020), [DOI](https://doi.org/10.1007/s40300-020-00191-5). Read publisher HTML sections 1–2 including Definitions 1–2, equation (3), and the retrieved section containing equation (4) and the Gini corollary. They relate the optimal likelihood-ratio ROC to relative concentration, rather than an arbitrary score ROC. Their continuous setting is not the finite partition problem above; the finite derivation is self-contained. Neither source was subjected to a full systematic review or admitted to the frozen empirical corpus. No scientific-priority claim.
- Repository antecedents: #545's actual report read; #36 issue and empty comments read, including explicit concern about task-specific averaging. Target #554 and empty comments read. Targeted issue searches for Simpson, collapsibility, Berkson, confounding and aggregation returned no direct competing expedition; search is bounded, not proof of novelty. Existing neighbouring workers' branches left alone.

Reproduction: run `node laboratory.cjs` and compare output with `qualification.json`. The exact integer computation uses positive compositions of eight mass units for each law, dimensions 2–5, and a scale 840 divisible by all possible group masses. It enumerates fractional allocations in integer q-mass units; all curve knots are integer in this grid. It checks 2,940 profiles, 215,663 allocation witnesses, 26,460 curve knots, 84,378 deterministic coarsenings (hinge, area, losslessness, ordering), and 12,446 contiguous-DP comparisons with literal partitions. The implementation's function was executed in a JavaScript runtime before publishing the exact function source; the Node CLI wrapper was not executed locally. No assertion failed.

Run `python witness.py` in this directory to reproduce the native receipt and original WAVs. Python 3.13.5 executed twice, byte-identical JSON receipts, 10,000 literal vertex checks for constant local margins (not heterogeneous margins), strict counterexample search stopped after 118 ordered strict profiles. Source and receipt Git blob IDs match the native files: 214524aac7477828a2ed1c1c466d30cf0899f1b4 and 505257c99a5f7104fd92b60edf1de0cc718c9b34. Audio hashes are recorded in the native receipt; WAV files are generated, not committed. This is same-agent cross-checking, not independent peer review. Theorems proved above are distinct from bounded computational results and the proposed experiment.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866; 337 branch entries, 100 open issue and 100 open PR results inspected. AGENTS, RAG, programme, runbook, integrity, validation and experiments read. Previous expedition #546 exact-head workflow 45607331572 completed successfully. Fresh issue-scoped branch only. No shared manifest, canonical registry, other branch or frozen protocol changed. Full repository CI and integrator review remain separate gates; no merge here.

*Fiction:* the clerk walked through every room and found the new bell more reliable. Back in the lobby he read the ledger and found the old bell had won. The apprentice looked at the doors rather than the bells. The ledger had counted the rooms in different proportions.
