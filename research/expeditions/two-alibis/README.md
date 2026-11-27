# The Chord With Two Alibis

Refs #767, #763, #759, #750 · 27 November 2026 · Exploratory mathematical DSP. One ChatGPT agent derived the results, read the specified source passages, performed LP discovery, exact arithmetic qualification and repository delivery. No independent peer review, physical transmission, human evidence or priority claim.

## Question and result

The full-Cartesian theorem in #763 restores optimal least-absolute-deviation (LAD) decoding for coprime periods. It leaves the short consecutive-prefix problem open. For the five-prime fixture (5,7,11,13,17), this expedition finds an exact minimum of **51 samples** for one arbitrary error by syndrome decoding and **57 samples** for universal unit-weight LAD correction. At the information-optimal 51-sample deadline, LAD can assign a false explanation only 2/127 of the true explanation's cost. At 56 samples it still fails. These are different, sharp deadlines for the same signal model. The complete period is 85,085 samples.

## Polynomial parity checks

Let p_i be known pairwise coprime integers >=2. The real additive model is

    y(t)=b+sum_i f_i(t mod p_i),

with each private waveform unrestricted and zero-mean (equivalently fix a reference residue and retain an intercept). Its dimension is D=1+sum_i(p_i-1). Use the forward shift E and the monic polynomial

    P(z)=(z-1) product_i (1+z+...+z^(p_i-1)).

Pairwise coprimality gives distinct Fourier roots: every nontrivial p_i-th root plus the single common root 1. The D consecutive evaluations form an invertible complex Vandermonde matrix on these modes. Conjugate symmetry gives the corresponding real solution space; thus every D consecutive samples determine the full additive signal. This is the recurrence formulation of #750's linear reconstruction result.

Write P(z)=sum_{j=0}^D a_j z^j. For N>=D, the N-D shifted coefficient rows form H_N. Each row is an annihilator of the additive model. Their leading nonzero coefficients are at distinct positions (a_0=-1), so they are independent. Hence ker(H_N) is exactly the observed additive signal space, by equal dimension D. This is also an exact certificate of membership: a finite sample vector satisfying these recurrences extends uniquely to the full admissible periodic signal.

## Two alibis: a sharp single-error deadline

For N=D+2, the columns of H_N are two-dimensional signatures

    v_t=(a_t,a_(t-1)), with a_j=0 outside 0..D.

Every nonzero column, with all pairwise determinants nonzero, is necessary and sufficient for distance at least three: a nonzero codeword supported on one or two positions would give a dependence among those columns. Conversely, any two linearly dependent columns give such a word. At distance three, a nonzero single-error syndrome equals alpha v_t for a unique t and unique signed alpha. Find the line by exact cross-products, divide by a nonzero component, subtract the error, and reconstruct from any D consecutive clean samples. The zero syndrome means no error within the assumed one-error contract. Outside that contract it does not diagnose the number of actual faults.

For (5,7,11,13,17), D=49. Polynomial coefficients (ascending degree) are

    -1,-4,-10,-20,-35,-55,-80,-109,-141,-175,-210,-244,-276,
    -304,-326,-340,-345,-339,-322,-294,-256,-209,-155,-95,-32,
    32,95,155,209,256,294,322,339,345,340,326,304,276,244,
    210,175,141,109,80,55,35,20,10,4,1.

All 1,275 unordered pairs of the 51 columns have nonzero integer determinant; the smallest absolute determinant is 1. This is an exact finite certificate, not a conjecture about all prime vocabularies. Distance is exactly three: deletion of any three coordinates leaves fewer than D observations, and alternatively a single residue indicator of the largest period has weight three. More generally N>=D+2 is necessary for a D-dimensional code correcting one arbitrary error, by the same deletion dimension argument. This proves the 51-sample deadline optimal even if arbitrary indexed observation positions were permitted.

The native exact decoder replays eight deterministic additive signals, each with errors at every one of 51 positions and three signed magnitudes (-10001, 7, 123456): 1,224 exact correction trials plus eight zero-error checks. The corrected 51-vector is returned; reconstruction of private components follows by the already established full-rank linear model rather than being a new implemented decoder in this packet.

## A false answer with a 63.5-fold cost advantage

