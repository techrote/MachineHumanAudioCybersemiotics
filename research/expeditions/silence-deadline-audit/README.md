# The Silence That Cannot Be Audited at One Deadline

Refs #715; 26 November 2026. Exploratory mathematics and synthetic communication design, outside frozen Tracks E/G. One ChatGPT agent; no human testing, independent critique or production security certification. Base 495a98ca12bae467a507031f04931aa4254b1866. Predecessor #711 / #712 pinned faacc4e9017dc9222b8757187ac4aff3c6c2bfdc; exact-head CI 45870748461 completed successfully. No dependency on merging that branch.

## A clock is not a single threshold

A completion time T is distributed as A or B depending on a binary withheld label. The release controller knows the label and actual T, and can randomize after completion. It must emit an identical waveform at L with T <= L <= T+M. The observer sees L, not the internal controller, and no other side channel. Let U,V be the conditional laws of L. Our objective is minimum total variation TV(U,V), equivalently the residual advantage of the optimal equal-label-prior timing classifier (accuracy (1+TV)/2). This is not a general information-security model, nor a prescription to delay urgent notifications.

Previous #711 obtained exact equalization and a sharp four-tick cap for a sequential test. What if the system cannot afford that cap, or must trade expected latency against residual disclosure? The answer is a partial transportation problem, not a full quantile coupling.

## Exact causal partial matching theorem

For finite discrete time laws A=(a_i), B=(b_j) at sorted completion times x_i,y_j, a partial coupling gamma is a nonnegative matrix with row sums <= a_i and column sums <= b_j. Its allowed edges satisfy |x_i-y_j|<=M. Let m be its largest achievable total mass. Then

    inf TV(U,V) = 1-m
                = max over subsets S of A's support [A(S)-B(N_M(S))],

where N_M(S) consists of B's support points within distance M of at least one member of S. Empty S ensures the maximum is nonnegative.

Proof of attainability: for each matched piece gamma_ij, emit at max(x_i,y_j) on both branches. For a realized x_i, select j with probability gamma_ij/a_i, otherwise release immediately; analogously for y_j. This is a genuine post-completion randomized policy, not an instruction to know the other episode's actual time. Every matched piece respects the cap. The resulting release laws overlap by at least m, hence TV<=1-m.

Proof of necessity: for any two feasible release kernels, take their common output mass min(U(l),V(l)) at each l. Conditional on this shared release time, couple the two original completion-time distributions (their conditional joint input/output masses normalized at l). Summing these couplings yields a partial coupling with mass 1-TV(U,V). Each paired input lies in [l-M,l], hence the edge is permitted. Thus TV>=1-m. This also proves that the constructed policy cannot accidentally exceed the optimal overlap.

The subset expression follows by a source-to-A-to-B-to-sink flow network: source capacities a_i, sink capacities b_j, permitted middle edges of effectively infinite capacity (greater than 1). Any minimal cut can be represented by A subset S and its neighboring B vertices on the source side; cut capacity 1-A(S)+B(N_M(S)). Max-flow/min-cut then yields the formula. Koperberg's Proposition 6 (see sources) directly supplies the same coupling-with-deficiency formula. The scoped result here is its exact realization by nonnegative causal release delays.

**Linear scan compiler.** Ignore zero masses. Inspect the earliest remaining x,y. If x+M<y, discard remaining mass at x from matching (it can never be matched with any later y). Symmetrically if y+M<x. Otherwise match as much of the two masses as possible and continue. To see optimality, start with a maximal partial matching. If both earliest vertices match later partners, exchange an equal amount of edges (x,y') and (x',y) for (x,y) and (x',y'). Because x<=x', y<=y', and the original edges are feasible, both replacements satisfy the cap. If one earliest vertex is unmatched, transfer mass from the other's later match; if both are unmatched, add their common mass. Repeat until the earliest pair is saturated or exhausted. This preserves or increases matched mass, and induction on exhausted vertices proves the greedy rule. Complexity O(n+m) for sorted supports (here n,m are support counts). The executable uses integer inventories for exact tests.

## A mean-delay budget is a transportation cost

Let alpha in [0,1] be the population weight of the A branch (not necessarily the underlying state prior). The expected added delay is alpha E[L-T|A]+(1-alpha) E[L-T|B]. Each unit of matched mass between x,y costs at least

    c(x,y) = alpha max(y-x,0) + (1-alpha) max(x-y,0).

