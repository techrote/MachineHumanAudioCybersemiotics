# The Museum of Unasked Questions

**Refs #236 · 24 November 2026 · bounded mathematical expedition, original interpretive and acoustic work.**
Base main: 495a98ca12bae467a507031f04931aa4254b1866. One ChatGPT research agent; no independent human review, no participant observations, no priority claim. This is not an accepted Track E/G finding or an audio-engine requirement.

## Contents

1. The anomaly — two instruments that agree on every restricted world.
2. The exact laboratory — subset-reporting experiments and reversible restriction.
3. The missing dimension — sharp parity obstruction and its converse.
4. Decision reversals — exact shortlist gaps and a stronger impossibility.
5. Interpretive archaeology — meaning, contextuality and decision contracts.
6. Verification — actual exhaustive execution, controls and limits.
7. An original acoustic construction — a chord whose usefulness depends on the question.
8. Sources, limitations and disposition — source boundaries and next falsifiers.

## 1. The anomaly

A museum possesses three possible locations for an artefact: A, B and C. Two instruments emit perfectly truthful reports of the form “it is in one of these rooms.” Neither instrument promises to know the room precisely. The first names an odd-sized set of possible rooms, the second an even-sized set. Given the true location, every allowed report containing that location is equally likely.

For example, if the true location is A:

| Instrument O | Instrument E |
| --- | --- |
| A (probability 1/2) | AB (probability 1/2) |
| ABC (probability 1/2) | AC (probability 1/2) |

Suppose a preliminary briefing eliminates C. Both instruments now tell the same statistical story: if A is true, the remaining candidates are A or AB with equal probability; if B is true, they are B or AB with equal probability. In fact each instrument can simulate the other's complete raw output by a state-independent randomization on this restricted support. The same is true for every other two-room support and every singleton.

But when all three rooms are genuinely possible, O and E are not interchangeable:

| Objective, uniform prior | O | E |
| --- | ---: | ---: |
| Name the correct room, one attempt | 2/3 | 1/2 |
| Provide a two-room shortlist containing the artefact | 5/6 | 1 |

There is no single winner. The instrument preferred by the exact-identification problem loses the shortlist problem. Both are operating on the same state population and with truthful reports, no receiver mistakes, no deadlines and no physical noise.

The motivating seam is between the scope of an experiment and the scope of a statement about informativeness. This is not another demonstration of signal collision: the complete messages are observed and have explicit, known meanings.

## 2. The exact laboratory

Let the state i belong to [n]={1,...,n}, and the output S be a nonempty subset containing i. A symmetric subset-reporting experiment is specified by nonnegative weights c_1,...,c_n with

    sum_{k=1}^n binom(n-1,k-1)c_k = 1.

The probability of output S given i is c_|S| if i belongs to S, and zero otherwise. We use actual probabilities in this derivation; the code uses nonnegative integer weights divided by their exact row denominator. The experiment reports no false exclusions. This does not imply a real-world diagnostic channel is truthful.

Restrict the possible states to a fixed nonempty set T of size r. This is a change of the state support, not conditioning the output on passing some acceptance filter. The parties know T. For any output S with positive probability, U=S∩T is nonempty. The conditional probability of observing U given i in U is

    d_j = sum_{h=0}^{n-r} binom(n-r,h)c_{j+h},    j=|U|.

Reason: each choice of h external elements defines one S with the same intersection U. If i is not in U, the probability is zero.

The projection S→U is deterministic. It is also reversible *as a statistical experiment on T*. Given U, choose an outside subset B⊆[n]\\T with probability c_(j+|B|)/d_j and output U∪B. For every positive-probability U these weights sum to one. Zero-probability U needs no prescribed behavior beyond an arbitrary normalized kernel. This randomization is independent of the unknown true i. Its composition with the projected experiment reproduces all original conditional output probabilities. Thus preserving the external labels is unnecessary for any decision whose true state is confined to T, under these assumptions.

This is Blackwell equivalence (mutual state-independent stochastic simulation), not literal reconstruction of an individual discarded output. A sampled reinflation is not the original historical event. Nor is T permitted to vary secretly with the true state: it is common fixed context, not an additional unmodeled observation.

**Converse inside the symmetric family.** Suppose two channels restricted to T are Blackwell equivalent. Under the uniform prior on T, the posterior after U is uniform on U. Distinct nonempty U yield distinct posterior vectors. If an experiment is garbled, the garbled posterior is the conditional expectation of the original posterior given the garbled signal. By the conditional variance identity, the expected squared Euclidean norm of the posterior cannot increase. Mutual garbling implies equality in both directions; equality forces the original posterior to equal the garbled posterior almost surely under the corresponding coupling. Consequently the two posterior laws coincide. The mass of each U is |U|d_|U|/r, so all the projected weights d_j must coincide. This proves necessity as well as sufficiency. No black-box optimization solver is required for this restricted family.

