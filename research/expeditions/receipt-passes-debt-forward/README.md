# The Receipt That Passes Its Debt Forward
## Exact one-tick streaming frontier, Fibonacci growth and the distinction between individual and collective completion

**Refs #370 · 24 November 2026 · mathematical and synthetic expedition.** ChatGPT GPT-6.2, single AI author/self-review. No empirical participant, acoustic intelligibility, physical restoration, production policy, Track E/G acceptance or priority claim.

## Contents

1. Excavation — recover the explicit unresolved one-tick question.
2. Model — characterize deadline-valid prefix fibres.
3. Local frontier — exhaustively certify three transition types.
4. Exact optimum — derive Fibonacci counts and an infinite causal policy.
5. Termination — separate abrupt stop, one-tick flush and two-tick flush.
6. Evidence and exaptation — reproducibility, source bounds and falsification.

## 1. Excavation and adversarial disagreement

[The Receipt That Needs a Wider Second Tick (#355)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/24e2500e7d0926aae5dcfa67c703c68c24cb38d3/research/expeditions/receipt-wider-second-tick/README.md), §5, left uniformly one-tick streaming unresolved. [The Receipt That Cannot Retire Its Debt (#363)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/ecd920aeba3d5d3fdf82921e7c79880715ea29d8/research/expeditions/receipt-cannot-retire-debt/README.md), §§2–5, proved that a narrow source-bearing slot cannot retire all existing ambiguity. It explicitly did not prove that the same historical item remains ambiguous. The missing question is whether debt can migrate forward indefinitely while meeting *each item's* deadline, and whether this permits compression.

The answer for the ternary pentagon is yes, but with a strict rate penalty relative to the two-tick-delay paired code. This preserves both earlier results; it falsifies an extrapolation from the closed-horizon obstruction to all deadline-limited streams. It also recovers #339's distinction between knowing a previous state and being able to restore it; no actuator is assumed.

Reconciliation: fetched live main twice, 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity and validation inspected. Reviewed 100 returned open issue titles and 100 returned open PR titles (capped searches, not exhaustive totals); targeted one-tick issue search returned an unrelated forecast issue; matching branch search empty. Read exact #355/#363 reports, #362 issue and zero comments; #363 open draft at ecd920ae, run 45438599206 successful. Recent #365/#367/#369 concern hysteresis, syntax and redundant-frame consistency, not this scope. Created #370, read its body and zero comments, branched from live main. This is a separate expedition, not a core-programme advancement.

## 2. Model and deadline fibres (mathematics)

Use X=Z/5Z, with five possible interventions: action a collapses a+1 (mod 5) onto a and otherwise preserves the original. The decoder sees the action and its result at each tick; the encoder sees only the original prefix. Every original sequence and action sequence is legal independently in the sense of support, not a probability model. Tags are deterministic, causal, and drawn from {0,1,2} at known boundaries. No future input or decoder-observation feedback is available.

After tick t the decoder must recover x_1,...,x_(t-1) exactly for every legal observation. The current x_t need not yet be recoverable. A finite prefix objective counts distinct tag strings after n source-bearing ticks, with only this deadline required, not final recovery of x_n. A source-free final slot will be considered separately. The infinite-stream objective is the exponential growth of the number of possible length-n tag prefixes, not average code length or physical throughput.

Let G=C5. Two distinct histories can share all intervention observations iff their coordinates are equal or adjacent in G, i.e. they are adjacent in the strong graph power. A tag fibre is the set of source histories producing a particular tag prefix. Deadline validity is equivalent to: every confusable pair in that fibre agrees in its first t-1 coordinates. Thus partition a fibre by the exact older prefix p=(x_1,...,x_(t-1)). Within a group the possible last values form a nonempty subset S_p of X. Between distinct groups there are no confusability edges. Distinct histories from different groups cannot become confusable by appending another coordinate.

Classify each S_p by its chromatic number: type 1 for an independent set, type 2 for a proper subset with an edge (bipartite), type 3 for the full pentagon. Empty type 0 is reserved for absent output branches. A nonempty fibre has type k=max_p type(S_p). The initial empty history behaves as a single type-1 row.

At the next tick assign a ternary row r_x(y) for every x in each S_p, where y is the newly arriving original. The previous item's deadline is satisfied exactly when, for every edge x~x' in S_p, r_x(y) differs from r_x'(y') whenever y=y' or y~y'. No such constraint is required between different old groups or within one row, because the new item is not yet due. Each output branch has new type equal to the maximum of the types of its individual row masks {y:r_x(y)=tag} over all old histories. This characterizes the legal transition without assuming that the current tag decodes either item alone.

## 3. Complete finite local frontier (mathematics with exhaustive certificate)

For each fibre type, the sorted triple of child types has the following componentwise-minimal possibilities, with 0 meaning absent:

| Parent type | Minimal sorted child triples | Meaning |
| --- | --- | --- |
| 1 | (0,0,3), (0,1,2), (1,1,1) | Wait, split, or fully distinguish |
| 2 | (0,3,3), (1,2,2) | Lag, or transfer reduced ambiguity |
| 3 | (3,3,3) | Three persistent full-pentagon branches |

These are exact Pareto minima, not all feasible triples. For a singleton, edge, and full pentagon respectively, certify them by a complete finite enumeration, not a guessed stationary policy.

Certificate procedure: let S be {0}, {0,1}, or X. A column c assigns a tag to every x in S for a fixed new value y; enumerate all 3^|S| vectors, retaining those proper on edges of S. Connect columns c,d if c(x) != d(x') for every ordered adjacent pair x~x' in S. A valid local matrix is exactly a length-five closed walk of columns (choose c0,...,c4 and require each consecutive pair including c4,c0 compatible). This checks equal-y via the proper-column filter and adjacent-y via the walk. For every walk, classify each row's tag masks, take columnwise maxima over rows, sort the resulting triple, retain the distinct triples, and discard dominated ones. No symmetry reductions are needed. The lab enumerates all rooted oriented walks:

| S | Proper columns | Closed walks | All sorted triples |
| --- | ---: | ---: | --- |
| singleton | 3 | 243 | 003,012,022,111,112,122 |
| edge | 6 | 306 | 033,122,123,222,223 |
| C5 | 30 | 1530 | 333 |

This is a finite computer-assisted lemma; its complete algorithm and small inputs are supplied, rather than claiming a separate human proof of the enumeration. For arbitrary type-1 groups, restricting to one row gives the lower bound and repeating a singleton witness across the group attains it. For type-2 groups, restrict to any edge for the lower bound and extend an edge witness using any proper bipartition of the group; both sides occur in a group with an edge. For type-3 groups the full pentagon is present and the table applies. Align tag labels between groups to attain the same maximal triple: for a lower-type group use a restricted higher-type witness (constant across independent rows, bipartition for type 2, or simply restrict the full-pentagon assignment). This preserves all constraints. A group of maximal type guarantees the lower bound on each sorted global triple. Thus the type abstraction loses no information relevant to optimal descendant counts.

Explicit witnesses, columns y=0,1,2,3,4:

    type 1, 003:  2 2 2 2 2
    type 1, 012:  2 2 2 2 1
    type 1, 111:  2 1 2 1 0

    type 2, 033:  2 2 2 2 2
                  1 1 1 1 1

    type 2, 122:  2 2 2 2 0
                  1 0 1 1 1

For type 2's second witness, tag 0 is shared only at y=4 and y'=1, which are distinct and nonadjacent; the other tags are disjoint across rows. For type 3, assign every row the scalar colour of x under 0,1,0,1,2. All three children have a full row. Note the surprising rigidity: from a type-3 fibre *every* legal transition gives 333, not just this witness.

## 4. Exact finite-prefix and infinite-stream rates (mathematics)

Let V_k(h) be the minimum number of distinct descendants after h additional source-bearing ticks from a type-k fibre, preserving every due deadline. V_0(h)=0 and V_k(0)=1 for k>0. Children have distinct prefixes and independently selectable continuation policies. The preceding exact frontier yields, with a=V_1(h), b=V_2(h), c=V_3(h):

    V_1(h+1) = min(c, a+b, 3a)
    V_2(h+1) = min(2c, a+2b)
    V_3(h+1) = 3c.

Monotonicity a<=b<=c follows either by restricting to the smaller representative group or directly by induction in these recurrences, so dominated sorted triples may be discarded. Horizon one yields (1,2,3). For h>=1 the exact solution is

    V_1(h)=F_(2h),  V_2(h)=F_(2h+1),  V_3(h)=3^h,

where F_0=0, F_1=1, F_(j+2)=F_(j+1)+F_j. To verify induction, a+b=F_(2h+2), a+2b=F_(2h+3); b<=2a gives a+b<=3a. Also 3^h>=F_(2h+2) and 2*3^h>=F_(2h+3) for h>=1 (base cases and F_(j+2)<=3F_j for j>=2). Thus the indicated sums attain the minima. Starting from the empty prefix (type 1), the exact finite-prefix optimum after n>=1 ticks is F_(2n). These horizon-tuned minima need not be simultaneously attained by one infinite encoder: at n=1 the optimum is one tag, leaving full type 3, which thereafter must branch three ways forever.

A single horizon-independent causal policy instead always uses 012 on type 1 and 122 on type 2. It never enters type 3. If A_n,B_n count type-1 and type-2 prefixes, starting with A_0=1,B_0=0,

    (A_(n+1), B_(n+1)) = (A_n+B_n, A_n+2B_n).

Consequently A_n=F_(2n-1), B_n=F_(2n) for n>=1, and T_n=A_n+B_n=F_(2n+1). The policy is implementable causally: at each tick the encoder knows its source history, the prior tag string and the public deterministic policy; it can enumerate the finite corresponding fibre from all hypothetical prefixes, choose the stipulated row, and emit a tag. No actual future values or intervention observations enter that computation. The decoder can enumerate candidates using its observations and tags and returns the common due prefix. This is an executable existence construction, not an efficiency claim for that brute-force implementation.

By the finite lower bound, every valid infinite encoder has T_n>=F_(2n). The stationary witness achieves F_(2n+1), so the sharp exponential rate is phi^2=(3+sqrt(5))/2, approximately 2.618033989 distinct-prefix growth per source, or log2(phi^2) approximately 1.388 bits of log-cardinality per origin. This lies strictly between the offline/two-delay pentagon rate sqrt(5) and the zero-delay/closed rate 3. The finite lower bound and witness establish the optimal liminf and limsup exponential rates; no stochastic distribution or entropy-rate claim is involved.

## 5. Termination: individual deadlines do not imply collective closure

A source-free flush after n arrivals must fully distinguish the remaining row masks. Since different older groups are nonconfusable, the exact flush alphabet of a type-k fibre is k, by independent proper colouring and reuse across groups. This is precisely the one-additional-source-tick minimum descendant count V_k(1)=k, although the resulting targets differ. Therefore the exact n-origin transcript optimum with uniformly one-tick deadlines and one source-free ternary flush is V_1(n+1)=F_(2n+2). Moreover the stationary policy above achieves it for *every* announced stop, without advance knowledge of n: its total is A_n+2B_n=F_(2n+2).

| Origins n | Abrupt closed, zero ambiguity | One-tick deadline + flush | Two-tick max delay + flush (#363, even n) |
| ---: | ---: | ---: | ---: |
| 2 | 9 | 8 | 5 |
| 4 | 81 | 55 | 25 |
| 8 | 6561 | 2584 | 625 |
| 16 | 43046721 | 5702887 | 390625 |

The middle column is neither a full block-code optimum nor the abrupt-closure theorem. At an arbitrary source-bearing cut, the stationary policy retains at least one ambiguous last-item fibre. Every older item is nonetheless exactly known by its deadline. The earlier propagation lemma is vindicated: debt survives somewhere, but it is not tied to any one item. For example the first 012 row produces tag 2 on both original 0 and 1; action 0 collapses both. Stopping immediately cannot recover that item. With the next source-bearing slot, the edge witness separates confusable continuations of those distinct older values; any remaining ambiguity concerns the new value.

Changed assumptions: two-tick delay admits the five-tag pair code with a flush, as #363 proves; abrupt zero-ambiguity stop forces scalar 3^n under ternary cap; decoder feedback, shared rather than independent actions, restricted support, noise, or acceptable-remedy rather than exact reconstruction change this model. The larger graph/general-delay rate problem remains open here. A prefix-cardinality saving does not establish a reduction in physical slots, acoustic bandwidth, expected encoded bits, energy, computation or retention costs. Abrupt failure can prevent the flush. No design recommendation to retain more sensitive history follows.

## 6. Evidence, exaptation and reproducibility

Source comparison, one AI reader, accessed 2026-11-24: H. S. Witsenhausen, *The zero-error side information problem and chromatic numbers*, IEEE TIT 22(5), 592–593 (1976), DOI 10.1109/TIT.1976.1055607, publisher abstract https://ieeexplore.ieee.org/document/1055607/ read; it establishes the graph-colouring connection and possible block savings. H. Palaiyanur and A. Sahai, *Sequential decoding for lossless streaming source coding with side information*, arXiv:cs/0703120 (2007), https://arxiv.org/abs/cs/0703120, abstract read: streaming side-information codes are assessed via probability of error decaying with delay, unlike this exact zero-error support and prefix-cardinality objective. Y. Kaspi and N. Merhav, *Zero-Delay and Causal Single-User and Multi-User Lossy Source Coding with Decoder Side Information*, arXiv:1301.0079, https://arxiv.org/abs/1301.0079, abstract read: average distortion, sequential encoding and instantaneous codes, not our one-tick fixed ternary frontier. Offline pentagon rate is inherited from #355/#363's source-bounded use of Lovász's theorem. No full-text priority audit performed; no claim to originate graph coding, Fibonacci recurrences or streaming coding.

Design hypothesis: distinguish **age of the oldest unresolved obligation** from **existence of any outstanding obligation**. An interactive instrument may meet every per-event latency while never reaching an all-clear state until a drain is admitted. Test these properties separately: compare due-prefix recovery at every tick, complete recovery under abrupt interruption, and complete recovery after an explicitly source-free flush. Do not add the next transaction merely to simulate successful shutdown. Separately audit known support, trust, feedback and real restoration capability. This is a synthetic falsification contract, not an accepted design.

Artistic score (symbolic): three timbres 0,1,2; the first event emits 2 except at state 4, when it emits 1. In a type-2 fibre the two rows above form a two-voice score: timbre 0 is shared only in two nonadjacent positions. Play the last unresolved distinction in a source-free coda. No audio rendering or listener data asserted.

Fiction: the archivist's report says every object is catalogued by the next appointment. The auditor asks whether the archive is empty of unfinished business at any arbitrary instant. The archivist offers a last appointment with no visitor. The auditor accepts it as a separate operation, not as evidence that the archive had already closed.

Run `node lab.js` in this directory. The lab enumerates all local matrices via closed walks of columns, independent of the hand-written row witnesses. It checks BigInt recurrences through horizon 50, constructs actual source-prefix tables for the stationary and horizon-tuned policies through six ticks, checks equal-prefix causality, and tests all direct action/result observations through four ticks. A separate flush procedure properly colours the final row masks and checks full decoder recovery. Exact synthetic counts from runtime execution of the lab committed at f027d871abd1214eb533419ff03270a2d5dea427:

| Check | Count |
| --- | ---: |
| Rooted local closed walks | 2079 |
| Dynamic-programming horizons | 50 |
| Direct deadline decoder observations | 1644550 |
| Direct complete flush decoder observations | 406900 |
| Within-tag source pair comparisons | 2084446 |
| Prefix causality checks | 43935 |
| Tested cuts with an abrupt-stop ambiguity witness | 27 |

The stationary prefix counts through six arrivals are 2,5,13,34,89,233; finite-prefix minima 1,3,8,21,55,144; exact flushed counts 3,8,21,55,144,377. Overlapping synthetic activities, not independent experiments. The exhaustive finite lemma, algebra and implementation share one author. Native Node/full checkout validation and independent substantive review are outstanding; use Refs #370 and retain draft status pending qualification. No shared manifests or other workers' files modified.
