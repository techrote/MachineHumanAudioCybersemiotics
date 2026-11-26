# Beyond truthful reports: the arbitrary finite channel envelope

Addendum to #638, 26 November 2026. The original subset-specific proof led to a stronger result. This document separates the known Doeblin endpoints from the bounded-action interpolation. No priority claim or human result.

## General exact comparison

Let K be any finite row-stochastic channel from n>=2 states to q observed outputs. For nonempty T of states set

    C(T)=sum_y min_{i in T} K(i,y).
    C_m=min_{|T|=min(m,n)} C(T).

Let U_i be the set of outputs y for which K(j,y)=0 for every j!=i, and put

    sigma=min_i sum_{y in U_i} K(i,y).

Outputs of zero probability in every state cause no issue. For at most m>=2 actions and normalized prior-weighted losses a_j(i)>=0 with row minima zero, define L=min_j sum_i a_j(i), R=sum_y min_j sum_i K(i,y)a_j(i). Then the sharp envelope is

    C_m L <= R <= (1-sigma)L.

For L>0 both bounds are attained for any fixed full-support prior with suitable finite losses. This specializes to the subset theorem exactly: C(T)=c(T) and exclusive output mass is singleton weight. It works even for ambiguous labels whose likelihoods are not constant.

Lower proof: pick a minimizing action j(y) for each output, define b_j(i)=sum_{y:j(y)=j} K(i,y), choose i_j minimizing b_j(i). Then R>=L sum_j b_j(i_j). With T={i_j}, sum_j b_j(i_j)=sum_y K(i_{j(y)},y)>=sum_y min_{i in T} K(i,y)>=C_m. To attain equality, use one loss column per distinct state in a minimizing T, with cost 1 exactly there and 0 elsewhere. Each has total 1; optimum risk is the sum of pointwise minima. No stochastic policy can beat the pointwise minimizer. Pad with duplicates if desired.

Upper proof: choose a baseline-optimal action; replace it by a zero-loss action only on unambiguous outputs U_i. This gives risk <=(1-sigma)L. For equality choose i attaining sigma. Action A has weighted loss 1 at i and zero elsewhere. Action B has zero at i and constant M>=1 at all other states. Pick finite M large enough that for every output with positive likelihood at i and at another state, M sum_{j!=i} K(j,y) >= K(i,y). Such M exists because the output alphabet is finite. Baseline is 1 and optimum risk on each ambiguous output is K(i,y), zero elsewhere. Hence R=1-sigma. Any full-support prior is incorporated by dividing weighted costs by the prior; rescale both columns to place raw losses in [0,1] if desired. The ratio is invariant under rescaling. If prior has zeros, bounds still hold but attainment is not guaranteed.

Consequently, a reveal-or-erase channel with reveal probability p dominates K on every decision with <=m actions iff p>=1-C_m. K dominates the reveal channel on all such decisions iff p<=sigma. For unrestricted action sets the endpoints already settle full Blackwell dominance: C_n is the Doeblin coefficient, and sigma is the maximal universally extractable exact-reveal probability. An explicit forward garbling exists when 1-p<=C_n: use the erasure output to sample from the normalized pointwise minimum of all channel rows; use revealed states to sample from the remaining normalized probability mass. Conversely any garbling must reserve that common mass across all rows. The reverse garbling thins the exclusive outputs. Treat zero-probability branch endpoints separately.

## Prior art and distinct scope

For m=2, 1-C_2 is the familiar maximum pairwise TV distance between channel rows (one half of their L1 distance). For m=n, C_n is the standard Doeblin coefficient. The full-action erasure degradation criterion is established in Makur and Singh, *Doeblin Coefficients and Related Measures*, arXiv:2309.08475v2, 2 July 2024, Definition 1, equation (1), and Lemma 1. Their proof of Part 8 on printed p. 11 also explicitly connects the Doeblin coefficient to minimum wrong-guess probability with identity loss and a uniform prior. The source was read at these passages on 26 November 2026, and original images of printed pp. 1 and 11 inspected. URL https://arxiv.org/pdf/2309.08475. The bounded-action interpolation and two-sided ratio proof above are self-contained; the endpoints and particular witness family have direct prior overlap. No exhaustive novelty audit was conducted.

