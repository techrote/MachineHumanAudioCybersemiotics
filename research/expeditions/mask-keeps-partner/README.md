# The Mask That Keeps a Partner
## Temporal privacy, changing states, and the cost of forgetting a coupling

**Refs #274 · 24 November 2026 · original bounded mathematical expedition.** One ChatGPT AI author, derivation, code and self-review. No independent scholarly review, human listening, empirical finding, production privacy claim, accepted Track E/G evidence or mathematical priority claim.

## Contents

1. Excavation — recover the untested changing-state clause of #267 and connect it to #241.
2. Model and exact threshold — an optimal two-announcement trade-off and causal construction.
3. Persistent pairing — sharp asymptotic leakage and a reset counterexample.
4. Delayed obstruction — perfect privacy of every proper projection need not glue.
5. Design and artistic interpretation — specify coupling lifetime, not simply randomness.
6. Provenance and execution — source extent, tests, limitations and acceptance boundary.

## 1. Excavation: the cached answer becomes stale

Draft [#267](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/267) proves perfect single-release group privacy for an even-parity code, inevitable leakage when independently reissuing a fixed state, and a cached-draw alternative. Its section 4 explicitly warns that reuse after state change may break correctness. That warning is the orphaned result pursued here. Draft [#241](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/241), sections “Four-state counterexample” and “Arbitrarily delayed higher-order failure”, supplies a second seam: temporal pair statistics do not determine complete word laws. Both are unaccepted drafts, despite passing repository-integrity jobs. Their joint implication is not “use more randomness” or “preserve all state”; the temporal dependence of a valid encoder itself becomes a design variable.

Accepted X004 [quotient guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md) explicitly excludes stochastic and dynamic guarantees. Accepted X005 [negative-space protocol](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/sound-of-nothing/NEGATIVE-SPACE-PROTOCOL.md) treats expired state as stale, not resolved; this is a candidate lifecycle rule, not a demonstrated human benefit. Caching a now-false tone is therefore not a satisfactory privacy mechanism. An explicit erasure or omission is also not a free escape if exact per-tick decoding is required.

Main observed twice at 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity and validation; enumerated 78 open issues and 60 open PRs and live PR heads. The most recent parallel topics include winding lifts, instrument appropriation, context-erasure codes and quantized attractors; scope triage by titles and selected descriptions, not full technical review of all 60. Read #266/#267, #240/#241 and #268/#269 issue/PR descriptions and comments (empty), plus the relevant #267 and #241 report passages at heads 40b97941 and d4f73ea3. Main and those heads had successful repository-integrity checks. R005/R006 remain open, downstream scientific acceptance remains gated. No concurrent branch or central file modified.

## 2. The changing-state code

The group g is fixed in {1,2,3}. Its private binary source B_t has a group-independent law. The emitted symbol W_t is a three-bit vector in E={000,011,101,110}, the even-parity words. Decoder g knows g and reads its coordinate (W_t)_g=B_t. The full #267 contextual-admissibility restriction is inherited: a word must represent an admissible transversal; odd words are disallowed by the cross-group action contexts constructed there. If that restriction is dropped, all-equal words 000/111 can trivially encode the bit with group privacy. This is an important negative control. We study the exact four-word alphabet only, no claims about arbitrary channels, timing side channels or extra metadata. The observer sees the entire ordered W transcript but not g. Let Q_g denote its conditional distribution. Objective is the maximum pairwise total variation delta = max TV(Q_g,Q_h), with TV(P,Q)=max_event |P(event)-Q(event)| = half the L1 distance. No group prior needed. Perfect group privacy means delta=0.

### 2a. Sharp two-announcement bound

Let B_0 be fair; let its next flip X_1=B_0 XOR B_1 be independent of B_0 and Bernoulli(r), identical for every group. Define D_1=W_0 XOR W_1, necessarily in E. Write A_i for the event D_1 has coordinate i equal to one. Under Q_g, Q_g(A_g)=r. Since there are at most two ones in D_1, sum_i Q_g(A_i) <= 2. Each other Q_g(A_i) >= Q_i(A_i)-delta = r-delta. Thus 3r-2delta <=2, yielding

    delta >= max(0, (3r-2)/2).

The argument applies to any randomized, even offline policy on these two ticks; it is not a restriction to memoryless encoders.

Attainment: sample W_0 uniformly among the two compatible words for observed B_0. Then W_0 is uniform on E conditional on g, independent of future flips. Construct the following target law for D_1:

- r <= 2/3: mass 1-3r/2 on 000, mass r/2 on each nonzero word. This is a common law with every coordinate's marginal Bernoulli(r).
- r > 2/3: mass 0 on 000; mass 1-r on the nonzero word with coordinate g zero; mass r/2 on each of the other two words.

Upon observing X_1, sample from that target law conditioned on coordinate g=X_1, and set W_1=W_0 XOR D_1. A zero-probability conditioning event is unreachable and need not be defined on-model. This preserves exact decoding and implements the target law without access to future state. For r>2/3 the two group laws differ only by swapping two masses 1-r and r/2, so their TV is r/2-(1-r). W_0 is independent and has common law, so the entire two-word transcript has the same TV as D_1. This attains the lower bound.

The same construction repeated with independent increment randomness when source flips are IID yields a group-independent full transcript at **every** finite horizon for r<=2/3. For r>2/3 no even two-tick group-private policy exists. Therefore 2/3 is the exact causal perfect-privacy threshold under this symmetric IID increment model. At r=0 we reproduce cached output; at r=1/2 this is the uniform even increment law, consistent with the independently resampled source control in #267. At r=1, exactly two coordinates must flip but every actual source demands a flip at each step; the contradiction is not acoustic.

| Source flip probability r | Best two-tick max pairwise TV |
| ---: | ---: |
| 0 | 0 |
| 1/2 | 0 |
| 2/3 | 0 |
| 3/4 | 1/8 |
| 9/10 | 7/20 |
| 1 | 1/2 |

These exact values are mathematical consequences of stipulated rates, not empirical rates or measured listener performance.

## 3. Persistent pairing versus fresh choices

### 3a. A causal policy that never leaks more than one-half

Choose one partner H uniformly among the two other groups, independently of the source, once at the beginning. Use the initial W_0 rule above. Whenever the actual source flips, flip both coordinates g and H; otherwise leave W unchanged. Decoder g is always correct, and no future bit is needed. This works for any increment law independent of the fair initial bit and common across groups, not just IID. The unordered pair {g,H} determines the law of the output increments. Under Q_g the two possible pairs are equally probable. Two groups share exactly one possible pair; if there is at least one flip, the three pair supports are disjoint. All-zero increments are common. Thus for L transitions,

    TV_pair(L) = (1 - P(no source flips in L transitions))/2.

With IID switching this is (1-(1-r)^L)/2. This is an achievable policy, not the general finite-horizon optimum. In particular it leaks unnecessarily for 0<r<=2/3, where section 2 gives perfect privacy.

The locally optimized fresh increment scheme for r>2/3 produces independent samples of different group laws. A frequency test on a coordinate-zero word with differing probability distinguishes any two groups with success tending to one (weak law of large numbers), so its transcript TV tends to one. At r=1 the exact fresh TV after L flips is 1-2^(-L): only the transcript consisting exclusively of the shared pair is common. Persistent pairing instead attains 1/2 at every L>=1.

### 3b. Sharp asymptotic minimax result

Suppose r>2/3 and the source flips IID. For each coordinate i, let F_i be the event that its observed flip count exceeds 2L/3. No transcript belongs to all three F_i because the total count is <=2L. Let p_L be the probability Binomial(L,r)>2L/3. Exact utility implies Q_i(F_i)=p_L, regardless of the policy. For any g, sum_i Q_g(F_i)<=2 and each of the two other probabilities is at least p_L-delta. Hence

    delta >= max(0,(3 p_L-2)/2).

The weak law gives p_L→1. Combined with the causal pairing upper bound, this proves that the optimum max pairwise TV tends to 1/2 as L→∞ for every r>2/3. For r<=2/3 the optimum is zero at all horizons. At r=1 the two bounds match for every positive L. No rate of convergence of the optimizer itself, finite-horizon solution for intermediate r, or uniqueness claim is made. The finite-horizon upper bound can be combined with the fresh policy by taking the better achievable bound, not by averaging incompatible metrics.

### 3c. Resetting the partner defeats the guarantee

If the partner is independently redrawn at each of R blocks of L transitions, with independent source increments across blocks, and the observer knows block boundaries, pairwise overlap is multiplicative. In a block the common mass is P(no flip)+(1-P(no flip))/2. On this common support the two group probabilities agree pointwise; all other supports are disjoint. Thus

    TV_reset(R,L) = 1 - ((1+(1-r)^L)/2)^R.

The initial output need only be sampled once; subsequent increments preserve its coordinate and are independent of it. Resetting the partner need not change the emitted current word. This formula concerns an observer who sees all blocks, not just a new observer per block. At r=1, R=1 gives 1/2, R=2 gives 3/4, R=8 gives 255/256. The same initial privacy audit and locally correct decoder could therefore miss a restart-induced disclosure. This is a concrete exaptation of #267's caching warning, not a prescription to persist real secrets forever. Persistent coupling can conflict with revocation, fault recovery, membership change, or privacy of the partner itself.

## 4. Delayed obstruction: every proper projection is private

### 4a. A non-Markov source, not just a different switching rate

Let L>=2 and draw a source sequence of L binary observations uniformly from odd-parity words. Every proper subset is independently fair (count the completions). For any encoder under the even-word rule, the XOR across all L emitted vectors is itself even. Let F_i now denote that the XOR of coordinate i across the complete sequence is odd. Under Q_i, F_i is certain. No transcript belongs to all three F_i, so the event inequality in section 3 forces delta>=1/2. This is a purely finite support obstruction; pairwise independent source observations do not suffice to guarantee transcript privacy.

The bound is attained with **all proper output projections perfectly private**, simultaneously. At the first L-1 ticks emit a uniformly chosen compatible even word; because the corresponding source bits are independent fair, the emitted prefix is uniform on E^(L-1), independent of group. At the final tick let P be the XOR of the emitted prefix; the three hypothetical final bits needed for each coordinate to achieve odd parity form T=111 XOR P, an odd word. The actual final source bit equals T_g by the stipulated odd source law. For each h != g the even word T XOR e_h matches the actual bit at g and misses exactly one of the other hypothetical requirements. Choose the two possibilities equally. This is causal (uses past words and the current bit; under the model the current bit is also determined by its past). It needs a known block boundary and source law.

The complete transcript is uniform over precisely those sequences of even words whose XOR has two ones, including coordinate g. Each has mass 1/(2*4^(L-1)). Two groups' supports intersect on exactly 4^(L-1) sequences, hence delta=1/2. For uniform group priors the observer can exclude one group but the other two have equal posterior probability: optimal success 1/2, not certainty. Delete any one output tick: for each fixed remaining sequence, exactly two completions are allowed for any group, with equal masses. Its law is uniform on E^(L-1), hence private; marginalizing further establishes every proper projection. For L>2 every two-tick output statistic is group-independent, even though the full transcript is not. This is exact projection equality, not a finite sample claim.

For contrast, if the source sequence is IID fair rather than conditioned on odd parity, emitting independent uniformly compatible words is fully private. All proper source projections agree between the two models. The known source law, not the nominal bit rate, determines which privacy contract is achievable. The all-even source sequence also permits perfect privacy: choose first L-1 words independently and set last to their XOR; the source's last bit is then exactly correct in each group.

### 4b. A subtle counterargument: increments and levels are not the same observation

The same proof and causal policy apply to L **increments** drawn uniformly from odd-parity sequences, with independent fair initial B_0. Interpret the even words as D_t and integrate them via W_t=W_(t-1) XOR D_t. This gives exact correctness, sharp TV=1/2, and uniform privacy for every proper subset of increments, even with the independent initial word present.

But do not advertise this as an arbitrarily high-order privacy failure in level samples. W_0 XOR W_L equals the XOR of all increments. Observing the two endpoints alone exposes the parity syndrome and achieves the full leakage bound. An increment projection is not a level projection. The genuinely high-order *level* result is section 4a, whose source constraint is on levels, not increments. In both constructions a targeted derived feature (the XOR aggregate) suffices, so even high-order marginal equality does not imply the adversary must store all raw events. This is a direct qualification of any “test every pair” approach: specify the observation map and allowable derived features.

## 5. Exaptation: coupling lifetime as part of a disclosure contract

Interpretive synthesis, not a theorem of cybersemiotics: an audible sign is also a commitment to a stochastic history. The same four labels, identical single-word marginals and exact decoder can produce different transcript disclosures. A policy that optimizes each new transition independently need not be a good policy for the complete history. However, at lower switching rates the fresh causal construction wins; the disagreement cannot be settled by a universal preference for persistent memory.

Proposed test-only contract: record the protected group, source process and group priors (if using classification metrics), context decoder, admissible words, observer's view including boundaries and derived features, causal access, coupling lifetime, reset semantics, and whether the loss is worst-pair TV, classification accuracy, a likelihood-ratio guarantee, or something else. Distinguish an observer who hears one period from one who hears a lifetime. Verify the actual source law rather than treating the stipulated law as measured. TV bounds do not imply differential privacy, cryptographic secrecy or safety. If a simpler deterministic code meets utility and privacy, do not introduce this mechanism. If source dynamics or group membership change, all current proofs may become irrelevant. Test delayed parity and reset fixtures as negative controls before claiming a temporal privacy property.

**Artistic score instruction (not executed audio):** three labelled pitches, four permissible chords (silence or a pair of pitches); read the chord bits as state, and the symmetric difference of adjacent chords as a gesture. For a listener who knows one pitch's part, every gesture in that part is correct. In the paired score, every source flip changes the same two parts. In the fresh score the pair changes. In the reset score it changes only at the block boundary. This is a symbolic score, not an acoustic masking claim; the absence of a pitch is an ideal coded zero, not a guarantee of perceptual silence.

**Fiction: The custodian's dance.** A bell-maker was ordered never to identify the dancer, but always to announce the dancer's step. Three dancers knew three readings of the bells. At first the bell-maker invented a new partner for every step. The audience learned the dancer's identity by watching who never failed to move. So the bell-maker chose one partner for the entire performance. Now the audience knew a pair but not which member was real. The director applauded the improvement and ordered a restart at every intermission. By the third intermission the audience had intersected the pairs. The director had believed that a reset erased memory; it erased the instrument's memory, not the audience's. Fiction only.

## 6. Source comparison, computational receipt and limits

Public source inspection, 24 November 2026, same AI author; no systematic novelty search or full-text claim:
- Backhoff, Beiglböck, Lin & Zalashko (2017), *Causal Transport in Discrete Time and Applications*, SIAM J. Optimization 27(4), 2528–2562, [DOI 10.1137/16M1080197](https://doi.org/10.1137/16M1080197). Publisher abstract and publication metadata inspected. It distinguishes causal transport plans and adapted processes and describes a dynamic programming result. Our elementary explicit conditional kernels share the nonanticipation concern; we do not apply their DPP or claim a causal optimal transport theorem.
- Kifer & Machanavajjhala (2014), *Pufferfish: A framework for mathematical privacy definitions*, ACM TODS 39(1), article 3, [DOI 10.1145/2514689](https://doi.org/10.1145/2514689). Publisher abstract and metadata inspected, especially applications to prior beliefs, composition and prior releases. It motivates explicit privacy specifications; our worst-pair TV objective is different from a likelihood-ratio Pufferfish guarantee and we make no such guarantee.
- Abramsky & Brandenburger (2011), *The Sheaf-Theoretic Structure of Non-Locality and Contextuality*, [arXiv:1102.0264](https://arxiv.org/abs/1102.0264), abstract inspected. Their global-section obstruction for compatible local distributions is a useful structural analogue to the failed three-coordinate coupling. No quantum, sheaf-cohomological or physical interpretation follows from our classical code.
- *Detecting complete and joint mixability*, J. Comput. Appl. Math. 280 (2015), 174–187, [DOI 10.1016/j.cam.2014.11.050](https://doi.org/10.1016/j.cam.2014.11.050). Publisher abstract and definitions 1.1–1.2 inspected. Real-valued constant-sum couplings are a nearby antecedent, but XOR is addition in a finite group, not a constant real sum. We do not invoke their detection algorithm or assume an existing real-valued mixability result proves our theorem.

Actual execution: [lab.js](lab.js) source function executed in V8 before commit. All arithmetic in finite census is integer or BigInt; no floating-point tolerance in assertions. From expedition directory run Node: node lab.js. Results:
| Check | Count |
| --- | ---: |
| Two-tick rational grid models d=1..6, k=0..d | 27 |
| Candidate triples of group laws on denominator 2d grids (direct TV minimization) | 548,019 |
| IID product vs persistent pairing model/horizon checks d<=5, L<=6 | 120 |
| Reset overlap binomial checks, 1..8 blocks | 960 |
| Delayed parity transcripts L=2..8 | 87,376 |
| Proper deletion projection support entries checked | 502,440 |
| Uniform odd source path entries checked | 762 |
| Invalid-input refusal controls | 5 |

Counts describe overlapping computational activities, not independent experiments. The grid search is a finite corroboration, not a proof of continuous optimality; the event inequality supplies that proof. Delayed construction is tested by comparing final causal selection to the direct global parity predicate and tallying source and deletion laws. Product and reset checks compare explicit transcript enumeration or binomial expansion to formulas. The asymptotic lower bound is analytic, not a numerical extrapolation. Same author for all code and proofs; no participant data. Full clean-checkout repo tests and exact-head CI not asserted here; substantive review and normal repository acceptance still required. Keep issue open and PR draft. No shared/frozen files changed.

**Negative memo:** reject universal claims that cache reuse or fresh randomness solves temporal privacy. The exact threshold, endpoint caveat and reset counterexample delimit their usefulness. Open questions: sharp finite-horizon optimum for 2/3<r<1; arbitrary group size and nonuniform source law; additional observer side information; protected membership changes; causal vs offline feasibility for more general source processes. No research stage completion follows.
