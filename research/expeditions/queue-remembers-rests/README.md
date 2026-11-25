# The Queue That Remembers the Rests

Refs #592 · 2026-11-25 · Exploratory deterministic mathematics, software and original synthetic score. Not a selected Track E/G finding, safety qualification or human experiment.

## The anomaly

Consider a repeating score of 24 slots. Active slots inject two work units into a server that can process one unit every slot. Rest slots inject none. Work is retained unless a finite buffer clips it. Measure backlog immediately after service, not before service.

Both scores have active run lengths 4,4,2,2 and rest lengths 4,4,2,2 as unordered inventories. Score A pairs each active run with an equal rest: 111100001111000011001100. Score B pairs the same active sequence with rests 2,2,4,4: 111100111100110000110000. Both have exactly twelve active and twelve inactive slots, four episodes, maximum active and inactive length four, and identical circular histograms through order three. Their peak backlogs are respectively four and six. A four-unit buffer loses zero units per period in A and two in B.

The distinction is that a rest is not necessarily a reset. An active period can leave unfinished work that changes the meaning of the next active period. This extends the duration-fibre research in #562 from local and individual episode properties to cumulative workload. It does not model attention as a proven single-server queue.

## Model and workload lemma

Let a mixed cyclic binary word have A ones and B zeros, with A <= B. Net input x_i is +1 for a one and -1 for a zero. The infinite-buffer dynamics are q_i = max(0, q_(i-1)+x_i). Use the least periodic nonnegative solution; starting from zero and running two periods obtains its values on the second period. There is no arbitrary inherited backlog in this contract. For A>B no bounded periodic infinite-buffer solution exists.

Unrolling the recursion from zero yields the maximum of zero and all suffix sums since initialization. In a periodically extended record, any suffix longer than a period can be shortened by removing a complete period whose sum is nonpositive. Thus the least periodic q_i is the maximum of zero and every suffix sum of length at most one period ending at i. It satisfies the recursion, and every nonnegative periodic solution dominates it by iterating the recurrence backward one period. Its peak P is precisely the maximum sum over cyclic intervals of length at most one period. At A=B, this also equals the range of the ordinary cumulative-sum walk including zero, because the complement of a negative interval is positive with the opposite sum.

This is a finite, exact special case of deterministic workload/arrival-curve reasoning, not a claim to replace general network calculus. Given an actual ordered record, the recurrence solves the problem in linear time.

## Exact peak range with a full local histogram

Fix R alternating runs of each symbol, A active slots and B inactive slots, with A<=B. Fix r>=2 and let a=r-1. Restrict every run of both symbols to length at least a, so A and B are at least R*a. All such words have identical full order-r circular histograms: each mixed word of length r can contain at most one transition, each specific single-transition pattern occurs R times, and the homogeneous counts are A-R*a and B-R*a. Shorter histograms follow by marginalization. Conversely this histogram excludes every run shorter than a (it would generate a two-transition pattern of length at most r), and fixes A, B and R.

**Theorem 1.** The exact attainable set of peak backlogs within this histogram is every integer from ceil(A/R) through A-(R-1)*a, inclusive.

Proof. Some active run has length at least ceil(A/R), and the backlog grows by one each slot during that run. A positive maximum interval can be extended to whole active runs at both endpoints and includes k consecutive active runs and their k-1 full intervening rests, with 1<=k<=R. The chosen active runs have total length at most A-(R-k)*a; the intervening rests have length at least (k-1)*a. Subtracting gives the upper bound A-(R-1)*a. For any integer M between the endpoints, choose one active run of length M, distribute A-M among the other R-1 runs with each between a and M, then choose each following rest at least as long as its active run. This is possible because B>=A. Every episode drains entirely, so the resulting peak is exactly M. For R=1 the single value is A. This proves no integer holes and both endpoints. QED.

The formula is restricted to the all-long-run histogram class; no general claim is made that arbitrary mixed higher-order histograms have this same range. In particular the full histogram does not tell us whether a rest empties the queue.

## Exact adverse ordering with complete run inventories

Now retain both complete sorted run multisets, not merely their histogram. Let u_1>=...>=u_R be active lengths in descending order, and v_1<=...<=v_R rest lengths in ascending order. Totals remain stable.

**Theorem 2.** The largest possible peak over all circular alternating arrangements of the two inventories is

    P_max = max over k=1,...,R of (sum of the k largest u - sum of the k-1 smallest v).

Proof: any maximal interval contains k whole active runs separated by k-1 rests, and its surplus is bounded by the indicated sums. For the maximizing k, put those active runs in one consecutive group separated by exactly those rests, then append the remaining runs alternating around the circle. The chosen interval attains the bound. QED.

Sorting and prefix sums solve this adversarial problem in O(R log R) time. It is not necessary to reconstruct or enumerate every compatible history.

