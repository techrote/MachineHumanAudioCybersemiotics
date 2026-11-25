# The Renderer That Knows the Unspoken Context
## Exact hidden conditional dependence, preserved reconstruction and disclosure through a calibrated renderer

Refs #488 · 25 November 2026 · mathematical and synthetic-computational expedition. One ChatGPT GPT-6.2 author, self-review only. No independent scientific review, human data, operational privacy certification or priority claim.

## Contents

1. Excavation — identify the independence assumption across earlier work.
2. Model — distinguish the original, transmitted word, error pattern and received word.
3. Sharp theorem — derive the largest possible new binary group disclosure under exact proper-marginal calibration.
4. Invisible witness — preserve both full error histograms and authorized semantic recovery.
5. Direct finite qualification — compare actual conditional channel rows and target audits.
6. Exaptation — a factorial calibration contract, objections and falsification criteria.

## 1. Excavation

[Draft #478](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/77aa4b70aae14ab191e0beba944a72f5b43cb451/research/expeditions/dictionary-mishears-in-concert/README.md), §§2–5, extends the independent-bit model of #465 to arbitrary dependence among flips. Its decisive assumption is that the error pattern is independent of both transmitted word and original. This is explicitly stated and is NOT refuted here. The new question is whether that independence can be inferred from successful calibration.

[Draft #411](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/5140eb0d86b04dc6f4abc272dd6fdb77445f1ed9/research/expeditions/receipt-protects-wrong-secret/README.md), §§2–4, insists that protected targets and whole-state guessing must be specified separately. Its channel has no side channel. This experiment adds a context-conditioned renderer and tests a previously perfectly hidden group attribute.

[#45, multivariate acoustic mapping independence](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/45), Objective and non-duplication boundary, distinguishes measurable waveform dimensions from semantic independence. Its proposed human protocol and source reports are not empirical evidence for this construction. Accepted [X004 Quotient Guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md), Exact finite claim and Limitations, tests deterministic decision sufficiency, not stochastic independence. The [project foundation](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/docs/PROJECT_FOUNDATIONS.md), Proposed functional chain, distinguishes semantic message, rendering and interpretation. This result motivates an explicit information boundary between those stages.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866, refreshed before creating branch. Read AGENTS, RAG, programme, runbook, integrity, validation, foundation, X004 and the pinned #478 and #411 reports. Inspected first 100 open issue entries (including PR entries) and 100 open PRs, not exhaustive inventories. Inspected #476 issue/comments (none), #478 metadata and exact-head repository-integrity check (success), #449 and #317 PR descriptions and #481 scope. Targeted issue searches for source-dependent and renderer/parity returned five adjacent records and zero respectively; #45 and #49 bodies examined. Created #488, read complete new scope and empty comments, branched from verified main. All these expedition predecessors remain draft work, not accepted scientific findings. No external source was necessary for the elementary finite derivation below; no broader prior-art or novelty assessment is claimed.

## 2. Model (mathematical)

Let k>=2 binary transmission coordinates, L=2^k, original X=(i,s), with m even equally likely collision pairs i and sign s equally likely in {-1,+1}. The word W has conditional probability (1+s f_i(w))/L, where f_i is balanced and sign-valued. A pair intervention collapses the two originals (i,+), (i,-); authorized reconstruction knows i and observes Y. The observer sees Y only. The declared protected attribute H=h(i) assigns half the pairs to +1 and half to -1. Consequently W is uniform conditional on any pair and on H. Before noise, H and W are independent even though W is informative about s given i.

Let Y=W XOR E. Unlike #478, E may depend on X and W. Fix q in [0,1/2]. The strong calibration contract is: for every allowed (x,w) and every proper coordinate subset S of {1,...,k}, the conditional law of E_S is exactly independent Bernoulli(q) on S. This includes all (k-1)-dimensional marginals, much stronger than merely measuring pooled slot rates or pairwise correlations. No claim is made that any actual acoustic system meets this contract.

Write P0(e)=q^|e|(1-q)^(k-|e|), chi(e)=(-1)^|e|. Let u=min_{chi=+1} P0(e), v=min_{chi=-1} P0(e). Every conditional law satisfying the contract necessarily has form

    P(e|x,w)=P0(e)+a(x,w) chi(e),   -u<=a(x,w)<=v.

Proof: subtract the product distribution. Every marginal omitting one bit vanishes, so the difference changes sign across each edge of the binary cube. Starting at zero fixes its value everywhere by parity. Nonnegativity gives precisely the interval; normalization follows from the zero sum of chi. This also proves sufficiency. The two parity minima are q^k and q^(k-1)(1-q), in either order, so u+v=q^(k-1), including endpoints by continuity.

This characterization is elementary and exact. It imposes no practical implementation or adversary capability claim.

## 3. Sharp protected-attribute disclosure theorem (mathematical)

**Theorem.** Over all conditional error laws satisfying the contract, the largest possible optimal observer guessing probability for H is

    V_H^max = 1/2 + (2q)^(k-1)/2.

For q=0 the bound is chance; for q=1/2 it is one. This theorem concerns a balanced binary group attribute whose transmitted word is uniform within each attribute class, not arbitrary protected targets.

Proof: conditional on H=h, averaging over x,w gives

    P(Y=y|H=h)=1/L + b_h chi(y),
    b_h = E[a(X,W) chi(W)|H=h].

The product term becomes uniform because W is uniform within H; chi(y XOR w)=chi(y)chi(w). Each parity of W has probability one half within H. The interval for a implies |b_h|<=(u+v)/2. Consequently the total variation between the two output rows is (L/2)|b_+-b_-| <= L(u+v)/2. Equal-prior Bayes guessing is (1+TV)/2, giving the result.

Attainability: define c=(v-u)/2 and d=(u+v)/2. Set a(x,w)=c+d h(i)chi(w). Its only values are the interval endpoints. Then b_h=d h, and both conditional output rows have the form

    P(Y=y|H=h)=[1+h (2q)^(k-1) chi(y)]/L.

The group contrast lives in exactly one parity component. Every proper coordinate subset of Y remains uniform even conditional on H. The full word is necessary to see this particular contrast.

**Countercontrol:** If the renderer is source-blind, P(E|X,W)=P(E|W), even with arbitrary word dependence and no calibration constraint at all, H remains independent of Y. Summing the same uniform W law through the same stochastic kernel proves it directly. The new disclosure is not caused by word dependence alone: it requires additional source/context information beyond W. This is the boundary the renderer architecture must either enforce or test. Do not infer this capability in a real renderer merely from the counterexample.

## 4. The invisible witness (mathematical)

Take the centered reference error law P_c=P0+c chi. Compare a source-independent renderer using P_c to the context-conditioned law above. Both meet exactly the same proper-marginal contract.

For each original (i,s), the new received-word row differs from the centered reference by

    P_new(y|i,s)-P_c(y|i,s)=d h(i) chi(y).

This follows pointwise, without needing uniformity of W conditional on the individual original: the product of the two parity factors is always chi(y). Subtract the two sign rows within any pair i. The shift cancels identically. Hence every authorized conditional Bayes accuracy and every fixed sign decision's *average* success within its pair is unchanged. In particular this is not merely equality of the weakest pair or of an aggregate scalar. Individual-sign accuracy need not remain unchanged for arbitrary fixed decoders. No worst-original guarantee is claimed.

An additional condition makes the calibration failure more severe: suppose E[chi(W)|X=x]=0 for each original. This holds exactly when each f_i has zero full-degree Walsh coefficient. Then the COMPLETE error histogram conditional on X equals P_c, not merely its proper marginals. Furthermore the COMPLETE error histogram conditional on W equals P_c because H and W are independent. The original-word joint law is unchanged. Therefore all three two-variable marginals of (X,W,E) agree exactly between the reference and new channels, yet the (H,Y) joint law differs. The aggregate received-word histogram is also unchanged. This is a three-variable interaction invisible in separate source-conditional and word-conditional error audits.

For k=3 use the #465/#478 dictionary masks [27,53,71,141], bit w selecting sign +. Every row is balanced and has zero full-degree coefficient. For larger odd k append k-3 singleton rows on the additional coordinates to obtain m=k+1 even; this preserves exactly one representative per antipodal class and all required parity balances. The centered reference's actual received-word rows also equal those of the ordinary independent product noise P0 for these dictionaries: their difference is c E[chi(W)|X]chi(y)=0.

Do not confuse the centered full error histogram with the product histogram: they generally differ. The stronger invisibility comparison uses the same centered reference on both sides. An audit explicitly requiring the entire product law per original and per word could reject BOTH; the two-way margins cannot tell the centered and context-conditioned cases apart. The proper-subset conditional contract is satisfied even relative to the product law.

At q=1/2 the constructed disclosure becomes perfect while authorized pair recovery falls to chance in the tested low-degree dictionary. This endpoint is not perfect utility plus perfect disclosure; the moderate-noise examples are the relevant simultaneous-utility countercontrols.

## 5. Direct finite qualification (synthetic computation)

The following exact rational results (display rounded) use four pairs, three slots and the nonlinear witness. The target H is the half-of-pairs attribute specified before observing the output. The last two columns exhaust all 70 balanced binary targets on eight originals, not adaptive posterior-selected targets.

| q | Authorized worst-pair success, both | H guessing, centered | H guessing, context-conditioned | Worst balanced target, centered | Worst balanced target, context-conditioned |
|---:|---:|---:|---:|---:|---:|
| 0 | 100% | 50% | 50% | 68.75% | 68.75% |
| 0.10 | 86% | 50% | 52% | 65% | 65% |
| 0.25 | 68.75% | 50% | 62.5% | 59.375% | 62.5% |
| 1/3 | 61.1111% | 50% | 72.2222% | 56.25% | 72.2222% |
| 0.50 | 50% | 50% | 100% | 50% | 100% |

At q=.10 even the exhaustive worst-target scalar remains identical while a specifically hidden attribute becomes informative. This is a finite negative control, not a general equality theorem for the scalar.

Run `node lab.js`. The lab directly sums conditional output rows from transmitted words and error vectors, checks every maximal proper subset of the two endpoint laws and the centered law, checks source-conditional and word-conditional complete error histograms, verifies exact pair-contrast equality at every y, and checks the sharp group contrast. An independent enumeration of the 256 endpoint assignments per dimension-three case checks the bound on b; real intermediate coefficients lie in the same box. Fifteen cases span k=3,5,7 and q=0,1/10,1/4,1/3,1/2. Integer counts fit within Number's exact range; only reported ratios and the tolerance-checked probability formula are floating-point. V8 development execution passed: 8,100 proper marginal cells; 687,360 conditional channel summands; 12,480 source-error cells; 87,360 word-error cells; 6,240 pair-contrast cells; 840 group-output cells; 1,280 endpoint assignments; 700 balanced-target audits. These overlap and are not independent scientific observations. Native checkout/full repository validation, independent mathematical critique and empirical/acoustic qualification remain outstanding. No shared canonical records changed.

## 6. Exaptation and falsification

**Design hypothesis:** in a context-adaptive auditory system, renderer qualification should include a declared information boundary: which context fields are permitted to reach the rendering stage beyond the abstract message? If none, enforce and inspect that architecture before relying on a source-blind Markov model. If additional context is permitted, treat the renderer as part of the communication channel rather than as a neutral acoustic conversion.

A proposed synthetic factorial audit holds the transmitted word fixed, varies allowed source/context fields, and compares full received-word distributions. Separately hold source fixed and vary word. Estimate joint conditional confusion matrices rather than independently pooled confusion histograms, report a protected target before evaluation, and retain per-pair utility and target disclosure simultaneously. For continuous audio, determine whether a bit-error abstraction is even adequate; a waveform, duration or timing difference can be an unmodeled observation. Do not use real protected personal attributes or participants for this synthetic apparatus.

Counterarguments: context-dependent rendering can be intentional and desirable, for example when the context is explicitly meant to be conveyed. Preserving independence then conflicts with that communicative objective. A design that enforces the Markov boundary may sacrifice legitimate adaptive output. The result is not a prohibition on adaptive rendering. Also, exhaustive factorial calibration can be expensive; direct architecture restrictions may be preferable to a purely statistical certificate. No claim is made that finite samples can establish exact independence.

Revision criteria: a calibrated conditional distribution outside the one-dimensional parity interval; a larger group contrast under the stated uniformity contract; a failure of the pointwise pair-contrast cancellation; or an exact counterexample to the source-blind control. Any of these defeats the relevant theorem. Actual empirical applicability requires independent evidence about the real renderer's observation and context pathways, with proper authorization and no claim-class promotion.

Fictional miniature (not evidence): a conductor plays the same abstract score to two rooms. Both rooms report the same note errors, even when sorted by the player or by the score. A listener can nevertheless tell which room the sound came from. The archivist asks whether the room was ever meant to be part of the message.
