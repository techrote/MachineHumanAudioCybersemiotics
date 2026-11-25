# The Alarm That Survives Its Own Silence

Exploratory mathematical expedition, 2026-11-25. Refs #458. Original model, proofs and synthetic score; not a selected empirical study, clinical recommendation or protocol amendment. No priority claim.

## The anomaly

Two machines have the same event rate, average duration, active-time fraction and every contiguous binary window probability through length five. Apply the same four-slot persistence gate (suppress the first four slots of each active episode). Both then produce precisely the same long-run active-time fraction. One produces twenty times as many distinct audible episodes as the other.

The difference is not measurement error. Counting episodes and counting occupied time are different functionals of the same duration distribution. An audit horizon adequate for one can be exactly one observation too short for the other.

## Model and stationary window theorem

Let X be a stationary binary alternating renewal process on integer time slots. Successive complete run lengths are mutually independent, with state-specific laws p_s(l) on positive integers and finite means mu_s. Write S_s(r)=P(L_s>=r), F_s(h)=E[(L_s-h)_+], and lambda=1/(mu_0+mu_1), the intensity of starts of runs of either specified state. Stationarity means sampling the initial cycle in proportion to its length and taking a uniform position in it, not starting at a renewal. No aperiodicity assumption is needed for this stationary construction.

In particular P(X=1)=lambda mu_1, and P(01)=P(10)=lambda. At a random slot, the joint probability of state s and exactly r remaining slots in its current run (including the observed slot) is lambda S_s(r). This follows by counting one position with that remaining length in each run of length at least r.

**Theorem.** For w>=2, two such processes have identical laws of all contiguous words of length at most w iff both means and both sets of masses p_s(1),...,p_s(w-2) agree.

Necessity: P(01) determines lambda; P(s)/lambda determines mu_s; P((1-s) s^l (1-s))=lambda p_s(l) for 1<=l<=w-2. Shorter probabilities are marginals of length-w words.

Sufficiency: a constant word s^w has mass lambda F_s(w-1). For a nonconstant word with r>=2 maximal runs of states s_j and lengths l_j, its exact mass is

    lambda S_{s_1}(l_1) * product_{j=2}^{r-1} p_{s_j}(l_j) * S_{s_r}(l_r).

The first run must end at its observed boundary, complete interior runs are sampled from their independent laws, and the last need only survive to the end of the observation. Interior lengths are at most w-2; the first and last lengths are at most w-1. Their survival probabilities are determined from the specified short masses. Finally F_s(w-1)=mu_s-(w-1)+sum_{l<w-1}(w-1-l)p_s(l), so the constant words are also fixed.

**Sharp horizon for bounded runs.** If both laws are supported on 1,...,M with M>=2, windows of length M determine the entire independent alternating renewal law. The remaining masses at M-1 and M follow from normalization and the known mean. For M>=3, windows of length M-1 do not suffice: compare a constant length M-1 with equal masses at M-2 and M, leaving the other state's law unchanged. M=2 requires w=2 in general (marginal occupancy does not determine rate); M=1 is trivial. Without a known finite support bound, no universal finite identifying horizon exists.

These are finite-word identifiability statements, not finite-sample estimators. They require contiguous ordered windows, not shuffled samples or marginal histograms alone.

## Sharp residual-time uncertainty

For a random active slot define R as the number of slots remaining in that run including the current slot. Conditional on X=1,

    P(R>h | X=1)=F_1(h)/mu_1.

Suppose the audit horizon is w>=2, let a=w-1 and focus on one state's unobserved duration tail. Its probability t=P(L>=a) and conditional mean m=E[L|L>=a] are known from the theorem. If t=0 there is no tail ambiguity. Assume t>0, finite support cap M>=a, and integer h>=a. For a<=h<=M and M>a:

    t max(m-h,0) <= F(h) <= t (m-a)(M-h)/(M-a).

Jensen gives the lower bound for the convex hinge (L-h)_+. The secant between a and M gives the upper bound. The lower is attained by masses at floor(m),ceil(m) (the hinge is affine between adjacent integers); the upper is attained by masses at a,M with the given mean. Both attain all the corresponding integer-h bounds simultaneously. Preserve the observed short masses unchanged. Degenerate cap M=a or h>=M gives zero; for h<a the exact F(h) is already known. Divide by mu for conditional residual survival, multiply by lambda for unconditional occupancy after gating.

Without a finite cap, the upper supremum for h>=a is t(m-a), approached by moving a diminishing tail mass to arbitrarily long durations. It need not be attained for h>a. If m>a, E[R|X=s]=E[L(L+1)]/(2mu) has no finite upper bound across the compatible laws: endpoint laws with increasing M have unbounded second moment despite fixed finite first moment. A random-time view is length-biased; an onset view is not. This is established renewal/inspection-paradox mathematics applied to an exact finite-observation fibre.

## Persistence gating: the one-observation debt

