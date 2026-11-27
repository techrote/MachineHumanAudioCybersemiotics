# The Chord That Weighs Its Alibis

Refs #771, #767, #754, #763 · 27 November 2026 · Exploratory mathematical DSP, outside frozen Track E/G. One ChatGPT agent performed the derivation, source reading, exact and numerical checks, and repository delivery. No priority, independent review, human evidence or physical qualification claim.

## The anomaly and result

The predecessor #767 establishes a 51-sample information-optimal single-error deadline for periods (5,7,11,13,17) with an intercept, but a 57-sample deadline for ordinary unweighted LAD. #754 shows that arbitrary confidence weighting can destroy an otherwise good decoder. Here weighting rescues rather than harms the decoder, provided the weights derive from the syndrome geometry. In fact, every real linear observation code admitting universal single-error correction admits a weighted LAD decoder attaining that same exact threshold. For the five-prime fixture, exact integer certificates establish this at 51 samples. A separate sharp deterministic noise analysis reveals why exact correction at this deadline is a poor proxy for robust localization.

## Proof: geometry-derived weights restore convex repair

Let A have full column rank, H be a full-row-rank parity-check matrix with ker H = range A, and v_i be column i of H. For received z, fitting a clean signal by weighted LAD is equivalent to minimizing sum_i w_i |e_i| subject to H e = H z. Universal single-error identifiability holds exactly when the v_i are all nonzero and no two are collinear: otherwise a nonzero vector supported on at most two positions is in the code, and conversely.

For any positive definite matrix M on the syndrome space, choose

    w_i = sqrt(v_i^T M v_i).

For a single actual fault alpha at i, the dual vector lambda = sign(alpha) M v_i / w_i has lambda^T v_i = sign(alpha) w_i and, for j != i, |lambda^T v_j| < w_j by strict Cauchy–Schwarz. Thus every feasible error vector with a nonzero entry off i has strictly greater objective than the true single fault. If supported on i only, feasibility fixes its amplitude uniquely. The zero syndrome has unique zero minimizer because all weights are positive. This proves sufficiency. Necessity follows from the same identifiability obstruction, regardless of decoder. The result is a general elementary normalized-dictionary fact; it is not a new claim of priority in compressed sensing.

For a positive rational or integer approximation w, set G_ij=v_i^T M v_j. A sufficient exact certificate is

    G_ii w_j > |G_ij| w_i       (every i != j).

Indeed, scaling M v_i by w_i/G_ii produces the strict dual witness. Positive real norm weights meet these finitely many inequalities strictly, so positive rational approximations and integer rescalings always exist. This is a certificate for a particular choice, not a necessary quantization rule. Weighting cannot cure a nonidentifiable code. The proof covers one error, not arbitrary multiple-error supports. It also does not assert optimality of the weighted objective under dense noise.

## Exact 51-sample repair

For the five known prime periods, D=49 and P(E)=(E-1) product_p sum_{j=0}^{p-1} E^j. The 51-sample H has two shifted rows of its integer coefficients. This is the #767 recurrence model; the checked kernel equals the additive space by rank/dimension. Use either M=I in this particular syndrome basis or the coordinate-invariant choice M=(HH^T)^(-1).

For either Gram matrix G, the laboratory tests integer weights

    w_i = floor(2^b sqrt(G_ii / max_j G_jj)).

No floating-point decisions are needed: square root of the integer quotient at scale 2^(2b) is integer floor square root. The first passing scale in this specific floor-quantization family is b=20 for the raw syndrome and b=16 for the orthogonal quotient. This is not a minimum bit-width over all possible integer weight vectors. In particular the maximum weight 65536 needs 17 unsigned storage bits. Both sets of 51 exact integer weights and all failed smaller-scale inequality counts are retained in execution.json. The orthogonal certificate passes all 2,550 ordered strict inequalities; its minimum ratio G_ii w_j/(|G_ij| w_i), over nonzero denominators, is 273618876211/273594544463. At b=15 two directed inequalities fail this certificate; that alone does not establish decoder failure.

