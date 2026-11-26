# The Choir That Cannot Admit Another Singer

Expedition #658 — 26 November 2026. Original mathematical investigation and synthetic compositional specimens. Not a selected Track E/G result, human experiment, operational assurance claim or priority claim.

## Question: how far can a local law travel?

Three fair binary voices can be individually and pairwise independent while their product has expectation 1/3. This is a completely legitimate three-voice probability law. It can also be realized as the marginal of five exchangeable voices. But it cannot be the marginal of six exchangeable voices, no matter how the additional voices are coupled.

The same local sign distribution has an infinite stationary temporal realization, so the impossibility is not a finite lifetime or general inability to add events. It is a failure of the specific promise that every distinct subset of the same cardinality receives the same law.

The target is to quantify that population horizon exactly for third- and fourth-order parity, rather than just exhibit a parity collision or optimize endpoint concurrence at a fixed population. The relevant prior MHAC work is #420 (read complete report, PR #421), which already establishes moment reductions and joint silence/tutti polygons, and #240 (issue and PR #241 metadata read), which already explores parity blocks and temporal dependence. Those are not claimed as new here.

## Model and finite population reduction

For k=3 or 4, let X_1,...,X_k take values in {-1,+1}. Require fair (k-1)-wise independence. Walsh expansion then gives the entire joint law:
\[
 P_c(x)=2^{-k}(1+c\prod_{i=1}^k x_i),\qquad -1\le c\le1.
\]
Here c is the expected sign product. This law is exchangeable; the probability of positive parity is (1+c)/2. The total variation distance between P_c and P_d is |c-d|/2.

An N-extension means a permutation-invariant law on N labelled binary voices whose first k coordinates have exactly this law. All distinct k-subsets then have this same law. Let S be the sum of the N signs, on the grid -N,-N+2,...,N. Exchangeability is equivalent to selecting a count law on S and then selecting the positive positions uniformly, since the permutation orbits are indexed by S. This finite urn representation is established background, not a new discovery.

Fair pairwise independence is equivalent to ES=0, ES²=N for the exchangeable law. Fair triple-wise independence additionally requires ES³=0. Expand the powers, using X_i²=1:
\[
 ES^3=N(N-1)(N-2)c_3,\quad
 ES^4=3N^2-2N+N(N-1)(N-2)(N-3)c_4
\]
under the corresponding lower-order independence. Conversely these moments identify the lower Walsh coefficients and the top coefficient, hence the entire k-coordinate marginal. Nothing about independence of all N variables is assumed.

## Exact triple parity horizon

For N>=3 the feasible interval is exactly [-b_N,b_N], with
\[
 b_N=\begin{cases}
 1/(N-2)&N\text{ odd},\\
 1/(N-1)&N\text{ even}.
 \end{cases}
\]
Proof, odd N: the polynomial (N-S)(S+1)^2 is nonnegative on the grid. Taking expectations gives ES³ <= (N-2)N+N=N(N-1). Equality is achieved by mass N/(N+1) at S=-1 and 1/(N+1) at S=N. These weights give ES=0, ES²=N. Even N: (N-S)S(S+2) is nonnegative on the even grid because no grid point lies strictly between -2 and 0. Its expectation gives ES³ <= (N-2)N. Equality is achieved by masses N/[2(N+2)], 1/2 and 1/(N+2) at S=-2,0,N respectively. They sum to one and have the required first two moments. Reflect S to achieve the negative endpoints. Mixtures fill the interval. Divide by N(N-1)(N-2). This proves feasibility and impossibility, without relying on numerical optimization.

For c!=0 the maximum exchangeable extension length is the largest odd integer N<=2+1/|c|. An even N and its following odd N have identical bounds, so the largest admissible N is odd. For c=0 ordinary independent fair signs extend indefinitely. A perfect parity clause c=1 is possible at length three but cannot accept a fourth anonymous voice. At c=1/3 the horizon is five; c=1/5 allows seven. The formula is not a bound on the physical number of voices in an arbitrary nonexchangeable instrument.

For the N=5 endpoint, select exactly two positive signs with total probability 5/6, uniformly across the ten possibilities, or all five positives with probability 1/6. All ten distinct triples have the same probability law: each positive-product pattern has probability 1/6; each negative-product pattern has probability 1/12. Every pair has all four patterns with probability 1/4. This is a direct constructive witness.

## Exact fourth parity horizon and asymmetry

For N>=4 impose fair triple-wise independence, and put Z=S². Its grid is the squared magnitudes of the allowed S grid. It has mean N. Let a<=N<=b be the nearest squared grid values below and above N (a=b when N itself is an allowed square). Put m=N mod 2. Then
\[
 L_N=\frac{(a+b)N-ab-3N^2+2N}{N(N-1)(N-2)(N-3)},\quad
 U_N=\begin{cases}
 1/(N-2)&N\text{ odd},\\
 1/(N-3)&N\text{ even}.
 \end{cases}
\]
The exact feasible interval of c_4 is [L_N,U_N].

