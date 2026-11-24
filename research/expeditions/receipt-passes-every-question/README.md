# The Receipt That Passes Every Question
## Fixed-target privacy, posterior concentration and the price of asking too late

**Refs #418 · 24 November 2026 · mathematical/synthetic expedition · one GPT-6.2 agent, self-review only.** No empirical listener results, Track E/G acceptance, operational security certification or mathematical priority claim.

## 1. Excavation and the opposing objection

[X004 Quotient Guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md), Exact finite claim, tests whether a representation preserves a declared decision vector. [#219 The Secret in the Chord](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/219), §§2–3 and 6, shows that testing each released component cannot establish privacy of the joint view. [#411 The Receipt That Protects the Wrong Secret](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/5140eb0d86b04dc6f4abc272dd6fdb77445f1ed9/research/expeditions/receipt-protects-wrong-secret/README.md), §§2–4, replaces original-state guessing with a declared target and proves that independent privacy promises need not share a witness.

A tempting answer is to test EVERY balanced binary target on the same complete receipt, not merely a selected few. This expedition asks what such a stronger test establishes. The answer is not that these metrics are defective; they are exact for the decisions they specify. The objection is to treating a small worst-fixed-target guessing advantage as a certificate of negligible whole-state disclosure.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866. AGENTS, RAG, programme, runbook, research integrity, validation and X004 actual report inspected. First 100 returned open issue titles and 100 open PR titles inspected, not claimed as full totals. Targeted searches for parity/Fourier, parity/privacy and the proposed branch found related #191, #219, #267, #275, #283 and #395, but no matching scope. #219 draft diff and #411 actual report, #410 issue and empty comments inspected. #411 exact-head Actions run 45501866155 completed successfully (structural only). Created #418, read its body and empty comments, refreshed main and branched from the same SHA. No other branch edited.

## 2. Model and sharp parity theorem (mathematics)

There are N=mh equiprobable originals, partitioned into m groups of h states. An allowed action merges any pair within a single group and leaves all other states distinct. The encoder knows the original X but not the action; the authorized decoder observes the receipt J, action and resulting state. The observer sees J alone. No shared key, side channel or alphabet cap. Exact authorized recovery holds iff each positive-probability posterior p_j=P(X|J=j) has at most one member of each group in its support. A group is a clique in the collision graph, and a legal full support is a transversal.

For a balanced binary target f:X→{-1,+1}, its prior guessing accuracy is 1/2 and its posterior Bayes accuracy is

    V_f = 1/2 + (1/2) E_J |sum_x p_J(x) f(x)|.

The target is fixed before J is observed; the best guess of its value can depend on J. The designer selects one channel to minimize the maximum over the specified family of f.

First let m=2^ell, h=2^k, ell,k>=1. Write X=(y,a) in F2^ell × F2^k, grouping by y. Define characters f_s(x)=(-1)^(s dot x) for all nonzero binary masks s. Let H={0}×F2^k, H-perp the masks vanishing on H. For a posterior p, write b_s=sum_x p(x)f_s(x).

**Theorem A.** Over all finite stochastic zero-error receipt channels, the minimum of the maximum parity guessing accuracy is exactly

    V_parity* = 1/2 + 1/(2m).

Proof of lower bound: select a positive posterior atom x of maximum mass, at least 1/m. Because support contains at most one point in each H coset, sum of p on x+H equals p(x). Character orthogonality gives

    sum_{s} b_s f_s(x) = N p(x)
    sum_{s in H-perp} b_s f_s(x) = m p(x).

Subtract. The sum of absolute biases over masks not in H-perp is at least (N-m)p(x)>=h-1. There are m(h-1) such masks. Averaging over posterior labels and then over these masks proves that at least one FIXED mask has expected absolute bias at least 1/m. The choice of the maximal atom in this proof need not be available to the observer.

Attainment: choose a uniform k-by-ell binary matrix A independently of X, issue J=(A,b) with b=a+A y. Conditional on J the posterior is uniform on the affine transversal a=A y+b. This is exact recovery, and each state has probability 1/m on that support. For mask (u,v), its character average over the transversal has absolute value 1 iff u=A^T v, else zero. When v≠0, A^T v is uniform over ell bits, so its mean absolute bias is 1/m. When v=0 and u≠0 the bias is zero. All nonzero parities qualify simultaneously on this one channel.

The alphabet has h^(ell+1) labels (matrices and intercepts); the result is a privacy optimum, not an alphabet optimum. All posteriors have some perfectly determined parities, but not the same parities. At zero allowed advantage for ALL nonzero parities, Fourier inversion instead forces every posterior to be uniform over X, impossible for h>1. Approximate parity privacy must not be confused with exact privacy.

## 3. Strengthening the adversary: every balanced Boolean target (mathematics)

Assume m and h are even (not necessarily powers of two). Enlarge the target family to every balanced Boolean function, including nonlinear ones.

**Theorem B.** The exact minimum worst-fixed-target guessing accuracy is

    V_bool* = 1/2 + binom(m,m/2)/2^(m+1).

Lower bound: choose a uniformly random balanced sign assignment independently within EACH group. This always defines a globally balanced target, because h is even. For any legal posterior, its selected atom in each nonempty group receives an independent fair sign. Let w_i be its mass in group i (zero for an empty group). The average absolute bias over this random target is E|sum_i w_i eps_i| with independent Rademacher signs eps_i. This is a convex symmetric function of w. Average over all permutations of w and apply Jensen: it is minimized at w_i=1/m. Hence the average bias is at least E|S_m|/m, where S_m is the sum of m independent fair signs. For even m the binomial sum telescopes to E|S_m|=m binom(m,m/2)/2^m (equivalently use i binom(m,i)=m binom(m-1,i-1) on the upper half). Averaging over J implies at least one fixed balanced target attains this lower bound or worse.

Attainment: for each original issue a uniform random transversal containing that original. Equivalently choose a uniform transversal then a uniform member as original. The posterior is uniform on that transversal; all h^m transversals occur equally often. Fix ANY balanced target f. Let t_i be the number of plus signs in group i. A random transversal gives independent Bernoulli signs with plus probabilities q_i=t_i/h and sum_i q_i=m/2.

The convex function of the number of plus signs, F(z)=|2z-m|, has greatest expectation at q_i=1/2 for all i, subject to that sum. Self-contained proof: condition on the count Z from all but two trials. The expectation over the remaining pair with probabilities p,q is F(Z)+(p+q)[F(Z+1)-F(Z)]+pq[F(Z+2)-2F(Z+1)+F(Z)]. The last coefficient is nonnegative. Averaging p,q while holding their sum fixed increases pq and cannot decrease expectation. Repeatedly average the current largest and smallest probabilities; their variance decreases by half the squared range, so the vector converges to the constant vector. Continuity gives the bound. A target with exactly half plus signs in each group attains it. Thus the upper and lower bounds coincide, for arbitrary stochastic channels and arbitrary balanced binary questions.

This is not the same optimization as Theorem A. As m grows the optimal parity advantage is 1/(2m), but the optimal unrestricted Boolean advantage is asymptotic to 1/sqrt(2 pi m) by Stirling's formula. Merely exhausting the linear tests is therefore not equivalent to exhausting all binary tests. Nor does even exhausting the latter eliminate the following obstruction.

## 4. The posterior still loses almost everything (mathematics)

Every legal posterior has support at most m, regardless of the privacy objective. Against the uniform prior this implies:

- whole-original guessing probability at least 1/m, versus prior 1/(mh), a factor of at least h;
- posterior total variation from the prior at least 1-1/h (take the posterior support as a witness event);
- Shannon mutual information at least log2(h), since posterior entropy is at most log2(m).

Both constructions attain equality in these three measures. Here the lower bounds are necessary, not artefacts of a poorly chosen encoder. In particular no single admissible channel is better than the uniform-transversal mechanism in these measures.

For m=h=1024, the optimal parity audit gives worst fixed guessing accuracy about 50.049%, and the optimal all-balanced-Boolean audit about 51.246%, while the whole-state guessing gain is 1024-fold and posterior TV is at least 99.902%. The observer learns at least ten bits of mutual information. The baseline original-guessing probability was already very small; this is a large relative gain, not a claim of near-certain single-receipt identification.

The quantifier order explains the apparent paradox. For EVERY realized receipt J, select a balanced function which is +1 on its posterior support (possible because m<=N/2). That receipt then determines the value of the selected function with certainty. Yet no SINGLE fixed balanced function need yield much guessing advantage when averaged over receipts.

This adaptive target is not itself a fixed secret and its selected value is always +1 under the proposed selection. It is not legitimate to advertise this as having inferred a pre-existing unknown binary attribute. It is a posterior-concentration witness. The corresponding prior comparison is with a fresh independent X', keeping the selected function fixed. For that independent reference sample the selected function is still balanced. This distinction prevents circular reinterpretation of the adaptive audit.

The two notions are related to a maximum outside versus inside an expectation. Exact zero advantage for all balanced targets WOULD imply independence (balanced sign vectors span the zero-sum subspace); the counterexample concerns nonuniform approximate guarantees as m and h grow. No contradiction to exact privacy.

## 5. Reissuing the instrument (mathematics and boundary controls)

Use the uniform-transversal mechanism from Theorem B, issuing r fresh conditionally independent receipts of the SAME original. The posterior is uniform on their intersection: likelihood is constant for every original contained in every released transversal and zero otherwise. The true group always retains its true original. In each other group all r selections agree with probability p=h^(1-r), independently across groups, conditional on X. Therefore the intersection size K has law

    K = 1 + Binomial(m-1,p)
    V_X(r) = E(1/K) = [1-(1-p)^m]/(mp).

The last equality follows from binom(m-1,z)/(z+1)=binom(m,z+1)/m and the binomial theorem. At r=1 it reduces to 1/m. For r→infinity it tends to 1. For m=h=1024, two exposures already give approximately 63.23% whole-state guessing, and three give over 99.95%. Replaying the identical label instead preserves the original posterior and 1/m identity guessing. These are different conditional joint laws, not a claim about all repeated channels. No independent-source or fresh-secret result follows.

Other controls: h=1 removes collision constraints and allows a constant receipt; the theorem assumptions exclude this. Nonuniform priors or unequal group sizes change both balanced-target families and posterior weights, and require a fresh proof. An alphabet cap can destroy attainability. An external observer who also sees intervention results or a shared randomizer is a different receiver. Physical restoration is not established by reconstruction. For the authorized recovery model, if only a satisfactory remedy is required rather than the actual original, the collision graph itself may shrink.

## 6. Source boundary, proposed exaptation and fictional miniature

**Source context:** Alvim, Chatzikokolakis, Palamidessi and Smith (2012), *Measuring Information Leakage Using Generalized Gain Functions*, DOI [10.1109/CSF.2012.26](https://doi.org/10.1109/CSF.2012.26), publisher-rendered abstract and §III definitions 3.1–3.2 and 2-block/partition gain discussion inspected. The fixed Boolean targets are instances of 2-block gain, not a new metric. Naor and Naor (1993), *Small-Bias Probability Spaces: Efficient Constructions and Applications*, DOI [10.1137/0222053](https://doi.org/10.1137/0222053), publisher abstract and institutional bibliographic record inspected 2026-11-24. Their almost-balanced parity distributions motivate the comparison, but Theorem A bounds expected conditional absolute bias under a reconstruction constraint; it is NOT a pointwise small-bias guarantee. No full paper review or exhaustive novelty search. Elementary Fourier identities, convexity and Stirling's formula are established tools; proofs of the specific optimizations above are supplied rather than borrowed. No priority claim.

**Interpretive proposition:** target-specific audit is indispensable but an audit's target class and timing are part of its scope. Even exhaustive fixed binary average-success audits are not substitutes for posterior concentration, many-valued partition gains, adversarial prior changes or repeated joint views. This does not refute #411's transport theorem or #219's joint-view critique. It challenges their possible extension to treating the worst fixed binary score as a universal scalar privacy certificate.

**Design hypothesis:** a finite acoustic/telemetry qualification should distinguish fixed declared target score, maximum posterior concentration, prior-to-posterior shift, repeat-exposure model, and authorized decision loss. For a known finite equal-clique fixture, the formulas above are exact negative controls. A listening study would need operationalized target choice timing and controlled prior/context access; none conducted or authorized. No production privacy mechanism or covert acoustic code is proposed.

**Fiction (not evidence):** The archive permits every question that can be answered yes or no. Each visitor leaves almost as uncertain about their chosen question as when they entered. The inspector instead looks at the shelf of remaining candidates. Almost every shelf is now empty. The archive protests that no particular question was answered reliably. The inspector agrees, and asks why the audit did not count the empty shelves.

**Revision criterion:** an admissible channel beating either worst-fixed-target bound, an actual balanced target exceeding the uniform-transversal bound, or an intersection distribution violating the stated independent-release law refutes the corresponding result. Application claims require separate empirical evidence.

## 7. Synthetic laboratory and disposition

Run Node: `node research/expeditions/receipt-passes-every-question/lab.js`. The lab enumerates every balanced target on small explicit state spaces and compares the result against a separate count-vector polynomial oracle; builds affine transversal labels directly; checks actual pair-collapse decoder maps; enumerates integer posterior weights for the convex lower bound; and enumerates repeated-label intersections. Counts from executed ECMAScript isolate:

| Check | Count |
|---|---:|
| Balanced fixed targets | 25,886 |
| Count-vector oracle cases | 1,219 |
| Transversal/target evaluations | 6,591,704 |
| Affine parity evaluations | 10,308 |
| Direct positive decoder observation cells | 155,808 |
| Integer posterior weight cases | 65,805 |
| Repeated receipt sequences | 266,820 |

All assertions passed. Counts overlap and are not independent experiments. The proofs and code share one AI author. The finite enumeration is not a proof of arbitrary real channel laws; §§2–5 supply the arguments. No human study, physical security qualification, native full checkout validation or independent substantive review. Draft/HOLD; no canonical records edited.

## Contents

1. Excavation — from selected targets to all fixed binary targets.
2. Parity theorem — exact minimax over linear characters.
3. Boolean theorem — exact minimax over all balanced binary functions.
4. Concentration — fixed questions versus posterior-adaptive witnesses.
5. Reissue — exact intersection law and negative controls.
6. Exaptation — source limits, proposed audit and fiction.
7. Reproduction — finite checks and outstanding qualification.
