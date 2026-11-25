# The Waveform That Passes Both Mirrors

**Issue #502 | 2026-11-25 | Exploratory mathematical expedition, not canonical empirical evidence.**

## Question and result

Suppose an acoustic witness supplies the exact energy of every time sample and the exact power at every Fourier frequency. Must the waveform be determined, up to polarity and reversal? No. We construct a full-support real integer family with 2^m distinct members modulo polarity, at length N=3^m; 2^(m-1) remain after also identifying reversal. The cardinality grows exponentially in construction depth, not in N. We then characterize precisely which local intensity measurements can recover its hidden orientation bits, how early they can be observed, how coding reduces the required number of fault-tolerant probes, and how the benefit disappears as measurement precision deteriorates.

This is a constructive lower bound on the size of a joint magnitude fibre, not a claim that the displayed family exhausts the fibre for arbitrary m. It is an explicit exceptional family, not a claim of mathematical priority or generic nonuniqueness.

## Source and repository reconciliation

Read live AGENTS.md, README.md, RAG.md, docs/PROGRAMME.md, docs/AGENT_RUNBOOK.md, docs/RESEARCH_INTEGRITY.md and docs/VALIDATION.md. Base main commit 495a98ca12bae467a507031f04931aa4254b1866. Reconciled 311 branch names across all returned pages, 100 recent open issue results and 100 open PR results. Preceding expedition #493 had successful exact-head workflow run 45555938811. Read the complete issue bodies of #199, #412, #372, #380 and their empty comment collections. #199 treats circular binary homometry; #412 treats periodic higher-order correlations; #372 treats arbitrary real-sign pair probes with silent coordinates; #380 treats unsigned complex orientation. This work uses a special full-support aperiodic joint-magnitude fibre whose probe structure is a linear code over hidden factor orientations. Targeted searches for Pauli, phaseless, minimum phase, zero flipping and time-domain magnitudes returned no matching issues. This is a bounded duplicate search, not proof of absence. Only this new expedition directory is modified.

Source ledger (accessed 2026-11-25 by the same AI research agent):

- Robert Beinert and Gerlind Plonka, *Enforcing uniqueness in one-dimensional phase retrieval by additional signal information in time domain*, ACHA 45(3), 505–525 (2018), DOI https://doi.org/10.1016/j.acha.2016.12.002. Open preprint https://arxiv.org/abs/1604.04493 (v1, 15 April 2016): read introduction and selected §3 results, inspected original page images of printed pp. 3, 10–11 (PDF indices 2,9,10). Theorem 3.4 and Corollary 3.5 establish almost-everywhere uniqueness in the complex finite-support model with extra time-domain magnitudes. Theorem 3.6 exhibits exceptional complex signals of every length N>3 with nonunique joint magnitudes. This is a direct contrary constraint against claiming our obstruction is generic or the basic ambiguity new. Publisher DOI full-text redirect failed; the preprint is the version used for mathematical locators.
- Beinert and Plonka, *One-Dimensional Discrete-Time Phase Retrieval* (2020), pp. 603–627, https://doi.org/10.1007/978-3-030-34413-9_24. Read open chapter §§24.1–24.3 through Theorem 24.1. Equations 24.1–24.5 connect Fourier intensity, aperiodic autocorrelation and factor reversal/zero reflection. The factor-reversal construction below is an application of that established mechanism.
- R. W. Hamming, *Error Detecting and Error Correcting Codes*, Bell System Technical Journal 29(2), 147–160 (1950), https://doi.org/10.1002/j.1538-7305.1950.tb00463.x. Publisher metadata inspected; original full paper not read. The sphere bound and shortened binary Hamming construction below are proved self-contained; the citation is historical attribution.
- Rupp, Sieroka, Gutschalk and Dau (2008), *Representation of Auditory-Filter Phase Characteristics in the Cortex of Human Listeners*, https://doi.org/10.1152/jn.00778.2007. Read publisher abstract and introductory text: phase-related masking and auditory-filter phase response motivate caution, not evidence for our signals.
- Green and Rosen (2013), *Phase effects on the masking of speech by harmonic complexes: Variations with level*, JASA 134(4), 2876–2883, https://doi.org/10.1121/1.4820899; institutional abstract https://discovery.ucl.ac.uk/id/eprint/1415965/. Abstract-level reading only. Reported phase effects were limited at moderate levels under their conditions. The two auditory sources concern different stimuli/tasks and neither validates the present decoder or predicts audibility of these recordings.