Corollary: even if the longest active run M is known and every rest lasts at least a, P can reach R*M-(R-1)*a. Take all active lengths M, R-1 short rests a, and a final rest of length R*M-(R-1)*a. Totals balance. Individual duration bounds alone are not an accumulated-work bound. In this family the long final rest is essential; moving it merely rotates the score.

## The optimization asymmetry: benign ordering is strongly NP-complete

**Theorem 3.** Given the complete unordered positive and negative run inventories of a balanced cycle and an integer capacity H, deciding whether an alternating arrangement exists whose peak is at most H is strongly NP-complete. This remains true for every fixed observation order r>=2 even when every run is at least r-1 and the complete order-r histogram is supplied.

Proof of membership in NP: a certificate lists the two run permutations. Check multiset equality and total balance, then compute the maximum minus minimum cumulative sum at run boundaries. The extrema occur at boundaries because each run is monotone. This is polynomial in the binary-encoded run inventory. The same verification works for unary input.

Reduction from 3-PARTITION (Garey and Johnson, 1979, Theorem 4.4 and SP15). Take 3m positive integer items b_i with target B, total mB, and strict B/4 < b_i < B/2. Here B denotes the partition target, not the number of rest slots. Fix any positive integer a. Make 3m active lengths a+b_i, 2m short rests of length a, and m long rests of length a+B. Both totals are 3ma+mB. Set capacity H=a+B.

If a 3-partition exists, arrange each triple as three active runs separated by two short rests, followed by one long rest. Starting empty, the post-active peak in the group is a plus its partial item sum; at the third active endpoint the peak is a+B. The subsequent long rest drains exactly. Thus the cyclic arrangement has peak H.

Conversely, in any arrangement the m long rests delimit m nonempty groups of active runs separated internally only by short rests. An interval from the beginning of the first active run to the end of the last active run in any group has surplus a plus the sum of its items. If the peak is at most a+B, every group has item sum at most B. The total mB forces every group sum to be B. The strict item-size inequalities then force exactly three items in each group. These groups constitute a 3-partition.

The construction adds a fixed constant to the numbers and uses linearly many runs; its size remains polynomial on the strongly restricted 3-PARTITION instances. It proves strong NP-hardness, and membership gives completeness. Choosing a=r-1 also makes every run sufficiently long and every arrangement share exactly the same order-r histogram by Theorem 1. Supplying this redundant histogram cannot remove the hardness; for fixed r it is computable in polynomial time. QED.

The negative result is specifically about selecting the best ordering given inventories, not evaluating a known score or computing the worst possible peak. NP-completeness is conditional evidence against a general polynomial-time exact optimizer, not proof that every instance is difficult.

Concrete witnesses: with B=15 and a=2, items 4,4,5,5,6,6 admit two triples and have exact optimum 17. Items 4,4,4,6,6,6 have the same total but no triple can sum to the odd target; the exhaustive optimum is 18. Both are balanced and have 84 total slots, six episodes, and identical full order-three histograms, although their complete active run inventories differ. Their worst-case peaks can be computed cheaply by Theorem 2. The executable census retains both yes and no instances.

## Capacity, loss and negative sediment

For a buffer of integer post-service capacity C use q_i=min(C,max(0,q_(i-1)+x_i)); the clipped positive excess is lost work. Use the least periodic solution, obtained by two periods from zero. One way to verify this is to compose the monotone clamp-affine maps over a cycle: the resulting map is a clamp of q+S between two fixed endpoints, with S=A-B<=0, so its image of zero is already a fixed point. The infinite-buffer case follows from the suffix lemma.

If C>=P, the least infinite-buffer periodic trajectory fits, so no loss occurs in the capped least solution. If C<P, choose an interval with net input P. Summing conservation of work on the interval, the change in queue is net input plus unused service minus lost work. Since the change in queue is at most C, interval loss is at least P-C. The interval is no longer than a period, so total periodic loss is at least P-C>0. Consequently capacity sufficiency is exact, not just a worst-case inequality. Multiple disjoint overload episodes can make the total loss larger than this lower bound. When A=B, over a complete period lost work equals unused service. No claim is made about the distribution of individual job delay or a real human response.

Rejected shortcuts:
- Equal arrival totals, episode counts, longest durations and all local order-three counts do not imply equal queue peaks (24-slot witness).
- Even exact unordered active/rest run inventories do not identify the peak.
- Optimizing the worst possible arrangement and finding the best arrangement have different complexity. A single sorted statistic cannot solve the latter unless P=NP.
- Infinite-buffer and finite-buffer traces are not interchangeable. Clipping changes the subsequent state; equal post-clip maximum does not imply equal loss.
- A real listener is not a constant-rate service mechanism. Prioritization, abandonment, overlapping activity, variable workload, recovery, and adaptation could all invalidate the model. The mathematical reduction cannot establish human capacity.

## Computational qualification and art

