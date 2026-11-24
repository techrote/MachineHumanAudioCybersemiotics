# The Chord That Manufactures Its Own Witness

Refs #296 · 24 November 2026 · isolated formal/synthetic/artistic expedition. Not a Track E/G finding, real receiver qualification, or human perceptual result.

## Model and false activation

Let z(t)=sum_j a_j exp(i f_j t), with distinct integer frequency bins f_j, arbitrary complex amplitudes a_j (including zero), and an ideal memoryless analytic-baseband channel y=z+gamma z|z|^2. All Fourier projections are exact over a common period; there is no sample aliasing, finite-window leakage, channel memory or phase drift. The cubic coefficient at allocated bin f_l is

    C_l = sum_{f_i+f_j=f_k+f_l} a_i a_j conjugate(a_k).

The trivial terms (i=k or j=k) contribute precisely a_l(2 sum_j |a_j|^2 - |a_l|^2). They survive all phase cycling below; the goal is not to linearize the whole channel. Let R_l count ordered nontrivial triples and F_l count those additionally satisfying k != l. No nontrivial triple can have i=l or j=l, because this would force j=k or i=k. Thus with the target muted, exactly F_l triples remain. With all other magnitudes bounded by A, the sharp worst-case false coefficient magnitude is |gamma| A^3 F_l, by the triangle inequality and attainment when all other amplitudes are +A. For a fully occupied grid the sharp residual after subtracting diagonal terms is |gamma| A^3 R_l. These maxima are attained simultaneously, not merely separately. They are worst cases over the defined complex amplitude domain, not real-world error probabilities.

## The static no-false-tone criterion

A grid has no false activations for every choice of inactive target and other amplitudes iff it is a Sidon set (all unordered pair sums, including repeated summands, distinct). If pair sums are distinct there are only trivial terms. Conversely, a nontrivial equality between unordered pairs has disjoint supports (otherwise cancel the common member). The pairs cannot both be doubles. Choose a target in a distinct-element pair, use the opposite pair as the positive factors and the other member of the target pair as conjugate factor. This yields a nontrivial triple with every source different from the target, and all-positive active coefficients attain positive F_l. Equivalently all positive pairwise differences must be distinct: a repeated positive difference rearranges to a nontrivial equal sum and vice versa. Therefore span B >= n(n-1)/2, a simple counting lower bound, not generally sharp.

Avoiding three-term arithmetic progressions only removes collisions involving doubled summands. The four marks 0,1,4,5 contain no 3-term AP, but 0+5=1+4 and each of their four targets has F_l=2. Example: mute 0 and activate 1,4,5; 1+4-5=0. The marks 0,1,4,6 are Sidon, so have no cubic false activation. Fifth-order falsifier: mute 6 and activate 0,1,4 with unit amplitudes, then 4+4+0-1-1=6. Direct convolution gives fifth-order coefficient 6. A cubic guarantee is not an arbitrary-nonlinearity guarantee.

## Phase-cycle compiler: spend time instead of bandwidth

In r binary phase dimensions choose a label L_j in GF(2)^r per allocated carrier. Use all 2^r frames t in GF(2)^r, transmit a_j times (-1)^(L_j dot t), project at each allocated bin and multiply by that bin's known sign before averaging. Complex conjugation leaves signs unchanged. The sign of a cubic term after demodulation is the character of L_i xor L_j xor L_k xor L_l. Averaging is exactly zero for a nonzero label XOR, one for zero. Therefore the necessary and sufficient condition for cancelling each nontrivial cubic monomial is

    L_i xor L_j != L_k xor L_l
    whenever f_i+f_j=f_k+f_l and unordered pairs differ.

Necessity for the whole arbitrary-complex-amplitude polynomial follows from independent monomials in amplitudes and conjugates (the i/j swap only doubles coefficients). In particular for each equal-sum class the pair XOR labels must be injective. The search stores odd-multiplicity support masks; supports have size 2 or 4, never zero. Translating every label by one constant leaves all constraints invariant, so fix L_0=0. Try successive bit counts, prune only fully assigned violated constraints. First solution after exhaustive lower-bit searches is optimal in the full Walsh-group design family. Budget exhaustion is not an impossibility result.