Proof: on the squared grid (Z-a)(Z-b)>=0, since no admissible square is strictly between a and b. Hence E Z² >= (a+b)N-ab. Also (Z-m²)(N²-Z)>=0 gives E Z² <= (m²+N²)N-m²N². Both bounds are attained by distributions on their two defining squared magnitudes with mean N (the one-point case a=b is immediate). Lift them with equal signs at nonzero magnitudes, so ES=ES³=0. Substitution in the fourth-moment identity gives the displayed interval; mixtures fill it. The positive endpoint simplifies to the stated parity-dependent rational expression.

The negative endpoint may be rewritten as
\[
 L_N=-\frac{2}{(N-2)(N-3)}
      +\frac{(N-a)(b-N)}{N(N-1)(N-2)(N-3)}.
\]
The correction is nonnegative and O(N^-3): the neighboring squared grid magnitudes differ by O(sqrt(N)). Thus L_N=-2/N²+O(N^-3), while U_N=1/N+O(N^-2). At perfect-square N the correction vanishes. This creates a striking asymmetry: a weak positive four-way parity bias permits an exchangeable population of order 1/c, whereas a negative bias of the same magnitude permits only order sqrt(2/|c|). These are asymptotic horizon statements as |c| approaches zero. Exact negative horizons are computed by the interval test, not an asymptotic approximation. By marginalization the intervals are nested with N.

| N | third interval radius | fourth lower | fourth upper |
|---:|---:|---:|---:|
| 3 | 1 | not applicable | not applicable |
| 4 | 1/3 | -1 | 1 |
| 5 | 1/3 | -1/5 | 1/3 |
| 6 | 1/5 | -1/9 | 1/3 |
| 7 | 1/5 | -3/35 | 1/5 |
| 8 | 1/7 | -1/15 | 1/5 |
| 9 | 1/7 | -1/21 | 1/7 |

For the positive fourth coefficient the maximum horizon is the largest even N<=3+1/c. For negative c, use the exact lower endpoint; it is not obtained by reflecting all signs, since a four-sign product is complement invariant. This is unlike odd-order parity.

## Repair cost and negative controls

Under the contract that the lower marginals must remain exactly fair independent, the minimum total variation change to make the local law N-extendible is half the distance from c to the corresponding feasible interval. Proof: the admissible local family is one-dimensional, the formula for TV is exact, and interval endpoints are attainable. Equivalently, clamp c to the interval and construct the corresponding count-law mixture. This is an optimal repair only within that contract; allowing lower-order calibration changes or abandoning exchangeability defines different optimization problems.

Independent symmetric sign-flip noise on each observed coordinate multiplies c by (1-2e)^k, where e is the flip probability, and preserves lower independence. It can hide a horizon violation rather than resolve it at the latent source. A finite sample does not establish exact marginals or exact parity. An approximate measurement should report uncertainty in all lower coefficients as well as c; the exact projection result must not be treated as a confidence interval.

Infinite exchangeability plus pairwise independence forces the iid fair law: the exact third and fourth intervals shrink to zero; more generally de Finetti's Bernoulli mixture has mean parameter 1/2 and variance zero from the pair moment, hence the mixing parameter is constant. The finite horizon here is quantitative, not a claim to have discovered de Finetti's theorem.

Stationarity is a much weaker contract. For example take a bi-infinite sequence of independent uniform positive-parity triples, then choose one common random block phase uniformly in {0,1,2}. The resulting sequence is stationary, each individual and each distinct pair is fair independent, and every *consecutive* triple has c=1/3 because it is a full block one third of the time and otherwise spans independent blocks. It can run indefinitely. A scattered triple such as positions 0,3,6 has c=0. Thus it is not exchangeable. #240 already explores parity-block families; this example is retained as a comparator, not a new temporal construction. A failed extension test cannot establish physical finite duration, order effects, common cause, or which labelled source is at fault.

A direct joint lookup or deliberate block protocol is an essential engineering comparator. Anonymous independent-role substitution is an explicit additional design promise, not a necessity of acoustic communication.

## Computational qualification

Run node laboratory.cjs for the standalone integer census. On a moment polytope with k constraints (including normalization), every vertex has at most k positive count weights: otherwise a nonzero null vector supported on positive weights permits a two-sided perturbation. Enumerating exactly k distinct nodes includes degenerate smaller supports with zero weights. Expectation of each Lagrange basis polynomial gives the unique corresponding weight; its numerator and denominator are integers. Nonnegative weights characterize feasibility. The support polynomial then yields the next moment directly. All arithmetic is safe integer arithmetic for N<=40.

Executed the JavaScript core in V8 (not native Node CLI): 75 population/order profiles, 962,596 candidate supports, 81,681 feasible support instances including duplicates. All third/fourth extrema agree exactly with the proofs, zero assertion failures. See execution.json. Census is corroboration, not the proof.

