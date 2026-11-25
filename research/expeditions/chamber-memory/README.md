# The Chamber That Hides Its Memory

**Expedition #538 — 25 November 2026 — mathematical research, not selected evidence or empirical qualification.**

A passive chamber may be invisible to a surprisingly thorough boundary experiment. The question is not merely how many hidden states are present, but which directions excite them, which transfer functions distinguish them, and which information about their realization is permanently absent.

## 1. Boundary equivalence and hidden storage

Let n ideal pressure (or voltage) ports be connected by conductances g_i > 0 to a hidden chamber of compliance c > 0. Let g denote the column of conductances and G their sum. With port pressure u and hidden pressure z, use the ideal linear lumped model

    c dz/dt = g^T u - G z
    j = diag(g) u - g z.

Assume zero initial state. The boundary admittance is Y(s) = diag(g) - gg^T/(G+cs). At DC, it is exactly the admittance of a complete mesh of direct resistive links with conductances g_i g_j/G for i != j. This is the standard star/mesh instance of Kron reduction, not a new electrical-network theorem.

The dynamic difference from this memoryless mesh is

    Y(s) - Y(0) = (gg^T/G) s tau/(1+s tau),   tau=c/G.

Thus a boundary experiment with g^T u(t)=0 for all t cannot detect the hidden compliance at all. This is exact for arbitrary such time-dependent inputs, not just a DC equality. A common pressure drive does excite it. For a symmetric three-port example g=(1,1,1), the probe (1,-1,0) is blind, while (1,1,1) is informative. Repeating a blind experiment at more frequencies will not repair the choice of direction.

**Generalization.** Let the real symmetric conductance block matrix have boundary block D, cross block B and interior block L positive definite, with interior compliance matrix C positive definite and no boundary storage. Elimination gives Y(s)=D-B(L+sC)^(-1)B^T. Write A=C^(-1/2)L C^(-1/2), U=C^(-1/2)B^T. For any omega>0,

    Im Y(i omega) = U^T [omega (A^2+omega^2 I)^(-1)] U.

Here Im is entrywise imaginary part of the symmetric complex matrix. The bracket is positive definite, so the kernel is precisely ker B^T and the rank equals rank B. The same kernel holds for the dynamic difference from DC: if that difference annihilates a complex direction, its positive-semidefinite imaginary quadratic form vanishes, implying Uu=0; the converse is immediate. This exposes boundary-coupled directions at one nonzero frequency, not the number of internal states. The result assumes complete calibrated matrix access, positive compliance, and this strictly resistive/storage model; inductive effects, boundary storage or unknown gains may invalidate the inference.

**Permanent realization ambiguity.** Replace the one hidden chamber by any number of parallel chambers. For positive fractions alpha_l summing to one, give chamber l conductances alpha_l g and compliance alpha_l c. Its admittance contribution is alpha_l times the original contribution. The complete boundary admittance, including every entry at every frequency, is unchanged. Under common zero initial state their trajectories are identical; differential internal modes are unobservable. With arbitrary initial pressures only their weighted sum contributes to the boundary response, and it decays with the shared time constant. No number of boundary probes can count physical chambers in this family. Local inspection or an intervention that breaks the proportionality is necessary.

## 2. Sharp relaxation spectroscopy

Separate physical topology from the reduced transfer function. For a positive mixture with at most k **distinct** relaxation rates lambda_j > 0 and positive weights w_j summing to one, define

    H(s) = sum_j w_j lambda_j/(s+lambda_j).

This is the normalized hidden correction transfer, not the full admittance, for parallel stars with common boundary proportions: if the total branch vector is g and each chamber has fraction w_j of g and compliance w_j G/lambda_j, the correction to diag(g) is -(gg^T/G) H(s). It also describes a bank of first-order low-pass responses. DC normalization H(0)=1 is assumed known exactly. No direct feedthrough, unknown time delay or unrelated gain is permitted.

**Theorem A (complex probes).** Any k distinct positive angular frequencies, with exact complex H(i omega) observations, identify the entire reduced rate/weight profile. Any prescribed k-1 frequencies fail in the worst case.