This trades occupied bandwidth for coherent repeated observations. The amplitudes must be constant across frames, the receiver must know and synchronize the signs (including the sign of a muted channel), and projections must have a consistent phase reference. Averaging complex coefficients, not their magnitudes, is essential. Channel memory, drift, changing symbols, extra interferers and higher nonlinear orders are outside the guarantee. A frame is a mathematical observation, not a specified real-time latency.

## Beyond Walsh: arbitrary equally weighted sign schedules

Allow any finite multiset of binary sign vectors, with equal positive frame weights; the same demodulation rule applies. For every nontrivial support mask m, require the average parity character to be zero. For the contiguous grid of at least five marks, masks 5,10,17 (bit j denotes carrier j) are independent; all seven nonzero XOR combinations occur among collision masks. Explicitly these are 5,10,15,17,20,27,30. Consequently the joint distribution of the three parity bits is uniform by finite Fourier inversion (all seven nonconstant characters vanish). Frame count must be divisible by eight. For n=4 masks 5,10,15 similarly force divisibility by four; n=3 mask 5 forces even count. These are necessary for *any* equally weighted sign schedule, not only Walsh designs.

For exactly eight frames, each of the eight three-bit values occurs once. Reorder frames into that canonical order. Global flip of each frame leaves all even-support characters unchanged, hence column 0 can be zero. A constant flip of a column only changes signs of character means and preserves zeros; normalize all columns to zero in the first frame. Represent columns by 8-bit truth tables: x2=0xaa, x1 xor x3=0xcc, x4=0xf0. All other columns are arbitrary even integers 0..254 (low bit zero), not restricted to linear functions. The exact search in frame_exact.py checks each constraint as soon as its final column is assigned; each character must have popcount 4. It covers every normalized eight-frame possibility. Results: n=5,6,7,8 feasible (4,35,87,312 visited assignments respectively); n=9 and n=10 infeasible (131584 visited assignments each). Infeasibility at n=9 also follows for any larger consecutive grid by restriction to its first nine columns. With the verified 16-frame Walsh witnesses for n=9,10, this proves the table's minima for arbitrary equally weighted sign schedules.

| consecutive carriers | minimum frames | Walsh labels (one witness) |
|---:|---:|---|
| 2 | 1 | 0,0 |
| 3 | 2 | 0,0,1 |
| 4 | 4 | 0,0,1,2 |
| 5 | 8 | 0,0,1,2,4 |
| 6 | 8 | 0,0,1,2,4,1 |
| 7 | 8 | 0,0,1,2,4,1,3 |
| 8 | 8 | 0,0,1,2,4,1,3,7 |
| 9 | 16 | 0,0,1,2,4,1,3,7,8 |
| 10 | 16 | 0,0,1,2,4,1,3,7,8,15 |

Unequal frame weights, continuous phases, adaptive measurement or different receiver estimators are not covered. This result concerns exact cancellation of all specified nontrivial monomials for arbitrary stationary amplitudes, not the minimum number of measurements for identifying a particular unknown signal.

## Exact census and reusable artifacts

Fixed endpoints 0 and B, n=3..6, B=n-1..20. Enumerate every unordered grid with these endpoints, counting reflections separately when distinct. 70 (n,B) configurations, 21679 grids, 2322 Sidon grids, 6962 AP-free grids, including 4640 AP-free but cubic-unsafe grids. Every reported frontier is exact for the finite population, minimizing peak silent-channel collision count and total occupied residual count. In this census both objectives have a common minimizer in every row (no multi-point frontier); no claim of general equivalence. For six tones the minimum peak at spans 5,6,8,10,12,14,16,17 is 12,8,5,4,2,1,1,0. At span 17 there are eight Sidon grids out of 1820; none at smaller spans in this search. The zero-collision span is the familiar Golomb-ruler problem, not a new record. Planner supports required and allowed bins, returns partial observations if search budget exhausted. Core supports at most 32 distinct bounded integer bins. It does not enforce physical bandwidth, Nyquist, analog distortion coefficients or regulatory requirements.