Bertschinger and Rauh (2014) already discuss Blackwell's k-decision orders in §3 and give the three-state counterexample in Example 18; see README. This addendum is a specific exact calibration of those orders against one reference experiment, not a characterization of arbitrary comparisons of two arbitrary channels.

## Repetition changes its meaning

For d conditionally independent samples from a fixed state, let K_d(i,y_1,...,y_d)=product_l K(i,y_l). Then C_m(K_d)>=C_m(K)^d because the minimum of products is at least the product of the corresponding minima. Equality holds for constant-on-subset reports as proved in README, but NOT generally for arbitrary channels: the same input state must minimize the likelihood of the entire tuple. This is not the independent-input tensor product, which allows a different unknown state at each coordinate.

Example: two states, binary symmetric channel K=[[3/4,1/4],[1/4,3/4]]. C_2(K)=1/2; C_2(K_2)=1/2 (not 1/4), since opposite observations tie. Compare with p=2/5 reveal-or-erase. One reveal has residual ratio 3/5, greater than 1/2, so it fails forward dominance. Two reveals have residual ratio 9/25, below 1/2, so forward dominance now holds universally. The reverse cannot hold at either horizon because the binary symmetric channel has no exclusive outputs. The single-shot channels are incomparable; after two observations the reveal channel dominates. Thus the no-reversal repetition result in README is genuinely specific to the subset family.

The general laboratory also verifies this example through d=10. No claim that arbitrary comparisons always reverse or that this particular result persists to all horizons is made based on a finite census.

## Tiny noise and a discontinuity

A channel whose entries are all strictly positive has sigma=0. Therefore even an almost-perfect such channel fails to universally dominate a reference experiment with any positive reveal probability, however small. The high-penalty witness in the upper proof can magnify rare ambiguities until a particular observation is not worth acting upon. This does not imply large absolute performance loss: the normalized baseline L may itself be arbitrarily small after bounding raw losses. The relative criterion and absolute utility bounds are different. Explicitly distinguish support zeros from merely small probabilities when applying the theorem to estimated acoustic confusion matrices.

By contrast C_m is continuous: if every row of K differs from the corresponding row of K' by TV at most epsilon, then |C_m(K)-C_m(K')|<=min(m,n) epsilon. For fixed T, a decrease in its overlap at output y is at most sum_{i in T} (K(i,y)-K'(i,y))_+, whose sum over y is at most |T|epsilon; exchange K and K' for the opposite direction. Taking minima preserves the bound. The forward threshold therefore has a quantitative sensitivity bound. Estimating a true zero for the reverse threshold would require a much stronger observational contract.

## Qualification

The executable general.cjs implements arbitrary finite integer-weight channel matrices (common row denominator) and calculates literal minimum expected loss. It enumerates every row-stochastic channel with denominator 2, two or three states, two or three outputs; for these it enumerates all normalized binary-loss matrices over the allowed menus. Seeded channels through seven states and broader integer losses extend the census. All arithmetic comparisons are exact in the bounded integer domain.

Actual V8 function execution: 438 channel profiles, 114,315 loss matrices (68,229 positive baseline), 1,131 lower and 1,131 upper endpoint checks, 10 repetition checks, no failures. Source body serialized directly to general.cjs, receipt general-execution.json. The CLI wrapper was not executed in a full native repository checkout. This is same-agent computational verification and proof, not independent peer review. The original local PCM specimens remain subset-specific; no general physical acoustic channel was acquired.

## Research interpretation

The exact family of action-menu audits now reduces to computing a sequence of restricted row-overlap coefficients. An acoustic receiver with a known confusion matrix can use this sequence to compare its decision value to a calibrated reveal-or-erase baseline. The stipulated noise model, priors, allowed losses, and action alternatives remain distinct from human perceptual performance. Reporting the whole sequence is preferable to making an unrestricted claim from its first entry. A useful contrary design is to communicate the state directly, or provide an interactive clarification query whose decision model changes. No claim of unique semiotic explanatory power.
