# The Decay That Refuses to Die

Refs #264. Synthetic mathematical expedition; AI-assisted by ChatGPT, 2026-11-24. Reconciled base 495a98ca12bae467a507031f04931aa4254b1866. The open-PR list and targeted issue/branch searches revealed no competing quantized-decay scope. No central records or protocols changed. No empirical or production claim.

## Exact model and coverage

Let x be an integer pair. The undriven update before quantization is Mx, where M = [[a,-b],[b,a]]/q and a²+b² < q². N rounds each coordinate to nearest integer, ties away from zero; T truncates toward zero. There is no finite-word overflow, saturation, external excitation, dither or measurement noise. The ideal linear system has Euclidean contraction r = sqrt(a²+b²)/q < 1.

Write delta = q²-a²-b² and R = ceil(3q²/(2 delta)). Since 1-r = delta/(q²(1+r)) >= delta/(2q²), we have (1-r)R >= 3/4 > sqrt(1/2), the maximal Euclidean rounding error. Thus for norm(x) <= R, norm(Nx) <= rR+sqrt(1/2) < R. T is also invariant. Outside R, N strictly decreases norm, and squared norm is a nonnegative integer, so every integer start eventually enters the disk. Hence every nearest-rounding cycle on the whole lattice lies in the enumerated disk, not merely in a guessed test window. Initial states outside the disk are NOT covered by the intervention-optimality census. Magnitude truncation strictly decreases squared norm for every nonzero x because each truncated coordinate has magnitude no larger than its ideal coordinate and r<1.

## Exact intervention compiler

Build the finite graph with N and T edges per state. N costs (0,1); T costs (1,1). Target zero, minimize lexicographically (number of T updates, total number of steps). This is not minimization of changed bits, integrated quantization error, elapsed time alone, or a single globally sparse lookup table.

Truncation provides an all-state feasible route. Optimal routes are simple before zero: deleting any repeated-state loop strictly improves the objective. For n disk states, a simple path takes <= n-1 steps. Encode costs as 1 or W+1, W=n+1. Scalar shortest paths then implement the exact lexicographic objective (a shortest scalar path is simple too). Reverse Dijkstra from zero gives the cost-to-go for every state. Choose a minimizing outgoing edge; cost-to-go strictly falls at each step, proving finite termination and simultaneous pointwise optimality. Equal successors need only the N edge. Implementation caps q and disk radius, uses safe integers within that cap, and rejects unsupported parameters.

The comparison guard uses N only when it strictly decreases squared norm, otherwise T. That guard terminates, but can waste interventions by refusing harmless transient excursions or equal-energy steps. A negative control is pure truncation: it always terminates but can spend more interventions; another is a system with a=b=0, which needs no T. The optimized policy trades possible extra time for fewer changes. It does not optimize both objectives independently.

## Unbounded exact construction

For q >= 2, take a=0, b=q-1, m=floor(q/2). On the square |x1|,|x2| <= m, the nearest update is exactly the quarter turn (-x2,x1): the magnitude error from the ideal quarter turn is <= 1/2 and ties round away from zero. All nonzero states in that square have period exactly four; the number of distinct four-cycles IN THIS SQUARE is ((2m+1)²-1)/4 = m(m+1). No claim about cycles outside the square is required.

T rotates while decreasing each nonzero coordinate magnitude by exactly one. Both actions leave the square invariant; N preserves the maximum coordinate magnitude and T reduces it by one until zero. Consequently the exact minimum intervention count from any state in this square is max(|x1|,|x2|). In particular (m,m) requires exactly m interventions. There is no uniform intervention budget as q increases, despite strict contraction for every fixed q. Proof is for these rounding conventions and the two-action model only.

## Synthetic census and falsifier

Enumerate labelled nonnegative a,b with q=2..10 and a²+b²<q². Repeated rational coefficient pairs at different denominators are intentionally retained. 339 models, 168187 disk-state/model pairs, 230 models with nonzero cycles, 2305 nonzero cycles; 166396 state/model pairs have a nonzero nearest-rounding attractor. Disk radii vary with coefficients: these are not equal-weight frequencies for initial signals or real devices. Full period histogram and witness traces in results.synthetic.txt.