Release at max(x,y) attains this bound; release unmatched mass immediately. The optimal residual TV at expected added-delay budget d is exactly 1 minus the maximum mass of a partial coupling with allowed edges, row/column bounds and sum gamma_ij c(x_i,y_j)<=d.

Proof: the preceding shared-release construction gives a partial coupling from every feasible policy; any common l costs at least c(x,y), and unmatched delays are nonnegative. Conversely the matched-pair release construction spends exactly the stated cost and realizes at least the selected overlap. Both bounds prove equality. Finite linear programming yields a continuous piecewise-linear nonincreasing convex frontier as a function of the budget (or the constant zero-cost case); it need not coincide with the hard-cap greedy solution. Example A equally weighted at 0,10, B at 1,14, cap 4 and alpha=1/2. Only two edges are feasible, with unit costs 1/2 and 2. The maximum matched mass is 2d for 0<=d<=1/4, then 1/2+(d-1/4)/2 until d=5/4, then 1. Thus residual TV has a kink at d=1/4. Even with the same max delay, different average costs change which distinctions can be concealed.

## The exact partial repair of the sequential bell

Revisit #711's +1/-3 exit boundaries, w=p(1-p), 0<p<1. The conditional duration laws A (near) and B (far) are independent of the true state given endpoint. In ticks 1+2k:

    A_0=(1-2w)/(1-w), B_0=0;
    B_k=(1-2w)(2w)^(k-1), A_k=w B_k/(1-w) for k>=1.

These formulas come from the two-step killed walk's rank-one transition matrix (see predecessor). They sum to one and all other tick masses vanish. The optimal remaining TV, allowing adaptive delay on either branch, is

    M=0,1: (1-2w)/(1-w)
    M=2,3: w(1-2w)/(1-w)
    M>=4: 0.

For M<=1 only equal odd completion times can be paired, so raw TV cannot improve. Immediate release realizes it. For M=2 or 3 the early A mass at 1 can only overlap B's completion mass at 3, giving lower bound A_0-B_1. Delaying all A times by exactly 2 and leaving B unchanged realizes this bound: at tick 3 the shifted A mass exceeds B; for all later ticks shifted A/B = 1/[2(1-w)]<1. For M>=4 use the adaptive #711 kernel: near at tick 1 delay 2 with probability 1-w else 4; near later delay 2 with probability 1-2w else 4. Far is unchanged. Substitution in the above geometric masses proves equality for every tick, not just a truncation. The finite laboratory verifies the coefficient identities for rational test parameters.

For p=3/4, w=3/16, the residual endpoint-TV sequence is 10/13, 15/104, 0. The state posterior endpoint mixture weights differ by 13/20, so residual state-TV is 13/20 times the endpoint-TV. Under equal state priors, optimal state classification by release time falls from 75% to 54.6875% to 50%. The intermediate two-tick policy sacrifices much less worst-case time than the four-tick perfect policy, while removing most of the timing advantage. These are exact population calculations, not timing measurements or human results.

## When deadline and quantile audits fail

**Alternating comb.** For any integer n>=1 and cap M>=0, let A be uniform on times 2j(M+1) and B uniform on (2j+1)(M+1), j=0,...,n-1. Every cross pair is farther apart than M, so even optimal causal release leaves TV=1. Yet the two unpadded CDFs differ at every deadline by at most 1/n, since their steps interleave. The shifted one-sided CDF deficits max_t [F_A(t)-F_B(t+M)] and reverse are also at most 1/n. Thus an observer restricted to a single deadline threshold has optimal equal-prior accuracy only (1+1/n)/2, while a union-of-windows observer distinguishes perfectly. The same small single-threshold gap holds for immediate release (a feasible policy). This is not a contradiction to the exact equalization CDF criterion: zero deficit suffices for perfect matching, but small positive deficit does not control TV uniformly. A union of separated windows can add many individually small deficits.

**Quantile is not a partial matching algorithm.** A uniform on {0,2}, B uniform on {2,3}, M=0. Pairing equal quantiles matches no mass; the actual common atom at 2 matches half. Quantile coupling remains suitable for exact full equalization when feasible; optimizing the probability of equality under a cap is a different objective.

**The controller's knowledge matters.** Both release policies are label-aware. Requiring a single kernel for both labels, or requiring delay to be independent of completion, is a stricter problem. This result does not authorize treating a secretly unavailable label as a control input. If time itself is intended to carry urgency, equalization destroys desired information. If an observer obtains the final withheld label, classification from the combined observation is not reduced to chance. Correlated episodes, observable controller activity and unknown time laws invalidate the stated guarantee.

