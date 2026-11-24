# The Clock That Cannot Shuffle

**Issue #260 · 24 November 2026 · Exploratory mathematical and artistic work, outside Track E/G.** No claim of new mathematical priority, observed machine timing, human comprehension, or adopted design policy.

## A missing dimension of chronology

MHAC-X003 (issue #183, draft PR #185, branch head 3fcdf4f0e3a950bc9e4a95bbf24ad5f0477dbe6d) establishes the reversal lemma for incomparable vertices of a recorded dependency DAG. Its README explicitly leaves reliable physical clock evidence as a different question. I read that README, its EVIDENCE.md, the complete issue and its empty comment list. The new problem is not to recover causality from sound, but to reconstruct feasible physical chronologies under correlated timestamp uncertainty. The two models are complementary, not interchangeable. Do not change X003.

A local timestamp can be accurate as an elapsed-time measurement while its clock's absolute origin is unknown. An entire sequence then slides rigidly along time. Treating each event as individually movable forgets shared offset identity. Even a graph of all universally true pairwise precedences can lose restrictions on the joint history.

## Exact model and two-clock theorem

There are k nonempty streams. Stream i has strictly increasing integer timestamps t[i,j] and unknown real additive correction x[i], constant over the recording. The hypothetical common coordinate is t[i,j]+x[i]. No drift, rate error, quantization uncertainty, causal message edges, synchronization bounds or ties are assumed. The offset vector is unrestricted and only its differences matter; set x[0]=0. A chronology is a strict total ordering of all labelled events. A word of stream labels determines a unique chronology because local order is fixed.

For two streams of lengths a,b, the order changes only at an offset difference equal to a cross-stream timestamp difference. Let X={A_i-B_j}. Each of the |X|+1 open intervals between these thresholds induces one distinct chronology: crossing any threshold reverses at least one labelled pair and no pair can reverse twice as the offset increases. This proves exactly |X|+1 orders, at most ab+1, attained when all cross differences are distinct.

Compare with the binomial(a+b,a) interleavings admitted by the local-chain partial order. Every individual cross-stream pair can occur in either order by sliding the streams, so the partial order of universally true comparisons is precisely the disjoint local chains. Yet when both have two events, at most five of six interleavings can occur. Example A=(0,1), B=(0,2). A1 B1 B2 A2 would put a two-unit interval inside a one-unit interval. Equal spans forbid both strict nestings and leave four orders. This refutes the claim that all linear extensions of the known pairwise relations necessarily remain physically possible. With a one-event stream, all interleavings are possible.

## Three-clock theorem

Write x=x[B]-x[A], y=x[C]-x[A]. The comparison boundaries are three parallel families:

- vertical x in X={A_i-B_j};
- horizontal y in Y={A_i-C_l};
- diagonal y-x in Z={B_j-C_l}.

Let p=|X|, q=|Y|, r=|Z|; define T as the number of distinct (x,y) in X×Y such that y-x belongs to Z. The exact number of strict chronologies is

    R = 1+p+q+r+pq+pr+qr-T.

Proof: start with the p vertical lines, giving p+1 regions. Each of the q horizontal lines crosses all p vertical lines in distinct points, adding p+1 regions. Each diagonal crosses p+q lines at p+q distinct points except for coincident crossings at vertical-horizontal intersections. It adds one more region than its number of distinct crossing points. Parallel diagonals do not meet each other. Summing subtracts exactly T. Each open cell has a fixed sign for each pairwise comparison and hence a strict chronology. Conversely the set inducing a fixed chronology is an intersection of open half-planes and is convex, so cannot contain two disconnected cells. Thus cells and chronologies are in bijection, including unbounded cells. Boundary ties are excluded, not broken arbitrarily.

For fixed stream sizes a,b,c the sharp maximum is

    Rmax = 1+ab+ac+bc+(ab)(ac)+(ab)(bc)+(ac)(bc)-abc.

For generic timestamps, the difference sets have sizes ab, ac, bc. A triple intersection always occurs for a shared event triple (A_i,B_j,C_l). All other triple intersections require a nonzero linear relation among the independent timestamp coordinates and are excluded by genericity. Under these conditions the abc forced intersections are distinct. Generic timestamps exist even in integers: assign distinct increasing powers of two to the events, taking each stream in order. A spurious equality of differences or triple concurrence would express a nonzero combination of distinct powers with coefficients in {-1,0,1}; the largest power dominates the sum of all smaller powers. (The statement concerns the relevant cross-family equations, not arbitrary polynomial equalities.)

To see why degenerate cases cannot exceed the generic count, select one offset witness inside each of their finitely many open cells. All finitely many strict comparisons at these witnesses have positive slack. Perturb timestamps sufficiently little to preserve all those comparisons and all within-stream strict orders, while avoiding the finitely many nontrivial linear equalities above. Each original order survives. The formula is therefore a global upper bound, not just a generic expectation. It is attained.

For equal lengths n the maximum becomes 1+3n²+3n⁴-n³, versus (3n)!/(n!)³ chain interleavings. More generally k fixed clocks have at most M=sum_{i<j} n_i n_j comparison hyperplanes in dimension k-1. The ordinary hyperplane bound sum_{j=0}^{k-1} binomial(M,j) follows inductively by inserting one hyperplane: new regions are bounded by the number of cells cut on it, an arrangement in one lower dimension. This bound need not be sharp for our structured arrangement; it does show polynomial growth in equal stream length at fixed k versus exponential growth of all chain interleavings.

## The three-clock splice: all pairwise histories fit, the whole history does not

A=(0,1), B=(0,1), C=(0,2). Proposed chronology:

    A1 C1 B1 A2 C2 B2

Each restriction to two streams is possible with a separate offset assignment:

| Pair | Projected chronology | Corrections (first, second) |
|---|---|---|
| A,B | A1 B1 A2 B2 | 0, 1/2 |
| A,C | A1 C1 A2 C2 | 0, 1/2 |
| B,C | C1 B1 C2 B2 | 0, -3/2 |

But let their first adjusted timestamps be a,b,c. The full order implies a<c, b<a+1, and c+2<b+1. Therefore c<b-1<a, contradicting a<c. Three strict inequalities furnish a compact refusal certificate. The pairwise witnesses have incompatible shared corrections; independently feasible pair projections are not a global witness.

Minimality within this model: two clocks trivially reduce to the one pair. For three clocks, if one has only one event, first realize the proposed projection on the other two clocks, then place that single event in its designated open gap (including either unbounded end gap) by freely choosing its offset. Thus a pairwise-feasible but globally impossible example needs at least two events per clock, and this six-event example attains the minimum. The same insertion argument rules out a smaller example with extra singleton clocks. No physical paradox: the impossible order is only an invalid hypothetical reconstruction.

## Exact executable oracle and census

For successive events (u,a) then (v,b) in a proposed word we need x[u]-x[v] < b-a. Integer timestamps allow exact reduction to nonstrict difference constraints: write z[i]=k*x[i], and require z[u]-z[v] <= k*(b-a)-1. The equivalence concerns feasibility, not equality of solution sets.

Proof: a real solution of all strict constraints implies every directed cycle's sum of original right-hand sides is positive. For a simple cycle of length l<=k this sum is an integer >=1, so the scaled nonstrict cycle weight is >=k-l>=0. Every directed cycle decomposes into simple cycles, including loops. Therefore the scaled system has no negative cycle and has a solution via shortest paths from a zero-weight super-source. All distances are integers. Conversely any such solution divided by k satisfies the original strict constraints. Adjacent comparisons suffice by transitivity. Bellman–Ford checks the system, subtracts the first distance to fix the gauge, and explicitly rechecks the returned order. This is a finite exact feasibility algorithm for the declared bounded-integer input range; no floating epsilon or optimizer tolerance.

The JavaScript core was executed in a tool-provided V8 isolate on 24 November 2026. No Node CLI invocation or full repository test run is claimed. The second algorithm counts planar cells from sets of threshold values without using Bellman–Ford or enumerating words. Cross-checks and receipt are in [laboratory.js](laboratory.js) and [execution.json](execution.json). Both algorithms were implemented by one AI assistant, not independent human review.

| Experiment | Actual result |
|---|---:|
| Two-clock profiles with both gaps in 1..8 | 64 |
| Two-clock word checks | 384 |
| Three-clock profiles with gaps independently in 1..8 | 512 |
| Three-clock word checks | 46,080 |
| Globally feasible words | 25,272 |
| Pairwise feasible but globally infeasible words | 1,008 |
| Generic length triples 1..3 per clock | 27 |
| Count discrepancies / assertion failures | 0 |
| Explicit malformed-input refusals | 3 |

Three-clock profiles are labelled and each includes all 90 local-chain shuffles. Exact feasible count distribution: 30 orders (8 profiles), 42 (12), 44 (156), 51 (72), 53 (264). The census has only tiny integer gaps, not a probability model for physical timing. Generic three clocks with three events each admit 244 orders, not 1,680. The other 1,436 are impossible under those particular exact elapsed-time constraints. Three one-event clocks admit all six; degeneracy never increases the count; independently uncertain event timestamps would be a different model.

To reproduce with Node:

    node research/expeditions/clock-that-cannot-shuffle/laboratory.js build/clock-that-cannot-shuffle

The optional file-output wrapper writes a JSON receipt and two generated WAVs, which are disposable and not committed. Core arithmetic and bytes were actually run; filesystem wrapper remains unexecuted. The oracle has no claim of production scalability.

## Acoustic exaptation: the cut-and-spliced sextet

Original 8 kHz mono PCM16, integer pulse oscillator, fixed equal presentation slots, two pitches per stream. Each event has a stable pitch independent of its slot. The score for the impossible splice and one legal order (A1 A2 B1 B2 C1 C2) each contain the same six note motifs. Their bytes differ: both are 9,644 bytes, FNV-1a fingerprints 5a4063b9 (impossible) and 34e9cd39 (possible); direct byte inequality also checked. The legal order has correction witness (0,4/3,8/3).

The word-to-sound mapping represents a chosen *presentation order*, not the physical time intervals. Both scores are playable by the instrument, including the impossible history. Neither asserts the underlying times. That is the point: representational fluency can conceal physical infeasibility. A later instrument could retain elapsed duration as a rigid per-voice pattern, letting the composer slide whole voices through offsets rather than freely reorder notes. Its arrangement regions would be discrete compositional regimes; crossings produce ties. This is a speculative musical interface, not demonstrated human perception.

## Interpretation, source ledger and transfer limits

**Source A:** Leslie Lamport, *Time, Clocks, and the Ordering of Events in a Distributed System*, CACM 21(7), 1978, 558–565, DOI 10.1145/359545.359563. Author-hosted PDF https://lamport.org/pubs/time-clocks.pdf . Read and visually inspected printed pp. 558–559 (PDF indices 0–1), Introduction and The Partial Ordering, including the three defining conditions and discussion of logical clocks. This is passage-level, not complete paper reading. Lamport's causal order is distinct from numerical physical time; our additional restrictions arise from measured-interval assumptions, not Lamport's theorem.

**Source B:** Mills et al., RFC 5905, June 2010, *Network Time Protocol Version 4: Protocol and Algorithms Specification*, https://www.rfc-editor.org/info/rfc5905/ . Read §8 four-timestamp equations on p. 29 and §9 dispersion discussion on p. 36 in the RFC Editor HTML. Those equations motivate the distinction between clock estimates, delay and uncertainty. Our toy does not implement NTP, model drift or claim to infer actual offsets. Under a simplified exchange with fixed offset theta and nonnegative forward/reverse delays f,r, the two timestamp differences are theta+f and theta-r; hence their midpoint differs from theta by (f-r)/2. That elementary algebra is our contextual observation, not a new NTP result.

**Source C:** Sylvie Corteel, David Forge, Véronique Ventos, *Bijections between affine hyperplane arrangements and valued graphs*, arXiv:1403.2573, https://arxiv.org/abs/1403.2573 ; version displayed dated 11 March 2014. Read HTML rendering §§1–2 and §4 opening through the region/NBC correspondence. These sections identify arrangements x_j-x_i=g with integral gain graphs. Our clock thresholds are an instance of that established framework. The planar formula and explicit size-bound proof above are independently reconstructed special-case calculations; no priority claim or literature-wide novelty search.

**Engineering hypothesis:** retain clock domain, local elapsed intervals, calibration epoch, offset/drift assumptions, message dependencies, and the single shared feasible-offset region in a chronology receipt. A projected pairwise receipt should disclose which unknowns were existentially reselected. If a downstream query depends on one specific ordering, supply a joint witness or refusal. Add measured synchronization bounds and known causal constraints before assessing actual logs. The present unconstrained-offset model cannot certify a physical order from a real system, handle drift, model simultaneous events, or establish listener inference. If intervals are not known reliably, the entire feasible set must change. A simple conservative partial order may be entirely adequate for applications that do not need physical interval reconstruction.

**Fictional afterword:** An editor inherited six notes from three machines. Every two-track mix could be assembled without changing the original tempo. The editor made a six-note recording that passed every two-track audition. The machines refused to perform it together. In the margin of the score, one of them wrote: "You have given us three introductions to the same afternoon. You have not given us an afternoon."

## Repository and integrity receipt

Base observed 495a98ca12bae467a507031f04931aa4254b1866 (main). Read root AGENTS, RAG, programme, runbook, integrity and validation instructions; queried live open issues, paginated branches and recent PR metadata, including #185, #253, #255, #257, #259. The issue-search endpoint returned issue records even with is:pr; direct PR lookups were used for the adjacent active branches. New issue #260 and its empty comments were checked before edits. Read-only related artifact inspection; no dependency on acceptance of draft #185. No other worker branch, protocol, registry, canonical manifest or evidence claim changed. Only this expedition directory is owned. Single ChatGPT assistant performed source consultation, derivations, implementation, execution and self-critique; no subagents, human participants, external review or human validation. Exact-head CI and merge review remain separate acceptance gates.
