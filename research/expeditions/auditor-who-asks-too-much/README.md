# The Auditor Who Asks Too Much
## Missing outcomes, exact comparative score bounds and when adaptive inquiry earns nothing

**Refs #250 · 24 November 2026.** Exploratory mathematical model and synthetic experiment with interpretive commentary and fiction. No human observations, Track E/G evidence, accepted design rule, or assertion of mathematical priority.

## Contents

1. **Archaeology** — distinguish missing outcomes from missing utterances.
2. **Sharp paired score bounds** — derive exact extrema with and without a known count.
3. **The audit theorem** — prove the optimal fixed plan and minimax equivalence.
4. **A contrary case** — demonstrate a strict expected-width gain from adaptivity.
5. **Source boundary and exaptation** — distinguish previous research and propose an audit receipt.
6. **Reproducibility and claim status** — record actual tests and remaining gates.

### 1. Archaeology: the missing answer, not the missing utterance

The [quotient guard](../intellectual-sediment/QUOTIENT-GUARD.md) tests whether a declared decision is constant across states collapsed by a representation. It does not say which additional observations to obtain when a decision is not constant. The Examiner of Silences (draft [#235](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/235), head 7d5bdf8643639700d40e279f94e21ca540d67f4e) studies unobserved fallback losses for abstained cases. The Warning That Makes Itself False (draft [#227](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/227), head c501a4ed3e3b1f15b6e2ab2a3d1b978230f7c332) questions the outcome law itself. The Bell That Cannot Promise (draft [#243](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/243), head 54b547c8fe1f04f6d79fa99eedf867c5f8488ba8) separates incentives from representation; its audit model concerns penalties for false reports, not acquisition of comparative evaluation data. Consensus calibration [#221](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/221) assumes a fixed roster for its identities. This expedition asks something distinct: **both forecasters spoke, the target is shared and static, but some outcomes were never recorded. Which observations are worth recovering?**

The natural answer in a research culture that prizes adaptive clarification is to ask one question, interpret its answer, then decide what to ask next. Under one exact adversarial criterion this extra flexibility is entirely unnecessary. Under a different criterion it can pay. Neither result should be promoted to a universal claim about inquiry.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866, repository-integrity success on that commit. Read AGENTS, RAG, programme, runbook, integrity rules and protocol freeze; inspected live branch list (first page), open issue and PR lists (up to 100 each), the main quotient guard and the actual reports at the three pinned draft heads above. The latest visible open subjects included #244 positional scoring, #246 unequal protection and #248 switched dynamics; these concern different mathematics. Related open work is not accepted evidence. The new issue #250 had zero comments at creation. Base and path are isolated; no change to other branches, shared manifests, canonical records, human gates, or frozen methods.

### 2. Sharp paired score bounds

Let N>0 fixed cases each have two frozen binary event probabilities p_i and q_i in [0,1]. A single binary outcome y_i is shared by both predictions; some are observed, some unknown. Define the difference of empirical mean Brier losses (binary squared-error convention) as

    Delta = (1/N) sum_i [(p_i-y_i)^2 - (q_i-y_i)^2].

Expand using cancellation of the shared outcome square:

    N Delta = C + sum_(i unknown) w_i y_i,
    w_i = 2(q_i-p_i),
    C = sum_i (p_i^2-q_i^2) + sum_(i observed) w_i y_i.

This is a finite-roster algebraic identity, not calibration, causal utility or out-of-sample performance. With n missing outcomes, all assignments in {0,1}^n admitted, the exact minimum and maximum numerators are C plus the sum of negative weights and C plus the sum of positive weights respectively. They are attained by setting the associated outcomes to one. The attainable set need not contain all intermediate values: it is discrete. We report its bounding interval, not a statistical confidence interval.

If independently credible evidence fixes the number m of positive outcomes among the n missing ones, sort weights a_1 <= ... <= a_n. The sharp numerator endpoints become

    L = C + sum of the m smallest weights,
    U = C + sum of the m largest weights.

Proof: swapping a selected large weight for a smaller unselected weight cannot increase the minimum; repeat until the m smallest are selected. Reverse for the maximum. m=0 and m=n have width zero; empty sums are zero. Equal weights have zero width under fixed m even when every missing outcome individually remains unknown. Without that count, n equal nonzero weights give width n|w|. A count is thus capable of identifying a comparison without identifying any case.

Do not use prevalence on a selected subset as m. Do not assume the total from a model being evaluated. If outcomes change under the competing policies, one shared y_i is not defensible: this analysis must refuse that causal comparison. If one forecaster has missing predictions as well, the current setup is not the required model.

A strict rank is warranted by U<0 (A lower loss) or L>0 (B lower loss); zero endpoints permit only weak inequalities. A bound straddling zero permits rank reversal. This is not a statement about expected future ranking.

### 3. The audit theorem

Stipulate perfect reveal-only, equal-cost queries: querying one missing case reveals its already-fixed outcome. No change in forecasts or target, no errors, no extra information, no group constraints besides m if supplied. The auditor commits to at most k distinct queries and minimizes the **worst possible final width**, not expected width, sign uncertainty, or acquisition cost. Put l=n-k. Additional queries never enlarge the identification interval, so exactly k may be considered.

**Unrestricted outcomes.** Each unqueried weight contributes |w_i| to width; the answer to a query changes only the offset, not the width. Query the k largest absolute weights. Adaptive policies cannot improve this bound, because every terminal retained subset has width at least the sum of the l smallest absolute weights. Ties may be resolved arbitrarily. A large absolute weight is disagreement, not inherent uncertainty of the event.

**Known total.** For sorted retained weights b_1,...,b_l and remaining positive count s, define

    W(b,s) = sum of largest s b's - sum of smallest s b's.

Complement symmetry gives W(b,s)=W(b,l-s). For s<floor(l/2), the increment is b_(l-s)-b_(s+1)>=0, hence the width rises to the middle. After k fixed audits, feasible s ranges from max(0,m-k) to min(m,l), inclusive. Its maximal minority count is

    r = min(m,n-m,floor(l/2)).

Thus the worst final width for that retained subset is W(b,r). The possible outcomes of queried cases need not be enumerated to find the worst width.

**The contiguous-block theorem.** Among all subsets of l retained weights, an optimum is always a consecutive block in the sorted original weights. If r=0, all have width zero. Otherwise let i_1<...<i_l be the chosen indices (one-based). Consider the consecutive block of length l starting at i_r-r+1. It is valid: its start is at least 1 and its end is at most i_l. For j<=r its jth index is at least i_j, so its low-end weights are no smaller. For j>=l-r+1 its jth index is at most i_j, so its high-end weights are no larger. Its width at r cannot exceed that of the chosen subset. This proves the claim including duplicate weights. Enumerate the k+1 consecutive windows and choose the minimum, using prefix sums if desired. The executable uses direct sums; no claim of optimized runtime.

    V(n,m,k) = min over consecutive blocks b of length l W(b,r).

Query the complement of any minimizing block. Retaining a central dense cluster can be optimal, but it need not be centered on zero. With all weights equal, every window works. At k=n-1 the known total supplies the last outcome without querying it; even earlier identification can occur when surviving coefficients coincide.

**No minimax-width value of adaptivity.** For any deterministic adaptive policy, an admissible adversary supplies the majority label among remaining positives and negatives on every query (break equal-count ties arbitrarily). This preserves the minority count until the counts balance, then maintains a difference of at most one. After k reveals the remaining minority count is exactly r. The policy's retained subset on this path has width W(b,r)>=V(n,m,k). The adversary is consistent with a single complete assignment: extend the answers at the end using the remaining count. The fixed window policy achieves the matching upper bound on every path. Hence the adaptive minimax value equals the nonadaptive optimum. For policies randomized with a worst-case criterion over both labels and realized random seed the same proof applies per seed. We do **not** claim equality for an oblivious adversary evaluating expected width over private randomization.

Example: weights [-4,-3,-2,1,2,5], m=2. These are unnormalized coefficient units; any finite integer vector can be scaled into the allowable Brier weight range. Divide widths by the roster size and undo the chosen coefficient scale before interpreting them as Brier-loss differences.

| Audits k | Count known: optimal worst width | Count unknown: optimal worst width |
|---:|---:|---:|
|0|14|17|
|1|10|12|
|2|6|8|
|3|2|5|
|4|1|3|
|5|0|1|
|6|0|0|

If the count is unknown the rule is remove largest magnitudes; if known the rule becomes a shortest-width retained window. The same forecast pair can therefore rationally receive different audit plans depending on which auxiliary evidence is trusted.

### 4. A contrary case: why the theorem is not anti-adaptivity

Change only the objective to expected final width and stipulate a uniform distribution on the binary assignments with exactly m positives. Let w=[0,1,1,3,3,4], m=2, k=2. There are 15 equally likely worlds. Exact enumeration gives the best fixed expected width 40/15=8/3. Auditing the zero and four weights achieves that value.

An adaptive optimum first queries the zero-weight case. If it is negative, query a weight-one case; if positive, query the weight-four case. Across the original 15 worlds, the branch width sums are 30 and 8 respectively, giving 38/15. Thus adaptation strictly improves the stipulated expectation by 2/15, while the optimum worst-case width remains 3 for both policy classes. The zero-weight case has no direct contribution to the comparative score, yet its outcome changes the remaining count and can redirect inquiry. Without the trusted total, a zero-weight label cannot improve the bounds at all.

This is a disagreement with an overly broad interpretation of selective clarification. A query may have value through the constraints it changes rather than the term it measures. Conversely an adaptive workflow may burn compute, time and interaction budget without improving its chosen adversarial guarantee. In a sign-certification problem, variable stopping, priors, asymmetric costs, constrained strata, noisy reveal, or policies changing outcomes, a different optimization is required. No theorem for those objectives is proved.

### 5. Source boundary and exaptation

- Charles F. Manski (2005), *Partial identification with missing data: concepts and findings*, International Journal of Approximate Reasoning 39(2–3), 151–165, https://doi.org/10.1016/j.ijar.2004.10.006. Publisher abstract inspected 2026-11-24; describes identification regions by admitting possible missing-data distributions before imposing identifying assumptions. Our finite-roster bounding interval follows the same broad discipline but is a discrete deterministic construction, not a population estimate or reconstruction of the article's results.
- Himabindu Lakkaraju, Jon Kleinberg, Jure Leskovec, Jens Ludwig and Sendhil Mullainathan (2017), *The Selective Labels Problem: Evaluating Algorithmic Predictions in the Presence of Unobservables*, KDD, 275–284, https://www.kdd.org/kdd2017/papers/view/the-selective-labels-problem-evaluating-algorithmic-predictions-in-the-pres ; DOI 10.1145/3097983.3098066, metadata cross-check https://pubmed.ncbi.nlm.nih.gov/29780658/. KDD abstract inspected. The authors describe labels observed as consequences of human decisions and develop a specific evaluation methodology; our toy problem does not reproduce that methodology or address intervention-dependent potential outcomes. It is a counterexample to treating incomplete ground truth as a mere measurement nuisance.
- Jannik Kossen, Sebastian Farquhar, Yarin Gal and Tom Rainforth (2021), *Active Testing: Sample-Efficient Model Evaluation*, PMLR 139, 5753–5763, https://proceedings.mlr.press/v139/kossen21a.html. Publisher abstract inspected; the authors distinguish acquisition for evaluation from acquisition for training and describe bias correction. Their stochastic estimation goal is different from our exact worst-case finite-roster interval objective. No conclusion against active testing follows from the no-adaptivity theorem.

Only metadata and abstract-level claims are used. No full-text review, exhaustive novelty search, empirical generalization or mathematical priority asserted. No copyrighted source copies included. These are exploratory references outside the frozen search/selection pipeline, not additions to Track E/G.

**Proposed audit receipt** (unvalidated): retain common target and policy identity, paired predictions, roster and unknown-label mask, scale, known outcome count and its independent provenance (or null), acquisition budget and objective, exact interval and endpoint witnesses, and the selected audit indices. When a query returns, record the verified label and recompute the interval. If cost or target changes, invalidate this receipt. A rank interval is not calibration; an audit plan is not a safety policy. In MHAC, the primary application might be comparing two synthetic warning classifiers or two agentic reviewers whose verdict labels have only partially been adjudicated. It must not substitute for the research protocol's source-appraisal or human gates.

Adversarial checks: (a) identical forecasts yield zero difference regardless of labels; (b) equal nonzero weights plus fixed count identify the difference, but not individual scores; (c) an unknown or fallible count must not be treated as exact; (d) a fixed nonadaptive optimum may be unacceptable if observation costs vary; (e) an empirical sample from the audited cases is selectively chosen, not automatically representative; (f) choosing forecasts after seeing audits violates the frozen-comparison premise; (g) lack of a strict rank is not evidence of equal performance; (h) minimax width is not the probability of finding a winner. The most likely bad transfer is using the theorem to reject adaptive research generally.

### 6. Reproducibility and claim status

Run node lab.js from this directory. No dependencies or network access required. All arithmetic in the bounded census is integer; forecasts are stored on a grid p=P/D and outcomes are 0,1,null. The Brier numerator is in units of 1/(N D^2). The executable rejects out-of-range grids, counts and budgets and limits the abstract weight domain; exponential oracles are for small cases only.

Executed 2026-11-24 in V8: 61,056 exact Brier-bound comparisons against direct assignment enumeration across every roster of length 1–3 with forecasts in {0,1/2,1} and observed/unknown labels; 43,824 audit-value comparisons across sorted weight multisets from {-2,-1,0,1,2}, lengths 0–7, every budget and every valid count plus unknown count. Compared the window or magnitude rule with exhaustive fixed subsets and a separate adaptive minimax recurrence, and checked the returned policy witness. All passed. Five malformed-input refusals and named controls passed. The expected-width strict counterexample was found separately by Python Fraction search; its numerator totals were verified in the JS executable. A preliminary Python search checked 19,916 interior known-count/budget models of length 3–7 against fixed subset enumeration without finding a strict worst-case adaptive improvement; this motivated the proof, but is not itself proof.

The JS function body executed was serialized into the committed executable; clean-checkout Node replay and repository CI are separate checks. One ChatGPT agent authored the report and both computational approaches; no independent human or external review. The finite proof and test outputs are mathematical/synthetic claims; the audit receipt is a design hypothesis; the archaeology is interpretation. No empirical findings.

Remaining: exact final-head repository check and independent substantive review; merge only after appropriate integrator/approval and normal checks. Issue remains open. No human gate necessary for synthetic mathematics itself; none bypassed.

### Afterword (fiction): The Conservatory's Unheard Examinations

A conservatory commissioned two mechanical adjudicators. Both wrote, in advance, a number beside every student's name: the probability that the student would find the lost note in a particular score.

A flood destroyed several examination tapes but left the two sets of numbers intact. The committee was instructed to recover as few recordings as possible and determine how much the two adjudicators might differ.

The first examiner built a beautiful brass instrument that selected a tape, listened, adjusted a dial and selected another. Its sequence was different for every possible performance. The second examiner used a pencil to circle a set of names and sent a porter downstairs.

The first examiner demanded that the committee recognize the sophistication of the machine. The porter observed that their instructions concerned only the largest possible remaining disagreement. The brass instrument could not make that number smaller.

Then the committee changed its instructions: it wanted a smaller disagreement on average, rather than a guarantee against the worst case. The first examiner quietly switched the instrument back on.

There was no dispute about the machine. There had been a dispute about the examination.
