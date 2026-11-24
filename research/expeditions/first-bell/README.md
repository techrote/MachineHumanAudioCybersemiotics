# The Bell That Rings Once
## First-hit calibration, repeat-exposure debt and the semantics of an alert

**Refs #284 · 24 November 2026 · bounded mathematical reconstruction, synthetic computation, interpretation, design hypothesis and fiction.** Outside frozen Track E/G. Not empirical auditory evidence, human validation, production software or a priority claim.

### The anomaly

Suppose a machine repeatedly forecasts the same binary event Y (not a new event each tick). Each tick is perfectly calibrated in isolation: among cases reporting p, the event occurs with probability p. An interface sounds a bell the first time p is reported, then suppresses repeats for that case. Does that bell still mean p? No. A calibration certificate for repeated exposures is not a certificate for distinct alerted cases.

For three ticks and p=1/2, there can be one positive case that triggers at every tick and three distinct negative cases that trigger once each. Each tick has exactly one positive and one negative alert. The bell rings for four distinct cases; only one is positive. The per-tick probability is 1/2; the per-bell probability is 1/4. Reverse the labels to attain 3/4. There is no faulty speaker, false label or inaccurate arithmetic. Deduplication changes the reference population.

### Proof: sharp first-hit bounds

Let Y in {0,1}, P_t in [0,1], t=1,...,T, with E[Y|P_t]=P_t at every fixed t. Call A_t={P_t=p} for one fixed interior p, H=union A_t, with P(H)>0. Empty A_t are permitted. Let a_t=P(Y=1,A_t), b_t=P(Y=0,A_t). Then a_t=p P(A_t), b_t=(1-p) P(A_t). Let a=P(Y=1,H), b=P(Y=0,H), and r=a/(a+b). The same p is emitted once at the first hit, and no p alert is emitted on nonhits.

The union bounds max a_t <= a <= sum a_t and max b_t <= b <= sum b_t follow by inclusion and subadditivity. Put S=sum P(A_t), M=max P(A_t). Since S<=TM and M>0, a/b lies between pM/((1-p)S) and pS/((1-p)M). Thus:

**p/[p+T(1-p)] <= r <= Tp/[Tp+1-p].**

In odds units, the maximum discrepancy is a factor T in either direction. It is not a bound on the posterior after a particular hit time, nor a guarantee for arbitrary adaptive reporting.

Sharpness: assign mass p to a common positive block and mass (1-p) to each of T disjoint negative blocks, then normalize by total mass. A_t is the common positive block plus negative block t. Outside A_t the forecast is 0, ensuring full per-time calibration. H is the whole population. Swapping the roles of positive and negative blocks gives the upper extremum with outside forecast 1. For rational p this is a finite uniform population with replicated blocks. For arbitrary real p use the indicated finite atom weights. At p=0 or 1 calibration makes every nonempty hit pure and the union pure as well. T=1 is exact ordinary calibration.

**A stronger fixed-cohort result.** Suppose a finite roster has N+ positives, N- negatives, and at each tick the hit set contains known counts a_t,b_t with a_t/(a_t+b_t)=p when nonempty. Set L+=max a_t, U+=min(N+,sum a_t), L-=max b_t, U-=min(N-,sum b_t). Then the exact extrema of the distinct-case hit rate over compatible hit arrangements are

**r_min=L+/(L++U-), r_max=U+/(U++L-).**

Proof: the upper/lower union-size bounds are necessary separately for each label class. To attain the minimum union size, nest each time's hit set inside the largest set. To attain the maximum union size, take consecutive blocks of the specified lengths on a cyclic list of all class members, continuing from where the preceding block ended. Each block has length at most class size, and the covered union has size min(class size,sum lengths). Positive and negative arrangements are independent and combine at each time. Any resulting hit arrangement can be completed to calibrated forecasts by reporting p on hits and the degenerate posterior 0 or 1 outside, as a synthetic observation that reveals the label outside hits. This is a realizability construction, not an assertion that a deployed forecaster sees the outcome. If total distinct alerts h is also known, feasible positive union counts lie in [max(L+,h-U-),min(U+,h-L-)]. Every integer in a class union-size interval is attainable: start with nested sets, replace a duplicated covered element in some set by a new uncovered element, increasing the union by one; continue until the desired size. The two classes can therefore realize any compatible h and positive count. An empty interval refuses an inconsistent receipt.

