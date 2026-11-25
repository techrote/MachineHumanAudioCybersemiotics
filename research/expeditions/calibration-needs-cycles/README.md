# The Calibration That Needs Only Its Cycles
## Sparse factorial audits, circulation certificates and target-specific observability

Refs #500 · 25 November 2026 · mathematical and synthetic-computational expedition · one GPT-6.2 author, self-review only. No empirical, operational security, or scholarly priority claim.

## 1. Archaeology and the objection

[Pinned #489 report](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/93edb0e2de0c9239b1a4916c70c25d01204b81a6/research/expeditions/renderer-unspoken-context/README.md), §§2–6, demonstrates a context-conditioned renderer invisible to separately pooled source and word error histograms, even with all proper error marginals calibrated conditionally. Its proposed repair is a factorial audit. This expedition challenges the implied need to measure every factorial cell. The original counterexample remains valid; the minimum identifying audit depends on which source/word combinations actually occur and which distinctions are required.

[Accepted X004](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md) distinguishes necessary separation from safe collapse, in a deterministic finite setting. [Draft #411](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/5140eb0d86b04dc6f4abc272dd6fdb77445f1ed9/research/expeditions/receipt-protects-wrong-secret/README.md), §§2–4, gives a different transport reduction for target privacy. Here the transport object is not a receipt assignment but an unidentified interaction in the calibration table. The project foundations separate semantic message, rendering policy and acoustic output; the present theorem concerns exact finite calibration of that boundary.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity, validation, project foundations and X004 inspected; first 100 returned open issue and 100 PR titles inspected (not full inventories). Targeted renderer/cycle search and renderer branch lookup did not identify this scoped audit. #488 issue and comments (empty), #489 report, metadata and successful exact-head Research integrity workflow inspected; #489 remains draft. Read #500 and empty comments, refreshed main, created isolated branch. No accepted empirical status changed.

Nearby established mathematics: De Loera, Kim, Onn and Santos, *Graphs of transportation polytopes*, JCTA 116 (2009), 1306–1325, [abstract and bibliographic record](https://cris.technion.ac.il/en/publications/graphs-of-transportation-polytopes/) and [arXiv abstract](https://arxiv.org/abs/0709.2189), inspected at abstract/metadata level only. The row/column nullspace and forest argument are elementary standard graph/transport mathematics, proved below; the MHAC application to economical conditional-renderer and target audits is the proposal, not a new graph-theory result. No comprehensive prior-art review.

## 2. Exact identifying audit (mathematics)

Let X be a finite original/context, W a finite transmitted word, and p(x,w)>0 on a known support S, with total mass one. Make a bipartite graph G with one edge per supported cell, directed from context to word. Let n be its vertex count (isolates may be included), e its edge count, c its number of connected components. Assume known source and word pooled conditional error distributions, compared against a specified reference renderer R0(e_pattern|x,w). For the necessity results assume the reference has strictly positive conditional probability for every error outcome on every supported edge. Let R be a candidate renderer with matching pools; direct probes identify full conditional distributions for selected supported cells.

First use the proper-subset binary-error contract of #489. Write chi(z)=(-1)^popcount(z), L=2^k and R=R0 + a(x,w) chi(z), where R0 and R meet that contract. Define F(x,w)=p(x,w)a(x,w). Equality of the complete source and word pools is precisely zero signed divergence B F=0 for the oriented incidence matrix B: every row and column sum of F vanishes. A direct cell probe pins F to zero if it matches reference. The unidentified perturbation therefore lies in the circulation space of the unprobed graph.

**Theorem 1.** With a strictly interior reference, pooled equality plus exact cell probes certifies equality of the full conditional renderer on its support iff the unprobed graph is a forest. The exact minimum number of extra full-cell probes is e-n+c.

Proof: in a forest, any leaf's single incident edge must carry zero flow. Remove leaves until all edges vanish. Conversely an unprobed cycle supports alternating positive and negative flow, preserving all pools. Scale it sufficiently small that every conditional error distribution remains nonnegative; strict interior and positive p guarantee a nonzero feasible scale. A maximum forest retains n-c edges, so its complement realizes the lower bound. Deleting fewer than e-n+c edges cannot leave a forest. This is valid for disconnected graphs too.

The same forest sufficiency and necessity hold WITHOUT the parity restriction for arbitrary finite error alphabets of at least two outcomes: define a flow F_z for each outcome z, with zero divergence, and sum_z F_z=0 at every cell. Forest elimination works coordinatewise; a cycle can put opposite small circulations in two distinct outcomes. In this general model a full cell probe must measure all error outcomes. In the parity model one scalar (e.g. full parity contrast) suffices because all other degrees of freedom were already fixed.

Boundary qualifications: if the reference has zero probabilities the cycle perturbation may be infeasible; the forest criterion remains sufficient, not necessarily necessary. Structural zeros p=0 are NOT measured cells and the theorem says nothing about future support changes or interventional combinations outside S. Exact equality with R0 does not establish source blindness unless R0 actually has that property.

**Weighted audit.** Give each additional cell probe a nonnegative cost. The cheapest fully identifying set is the complement of a maximum-weight spanning forest (cost of all edges minus maximum retained cost). Any cheaper putative set has a forest complement by Theorem 1, and that forest can be extended to a spanning forest without increasing the probe cost. Maximum-weight Kruskal therefore constructs an optimum. This cost is a declared per-cell design cost, NOT sample size or measured experiment time.

For a complete a-by-b table the exact count is (a-1)(b-1), not ab. For a tree support it is zero. Sparsity alone is not the explanation: an equally sparse graph containing a cycle has an unidentified direction.

## 3. When the remaining cycles do not matter (mathematics)

The preceding theorem solves full identification; it can be overly expensive when only a single declared target is required. For a balanced protected binary H=h(X) in {-1,+1}, let Y=W XOR E. Assume the parity perturbation model above. The change in E[H chi(Y)] from reference is

    L * sum_(x,w in S) h(x) chi(w) F(x,w).

Proof: sum the conditional difference over error patterns, using chi(w XOR z)=chi(w)chi(z), chi(z)^2=1 and L possible errors. Set the edge weight g(x,w)=h(x)chi(w).

**Theorem 2.** After the exact matching probes, the target's parity contrast is uniquely determined by the pools iff the oriented alternating sum of g around every remaining cycle is zero, equivalently g is a vertex-potential difference on the remaining graph. Strict interior is assumed for necessity.

Proof: a potential difference pairs to zero with any conserved flow by summation over vertices. If a cycle has nonzero signed g-sum, place a small nonzero circulation on it as above; the target changes. If all cycle sums vanish, pick a root in each component and integrate g along paths to define a consistent potential. A spanning forest plus one fundamental-cycle check per extra edge suffices.

In the particular balanced uniform-word-per-H setting where the reference received-word distribution is uniform for each H, the new row is uniform plus a parity term. Because matching word-pooled errors fixes the unconditional output, the two coefficients are opposites; the target's Bayes guessing probability is exactly 1/2 + |E[H chi(Y)]|/2. Thus Theorem 2 also characterizes whether this particular protected target stays at chance. For nonuniform baseline rows, the parity contrast still has the stated identification theorem, but do not automatically equate it with the complete Bayes score.

For an arbitrary finite error alphabet and arbitrary declared linear channel statistic, the general counterpart uses a cycle test on the differences between its outcome-specific edge weights; an arbitrary nonlinear statistic may need more work. No universal target-only privacy certificate is implied.

### Concrete selective-audit witness

Take two equally likely contexts A,B, four uniformly distributed words 00,01,10,11, and q=1/4. All eight cells supported. The reference conditional error distribution on 00,01,10,11 is (10,2,2,2)/16, centered as in #489. Let a(x,w)=(2/16)h(x)chi(w). All complete source and word error pools match; both one-bit error rates equal 1/4 in each cell. Direct received rows are (24,8,8,24)/64 and its complement (8,24,24,8)/64. Guessing H improves from 50% to 75%, and no single received bit reveals H.

Full identification needs 8-6+1=3 probes. To certify this particular target at chance, measure just the A cells for the two odd words 01 and 10. Remaining cycles involve only the even words, whose g-sums vanish. The two even words may still support a nonzero circulation. One probe cannot suffice: at least three complete columns remain, containing both parities, hence a harmful rectangle. So two is the exact selective minimum, with one fewer probe than full identification.

Generalization for two contexts and b words with nonempty parity classes of sizes b0,b1: full audit costs b-1 probes; selective audit costs min(b0,b1) probes. Every remaining complete column of one class can coexist harmlessly with others of that same class; one complete column of each class creates a harmful rectangle. At least one edge must be probed in every column of at least one entire class. This argument assumes equal probe costs and positive cell weights, not necessarily uniform p for identification of the linear contrast.

This is a concrete objection to reflexively preserving every distinction. A target-specific audit can be smaller precisely because some hidden interactions cannot affect the declared target. But a newly declared target may require those same interactions, and a harmless cycle is not source blindness.

## 4. Exactness is not a finite-sample guarantee (mathematics and design hypothesis)

Let residual signed divergence b_v represent approximate pool matching, and suppose a set of probes leaves a forest T. A tree edge e partitions its tree into two pieces when deleted; choose one side U. Summing divergence over U gives, up to orientation,

    F_e = sum_(v in U) b_v - sum_(probed edges crossing U) signed F_j.

Thus if the divergence errors are bounded by beta_v and the probed flow errors by delta_j, then

    |a_e| <= [sum_(v in U) beta_v + sum_(probed crossing j) delta_j] / p_e.

One may take the smaller bound from the two sides. This is a deterministic error-propagation inequality, not a confidence interval. Rare cells can be badly conditioned because division by p_e magnifies errors. Exact minimum count or cost does not establish statistically efficient design. A redundant probe may improve conditioning or detect a false support/measurement model; an independently specified finite-sample design must address uncertainty, multiple comparisons, selection, drift and unobserved cells. Pool and probe statistics must share the same reference and sampling law. In continuous or adaptive renderers, the finite additive-error model itself needs qualification.

Design hypothesis for the Observatory/Grammar/Interaction lanes: retain a known support graph and declared baseline. Compile the mandatory pools, select probe cells by a maximum-weight forest, then retain a signed cycle witness whenever a required target is not identified. For target-only scope, evaluate potential consistency on remaining edges. Prefer explicit architectural separation where possible; measurement cannot qualify unobserved contextual pathways. No actual listener or acoustic study is performed here.

Falsifiers: a feasible nonzero conserved perturbation on a forest; an interior cyclic support with no perturbation; a target-changing flow with zero cycle sums; a cheaper exact full audit than the forest complement; or a direct contradiction of the cut inequality. An actual renderer violating the model's support or additive-error assumptions limits transfer, rather than refuting the abstract theorem.

## 5. Reproduction and disposition

Run [lab.js](lab.js) with Node. Development execution in V8, with console shim, passed: all 512 subgraphs of K3,3; 262,144 ternary-flow candidates; 1,184 conserved flows; 1,024 target-potential comparisons; 19,683 probe subsets; 512 comparisons of weighted and cardinality minima; 32 direct channel cells; all 256 K2,4 probe subsets. A simple oriented cycle is ternary, so this independent finite oracle detects any nonzero circulation and any nonzero cycle contrast in those graphs. The direct channel computation uses integer arithmetic, not fitted results. Counts overlap; they are not independent empirical observations. Native full-checkout validation, exact-head structural CI and independent substantive review are outstanding. No human study, source register, shared manifest or frozen protocol altered.

Interpretive conclusion: a calibration table is not just a list of cases; the topology of its allowed combinations determines what separate measurements leave unidentified. The cycle rank is the missing measurement budget, not a measure of meaning.

Fictional miniature (not evidence): an archivist records every singer's average errors and every score's average errors. Four performances form a loop. The errors walk around it without changing either register. The archivist samples one performance and the loop closes. A second archivist asks whether the loop could ever change the question she cares about.
