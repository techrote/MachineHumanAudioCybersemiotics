# The Ledger That Cannot Count a Long Note

Exploratory deterministic mathematics and original sonic score, 2026-11-25. Refs #562. No claim of scientific priority, human validation, safety certification or frozen-protocol amendment.

## A local inventory is not a duration receipt

Two 40-slot binary circular scores have four rests of one slot each. The first has four active runs of nine slots; the second has active runs of lengths 3, 3, 3 and 27. Both have 36 active slots, four onsets, the same complete counts of every contiguous word through length four, and identical digital squared-sample energy in the renderer. Nevertheless, their longest active episodes differ by a factor of three. All intermediate maximum lengths from nine to 27 are also compatible with this receipt.

The older expedition #458 already established a stochastic independent-renewal horizon theorem, residual-life bounds and a deterministic gated-load witness. This work asks a different question: what is the exact attainable set of finite-record run spectra, including the worst possible longest-run ambiguity at a fixed record length, without independence assumptions? #302 studied Euler traversal of a novelty inventory, not these target functionals. Both issue bodies, comment collections and reports were inspected before scoping this work.

## Model and exact fibre theorem

Let W be a mixed binary circular word of N slots (both symbols occur), with 1 <= r <= N. C(u) counts cyclic occurrences of u, once per start position; the observer receives the complete histogram of length-r words, with no position labels. Shorter counts are obtained by summing over continuations. An all-constant record is separately recognizable and its finite-record maximum is N for its own symbol and zero for the other; an indefinitely repeated constant signal is not a finite run.

For either symbol b, let a=r-1, with r>=2. Use the notation b^j for j repetitions of b, and c for the opposite symbol.

* For 1 <= j < a, the number of length-j runs is C(c b^j c).
* The number L of runs of length at least a is C(c b^a).
* The total excess E above a among those L runs is C(b^(a+1)).

Each identity counts starts of runs or homogeneous windows literally. If L=0, the complete run-length multiset of b is already determined. If L>0, every compatible b-run multiset has precisely the fixed short runs plus L lengths a+e_i with nonnegative integer e_i summing to E.

**Theorem: every such weak composition of E is realizable inside the original full histogram fibre, simultaneously and independently for the two symbols.** This is stronger than merely preserving individual run-count statistics.

Proof: take any witness word for the receipt and hold its cyclic sequence of alternating run slots fixed. Keep short runs fixed and change only long-run excess allocations, preserving their total separately for each symbol. For a nonconstant pattern of length at most r, locate its first transition in the witness word. The remaining matching constraints require its internal complete runs to equal their specified lengths (at most r-2), and its first and last runs to be at least their specified lengths (at most r-1). These constraints, and the number of placements, depend only on the ordered run slots clipped at a. If the first and last fragments lie in the same cyclic run, their combined length is at most r-1; the condition still depends only on the clipped length. There is one candidate start per first transition. The clipped ordered slots are unchanged. Constant length-r patterns depend only on E; shorter constant counts follow by marginalization. Therefore every proposed redistribution preserves the complete receipt. The converse follows from the three literal count identities. QED.

This does not claim that the receipt determines the ordered clipped skeleton, nor that two records with identical run multisets have identical receipts. For example 001011 and 001101 have the same sorted on/off run lengths but different circular length-four histograms. The census found this counterexample at N=6. The theorem is about what can vary inside a fibre, not what determines the fibre.

## Peak-duration intervals and their exact finite-record envelope

Let M_b denote the longest b-run. When L>0, the exact attainable integer interval is

    a + ceil(E/L) <= M_b <= a + E.

The endpoints are attained by balancing excesses and concentrating all excess in one run, respectively. Every intermediate excess maximum m between ceil(E/L) and E can be realized: allocate m to one slot and distribute E-m among L-1 slots each capped by m. The zero-excess and L=1 cases are immediate. When L=0, the peak is known from the short-run counts.

The simultaneous attainable set of (M_0,M_1) is the Cartesian product of the two independently derived intervals, by the fibre theorem. This remains true even if the baseline histogram contains mixed patterns linking nearby opposite-symbol runs. An audit need not reconstruct the whole history to compute these exact target intervals.

The width is E-ceil(E/L). For absolute-error estimation of a peak, its real-valued interval midpoint is minimax, with error half the width; integer estimates require the ceiling of half the width. The longest run is identified iff L=0, L=1 or E<=1.

**Worst-case finite-record theorem.** For N>=2 and 2<=r<=N, the greatest possible ambiguity width over all mixed-word receipts is

    D(N,r) = max({0} union {N-(L-1)r-ceil(N/L): 1<=L<=floor(N/r)}).

Each long b-run costs at least r-1 slots plus a distinct intervening opposite-symbol slot. Thus E<=N-Lr. The width E-ceil(E/L) is nondecreasing in integer E, giving the stated bound after substitution. For each allowed L, a circle of L singleton opposite runs alternating with L long b-runs of total length N-L attains it by the redistribution theorem. This includes equality and degenerate cases. The formula is a finite maximization, not a numerical fit.