## 3. The missing dimension

Let n≥2. Define O and E by assigning weight 1/2^(n-2) to each allowable odd-sized or even-sized subset respectively, and zero to the opposite parity. For every true i there are 2^(n-2) subsets containing i of each parity: choose a subset of the n−1 other elements and select the appropriate parity. The row sums are one.

For every proper T, at least one external element remains. For each U, exactly half of the outside subsets give odd total cardinality and half give even total cardinality. Thus both projected profiles are identical:

    d_j = 2^(1-r) for every j in 1..r.

Every nonempty U containing i is equally likely, and the reverse randomization in Section 2 exists in both directions. This proves equivalence for **all proper supports, all priors on those supports, all finite action sets and all finite payoff matrices**. It is much stronger than equal pairwise classification accuracy.

A second result explains why the parity construction is not an arbitrary trick. Within this symmetric subset family, consider any two probability profiles c and e. Equivalence on all (n−1)-state supports is necessary and sufficient for equivalence on all proper supports. On an (n−1)-state support,

    c_j + c_(j+1) = e_j + e_(j+1)  (j=1,...,n−1).

Writing Δ_j=c_j−e_j, these equations force

    Δ_j = (-1)^(j−1) δ,    δ=Δ_1.

The row normalization is automatically unchanged by this perturbation because the alternating binomial sum is zero. All lower restrictions also coincide, either by repeated projection or direct binomial expansion. The space of possible hidden differences therefore has exactly one linear dimension; feasible differences are cut down by nonnegativity.

**Sharp amplitude.** If δ≥0, c must have at least δ in every odd position; its normalization implies δ·2^(n−2)≤1. For δ<0 interchange the profiles. Thus |δ|≤2^(2−n), and the two parity endpoints attain equality. This is a bound within the stipulated symmetric family, not a global theorem for arbitrary channels. If δ=0 the entire channels coincide; additional proper-support tests cannot distinguish a nonzero admissible δ.

This is a useful descendant of #195's parity argument, not a claim of an unrelated new mathematical phenomenon. #195 holds proper coordinate summaries fixed while varying joint-witness existence. Here the proper object is a **restriction of the possible state population**, and the invariance is statistical decision equivalence of stochastic experiments, with explicit garbling kernels. Neither result licenses extrapolation to unrelated empirical contexts.

## 4. Decision reversals

Under the uniform prior on all n states, the posterior is uniform on the reported subset S. A receiver chooses a shortlist of exactly l states, receiving utility one if the true state belongs to it, zero otherwise. Optimally, choose min(l,|S|) members of S and fill unused positions arbitrarily. The expected utility is

    V_l(c) = (1/n) sum_{k=1}^n binom(n,k)c_k min(l,k).

The factor k from the probability of receiving a specific k-subset cancels the 1/k posterior success probability. For locally equivalent profiles, substituting the alternating perturbation yields

    V_l(c) − V_l(e) = (δ/n)(−1)^(l−1) binom(n−2,l−1),  1≤l<n,
    V_n(c) − V_n(e) = 0.

Proof of the finite identity: express min(l,k) as sum_{t=1}^l 1[k≥t], interchange sums, and use the alternating binomial tail identity
sum_{k=t}^n (−1)^(k−1)binom(n,k)=(−1)^(t−1)binom(n−1,t−1).
This identity follows by substituting Pascal's recurrence; the adjacent terms telescope. Summing the tails telescopes again to the stated coefficient. At l=n the final alternating sum is zero.

Together with Section 3, this supplies the **sharp** absolute gap

    |V_l(c) − V_l(e)| ≤ binom(n−2,l−1)/(n·2^(n−2)).

The bound is attained by the parity pair for every l<n simultaneously. It alternates in sign as l increases. For n≥3, the l=1 and l=2 tasks therefore give strict opposite preferences whenever δ≠0. No channel can simulate the other on the full support: any such simulation would permit the simulated channel's strategy to be implemented by the original channel, contradicting one of the two strict utility inequalities. This proves full Blackwell incomparability without assuming any unverified general converse theorem.

For n=2 the negative control is important: O is perfect identification, E is complete erasure, O dominates E, and both have identical singleton restrictions. Local equivalence alone does not force incomparability. For n≥3 the two shortlist reversals establish it in this family. At l=n all experiments tie.

