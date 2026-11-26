# The Bell That Passes Every Smaller Menu

Refs #638 · 26 November 2026 · base main 495a98ca12bae467a507031f04931aa4254b1866.
Scope: original finite mathematical research and synthetic acoustic demonstration; no canonical evidence admission, human study, production claim or priority claim. One ChatGPT research agent performed derivation, source reading and implementation.

**Subsequent generalization:** [Beyond truthful reports](GENERAL-CHANNELS.md) extends the exact bounds to arbitrary finite channels, credits the established Doeblin endpoint, and disproves the unrestricted repetition rule using a binary symmetric channel. It has a separate executable and receipt.

## The anomaly

Five possible machine states A–E. Two instruments report truthful subsets of possible states. R identifies the state with probability 1/2 and otherwise reports the whole universe. T always reports a uniformly selected three-state subset containing the actual state. Both are perfectly calibrated under this stipulated channel. Consider a receiver with two actions, each harmful only in its corresponding state, or a receiver with three such actions. Under a uniform prior, R and T have equal optimum residual risk 1/10 on the two-action example. With three actions, R retains risk 1/10 while T reduces risk to 1/30. More strongly, R is at least as good as T for EVERY two-action decision problem, with arbitrary prior and finite losses; yet it fails for a three-action problem. These are action alternatives, not state supports (the earlier #236 expedition addresses the latter).

The smallest three-state case is established prior art: Bertschinger and Rauh's Example 18 is exactly a half-revealing three-state channel versus uniform two-state reports (up to output permutation). Their section 3 also attributes the general distinctness of bounded-action orders to earlier work. This report develops a quantitative formula for the whole truthful subset family, not a claim of priority over the known separation.

## Exact two-sided residual risk envelope

Let X have n >= 2 states. A subset channel is defined by weights w(S) >= 0 for nonempty S subset X, with sum of w(S) over S containing i equal to 1 for every i. Conditional on state i, report S has probability w(S) if i belongs to S and zero otherwise. Its likelihood is constant on each reported subset; this is a stronger requirement than mere truthful inclusion. Repeated labels with different likelihoods cannot be silently merged.

Define coverage c(T) = sum of w(S) over S containing T. It is antitone in T, and c({i}) = 1. Define c_m = min c(T) over |T| = min(m,n). Let sigma = min_i w({i}).

For a decision problem with at most m >= 2 actions, subtract the smallest loss in each state (the irreducible perfect-information loss). Multiply the remaining losses by the state prior. Write these nonnegative columns as a_j(i), so min_j a_j(i)=0. Define L=min_j sum_i a_j(i) (residual risk with no observation), and R=sum_S w(S) min_j sum_{i in S} a_j(i) (residual risk after observing S). We permit finite arbitrary real losses; the normalization does not alter comparisons. If L=0 then R=0. Otherwise:

    c_m <= R/L <= 1-sigma.

Both bounds are attained for every full-support prior, even with nonnegative bounded raw losses after a suitable common rescaling. For a fixed prior with zero masses the inequalities remain valid; the endpoints need not be attainable.

Proof of lower bound: choose a minimizing action j(S) for each S, breaking ties deterministically. For action j define b_j(i) = sum of w(S) over S assigned to j and containing i. Then R=sum_j sum_i b_j(i) a_j(i) >= L sum_j min_i b_j(i). Choose a witness i_j attaining each minimum. Every S containing all i_j contributes its weight exactly once to sum_j b_j(i_j), namely to its assigned action. The sum is therefore at least c({i_j}). There are at most m distinct witnesses; monotonicity gives c({i_j}) >= c_m. For equality choose a minimizing T and one action per state in T, each with weighted loss 1 at that state and 0 elsewhere. There are at least two distinct states and thus row minima zero. Duplicate an action if needed. Each column has total 1; every report containing T incurs loss 1, and every other report allows zero loss. This is a constructive certificate, not an optimizer-dependent inequality.

Proof of upper bound: take a minimizing no-observation column a*. On all nonsingleton reports use this fixed action; on singleton reports choose the statewise zero-loss action. Risk is at most sum_i a*(i)(1-w({i})) <= (1-sigma)L. For equality choose i minimizing w({i}); let action A cost 1 at i and 0 elsewhere, and B cost 0 at i and 1 at every other state, all in prior-weighted units. L=1. Every nonsingleton report containing i costs 1; all other reports cost zero. Hence R=1-w({i}). In both proofs an arbitrarily nonuniform full-support prior can be handled by dividing the chosen weighted losses by the prior and scaling globally. No utility comparison requires an empirical decision maker.

## The action-arity frontier

Let E_p reveal the state with probability p, otherwise output the entire state set. Its residual risk is exactly (1-p)L. The preceding envelope proves:

    E_p dominates the subset channel on every <=m-action problem iff p >= 1-c_m.
    The subset channel dominates E_p on every <=m-action problem iff p <= sigma.

Dominance means weak inequality of optimal expected loss for every prior and finite loss matrix; the necessity witnesses use full support. When sigma < p < 1-c_m, neither dominates: one task favors each. At equality the relevant weak dominance holds; if both conditions hold the channels are equivalent for the menu size. The case m=1 is vacuous (there is no choice). For all finite menus, m=n suffices in this particular comparison, because c_m saturates at w(X). This is not a bound for arbitrary pairs of channels. At p >= 1-w(X), E_p actually garbles into the subset channel: map its erasure to X, and its revealed states to the remaining conditional report masses, including any remaining X mass. Conversely if p <= sigma, each singleton can be thinned to reveal its state with probability p; all other output is erased. The endpoint p=0 or 1 is handled by dropping unused output symbols.

For uniform r-element reports (1 <= r <= n), w(S)=1/binom(n-1,r-1) for |S|=r. Hence

    c_m = binom(n-m,r-m)/binom(n-1,r-1), for 2 <= m <= n,

with zero for r<m and saturation for m>n. In particular for r=n-1 the sharp reveal probability is (m-1)/(n-1). For each k from 2 to n-1 choose p=(k-1)/(n-1): the revealing instrument passes EVERY test with at most k actions, but a (k+1)-action avoidance task refutes universal superiority. This is an explicit hierarchy inside a simple family. It generalizes the three-state Example 18, not the first known existence of the hierarchy.

For n=5,r=3, p=1/2 and uniform prior, give each action a unit loss only in one distinct named state. With two actions the two instruments tie at 1/10; with three, subset reporting has loss 1/30 versus 1/10. With four such actions T has zero loss versus 1/10. Conversely the two-action witness from the upper bound gives T risk 1/5 versus 1/10 for E_p. Note that a decision problem with m actions is not an m-state classification problem, and arbitrary sequential actions need not be equivalent to a single m-choice menu.

## Repeated observations and the information budget

For d independent reports conditional on one fixed state, the whole ordered report tuple has likelihood product_j w(S_j) if the state lies in the intersection, zero otherwise. Thus the intersection is a sufficient observation and its weights are obtained by summing products over tuples with that intersection. A state-independent reinflation chooses a tuple proportional to its product weight; it reconstructs the channel law, not the historical report. The new coverage for T is exactly c(T)^d. Accordingly the exact lower residual-risk ratio with at most m actions becomes c_m^d. The maximum ratio becomes 1-min_i w_d({i}), where w_d({i}) can be computed by inclusion-exclusion:

    w_d({i}) = sum_{T contains i} (-1)^(|T|-1) c(T)^d.

The formula follows by expanding the indicator that no other state remains in the intersection. Independently repeating E_p a times gives risk (1-p)^a L. Comparing to b independent subset reports, its exact forward dominance condition is

    (1-p)^a <= c_m^b.

At equal repetition counts, the direction of this guarantee never changes (strict monotonicity of positive integer powers). Repetition improves absolute risks but does not repair a failed universal comparison with the same number of receipts. If c_m=0 and p<1, no finite number of reveals suffices to dominate that subset experiment on all such menus. For the five-state triples example and three actions, one subset report needs three independent p=1/2 reveal reports to match or exceed it universally: 1/8 <= 1/6 < 1/4. At four actions no finite reveal budget suffices. Independence and fixed state are essential: duplicating a single report d times leaves coverage unchanged, not exponentiated.

## Executable qualification and acoustic specimens

Run node laboratory.cjs in this directory. The laboratory function was executed in a V8 isolate; its body was directly serialized into the committed source. The Node CLI wrapper was not independently executed in a repository checkout. Integer report weights and state-weighted integer costs give exact risk comparisons throughout the bounded domain (values are safely within exact integer range). The laboratory tested 123 channel profiles (not necessarily distinct), 53,182 literal loss matrices (44,624 positive baseline), 523 exact lower and 523 upper witnesses, 112 fixed-size formulas and 3,876 intersection coverage comparisons across 220 repeated channel profiles. Binary loss rows are exhaustive in designated small cases; seeded integer losses and partition mixtures broaden the census. Repeated partition draws need not cover every subset-weight channel. No assertion failures. The counterexample and illustrative example fields in the JSON are documented witnesses, not separate assertion counts.

A second native Python 3.13.5 implementation used explicit conditional matrices and Fraction arithmetic; it enumerated every normalized three-state integer-weight profile with denominators 1..3, and uniform subset channels through seven states. Results: 87 channel profiles, 239,436 literal risk checks (165,147 positive baseline), 464 endpoint checks, 112 uniform formulas, 4,440 literal report tuples and 12 repetition endpoint checks. The source and outputs are retained in the companion local native package, not committed by this PR. Both executions reproduced their native JSON and WAV files byte-for-byte.

Two original 0.6-second mono PCM16 scores at 8 kHz enumerate six equally weighted conditional outcomes for true state A: one score has three A-only chords and three full-universe chords, the other has the six distinct triples containing A. Seeded ordering changes neither inventory. Carrier frequencies 300,400,500,600,700 Hz; 100 ms per chord; fixed coefficient 4400 integer PCM units per included carrier. No silence is used for erasure: it is the all-state chord. Both banks were read from PCM and decoded via sinusoidal projection, recovering all 12 chords exactly. Maximum absolute coefficient errors 0.12483029 and 0.13587287 PCM units; peaks 19889 and 12530. These are digital representations of stipulated set-valued symbols, not physical transmission or human reception tests. Energy is not matched; the audio examples are not controlled listening stimuli. The finite scores enumerate conditional outcomes, not samples from an independently randomized population.

Negative controls: the theorem fails if report likelihoods vary within a set. For example, two distinct tagged reports both name {A,B}, but tag 0 is exclusive to A and tag 1 exclusive to B. Observing the tag perfectly identifies the state; discarding it yields the uninformative full set. Treating mere inclusion as equal likelihood is unjustified. Changing the state during repeats, dependent reports, action-dependent observations, non-Bayes behavior and uncertain priors are outside the contract. A correct direct message may be cheaper than either instrument.

## Interpretation, sources and disposition

The distinction is between the number of possible world states, the number of feasible actions, and the statistical structure of a report. The earlier #236 expedition holds decisions unrestricted but narrows the state support; here state support is unrestricted, and the number of actions is bounded. This offers a testable design convention: attach the menu-arity and loss contract to any claim that one acoustic reporting system is no worse than another. A new action can invalidate the qualification without any change in the sender's error rates. A human listener's effort, memory, training, and acoustic perceptual confusion are not captured by the optimum-risk model. In particular we do not infer that a report containing more tones is cognitively better, or that cybersemiotics explains the inequality beyond conventional statistical decision theory.

Sources accessed 26 November 2026:
- Nils Bertschinger and Johannes Rauh, "The Blackwell relation defines no lattice", arXiv:1401.3146v1 (2014), https://arxiv.org/abs/1401.3146 and https://arxiv.org/pdf/1401.3146. Read introductory setup, Theorem 4, Proposition 9, Section 3 Definition 13/Lemma 14, and Example 18. Inspected original PDF images of printed pp. 6–9 (PDF indices 5–8). The source supplies established bounded-action comparison and the exact three-state special case. Its general separation is explicitly credited; the report's quantitative coverage envelope is self-contained and its scientific priority not established. The whole paper was not read.
- MHAC #236, https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/236 and its complete report on mhac-236/museum-of-unasked-questions: read as upstream exploratory sediment, not accepted research evidence. It uses proper-support equivalence and subset reporting; our restricted action contract is distinct. Issue and comments inspected (none returned). No external source material redistributed.

Repository reconciliation: main metadata and AGENTS, RAG, PROGRAMME, AGENT_RUNBOOK, RESEARCH_INTEGRITY, VALIDATION read; 379 branch entries, 100 recent open issue and 100 recent open PR results inspected; targeted searches for Blackwell, garbling, zonotope and action alphabet. No matching scoped action-arity extension found, but no exhaustive literature novelty claim. Previous PR #631 exact-head PR workflow returned completed/success. Native git ls-remote failed DNS resolution; full clean checkout validation not run. Fresh branch only, no canonical manifest edits, no production promotion. Leave issue open for independent critique and exact-head CI; separate local package contains the native witness and audio.

Fictional afterword: a machine was judged by every question with two buttons. The apprentice installed a third button. The earlier verdict had been accurate, but the machine was no longer the better oracle.