## Source ledger and qualification

- Twan Koperberg, *Couplings and Matchings: Combinatorial Notes on Strassen's Theorem*, arXiv:2202.02092v1 (4 February 2022), https://arxiv.org/abs/2202.02092. Original PDF read at pp. 1–3 and 7–9: Theorem 1, Hall condition, Propositions 5–6 and deficiency proof. Page images pp. 2,7,8 inspected. Established ancestry for the subset formula; not claimed as a new theorem of coupling theory.
- Zachary Ratliff and Salil Vadhan, *A Framework for Differential Privacy Against Timing Attacks*, CCS 2024, arXiv v2 dated 24 November 2024, https://arxiv.org/html/2409.05623v2. Read abstract, introduction and Section 1.1 Definitions 1–4 and discussion through Section 1.2. They distinguish output-conditional and joint timing privacy and discuss random delays and the cost of constant runtime. Our fixed pair of conditional completion laws and TV objective are narrower; no differential-privacy result for neighboring datasets or physical implementation follows.
- Internal predecessor #711, full relevant timing derivation at pinned #712 (above). Its exact CDF equality result is recovered at m=1; the present partial optimization and countercontrols are additive.

The standalone JavaScript laboratory was executed in V8. It compared greedy matching with every subset deficiency on all ordered pairs of 126 five-unit, five-bin inventories at caps 0–4 (79,380 profiles, 2,540,160 subset evaluations). A separately structured exhaustive literal-release oracle on three-unit, four-bin inventories and caps 0–2 checked integer mean-delay budget frontiers against partial-matching enumeration (1,200 profiles, 317,600 ordered release assignment pairs). It tested 160 alternating comb controls and 4,560 exact geometric coefficient cases. An initial test harness had incorrect scaling when clearing rational denominators; replaced by direct rational multiplication/addition before successful execution. Final execution receipt is execution.json; run with node laboratory.cjs. Integer inventory tests are finite cross-checks, not the proof for arbitrary real weights. No second independent agent or human reviewer. Repository-wide validation pending exact-head CI and integrator review.

Interpretation: a deadline is a question about a prefix of time; a timing observer may ask about a disconnected collection of intervals. The acoustics are secondary to the observation contract. A proposed Observatory inspector could expose full timing TV, the best hard-cap release kernel, the subset witness explaining residual leakage and the expected-delay frontier separately. This is a design hypothesis only. The mathematical substance follows from coupling, transport and the predecessor random walk; no extra explanatory contribution from cybersemiotics is established.

Fiction: a clerk examined the silence before noon, then the silence before one. Each comparison seemed harmless. The apprentice stopped looking at a single deadline and drew a comb over the clock face. Every tooth caught the same answer.

### Native cross-check and acoustic score

Run python witness.py with NumPy/SciPy (qualified here using Python 3.13.5, SciPy 1.17.0). One LP uses literal release variables indexed by branch, input tick and output tick, enforces exact input marginals and a separate common output mass variable at each tick. The other LP uses partial transport variables and the weighted cost formula. Across 480 paired LP cases, including branch weights 0 and 1, their optimal overlaps differed by at most 2.3314683517128287e-15. Two native executions produced identical native-execution.json and WAV SHA-256s. The committed native source and receipt blob IDs matched the locally executed bytes. Committed JS source was independently retrieved and replayed in V8, exactly reproducing execution.json. Both formulations are the work of the same agent.

The original score **The Comb Organ** has twelve episodes per class; completion ticks alternate between A={0,4,...,44} and B={2,6,...,46}. A deterministic test inventory adds zero or one tick on alternating episodes in each shuffled class. Each episode contains the same tapered 500 Hz onset on the left and answer pulse on the right, 10 ms per tick plus a common 20 ms offset. A 520 ms fixed frame prevents inter-episode ambiguity. The renderer writes 6.24-second stereo PCM16 WAV files and decodes all 24 answer times directly from the integer samples. The decoded class supports are disjoint while the largest empirical CDF gap is 1/12. The files are deterministic score specimens, not independent empirical trials or claims about human perception. Generate them locally from the source; the JSON preserves hashes and exact decoded tick inventories. No binaries or dependencies are added to the canonical project.
