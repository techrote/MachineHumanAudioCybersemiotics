# The Audit That Keeps Its Seed
## An adversarial afterlife for the deterministic audit theorem

Refs #258 · 24 November 2026. Original finite mathematical construction, exact synthetic computations, interpretive commentary and fiction. No Track E/G admission, human observations, causal identification, production safety requirement or mathematical priority claim.

### Archaeology: an overlooked quantifier

The intellectual sediment atlas on main (see [quotient guard](../intellectual-sediment/QUOTIENT-GUARD.md)) asks when omitted distinctions change a decision. In draft [#251](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/251), The Auditor Who Asks Too Much proves that adaptive deterministic revelation cannot beat an optimal fixed audit under worst-case remaining identification-interval width. Its explicit caveat near the end of section 3 is the object recovered here: it does not prove the same equality for a fixed hidden assignment evaluated in expectation over private randomness. The draft's section 4 supplies a Bayesian expected-width counterexample, but that assumes a distribution on the labels. Neither result answers the private-coin minimax question.

Draft [#245](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/245) independently makes a closely related timing distinction for mixed decisions under unknown positional scoring conventions. Its regret matrix is not our missing-label audit matrix; its timing lesson does transfer. The following is a concrete candidate exaptation of that lesson into #251, not a claim of independent rediscovery. The Examiner of Silences (#235) instead studies missing fallback loss; The Warning That Makes Itself False (#227) allows the report to change its target. Here labels are static and reveal-only. If audit selection changes labels, the model refuses its own application.

Reconciliation: main observed at 495a98ca12bae467a507031f04931aa4254b1866; read AGENTS, RAG, programme, runbook, integrity and freeze; inspected current open issue/PR listings and first page of branches. Exact main check repository-integrity passed (run 45256194041, job 137978536422); #251 exact head 94cf0033089734409e460cd3292ff19353a7cc42 has a successful repository-integrity check (run 45313206261, job 138173818611); legacy status lists empty for both, not affirmative checks. #251 remains draft, not accepted scientific research. Inspected #251, #235, #227 and #245 reports at their pinned heads (94cf0033, 7d5bdf86, c501a4ed, 5503e3f4 respectively), and the main atlas/quotient guard. #197's earlier landed tranche is not an orphan: post-merge check is successful. #211 has an existing branch at 335ba8dec5f017e39a434f5c74d4aaf2fca0405d and no matching open PR observed; no takeover or inference of abandonment. #184's longer longitudinal agenda remains open. New issue #258 had no comments at creation. The scope is isolated, no other branches or central records changed.

### Model and exact reduction

Let n>=2 cases have distinct scalar weights w_i (not necessarily sorted unless specified). The score numerator is C+sum_i w_i y_i, with exactly one positive label. This is the one-positive specialization of #251's paired Brier-loss difference with missing labels, where w_i=2(q_i-p_i) up to a positive scale factor. C can change as observations arrive but never affects width. Arbitrary integer weight examples are in coefficient units, not raw Brier loss; rescale into [-2,2] and divide by the original roster size to recover score units. The count must be independently established, not assumed by the system under test. Allow n-2 perfect, equal-cost queries. If the positive is found, the remaining width is zero; otherwise two cases i,j remain and the width is d_ij=|w_i-w_j|. The interval is an identification bound, not a confidence interval.

Each deterministic adaptive algorithm has an all-negative path with a retained pair e={i,j}. For any positive outside that pair, it finds the positive and width becomes zero (even if it continues querying). For either endpoint, it follows exactly the all-negative path and finishes with width d_e. Without loss of optimality the algorithm always uses its budget unless the answer is already determined. Hence every such deterministic policy has exactly the same loss vector as a fixed audit leaving that pair, and random mixtures of adaptive policies reduce to random mixtures of fixed pairs. No adaptivity advantage exists here even under an arbitrary fixed prior. This equivalence is specific to one positive and this terminal budget, not a claim for the general #251 problem.

A deterministic minimax policy keeps a closest pair; value delta=min_e d_e. If two weights coincide, keeping that pair makes width zero in every world and the optimization below (division by d) is unnecessary. For distinct weights, delta>0.

Now change the order of moves. The hidden positive location is fixed before the independent audit random draw. The adversary knows the distribution p over retained pairs but not its realization when choosing the location. In world i the expected width is

    L_i(p)=sum_(e incident to i) d_e p_e.

The private-randomized value is V=min_p max_i L_i(p), with p>=0 and sum p=1. In contrast, if the adversary can select the world after seeing the realized pair, then it chooses an endpoint; the expected maximum width is sum p_e d_e >=delta. The strongest per-run bound, max over both seed and world, likewise cannot beat delta. No contradiction with #251: these are different orders of quantification. The roster can be public and the seed disclosed after it is irrevocably fixed; perpetual secrecy is not necessary.

### Weighted fractional matching certificate

For strictly positive gaps, define

    F = max sum_e x_e/d_e
        subject to x_e>=0, sum_(e incident to i) x_e<=1.

This is a weighted fractional matching on the complete graph of cases, with inverse-gap edge weights. The sharp identity is V=1/F.

Proof: for any p with worst expectation M>0, put x_e=d_e p_e/M. These edge variables are feasible and their objective is 1/M, so M>=1/F. Conversely take any optimal x and set p_e=(x_e/d_e)/F. This is a probability distribution and every world has expected width <=1/F. Existence follows from compactness of the primal feasible set. The reciprocal is thus exact.

A reusable lower-bound certificate is a vector a_i>=0 such that a_i+a_j>=1/d_ij for every pair. Weak duality follows by summing edge constraints multiplied by x and applying the vertex capacities. The dual minimum sum a_i equals F by ordinary finite linear-programming duality; our sharp examples below exhibit equality directly, without reliance on a numerical LP solver. The normalized hard distribution h_i=a_i/sum a gives each pure retained pair average loss d_ij(h_i+h_j)>=1/sum a. This distribution is a mathematical adversarial certificate, not a belief or an estimate of positive prevalence. Feasible x and a with equal objective certify both optimal audit and worst-case lower bound. An auditor need not guess the hidden world.

The small exact oracle enumerates feasible half-integral edge capacities. Why is that sufficient? At a vertex of the matching polytope, columns of the positive-edge incidence matrix restricted to tight vertex rows must be linearly independent: otherwise a small signed perturbation preserves positivity and all tight inequalities, contradicting extremality. An edge with x=1 is an isolated component. For a nontrivial connected component of fractional edges, a leaf is slack because its only incident weight is <1. A tree would have at least two slack leaves, so its number of edges exceeds its tight-row count. A component containing a cycle has at least as many edges as vertices; independence forces equality, all rows tight, and no leaves, hence a simple cycle. An even cycle admits alternating signed perturbations; an odd cycle has the unique all-half solution. Thus an optimal vertex is made of isolated edges with weight 1, odd cycles with weight 1/2 and unmatched vertices. Enumerating degree-feasible units 0,1,2 (where units represent halves) includes every vertex, and all candidates are feasible.

For a separate dual vertex oracle, choose n active constraints among a_i=0 and a_i+a_j=1/d_ij; solve exactly and retain feasible solutions. The dual has an optimum vertex: it is nonempty, nonnegative and has compact nonempty objective sublevel sets. For integer weights use L=lcm of all positive integer distances, and scale by 2L. Every nonsingular active incidence system has integral coordinates in that scale: within a connected equation component all coordinates equal a signed root plus an even integer; an anchor fixes the root directly or an odd cycle fixes twice the root to an even integer. A component with neither leaves a free variable, so cannot occur in a nonsingular system. Exact elimination is checked for divisibility rather than silently rounded. General primal enumeration capped at seven vertices, dual at five; large regular examples use explicit certificates.

### Sharp lattice law and a counterargument to risk averaging

Take n equally spaced weights with step s>0. Write x in the graph above. For even n, disjoint adjacent pairs with x=1 give F=n/(2s). The dual a_i=1/(2s) for all i is feasible because every distance is at least s. For odd n, pair the first n-3 vertices adjacently, then form a triangle on the last three consecutive vertices with x=1/2 on its three edges. Its objective is (n-3)/(2s) + 1/(2s)+1/(2s)+1/(4s) = (2n-1)/(4s). A matching dual sets a_i=1/(4s) at zero-based even vertices and 3/(4s) at zero-based odd vertices. Adjacent sums are 1/s, equal-parity even pairs have gap at least 2s and sum 1/(2s), and all other constraints hold. The objective agrees. Therefore

    V = 2s/n         for even n,
        4s/(2n-1)    for odd n.

Every world's expected loss equals V for these constructed lotteries. The deterministic value remains s, so the ratio s/V grows with n; this is a relative statement, not an unbounded absolute Brier error. Example n=3, s=1: leave pairs (0,1), (0,2), (1,2) with probabilities 2/5,1/5,2/5. Every world's expected width is 4/5. A hard prior with masses (1/5,3/5,1/5) gives every pure plan average width 4/5. With a uniform prior, a deterministic adjacent pair has average width 2/3; that smaller number solves a different objective. A single deterministic plan still has worst width 1. For n=2 there is no query and no gain; for duplicate weights there is already zero width.

| n | deterministic worst width / s | private randomized worst expected width / s |
|---:|---:|---:|
|2|1|1|
|3|1|4/5|
|4|1|1/2|
|5|1|4/9|
|8|1|1/4|
|16|1|1/8|
|32|1|1/16|

Do not disguise the change from a deterministic bound to an expected bound. In the odd construction the long triangle edge has probability 1/(2n-1), and for either endpoint its realized width is 2s on that draw. Thus the optimum expectation may require accepting worse single-run uncertainty than the deterministic optimum. If every seed/world must have width <=s, only adjacent pairs can receive mass. On that path graph the uniform distribution over floor(n/2) disjoint edges gives worst expected width s/floor(n/2). The zero-based odd vertices cover every adjacent edge; averaging the load over these floor(n/2) vertices proves the matching lower bound. For even n the cap is free, for odd n it costs a strictly worse expected width than the unrestricted optimum. At n=3 the cap eliminates the benefit entirely. This is a separate safety/robustness preference, not a proof that real auditors should accept larger residual intervals.

### Source boundary, transfer and adversarial objections

Yao, A. C.-C. (1977), Probabilistic computations: Toward a unified measure of complexity, 18th SFCS, pp. 222–227, DOI https://doi.org/10.1109/SFCS.1977.24. IEEE metadata and DBLP record https://dblp.org/rec/conf/focs/Yao77.html inspected 24 November 2026; full paper not read. Ben-David & Blais (2020 preprint), A New Minimax Theorem for Randomized Algorithms, https://arxiv.org/abs/2002.10802; author abstract inspected, which identifies Yao's classical minimax context and discusses a different new theorem. No import of their theorem into this proof and no mathematical priority assertion. For standard fractional matching terminology, inspected the teaching note https://jhc.sjtu.edu.cn/public/home/kuanyang/teaching/MATH3806/notes/lec08.html, section 8.3 (matching LP relaxation). This secondary teaching source is not claimed to establish the weighted complete-graph construction here. The exact certificate above is self-contained. No empirical sources used.

A concrete exaptation is a paired-evaluation audit receipt containing roster commitment, trusted count provenance, allowed reveal budget, decision target and loss functional, randomization policy, order of adversarial moves, realized seed after the freeze, deterministic fallback bound, and primal/dual certificates. Only if the audit is genuinely reveal-only, with static labels and fixed roster, could the proposed method be tested on comparative software evaluation. No secrecy about the research or data manipulation is implied; the protocol and probabilities can be fully inspectable. A simpler alternative is to publish the sharp deterministic width and leave the result unresolved. Randomness should earn its complexity by an explicitly agreed objective.

Negative controls and refusal conditions: no known count -> the original unrestricted width is additive and independent of revealed values; arbitrary label counts -> the all-negative-path reduction is not justified; unequal costs, noisy reveals, label changes, adaptive adversary and compromised random draw -> this theorem does not apply. If one needs sign certification rather than width, decision value must be modeled separately. Expected width does not imply a per-run interval or a confidence guarantee. Distinct coefficients are not necessarily distinct human-perceived sounds. The cap result demonstrates why expected-risk improvement is not unconditional improvement. Preserve disagreement between #251's worst-case guarantee and #245's mixed decision model rather than replacing either.

### Reproduction and qualification

Run with Node.js (standard library only):

    node research/expeditions/audit-that-keeps-its-seed/lab.js

One AI (ChatGPT) authored proof and code. Executed the JS function bodies in a V8 isolate, with independent primal half-unit enumeration and dual active-equation elimination using BigInt. The cap certificate additionally checks a direct reveal oracle. Exact outputs: 56 distinct integer-weight models, 21,613 candidate dual active systems, 78,343 feasible primal leaves (including regular cross-checks), 189 regular primal/dual certificate comparisons (n=2..64, s=1,2,7), 189 hard-cap certificates, 3,069 probability-grid mixtures (three/four states, denominator ten), 73,758 direct reveal evaluations in those grid and ordering controls, and five malformed input refusals. Named duplicate and n=2/3/4/5 cases passed. These counts are overlapping categories, not a combined independent test total. The general proof, not the finite enumeration, establishes the arbitrary-size lattice law. V8 execution is not a native clean-checkout Node replay or independent review; exact-head repository CI and review pending at time of writing.

### Fiction — the auditor's sealed envelope

A museum held three clocks. One clock was running, but no one could remember which; opening a clock's case would reveal the answer without changing it. The auditor was allowed to open only one case. A clerk asked that the selection always be printed in the morning paper, another that the clocks be fixed first and the envelope opened afterwards. Both called their procedure a public audit. Only one had given the clockmaker the opportunity to choose which clock to leave running after learning the question. The third clerk refused the envelope entirely: her contract required every unresolved interval to be small, not merely the average of many such intervals.

No empirical or mathematical premise depends on this fictional scene.