Run node laboratory.cjs from this directory; the JSON output reproduces execution.json. The JavaScript core was executed in the tool isolate. It enumerates 4,720 labelled stable mixed binary circles of lengths 2..12, 16,314 finite-capacity checks, 226 complete run-inventory classes and 157 all-long-run histogram classes across the tested lengths/orders. It checks the literal maximum-interval calculation against queue dynamics, all attained histogram peak sets against Theorem 1, and maxima against Theorem 2. A separate census enumerates 31 valid two-bin 3-PARTITION item profiles (26 yes, 5 no), for padding a=1,2,4, and 15,465 distinct arrangements after fixing a long rest at the circular boundary. Every decision agrees with the triple oracle.

A separate native standard-library Python implementation ran twice, with byte-identical execution JSON and WAVs, independently reproducing all aggregate counts and examples. It uses literal per-slot queue simulation, explicit circular substring counters and prefix-range evaluation of balanced run permutations. Both methods are same-agent cross-checks, not independent human review. The native package is provided in the run's downloadable artifacts, not in the repository at this checkpoint. Native JSON SHA-256: 0f3d5075e81e9adb7005d9959fd60cacf4182881990b573e7815c62ce12bf6e7.

Four original 2.4-second 8 kHz mono PCM16 recordings: two arrival scores use 250/500 Hz tapered tones for rest/active; two backlog scores use 220+60*q Hz for the post-service workload. The arrival scores have identical symbol inventories and digital energy. They are not byte-identical, and no perceptual equivalence is claimed. The backlog rendering makes the difference between a short rest and an actual reset explicit. The live performance idea is a movable-rest sequencer with an audible backlog oscillator and a separately audible loss counter. Such a real-time instrument is speculative; the executable score and exact verifier are implemented.

## Sources and interpretation

S1. Jean-Yves Le Boudec and Patrick Thiran, Network Calculus: A Theory of Deterministic Queuing Systems for the Internet, Springer LNCS 2050. Author-hosted book and online edition: https://leboudec.github.io/netcal/ and https://leboudec.github.io/netcal/latex/netCalBook.pdf . Read section 1.4.1, Theorem 1.4.1 and its proof (printed pp.22–23; PDF indices 39–40 visually inspected), and the nearby statement of tightness in section 1.4.2 (text). This establishes the relevant arrival/service deviation framework. Our cyclic run inventory proofs and reduction are self-contained, not attributed to the book.

S2. Michael R. Garey and David S. Johnson, Computers and Intractability, 1979, section 4.2 Theorem 4.4 and Appendix A3.2 SP15 (ISBN 0-7167-1045-5). Read the indexed original book text around the strong NP-completeness theorem and exact SP15 statement at https://perso.limos.fr/~palafour/PAPERS/PDF/Garey-Johnson79.pdf ; screenshot retrieval failed due to document size, so no visual confirmation of these pages. MIT Demaine lecture 2 corroborates the strong-hardness framing: https://courses.csail.mit.edu/6.892/spring19/lectures/L02.html (lecture description read, not video). Only the established 3-PARTITION complexity is imported; the cyclic scheduling reduction is derived here. No full book reading or priority claim.

S3. MHAC #562, branch mhac-562/long-note-ledger, full issue and report read and comment collection empty. Earlier run redistribution determines individual longest episodes; the present target is a cumulative signed interval functional and its rearrangement complexity. Targeted searches for queue backlog, buffer overflow, Lindley, network calculus, waiting time and traffic burst found related interaction/grammar work but no exact overlapping theorem. This is not an exhaustive novelty search.

The design hypothesis is to distinguish arrival-state sonification from outstanding-work sonification and to communicate the queue's measurement timing, service assumptions, loss and reset state. A listener may need a state receipt even when the current event is correctly decoded. Test first with synthetic schedulers of varying service rate and known actual backlog, against arrival-only and longest-run-only controls. A later human protocol would need independent validation and attention to competing explanations such as cue salience. Conventional queueing and combinatorics already explain the mathematical effect; no additional explanatory contribution from Brier's cybersemiotics is established.

Fiction: A clerk counts the notes and counts the rests. Every performance receives the same certificate. The apprentice moves a rest from after the first phrase to after the last. The clerk's pile of unanswered letters grows before the final silence. He has counted the pauses but not what they had time to finish.

## Checkpoint

Base main 495a98ca12bae467a507031f04931aa4254b1866, read live. Read AGENTS, README, RAG, programme, runbook, integrity, validation; checked 100 recent open issues and 100 open PR results and enumerated 356 branch entries; read #562 issue/comments/report; newly scoped #592 with no comments. Previous corridor head fb03aaf8caa7683e31912578332de6bf1ab9a0c0 returned successful completed workflow status. Native full repository checkout attempt failed DNS resolution, so full local repository validation is not claimed. Standalone checks completed. Draft and Refs only pending exact-head CI and integration critique. No other branch or canonical manifest modified. AI-assisted original research and code, same-agent review; external review absent. No human action required to reproduce. No restricted source files committed.
