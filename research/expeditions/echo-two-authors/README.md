# The Echo That Has Two Authors

**MHAC issue #300 — 2026-11-24.** Independent synthetic/formal research, not canonical Track E/G evidence, not a claim of mathematical priority, not an empirical auditory experiment.

## Contents

1. [The problem](#1-the-problem) — two complete recordings, competing source/channel explanations.
2. [Exact obstruction](#2-exact-obstruction) — the ordinary GCD is positive but inadmissible.
3. [An arbitrarily large family](#3-an-arbitrarily-large-family) — the complete admissible common-filter poset is a discrete simplex.
4. [The calibration that misses its target](#4-the-calibration-that-misses-its-target) — even exact gain, length and two taps can coincide.
5. [Executable qualification](#5-executable-qualification) — integer long division, bounded enumeration and audio witnesses.
6. [Exaptation and refusals](#6-exaptation-and-refusals) — interpretation, potential instrument, limitations and negative results.
7. [Source ledger and checkpoint](#7-source-ledger-and-checkpoint) — accessed passages and actual execution status.
8. [Fiction: the room that composed the tune](#8-fiction-the-room-that-composed-the-tune) — an invented afterword.

## 1. The problem

A machine emits a nonnegative pulse envelope, which passes through an unknown finite nonnegative echo kernel. The listener records its entire output, including the tail. A second utterance passes through the same kernel. Can the room's contribution be extracted unambiguously by assigning as much of the shared structure as possible to the room?

Model: all sequences are finite real polynomials in a delay indeterminate z, with nonnegative coefficients, strictly positive constant and leading coefficients, and value at z=1 equal to 1. This removes scale and pure-delay ambiguities; it makes the same mathematics applicable to distributions of independent nonnegative integer-valued delays. We use complete, noiseless, ordinary linear convolution, not circular convolution or cropped signals. A pair of observed polynomials Y0,Y1 admits H if Y0=H S0 and Y1=H S1 with all three factors in this model. Every factor is normalized separately; writing unnormalized positive polynomials is shorthand for normalizing each by its value at 1.

Define the order among admissible H by ordinary polynomial divisibility over the reals (normalization removes units). The order is not necessarily the same as requiring the quotient of two admissible H to be nonnegative in general. In the explicit families below, that stronger order agrees exactly with this one.

**Established context.** Common-factor ambiguity in blind multichannel identification is well known; Tong and Perreau's survey explains why a common factor of the channels cannot automatically be assigned to the source rather than the channels (§II-B.1, p.1954, eq.12). Our setup is algebraically the same with the names of source and channel reversed (shared filter, multiple unknown inputs). The complete finite-polynomial observations used here are stronger than many practical observation models.

A particularly close conceptual predecessor is Israel Klich's 2026 preprint on positive probability-polynomial factorizations: §2, Example 2.4, Proposition 2.5 and Remark 2.6 discuss competing maximal atomizations, lack of a common positive refinement and finite root partitions. We explore the common-divisor intersection for two observations, rather than the factorization poset of one observation. No exhaustive priority search was carried out.

## 2. Exact obstruction

Let p=1+z+z², r=2+2z+z² and q=1-z+z². Define Y0=p r and Y1=p r q, always understood with normalization at 1.

Raw coefficient vectors (in ascending delay order):

| item | coefficients |
|---|---|
| p | 1,1,1 |
| r | 2,2,1 |
| q | 1,-1,1 |
| Y0 | 2,4,5,3,1 |
| Y1 | 2,2,3,2,3,2,1 |
| p q | 1,0,1,0,1 |
| r q | 2,0,1,1,1 |

The two histories H=p with inputs (r,rq), and H=r with inputs (p,pq), reproduce both normalized outputs exactly. Both H have degree 2 and unit DC gain. The ordinary GCD is p r (up to a unit), since Y1=Y0 q. Yet assigning all of that GCD to H would require the impossible nonnegative input q.

Over the reals p and r are irreducible quadratics (discriminants -3 and -4) and are not proportional. Every normalized common divisor is consequently one of 1,p,r,pr. The first three are admissible and the fourth is not. Thus p and r are incomparable maximal admissible filters, without a common admissible upper bound. This is not merely a numerical optimizer tie, and cannot be resolved by better numerical precision, by knowing the order of the maximal filter, or by the assumption of nonnegativity.

A simpler related failure: the GCD itself need not even have nonnegative coefficients. The two positive outputs p q and r q have GCD q, which is signed and irreducible; only the unit is an admissible common filter. This follows by unique factorization; it is not part of the bounded executable census below.

## 3. An arbitrarily large family

**Proposition (self-contained derivation).** Fix integers m>=2 and k>=1. Select m distinct real numbers a_i in (1/4,1]. Define p_i=1+z+a_i z², t=(m-1)k, G=product_i p_i^k, and q=1-beta z+z², where 1-1/t < beta <= 1. Observations are normalized G and G q^t.

Then the full set of admissible filters is precisely the normalized products H_e=product_i p_i^e_i for nonnegative integer vectors e with sum e_i <= k. The number of admissible filters is binomial(m+k,m), and exactly binomial(m+k-1,m-1) are maximal. Every maximal filter has degree 2k. With beta<1 the two outputs and every admissible factor and quotient have strictly positive coefficients over their full finite supports.

**Proof.** Each p_i is a real irreducible quadratic by discriminant 1-4a_i<0. They are pairwise nonproportional. Since one observation is G, every possible normalized common factor has exactly one representation as H_e with 0<=e_i<=k. It remains to test the second residual.

Write s=sum e_i and M=mk-s, the number of p factors remaining after division. The coefficient of z divided by the constant coefficient of a product of polynomials with nonzero constant terms is the sum of their corresponding ratios (the product rule at z=0). Hence the residual G q^t / H_e has first-lag ratio M-beta t. If s>=k+1, then M<=t-1 and M-beta t<0 by the strict lower bound on beta. It cannot be nonnegative.

If s<=k, M>=t. Pair each copy of q with one of the remaining p_i factors. Their coefficient list is

    p_i q = [1, 1-beta, 1+a_i-beta, 1-beta*a_i, a_i].

Every entry is nonnegative, and all are strictly positive if beta<1. The unpaired p factors also have strictly positive coefficients. Products of positive full-support factors retain positivity, as does normalization. The first residual G/H_e is positive independently. This proves sufficiency.

The exponent vectors are now exactly the integer points of a simplex. Divisibility is coordinatewise comparison; every strict extension is nonnegative because it is itself a product of p_i. The maximal vectors have sum k; any vector with smaller sum can be extended. Counting weak compositions with a slack coordinate yields the first binomial coefficient; counting exact weak compositions yields the second. Degree is twice the sum. This proves the proposition.

For m=2, the maximal ambiguity is k+1; with m=5,k=5 it is 126. With fixed m, the maximal count grows like k^(m-1)/(m-1)!; taking both large yields much faster growth. The model includes the unit filter but all maximal candidates have a nontrivial equal order. It is not claiming every positive observation pair admits this structure.

**Further exact consequence.** On all degree-2k maximal filters H'(0)/H(0)=k, independent of the choice of e. In a probability interpretation, the mean hidden delay is H'(1)=sum_i e_i (1+2a_i)/(2+a_i), using normalized factors. This gives the exact interval of extrema k*min_i (1+2a_i)/(2+a_i) to k*max_i (1+2a_i)/(2+a_i). The possible means are a finite set, not necessarily every real number in that interval.

For example with m=3,k=2, there are six distinct maximal kernels, and knowing the filter length reduces the feasible set of ten to six, not to one.

## 4. The calibration that misses its target

Can two actual leading taps resolve the ambiguity? Not necessarily. Choose m=3,k=2 and

    p1 = [5,5,2], p2 = [25,25,16], p3 = [125,125,113].

The normalized a_i are 2/5,16/25,113/125. Their constant-normalized sums 12/5,66/25,363/125 form a geometric progression, so the first two normalized taps of H_A=p1 p3 and H_B=p2² match. Use beta=7/8, strictly within the proposition's interval (t=4). The raw kernels happen to share the same sum 4356:

| delay tap | H_A numerator | H_B numerator |
|---|---:|---:|
| 0 | 625 | 625 |
| 1 | 1250 | 1250 |
| 2 | 1440 | 1425 |
| 3 | 815 | 800 |
| 4 | 226 | 256 |

Divide each column by 4356. All taps are strictly positive. Gain, length, early ratio and first two actual normalized taps agree; the third tap distinguishes the pair. Both are admissible maximal filters for the same two strictly positive observed sequences.

This is a counterexample to universal identification by two early taps, not a claim that every two-tap calibration fails. A full known nonzero training input S is sufficient in this noiseless complete model: equality H S=H' S implies H=H' by cancellation in the polynomial integral domain. An impulse input reveals the filter directly. No finite-precision stability guarantee follows.

A separate sufficient condition: if the observations have a known admissible decomposition with coprime residuals over the real polynomial ring, their ordinary GCD is exactly H up to scale. If coprimeness is imposed on all explanations, the normalized solution is unique. If it is not imposed, a smaller candidate may still exist. When every real irreducible factor of both outputs is itself nonnegative after normalization (for example strictly Hurwitz-stable probability polynomials), the normalized GCD is admissible and is greatest even under the stronger positive-extension order. These are useful positive regimes; do not generalize the obstruction to them.

### Unbounded ambiguity even after exact two-tap calibration

Choose a geometric progression 2+a_i=C R^i for i=0,...,m-1, with C=5/2 and R=1+1/(10m). All a_i lie in (1/4,1], since R^(m-1)<exp(1/10) and (5/2)exp(1/10)<3. Use the strictly positive beta construction from §3. A maximal normalized filter with exponent vector e then satisfies

    H(0)=C^(-k) R^(-w), H'(0)=k H(0), w=sum_i i e_i.

Thus the first two actual normalized taps depend only on w, which ranges over every integer from 0 to (m-1)k (distribute w among k choices of an integer in [0,m-1]). Since R>1, there are exactly (m-1)k+1 early-tap classes. Distinct exponent vectors remain distinct full filters by unique factorization. The pigeonhole principle guarantees at least one class with at least

    ceil(binomial(m+k-1,m-1)/((m-1)k+1))

distinct filters. This diverges for any fixed m>=3 as k increases, with order k^(m-2). In particular for m=3,w=k the exponents are (j,k-2j,j) for 0<=j<=floor(k/2), giving exactly floor(k/2)+1 distinct filters sharing the two measured taps. Therefore two-tap calibration cannot provide even a universal constant bound on the remaining ambiguity. Full lengths and gain agree as before.

The separate [early-taps.mjs](early-taps.mjs) laboratory independently enumerates exact weak compositions and uses reduced BigInt rational keys for the two taps and complete normalized filters. It checks 4,990 distinct maximal filters across 40 parameter instances (m=2..6, k=1..8), all exact weight-class identities and the pigeonhole bound. At m=6,k=8 there are 1,287 maximal filters, 41 early-tap classes, and the largest class contains 73 distinct filters (weight 20). At m=3,k=8 the largest class contains five. See [early-taps-execution.json](early-taps-execution.json); the core was executed, not the native CLI wrapper.

## 5. Executable qualification

Files: [laboratory.mjs](laboratory.mjs), [execution.json](execution.json), [early-taps.mjs](early-taps.mjs), [early-taps-execution.json](early-taps-execution.json). Run from this directory with Node 18+:

    node laboratory.mjs > rerun.json
    node laboratory.mjs --wav
    node early-taps.mjs > early-taps-rerun.json

The second command writes six original mono PCM files to echo-wavs/. The committed receipt is the core output, not a certificate that the Node wrapper or full repository suite has run.

The oracle uses integer BigInt convolution, independent exact long division (refusing fractional quotient coefficients or remainder), reassembly, coefficient-sign checks and exact cross-products for normalization. It enumerates every exponent vector in [0,k]^m. Completeness over real normalized filters rests on the analytic irreducibility argument, not on a discretization of real coefficients. For m=2..5 and k=1..5 it checks both beta=1 and beta=1-1/(2t), 40 family instances. The early-tap probe is a separate 27-vector family.

| core family count | result |
|---|---:|
| candidate vectors | 30,008 |
| admissible filters | 1,784 |
| maximal filters | 902 |
| strictly positive filter-and-residual cases | 1,333 |
| refused candidates with negative first residual lag | 28,224 |
| failed assertions in final run | 0 |

The strict and boundary families are separate parameter instances, not disjoint empirical populations. The first attempted PCM render allocated 4800 samples and hit a bounds error on the seven-tap observation; the fixed 6400-sample buffer includes an explicit capacity assertion. No receipt was published for the failed attempt.

For the small obstruction, two complete histories give coefficient-identical output pairs. Render every normalized coefficient as the amplitude of a fixed bipolar pulse at 100 ms intervals, with fixed duration 0.8 s, 8 kHz, signed 16-bit mono. This is exact deterministic sonification of the pulse envelope, not a physical room impulse-response measurement. Both histories have byte-identical observed audio for each of the two observations. A pilot that exposes H gives distinct audio. Each array is 12,844 bytes.

| original waveform | FNV-1a |
|---|---|
| observation Y1, both histories | 19988656 |
| observation Y0, both histories | 64a29b2c |
| pilot p | 472f38d0 |
| pilot r | ee3b6be8 |

Fingerprints are noncryptographic; the lab also compares every byte directly. The two pairs are generated from separately multiplied source/filter histories, not simply by duplicating a single byte array.

## 6. Exaptation and refusals

**Interpretation:** the common part of a signal is not necessarily a realizable common cause. If a decoder calls a recurring delay pattern the room, or calls it the speaker, that decision can encode an unstated assumption about the family of physically admissible sources. The latent factorization cannot be inferred from the two outputs alone. The probability generating-function interpretation gives a second exact realization of the mathematics: observed delay can be the sum of independent source and channel delays, with competing latent decompositions. Independence within each model is an assumption; it is not established by the marginals.

**Design hypothesis:** a convolver-organ could present multiple physically admissible source/echo factorizations of the same rendered score. The performer changes the latent attribution while the sound stays fixed, then sends an impulse probe to expose the selected filter. The silence of the distinction before intervention is mathematical, not a claim about listening behavior. A useful engineering interface might retain a candidate set and the signed-quotient refusal, not merely display a best-fit filter. When a known probe is feasible, capture its full response. If only partial calibration is possible, retain the actual samples and uncertainty instead of claiming identification.

**Negative results and scope:** the common-filter obstruction survives complete noiseless observations, equal length and gain, strict positivity, and (for the separate construction) two exact leading taps. It does not survive a full known nonzero input. Adding an extra observation with no further restriction cannot expand the candidate set; copies of existing observations add no constraints. One cannot assume additional unknown inputs have coprime residuals, and extra observations may remove every ambiguity if suitably designed. Signed impulse responses, time-varying channels, noisy or cropped signals, perceptual masking, continuous acoustic wavefields and actual reverberation require different models. A nonnegative finite envelope is not a general physical acoustic transfer function. The strict-beta family gives a nonempty parameter interval within the constructed algebraic family, not robustness to arbitrary perturbation of the data. Arbitrary noisy polynomials need not share any exact factor. No performance or listening trial is implied.

**Cross-domain bridge:** positive factorization of probability polynomials also appears in independent latent counting processes and ligand-binding models, as Klich notes in §1. The common-divisor construction might serve as a toy model of two experiments sharing a hidden independent delay distribution. Whether this transfers to binding sites or measurement instruments is speculative and depends on their actual generative constraints. Do not interpret polynomial irreducibility as semantic or biological indivisibility.

## 7. Source ledger and checkpoint

- Lang Tong and Sylvie Perreau, *Multichannel Blind Identification: From Subspace to Maximum Likelihood Methods*, Proceedings of the IEEE 86(10), Oct. 1998, pp.1951ff. [Author-hosted PDF](https://people.ece.cornell.edu/ltong/papers/TongPerreau.pdf). Accessed 2026-11-24, read introduction and §II-B.1, printed p.1954 (PDF index 3), including eqs.12–14; page image inspected. Survey source for common-factor ambiguity and coprime channel condition; not a source for the simplex proposition.
- Israel Klich, *On Factorizing Aggregate Counting Distributions into Independent Latent Processes*, arXiv:2607.14409, July 15 2026, [preprint](https://arxiv.org/abs/2607.14409). Accessed 2026-11-24; web text exposed §1, §2 definitions, Example 2.4, Proposition 2.5, Remark 2.6, and §4.2 Theorem 4.3/Corollary 4.4. The HTML endpoint failed but the abstract-page extraction contained those passages. Some displayed formulas were missing; no reliance on missing equations. Primary author preprint, peer-review status not established; relevant prior positive-factorization obstruction and finiteness, not claimed to prove our common-filter family.
- The simplex proposition, early-tap pair, bounded census, pulse rendering and interpretation are this expedition's derivations and synthetic experiments. No original sources were copied into the repository. No novelty or independent reviewer claim.

Reconciled live main at 495a98ca12bae467a507031f04931aa4254b1866; read AGENTS, RAG, programme, runbook, integrity and validation documents. Inspected 50 most recently updated open issues and PRs, the first 100 branches and a focused echo branch search; searched for blind deconvolution overlap. Existing #193/#194 is epistemic copying, #199/#200 spectral homometry, #288/#289 moment-null leakage, not this common-factor model. Recent worker #298/#299 handles version-blind reconstruction, not this path. This new issue had zero comments at opening. Branch mhac-300/echo-two-authors; only this directory is owned. No canonical data, manifests, programme files, other workers' branches or production code modified.

ChatGPT (GPT-6.2) performed source reading, derivation, implementation, execution and self-review. No independent human or agent review. Core executed in a bare JavaScript runtime; both exact receipts committed. Full native Node CLI and repository CI must be distinguished from core execution. Draft PR with Refs #300 until those and independent conceptual critique are qualified; no merge or scientific acceptance claimed.

## 8. Fiction: the room that composed the tune

The archivist found two recordings of the same room. He removed their common rhythm and discovered a silence that would have required a negative echo. He tried again, and this time the voice came out of the walls in two different ways.

Both accounts fit the recordings. He measured the first two reflections, found them identical, and declared that the room was now known. The apprentice struck a single wooden block. A third reflection gave him two different answers.

The archivist had not heard a different tune. He had finally asked the room a different question.
