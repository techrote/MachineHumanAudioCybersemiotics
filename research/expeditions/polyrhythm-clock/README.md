# The Polyrhythm That Cannot Share a Clock

Refs #216. Independent exploratory synthetic mathematics and original audio, 2026-11-23. Base 495a98ca12bae467a507031f04931aa4254b1866. GPT-6.2 assisted; local execution and self-review only, no independent human assessment.

## Question

Can two individually maximally even pulse streams always be combined into a single exclusive event channel without losing their local regularity, provided their total rates fit? No. This is a finite analogue of the difference between aggregate resource sufficiency and simultaneous local guarantees. A second question is quantitative: what minimal regularity sacrifice makes the streams compatible?

## Model and proof

A binary word w of period q has p ones. For a cyclic interval of length k, define its error as its pulse count minus kp/q. Let E(t)=q sum(w[0:t])-pt, so E(0)=E(q)=0. Extend E periodically. The maximum absolute cyclic interval error, multiplied by q, is D=max E - min E: any interval difference is bounded by the range, and the two extremal positions define a cyclic interval attaining it. This holds for intervals of all lengths, since adding full cycles adds zero error.

Let g=gcd(q,p). E(t) is a multiple of g and is congruent to -pt modulo q. Over one period its residues include q/g distinct multiples of g. Consequently D >= q-g. The mechanical word given by consecutive differences of floor((tp+phase)/q) attains this bound: its E(t) equals (phase mod q) minus ((tp+phase) mod q), and these residues have range q-g. This includes p=0 and p=q. No floating-point arithmetic is needed for this proof or for the solver.

For streams A and B with p and r events respectively, require p+r<=q. Measure overlap by the number of simultaneous ones and each stream's excess D over its individual optimum. The solver enumerates every ordered pair of fixed-weight binary words, without quotienting rotations; it retains a witness for each objective triple and returns the nondominated front. A collision-free schedule always exists without regularity constraints in this finite model: simply allocate disjoint sets of the requisite sizes. This is not a real-time deadline guarantee.

### A minimal obstruction

At q=6, p=2, r=3, individually optimal streams have respective gaps 3 and 2, i.e. residue classes modulo 3 and 2. To see why, any deviation from the uniform gap forces a gap at least one slot too long, yielding an all-zero interval whose scaled error is at least q, larger than q-g. Every pair of residue classes intersects exactly once per six slots (Chinese remainder theorem). Total utilization is only 5/6, but zero overlap is impossible at both individual optima.

The complete 300-pair enumeration produces exactly three nondominated points (overlap, excess A, excess B):

| Point | A | B |
| --- | --- | --- |
| (1,0,0) | 100100 | 101010 |
| (0,2,0) | 101000 | 010101 |
| (0,0,3) | 100100 | 011010 |

The first obstruction in the ordered census q=2 through 10 occurs at q=6. The two zero-overlap options preserve total pulse counts while assigning the cost to different streams. The minimax excess criterion selects (0,2,0), but another fairness objective may prefer the other point.

### Infinite counterexample family

For odd a>=3 take q=2a, p=2, r=a. At their individual optima, A and B occupy residue classes modulo a and 2, respectively; they intersect once in each common period. All E values for A are multiples of 2 and all E values for B multiples of a, so any departure from individual optimality costs at least 2 or a in scaled discrepancy. The minimal possible maximum excess for a disjoint pair is therefore at least 2. Keep B on odd slots, and place A at 0 and a-1 (both even). Its two gaps are a-1 and a+1. The longest zero interval has length a, and the shortest interval containing both pulses has length a; both attain scaled error magnitude 2a=q, and every other interval has error magnitude at most q (check separately the zero-, one-, and two-pulse cases). Thus A's excess is exactly 2, B's zero, attaining the lower bound. This proves a sharp minimax penalty for this particular family, not a universal optimum.

## Experiment

The q=2..10 census covers all positive unordered density pairs p<=r with p+r<=q, and every labelled binary placement for both channels. Result: 95 density cases, 490,166 placement pairs, 11 cases where zero overlap is impossible at the individual optima. At q=10,p=4,r=5 the minimum overlap with both individually optimal is two; minimax disjoint excess is 4. This is a bounded exact combinatorial census, not a probability estimate for real traffic. Negative controls include q=6,p=r=2, q=6,p=r=3 and q=4,p=1,r=2 where zero overlap and both optima coexist.

The original stereo examples use six repetitions of the six-slot witness at 120 ms/slot; the left and right channels are separate 440 and 660 Hz decaying sine pulses. The coincident stream and its collision-free alternative have the same counts; the latter shifts one A onset. This is an artistic rendering of the schedule, not a listening experiment, and stereo audio itself can carry simultaneous pulses. The exclusive-slot rule is a chosen abstraction rather than a property of stereo acoustics.

## Reproduction and custody

From this directory run:
    python -m unittest -v test_clock
    python clock.py --out run

Five test methods passed locally, including independent direct cyclic-window enumeration for every binary word of length 1..8 (510 words), all intercepts of the mechanical words, exact q=6 front, positive/negative controls, front witness consistency through q=8 and coprime phase checks. The default run was repeated and the three output byte hashes matched on this runtime:
- collision-free.wav: 3cc951b81029b52be8162edb8009c77f89e101b64bb5a831ab8219ea6fc05613
- independently-even.wav: a8846f3f8057105897ae577bfa0798f18a0302a03ce31e62ad852a605d01d06d
- results.json: c6f825441f22527a6c4ef23653b31153a06f113327d2f6f88394174c4eba8154

