# The Dictionary That Loses a Bit
## Noisy serialization, asymmetric recovery and nonlinear relabeling

Refs #464 · 25 November 2026 · mathematics and synthetic computation. One ChatGPT GPT-6.2 agent, self-reviewed; not independent peer review or a human listening study.

## Contents

1. Excavation — challenge the implicit equivalence of an abstract label and a rendered message.
2. Model — define the full-transversal dictionary and binary noisy slots.
3. Affine obstruction — derive the sharp bottleneck and an end-to-end repair.
4. Nonlinear counterexample — solve the four-pair minimal-dictionary case by a finite certificate.
5. Exaptation — distinguish utility, privacy, serial duration and physical rendering.
6. Reproduction — retain exact calculations, scope and acceptance limits.

## 1. Excavation

[Draft #455](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/e2c4f294f10d054e59a5feeb8780299db17a5e1c/research/expeditions/dictionary-survives-errors/README.md), §§3–6, establishes that an exact-optimal noisy dictionary can have very low marginal entropy without shrinking its positive-probability alphabet. [Draft #427](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/5158863f7f9b0d881a320c7678008bc04afbfa57/research/expeditions/receipt-cannot-fit-dictionary/README.md), §§2–3, gives the exact minimum noiseless dictionary and its antipodal law. [Draft #435](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/dfdcdf848996c4ca0a7702f73881f62145c0eb30/research/expeditions/dictionary-missing-pages/README.md) shows that a nearly optimal scalar score need not establish structural coverage. None specifies how the dictionary's names are represented in a noisy serial channel.

The accepted [X004 Quotient Guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md) is decision-scoped and deterministic; it is not a noisy-channel guarantee. The foundation's functional chain explicitly separates semantic message, rendering policy, acoustic output and situated interpretation. Here we make one such separation executable. We find that a noiseless-optimal dictionary's physical encoding can introduce unequal conditional utility despite symmetric hardware noise. Nonlinear relabeling can improve the worst utility while sacrificing exact end-to-end privacy optimality.

Live main reconciled at 495a98ca12bae467a507031f04931aa4254b1866, refreshed before creating mhac-464/dictionary-render. Read AGENTS, RAG, programme, runbook, integrity, validation, foundations, X004 and the actual draft reports above. First 100 returned open issue/PR search entries surveyed separately (connector returned the same titles for both queries; this is not a verified exhaustive type-separated survey). Targeted binary symmetric issue search and dictionary-render branch search did not locate a competing scope. #454 body and zero comments inspected; #455 remains open Draft, mergeable; Actions run 45533737997 reported success for the pinned predecessor query (structural, not scientific). New #464 body and zero comments inspected before branching. No central records changed. The unmerged predecessors are mathematical working inputs, not accepted scientific findings.

## 2. Model (mathematics)

There are m even, m>=4 collision pairs of equiprobable states (i,s), s=+/-1. The authorized decoder sees the chosen pair-collapse intervention, its result and the *received* word. The observer sees only that same word. A source-independent action collapses the two states of its chosen pair and leaves all other states distinct. For each pair define T_i as the total variation between its two conditional received-word distributions; its conditional Bayes accuracy is (1+T_i)/2. Outside the collapsed pair the intervention result already identifies the state. This is not a worst-original guarantee.

Take k=m-1 binary slots and n=2^k equiprobable transmitted words x. The noiseless optimal full-transversal dictionary maps x to a sign vector f(x) in {-1,+1}^m, with exactly one representative of each antipodal pair and each coordinate balanced. These conditions are exactly the minimal-cardinality full-recovery optimum in #427, and imply that the f_i are orthonormal under uniform x (every nonempty even product has mean zero). We study a uniform label law, not #455's concentrated minimum-entropy law. Optional prespecified contrast throttles t_i in [0,1] define the transmitted word channel

    P(Xword=x | i,s) = (1+s*t_i*f_i(x))/n.

Rows normalize by balance and the marginal word law stays uniform. Full t_i=1 realizes exact noiseless pair recovery. This encoder with fixed t_i has the same stipulated prior and action family as #455.

The renderer independently flips each bit with probability q in [0,1/2], identical across slots and source-independent. Let rho=1-2q. Received word y is also uniform; its pair contrast is

    P(i,+ | y)-P(i,- | y) = (t_i/m) (N_rho f_i)(y),

where N_rho is averaging f_i over the independent bit-flip kernel. Hence T_i=t_i E_y |N_rho f_i(y)|.

For a fixed balanced target on all 2m states the observer's Bayes accuracy is one-half plus half the expected absolute posterior target mean. Uniform posterior pair mass 1/m ensures constant-sign groups cancel. Adding random signs on omitted groups and applying Jensen shows the worst target can be chosen mixed within every pair. Thus the exact observer score is

    V = 1/2 + (1/(2m)) max_{u in {-1,+1}^m} E_y |sum_i u_i t_i N_rho f_i(y)|.

The noise operator is established mathematics. Ryan O'Donnell, Analysis of Boolean Functions, May 2021 arXiv edition, [author-hosted PDF](https://www.cs.cmu.edu/~odonnell/papers/Analysis-of-Boolean-Functions-by-Ryan-ODonnell.pdf), §2.4 printed pp.55–56, Definition 2.46, Proposition 2.47 and Theorem 2.49, text and page images inspected 25 Nov 2026. Only this passage read; no priority claim. Our operator is precisely his noise operator. The Bayes advantage here is its L1 norm, not automatically the noise stability of a fixed sign decoder.

## 3. Affine serialization (mathematics)

Choose f_i(x)=c_i (-1)^(a_i dot x), with c_i in {-1,+1} and a_i nonzero binary vectors of length k. The noiseless antipodal criterion says no nonempty even subset of rows a_i XORs to zero. Equivalently the linear map from the m-dimensional coefficient space has trivial kernel on the even-parity subspace. Since that subspace has dimension m-1=k, rank is k, and its unique nonzero kernel vector has odd weight. Conversely that condition is sufficient for the antipodal criterion; all a_i nonzero are also necessary for source balance.

Independence of bit errors gives N_rho f_i(y)=rho^(|a_i|) f_i(y) directly: each factor is multiplied by the mean sign of its flip. Therefore T_i=t_i rho^(|a_i|).

**Theorem A (sharp affine bottleneck).** For t_i=1 and 0<rho<1, the maximum possible min_i T_i among affine minimal dictionaries is rho^2. Moreover no such dictionary has all T_i equal.

Proof: there are m=k+1 distinct nonzero rows (duplicate rows violate the even-subset criterion) but only k weight-one vectors. Some row has weight at least two. Attain equality by taking the k unit vectors and the XOR of the first two: the only dependence is an odd triple. If all row weights were equal, either all were even, which confines their span to the k-1-dimensional even subspace, or all were odd, in which case an odd collection cannot XOR to zero (parity is linear). Both contradict the rank/kernel criterion. The excluded endpoints q=0 and q=1/2 have respectively perfect and chance recovery for every row.

**Theorem B (end-to-end optimality for the ACTUAL heterogeneous caps).** For any affine dictionary and any throttles, let v_i=t_i rho^(|a_i|). The end-to-end observer score is exactly

    V = 1/2 + E_Z |sum_i v_i Z_i|/(2m),

for independent fair signs Z_i. Indeed every absolute signed sum is invariant under global reversal, so its expectation over one representative of each antipodal pair equals its expectation over the full cube. This is also the general heterogeneous minimax lower bound from #455: average over all mixed targets, use convexity of the absolute signed-sum norm and its coordinatewise monotonicity on nonnegative magnitudes. This attains it for the actual vector v, not necessarily for the equal cap defined by its minimum.

**Repair without another slot.** In the attaining affine construction, set t_i=rho for the k weight-one rows and t_i=1 for the weight-two row. Every output T_i becomes rho^2. The worst pair utility is unchanged from the unthrottled construction, while the other pairs lose excess utility and the privacy score strictly improves for 0<rho<1. Strictness follows from #455's strict permutation lemma: for even m a nonuniform nonnegative vector has a strictly greater signed-sum norm than its uniform mean vector, and this latter mean strictly exceeds the minimum. If the intended requirement is an equal per-pair cap at the worst value, this is optimal. If some pairs need higher utility, throttling is not an improvement on that contract.

**Extra-slot comparator.** With m slots, use all m independent coordinate signs and transmit the full cube uniformly. All T_i=rho and the equal-cap privacy optimum holds. This doubles abstract label count, adds exactly one binary slot under the present serialization, and raises worst conditional accuracy from (1+rho^2)/2 to (1+rho)/2. It does not establish minimum physical time or redundancy for other renderer models.

**Universal non-affine upper bound.** For any of the uniform full-transversal labelings at t_i=1, f_i are m orthonormal balanced Boolean functions on k bits. In the standard orthonormal character basis let A_i be the squared degree-one Fourier mass of f_i. Bessel's inequality for each of the k degree-one basis vectors gives sum_i A_i<=k. Some A_i<=k/m. Parseval and independent noise give

    T_i^2 <= E (N_rho f_i)^2
          <= rho^2 A_i + rho^4 (1-A_i).

Thus min_i T_i <= rho sqrt(1-(1-rho^2)/m) < rho for 0<rho<1. This does not assert rho^2 is universal or the displayed bound is sharp. An arbitrary relabeling cannot fully recover the extra-slot reliability under these assumptions. The next section explicitly refutes the stronger affine-only bound.

## 4. Exact nonlinear result for m=4, k=3 (mathematics + finite certificate)

**Theorem C.** Among all uniform full-recovery minimal dictionaries serialized bijectively into three independently corrupted bits, the maximum min_i T_i for four collision pairs is rho(1+rho)/2 for every rho in [0,1]. In particular this strictly exceeds rho^2 in the interior. No claim for arbitrary m or nonuniform/noisy input dictionaries is made.

Finite proof: normalize each Boolean function by choosing its overall sign so f(0)=+1. Any balanced function on eight words then corresponds to a mask with exactly four one bits including bit zero; there are 35. Reordering the four functions or negating any of them does not change utility or validity. Enumerate every 4-subset of these 35 masks (52,360 candidates). Pairwise balanced products are exactly Hamming distance four; the fourfold product must also be balanced (XOR of all four masks has four one bits). These tests are necessary and sufficient for all nonempty even moments to vanish, hence for antipodal uniformity. A separate direct antipodal coverage check confirms all 840 valid sets.

Classify the 35 masks by the signed shell sums at each received word y,

    b_d(y)=f(y) sum_{x: Hamming(x,y)=d} f(x), d=0,1,2,3.

Then the sign-adjusted noise average is sum_d b_d(y) (1-q)^(3-d) q^d. This gives the following complete classification. Multiplicities are counts across eight values of y; rho is in [0,1].

| Type | Number of masks | Shell tuple(s), multiplicity | T=E absolute noise average |
| --- | ---: | --- | --- |
| D | 3 | (1,1,-1,-1) x8 | rho |
| P | 3 | (1,-1,-1,1) x8 | rho^2 |
| Q | 1 | (1,-3,3,-1) x8 | rho^3 |
| B | 12 | D x4, P x4 | rho(1+rho)/2 |
| M | 4 | (1,-1,1,-1) x6; (1,3,-3,-1) x2 | (3rho+rho^3)/4 |
| C | 12 | (1,-1,1,-1) x4; (1,-3,1,1) x2; (1,1,-3,1) x2 | max(rho/2, rho(1+rho)^2/4) |

The table is a finite combinatorial certificate, not a grid fit in rho. Each shell polynomial can be evaluated directly in rho. For C, only the middle tuple's signed polynomial rho*(rho^2+2rho-1)/2 can change sign. Summing its absolute value with the other two polynomials produces the stated maximum. P, Q, C have T<=B for all rho. D and M can be stronger, but none of the 840 valid four-sets consists only of D and M. The exhaustive certificate checks that assertion and finds 24 valid four-sets consisting entirely of B. Thus some member of every valid set has T<=B, and an all-B set attains equality, proving the claimed bound for the continuum. The lab additionally checks the shell expressions by direct integer bit-flip convolution at seven rational q values.

An explicit witness uses masks [27,53,71,141] (decimal; bit x selects f_i(x)=+1). Each has four ones including bit zero; all six pairwise XORs and the fourfold XOR have weight four. Each is type B. Its truth table is:

| x (decimal) | f1 | f2 | f3 | f4 |
| ---: | --- | --- | --- | --- |
| 0 | + | + | + | + |
| 1 | + | - | + | - |
| 2 | - | + | + | + |
| 3 | + | - | - | + |
| 4 | + | + | - | - |
| 5 | - | + | - | - |
| 6 | - | - | + | - |
| 7 | - | - | - | + |

The witness maximizes worst recovery, but not the privacy objective at its new equal utility cap. At q=.1, rho=.8, exhaustive actual received-word target enumeration gives:

| Policy | Slots | Conditional pair accuracies | Worst fixed balanced-target guessing | Unconstrained optimum at ACTUAL pair cap vector |
| --- | ---: | --- | ---: | ---: |
| Raw affine | 3 | 90%,90%,90%,82% | 65% | 65% |
| Throttled affine | 3 | 82%,82%,82%,82% | 62% | 62% |
| Nonlinear all-B witness | 3 | 86%,86%,86%,86% | 65% | 63.5% |
| Full cube | 4 | 90%,90%,90%,90% | 65% | 65% |

The nonlinear 1.5 percentage point gap is a directly evaluated finite result, not a proof that every nonlinear witness incurs the same gap. Unlike raw affine, its pair contrasts do not all have constant magnitudes across received words. Equality of marginal pair utilities alone does not ensure the optimal privacy score. This is precisely why a renderer cannot be assessed using only a pre-render dictionary or a table of average confusion rates.

## 5. Exaptation and objections (interpretation/design hypotheses)

The engineering lesson is not that extra slots are always desirable. A compact affine grammar can secretly make a semantic contrast depend on multiple independent discriminations. A nonlinear arrangement can improve the worst contrast without adding a slot, but may change the privacy score in ways not explained by marginal utility. Selective throttling is useful only when excess utility is genuinely unnecessary; destroying safety-relevant distinctions to lower disclosure would violate a different specification.

For an eventual synthetic auditory apparatus, map slots to fixed-duration binary motifs, declare a received-word observation model, and compare (a) single/double dependency affine map, (b) same map with pre-encoding throttle, (c) explicit all-B nonlinear map, (d) extra-slot map. Use identical declared q for the first numerical model, then separately evaluate measured/correlated symbol confusion, missed onsets, timing costs and decoder/observer asymmetry. The present independent bit-flip model is deliberately not a hearing model. A received-word experiment with synthetic flips cannot establish discrimination, learning, workload or privacy under real listening conditions. No participant activity or operational security assertion is included.

This also exposes a negative result about evaluation: since the renderer garbles the original label, for every pair T cannot increase. Equality in the triangle inequality requires each received word to mix only inputs whose signed pair contrasts have compatible signs. A strictly positive bit-flip matrix (0<q<1/2) mixes every input into every output; any balanced nonzero contrast then loses strictly positive total variation. A certificate of an abstract label's recovery is never a certificate of unchanged received-word recovery under this renderer. This elementary observation does not establish an irreducible acoustic loss for differently designed channels.

Fictional miniature: four musicians are promised equal access to a three-note signal. Three interpret a single note; the fourth reads a relationship between two notes. Every note is equally likely to be misheard. The fourth musician is not. The composer can write another note, change the arrangement, or stop promising more information than the others need. The listener's actual demands decide which is a repair.

## 6. Reproduction and status

Run node lab.js in this directory. The independent finite oracle within the same authoring process enumerates shell polynomials and orientation sets, and separately constructs conditional channel rows by exact integer convolution rather than using the affine spectral formula. It computes actual conditional decoder advantages from row differences and enumerates all balanced target functions. It also enumerates affine row sets in dimensions 3 and 5. All integers used in these finite cases are within the exact safe integer range of JavaScript.

Development execution passed: 35 balanced functions, 52,360 orientation candidates, 840 valid orientations, 24 all-B orientations, 245 rational noise function checks, 361,116 valid affine row sets, 1,102,336 direct channel summands, 10,176 conditional decoder cells, 55,596 balanced target evaluations and 6,711,632 target-label evaluations. These counts overlap and are not independent trials. The analytical argument and lab share one AI author. No native Node checkout/full repository validation or independent substantive critique performed yet. Keep draft/HOLD; #464 remains open. No frozen protocol, canonical manifest, shared aggregate, accepted research record or another worker's branch changed.

Revision criteria: a valid affine minimal dictionary with all equal interior advantages or a worst advantage exceeding rho^2; a valid four-function mask set with stronger worst advantage than the all-B result; a direct decoder/target discrepancy; or failure of the exact prior, shell enumeration or antipodal constraints. General nonlinear optimization for larger m, nonuniform word laws, other physical noise models, and perceptual realization remain open.
