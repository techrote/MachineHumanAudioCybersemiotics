# The Chord That Needs a Clock

Refs #740 · 26 November 2026 · Exploratory synthetic DSP and exact algebra. One ChatGPT agent read sources, derived results, implemented and self-checked. No human review, perceptual evidence, scientific priority, or canonical evidence promotion.

## Observation contract

[#724](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/724) constructed integer signals whose complete ordinary cyclic correlations through fifth order collide. [#733](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/733) recovered individual pair relations by balanced two-tap filtering and a lagged sixth-order receipt, with calibrated baseline and complete-period averaging. Here grant the observer a coherent sample index, but no absolute phase origin, and ask what it buys.

For distinct odd primes p_i, positive amplitudes A_i (integers for PCM, arbitrary positive reals for identifiability), and signs s_i, let P=product p_i and

    x(t)=(-1)^t sum_i s_i A_i R_(p_i)(t),
    R_p(t)=p*1_(p divides t)-1.

An unknown common cyclic shift r changes the observation to x(t+r). Demodulate using only the LOCAL sample parity:

    u(t)=(-1)^t x(t+r)=(-1)^r sum_i s_i A_i R_(p_i)(t+r).

The unknown origin changes every sign together. That is already the physical translation ambiguity. A sample counter with no slips is required; the method is not shift-invariant in the ordinary scalar sense. The ratio of any two recovered signed coefficients is shift invariant in sign. This is a different observer contract, not a contradiction of the earlier correlation-order theorem. Direct Fourier access is another solution, and may be preferable.

## Exact cubic receipt and individual selection

Use T(a,b)=E[u(t)u(t+a)u(t+b)] over uniform t modulo 2P. By the Chinese remainder theorem, private prime residues are independent, and every R_p has zero mean. All mixed terms with a singleton component vanish. Thus

    T(a,b)=sum_i w_i f_(p_i)(a,b),  w_i=(-1)^r s_i A_i^3.

For each p, f_p depends solely on how many distinct residues occur among 0,a,b modulo p:

    one:   (p-1)(p-2)
    two:   -(p-2)
    three: 2

Proof: expand (p I_0-1)(p I_-a-1)(p I_-b-1) and average over p residues. The constant plus the three linear terms contributes 2, each coincident pair contributes -p, and a simultaneous triple contributes p^2. This gives the three cases. Independence proves the full formula; translation r does not change uniform residue averaging.

For lag p_i, distinct primes ensure no other component divides the lag, whereas all primes fail to divide 1. Consequently

    T(0,p_i)-T(0,1)=p_i(p_i-2) w_i.

This requires no filtering, sixth-order processing, known baseline energy, known common gain, or known relative positive component gains. It uses a common reference receipt and one lag-specific receipt. Positive gains rescale each w_i without changing its sign; a negative common gain reverses all signs and does not change their pair relationships. A real negative individual transfer changes the encoded sign itself and cannot be distinguished without a model. Discarding amplitude calibration does not eliminate the need for sufficiently precise estimates. This is not a one-statistic solution: direct selection needs a shared reference and additional measurements.

## Sharp aperture rank and a smaller compiler

An aperture B permits all integer-shift triples with maximum separation at most B. Translation and symmetry reduce them to 0<=a<=b<=B. Let k=# of primes <=B and m the number of components. For B>=2, the exact linear rank of ALL permitted third-order receipts as functions of the signed cubic amplitudes is

    rank = k + min(3,m-k).

Proof (upper bound): for p>B, two shifts are congruent modulo p iff they are equal as integers. Thus every row restricted to the large primes is one of three vectors, the evaluations of polynomials (p-1)(p-2), -(p-2), 2. On the small primes the dimension is at most k. Proof (attainment): the reference T(0,1) and the k receipts T(0,p_i) individually isolate all small coordinates by the previous identity. The three baseline receipts T(0,0), T(0,1), T(1,2), after subtracting small-coordinate contributions, give the three polynomial evaluation rows on the remaining primes. They span all polynomials of degree <=2 and hence have Vandermonde rank min(3,m-k). For B=0 and B=1 the corresponding ranks are min(1,m) and min(2,m), since all primes are odd.

For m>=4, in increasing prime order p_1<...<p_m, the minimum aperture for identifying ALL signed cubic amplitudes is exactly p_(m-3). For m<=3 it is m-1. For the five-prime fixture (5,7,11,13,17), aperture 7 suffices, not 17: isolate 5 and 7, then solve the three-dimensional Vandermonde system for 11,13,17. Exactly five scalar receipts suffice: T(0,0), T(0,1), T(1,2), T(0,5), T(0,7). The witness inputs w=(1,8,-27,1,-8), receipts=(-3966,309,-50,324,589), and recovers w exactly by Cramer's rule.

Rank deficiency also obstructs universal relative-sign identification under arbitrary unknown positive real amplitudes when m>=2. For B>=2, the nullspace contains a nonzero vector supported on the large primes whose entries sum to zero (since the constant row is present). Such a vector has both signs. Start with all-positive weights and move sufficiently far in that null direction, avoiding the finitely many zero crossings: some but not all signs reverse without any receipt changing. For B<2, the positive all-equal-lag coefficient row similarly forces mixed signs in any nonzero null vector. This proves nonidentifiability with unknown gains, not a universal claim that every fixed known amplitude profile has collisions.

Exact fixed-unit-gain negative control: prime triples (7,37,73) and (5,41,71) both sum to 117 and have squared sum 6747. Assign opposite signs to the two triples, and keep a positive prime-3 anchor fixed. Reverse all six large signs but not the anchor. Every cubic receipt of aperture <=4 agrees because the large-prime signed polynomial sums all vanish. These two configurations are not translations; T(0,5) distinguishes them. This negative control is evaluated exactly by the proved private-moment formula, not by enumerating the enormous full cyclic period.

A shorter aperture is not a promise of shorter total observation, lower processor utilization, or better numerical conditioning. Vandermonde inversion can magnify measurement error, particularly for nearby large primes. The direct longer-aperture individual selector avoids this particular inversion.

## Stationary-noise cancellation beyond Gaussianity

Let n(t) be an independent additive strictly stationary real noise process with finite third absolute moment. It may have nonzero mean, skewness and arbitrary temporal correlation. Consider a random uniform time U in a complete 2P period, independent of the entire noise process. The demodulated noise vector at any fixed lags a,b is

    V=(-1)^U (n(U), (-1)^a n(U+a), (-1)^b n(U+b)).

Strict stationarity makes the parenthesized vector's conditional law independent of U. By CRT, parity of U is independent of the complete private-residue signal vector (also under a fixed unknown shift). Therefore V is independent of that demodulated signal vector, and V is centrally symmetric: the two parity classes supply equal-probability opposite vectors. Both signal and V have zero mean. Expanding the third product, every mixed term vanishes by independence and zero mean, and the pure-noise term vanishes by symmetry.

**Population theorem:** the entire third-order receipt surface, and hence the individual selection and rank compiler, is exactly unchanged by this noise model. It is sufficient that the relevant noise-vector laws are invariant with the absolute time origin; the full strict stationarity assumption is an easily stated sufficient contract. The conclusion does NOT require Gaussianity or a symmetric noise marginal before modulation. This is a synchronous averaging result, not a universal higher-order-statistics noise-rejection claim.

Exact witness: independent uniform random phase of each of three periodic noise sequences [0,0,9], [2,2,2,-7], [1,4,-2,8,8]. These are stationary in ensemble, non-Gaussian, temporally correlated and potentially biased. Enumerate all phases and complete signal times, both starting parities, and all 55 lag pairs up to aperture 9; 330 exact noise profiles reproduce the clean moments. No Monte Carlo approximation enters these checks.

**Crucial negative sediment: population identity does not imply one-record consistency.** Consider clean x(t)=(-1)^t R_5(t) and noise n_U(t)=-(-1)^(t+U)R_5(t+U), U uniform on 0,...,9 and independent of the signal. This is a strictly stationary random-phase process. Across all phases the exact selector gives 15, as predicted. For a single phase U=0, the observed waveform is identically zero forever, while U=5 doubles it and yields 120. Other phases give selectors 5,0,10,25,-25,10,0,5 (see ordered JSON receipt). More complete cycles in a fixed phase do not resolve this obstruction. Ergodicity/mixing or an independent-episode acquisition model is an additional requirement for sample consistency. Even an infinitely long single trace can fail under mere stationarity. Phase slips, nonstationary coherent interference, nonlinear clipping and clock-rate mismatch are also outside the theorem. A periodic deterministic disturbance synchronized to the intended carrier can directly mimic or cancel a target.

## Sources, tests and disposition

- J. M. Mendel, *Tutorial on higher-order statistics (spectra) in signal processing and system theory: theoretical results and some applications*, Proc. IEEE 79(3), 278–305 (1991), https://doi.org/10.1109/5.75086 . Author-hosted PDF https://sipi.usc.edu/~mendel/publications/HOSATutorial.pdf, printed pp. 279–280 (PDF pages 2–3), Section II, eqs. (2b), (4b), CP5–6 and (7), read with page images. Established cumulant additivity, third-order zero-mean moments and additive Gaussian-noise rejection; the parity-induced symmetrization above is a separate direct derivation, not attributed to Mendel. Section VIII discussion of sample-estimation burden is a relevant caution; no complete article review or priority claim.
- W. A. Gardner, *An Introduction to Cyclostationary Signals*, in *Cyclostationarity in Communications and Signal Processing*, IEEE Press (1994). https://cyclostationarity.com/wp-content/uploads/2021/08/An-Introduction-to-Cyclostationary-Signals.pdf . Inspected equations (23)–(26), discussion of frequency translation and the printed pp. 52–53 time-delay example (PDF page 34 image). Context for synchronous frequency translation and timing-sensitive statistics; this chapter is not claimed to establish the present prime-indexed cubic compiler. No full chapter review.
- Read full #733 report, issue and comments (none); successful predecessor exact-head workflow 45906910295. Governing AGENTS, README, RAG, programme, runbook, integrity and validation read. 432 branch entries, 50 recent open-issue and 50 recent PR search results; targeted Ramanujan/cumulant/lagged-cubic searches. Fresh #740 created, comments empty. Base 495a98ca12bae467a507031f04931aa4254b1866. Native git ls-remote failed DNS; no repository-wide local test claimed. Only new issue-scoped directory modified. Draft/HOLD for mathematical critique and integrator review.
- Run node laboratory.cjs. Executed exact integer sums and BigInt elimination in V8, not a native Node process. 3202 private-moment identities, 576 literal complete-period demodulated triples across signs and origins, 576 raw odd-moment negative checks, 1134 exact aperture-rank tests, 330 noise phase-ensemble profiles and 17 collision/coherence negative checks; zero assertion failures. The five-prime recovery uses separate exact integer determinant computations. Arithmetic bounds checked for literal sums; all fixtures small enough for exact JS integers. Same-agent cross-checks, not independent peer review. JSON is the actual execution receipt.

Interpretation: the clock changes the observer's available invariants. What looked like an intrinsic sixth-order obstacle was a sixth-order obstacle under an ordinary translation-invariant observation contract. A coherent parity reference is an extra resource. For MHAC the useful experimental module is a sample-clocked cubic inspector, with explicit "population only" and "coherent interference" flags. The small-aperture rank theorem could inform a VST prototype, but finite observation, clock fidelity, analog channels and actual auditory utility are unqualified. Conventional harmonic algebra, probability and DSP suffice; no incremental cybersemiotic explanatory contribution established.

Fiction: the clerk demands a sixth witness. His apprentice turns over the clock and discovers that every second tick has been speaking in the opposite voice.