Proof of sufficiency: a difference of two such rational functions has a numerator of degree at most 2k-1 over a denominator with at most 2k distinct negative poles. A zero at DC plus k complex conjugate pairs of zeros forces the numerator to vanish. Uniqueness of simple-pole partial fractions then recovers every distinct rate and weight.

Sharpness: choose 2k distinct positive rates l_1 < ... < l_(2k). Form the rational function

    R(s) = s product_j(s^2+omega_j^2) / product_i(s+l_i),

where j ranges over the k-1 prescribed probes. It is proper and has nonzero real residues. At s=-l_i the numerator is strictly negative and the denominator derivative has alternating sign. Thus the residues alternate; exactly k are positive and k negative. In the normalized basis l_i/(s+l_i), the coefficient is the residue divided by l_i. Their sum is R(0)=0. Divide their positive and negative parts by their common mass to obtain two normalized positive k-rate profiles. They coincide at every selected frequency and differ at every other positive frequency. This construction works for any prescribed frequencies and any 2k distinct positive rates, even within a prescribed open bounded interval. It is a fixed-probe worst-case statement, not an adaptive-query lower bound.

**Theorem B (magnitude-only probes).** Any 2k-1 distinct positive frequencies of exact magnitude (or squared magnitude) identify the same reduced profile. Any prescribed 2k-2 fail.

The key is a bijection between normalized positive k-rate transfer functions and normalized positive mixtures of squared-frequency Lorentzians with the same rate support:

    |H(i omega)|^2 = F(omega^2)
    F(x) = sum_j v_j lambda_j^2/(x+lambda_j^2)
    v_j = 2 w_j H(lambda_j) > 0.

To prove this, compare residues of H(s)H(-s) with F(-s^2) at s=-lambda_j. Both have the same residue, w_j lambda_j H(lambda_j), and symmetry supplies the other poles. Both vanish at infinity, so equality follows. Evaluating at zero gives sum v_j=1.

For the inverse, F has strictly negative derivative between poles on the real axis; each adjacent pole interval contains exactly one zero, by the signs at its two ends. These k-1 real negative zeros exhaust its numerator degree. Write the zeros as -zeta_j^2, with zeta interlacing the positive rates. The unique normalized stable factor is

    H(s) = product_j(1+s/zeta_j) / product_i(1+s/lambda_i).

Its residues at the negative poles are positive by interlacing: the numerator and the derivative of the denominator have the same alternating signs at consecutive poles. Therefore it is exactly a positive relaxation mixture. H(s)H(-s)=F(-s^2), and the stable selection and normalization exclude the alternative reflected zeros and global sign. This is a restricted minimum-phase spectral factorization; a general acoustic system with all-pass factors need not be identifiable from even its complete magnitude spectrum.

Sufficiency now follows by the rational numerator degree bound in x: 2k-1 positive roots plus zero force equality. For sharpness construct

    S(x) = x product_j(x-omega_j^2) / product_i(x+l_i^2),

with 2k-2 probes and 2k rates. Its numerator has constant negative sign at every negative pole (the number of factors besides x is even). The same alternating-residue argument produces two positive normalized Lorentzian mixtures with k rates each, then the proven inverse factorization turns them into distinct valid H profiles. They agree at the stipulated magnitude probes, and at no other positive frequency.

**Corollary (sharp symbol-error/erasure budgets).** For N distinct positive frequencies and an upper bound k on reduced order, the minimum Hamming distance between exact complex-receipt vectors is max(0,N-k+1); for magnitude vectors it is max(0,N-2k+2). Root counting provides the lower bounds; choosing any allowed number of collision frequencies and filling unused collision roots off the grid attains them. Correcting t arbitrary whole-receipt errors and e known erasures therefore requires and suffices, respectively,

    N_complex = k + 2t + e
    N_magnitude = 2k - 1 + 2t + e.

