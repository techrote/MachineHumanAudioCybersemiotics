# The Hint That Changes Its Listener
## Noisy side information, exact privacy optimization and minimax regret

**Refs #306 · 24 November 2026.** Original finite mathematical expedition; one AI author, no empirical, participant or acoustic data, no priority claim, no Track E/G admission.

## Contents

1. [Archaeological premise](#1-archaeological-premise-and-scope) — recover the missing noisy-observer model.
2. [Universal reduction](#2-theorem-a-all-observer-channels-admit-the-same-one-parameter-reduction) — prove a single parameter suffices.
3. [Interpolation falsifier](#3-a-falsifier-for-interpolation-between-endpoint-optima) — an asymmetric cue reverses the optimizer ordering.
4. [Minimax regret](#4-theorem-b-a-universal-minimax-regret-compromise) — derive an exact robust compromise.
5. [Negative memo and score](#5-negative-memo-exaptation-and-artistic-distinction) — separate shared randomness, design and fiction.
6. [Source and execution receipt](#6-source-and-execution-receipt) — record bounded evidence and qualification.

## 1. Archaeological premise and scope

[Draft #299, The Law That Cannot Introduce Itself](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/7658412a47302facf5810613ff785b0a4543e688/research/expeditions/law-cannot-introduce-itself/README.md), §4, distinguishes an observer who knows the source law from an observer who sees only pooled announcements. Its three-recipient, fair-bit example proves a conflict between the two optimal encoders. This report removes the artificially binary choice of observer: what if the observer receives a noisy, asymmetric hint about the law? Is the optimal policy merely an interpolation between the two previous optima? No. Can there still be a rigorous compromise across all possible hint channels? Yes, for a precisely defined regret criterion.

[Draft #291, The Rest That Arrives Too Late](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/6dab50fb3685bbed534f017ca6259a29ac6e9304/research/expeditions/rest-arrives-too-late/README.md), §§2–4, explicitly restricts the recipient to a local coordinate, and makes source-law knowledge an assumption. #299 shows how law disclosure can change group privacy. Here the law is the one-bit source itself, as in #299 §4; no erasures, decoder uncertainty or sequence dynamics are included. The goal is not to optimize a hint channel but to choose an encoder when the external observer's hint channel is known or unknown.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, research integrity, validation and project foundations read. Separate live searches returned 94 open issue titles and 76 open PR titles before #306. Recent #301/#303/#305 concern common filters, constrained improvisation and equalization; no overlap at the scope/title level. #298 issue and comments (none) inspected; #299 remains a draft and its exact-head Research integrity run completed successfully. The pinned #299 and #291 reports are upstream hypotheses/proofs, not accepted empirical findings. The new issue owns only this directory. This is focused reconciliation, not a review of all 76 PRs or a declaration of programme readiness.

## 2. Theorem A: all observer channels admit the same one-parameter reduction

Let G be an odd integer at least 3. The protected recipient index g can be any of G coordinates. A source bit b is Bernoulli(p), with the same p for each g; 0<p<=1. An encoder knows b and g. It emits a binary word W of length G with even Hamming weight, and W_g=b exactly. The observer also receives a cue Z drawn from an arbitrary finite channel q_b(z). **Critical assumption:** conditional on b, Z is independent jointly of g and W (in particular of the encoder coin). That is, P(W,Z|g,b)=P(W|g,b)q_b(Z). The encoder cannot observe Z or adapt to its realized value.

Define D_q(K)=max over g,h of TV(P(W,Z|g),P(W,Z|h)), where TV is half the L1 distance. We protect recipient identity, not the bit or cue. There is no assumption about an actual human's knowledge, signal recognition or preferences.

Put B=p/(G-1), L=(1-p)/B. Then the exact optimum over all valid stochastic encoders is

    D_q* = B min_{0<=t<=L} F_q(t),
    F_q(t) = sum_z |t q_0(z) - q_1(z)|.

Moreover, every encoder is weakly dominated, **simultaneously for all such channels**, by one member of this one-parameter family:

* If b=1, choose uniformly among words of weight G-1 with the actual coordinate one.
* If b=0, emit the all-zero word, except with probability Bt/(1-p) emit the weight G-1 word whose sole zero is the actual coordinate.
* For p=1 the interval is the singleton t=0 and the b=0 branch never occurs. For p=0 all-zero is sufficient and every optimum is zero.

Proof: symmetrize any encoder over all coordinate permutations, including relabelling the actual recipient. The validity constraints are invariant, and the worst-pair TV is convex in the encoder, so this weakly reduces D_q for every q, without selecting q in advance. For the symmetric encoder let a_w and c_w be the conditional probabilities of the even weight w given b=0 and b=1, respectively. Words of a given weight satisfying the actual coordinate constraint are uniform. For any two indices g,h, words on which these coordinates agree contribute zero to pairwise TV. For a weight w>0, the fraction of b=0-compatible words with the other coordinate equal to one is w/(G-1); the fraction of b=1-compatible words with the other coordinate zero is (G-w)/(G-1). Counting both exchanged orientations cancels TV's factor one-half. Consequently,

    D_q = sum_{z,w>0 even} |q_0(z) A_w - q_1(z) C_w|,
    A_w=(1-p)a_w w/(G-1),
    C_w=p c_w (G-w)/(G-1).

Set A=sum A_w and C=sum C_w. Then 0<=A<=1-p and C>=B, since w<=G-1. The triangle inequality yields D_q>=sum_z |q_0(z)A-q_1(z)C|=C F_q(A/C). Thus t=A/C<=L, and the claimed replacement has D_q=B F_q(t)<=D_q(original) for every q. In that replacement only weight G-1 contributes to differences, so the lower expression is attained exactly. Both the reduction and its feasibility use odd G. For even G the all-zero/all-one encoder trivially achieves zero for all channels.

Optimization: terms with q_0(z)=0 are constants; all other terms equal q_0(z)|t-r_z| with r_z=q_1(z)/q_0(z). Any weighted median of the finite ratios, with weights q_0(z), clipped to [0,L], minimizes F_q. The lab evaluates all in-range breakpoints and endpoints instead of implementing a median sort. This is an elementary weighted absolute deviation problem; no novel median theorem is claimed.

The fully revealing cue has F(t)=1+t. A completely uninformative cue has F(t)=|1-t|. These recover #299's endpoints and generalize its one-bit conditional/pooled frontier to arbitrary p and odd G: for 0<=t<=min(1,L), the respective leakages are B(1+t) and B(1-t). For L<1 even an uninformative cue cannot permit zero leakage; the source bias exceeds (G-1)/G.

## 3. A falsifier for interpolation between endpoint optima

Take G=3, p=1/2, so B=1/4 and L=2. Consider the asymmetric binary cue q_0=(3/5,2/5), q_1=(1,0). It is neither perfectly revealing nor uninformative. The weighted median is 5/3, **beyond** the pooled optimum t=1. Its loss is F(t)=|3t/5-1|+2t/5. Thus the unique optimum has D=1/6, whereas t=1 has D=1/5. The optimum cannot be obtained by mixing the old full-information and no-information optimal encoders. A cue can sometimes warrant more dummy activation than a listener with no cue at all.

| t | Full cue TV | No cue TV | Asymmetric cue TV |
| ---: | ---: | ---: | ---: |
| 0 | 1/4 | 1/4 | 1/4 |
| 1/2 | 3/8 | 1/8 | 9/40 |
| 1 | 1/2 | 0 | 1/5 |
| 5/3 | 2/3 | 1/6 | 1/6 |

This does not violate data processing. For a fixed encoder, garbling the cue cannot increase worst-pair TV, as follows directly from applying the triangle inequality to the stochastic postprocessing. The minima obey the same order. What does not obey that order is the minimizing encoder's parameter. Here the asymmetric cue is a garbling of the revealing cue, and the uninformative cue is a garbling of the asymmetric one. Their optimal t values are 0, 5/3, 1: not monotone. The distinction between comparing optimal values and comparing optimizers is essential.

For a binary symmetric cue with crossover e in [0,1/2], the clipped optimum is min(L,e/(1-e)). This restricted family happens to interpolate monotonically; using it alone to validate a general design would conceal the asymmetric counterexample.

## 4. Theorem B: a universal minimax-regret compromise

Let the encoder be chosen before the observer channel is specified. Two different robust objectives are legitimate:

* Absolute worst leakage over all q is minimized by t=0, value B, since the fully revealing cue dominates all others by data processing.
* Regret relative to the best encoder for the realized channel is R_q(K)=D_q(K)-D_q*. The encoder may instead minimize its worst such regret.

The exact minimax-regret value is

    min_K sup_q R_q(K) = B min(1,L)/2,
    t_robust = min(1,L)/2.

The supremum is over all finite cue channels satisfying the conditional-independence model; there is no probability distribution over channels. By Theorem A it suffices to optimize t. Write m=min(1,L). The revealing and uninformative channels already give a lower bound Bm/2: for 0<=t<=m their regrets are Bt and B(m-t); for t>m the revealing channel alone exceeds the bound.

To establish attainment against every other channel, divide by B. The function F_q is 1-Lipschitz in t because sum q_0=1. If L<=1, the midpoint L/2 is within L/2 of every channel-specific optimum, giving the required upper bound. If L>=1, use t=1/2. For any comparator s in [0,1], the Lipschitz argument gives F(1/2)-F(s)<=1/2. For s>=1, the terms where q_0=0 cancel in the difference. Write r=q_1/q_0 for the rest; their weighted mean is at most one, since mass of q_1 outside the support of q_0 is nonnegative. For all r>=0,

    |1/2-r| - |s-r| <= (s-1/2)(2 min(r/s,1)-1).

This follows by splitting r at 1/2 and s. Average with weights q_0; the expected min(r/s,1) is at most 1/s. Hence

    F(1/2)-F(s) <= (s-1/2)(2/s-1)
                 = 5/2-s-1/s <= 1/2.

The final inequality is s+1/s>=2. Taking the best comparator proves the desired upper bound, and the two endpoint channels attain it. No assumption of symmetric hint noise is used.

The useful surprise: intermediate cues can force an individual optimum outside the endpoint range, but the midpoint of the endpoint optima remains minimax-regret optimal against the entire class. This is not because interpolation describes every optimum; it is because the worst potential regret admits a sharper bound than a naive distance-to-optimum argument.

For G=3 and p=1/2, absolute worst leakage is minimized at 25%, whereas the regret-optimal policy has absolute worst leakage 37.5% and worst regret 12.5 percentage points. These objectives are not interchangeable. If a privacy specification requires a hard upper limit, optimizing regret is not a substitute. Neither criterion has been established as the right policy for MHAC.

## 5. Negative memo, exaptation and artistic distinction

Do not add a generic noisy-metadata privacy layer based on these results. There is a crucial extra assumption beyond the issue's phrase “independent of the actual recipient given the bit”: the cue must also be conditionally independent of the emitted word. A fair random cue can be marginally independent of identity yet expose it in conjunction with the word. For example, take G=3 and b=1. A fair coin z chooses the clockwise or counterclockwise partner of g, and the encoder emits the weight-two word selecting g and that partner. If the coin is exposed as Z, each z marginal is fair for all g, but the pair (W,Z) identifies g exactly. The naive independent-cue formula predicts TV=1/2; actual TV is 1. The test oracle constructs all three disjoint transcript supports. This is a concrete boundary on the entire reduction and on any policy exaptation.

Other boundaries: the bit prior must be the same for each g and known to the policy designer; the finite cue mechanism is exogenous and encoder-independent; there is no repeated emission, adaptive observer, secret decoder, law hint cost, acoustic confusion, timing side channel, source confidentiality or differential privacy claim. If the encoder sees Z, the optimization problem changes. If arbitrary protected bits are correlated over time, neither marginal nor one-message bounds constitute transcript guarantees. Pairwise TV corresponds to a binary comparison with equal hypothesis odds, not a general multiclass guessing accuracy or measured human anonymity.

Proposed falsification contract for an agentic/audio interface: record the exact observer variables, their conditional independence assumptions, the protected distinction, the source prior, the optimization criterion (hard cap versus regret), and the cue-specific optimum used as a comparator. Test at least a fully revealing cue, no cue, a skewed cue, and a shared-coin counterexample. Fail the claim if the inferred guarantee survives a violated factorization assumption only by silently dropping the cue from the observer's view. No production action authorized.

**Artistic score (symbolic, not rendered or evaluated):** three instrumental parts; a low tone denotes zero, a high tone one. On bit one exactly two parts play high, including the intended part. On bit zero either all play low or only the intended part plays low. In a separate balcony line, let the cue sound a fifth or an octave with probabilities (3/5,2/5) when the source bit is zero, and always a fifth when it is one. Compare t=0, 1/2, 1, 5/3 in separate performances. This score implements a probability model on symbols; it does not imply listeners perceive parity, statistical independence or privacy.

**Fiction:** Three ushers heard the same bell. The balcony had been issued an inaccurate guide to the bell's language. The bellmaker optimized the instrument for the guide, and was surprised to discover that its optimal deceit was greater than that required when the balcony knew nothing. The archivist asked which error to minimize. The bellmaker replied that a better guide might still prefer a different bell. They filed separate specifications instead of agreeing on one word for safety.

## 6. Source and execution receipt

Source comparison, AI reading on 24 November 2026: Rassouli and Gündüz, *Optimal Utility-Privacy Trade-off with Total Variation Distance as a Privacy Measure*, arXiv:1801.02505, [HTML text](https://arxiv.org/abs/1801.02505), §I equations (1)–(2), §II equation (3) and §III Theorem 2. These passages define TV, distinguish average posterior-to-prior leakage, and present LP optimization for that measure. Our maximum pairwise TV is different; their Markov model and utility objectives are not ours. This report uses a direct special-case proof rather than borrowing their optimization theorem. Access: HTML text, targeted sections only, not whole paper or independent reproduction. Published-version metadata: IEEE TIFS 15, pp.594–603, DOI 10.1109/TIFS.2019.2903658 ([Essex repository metadata](https://repository.essex.ac.uk/24471/), search record visible, direct fetch failed). Blackwell, *Equivalent Comparisons of Experiments* (1953), DOI [10.1214/aoms/1177729032](https://doi.org/10.1214/aoms/1177729032), bibliographic/abstract discovery via [Celebratio Mathematica bibliography](https://celebratio.org/Blackwell_DH/article/255/), primary publisher returned only an iframe; no full-text reading claimed. It provides historical context for comparing experiments; the contraction argument used here is proved directly. No literature-wide originality review.

Run from repository root:

    node research/expeditions/hint-changes-listener/lab.js

Precommit execution of the exact source function in a V8 isolate passed the following bounded integer assertions. The optimizer uses rational breakpoints with integer cross-products; the separate direct-law oracle enumerates all valid words, and the asymmetric census enumerates six independent local probabilities. All bounded products fit within safe integer range. No floating-point tolerance is used.

| Activity | Count |
| --- | ---: |
| Finite channel/prior/group configurations | 26,688 |
| Midpoint regret bounds | 26,688 |
| Grid versus breakpoint comparisons | 1,307,712 |
| Asymmetric policy/view comparisons (G=3) | 78,125 |
| Symmetric weight-law direct comparisons (G=3,5,7) | 1,220 |
| Universal dominance comparisons | 1,220 |
| Named negative controls | 3 |
| Malformed input refusals | 5 |

Counts overlap, not independent experiments. The channel census uses all distributions with six mass units over one, two or three symbols, G in {3,5,7,9}, p in {1/8,...,1}. The asymmetric census uses a fair bit and all 5^6 choices of probability assignments on four mass units, evaluated across five specified views. The proof covers arbitrary finite channels in the mathematical domain; the census qualifies a bounded implementation, not scientific novelty or empirical utility. One AI authored and checked both proof and code. Full repository CI and substantive review remain acceptance gates. Keep draft; no central records, frozen methods or other branches altered.

The recovered disagreement is not that one observer is objectively better than another. It is that an ordering of information, an ordering of optimized leakage values, and an ordering of the policies that attain those values are different objects. The first can imply the second without implying the third.