With H b-slots and Z=N-H opposite slots fixed and positive, the corresponding bound is the maximum of E_L-ceil(E_L/L) over 1<=L<=min(Z,floor(H/a)), together with zero, where E_L=H-La. It is attained by putting all b-slots into the L long runs and distributing Z among L positive opposite runs. This refinement follows analytically, but was not separately exhaustively tested.

For r=1 the histogram records only H and Z. The attainable peak interval is ceil(H/Z) to H: distribute H among up to Z positive b-runs, or take one run. In particular the maximum ambiguity is max over 1<=H<N of H-ceil(H/(N-H)), together with zero. This case does not assert joint rectangularity.

**Sharp universal horizon.** For r>=2, positive ambiguity is possible iff N>=2r+2. Necessity: L>=2 and E>=2; sufficiency: use L=2 and E=N-2r. For r=1 positive ambiguity first occurs at N=4 (1100 versus 1010), with longer witnesses obtained by concentrating or splitting ones. Therefore the smallest universal observation order for exact longest-run identification of every mixed length-N circle is floor(N/2), for N>=2. This identifies one statistic, not the whole word or its rotation. At N=12, order six identifies the maximum in every fibre although the exact census still has 338 receipt classes, versus 350 at full order.

For N=40,r=4 the maximizing width is 18, attained with L=4 (also L=3). For N=100,r=5 the width is 60. In general the upper bound remains large when the window horizon is small relative to the record.

## A finite integer frontier for episode and occupied-time receipts

A gate retains the slots at and after the T-th slot of each b-run. Let T=a+s, s>=1; all short runs are suppressed. For a long run a+e_i, its retained occupancy is max(0,e_i-s+1). Define Q as number of retained episodes and G as retained slot count.

For L>0, the exact possible integer pairs (Q,G) are specified by

    0 <= Q <= L
    0 <= G <= E
    Q <= G
    Q=0 iff G=0
    Q(s-1)+G <= E <= L(s-1)+G.

Necessity: each surviving run contributes at least one retained slot and consumes s-1 additional excess slots; each non-survivor can consume at most s-1 excess slots. Sufficiency: allocate G as Q positive integers, add s-1 to each surviving excess, then distribute E-Q(s-1)-G among L-Q non-surviving excesses each bounded by s-1. For Q=0 distribute the entire E among non-survivors; for Q=L the residual must vanish. All constructions remain inside the original complete histogram fibre. The finite integer feasible set is therefore exact and not a probabilistic relaxation.