The earlier unit-weight counterexample had true residual e_0=1 and alternative e_25=e_26=-1/127. Both have the same syndrome. Its false-to-true cost ratio changes from 2/127 to 1.1460731803 (raw weights) or 1.0029671315 (orthogonal weights). The new strict dual inequalities prove the truth is preferred over *every* feasible alternative, not only this witness. The small margin is itself negative engineering sediment.

These are geometry-derived weights, not asserted estimates of sample credibility. Multiplying one weight because a human or heuristic regards the corresponding observation as trustworthy is an entirely different intervention; the #754 counterexample remains applicable. Changing parity-check row coordinates changes raw norm weights but leaves orthogonal quotient weights invariant.

## Proof: the physical sample-space quotient and the noise deadline

Now add arbitrary dense noise n with Euclidean norm at most epsilon in the original N raw samples. Define Q = H^T(HH^T)^(-1)H, the orthogonal projector onto the complement of range A. It removes the unknown clean signal and has operator norm one. Put u_i=Q e_i, where e_i is the coordinate unit vector (not an error amplitude), and q_ij=Q_ij. Then u_i dot u_j=q_ij since Q is symmetric idempotent. This is the canonical syndrome metric for bounded raw l2 noise, also corresponding to whitening independent equal-variance raw noise. No Gaussian distribution is needed below.

First, if the true nonzero fault is alpha at i, its projected center has distance |alpha| sqrt(q_ii-q_ij^2/q_jj) from competitor line j with unrestricted amplitude. Half this distance is the sharp radius for uniform uniqueness of epsilon-compatible explanations around that fixed center, given arbitrary competitor amplitudes; the midpoint with its orthogonal projection onto the competitor line is ambiguous at equality. Include the no-fault center at zero if desired; its distance is never smaller than the line distance. This is a compatibility bound, not the exact decision-boundary radius of unconstrained nearest-line classification.

For a sharp *global* contract impose a minimum gross fault magnitude a>0 for both true and competing explanations, and allow no fault. The projected hypothesis sets are {0} and two rays per position, {alpha u_i: |alpha|>=a}. The least inter-set distance divided by two is the exact supremal universally safe raw noise radius. By triangle inequality, any nearest-set decoder (or unique compatible set) succeeds strictly below half the separation. At equality, choose closest centers and their midpoint. Each center can actually be generated by an admissible clean waveform plus its stipulated gross fault: use clean vector -alpha(I-Q)e_i, which lies in range A. The two raw perturbations from the respective centers to their midpoint have norm equal to half the separation. Thus no decoder can universally localize the fault at equality. The target is support localization, not exact amplitude or noiseless waveform reconstruction in dense noise.

For a=1 write U=q_ii, V=q_jj, W=|q_ij|. Choosing the optimal signs reduces the squared pair distance to minimizing U s^2+V t^2-2Wst over s,t>=1. Strict positive definiteness excludes an interior optimum (only the origin solves the stationary equations). On either boundary, one-dimensional minimization gives

    D_ij^2 = U-W^2/V       if W>V
           = V-W^2/U       if W>U
           = U+V-2W        otherwise.

The first two cases cannot both hold. Compare all pairs and the no-fault distances q_ii. For general a, multiply squared distances by a^2. All comparisons can be exact rational arithmetic; only presentation square roots need floating point.

## Exact geometry and independent numerical formulation

For N=51 the limiting pair is positions 0 and 1 (and its reflection). Exact squared separation is 1/2270030. The explicit closest fault magnitudes are 3418348/1135015 and 1, with matching signs. The exact midpoint's squared noise norm is 1/9080120; the laboratory checks both lifts into the additive model and the squared distance with integer arithmetic.

| N | Sharp radius / minimum fault magnitude | Minimum acute quotient line angle (degrees) |
|---:|---:|---:|
| 51 | 0.000331859463 | 0.780896 |
| 52 | 0.002173909693 | 0.982688 |
| 53 | 0.013519407967 | 5.164942 |
| 55 | 0.019324126949 | 7.089194 |
| 57 | 0.107635668215 | 36.471010 |
| 60 | 0.129685345770 | 38.018628 |
| 64 | 0.183654408939 | 45.678122 |
| 70 | 0.244213780724 | 59.926391 |
| 85 | 0.313318281039 | 68.913953 |