At the same N=51 let the true signal be zero and received vector z have value 1 at tick zero only. The syndrome of z is (-1,0). Columns 25 and 26 of H are respectively (32,-32) and (95,32). Thus the error candidate eta' with values -1/127 at ticks 25 and 26 and zero elsewhere has exactly the same syndrome:

    (-1/127)[(32,-32)+(95,32)]=(-1,0).

The competing signal h=z-eta' belongs to ker H and therefore is a valid additive signal. The true signal has one nonzero residual, absolute cost 1; the competing signal has two residuals of total cost 2/127. This establishes strict failure of LAD, without requiring the alternative to be a global LP minimizer. The true signal is still the unique admissible signal within one gross error. This is a stronger separation than the mere existence of an ill-conditioned clean receiver.

Geometrically, the two signed syndrome columns with large norm combine to explain a small column's direction with small coefficient cost. Projective distinctness certifies sparse identifiability; convex hull geometry governs absolute-mass minimization. They are not equivalent. No magnitude bound on the single fault was assumed. No ordinary floating-point classification of nearly parallel directions is part of the exact proof.

## The first universally LAD-safe consecutive prefix

For any full-rank finite observation matrix A, consider a left-null vector c with c_i>0 and |c_j|<=1 for j!=i. Since c dot h=0 for every admissible difference h,

    sum_(j!=i) |h_j| >= c_i |h_i|.

A certificate with c_i>1 at every possible corrupted index proves strict universal one-error LAD recovery: for nonzero h, correct observations carry more absolute mass than the corrupted observation (if h_i=0, full rank ensures positive mass elsewhere). Triangle inequality then gives strictly greater LAD objective for every alternative. The stronger c_i>=d-1 at every index gives ||h||_1>=d||h||_infinity. As in #763 this suffices for arbitrary errors e and flagged erasures f whenever 2e+f<d, regardless of amplitudes; bounded noise admits the same observed-vector stability inequality, not automatically a bound on the unobserved full waveform.

At N=56 the following exact admissible difference is a negative certificate (integer numerator over common denominator 8930):

    index:     3     4    16   17   38   39   50    51
    numerator:8930 -6732 205  205  205  158  -47  -810

All other samples are zero. The seven shifted recurrence constraints vanish exactly. Corrupt truth zero at tick 3 to the indicated value. The true residual cost is 1; the alternative costs 4181/4465 <1. This is a strict obstruction, not an unsuccessful numerical search.

At N=57, the dependency-free certificate.cjs retains 29 eight-coefficient integer polynomials Q_i. Each product P Q_i has 57 coefficients; reversal gives the remaining 28 certificate rows, because consecutive reversal maps each residue to another residue. The replay checks all 57 rows directly against all private residue sums and compares their designated coefficient to every other coefficient using integers. Every row has strictly larger absolute designated coefficient. The smallest certified ratio is 2262526/2207931 (>1). The native solver also generated these witnesses and separately verified exact residue equations. A ratio certificate can be scaled and sign-adjusted to meet the inequality above; we do not need to claim numerical optimality of the LP to prove the deadline.

Universal LAD single-error recovery on a consecutive window is monotone in window length: any designated tick of a longer window lies within a translated copy of a shorter window. The model is invariant under translation. Its good-minus-bad absolute mass on that subwindow is strictly positive unless h vanishes there, which by the full-rank condition implies h=0 globally. Adding the other good samples cannot decrease the margin. Thus the 56 failure rules out every shorter window and the 57 certificates prove the exact first universal LAD deadline.

## Sharp short schedules beyond one error

The native LP search found and exact rational verification established these additional concentration certificates:

| Periods | Consecutive observations | Certified d | Sharp fault contract |
|---|---:|---:|---|
| 3,5,7 | 21 | 3 | 2e+f<3 |
| 3,5,7 | 35 | 5 | 2e+f<5 |
| 5,7,11,13,17 | 85 | 5 | 2e+f<5 |

