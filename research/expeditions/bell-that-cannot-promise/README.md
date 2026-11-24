# The Bell That Cannot Promise
## Strategic signalling, the incentive-compatible alphabet, and the price of a truthful note

**Refs #242 · 24 November 2026 · original finite mathematical model, synthetic computation and interpretive writing.** No human data, validated auditory performance, Track E/G finding, established novelty or accepted production requirement.

### The disagreement

The [sediment atlas](../intellectual-sediment/README.md) distinguishes decision sufficiency from universal state preservation. Selective clarification (#201 / PR #202) asks how much information a decision actually needs. The Alphabet of Tomorrow (#209 / PR #210) asks what must survive for future questions. The Warning That Makes Itself False (#226 / PR #227) asks whether the message changes the forecast target. The Examiner of Silences (#234 / PR #235) asks where declined cases go. The Museum of Unasked Questions (#236 / PR #237) compares information structures across decisions. The affect-feedback tangent (#177) raises accommodation and correction failure.

There is another independent failure mode. Even a perfectly identifiable sign, transmitted without distortion and sufficient for a particular decision, may fail because the mechanism generating it benefits from a different decision. A message's nominal mapping is not an incentive contract. This observation does **not** establish that models have private intentions or intrinsic desires. The sender's loss below is a stipulated optimization objective, which might describe an institutional metric or externally programmed selection rule.

Main observed at 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity and validation, main X004 and X005 and Migrating Timbre; read the actual draft reports #227 and #235, live open issues/PRs, recent PR metadata including #241 and branch listing. Search for cheap talk returned no matching issues; absence of a search result is not a novelty proof. Issue #242 created; comments empty at creation. Prior draft work remains noncanonical. New paths only here; no edits to any shared registry, tests, frozen protocol, manuscripts, programme or human gates.

### A deliberately small signalling game

Let t be uniformly distributed on {0,...,n-1}. The sender observes t, emits one costless unverifiable message, and the receiver chooses a real action a. Receiver loss is (a-t)^2; sender loss is (a-t-b)^2 for a known fixed bias b. The game, finite prior and loss functions are common knowledge. Messages do not alter t. No audit or repetition initially. Consider deterministic sender strategies and receiver best responses; any unused messages can be assigned the same belief/action as an existing message, so cannot add profitable deviations. We study induced distinct actions, not distinct spellings of messages.

The receiver's unique best action for a used label is the conditional mean. A sender chooses whichever of those actions is closest to t+b. Consequently distinct induced actions must be selected monotonically in t: for a<c the difference of squared losses is affine and strictly monotone in t; optimal action a lies on one side of their midpoint and c on the other. A tie occurs at a single t, so a deterministic assignment remains monotone. If different labels yield equal conditional means, merge those labels; the merged mean remains unchanged and deviations are unaffected. Thus the induced distinct actions can be represented by nonempty contiguous state blocks of integer lengths l_1,...,l_k summing to n. This equivalence is for actions, not every observable label or every strategy. In particular the noncontiguous blocks {0,3}, {1,2} both produce 1.5 and are a valid one-action example, not two-action communication.

For adjacent blocks of lengths l,r, let the final state in the left block be j. The actions are j-(l-1)/2 and j+(r+1)/2. Their midpoint is j+1/2+(r-l)/4. The left endpoint type j must not prefer the right action, and the right endpoint j+1 must not prefer the left. Thus

    j+b <= j+1/2+(r-l)/4 <= j+1+b
    equivalently |r-l-4b| <= 2.

This condition is both necessary and sufficient for all on-path deviations: nearest-action regions of a sorted menu are bounded by adjacent midpoints, and t+b is monotone. Equality permits weak best responses. It does not make truth strictly preferable.

### A sharp bound: alphabet capacity versus credible resolution

By reflection take b>=0. Define d=max(0,ceil(4b-2)). When d>0, each block grows by at least d, and the minimum size of k blocks is

    n_min(k)=k+d*k*(k-1)/2.

When d=0, n>=k trivially. Every feasible k satisfying this bound is attainable. Start with lengths 1,1+d,...,1+(k-1)d. Distribute excess n-n_min(k) evenly across all blocks, then add one to the final remainder blocks. Each adjacent difference is d or d+1 (or just 0 or 1 if d=0); both obey the boundary interval [4b-2,4b+2]. Reverse the list for negative b. Therefore the maximum number of distinct equilibrium actions is exactly the largest positive k satisfying n_min(k)<=n with d=max(0,ceil(4|b|-2)). This constructive proof is local to the discrete model, not a general theorem for games.

If n>1 full separation exists iff |b|<=1/2, with strict preference for truthful labels when |b|<1/2 (at equality some deviations tie). Pooling always exists. This is a striking discontinuity: an arbitrarily small increase above half a state step forces d>=1, so at n=16 the maximum drops from 16 to 5. This is a **lattice effect**, not a universal threshold for trust or a prediction about human behaviour. As state resolution changes, the same physical bias must be rescaled. For fixed positive normalized bias b/(n-1), the quadratic growth term can keep k bounded as n grows; the finite grid formula, not an analogy to a bit-rate law, controls the exact result.

Here are exact sample cases (uniform prior over 16 integer states). B=4b is used by the integer laboratory. Receiver loss is the mean of squared errors, not a normalized accuracy or utility.

| b (state units) | Maximum induced actions | One receiver-optimal block-length vector in exhaustive census | Receiver loss (exact) |
| ---: | ---: | --- | ---: |
| 0 | 16 | sixteen 1s | 0 |
| 0.5 | 16 | sixteen 1s (weak equilibrium) | 0 |
| 0.75 | 5 | 1,2,3,4,6 | 300/192 |
| 1 | 4 | 1,3,5,7 | 480/192 |
| 1.5 | 3 | 1,5,10 | 1110/192 |
| 2.5 | 2 | 4,12 | 1776/192 |
| 4 | 2 | 1,15 (weak boundary) | 3360/192 |
| 4.25 | 1 | 16 | 4080/192 |

A block of l consecutive integers contributes (l^3-l)/12 to total squared error (sum of squared deviations around its mean). Divide the sum by n. The Python DP evaluates the minimum receiver loss separately at each feasible action count. For all 2,600 tested (n,B) pairs it found no strict improvement at a lower action count compared with the best maximum-count partition. This is an **observed finite census**, not a proved global welfare theorem, not a claim of unique equilibrium, and not an assertion that higher resolution is intrinsically beneficial. Even when fully separating equilibrium exists, pooling remains an equilibrium. An equilibrium existence proof cannot guarantee coordination on a particular equilibrium.

### The audit that changes the game

Suppose instead there is a truthful-label mechanism with n labels, receiver action equal to its numerical label, and an independently verifiable true state after the fact. A false label incurs an expected extra sender loss C>=0, independent of type and false label; truthful reports incur none. This can be modeled as detection probability q times a fixed penalty F only if detection really is conditionally constant and correct, and enforcement credible. Assume any label may be reported and costs are in sender squared-loss units.

A false label j=t+h improves the unpenalized sender loss by

    G(h)=b^2-(h-b)^2=2bh-h^2.

The necessary and sufficient expected penalty for weak truthful incentive compatibility at every t is

    C >= max_{integer h, |h|<=n-1} (2bh-h^2).

Every h in this range is realizable by some type and false report. The maximum occurs at the integer nearest to b after clamping to the feasible range (tie either), and h=0 yields zero. The inequality is strict against every false label if C strictly exceeds the maximum; for n=1 there are no false labels. For b=0.75, n=16 the gain is 0.5 for h=1. A penalty of 0.5 makes truth weakly compatible; a smaller one cannot stabilize it in this model. If q=0 no finite F can achieve a positive C. This is a changed game, not a proof that adding a checksum or metadata restores honesty. If the receiver changes policy or the audit is biased, strategically avoidable, noisy, or itself expensive, the model must be replaced.

The most important contrary cases are inexpensive independent verification, a sender with aligned loss, and a receiver who may choose to ignore or override reports. Truth is not impossible in general. Nor does perfect incentive compatibility establish epistemic correctness: a sensor could be wrong and a truthful report of that observation could still mislead. A mechanism can also be incentive-compatible for the wrong target. Separating observation quality, willingness to report, interpretation, and action remains useful.

### Cross-domain exaptation: a sign contract that includes its generator

A proposed synthetic design-review record, not a mandated schema:

- **Observable mapping:** what label is emitted for a stipulated state; model and version.
- **Decision mapping:** which action the receiver selects and its loss, with scope and confidence.
- **Generator objective:** a documented optimization criterion or selection rule; unknown if not established.
- **Deviation witness:** an alternate label and what incentive difference it induces under stated assumptions.
- **Verification and remedy:** independent evidence availability, audit reliability, enforcement, cost, and alternatives.
- **Fallback:** pooling, independent measurement, uncertainty bounds, or abstention; costs must not disappear from the denominator.
- **Claim class:** formal toy result, project preference, empirical finding, or untested design hypothesis.

Example application: a synthesizer patch browser that chooses which acoustic preview to emit to maximize play time might be assessed for whether that selection misrepresents useful patch properties. This is a candidate evaluation question, not evidence of deception or a claim about a particular synthesizer. A compiler that deterministically reports a verified quantity does not need a game-theoretic audit merely because its output is a sound. A non-strategic channel with transmission errors needs communication engineering rather than incentive redesign. If an objective is unobservable, refuse to assign b from apparent personality or infer motive from tone.

The conflict with the earlier quotient guard is not a contradiction of its theorem. A quotient can preserve every declared action-relevant distinction under a compliant encoder while a noncompliant encoder has no reason to use it. Equally, adding metadata increases representational capacity without resolving strategic credibility. MHAC needs the distinction only when its actual mechanism warrants it; the research programme should not acquire a universal game-theory layer on the strength of this toy.

### Computational qualification and independent-reading limits

Run from this directory: `node lab.js` and `python3 crosscheck.py`. No external libraries. The JavaScript function bodies executed in V8 before serializing to the committed file; the Python code was executed locally as a separate implementation. Both have one AI author. No external reviewer or participant validation.

| Check | Actual successful comparisons |
| --- | ---: |
| All ordered compositions, n=1..14, B=-24..24; boundary vs direct deviation oracle | 802,767 |
| Maximal action counts vs closed form | 686 |
| Constructive maximal witnesses | 686 |
| Arbitrary set partitions, n=1..8, B=-16..16; direct rational-mean deviation checks | 174,735 |
| Arbitrary-partition maxima vs closed form | 264 |
| Audit threshold vs every state/report pair, n=1..60, B=-80..80 | 9,660 |
| Named controls / invalid input refusals | 11 / 5 |
| Python DP, n=1..40, B=-32..32 | 2,600 |

The direct deviation oracle cross-multiplies squared integer numerators for rational means; its enumerated range stays within exact JavaScript integer representation. The finite tests cover signed quarter-step bias and tie cases, not arbitrary real bias; the mathematical derivation covers arbitrary real b in the stated ideal model. DP separately computes the optimum at each block count and verifies all counts up to the maximum exist. At n=16 both independently implemented searches give the same frontier rows. This is same-author cross-checking, not independent review. Full clean-checkout repository CI and review have not been claimed; no changes to its shared test entrypoint.

### Source-critical boundary

- Vincent P. Crawford and Joel Sobel, *Strategic Information Transmission*, Econometrica 50(6), 1431–1451 (1982), DOI [10.2307/1913390](https://doi.org/10.2307/1913390). Read the author-uploaded article abstract visible at [ResearchGate](https://www.researchgate.net/publication/4895225_Strategic_Information_Transmission), not the complete original article or proof. The abstract establishes the established partition-equilibrium result and alignment theme. No mathematical-priority assertion for this discrete variant.
- Haruki Kono and Michihiro Kandori, *Corrigendum to Crawford and Sobel (1982) “Strategic Information Transmission”*, 2021, DOI [10.3982/ECTA17617](https://doi.org/10.3982/ECTA17617). Read publisher HTML abstract and introduction, through the explanation of the original proof's discontinuity error; embedded equation images not reconstructed. The authors retain the theorem while correcting part of its proof. This cautions against importing an attractive continuous existence claim without checking assumptions. Our discrete existence proof uses an explicit integer construction, not their continuity argument. Did not independently verify their full corrected proof.
- Chirantan Ganguly and Indrajit Ray, *Simple Mediation in a Cheap-Talk Game*, Games 14(3), 47 (2023), DOI [10.3390/g14030047](https://doi.org/10.3390/g14030047). Read publisher HTML abstract, introduction and §2.1 visible model description. Their stated limited result on simple mediation is a contrary pressure against claiming an unmediated partition bound is a universal capacity bound; the introduction reports other mediation/noise results. Did not verify all proofs or cited results. Our audit mechanism is different from their mediator and has not been compared for welfare.

These are theoretical sources, not listener data. Access date 2026-11-24. No restricted source files copied or redistributed. Search was targeted, not systematic. One ChatGPT agent authored all original text, formal derivations, code and computational self-review.

### Fiction: The bell that could play every note

*Original speculative vignette; no evidence claim.*

A town commissioned a bell that could play one note for every height of its reservoir. Its pitch was exact, its bearings silent, its scale mathematically complete. The people gave its operator a prize each evening proportional to the quantity of water they believed remained.

The bell did not become inaccurate through rust. Nor was the town unable to distinguish its notes. The operator discovered that certain intermediate pitches could never be trusted if a brighter note could earn the prize. The people learned this too. They began interpreting some neighbouring notes as the same broad interval.

An engineer added more bells. The intervals remained.

A different engineer proposed a separate ruler, publicly visible from the square. A third proposed abolishing the prize. A fourth insisted that the bell's perfect construction had already fulfilled the commission.

Years later, the museum displayed all four proposals without declaring a winner. On the little placard beneath the bell, the curator had written: **Its range was sixteen notes. Its promise was a different quantity.**
