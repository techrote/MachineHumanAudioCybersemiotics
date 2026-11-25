# The Dial That Cannot Add

**MHAC exploratory expedition #468 — 25 November 2026.** Original mathematical/synthetic work outside the frozen empirical/theoretical selection. Not a clinical or operational priority rule, human experiment, or claim of scientific novelty.

## Question and source boundary

Suppose an auditory interface compresses two ordered machine-state dimensions into a single priority dial. Increasing either dimension at fixed value of the other always increases the intended priority. Does this justify independently calibrating the two dimensions and adding the calibrations? No. Even every proper rectangular calibration experiment can succeed while the full intended ordering has no additive representation.

Source ledger, accessed 2026-11-25 by this agent:

- Arkadii Slinko, *Additive Representability of Finite Measurement Structures*, revised March 2008, author-hosted manuscript, https://www.math.auckland.ac.nz/~slinko/Research/survey5.pdf . Read introduction and section 3, printed pp. 5–7 (PDF indices 5–7 inspected visually), especially definitions 3–4 and Example 2. The source distinguishes cancellation width from cardinality and gives an existing 3×3 counterexample. Our cancellation framework is established measurement theory, not a discovery of the cancellation axiom.
- Peter C. Fishburn (2001), *Cancellation Conditions for Finite Two-Dimensional Additive Measurement*, J Math Psychol 45(1), 2–26, DOI 10.1006/jmps.1999.1285, https://pubmed.ncbi.nlm.nih.gov/11178919/ . Institutional abstract read only, not full paper. It reports f(3,4)=f(4,4)=4 under its cancellation-width definition. Do not claim priority for four-comparison obstructions.
- R. Duncan Luce and John W. Tukey (1964), *Simultaneous conjoint measurement: A new type of fundamental measurement*, J Math Psychol 1(1), 1–27, DOI 10.1016/0022-2496(64)90015-x. Metadata checked at https://cir.nii.ac.jp/crid/1364233269628537728 ; not read as primary text. Historical discovery lead only.

Project boundary: #45 concerns perceptual/semantic independence of multivariate mappings; this expedition instead falsifies an additive *ordinal priority function*, even with perfect discrimination of emitted values. #252 concerns lost unit correspondences, #430 attention allocation. A candidate destructive-query topic was abandoned after reading issue #203 (already implements a related exact state-identification oracle). No empirical source registry, human gate, or canonical manifest changed.

## Model and exact certificate

Let the intended strict total order of cells (i,j) extend the product order of an m×n grid. The proposed score is a_i+b_j with arbitrary real increasing calibrations. A strictly increasing output transformation is irrelevant to ordinal feasibility. Fix a_0=b_0=0 without loss of generality. Write each cell as its row/column one-hot vector f, dropping the two baseline coordinates. If cells c_1,...,c_N are in increasing desired order, construct a matrix A with rows f(c_{k+1})-f(c_k). Existence of a strictly order-preserving additive score is equivalent to Aw>0 and hence, by scaling, Aw≥1.

By the theorem of alternatives, infeasibility is equivalent to a nonzero vector lambda≥0 with A^T lambda=0. Rational certificates exist for this rational matrix. Clearing denominators gives integer multiplicities: each selected comparison insists on a positive increase while the sum of its row and column feature differences is zero. This is a directly checkable cancellation witness. Adjacent comparisons suffice because transitivity supplies all others. This is classical finite additive measurement recast as an executable audit.

## A smallest-grid obstruction and why two levels are deceptive

All strict monotone orders on 2×n grids admit an additive realization. Here is a constructive proof. Normalize the row gap to one. Think of row 0 as starts x_j and row 1 as ends x_j+1 of intervals. Both starts and ends occur in the same order. Set x_0=0. When inserting the next start x_j, the desired order specifies how many previous ends precede it, say k. Choose x_j above x_{j-1} and above the kth earlier end (if k>0), and below the next earlier end (if k<j). The interval is nonempty: ends are increasing, and x_{j-1} was necessarily earlier in the desired order than that next end. Future ends have the prescribed relative order automatically. Repeat. Transposition supplies n×2. Strict monotonicity holds on both axes by construction. Therefore at least three levels on both axes are needed for failure.

