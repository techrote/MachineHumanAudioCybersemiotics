# The Receipt That Protects the Wrong Secret
## Target-specific privacy, capacitated transport and incompatible privacy promises

**Refs #410 · 24 November 2026 · mathematical/synthetic expedition · one GPT-6.2 agent, self-review only.** Not a human study, accepted Track E/G result, physical restoration proof or operational privacy certification. No priority claim.

## 1. Excavation and scope

[X004 Quotient Guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md), Exact finite claim, requires a declared downstream decision vector before judging whether a representation is sufficient. Reverse the direction: an observer's protected target must also be declared before judging whether a representation discloses too much.

[The Receipt That Needs More Names (#379)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/8f0bc1e9335fe63913ca714d9a1008e7bb281918/research/expeditions/receipt-needs-more-names/README.md), §§2–4, minimizes exact-original guessing probability. [The Receipt That Walks Away (#395)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/00d034a8977a9c1697e3d2a98ba852e545f08e65/research/expeditions/receipt-walks-away/README.md) and [The Receipt That Forgives a Collision (#403)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/274f018579df3904366e596b4ba39398d30db598/research/expeditions/receipt-forgives-collision/README.md), §§2–4, study distribution equality and distinguishability for specific originals. The present question is neither identity guessing nor equality of individual rows: how well can an observer infer a *declared binary field* after marginalizing over all originals that share that field? Restore exact authorized reconstruction and allow nonuniform priors. Distinguish hiding a field from hiding individual originals.

[#218 The Secret in the Chord](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/218) explicitly separates marginal non-disclosure from joint disclosure. Its issue scope and empty comments were inspected. Here the reversed quantifier matters: separately feasible privacy promises about different fields may be incompatible even for a SINGLE receipt, without any repeated release.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, research integrity, validation and X004 inspected. First 100 returned open issue titles and 100 open PR titles inspected, not full totals. Targeted searches for target/privacy, Hall, matching/receipt and semantic/privacy and a candidate branch-name search found no overlapping scoped expedition. Prior #403 exact report inspected; its exact-head Actions run 45492301225 succeeded (structural, not scientific acceptance). Created #410, read its full scope and empty comments, refreshed main and branched from that SHA. No changes to shared records or frozen methods.

## 2. The exact binary transport theorem (mathematics)

Let G=(X,E) be a finite simple collision graph. Each action collapses one edge's endpoints and leaves other originals distinguishable. The original X has known strictly positive prior weights pi_x summing to one. The encoder knows the original but not the action. The authorized decoder sees action, collapsed output and receipt J; the external observer sees J alone. No shared secret, source-dependent action, side channel or alphabet cap. Zero-error reconstruction is equivalent to each receipt's positive support being independent in G. Write z_xj=pi_x p(j|x) for joint mass. For a declared binary target t(x) in {0,1}, partition X into A and B, both nonempty. Let a_j=sum_{x in A} z_xj and b_j=sum_{x in B} z_xj.

    V_X = sum_j max_x z_xj
    V_t = sum_j max(a_j,b_j) = 1 - sum_j min(a_j,b_j).

These are posterior guessing probabilities, not normalized leakage ratios or Shannon information. Prior guessing for t is max(pi(A),pi(B)).

Form the bipartite *compatibility* graph K on A,B with an edge between x and y iff xy is NOT a collision edge. It is the cross-target part of the complement of G, not G itself. Build a transport network: source to each x in A of capacity pi_x; each compatibility edge directed A to B with capacity 1 (effectively unlimited); each y in B to sink of capacity pi_y. Let M be its maximum flow.

**Theorem 1.** The minimum V_t over all finite stochastic zero-error receipts is exactly 1-M.

Necessity: for each receipt j, couple the smaller of a_j,b_j to an equal mass on the other side, using nonnegative transport between the two sets of contributing originals. Every such pair is compatible because the whole column has independent support. Add these transports over j; row and column capacities cannot exceed the respective prior masses. Thus sum_j min(a_j,b_j)<=M.

Sufficiency: for each positive flow f_xy issue a separate receipt label carrying exactly f_xy joint mass from x and f_xy from y. Give unmatched prior mass a separate singleton label per original. This has legal supports and row sums pi_x, and exactly M total matched mass. The construction is finite for real as well as rational weights. It makes no claim to minimize the number of labels or V_X.

By max-flow/min-cut, the exact certificate is

    M = min_{S subset A} [pi(A\S) + pi(N_K(S))].

The capacity of a compatibility edge may be taken strictly greater than 1 to make the cut argument immediate; the optimum is unchanged at capacity 1. A deficient cut gives actual original-state groups whose prior mass cannot be matched. If pi(A)<=pi(B), attaining the prior guessing baseline is equivalent to pi(S)<=pi(N_K(S)) for every S subset A. For balanced targets it also implies independence of J and t.

**Important nonuniform-prior countercontrol.** For imbalanced targets, attaining the Bayes baseline does NOT imply independence. Exact independence instead holds iff the compatibility network can transport one full unit between the *conditional* priors pi_x/pi(A) and pi_y/pi(B). Necessity follows by coupling equal conditional masses in each column; sufficiency by using each flow edge as a label with joint masses pi(A) f_xy and pi(B) f_xy. For example, pi(a)=0.8, pi(c)=0.1 in A and pi(b)=0.1 in B, with a-b the sole collision: c-b compatibility suffices to match 0.1 raw mass and attain V_t=0.9, but conditional A mass 8/9 at a cannot be transported anywhere. Exact independence is impossible. Do not describe a zero guessing advantage as zero information in this case.

## 3. The crown frontier (mathematics)

Let G be the crown graph with r>=3 originals A_i and r originals B_i, with cross-collisions A_i--B_j for i!=j and no other collisions. Uniform prior, target t is side. Each side alone is independent; the only independent mixed-side support is {A_i,B_i}. G is connected and bipartite. Define M_j=min(a_j,b_j) and m=sum_j M_j=1-V_t.

Every mixed column can be split into a balanced pair of mass M_j on each vertex plus any excess singleton. This preserves both V_X and V_t: max(a,b)=min(a,b)+|a-b|. Pure columns retain total mass 1-2m. Each pure column has at most r entries, so its maximum is at least its mass divided by r. Therefore

    V_X >= m + (1-2m)/r = 1/r + (1-2/r)(1-V_t).

This is sharp for every V_t in [1/2,1]. Let lambda=2m. With probability lambda, use the paired receipt i common to A_i,B_i; otherwise use the two side labels. Distinct alphabets identify the mode, and the mode selection is independent of X. Then

    V_t = 1 - lambda/2
    V_X = lambda/2 + (1-lambda)/r.

At exact identity-privacy optimum V_X=1/r, target guessing is perfect (V_t=1). At exact target privacy V_t=1/2, identity guessing is at least 1/2. The pair receipt attains it and reveals the index i perfectly. The two extremes optimize different gain functions. For r=100 this means 1% versus 50% identity guessing, even though target guessing goes from 100% to 50% and authorized recovery stays exact. A system cannot monotonically improve both scores in this family.

The four-original example in §4 also proves that the SAME full-original score can coexist with opposite outcomes for a declared target. No universal scalar-to-target identification rule exists even at fixed prior and graph.

## 4. Separately private fields, no common privacy witness (mathematics)

Four equiprobable originals have labels 00,01,10,11. Collision edges are 00--11 and 01--10. Every independent support contains at most two vertices; any pair differs in exactly one bit. For target bit 1, pair 00 with 10 and 01 with 11. For bit 2, pair 00 with 01 and 10 with 11. Both are exact-recovery channels and individually perfectly private for the specified bit, with full-original guessing 1/2 in both cases. In each case the OTHER bit is perfectly revealed.

For any stochastic exact-recovery channel, each column has at least one deterministic bit. If its total mass is w, its contributions to the two bit-guessing probabilities sum to at least 3w/2 (one bit contributes w, the other at least w/2). Summing yields V_1+V_2>=3/2. Thus the minimax simultaneous target guessing optimum is 3/4, attained by a fair, visibly flagged mixture of the two deterministic channels. The mixture keeps full-original guessing at 1/2. This proof allows arbitrary finite stochastic alphabets; it is not a limitation of a particular deterministic code.

The collision graph is disconnected; no connected-graph generalization is asserted. Hiding each bit marginally would still not imply hiding their joint value in other models. This obstruction is about feasibility of concurrent marginal promises on one channel, not #218's compositional leakage theorem.

## 5. Exaptation, source boundary and reproduction

**Interpretive proposition:** MHAC's anti-collapse posture needs a protected-target specification as well as a required-action specification. A field can be private while a different field is fully exposed; exact reconstruction and target privacy may be in genuine tension even when full-state privacy looks excellent. No claim that every interface should maximize either metric. Authorized context, observer access and prior must be recorded rather than assumed. A direct design falsifier: supply a finite table of originals, intervention observations, intended protected fields and declared priors; construct the collision graph, solve the transport for each binary field, report deficient cuts, and evaluate all target scores on the SAME candidate channel. For correlated or repeated observations, perform a separate joint-transcript audit. Nonuniform priors and adversarial changes of prior need fresh qualification. Zero-error is support-based here, not an estimate of real recovery, action feasibility, or listener competence.

**Source review:** Alvim, Chatzikokolakis, Palamidessi and Smith (2012), *Measuring Information Leakage Using Generalized Gain Functions*, DOI [10.1109/CSF.2012.26](https://doi.org/10.1109/CSF.2012.26), IEEE publisher-rendered abstract and visible §III definitions 3.1–3.2 inspected 2026-11-24 by this agent; not complete paper review. Their gain-function formulation explicitly accommodates guessing a property of a secret. The target objective here is an instance, not a new leakage metric. The transport/min-cut theorem uses classical maximum-flow/min-cut and a weighted Hall condition; the derivation above is self-contained apart from that standard theorem. No exhaustive prior-art search, priority claim or empirical citation. The specific receipt reduction and crown counterexample are the contribution under investigation.

**Synthetic laboratory:** run `node research/expeditions/receipt-protects-wrong-secret/lab.js`. All scores use integer joint masses (divide by total mass to obtain probabilities). An augmenting-path matching implementation on expanded integer prior copies returns the transport witness; exhaustive cut enumeration verifies its optimum. A separate set-partition oracle partitions copies directly into valid independent-support blocks and minimizes target guessing, without invoking matching. It tests every labelled four-vertex graph, all 14 nonconstant binary targets and three prior vectors. Integer enumeration is not a proof for arbitrary real priors; the analytic construction handles those. Direct intervention maps check each decoder observation. Crown witnesses and four-state controls verify exact formulas.

Observed in the JavaScript execution before committing:
- 2,688 graph/prior/target cases;
- 60,382 partition/target comparisons;
- 12,288 cut comparisons;
- 12,294,160 positive decoder observation cells;
- 968 rational crown witnesses and 41 independent crown partitions;
- 7 four-state partitions, plus explicit optimal witnesses and equal-full-score controls.

All assertions passed. These counts overlap; they are neither independent experiments nor evidence of human perception. The same agent authored proof and code. Committed lab text fetched from its creation commit was exactly equal to tested source. Full native checkout validation, independent substantive review and broader literature search remain outstanding; draft/HOLD. No new empirical, artistic or fictional claim is smuggled into the mathematics.

**Fictional miniature (not evidence):** An archive publishes a receipt that hides which shelf a manuscript came from. The conservator applauds its anonymity. The librarian points out that the receipt reveals the manuscript's subject. They had both asked for privacy, but signed different specifications.

**Revision criterion:** a valid zero-error channel violating the transport bound, a deficient cut with a claimed perfect-privacy witness, or an admissible crown channel below its frontier refutes the corresponding mathematical claim. For application transfer, a listening experiment would need separate prior, recovery, target-disclosure and decision-loss measures; none is authorized or conducted here.
