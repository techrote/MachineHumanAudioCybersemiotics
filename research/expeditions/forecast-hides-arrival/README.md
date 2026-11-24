# The Forecast That Hides Its Arrival
## The exact value of private preview and the cost of exposing its availability

**Refs #322 · 24 November 2026 · isolated mathematical/synthetic expedition.** One ChatGPT (GPT-6.2) author and self-review. No empirical, participant, physical-acoustic, production privacy, Track E/G acceptance or mathematical-priority claim.

## Contents

1. Excavation — connect the causal/offline gap with task-relative informativeness and observer metadata.
2. Exact finite-channel theorem — optimal posterior-tail selection, lower bound and implementable witness.
3. Erasure preview — closed form, feasibility threshold and public availability penalty.
4. Accuracy counterexample — a predictor with zero classification gain can eliminate leakage.
5. Exaptation and refusal — forecast provenance, lawful preview, telemetry and scientific boundaries.
6. Qualification and sources — executable exact finite tests, source extent and disposition.

## 1. Excavation

[Draft #315](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/c0349ccf1c308c1e0bdf4c3a747d51fbff7b814d/research/expeditions/mask-borrows-tomorrow/README.md), §3, separates a causal encoder from an offline one for a fair initial bit, asymmetric second-bit transition, and the three-coordinate even-parity alphabet. The gap prices an extreme information restriction. The report's preview receipt, §4, explicitly leaves legitimate prediction outside its theorem. Does a predictor have to be accurate to close the gap? Does observing when it arrives matter?

[Draft #307](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/51f171155273b0c4ca4f903317679fc489e02819/research/expeditions/hint-changes-listener/README.md), §2, gives the *observer* a noisy cue inaccessible to the encoder. Here it is the *encoder* that has an early cue, initially unavailable to the observer. Neither experiment can silently substitute for the other. [Draft #237](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/0bd86578cc7dd27ce6ec176ab04c631b8f9e4a7d/research/expeditions/museum-of-unasked-questions/README.md), §§1–3, separates decision equivalence from scalar measures of information. Here two forecasts equally good for classification differ in their value for privacy. [Draft #257](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/de904fa15d96328dd1308e57e8e2936c154d7684/research/expeditions/preview-debt/README.md), single-stage and two-stage sections, prices delay for recovery of a nonminimum-phase audio channel. That is a different objective and signal model, not a privacy theorem: its transferable idea is to price information access separately from final fidelity.

Base main: 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, research integrity, validation, relevant draft reports and issue scopes/comments (#314, #306, #236, #256; no comments at read). Open inventory snapshot: 102 issues and 84 PRs; recent #317, #319, #321 concern switching observers, relational notation and sample restoration. Inspected open titles and first 200 branch names for collision; not a full review of every branch. #315 remained draft with successful exact-head Research integrity run [45375905916](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45375905916). These upstream results are draft mathematical claims, not accepted empirical records. New issue #322 owns only this directory; core corpus gates remain open.

## 2. Exact finite-channel theorem

Three possible recipient indices g, fixed for two ticks. The public alphabet is A={000,110,101,011}. At each tick the actual recipient's coordinate must equal the actual source bit. The observer sees the ordered pair of words. The source law is the same for all g:
 
    P(X1=1)=1/2
    P(X2=1 | X1=0)=a
    P(X2=1 | X1=1)=1/2.

At tick one the encoder knows g, X1 and a finite signal Z; at tick two it also knows X2. The joint source/signal law is exogenous and invariant under g; private encoder randomness is independent of it. Z may be correlated with X2 but does not change its law. No further feedback or preview is permitted. The observer does not see Z or its availability flag unless explicitly specified in §3.

Put p_z=P(Z=z|X1=0), h_z=P(X2=1|X1=0,Z=z); omit zero-mass z. For 0<=t<=1/2 define

    M(t) = min (1/2) sum_z p_z h_z s_z
           subject to (1/2) sum_z p_z s_z = t,  0<=s_z<=1.

This is the smallest possible joint mass of X2=1 and first word 000, if that word has mass t. Sort h_z from low to high, fill the lowest-posterior cells first, and randomize at the boundary if necessary. Swapping selected mass from a higher to a lower posterior cannot increase cost; thus the construction solves the optimization. It is a fractional knapsack / likelihood-ratio threshold problem, not a new general optimization theorem.

**Theorem:** the optimal worst-pair total variation leakage with hidden preview is

    delta* = max(0, 3 M(1/4)/2 - 1/4).

Equivalently, let L be the mean posterior over the lowest half of the conditional signal probability mass (fractionally splitting a cell at the median). Since M(1/4)=L/4,

    delta* = max(0,(3L-2)/8).

In particular, perfect anonymity is possible iff L<=2/3. No property of the cue conditional on X1=1 is needed: the attaining policy can ignore it there.

**Lower bound.** Symmetrize any admissible policy by uniform coordinate permutations, relabelling the actual recipient. This preserves utility, source/cue law and allowed information; by convexity it cannot increase maximum pair TV. In the resulting law first word 000 has mass t for each g. The nonzero word omitting g has mass 1/2-t, and each including g has mass 1/4. At first word 000 let m=P(X2=1,W1=000). Each second word containing g has mass m/2; the other nonzero word has mass at most t-m. For any pair of groups the contribution from this block is at least max(0,3m/2-t), and m>=M(t). The two nonzero first-word blocks omitting one of the pair each contribute at least half the absolute difference of their first-word masses. Hence

    delta >= max(0,3 M(t)/2-t) + |t-1/4|.

M is piecewise linear with slopes in [0,1]: adding selected mass adds between zero and that mass of ones. So F(t)=max(0,3M(t)/2-t) is 1-Lipschitz (its nonzero slopes are in [-1,1/2]). Consequently F(t)+|t-1/4|>=F(1/4). This also covers a=0, a=1, degenerate hints, and discontinuous posterior cells; no differentiability assumption at corners is needed.

**Attainment.** At tick one, when X1=0, use the minimizing selection s_z for t=1/4 to emit 000, otherwise emit the nonzero word omitting g. When X1=1 choose uniformly between the two words including g, ignoring Z. All first words now have mass T=1/4, independent of g. Write M=M(T). After first word 000, actual next-bit probability is M/T. After a nonzero first word the omitted coordinate has next-bit probability (a/2-M)/T; each included coordinate has probability 1/2. All these probabilities belong to [0,1], since each is a true conditional probability under the first-tick selection policy.

For a common second-word law with marginals x,y,z, use the four masses from #315 §2:

    (1-(x+y+z)/2, (x+y-z)/2, (x+z-y)/2, (y+z-x)/2).

At nonzero first words the vector is a permutation of ((a/2-M)/T,1/2,1/2), always feasible. After 000 it is (M/T,M/T,M/T), feasible exactly when M/T<=2/3. Otherwise use a group-specific law assigning zero mass to 000, mass 1-M/T to the nonzero word omitting g, and M/(2T) to each word including g. Each actual group marginal is correct. At tick two, sample the designated conditional law given that its g-coordinate equals the actual X2. The actual conditional bit probability equals that law's g-marginal, so integrating over X2 reproduces the specified law. Unreachable conditionings do not need an output. This is an executable two-tick policy given the stipulated legitimate cue, not a retrospective coupling disguised as a forecast. It attains the bound because only the 000 block may differ, and its pair TV is exactly F(T). More capable first-tick processing cannot improve the optimum.

The proof relies on the fair initial bit, three coordinates, b=1/2 and the specific vocabulary. It does not establish a scalar reduction for arbitrary longer-horizon controlled sources or arbitrary observer knowledge.

## 3. Erasure preview and the availability flag

Let an independent Bernoulli(q) availability flag R determine whether X2 is revealed to the encoder at tick one. With R=0 the cue is an erasure, not a wrong prediction. Conditional on X1=0 the posterior distribution has masses q(1-a), 1-q, qa at 0,a,1 respectively. The lower-half selection gives

    M(1/4) = max(0, a/2-1/4, a/4 - q a(1-a)/2)
    delta_hidden(a,q) =
      max(0, (6a-5)/8, (3a-2)/8 - 3 q a(1-a)/4).

For example, if the zero cell fills the lower half the minimum is zero. Otherwise take the zero cell, fill from the erasure cell, and if necessary take some of the one cell. The three terms for M correspond to these cases, respectively. At q=0 recover #315's causal formula; at q=1 obtain the additional sharp offline leakage formula max(0,(6a-5)/8), not only its zero/nonzero threshold.

For 2/3<a<=5/6, the exact minimum availability for perfect anonymity is

    q_min = (3a-2)/(6a(1-a)).

For a<=2/3 no preview is needed; for a>5/6 perfect anonymity is impossible even with full preview. At a=5/6, q_min=3/5.

**Now expose only R to the observer**, not the forecast value. Because R is independent of the source and group, conditioning on R yields exactly the no-preview and full-preview problems. Symmetrize to make all pair distances equal; TV for disjoint flagged blocks is the weighted sum. Apply the respective sharp bounds in the two blocks, then use their attaining policies separately. Thus

    delta_public(a,q) =
      (1-q) max(0,(3a-2)/8) + q max(0,(6a-5)/8).

At a=5/6, hidden preview closes the gap at q=.6, but public availability requires q=1 to reach zero. This does not make metadata intrinsically harmful: it changes the modeled observer's information and the privacy objective. No claim about observing the *value* of X2, additional logs, side channels or a source-dependent flag follows from this derivation.

| q at a=5/6 | Hidden flag TV | Public flag TV |
| ---: | ---: | ---: |
| 0 | 1/16 | 1/16 |
| 1/5 | 1/24 | 1/20 |
| 2/5 | 1/48 | 3/80 |
| 3/5 | 0 | 1/40 |
| 4/5 | 0 | 1/80 |
| 1 | 0 | 0 |

The two notions are genuinely different design contracts. Hiding the flag allows cross-flag cancellation of differences in law, whereas disclosing it prohibits that cancellation. Independence of the flag from group does not imply independence from the joint transcript given group.

## 4. A forecast with no classification advantage

At a=5/6, consider the following two conditional cue channels on X1=0.

| Channel | Cue mass | Posterior P(X2=1) |
| --- | ---: | ---: |
| No cue | 1 | 5/6 |
| Weak cue, low | 1/2 | 2/3 |
| Weak cue, high | 1/2 | 1 |

The weak channel's joint counts for X2=0,1 are (1,2) and (0,3) out of six. Both channels have the same Bayes-optimal next-bit classification accuracy, 5/6: both always guess one. But the weak channel has lower-half mean 2/3, versus 5/6 for the no-cue channel. Therefore their optimal privacy leakages are zero and 1/16 respectively. This is not an assertion of equality under other scoring rules. In fact the expected Brier loss of the posterior forecast decreases from 5/36 to 1/9. The distinction is strictly about classification accuracy, not an absence of information.

The general family 2/3<a<=5/6 admits the same counterexample: equal-mass posteriors 2/3 and 2a-2/3, both above 1/2. This is an exaptation of #237's decision-relative information: a predictor can be useless for changing a hard action and useful for modulating a stochastic encoding policy. Conversely, no cue improvement can eliminate the vocabulary obstruction above a=5/6. Increasing prediction skill does not abolish every architectural constraint.

## 5. Exaptation, deliberate refusals and score

**Interpretive synthesis, not a human-performance finding.** A forecast's marginal accuracy and its operational value can diverge, because the receiving decision rule may use its uncertainty rather than its most probable class. A forecast-availability log can also change the observer's information even when the log alone reveals no recipient identity. The earlier #315 future-suffix falsifier needs a refinement: hold *all legitimately available inputs*, including the forecast and independent seed, fixed before varying an unseen suffix. If a forecast is statistically coupled with the suffix, arbitrary incompatible counterfactuals are not valid inputs. A change with a genuinely fixed available prefix is evidence against the no-preview contract; variation due to a legitimate different forecast is not.

**Proposed test-only forecast receipt:** record the target and distribution, authorized availability time, calibration/provenance of predictor, whether the system can see the realized hint, whether observers see its value/availability/timing, what decision criterion uses it, and exact evaluation population. Test both pooled and flag-conditioned transcripts, not merely whether the flag alone is independent of the group. Compare task-specific loss, hard accuracy, calibration and a no-preview control separately. This is not a requirement to conceal operational telemetry; safety, auditability, and regulatory requirements can outweigh the toy anonymity gain. Never use this argument to hide an actual failure or invent forecast availability.

**Negative controls:** unrestricted alphabet including 111 permits exact anonymous repetition of the bit without preview; independent fair source bits require no cue; full preview does not rescue a>5/6. The weak-cue example has a different Brier score, so it cannot refute the value of proper scoring. An observer who also sees the cue value needs a separately derived optimum. Real auditory signals have timing, recognition and contextual channels absent from these ideal symbols.

**Symbolic score (unrendered, artistic):** two chords from the even-word vocabulary. Before the first chord a backstage light signals either the low or high posterior. The performer still predicts the same next note in both cases, but changes the first chord's distribution. In the second edition an independent light marks forecast availability publicly. The second note is played only after its value arrives. No measured sound, human comprehension or privacy result is asserted.

**Fiction:** A conductor says the new oracle is no better than the old: it predicts rain every time. The percussionist replies that the oracle distinguishes drizzle from certainty. The conductor looks at the printed score and finds no difference. The percussionist looks at the rests.

## 6. Qualification and sources

Run `node lab.js` in this directory. Dependency-free bounded exact integer calculations (all tested intermediate products fit the safe-integer range; no arbitrary-precision or unbounded input claim). The actual V8 execution returned:

| Activity | Count |
| --- | ---: |
| Three-cell joint signal families, even total count 2..10 | 4,899 |
| Vertex candidates in independently formulated selection oracle | 213,768 |
| Greedy versus vertex optimum comparisons | 48,543 |
| Mass-shift lower-bound comparisons | 48,543 |
| Constructed recipient transcript-law checks | 41,022 |
| Direct pair TV checks | 41,022 |
| Erasure-preview parameter grids | 2,924 |
| Public flag comparisons | 2,924 |
| Named controls / malformed-input refusals | 4 / 5 |

The oracle enumerates full/empty selection cells and at most one fractional cell rather than trusting the posterior sort. The witness checks exact joint source marginal and normalization for each recipient, actual next-bit mass at each first word, and pair TV from all 16 transcript cells. The lower-bound grid tests the mass-shift argument. It is not a separate exhaustive search over every arbitrary encoder; the analytic symmetrization and Lipschitz proof supply that bound. The counts overlap and are computational checks, not independent experiments. V8 executes the same function text committed to the repository; native Node and full clean-checkout repository suite not run at the time of this report. Exact-head repository integrity CI and substantive review remain acceptance items.

**Source comparison:** Mikael Vejdemo-Johansson, [MTH410 lecture 11, Hypothesis Testing: Neyman-Pearson's Lemma, Most Powerful Tests, Proportions](https://www.math.csi.cuny.edu/~mvj/MTH410/lectures/L11.html), sections Probabilistic Testing and Finding the Best Test: Neyman-Pearson, theorem/proof and likelihood-ratio test definition. Open HTML, targeted reading 24 November 2026 by the same AI author. The established threshold principle allows randomization to meet a prescribed constraint; our constrained mass selection uses the equivalent posterior ordering and a direct exchange proof. This is scholarly teaching exposition, not a primary historical reading of Neyman/Pearson. No literature-wide novelty assessment is claimed. Pinned upstream MHAC drafts are read as internal mathematical arguments, not empirical sources. No external reviewer or new human evidence.

Disposition: two additions under this issue-owned directory; no changes to canonical records, protocols or shared manifests. Draft PR, Refs #322, pending review and integrity qualification. The key disagreement remains: prediction evaluation and the value of the prediction to another procedure are distinct; public accountability and pooled anonymity can also be distinct objectives. Neither should be silently optimized in place of the other.