The known 3×3 example reproduced by our census has ascending ranks

| | 0 | 1 | 2 |
|---|---:|---:|---:|
|0|1|2|6|
|1|3|4|7|
|2|5|8|9|

Its three comparisons (0,1)<(1,0), (2,0)<(0,2), (1,2)<(2,1) have matching row and column multisets on their two sides. Adding the inequalities gives a strict increase from a quantity to itself. This is the Fishburn example as presented by Slinko, not new prior art.

## A local calibration paradox on 3×4

The census located this exact strict monotone target:

| | 0 | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
|0|1|2|3|6|
|1|4|5|8|9|
|2|7|10|11|12|

Four ascending *adjacent* comparisons obstruct the full score:

- (0,2) < (1,0)
- (1,1) < (0,3)
- (2,0) < (1,2)
- (1,3) < (2,1)

Both sides have identical row and column multisets. Every proper rectangular restriction is nevertheless additive. For the four ways to remove a column, the following explicit integer scores certify all four 3×3 subgrids:

| Retained columns | row scores | retained column scores |
|---|---|---|
|0,1,2|0,5,8|0,2,4|
|0,1,3|0,3,8|0,2,6|
|0,2,3|0,5,8|0,4,6|
|1,2,3|0,3,8|0,2,4|

Two-row restrictions pass by the preceding theorem. Any cancellation witness supported on at most three distinct comparisons uses at most three distinct levels of each coordinate: positivity and marginal balance mean every high-side level occurs also on the low side. Such a witness would fit a proper subgrid, contradiction. Four is thus minimal cancellation width here, even allowing repeated comparisons. The four individual local calibrations are each valid, but the freedom to recalibrate a row or column differently in each test hides the global obstruction. A shared-parameter audit would fail.

## Quantifying an interaction repair

Ordinal feasibility alone has no meaningful absolute magnitude because scaling preserves order. Define a new, deliberately normalized model: score s(c)=f(c)^T w+e(c), require every consecutive rank to have gap at least 1, and minimize epsilon=max|e(c)|. This is the minimum context-dependent adjustment to an additive baseline under a *declared* score margin, not a psychophysical measurement.

Let B be the (N−1)×N first-difference matrix so B e contains consecutive differences. The primal is min epsilon subject to Aw+B e≥1 and |e|≤epsilon. Its dual, via the nonnegative multipliers on rank constraints and the support function of the infinity-norm ball, gives

    epsilon* = max_{lambda >= 0, A^T lambda=0, lambda != 0}
                 sum(lambda) / ||B^T lambda||_1

with maximum over an empty set defined as zero. To see the lower bound, multiply the rank constraints by lambda and cancel A: sum(lambda) ≤ lambda^T B e ≤ epsilon ||B^T lambda||_1. Conversely, LP strong duality applies (feasible finite primal, choose sufficiently large rank residuals) with normalization ||B^T lambda||_1≤1. B^T has no nonzero kernel; the ratio is well-defined. For any nonzero cancellation, triangle inequality gives ||B^T lambda||_1≤2 sum(lambda), so every impossible strict additive order requires epsilon*≥1/2 under the specified margin.

For the 3×4 witness the four disjoint adjacent comparisons force epsilon≥1/2. Attainment: use a=(0,4,8), b=(0,2,4,6), and residual +1/2 at ranks 4,6,8,10,12, −1/2 at all others. The resulting ordered scores are −0.5,1.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,14.5. All successive gaps are at least one. The four disputed pairs tie in the additive baseline, then become strictly separated after repair. The bound is sharp.

The interaction term need not indicate a psychological interaction; it is a mathematical cost of this specified representation and separation requirement. Other models (lexicographic, nonadditive, structured contextual rules, vector-valued cues) are alternatives, not conclusions.

## Exhaustive experiment