### The repeat-exposure identity

Define K=sum 1(A_t), the number of hits for a case. On H, K>=1. Per-time reliability gives E[YK|H]=p E[K|H], so

**p-r = Cov(Y,K | H) / E[K|H].**

This exact identity locates the defect: if positive cases receive more repeated hits than negative cases, the per-exposure value overstates the distinct-case rate. Equal hit multiplicities, or zero conditional covariance, preserve calibration. A uniformly random tick chosen independently of the forecasts and outcome also preserves fixed-time calibration; first-hit selection is different. The rate r is an observational property in a fixed-outcome world; if an alarm changes the event, this proof is not a causal-effect analysis. The construction uses exact p, not finite-width bins or continuous threshold crossing. For threshold hits P_t>=p, E[Y|A_t]>=p and the lower bound still follows from a_t>=p/(1-p)b_t and max b_t >= sum b_t/T; the symmetric upper bound no longer follows (all hit forecasts could be 1).

### Even a complete unlabelled transcript cannot rescue the certificate

Consider two ticks, four cases per hit-mask, and seven positives in sixteen cases overall. Each tick reports 1/2 when its bit is set and 3/8 otherwise. Here is the entire joint trace distribution and two possible hidden allocations of positives:

| Hit mask (tick 1, tick 2) | Cases | Positive in world H | Positive in world L |
|---|---:|---:|---:|
| 00 | 4 | 0 | 3 |
| 10 | 4 | 3 | 0 |
| 01 | 4 | 3 | 0 |
| 11 | 4 | 1 | 4 |

Both worlds have 4/8 positives in each tick's hit group and 3/8 in its complement. Thus both have the same per-time reliability, forecast histograms, binary Brier scores, base rate, full unlabelled trajectory distribution, first-hit timing distribution, and repeat multiplicity distribution. Yet first-hit reliability is 7/12 in H and 4/12 in L, straddling 1/2. The first tick is calibrated in both; the second tick's *new* alerts have reliability 3/4 and 0 respectively. A calibration report that simply joins per-tick score bins cannot tell the worlds apart.

More generally with two ticks let c_0,c_1,c_2,c_3 be the known trace counts, M the total positives, a_1,a_2 positives in each hit group. Set z=positives in cell 11. Then the positive allocation is (M-a_1-a_2+z, a_1-z, a_2-z, z). Capacity constraints are exactly:

- L=max(0,a_1-c_1,a_2-c_2,a_1+a_2-M)
- U=min(c_3,a_1,a_2,c_0+a_1+a_2-M).

All integer z in [L,U] are attainable by choosing that many positive members in each trace cell. With h=c_1+c_2+c_3>0, r=(a_1+a_2-z)/h, giving sharp bounds [(a_1+a_2-U)/h,(a_1+a_2-L)/h]. For the witness L=1,U=4. This is a partial-identification result even with perfect trace observability but no joined outcomes. It is not a claim that any individual label can be inferred from such a receipt.

### The mathematical ancestry and the repair

