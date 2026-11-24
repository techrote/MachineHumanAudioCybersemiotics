# The Examiner of Silences
## A paired audit of abstention, fallback and the invisible denominator

**Refs #234 · 24 November 2026 · exploratory mathematical and interpretive report.** Not accepted Track E/G evidence, a listening experiment, a production warning rule, or a claim of mathematical priority.

### The conflict

The intellectual sediment atlas (#184) identifies the recurring refusal to conflate epistemic quantities; its quotient guard asks when a representation preserves a decision. Selective clarification (#201, draft #202) pushes back: questions cost something, and state identification is not always necessary for action. The performative warning (#226, draft #227) complicates the target of evaluation itself. The first auditory tangent (#30) separates missed responses from the stages that could cause them. These are different interventions, not equivalent theories.

This expedition challenges an attractive compromise: **speak only when sufficiently certain**. Silence may eliminate an erroneous emitted statement, or it may merely transfer responsibility for the same case to an unmeasured fallback. Neither conclusion follows from the issued-message accuracy alone. Indeed, abstention can be valuable precisely when fallback is good. The objection is to denominator substitution, not to abstention.

Reconciliation: main observed at 495a98ca12bae467a507031f04931aa4254b1866; read AGENTS, RAG, programme, runbook and the X004, Migrating Timbre and Chiastic Trap reports. Read #30, #31, #201, #226, #232 and the PR metadata for #202, #227, #233. The recent open expedition index includes #218 joint disclosure, #220 consensus calibration, #228 scalar distortion, #230 source attribution and #232 robust reset. None of those issue titles establishes an accepted result. This package does not solve classification calibration, optimal clarification, source attribution, reset or performative outcome changes. It isolates **comparison of selective policies under incomplete fallback-cost information**, with a fixed, matched roster. No shared paths or other branches modified.

### A finite model and a sharp difference bound

Take N positive integer cases, observed under both abstract policies A and B in a stipulated static benchmark. Each entry is C (correct issued prediction), W (wrong issued prediction), or S (abstention). Set the loss of C to 0 and W to 1. On case i, assign S a fallback loss z_i in [0,1], the **same hypothetical loss for both policies**. This is an assumption, not an observed fact: it presupposes comparable fallback and no policy interference, workload coupling, different fallback semantics, or changed target. Correct speech can still be operationally harmful outside this toy loss model.

Define w = W_A - W_B (difference in wrong counts); P = cases where A alone abstains; M = cases where B alone abstains; p and m their cardinalities; r = N-p-m. The difference of mean losses, A minus B, is

    N Δ = w + sum(i in P) z_i - sum(i in M) z_i.

Cases of joint abstention cancel exactly because their fallback loss is common. Cases of joint delivery contribute only to w. If there is no further restriction on z, the **sharp** interval is

    (w-m)/N <= Δ <= (w+p)/N.

For the minimum, put loss 1 on M and 0 on P; reverse these assignments for the maximum. Intermediate values follow by convexity of the box and linearity. If all z are fixed the difference is a number, not an interval; if both policies abstain on the same cases, it is w/N even when their absolute losses remain unidentified. With zero issued cases, conditional issued accuracy is undefined, not 100%.

Strict dominance under every admitted fallback assignment occurs if the upper endpoint is negative (A better) or lower endpoint positive (B better). A zero endpoint supports weak dominance only. An interval containing both signs certifies that a ranking can be reversed without changing the reported benchmark predictions. These are finite identification bounds, not statistical confidence intervals.

#### A global budget changes the answer

Suppose additional independent knowledge fixes the total hypothetical fallback loss across **all N cases**, not just actual abstentions, at T in [0,N]. Let all losses be multiples of 1/D, and write t=DT. The attainable extrema for the numerator N D Δ are

    lower = D w - min(t,D m) + max(0,t-D(m+r))
    upper = D w + min(t,D p) - max(0,t-D(p+r)).

For the lower bound, allocate the t units first to M, then neutral cases, then P. Each unit allocated to M reduces the objective by one, each to a neutral slot changes nothing, each to P increases it by one. An exchange from a higher coefficient to a lower coefficient with spare capacity never raises the objective; the greedy order thus gives an optimum, and capacities are integral. Reverse the order for the maximum. Both assignments exist for every admissible t, including endpoints. For continuous costs the identical argument works without integer units. Neutral slots include joint delivery: the global budget requires a hypothetical fallback on those cases too; a measured sum over just the cases actually deferred cannot be substituted for it.

#### If the evaluation discarded the pairing

Let a and b be the abstention counts of A and B and let k be the number of joint abstentions. Then p=a-k, m=b-k. Feasible k ranges from max(0,a+b-N) to min(a,b), by elementary set cardinality. Every such overlap is realizable; C/W counts can independently be assigned within each policy's delivered set. No further compatibility restrictions on error locations have been imposed.

Without a pairing, the union of admissible loss ranges has its extreme endpoints at k_min=max(0,a+b-N). This is immediate in the unconstrained case, since decreasing k increases both p and m. It also holds under the total budget: decreasing k by one replaces two neutral coefficients by one +1 and one -1; for any old allocation to the two slots, assign the larger value to the +1 coefficient for a weakly larger result, or to the -1 coefficient for a weakly smaller result. The sum of the two allocations remains unchanged. Hence the extrema cannot contract as overlap decreases. Apply the previous bound using p=a-k_min, m=b-k_min. The endpoints are attainable for some matched roster consistent with the published marginals. They need not be the actual roster's endpoints. No causal independence or probability model is needed.

This gives a precise value of retaining pairing: if actual overlap exceeds minimum overlap by d, the unbudgeted range width shrinks by 2d/N. Keeping a privacy-compatible aggregate overlap count (plus totals) suffices for this *particular* bound; raw identities, raw audio and pairwise correctness labels need not be retained for that calculation. It does not suffice for arbitrary subgroup analyses, temporal effects or future questions. This is a concrete disagreement with indiscriminate archival retention (#209): the sufficient statistic depends on the agreed query family.

### Counterexamples

Ten equally weighted cases, A correct on 2 and silent on 8; B correct on 8, wrong on 1 and silent on 1. Let B's silence coincide with one of A's. The lab uses this exact fixture.

| Metric | A | B |
| --- | ---: | ---: |
| Issued accuracy | 100% | 8/9 |
| Coverage | 20% | 90% |
| Mean loss if every fallback costs 0 | 0 | 0.1 |
| Mean loss if every fallback costs 1 | 0.8 | 0.2 |

With constant fallback cost c, Δ=(-1+7c)/10. The crossover is c=1/7; for heterogeneous unconstrained common fallback the sharp interval is [-0.1,0.6]. There is nothing paradoxical about this once the loss is specified: A's better issued accuracy measures a different target.

For two cases, compare [C,S] with [C,S], and compare [C,S] with [S,C]. All four policies have 50% coverage and 100% issued accuracy. In the first pairing, Δ is identically zero; in the second, Δ=(z_2-z_1)/2 in [-0.5,0.5]. Thus even identical marginal accuracy and coverage cannot recover the comparative uncertainty. The latter example's endpoints are achieved by setting one fallback loss to 0 and the other to 1. A known zero total fallback loss collapses both intervals to zero; this is a negative control against claiming pairing always matters.

Further controls and cautions: (i) full coverage reduces the interval to the ordinary wrong-count difference; (ii) matched silence cancels only under a common fallback; (iii) abstention may be strictly optimal at low fallback loss; (iv) bounds cannot identify a hypothetical forced prediction when none is defined; (v) unequal case weights or distinct wrong-message harms require another loss model; (vi) a missing log entry is not necessarily an intentional abstention; (vii) changing fallback queue capacity can invalidate even the static roster model; (viii) a common fallback under a counterfactual deployment may be untestable; (ix) neither scalar loss nor its interval settles distributional fairness; (x) no claimed observed human accuracy, costs, or decision thresholds.

### Literature and bounded interpretation

- El-Yaniv, R. and Wiener, Y. (2010), *On the Foundations of Noise-free Selective Classification*, JMLR 11:1605–1641, [publisher abstract](https://jmlr.csail.mit.edu/papers/v11/el-yaniv10a.html), read 24 November 2026. The abstract introduces the accuracy/coverage tradeoff for classifiers with a reject option. We do not reproduce their noise-free results or claim novelty for this framing.
- Manski, C. F. (2005), *Partial identification with missing data: concepts and findings*, IJAR 39:151–165, [DOI](https://doi.org/10.1016/j.ijar.2004.10.006). Publisher abstract as surfaced by search examined 24 November 2026; direct DOI follow returned HTTP 403. The abstract motivates considering identification regions before imposing assumptions that give point estimates. This is a methodological antecedent only; our unknown fallback cost is not literally the missing outcome distribution in his paper. No full text read.
- Jones, E., Sagawa, S., Koh, P. W., Kumar, A., Liang, P. (2020 preprint), *Selective Classification Can Magnify Disparities Across Groups*, [arXiv:2010.14134](https://arxiv.org/abs/2010.14134), abstract and accessible text §§1, 3 (metrics), and opening of §4 read 24 November 2026. The authors report average improvements alongside possible worsening of particular groups. This is a contrary empirical result in their datasets, not evidence about auditory warnings or our fallback model. No full-text reconstruction, figure inspection, or appraisal was conducted.

These sources concern adjacent questions and are scouting leads, not a new admissible systematic-review batch. The small algebra here is original to this expedition in exposition and application, not claimed as new mathematics. It is entirely compatible with ordinary decision theory, bounded linear optimization and partial identification. No special cybersemiotic doctrine is necessary to derive it; that negative result should survive the remove-Brier test.

### Exaptation: the missing-case ledger

A candidate evaluation artifact, not an approved interface specification: preserve the evaluation roster version, case count, each policy's C/W/S totals, explicit distinction between unobserved and intentional silence, pairing/overlap if lawfully available, definitions of correct and wrong, fallback policy identity, admissible cost bounds, and separate evidence for any budget restriction. Report issued accuracy with its denominator, coverage, and a conditional comparison interval. If policy-specific fallbacks differ, do not use the shared-loss cancellation.

This is relevant beyond audio: agent deferral, procedural art acceptance, selective classifiers, reviewer queues, batch simulations. A silence is not necessarily a sign: it may be a missing event, an intentional action, an unavailable observation, or an aesthetic rest. A musical rest can be intentional without requiring a downstream repair. An institution that scores only spoken cases can improve the appearance of correctness while externalizing hard cases to an unobserved process. That is an interpretive possibility, not an attribution of motive to a real institution.

A leaner alternative deserves priority: instead of implementing a new telemetry subsystem, first disclose the denominator and stop publishing a comparative rank that the admissible interval does not identify. The paired overlap statistic is optional where privacy or retention costs exceed the benefit.

### Reproduction and limits

Run Node.js with no packages:

    node research/expeditions/examiner-of-silences/lab.js

The dependency-free JS function bodies were executed in a V8 isolate on 24 November 2026 before being serialized into the committed source. The oracle directly enumerates C/W/S arrays for each policy on 1 through 4 cases and all fallback assignments from {0,1/2,1}; it computes losses separately then groups their extrema by total budget or marginal counts. It does not call the formula when building those extrema. The formula and oracle share a single AI author; this is not independent human or scholarly review. Local clean Node checkout and repository CI are not asserted.

Actual comparison counts:

| Test family | Count |
| --- | ---: |
| Paired unconstrained bounds | 7,380 |
| Direct assignment evaluations | 551,880 |
| Paired fixed-budget bounds | 64,584 |
| Aggregate-only fixed-budget bounds | 2,932 |
| Aggregate-only unconstrained bounds | 370 |
| Input rejection controls | 5 |

All passed, plus four named range assertions. The roster census is small and exhaustive within its stated grid, not a prevalence estimate. Proof handles arbitrary N under the assumptions; the grid checks are corroboration and implementation qualification, not a replacement for the proof. The primitive bounds routine accepts aggregate coefficient summaries, not proof that those summaries were observed. Safe-integer checks protect the intended arithmetic; large experiments may need a different implementation.

No new dependencies, participant data, claims of listening performance, protocol amendments, registry edits or production control. Review and exact-head checks remain pending. Refs #234, not Closes.

### Fictional afterword — The Conservatory of Unplayed Examinations

In the conservatory, every instrument was marked only for notes that it chose to play. The cello performed two perfectly judged notes and received full marks. The clarinet attempted nine and missed one. The cello was promoted to first chair.

The clerk who maintained the tally was not dishonest. The rules had been obeyed. Yet behind the curtain a second musician attempted all the notes the cello had declined, and nobody had thought to put a chair, a name, or a column for this musician on the examiner's form.

One year the second musician was magnificent. The cello's silence made the ensemble better. The next year the musician was tired, and the same silence made it worse.

The clerk added a column to the ledger. It was not called error. It was called *who played the rest?*

The fiction is an original artistic interpretation of the model, not an empirical description of human musicians or a claim that all musical silence transfers work.
