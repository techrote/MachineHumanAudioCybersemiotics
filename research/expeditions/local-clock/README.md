# The Clock That Stops Counting

Refs #750, #744, #740, #724 · 27 November 2026 · Exploratory mathematical DSP; one ChatGPT agent performed source reading, proofs, implementation and same-agent cross-checks. No independent critique, human listening evidence, production qualification or novelty priority is claimed.

## A different observation contract

The weighted-clock expedition (#744) attains exact universal cubic quadrature in 10,167 starts plus seven lag samples rather than 170,170 starts for a five-prime noise-balanced example. That is a theorem about a particular invariant/population-statistic contract. What if the receiver has coherent raw samples, knows the component periods and wants their actual signed periodic shapes? A much shorter observation is then possible. Do not call this a faster implementation of the same statistic: it is a different observation.

After demodulating by local sample parity, model the data as

    y(t) = sum_i f_i(t mod p_i) + b + c*(-1)^t + e(t),

where distinct odd primes p_i are known, each arbitrary real periodic component f_i has zero mean, b,c are unknown constant nuisance coefficients, and e is measurement error. The b/c terms cover a constant offset after demodulation and a constant raw-input bias. The original Ramanujan family is a special case f_i(r)=a_i*(p_i*1[r=r_i]-1), with arbitrary nonzero signed amplitudes and unknown independent private residues. A change in origin of the parity clock reverses all signed amplitudes together; relative signs remain identifiable. Timing slips and unknown periods are not covered.

## Sharp linear reconstruction deadline

Let D=sum_i(p_i-1). Each private component has an independent zero-mean residue basis, the differences between each of its first p_i-1 coordinate indicators and its final coordinate indicator. This yields a real design X with D columns; add columns 1 and (-1)^t for nuisance, giving dimension D+2.

Over the complex numbers each private space is spanned by the distinct nontrivial p_i-th roots raised to t. For prime p_i all nontrivial roots have exact order p_i. These root sets are disjoint; adding +1 and -1 leaves them disjoint. The first D consecutive rows (D+2 with nuisance) in the exponential basis form a square Vandermonde matrix. Its determinant is the product of nonzero pairwise root differences; shifting the start multiplies columns by nonzero factors. Thus the restriction to any D (or D+2) consecutive samples is injective and invertible, in exact arithmetic. Any smaller observation count has rank at most that count and cannot universally determine this full linear space. With nuisance, a kernel for N>=2 cannot consist solely of nuisance because 1 and (-1)^t are independent there.

For the five primes (5,7,11,13,17), D=48. The original single-spike templates span each zero-mean residue space, so any linear map that reconstructs every template mixture also reconstructs their full linear span. This lower bound is NOT a lower bound for nonlinear decoding of the narrower template family.

## A nonlinear shortcut: two residuals locate one hidden phase

Keep the first four components completely unrestricted within their zero-mean periodic spaces, but stipulate that the 17-period component is a single shifted Ramanujan template of unknown nonzero signed amplitude. This is a weaker prior than stipulating all five are single-spike templates.

Let E be the forward shift and

    L(E) = product_{p=5,7,11,13} (1+E+...+E^(p-1)).

It annihilates the four nuisance periodic components, by zero mean. Degree d=32. To include both constant nuisance columns multiply by E^2-1, giving d=34. The root set is exactly that of the relaxed nuisance space. With d+2 consecutive samples compute v=((Ly)(0),(Ly)(1)). For a target private residue r define the exact integer signature

    V_r = ((L R_17(. - r))(0),(L R_17(. - r))(1)).

Then v=a V_r. Signed amplitude means phase is identified by an unoriented line, not a ray. If all V_r are nonzero and no two are collinear, the phase and amplitude follow by one determinant comparison and division by a nonzero coordinate. Subtract the recovered 17-period component; the first d residual raw samples reconstruct the remaining linear space using the preceding theorem.

For this fixture all 136 pair determinants are nonzero, in both contracts. The exact minimum absolute determinant is 7990 (clean) and 6069 (with nuisance). For example, without nuisance the first three signatures are (792,860), (605,792), (333,605); with nuisance they are (0,-255), (255,0), (459,255). The full table is emitted by sparse.py. Thus **34 clean samples or 36 with the two nuisance columns suffice** for full identification in the relaxed model. The laboratory explicitly decodes phase and signed amplitude for all 17 residues and four signed gains, with independently varied arbitrary smaller-period shapes; the remaining linear reconstruction follows by the proved Vandermonde theorem.

Sharpness in the relaxed model: at d+1 samples there is only one annihilator residual. For the clean fixture, phase 0 with gain 605 and phase 1 with gain 792 give the same first residual. In the nuisance fixture, phase 1 with gain 459 and phase 2 with gain 255 do likewise. The difference sequence on those d+1 samples is annihilated by the single recurrence equation. The first d values extend uniquely to a nuisance-space sequence by the Vandermonde theorem, and the recurrence enforces the final value, so a change to the nuisance components makes the two observations identical. Both target gains are nonzero. This is an exact collision and proves sharpness for the relaxed model. It does not establish sharpness if all five components are single-spike templates. Nor does it prove a sign-only lower bound.

The small phase decoder is a line classifier in a two-dimensional residual space. Its determinant certificate concerns exact arithmetic; filtering with large integer coefficients may worsen noise amplification. Do not assume 34/36 samples are a robust operational deadline.

## The conditioning cliff

For N>=dimension and independent equal-variance zero-mean sample errors, the minimum-variance linear unbiased estimate of any residue coordinate uses the corresponding row of the Moore-Penrose left inverse B=(X^T X)^(-1) X^T, with the final residue recovered by the negative sum of the preceding residues. Proof: any other unbiased linear row differs by a vector in the nullspace of X^T, orthogonal to this minimum-norm row. Its squared norm is no smaller. Variance for each residue is sigma^2 times squared row norm. With arbitrary deterministic sample error bounded by epsilon in absolute value, its error is at most epsilon times row L1 norm, and the bound is attained by taking the signs of the row as the error vector. These are distinct uncertainty models.

The exact rational witness verifies B X=I at 48, 50 and 64 samples. The maximum residue row norms are:

| N | nuisance | max squared L2 | max L1 |
|---:|---|---:|---:|
| 48 | no | 4022055558 | 327250 |
| 50 | yes | 32715015014/169 | 80826 |
| 64 | yes | 137120343162059355343216839641/165865082905499973967478113760 | 6710810691360943206284629449/1219596197834558632113809660 |

At N=50 the worst residue variance multiplier is about 193,579,970.5. At 64 it is 0.826698. Adding fourteen samples reduces the optimal worst residue white-noise variance multiplier by roughly 234 million times in this fixture. This is a statement about the exact linear estimator under the declared noise model, not a measured physical signal-to-noise ratio or a lower bound on nonlinear template estimators.

Numerical SVD cross-checks, same-agent and same matrix model, with the two nuisance columns:

| samples | design condition number | max squared residue-row L2 | max residue-row L1 |
|---:|---:|---:|---:|
| 50 | 395726.496 | 193579970.498 | 80826 |
| 64 | 15.824 | 0.826698 | 5.502486 |
| 80 | 10.119 | 0.387960 | 3.631279 |
| 96 | 8.041 | 0.246236 | 3.009679 |
| 128 | 5.976 | 0.150602 | 2.323738 |
| 256 | 4.438 | 0.063780 | 1.882353 |
| 512 | 4.261 | 0.031525 | 1.882353 |

The condition number depends on the chosen coordinate basis; the residue-row amplification refers to actual physical component values and does not. At 64 samples an adversarial bounded error of 0.1 attains a worst-residue deviation of 0.550248574345858. For a true single-spike template, the unique largest absolute residue has a gap of (p-2)*abs(a) over other residues. If every residue error is below half that gap, the recovered maximum-absolute residue still identifies phase and sign. For p>=5, min amplitude A, the uniform sufficient 64-sample bound is epsilon < 1.5*A/5.502486, approximately 0.2726*A. This is a deterministic sufficient condition, not a necessary one.

## Negative sediment and limits

- Exact identifiability does not imply usable recovery at the minimum sample count. The square system is extraordinarily ill-conditioned. A rational inverse validates the exact mathematical map but does not make it an appropriate noisy receiver.
- The 34/36-sample shortcut uses a narrower shape prior on the largest period; a non-template component may not lie on any of the admitted lines. A decoder must reject rather than force a match. The exact laboratory checks every candidate line, not a noisy nearest-line classifier.
- Under known coherent raw samples, linear reconstruction bypasses the earlier invariant statistics, but does not invalidate their optimality statements under their own contracts. It does not give translation-invariant observations without a sample clock.
- A constant bias can be removed by nuisance fitting, but independent stationary additive noise with unknown covariance is not deterministically rejected in general. Coherent interference that exactly cancels the signal remains fatal.
- Near-zero amplitudes, unknown periods, clock drift/slips, transients, clipping, physical transmission, finite precision implementations, listener performance and comparison against modern periodicity dictionaries require separate qualification.
- No claim of scientific priority. The theoretical ingredients are established linear algebra and annihilating filters. The specific line certificate, exact noise-gain comparison and negative control are new scoped derivations within this expedition, not asserted novel in the literature.

## Source ledger and replay

Vaidyanathan and Tenneti, *Srinivasa Ramanujan and signal-processing problems*, Phil. Trans. R. Soc. A 378:20180446, DOI https://doi.org/10.1098/rsta.2018.0446 (online 2019-12-09; issue 2020-01-24). Full-text PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC6939226/ ; read abstract, §1 Eq. 1.1 and §3 Eqs. 3.4–3.13, especially dimension and basis properties. Their Ramanujan-subspace and short-record dictionary perspective motivates the contract change; the particular fixture results here are not attributed to them.

Vetterli, Marziliano and Blu, *Sampling Signals With Finite Rate of Innovation*, IEEE TSP 50(6), 1417–1428 (2002), DOI https://doi.org/10.1109/TSP.2002.1003065 . Read original PDF text at printed pp. 1417–1418, abstract/introduction and Eq. 1; screenshot request timed out, no visual verification claimed. Their continuous-time sampling and annihilating-filter framework is conceptual ancestry, not a direct proof of this discrete known-period result.

Repository reconciliation: root AGENTS, README, RAG, programme, runbook, integrity and validation inspected; no nested AGENTS at research or research/expeditions. Live main 495a98ca12bae467a507031f04931aa4254b1866, 437 branch entries paginated, 50 recent open issue and 50 recent PR search results, targeted Ramanujan/linear/conditioning/reconstruction and quadrature/variance queries. Read complete #744 report and issue, no comments; #745 exact head 7e29f0096de0081c978875cf1ef7fe356731de81 remains draft, workflow 45919416580 completed success. New #750, comments empty, branch mhac-750/local-clock. Native git ls-remote blocked by DNS; no full checkout or repository-wide native validation claimed. Additive scope only.

Replay: Python 3.13.5; run python sparse.py (standard library) and OPENBLAS_NUM_THREADS=1 python witness.py (NumPy 2.3.5 and SymPy 1.14.0). Both native runs repeated byte-identical JSON locally. Native results: 272 nonzero exact pair determinants, 136 exact target phase/amplitude decodes, two one-short recurrence collision witnesses, three exact left inverses, 3500 numerical component sign/phase recoveries over 700 deterministic-seed synthetic profiles and seven apertures, one worst-error construction. Maximum clean numerical error 2.62e-9 at the 48-sample square system. No failed assertions in final runs. Committed source blob IDs matched native executed source: witness.py 3e8b44bacdc0e8b67f8e9fc109a153c83408db6c and sparse.py b1826dfcb4c7720b32f5f14d346fd16ef476ba3d. Exact and numerical calculations are same-agent cross-checks, not independent review.

Interpretation: an observer's resource budget is not an intrinsic property of the message. It depends on what prior structure the observer is licensed to use and which distinctions the observation must preserve. Candidate Observatory experiment: show the minimum exact deadline beside a conditioning-controlled deadline, and include a rejection state when the one-spike prior fails. No VST or human evaluation is delivered here. Conventional harmonic analysis and linear algebra explain the results; no incremental cybersemiotic explanation has been established.

Fiction: the clerk keeps weighing every tick until the entire calendar has been represented. The apprentice instead learns the recurrence of the calendar. Then she waits fourteen ticks longer than necessary, because a perfectly invertible ledger can still be impossible to read.
