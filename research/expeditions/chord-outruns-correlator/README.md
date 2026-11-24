# The Chord That Outruns Its Correlator

Refs #412 · 24 November 2026 · Original exploratory mathematics, synthetic computation, musical proposal and fiction. One ChatGPT agent conducted the source reading, derivations, implementation and self-check. No independent or human review, priority claim, participant result or advancement of the frozen Track E/G corpus.

## Contents

1. [Anomaly](#1-anomaly) — phase information can require arbitrarily high correlation order.
2. [Measurement law](#2-measurement-law) — translation-invariant products and an integer relation lattice.
3. [Contiguous support](#3-contiguous-support) — sharp order for identifying a cyclic sampled score.
4. [Two distant tones](#4-two-distant-tones) — sharp continuous and finite-cyclic thresholds; rank suffices in dimension two.
5. [Pilot paradox](#5-pilot-paradox) — exact identifiability at vanishing numerical margin.
6. [Laboratory and score](#6-laboratory-and-score) — executed checks, original PCM and a compositional proposal.
7. [Sources and limits](#7-sources-and-limits) — prior art, contrary cases and the repository checkpoint.

## 1. Anomaly

A machine records an entire period of a signal, but its summary must not depend on which point in the period was chosen as the time origin. It retains power spectra, then triple correlations, then fourth-order correlations and so forth. Surely every new order reveals more of the signal's shape?

For a fundamental and its seventh harmonic, the two positive periodic functions

    f+(t) = 5 + 2 cos(t) + 2 cos(7t)
    f-(t) = 5 + 2 cos(t) - 2 cos(7t)

have all their translation-averaged correlations of orders one through seven exactly equal, at *every* lag tuple. They are not time translations: the fundamental fixes the translation modulo a period, at which the seventh harmonic is also unchanged. The eighth-order moment alone already differs. This is stronger than a matched magnitude spectrum, and different from reflection: both functions here are even.

No universal auditory claim follows. This is a problem about an invariant measurement, not the entire waveform or a listener. The choice of nuisance group matters too: a discrete integer sample origin and an arbitrary continuous time origin are not the same equivalence.

## 2. Measurement law

For a real periodic f on the circle, or a real sequence on Z/NZ, normalize integration or summation by one period. Define

    C_r(t_1,...,t_(r-1)) = average_x f(x) product_i f(x+t_i).

We use Fourier coefficients with inverse expansion sum_j F_j exp(ijt) on the circle, or sum_j F_j exp(2pi i j t/N) on the cyclic group. Fourier expansion in the lag coordinates gives products of r coefficients whose frequencies sum to zero in the underlying frequency group. All products of that order occur. This is the k-deck/Fourier identity of Jaming and Kolountzakis, §2.1, equations (2.1)–(2.3), adapted to finite cyclic and periodic discrete spectra.

Assume positive real DC D and specified nonzero magnitudes on a symmetric support, with conjugate coefficient pairs. DC allows padding lower orders by zeros: order r>=2 recovers D from the all-zero product and magnitudes from j,-j,0,...,0. To permit every phase in the proofs within nonnegative functions, choose D>2 sum of positive-frequency magnitudes. This sufficient bound is not necessary. Exclude the Nyquist singleton for the cyclic model. Our comparisons use exact coefficients, not finite noisy estimates.

Write S+ = {s_1,...,s_d} for the positive-frequency indices, and phase ratios between two candidate spectra as exp(i alpha_j). A product involving net multiplicities v in Z^d has phase ratio exp(i v dot alpha). It is invariant under physical translation iff sum_j s_j v_j=0 on the circle, or equals 0 modulo N for the cyclic group. Its minimal order is the l1 length sum |v_j|; cancellations only increase length, and DC fills unused positions.

Let L_r be the integer span of these relation vectors of length at most r. Then the phase fiber is exactly

    {alpha in (R/2pi Z)^d : v dot alpha = 0 mod 2pi for all v in L_r}.

Full translation identification is equivalent to L_r equalling the full relation lattice L. Sufficiency follows because the resulting character on Z^d descends to the image of the frequency map, a cyclic group (infinite on the circle or finite in the sampled case), and all characters of that image arise by physical translation. Necessity: if L_r is a proper sublattice, the finitely generated abelian quotient L/L_r has a nontrivial circle character; it extends to Z^d/L_r (e.g. via Smith normal form and divisibility of the circle group). Hence there is a phase difference invisible at order r that is not a physical translation. In the worked one- and two-dimensional cases below the proof is also explicit. This is an exact algebraic criterion, not a computational guarantee for estimating high-dimensional correlations in noise.

## 3. Contiguous support

**Theorem A (sharp cyclic order).** Let N>=3 and 1<=k<N/2. Suppose every Fourier coefficient with index in {-k,...,k} is nonzero, all others zero, and DC is positive. Uniform identification of the phase configuration up to *integer* cyclic translation from the order-r deck is guaranteed at

    r_min = ceil(N/k).

This sharp worst-case result holds even for strictly positive signals with a sufficiently large fixed DC.

Proof. The threshold is at least three. For k>=2, the triple products F_1 F_j conjugate(F_(j+1)), j=1,...,k-1, give ratio equations alpha_(j+1)=alpha_1+alpha_j. Thus alpha_j=j alpha_1; for k=1 this already holds. Put r=ceil(N/k). There are r positive integers at most k summing to N (use r-1 copies of k and the positive remainder). Their product is included in the cyclic r-deck and imposes N alpha_1=0 modulo 2pi. Hence alpha_1=2pi t/N for integer t, exactly a discrete translation. Conversely, for any r'<r, every zero-sum-mod-N tuple of r' signed indices sums to zero as integers since its absolute sum is less than N. Multiplying F_j by exp(i j beta) leaves every such product unchanged. A beta not in (2pi/N)Z yields a noninteger displacement and distinct cyclic translation classes, since F_1 is nonzero. Large DC ensures both sequences remain strictly positive. This covers even the absence of triple constraints at r'=1 or 2. QED.

For N=64, the thresholds for k=1,2,4,8,16,22 are 64,32,16,8,4,3 respectively. When N>3k, all triple correlations can at best identify the contiguous-support interpolating trigonometric polynomial up to arbitrary continuous time shift (assuming k>=2); they cannot identify its integer sample origin. When N<=3k, the wrap product removes this continuous ambiguity. On the continuous circle the integer-origin constraint does not exist and order three suffices for contiguous support k>=2; order two suffices for the single-tone k=1 case. Therefore increasing sampling resolution while keeping harmonic bandwidth fixed can increase the required order for *discrete* identification without increasing the order for the physically continuous translation quotient. Do not confuse the two tasks.

The proof also gives a sparse Fourier-product certificate: k-1 nonwrapped triple products and one wrap product, besides known magnitudes/DC. No claim is made that this is the minimum number of scalar real observations under all possible measurement architectures.

## 4. Two distant tones

**Theorem B (continuous circle).** For two distinct positive harmonic indices p,q with g=gcd(p,q), the exact order required to recover the relative phase up to continuous translation is (p+q)/g. The full relation lattice consists of integer multiples of (q/g,-p/g), since ap+bq=0 iff (a,b)=h(q/g,-p/g). The first nonzero such vector has l1 length (p+q)/g. Below that length every admissible Fourier product cancels the two phases separately. At that length the product

    F_p^(q/g) conjugate(F_q)^(p/g)

fixes the invariant phase (q/g)theta_p-(p/g)theta_q. Its kernel consists precisely of continuous translations, because the reduced integers p/g,q/g are coprime. In particular a fundamental plus harmonic m requires order m+1, however accurate the lower-order summaries.

For the two positive functions in §1, changing the sign of the high tone alters the first admissible relation product by 2 in the chosen normalization. Ordinary moments are the zero-lag special case: expanding f^r, the constant term first changes at r=m+1. The two nonzero relation directions contribute m+1 identical terms each, and their signs invert, so the difference in mean f^(m+1) is exactly 4(m+1). All other terms cancel in the comparison. For m=7 this is 32. Lower moments and *all* lower-order lag products agree.

**Theorem C (finite cyclic two-tone rule).** For 1<=p<q<N/2, define the rank-two lattice

    L = {(a,b) in Z^2 : ap+bq = 0 mod N}.

Its index in Z^2 is N/gcd(N,p,q) by the image of the frequency homomorphism. Then the first complete order is the smallest r for which there are two linearly independent vectors in L with l1 norm at most r. This is the second successive minimum of L in the l1 norm. It is not merely the first nonzero relation. It can be computed by enumerating integer vectors in successive diamonds. Pure axis vectors of lengths N/gcd(N,p), N/gcd(N,q) show the threshold never exceeds N.

Proof of the unexpected rank-to-saturation step. Choose independent u,v in L in the closed radius-r diamond. They generate a full-rank sublattice M. Every coset of M in L has a representative w=s u+t v with |s|,|t|<=1/2, obtained by rounding real coordinates of a lattice point in the basis u,v. This representative is in L and ||w||_1 <= (||u||_1+||v||_1)/2 <= r. Hence all cosets have representatives in the measured diamond; together with u,v they generate all of L. Conversely rank less than two leaves a continuous family of phase ratios, whereas physical cyclic translations form a finite set. QED. This rank argument is special to two dimensions; the same rounding proof in d dimensions only gives d r/2, not r.

The executable cross-checks the integer span criterion using the gcd of 2x2 determinants (the full-rank lattice index, by integer row/column elimination) and independently enumerates finite-grid phase ratios for small N, forming constraints from literal signed frequency multisets.

Examples:
- N=31, p=4, q=7: order 6 exposes (1,-5); order 7 adds (6,1). Their determinant has magnitude 31. The discrete threshold is 7, versus continuous order 11.
- N=64, p=1, q=7: the continuous threshold is 8, but cyclic identification also needs (1,9), giving threshold 10.
- N=17, p=1, q=7: (3,2) and (1,-5) have determinant -17; threshold 6, less than continuous order 8.

Thus sampling can either introduce earlier distinguishing constraints by modular aliasing or impose an additional origin-identification burden. Neither ordering of thresholds is universal. These examples concern exact finite cyclic Fourier products, not a recommendation to deliberately undersample sound.

## 5. Pilot paradox

Insert all intermediate harmonics 2,...,m-1 into a fundamental/high-tone pair with m>=3. Give every inserted Fourier coefficient the same positive real magnitude rho, with rho<=min(A,B), where A=|F_1| and B=|F_m|. On the continuous circle, the recurrence in Theorem A now identifies every phase up to translation from order three. This is an exact repair for any rho>0, no matter how small.

But compare two such spectra differing only by inversion of F_m (and its conjugate), keeping pilots identical. Every differing triple product must contain exactly one high-tone factor; two opposite high tones cancel, and two same-sign high tones cannot sum to zero with another supported frequency. The remaining two factors must sum to m or -m and include at least one pilot because m>=3. Thus the maximum absolute difference of any triple-product coordinate is exactly

    Delta_B = 2 A B rho

provided the other low-frequency magnitudes are A and rho as stipulated, and all pilots are nonzero. Attainment is the product at 1,m-1,-m; other differing products with two pilots have difference 2B rho^2 <= 2AB rho. Terms containing DC or no high tone are unchanged. If each complex triple-product coordinate has independent bounded absolute error eta, the two possible observation boxes intersect iff eta>=AB rho. This is a sharp two-candidate adversarial statement, not a global stable inversion theorem.

Exact recovery therefore jumps discontinuously at rho=0, while the relevant measurement margin tends continuously to zero. For A=B=1, rho=0.001, the ideal maximum third-order witness difference is 0.002. A zero-error structural certificate must not be substituted for a noise-aware certificate.

A sparse constructive alternative uses an addition chain from 1 to m: whenever a new harmonic is the sum of two already fixed harmonics, a nonzero triple product fixes its phase ratio. For m=2^h, the chain of powers of two uses h-1 pilot frequencies. This is an upper bound on pilot count, not a proof of minimum; arbitrary sum/difference relations or simultaneous equations may do better. A single arbitrarily placed pilot need not connect all phase degrees of freedom. Pilot tones also change the physical sound and may consume dynamic range or conflict with other message channels; the model makes no claim of perceptual invisibility.

## 6. Laboratory and score

Run from this directory with Python >=3.11:

    python laboratory.py --out results > execution.json

The standard-library implementation uses integer sums, relation shell enumeration, determinant gcd, finite modular phase grids and exact Laurent-polynomial convolution. The grid is a separate implementation check rather than a proof over all continuous phases; its resolution 2N can fail to sample some hypothetical finite ambiguities. The rank/saturation argument above explains why none appeared in the two-tone census. Actual executed Python 3.13.5 receipt:

| Check | Count |
|---|---:|
| Contiguous support wrap-sum checks | 12,894 |
| Continuous relation shell checks | 17,933 |
| Finite cyclic two-tone profiles (N=5..50) | 4,600 |
| Direct finite phase-grid comparisons at threshold (N<=16) | 112 |
| Exact integer moment coefficient checks | 228 |
| Assertion failures | 0 |

No observed gap between the first rank-two shell and full lattice generation; this motivated the rounding proof. No missed lower-order ambiguity on the 112 finite-grid profiles. The receipt reproduced byte-for-byte on a second native run. Source Git blob a58fbf323a00eb6a7c669681f38429aa47d24330; receipt Git blob 5acb7e7fed1c665d7d4afd6fbe238acf35a68e15. Both were fetched back from GitHub and matched local hashes. Counts are loop-specific, not independent statistical samples. The pilot result is an analytical derivation, not included in these test counts.

The original score is two one-second mono PCM16 files at 8 kHz: aligned.wav and inverted.wav. They contain 200 Hz and 1400 Hz tones at equal gain; only the sign of the upper harmonic changes. They are zero-mean AC renderings of the two positive mathematical functions, with quantization. The exact correlation equality is proved for the ideal continuous waveforms with DC, not for arbitrary quantized PCM measurements or their finite-window feature estimates. The executable writes both files and records SHA-256; they differ byte-for-byte. No listener test is conducted. No third-party recording is used.

**Speculative instrument — The Order Organ.** Let the performer choose a fundamental, a high harmonic, their relative phase and a bank of optional pilot harmonics. A separate observer can request the correlation order or individual product witness. Provide two audition routes: the original chord and an explicit sonification of the selected invariant. One performer can alter the chord while every selected summary remains invariant; the other can buy a new order of observation or insert a pilot to expose the concealed dimension. This is a proposed composition procedure, not a completed instrument. The PCM demonstration is implemented. A design hypothesis for MHAC: any descriptor intended to preserve a distinction must name its permitted support, nuisance group and error bounds. Test with phase-adversarial synthetic pairs before considering empirical comprehension research.

**Original fiction.** A bellmaker gives a clerk two bells and a ledger with seven columns. For every way the clerk can shift his ruler the columns agree. The apprentice inserts a wire so thin it almost fails to ring. The third column now trembles. The clerk announces that the distinction is finally measurable. The apprentice writes a second number beneath his declaration: the precision it will cost.

## 7. Sources and limits

Source ledger, 24 November 2026:
- Philippe Jaming and Mihail N. Kolountzakis, *Reconstruction of functions from their triple correlations*, arXiv:math/0207051v2 (20 June 2003), https://arxiv.org/pdf/math/0207051. Read introduction, §2.1 equations (2.1)–(2.3), Lemma 2.1, and §2.3 Theorem 2.4, Proposition 2.5 and Lemma 2.6 (PDF indices 0–5, especially page images at indices 3 and 5; printed pp. 4 and 6). Source already establishes spectral-gap phase ambiguity and smooth nonnegative functions not determined by any prescribed finite order on the real line. Our periodic support-specific thresholds, second-successive-minimum formulation and pilot noise comparison are elementary specializations/extensions explored here, not claims to discovery of the general ambiguity or priority.
- Tamas Keleti and Mihail N. Kolountzakis, *On the determination of sets by their triple correlation in finite cyclic groups*, arXiv:math/0603415, https://arxiv.org/abs/math/0603415. Abstract inspected only. Important contrary class: indicator functions have additional algebraic constraints, so the nonnegative general-weight results here do not transfer to binary rhythms without proof.
- Luke Pebody, *The Reconstructibility of Finite Abelian Groups*, Combinatorics, Probability and Computing 13 (2004), 867–892, DOI 10.1017/S0963548303005807, https://doi.org/10.1017/S0963548303005807. Publisher abstract only. Reports finite bounds for reconstructing *sets*, a different problem from arbitrary weighted Fourier coefficients. No theorem-level attribution beyond the abstract.
- Internal predecessor #199, The Spectral Doppelgänger, branch mhac-expedition/spectral-doppelganger-199: full README inspected. Its binary antipodal homometry and fourth-order repair are not our weighted spectral-support result. Its source ledger cited Jaming at abstract level; this expedition reads the relevant equations and negative result. #380 (branch mhac-380/chord-cannot-name-hand): read model and generic/worst-case sections; concerns cosine graph edges between equal-frequency phasors, unlike our translation-weighted frequency relations. #404 distinguishes tempo nuisance from expression, rather than correlation order.

Contrary cases and limits: an external time reference or raw waveform makes this particular invariant ambiguity unnecessary. Binary support, positivity without a sufficiently large DC, unknown amplitudes, Nyquist modes, stochastic phase drift, windowing, finite precision, physical propagation and human perceptual organization require separate analysis. Exact third-order sufficiency for fully supported spectra is classical; the current results do not discredit bispectral analysis. Higher-order products can be noisy and numerous. An acoustic receiver might detect phase differences through other mechanisms even when these descriptors collide. No conclusion about human comprehension, affect, listening benefit, Brier's endorsement or operational warning reliability is asserted.

Repository checkpoint: reconciled main at 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, README, RAG, programme, runbook, integrity, validation, human gates and project foundations inspected. 265 branch names across paginated listings (terminal empty page), two recent issue/PR search requests returned 100 records each but overlapping issue results; targeted homometry/turnpike/autocorrelation/bispectrum search and predecessor files used to narrow overlap, not establish exhaustive novelty. #405 predecessor exact-head workflow reports success. Issue #412 read back in full, no comments at creation. Native checkout failed DNS resolution; full repository validation not run locally. Only additive files under this expedition on mhac-412/chord-outruns-correlator; no shared manifests, branches or frozen records modified. Draft PR for integration/critique, Refs #412, no merge or independent acceptance claimed. Source and receipt hashes verified; native laboratory executed twice; full repository CI and independent mathematical review remain separate acceptance items.
