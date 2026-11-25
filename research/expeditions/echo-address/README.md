# The Echo That Learns Its Address

**Refs #570 · 2026-11-25.** Additive synthetic/formal expedition. Not Track E/G evidence, an accepted design requirement, or a human listening experiment. No claim of mathematical priority.

## Contents

1. [The indistinguishable echo](#1-the-indistinguishable-echo) — recover a source and room by changing only the source.
2. [An exact address theorem](#2-an-exact-address-theorem) — necessary and sufficient mask separation, constructive inversion.
3. [The fault-distance theorem](#3-the-fault-distance-theorem) — codewords of positions, not of messages.
4. [Amplitude precision and packing](#4-amplitude-precision-and-packing) — an exact onset-only noise budget.
5. [Negative sediment](#5-negative-sediment) — shared roots, uncalibrated gain, crops and weak coefficients.
6. [Executed laboratory and sound witnesses](#6-executed-laboratory-and-sound-witnesses) — bounded census, exact arithmetic and reproducibility.
7. [Exaptation and source ledger](#7-exaptation-and-source-ledger) — related methods, proposed instrument and claim boundaries.
8. [Checkpoint and fictional coda](#8-checkpoint-and-fictional-coda) — repository state and a deliberately invented ending.

## 1. The indistinguishable echo

The earlier [issue #300](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/300) and [PR #301](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/301) construct many positive common filters that cannot be distinguished by complete outputs of unrelated unknown inputs, even with partial calibration. That result admits a full known training impulse as a repair. Here the original waveform is still unknown; instead, we repeat it with a controlled transformation.

Consider two candidate histories:

| History | source x | channel h | output y |
|---|---|---|---|
| A | 1,2,1 | 1,1 | 1,3,3,1 |
| B | 1,1 | 1,2,1 | 1,3,3,1 |

The original observations coincide exactly by commutativity of linear convolution. Change only the source, multiplying its successive coefficients by 1, 1/2, 1/4 (not the output, and not the channel). The two new observations are:

| History | masked output |
|---|---|
| A | 1,2,5/4,1/4 |
| B | 1,5/2,2,1/2 |

These differ. What is the most general condition making this distinction possible for every finite waveform, even with an unknown division of the total delay between source and channel?

This is a controlled-repeat experiment, not an assumption that an observer can reconstruct two uncontrolled performances. Source-side multiplication is a known operation; the mask can be applied without knowing the coefficients, but its timing and gain are part of the apparatus contract.

## 2. An exact address theorem

**Model.** All coefficients are real, and all sequences are finite, causal and nonzero. Write X(z)=sum x_i z^i for an unknown source supported in indices 0,...,N-1 (including possible leading zeros), and H(z) for an arbitrary finite unknown channel, with no restriction on its onset. The ordinary unmasked output is Y=XH. In probe l, the source is multiplied coefficientwise by the known positive mask d_l, then passed through the unchanged channel. Denote its polynomial D_l X and output Y_l=H D_l X. All records are complete, noise-free, aligned to the same absolute sample index and share calibrated gain. The mask applies in the source time reference, not the receiver arrival time.

The unavoidable overall scalar symmetry is (X,H) -> (aX,H/a), a nonzero real. We remove it by making the first nonzero source coefficient equal to 1. No absolute source/channel amplitude identification is claimed.

Define the signature of source index i to be the vector

    c(i) = (d_1[i], ..., d_q[i]).

**Theorem 1 (exact universal injectivity).** For N>=2, the baseline plus q probes identifies every source/channel pair modulo that scalar symmetry if and only if c(0),...,c(N-1) are pairwise distinct. N=1 needs no supplementary probe. The filter class for the necessity result must allow the required delay of up to N-1; our arbitrary finite class does.

**Proof, sufficiency and constructive decoder.** Let ell be the first nonzero coefficient index of Y. For nonzero finite polynomials the onset of a product is the sum of onsets. Let p be the source onset; then ell-p is the channel onset. The leading-coefficient ratios Y_l[ell]/Y[ell] are exactly c(p), regardless of source and channel amplitude. They identify p.

Set X=z^p F, H=z^(ell-p) G, with F(0)=1. Strip the common delay from the baseline to obtain U=FG. Strip the same delay from Y_l to obtain V_l=G M_l F, where M_l multiplies coefficient k of F by d_l[p+k]. The quotient R_l=V_l/U exists as a formal power series since U(0) is nonzero. It satisfies

    R_l F = M_l F,
    R_l[0] = d_l[p],
    (d_l[p+k] - d_l[p]) F[k]
        = sum_{j=0}^{k-1} F[j] R_l[k-j].

For each k=1,...,N-1-p, choose any row l separating indices p and p+k. The right side involves only previously recovered coefficients. Pairwise distinct signatures guarantee such a row. This recursively determines F exactly. Formal division U/F determines G; because the data come from a finite product, the quotient terminates. A decoder should verify full reassembly for every supplied record rather than silently accepting arbitrary incompatible data. The laboratory does so.

Necessity: if c(i)=c(j), i<j, compare histories (X=z^i,H=z^(j-i)) and (X=z^j,H=1). Their baseline is z^j and every masked record is c_l(i) z^j=c_l(j) z^j. They are not scalar-equivalent. Even nonnegative unit-gain histories suffice for this counterexample.

**Corollary 1 (known onset).** If p is known, only separation of c(p) from every later c(j) is required; mutual separation among later positions is unnecessary. The above recurrence proves sufficiency. Necessity follows with histories X=z^p(1+z^(j-p))/2, H=1 and X=z^p,H=(1+z^(j-p))/2, both with known onset p and equal DC gain. When the two signatures coincide, all outputs coincide. Thus one two-level positive mask is enough if onset is known. This is not the same problem as unknown delay ownership.

**Corollary 2 (finite mask alphabet).** With b>=2 calibrated levels, the exact minimum number of supplementary records for arbitrary unknown onset is ceil(log_b N). Necessity counts distinct column signatures. Sufficiency writes every index in base b and uses its digits as the respective mask levels. For N=1, zero probes suffice. The baseline is additional and reliable throughout.

## 3. The fault-distance theorem

One independently corruptible symbol is an entire supplementary waveform record, not one PCM sample. The baseline remains exact. For a fixed mask family define

    D = min_{i<j} Hamming(c(i),c(j)).

**Theorem 2.** Among all distinct scalar-normalized histories sharing a baseline, the minimum possible number of differing supplementary records, minimized also over feasible baselines, is exactly D.

For histories with different source onsets p,p', the leading ratios prove at least Hamming(c(p),c(p')) differing rows. If p is the same, their normalized F polynomials differ unless the histories coincide; the channel is already determined by F and the baseline. Let k>0 be the first coefficient at which F and F' differ. For each row l the first k-1 coefficients of R_l agree by formal series division. Subtracting the coefficient-k recurrence gives

    R_l[k] - R'_l[k]
      = (d_l[p+k]-d_l[p]) (F[k]-F'[k]).

Thus each row separating p and p+k necessarily differs, yielding at least D differing records. The baseline is common and nonzero, so multiplication by U cannot erase a nonzero formal-series difference. Equality is attained by the pure-delay pair from Theorem 1 for indices attaining D. This is a universal worst case, not a claim that each particular baseline has distance exactly D.

Consequently, correction of t arbitrary whole-record substitutions and e flagged erasures is guaranteed precisely when D>=2t+e+1. After removing e coordinates, two distinct candidates cannot both lie within distance t if their surviving distance exceeds 2t. Conversely, erase up to e of a closest pair's differing records and split the remaining disagreements between the two candidates; both are within the permitted error budget. The lower bound is achieved by physically admissible synthetic pure-delay histories.

The standard-library decoder enumerates subsets of nonerased rows of size (number available minus t). On at least one all-clean subset, the remaining signatures still separate all positions, since at most t+e rows were dropped. It recovers a candidate and checks all nonerased observations, accepting only a unique candidate within the error budget. It is intentionally a small exact oracle, not a claim of efficient decoding for large q.

### A closed-form binary frontier

For N=2, the minimum q equals d=2t+e+1, by repeating one separating mask.

For N=3 or N=4, the exact optimum is

    q_min = ceil(3d/2).

Proof: for three binary codewords each coordinate contributes at most two to the sum of all three pair distances; for four codewords it contributes at most four to the sum of six pair distances (partition sizes 2 and 2). In either case q>=ceil(3d/2). The four binary words 000,011,101,110 have mutual distance two. Repeat this length-three block floor(d/2) times. For odd d append the two-bit words 00,01,10,11, of minimum distance one. Retain any three words if N=3. This attains the bound for every d>=1. It is a simple coding-theoretic construction, not a new coding bound claimed against the literature.

| Onset positions | No faults | One erasure | One error | One error + one erasure |
|---|---:|---:|---:|---:|
| 2 | 1 | 2 | 3 | 4 |
| 3 or 4 | 2 | 3 | 5 | 6 |

These are counts of supplementary full-length recordings, not transmitted bits or seconds of sound. The number of source coefficients to recover can be far greater than the number of probe recordings because every recording has multiple sample values.

## 4. Amplitude precision and packing

Let all mask entries lie in the fixed positive interval [a,b], a<b. There are q real-valued probe rows and N>=2 possible source indices. Define minimum signature separation in the max norm as Delta = min_{i<j} max_l |d_l[i]-d_l[j]|.

**Theorem 3.** For q>=1, the sharp largest achievable Delta is

    Delta* = (b-a)/(ceil(N^(1/q))-1).

Put L=ceil(N^(1/q)), so (L-1)^q<N<=L^q. A regular L-level grid of the q-dimensional cube has L^q points and separation at least (b-a)/(L-1); choose any N. Conversely partition the cube into (L-1)^q half-open subcubes, with the last boundary included, of side (b-a)/(L-1). Two of N points occupy one cell and their max-norm distance is no greater than that side. This proves the exact packing bound. For q=1 a uniformly spaced ramp is optimal. When q>=ceil(log_2 N), the endpoint alphabet suffices for the full dynamic-range separation.

**Corollary (onset-only bounded analog error).** Assume the baseline and its nonzero leading value B=Y[ell] are exact. Observe the leading coefficient of each supplementary output with independent, arbitrarily signed errors of magnitude at most eps. An onset is determined by a unique signature whose leading predicted values B*c(i) are within eps of the data. A universal guarantee over possible onsets at this amplitude holds if eps < |B| Delta/2. Conversely at equality, choose the closest signature pair, use the two pure-delay histories with the same B, and return the midpoint of their records. Every measured coefficient is consistent with both worlds; even the remaining complete output samples do not help in this witness.

For [a,b]=[1/2,1], N=16, q=1 the best separation is 1/30 and eps must be below |B|/60. With four binary-level probes, separation 1/2 is attainable and the threshold becomes |B|/4. The onset-only tolerance improves by a factor of fifteen. This does NOT establish a uniform error bound for recovery of all later coefficients or for a noisy baseline.

An additional useful lower bound for exact support recovery: X=1+eta*z and H=1 versus X=1 and H=1+eta*z have the same baseline. Every masked output differs only at the second coefficient by eta*(d_l[1]-d_l[0]). For any positive uniform analog error and bounded mask contrast, eta>0 can be chosen small enough to hide the presence or absence of that source coefficient even with arbitrarily many masks. Full support identification is not uniformly stable. A realistic model needs amplitude floors, noise and conditioning assumptions; more recordings alone do not prove them.

## 5. Negative sediment

**The GCD shortcut can fail even when the controlled repeat succeeds.** Take X=(1+z)(1+2z), H=1+3z, and d_i=2^i/4 on the three source positions. Then D X=X(2z)/4=(1+2z)(1+4z)/4. The ordinary GCD of the two outputs includes H*(1+2z), strictly more than the channel. Yet all three mask entries are distinct; Theorem 1 identifies X and H. Coprime residuals are not required by this stronger linked-input contract. This is the key distinction from #300 and ordinary blind multichannel identification. For a general geometric mask with positive ratio other than one, the recurrence is a first-order q-difference relation X(qz)/X(z); it is not an invented new branch of difference equations.

**Unknown independent trial gain destroys onset ownership.** For two pure-delay histories X=z^i,H=z^(j-i) and X=z^j,H=1, the modulated waveforms are scalar multiples. If each probe is permitted its own unknown positive gain, every pair is observationally equivalent after adjusting these gains, regardless of how many strictly positive masks are available. Per-record peak normalization also erases this distinction. A shared known relative gain, clock and placement of the mask are part of the evidence, not mere display settings. Known onset can simplify the unknown-gain problem, but we have not proved a general noisy recovery method.

**A cropped record is not the polynomial.** X=1+z,H=1 and X=1,H=1+z produce the same unmasked record. The mask (1/2,1) distinguishes their second samples; cropping both records to their first sample defeats the experiment. Full linear convolution cannot be replaced silently by circular convolution, truncation or magnitude-only data. The report makes no theorem for those observation models.

**Stability, repeatability and instrumentation are separate.** A controlled replay must actually preserve the latent source before the mask and the filter across trials. Unknown re-synthesis, physical feedback, clipping, drift, arbitrary unknown phase and mask misalignment can invalidate the model. Multiplying the already recorded signal at the receiver is not the intervention: the product would not separate histories that have identical recordings. We have not established that an unknown real acoustic source permits this operation without disturbing its state.

## 6. Executed laboratory and sound witnesses

The [laboratory](laboratory.py) is standard-library Python, with exact fractions, literal convolution, a formal-series quotient decoder and a separate exhaustive pairwise-output-distance oracle. Run in a writable copy of this directory:

    python laboratory.py > rerun.json

It renders four original WAV files alongside its source and prints a deterministic structured receipt. Compare with [execution.json](execution.json). Files are generated, not externally sourced. The native execution used Python 3.13.5, twice after the final source edit; both receipts were byte-identical.

| Check | Count |
|---|---:|
| Distinct normalized histories from length<=3 sequences over {0,1,2}, excluding zero | 627 |
| Distinct complete baseline fibres | 302 |
| Unordered distinct-history pairs sharing a baseline | 395 |
| All subsets of the eight two-level masks at N=3 | 256 |
| Exact distance predictions compared with literal records | 256 |
| Ramp reconstructions over the exhaustive nonnegative census | 627 |
| Seeded signed histories recovered | 193 |
| Six-mask one-error/one-erasure decoder trials | 1,200 |

The complete dictionary distance histogram was: 40 dictionaries of distance 0, 96 of distance 1, 92 of distance 2, 24 of distance 3, 4 of distance 4. These are combinatorial counts, not device failure rates. The 1,200 decodes comprise 40 seeded nonzero signed histories and all 30 distinct positions of one substitution and one erasure. The injected erroneous record is an obvious numerical outlier; do not claim an exhaustive census of arbitrary corruption values. A separate distance-two counterexample combines plausible records of two pure-delay histories; the decoder refuses the ambiguous hybrid. The proof, not the finite census, establishes the arbitrary-value fault guarantee.

The negative gain-normalization and cropping cases and noncoprime geometric-mask example are also explicitly tested. This single agent authored the proof and laboratory; the direct-pair oracle and triangular decoder are different computational routes, not independent scientific review. The source and execution receipt Git blobs match the locally executed files. No full repository checkout: native git ls-remote failed because github.com could not be resolved; connected repository API remained functional. No full local repository suite or absent CI success is claimed.

**Original sonification.** A common bipolar pulse basis is placed at 100 ms coefficient intervals, 8 kHz mono PCM16, fixed gain, 0.5 s per file. The raw A and B WAVs are byte-identical; the masked A and B files differ, as checked directly. The exact vector values and SHA-256 digests are in the receipt. These WAVs are coefficient sonifications, not impulse responses measured in a room. They are regenerated by the laboratory rather than committed as binary files. No loudness or listening-test result is claimed.

## 7. Exaptation and source ledger

**Interpretation.** A repeated utterance can be more than additional exposure: a precisely controlled change at one point in a causal chain can discriminate explanations that passive observations cannot. The operative information is the relationship between the original and changed input. A record of the modulation's position in the chain is therefore evidentially material. If one applies the same apparent mask downstream instead, its effect cannot establish source/channel ownership. The delayed source can acquire an address only from a clock that acts before the channel.

**Hypothesis for MHAC.** A source-aware echo calibration instrument could offer two independent tracks: a repeatable latent pulse score and a bank of calibrated masks. It could display the inferred source, channel, onset ambiguity, minimum mask-code distance, and explicit reassembly residual. One performer changes the attribution of a fixed observed echo; a second applies a source-side mask to reveal the change. An observer who receives only the final sound without the mask receipt cannot necessarily establish why it changed. This is a compositional analogy and prototype suggestion, not a validated acoustic interface requirement. Reject the proposed mechanism if controlled replay and source timing cannot be established, or if measured noise overwhelms the distinguishing signature; compare with a conventional known-pilot calibration when possible.

There is no demonstrated explanatory gain from Brier's cybersemiotics in this algebraic model. Standard inverse-problem reasoning, pointwise modulation, formal series and code distance suffice. Any further semiotic interpretation must not be presented as a consequence of the theorems.

**Read sources (2026-11-25, AI-assisted, selected passages only):**

- Lang Tong and Sylvie Perreau (1998), *Multichannel Blind Identification: From Subspace to Maximum Likelihood Methods*, Proceedings of the IEEE 86(10), pp.1951–1968, [author-hosted PDF](https://people.ece.cornell.edu/ltong/papers/TongPerreau.pdf), §II-B.1, printed p.1954, PDF index 3, eqs.12–14; text and original page image inspected. Established comparator: a common polynomial factor can move between unknown input and channels without changing observations unless further conditions hold. Their ordinary model does not impose the exact linked-source masks used here.
- Ali Ahmed (2018), *Blind Deconvolution using Modulated Inputs*, [arXiv:1811.08453](https://arxiv.org/abs/1811.08453), abstract and §I, eqs.1–3 and surrounding assumptions, full-text HTML extraction inspected. Their known pointwise random modulations and shared filter apply to circular convolution with multiple unknown subspace inputs; this is substantial method ancestry. Our exact repeated-source, complete-linear-output and unknown-onset assumptions are different. No performance comparison or priority claim.
- J. Cano and P. Fortuny Ayuso (2022), *Power Series Solutions of Non-linear q-Difference Equations and the Newton–Puiseux Polygon*, [publisher HTML](https://doi.org/10.1007/s12346-022-00656-0), §1 and §2 introductory automorphism definition, eq.1. Their general formal q-shift machinery provides mathematical context for the geometric-mask special case. The finite polynomial recurrence here is self-contained and not an application of their nonlinear existence results.
- C. A. Lin and J. Y. Wu (2002), *Blind identification with periodic modulation: A time-domain approach*, IEEE Transactions on Signal Processing 50(11), 2875–2888, [institutional record](https://ir.lib.nycu.edu.tw/handle/11536/28403), abstract and metadata only. Their periodic modulation/second-order statistical approach is a related established research direction; no full-text theorem attributed.

No restricted full text copied. Sources above are related-method context, not human evidence for MHAC, and the finite derivations are not asserted to be novel in the mathematical literature. The predecessor #300 was read in full at PR #301 head 9179dc435e7de9813cce10e385b930e6118f519a; its theorem is not treated as externally validated. We initially considered unrestricted blind common-factor separation, then abandoned that as duplicate scope after discovering #300. The controlled-repeat problem is the distinct successor.

## 8. Checkpoint and fictional coda

Observed main 495a98ca12bae467a507031f04931aa4254b1866; read AGENTS, RAG, programme, runbook, research integrity, validation and project foundations. No nested AGENTS at research/ or research/expeditions/ found. Reconciled 100 recently updated open issues, 100 open PR results, 345 branches through pagination, targeted searches for convolution, modulation, coprimeness, destructive probes and prior echo work. Previous expedition PR #563 exact-head workflow completed successfully. #570 created with zero comments, fresh branch mhac-570/echo-address. Only this directory added. No canonical manifests, frozen research records, shared implementation or other worker's branch changed.

ChatGPT GPT-6.2 performed source reading, formal derivation, native Python implementation, execution, same-agent review and publication. No independent critique, human validation or production device testing. Draft PR references #570 rather than closing it. Full exact-head CI and independent mathematical scrutiny remain acceptance items; the synthetic experiments are complete within their declared scope. No human action requested.

*Fiction:* A clerk hears the same echo from two chambers. In one account the long sound belongs to the voice; in another it belongs to the walls. He asks for another performance, but this time the speaker must turn down its first syllable before the sound leaves the mouth. The walls do not follow that instruction. The clerk can finally assign the delay. He writes the location of the instruction in the ledger, next to the sound.