No full corpus screening, new participants, independent review, protocol amendment or source promotion is performed. All proofs and fixtures below are original derivations for this model, with established mathematical ancestry.

## A family that defeats both mirrors

Use the real vectors u=(1,2,-1) and v=(-1,2,1)=reverse(u). Both have coordinate magnitudes (1,2,1), and their nonnegative-lag aperiodic autocorrelation is (6,0,-1).

Let b in {0,1}^m, let g_0=u and g_1=v, and define
\[
 X_b(z)=\prod_{j=0}^{m-1} G_{b_j}(z^{3^j}),\quad
 G_i(z)=\sum_{d=0}^2 g_i[d]z^d.
\]
Every n in [0,3^m-1] has unique ternary digits d_j(n), so the coefficient is
\[
 x_b[n]=\prod_j g_{b_j}[d_j(n)].
\]
No overlapping terms occur and all coefficients are nonzero. Every coefficient magnitude is independent of b. Because G_1(z)=z^2G_0(1/z), the two factors have identical magnitudes on the unit circle; all products have identical Fourier magnitudes for all frequencies, not just on a DFT grid. Total squared energy is 6^m. Equivalently every aperiodic autocorrelation coefficient is identical.

Let c=(3^m-1)/2, whose digits are all one. Then x_b[c]=2^m for all b. The coefficients at c+3^j are -2^(m-1) times (-1)^b_j. This proves distinctness, also modulo overall polarity since the center is fixed positive. Reversing the full vector changes every digit d to 2-d, so maps b to its bitwise complement. There are exactly 2^(m-1) reversal classes within this family. Fixed nonzero endpoints eliminate translation ambiguity under the anchored model.

At m=2, two nontrivially different signals are
- A=(1,2,-1,2,4,-2,-1,-2,1)
- B=(-1,2,1,-2,4,2,1,-2,-1)

Both have the same pointwise squared magnitudes and the same autocorrelation (36,0,-6,0,1,0,-6,0,1), listing nonnegative lags. They are not reversals or global polarity changes of one another. Exhaustive enumeration of all sign assignments with positive center verifies the entire joint-magnitude fibre has exactly four members for this specific length-nine example, and two at length three. No such exhaustiveness claim is made at larger depths.

## Local measurement is a binary parity language

Write a(n) for the m-bit mask with bit j set when d_j(n) is not one. Then
\[
 x_b[n]=x_0[n](-1)^{a(n)\cdot b}.
\]
The dot product is over F_2. A polarity-invariant pair intensity M_{ij}=(x_b[i]+x_b[j])^2 is equivalent, given the already known squared magnitudes, to measuring the signed product x_b[i]x_b[j]. After removing the known reference polarity, it returns exactly the parity (a(i) XOR a(j)) dot b. This holds for all distinct indices. A zero mask gives no information.

Every nonzero parity mask S is available: choose i=c and j=c+sum_{k in S}3^k (all selected ternary digits become two, the others remain one). Thus any binary linear code generator can be physically represented by a collection of these ideal pair intensities. The bit string is defined by the family, not inferred to be a human perceptual vocabulary.

For noiseless, nonadaptive pair probes the hidden orientation vector is uniquely identifiable iff the parity masks span F_2^m. At least m probes are needed even adaptively (each observation has at most two values, hence at most 2^q leaves at depth q). The m single-bit masks attain the bound. This result conditions on membership of the displayed family. It is not a full-fibre uniqueness theorem or an arbitrary phase retrieval bound.

### Prefix horizon and an adjacent-only surprise

Consider a receiver given the global magnitude receipts and access to any polarity-invariant information about the first L coefficients. For all j with 3^j>=L the ternary digit j is zero throughout that prefix. Flipping b_j merely flips every prefix sample, which the receiver cannot distinguish. Conversely for 3^j<L, the pair of samples at 3^j-1 and 3^j has a relative polarity that isolates b_j: the carry changes lower digits from two to zero, both outside the middle digit, while digit j moves from zero to one. Therefore exactly k=number of j with 3^j<L bits are accessible in the prefix; there are 2^k distinct prefix classes modulo global polarity, each with 2^(m-k) possible orientation vectors.