The gap at l=1 shrinks exponentially with n. The central shortlist coefficients shrink much more slowly: by the standard central binomial approximation their normalized scale is approximately sqrt(2/pi)/(n sqrt(n−2)). That asymptotic is an elementary approximation, not needed by the exact finite result. Larger support does not imply a larger defect for every task.

There is also a scalar-information trap. For n=3 and a uniform prior, the mutual information of O is log2(3)/2 bits, whereas E gives log2(3)−1 bits. O has greater mutual information, yet E attains strictly better shortlist utility. This is not a contradiction of data processing: neither full experiment is a garbling of the other. Entropy measures a particular average reduction in uncertainty, not performance on every downstream payoff.

## 5. Interpretive archaeology

The live repository was reconciled before scope selection. #195's report and #209's report were inspected on their own active branches; neither was treated as accepted mainline evidence. #201 covers adaptive clarification for set-valued decisions, #220 calibration and pooling, #234 selective policy abstention, and #230 attribution of mixtures. Our channels are fixed, fully specified stochastic experiments with no adaptive query or action-induced change. Their comparison is relative to a state support and a decision problem.

The conceptual tension in MHAC is between anti-collapse (preserve important distinctions) and the economy of an efficient sign (discard distinctions that do not matter). This expedition introduces a third concern: **a distinction can be dispensable on every restricted support used in qualification, yet indispensable to comparing instruments on the union of those supports**.

A plausible engineering exaptation is an information-equivalence receipt:

- Declare the supported state universe and each restricted qualification context explicitly.
- Declare what is observed, including any side information and whether it is known before decoding.
- Record the tested priors, payoff families and objectives separately from the claimed comparison.
- Where a universal local-equivalence claim is intended, supply both stochastic kernels and verify their row sums and composition.
- Where a global dominance claim fails, retain concrete decision reversals rather than average them away.

Example: agents reviewing alternate software diagnostic interfaces may each be assigned a different pair of fault hypotheses. All may correctly report equivalent decision value for their assignment. A coordinator must not infer global equivalence unless it independently establishes the relevant full-support guarantee. This is a candidate test-design convention, not evidence about actual agent performance.

A semiotic interpretation: the significance of an accurate sign is partly constituted by the question it can answer and the alternatives that remain possible. That is an interpretive reading, not a demonstration of Brier's theory, Peirce's interpretant or human meaning. The exact model stipulates signal semantics from the beginning; it does not solve symbol grounding.

The title's “museum” is an archive of decision experiments rather than a mind. A sign may be informationally useful for one curator's task and worse for another. It is possible to certify equality without making the equality unrestricted, and to preserve ambiguity without assuming every ambiguity is operationally harmful.

## 6. Laboratory and execution

Run from this directory:

    node laboratory.js
    node laboratory.js /tmp/mhac-236-audio

The executable uses integer arithmetic with bounded exactly representable JavaScript numbers and rational cross multiplication, not floating-point comparisons of approximate probabilities. It enumerates actual subset masks, separately computes projected weight formulas, explicitly verifies projection/reinflation compositions for supported states, and maximizes finite utility matrices. It compares the explicit utility calculation against the closed shortlist formula for n≤7, and verifies the formula through n=9. The proof is unbounded in n; the executable census is not.

The laboratory function was executed in a V8 JavaScript environment by the implementing agent on 24 November 2026; its source was serialized directly into laboratory.js, with a small Node CLI wrapper added. The result is execution.json. The wrapper itself was not executed in that environment; there was no independent reviewer or human test. Four PCM arrays were constructed and directly compared byte-for-byte.

| Check | Count, actual run |
| --- | ---: |
| Conditional row normalizations | 88 |
| Every nonempty proper support, n=2..9 | 1,004 |
| Projected row/output equalities | 155,060 |
| Reverse-kernel composition entries, positive intersecting target outputs | 1,422,808 |
| Heterogeneous prior/signed utility comparisons | 1,004 |
| Closed-form shortlist checks | 44 |

All completed without assertion failure. The heterogeneous utilities are deterministic synthetic fixtures, not a statistical sample or a substitute for the proof of all utility functions. They do not imply coverage of actual usage. A separate integer-profile enumeration at fixed normalization denominator 8 yielded:

| n | Profiles | Distinct restriction classes | Distinct locally equivalent unordered profile pairs | Maximum observed shortlist gap |
| ---: | ---: | ---: | ---: | ---: |
| 3 | 25 | 9 | 30 | 1/6 |
| 4 | 30 | 21 | 10 | 1/8 |
| 5 | 25 | 24 | 1 | 3/40 |

This independently enumerates feasible profiles, including mixed and nonparity profiles, then groups them by computed (n−1)-restriction. For every distinct pair within a class, it checks the forced alternating difference, amplitude bound and shortlist difference. The maximum matches the sharp bound in each case. It does not enumerate all rational profiles, much less arbitrary asymmetric experiments.

