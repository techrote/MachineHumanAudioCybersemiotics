# The Ruler That Changes Its Winner

**Refs #244 · 2026-11-24 · mathematical reconstruction, bounded synthetic census, original audio, design conjecture and fiction.** No Track E/G admission, human experiment, psychophysical claim or priority claim.

## The anomaly

Two perfectly honest experts submit complete rankings: B>A>C and C>A>B. A is the compromise everyone places second; B and C each have one first place. Plurality chooses B or C; veto chooses A. There is no missing ballot, no mistaken rank, no inconsistent scalar equation, and no need to attribute disagreement to emotion. What is missing is the convention by which rank positions acquire cardinal value.

Suppose an operator must choose an alternative before learning that convention. A single choice necessarily incurs a worst-case regret of one point. A lottery choosing A or B with equal probability reduces the worst-case *expected* regret to half a point, but only if the scoring convention is fixed independently of the realized draw.

This is a different problem from #228, which fits pairwise numerical margins into an additive potential. Here every ballot is a strict total order and every specified scoring rule is well defined. #220 concerns calibrated probability pooling; #236 concerns statistical experiments and changing decision tasks; #242 concerns incentives and strategic reports. Here reporting is assumed truthful, the rank evidence is complete and the policy family is the uncertainty. In #184's language this is a further candidate exaptation of anti-collapse: a ranking of preferences is not itself a common cardinal scoring convention.

## Source and authority boundary