Thomas Wilkinson and Christopher Ferro, *Calibrated Probability Forecast Sequences and Measure-Valued Martingales*, arXiv:2606.31621 (30 June 2026), [public preprint](https://arxiv.org/abs/2606.31621), Introduction and section 2, Definitions 2.1–2.2, Proposition 2.4 and remark following it. Accessed 24 November 2026 via rendered public web text, read Introduction and section 2; some displayed equations were omitted by the text rendering, so rely on the surrounding explicit prose and proposition statements, not a transcription of missing equations. Their fixed-event sequence calibration requires the current forecast to condition on the history, unlike merely checking each tick separately. Their proposition connects sequence calibration with the terminal outcome appended to a measure-valued martingale. The binary first-hit bound and trace proof above are self-contained derivations, not claimed to be their theorem, nor claimed novel relative to the broader literature. The preprint is not treated as peer-reviewed evidence.

Gneiting and Resin, *Regression Diagnostics meets Forecast Evaluation: Conditional Calibration, Reliability Diagrams, and Coefficient of Determination*, arXiv:2108.03210 (2021), [public abstract](https://arxiv.org/abs/2108.03210), accessed same date; abstract only, supports the general distinction between conditional calibration concepts. Kees van Schaik's [Martingale Theory notes, chapter 6](https://keesvs.net/UoM/teaching/martingales/notes/Chapter6.html), section 6.2 (definition of stopping time) and 6.4 (optional stopping context), public web text accessed same date, no claim of reading the whole course. No external review.

**Positive theorem.** If F_t is an increasing history including all information used by the alert selector, and P_t=E[Y|F_t], then for a bounded stopping time tau, P_tau=E[Y|F_tau]. For every event B in F_tau, partition B by tau=t. Each B intersect {tau=t} lies in F_t, hence E[Y 1(B,tau=t)]=E[P_t 1(B,tau=t)]. Sum over t. Conditioning on P_tau and, where relevant, the observed stop event therefore preserves the probability. For the first-hit rule, apply this to tau=min(first hit,T); the actual hit indicator is known at tau, so E[Y|H]=p whenever H has positive mass. This result depends on the selector's information being contained in the filtration and the event definition remaining fixed. Merely having a martingale of forecasts without terminal outcome consistency is insufficient; a constant 1/2 process with Y always 1 is a trivial counterexample.

**Stronger negative result: even an exact martingale test can miss first-hit bias.** Consider 32 equally weighted cases and first-tick forecasts 1/2 and 1/4. Second-tick forecast values are 0, 1/4, 1/2, 3/4. The trace count matrix (rows in that first-tick order) is

| First forecast | 0 | 1/4 | 1/2 | 3/4 |
|---|---:|---:|---:|---:|
| 1/2 | 0 | 4 | 8 | 4 |
| 1/4 | 4 | 8 | 4 | 0 |

The conditional means of the second forecast in the two rows are exactly 1/2 and 1/4: the forecast process itself is a martingale. The positive-count matrix can nevertheless be either the ideal matrix ((0,1,4,3),(0,2,2,0)) or the family ((0,1+d,4-d,3),(0,2-d,2+d,0)) for integer -1<=d<=2. The row sums remain (8,4) and column sums remain (0,3,6,3); hence each forecast is calibrated in isolation and every world has the same forecast-path law. Only d=0 is history-conditioned at tick 2. For the first hit of 1/2, all 16 first-row cases and the 4 second-row cases in the 1/2 column are selected, yielding exactly (10+d)/20 positives. The range is 45% to 60%, with 50% for the history-conditioned world. A test of the forecast martingale property alone, even with perfect fixed-time calibration and full unlabelled forecast histories, cannot distinguish these worlds. It must also test consistency with the terminal outcome given the history. This directly illustrates the terminal condition in Wilkinson/Ferro Proposition 2.4, not a counterexample to that proposition.

The independent small integer enumeration in martingale-counterexample.mjs checked all 5*9*5*5*9*5=50,625 cell allocations and found exactly four calibrated matrices; all four have the stated first-hit rates, only one is history-conditioned. The execution receipt is martingale-execution.json. This is a separate executed computation by the same assistant, not an independent human audit.

**Converse with a terminal reveal.** Append P_(T+1)=Y. If every bounded history-adapted stopping time yields a calibrated stopped forecast, then for every interior forecast value p and measurable history event B contained in {P_t=p}, select tau=t on B and T+1 otherwise. The only cases with stopped p are B, so E[Y|B]=p. More generally choose B within arbitrary history events and interior forecast-value ranges; the stopped conditional moment identity gives E[(Y-P_t)1(B)]=0. Endpoints are already pure by fixed-time calibration. Thus history-conditioned calibration is necessary in this augmented model. This is not a converse without the terminal reveal assumption.

### Executed laboratory and contrary evidence

Run from the repository root with Node 18+: `node research/expeditions/first-bell/laboratory.mjs /tmp/first-bell-wavs`. Omit the directory for JSON output alone. Compare with execution.json. The computational core was actually executed in a JavaScript V8 isolate by the same GPT-6.2 assistant that authored the report. The Node filesystem wrapper was not thereby exercised. No external human reviewer or subagent was used.

The first census fixes a labelled uniform roster of size n, all k=1,...,n-1 positive-count configurations represented by the first k labels, and enumerates all ordered triples of nonempty mixed-label hit subsets sharing an exact interior p. It does not weight by the number of label permutations. For each ordered triple of hit-count pairs it checks that observed extreme union rates equal the fixed-cohort formula; every case checks the universal and cohort bounds, pooled per-occurrence calibration and the integer covariance identity.

| n | Triples | Distinct fixed-cohort groups | Miscalibrated first hit | Groups admitting both bias signs |
|---:|---:|---:|---:|---:|
| 2 | 1 | 1 | 0 | 0 |
| 3 | 18 | 4 | 12 | 0 |
| 4 | 251 | 16 | 132 | 1 |
| 5 | 2652 | 32 | 2004 | 4 |
| 6 | 24105 | 83 | 15948 | 16 |
| 7 | 205998 | 140 | 152580 | 32 |

The second census enumerates the 50,625 two-tick trace tables with each cell total 0..4 and each positive cell count 0..total (the labelled cases within a cell are not permuted). 3,004 tables survive nonempty hit/nonhit, common interior hit probability and distinct complement-probability filters. They form 1,988 groups sharing trace counts, total positives and per-time hit positives. 824 are nonidentified by those observables; 616 admit both signs of bias. All observed extrema agree with the exact interval. These are counts in a stipulated synthetic model, not occurrence rates in deployed systems. Separately, all 256 binary assignments on an eight-leaf balanced information tree passed the stopped-posterior control (618 nonempty stop-time/probability groups).

Contrary cases: equal multiplicities give exact calibration even if repeated alerts exist; individual fixed-tick checks may suffice when only a prespecified single tick is released; full *labelled* histories identify the stopped rate; actual Bayesian updates on the selector's filtration are safe under the stated fixed-outcome assumptions. The sharp universal range does not imply a specific bias direction for ordinary systems or guarantee practical identifiability with finite noisy calibration data.

### An acoustic witness: the once-rung bell

The original integer triangle-wave renderer encodes each row's two forecasts as 450 Hz (3/8) and 500 Hz (1/2) tones; the stereo outcome track is 260 Hz or 740 Hz. Each note lasts 100 ms, with a short integer envelope. Four PCM WAV byte arrays were generated in memory. The two public tracks are byte-identical (51244 bytes, FNV-1a f80d85c1). The two paired stereo tracks differ (102444 bytes each; b5ae7e09 and 87fd7589). Direct byte comparison accompanies fingerprints. The public tracks encode complete forecast traces, not just a pooled histogram. The paired tracks are synthetic diagnostics, not an operational channel that should disclose outcomes before they occur.

Speculative performance: a choir of bells sounds each probability at every tick. A gate cuts off subsequent repetitions by the same case. A second ensemble plays the case-linked outcomes once they are resolved. By varying the overlap of the alert sets while retaining all per-tick statistics, the composer alters the relation between the two ensembles without changing the public score. This is a study of exposure versus reference, not a perceptual claim. Human interpretation, accessibility, alarm burden and hazard response need distinct evaluation.

### Engineering interpretation and scope checkpoint

An alert phrase such as "one in two" needs a reference class: each forecast exposure, each distinct episode, each newly alerted episode at time t, or the posterior conditioned on the actual trace. It need not encode every detail acoustically, but the machine must not silently transfer a calibration certificate between those classes. Candidate receipt: event definition, target horizon and fixed-event identity, case/deduplication key, full forecast history and availability of joined outcomes, selector and its information filtration, hit definition, episode and exposure counts, first-hit timing, calibration population, and uncertainty/shift assessment. Compare repeat-enabled and deduplicated policies on the same cases; estimate stopped calibration directly or establish an appropriate history-conditioned forecast contract. Do not infer false-alarm behavior or user trust from this theorem.

Reconciled main 495a98ca12bae467a507031f04931aa4254b1866; root AGENTS, RAG, programme, runbook, integrity and validation read; recent issues/PRs and branch search inspected; targeted keyword search found #220 fixed-weight pooling, whose issue/comments and actual draft report were inspected. #284 issue and empty comments verified; branch created from refreshed main. No dependence on acceptance of #221, no canonical manifest edits. #277's final head had successful CI, but it belongs to another expedition and is untouched. The source-bounded proof and synthetic computations are local to this branch. Exact-head CI and review are separate from this receipt; leave PR unmerged until qualified.

### Fiction — the station of short announcements

Every hour the station bell was tested on a fresh list of trains. Its keeper could prove that half of the trains it announced arrived late. The new superintendent, disliking repetition, instructed him to ring only once for each train. The same late train had been on every list. The punctual trains, arriving from different towns, had appeared only once.

The keeper did not change the pitch. The superintendent asked him why the bell had become unreliable.

It had not changed its note, the keeper said. It had changed what it counted.
