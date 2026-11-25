# The Dictionary That Mishears in Concert
## Correlated slot errors, robust semantic recovery and the limits of marginal calibration

Refs #476 · 25 November 2026 · Mathematical and synthetic-computational expedition. One ChatGPT GPT-6.2 author; self-review and deterministic replay, not independent scientific review.

## Contents

1. Excavation — distinguish symbol error rates from the joint renderer.
2. Model — exact authorized recovery before noise, Bayes and law-blind decoding after noise.
3. Sharp robust result — prove the four-pair optimum for arbitrary dependence.
4. General affine obstruction — extend the exact affine result and give a scalable nonlinear lower bound.
5. Countercontrols — identical marginals and even identical pairwise statistics can conceal different outcomes.
6. Exaptation and qualification — record proof scope, tests and outstanding research.

## 1. Excavation

[Draft #465](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/a0ac0a09951c4aea22dd5bcf13f02edeaf30c91a/research/expeditions/dictionary-loses-bit/README.md), §§2–5, demonstrates a nonlinear advantage under independent symmetric bit flips. Its assumptions explicitly exclude correlated errors. It is tempting to transfer that result to audio after estimating an average error probability for each note or slot. That transfer is invalid without a dependence contract.

A complementary line is [draft #449, jitter-fragile alphabets](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/b57f8a35a7d84c9f6d278dae7bd967a8c74b5616/tools/experimental/adversarial-448-jitter-alphabets/README.md), Model and operation / Search and held-out evaluation: a noiseless deletion packing has a small bounded-jitter separation, with common timestamp witnesses; the set-membership receiver can abstain. Those are bounded continuous timing errors with a different observation model, not additive binary errors. The common lesson is the need to state the entire perturbation class and decoder access, not that one laboratory's results transfer to the other.

Accepted [X004 Quotient Guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md) is a static deterministic fibre test. It does not certify uncertain rendering. The [foundation](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/docs/PROJECT_FOUNDATIONS.md) separates rendering, output, interpretation and action. This report turns one uncertainty boundary into an exact minimax contract.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866, rechecked before branching. Read AGENTS, RAG, programme, runbook, integrity, validation, foundation, X004, predecessor report and #449's primary report. Inspected #464 body/comments (none), #465 head/mergeability and Actions run 45540418109 (success; not scientific validation), #448 body and #449 report. Open issue and PR searches each returned 100 titles, with overlapping entries; not a certified exhaustive type-separated inventory. Targeted correlated-noise issue and branch searches returned no competing scope. New #476 body/comments (none) checked before branch creation. #465 and #449 remain drafts, not accepted findings. No central records, other branches or frozen methods changed.

External orientation only: Guruswami and Smith, [Explicit Capacity-achieving Codes for Worst-Case Additive Errors](https://arxiv.org/abs/0912.0965), arXiv abstract, 2009 version metadata, accessed 25 Nov 2026; and Yasunaga, [Error Correction by Structural Simplicity: Correcting Samplable Additive Errors](https://arxiv.org/abs/1506.03171), arXiv abstract, 2015, same access date. These discuss different additive error models and coding objectives. Only abstracts inspected, no claim of full-text review or scholarly priority. The finite Walsh identities below are derived directly.

## 2. Model (mathematical)

There are m even collision pairs of equiprobable originals (i,s), s in {-1,+1}. The intervention collapses the two states in one named pair and leaves other states distinct. The receiver knows that intervention and its result; an external observer knows only the received word. We use the uniform minimum-size noiseless full-transversal dictionary of #465: k=m-1 bits, word x uniform marginally, balanced functions f_i(x) in {-1,+1}, exactly one sign vector per antipodal class. The conditional transmitted word law is (1+s f_i(x))/2^k. No input throttle, nonuniform label law, additional slots, shared secret, or error correction by retransmission is allowed in the primary theorem.

The received word is y=x XOR E. E is independent of x and the original. All k marginal probabilities P(E_j=1)=q are identical, 0<=q<=1/2. No independence between coordinates is assumed. The joint law P is otherwise arbitrary. The same law applies to all pairs. This is not a message-dependent adversarial flip budget.

Write N_P f(y)=sum_e P(e) f(y XOR e). The uniform output marginal and direct conditional rows give the conditional Bayes advantage T_i(P)=E_y |N_P f_i(y)|, conditional success (1+T_i)/2. A fixed sign decoder d_i(y) has advantage E_y d_i(y) N_P f_i(y), which need not equal T_i. A law-blind decoder may know q and the chosen dictionary, but not P. The primary robust score is max_dictionary inf_P min_i T_i(P); the law-blind variant also chooses decoders before the adversary chooses P. Random guessing is allowed. All probabilities are averaged across the two colliding originals, not a guarantee for each original individually.

For character chi_a(x)=(-1)^(a dot x), N_P chi_a=eta_a chi_a with eta_a=E chi_a(E). This follows by multiplication under XOR, no assumption of independence. For singleton a, eta_a=A=1-2q; for two coordinates eta_ij=1-4q+4P(E_i=E_j=1)>=1-4q. The independent model in #465 is the special case eta_a=A^|a|. The correlation multipliers may be negative.

## 3. Exact robust nonlinear optimum (four pairs, three slots)

**Theorem.** For four pairs and three slots the exact minimax reconstruction advantage is

    R(q) = (1-2q + max(0,1-4q))/2
         = 1-3q             for 0<=q<=1/4
         = 1/2-q            for 1/4<=q<=1/2.

The law-blind variant has the same value. Both claims concern the stipulated uniform noiseless-optimal dictionary family, not arbitrary codes.

**Lower certificate.** Use the admissible masks [27,53,71,141] from #465 (bit x selects +1). Their Walsh coefficients are exactly +/-1/2 on two singletons and two doubletons each, zero elsewhere. This is verified by integer summation in lab.js and by direct antipodal coverage. For q<=1/4 choose d_i=f_i. Orthogonality gives advantage

    (2A+eta_b+eta_c)/4 >= (A+1-4q)/2,

where b,c denote the doubletons specific to f_i. For q>=1/4 choose d_i equal to one singleton character multiplied by the sign of its Fourier coefficient. Its advantage is A/2 regardless of P. Thus a fixed decoder at each declared q achieves the bound simultaneously across all pairs and all permitted laws; a Bayes decoder cannot do worse. The decoder switch at q=1/4 is an engineering option, not a requirement to know correlations.

**Upper certificate.** At q=1/4 let E be uniform on {000,001,010,100}. The endpoint noise operator averages a function at a word and its three neighbours. Normalize balanced masks by f(0)=+1; there are choose(7,3)=35. Direct integer convolution gives exactly four masks with T>1/4: 15,51,85,105, corresponding to the four odd-weight characters (three singletons and the triple). The other 31 have T<=1/4. No valid dictionary can use only the four stronger masks: their product is constant, contradicting the balanced even-product condition. This last assertion also follows by enumerating all 52,360 four-subsets, checking all six pairwise XORs and the fourfold XOR for weight four, and comparing with literal antipodal coverage. There are 840 valid normalized sets. Thus each dictionary has a row with T<=1/4 under this endpoint law.

For q<=1/4 the explicit least-favourable candidate is P(000)=1-3q, each single flip has mass q, and all other patterns have zero mass. It is the linear interpolation between no noise and the endpoint. T for the selected weak row is convex in P (sum of absolute linear forms), so T<=(1-4q)*1+4q*(1/4)=1-3q. For q>=1/4 mix the endpoint law with uniform noise over all eight words, with endpoint weight 2-4q. Every balanced row is annihilated by uniform noise. Its T is therefore scaled by 2-4q, and the weak row has T<=(2-4q)/4. These two explicit adversarial laws work against every valid dictionary, even if a Bayes decoder knows the law. The lower witness and upper certificates meet. This is a continuum proof, not a fit to simulated q values.

At q=.1, the optimal robust conditional success is 85%, compared with #465's independent optimum 86%. At q=.25 it is 62.5%, compared with the affine robust optimum of 50% below. A difference of one percentage point at .1 is real but does not justify an empirical significance claim.

## 4. General affine theorem and a scalable construction

For arbitrary even m>=4 with k=m-1, the exact affine robust optimum is

    R_affine(q)=max(0,1-4q).

This also holds for the law-blind contract. Proof: a valid affine dictionary has m nonzero binary row vectors a_i, rank k, and a unique nonzero linear dependence of odd cardinality (even dependence would violate antipodal coverage). If every row had odd weight, that odd collection could not XOR to zero. Thus at least one row has even weight >=2.

Choose two coordinates in this even row. Couple the remaining coordinates of that row in pairs with identical Bernoulli(q) flips, so their contribution to its parity cancels. For q<=1/4, make the two chosen coordinate flips mutually exclusive, each with probability q. Their parity correlation is 1-4q. For q>=1/4, assign the two singleton patterns probability 1/4 each, the double-flip pattern probability q-1/4, and the no-flip pattern 3/4-q; parity correlation is zero. Other coordinates can be independently assigned Bernoulli(q). This is a single source-independent joint law with the stipulated marginals. The selected row's Bayes advantage is exactly the absolute correlation, giving the upper bound. To attain it use k singleton rows and the XOR of the first two; the latter has eta>=1-4q. The direct parity decoder attains the bound below 1/4; above it, random guessing guarantees zero. The singleton decoders attain A. This proves the general affine result.

A scalable nonlinear lower bound: use the four-pair/three-slot witness and append m-4 independent singleton coordinates as additional semantic rows. The word-to-sign map still selects exactly one representative per antipodal pair, and every row is balanced: the first four signs uniquely orient each antipodal class and the appended signs are unrestricted. There are still m-1 slots. Since every marginal is q and the first-three marginal joint law is admissible, the previous law-blind guarantee R(q) holds, with appended rows at A>=R(q). Thus for every even m>=4 a nonlinear minimal dictionary strictly beats the optimal affine robust score in 0<q<1/2. This is a lower bound, not an exact general nonlinear optimum. Four additional independent physical slots are not needed; the m-slot full cube comparator has robust advantage A using direct singleton decoders.

## 5. Countercontrols and observer privacy

The following three laws all have slot error q=1/10 and are source-independent. The exclusive law is the low-q adversarial witness, the independent law is the predecessor assumption, and the common law flips all three together with probability q. Actual conditional rows and all choose(8,4)=70 balanced target functions were enumerated for each of the two dictionaries. The external observer uses the correct joint law and sees only y.

| Error coupling | Affine worst-pair accuracy | Nonlinear worst-pair accuracy | Affine worst fixed balanced-target guessing | Nonlinear worst fixed balanced-target guessing |
|---|---:|---:|---:|---:|
| Mutually exclusive single flips | 80% | 85% | 65% | 65% |
| Independent flips | 82% | 86% | 65% | 65% |
| All three flip together | 90% | 95% | 66.875% | 68.75% |

The affine row vector is [A,A,A,eta_12]; for common flips its parity row is perfect. For the nonlinear witness the four accuracies coincide in these exchangeable examples, not necessarily for an arbitrary joint law. Correlation is neither inherently harmful nor inherently beneficial: the dependency structure determines its effect. Greater receiver utility can also increase disclosure under a separate protected-target contract. The table is not a minimax privacy theorem.

**Pairwise auditing is insufficient.** At q=1/4 the following three laws all have every singleton flip probability 1/4 and every pair intersection probability 1/16 (pairwise independence). In decimal XOR word order 0,...,7, two are

    P0 = [7,2,2,1,2,1,1,0]/16
    P1 = [6,3,3,0,3,0,0,1]/16

and the third is their mean. The triple parity correlations are respectively +1/4, -1/4 and zero. A triple-dependent semantic distinction has conditional Bayes accuracies 62.5%, 62.5% and 50%. Even the correct pairwise covariance matrix cannot determine that utility; the sign change also defeats a decoder calibrated to the wrong law. This triple character can occur in a valid minimal affine dictionary, for example character indices [1,2,3,7] (unique odd triple dependence). The example is not a claim about all functions or actual auditory error structure.

## 6. Exaptation, reproducibility and limits

A proposed renderer qualification is to retain the empirical joint confusion counts, not merely marginals, and evaluate declared semantic contrasts against a held-out dependence uncertainty set. Measure singleton, pair and higher-order error moments where identifiable, worst-pair conditional success, worst-original success separately, and observer disclosure against the same realized channel. If estimating the joint distribution is expensive, marginal-only robust certificates provide a defensible fallback for this particular synthetic class. For acoustic motifs a wrong onset, erasure or synchronization error may not even be representable as an additive bit flip; #449's timestamp ambiguity illustrates why that model must be tested rather than assumed. Do not treat q as a human perceptual parameter or the analytic guarantee as a listening result. An actual evaluation would need an independently qualified feature detector and appropriately authorized participant work, with observation, decoder access and abstention separately specified.

Run `node lab.js` in this directory. The self-contained JavaScript certificate enumerates 52,360 candidate dictionaries, compares 840 valid sets to direct antipodal coverage, checks the quarter-noise endpoint against all 35 balanced normalized masks, independently enumerates 57,153 integer noise laws (592 with the specified equal marginals and q<=1/2), and tests 18,944 actual conditional decoder cells and 2,368 law-blind decoder checks. The finite grid is denominator 4,8,12, not exhaustive over real-valued laws. The continuum lower and upper proofs are separate. Six policy/law combinations each enumerate 70 balanced targets, with a separate pairwise-statistics negative control. The exact integer development run and fetched committed-blob replay returned identical results; lab blob 78215d9831a1a671f5a7082e75c0a4c55fcc1bea. Counts overlap and are not independent trials. Native Node checkout, full repository validation, independent mathematical review, broader literature comparison and acoustic/empirical qualification are outstanding. Keep Draft/HOLD and #476 open. No human evidence, actual audio recordings, operational security promise or new scholarly priority claimed.

Revision triggers: a valid four-pair normalized dictionary with all endpoint advantages >1/4; a permitted law violating the law-blind bound for the explicit witness; a valid minimal affine dictionary escaping the even-row obstruction; or a disagreement between direct conditional rows and reported target/decoder results. General nonlinear optimality beyond four pairs, asymmetric marginals, input-dependent noise, temporal dependence between receipts and real acoustic observations remain open.

Fictional miniature (not evidence): a quartet is given a score in three symbols. Sometimes each musician mishears independently; sometimes all mishear together. The conductor reports the same note error rate in both rehearsals, yet one relationship survives every collective mistake. The score was never calibrated by counting mistakes alone.