A gate with delay h>=1 outputs 1 only after h preceding consecutive active slots. For a general stationary binary process, its occupied-time fraction is P(1^(h+1)); its start rate is P(0 1^(h+1)). These identities follow directly from the Boolean gate and require no renewal independence (the notation denotes a repeated symbol, not exponentiation).

Under the alternating renewal model, each original episode of length L contributes (L-h)_+ audible slots and one audible episode iff L>h. Hence:

    gated occupancy = lambda F(h)
    gated episode intensity = lambda P(L>h).

The first is exactly determined by length h+1 windows, the second by length h+2. At length h+1 the total remaining tail mass t=P(L>=h) and excess s=F(h) are known, but not q=P(L>h). With cap M>h:

    s/(M-h) <= q <= min(t,s).

The excess per surviving episode lies between 1 and M-h; the excess is zero for a tail episode of length h. Both endpoints are attainable: assign tail mass t-q to h, and distribute q on h+1,M to achieve excess s, with no change to short masses or mean. If M=h or s=0 then q=0. The full closed interval is attainable by interpolation. When s>0 the ratio of extreme possible episode intensities is at most M-h and can equal M-h. No cap implies no positive uniform lower bound on episode intensity when s>0.

**Sharp witness.** For arbitrary h>=1, M>h, let off-runs be fixed at h. A uses on-length h+1. B uses length h with probability 1-1/(M-h), length M otherwise. Both have mu_1=h+1, mu_0=h, lambda=1/(2h+1), and no runs shorter than h. They have identical window laws through h+1, and exactly equal gated occupancy lambda. Their gated start intensities are lambda and lambda/(M-h). The first differing word length is h+2 when M>h+1, for instance 0 followed by h+1 ones. Thus the one-slot extra identification requirement for the gated episode count is genuinely necessary in the class. For the occupancy requirement itself, take the same construction at h-1 (for h>=2) with M>h: the two laws agree through h but differ in F(h). At h=1, occupancy cannot be recovered from P(1) alone: fixed equal on/off lengths 1 versus 2 both have occupancy 1/2 but F(1)/(mu_0+mu_1) differs. This establishes sharp uniform horizons for both functionals (not for every individual law).

Conditional on a randomly inspected gated-active slot, the mean number of remaining audible slots is 1 in A and (M-h+1)/2 in B. This quantity can grow arbitrarily large despite identical original short windows and equal gated duty. The conditioned quantity is not the average remaining time at onset.

### Joint event and occupied-time frontier

For an entire duration law supported on integer [a,M], with mean m, a<=h<M, let q=P(L>h) and s=E[(L-h)_+]. Exactly the following linear inequalities describe the feasible pair (q,s):

    0<=q<=1
    q<=s<=(M-h)q
    a(1-q)<=m-hq-s<=h(1-q).

Necessity: long durations contribute total first moment hq+s and lie in [h+1,M]; short durations lie in [a,h]. Sufficiency: place the short mass 1-q on a,h to give moment m-hq-s, and long mass q on h+1,M to give moment hq+s. Degenerate intervals use their only endpoint. The four-point construction is valid for arbitrary real feasible masses. Conditional tails use the same polygon after normalization. The exact integer-grid census below checks this construction, including zero mass and coincident endpoints.

This identifies the feasible trade-off between a persistence filter's surviving episode count and occupied time, rather than treating them as interchangeable notions of burden.

## Synthetic score and executable evidence

For h=4,M=24, construct two deterministic circular scores with twenty active runs and twenty four-slot rests. A uses twenty five-slot runs; B uses nineteen four-slot runs and one twenty-four-slot run. Each has 180 slots and 100 active slots. Every circular window histogram through length five is identical; length six differs. These scores are deterministic, not samples asserted to be iid renewal runs. All windows are counted with wraparound; the gate starts after a rest.

After four-slot gating, each score has twenty active slots. A has twenty one-slot audible runs; B has one twenty-slot run. The Python renderer assigns each active slot an identical 250 Hz tapered pulse (320 samples at 8 kHz) and each inactive slot zero. Thus the raw pair and the gated pair separately have exactly equal PCM sum of squared samples, but distinct PCM arrays. Four original 7.2-second mono PCM16 WAVs are generated locally; no third-party stimuli or binary commits. The occupied-slot metric is not a claim of equal perceived loudness or number of pulse onsets.

Reproduction from this directory:

    node laboratory.cjs > build-execution.json
    cmp execution.json build-execution.json
    python3 witness.py --out build
    cmp witness.json build/witness.json

The JavaScript exact-integer laboratory enumerates all quarter-mass laws on five on-lengths and three off-lengths (1050 combinations). It compares explicit hidden residual-state path enumeration with the run factorization on 130200 literal words, checks 5250 bidirectional signature/word-law associations and 966 stop-loss inequalities. It constructs witnesses for 300 feasible quarter-grid joint-polytope points; 5950 other grid points fail the explicit necessary inequalities. All assertions passed. Integer numerators are small enough for exact JS Number arithmetic in this bounded census; it is not a general arbitrary-size solver. The core ran in a JavaScript isolate, not a native Node CLI. Distinct window-law counts for w=2..6: 153,525,825,1050,1050.