This is uniqueness of a valid explanation under the stipulated fault contract, not an efficient decoding algorithm. Independent component errors inside a complex pair and correlated errors are different channels. The proof also does not cover arbitrary analog noise.

## 3. Exact witnesses and numerical fragility

A two-rate complex collision uses these two profiles (rate, weight):

| A | B |
|---|---|
| (2, 15/32) | (1, 1/16) |
| (4, 17/32) | (3, 15/16) |

At omega=1 both yield 7/8 - 5i/16. At omega=2 they yield 211/320 - 143i/320 and 43/65 - 119i/260, respectively. One calibrated complex observation cannot distinguish them; a second can.

The magnitude collision in the machine receipt is expressed in the Lorentzian basis (squared rate, weight): A=(4,14/31),(16,17/31); B=(1,7/124),(9,117/124). The common squared magnitudes at omega=1 and 2 are 136/155 and 103/155. At omega=3 they differ: 4936/10075 and 74/155. These are exact squared magnitudes of physical-class positive transfer functions by Theorem B, not their original relaxation weights. For two rates, the inverse can be written explicitly: zeta^2=lambda_1^2 lambda_2^2/(v_1 lambda_1^2+v_2 lambda_2^2); use the factor above. In general the inverse zero locations can be algebraic rather than rational; the laboratory verifies the Lorentzian collisions exactly and the forward identity on rational profiles, not numerical root recovery of every inverse.

**Uniform near-collisions even with all frequencies.** Choose n=2k-1 and time constants tau_j=tau_0+jh, j=0,...,n. Assign even and odd j to separate profiles with binomial weights binom(n,j)/2^(n-1). The two normalized profiles have disjoint rate support and total variation distance one as probability measures. Their difference is

    H_A(s)-H_B(s) =
      n! (s h)^n / (2^(n-1) product_j(1+s tau_j)).

This identity follows by induction on n using successive forward differences of 1/(1+s tau), or by partial fractions. On the imaginary axis each of n factors has magnitude at least |omega| tau_0, and the remaining factor has magnitude at least one. Hence, uniformly in real omega,

    |H_A(i omega)-H_B(i omega)| <= n! (h/tau_0)^n / 2^(n-1).

The bound also holds at zero by continuity. Magnitude differences are at most the complex differences by the reverse triangle inequality. Fixed k, arbitrarily small h gives arbitrarily small observable differences while the discrete support distributions stay mutually singular. No uniform exact-support guarantee under positive measurement error follows from the sharp noiseless counts. This is not a bound on Wasserstein distance (the supports become geometrically close), nor a claim that every profile is poorly conditioned.

The permanent split ambiguity of section 1 is stronger than this near-collision: it is an exact topology failure even without measurement error, independent of the probe count. Count poles, not rooms.

## 4. Executed apparatus and proposed composition

Run from this directory:

    node laboratory.cjs
    python witness.py

The JavaScript laboratory uses reduced BigInt fractions, exact complex arithmetic and direct residues. It executed 1,716 assertions: 28 complex collision families, 28 squared-magnitude collision families, 400 forward spectral-factor comparisons, 216 finite-difference comparisons, 576 parallel-split entry checks and 64 balanced-drive checks. The native Python 3.13.5 witness independently solves linear interpolation constraints using rational Gaussian elimination (rather than residue evaluation): 18 complex and 18 magnitude collision profiles, 135 shared-receipt checks, 36 extra-probe checks, and 180 forward spectral identities. Native receipt reproduced byte-for-byte on two runs. Both implementations and their receipts are in this directory. Same-agent cross-checks, not independent review.

The native witness also generates four original mono PCM16 WAVs, with 16 kHz sample rate. The example two-rate profiles render a 250 Hz calibrated steady-state response, then a second composition includes a 500 Hz challenge response. The two 250 Hz files are byte-identical; the two two-slot files differ. Each slot lasts 0.5 seconds and has a common amplitude taper. These are direct analytic steady-state digital renderings, not a transient circuit simulation or a calibrated physical acoustic experiment; the taper is applied after the response is calculated. WAVs are generated locally rather than committed; their SHA-256 fingerprints are in the native witness receipt.