Negative controls: n=2 has no reversal; a nonalternating profile perturbation is detected by a proper restriction; l=n always ties. Full-output audio distinguishes the channels' chosen sequences, while their restricted projection matches exactly. Failure to distinguish after projection is deliberate and task-specific.

## 7. The Chord of Possible Rooms

The original sound experiment uses three simultaneous integer square-wave oscillators at approximately 200, 266.67 and 333.33 Hz; a chord indicates a set of possible rooms, not a probability or physical measurement. A short integer envelope and fixed silent gap separate reports. The truth is stipulated as A. Enumerate each allowed output once for O (A, ABC) and E (AB, AC). Under T=AB, sort the projected sets into canonical order; both then produce (A, AB).

The rendered four mono 8-kHz 16-bit PCM WAV byte arrays are 8,044 bytes each. The full sequences are different by direct byte comparison; the projected scores are identical by direct byte comparison. FNV-1a 32-bit fingerprints in execution.json are convenient reproducibility checks, not cryptographic identity proofs. The construction enumerates equally weighted outcomes rather than simulating a time series of independent reports. Canonical sorting is explicit; it is not a claim that the chronological outputs of two stochastic devices coincide.

A prospective instrument might give the listener control over the active hypothesis support T, while a separate voice announces whether the user wants exact identification, shortlist coverage or some other decision. The point would be to hear how a changed question can reverse a preference even though the source codebook has not changed. This is artistic research and an unvalidated interface hypothesis. No claims are made about detectability, pleasantness, cognition or action accuracy.

**Fictional afterword.** The museum had two bells. One rang alone or with every other bell. The other refused solitude, answering always in pairs. The archivists tried them in each wing, closing the doors to all but two rooms, and issued identical certificates. At the annual inventory the doors stood open. One curator needed to find a vase; another needed to name two rooms in which it could be kept safe. They returned with opposite verdicts on the bells. The committee wanted a single rating. The bells did not disagree. The committee had asked two questions of one certificate.

## 8. Sources, limitations and disposition

**Source ledger (accessed 24 November 2026):**

- David Blackwell, “Equivalent Comparisons of Experiments,” *Annals of Mathematical Statistics* 24(2), 265–272 (1953), https://doi.org/10.1214/aoms/1177729032. Bibliographic metadata verified via https://cir.nii.ac.jp/crid/1362544419209410176; abstract read via https://celebratio.org/Blackwell_DH/article/255/ (1953 entry). The primary publisher route returned an iframe without article text; no primary full-text reading or exact theorem-page attribution is claimed. The abstract establishes historical interest in weaker comparisons and dichotomies; its k-decision comparisons concern action alternatives and must not be conflated with our restrictions of state support. The 1951 precursor's bibliographic entry was located at https://digicoll.lib.berkeley.edu/record/112749; the direct archive returned 403 and Project Euclid an iframe. No further primary claims from these inaccessible texts.
- Tilman Börgers, *Notes on Blackwell Dominance*, 3 December 2023, https://websites.umich.edu/~tborgers/BlackwellDominance.pdf. Read pp. 1–4 (finite experiment setup, risk vectors, Definition 2 and Proposition 1) in extracted text, with visual page verification of pp. 1 and 4. Also inspected the extracted Proposition 2 statement on pp. 7–8. These notes supply the precise stochastic-garbling antecedent; they are scholarly exposition, not an empirical paper. The present counterexample and kernel/variance proofs do not rely on undocumented historical priority. No claim of reading the entire notes.

No source article is redistributed; only original derivations, paraphrases and metadata. The model intentionally excludes asymmetric priors for the displayed full-support shortlist formulas (the local equivalence proof does include arbitrary priors), channel noise, untrusted support announcements, action costs, time, observation dependence, human listeners, and cross-agent strategic behavior. A general finite experiment may not have the simple subset form or alternating one-dimensional kernel. Our sharp bounds cannot be transferred to those experiments without proof.

Potential next falsifiers: change known support into an uncertain side-information signal; introduce nonuniform costs or nonuniform full-state priors; search for asymmetric channels with greater decision reversals under local equivalence; add a physical acoustic channel and compare actual decoded outcomes (would require separate validation for human claims). A useful negative result would be evidence that the support-conditioned qualification is exactly the intended complete operational domain, in which case no global equivalence claim is needed.

**Disposition:** retain as a scoped mathematical/interpretive/artistic expedition with the actual execution receipt. No canonical source, screening, protocol, evidence or programme fields edited. Issue remains open for exact-head CI, independent critique and acceptance. The required human gates of the core programme are unchanged.