Every target row passes its rational left-null constraints and coefficient bound. Each d is sharp via a single-residue indicator on the largest-period component. Moreover for any schedule of N observations, some largest-period residue occurs at most floor(N/M) times, M=max p_i; an indicator there is an admissible word (or unidentifiable full signal if missing). Universal correction of e errors and f erasures requires at least M(2e+f+1) observations. For the listed boundary cases (d=2e+f+1), these schedules attain that bound even over arbitrary indexed acquisition schedules. The five-prime 51-sample syndrome case also attains it. These are certified finite constructions, not a general prefix formula for every collection of coprime periods or every fault budget.

## Qualification and literature

Native replay: python laboratory.py (Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, SymPy 1.14.0). HiGHS discovers candidate dual vectors; Fraction verifies the exact equations and bounds, with exact polynomial-factor reconstruction from active constraints when direct rational rounding fails. For the negative witness the solver discovers support and an exact linear system reconstructs the integer/rational values. Two native runs gave byte-identical output. The committed Python source blob 84ee16a12c4f722f3848a2350f417cf02d284720 and execution receipt 6c66e7720a9298b11979c4fbf58b2b1338d5df17 match the locally executed bytes. 198 dual row certificates, 1,275 exact column-pair determinants, 1,224 exact error corrections, eight clean trials, two strict negative cases.

Static replay: node certificate.cjs. This separately formulated dependency-free BigInt checker verifies the retained 57-sample dual and 56-sample primal witnesses without a numerical solver: 3,021 residue buckets, 57 strict dual margins and seven primal recurrences. Committed source retrieved and executed in V8; certificate-execution.json records its output. This is same-agent cross-checking, not independent mathematical review.

Primary source: E. Candès and T. Tao, Decoding by Linear Programming, IEEE Transactions on Information Theory 51(12), 4203–4215 (2005), DOI 10.1109/TIT.2005.858979; public author record https://authors.library.caltech.edu/records/pxr5b-3zf41 and preprint https://arxiv.org/pdf/math/0502327. Read abstract and §§1.1–1.3, equations (1.1)–(1.6), inspected original printed page 4 (PDF index 3). The general real-valued sparse-error model, syndrome reduction and convex objective are established prior work. The consecutive periodic polynomial certificates, particular deadlines and strict counterexample are present derivations; no novelty or priority conclusion. Other literature searches were not a systematic novelty audit.

Repository reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, README, RAG, programme, runbook, integrity and validation inspected; nested research/AGENTS and research/expeditions/AGENTS absent. Paginated search returned 446 branch entries; 30 recent issue and 30 recent PR results inspected; targeted short-LAD and syndrome-prefix searches. Read the complete #763 report, issue and comments; predecessor exact-head workflow 45942131354 succeeded. Fresh issue #767 and its comments inspected. Native git ls-remote failed DNS; no full-repo native tests claimed. Isolated fresh branch only; no shared registry/manifest or another worker branch changed. Draft/HOLD for critique and integrator per issue scope.

## Interpretation, negative sediment and exaptation

A receiver can be information-theoretically correct and computationally easy while a fashionable generic convex objective fails dramatically. Here the one-error decoder needs only two dot products and a projective lookup. Conversely, its narrow fault contract and severe numerical scaling make the six additional samples required by LAD a potentially useful trade. The two-syndrome columns are not well separated uniformly; exact determinants alone do not imply practical floating-point/noisy recovery. Exploratory numerical geometry gives a minimum acute line separation of approximately 0.0844 degrees, and the recurrence coefficient L1 norm is 8754. These are not a physical noise tolerance or benchmark. A multi-error input can imitate a valid one-error syndrome; explicit rejection of all out-of-contract inputs is impossible.

A compact Observatory experiment could switch between 51-sample syndrome, 57-sample LAD and 85-sample two-error LAD, injecting identical timed faults and exposing both residual costs and syndrome lines. The short windows are exact sample counts under coherent indexing, known periods and a constant additive intercept, not end-to-end latency or a human evidence-acquisition rate. No streaming VST, unknown-period discovery, clock-slip handling, physical audio test or human validation has been performed. Conventional harmonic algebra, linear coding and convex analysis suffice; no incremental explanatory contribution from cybersemiotics is established.

Fiction: two clerks independently report the same discrepancy. The first names the only witness whose error could generate both numbers. The second divides the discrepancy into two much smaller lies and calls the cheaper account true. The apprentice waits six more ticks before giving the second clerk a vote.
