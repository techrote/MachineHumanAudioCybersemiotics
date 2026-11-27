# The Clock That Weighs Its Ticks

Refs #744 · 27 November 2026 · Exploratory exact DSP, combinatorial design and polynomial algebra. One ChatGPT agent performed the derivations, source reading, implementation, numerical discovery and exact self-check. No external review, human listening evidence, canonical evidence promotion or priority assertion.

## The problem: aperture is not observation duration

[#740](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/740) reduces the five-prime Ramanujan cubic inspector's sample aperture to seven, but averages over the complete cyclic period. With primes (5,7,11,13,17), that is 85,085 starts for the demodulated clean signal or 170,170 starts for parity-balanced stationary-noise ensemble cancellation. Can exactness be attained earlier without knowing the component amplitudes or the starting phase?

Yes, if the observer assigns different weights to different sample times. Equal-weight subsampling cannot universally solve this problem. The new result concerns acquisition weights, not a filter applied to the acoustic waveform.

## Exactness is a strength-three design

Let p_i be distinct odd primes, R_p(t)=p*1[p divides t]-1, and

    x(t)=(-1)^t sum_i a_i R_(p_i)(t),   a_i nonzero signed real.

The local sample clock produces u(t)=(-1)^t x(t+r), with unknown cyclic shift r. A fixed, real finite weight sequence w_t with total W>0 defines the normalized weighted cubic statistic

    T_w(a,b)=sum_t w_t u(t)u(t+a)u(t+b)/W.

**Theorem (clean):** T_w agrees with the complete-period cubic statistic for all amplitudes, common shifts and lags if and only if the weighted time residues are uniform on every subset of at most three private prime coordinates. This even holds with signed weights. Necessity requires only the zero-lag cubic T_w(0,0), not the complete lag surface.

Proof of sufficiency: expand the triple product. Each monomial depends on at most three private residues, so uniform marginals reproduce complete-period averaging. The CRT identifies these joint residues with time modulo the product of the selected primes. A fixed shift does not alter a uniform marginal.

Proof of necessity: choose r even; CRT still permits all independent private offsets. The cubic is a polynomial in the signed amplitudes. Equality on all nonzero real amplitudes implies equality of all coefficients. In the single-coordinate terms use

    R_p^3 = (p^2-3p+3) R_p + (p-1)(p-2).

The nonzero coefficient of R_p forces its mean to vanish at every private offset. Since R_p is an indicator contrast, this is exactly uniformity of the one-coordinate marginal. In the two-coordinate terms use

    R_p^2 = (p-2) R_p + (p-1).

Since p is odd, p-2 is nonzero. Once the singleton margins are uniform, the mixed coefficient forces E[R_p R_q]=0 for every pair of offsets. This is equivalent to uniform pair margins. For three distinct components the coefficient 6 E[R_p R_q R_v] must vanish for every triple of offsets; expanding the three indicator contrasts and using the already uniform lower-order margins forces uniform triple margins. This proof is valid for finite signed measures of total one as well. It does not assume a fixed known amplitude vector; narrower contracts may permit much shorter schedules.

**Corollary:** an exact equal-weight schedule with N starts (even allowing arbitrary nonconsecutive or repeated starts) requires p_i | N for every i. The coprimality forces product p_i | N. The complete demodulated period attains this bound. This is the mixed-level orthogonal-array divisibility obstruction, not a novel combinatorial theorem. Its application follows from the preceding necessary/sufficient cubic criterion.

## The noise contract adds one more coordinate

Let n(t) be independent strictly stationary additive noise with finite third absolute moments, including arbitrary constant bias. After demodulation its sample at lag a is (-1)^(t+a)n(t+a).

**Theorem (population noise):** universal exact cubic recovery in this noise model is equivalent to the preceding strength-three condition on the extended prime list (2,p_1,...,p_m).

Sufficiency: stationarity makes the needed joint noise moments independent of t. Terms with two noise factors contain a single centered signal component, hence vanish by uniform singleton margins. Terms with one noise factor contain parity times a product of at most two private components; these vanish by uniform joint parity/private margins. The pure noise term contains one parity factor and vanishes by uniform parity. The clean term is correct by the clean theorem. This proves ensemble expectation, not time-series consistency or immunity to coherent noise on a single record.

Necessity: zero noise already forces the clean condition. Substitute a constant noise c (a strictly stationary process) in the zero-lag cubic. The c^3 coefficient forces the parity mean to vanish. The coefficient of c a_i^2 forces E[parity*R_i^2]=0 for every private offset, hence E[parity*R_i]=0 via p_i-2 !=0. The coefficient of c a_i a_j forces E[parity*R_i*R_j]=0 at every pair of private offsets. Together with the clean margins, these force all joint parity/private margins of size at most three to be uniform, by the indicator contrast expansion. No additional constraints involving four coordinates are needed.

Equal-weight exactness now requires a multiple of 2*product p_i starts. An ordinary short flat average cannot in general be substituted for the weighted acquisition window.

## A cyclotomic span obstruction

Translate the weight support to start at zero; its span is the polynomial degree of

    A(z)=sum_t w_t z^t.

For each nonempty subset J of at most three primes from the relevant list S, let Q_J=product J. Uniformity modulo Q_J is equivalent to A vanishing at every nontrivial Q_J-th root of unity. This follows by the finite Fourier transform of the residue bucket sums (or by reducing A modulo z^Q_J-1). The primitive root classes are disjoint, so universal exactness is equivalent to divisibility over the reals by the monic polynomial

    L_S(z) = product_{J subset S, 1<=|J|<=3} Phi_(Q_J)(z).

Here Phi_q is the cyclotomic polynomial with the primitive q-th roots as its zeros. Hence the exact minimum span allowing signed weights is

    D_S = sum_{J subset S, 1<=|J|<=3} product_{p in J}(p-1).

The lower bound follows by counting distinct roots; L_S attains it and has L_S(1)=product S>0. Its coefficients can be constructed in integer arithmetic by expanding the Mobius product of factors (1-z^d), truncating at D_S. With nonnegative weights, D_S remains a lower bound but need not be attainable.

Example: for (2,5,7,11,13,17), D=9401, yet L has coefficient -2542 at degree 13 (and 4704 negative coefficients overall). At degree D every nonzero candidate is a scalar multiple of L; normalization forces a positive scalar. Nonnegative weights therefore require at least 9402 span. We do not confuse a real-weight divisibility bound with an attained positive design.

## A constructive positive acquisition window

Sort S increasingly. For each pivot p, let R be the later primes. For every subset J of R of cardinality min(2,|R|), multiply the positive factor

    G_(p,J)(z) = 1 + z^d + ... + z^((p-1)d),  d=product J.

The empty product is one. The factor vanishes at primitive roots of every order p*product K for K subset J: z^d then has order p. Every required cyclotomic factor has a smallest prime p and at most two later primes, which can be extended to some such J. Thus the product is divisible by L, has nonnegative integer coefficients and positive total weight. Normalize by the sum of coefficients.

The construction has span

    H_S = sum_(p,J) (p-1)*product J.

It is explicit, no numerical optimization required, and is cubic in the number of prime coordinates for fixed largest prime (as a bound on H, not a general runtime bound). The number of factors is binom(m,3)+2 for m>=3. Each factor can be convolved with an O(current output length) running-sum recurrence along its stride. These are offline integer weight compilers; streaming can use the resulting precomputed weights as accumulation coefficients. No requirement to physically replay the weight multiplicities.

For fixed receipt aperture B, the raw acquisition window uses H+1+B samples, not merely B. For clean and ensemble contracts respectively, the familiar five-prime aperture-7 decoder needs 9,096 and 10,174 raw samples using the constructive weights (9,089 and 10,167 start positions). Full-cycle comparisons use 85,085 and 170,170 start positions plus the same lag allowance. This is exact deterministic duration reduction, not a benchmark of estimator latency under stochastic noise.

| Relevant prime list | Equal-weight minimum starts | Signed minimum span | Positive constructive span | Nonzero positive weights |
|---|---:|---:|---:|---:|
| 3,5,7,11 | 1155 | 674 | 718 | 719 |
| 2,3,5,7,11 | 2310 | 861 | 954 | 955 |
| 5,7,11,13,17 | 85085 | 8476 | 9088 | 9089 |
| 2,5,7,11,13,17 | 170170 | 9401 | 10166 | 10167 |
| 2,5,7,11,13,17,19 | 3233230 | 26933 | 29173 | 29174 |

These positive spans are upper bounds, not asserted optima. The polynomial factors overlap in their zero sets. The next section resolves one small example exactly and shows that the simple constructive factorization is not optimal.

## A sharp positive optimum, by primal and dual certificates

For S=(3,5,7,11), L has degree 674. Search for nonnegative multiples L*C. A native SciPy/HiGHS linear feasibility search over unconstrained real coefficients of C with sum C=1 first found feasibility at degree 22. Numerical search is discovery only; exact verification follows.

Multiply its quotient by three to obtain the integer coefficients

    C = [1,-1,0,1,-1,1,0,0,0,0,1,-1,1,0,0,0,0,1,-1,1,0,-1,1].

The executable certificate independently constructs L=(1+...+z^1154)/Phi_1155 using the inverse Mobius product. Its convolution with C has nonnegative coefficients, degree 696, sum 3465, 635 nonzero weights and maximum weight 9. All 886 literal triple-modulus buckets satisfy the exact normalized marginal condition. This proves feasibility.

For impossibility at span <=695, any multiple has quotient degree <=21. Define nonnegative dual weights on output coefficient indices as follows (unlisted weights zero; values are twice the LP dual):

    (19,1),(22,2),(25,3),(29,4),(30,2),(49,1),(51,1),
    (52,2),(53,4),(642,4),(643,2),(644,1),(646,1),(665,2),
    (666,4),(670,3),(673,2),(676,1).

For each j=0,...,21 the exact dot product sum_i dual_i*L_(i-j) is -2 (out-of-range L indices zero). If W=L*C is nonnegative and not identically zero, then sum C=W(1)/L(1)>0. But dual dot W=-2 sum C<0, contradicting nonnegative dual and nonnegative W. This is an exact infeasibility certificate for all real quotients, not a restriction to integer or nonnegative quotient coefficients.

The sharp positive span is therefore **696**. Its 697 possible start positions include 635 nonzero weights. The signed optimum is 674; the naive constructive positive span is 718. The certificate is independently replayable without an LP solver. This does not establish the sharp optimum for the larger five-prime fixtures.

## Negative sediment: what uniformity and weighting do not guarantee

- Pairwise uniformity is insufficient. On CRT coordinates (3,5,7), weight each complete-period position by 1+f_3(t)f_5(t)f_7(t), where f_p is +1 on residue zero, -1 on residue one, otherwise zero. Every singleton and pair is uniform. The clean all-positive unit-amplitude zero-lag cubic changes from 44 to 50. Each E[R_p f_p]=1, so the error is exactly 6. The analogous (2,3,5) fixture with constant noise 1 changes the expected clean cubic from 14 to 20, despite clean private uniformity and all pair margins. This tests the genuine parity/private/private condition.
- A flat 10,167-start window cannot cancel even constant bias on a silent input: its odd number of starts leaves a parity mean 1/10167. This is a counterexample to simply truncating to the successful weighted window length.
- Weight concentration matters. The constructive noise-balanced five-prime window has integer mass 13,341,328,000,000, peak unnormalized weight 4,635,503,817 and inverse concentration (sum w)^2/sum w^2 approximately 3973.92, versus 10,167 start positions. This is the conventional independent equally variable sample-count proxy only; overlapping cubic products and correlated noise invalidate an automatic effective-sample-size interpretation. The corresponding six-private-prime window already needs integer weight mass greater than 2^64. Production coefficient representation, normalization precision, accumulation overflow and variance need their own qualification.
- Exact weighting does not cure #740's coherent stationary random-phase cancellation: one realization can erase the entire input forever. The laboratory confirms zero output in that realization even with the new weights. Ensemble equivalence is not recovery from every realization.
- Clock slips, unknown private periods, time-varying signs, changing gains, nonlinear channels, estimation under partial/stochastic coverage and human utility remain open. Unknown fixed phase origin and arbitrary fixed signed amplitudes are covered. No universal advantage over direct Fourier access is claimed.

## Source and execution ledger

Jay H. Beder and Margaret Ann McComack, *A note on the minimum size of an orthogonal array*, arXiv:1508.06558v1 (24 Aug 2015), https://arxiv.org/abs/1508.06558 ; https://doi.org/10.1080/03610926.2015.1071391 . Read the introduction, Section 1.1, Eq. (1)–(2) and Section 2 through Theorem 2.1 and its proof, PDF pp. 1–5; inspected page images 2–3. Their result identifies the necessary divisibility of equal-weight mixed-level arrays and the pairwise-coprime case. The cubic necessity theorem, finite weighted clock polynomial and exact positive span certificate above are direct derivations; no attribution of them to this source or claim of novelty/priority. The cited paper is not a human-audio experiment.

Repository reconciliation: AGENTS, README, RAG, programme, runbook, integrity and validation read; 434 live branch entries, 50 recent open issues and 50 recent open-PR search results; targeted quadrature, orthogonal array, CRT averaging, sparse sampling and three-wise searches. Complete #740 report, issue, comments (none) and PR #741 metadata read; exact-head workflow 45912876755 completed successfully. #740 remains Draft/HOLD. Fresh #744 created; comments empty; base 495a98ca12bae467a507031f04931aa4254b1866. Native git ls-remote blocked by DNS resolution, so no repository-wide local validation asserted. No changes to predecessor branches or canonical manifests.

Run node laboratory.cjs and node certificate.cjs. The V8 executions verify 131,474 exact residue buckets, 180 literal clean moments, 192 stationary-noise phase-ensemble profiles, 17 negative checks, plus the 886 exact triple buckets and 22 exact dual identities in the separate certificate. No assertion failures. Both arithmetic programs were replayed in V8 and their source and JSON were read back byte-equivalent as text from the fresh branch. Native Python/SymPy/SciPy was used for the small signed-polynomial exploration and LP discovery; the committed solver-independent exact certificate, not floating feasibility, supports the sharp result. No native Node process or full checkout executed. Same-agent cross-checks, not independent review.

Interpretation: the clock has acquired a second role. It not only provides a reference for distinguishing the components, it distributes the observer's attention nonuniformly over time. Exact finite sampling is a combinatorial balance contract. The likely MHAC experiment is a weighted cubic inspector with an explicit display of aperture, acquisition span, marginal exactness, weight concentration and noise regime. This is an unvalidated design hypothesis, not a VST implementation or safety-critical recommendation. Conventional probability, Fourier analysis and combinatorial design account for all established results; no incremental cybersemiotic explanatory contribution established.

Fiction: the clerk asks whether every witness has spoken the same number of times. The apprentice shows him a ledger where every triple has been heard in proportion, although some ticks count more than others.
