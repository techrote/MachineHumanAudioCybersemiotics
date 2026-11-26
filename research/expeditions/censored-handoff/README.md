# The Bell That Hides Its Runner-Up

Issue #654 · 26 November 2026 · exploratory mathematics and synthetic DSP. Single ChatGPT agent, no independent review, scientific-priority claim, participant evidence, or canonical programme adoption.

## The anomaly

Two machine subsystems have latent readiness times A and B, both integer slots 1..n. An arbiter sounds only the first ready subsystem and records its identity and time; ties receive a distinct symbol. A separate isolated test may record each subsystem's entire marginal readiness law. Even all these ideal population receipts need not identify how soon the second subsystem would have been ready in the same episode. This is a competing-risks observation contract, not a model of causal intervention unless the readiness times remain invariant under suppression.

Example: with probability 1/4 each, model I has (A,B)=(1,3),(2,4),(3,1),(4,2). Model II has (1,4),(2,3),(4,1),(3,2). Each has uniform solo marginals, first winner/time equally distributed among A1,A2,B1,B2, maximum time equally distributed among 3,4, and mean gap 2. In I the gap is always 2; in II it is 1 or 3 equally often. The probability of a runner-up within one slot is 0 vs 1/2. Every receipt is truthful, and no measurement noise or sampling error is required.

## First-only ambiguity and sharp marginal bounds

Let q_ij=P(A=i,B=j). The first archive supplies upper row sums u_i=sum_{j>i} q_ij, lower column sums l_j=sum_{i>j} q_ij, and diagonal d_i=q_ii. These are disjoint nonempty cells groups: n diagonal and 2(n-1) strictly triangular groups. On a strictly positive population their joint fibre has dimension n²-(3n-2)=(n-1)(n-2), by independently redistributing the masses within the groups. This is also the maximum dimension over all feasible archives.

For a threshold h in 1..n, let M_h=P(min(A,B)>h). Then the sharp bounds are

    M_h+l_h <= P(A>h) <= M_h+sum_{j<=h}l_j     (h<n).
    P(A>n)=0.

Proof: if the minimum exceeds h, A does too. If B wins at h, A necessarily exceeds h; if B wins earlier, A may be on either side. Put all losing A at j+1 for the lower endpoint or at n for the upper endpoint; preserve all the other groups. The analogue for B exchanges u and l. These are discrete-time versions of the classical competing-risks identification problem; no novelty asserted for the basic bounds. With an infinite time horizon a censored runner-up can be arbitrarily late. A finite deadline must not be inferred from winner-only records.

## Even knowing both solo laws leaves a quadratic ambiguity

Assume the solo marginals r_i=sum_j q_ij and c_j=sum_i q_ij are known for the same latent population. The upper triangle then has known row sums u_i and column sums c_j-d_j-l_j. The lower triangle independently has known column sums l_j and row sums r_i-d_i-u_i. The graph of each triangle is a connected bipartite Ferrers graph on 2(n-1) nonisolated vertices, with n(n-1)/2 edges. A spanning tree consists of row 1 and column n in the upper triangle, and their transposed counterpart below.

**Theorem.** For n>=2, the maximum dimension of the combined fibre is (n-2)(n-3). This dimension is attained at any strictly positive table. Exactly (n-2)(n-3) extra fixed scalar cell-probability receipts are necessary and sufficient to identify every table.

Proof: reveal q_ij for 1<i<j<n and its lower-triangle transpose. For each upper row i>1, subtract the known interior cells from u_i to determine q_i,n. For each upper column j, subtract its now-known cells from c_j-d_j-l_j to recover q_1,j. Transpose for the lower triangle. These interior coordinates are freely variable in a sufficiently small neighbourhood of any strictly positive table: varying an interior cell by epsilon and the opposite corner (1,n) by epsilon while subtracting epsilon from (i,n) and (1,j) preserves all row and column sums. Every interior coordinate has its own independent rectangle trade. Thus the fibre is locally full-dimensional in precisely those coordinates. Any collection of fewer scalar linear measurements has a nonzero kernel on this interior space; sufficiently small positive and negative perturbations are both admissible. This proves the fixed linear receipt lower bound, not a lower bound for a paired log of entire episodes, which measures many cells at once. n=2 and n=3 are degenerate zero-dimensional cases when both solo laws are known.

