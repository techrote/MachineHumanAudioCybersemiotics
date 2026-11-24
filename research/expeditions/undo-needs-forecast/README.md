# The Undo That Needs a Forecast
## Pre-action receipts, late-bound interventions and the topology of lost history

**Refs #338 · 24 November 2026 · original finite mathematical/synthetic expedition, AI-authored and self-reviewed by ChatGPT GPT-6.2.** Not Track E/G evidence, an auditory experiment, production safety qualification, physical reversibility, or a mathematical priority claim.

## Contents

1. Excavation — move from the forecast sequence to an older unresolved retraction problem.
2. Exact receipts — distinguish knowing an action before and after writing its historical receipt.
3. Preview tradeoff — characterize pair-collapse hints and falsify a generalization to bundled actions.
4. Randomized recovery — derive sharp minimax error and the price of adversarial timing.
5. Counterexamples and exaptation — separate reconstruction, action identity, actual recovery and verified delivery.
6. Qualification — exact finite enumerations, source extent and integration boundaries.

## 1. Excavation

The main [quotient guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md) establishes the static finite-table condition that a decision must be constant on retained fibres. It explicitly refuses to elevate every conceptual distinction into a permanent schema field. Can a receipt be compiled *before* we know which quotient an intervention will induce?

The older [T014 #56 / draft #57 decision record](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/mhac-t014/post-emission-retraction-falsifier/research/tangents/post-emission-retraction/DECISION.md) is unusually useful: 21 of 22 required fictional obligations remain independently unresolved despite bound correction messages. Its verbose uncertainty policy has no additional demonstrated logical benefit over the minimal one. Neither assertion is empirical. Rather than write another retraction oracle, this report asks what historical information would be sufficient even if a perfect observation of the current state were available.

[X006 #188](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/188) distinguishes a mirrored symbolic utterance from a genuine inverse. [#203](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/203) investigates state-changing diagnostic queries with origin tags, but optimizes query policies rather than receipts for a later fixed intervention. [#258 / #259](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/259) contrasts an oblivious fixed world with an adversary observing the audit draw. [#298](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/298) makes the source-law version part of the inference warrant. These distinctions compose here, not because their domains are identical but because each specifies a different missing input to the reconstruction problem. [#331](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/331) concerns forecast scoring; here preview means actual advance knowledge of a permissible intervention class, not a calibrated prediction of it.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity and validation read; first 100 returned open issue titles and 92 open PR titles/branches inspected. The search connector returned issue records even for its PR-qualified search, so the separate recent-PR listing is the basis for the PR count. Reviewed #56 issue, empty comment list, #57 decision artifact, #188/#203/#258/#298 scopes, #259 report, main quotient guard and #331 report. #331 exact-head workflow 45394622872 succeeded; structural check is not scholarly acceptance. No complete audit of all branches claimed. New issue #338 and empty comments reconciled; fresh isolated branch only. Canonical programme stages remain in progress.

## 2. Exact receipt alphabet (mathematics)

Let X be a finite nonempty set of original states, A a finite set of deterministic interventions f_a:X→Y. A receipt e(x) in an alphabet of m symbols is written before the action identity is known to the writer. Afterward the decoder observes the exact pair (a,f_a(x)) and e(x). Its target is x, not simply a new desired state. The action and final state observations are trusted, receipt delivery exact, and all permitted (x,a) combinations possible. This is an information model, not a claim that a physical actuator can restore x.

**Theorem 1.** If the action is known to the writer before the receipt is produced, the minimum uniform receipt alphabet is max over a,y of |f_a^-1(y)|, denoted F. If only the decoder knows the action, it is chi(G), where vertices are X and two distinct originals are adjacent if any permitted action maps them to the same output.

Proof: in the first case assign distinct ranks inside each action fibre and reuse ranks across fibres. A largest fibre proves necessity. In the second case a shared receipt on adjacent vertices produces an indistinguishable decoder input; every valid receipt assignment is a proper colouring. Conversely a proper colouring makes each fibre injective, so lookup recovers x. A random encoder cannot evade zero-error necessity: for every fixed shared seed of positive probability (or almost every seed in a general space, since worlds are finite), all worlds must decode exactly; without shared randomness, any positive-support symbol selection gives a deterministic valid code. F <= chi(G), but equality is not guaranteed.

Every simple graph is realizable. For each edge {u,v}, allow a distinct action that maps v to u, keeps u at u, and leaves all other originals fixed. The only nontrivial fibre has size two. Thus with any nonempty graph F=2, and the union graph is precisely the chosen graph. On the complete graph K_n, the late-bound receipt needs n symbols (ceil(log2 n) fixed bits), whereas a known pair action needs only two symbols (one bit). The gap is unbounded even though **no action individually destroys more than one bit of worst-case historical distinguishability**. Empty graph: one symbol suffices.

Example n=8: the operation may collapse any one of 28 pairs. Knowing the pair before the receipt permits a binary indicator selecting which member was present. Not knowing which pair will be collapsed forces eight distinct immutable tags. This is the one-shot zero-error decoder-side-information graph-colouring problem in a control/retraction setting, not a new coding-theory principle.

## 3. Exact partial preview and a failed generalization (mathematics)

Suppose a trusted scheduler sends one of k advance hint values h(a) to the receipt writer. The writer knows x and h(a), not necessarily a; the decoder knows a, f_a(x), and the receipt, so it can compute h(a). The hint is a deterministic function of the actual action, not the initial state. It incurs its own channel cost. Receipt tags may depend on the hint.

**Theorem 2.** For the pair-collapse construction, the minimum pair (k,m) is characterized exactly by chi(G) <= m^k, for positive integers k,m.

Necessity: each hint j has a receipt function c_j:X→{0,...,m-1}; its assigned edges must be properly coloured by c_j. The tuple (c_1(x),...,c_k(x)) distinguishes endpoints of every edge, so it is an m^k-colouring. Sufficiency: choose a proper chi(G)-colouring, encode its colours as k base-m digits (for m=1 the graph must be edgeless), assign each edge to any digit at which its endpoints differ, and use that digit as receipt. For each edge action the decoder sees the action and hence knows which digit scheme applies. Unmerged states are already uniquely identified by their post-action state.

For K_n, a one-bit receipt can be supported by ceil(log2 n) *hint values*, i.e. ceil(log2 ceil(log2 n)) fixed preview bits for n>=2. This is not clairvoyance at no cost: the scheduler must actually know the pair before the receipt is committed. It is a compression of action identity relative to a specified recovery objective, not a reconstruction of the full action at the encoder.

| Originals | Full action count | No preview: receipt bits | With one-bit receipt: hint values | Preview bits |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 6 | 2 | 2 | 1 |
| 8 | 28 | 3 | 3 | 2 |
| 16 | 120 | 4 | 4 | 2 |
| 256 | 32640 | 8 | 8 | 3 |

**Adversarial correction:** the product bound is necessary for general actions but no longer sufficient. In general, a hint class must contain entire actions whose union collision graph is m-colourable. One action may impose many edges simultaneously; assigning its edges separately may illicitly assign multiple hints to the same action.

A stronger counterexample than a single large fibre: use five actions, and a separate triangle of three originals for each of the ten triples of actions (30 originals). Within a triangle corresponding to actions i,j,k, assign its three distinct edges respectively to i,j,k; each of these actions collapses its assigned pair and leaves the remaining vertex fixed. Other actions are identity on that triangle. Across triangles each action is a disjoint matching, so F=2. The full union graph is ten disjoint triangles, chi(G)=3 <= 2^2. Any three actions together contain the full triangle associated with them, so cannot share a binary receipt. Any two actions together form paths or single edges in each triangle, so can share a binary receipt. Two hints would require partitioning five actions into two groups, one of which has at least three actions; impossible. Three hints work (2+2+1). Thus the pair-collapse product sufficiency fails **even though every individual action has binary-sized fibres and the overall graph is 3-colourable**.

The exact general criterion is a partition of actions into k groups, each of whose union collision graphs is m-colourable. Do not substitute an edge partition for an action partition.

## 4. Randomized receipt minimax error (mathematics)

Return to K_n pair-collapse actions. A world selects both a pair and one of its two endpoints as original state before a shared random seed is drawn. The writer uses that seed to pick an m-colour tagging; the decoder sees the seed, the exact action and output, and may use an independent fair tie-breaking coin. Errors are measured as worst-world probability of returning the wrong original, not average over a presumed distribution of actual worlds.

For 1<=m<=n, write n=mq+r, 0<=r<m. The sharp minimax error is

    E*(n,m) = [r q(q+1)+(m-r)q(q-1)] / [2 n(n-1)].

For m>=n it is zero. Proof: for a deterministic tag assignment with class sizes s_i, exactly sum_i C(s_i,2) unordered pairs collide. For a collided pair the two worlds have identical observations; their average error is at least 1/2 regardless of decoder. Uniformly average over pairs and endpoints to lower-bound the worst-world error, then average over random seeds. The minimum collision count occurs at balanced sizes (moving one element from a class of size at least two larger strictly decreases the sum). Hence the displayed lower bound. Achieve it by uniformly randomizing balanced colour assignments, making every pair collide with the same probability; decode uniquely when possible, otherwise use a fair coin. This attains the bound for every endpoint. The argument also lower-bounds private stochastic tags: sample a table of all hypothetical encoder draws independently of the world, reveal it to the decoder (which cannot hurt), and apply the shared-seed lower bound. This is a finite one-shot result, not a general advantage of randomized logging.

For n=8,m=2 the collision probability is 3/7, worst-world error 3/14, versus 1/2 for any fixed binary tagging with optimal fair tie-breaking. For n=256,m=2 the error is 127/510, approaching 1/4. For m=n-1 there is only one collided pair per assignment, giving error 1/[n(n-1)]. A low expected error does not imply the log is safe for every realized seed.

If instead the adversary sees the tagging before choosing both pair and original, every realized m<n colouring has a collision. With a private fair decoding coin the adversary can force conditional error >=1/2 and the fair tie policy attains 1/2. If the adversary sees *all* randomness including the decoder's tie-breaking choice before choosing the world, a deterministic wrong endpoint can be selected, and worst error is one. If the action is chosen after the draw but the original is fixed earlier, that is a different game; this theorem does not identify its value. Merely writing 'randomized log' is not a sufficient specification of the threat model.

## 5. Counterexamples and exaptation

**Missing action identity:** even bijections may need receipts. On X=Z_n, allow all translations x→x+a mod n. With known a, every map is invertible and one receipt symbol suffices. With a absent at both writer and decoder, all originals can produce final state zero via different actions; n distinct receipts are necessary and sufficient. This is a different confusability relation, including cross-action collisions. Recording a can be more economical than recording x on some domains; here it would require n action values. No blanket mandate to store either is justified.

**Physical counterexample:** an abstract operation can merge two original states and the receipt can identify which was present, while the only available subsequent actuator remains the same merge operation. If the original was the absorbed state, no available sequence can restore it. Conversely a command such as 'set output to zero' may establish a new acceptable target without reconstructing the original at all. Exact historical knowledge and operational controllability are distinct, and a receipt saying 'undo complete' cannot witness either by itself.

**Interpretive proposal:** the older T014 negative result becomes a positive research question about the information budget of prospective recovery. A candidate recovery receipt should declare the protected origin or decision class, action family, when the action identity/hint becomes available, final observation reliability, tag alphabet and retention lifetime, and separately which actions can actually restore an acceptable state and how that outcome is verified. A receipt is justified only for a declared downstream decision; if all origins sharing an observation have the same required remedy, the extra distinctions are dispensable. The graph theorem in this report targets exact origin recovery and may overstate the tag burden for a coarser remedy. This preserves X004's safe-collapse position and T014's warning that verbosity is not evidence of resolution.

Concrete synthetic falsifier: enumerate two distinct origins sharing the same retained action/output/tag; if the declared target differs, the contract fails. Then independently enumerate authorized restoration paths. A pass on the first check does not imply a pass on the second. Test missing action identity, late hints, seed disclosure and an unreachable original. No production undo/retraction mechanism or new canonical field is proposed. No actual user action or auditory comprehension has been measured.

**Original unrendered score (artistic):** eight opening pitches encode eight original states. A later instruction may coalesce any two pitches into the same note. A binary overtone is chosen before the coalescence. With no advance information, there is always a pair it cannot distinguish. With a trusted three-valued action hint, choose one of three binary pitch-index digits as the overtone. The ending sound may now identify the initial pitch, but no claim is made that the listener recognizes it. A score can reconstruct an opening note without returning the vibrating string to its earlier physical trajectory.

**Fiction:** The conservator receives a restoration certificate with a one-bit inscription. It is perfectly adequate for the damage she was told to expect. The next conservator receives the same inscription, but the damage has not yet been selected. They disagree on whether the certificate is complete. Neither is entitled to claim the instrument has been repaired.

## 6. Qualification and source extent

Run `node lab.js` in this directory. The first exact bounded-integer JavaScript execution of the main laboratory returned the following counts; the separately executed bundle control adds the last three. The lab constructs action maps, checks the actual decoder-input collisions separately from graph adjacency, enumerates hint partitions for small graphs, and directly verifies every possible endpoint in balanced randomized assignments. Counts overlap and are not independent experiments.

| Activity | Count |
| --- | ---: |
| Graph families, all graphs on 2–5 vertices | 1,098 |
| Direct receipt assignment checks | 4,554,154 |
| Hint partition checks (2–4 vertices) | 14,991 |
| Constructed hint class checks | 12,459 |
| Random-tag colourings (2–7 vertices, up to four tags) | 25,285 |
| Balanced-tag edge checks | 89,460 |
| Direct decoder world checks | 178,920 |
| Missing-action-identity checks | 238 |
| Bundle subsets and two-hint assignments | 32 / 32 |
| Three-hint bundle witness | 1 |

The mathematical arguments, not the finite grid, establish the general claims. No independent scholarly review, human participant, real-world restoration, or native Node/full-repo CI run is claimed by this report. The input model is synthetic. The laboratory includes the bundled-action falsification rather than assuming that the product bound generalizes.

**Source comparison:** H. S. Witsenhausen (1976), [The zero-error side information problem and chromatic numbers](https://doi.org/10.1109/TIT.1976.1055607), IEEE Transactions on Information Theory 22(5), 592–593. Publisher abstract inspected 24 November 2026: explicitly identifies graph chromatic number for the decoder-only side-information case, and contrasts transmitter side information. Full article not read; no priority claim for Theorem 1. The partial-preview construction is a direct restricted derivation, not an assertion of literature-wide novelty. C. H. Bennett (1973), [Logical Reversibility of Computation](https://doi.org/10.1147/rd.176.0525), IBM J. Res. Dev. 17(6), 525–532. Publisher abstract inspected on the same date: records intermediate results to avoid irreversible logical erasure and reconstructs input by retracing reversible operations. This supports the historical comparison with preserving information, not the claim that all physical interventions can be undone or that our receipt bound is a thermodynamic bound. No full-text appraisal or canonical source admission. No restricted material reproduced.

Disposition: two additive files in a new issue-scoped branch, Refs #338; draft pending exact-head repository qualification and substantive review. No changes to frozen protocol, live records, other workers' branches or central manifests. The point is not that every act needs a receipt. It is that the adequacy of an irreversible receipt may depend on the family of interventions that have not yet been chosen.
