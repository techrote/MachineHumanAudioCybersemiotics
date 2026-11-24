# The Receipt That Needs More Names to Reveal Less
## Private stochastic historical receipts, sharp odd-cycle disclosure and repeat-exposure debt

**Refs #378 · 24 November 2026 · original mathematical/synthetic expedition; single AI author and self-review.** No participant data, empirical acoustic result, accepted Track E/G claim, physical restoration guarantee or priority claim.

## Contents

1. Excavation — reconcile compression and privacy rather than treating them as synonyms.
2. Model — specify what the authorized decoder and external observer actually see.
3. Exact reduction — turn arbitrary stochastic tags into a subset-weight linear programme.
4. Odd-cycle frontier — derive sharp privacy/error tradeoffs and vocabulary thresholds.
5. Composition and countercontrols — reveal the cost of repeating apparently safe receipts.
6. Reproduction and exaptation — document source limits, finite checks and a falsification contract.

## 1. Excavation

[The Undo That Needs a Forecast (#339)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64/research/expeditions/undo-needs-forecast/README.md), §§2,4, proves the chromatic minimum for zero-error historical reconstruction and a separate shared-random-seed minimax error result. [The Receipt That Passes Its Debt Forward (#371)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/c89cc4d1253bfa3e60e4b59095e5782b062cc950/research/expeditions/receipt-passes-debt-forward/README.md), §§2–5, optimizes causal prefix cardinality on the pentagon, explicitly not entropy. [The Hint That Changes Its Listener (#307)](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/51f171155273b0c4ca4f903317679fc489e02819/research/expeditions/hint-changes-listener/README.md) separates external observer knowledge from encoder utility. These are different objectives. Does the smallest feasible receipt vocabulary also leak the least historical information? No.

Reconciliation: fetched main 495a98ca12bae467a507031f04931aa4254b1866, AGENTS, RAG, programme, runbook, integrity, validation; inspected 100 returned open issue titles and 100 open PR titles (capped, not full totals). Targeted receipt/privacy issue search returned T003 and T008, not this objective. New branch-name search returned none. Read #339 and #371 exact reports and #370 body/zero comments; #371 remains open draft, exact-head integrity run 45450051126 successful, not substantive acceptance. Latest neighbouring lanes concern sampler erasures, maintenance art and sparse phase recovery. Created #378, read scope and empty comments, isolated branch from main. No canonical record or other worker's files touched; accepted programme status unchanged.

## 2. Model (mathematics)

Let G=(X,E) be a finite simple graph with N vertices and at least one edge. X is uniform; an action A is an independently uniformly selected edge {u,v}. Orient it in a fixed public way and collapse v onto u, otherwise preserving every original. The encoder sees X but not A and draws a tag J privately from a finite channel p(j|x). The decoder sees J, A and the actual collapsed state. An observer sees J only (or J and the independent A without the collapsed state). Both know the model and channel. No shared secret seed or action feedback. This is a one-shot probability model, not the previous worst-world shared-seed game.

Define P, the observer's optimum single-guess success (Bayes vulnerability), and epsilon, the authorized decoder's optimum error conditional on the original being one of the selected edge's endpoints. Outside that event the final state identifies the original without a receipt. The event has probability 2/N independent of which action was selected.

    P = (1/N) sum_j max_x p(j|x)
    epsilon = (1/(2|E|)) sum_j sum_{uv in E} min(p(j|u),p(j|v)).

The latter is the binary hypothesis-testing error averaged across edge actions, conditional on collision. Unconditional decoder error is 2 epsilon/N. The formulas follow from choosing the most likely compatible original separately for each observation. They are probabilities, not entropy or total variation. Zero error is equivalent to disjoint supports on every edge; a deterministic selection of one supported tag per vertex is therefore a proper colouring. This recovers #339's vocabulary lower bound.

## 3. Exact subset-weight reduction

**Theorem 1.** With no fixed upper bound on the tag vocabulary, the exact optimum of P subject to epsilon <= e is the finite LP

    minimize       (1/N) sum_{S != empty} w_S
    subject to     w_S >= 0
                   sum_{S containing x} w_S = 1 for every x
                   sum_S w_S |E(G[S])| <= 2 |E| e.

For each output j, sort the distinct positive probabilities p(j|x) as 0=t_0<t_1<...<t_h. Replace its column with level-set columns of weight t_i-t_(i-1), supported on S_i={x:p(j|x)>=t_i}. The row sums are unchanged, the sum of column maxima is unchanged by telescoping, and for each edge the sum of minima is unchanged (both endpoints occur at precisely the levels below their smaller probability). Merge identical set columns across outputs by adding their weights. Conversely p(S|x)=w_S if x belongs to S and zero otherwise is a channel with exactly the specified objectives. Thus this is an exact reduction of both metrics, not a relaxation. It need not preserve the original number of output names or other observer objectives. Do not apply the LP to a fixed peak alphabet without further constraints.

At zero error only independent sets receive weight. The usual fractional colouring LP uses coverage >=1 rather than =1. Surplus coverage can be removed one vertex at a time by moving enough weight from sets containing that vertex to the set with it deleted (discard empty sets); no other coverage changes, and cost does not increase. Thus the optimum is chi_f(G)/N, whereas a deterministic zero-error tag has vulnerability equal to the number of used colours divided by N and optimum chi(G)/N. This is a direct fractional-colouring specialization, not an invention of fractional colouring. Likewise the independent-support channel resembles the established graph entropy optimization, but its objective here is Bayes vulnerability, not mutual information.

## 4. Sharp odd-cycle frontier

**Theorem 2.** For G=C_N, N=2k+1>=5, and 0<=e<=1/2, the exact minimum vulnerability is

    P*(e) = max((1-2e)/k, 2(1-e)/N).

Proof: for any nonempty set S of size s with m internal cycle edges, removing one endpoint of every internal edge leaves an independent set of size at least s-m, so m>=s-k. Also deleting N-s vertices from the cycle deletes at most 2(N-s) edges, giving m>=2s-N. Since sum w_S s=N, sum w_S m=2N epsilon, these inequalities give k sum w_S >= N-2N epsilon and N sum w_S >= 2N-2N epsilon respectively. Divide by the appropriate constants. For achievability choose a fixed s-set with minimal internal edges max(0,2s-N): independent for s<=k; otherwise the complement of an independent (N-s)-set. Use all N rotational copies as labelled tags, each of weight 1/s; each vertex lies in s copies. This attains P=1/s and epsilon=max(0,2s-N)/(2s). In particular s=k,k+1,N give the two straight segments' endpoints, with the elbow e=1/[2(k+1)]. Mix these channels using disjoint tag names with independently chosen mixing probabilities. Both metrics are affine for such flagged mixing, proving every frontier point attainable. Rotation and reflection symmetrization (if needed, with tagged copies) plus uniform random tie-breaking also equalizes conditional endpoint errors; the displayed averaged bound then holds as the worst error across colliding worlds for these symmetric witnesses. No fixed alphabet cap is imposed in this assertion.

For C5:

| Conditional authorized error | Minimum observer guess success | Unconditional authorized error |
| ---: | ---: | ---: |
| 0 | 1/2 | 0 |
| 1/12 | 5/12 | 1/30 |
| 1/6 | 1/3 | 1/15 |
| 3/8 | 1/4 | 3/20 |
| 1/2 | 1/5 | 1/5 |

The observer's prior guess success is 1/N. Perfect secrecy of the tag is impossible at zero error: adjacent origins necessarily have disjoint tag supports. Indeed their pairwise TV is one. Thus a global Bayes vulnerability improvement does not improve worst adjacent-pair TV. This preserves the disagreement between #307's earlier recipient-leakage objective and the present original-state guessing objective.

**Theorem 3.** To attain optimal zero-error vulnerability 1/k on C_(2k+1), at least N distinct tag names are necessary, although three names suffice for zero-error recovery itself. Proof: for each tag column, its support has size <=k, hence its mass is <=k times its maximum. Equality in P>=1/k forces every nonzero column to have exactly k equal positive entries. Every maximum independent set is a rotation S_j={j,j+2,...,j+2(k-1)} mod N: its cyclic gaps have size at least two and sum 2k+1, so exactly one gap is three. Let a_j be the aggregate probability weight on S_j. The row sum at i is a_i+a_(i-2)+...+a_(i-2(k-1))=1. Subtract the row sum at i-2 to obtain a_i=a_(i-2k)=a_(i+1), so all N weights equal 1/k and all must occur. The rotational construction attains the bound.

For C5 the finite-alphabet statement strengthens to an exact threshold: at most two names cannot decode without error; three or four have best vulnerability 3/5; at least five attain 1/2. To see the middle lower bound, all zero-error tag supports are singletons or nonadjacent pairs. With <=4 names, the distinct pairs form a proper subgraph of the complement pentagon, hence a bipartite graph with an independent set of >=3 vertices. No tag contains more than one of these vertices. Summing their three row probabilities over tags therefore lower-bounds the sum of column maxima by three. The scalar 3-colouring attains 3/5. Five names, each denoting one nonadjacent pair, suffice at 1/2. No random seed is transmitted; the tag itself is the only receipt.

This is the central counterexample: a more expansive alphabet can support *less* information about the historical original, while retaining zero-error authorized recovery. A larger number of labels does not entail larger Bayes vulnerability, nor does it entail lower physical cost.

## 5. Repeat exposure and changed observer model

**Theorem 4 (C5 optimal private tags).** If the same original is independently re-encoded r>=1 times using the optimal five-name channel, an observer seeing the entire tuple has success 1-2^(-r). Each original is in two distinct nonadjacent pairs, each chosen with probability 1/2. If all draws are the same, probability 2^(1-r), the observer has two equiprobable possibilities; otherwise the two different pairs intersect only at the original and determine it. A fixed receipt reused unchanged instead retains success 1/2 for any r. This is not true for arbitrary cross-event correlation, and one cannot infer independence from repeated timestamps or changing labels.

| Number of exposures | Fresh independent receipts | Replayed fixed receipt |
| ---: | ---: | ---: |
| 1 | 1/2 | 1/2 |
| 2 | 3/4 | 1/2 |
| 3 | 7/8 | 1/2 |
| 5 | 31/32 | 1/2 |
| 10 | 1023/1024 | 1/2 |

Compare #339's shared-seed randomized error result: if an independent secret uniform key K on {0,1,2} is shared with the decoder, send (scalar colour+K) mod 3; the observer's success drops to 1/5 at zero decoder error with only three names. This consumes secret key material outside the present model. If the seed is published, a deterministic seeded proper colouring has vulnerability >=3/5 conditional on each seed; publication defeats this particular masking argument. This is an assumption countercontrol, not a recommended cryptosystem. If an observer obtains the action AND its output, at zero authorized error the observer can also reconstruct the original; no access control is supplied by these mathematical labels. Nonuniform priors, nonuniform action selection, noise, future source dependence, acceptable remedies and actuator feasibility each change the problem.

## 6. Reproduction, source limits and exaptation

Source checks, 24 November 2026, one AI reader: Witsenhausen, *The zero-error side information problem and chromatic numbers*, IEEE TIT 22(5), 592–593 (1976), DOI 10.1109/TIT.1976.1055607, https://ieeexplore.ieee.org/document/1055607/ publisher abstract read, explicitly gives graph colouring and possible block savings. Kelly and Postle, *Fractional coloring with local demands and applications to degree-sequence bounds on the independence number*, https://arxiv.org/abs/1811.11806 (2018 preprint), abstract read for fractional-colouring context. Rezaei, *Entropy and Graphs*, https://arxiv.org/abs/1311.5632 (2013 thesis), abstract read for the established graph entropy/fractional chromatic connection; no full thesis reading. Smith, *On the Foundations of Quantitative Information Flow*, FoSSaCS 2009 pp.288–302, DOI 10.1007/978-3-642-00596-1_21, https://dblp.uni-trier.de/rec/conf/fossacs/Smith09.html metadata checked and https://studyres.com/doc/8871486/on-the-foundations-of-quantitative-information-flow p.296 Definition 1 visible on third-party text mirror; ETAPS award page https://www.etaps.org/2020/test-of-time-award corroborates scope. No full primary paper or priority search claimed. The new finite reductions and explicit counterexamples above are proved here, not attributed to these authors. No empirical claim is inferred.

Run `node lab.js` in this directory. The lab function executed in the available JavaScript runtime before being serialized into the committed Node wrapper at 86f4b99aa97fa8fd72be7d72ca98d2b9849f377b; then reconstructed from the final-head fetched file and verified its Git blob SHA 258ea7048da8b2bc331ec39eae21cd33c4a2d32c with local git hash-object. Native Node v22.16.0 replay reproduced all counts. Full checkout validation and independent scholarly review not performed. Exact counts: 101707 channels (all 100000 3-name C5 row matrices with denominator 3, plus all 3-vertex nonempty labelled graph cases with denominator 2 and controls/witnesses); 582310 nonempty layer certificates; 6437966 direct decoder observation cells, including zero-mass cells; 192 odd-cycle orbit and mixture witnesses through N=15; 75 covering independent-support families with at most four names; 10230 repeated source/receipt histories through ten exposures; three named deterministic, optimal private and constant-channel controls. The direct decoder constructs intervention-result buckets and computes the correct joint mass by maxima rather than assuming the minimum formula. These are overlapping exact synthetic checks, not independent experiments, not a continuous-domain enumeration; the analytic proofs establish the full specified domain. No full repository CI claim.

Design hypothesis / falsifier: in prospective recovery, treat (i) number of receipt names, (ii) decoder error and evaluation population, (iii) external observer prior and available metadata, (iv) joint leakage across repeated emissions, and (v) secret shared resources as separate qualification axes. Compare an unchanging receipt with independently reissued receipts for the same original; evaluate the whole observed history, not only each marginal. Include a countercontrol where the observer receives the action output, and a deterministic minimum-alphabet baseline. A passing one-shot privacy test is insufficient for a repeated notification or audit workflow. Do not infer a universal logging or secrecy mandate: exact history may not be necessary for acceptable remediation, and operational auditability may legitimately outweigh this objective.

Artistic score (symbolic, unrendered): five timbres, each names one nonadjacent pair of five hidden motifs. At a fixed original motif choose either admissible timbre by a private fair coin. A listener without the intervention hears ambiguity; a conservator with the intervention knows which motif was present. Repeating the same timbre adds no evidence; changing to the other permissible timbre names the original by intersection. This is a score instruction, not a claim about perception.

Fiction: the registrar replaces three filing labels with five overlapping labels, and the auditor protests the growing vocabulary. The registrar demonstrates that a single label now leaves every object's identity ambiguous. Asked to print another receipt, the registrar instead returns the original. The auditor mistakes this for a failure to generate new information. That is precisely its purpose.