- chord.mjs: exact witnesses, bounded grid planner, Walsh compiler.
- results.synthetic.txt: complete finite census and Walsh search receipts.
- verify.mjs: independent ordered pair convolution and explicit mute tests across all 21679 grids, recomputed AP and difference checks, all 70 Pareto fronts, independent pair-sum checks for 9 phase plans, 9837 ternary amplitude-word cycle checks, direct lower-bit brute force for n<=5, malformed-input and budget controls. Executed fetched-back functions in V8; receipt byte-identical; Node import/CLI path still to be qualified in clean checkout.
- check_audio.py: independent Python convolution census and 9837 ternary checks, fifth-order falsifier and original stereo PCM16 audio render. Python 3.13.5 local execution twice, identical output hashes. Source blob e842d3a6deb6c607766aadf552bea72b8f5f9eb9 matches local file.
- frame_exact.py: independent arbitrary equal-weight eight-frame exact search, Python 3.13.5 executed; source blob 6041469a67f53d093de52aee47fffb5536baccb4; stdout SHA256 0b3a67a0cf119e34dfd48e0d6d971f118a7db38ba1a6f2e829daea02dacba4da.

Reproduction from this directory: node verify.mjs; python check_audio.py; python frame_exact.py. No dependencies outside standard runtimes. Python outputs run/verification.json and two WAVs. Local verification JSON SHA256 3a1aa8f233391ac607c5125aba1700022e830af2086a1efe72ac350c6041255f. Audio:
- manufactured-carrier.wav, SHA256 fd17a6e706225ad986d9a69620dd916c751d38727abeec47b55d4e6475a32ffd: raw cubic coefficient 2 versus corrected 0.
- genuine-carrier.wav, SHA256 9fe564eb101deb7735be40f170647af392a5036fbf19da7f64fe4fcd2766808f: raw 9 versus corrected 7 (diagonal retained).
Both are 2-second, 16 kHz stereo, common gain per file, 400 Hz cosine sonifications of the projected coefficients, not actual hardware recordings or a listening trial. The original grid can be mapped to 400,480,720,800 Hz; signs control an analytic mathematical model. Rendering envelope is artistic, not part of the projection proof.

## Provenance and exaptation

Historical overlap: W.C. Babcock (1953), Intermodulation Interference in Radio Systems: Frequency of Occurrence and Control by Channel Selection, Bell System Technical Journal 32(1), 63–73, https://doi.org/10.1002/j.1538-7305.1953.tb01422.x . Read publisher abstract and Bell Labs archive abstract (https://www.nokia.com/bell-labs/publications-and-media/publications/intermodulation-interference-in-radio-systems-frequency-of-occurrence-and-control-by-channel-selection/) on 24 November 2026. Established frequency selection to mitigate third- and fifth-order products; no historical priority claim. Kevin O'Bryant (2024), On the size of finite Sidon sets, https://doi.org/10.3842/umzh.v76i8.7858 , journal abstract https://umj.imath.kiev.ua/index.php/umj/article/view/7858 read same date, gives definition and stronger asymptotic diameter bounds. Only abstract-level reading, not a systematic literature review. Derivations above self-contained; phase cycling and character orthogonality are established tools, no claim of mathematical novelty or exhaustive prior art. AI-authored formal construction and computational artifacts, no independent human review.

Possible transfers: dense multitone control in a calibrated analytic DSP path; a modular synth whose phase cycle suppresses or deliberately exposes phantom partials; exact frequency-assignment fixtures; comparison of temporal repetition against spectral separation; diagnostics that identify whether a silent channel can be spuriously activated. An agentic analogy is that an observation can be fabricated by interaction among other genuine signals, not necessarily by a dishonest sender. That is a conceptual analogy, not evidence about agents or people. A surviving coefficient is not by itself proof of source presence outside the explicitly modelled channel and decoding protocol.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866; repo AGENTS, RAG, programme and runbook read; issue inventory and open PR titles checked, searches for intermodulation/Sidon returned no matches. All artifacts confined to new issue-scoped directory; frozen records and central manifests untouched. Draft, review and CI pending, no merge authorized by this isolated expedition.