At 57 samples the sharp radius is approximately 324 times the 51-sample value. The #767 raw syndrome angle was 0.0844 degrees; this was basis-dependent, whereas the present quotient geometry is invariant under any invertible recombination of syndrome rows. The smallest angle does not necessarily determine the smallest distance: column norm and minimum allowed amplitude matter as well. No positive uniform localization guarantee exists without a lower bound on the nonzero fault amplitude. No exact clean-waveform guarantee exists in arbitrary nonzero dense noise, even with correctly identified support.

The exact laboratory constructs orthogonal rows by integer Gram–Schmidt with gcd reduction, computes Q with a common integer denominator, and checks orthogonality, trace, fixed recurrence rows and annihilation of every private residue indicator. It checks 33,662 ordered pair determinants and distance candidates across nine profiles. All reported exact fractions, quantized weights, and the midpoint collision are in execution.json. The committed CJS source was retrieved and run in V8, reproducing its committed receipt byte-for-byte. No native Node execution claimed.

The separate native Python laboratory computes the quotient from a complete QR factorization of the actual residue-indicator design matrix, not from recurrence coefficients. NumPy 2.3.5, SciPy 1.17.0, Python 3.13.5. All nine radii agree numerically (reflection can change the selected minimizing pair). The numerical weighted-LP test uses continuous orthogonal norm weights, not the integer approximations: 102/102 unit single-fault trials (both signs at all positions) succeed, maximum coordinate error 1.74e-14. The minimum-amplitude nearest-ray/no-fault receiver succeeds in 1,028/1,028 seeded synthetic gross-fault plus dense-noise trials at 0.99 times each certified radius. These trials do not establish the bound; the proof and exact midpoint do. Two native runs produced byte-identical receipts, and Git blob hashes match the committed native.py (39e6193dfca40a65c67634790bcac538d6eeb2eb) and native-execution.json (34cbd414c9f432fce5ab1602540dfdbee803435b). Same-agent cross-check, not independent peer review.

## Source and interpretation boundaries

Scharf and Friedlander, Matched Subspace Detectors, IEEE Transactions on Signal Processing 42(8), 2146–2157 (1994), DOI 10.1109/78.301849, institutional record https://mountainscholar.org/items/06a68de8-560b-47ac-93a8-c9839b17aab3 ; public copy https://www.mssc.mu.edu/~daniel/mscs6960/spring2010/ScharfFriedlanderTSP94.pdf. Read §§I–II and the start of §III, equations (2.1)–(2.6), and visually inspected original printed p.2147 (PDF index 1), Fig.1 and equation (3.1). Established context: project out structured interference and distinguish hypotheses in subspace geometry. Their Gaussian GLR/UMP-invariance analysis is not the present deterministic minimax proof. No full-paper read claimed. The earlier #767 Candès–Tao source notes provide related sparse-error context; no new reading of that paper is asserted here. No systematic novelty audit.

The observer's price for an error is not necessarily its raw amplitude. It can be calibrated to the scale at which the error can affect the observation system's invariant. This provides a precise analogy with testimony: two statements can differ equally in literal magnitude yet differ greatly in their capacity to alter a contradiction. It is an analogy, not a cognitive or semiotic finding. Conventional linear algebra, convex analysis and distance geometry suffice. Proposed experimental use: expose unit-weight LAD, normalized LAD, nearest-ray localization, minimum amplitude and a certified noise margin in an Observatory receiver. Do not represent weighted-LAD noiseless correctness as a guarantee of its dense-noise performance. No VST implementation, physical audio test or human evaluation.

Repository reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity, validation and README read; nested research/AGENTS and research/expeditions/AGENTS absent. 448 paginated branch entries, 30 recent issues, 30 recent PRs and targeted duplicate searches inspected. Predecessor #767 full report and issue read, no issue comments, exact-head workflow 45947909832 completed successfully. Fresh #771 scoped issue and comments inspected. Native git ls-remote failed DNS; no full-repo native tests claimed. Five files confined to new issue-scoped directory; no canonical changes or other worker branch edits. Draft/HOLD for critique and integrator per issue scope.

Fiction: a clerk learns that each witness has a different capacity to make the ledger contradict itself. She weights their errors by that capacity, not by their apparent sincerity. Then she discovers that even the correctly weighted ledger must sometimes wait.
