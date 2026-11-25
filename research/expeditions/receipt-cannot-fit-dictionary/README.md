# The Receipt That Cannot Fit Its Dictionary
## Exact audit equality, exponential alphabet cost and the value of a tolerance

**Refs #426 · 25 November 2026 · mathematical / synthetic expedition.** One GPT-6.2 agent, self-review; no human observations, independent review, operational privacy qualification or priority claim.

## Contents

1. Archaeology — separate the value of the audit from its representational cost.
2. Equality — every exact Boolean optimum uses uniform full transversals.
3. Dictionary theorem — the antipodal distribution is necessarily uniform.
4. Parity contrast — a much smaller exact alphabet with a different objective.
5. Approximation — a polynomial-size existence bound and finite examples.
6. Exaptation — a vocabulary-budget qualification contract and a negative recommendation.
7. Reproduction — execution, boundaries and disposition.

## 1. Archaeology and scope

[#418/#419](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/419), actual report at [61321a6f](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/61321a6f898b37f0b2bc819b5e718584d18d6061/research/expeditions/receipt-passes-every-question/README.md), establishes exact minimax scores for fixed parity and all balanced Boolean targets. It explicitly leaves alphabet caps unresolved. [#237 The Museum of Unasked Questions](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/237), actual report §§2–5 inspected on the PR head, demonstrates that local Blackwell equivalence need not imply global equivalence. [X004 Quotient Guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md) tests necessity of distinctions against declared decisions; it does not identify which decisions to preserve. [Project foundations](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/docs/PROJECT_FOUNDATIONS.md) explicitly treat auditory vocabulary and state rendering as provisional design hypotheses.

A natural response to the earlier result is to strengthen qualification from every parity question to every balanced binary question. But exact attainment has a cost that the earlier unlimited-alphabet optimization hides. In the simplest nontrivial recovery family, the minimum vocabulary changes from linear to exponential. The point is not that a stronger privacy audit is undesirable. It is that optimizing it to mathematical equality is a materially different design requirement from enforcing a small tolerance.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866, rechecked before creating the issue-scoped branch. Read AGENTS, RAG, programme, runbook, integrity, validation, foundations, actual X004 and the two draft reports above. Inspected first 100 returned open issue titles and first 100 PR titles (not total population); targeted searches for transversal/alphabet and antipodal scope returned no matching expedition. The #418 issue and empty comments inspected; #419 exact-head Actions run 45510934649 was completed successfully, structural only. New #426 scope and empty comments inspected. Neither draft predecessor is accepted scientific evidence. No shared files or other workers' branches modified.

Model: m groups of two equiprobable originals (y,a), y in [m], a in {0,1}. N=2m. The authorized decoder sees the selected pair-collapse operation, its result, and the emitted receipt; the observer sees the receipt only. No shared key, action preview or alphabet cap unless stated. Exact recovery iff every posterior support contains at most one state from each group. A full support can be identified by a sign vector z in {-1,+1}^m (one state per group). The target f is a fixed balanced +/-1 function on the 2m originals; its guessing score is 1/2 plus half the expected absolute posterior mean. We count positive-probability distinct observable labels; redundant names with identical posterior can be merged without changing any metric here. The source prior and authorized action family remain fixed.

## 2. Equality rigidity of the Boolean optimum (mathematics)

Let m be even, m>=2, and c_m=binom(m,m/2)/2^m. From #419, the exact worst-balanced-target optimum is B_m=(1+c_m)/2. Here we prove the missing equality conditions.

For each receipt j, let w be its posterior group-mass vector, padded by zeros for absent groups. Draw a target with one plus and one minus in each group, independently and uniformly. The average absolute posterior bias equals F(w)=E_e |sum_i w_i e_i| for independent fair signs e_i. Averaging over permutations of w and using convexity gives F(w)>=F(uniform)=c_m.

**Strict equality lemma.** If equality holds, w is uniform. For any fixed sign vector with m/2 plus signs, the average signed sum over all permutations of w is zero. Jensen's inequality at that vector is equality only when every permuted signed sum is zero (the average absolute value must vanish). If F(w)=c_m, every nonnegative pointwise Jensen gap vanishes. Hence every subset of m/2 coordinates has mass 1/2. Exchanging one coordinate of such a subset with another proves all coordinates equal. This includes zero masses and the m=2 boundary.

If the worst target score is B_m, the mean over these group-balanced targets cannot exceed it, but the lower bound just proved holds at every posterior. It follows that every positive-probability receipt has w_i=1/m for all i, and every group-balanced target has score B_m. This conclusion is for arbitrary real stochastic channels, not just uniform mixtures.

Thus all optimum posteriors are uniform full transversals, and the remaining variable is the distribution mu on sign vectors. The uniform prior requires E_mu z_i=0 for each coordinate. Any such distribution is implementable: for x=(y,a), emit label z with conditional probability 2 mu(z) when z_y selects x, and zero otherwise. Marginal balance makes each row sum to one; Bayes yields the stipulated posterior. Repeated labels with the same z can be aggregated.

## 3. Exact dictionary theorem (mathematics)

A group-balanced target is specified by a sign vector t, with its value on a selected original equal to t_i z_i. Define g(z)=|sum_i z_i|. Its expected absolute posterior bias is E_mu g(t*z)/m (coordinatewise multiplication).

Every t has the same score at exact optimality; therefore this convolution is constant in t. For a subset S of coordinates write chi_S(z)=product_{i in S} z_i. Orthogonality on the cube implies the coefficient of chi_S in this convolution is E_mu chi_S times the uniform-cube Fourier coefficient of g. This follows directly by substituting u=t*z in the finite sum.

The Fourier coefficient of g is zero for odd |S| by global sign reversal. **Every nonempty even coefficient is nonzero.** For |S|=2k choose two coordinates in S and condition on the sum T of the other m-2 signs. Averaging over the chosen two signs, weighted by their product, gives

    (|T+2|+|T-2|-2|T|)/4 = 1[T=0],

since T is even. Multiply by the remaining 2k-2 selected signs and average. Conditional on T=0 the remaining signs contain equally many plus and minus. The mean product of any r of them is the coefficient of v^r in (1-v^2)^((m-2)/2), divided by binom(m-2,r), by permutation symmetry. Hence

    ghat(S) = binom(m-2,(m-2)/2)/2^(m-2)
              * (-1)^(k-1) binom((m-2)/2,k-1)/binom(m-2,2k-2).

This never vanishes. Consequently E_mu chi_S=0 for every nonempty even S. The antipodal symmetrization nu(z)=(mu(z)+mu(-z))/2 has these same even moments, all odd moments zero, and constant moment one. Fourier inversion forces nu to be exactly uniform. In particular

    mu(z)+mu(-z)=2^(1-m) for every antipodal pair.

Necessity: at least one positive label from every antipodal pair, giving 2^(m-1) labels. Sufficiency: if the antipodal law is uniform and each coordinate marginal balanced, every group-balanced target has score B_m. An arbitrary globally balanced target may also have constant-sign groups. Their contributions cancel (equal number of all-plus and all-minus groups), leaving an absolute signed sum over the mixed groups, which is an even function of z. Thus its expectation agrees with the full uniform cube. The all-balanced upper bound of #419 applies; alternatively if r groups are mixed, E|S_r|<=E|S_m| by adding independent zero-mean signs and Jensen. Therefore the characterization is exact.

For even m>=4 choose the uniform distribution on z_1 z_2 z_3=+1. It selects exactly one representative of every antipodal pair, and every individual coordinate has zero mean (flip it together with another constrained coordinate, or alone outside the constraint). Thus the exact minimum dictionary size is

    L_bool(m)=2^(m-1) for even m>=4.

Exception m=2: the uniform prior forces both first moments zero and the optimum forces the second moment zero, hence Fourier inversion requires all four sign vectors with equal probabilities. L_bool(2)=4. The antipodal condition alone is not enough without the prior condition.

The theorem also distinguishes alphabet cardinality and the number of declared targets: the latter can be enormous regardless of which labels are used. The lower bound is on actual distinct positive-probability emitted names, not on the number of possible source states, bits spent per tick, hardware channels or time slots. For optimal channels the entropy of the label is at least m-1 bits because the antipodal pair is uniform; the half-cube witness attains it. This is a further cost even with variable-length compression. It does not imply that an acoustic device must literally store a dictionary table of that size; an implicit algorithm can produce the names.

## 4. Exact parity comparison (mathematics)

Let m=2^ell, ell>=1, with group index y in the binary vector space F2^ell. The fixed nonconstant parity targets are (-1)^(u dot y + v a), u in F2^ell, v in F2. #419's optimum is P_m=(1+1/m)/2.

We sharpen its alphabet result for h=2. In any posterior choose z_y to be the sign (-1)^a of its supported state in group y (arbitrary if w_y=0). Write

    b_u=sum_y w_y z_y (-1)^(u dot y).

Inversion gives sum_u |b_u|>=m max_y w_y>=1. If the channel attains the exact parity optimum, every u with v=1 has expected |b_u|<=1/m. Their sum has expectation <=1, so every positive posterior must attain both inequalities, w must be uniform, and E|b_u|=1/m for every u.

With uniform w, equality in the triangle bound at EVERY y gives z_y b_u (-1)^(u dot y)>=0 for every u,y. Any nonzero b_u therefore fixes z as an affine character with slope u and sign b_u. Two distinct slopes cannot give the same character up to sign. Hence every optimal posterior has precisely one nonzero coefficient b_u=+1 or -1.

The aggregate weight of each slope is 1/m. Let d_u be the weight of its plus intercept minus its minus intercept. The uniform prior demands sum_u d_u (-1)^(u dot y)=0 at every y. Invert to get d_u=0 for each slope. Both intercepts of every slope are required, each with weight 1/(2m). The uniform affine-character ensemble attains the optimum (v=0 nonconstant targets have zero bias).

    L_parity(m)=2m.

This is a necessary and sufficient size, not only a construction. It is compatible with #419's affine formula (h=2). The two optimality objectives are different; the parity-optimal law need not pass the stronger Boolean test at its optimum even when both dictionary minima happen to coincide, e.g. m=4.

| m groups | Original states | Exact parity dictionary | Exact Boolean dictionary |
|---:|---:|---:|---:|
| 2 | 4 | 4 | 4 |
| 4 | 8 | 8 | 8 |
| 8 | 16 | 16 | 128 |
| 16 | 32 | 32 | 32,768 |
| 32 | 64 | 64 | 2,147,483,648 |
| 64 | 128 | 128 | 9,223,372,036,854,775,808 |

This is a separation between the representational costs of attaining distinct audit optima, not a comparison at an identical guessing threshold. The stronger family itself has a larger optimum score. Both mechanisms retain m candidates and disclose exactly one bit of whole-original mutual information (h=2); the huge alphabet difference is not a huge difference in that particular disclosure quantity.

## 5. Approximation and finite examples (mathematics / synthetic computation)

Is exact optimality a reasonable acceptance criterion? Fix additive tolerance eps>0 in guessing probability (not relative error). Draw L independent uniform cube vectors; include both z and -z with equal weights 1/(2L), aggregating duplicates. The prior is exactly uniform and recovery is exact, regardless of sample. For a fixed balanced target the average of each sampled pair's normalized absolute posterior bias is in [0,1], with mean <=c_m by the full-cube result. The elementary bounded-sample Hoeffding bound gives probability <=exp(-8 L eps^2) of exceeding c_m+2eps. For completeness the standard bound follows by exponential Markov inequality: the centered log moment generating function of a variable on [0,1] has second derivative the variance under the tilted law, <=1/4, hence <=lambda^2/8 by integrating twice from zero; independence and lambda=4t give exp(-2Lt^2).

There are at most 4^m balanced target assignments (indeed binom(2m,m)). Union bounding proves existence of a common sample with every score <=B_m+eps whenever

    L > m ln(4)/(8 eps^2).

Thus at most 2L observable names suffice for approximate optimality, with exact authorized recovery. The bound is constructive by sampling and exhaustive verification for small m; it is not a polynomial-time verifier for all targets. One may take the smaller of the exact dictionary and this upper bound. If eps is a fixed fraction of B_m-1/2, Stirling gives L=O(m^2) for fixed relative tolerance. This demonstrates an exact exponential versus approximate polynomial gap, not a tight approximate alphabet frontier.

The finite laboratory supplies two sparse reproducible examples (the sampled antipodal pairs are not a statistical performance estimate; all balanced targets are explicitly enumerated):

| m | Distinct sampled labels | Exact optimum labels | Worst sampled Boolean score | Exact Boolean score |
|---:|---:|---:|---:|---:|
| 8 | 28 | 128 | 368/512 = 0.71875 | 0.63671875 |
| 10 | 118 | 512 | 1672/2560 = 0.653125 | 0.623046875 |

The m=8 sample is deliberately not advertised as a small-error optimum. It illustrates the need to report actual worst-target score, not just label savings. The m=10 sample uses 64 draws and their negatives (128 equiprobable slots before merging repeats); 118 distinct labels remain. For both examples a concrete balanced target mask achieving the worst score is emitted by the lab. No claim that these samples minimize label count.

Sources: O'Donnell, *Analysis of Boolean Functions*, Cambridge University Press 2014, DOI [10.1017/CBO9781139814782](https://doi.org/10.1017/CBO9781139814782), publisher overview inspected, not full book. Walsh characters and inversion are classical; the exact coefficient and equality arguments above are supplied self-contained. Hoeffding (1963), *Probability Inequalities for Sums of Bounded Random Variables*, JASA 58:13–30, DOI [10.1080/01621459.1963.10500830](https://doi.org/10.1080/01621459.1963.10500830), publisher abstract and metadata inspected 2026-11-25, not the complete paper; concentration bound proved here to avoid relying on unread sections. This is not an exhaustive prior-art review. No novelty priority claim.

## 6. Exaptation and preserved disagreements (interpretation / design hypothesis)

- X004 says to justify each distinction by a declared decision. The present result says a larger audit class may require an exponentially larger set of possible labels even when the state-recovery obligation does not change.
- #237 compares channels on distinct decision scopes. Here, equal declared recovery and equal whole-state information do not imply equal target scores, or equal alphabet requirements.
- #419's exact score remains valid. Its lack of a vocabulary cap is not a defect in its theorem, but a transfer boundary for actual interfaces.
- #379's vocabulary-versus-privacy distinction survives. The new result identifies an equality constraint that forces an exponential alphabet even for pair collisions.
- A finite vocabulary is not automatically a finite perceptual vocabulary. A large combinatorial alphabet could be serialized or generated compositionally, but its timing, learning, confusability and working-memory costs must be measured separately. No human experiment was performed.

Proposed qualification contract: specify the authorized decoder's side information, protected target class, exact or tolerated guessing score, positive-label cardinality, label entropy, peak channel capacity, and deadline separately. Do not optimize an exact minimax criterion by default when a tolerance is sufficient; conversely do not substitute a sampled audit for an exact all-target guarantee without a declared uncertainty or exhaustive verification. The polynomial existence result concerns a known synthetic finite domain with a uniform prior; it cannot establish real-user privacy, operational acoustic safety or perceptual discriminability. General h>2, nonuniform priors, odd m, bounded delay, nonzero recovery error and exact approximate-cardinality frontiers remain separate problems.

**Fictional miniature (not evidence):** A librarian orders a dictionary large enough to pass every possible yes/no question with the smallest attainable guessing advantage. The printer requests a new building. The librarian permits a tolerance and the dictionary fits on a shelf. Neither has repaired the information already lost by the register. The printer asks which guarantee the librarian actually purchased.

**Revision criteria:** exhibit an admissible exact-optimum channel with fewer than the stated labels, a nonuniform antipodal law achieving the Boolean optimum, a parity-optimal posterior that is not an affine character, or a valid finite sampled counterexample to the stated union bound (as a probability bound, not an individual failure). Application claims require actual perceptual and contextual evidence.

## 7. Laboratory and disposition

Run from repo root: `node research/expeditions/receipt-cannot-fit-dictionary/lab.js`. The lab independently computes the Walsh spectrum directly, enumerates finite posterior weight vectors, enumerates small antipodal orientation assignments, builds actual pair-collapse maps and exhaustively scores all balanced targets for the displayed finite constructions. Arithmetic uses bounded integers and exact cross-products.

Executed the laboratory function in a V8 ECMAScript isolate before serializing that same function into the committed JS file. Initial test exposed an extra factor of two in the lab's cross-multiplication assertion; corrected the assertion and reran all tests. Successful run:

| Check | Count |
|---|---:|
| Direct Fourier coefficients | 1,364 |
| Integer posterior weight vectors | 6,358 |
| Weight/sign evaluations | 398,692 |
| Antipodal orientation assignments | 260 |
| Balanced targets (across policies) | 224,442 |
| Receipt–target evaluations | 25,944,624 |
| Decoder observation cells | 25,504 |
| Parity target evaluations | 308 |

All assertions passed in that run. These are overlapping synthetic checks, not independent experiments. Proofs and lab share one AI author. Full native checkout validation, exact-head CI, independent substantive critique and source-priority review remain outstanding at report creation. Draft/HOLD; no canonical research records, protocols, manifest or shared aggregate edited.
