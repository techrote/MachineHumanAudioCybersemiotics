# The Dial That Remembers Its Retreat

**Issue #364 — exploratory mathematical expedition, 2026-11-24.** Agent-generated derivations and synthetic tests; no claim of mathematical priority, no human validation, no production or canonical research changes.

## Question

A dial controls a bank of latching binary voices. Each voice turns on when the input crosses its upper threshold and turns off when it drops below its lower threshold. If two instruments agree throughout a full excursion from minimum to maximum and back, have we measured their memory? What if all single-reversal experiments also agree to a very small tolerance?

The answer depends on whether calibration is exact, and on the number of surviving turns of the input history. Exact first reversals identify the stipulated model. Approximate first reversals can fail spectacularly when the input remembers a deep succession of retreats.

## Source ancestry and evidence boundaries

* [Gutowski, Varga and Kákay, *Fast, Preisach-like characterization of hysteretic systems* (2005), arXiv:cond-mat/0506177](https://arxiv.org/abs/cond-mat/0506177). Read the rendered text §§1–3, especially §2.2, equation (2) and the paragraph immediately after it. The authors explicitly establish nonuniqueness of a Preisach map inferred from its major loop; they obtain uniqueness only in their constrained model. They also note that their simplified model's minor-loop reproduction was not tested. This expedition does **not** rediscover major-loop nonuniqueness as a new scientific result.
* [Daniels, Zeinali, Overboom, Curti and Lomonova, *Constrained B-Spline Based Everett Map Construction for Modeling Static Hysteresis Behavior* (2024), arXiv:2410.02797](https://arxiv.org/abs/2410.02797). Read rendered text §§1–6, particularly §2 equations (1)–(3), §4's constraints and §5's descriptions of first and higher reversal validation. The authors represent the classical model through a cumulative Everett map and recover a density by differentiation; they report residual deviations even in their constrained model. The figures were not independently inspected or reanalyzed; no numerical performance claim is imported. The attempted direct HTML route was inaccessible; the arXiv abstract route returned section text.
* [Aistleitner and Dick, *Functions of bounded variation, signed measures, and a general Koksma–Hlawka inequality*, Acta Arithmetica 167 (2015), 143–171](https://doi.org/10.4064/aa167-2-4). Publisher abstract only; discovery context for the discrepancy/variation analogy below, not relied on for any proof or claim about the theorem's exact hypotheses.

All reading and calculations are by one ChatGPT agent in this run. No independent reviewer, source image audit, empirical extraction or claim-register admission. The discrete proofs below are self-contained.

## Model: a finite relay ensemble

There are n input boundaries, indexed 1,...,n; input levels are integers 0,...,n. Relay (i,j) has upper boundary i and lower boundary j, with 1 <= j <= i <= n. At level x it is set ON if x >= i, OFF if x < j, otherwise retains its prior state. Thresholds can equivalently be halfway between adjacent input levels. Initially x=0 and all relays are OFF. Assume nonnegative fixed weights W(i,j) summing to one; outside the triangle weights are zero. Output is total ON mass, in [0,1]. There are no interactions, noise, rate effects, inertia or unknown initial states. A sample-to-sample jump represents a monotone traversal.

Define the joint cumulative table F(u,v)=sum_{i<=u,j<=v} W(i,j), zero if either index is zero.

A full ascending sweep outputs R(u)=F(u,n); a descending sweep from positive saturation outputs C(v)=F(n,v). Thus major-loop observations are exactly the two threshold marginals. They do not specify how the upper and lower thresholds are paired. The two systems may even agree on the integrated area between major branches; that area is already determined by the major observations.

A first reversal from 0 to u then down to v<=u outputs F(u,v): a relay must have switched on and not yet switched off. For v>=u, F(u,v)=R(u) by triangular support. These conventions are for ON mass, not the bipolar magnetization or Everett loss of a particular physical paper.

## Result A — exact probe budget

All F entries are known from the major loops except

    1 <= v < u < n.

There are d=(n-1)(n-2)/2 such entries. Measuring those d first-reversal endpoints identifies all W by the mixed difference

    W(i,j) = F(i,j)-F(i-1,j)-F(i,j-1)+F(i-1,j-1).

This is an exact worst-case minimum number of additional scalar linear probes, not a minimum number of physical sweeps (one sweep may provide several endpoints). Proof of lower bound: every one of the d interior entries is a free perturbation coordinate. An arbitrary perturbation supported there vanishes on the boundary; its mixed difference has zero row and column sums and vanishes above the triangular support. The mixed difference is invertible on cumulative tables with zero lower boundaries, so the perturbation space has dimension d. At a strictly positive triangular baseline all sufficiently small such perturbations preserve nonnegativity. Fewer than d scalar linear measurements leave a nonzero kernel and hence two admissible indistinguishable models. This also applies to a deterministic adaptive choice of linear measurements: follow the transcript on the baseline, choose a kernel perturbation of the realized probes, and it follows the same transcript. Finite, noiseless, exact real-valued observation; not an encoding argument against arbitrary nonlinear probes.

For n=2 major loops already suffice. At n=3 one missing interior scalar suffices. For sparse supports or particular observed margins, the admissible dimension can be smaller; no claim every major loop requires d probes.

## Result B — sharp worst-case ambiguity for a nested history

The active set has a staircase representation. For analysis, extend the weight table by zeros to the square. Maintain virtual row widths w_i (nonincreasing in i). On a rising input x, set widths for i<=x to n; on a falling input x, clamp every width to x. This union/intersection rule agrees with every physical relay on the triangle by its switch rule. The virtual active set is a union of nested-origin rectangles, with r maximal corners (u_l,v_l), u_1>...>u_r>0, v_1<...<v_r. Some portions may lie outside physical support; the bound uses the number of corners of the chosen representation, and one can take a smaller valid representation if available. r=0 is empty. It is the number of surviving staircase steps, not the raw count of direction changes.

For any two normalized ensembles P,Q with identical major loops, their outputs a,b at this staircase obey

    |a-b| <= r/(r+1).

Proof: partition the row axis into r+1 consecutive groups, from the widest active interval to the empty group, and the column axis into r+1 bands cut at the r widths. Empty groups are allowed. Index both from 0 to r. Then the active event is h=I+J<=r-1. P and Q share the marginals of I,J, hence E_P h = E_Q h. Assume a>=b. On the active region h<=r-1; everywhere h<=2r. On the inactive region h>=r; everywhere h>=0. Therefore

    r(1-b) <= E_Q h = E_P h <= (r-1)a+2r(1-a).
    (r+1)a-rb <= r.
    a-b <= (r-b)/(r+1) <= r/(r+1).

Swap P,Q for the other sign. This proof is unaffected by triangular support.

Sharp witness: let m=r+1 and place all upper thresholds at m+i, all lower thresholds at j, for i,j=1,...,m. Each ensemble has m relays of equal mass 1/m, one in every row and column.

* P: cells (i,m-i) for i=1,...,m-1, plus (m,m).
* Q: cells (i,m+1-i) for i=1,...,m.

Indices in this list are local to the separated m-by-m block. Both have identical uniform threshold marginals. Drive the same input from zero through successive peaks 2m-1,2m-2,...,m+1 and troughs 1,2,...,m-1. The final active event on this block is i+j<=m, exactly r corners. P has r active relays and Q none. Thus the bound is attained at every r>=1. At r=1 this recovers a sharp one-reversal gap of 1/2.

This gives the first surprise: arbitrarily many relays may have the same complete major loop and nevertheless attain output gaps as close to one as desired under the same history.

## Result C — arbitrarily close complete first-reversal maps, nearly opposite output

For the same witnesses, all cumulative rectangles differ by at most one relay. In local coordinates, for 1<=u,v<m, the two prefix counts are

    P count = max(0,u+v-m+1)
    Q count = max(0,u+v-m).

On outer boundaries the counts are identical by the marginals. Hence the supremum absolute first-reversal error is exactly 1/m, while the nested-history gap is (m-1)/m.

This is a nonuniform stability obstruction: no modulus of continuity tending to zero in the first-reversal sup error can bound arbitrary-history output uniformly across all grid sizes and history complexities. The counterexample uses increasingly many distinct relays and increasingly deep histories. It does NOT show discontinuity at a fixed grid or fixed number of corners; one can rescale all thresholds into a common finite input interval, but their spacing then decreases.

At m=64 the worst single-reversal difference is 1/64 (1.5625 percentage points of full scale), whereas one nested input ends with a 63/64 (98.4375 percentage points) disagreement. Both models are nonnegative, normalized, and exactly major-loop equivalent. This is an adversarial construction, not a typical calibration error.

## Result D — exact history-complexity amplification constant

Let epsilon=max_{u,v}|F_P(u,v)-F_Q(u,v)|. All square cumulative entries are determined by physical first reversals and major-loop entries. Inclusion-exclusion over the staircase gives

    output = sum_{l=1}^r F(u_l,v_l)
             - sum_{l=1}^{r-1} F(u_{l+1},v_l).

Consequently

    |a-b| <= (2r-1) epsilon,

for r>=1, and output difference zero at r=0. Combining with Result B under exact major-loop equivalence gives min(r/(r+1),(2r-1)epsilon). We do not assert this combined bound is attained at every epsilon.

The coefficient 2r-1 cannot be reduced even when major loops are identical. Construct a signed cumulative table H on a separated block with m=r+1 rows and columns, zero everywhere except +1 at the r convex corners (m-l,l) and -1 at the r-1 concave corners (m-l-1,l) for l=1,...,r-1. All nonzero entries are interior. Take its mixed difference D; it has zero margins and is supported on the block. Let L=sum D_+ = sum D_- >0 and set P=D_+/L, Q=D_-/L. Both are nonnegative probability ensembles with matching marginals; F_P-F_Q=H/L. The same realizable staircase as above yields |a-b|=(2r-1)/L and epsilon=1/L. Thus the ratio is exactly 2r-1. The executed family has L=4r-2, but that additional simplification is not needed in the proof.

The bridge into numerical integration is a finite discrepancy argument: cumulative rectangle error bounds a signed measure on rectangles, whereas a staircase indicator has a signed rectangle decomposition with 2r-1 terms. This resembles discrepancy-times-variation reasoning in quadrature. It is an interpretation of our elementary proof; we have not established a general continuous Hardy–Krause theorem or claimed priority.

## Synthetic experiments and reproducibility

Run from this directory using Node.js 18+:

    node laboratory.cjs > rerun.json
    node laboratory.cjs output-directory

The second invocation also writes four original PCM WAVs. Compare rerun.json with execution.json. The core has no external dependencies. It was executed in the tool's JavaScript runtime; source and receipt were committed then read back and compared byte-for-byte. Native Node filesystem CLI and full repository tests were not executed in this run. The numerical claims use exact small integer masses rather than floating comparisons; normalization is algebraic.

The census enumerates every nonnegative integer allocation of four units across the triangular support for n=2,3,4; a BFS of reachable virtual staircases stores one witness input for each (input, widths) state. For each ensemble, an explicit relay simulator, cumulative rectangles and direct row sums agree on all states. It also reconstructs every ensemble from major margins plus just the additional probes of Result A. Within each major-loop equivalence class every unordered distinct pair is tested on every reachable state for both bounds. This is independent algorithmic comparison by the same agent, not independent review.

| n | ensembles | major classes | classes with ambiguity | reachable states | matched pairs | pair/path checks |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 15 | 15 | 0 | 4 | 0 | 0 |
| 3 | 126 | 105 | 20 | 8 | 22 | 176 |
| 4 | 715 | 490 | 164 | 16 | 310 | 4960 |

Totals: 856 ensembles; 12,075 first-reversal checks; 12,508 history comparisons; 332 matched pairs and 5,136 pair/path comparisons. The two sharpness families were separately checked at r=1,2,3,4,5,8,15,31,63. All assertions passed. These finite censuses are checks of the code and the stated formulas, not proof by extrapolation or observations of physical equipment.

## Original audio: the retreat organ

A single 250 Hz triangle oscillator is amplitude-modulated by the simulated ON mass, with an identical short linear envelope at each 80 ms slot. 8 kHz mono signed 16-bit PCM, integer waveform and deterministic quantization. Use the same input trace, gain and renderer in both worlds; no normalization per recording. The experiment is a sonification of model outputs, not a magnetic recording.

| WAV | bytes | FNV-1a 32-bit fingerprint |
|---|---:|---|
| major-a | 42284 | 4478b173 |
| major-b | 42284 | 4478b173 |
| nested-a | 19244 | 7ec5470b |
| nested-b | 19244 | 33646de5 |

The major pair was compared byte-for-byte; nested pair differs. Fingerprints are reproducibility conveniences, not cryptographic identities. The nested m=8 input levels are 0,15,1,14,2,13,3,12,4,11,5,10,6,9,7. The final active masses are 7/8 and 0. WAV arrays were generated in memory; the CLI can write them to disk. No human listening or acoustic perceptual result is claimed.

A speculative instrument would allow upper threshold marginal, lower threshold marginal and their coupling to be composed independently. A performer could exchange coupling matrices while preserving a routine calibration sweep, then play nested trajectories that disclose the hidden memory. A second performer could choose when to erase the latent state with a saturation excursion. The composition is made of paths through memory rather than static note values.

## Exaptation, failures and a falsifiable proposal

Hysteresis is commonly introduced to keep an alert from flickering around a threshold. In a bank of such indicators, independently documenting activation and release distributions loses the pairing, even if both distributions are exact. A machine-state receipt that certifies only major response curves could be completely insufficient for paths that matter in a workshop or software interface.

Provisional engineering contract: keep the threshold coupling or exact first-reversal map; for an approximate map, record its pairwise error bound, the maximum staircase complexity of the permitted input history, the reset convention and the current memory-state provenance. If the map is compared against a reference rather than directly against another candidate, use the triangle inequality to convert separate errors to a pairwise bound. For a decision with a known threshold, refuse a guarantee if the resulting output interval intersects the threshold. A system can request a targeted nested-history probe instead of more major-loop sweeps. Do not implement device control from this proposal.

Contrary cases and negative sediment:

* Exact first-reversal data **does** identify this finite classical nonnegative relay ensemble. More exact data is useful; the counterexample is to approximate uniform certification without a history bound, not to the method itself.
* The r bound is on effective staircase corners, not elapsed time or raw reversals; saturation can erase previous memory.
* Signed weights, relay interactions, rate dependence, unmodeled state, stochastic switches and drifting thresholds invalidate the stipulated bounds. The cited 2005 paper itself discusses signed effective weights. These are not universal material laws.
* Real first-reversal sampling is finite, with noise and interpolation; an empirical residual on a finite set is not an established sup norm. A physical grid-resolution or smoothness constraint may change conditioning; not investigated.
* The major-loop equality is within an ideal model. No claimed implications for listener affect, cognition, learning, perceived urgency or Brier's theory. One potential future design hypothesis would compare a displayed memory-complexity certificate with a conventional static alarm calibration under safe simulation; participant testing requires the separate authorization and methods gates.

## Fiction — the surveyor of retreats

The surveyor had two dials built to the same specification. Both rose by the same amounts as he turned the handle clockwise; both fell by the same amounts as he returned it. He signed the certificate.

The apprentice placed a chalk mark just below the top of the scale, another just above its bottom, then moved each mark inward by a small amount. She repeated the motion between them until they almost met. One dial sang at its fullest volume, the other was quiet.

He asked which turn had broken the certificate. She answered that not one had. The certificate had been about excursions; the instrument was about what survived them.

## Reconciliation checkpoint

Base main: 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity, validation, experiment and human-gate documents. Nested AGENTS files under research and research/expeditions returned 404. Reviewed the returned 100 recent open issue records (search result cap), 105 open PR snapshots, and all 241 returned branches. Targeted Preisach/hysteresis/reversal-curve issue search returned none. Existing research on quantized decay, silent state evolution, reversal grammars and contextual thresholds is related but does not make a claim about the pairing of relay thresholds in the inspected titles. No complete novelty audit of all draft branches; no novelty claim. Previous expedition #357 exact head b1432782fd8e9e56e32b9dbfe510d8c1c5563b6e had completed successful PR workflow 45430044751.

Issue #364 was created, read back (no comments), and a fresh branch created at that base. Only these three additive files are owned. No shared manifests, claims, corpus gates or other branches changed. Remaining: native Node CLI execution; repository validation and exact-head CI; critique by a separate reviewer/integrator; no human data or scientific acceptance. This is intentionally partial draft research, not a completion claim for the formal programme. No human action required for the computational next step.