**Design hypothesis:** a listener or automated system could compare a memoryless patch, a hidden single relaxation, and a multi-relaxation patch under spatially balanced and common-mode challenges. An instrument could deliberately let a performer add hidden storage that no current probe excites; a second performer chooses the drive direction, a third chooses complex versus energy-only observation. Treat probe choice, not merely the sound, as compositional material. Evaluate correct discrimination of model classes, false topology claims and robustness under fixed noise; test the physical lumped approximation separately before participant work. No participant contact or result is claimed. The complete interactive instrument is not implemented.

**Fiction:** A clerk listens at every door of a chamber. The pressure ledger never changes when two doors are pushed in opposite directions. He makes the same measurement at a thousand pitches. The apprentice pushes both doors together. Later she discovers that the single chamber could be a row of smaller rooms, each breathing at the same rate. The ledger records a memory, not its architecture.

## 5. Sources, reconciliation and limits

- Florian Dörfler and Francesco Bullo, *Kron Reduction of Graphs with Applications to Electrical Networks*, IEEE Transactions on Circuits and Systems I 60(1), 150–163 (2013), [publisher DOI](https://doi.org/10.1109/TCSI.2012.2215780). Metadata checked against IEEE CASS. Read the author-hosted preprint [p. 1, Introduction, equations (1)–(2) and immediately following star-triangle discussion](https://motion.me.ucsb.edu/pdf/2011d-db.pdf) in extracted text and inspected page image. Only this passage is used for the established DC boundary-equivalence ancestry. The dynamic claims are derived here, not attributed to the authors. ArXiv PDF endpoint failed; author-hosted copy succeeded.
- COMSOL 6.3, [Lumped Loudspeaker Driver](https://doc.comsol.com/6.3/doc/com.comsol.help.models.aco.lumped_loudspeaker_driver/lumped_loudspeaker_driver.html), Introduction and Electroacoustic Analogy, Table 1. Read the actual documentation passage: pressure/volume velocity analogies and correspondence of resistance/compliance to circuit elements. This is technical documentation, not an empirical study of human listening. The example itself uses a distributed acoustic domain, so does not validate this particular ideal chamber model.
- *On the physical origin of the electro-mechano-acoustical analogy*, [DOI landing route](https://doi.org/10.1121/10.0009803). Search result exposed a potentially relevant passage on lumped validity; publisher full text inaccessible in this run, so no decisive claim uses it. Retain as discovery sediment only.

The rational interpolation, spectral-factor and error-distance arguments are self-contained. They have classical ancestry in rational interpolation, passive network synthesis and minimum-phase factorization; priority or literature novelty is not established by this bounded search. The project-level contribution is the particular combination of sharp receipt budgets, directional blindness, realization ambiguity and uniform near-collisions in a concrete semiotic apparatus.

Reconciled live main at 495a98ca12bae467a507031f04931aa4254b1866; read AGENTS, RAG, programme, runbook, integrity, validation and README. Inspected 100 recent open issue entries, 100 recent open PR entries, 329 branch entries across pages (live search is not atomic), and targeted searches for Kron, Dirichlet, star-delta, electrical network, Schur complement and effective resistance (no issue matches). A previous idea on variable-length codes was abandoned after finding #224. Existing cospectral graph work concerns a different observation model. Prior expedition #531 exact recorded head ede894814753cbbeb815047d771674d14c24f941 had a successful Actions run 45589102615. New issue #538 has no comments at intake. Only additive expedition paths are touched; no canonical records or active worker branches modified.

Verification actor: ChatGPT/GPT-6.2, 2026-11-25; same-agent proof review, exact JS calculations and native Python cross-check. Native Git checkout unavailable (DNS could not resolve github.com), so full repo test suite not run locally. Repo CI and independent critique remain to be checked before any landing. No inference about Brier's endorsement, perceptual equivalence, clinical benefit or real-device accuracy is supported by these calculations. Keep this exploratory dossier distinct from the frozen empirical programme.
