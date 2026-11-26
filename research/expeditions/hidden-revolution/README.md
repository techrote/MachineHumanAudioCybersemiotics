# The Clock That Hides a Revolution

**MHAC expedition #670 · 26 November 2026 · synthetic mathematics and acoustic illustration; not a frozen-corpus contribution.**

A complete ordered transition archive can conceal continuous-time irreversibility. Even infinite samples on one fixed clock need not resolve it. A second clock repairs exact identifiability, but its best timing under an absolute-error model is surprisingly early, rather than the maximally spread phase code.

## Contract and prior overlap

Consider a fully observed, homogeneous, finite continuous-time Markov chain with labelled states. The observer knows the complete population transition matrix at a positive lag T. This is much stronger than the reversal-symmetrized discrete archive in #648 / PR #649 (full report read); the new obstruction survives ordered observations. No claim is made for time-varying generators or state lumping.

The matrix-logarithm ambiguity is established prior art. Lencastre, Raischel, Rogers and Lind explicitly study three-state circulant generators and multiple embeddings in [arXiv:1510.07282v1](https://arxiv.org/abs/1510.07282), §III, printed pp.4–5, equations (8)–(15) and Figure 1. Read those pages, including original page images, plus introduction equations (1)–(3); not the entire paper. Yue, Thunberg and Goncalves, [arXiv:1605.06973](https://arxiv.org/abs/1605.06973), 2016, explicitly call the matrix-exponential inverse ambiguity system aliasing (abstract and institutional metadata read, not full text). The basic example is not a scientific priority claim. The scoped extension here is the reversible/irreversible contrast, exact general clock criterion, and decay-aware optimal supplementary receipt for a bounded circulant fibre.

## The hidden rotation

Write the three-state generator in row convention as circ(-s,a,b), where a,b are nonnegative clockwise and counterclockwise jump rates, s=a+b and d=a-b. Its nonconstant eigenvalues are

    lambda = -3s/2 + i sqrt(3)d/2, and conjugate(lambda).

The first row of exp(t Q) is

    P_j(t) = [1+2 exp(-3st/2) cos(sqrt(3)dt/2 - 2 pi j/3)]/3.

The sampled nonconstant Fourier coefficient has modulus exp(-3sT/2) and argument sqrt(3)dT/2 modulo 2 pi. Thus the full fibre **within the circulant generator family** is exactly

    s = -2 log|z|/(3T),
    d_k = 2(arg(z)+2 pi k)/(sqrt(3)T), |d_k| <= s.

The spacing D=4 pi/(sqrt(3)T). With H=sqrt(3)sT/2 and principal phase theta, the number of admissible integers is

    max(0, floor((H-theta)/(2 pi)) - ceil((-H-theta)/(2 pi)) + 1).

The upper endpoint count includes zero rates; use strict inequalities if both rates must be positive. The maximal count over phases for fixed s is floor(H/pi)+1 (closed interval). A repeated eigenvalue of the sampled matrix can admit noncirculant logarithms; the formula does not enumerate those.

For T=1, choose s=D+epsilon, epsilon>0. Compare d=0 (reversible) with d=D (circulating). Both are strictly positive off diagonal. At every integer lag the full ordered transition matrix agrees exactly, since the eigenphase difference is an integral turn. With the same stationary uniform initial law, all finite-dimensional distributions on the integer clock agree, including every higher-order word. No statistic of that archive can distinguish these models. For equal prior odds any binary identification rule has error exactly 1/2 (including randomized decisions), since its observation law is identical.

For a fully observed stationary continuous-time path over duration L, the KL divergence against its reversal is L times

    E = (a-b) log(a/b).

Indeed the stationary distribution is uniform; the reversed chain exchanges a,b and preserves holding rates. The waiting-time factors and initial stationary factors cancel in the path likelihood ratio. Expected clockwise and counterclockwise jump counts are aL and bL. Grouping their log likelihood ratios proves the expression. This is information divergence in nats per time unit, not physical entropy production.

The reversible model has E=0, whereas the circulating one has

    E = D log((2D+epsilon)/epsilon),

which diverges as epsilon decreases to zero. Both share the same total jump intensity s: observing merely the total jump count also fails (Poisson(sL) in both). Observing directed jump counts or the conditional direction given one jump resolves d. At epsilon=.1, the rates are (3.6775987285,3.6775987285) versus (7.3051974569,.05), and the common sampled row is approximately (.3333441086,.3333279457,.3333279457). The circulating E is 36.1622138086.

## Two clocks: a general exact theorem

For arbitrary real square matrices Q and R, if exp(T Q)=exp(T R) and exp(U Q)=exp(U R) with T/U irrational, then Q=R. Proof: matrix exponentials are invertible, so equality holds for every integer linear combination mT+nU, using multiplication and inverses within each one-parameter group. Such times are dense in the real line. By continuity the exponentials agree for all real times; their derivatives at zero are equal. No diagonalizability, common eigenbasis, or stochastic assumption is needed. This is a population identity, not a numerical inversion algorithm: inverse powers can be ill-conditioned.

If a finite collection of lags are commensurate, write them as integer multiples m_i g with gcd(m_i)=1. Bezout's identity gives equality of exp(gQ) from equality at all measured lags; the reverse follows by powers. Thus commensurate measurements are algebraically equivalent to one common-base observation, and the three-state construction with T=g supplies counterexamples to universal generator uniqueness. No finite digital tick grid guarantees universal exact identification at arbitrary rates. This is not an assertion that every particular grid has multiple embeddings.

For a known bounded circulant fibre with M+1 consecutive alias candidates, however, a second lag U/T=u/v in reduced terms separates all of them exactly iff v>M. Two indices j,k collide exactly when v divides j-k. Irrational ratios are unnecessary in that bounded problem. Both conditions assume the stated actual lag is known, not simply a nominal device clock.

## Choosing the second clock: sharp absolute-error optimum

Suppose the first observation has exactly M+1 feasible consecutive circulant candidates (M>=1), with known s and coarse lag T. Measure their complex nonconstant Fourier coefficient at a second lag U=tT. Under an absolute complex-error contract their minimum pairwise separation is

    G(t) = 2 exp(-ct) min_(1<=k<=M) |sin(pi k t)|,
    c = 3sT/2.

The first sample and s are treated as exact, with only the second complex receipt subject to noise. Distinct candidates differ in phase by 2 pi k t; their equal radii decay as above.

Ignoring the radius decay, circular packing of M+1 points implies minimum arc separation <=2 pi/(M+1), attained at t=1/(M+1). This gives the normalized-phase-only optimum 2 sin(pi/(M+1)). But it ignores attenuation in the actual measured complex coefficient.

**Absolute-error optimum:** for a feasible alias population,

    t* = arctan(pi/c)/pi,
    G* = 2 exp(-c t*) sin(pi t*).

Proof. For every t>=0, G(t) <= 2 exp(-ct)|sin(pi t)| from k=1. The upper envelope has its global maximum at t* in the first half-cycle (differentiate there; later periods are exponentially smaller). Feasibility of M spacings in [-s,s] implies sT>=2 pi M/sqrt(3), hence c>=sqrt(3) pi M. Therefore t* < 1/(M+1): arctan(pi/c)/pi <=1/(sqrt(3) pi M) <1/(M+1). At t* all kt* lie in [t*,1-t*], so their sine is at least sin(pi t*). The upper envelope is attained by k=1, establishing global optimality, not just a grid search. The proof also covers the restricted interval [0,T] in physical lag.

The optimal worst-pair margin is attained before the equally spaced phase-code lag. The sharp guarantee under an adversarial complex error of magnitude strictly below G*/2 is nearest-candidate decoding; at the midpoint two candidates become indistinguishable. This is not a sample-size guarantee or an optimality claim for a likelihood-based estimator or full transition-matrix error.

For epsilon=.1 the full circulant fibre has d=-D,0,D (M=2); the optimal U=.0883017894 T, gap=.2067608562. U=T/2 gives zero separation for the whole fibre (opposite aliases collide); for the restricted reversible-versus-positive-circulation pair only, its gap is .0080406053. The commonly tempting half-clock is therefore poor even when it does separate the specified pair. The phase-only optimal lag for all three candidates is T/3, not T/2.

As c increases, t*~1/c and G*~2 pi/(e c). Even the optimum becomes arbitrarily fragile in absolute units for large rates. If a minimum accessible lag t_min>0 is imposed, G(t)<=2 exp(-c t_min) for every permitted t, yielding an exponential conditioning obstruction. Knowing the exact generator family and choosing an irrational ratio do not remove measurement uncertainty. Finite clock resolution, uncertainty in the first receipt, sample dependence and model error require separate analysis.

## Synthetic checks and acoustic witness

Run node laboratory.cjs in this directory; it prints the committed execution.json. The same function was executed in the tool JavaScript runtime before commit. It compares the Fourier row against literal Poisson uniformization (independent step probabilities), validates 608 candidate profiles across 64 feasible fibre designs, tests 128064 secondary-lag grid points against the analytic bound and 75264 exact integer clock-collision cases. 224178 assertions, no failures. Maximum numerical discrepancy 2.95e-15 or less. The grid is a check, not the proof. Native full checkout was attempted and blocked by GitHub DNS resolution; full repository checks were not run locally.

Separate native Python witness (delivered locally with receipt and original WAVs) used scipy.linalg.expm on the literal generators. 642 matrix/optimal-lag checks, maximum row error 7.89e-15 or less. It also constructs a shared 25-state skeleton on the coarse integer grid, then samples each model's conditional unit-interval CTMC bridges by rejection, using exponential holding times and directed jumps. Sampling the skeleton from the common endpoint law and then sampling bridges yields the respective model laws marginally (up to floating-point/pseudorandom approximation); the two specimens are deliberately coupled, not independent trials. For each of 24 intervals the shadow archive records ten sub-grid samples plus the final endpoint. Their 241-frame detail scores disagree at 143 positions. Both coarse WAVs are byte-identical by construction, not a statistical estimate. The 25 coarse frames and 241 detailed frames per model are 40 ms tapered 300/500/700 Hz tone symbols, 8 kHz mono PCM16; all 532 frames decoded from actual PCM by template matching. Both native runs reproduced all audio and receipt SHA-256 hashes. The audio is a sampled sonification, not a continuous-time physical measurement; the score playback time is not the model clock. No human validation, perceptual equivalence or benefit claimed.

## Exaptation and countercontrols

Design hypothesis: a machine's state snapshot vocabulary should declare the sampling horizon, maximum plausible transition rates and whether internal transitions are logged. A secondary lag tuned to the observed decay rate might make a rate-alias alarm more reliable than evenly spaced phase sampling. Test against direct ordered event logging, one-jump receipts, shorter uniformly sampled histories, and likelihood-based inference using the same acquisition budget. Direct event logs are the simplest baseline when available. Neither a different state vocabulary nor more samples at the original lag fixes exact aliasing.

Countercontrols: changing generator during the interval defeats the homogeneous semigroup premise; hidden states can invalidate the Markov premise; measuring only the stationary marginal yields no generator information here. A finite sample cannot determine the first Fourier coefficient exactly. Negative probabilities from noisy matrix logs do not prove the real process impossible. The theoretical error margin is not a physical or human guarantee. No special explanatory power of cybersemiotics has been established.

Artistic interpretation: a Clock Organ sounds a common coarse score while two internal circulation engines produce distinct sub-grid paths. A performer controls the second clock and chooses whether to expose directed jump events, phase-normalized receipts, or raw attenuated receipts. The composition is the difference between an observationally stable score and its incompatible continuous-time histories. Offline acoustic illustrations exist; the real-time instrument is speculative.

Additional prior comparator: Carette and Guerry, [The Markov chain embedding problem in a one-jump setting](https://doi.org/10.1017/jpr.2024.96), J. Appl. Probab. 62 (2025), 674–696, publisher introduction and abstract read. Their different conditional-one-jump embedding formulation is a relevant engineering comparator, not a validation of this timing design.

## Reconciliation and disposition

Default main 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, README, RAG, programme, runbook, integrity and validation; nested research/AGENTS and research/expeditions/AGENTS not found. Reviewed 395 live branch entries, 100 recent open issue results and 100 open PR results, targeted searches for matrix logarithm, Markov embedding, aliasing, incommensurate and sampling clock. Read #648 and all comments (none), plus its complete upstream report on its branch (unmerged; treated as research sediment). Preceding #667 head af31f48cb9f5816bf503bee351b8e6f445ce4779 had a completed successful PR workflow. New #670 body and empty comments read back; created fresh branch at recorded base. No canonical manifest, accepted record, other worker's branch or protocol changed. One ChatGPT/GPT-6.2 agent performed research, proofs and computations; no independent human review. Source access and reading limits are stated above. Draft pending independent critique and exact-head integrity checks; no merge claimed.

**Fiction:** A clerk listens to the tower at each strike of the hour. One mechanism merely oscillates; another has revolved many times between strikes. The apprentice listens sooner, before the vibration has faded. The clock had never lied about the hour; it had omitted the journeys between hours.