The separate native Python 3.13.5 program checks circular histograms, PCM energy and 1024 exact rational boundary-family cases. Executed twice, with byte-identical receipt; source and receipt Git blobs match locally executed bytes. All tests passed. Native full repository checkout failed DNS resolution; full repository tests not claimed. Same-agent independent methods, not independent scientific review.

## Interpretation, negative cases and design boundary

A candidate MHAC telemetry receipt should distinguish state occupancy, event onset rate, surviving-event rate, persistence threshold, sampling convention, maximum possible duration and remaining-time uncertainty. A system can exactly qualify its aggregate acoustic workload while remaining unable to identify the number of separate interruptions it creates. If an operator acts per episode, the latter may matter; if an operator reacts to exposure time, the former may matter. Which model describes humans is an empirical question, not settled by either measure.

The proposed artistic instrument, the Persistence Organ, lets one composer vary duration-tail mass while another chooses the gate delay. The score includes separate event and time counters. One can cross from many little pulses to a long sustained sequence while keeping total occupied time and squared sample energy unchanged. The rendered score exists; interactive instrument and perception study do not.

Contrary cases:
- If runs are dependent, the finite-window sufficiency theorem fails. Example: each on/off duration marginal is uniform on {1,2}. Compare independent runs with paired cycles in which on and following off have identical lengths, independent across cycles. Both means and every marginal duration mass agree; the stationary probability of 0101 is respectively 1/12 and 1/6 because both complete interior runs must be of length one. The direct Boolean gate identities remain true.
- Time-varying rates, overlapping channels, censoring, missing transitions, acknowledgement-triggered termination and nonstationarity are outside the independent renewal theorem. The score is not evidence for a real device.
- With a known fixed duration or zero tail mass, short-window ambiguity can disappear. The horizon results are worst-case over the stated model.
- Event rate is not the count of emitted beeps if an audible episode contains repeated beeps or priority-dependent playback. PCM energy is not human attention, nuisance or loudness. No clinical delay policy is proposed or validated.
- The simple pulse renderer does not model continuous phase, hearing, acoustics or environmental interference. No participant was contacted or exposed.

## Source ledger

S1. Takuma Akimoto, *Statistics of the number of renewals, occupation times, and correlation in ordinary, equilibrium, and aging alternating renewal processes*, Physical Review E 108, 054113 (2023), [DOI](https://doi.org/10.1103/PhysRevE.108.054113), [author preprint v1](https://arxiv.org/pdf/2306.00359). Publisher metadata/abstract and preprint pp.3–4 (PDF indices 2–3) visually inspected, specifically §III.A Eqs.12,18–21 and §III.B Eqs.31–32. Establishes occupation/recurrence context in continuous time and highlights divergent mean recurrence with finite mean durations. Our discrete proof and observation-horizon theorems are separately derived, not claims attributed to Akimoto. No full-paper or priority review claimed.

S2. J.O. Jämsä, K.H. Uutela, A.-M. Tapper and L. Lehtonen, *Clinical alarms and alarm fatigue in a University Hospital Emergency Department—A retrospective data analysis*, Acta Anaesthesiologica Scandinavica 65(7),979–985 (2021), [publisher full text](https://doi.org/10.1111/aas.13824). Read HTML §2.2–2.3, §3.3–3.4 and relevant §4 limitations. The authors distinguish individual alarm episodes from estimated repetitions of their sounds; the latter are governed by priority and durations. They report inability to determine clinical significance, and limitations in generalizability. This motivates separating count and exposure, and also directly limits transfer from our binary gate. No new study extraction, clinical threshold recommendation or independent validation inferred. Source access and reading by one ChatGPT/GPT-6.2 agent on 2026-11-25; no participant records or restricted source copies retained.

The elementary convex hinge bounds are standard Jensen/secant arguments. No new mathematical priority is asserted.

## Reconciliation and custody

Base main 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity, validation and experiment boundary; inspected 288 branch names, 100 recent open issues, 100 recent open PRs, and searched renewal, residual life, inspection paradox, length bias, duration bias and debounce (no returned matching issue). Rejected a first idea about reversible binary block statistics after reading the existing #340 expedition, which already treats that topic. Prior #441 exact-head workflow 45529023146 succeeded; it remains separate. The new issue #458 had no comments at intake; fresh branch mhac-458/finite-window-renewal owns only this directory. No shared manifest, accepted baseline or other worker branch touched. Draft pending independent mathematical critique and exact-head structural qualification. No human gate is claimed satisfied.

## Fictional afterword

The engineer took four beats of sound away from every warning. She counted the remaining beats and announced the two machines were equally quiet. One listener marked twenty beginnings; the other marked one long passage.

The engineer had measured the silence she had purchased. She had not counted the interruptions that remained.