Longest observed cycle: 68 updates at (a,b,q)=(8,4,9), starting (-16,4), with nine truncation interventions in a 60-step optimal escape. Not a general maximum. At (4,8,9) start (-81,12), greedy requires 48 interventions/140 steps; exact policy requires 9 interventions/283 steps. The optimal path is deliberately slower. Maximum minimum intervention count observed is 34, at (7,7,10), start (-70,-26). These examples falsify one-intervention escape and local strict-energy-gate optimality, but do not invalidate the guard's convergence guarantee.

## Qualification and acoustic mapping

- V8 executed the exact JS function declarations serialized into decay.mjs: disk closure, truncation descent, Bellman equations, distance bounds and comparison against greedy for the whole census; independent augmented-state BFS for 1644 small-model initial states (q<=4).
- Python 3 local execution of render.py and crosscheck.py: independently implemented divmod rounding, tuple-weight Dijkstra and orbit decomposition. All nine aggregate metrics and every period bin matched JS, and 91583 square-state construction checks passed for q=2..64. This is an independent algorithm/implementation cross-check by the same agent, not external review.
- Two local executions produced identical WAV bytes and manifest. persistent-orbit.wav: 2.55s stereo 16 kHz PCM16, 2 PCM samples per update; left directly emits x1*900, right follows same orbit for 100 cycles then escapes using the exact policy. intervention-debt.wav: 6.08s stereo; radius floor controls a 400 Hz triangle-wave amplitude, 20 ms per state; left optimum, right greedy. The latter is deliberately an artistic time-expanded mapping, not a physical resonator recording.
- Native clean-checkout Node runner and repository-wide CI not yet qualified at preparation. No listening experiment or listener-effect inference.

Reproduce from this directory:
    node verify.mjs --check
    python crosscheck.py
    python render.py run

Local source SHA256: render.py 754c1dd4492bc1a928cbd9dda16782d870d0c9e402946aefb5d33fa181547cc2; crosscheck.py ca75a1687352a88f2c1033397804a195203530429247678a62493a75afb20658. WAV SHA256: persistent-orbit ac642bc0b9446c756a83026e7af274e87dc370ee5ca7458885ea8df975a2fe4a; intervention-debt 455d4d3bb8f8dc3e035aa10f31f5264b617b5afaca7538ec8243c45c116276fe. WAVs are generated, not committed.

## Provenance and transfer

Lawrence, V.B. and Mina, K.V. (1979), "A New and Interesting Class of Limit Cycles in Recursive Digital Filters", Bell System Technical Journal 58, 379–408, https://doi.org/10.1002/j.1538-7305.1979.tb02225.x . Publisher landing page and abstract read on 2026-11-24; no full-text claim. The abstract establishes historical context: recursive filter quantization can generate sustained periodic orbits; specialized countermeasures are known. Its rolling-pin construction is NOT asserted to be the same as this coupled rotation. References to controlled and randomized rounding are discovery leads, not reviewed primary results. IEEE article https://ieeexplore.ieee.org/abstract/document/1083367 was search-abstract visible but direct access returned 418; no full-text claim. All proofs and numerical results here derive from the explicitly defined toy, not those articles. Mathematical priority is not claimed.

Candidate exaptations: integer resonators as switchable finite-state wavetable oscillators, exact escape maps for discrete agents, and intervention-minimal repairs in finite deterministic transition systems. A finite-state signal may persist after its excitation ends; treating persistence as evidence of an ongoing external cause is an invalid inference in this model. This is a design analogy, not a claim about human interpretation. Do not use this as an industrial shutdown guarantee: physical devices have overflow, noise, coefficient changes and implementation constraints absent here. Storage cost can grow with the disk, and the objective ignores real-time deadlines.