In particular the attainable number of surviving episodes ranges from zero (if E<=L(s-1)) or one otherwise, through min(L,floor(E/s)). The occupancy range is max(0,E-L(s-1)) to max(0,E-(s-1)); these are separately sharp and must not be combined arbitrarily. This extends the earlier renewal-law polygon (#458) to exact finite integer counts with all higher-order mixed-pattern counts preserved.

At threshold T=r, s=1, G=E is already known, while Q can still vary. This recovers the persistence debt of #458 as a special deterministic case rather than claiming it as new. At T>r, even the retained occupancy need not be known.

## The cost of asking the right duration question

Suppose a supplementary authenticated yes/no probe asks whether M_b>=T. It can be realized symbolically by testing whether C(b^T)>0. In a fibre with attainable integer peak interval [lo,hi], let W=hi-lo.

* A nonadaptive dictionary of such threshold questions must include every threshold lo+1,...,hi. Otherwise the two consecutive attainable peaks on either side of an omitted threshold produce identical answers. Exactly W questions suffice.
* Adaptive threshold interrogation uses binary search and requires exactly ceil(log2(W+1)) questions in the worst case. A binary decision tree with fewer leaves cannot distinguish all W+1 possibilities; splitting the remaining interval as evenly as possible attains the bound.

For the 40-slot example the receipt leaves 19 possible peak lengths: 18 predetermined questions or at most five adaptive questions. For a specific operational threshold, only one extra yes/no receipt is needed. This is a bound on this particular query language, not on arbitrary count-valued receipts, raw timestamp access, active interventions or a directly reported maximum. A transmitter already storing the longest run can report it instead. No claim of secure authentication, fault tolerance, or measured communication efficiency follows.

## Executable qualification and original score

From this expedition directory:

    python3 laboratory.py --out build
    node crosscheck.cjs

The standard-library Python census directly enumerates every labelled mixed binary word for N=2..12 and every r=1..N. It groups literal cyclic substring counts, checks every attained peak, verifies the complete joint rectangle against actual point sets for r>=2, and compares every profile maximum width with the formula. Separately it enumerates every weak composition for L=1..6, E=0..12 and s=1..7 and compares the exact attainable joint gate frontier to its inequalities.

Native Python 3.13.5 ran twice: 89,958 word/horizon cases, 6,259 fibres, 6,193 joint rectangles and 546 gate frontiers; no assertion failure. The full generated qualification receipt reproduced byte-for-byte, SHA-256 recorded in execution.json. The exact Python source blob was verified on GitHub. A separate JavaScript bit-rotation implementation computes histograms without slicing strings and computes longest circular runs by iterated bit erosion. Its core ran in the JavaScript isolate, not a native Node CLI. Aggregate counts agree exactly; its full profile table is in execution.json. Same-agent independent calculation methods, not independent human review.

The renderer generates balanced.wav and concentrated.wav: 3.2-second original 8 kHz mono PCM16. Each active 80 ms slot uses the same integer-period 500 Hz oscillator samples, silence elsewhere. The first score has four 720 ms active runs; the second has three 240 ms runs and one 2.16 s run. Squared PCM energy is exactly 233257288320 for each recording. The underlying 40-symbol words have identical four-window histograms and different five-window histograms. File hashes differ. This establishes exact digital properties, not equal loudness, perceptual indistinguishability, participant response or physical room-acoustic equivalence. Binary WAVs are regenerated locally, not committed.

The speculative Long Note Organ would expose the clipped run skeleton, excess allocation knobs, and separate occupancy/peak/episode receipts. One performer can redistribute excess while the local-statistics display stays frozen. Another can ask one duration-threshold question or request an exact maximum. The finite generator and auditor exist; the live performance interface does not.

## Sources, negative sediment and transfer boundaries

S1 — Karhumäki, Saarela and Zamboni, On a generalization of Abelian equivalence and complexity of infinite words, Journal of Combinatorial Theory, Series A (2013 publication metadata), https://doi.org/10.1016/j.jcta.2013.08.008 ; author preprint v1 https://arxiv.org/pdf/1301.5104 . Read abstract and introduction pp.1–2; original PDF page 2 (zero-based index 1) visually inspected. They define k-Abelian equivalence using counts of contiguous factors in finite linear words. Our cyclic counting contract is an explicit variant, not an attribution of these duration results to them. No complete-paper reading or priority claim.

S2 — NIST CSRC, Guide to the Statistical Tests, https://csrc.nist.gov/Projects/random-bit-generation/Documentation-and-Software/Guide-to-the-Statistical-Tests . Read the official page's Frequency, Runs, Longest Run of Ones and Serial Test descriptions. NIST distinguishes these statistical objectives; this expedition supplies exact deterministic collisions rather than testing randomness, making any statistical inference, or recommending an RNG test.

S3 — MHAC issue #458 and its finite-window-renewal report (branch mhac-458/finite-window-renewal), read model, sharp horizon, residual-time, joint gate frontier and deterministic score passages. MHAC issue #302 and its refrain-exhausts-itself report (branch mhac-302/refrain-exhausts-itself), read finite graph construction and novelty/repetition discussion. These are project sediment, not independent empirical evidence.

S4 — Loudness summation and the mismatch negativity event-related brain potential in humans (PMC2846746). Search discovery only; direct PMC retrieval returned browser challenge. No experimental finding or effect size extracted. The obvious alternative explanation for any future listening result is temporal integration, onset/offset grouping or stimulus envelope, not logical access to a histogram. A new controlled experiment and lawful participant gate would be required.

The source access was web-mediated, 2026-11-25; no restricted source bytes committed. The mathematical proof is self-contained. The counts are exact in their stipulated finite model. No implication for real alarm delays, human fatigue, or optimal perceptual code design has been established. Real records may be linear rather than circular, have missing samples or overlapping sources, or exhibit uncertain state decoding; the exact cyclic receipt theorem cannot be silently substituted for those models. A linear record with boundary fragments can need additional endpoint receipts. If the listener has the whole time series, local histogram ambiguity is not the listener's information limit.

Interpretation: a sign can accurately express a statistical equivalence class while failing to warrant a claim about a particular member of that class. The explicit duration interval is an alternative to overclaiming exactness. Conventional combinatorics suffices to explain the anomaly; cybersemiotics has no demonstrated additional predictive contribution here. A design hypothesis is to communicate occupancy and episode/peak evidence separately when the latter are action-relevant. Human validation is absent.

Fiction: A clerk measures every four-note phrase in two performances and finds the same inventory. The apprentice asks how long the longest note lasted. He offers her the inventory again. She asks for a single longer phrase.

## Repository checkpoint

Base main 495a98ca12bae467a507031f04931aa4254b1866, fetched live. Read AGENTS, README, RAG, programme, runbook, integrity, validation, #458 and #302 issues/comments/reports, and newly scoped #562 with empty comment list. Reviewed 100 recent open issue and 100 recent open PR results; enumerated 341 branches and searched Euler trail, de Bruijn, transition counts, Markov type and substring counts. Previous expedition #555 exact-head workflow run 45617922900 succeeded. No other branches or shared manifests changed.

Native full repository checkout failed DNS resolution (git ls-remote could not resolve github.com); full local validation not claimed. Draft PR for integration critique and exact-head CI; no closing keyword. Scope isolated to this directory. AI-assisted research, code and same-agent self-check; no external or human reviewer. Preserve source, exact execution record, and regenerable PCM. No human action required to reproduce; integration acceptance is outstanding.
