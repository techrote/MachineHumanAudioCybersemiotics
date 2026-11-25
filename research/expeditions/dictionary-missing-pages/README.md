# The Dictionary That Hides Its Missing Pages
## Exponentially ill-conditioned audit rigidity and exact syndrome witnesses

Refs #434 · 25 November 2026 · mathematical and synthetic expedition. One GPT-6.2 agent; no independent review, human observations, operational privacy validation or priority claim.

### Archaeology and scope

Read current AGENTS, RAG, programme, runbook, integrity, validation, foundations, the accepted [X004 Quotient Guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md), and actual draft [#419](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/61321a6f898b37f0b2bc819b5e718584d18d6061/research/expeditions/receipt-passes-every-question/README.md) §§2–4 and [#427](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/5158863f7f9b0d881a320c7678008bc04afbfa57/research/expeditions/receipt-cannot-fit-dictionary/README.md) §§2–5. Main 495a98ca12bae467a507031f04931aa4254b1866 refreshed before branching. First 100 returned open issue and PR titles surveyed; targeted Fourier/receipt search found related X001/X007 and spatial aliases but no matching new syndrome scope. #426/#434 comments empty when inspected; #427 exact-head Actions run 45519049943 successful (structural, not scientific). #427 remains draft and is not accepted evidence.

The previous result forces a uniform antipodal dictionary law at exact Boolean optimality. Does passing the same audit with very small tolerance certify a nearly uniform law? No: the convolution has exponentially weak directions. We produce a family where almost all antipodal dictionary pairs are absent, even though the exact worst-target score is exponentially close to optimal. This is about the distribution of emitted labels/supports, not additional leakage about the original. The central research programme and canonical records remain untouched.

### Model (mathematics)

Use #427's special case of m groups of two equiprobable originals, one possible pair-collapse intervention per group, and receipt labels that are full transversals. A sign vector z in {-1,+1}^m selects one original from every group. Given label z, the posterior is uniform across its m selected originals. A label law mu with unbiased coordinate signs implements a channel by emitting z with conditional probability 2 mu(z) when z selects the original and zero otherwise. The authorized decoder sees action and result and reconstructs exactly. The observer sees the receipt only. Restrict the new stability statements to these uniform full-transversal channels; no assertion about arbitrary nonuniform posterior channels.

For a balanced fixed Boolean target f on the 2m originals, Bayes accuracy is (1+E|posterior signed mean|)/2. Write c_m=binom(m,m/2)/2^m for even m. The exact optimum from #419 is B_m=(1+c_m)/2; its lower bound follows by averaging group-balanced targets and convexity, and uniform transversals attain it.

**Reduction to group-balanced targets, for every mu.** A globally balanced target has equal numbers of all-plus and all-minus groups. Their contributions cancel in each full uniform posterior. Its remaining mixed groups R contribute sum_{i in R} t_i z_i for some signs t_i. Fill in the omitted t_i independently with fair signs. Conditional on z, Jensen says the mean absolute full sum is at least the absolute partial sum. Averaging over z shows some full group-balanced target has at least the original score. Thus the maximum over ALL balanced targets equals the maximum over the 2^m group-balanced targets. This applies without assuming an optimal label law.

### Exact syndrome theorem (mathematics)

Let m=2^k with k>=3. Index coordinates by all vectors v in F2^k including zero. Write z_v=(-1)^b_v. Define syndrome s(z)=XOR of v for all b_v=1. This is a surjective linear map with m equal-sized fibres; the zero coordinate is free. The kernel is the ordinary Hamming parity-check kernel with one unconstrained coordinate appended, NOT the standard extended Hamming code with an extra overall parity check (correcting the terminology in the initial issue).

Every nonzero u in F2^k defines a Walsh character chi_u(z)=(-1)^(u dot s(z)), supported on the coordinates v with u dot v=1. Exactly m/2 such coordinates occur, by pairing each v with v+w for a w satisfying u dot w=1. This is the classical linear Walsh-Hadamard code. Background taxonomy checked against [Error Correction Zoo, Hadamard code, Description](https://errorcorrectionzoo.org/c/hadamard) and [simplex code, Description](https://errorcorrectionzoo.org/c/simplex), search-visible descriptions inspected on 2026-11-25, no underlying books read. All decisive calculations are provided here; no novelty priority claim.

Choose any probability vector alpha on the m syndromes. Issue a uniform label within the selected syndrome class, with class weight alpha_s. Every class is antipodally closed: complementing all bits XORs all v, which is zero for k>=2. Thus mu is antipodally symmetric and the required uniform source prior follows automatically. Each coset has 2^m/m labels. For any target sign vector t, componentwise multiplication adds syndromes.

Let g(z)=|sum_v z_v|. Under uniform cube signs, E g=m c_m. For any even set S of 2j coordinates, j>=1, its Walsh coefficient is

    ghat(S)= c_(m-2) * (-1)^(j-1)
              * binom((m-2)/2,j-1)/binom(m-2,2j-2).

Proof (rederived from #427): average over two chosen coordinates in S, with their product as multiplier. If T is the sum of remaining signs, the inner mean is (|T+2|+|T-2|-2|T|)/4 = 1[T=0]. Conditional on T=0, the remaining signs have equally many plus and minus. The mean product of 2j-2 specified signs is the coefficient of x^(2j-2) in (1-x^2)^((m-2)/2), divided by binom(m-2,2j-2). Odd coefficients vanish under global reversal.

For the m-1 nonzero syndrome characters, |S|=m/2, j=m/4 is even. All coefficients are therefore NEGATIVE, equal to -a_m, where

    a_m = c_(m-2) * binom(m/2-1,m/4-1)/binom(m-2,m/2-2) > 0.

The finite character identity 1[s(z)=q]= (1/m) sum_u (-1)^(u dot (s(z)+q)) gives, after conditioning a uniform cube on syndrome q,

    E[g(Z)|s(Z)=q] = m c_m + a_m(1-m*1[q=0]).

Since s(t*Z)=s(t)+s(Z), under the arbitrary mixture alpha we obtain

    E_mu g(t*Z) = m c_m + a_m(1-m alpha_{s(t)}).

All syndromes are attainable by t. The reduction above now proves the exact worst balanced Boolean score:

    V(alpha) = B_m + a_m/(2m) * (1-m min_s alpha_s).

No sampling or asymptotic approximation is used in this theorem.

### Instability and sharp restricted inverse (mathematics)

Let U denote the uniform sign-cube law (equivalently the uniform law of antipodal pairs for symmetric mu). Then TV(mu,U)=TV(alpha,uniform) exactly because the conditional distributions within classes coincide. Set d=1-m min alpha. If d>0 then alpha=(1-d) uniform+d beta for some probability vector beta with a zero coordinate. Hence

    TV(mu,U) <= (1-1/m)*d
              = (1-1/m)*(2m/a_m)*(V(alpha)-B_m).

Equality is attained for any d in [0,1] by mixing uniform syndromes with a point mass. This is a sharp inverse bound within the syndrome family, not a bound for all channels.

A single syndrome class has d=1, TV=1-1/m, and worst-target excess exactly a_m/(2m). It omits the same fraction 1-1/m of antipodal pairs. Relative to #427's exact minimum positive-label count 2^(m-1), the symmetric witness uses 2^m/m labels, a factor m/2 fewer. This is still exponential in m, not a polynomial dictionary construction. The #427 sampled polynomial bound and this exact instability theorem address different regimes.

The formula simplifies to a_m=4*(m/2)/(m/2-1)*binom(m/2-1,m/4-1)/2^m. Therefore a_m <= 4*2^(-m/2) for m>=8 and the excess <= (2/m)*2^(-m/2). The true coefficient is given above. With growing m, TV tends to one and the audit excess tends exponentially to zero.

| m groups | Antipodal pairs absent | Worst score above optimum (probability) |
|---:|---:|---:|
| 8 | 87.5% | 0.00390625 |
| 16 | 93.75% | 0.0000762939453125 |
| 32 | 96.875% | 9.988434612751e-8 |
| 64 | 98.4375% | 5.255586005455e-13 |
| 128 | 99.21875% | 4.274284374719e-23 |

Two opposite controls matter. Uniform alpha gives exactly B_m and TV=0. Uniform alpha over all BUT one syndrome gives the SAME excess as the point-mass law, but TV=1/m instead of 1-1/m. Thus even the exact small nonzero score gap does not identify the magnitude of the structural deviation. At fixed m, the inverse coefficient is finite; there is no contradiction with exact rigidity. The negative sign of the relevant coefficients is essential; m=4 is outside the theorem.

### Design exaptation and objections (interpretation / hypothesis)

X004's decision-scoped audit is correct within its domain. Here an exhaustive but scalarized audit is not a well-conditioned estimator of the dictionary ensemble. #427's exact identification is not a robust identification certificate at ordinary tolerances. #419's distinction between whole-original disclosure and fixed-target guessing remains unchanged: every witness still has uniform m-element posteriors, Shannon mutual information exactly one bit and original guessing 1/m. This expedition's TV compares LABEL LAWS, not posterior versus prior, not state privacy, and not an audible discrimination result.

Proposed contract: when structural diversity of a generated vocabulary is itself required, separately specify a structural observable (e.g., antipodal class coverage or declared syndrome counts), a tolerance for it, and decision utility. Audit that observable directly; do not infer it from a nearly optimal guessing score. Conversely, if the only operational requirement is the declared guessing tolerance and exact recovery, deliberately omitting labels is not a defect. There is no obligation to maximize representational diversity without a decision or artistic reason. A possible acoustic experiment would manipulate codebook diversity with fixed decision accuracy; it remains untested, not a human or perceptual claim.

Fictional miniature: a printer removes almost every section of a combinatorial dictionary. The inspector repeats every yes/no audit and can scarcely measure a difference. The printer has fulfilled the numerical brief. The librarian had meant to preserve a catalogue of possible voices. Neither requirement implies the other.

### Computational verification and disposition

Run node lab.js from this directory. The BigInt syndrome/weight DP builds counts by appending each coordinate with both bit values, not by using Fourier coefficients. It tests the analytic identities for m=8,16,32,64,128 and five syndrome mixtures, including all-but-one and point mass. The small direct oracle enumerates all 12,870 balanced targets on 16 originals with 32 actual labels, checks uniform prior and tests actual pair-collapse decoder observations. Its maximum sum of absolute signed sums is 72, giving V=1/2+72/(2*8*32)=0.640625. The initial handwritten expected integer 71 was wrong; direct enumeration and the analytical formula agree at 72. The corrected assertion passed.

Development V8 execution: 1,982,568 DP update operations, 248 syndrome identities, 1,240 mixture comparisons, 12,870 balanced target masks, 2,048 positive decoder cells. These are overlapping synthetic checks, not separate experiments. Native Node checkout, full repository validation, independent mathematical critique and broader prior-art assessment not yet established. No central manifests, frozen protocols, accepted research records or other worker branches edited. Draft/HOLD, Refs #434; no closure.

Revision criteria: exhibit a balanced target beating the group-balanced maximum for a uniform full-transversal channel; disprove the syndrome-conditioned signed-sum identity; give a same-syndrome mixture violating the exact TV bound; or show a computational mismatch under exact arithmetic. General nonuniform posteriors, other alphabets, nonuniform source priors and actual human interpretation remain separate questions.
