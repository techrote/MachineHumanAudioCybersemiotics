# The Receipt That Forgives a Collision
## Exact noisy-optimum duality, distance-dependent semantic aliasing and joint quotient costs

**Refs #402 · 24 November 2026 · mathematical/synthetic expedition by one ChatGPT GPT-6.2 agent.** Self-reviewed, not peer reviewed. No human data, accepted Track E/G finding, operational privacy assurance or priority claim.

## Contents

1. Excavation — challenge the zero-error boundary in the preceding rigidity theorem.
2. Exact duality — characterize all optimal noisy receipts by zero-error complementary channels.
3. Distance and vocabulary — give sharp alias thresholds and a necessary alphabet size.
4. Joint quotient obstruction — distinguish separate alias witnesses from a shared channel.
5. Exaptation and negative controls — specify what the metrics do not establish.
6. Reproduction and provenance — report checks and scope limits.

## 1. Excavation

[The Receipt That Walks Away (#395)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/00d034a8977a9c1697e3d2a98ba852e545f08e65/research/expeditions/receipt-walks-away/README.md), §2, derives a sharp distance-dependent stability theorem assuming exact authorized recovery and a positive excess in the observer's guessing score. [The Receipt That Needs More Names (#379)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/8f0bc1e9335fe63913ca714d9a1008e7bb281918/research/expeditions/receipt-needs-more-names/README.md), §§2–4, permits reconstruction errors averaged over selected edge actions and optimizes vulnerability on odd cycles. The combination leaves an important corner unexplored: enforce a separate Bayes-error cap on EVERY edge, optimize privacy exactly, and ask which semantic distinctions survive. The result is not a near-optimality perturbation: exact optimality itself can coexist with complete aliasing of formerly distinguishable rows.

The accepted-main [X004 quotient guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md), Exact finite claim, tests exact decision sufficiency of deterministic quotients. Here we instead ask how much explicitly permitted statistical error is necessary to make a proposed quotient invisible to an observer, given the authorized decoder's different observations. [The Receipt That Cannot Share a Drawer (#347)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/486498ef2fafa1f1bf1ae1b75e70b586d068d269/research/expeditions/receipt-cannot-share-drawer/README.md), §§1–2, separates individual compatibility witnesses from a single shared witness. Its vertices represent actions; our equivalence classes represent originals. The same quantifier caution applies, not the same obstruction theorem.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity and validation inspected. First 100 returned open issue titles and first 100 open PR titles inspected (capped lists, not repository totals); targeted noisy receipt search and branch search found no competing expedition. #394 scope and empty comments, #395 exact report and draft PR metadata checked. #395 exact-head workflow 45481944552 succeeded (structural qualification only). Read #379 report through its odd-cycle and composition results, #347 through its obstruction proof, and X004. Created #402 and read scope/empty comments before making an isolated branch from main. No edits to canonical records, frozen methods or other workers' branches; no programme promotion.

## 2. Model and exact complementary-channel duality (mathematics)

Take a finite connected simple bipartite graph G with N>=2 originals, uniform X, and a family of pair-collapse actions, one per edge. Each action merges the two endpoints and otherwise leaves originals unchanged. The encoder sees X, not the chosen action, and emits a finite random receipt with row p_x(j). The authorized decoder sees the action, exact collapsed state and receipt; the observer sees the receipt alone. Actions do not depend on X. For each edge uv define overlap

    o_uv = sum_j min(p_u(j), p_v(j)) = 1 - TV(p_u,p_v).

The optimal authorized Bayes error for this action CONDITIONAL on a collision is o_uv/2, because the endpoint prior is balanced. Unconditional error for that action is o_uv/N. This is not a worst-endpoint or worst-random-seed guarantee. Enforce o_uv <= e for every edge, with 0<=e<1. Define m_j=max_x p_x(j), normalized observer vulnerability C=sum_j m_j=N V. For every edge,

    C >= sum_j max(p_u(j),p_v(j)) = 2-o_uv >= 2-e.

The lower bound is attained on any bipartite G by two rows (1,0) and (e,1-e) on its sides. Hence exact optimal normalized vulnerability is 2-e. At equality, for EVERY edge, o_uv=e and max(p_u(j),p_v(j))=m_j for EVERY column. The per-edge error budget is saturated, not merely averaged.

**Theorem 1 (complement duality).** At exact optimality define

    q_x(j) = (m_j-p_x(j))/(1-e).

These are probability rows: each numerator is nonnegative and sums to C-1=1-e. Every edge has disjoint q supports, by the columnwise max equality. Also

    C_q = sum_j max_x q_x(j) <= (2-e)/(1-e) = 2 + e/(1-e).
    TV(p_u,p_v) = (1-e) TV(q_u,q_v).

Conversely, for any finite zero-error q with C_q <= (2-e)/(1-e), set m_j=(1-e) max_x q_x(j), then add a column with q identically zero and capacity 2-e-sum_j m_j if positive. Set p_x(j)=m_j-(1-e)q_x(j). The row sums are one; every used m_j is attained in at least one row since any edge has disjoint q supports; and every edge has max(p_u,p_v)=m_j and overlap exactly e. Thus p is optimal and has precisely the claimed scaled TV. The extra column may be omitted at zero capacity. This gives the entire pair/equality feasibility region, not necessarily a bijection of fixed-size alphabets: an arbitrary capacity vector m dominating (1-e)max q can equivalently be retained to reconstruct p without a padding label. e=1 is a separate trivial constant-channel case.

This is an elementary complement transform specific to equal row totals, uniform prior, individual edge cap and exact optimal C. It is not a general equivalence between noisy and noiseless channels, nor a claim that the observer can calculate a complementary receipt from a single sampled p receipt.

## 3. Sharp distance bounds and the cost of one equality

Apply #395's zero-error theorem with slack e/(1-e), then rescale TV by 1-e. For graph distance L, let l=floor(L/2). The exact attainable intervals at optimal C=2-e are

| Distance | Minimum TV(p_u,p_v) | Maximum TV(p_u,p_v) |
| --- | --- | --- |
| Even | 0 | min(1-e,l e) |
| Odd | max(0,1-(l+1)e) | 1-e |

This includes adjacent originals, whose TV is forced to be 1-e. Every interval endpoint is attainable, and intermediate values follow from visible independent mixtures of optimal channels with disjoint labels. Attaining one pair's endpoint does not imply simultaneous attainability for every pair.

For completeness, the attaining construction need not assume the previous theorem: use a palette of measure 2-e, with complementary supports of measure H=1-e. Along BFS levels from u use E_i=[ih,ih+H) for even levels, h=min(e,H/l) when l>=1. Between consecutive even supports there is at least H outside their union; select an odd support of measure H there. At the final odd level choose a support outside E_l maximizing overlap with E_0, namely min(H,lh). For an even target use the preceding odd support as the following odd support. Extend beyond the target by repeating the final even/odd pair. Every edge joins consecutive BFS levels in a bipartite graph. Complements yield p supports of measure one. Partition at interval endpoints to obtain finite columns; for rational e one can instead use a common integer grid. A binary q colouring attains the other interval endpoints. The l=0 case uses the binary construction. The bound also follows directly from the #395 edge slack argument applied to q.

For an opposite-side pair at odd distance L=2l+1>=3, identical p rows first become possible at e=1/(l+1), i.e. conditional authorized Bayes error 1/(L+1). Example: L=199, e=1/100. Every edge has exactly 0.5% conditional error while the endpoints have identical receipt distributions; on the 200-state path unconditional error for each action is 0.005%. The full-state observer guessing score is optimal at 1.99/200, below the zero-error optimum 2/200. There is no graph-independent continuity modulus for this opposite-side distinction, even at exact noisy optimality.

**Theorem 2 (sharp alphabet threshold).** At the first alias point for L=2l+1>=3, at least L receipt names are necessary, and L suffice, for any such pair on any connected bipartite graph.

Proof: along a shortest path the q rows of the two endpoints coincide. Identify the endpoints to get a zero-error channel on the odd cycle C_L. Every column has support at most l. The L row sums give C_q >= L/l, equal to the upper bound (2-e)/(1-e). Equality forces every positive column to be uniform on a maximum independent set. All such sets are rotations S_j={j,j+2,...,j+2(l-1)} mod L: cyclic gaps are at least two with exactly one extra unit. Denote aggregate column weights by a_j. Row equations sum a_(i-2t)=1 over t=0,...,l-1. Subtract consecutive equations at i and i-2: a_i=a_(i-2l)=a_(i+1). All L weights are 1/l and must occur. Each q name is an original p column, so the lower bound transfers. For sufficiency take these L complementary supports of l atoms of weight 1/(l+1); the p rows contain the other l+1 atoms. Assign by BFS level modulo L through the target; afterward alternate the last two levels. Adjacent levels never share q atoms. Both endpoints use identical p rows. No padding label is needed.

A two-name optimal channel cannot exhibit this migration even with long paths: write p_x=(z_x,1-z_x). Then C=1+max z-min z=2-e. Each edge must span the entire range, so connectedness forces two fixed side rows. This is a strict countercontrol to interpreting vocabulary size as irrelevant to the noisy optimum.

## 4. Simultaneous aliases are a different optimization

Let ~ be any proposed equivalence relation on originals, requiring p_u=p_v whenever u~v. Contract the classes to obtain the quotient collision graph H (merge parallel edges). If an edge becomes a loop, aliasing is impossible for e<1, because adjacent p rows must have TV=1-e. Otherwise H has at least one edge and the same equality relation holds for q by Theorem 1.

**Theorem 3 (exact joint threshold).** Write f=chi_f(H), the fractional chromatic number. Then optimal p with all prescribed aliases exists if and only if

    (2-e)/(1-e) >= f,

or equivalently e >= (f-2)/(f-1). Conditional Bayes error threshold is half this value. The case e=1 permits all aliases. Necessity: q descends to a zero-error channel on H, and #379's subset-weight reduction (level-set columns) gives C_q >= chi_f(H). Sufficiency: a fractional colouring with exact unit coverage yields q; the complement transform constructs p. This requires equality within specified classes, not inequality between every distinct pair of classes. Additional aliases are permitted.

This gives a precise noisy relaxation of a quotient audit, under the stipulated observer and utility. In the one-pair odd-distance case, identifying opposite vertices creates an odd cycle along the shortest path, and the BFS construction supplies the matching upper bound.

**Counterexample to pairwise certification.** Take the crown graph on 2r vertices a_i,b_i, i=1,...,r, with every a_i-b_j edge except i=j, r>=3. Connected and bipartite. Each proposed alias a_i~b_i is at distance three, so any SINGLE alias is feasible at e=1/2. But imposing all r aliases contracts the graph to K_r; f=r and the joint threshold is e=(r-2)/(r-1). For r=6, each pair individually needs 25% conditional Bayes error; all pairs jointly require 40%. As r grows the joint threshold tends to chance-level recovery on the colliding pair. Explicit joint witness: use r labels; p_(a_i)=p_(b_i) uniform on all labels except i. Each edge overlap is (r-2)/(r-1), C=r/(r-1)=2-e. This is not a result about independent releases or their composition; it concerns one shared channel satisfying many equality requirements. Separate witnesses cannot be silently combined.

## 5. Exaptation and negative controls

**Negative control: averaging actions.** A star has one central vertex and M leaves. Give one leaf the same deterministic receipt as its centre, all other leaves the other receipt. C=2; average conditional error across uniform edge actions is 1/(2M), arbitrarily small, but one edge has conditional error 1/2 and identical endpoint rows. The distance theorem assumes the per-edge cap at EXACT optimal C, and cannot be transplanted to this aggregate evaluation. A prior-weighted average may be legitimate for expected loss, but does not certify every action. Likewise per-edge Bayes error is an average of two endpoint risks; it need not bound each by e/2. A worst-world guarantee needs an explicit minimax decoder criterion.

**Interpretive hypothesis:** a semantic system optimized for broad recognition, anonymity, or a global score may lose an important long-range distinction even at the exact optimum for a slightly relaxed local correctness contract. Conversely, deliberate aliases may be desirable, in which case exact recovery and semantic privacy can conflict. Do not call either preference a finding about people.

**Test-only exaptation:** before accepting a receipt or auditory naming design, declare the actual observer and decoder observations, error aggregation, population, vocabulary cap and required alias/equality classes. Construct a finite collision graph from the permitted interventions and a quotient for proposed shared names. Measure decoder fibre losses separately; compute normalized guessing score and pair-specific TV. For a finite graph use fractional-colouring certificates or bounded exact search when tractable. Theorems above provide exact unit-test fixtures and counterexamples, not proof of acoustic or cognitive equivalence. For e>0 the labels are distributions, not deterministic names; X004's exact deterministic guard still applies to a different contract. If a decoder needs a common acceptable remedy rather than the exact original, revisit the collision graph itself.

**Artistic instruction (not evidence):** create a symbolic chain of 199 transitions with 199 receipt names; each state uses 100 names and excludes the other 99. Rotate the excluded alternating cycle sets; repeat the initial distribution at the terminal state. A listener with the intervention result can make a different inference from a listener without it. No audio generated and no listener response claimed.

**Fictional miniature:** Two archivists agree to forgive one ambiguous receipt in two hundred conditional encounters. The first optimizes the register and the second asks whether the first and last names still distinguish their origins. They do not. The first shows the optimum; the second asks which question was optimized.

## 6. Reproduction and provenance

Run the dependency-free [lab.js](lab.js) with Node. It uses integer counts, directly builds the oriented-collapse observation fibres, and compares the actual sum-minus-maximum Bayes loss with the edge cap. An independent finite-grid path oracle enumerates all unordered column-capacity partitions of 2D-a (D<=4, 0<=a<D), all bounded integer rows and their overlap-compatible transitions, and checks exact reachable TV extrema at distances 1..9. At first-alias points D=2,3,4 and a=1 it checks minimum palette size 3,5,7. This enumerates bounded grids, not all real channels. The general lower bounds are analytical; the quotient theorem is not proved by sampling.

Initial JavaScript execution: 218 labelled connected bipartite graphs (n=2..5), 62,220 constructed pair-extremum witnesses, 8,546,616 decoder observation cells, 62,250 pair checks including the cycle family, 63 oracle palettes, 16,949 candidate row transitions, 20,056 reachable endpoint comparisons, 20 crown witnesses and one average-error control. All assertions passed. Counts overlap; they are not independent scientific experiments. Same AI author wrote proof and code; the oracle is methodologically distinct, not independently authored. Full checkout validation, native Node replay and substantive independent review were not performed in this initial execution; exact-head replay and CI status are separately recorded on the PR.

External source comparison: Král’, Krnc, Kupec, Lužar and Volec, *Extending Fractional Precolorings*, SIAM J. Discrete Math. 26(2), 647–660 (2012), [DOI 10.1137/110828988](https://doi.org/10.1137/110828988), publisher metadata and abstract inspected on 24 Nov 2026. It concerns extension of prescribed fractional precolourings at distance; related to #395's geometric construction. The complement transform and noisy quotient criterion here have direct proofs, but no exhaustive prior-art search or claim of scholarly novelty. Choi, *On Sparsity Conditions Guaranteeing a Fractional Coloring*, J. Graph Theory (2026), [DOI 10.1002/jgt.70108](https://doi.org/10.1002/jgt.70108), abstract inspected for the established disjoint-set (a:b)-colouring formulation only. No full-text reading or result imported. Earlier MHAC reports are synthetic inputs, not accepted evidence. No human gates purportedly satisfied; no shared manifest touched. Keep this exploratory issue/PR open for substantive critique and qualification.
