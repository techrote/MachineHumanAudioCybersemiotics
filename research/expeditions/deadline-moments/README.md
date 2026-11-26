# The Deadline That Survives Every Moment

MHAC expedition #676 · 26 November 2026 · original synthetic mathematical derivations, computational checks and acoustic specimens. Not a frozen-corpus contribution or human validation.

## The anomaly and exact contract

A latency archive may contain the population mean, variance and any fixed finite number of higher raw moments, all measured exactly. Yet an operational deadline is a discontinuous functional of latency, not itself a moment. We ask for the largest difference in deadline success between *two* latency distributions sharing those moments. The common moment values are free to vary in this worst-case question, not fixed in advance. Compare #654 (read complete report and issue; no comments): its ambiguity is in a latent paired-readiness coupling, while this one occurs for a single fully specified latency variable compressed to moments. Direct empirical deadline counts are the essential baseline.

Established ancestry: Bertsimas and Popescu, *Optimal Inequalities in Probability Theory: A Convex Optimization Approach*, SIAM J. Optim. 15(3), 780–804 (2005), [DOI](https://doi.org/10.1137/S1052623401399903), [author-hosted paper](https://web.mit.edu/~dbertsim/www/papers/ioana/Optimal-inequalities-in-probability-theory-A-convex-optimization-approach-SIAM15.pdf). Abstract, §1 Definition 1.1 and 1.2, printed pp.780–781 read including original image of p.781. Their problem fixes a moment vector and optimizes an event probability; our worst-fibre diameter is different but closely related. Han, Jiao and Weissman, *Local moment matching*, COLT 2018, PMLR 75, [paper](https://proceedings.mlr.press/v75/han18b/han18b.pdf), Appendix B.1, Lemma 25 and equation (24), printed pp.23–24 read and images inspected. They give moment-matching / uniform polynomial approximation duality for continuous functions on a compact positive interval. We use the same duality on a finite grid (where every function is continuous), derive it below, and separately handle the discontinuous threshold on a continuum using explicit witnesses. Neither article is claimed fully read. No novelty priority is asserted for general moment optimization, LP duality or interpolation.

## A deadline can disagree arbitrarily strongly

Let k>=1. Take k+2 distinct ordered rational nodes x_i. Set

    w_i = 1 / product_(j!=i)(x_i - x_j).

The Lagrange interpolation formula for x^r, r<=k, says the coefficient of x^(k+1) is zero, hence sum_i w_i x_i^r=0. In particular the positive and negative weights have equal total mass M>0. Their respective normalized positive and negative parts are two probability laws with identical moments through order k. The signs alternate along the sorted nodes. This is a constructive exact rational witness, not a floating-point fit.

Choose nodes -1, 1, D, 2D, ..., kD with integer D>=2 and deadline zero. Choose the overall sign to make w_0 positive. Only the negative node -1 is early; the negative-weight law has no early mass. For fixed k as D increases, the first two absolute weights are asymptotic to 1/(2 k! D^k). Every anchor weight at jD is O(D^(-k-1)), since all k+1 factors in its denominator scale with D. Therefore the first positive node's normalized mass tends to one. Rescale x by kD, then apply an affine transformation to any bounded interval with an interior deadline (choose scale small enough to fit both sides). The moment equalities survive any affine transformation. Thus even with known bounded support and an exact finite archive, the worst-fibre diameter of deadline probability is one, as a supremum. It is not attained for k>=1: if one law has every latency <=deadline and the other every latency >deadline, their means cannot agree. For k=0 it is attained. This argument does not fix one nondegenerate moment sequence while D varies, and cannot be read as saying every given moment vector is uninformative.

The minimax absolute error for estimating a deadline success probability from only these exact moments, uniformly over all allowed laws on the interval, is exactly 1/2: each indistinguishable pair forces at least half its probability gap on one member, and the constant estimate 1/2 attains the uniform bound.

For k=2, D=5 the integer signed witness (up to sign) is (30,-55,33,-8) at (-1,1,5,10), common mass 63. Shift by 2 to obtain positive latency slots (1,3,7,12), deadline 2. Law A has 30/63 at slot 1 and 33/63 at slot 7; law B has 55/63 at slot 3 and 8/63 at slot 12. Common mean 29/7 slots and second raw moment 183/7 slots², variance 440/49 slots². Deadline success 10/21 versus zero. With k=12 and D=1,000,000 the exact construction achieves gap approximately 0.999235759; this is a mathematical finite-weight construction, not an acoustic hardware resolution claim.

## Sharp finite-grid compiler

Let x_1<...<x_n be distinct known permitted latencies, and f_i an arbitrary real objective (for a deadline, f_i=1[x_i<=h]). For two laws p,q with matching moments through order k, let z=p-q and V be the Vandermonde moment matrix with rows r=0,...,k. Then Vz=0 and ||z||_1<=2. Conversely any z satisfying those constraints is a difference of two probability vectors: normalize neither part, but add the same nonnegative remaining mass to each until both total one. Hence the maximum objective gap equals

    max { f.z : Vz=0, ||z||_1<=2 }
      = 2 min_(degree(g)<=k) max_i |f_i-g(x_i)|.

The equality follows from finite-dimensional norm duality (or LP duality on positive/negative parts). For any polynomial g the upper bound is immediate from Vz=0. The dual has one uniform error bound, and no duality gap by finite LP feasibility and boundedness. This is established approximation-theoretic machinery; our compiler below makes the extremizers explicit.

If k>=n-1, the moment matrix has rank n and the gap is zero. Otherwise a nonzero optimal gap is attained at a vertex with norm 2. If its support has more than k+2 coordinates, one can solve the homogeneous moment equations plus the sign-weighted sum equation for a nonzero perturbation on that support. Small positive and negative perturbations preserve signs, norm and moments, contradicting extremality. A nonzero kernel vector cannot have <=k+1 coordinates by Vandermonde rank. Thus every nonzero optimizing vertex uses exactly k+2 nodes and its signed weights are proportional to the interpolation weights above. (If the objective is already polynomial on the grid, all gaps are zero.) Enumerating the k+2 subsets and maximizing |sum f_i w_i|/M gives an exact finite algorithm and an explicit pair of distributions. It is combinatorial, not recommended for large n; an LP is the scalable baseline. The committed laboratory uses exact integer weights, not numerical rank thresholds.

For equally spaced nodes indexed 0,...,n-1 at k=n-2 there is just one support. The weights are alternating binomial coefficients of order n-1. For a deadline at index j (0<=j<n-1), the alternating partial sum equals ±binomial(n-2,j). Hence the exact gap is binomial(n-2,j)/2^(n-2); one further moment removes it entirely. In a grid symmetric about a central cut with no node at the cut, the step objective minus 1/2 is odd. Symmetrizing any polynomial approximant into its odd part cannot worsen its error. Therefore raising an odd moment budget by one (adding an even degree) never improves the worst-fibre diameter for that particular symmetric grid/cut. This is not an assertion about a fixed observed archive or asymmetric deadlines.

For 10 nodes 0..9 and deadline 4, the computed sharp gaps at degrees 0..9 are 1, 4/5, 4/5, 4/7, 4/7, 23/58, 23/58, 35/128, 35/128, 0. More even-order moments are not automatically more informative for this particular worst-case target.

## A guard band changes the contract

Assume latency has been centered and rescaled to [-1,-delta] union [delta,1], for 0<delta<=1, with deadline zero. This is a true support exclusion, not a tolerance silently applied to a measured value.

For k=1 or 2 the exact worst-fibre gap is (1-delta)/(1+delta). To see the upper bound, approximate sign(x) by 2x/(1+delta), whose maximum error on the allowed support is (1-delta)/(1+delta). Since the deadline indicator equals (1-sign(x))/2, and moments match, the bound on the gap equals this error. It is sharp: put probability 1/(1+delta) at -delta and delta/(1+delta) at +1, and reflect the law for the comparator. Both have mean zero and the same second moment delta. Their deadline probability gap is exactly the bound. For delta=1 they coincide.

For larger k, let m be the largest odd integer <=k. Define the polynomial g_m(x) as the probability that a Binomial(m,(1+x)/2) variable has a strict negative-majority outcome (at most (m-1)/2 successes). For x>=delta its maximum error is the binomial lower tail at p=(1+delta)/2, by monotone coupling; on the negative interval reflection gives the same error. The gap is therefore at most min(1, 2 Pr[Bin(m,(1+delta)/2)<m/2]). An exponential but looser closed bound is min(1,2(1-delta²)^(m/2)): apply the exponential Markov inequality to the centered Bernoulli sum, optimizing the exponent to obtain sqrt(1-delta²) per trial. This is only a sufficient bound, not a sharp general k>=3 formula. The finite-grid compiler provides sharp answers for specified discrete supports. A known guard can be an operationally meaningful way to constrain the inference, but if the guard contains real events, those events must be logged or accounted for rather than silently dropped.

## A second repair: exactly how many deadline receipts complete the archive?

For n distinct known permitted latencies, suppose the first k moments are known, with 0<=k<=n-1. Define cumulative probabilities C_i=P(X<=x_i) at the n-1 nontrivial boundaries. Summation by parts gives, for r=1,...,k,

    E X^r = x_n^r - sum_(i=1)^(n-1) C_i (x_(i+1)^r - x_i^r).

**Theorem:** any n-k-1 of the n-1 CDF receipts suffice to recover the entire distribution; this count is necessary for universal identification by fixed scalar linear receipts.

Proof: k boundaries remain unknown. The k×k coefficient matrix consists of the corresponding columns of the differences of powers. For ordered unknown boundary indices i_1<...<i_k its determinant equals

    (product_(r=1)^k r)
    * integral_[x_i1,x_(i1+1)] ... integral_[x_ik,x_(ik+1)]
        product_(a<b)(t_b-t_a) dt_1 ... dt_k.

Use multilinearity to move the column integrals outside the determinant of monomials. The Vandermonde is strictly positive on the product of interval interiors, so the determinant is positive. Hence every choice of k unknown boundaries can be solved uniquely. Recover cell masses by consecutive CDF differences, appending C_0=0 and C_n=1. The moment fibre at a strictly positive probability vector has dimension n-k-1 by Vandermonde rank, so fewer fixed linear receipts have a nonzero kernel and cannot identify all distributions. For k=0 all boundaries are needed; k=n-1 requires none. This theorem is about exact scalar population data; closely spaced nodes or noisy high-order moments can be badly conditioned. Directly measuring the target deadline, or keeping the latency histogram, is the simple baseline; full reconstruction is not necessary if only one threshold matters.

## Computational qualification and acoustic score

Run node laboratory.cjs (no dependencies). It prints execution.json. The same function was executed before commit; all weights and determinant checks use BigInt. It tested 114,384 candidate supports across 595 compiler profiles, 468,503 individual exact moment identities, 84 approaching-threshold constructions, 90 sharp first/second-order guard cases, and 8,178 exact positive CDF-minor determinants on a nonuniform integer grid. All assertions passed. These counts include overlapping checks, not independent experimental trials.

A separate native Python witness uses exact Fraction interpolation and a direct SciPy LP over two full probability vectors, not the support-reduction theorem. 275 LP cases on uniform and irregular grids agreed with the exact compiler to maximum absolute error 3.47e-14. It renders the 63-episode inventories above as stereo pulses, 400 Hz start in left channel, 800 Hz completion in right, 8 kHz PCM16, 10 ms latency slots, 140 ms episodes. Deadline at 20 ms. 126 completion times and start markers were decoded from actual PCM by slot energy. Both native runs reproduced the receipt and WAV hashes; see native-execution.json. The WAVs are delivered separately; the Python witness regenerates them. These are deterministic shuffled score inventories, not sampled human trials or real machine latency measurements. No perceptual claim is made.

## Exaptation, negative results and disposition

Design hypothesis: an acoustic telemetry system should declare the actual decision boundary, log its success/failure count (including missing or censored episodes), and retain the histogram when future thresholds are expected. Reporting the variance or higher moments alone is not a substitute. A soft deadline loss can be approximated by polynomials more effectively than a hard indicator, but replacing the operational loss with a smooth proxy changes the task. Test paired systems using the same logging budget: raw timestamps, direct counts, sparse CDF receipts, moment receipts, guard-band reports. Avoid treating exact moment agreement as equality of distributions, or treating compatible distributions as measured human behaviour.

Negative controls: the near-complete disagreement is a supremum over moment vectors, not a claim for every fixed vector; zero variance identifies a constant; n-1 exact moments identify a known n-point grid; the guard-band guarantee assumes the exclusion is real; nonlinear or adaptive measurements have different budgets; the LP concerns exact moment equality, not measurement noise or sampling uncertainty. The near-threshold example becomes physically difficult to render at fixed temporal resolution. Conventional approximation theory and probability explain these findings; no extra explanatory contribution from cybersemiotics, operational safety certification, or scientific priority established.

Artistic interpretation: an instrument plays pairs of pulse scores with identical reported moment signatures, but the success voice changes when the deadline crosses the concealed mass. Let the performer choose the reported moments, threshold and actual guard band. The exact compiler and offline acoustic specimen exist; the live instrument is speculative.

Reconciliation: default main 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, README, RAG, programme, runbook, integrity, validation; no nested research/AGENTS or research/expeditions/AGENTS found. Reviewed 398 live branch entries, 100 recent open issues and 100 open PR results; targeted searches for moment matching, deadline/moments, polynomial approximation, moment/latency and moment/quadrature returned no results. Read #654 and its complete report; #670 predecessor report and successful exact-head PR #671 workflow inspected. Created and read back #676 and comments (empty); isolated branch from recorded main. Native Git ls-remote failed DNS. No canonical manifest, accepted protocol, another worker's branch or shared aggregate changed. One ChatGPT agent performed derivations, source readings and computational self-checks; no independent human review. Draft for active integrator, independent critique and full repository checks; no merge or scientific acceptance claimed.

*Fiction:* A clerk adds a new column to a ledger every year, each a more elaborate power of the time at which a bell rings. His apprentice draws a single line through the score and asks which bells arrived before it. The archive has grown rich in numbers, but the question was never one of its columns.
