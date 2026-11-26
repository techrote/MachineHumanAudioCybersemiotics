# The Chord That Needs Three Taps

Refs #729 · 26 November 2026 · Exploratory mathematics and exact synthetic DSP. Single ChatGPT agent performed source reading, derivation, implementation and self-review. No independent human critique, perception trial or physical transmission measurement.

## Anomaly and scope

The preceding [#724](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/724) constructed integer signals whose cumulative cyclic correlation decks agree through order five. A sixth moment can expose their relative signs, but can also collide. This expedition asks whether a short linear prefilter followed by a cubic processor and an ordinary energy meter can target a specific relationship rather than summing all relationships indiscriminately.

Let p_i be distinct odd primes, A_i positive integer amplitudes, s_i signs, P=product p_i, N=2P, and R_p(t)=p-1 on multiples of p and -1 elsewhere. The family is x_s(t)=(-1)^t sum_i s_i A_i R_(p_i)(t). Time is cyclic and the observation covers a full period. Simultaneous sign inversion is a translation. The exact fifth-order invariance is established in #724; the present work does not reassert novelty of integer correlation collisions. For primes >=5 the earlier fourth-order fiber theorem also identifies the complete real-valued candidate class; here the probes operate on the declared sign family, not arbitrary spectra.

## Residue buckets and the two-tap obstruction

For distinct nonnegative delays d_l and real weights w_l with sum w_l=0, define a parity-balanced FIR

    y(t) = sum_l (-1)^(d_l) w_l x_s(t+d_l).

This forward cyclic convention can be converted to a causal FIR by a common time shift (energy and histograms unchanged). Parity balance annihilates the alternating carrier, not necessarily DC. Ordinary DC balance is sum_l (-1)^(d_l) w_l=0, a separate condition.

For uniform cyclic T, the CRT makes parity and every private prime residue independent. Then

    y(T) = (-1)^T sum_i s_i Z_i,
    Z_i = p_i A_i b_i(T mod p_i),
    b_i(r) = sum_(l: -d_l=r mod p_i) w_l.

Each Z_i is centered and independent; its kth moment is (p_i A_i)^k/p_i times the sum of kth powers of its p_i buckets. This equality follows directly from R_p=p*indicator-1 and sum w_l=0.

**Theorem 1 (histogram obstruction).** A parity-balanced two-tap FIR has identical complete output amplitude histograms for every s. Its weights are w,-w. In each private group either the residues coincide and Z_i=0 or there are two opposite buckets of equal multiplicity. Each Z_i has a reflection-symmetric law; flipping any sign leaves its distribution unchanged. Independence implies the same for their sum and the final parity factor. Therefore every memoryless transformation followed by any statistic of the single-sample distribution, not just a sixth moment, is blind to the signs. This does NOT rule out lagged statistics or filters without parity balance.

## Three-tap theorem and exact calibration

For three nonzero parity-compensated weights a,b,c with a+b+c=0, a private component has nonzero third moment precisely when all three delay residues are distinct modulo its prime. If all coincide it vanishes. If two coincide, the buckets are opposite and its third moment vanishes. If all are distinct,

    g_i = E Z_i^3 = p_i^2 A_i^3 (a^3+b^3+c^3)
        = 3abc p_i^2 A_i^3 != 0.

For any balanced FIR, define m_ik=E Z_i^k. Expanding the sixth moment of y gives

    E y^6 = K + 20 sum_(i<j) g_i g_j s_i s_j,
    K = sum_i m_i6
        +15 sum_(i<j)(m_i4 m_j2 + m_i2 m_j4)
        +90 sum_(i<j<k) m_i2 m_j2 m_k2.

All terms with an exponent one vanish by centering. The only remaining sign-dependent partition of six is 3+3, with multinomial coefficient 20. These are full-period mean-square energies of the cubic output. No floating-point approximation is required.

For target components i,j put D=P/(p_i p_j), take delays 0,D,2D and weights 1,1,-2 before parity compensation. Since D is odd, actual FIR taps are 1,-1,-2. Every other component is annihilated, while the target residues are distinct (even for p=3). Then

    E y^6 = K_ij + G_ij s_i s_j,
    G_ij = 720 p_i^2 p_j^2 A_i^3 A_j^3,
    K_ij = 66(p_i^5 A_i^6 + p_j^5 A_j^6)
           +1620(p_i^3 p_j A_i^4 A_j^2 + p_i p_j^3 A_i^2 A_j^4).

Proof: Z_i takes p_i A_i twice, -2p_i A_i once, and zero on p_i-3 residues. Thus even moment k is (2+2^k)p_i^(k-1) A_i^k and g_i=-6p_i^2 A_i^3. Insert into the preceding expansion. The calibrated energy midpoint determines one relative sign; the two energies differ by 2G_ij. Using edges of any spanning tree recovers the m-1 independent signs. At least m-1 binary pair receipts are necessary, even adaptively. This lower bound is not a claim about arbitrary high-precision aggregated scalars.

Three taps are minimal for this parity-balanced histogram-based task by Theorem 1. A polynomial of degree <=2 after any common FIR cannot expose the sign family through mean-square energy or complete output autocorrelation: expansion uses only original factors of order <=4, which already agree. Cubic is the minimum polynomial degree under this measurement contract.

## Exact spectral isolation versus selective testimony

**Theorem 2 (sharp isolation span).** With three distinct integer taps of nonzero weights summing to zero, annihilating a non-target prime component requires all three delays congruent modulo that prime. Otherwise a nonzero singleton residue bucket survives. Thus all delay differences are multiples of D. Three distinct positions have span at least 2D, attained by 0,D,2D. If ordinary DC balance is additionally required, all three taps must have the same parity: with mixed parities a singleton parity class would be forced to have weight zero. Then differences are multiples of 2D and the sharp span is 4D, attained by 0,2D,4D. The statement uses linear delay span, not a bound on arbitrary-length FIRs.

For pair-isolating receipts, the minimum total span over spanning trees is achieved by connecting every smaller prime to the largest prime. Root any tree at the largest prime; each edge from i to its parent has cost at least 2P/(p_i p_max). The star attains each lower bound. It also minimizes the maximum edge span by the same reasoning applied to the smallest prime. With extra DC balance all these costs double.

**But annihilation is more than the measurement needs.** To make a component irrelevant to the sign-dependent energy, it suffices that its third moment be zero. It can still contribute to the known baseline K. With delays 0,d,e and weights 1,1,-2, define the active set

    S(d,e) = {i : p_i does not divide d, e or e-d}.

If S(d,e)={i,j}, then the calibrated cubic energy still gives exactly one pair sign with the same G_ij as above, even if other components remain in the filtered waveform. Its K must be computed from the full bucket formula. This distinction produces much shorter spans.

Every excluded prime divides d*e*(e-d), hence D divides that product. As 0<d<e, d(e-d)<=e^2/4, giving the necessary lower bound e^3>=4D. This is not sufficient and does not claim that the cubic-root order is universally attainable. The exact compiler enumerates e in increasing order and d from 1 to e-1, until the desired active set appears. It must terminate by 2D via the isolating construction. This brute-force algorithm is not intended for huge prime products.

Five-prime unit-amplitude example p=(5,7,11,13,17), N=170170:

| Target pair | Shortest selective delays | Exact isolation span |
|---|---|---:|
| 5,7 | 0,17,39 | 4862 |
| 5,11 | 0,13,34 | 3094 |
| 5,13 | 0,11,28 | 2618 |
| 5,17 | 0,7,33 | 2002 |
| 7,11 | 0,13,30 | 2210 |
| 7,13 | 0,5,22 | 1870 |
| 7,17 | 0,11,26 | 1430 |
| 11,13 | 0,7,17 | 1190 |
| 11,17 | 0,7,20 | 910 |
| 13,17 | 0,10,21 | 770 |

These are exact finite-search optima for the specified three-tap contract. For (5,17), 7 divides d, 11 divides e, and 13 divides e-d. Neither 5 nor 17 divides any of the three differences. All three unwanted components have zero skew rather than zero output. The span is 33 instead of 2002, a factor of about 60.7. The shortest selective tree uses (5,13), (7,13), (11,13), (11,17), total span 87. Enumeration of all 125 spanning trees confirms this. The largest-prime star has selective cost 100 and is no longer optimal. Its exact-isolation cost is 5112. Summed span is a declared scheduling proxy, not a measured RAM, latency or CPU metric; shared buffers may change implementation cost.

## Counterexample, bounded perturbation and acoustic realization

The known raw sixth-moment collision from #724 uses signs (+,+,+,-,+) versus (+,+,+,-,-). Both raw sixth moments equal 5111904. Isolating the pair (5,17) at span 2002 yields energies 142356612 versus 131952612. The shorter selective span 33 yields 409314236 versus 398910236. The baseline changes, the gap 10404000 does not. Thus both repairs recover the hidden sign even where the unfiltered scalar fails. The larger baseline matters under finite precision: equal absolute gap does not mean equal relative contrast.

A deterministic perturbation guarantee for a calibrated isolated probe: if every input sample has error <=epsilon and the ideal filter output has magnitude <=B=2(p_i A_i+p_j A_j), then the FIR error is <=4epsilon and the sixth-energy error is <=24epsilon(B+4epsilon)^5 by the mean-value theorem. Correct midpoint decoding is certified if this is strictly below G_ij. For a selective (non-isolating) probe replace B by a valid bound including the remaining components, e.g. 2 sum_i p_i A_i. This is sufficient, conservative and assumes exact calibration, complete cyclic observation, no clipping and the same sample grid. Unknown gain, imperfect amplitudes, noninteger delays, partial periods, resampling and correlated measurement faults are not addressed.

Small audio witness: primes (5,7,11), unit amplitudes, signs (+++) vs (+-+), delays (0,11,22), actual taps (1,-1,-2). The exact cubic-output mean-square energies are 6393312 and 4629312; midpoint 5511312. Four original mono PCM16 WAV recipes use 15400 Hz, one second each, 20 complete periods. Raw files use integer scale 1000; processed files use unscaled integer cubes. Do not compare raw and processed levels as normalized listening stimuli; they deliberately preserve exact sample values within each pair. PCM was read back byte-for-byte, all 61600 samples recovered with no clipping. Listen quietly; these are unfiltered synthetic signals with strong upper partials. This establishes neither audible equivalence of the raw signals nor perceptual usefulness of the probe.

## Evidence and execution ledger

- Internal predecessor: full #724 report on its own branch inspected; exact-head PR #725 workflow 45894056296 completed successfully. This is structural CI, not acceptance of its mathematical claims. The previous fifth-order argument and scalar collision were checked against the actual report, not prior conversation alone.
- P. P. Vaidyanathan and S. Tenneti, *Srinivasa Ramanujan and signal-processing problems*, Philosophical Transactions A 378 (2163), 20180446, DOI https://doi.org/10.1098/rsta.2018.0446. Published online 9 December 2019, issue 24 January 2020. Open full-text HTML https://pmc.ncbi.nlm.nih.gov/articles/PMC6939226/ inspected at abstract, introduction equation 1.1 and section 3(c), equations 3.12–3.15, plus section 4 opening. The paper supplies established context for integer Ramanujan bases, decomposition and hidden periodicity analysis; it does not supply or validate the present parity-balanced cubic receipt construction. Its cited earlier Ramanujan work was not independently read. No scientific priority claim.
- Vaidyanathan, *Ramanujan Sums in the Context of Signal Processing—Part I: Fundamentals*, IEEE Transactions on Signal Processing 62(16), 4145–4157 (2014), DOI https://doi.org/10.1109/TSP.2014.2331617. IEEE abstract/metadata only, not a complete reading. Establishes ancestry of Ramanujan subspaces, not the present theorem.
- J. M. Mendel, *Tutorial on higher-order statistics (spectra) in signal processing and system theory*, Proceedings of the IEEE 79(3), 278–305 (1991), DOI https://doi.org/10.1109/5.75086. Bibliographic and abstract-level access only. Background lead on polyspectra and system identification; no theorem is attributed to unread text. The present moment proof is self-contained.
- Run python witness.py with Python 3.11+ standard library. Native Python 3.13.5 executed twice, identical output receipts and WAV hashes. Exact source Git blob aa49401f2830823a37fbb981d77d245b6ad49fc8 and receipt blob ddb4590724e82d07887d668fff3dd493f3469baf matched the locally executed files after commit.
- Computational scope: 1010 exhaustive delay profiles across three declared prime/weight fixtures, all classes' two-tap histograms compared; 52 isolated pair checks (including DC-balanced and prime-three cases); 640 direct versus independent residue-bucket histogram comparisons; 160 exact short-probe class energy checks across ten target pairs and 16 relative sign vectors; 125 spanning trees enumerated; literal 170170-sample collision witnesses evaluated; four WAV recipes roundtripped. No final assertion failure. Direct cyclic sample enumeration and bucket convolution are different formulations, but implemented by one agent. These finite checks support, rather than replace, the algebraic proof.
- Repository reconciliation: AGENTS, README, RAG, programme, runbook, integrity and validation read; 426 branch entries, 60 recent issue and 60 recent PR results, targeted nonlinear/filter/Ramanujan/cubic/delay searches reviewed. Fresh #729 read back, no comments. Base 495a98ca12bae467a507031f04931aa4254b1866. Native git ls-remote failed host resolution, so full native repository validation not run. Only the new expedition directory is changed. No canonical manifests, frozen research records or other workers' branches touched. Draft for independent mathematical critique and exact-head integrity checks, then integrator review. No human gate advanced.

## Interpretation and next design question

The distinction between physical removal and operational irrelevance is the useful bridge. A component can remain present in the sound yet cease to participate in a specific relational measurement. Conventional finite probability, harmonic algebra and DSP explain the results. Cybersemiotics has not been shown to add predictive power. A candidate Observatory or VST research control would select two known periodic components, compile a short balanced probe, and display the calibrated cubic-energy receipt alongside its delay span and numerical uncertainty. This is a design hypothesis, not a deployed effect. Next questions: asymptotic selective span bounds, noisy/gain-invariant calibration, and comparison with direct Fourier phase access. Direct raw-signal access already resolves the declared sign family; nonlinear inspection is useful only under the specified descriptor or acquisition constraint.

**Fiction:** The clerk silences every witness who is not named in his question. His apprentice leaves the room full of voices, but changes the question so that the others cannot alter its answer.
