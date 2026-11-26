# The Chord That Needs Two Taps and a Memory

Refs #733 · 26 November 2026 · Exploratory exact synthetic DSP. One ChatGPT agent performed the source reading, proof, implementation and self-check. No human validation, scientific priority claim, or promotion of canonical evidence.

## Question and scope

[#729](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/729) proved that balanced two-tap filtering cannot expose the relative signs of the integer Ramanujan family through ANY single-sample histogram statistic. It used three taps and cubic energy to recover selected sign relationships. This expedition asks whether the missing resource was a third tap or a memory of a second observation. The earlier impossibility remains true; changing the measurement contract opens an exact repair.

Let p_i be distinct odd primes, A_i positive integers, s_i in {-1,+1}, P=product p_i, N=2P. The input is

    x_s(t)=(-1)^t sum_i s_i A_i R_(p_i)(t),
    R_p(t)=p*1_(p divides t)-1.

All averages are over a complete cyclic period; input is the declared family from #724, not arbitrary real signals. Common inversion of all signs is a cyclic translation. The parity-balanced two-tap FIR is

    y(t)=x(t)-(-1)^d x(t+d), d>0.

Its output is (-1)^t sum_i s_i Z_i(t), where Z_i(t)=p_i A_i(1_(t=0 mod p_i)-1_(t=-d mod p_i)). The CRT makes all private residues and parity independent for uniform cyclic time. Each private marginal is symmetric and centered; the complete output histogram does not depend on s, so no memoryless nonlinearity and zero-lag statistic can help.

## Lagged cubic receipt theorem

Put W_i(t)=Z_i(t+l), l>0, and measure the parity-corrected ordinary autocorrelation of the cubic output:

    C(d,l)=(-1)^l E[y(t)^3 y(t+l)^3].

The carrier cancels. Each pair (Z_i,W_i) is independent of the other pairs, though Z_i and W_i need not be independent. Define

    h_i = E[Z_i^2 W_i]
        = p_i^2 A_i^3 (1_(l=d mod p_i)-1_(l=-d mod p_i)).

Proof: if d=0 mod p the component is zero and both indicators agree. Otherwise Z_i^2 is nonzero on residues 0 and -d, and evaluating W_i at those two residues gives the difference displayed above; the terms for l=0 cancel. Stationarity (or the same direct calculation) gives E[Z_i W_i^2]=-h_i. E Z_i^3=E W_i^3=0 by marginal symmetry.

Expand the product of the two cubics by multinomial coefficients. Terms with a private component of total degree one vanish by centering. Of all partitions of six with no ones, the only one involving odd degrees is 3+3. In that partition the degree splits (3,0) and (0,3) vanish because marginal thirds vanish. The two remaining allocations (2,1)+(1,2) each have coefficient 9 and moment product -h_i h_j. Hence

    C(d,l)=K(d,l)-18 sum_(i<j) h_i h_j s_i s_j,

where K is independent of the signs. Exact midpoint K can be computed without knowing them: multiply the private bivariate exponential-generating polynomials with coefficients E[Z_i^a W_i^b]/(a! b!) for 0<=a,b<=3, retaining only even a+b for each factor. Extract coefficient (3,3), multiply by 36. This is precisely the sign-independent part of the expansion.

A private component is active if exactly one of l-d or l+d is divisible by its prime. If exactly i,j are active, C-K recovers s_i s_j with magnitude 18 p_i^2 p_j^2 A_i^3 A_j^3. Thus even though the complete single-sample histogram of the cubed output is blind, one ordinary nonzero-lag correlation of that output can reveal a selected relation. This is a two-point sixth-order statistic of the original input, not a low-order counterexample to #724. Cubic degree is minimal under this polynomial-front-end autocorrelation contract: degree <=2 expands to input correlations of order <=4.

## Sharp aperture compiler

For two target primes i<j (here indices denote the prime values themselves), let D be the product of all other primes, with empty product one. Cost is the combined raw input aperture B=d+l: the four raw sample positions are t,t+d,t+l,t+d+l. A causal common shift realizes the same receipt. This counts span in samples, not acquisition duration, CPU cycles, buffer bytes or real-world latency.

**Theorem.** The minimum B over positive integer d,l producing an exactly pair-selective receipt is

    B_min = min(j, 2D).

Proof: if d!=l, the target prime j divides one of the two nonzero integers l-d or l+d, so B>=j. Equality is realized by d=(j-i)/2, l=(j+i)/2: l-d=i and l+d=j. These distinct primes activate exactly the targets, regardless of how many other primes are in the instrument. If d=l, a prime is active exactly when it does not divide d (all primes are odd). To exclude all other primes requires D|d and hence B>=2D; d=l=D attains equality since neither target divides D. These two cases exhaust all positive integer d,l. No numerical search or approximation enters the proof.

This differs from #729, where excluded primes had to divide one of three nonzero delay differences. Here, instead, the two chosen primes are placed directly into the sum and difference of a delay and a lag. Even adding further unwanted primes does not enlarge the distinct-delay solution.

For p=(5,7,11,13,17), D is large enough for every pair that B_min=max(i,j). Thus the pair (5,17) uses d=6,l=11, aperture 17. The previous selective three-tap energy span was 33 and the previous exact isolation span 2002. The smaller aperture does NOT preserve the same absolute energy gap: the statistic has changed. It avoids three taps at the expense of retaining a lagged cubic sample and accumulating cross-products.

All ten pair apertures, in lexicographic order, are 7,11,13,17,11,13,17,13,17,17. A spanning tree of four pair receipts recovers all relative signs; the minimum summed aperture is 7+11+13+17=48. Root any tree at the smallest prime. Each other vertex p has parent edge cost at least p, and the star attains the lower bound. This is not necessarily the unique optimum. The previous selective three-tap tree cost 87; exact-isolation tree cost 5112. These are comparable declared sums of raw-sample spans, not benchmarks of implementations.

## Negative controls and gain-invariant calibration

A one-tap cubic autocorrelation cannot achieve single-receipt exact pair selectivity when at least three components are present. To see this, drop the filter. For a private R_p component with amplitude A, the pure third moment is g=A^3(p-1)(p-2), and each mixed third moment at lag l equals k=g if p|l, otherwise -A^3(p-2). The sign-dependent coefficient of pair i,j in the carrier-corrected cubic autocorrelation is 2g_i g_j+18k_i k_j (two pure allocations and two mixed allocations). If neither or both primes divide the lag it is positive. If exactly one divides it, cancellation would require the other prime to equal 10, impossible. Thus every pair contributes for every lag. This does not rule out multiple receipts, weighted combinations, other nonlinearities, or direct raw-waveform identification. Two taps are minimal only for the stated single-lag, single-pair cubic contract with at least three components.

With a common unknown constant nonzero real gain gamma on the input, C scales by gamma^6. The ordinary filtered power is

    E[y^2] = 2 sum_(i: p_i does not divide d) p_i A_i^2.

It is sign independent and scales by gamma^2. The ratio C/(E[y^2])^3 therefore preserves the calibration under unknown common gain, including polarity reversal. Alternatively C/E[y^6] is a bounded parity-corrected correlation coefficient of the cubic signal, also gain invariant and with sign-independent denominator by the histogram theorem. Neither handles unknown relative component gains, nonstationary gain, clipping, timing errors or additive noise. The first ratio is not a correlation coefficient and can exceed one in absolute value.

The exact zero-lag obstruction survives even with the new two-tap design. A nonzero lag may still be uninformative if fewer than two components are active. Delay/lag perturbations can change the divisibility relations. A short aperture does not imply that a short observation window supplies an accurate full-period average.

## Concrete collision repair and audio

Five-prime fixture, unit amplitudes, sign vectors (+,+,+,-,+) and (+,+,+,-,-), complete period 170170. Both raw sixth moments are 5111904 (the #724/#729 scalar collision). At d=6,l=11:

| Quantity | First | Second |
|---|---:|---:|
| Corrected cubic autocorrelation | -1422360 | -1682460 |
| Filtered power | 106 | 106 |
| Raw sixth moment | 5111904 | 5111904 |

Midpoint -1552410; signed offset +/-130050; exact gap 260100. Both readings are negative: the sign of the raw correlation alone is not a valid decoder. Normalize by 106^3 if the common gain is unknown.

Small audio fixture p=(5,7,11), signs (+++) and (+-+), d=1,l=6, aperture 7. Both zero-lag cubic energies are 2061766. Corrected lag-six cubic autocorrelations are -169488 and -213588. Four mono PCM16 files are generated by witness.py (20 complete 770-sample periods, 15400 Hz, one second). Filtered specimens use integer scale 500 and cubes use scale 1. All 61600 sample values were read back exactly, peak <=12167. These are original digital witnesses, not normalized perceptual stimuli; listen at low volume. They establish neither perceptual equivalence nor actual human decoding performance.

## Evidence and reproducibility

- Read the full #729 report on its issue branch, PR #730 metadata and its exact-head successful repository workflow 45900361308. The structural check is not mathematical acceptance. The present proof is self-contained; neither predecessor needs to be merged.
- P. P. Vaidyanathan and S. Tenneti, *Srinivasa Ramanujan and signal-processing problems*, Philosophical Transactions A 378(2163), 20180446, https://doi.org/10.1098/rsta.2018.0446. Open full text https://pmc.ncbi.nlm.nih.gov/articles/PMC6939226/ inspected at abstract and introduction equation (1.1) and discussion of integer periodicity/subspace motivation. Context for Ramanujan signal representation; no attribution of this pair-selective receipt theorem.
- J. M. Mendel, *Tutorial on higher-order statistics (spectra) in signal processing and system theory: theoretical results and some applications*, Proc. IEEE 79(3), 278–305 (1991), https://doi.org/10.1109/5.75086. Author-hosted PDF https://sipi.usc.edu/~mendel/publications/HOSATutorial.pdf inspected at p. 278 introduction, including original page image: established background for higher-order statistics and the increased observation burden. The present statistic is a raw mixed moment, not a cumulant; no automatic Gaussian-noise immunity is claimed. Neither reading is a full article review. No priority search sufficient for novelty claims was performed.
- Run python witness.py (Python >=3.11, standard library). Native Python 3.13.5 ran twice with identical JSON receipts and WAV hashes. Tests: 1436 exact local mixed-moment profiles; 225 pair aperture optima over subsets of six primes, 13195 smaller aperture candidates excluded; 722 literal complete-period cubic correlation versus independent residue-polynomial predictions; 7087 one-tap coefficient negative controls; 26 exact common-gain checks; four WAV readbacks. No final assertion failure. Exact arithmetic via integer and Fraction, not floating-point numerical tolerances. Both formulations were implemented by one agent, not independent review. Expected source Git blob 954ef136bab273cebeef460110e3268a8e61e714; receipt blob 7b34f569af895ef7d25691d33ca5585f9fe8626d.
- Live reconciliation: AGENTS, README, RAG, programme, runbook, integrity and validation read; 428 branch entries, 60 recent open-issue search results and 60 recent PR search results, targeted lagged/cubic/two-tap/Ramanujan searches, new #733 body and empty comments read. Main base 495a98ca12bae467a507031f04931aa4254b1866. Native git ls-remote failed DNS; full checkout validation not executed. Only this fresh directory is changed. No canonical manifests, frozen records or other workers' branches touched. Draft/HOLD for independent mathematical critique and integrator review; no human gate advanced.

## Interpretation

A richer instantaneous transformation need not replace a weaker transformation with memory. The distinction is relevant to a future Observatory or VST experiment: a two-tap balanced FIR, cubic stage, lag register and calibrated cross-product accumulator can select a sign relationship at a short aperture. Real-time deployment, partial-cycle estimation, relative gain uncertainty, finite precision and auditory utility are open. Conventional probability, modular arithmetic and DSP suffice; cybersemiotics has not been shown to add explanatory power. A useful comparison is direct phase access, which already solves this declared family without nonlinear probes. The result is valuable only under the particular measurement contract.

**Fiction:** The clerk inspects every voice at the instant it speaks and finds nothing missing. The apprentice asks him to keep one statement until the next arrives. The missing relationship was between the statements, not inside either one.