The sharp first full-identification prefix length is L*=3^(m-1)+1. The argument is independent of how complicated the prefix-only polarity-invariant decoder is. Global signed phase, an external phase reference, or simultaneous use of future raw coefficients changes the contract.

Every adjacent pair n,n+1 isolates exactly one bit, namely j=v_3(n+1), the exponent of three dividing n+1. Higher digits are unchanged, lower digits carry between outer values, and only digit j changes whether it is the middle digit. Hence adjacent pair intensity is a very restricted measurement language even though arbitrary pair intensity can express every parity. This is the mechanism behind the coding and conditioning penalties.

## Fault correction: local versus nonlocal

For fixed noiseless binary probes subject to t arbitrary bit errors and e flagged erasures, a collection of probes is adequate iff its induced binary linear code has minimum Hamming distance greater than 2t+e. Necessity: two codewords at distance <=2t+e can have their differences erased in e positions and the remaining differences split between the two adversarial error patterns. Sufficiency: indistinguishable receipts would imply a codeword distance <=2t+e.

For adjacent-only probes, a message differing in bit j differs only in the probes of type j. Thus every bit needs at least 2t+e+1 separately received probes, and the exact minimum is m(2t+e+1). Repeated probes are permitted; if the fault corrupts a physical sample rather than a probe receipt, correlated errors require a different analysis.

For arbitrary pair probes and one bit error, the exact minimum is n=m+r, where r is the least integer satisfying 2^r>=m+r+1. Proof: 2^m disjoint radius-one Hamming balls of size n+1 must fit in 2^n words. For attainment, choose m distinct nonzero nonunit r-bit columns and append the r unit columns. The resulting parity-check matrix has rank r and no zero or repeated column. Its nullspace has dimension m and minimum distance at least three; its systematic generator can be realized via the preceding parity-probe construction. Syndrome decoding corrects every single fault. For m=12, seventeen arbitrary pair receipts suffice, whereas thirty-six adjacent receipts are necessary. No general optimal code-length formula for larger t is claimed.

## Conditioning: the price of an informative measurement

Normalize all signals to unit energy by dividing by sqrt(6^m). For a parity mask of weight s>0, the two possible pair intensities differ by 4|x_0[i]x_0[j]|/6^m. At each toggled digit one coefficient has magnitude two and the other magnitude one; at each untoggled digit their product is at most four. Therefore the largest possible separation is exactly
\[
 \Delta_s=4(2/3)^m 2^{-s}.
\]
The center construction attains it. For additive error in each intensity bounded by epsilon, guaranteed discrimination of that parity requires epsilon<Delta_s/2, with strict inequality because the two closed intervals meet at equality.

For adjacent-only probes of type j, the lower j digits are both outer digits, the jth digit contributes a product of two, and the higher digits contribute at most four each. Thus the sharp maximum product is 2^(2m-2j-1), attainable by choosing higher digits all one and the jth digit moving from zero to one. The sharp largest intensity separation is
\[
 \Delta^{adj}_j=2(2/3)^m4^{-j}.
\]
Consequently all bits can be recovered through adjacent pair measurements under bounded additive error iff epsilon < (2/3)^m 4^{-(m-1)}. Arbitrary single-bit pair measurements instead tolerate epsilon < (2/3)^m. Nonlocal pair registration improves the worst-bit threshold by a factor 4^(m-1), even before coding.

There is also a sharp fixed-probe transition between analog precision and binary coding. For (2/3)^m/2 <= epsilon < (2/3)^m, every parity of weight >=2 can be hidden by a constant midpoint receipt independent of b, while optimal single-bit probes remain reliably distinguishable. Hence m(2t+e+1) is again the exact minimum for arbitrary pair probes with t additional adversarial receipts and e erasures: apply the same differing-single-bit argument after masking all higher-weight probes at their midpoints. Repetition achieves the bound. For epsilon >= (2/3)^m every pair can be hidden at its midpoint, making guaranteed recovery impossible for this measurement class. For epsilon < (2/3)^m 2^(1-m), even the highest-weight parity is guaranteed distinguishable, restoring the noiseless bit-code construction. Intermediate precision may permit some but not all code generators; optimization of weight-constrained codes is left open.

