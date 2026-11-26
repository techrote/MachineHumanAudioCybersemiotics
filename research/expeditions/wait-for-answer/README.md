# The Bell That Must Wait for Its Own Answer

Refs #711 · 26 November 2026. Exploratory proof and synthetic acoustic design, not a canonical empirical finding or a deployed privacy mechanism. One ChatGPT research agent; no independent human critique.

## Contents

- [The silent report](#the-silent-report) — timing alone can reveal a withheld decision.
- [A published conjecture and a path proof](#a-published-conjecture-and-a-path-proof) — why a drift swap cannot change an endpoint-conditioned path law.
- [The optimal waiting law](#the-optimal-waiting-law) — an exact independent extra walk and a minimal-delay theorem.
- [A sharp four-tick mechanism](#a-sharp-four-tick-mechanism) — bounded adaptive delays succeed where bounded independent jitter fails.
- [Acoustic transfer and negative sediment](#acoustic-transfer-and-negative-sediment) — what the experiment does and does not hide.
- [Sources and qualification](#sources-and-qualification) — provenance, tests and disposition.

## The silent report

A machine observes iid binary samples. The persistent state X is + or -. Under X=+ the probability of an upward observation is p, with 1/2<p<1; under X=- it is q=1-p. Let S_t be the sum of unit signed observations, starting at zero. Stop at T, the first hit of +a or -b for positive integers a,b. Let Y be the exit endpoint. It is an exact-threshold sequential likelihood-ratio test, not a test with overshoot. Assume a<=b without loss of generality (reflect and relabel otherwise). Set R=p/q. The likelihood ratio of any finite stopped path is R^(S_T), because the net number of upward minus downward steps is S_T. Thus the complete stopped path, including T, is conditionally independent of X given Y: the likelihood ratio is constant within each endpoint class. Both endpoints have positive probability, and the stop is almost surely finite with finite mean (a run of a+b upward steps suffices to absorb from any interior point, and has positive probability in every block).

Let h_+,h_- be the probabilities of the near exit +a under the two states. In the shifted interval [0,N], N=a+b, the start is b. For right-step probability v and r=(1-v)/v, the upper exit probability is h(i)=(1-r^i)/(1-r^N), with fair limit i/N, by solving the harmonic second-order recurrence. Since R^a>1, h_+>h_-. Let A and B be the conditional duration laws for the near and far endpoints. Neither depends on the true state. The timing-only laws are h_+ A+(1-h_+) B and h_- A+(1-h_-) B. Therefore

    TV(T|+,T|-) = (h_+-h_-) TV(A,B).

At equal state prior, optimal binary classification accuracy from an observation with two conditional laws is (1+TV)/2, by pointwise maximization. If a,b have opposite parity, T mod 2 identifies Y exactly: each step flips parity and the two endpoint parities differ. A,B have disjoint support; timing alone is Blackwell-equivalent to the final answer, since the answer also generates the timing through a state-independent randomization. This is despite a deliberately identical emitted tone. For a=b, reflection of the walk and drift-swap symmetry give A=B; raw T discloses no state information. For unequal same-parity barriers, T=a is possible at the near exit but impossible at the far exit; overlap occurs at T=b by inserting pairs of interior steps before the near exit. Thus the timing leakage is strictly positive but less than the endpoint leakage.

Example at p=3/4, a=1,b=2: h_+=12/13, h_-=4/13, timing-only and explicit answer accuracy both 21/26. No frequency or waveform variation is required for this timing channel. Symmetric a=b is a genuine negative control, not a general assertion that stopped decisions never leak through latency.

## A published conjecture and a path proof

Lorek and Markowski, *Conditional Gambler’s Ruin Problem with Arbitrary Winning and Losing Probabilities with Applications*, Methodology and Computing in Applied Probability 27:54 (2025), DOI https://doi.org/10.1007/s11009-025-10181-7, Section 2.1, Theorem 2.8 and Conjecture 2.9, distinguish a proved expectation symmetry from a conjectured distribution symmetry under swapping p(i),q(i) with q(i)/p(i)=r constant. The older arXiv text numbers the conjecture 2.8. The published HTML was retrieved and the actual statement inspected.

Here is a direct proof, stronger at the path level. In their finite birth-death chain with holding, compare a chain with upward p(i), downward q(i), holding 1-p(i)-q(i) to the swapped chain. Along any fixed positive-probability finite path from i to j, let U,D,H be counts of upward, downward and holding moves. The original-to-swapped path probability ratio is

    (1/r)^U r^D = r^(i-j),

because holding factors are identical and U-D=j-i. This is independent of duration, intermediate positions and holding times. On paths first absorbed at N, the ratio is r^(i-N); on paths first absorbed at zero, it is r^i. Both chains absorb almost surely by a uniform finite-state positive block probability. Summing over each endpoint class gives the same ratio for the corresponding total exit probabilities. Dividing cancels it. The entire conditional stopped-path law, not only its time marginal or expectation, is therefore unchanged by swapping the rates. This proves the statement in Conjecture 2.9 under its declared assumptions.

**Priority correction:** a Polish University of Wrocław seminar announcement dated 10 January 2019 explicitly states that the conditional duration distribution symmetry will be demonstrated using Mao and Zhang (2016). Hence this expedition does not assert that the conjecture was previously unsolved or that the result is novel. The announcement is evidence of prior awareness, not access to the seminar proof. The short path argument above is a self-contained reconstruction and a useful source-level discrepancy: the 2025 publication still presents the distribution result as a conjecture. No correspondence, erratum or author validation was sought.

Negative control: on [0,3] start at 1 with (p(1),q(1))=(1/2,1/4), (p(2),q(2))=(1/4,1/2). The upper-absorption masses at times 2 and 4 are 1/8,7/128 before swapping and 1/8,1/32 after swapping. Their ratio is not constant, so normalization cannot yield equal conditional time laws. Constant drift ratio matters. More generally, a positive likelihood ratio on each directed edge of the form g(destination)/g(source) telescopes along a path, explaining the relation to Doob transforms and endpoint sufficiency. That is a sufficient geometric criterion; equality of time marginals alone is not a converse.

## The optimal waiting law

**Strong Markov factorization.** In [0,N], the near duration A is the law of the time from b to N conditioned on reaching N before zero. By reflecting the original walk, then using drift-swap conditional symmetry, the far duration B is the time from a to N under the same upper-success conditioning. Every such successful path from a must first reach b. Conditioned on eventual upper success, the initial segment from a to b is distributed as the walk in [0,b] started at a and conditioned to reach b before zero; the remainder is independent and has law A. Indeed at the intermediate hit b the conditional probability of subsequent success is a constant h(b), independent of the prefix. Consequently

    B = A * D

as a convolution of laws, where D is that smaller conditioned first-passage duration (D=0 if a=b). The law of D is the same for p and q, so the padding device need not know X. The near endpoint can be released after an independent draw of D; release the far endpoint immediately. The resulting release time L has law B conditional on either endpoint and either state, and thus L is independent of X and Y. The original answer, if released at L, is unchanged. No future machine observations need be acquired for the padding: a separate simulated conditional walk or equivalent sampler suffices. Internal timing and other observables must remain outside the stipulated observation channel.

**Optimality, more generally.** For arbitrary discrete nonnegative conditional times A,B with finite means, suppose a causal release policy can see the realized stop time and endpoint and use independent randomization, but may never release before the stop. If its final time distribution is common to both endpoints, its CDF G satisfies G(t)<=min(F_A(t),F_B(t)). The pointwise minimum of the two CDFs is itself a CDF. It is attainable by quantile coupling: on an observed discrete time t, draw U uniformly in (F(t-1),F(t)] using the appropriate conditional CDF F, and release at the generalized inverse of G at U. U is uniform conditional on the endpoint and the release is no earlier than the observed t. This is a post-stop randomized mapping, not clairvoyant coupling of actual observations. The pointwise largest feasible G gives the stochastically earliest common law and minimizes its expected time, for every prior and for each state separately. Here B stochastically dominates A by the convolution, so G=F_B is optimal and the independent-D policy attains it. Any finite bounded-delay policy with common release law must additionally satisfy max(F_A(t-M),F_B(t-M))<=G(t), where M is the allowed added delay. Conversely the quantile coupling attains a bound M if these inequalities hold for the largest feasible G. This is an exact CDF feasibility criterion, not just a bound on the mean.

For the informative binary state p>1/2, state-only release-time independence also implies endpoint independence: if release conditional on Y is state-independent (as it is for any state-blind policy using the stopped path and independent randomness), subtract the two mixtures, using h_+!=h_-. At p=1/2, state privacy is automatic without padding; endpoint independence is a strictly stronger contract.

**Exact cost.** Let kappa=|log(p/q)|/2. For a<b, the conditional expected padding is

    E D = [b coth(b kappa)-a coth(a kappa)] / tanh(kappa).

The limit at p=1/2 is (b^2-a^2)/3. For completeness, the unnormalized generating function f_i(z) of the upper-hit time on [0,N] solves f_i=z(p f_(i+1)+q f_(i-1)), with f_0=0,f_N=1. The two characteristic roots are sqrt(q/p) exp(+/- k(z)), where cosh k(z)=1/(2z sqrt(pq)). Hence f_i(z)=(q/p)^((i-N)/2) sinh(i k(z))/sinh(N k(z)). Normalize by f_i(1) and differentiate at z=1; k'(1)=-coth(kappa). The fair limit follows from coth x=1/x+x/3+O(x^3). This also agrees with Lorek and Markowski's classical conditional-duration formulas, Corollary 2.13 in the publisher's Section 2.3. Its displayed winning-probability formula appears to interchange the r=1 and r!=1 labels; the conditional-time formula used here is independently derived. The expected added delay across episodes equals the near-exit probability times E D. No independent-sample count or urgency guarantee follows merely from this average.

## A sharp four-tick mechanism

Choose a=1,b=3, 0<p<1, and w=p(1-p). Both conditional durations are odd. The exact survival probabilities for integer k>=0 are

    P(A>1+2k) = [w/(1-w)] (2w)^k,
    P(B>1+2k) = (2w)^k.

One derivation: on [0,4], start 3 for A and 1 for the reflected B; after each two steps the only surviving odd interior positions are 1 and 3. The killed two-step transition matrix on these positions has rows (w,p^2) and (q^2,w), rank one and nonzero eigenvalue 2w. The initial near absorption has conditional mass (1-2w)/(1-w), while the earliest far absorption (time 3) has mass 1-2w. These determine the displayed tails, or use the direct finite recurrence. In particular A and B overlap but differ.

The independent extra walk D from 1 to 3 conditioned on upper success has law 2+2K with K geometric on {0,1,...}, P(K=k)=(1-w)w^k. It is unbounded. However, a state-blind, outcome- and time-dependent delay can exactly hide the difference using ONLY 2 or 4 extra ticks on the near branch. Leave the far branch unchanged:

| Observed near stop | Add 2 ticks | Add 4 ticks |
| --- | ---: | ---: |
| T=1 | 1-w | w |
| T>=3 | 1-2w | 2w |

This is the quantile coupling specialized to the displayed tails. Alternatively substitute the geometric masses and verify each output coefficient equals B. At output time 3 the mass is (1-2w); at time 5 it is near_mass(1)*w + near_mass(3)*(1-2w)= (1-2w)*2w, and the remaining masses follow the same ratio 2w. It attains the mean optimum from the previous theorem, with a hard additional-delay cap of four.

**Sharpness:** if M<=3, the near mass released by tick 4 is at least P(A<=1)=(1-2w)/(1-w), which strictly exceeds P(B<=4)=1-2w; the far branch cannot be released earlier than its stop. No common release distribution exists, even if both branches are delayed. Four is therefore the minimum hard cap for all 0<p<1 under endpoint independence. The case p=1/2 requires no padding for state independence alone.

**Bounded independent padding is impossible** for this pair, even allowing different independent delay laws on the two endpoints. If P(z),Q(z) are their finite nonnegative-coefficient probability polynomials, equality of the release laws and convolution imply P(z)=Q(z) z^2(1-w)/(1-w z^2) on 0<z<1. Multiply through and use polynomial identity. At z=1/sqrt(w)>0 the left vanishes while the right is positive: contradiction. In fact common outcome-blind independent additive jitter of any distribution cannot equalize two different time laws, since its PGF is positive on (0,1) and cancels. Dependence on elapsed time is a resource, not a nuisance, here.

Worked example p=3/4, a=1,b=3:

| Quantity | Exact value |
| --- | ---: |
| Near exit probability under state + | 39/40 |
| Near exit probability under state - | 13/40 |
| Answer classification accuracy, equal prior | 33/40 |
| Raw timing-only accuracy, equal prior | 3/4 |
| Padded timing-only accuracy, equal prior | 1/2 |
| Mean near raw stop | 113/65 ticks |
| Mean far raw stop | 21/5 ticks |
| Mean extra delay given near exit | 32/13 ticks |
| Mean extra delay across equal-prior episodes | 8/5 ticks |
| Original mean across equal-prior episodes | 13/5 ticks |
| Mean common release time | 21/5 ticks |
| Optimal hard added-delay cap | 4 ticks |

The conditional timing TV equals A's time-1 mass 10/13 because the conditional tail after time 1 has precisely the B law. Multiplying by h_+-h_-=13/20 gives state timing TV 1/2. Both the answer's conditional error rates and optimal decision value are unchanged if it is eventually delivered. This does not claim unchanged utility when the receiver's utility depends on delivery time.

## Acoustic transfer and negative sediment

The proposed MHAC use is to treat silence duration as a separate semantic field rather than assuming identical tone identities imply identical messages. Sometimes timing is intentional urgency; sometimes it is an accidental disclosure of a withheld diagnostic conclusion. An audio renderer can have an explicit contract for which observation is permitted: final symbol, onset, onset plus symbol, pre-release progress sounds, or a deadline receipt. The timing equalizer above hides only release time in the stated model and must not suppress useful urgency or delay safety-critical notifications. It may add cost and could change the decision task. Use explicit event identity and deadlines; retain original decision-time metadata on authorized internal logs if needed, not on the hidden public channel. Fixed-rate transmission or a fixed known processing deadline may be simpler when applicable; the exact stopped-time distribution here is unbounded, so a finite absolute deadline cannot promise delivery of every answer. A cap on *added* delay is different.

Synthetic digital score: witness.py generates four stereo PCM16 WAVs at 8 kHz, 32 episodes each, with a left start pulse and identical right 600 Hz answer pulse at the chosen tick (40 ms per tick). The file label denotes the exit endpoint, not the hidden state. Each conditional score uses 32 equally spaced midpoint quantiles, ordered for inspection. The paired scores use the same quantiles deliberately, not independently sampled trials. Padded near and far files are byte-identical to the raw far file; the four-tick added-delay cap is checked across all constructed episodes. The exact population claims follow from the proofs, not from the finite rendered score or coincident hashes. Actual PCM onset decoding recovered all 128 episodes. No claim of human perceptual concealment, natural meaning, secure implementation, empirical machine latency, or hearing benefit. Other output parameters, logs, active interrogation, correlated episodes, overshoot, changing thresholds or states, state-dependent timing mechanisms and arbitrary adversarial access fall outside the theorem. Direct logging of actual onset/endpoint joint laws is the simple measurement baseline.

Interpretation: the raw sequence can already be a sign even before its final tone. A terminal message can be sufficient about truth while its production timing remains meaningful to someone who cannot see the terminal message. These are statistical distinctions; nothing demonstrates that cybersemiotics adds explanatory power beyond standard likelihood ratios, conditional probability and stochastic order. A playable installation could contrast a release pulse with an internally generated decision pulse (a separate audible channel only in demonstration mode), exposing the cost of concealing an answer that has already been reached. No real-time implementation is claimed.

Fiction: two clerks use the same bell. One waits until the verdict can be made public. The other waits until the waiting itself cannot give the verdict away.

## Sources and qualification

Read by the same research agent on 26 November 2026; selected passages only, not exhaustive literature or novelty searches.

- Meik Dörpinghaus, Édgar Roldán, Izaak Neri, Heinrich Meyr, Frank Jülicher, [An Information Theoretic Analysis of Sequential Decision-Making](https://arxiv.org/abs/1510.08952), 2015 preprint: HTML introduction, Section II model and Section III-B equations (31)-(40) retrieved, and conclusion inspected. Establishes symmetric exact-threshold duration independence and related information-density results. The present asymmetric timing-only and optimal padding arguments are our own scoped derivations. No claim that all sequential tests have no timing leakage.
- Paweł Lorek and Piotr Markowski, [Conditional Gambler’s Ruin Problem with Arbitrary Winning and Losing Probabilities with Applications](https://doi.org/10.1007/s11009-025-10181-7), published 26 June 2025, 27:54. Publisher full-text HTML read selectively: introduction, Section 2 chain model, Theorem 2.3 equations (5)-(6), Theorem 2.8 and Conjecture 2.9 in Section 2.1, classical formulas in Section 2.3. Older [arXiv:1812.00687](https://arxiv.org/abs/1812.00687) Sections 1, 2.1 and 2.3 inspected (Conjecture 2.8 in that version). The direct path proof above addresses exactly the published constant-ratio condition. The known first-passage theory and conditional mean are credited, not claimed original.
- University of Wrocław [probability seminar archive](https://zamawiane.math.uni.wroc.pl/seminarium/teoria-prawdopodobienstwa-i-modelowanie-stochastyczne), entry dated 10 January 2019, Paweł Lorek, Polish title on conditional gambler's ruin. Retrieved announcement read; it states a distribution-symmetry demonstration using Mao and Zhang. No seminar slides or proof retrieved. This prevents interpreting the later conjecture label as evidence of an open research problem.
- Yong-Hua Mao and Chi Zhang, [Hitting Time Distributions for Birth–Death Processes with Bilateral Absorbing Boundaries](https://doi.org/10.1017/S0269964816000280), published online 2016, journal 31(3), 345–356 (2017). Publisher abstract and metadata inspected, full proof not read. Discovery/ancestry lead only; not a premise for our elementary derivation.
- Yoav Ben Dov, Liron David, Moni Naor and Elad Tzalik, [Resistance to Timing Attacks for Sampling and Privacy Preserving Schemes](https://doi.org/10.4230/LIPIcs.FORC.2023.11), FORC 2023: abstract and metadata inspected; broader time-oblivious sampling problem, not a source for the sharp four-tick result. [Ratliff and Vadhan](https://arxiv.org/abs/2409.05623) abstract inspected for distinct runtime/output privacy notions; no differential-privacy certification attempted.
- Internal #682 full draft report read, issue body and empty comments inspected: concerns first-alert workload under matched snapshots, not timing privacy. #670 issue and checkpoint read as related temporal-observation context, not a mathematical dependency. No upstream draft merged or modified.

Run node laboratory.cjs (standard JS BigInt; executed in V8 code mode) and python witness.py (Python 3.13.5 standard library). The first uses exact rational forward recursion with variable holding and movement rates; the second uses integer weighted path counts and the explicit adaptive kernel rather than the CDF transport formula. The first execution receipt records 61,207 assertions, 108 homogeneous profiles, 4,428 convolution coefficients, 11,070 inhomogeneous drift-swap coefficients, 779 bounded-CDF checks, 703 positive transport cells; exact finite prefixes through time 40. The independent formulation in Python checks 39 rational biases, 2,418 explicit kernel/cap identities through time 60 and 128 decoded PCM episodes. Both native executions reproduced receipts and WAV hashes. Committed JS readback was replayed with identical receipt. Python source and receipt Git blobs 17297e63b627cdee24c111d41e7e21a1c863baf8 and 7d02395118c2e23545204159452af43050789334 match the locally executed bytes. No truncation is treated as proof of infinite-time equality; the analytical proof supplies that. Same agent, different formulations, not independent peer review. WAV files are regenerable locally and are not committed.

Reconciliation: default main exact base 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, README, programme, runbook, integrity, validation, protocol overview and project foundations; nested research/AGENTS and research/expeditions/AGENTS not found. Traversed 416 branch entries (including terminal empty page), 60 recent open issue results, 35 recent actual open PRs and targeted stopping-time/first-passage/timing-leakage/ancillary/optional-stopping searches. Previous PR #708 exact-head workflow 45862888841 completed success. New #711 body and empty comments read back. Native git ls-remote failed DNS; full repository checkout and local full suite unavailable. All work on fresh issue-scoped branch, five additive files only. No canonical manifests, protocol changes, other workers' branches, participant evidence or human gates altered. Draft/Refs pending substantive review and designated integrator; exact-head repository check separately required.