**Corollary (which targets are already identified?).** A linear statistic sum_{i,j} w_ij q_ij is universally identified by the archive and marginals iff the cost w is row-plus-column additive separately on each triangle. Diagonal costs are unrestricted. Necessity follows by testing every rectangle trade: w_ij+w_1,n=w_i,n+w_1,j in the upper triangle (transpose below). Sufficiency follows from the known row and column sums. This gives a target-specific test; full-table reconstruction is unnecessary for many questions.

For instance E|A-B|=E A+E B-2E min(A,B) is already identified. Even the complete maximum-time marginal is identified: P(max<=h)=P(A<=h)+P(B<=h)-P(min<=h). But neither statement identifies the gap distribution. A joint target can be measured directly instead of buying the complete table. For arbitrary known marginals and first receipts, sharp bounds on any linear gap objective reduce to two independent finite transportation linear programs, on the two triangles with the margins above. This is a formulation, not a claim that a general LP solver was implemented.

## Exact handoff-gap frontier in a uniform family

Let n=2m. In each episode choose the winner W=A or B with equal probability; its readiness I is uniform on 1..m. The runner-up has readiness m+J, where J is also uniform on 1..m conditional on W, but the coupling of I,J is unconstrained. Both solo laws are uniform on 1..2m, and the first archive and maximum-time distribution are fixed. The admissible couplings are scaled doubly stochastic matrices for each winner. Define G=m+J-I.

For each integer 0<=g<=2m-1 the sharp range is

    max(0,g-m+1)/m <= P(G<=g) <= min(m,g)/m.

For g<m, a short gap requires I>=m-g+1, whose probability is g/m. Match the last g early slots to the first g late slots via the circular permutation J=1+((I-1+g) mod m); each of those last g rows then has G=g (g=0 use identity), and all other rows have larger gap. The identity yields zero. For g>=m, a gap >g requires I<=2m-g-1; its probability is at most (2m-g-1)/m. Put h=g-m+1 and rotate forward by h modulo m, obtaining G=m+h=g+1 on the first m-h rows and smaller gaps on the rest (h=m use identity). Identity attains upper endpoint one. Mix endpoint couplings to fill each interval. These bounds hold without assuming permutation-valued coupling; the row-capacity argument works for all couplings.

The mean is m exactly. The sharp variance range is 0 to (m²-1)/3: Var(J-I)=2 Var(I)-2 Cov(I,J), and Cauchy–Schwarz bounds the covariance in magnitude by Var(I). Identity attains zero and reversal J=m+1-I attains the upper bound. Variance is in squared slots. At g=m-1 the short-handoff probability can range from 0 to (m-1)/m, approaching a complete disagreement despite identical solo laws, first logs, maximum-time laws and mean gaps. This is a population result, not a finite-sample estimate. At g=m the lower bound is 1/m, and at g=2m-1 the gap is always within deadline.

A companion negative result: even testing the product-model first archive against measured solo laws cannot certify independence. On a positive independent table with n>=4 apply any nonzero sufficiently small interior rectangle trade. The archive and solo laws remain exactly the same, but the joint table is no longer the product of the marginals. Independence can be falsified by incompatible observations; compatibility is not identification.

## Exaptation: the suppressed duet

A first-only synthesizer plays a 350 Hz or 550 Hz pulse in the winner's channel. The two latent schedules may generate byte-identical first-only WAV files while their paired shadow scores differ. The companion native witness renders m=4, eight enumerated episodes; constant gap 4 vs three gaps 3 and one gap 7 per winner. At a three-slot deadline the observed winner-only scores are indistinguishable while the latent handoff success fraction changes from 0 to 3/4. The offline specimen does not play real alarms, recruit listeners or measure physical readiness. A shadow observer logs both candidate events without changing arbitration. Separate solo experiments suffice for marginals only if population and intervention consistency hold.