The committed source blobs were compared to the locally executed blobs: clock.py 04d5104a98ff39e341034c4290270f1a02dc16c4; test_clock.py 53d335ea8d9c4ae8e9d60f48cc05601478cc0741. Floating sine rendering is not promised bit-identical across arbitrary libm implementations; the integer analysis is exact. Binary audio and generated JSON are reproducible outputs rather than canonical repository records.

## Sources, distinctions and exaptation

- [Paquin and Reutenauer, On the superimposition of Christoffel words (2010 preprint)](https://arxiv.org/abs/1004.1890). Inspected arXiv text abstract, introduction and §2.1 definitions, not all proofs. The authors explicitly place disjoint Beatty sequences and Christoffel superimposition in established mathematics and report necessary/sufficient conditions. Therefore the obstruction itself is not presented as a novel mathematical discovery. The expedition's particular excess-discrepancy objective and sonic rendering are original local constructions; priority is unassessed.
- [Toussaint, The Euclidean Algorithm Generates Traditional Musical Rhythms, Bridges 2005, pp. 47–56](https://archive.bridgesmathart.org/2005/bridges2005-47.html). Inspected conference archive metadata and abstract only. This supports the existing connection between even onset distributions, musical timelines and number-theoretic constructions, not the claim that any specific tradition uses this toy.
- The mathematical derivations above are self-contained; no claimed empirical results, no participants, no safety guarantees. No third-party full text copied.

Potential reuse: rhythm generators that offer a polyphonic/nonoverlap switch plus explicit irregularity cost; resource-slot toy benchmarks for agent message arbitration, pulse-density multiplexing or embedded serial scheduling; exact Pareto witnesses for testing greedy interleavers. In a real device, unequal event lengths, jitter, stochastic rates, priority, deadlines and aperiodic workloads break the model. There is no guarantee of human interpretability, auditory pleasantness, or acceptable device operation.

Unlike #199, this is not a feature-collision question; unlike #195, it is not a logical joint-witness inference; unlike #207, it is not about permutation composition. The overlap notion is simultaneous use of a declared exclusive slot, not causation (#183). This expedition does not alter frozen research scope or registries.

The intriguing semiotic implication is a hypothesis, not a finding: a perfectly truthful pulse count can conceal the local timing price paid to make multiple truthful streams coexist. A future system may wish to communicate scheduling debt separately from quantity. A human study would need its own authorization and construct validation.


## Second-stage experiment: exact discrepancy-band dynamic programming

The exhaustive Pareto solver is deliberately small-scale. A second independent search procedure finds the least maximum excess for collision-free schedules without enumerating all pairs of binary words. It is also a feasibility oracle for asymmetric discrepancy caps.

For any feasible schedule, rotate both words together so A's prefix error attains its minimum at the initial boundary. Rotation preserves pulse counts, overlap and cyclic discrepancy, so A's allowed band may be fixed at [0, D_A]. B's prefix error is still measured from zero; its minimum L is a multiple of gcd(q,r) with -D_B <= L <= 0. Enumerating these lower endpoints is complete. For each candidate L, traverse layers t=0..q of reachable cumulative counts (i,j). At each layer permit only idle, A, or B, and retain states whose scaled prefix errors satisfy both bands and whose remaining required pulses fit. The state is sufficient because all future constraints depend only on t,i,j and the two fixed bands. Every path ending at (p,r) is a feasible witness, and every feasible schedule has a representation in some enumerated band. Thus an exhausted search proves infeasibility under the stated finite assumptions. Monotone feasibility allows integer binary search of the minimax cap; block placement supplies a feasible upper bound.

This is a pseudopolynomial finite dynamic program in the period and numerical caps, not a general scalable scheduler for arbitrary continuous or multi-channel tasks. It solves a different objective from the full Pareto enumeration; it returns one minimax witness, not the entire frontier or a guaranteed secondary-optimal point.

All eight test methods passed locally after adding this solver (0.319 s in one run, no timing guarantee). The two solvers agree on the minimax value in all 95 census cases; returned witnesses were rechecked for counts, exclusivity and objective, and when the optimum is positive the immediately smaller cap was rejected. Asymmetric caps for the six-slot witness and the proved odd family through q=126 also passed.

Selected additional exact observations (scaled excess is in units of 1/q pulse):

| q | p | r | minimax excess | witness excess A,B |
| ---: | ---: | ---: | ---: | --- |
| 14 | 2 | 7 | 2 | 2,0 |
| 30 | 2 | 15 | 2 | 2,0 |
| 62 | 2 | 31 | 2 | 2,0 |
| 126 | 2 | 63 | 2 | 2,0 |
| 127 | 31 | 58 | 25 | 25,25 |
| 128 | 41 | 64 | 40 | 40,0 |
| 101 | 31 | 61 | 26 | 26,26 |
| 256 | 81 | 128 | 80 | 80,0 |

These are selected synthetic cases, not a statistical population. The final q=256 example ran in 0.525 s locally in a single observation. No generic speed claim is made. The useful exaptation is a certificate-producing bounded feasibility oracle for finite two-stream arbitration rather than just an aesthetic rhythm generator.

Reproduce the combined suite with python -m unittest -v test_clock test_band_solver. Local tested blobs: band_solver.py 788f0e75d5eca5fa35b6efd2a4fa52c9adbebf71; test_band_solver.py 338802392a00d14cda3abc8e4531656b8baf7c32. The existing generated audio/results are unchanged.

## Acceptance boundary

This package is Draft for review. Exact final-head repository CI, independent mathematical critique, any broader generalization and empirical claims are separate. No human action is currently required to reproduce the synthetic result.
