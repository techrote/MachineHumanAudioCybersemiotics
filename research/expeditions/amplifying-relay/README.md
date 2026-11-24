# The Relay That Amplifies Silence

Issue #248. Independent exploratory mathematical/software artifact; not an empirical or canonical MHAC claim. GPT-6.2-assisted derivation, implementation, source inspection and self-check, 2026-11-24. No human participants, external review, or actual device measurements.

## Motivation and non-duplication

An individually extinguishing operation need not extinguish a sequence of different operations. A switched instrument can preserve a hidden state direction that its next operation amplifies. Conversely a guard that removes every indefinitely growing cycle may leave a dangerously large finite excursion. This is an investigation of exact algebraic gain and transition-policy repair, not #207's reversible operation order, #216's exclusive scheduling, #232's omissions, #240's stochastic observation, or #246's ornament capacity. The intended exaptation is a small transition-guard compiler for symbolic or experimental synthesis networks.

## Model and established result

For nonzero integer vectors u_i,v_i of a common dimension, positive integer denominator d, mode M_i = u_i v_i^T / d acts on a column state. Every mode is initially selectable. A guard forbids an ordered adjacent pair of modes, not a whole mode. Other transitions remain legal; no reset policy, scheduling fairness, external forcing or physical clipping is assumed.

Chronological transition i->j has nonnegative rational weight w_ij = |v_j^T u_i|/d. Zero-weight transitions are legal unless forbidden but annihilate a product, so can be omitted in nonzero-path searches. For word i_1,...,i_l, multiplication of rank-one matrices gives

    M_il ... M_i1 = u_il v_i1^T / d * product_{k=1}^{l-1}(v_i(k+1)^T u_ik / d).

The induced l1 norm is therefore

    ||u_il||_1 ||v_i1||_infinity / d * product w_i(k),i(k+1).

This is exact, including signed factors; the absolute value is taken after the inner product, not componentwise before it. The largest geometric mean of a nonzero simple directed cycle is the worst asymptotic rate rho (zero if no such cycle). Repeated cycles yield the lower bound; any path splits into a simple path plus closed cycles, whose lengths grow at most at rho, yielding the upper bound with a finite multiplicative constant when rho>0. With no cycle all sufficiently long products vanish. This argument applies to the stated pair-constrained language; it is not a general switched-system solver.

Classification: rho<1 uniformly exponentially decays; rho=1 all products are bounded but some repeated cycle fails to decay on a suitable nonzero initial vector; rho>1 yields unbounded gain. This is established rank-one joint spectral radius theory, not a new theorem.