- Paolo Viappiani, *Robust Winner Determination in Positional Scoring Rules with Uncertain Weights*, Theory and Decision 88 (2020), 323–367, online 27 November 2019, [publisher DOI and abstract](https://doi.org/10.1007/s11238-019-09734-3). The publisher full text is subscription-gated; an [author-shared full-text rendering](https://www.researchgate.net/publication/337137282_Robust_Winner_Determination_in_Positional_Scoring_Rules_with_Uncertain_Weights) was accessible. Inspected §2.2 Definition 1 and Eq. 2 (cumulative ranks and differential weights), §3.1 Observation 1 (a minimax winner need not be a possible scoring winner), §3.2 Lemma 1 and Theorem 1 (exact maximum regret over decreasing normalized weights), §3.3 Theorem 2 and §3.4 opening (restricted weight families). Printed layout in the author-shared rendering has its own pagination; section/equation locators are used instead. Not a complete article reading; no claim that mixed decisions or the sharp ratio below are absent from the broader literature.
- S. S. Stevens, *On the Theory of Scales of Measurement*, Science 103 (1946), 677–680, [DOI](https://doi.org/10.1126/science.103.2684.677). Bibliographic identity checked via [PubMed](https://pubmed.ncbi.nlm.nih.gov/17750512/); original article not read in full. For the interpretation of ordinal representation, inspected [Measurement in Science, Stanford Encyclopedia of Philosophy, §3.2](https://plato.sydney.edu.au/entries/measurement-science/#ClaSca) (secondary overview). Ordinal scales preserve order under increasing transformation; the scoring functions below add a specified convention. This is a measurement-theory analogy, not a claim that Stevens proposed this voting model.

The established deterministic result is explicitly reconstructed rather than advertised as a discovery. The extension here is a mixed-decision model, proof of its exact sharp multiplicative advantage over deterministic choices within feasible ballot profiles, bounded census, timing counterexample and original sonification. Mathematical priority is not asserted.

## Exact model: fixed but unspecified score

Let m>=2 alternatives receive N>=1 equally weighted, complete strict ballots. R(i,k) is the number of ballots placing alternative i in the top k, k=1,...,d=m-1. No missing ballots, ties, voter-specific utility scales or weights are modelled.

Use a single common nonincreasing positional score w with w(1)=1, w(m)=0. Its adjacent differences q(k)=w(k)-w(k+1) are nonnegative and sum to one. Conversely every such q determines an allowed w. The score of i is q dot R(i), by telescoping.

For each k let M(k)=max_i R(i,k), and let L(i,k)=M(k)-R(i,k). Each column contains at least one zero; all entries are nonnegative.

The deterministic regret of choosing i at q is max_j q dot (R(j)-R(i)). Its supremum over q is max_k L(i,k): the upper bound follows by taking componentwise maxima, and the unit vector at a maximizing k attains it. Thus D=min_i max_k L(i,k), exactly the established result of Viappiani's Theorem 1. Zero regret means a necessary co-winner, not necessarily a unique winner.

Now choose a lottery p over alternatives, before observing the fixed policy q. Compare expected score to the best single alternative for that same q:

Regret(p,q) = max_j q dot R(j) - q dot sum_i p(i)R(i).

By the identical componentwise bound and unit-vector witness, its maximum over q is exactly max_k sum_i p(i)L(i,k). Therefore

V = min_p max_k sum_i p(i)L(i,k).

This is the finite zero-sum matrix game with loss matrix L. The chooser plays rows; the policy uncertainty can be represented by the pure threshold columns (or their mixtures in the dual certificate). Equivalently, find a probability vector p and smallest v with each expected column loss <=v. A nonnegative threshold distribution t summing to one and satisfying sum_k t(k)L(i,k)>=v for every row is a lower-bound certificate: averaging over t cannot exceed the maximum column loss. Matching primal and dual bounds certify exact optimality. The finite minimax theorem ensures matching certificates exist; the sharp construction below exhibits them directly.

If w must be strictly decreasing, the same numerical supremum applies by approximation to the simplex vertices, but it need not be attained. The allowed closed simplex here makes attainment literal.

## A sharp limit on the value of randomization

**Proposition.** For d=m-1 thresholds, V <= D <= d V. If V=0, D=0 too. For every m>=3 the multiplicative factor d is attained by actual complete strict ballots, not merely by an arbitrary loss matrix.

Proof of upper bound: take an optimal p. Every expected column loss is at most V, so the expected sum of all d losses is at most d V. Some row with positive probability has row sum at most d V. Nonnegativity means its maximum entry is at most its row sum. Choosing that row gives D<=d V. The lower inequality V<=D follows by admitting pure choices. This is a generic nonnegative matrix argument; it alone says nothing about realizability by ballots.

**Ballot-feasible extremal family.** Use m alternatives, N=m^2 ballots. Index thresholds and the first d alternatives by 1,...,d; label the remaining alternative m. Define L(i,k)=m if i=k or i=m, and zero otherwise. For each threshold set

R(i,k)=k m+2-L(i,k).

For m>=3 every column has at least one zero loss and exactly two entries equal to m. Each R row is nondecreasing, since the difference between successive columns is m plus the difference of two entries of L and is therefore nonnegative. The initial entry is nonnegative and the final entry is <=N. The sum of each R column is k m^2. Consequently the rank-frequency matrix H given by adjacent differences, with endpoints R(i,0)=0 and R(i,m)=N, has nonnegative integer entries and all row and column sums equal to N.

To realize H by actual ballots, take a bipartite multigraph between alternatives and rank positions with H(i,r) parallel edges. It is N-regular; Hall's condition follows by counting N|S| incident edges from any subset S against capacity N|neighbors(S)|. Extract a perfect matching and decrement it, repeating until the matrix is zero. Each matching is one complete strict ballot. The resulting cumulative counts and losses are exactly as specified. The executable generator reconstructs these ballots for m=3,...,12.

Every pure row has maximum loss m, giving D=m. A uniform lottery over the first d rows has expected loss m/d in every column. A uniform dual distribution over the d columns gives expected loss m/d on each specialized row and m on the final row, furnishing the matching lower bound. Hence V=m/d and D/V=d. The ratio is sharp. Dividing scores by N preserves the ratio but not the absolute loss: this is not a claim of unbounded absolute performance gain. For m=2 there is only one threshold, and randomization has no advantage.

**Timing falsifier.** If the adversary observes the realized choice and may then select q, the objective becomes sum_i p(i)max_k L(i,k), minimized by a pure optimal row. The randomized advantage vanishes. Likewise a guarantee on realized rather than expected loss cannot be inferred from the mixed solution. If a particular scoring convention is authorized and known before choosing, select its maximizing alternative and incur no regret. The uncertainty and decision timing are essential, not decoration.

## Exhaustive experiment and negative controls

The JavaScript laboratory enumerates every multiset of n=1,...,10 complete three-alternative ballots (six ballot types in lexicographic order). These are 8,007 labelled count vectors, not uniformly sampled elections or independent human observations. For two thresholds the mixed optimum can be found on an edge of the convex hull of candidate loss points: if the optimum is interior, moving toward smaller coordinates until reaching the boundary cannot increase the objective. Edges connect two vertices; checking both endpoints and the intersection with the diagonal suffices. The dual checks all pairwise line crossings and endpoints on [0,1]. Integer/rational comparisons agree exactly on every enumerated profile. No floating-point LP or tolerance is used; integer arithmetic is bounded to the census/construction inputs.

| n | Profiles | No necessary co-winner | Mixed strictly improves | Sharp factor 2 | Strict Condorcet winner not necessary co-winner |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 6 | 0 | 0 | 0 | 0 |
| 2 | 21 | 3 | 3 | 3 | 0 |
| 3 | 56 | 12 | 12 | 6 | 12 |
| 4 | 126 | 30 | 30 | 12 | 12 |
| 5 | 252 | 72 | 72 | 24 | 66 |
| 6 | 462 | 135 | 129 | 33 | 60 |
| 7 | 792 | 258 | 258 | 60 | 246 |
| 8 | 1,287 | 429 | 429 | 93 | 225 |
| 9 | 2,002 | 690 | 672 | 114 | 654 |
| 10 | 3,003 | 1,071 | 1,065 | 183 | 612 |
| **Total** | **8,007** | **2,700** | **2,670** | **528** | **1,887** |

Thirty profiles lack a necessary co-winner yet get no strict improvement from mixing: a positive regret is not enough to guarantee a lottery benefit. One hundred eight profiles have at least one pure minimax alternative that never wins under any allowed scoring vector (possibly tied for minimax); this is a bounded census of an already-established phenomenon, not priority.

An independently implemented Python Fraction-based dual/rank-count loop reproduced the 8,007 profile count, 2,700 without a necessary co-winner, 2,670 with a strict improvement, and 528 attaining factor two. It also independently extended the Borda check to n=11.

**Unexpected negative result and follow-up.** Through ten ballots, no profile was found in which *all* Borda winners have strictly worse worst-case regret than the optimum. This tempting observation does not generalize. At eleven ballots six labelled count vectors falsify it. The first lexicographic count vector (ABC, ACB, BAC, BCA, CAB, CBA) is (0,1,4,2,4,0):

| Alternative | Top-one count | Top-two count | Loss under top-one | Loss under top-two | Worst loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 1 | 9 | 5 | 0 | 5 |
| B | 6 | 6 | 0 | 3 | 3 |
| C | 4 | 7 | 2 | 2 | 2 |

B is the unique Borda winner (sum of cumulative ranks 12 versus 11 and 10), but C is the unique pure minimax choice. A mixture with probabilities 3/8 on A and 5/8 on B yields both expected column losses 15/8, better than C's 2; the dual threshold mixture (3/8,5/8) yields losses 15/8,15/8,2, proving optimality. The precise fractions here are direct arithmetic. This exposes three legitimate but distinct policies: Borda, pure robustness, mixed robustness. None follows from ordinal evidence alone.

The two-ballot example at the beginning is a minimal positive control for randomization. Unanimous first place gives zero regret. Negative ballot multiplicities are refused. The sharp family has been reconstructed and primal/dual-certified for ten sizes (m=3 through 12), including the loss and rank-count matrices. The code is intended for bounded exact experiments, not production election analysis.

## The acoustic witness: The Ruler Organ

The same two ballots can drive three sequential candidate tones. Map the candidate's score to a pitch (220 Hz + 40 Hz per score point, rounded to an integer); hold amplitude and duration constant. The generator writes 8 kHz mono 16-bit PCM using a simple integer-envelope square wave. Plurality, veto and Borda produce distinct arrays from unchanged rank data. For the two-ballot witness, the candidate scores are (0,1,1), (2,1,1), and (1,1,1), respectively.

| Policy | FNV-1a 32-bit fingerprint | Bytes |
| --- | --- | ---: |
| Plurality | a3bad6fb | 4,844 |
| Veto | af8e1253 | 4,844 |
| Borda | cc38e8d3 | 4,844 |

These fingerprints are deterministic reproduction checks, not cryptographic provenance. The generator compared actual arrays for difference and deterministic reproduction. No listening test was performed. Square-wave pitch and perceived urgency or importance are not interchangeable. The sonic mapping has no special epistemic status.

An artistic extension would give the policy itself a modulation input: instead of changing the oscillator data, sweep the rank gaps on their simplex, making the order of voices change while every vote remains fixed. A second channel could render a fixed baseline or candidate regret rather than pitch-ranked authority. That is a proposal, not a validated communication design.

## Practical exaptation: decision-rule receipts

A multi-agent evaluation can preserve its full rankings yet report a winner without identifying the scoring rule. A candidate receipt should retain:

- immutable alternative set and ballot/profile identity;
- allowed common score family, normalization and rank weights if fixed;
- cumulative count and loss vectors, pure maximum regret and maximizing threshold witnesses;
- if randomization is allowed, the lottery, expected worst-case regret and dual certificate;
- whether the policy is fixed before sampling, whether the draw is externally visible, and whether a realized-loss rather than expectation guarantee is required.

If evaluation criteria are already cardinal and comparable, forcing an ordinal transformation would throw away relevant information. If ballots are dependent, strategic, partial, weighted, or rank sets differ, this exact receipt does not by itself solve the problem. For irreversible choices or compliance gates, a lottery may be disallowed; seek the authorized rule instead. A small worst-case loss is not factual certainty, fairness, an empirical utility measure, or permission to act. Rank normalization does not make utilities interpersonally comparable.

## Reproduction and reconciliation

Run from this directory:

    node laboratory.js
    node laboratory.js /tmp/ruler-organ
    python3 crosscheck.py

The optional Node argument writes three WAV files to the requested local directory. All other results are printed to stdout. The JS experiment was executed in a tool-enabled JavaScript isolate before committing the same function definitions; the Python algorithm was independently run in a local Python process, and its replay script adds explicit expected-result assertions. No human reviewer, new subagent, or participant was involved. The main repository's Python structural checks are a separate acceptance requirement and do not by themselves execute these expedition scripts.

Base observed: 495a98ca12bae467a507031f04931aa4254b1866. Root AGENTS, RAG, programme, runbook, research integrity and validation read; current issue/PR inventory and first branch page inspected, plus actual #228 report and #184 accepted-main README. Newly created issue #244 had no comments at initial inspection. All additions live exclusively in this expedition directory. No frozen protocol, central manifests, human gates or other branch changed. No claimed empirical evidence or novelty review. PR, exact head, checks and any post-merge evidence must be verified separately.

## Fictional afterword — the clerk and the ruler

The clerk kept three scales in a velvet case. Each was marked first, second, third; each was entirely correct. On Monday, the scale made the loudest proposal victorious. On Tuesday, the quiet compromise rose above it. No witness was called back, no vote altered, no record corrected.

He began to announce the name of the ruler before he announced the name of the winner.

The committee complained that this doubled the length of the ceremony. The clerk replied that it was not a second announcement. It was the missing half of the first.