Native Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0. Run laboratory.py with Python (SciPy/NumPy required), redirect stdout to execution.json. All order classifications require a literal integer primal witness or nonnegative integer cancellation vector with exact zero sum in each coordinate. LP only discovers candidate certificates; a floating classification alone is never accepted. The enumeration grows each valid order ideal, adding precisely one minimal remaining cell. Each strict product extension appears once, independently cross-checked against the rectangular hook-length count (mn)! / product(m+n-i-j-1). Transitive subgrid restrictions are tested with the same exact certificates. Maximal proper subrectangles suffice, because restrictions preserve additivity.

| Grid | All orders | Additive | Nonadditive | Fail globally, pass all 3×3 | Fail globally, pass all proper rectangles |
|---|---:|---:|---:|---:|---:|
|2×2|2|2|0|—|—|
|2×3|5|5|0|—|—|
|2×4|14|14|0|—|—|
|2×5|42|42|0|—|—|
|2×6|132|132|0|—|—|
|3×3|42|36|6|0|6|
|3×4|462|295|167|8|8|
|3×5|6006|2583|3423|190|0|
|Total|6705|3109|3596|—|—|

For all 173 nonadditive orders on 3×3 and 3×4, the normalized interaction repair cost was separately optimized and certified by exact rational feasible primal and cancellation lower-bound witnesses with equal objectives.

| epsilon* | 3×3 | 3×4 |
|---|---:|---:|
|1/2|4|68|
|2/3|2|56|
|3/4|0|4|
|5/6|0|28|
|9/10|0|2|
|1|0|9|

All assertions passed in the completed bounded census. An attempted 4×4 exhaustive extension hit the execution timeout before a complete receipt; it is excluded, not a negative mathematical result. The 3×5 finding that no globally failing order passes all proper rectangles is finite-grid evidence only and cannot establish a universal local-to-global theorem. The code verifies certificates during execution; it does not claim to retain every individual certificate in the summary file. No human population, participant data, or independent review.

## Original acoustic witness and experimental design

witness.py uses a pure standard-library rational checker to verify the explicit 3×4 counterexample, its four local fits and the attaining repair. It renders four pairs of short tapered sine tones (8000 Hz sampling, PCM16 mono), mapping score to frequency by 220+35s Hz. Both members of each pair are equal in the additive baseline; the second exceeds the first by 35 Hz in the repaired score. The audio is a mathematical sonification, not an empirical demonstration of a listener's ranking. It is generated on demand, not committed as binary material.

A future synthetic evaluation could generate rank tables and compare a two-level factorial audit, separate local fits, a shared additive fit and an explicit context-dependent renderer. Predeclare allowable rank margins, comparison noise/ties, and the rule for withholding a scalar when a cancellation witness exists. If a lawful human study is later authorized, elicit comparisons of compound cue meanings independently of the acoustic score, retain ties and disagreement, test cue comprehension separately from priority ranking, and use held-out contexts. Reject the additive model when repeated, reliable comparisons jointly violate its constraints. Do not infer a true human priority order from a generated score. Do not use this construction to prescribe safety arbitration.

**Interpretation:** separability of individual signs and representability of their joint priority are distinct. A semantic score that sums urgency and consequence is an additional convention, not a consequence of either field being intelligible or monotone. If a system must preserve the axes, a vector-valued report may be more honest than a forced scalar. A scalar is not ruled out: a nonadditive or deliberately policy-defined score can be appropriate, provided the semantics and tradeoffs are explicit.

**Fiction:** A clerk calibrated the upper dial against every three positions of the lower one. Each card was correct. When the cards were bound, the clerk found four comparisons that summed to nothing. He left the two dials on the instrument, and wrote the arbitration rule beside them rather than under either needle.

## Checkpoint and scope

Base 495a98ca12bae467a507031f04931aa4254b1866 on main; fresh branch mhac-468/dial-cannot-add. Initial reconciliation covered 292 branch names, 100 recent open issues and 100 open PR snapshots; targeted duplicate searches and root authorities (AGENTS, RAG, PROGRAMME, runbook, integrity, validation, project foundations) read. Previous PR #459 exact-head run 45536035218 completed successfully. No other branch or canonical file modified. AI-assisted by one agent; source and analytical review are not independent peer review. Keep issue open and PR draft pending exact-head repository CI and integrator review. Native standalone checks passed; full repository checkout/validation not performed in this run. No human action necessary to reproduce this synthetic work.
