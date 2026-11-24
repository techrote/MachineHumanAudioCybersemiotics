# The Pulse That Cancels Its Own Drift

Issue #288. Synthetic mathematical expedition, 2026-11-24. AI-assisted derivation, implementation, execution and self-review by ChatGPT (no external reviewer). Base: 495a98ca12bae467a507031f04931aa4254b1866. Homometry abandoned after discovering existing #199; no modifications to that work, shared records or frozen Track E/G. This is an independent mathematical toy, not a claim of priority or of human audio effectiveness.

## Question and prior art

Can two equal-duration, equal-amplitude bipolar pulse blocks, both exactly immune to polynomial nuisance drift of a specified degree, have dramatically different robustness to *nonpolynomial* drift? Can a compiler allocate the cost among polarity switches, cumulative imbalance and worst-case leakage?

Buhler, Golan, Pratt and Wagon, *Littlewood Polynomials, Spectral-Null Codes, and Equipowerful Partitions*, 2019 preprint, [arXiv:1912.03491](https://arxiv.org/abs/1912.03491), section 1, introductory paragraphs and length-eight example (rendered HTML read): establishes the equivalence of equal moments, a zero at one and a low-frequency spectral null. Freiman and Litsyn, 1999, IEEE TIT 45(6), 1798–1807, [DOI 10.1109/18.782100](https://doi.org/10.1109/18.782100), institutional abstract read only: studies asymptotic sizes of spectral-null word populations; no quantitative asymptotic formula imported here. Pezeshki, Calderbank, Moran and Howard, 2008, IEEE TIT 54(9), 4254–4266, [DOI 10.1109/TIT.2008.928292](https://doi.org/10.1109/TIT.2008.928292), Duke institutional abstract/metadata read only: application of Prouhet–Thue–Morse (PTM) scheduling to complementary waveforms. These are antecedents, not evidence for an auditory effect. Source access 2026-11-24; no complete-paper review or novelty search claimed. Derivations below are self-contained.

## Exact bounded-difference certificate

Let s[0..n-1] be a word in {-1,+1}, and r a positive integer less than n. Let S(z) = sum s[t] z^t. The word is order-r null (at least r) iff the power moments sum s[t] t^j vanish for j=0..r-1. This follows because the falling-factorial basis from derivatives at z=1 spans the same polynomials. Hence S(z)=(1-z)^r Q(z), where Q has n-r integer coefficients q[j], uniquely obtained by r prefix sums, discarding a zero endpoint at each stage. A nonzero endpoint is a refusal.

For any real nuisance sample vector x of length n, define the forward difference Δx[j]=x[j+1]-x[j]. Multiplying the polynomial identity coefficient by coefficient gives

    sum s[t] x[t] = (-1)^r sum q[j] Δ^r x[j].

If |Δ^r x[j]| <= ε independently, the absolute response is bounded by ε L, where L = sum |q[j]|. The bound is sharp: select Δ^r x[j]=(-1)^r ε sign(q[j]) and integrate r times, starting with zero at each integration. This constructs a length-n witness and realizes the bound exactly. There is no amplitude cap on x; adding one can invalidate sharpness. Any polynomial drift of degree below r is cancelled. This is finite-block, unnormalized response, not a claim about online causality or general stochastic noise. The normalized average response bound is ε L/n.

A separate prefix metric P=max_i |sum_{t<=i} s[t]| measures signed accumulation (not physical charge without a hardware model). C counts changes between consecutive signs, excluding external block boundaries.

## Arbitrary separation, and an exact second-order optimum

For n=4m, m>=1, compare these order-two words:

    A = (+ repeated m)(- repeated 2m)(+ repeated m)
    B = (+--+) repeated m

Write H_m(z)=1+z+...+z^(m-1). A(z)=H_m(z)(1-z^m)(1-z^(2m)); its quotient Q_A=H_m(z)^2 H_2m(z) has nonnegative coefficients and sum 2m^3. B(z)=(1-z)(1-z^2) sum_{i=0}^{m-1} z^(4i), so Q_B=(1+z) sum z^(4i), with L=2m. Both have exactly the same length, energy and order of zero. The shared drift x[t]=t(t-1)/2 achieves both sharp leakage bounds simultaneously. A has C=2, P=m; B has C=2m, P=1. Their sensitivity ratio is m^2.

These endpoints are globally optimal for the corresponding objectives. No one-switch word can null both moments: a balanced single switch puts the positive and negative samples in different contiguous halves, with different centroids. A two-switch word starting positive must have the middle negative run length 2m (DC balance), centered at the full interval midpoint (first moment), so it is exactly A. A sign inversion is the other case. For *any* bipolar order-two word, modulo two the second prefix coefficients equal binomial(j+2,2) modulo two, with repeating parity 1,1,0,0. Among the n-2 quotient coefficients there are 2m odd ones. Thus L>=2m. B attains that bound and the trivial P>=1. For n not divisible by four there are no order-two bipolar words: DC requires even n and the equal first moments require n(n-1)/2 even. These are sharp statements about the indicated finite model.

More generally let U_r(z)=product_{i=0}^{r-1}(1-z^(2^i)), the length-2^r PTM word. Its quotient has nonnegative coefficients, total 2^(r(r-1)/2), and first-prefix peak 1 (opposite signs in every consecutive pair). Compare a repeated PTM block (m repetitions) to a stretched PTM block (each symbol repeated m times). Their quotients are respectively Q_U(z) sum z^(2^r i) and H_m(z)^(r+1) Q_U(z^m). Both are nonnegative, giving the exact ratio m^r between stretched and repeated leakage, with peak m versus 1. These are explicit witnesses, not a general optimality theorem for r>2.

## Compiler and finite results

[drift.mjs](drift.mjs) enumerates all sign-normalized words (s[0]=+1) by exact matching of half-word power moments; global inversion accounts for the other half. Complete counts are normalized words, not inequivalent under reversal or cyclic shift. It evaluates C, P, L, keeps one witness per nondominated cost tuple and constructs an adversarial drift. A budget-exhausted result carries a partial frontier only, never an infeasibility/optimality assertion. The supported exact search domain is n<=32, r<=5 (integer JS arithmetic in safe range for these bounds); helpers are qualified only in the reported domains. The separate PTM family check is limited to orders 1..10.

[results.synthetic.txt](results.synthetic.txt) preserves all 19 completed census rows (19,565 normalized feasible words across rows; repeated words across orders not deduplicated), 67 nondominated witness checks, 20,418 direct moment/brute-force checks through n=12, and PTM identities. There is an explicit budget refusal test. Example n=16, r=2: C/P/L frontier (2,4,128), (4,2,32), (6,2,16), (8,1,8). At n=32, r=3, 17,444 normalized words and 15 nondominated cost tuples; minimum leakage 32, minimum switches 5, the latter witness leakage 2048. At n=24, r=4, the peak-one witness has L=264, while a peak-two witness has L=164. Thus peak-first optimization need not minimize leakage. At n=12, r=3, a feasible word exists even though 12 is not a multiple of 8; PTM repetition is not a complete existence characterization. No feasible words at (4,3), (8,4), (16,5) in this exhaustive finite census. No extrapolated minimum-length claim.

[verify_audio.py](verify_audio.py) is an independent Python implementation of direct sign enumeration, explicit binomial polynomial deconvolution, Pareto extraction, and two original audio renderings. All 12 overlapping census rows through n=16 match the JS counts and cost frontiers by comparison; 128 additional exact family checks through m=64 pass. All computed witnesses and source are synthetic. Python output reproduced byte-for-byte twice, with SHA-256 below.

Run from this directory:

    node verify.mjs > result.txt
    python verify_audio.py

Actual JS execution in a V8 isolate, not clean-checkout Node execution. Python executed locally (not full repository validation). No third-party runtime dependencies. Full repo integrity CI and independent review pending. No external participants, audio-effect claims, radar performance claims or device acceptance.

## Audio, exaptation and falsifiers

Two 1.6-second stereo PCM16 files at 16 kHz are generated locally into run/ by Python, not checked in as binary assets.

* bipolar-words.wav — equal carrier amplitude and per-cell envelope; sign selects 0/π phase, A left and B right. SHA-256 8b7e348926d0aed31892af0d8229d1516e6b9c5967c7fa92a6ae12d59abe3c1d.
* integral-debt.wav — quotient coefficients mapped to amplitudes on a common carrier scale, A left and B right; two zero tail cells. SHA-256 6286ed6fdef585691d8da94a2179438047932608a6e7747e480c46129dfa491b.
* verification.json — local machine-readable costs, witnesses and hashes; SHA-256 359a7bf07c293ed4be13c0ef9b3156b7593db03068d72bddda4825765ee80fcc.

The phase choice is an artistic encoding, not an asserted audible distinction. The second mapping is deliberately different; it does not establish human detection or an acoustic null in the finite WAV. Peak audio amplitude is bounded. No raw external audio used.

Potential transfers: signed probe codes that reject slowly changing additive baselines; balanced parameter modulation; drift-rejecting calibration stimuli; a sequencer where polarity-change budget and drift leakage can be separately negotiated. An arbitrary nonlinear nuisance, unknown time warping or amplitude-dependent disturbance is outside this certificate. Timing jitter breaks the exact moments. A low-order null does not imply immunity to unbounded higher derivatives. A non-null block has unbounded worst-case response to the unconstrained polynomial part of the nuisance class; a null block's finite bound is contingent on the stated finite-difference constraint. A single action or polarity error may destroy the null. No production hardware control or empirical evaluation performed.

Interpretive proposition (not a theory finding): a signal can reject an entire named class of backgrounds while remaining exquisitely sensitive to departures from that class. A certificate of cancellation must name both its nuisance family and the cost of leaving it.