Interpretation: a truthful report about the first event is not a statement about the absence, urgency or readiness of another event. Possible interface contract: event identity, observation policy/version, first-versus-shadow flag, suppression reason, source timestamp, episode ID, actual paired readiness receipts, explicit missing/undefined fields. A controlled comparison could change only the paired logging policy and evaluate a predeclared deadline loss. No production recommendation or human effect is established. For an actual machine, suppressing a winner might change scheduling, resource availability or the latent loser itself; then a joint potential-readiness table is not identified by even shadow logging under a different intervention. Do not call hypothetical times observed facts. Directly logging both times, if technically feasible and noninterfering, is the essential simpler comparator.

Related MHAC: #545 addresses selection-dependent calibration of a fixed binary outcome, not a hidden second readiness time; #458 addresses renewal-window ambiguity and episode counts, not a paired table. The connection is interpretative, not evidence for Brier's account. Ordinary probability and transportation geometry explain the results. No additional explanatory contribution from cybersemiotics is established.

## Source ledger and reproducibility

- A. Tsiatis, *A nonidentifiability aspect of the problem of competing risks*, PNAS 72(1), 20–22 (1975), DOI [10.1073/pnas.72.1.20](https://doi.org/10.1073/pnas.72.1.20). Read the complete [PMC abstract](https://pmc.ncbi.nlm.nih.gov/articles/PMC432231/) on 26 November 2026, particularly its summary of Theorem 2; source explicitly describes nonidentification of net survival from crude cause-specific survival absent an independence assumption. PDF route returned a browser check; no full-text proof reading claimed. Classical ancestry, not validation of acoustic transfer.
- A. V. Peterson Jr., *Bounds for a joint distribution function with fixed sub-distribution functions: Application to competing risks*, PNAS 73(1), 11–13 (1976), DOI [10.1073/pnas.73.1.11](https://doi.org/10.1073/pnas.73.1.11). Read the complete [PMC abstract](https://pmc.ncbi.nlm.nih.gov/articles/PMC335828/) on 26 November 2026, including scope of Theorems 1–3. PDF route remained in download preparation. Sharp bounds under fixed subdistributions are established prior work. The present finite paired-marginal dimension and deadline family are derived here; priority is not asserted.
- J. A. De Loera and E. D. Kim, *Combinatorics and Geometry of Transportation Polytopes: An Update*, [arXiv:1307.0124](https://arxiv.org/abs/1307.0124) (2013 preprint), abstract-level reading on 26 November 2026. Mathematical background on constrained nonnegative tables; the explicit spanning-tree reconstruction and rectangle proof above are self-contained. No claim that the paper establishes our specific handoff statements.

All readings and derivations are by the same AI agent; none are independently verified by a human. These are exploratory discovery leads outside the frozen empirical corpus; do not enter them as selected empirical studies.

Run `node laboratory.cjs` in this directory. Exact integer arithmetic checks 608 reconstructed positive tables (n=2..20), 62,016 rectangle trades and mean-gap invariance checks, 6,688 survival profiles with constructed endpoints, and all 46,233 permutations of sizes 1..8 (725,758 gap threshold checks). The integer counts are within exact JS safe-integer bounds. [Execution receipt](execution.json) records results from the actual function executed before committing its source. Separate local Python 3.13.5 witness checked exact Fraction nullities for n=2..12 and the same permutation space via a different histogram algorithm; decoded all 288 stereo time slots, reproduced all four PCM files and receipt byte-for-byte twice. Native package delivered separately; not committed in this PR. All are same-agent computational checks, not peer review.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; 387 branch entries, 100 recent open issues and 100 recent open PR results; targeted searches for competing risks, censoring, renewal, waiting time, hazard rate and survival. Read AGENTS, README, RAG, programme, runbook, integrity, validation, target issue #654 and comments, #545 full report and #458 issue/comments. Prior own PR #649 exact-head workflow 45750842429 completed successfully. Native git access failed DNS. Keep this isolated issue-scoped PR draft pending integrator and independent critique; do not touch shared manifests or merge into active mainline.

*Fiction:* the clerk counts the bells that arrive first. The apprentice asks which bell would have arrived second. He shows her two perfect timetables, each correct separately. She asks to hear the bells together.
