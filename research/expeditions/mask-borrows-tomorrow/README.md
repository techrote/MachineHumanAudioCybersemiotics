# The Mask That Borrows Tomorrow
## Causal versus offline anonymity and the hidden price of preview

**Refs #314 · 24 November 2026 · bounded mathematical expedition.** One ChatGPT author, derivation, code and self-review. No participant data, listening experiment, production privacy guarantee, accepted Track E/G finding or mathematical priority claim.

## 1. Excavation: privacy certificates may borrow future information

Draft [#275](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/d0be377e9fed4986dccbcacf0fbd5c6b73e785c8/research/expeditions/mask-keeps-partner/README.md), §2, proves a sharp switching-rate threshold and supplies a causal policy attaining the two-tick lower bound even among offline policies. The coincidence of the online and offline optimum there is a property of the independent-increment source, not a general principle. Draft [#291](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/6dab50fb3685bbed534f017ca6259a29ac6e9304/research/expeditions/rest-arrives-too-late/README.md), §2, constructs causal masking for uniform affine sources; §4 explicitly excludes general nonuniform laws. Draft [#307](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/51f171155273b0c4ca4f903317679fc489e02819/research/expeditions/hint-changes-listener/README.md) shows that observer metadata can violate a required conditional-independence assumption. Here the independence constraint is instead on the encoder's past outputs versus the actual source's future. The distinction changes feasibility even with no additional observer metadata.

The accepted [X005 negative-space protocol](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/sound-of-nothing/NEGATIVE-SPACE-PROTOCOL.md) distinguishes status validity, resolution and unknown states. An offline replay that retrospectively rewrites its initial status would silently change the evidence available at that time. This is a design analogy, not a demonstrated acoustic effect.

Reconciled main at 495a98ca12bae467a507031f04931aa4254b1866 before branch creation. Read AGENTS, RAG, programme, runbook, integrity and validation; inspected 98 open issue titles and 80 open PR titles (bounded scope triage, not technical review of every PR). Recent other topics: mixer headroom, spatial aliasing, retrospective genre fit, room correction, common-filter ambiguity. No duplicate title/scope found. Read #274/#290/#306 issue bodies and comments (empty), PR descriptions and the relevant pinned upstream report passages; their exact heads had completed successful Research integrity workflows, but all three remained drafts. Also inspected #267's contextual restriction and X005 on main. Core R005/R006 acceptance remains open; this branch does not advance those gates. All work isolated under this directory.

## 2. A finite causal feasibility theorem

Let G>=2 groups have the same finite binary path law mu, on T ticks. The actual group g is fixed. A public symbol W_t belongs to a declared finite set A of G-bit words. In the original restricted vocabulary A is the set of even-parity words. Coordinate g must equal the actual source bit X_t exactly. The observer sees the full ordered symbol sequence but not g or the source separately. The encoder knows g and the source prefix through t, not future source values; its private randomness is independent of the source. No feedback changes mu, and there is no hidden predictive input. Privacy is identical transcript law across groups, or, for approximate privacy, the maximum pairwise total variation (TV) of their laws.

**Offline theorem.** A perfectly private offline encoder exists iff there is a common law Q on A^T whose G coordinate paths all have marginal mu. Necessity is immediate from exact decoding and identical transcript laws. For sufficiency, draw the remaining coordinates conditional on the complete actual coordinate path, using the conditional distribution of Q. This procedure is not necessarily implementable with prefix-only access.

**Online theorem.** The same statement holds with the additional requirement that under Q, for every positive-probability joint prefix h and group i, the probability that the next coordinate i is one equals the source's next-bit probability conditional on coordinate i's own prefix:

    Q(W_t[i]=1 | W_<t=h) = mu(X_t=1 | X_<t=h[i]).

Necessity: run the causal encoder for actual group i. Its past output is a function of its own past source and independent private randomness, so does not provide information about the future source conditional on its own prefix. Replace the actual group law by the common Q. This gives every coordinate constraint at once. Sufficiency: at a reachable history, draw the next word from the specified Q transition law conditioned on its i-coordinate equalling the current actual bit. The actual bit has the marginal required by that transition; summing over its possible values reproduces Q's transition. Induction over time proves exact reproduction of Q for each actual group and no preview. Zero-mass conditionings are unreachable, not an opportunity to issue a false symbol.

Equivalently, start from all feasible joint prefixes at depth T and recurse backwards. At prefix h of depth t<T, keep it iff the vector of G next-bit probabilities is in the convex hull of those words w in A for which hw is a viable successor. Exclude coordinate prefixes with zero mu probability. The root must be viable. The proof is the online theorem applied recursively; the convex combination is the conditional law for that step. This finite algorithm may be exponential in horizon and alphabet size. Checking the unrestricted next-word convex hull alone, without excluding nonviable successors, does not generally establish viability.

For G=3 and A={000,110,101,011}, each possible next-bit probability vector (x,y,z) uniquely determines the conditional masses:

    P(000) = 1-(x+y+z)/2
    P(110) = (x+y-z)/2
    P(101) = (x+z-y)/2
    P(011) = (y+z-x)/2.

The local law exists iff all four values are nonnegative. Thus for this alphabet any perfectly private causal transcript law is unique, if it exists: recursively propagate the unique transitions through every positive-probability history. No alternative coupling at one history can repair a later obstruction. In larger alphabets the transition solution need not be unique. The exact finite characterization is a specialized support-constrained instance of established multicausal transport, not a new general transport theory.

## 3. Sharp separation in two ticks

Take G=3, the four even words, and an initially fair bit. Let a=P(X_2=1|X_1=0), b=P(X_2=1|X_1=1). Perfect privacy forces the first output to be uniform on the four words (unique tetrahedron solution). In the common causal law the next-bit vector at 000 must be (a,a,a); at a nonzero first word it is a permutation of (a,b,b). Applying the preceding four inequalities gives the exact criterion:

    a <= 2/3,   a <= 2b,   a+2b <= 2.

For the remainder fix b=1/2 and allow any 0<=a<=1.

**Offline sharp feasibility: a<=5/6.** Under any perfectly private offline coupling the first word is uniform. Sum the second-bit ones over coordinates whose first bit was zero. At first word 000, this sum is at most two. At every nonzero first word, it is at most one (only one first-zero coordinate exists). Hence its expected value is at most (2+3)/4=5/4. Each coordinate's marginal contributes a/2, so 3a/2<=5/4. This proves necessity.

To attain a=5/6, first choose a uniform first word. If it is 000, select a uniform nonzero second word. If it is nonzero, select uniformly one of the two second words different from it and from 000. Thus the first-zero coordinate has second-bit probability 2/3 after 000 and one after the other possible first-zero word. The first-one coordinate has second-bit probability 1/2. Each coordinate's path law (00,01,10,11) is (1,5,3,3)/12. The common law is invariant under coordinate permutation. For a=0, use second word 000 after 000, and choose either 000 or the same nonzero first word with probability 1/2 after nonzero first word. Mixing these two laws realizes every a in [0,5/6], with the same fair first bit and b=1/2. The offline theorem implements these laws by conditioning on the whole actual path.

The endpoint a=5/6 is not causal. In particular Q(X_2=1|W_1=000)=2/3, but given the actual first bit zero the probability is 5/6. Under the endpoint construction, P(W_1=000|actual path 00)=1 and P(W_1=000|actual path 01)=2/5. The decision at tick one uses tick-two information. It is not merely a different choice of independent randomness.

**Sharp causal leakage for every a, b=1/2.**

    delta_online(a) = max(0, (3a-2)/8).

Proof. The zero case is the causal feasibility criterion. For a>2/3, symmetrize any policy by uniformly permuting coordinate/group labels. This retains causality and utility and cannot increase worst-pair TV by convexity. In the resulting family let t be the mass of first word 000 for each actual group. The first nonzero word omitting that group has mass 1/2-t; each of the two nonzero words including the actual group has mass 1/4. Here 0<=t<=1/2. At 000 the joint masses of the two second words including the actual group are each z=at/2. The mass y of the nonzero word omitting it is at most (1-a)t by the actual marginal. For two distinct groups the TV contribution from first word 000 is |z-y| >= t(3a/2-1). In the two nonzero first-word blocks where one of these groups is omitted and the other included, the summed TV contribution is at least |t-1/4| (half the absolute mass difference per block). Other contributions are nonnegative. Therefore

    delta >= t(3a/2-1) + |t-1/4| >= (3a-2)/8.

The last inequality follows because 0<3a/2-1<=1/2, so the piecewise linear expression is minimized at t=1/4. To attain the lower bound, choose a uniform first word for each group, conditionally sampled on its observed first bit. After each nonzero first word use the common local law for the next probability vector (a,1/2,1/2) permuted appropriately; its tetrahedron masses are nonnegative for all a in [0,1]. After 000 use group-specific conditional second-word masses: zero on 000, 1-a on the nonzero word omitting the actual group, a/2 on each of the other two. These give correct marginal a and are realizable by conditioning on the observed second bit. All nonzero first-word blocks are common; the only contribution is 1/4 times 3a/2-1, exactly the claimed value.

| a | Offline perfect privacy | Optimal causal TV |
|---:|---|---:|
| 1/2 | yes | 0 |
| 2/3 | yes | 0 |
| 3/4 | yes | 1/32 |
| 5/6 | yes | 1/16 |
| 1 | no | 1/8 |

Do not interpret 1/16 as a percentage of people identified. TV is the maximum difference in event probability between two group laws; under equal binary hypotheses the optimal success is (1+TV)/2. No multiclass or empirical listening metric follows.

The gap is specifically between no-preview causal policies and offline policies with one tick of preview. Buffering the first report until the second source bit arrives may remove this obstruction if the application permits that delay and the schedule itself discloses nothing further. It is not a solution to a first-tick decision deadline. For an unrestricted binary vocabulary allowing 111, simply repeat the actual bit in all coordinates and all these obstructions disappear. For IID source bits with a=b=1/2, both offline and online perfect privacy are feasible. For independent fair-initial flip dynamics, b=1-a, the preceding two-tick criterion reduces to the earlier r<=2/3 threshold. The old theorem is not refuted; its extension to arbitrary path laws is.

## 4. Exaptation and deliberate refusals

**Interpretive synthesis:** a report can have an immaculate final distribution while being impossible to issue when it claims to have been issued. Retrospective correction may be acceptable for a score or dataset but cannot serve as evidence of a real-time protocol. The chronology of available inputs is a separate constraint from final distributional fidelity. This adds a concrete counterexample to treating an archive's replay as a validation of its original interaction.

**Proposed test-only preview receipt:** identify source law and version; source event time; encoder availability time for each input (including forecasts); actual emit time; decoder deadline; observer-visible buffering, silence and revisions; alphabet restrictions; and whether evidence was generated online or from the completed trace. A no-preview conformance test should fix the observed prefix, hold independent encoder randomness fixed, vary the unseen suffix, and check that emitted prefix is invariant. With randomized black-box access only, conditional prefix-law comparisons are a weaker falsifier, not a proof that inaccessible future inputs were absent. The exact model test checks conditional transition probabilities for each actual group. Causal effects of emission on future states, predictive covariates, adaptive masking and observer side information require separately specified models.

Reject a universal architecture rule requiring all communication to be online: a delayed report may be the right product, and a source law or a trusted predictor can make future states legitimately inferable. Reject the contrary universal rule that offline privacy witnesses qualify deployed streaming encoders. The mathematical gap prices a particular information restriction, not the value of prediction in general. No actual privacy guarantee or Brier attribution follows from it.

**Artistic score (symbolic, unrendered):** three voices, two chords. The first chord is drawn uniformly from the four even words. In the retrospective edition, the second chord follows the endpoint coupling in §3. Each voice receives identical path statistics. In the live edition the same intended statistics are performed from a revealed bit at each tick; the ensemble uses the causal optimum. The first edition is a composition with the future visible to the composer, the second a performance with the future withheld. A rest or buffer would be a third edition, not an invisible patch. No listening study is claimed.

**Fiction:** A conservator finds a perfectly anonymous recording in an archive. She reconstructs the organ's score, but it requires the performer to know tomorrow's note when playing today's chord. The builder argues that the recording proves the instrument worked. The conservator writes two labels: *a possible recording*, and *an executable instrument*. Only the first has been demonstrated.

## 5. Source boundary, computation and disposition

Source comparison, one AI reader, 24 November 2026: Daniel Kršek and Gudmund Pammer, [General Duality and Dual Attainment for Adapted Transport](https://link.springer.com/article/10.1007/s00245-025-10240-y), Applied Mathematics & Optimization 91, article 52 (2025), DOI 10.1007/s00245-025-10240-y, abstract and §2.2 Definition 2.4, equation (2.5). Open HTML, targeted definition and introductory passages only; the definition constrains each process's whole path to be conditionally independent of the other processes' pasts given its own past. In our finite setting the successive next-step conditions imply the full future condition by iterated conditioning, and the converse is immediate. The proof above is a direct application to exact restricted-symbol anonymity; no general transport duality is imported. Beatrice Acciaio, Daniel Kršek and Gudmund Pammer, [Multicausal Transport: Barycenters and Dynamic Matching](https://epubs.siam.org/doi/abs/10.1137/24M1634096), SIAM Journal on Financial Mathematics 16(3), 1104–1138 (2025), DOI 10.1137/24M1634096: abstract/metadata only, confirms the multicausal framework's established scope. No full-paper reading, external verification, literature-wide novelty assessment or empirical source synthesis claimed.

Run from repository root:

    node research/expeditions/mask-borrows-tomorrow/lab.js

The exact precommit JavaScript source was executed in V8. All bounded arithmetic is integer arithmetic (except exact halves and tested integer divisions); the grid enumerator does not rely on floating-point tolerances. It enumerates symmetric causal policies at total mass 48, for a in {0,1/6,...,1} with b=1/2; for each actual-group distribution it independently checks source-path marginal and the conditional causal law, then measures TV on the full transcript. Symmetrization and the analytic proof cover arbitrary real-valued policies; grid qualification alone does not. A separate direct enumeration of all four-word probability laws with 24 mass units verifies the unique local transition law and exact two-tick criterion on rational grids. All 3^6 three-tick trees of conditional values in {0,1/2,1} with fair root are checked against the enumerated-law oracle. The offline construction is checked on 11 mixture values and all three marginals.

| Activity | Count |
|---|---:|
| Symmetric causal candidate policies | 184,289 |
| Actual-group path and causality validations | 552,867 |
| Offline group-marginal checks | 33 |
| Enumerated local probability laws | 2,925 |
| Local closed-form comparisons | 2,197 |
| Two-tick criterion grid comparisons | 169 |
| Three-tick source trees | 729 (114 feasible) |
| Named separation/boundary/IID controls | 3 |

Every assertion passed. These counts overlap and are computational activities, not independent experiments. One AI authored both proof and tests. Full clean-checkout repository tests, exact-head CI and substantive independent review are not claimed by the precommit run. No central records, frozen protocols or other active worker files altered. Keep draft pending the acceptance gates; no core research milestone declared complete.

The conclusion is deliberately narrower than an exhortation to preserve all history: **a feasible coupling of finished histories need not be a feasible coupling of the information available as those histories unfold.**