The thresholds depend on a prescribed normalization and additive error on the intensity itself. They do not transfer unchanged to amplitude noise, unknown gain, phase jitter, correlated sample faults, room acoustics, or a physical auditory system.

## Executable qualification and acoustic artefact

Run the exact integer JavaScript laboratory with Node.js:

    node laboratory.cjs

Its structured output should match execution.json. The tool's JS runtime ran the function twice with equal receipts; direct construction and correlation sums are exact within safe integer ranges. The census covers depths 1–5: 62 members, 9,330 autocorrelation cells, 9,330 squared-magnitude cells, 995,694 pair-parity comparisons, 363 prefix profiles, 9,268 adjacent checks, 260 full sign-census candidates at depths 1–2. It also checks 8,190 codewords across m=1–12 and 6,104 literal zero/single-error decoding receipts for m<=8. No assertion failed.

Run the independent-method standard-library Python witness:

    python witness.py

The native execution used direct ternary-index products rather than the JS repeated block expansion. It checked all 126 members through depth six (55,986 direct nonnegative-lag autocorrelation cells) and produced three original PCM16 mono 8 kHz recordings (1.2 seconds). Two native runs gave byte-identical JSON receipts. See witness.json. Each recording is a common, nonoverlapping integer tapered pulse convolved with a different length-27 coefficient train, with shared zero-padding and repetition. The 432-sample blocks were checked by literal aperiodic autocorrelation, and all 9,600 sample magnitudes were checked across full files. Common convolution with the repetition train preserves exact equality of the full finite-record spectra. This is an exact property of the digital samples, not a claim about loudspeaker output or human equivalence. Files are generated rather than committed; the witness receipt retains hashes and energies. The pulses are original, not borrowed audio. Neither implementation is independent peer review.

## Interpretation, contrary cases and design experiment

A spectral meter and an energy envelope meter are distinct witnesses, but their joint receipt may still be inadequate. Their agreement is not equivalent to agreement of everything a downstream transformation can do. A pair-intensity inspector can selectively expose an otherwise hidden semantic orientation; an inspector with the same nominal count of local and nonlocal probes need not have the same power or conditioning.

A useful MHAC experimental apparatus would present two channels: the entire shared magnitude receipt and a selectable interference measurement. The operator can move the pair endpoints or change its parity weight, specify whether the receiver has access to future samples, and simulate the noise radius. An honest report states which hidden factor orientations are identifiable, under what family assumption, with what margin. The synthetic laboratory implements the mathematical kernel, not a validated acoustic interface or a complete VST.

Negative sediment:
- Full joint magnitude does not uniformly identify our signals, but the generic complex-signal theorem of Beinert and Plonka remains intact. No claim about the size of the real exceptional set is established here.
- The exponential size is in m=log_3(N); the lower bound grows polynomially in waveform length. The full fibre at higher m is not enumerated.
- Equal raw pointwise energy and spectrum do not imply equal short-time Fourier magnitude or equal cochlear-channel envelopes. A time-varying window or filtering may reveal phase relations. The two auditory references provide reasons to avoid claims of perceptual sameness.
- Nonnegative amplitude-only encoders exclude these particular signed waveforms. Absolute polarity is a declared nuisance; a reference that fixes polarity can change the prefix result.
- Hamming optimality concerns fixed individually corruptible measurement receipts, not adversarial acoustic interference producing coordinated faults.
- The strongest nonlocal probe for a high-order parity is still numerically weak; exact code distance does not imply analog robustness. The intermediate weight-constrained coding problem and whole-fibre recovery are deliberately unresolved.

**Fiction, not evidence:** A clerk puts a waveform before two mirrors. The first reflects its energy at each instant, the second its energy at each frequency. Every image agrees with a different waveform on the other side of the glass. The apprentice moves one reflection until two samples meet. The mirrors were not lying; neither had ever been asked about that relationship.

## Checkpoint

Fresh branch mhac-502/waveform-both-mirrors, additive scoped files only. One AI research agent performed source reading, derivations, programming and same-agent computational cross-checks. No outside contact, real participants, human review or canonical registry advancement. Retain issue open and PR draft for critical review and exact-head repository qualification; local standalone checks are not full repository validation.