Primary provenance: Amir Ali Ahmadi and Pablo A. Parrilo, "Joint Spectral Radius of Rank One Matrices and the Maximum Cycle Mean Problem", 51st IEEE CDC (2012), pp. 731–733, DOI [10.1109/CDC.2012.6425992](https://doi.org/10.1109/CDC.2012.6425992). [Author-hosted PDF](https://www.mit.edu/~parrilo/pubs/files/AhmadiParrilo-Joint%20spectral%20radius%20of%20rank%20one%20matrices%20and%20the%20maximum%20cycle%20mean%20problem.pdf). Agent inspected extracted text and images of printed pp. 731–732 (PDF indices 0–1): rank-one factorization, Theorem 2.2, Corollary 2.1, Remark 2.2 and Example 2.1. Their cyclic coordinate example already establishes the failure of length-two products to determine the rate. Our chronology convention transposes their edge orientation. Their polynomial algorithm is not implemented here; exhaustive simple-cycle enumeration is deliberately inspectable and exponential. No priority claim, no article redistribution, and no assertion of a full literature search.

## Exact peak and guard compilation

If every cycle product is at most 1, any positive-gain path with repeated mode contains a cycle that can be removed while retaining its endpoints and without decreasing the norm above. Thus a maximum induced norm over **all nonempty legal words** occurs at length at most the number of modes. For each initial mode, a dynamic program retains the highest product numerator for each current mode and fixed length. The denominator is fixed at each length; endpoint factors are independent of the interior path. Compare rational values by cross multiplication. This proves a finite peak even for neutral cycles. If any cycle product exceeds 1, the peak is unbounded. The empty word is intentionally excluded (include max(1,peak) if identity matters).

A strict-stability guard must intersect every cycle with product >=1; a boundedness guard only needs to intersect cycles with product >1. Optionally impose a rational peak cap. After cycle violations are eliminated, an above-cap norm witness is a path whose edges must also be intersected. If that witness is a singleton, no pair guard can help. Recursively branch on every unlocked edge of a current witness; every feasible extension must remove at least one. Positive integer costs allow incumbent-cost pruning; each unique blocked set is visited at most once. A completed search yields all minimum-cost sets (not every feasible superset), or proves infeasibility. Budget exhaustion is separately reported, with any incumbent noncertified. Locked edges cannot be removed. No guard is implemented in a live device.

The solver uses BigInt for weights, roots represented by exact product and integer root, and rational comparisons; costs are bounded safe integers. Up to 12 modes are accepted as a syntax limit, not a practical complexity guarantee. Cycle enumeration can itself be expensive; the search-node budget does not limit cycle enumeration or total wall time. A future implementation could use exact threshold dynamic programming, integer optimization and independently checked certificates.

## Parametric separation: same stability, arbitrarily different excursion

Let K>1 be an integer, and e_0,e_1,e_2 coordinate vectors. Set

    A = e_0 e_2^T / K
    B = K e_1 e_0^T
    C = K e_2 e_1^T.

Every isolated mode squares to zero; every length-two product has spectral radius zero. The only positive directed cycle A->B->C->A has weights K,K,1/K, product K, rate K^(1/3). Starting at e_0, B,C,A yields norm K,K^2,K. Repetition multiplies by K every three operations.

Any one of the three nonzero transition edges can be forbidden at unit cost, leaving a positive-edge acyclic graph, rate exactly zero. But only blocking B->C lowers the all-word peak to K. The other two guards retain the word B,C, which has norm K^2. No larger norm is possible with a broken cycle, since every nonzero path contains each mode at most once and the gains are K,K,1/K. The singleton B (or C) has norm K, so no transition guard can achieve a smaller cap. Hence the ratio of the largest and smallest peak among equal-cost, equally asymptotically stable repairs is K, unbounded over the family. This is a derived toy example and a sharp result in this model, not claimed new to control theory. K=2..64 replayed by family.mjs.

## Census and adversarial qualification

The population is all 4^6 = 4,096 labelled three-mode off-diagonal weight assignments from {0,1/2,1,2}, with zero diagonals. These are realized by coordinate rank-one factors, with an extra initial coordinate feeding a mode if its incoming column would otherwise be zero; all output vectors have zero fourth coordinate so this does not change cycle weights. The extra coordinate is included in the induced norm calculation. It is a discrete constructed population, not a sampling distribution of real devices.

- 856 strictly decaying, 1,049 bounded-neutral, 2,191 growing.
- Even requiring all two-mode cycles to decay strictly leaves 88 neutral and 56 growing three-mode cases.
- Minimum strict guard costs 0,1,2,3 occur 856,1,938,1,086,216 times.
- Direct full-matrix multiplication and trace classification matched 4,160 cases (population plus 64 seeded signed-factor sets). Direct induced norms matched 1,933 non-growing cases; signed cases checked through length five.
- 256 independent exhaustive blocked-subset comparisons (128 strided population cases, two policies per case) matched optimal cost and the complete optimal solution sets, including locks, weighted costs and a cap.
- Explicit controls: a neutral cycle is bounded but not strictly decaying; a genuinely decaying example; an impossible singleton cap; an unremovable locked cycle; and budget exhaustion distinct from infeasibility.

The independent algorithm constructs full matrices, multiplies them directly and checks the trace of closed words through length m (rank at most one); it does not calculate inner-product edge gains. It shares the proved finite length bound, so not an independent proof of that bound. The signed population is a deterministic seeded test, not statistical evidence. The guard oracle enumerates every removable-edge subset in each selected test case and checks full matrix products. No other agent or human performed this verification.

## Acoustic construction and transfer

render.py generates two original stereo PCM16 files at 16 kHz. Each cell is 200 ms, the active coordinate chooses 240/320/480 Hz, and magnitude chooses a compressed/clamped triangle-wave amplitude. Zero state is silent. The score starts at e_0. In the unguarded-vs-guarded piece, the left schedule repeats B,C,A; the right repeats B,B,A (one arbitrary allowed policy replacing the prohibited step, not an asserted automatic response). In the equal-rate piece, the left B,C,A,A is admissible under the A->B guard; the right B,B,A,A under the B->C guard. They peak at 16 and 4 respectively for K=4 and then extinguish. Both obey their respective guard. The actual audio amplitudes are bounded, not literal unstable feedback; there are no real transducers or listening trials.

Possible transfers: modular synthesis routing macro qualification; finite transition-restriction suggestions for switched rank-one state updates; adversarial test generation for local stability checks; controllable musical transients; agentic tooling in which an individually harmless transformation participates in a multiplicative feedback loop. The last is only an analogy unless a valid linear state model and constraints are independently established. No operational warning, safety, firmware, controller, or perceptual efficacy claim.

## Reproduction and boundary

From this expedition directory, run Node 18+:
    node verify.mjs > reproduced.txt
    diff -u results.synthetic.txt reproduced.txt
    node family.mjs

Use Python 3.11+:
    python render.py run
    python render.py repeat
    diff -r run repeat

The computational routines and exact test functions ran in a V8 tool runtime by lexically linking the fetched JavaScript module bodies (not Node's native ESM loader). The renderer ran locally in Python; repeated WAV and manifest bytes matched, renderer source Git blob 29bcda44e51c9d79199f256242f18aacb042dd2f. WAVs generated on demand; no binary or primary article is committed. See audio-hashes.synthetic.txt. Clean-checkout Node execution, full repository CI and independent review remain acceptance items. Main observed before edits: 495a98ca12bae467a507031f04931aa4254b1866. This issue owns only its isolated directory, no changes to shared or frozen records. Keep the PR draft pending review.