A separate native Python witness (delivered with the audio package) uses exact rational hypergeometric marginals for endpoint distributions through N=64: 246 endpoint witnesses and 2,944 full marginal cells. It also uses SciPy HiGHS on the labelled bit cube, without imposing count symmetry: constraints on every proper subset's sign product, objective the average over all k-subsets. Permutation averaging preserves these constraints and objective. Thirty LPs for N<=10 agreed with the analytical endpoints to maximum absolute discrepancy 1.7733037260825313e-13. Python 3.13.5, SciPy 1.17.0, NumPy 2.3.5. Repeated native run gave byte-identical receipt; PCM hashes in receipt. Same AI agent, different methods, not independent peer review. Native witness source Git blob SHA da7ac0e221fc90555d40e64ba9b1e06ddf2e2569; receipt 25d9bd82f6ea1150e4416cf449720cc5be102ca0.

## Original score: the admission organ

Construct a literal 24-frame five-voice score from the N=5 witness (each of the ten two-positive patterns appears twice, all-positive appears four times). Shuffle reproducibly with seed 658. All ten triples have four instances of each positive-product pattern and two of each negative-product pattern. Every pair has six instances of each pattern. Project to the first three voices without changing frame order. Compare with a 24-frame iid-law inventory (each of the eight patterns occurs three times, independently shuffled). The scores are deterministic balanced multisets, not independent time draws. A composer can choose a desired local parity accent, then ask how many anonymous voices it permits before the law must change.

The three original mono PCM16 WAVs use 8 kHz, 80 ms frames, one sinusoidal carrier per active sign, 250–450 Hz in 50 Hz steps, fixed per-voice 3500 PCM-unit amplitude, no frame gain normalization. Each frame contains integer carrier cycles. Literal sinusoidal projection of the readback PCM recovers all 264 bits across three recordings; max amplitude error 0.198345 PCM units (rounded up). Five-voice extension and three-voice projection are aligned. The three-voice iid comparator is independently arranged. This is a digital construction, not acoustic transmission or a perceptual experiment. A live instrument is speculative.

## Source and claim ledger

- Takis Konstantopoulos and Linglong Yuan, On the extendibility of finitely exchangeable probability measures, Trans. Amer. Math. Soc. 371 (2019), 7067–7092, https://doi.org/10.1090/tran/7701. Agent verified journal abstract and read the accessible arXiv rendering https://arxiv.org/abs/1501.06188, section 1 from its opening through the finite/infinite extension definitions, urn example and finite-alphabet convex-set discussion (rendered lines 7–41). General finite extendibility and the geometric reduction are established prior art. Did not read all proofs, and no claim of priority for the specialized formulas.
- Ron Peled, Ariel Yadin and Amir Yehudayoff, The maximal probability that k-wise independent bits are all 1, Random Structures & Algorithms 38 (2011), 502–525, https://doi.org/10.1002/rsa.20329. Agent read current publisher abstract (discrete moment problem and extremal all-one probability). #420 contains a prior agent's more extensive section-level reading record, not an independent current reading. Its objective differs from parity-horizon extension. No claim of novelty for the underlying moment-polytope technique.
- Wenpin Tang, Finite and Infinite Weighted Exchangeable Sequences, Mathematics 14(18), 3291 (2026), https://doi.org/10.3390/math14183291. Current publisher abstract and introductory Bernoulli-mixture description read. Weighted exchangeability and finite approximation are broader topics; the present proof is only ordinary unweighted binary exchangeability. No inference from the weighted theorem is used.

Mathematical claims above are proved under stated assumptions; computational receipts are synthetic observations. Interpretation: interchangeability of anonymous participants is a relational contract distinct from local symbol accuracy. Design hypothesis: when an instrument's grammar will be scaled to more equivalent sources, record the population size and test finite extendibility of proposed local joint distributions. Falsifier: the deployment is not exchangeable or the measured law lacks the stipulated lower marginals; use a richer model or directly specify labelled source relations. No human listening benefit, machine safety, scientific priority, or extra explanatory contribution from cybersemiotics is established. Conventional probability and convex geometry explain the results.

## Checkpoint

Base 495a98ca12bae467a507031f04931aa4254b1866. Reconciled main, AGENTS/README/RAG/PROGRAMME/RUNBOOK/INTEGRITY/VALIDATION/PROJECT_FOUNDATIONS/EXPERIMENTS, recent 100 open issue and 100 open PR results, 389 branch entries; targeted search for exchangeability, extendibility, parity, independence, automata and stationary processes. Read #420 issue/comments, report and #421 metadata; #240 issue/comments and #241 metadata; #492 issue/comments and #493 metadata (discarded reset direction). Previous #655 exact head f4f771228417ac22d13a8b5394270cae63048e63 workflow 45757549832 completed successfully. #658 newly created, read back, no comments. No nested AGENTS found under research or research/expeditions on main. Native checkout attempted; DNS failed. No shared manifest or canonical record changes, no other branch mutations. All additions in this expedition. Keep draft and use Refs #658 until substantive independent review and exact-head repository checks are complete. No independent human validation performed.

Fiction: A clerk teaches three singers a refrain that every pair can sing without knowing the third. The choir expands to five, with every trio still keeping the same bargain. A sixth arrives. The clerk cannot admit her without changing a promise he had never written down: not merely that the singers were fair, but that every trio was interchangeable.
