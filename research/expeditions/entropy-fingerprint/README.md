# The Entropy Curve That Recognizes Its Instrument

Research expedition #686, 26 November 2026. Additive mathematical note, not a canonical Track E/G finding. AI agent derivation and synthetic checks; no independent human review or priority assertion.

## Abstract

A single Shannon information number is not a complete decision certificate. Surprisingly, the *whole* prior-dependent mutual information curve of a finite channel is complete up to Blackwell equivalence. For binary input and at most m distinct posterior values per channel, any 2m-2 distinct interior prior evaluations suffice, and fewer fixed evaluations cannot universally suffice. The same sharp count applies to curvature evaluations and to the derivatives of orders 2 through 2m-1 at the fair prior. Exact reconstruction can be extremely ill-conditioned. Even two-output channels admit a cubic information discrepancy but a linear decision-value discrepancy. This is a finite mathematical model of acoustic confusion tables, not an empirical perceptual claim.

## Canonical posterior coordinates

Let K be a binary-input row-stochastic channel; label the two input rows + and -. Discard columns zero in both rows. For output y put

    w_y=(K(y|+)+K(y|-))/2,
    t_y=(K(y|+)-K(y|-))/(K(y|+)+K(y|-)).

The probability law mu = sum_y w_y delta_(t_y) on [-1,1] has mean zero. Conversely every finitely supported such law defines a channel with rows w_y(1+t_y), w_y(1-t_y). Merge repeated t values. This loses only output labels and conditionally state-independent splitting: a merged column can be split back in the original w proportions, regardless of input. Equal mu therefore means mutual output garbling, and all finite decision risks are equal for every prior. Conversely, if mutual garbling holds, data processing gives equality of the information curves and the proof below recovers mu. No relabelling of the input states is allowed.

This is the centered Blackwell measure (Goela and Raginsky, v2, Section II.A, Definition 3 and Theorem 1; Section II.B equation 5). It is not the paper's conditional D-distribution. Distinct posterior values, not raw output count, govern the following budget.

Write u=2P(+)-1 in [-1,1], I_mu(u)=I(X;Y) in nats and g(v)=(1+v) log(1+v) with g(-1)=0. The output marginal is w_y(1+u t_y). Expanding the entropy difference gives

    I_mu(u)=int [ (1+u)/2 g(t)+(1-u)/2 g(-t)-g(ut) ] dmu(t).
    -I_mu''(u)=int t^2/(1+ut) dmu(t)   for |u|<1.

All channels have I(-1)=I(1)=0. The normalized curvature is a rational Stieltjes-type transform. In particular

    I_mu^(k)(0)=(-1)^(k-1)(k-2)! int t^k dmu(t), k>=2.

The missing moments k=0,1 are known (1,0). Thus the full entropy curve determines all moments; alternatively use the finite rational proof below. The logarithmic expression is continuous at both endpoints even for deterministic outputs.

## Sharp finite prior sweep

**Theorem.** Let two binary-input finite channels have at most m distinct posterior contrasts each (m>=1). If their information curves agree at any 2m-2 distinct priors strictly inside (0,1), then the channels are Blackwell-equivalent. The number of scalar samples is minimal for universal identification among this class.

Proof of sufficiency: subtract their measures, writing nu=sum_i c_i delta_(t_i) on r<=2m distinct surviving nodes with all c_i nonzero. Its total mass and first moment vanish. If nu is nonzero then r>=3. Write F=I_mu-I_lambda, and D(u)=product_i(1+ut_i). D is strictly positive in the open interval. The rational function

    H(u)=sum_i c_i/(1+ut_i)=u^2 sum_i c_i t_i^2/(1+ut_i)

has numerator of degree at most r-1 over D, including the case of a node t=0. The numerator is divisible by u^2 since H(0)=H'(0)=0. Consequently -F''=H/u^2 has a numerator polynomial of degree at most r-3. It is not identically zero: a nonzero t_i gives a distinct pole at -1/t_i with nonzero residue in H; a signed measure supported only on zero cannot have mass zero unless it vanishes. Hence F'' has at most r-3 distinct interior zeros.

If F has k distinct interior zeros, then F(-1)=F(1)=0 supplies two further zeros. Rolle's theorem twice yields at least k distinct interior zeros of F''. Thus k<=r-3<=2m-3 for any nonequivalent pair. For m=1 the only mean-zero law is the singleton at zero, so no samples are needed.

The same rational numerator proves that any 2m-2 distinct interior measurements of -I'' suffice. There is no need to assume the sample priors are regularly spaced or selected adaptively. Equality at the endpoints alone never distinguishes channels.

**Sharpness of the scalar count.** For m>=2 use the open family of two labelled row distributions on m outputs with all entries positive, distinct ordered t values, and row sums one. Parameterize each row by its first m-1 probabilities. The open parameter domain is nonempty (e.g., take equal w and distinct equally spaced small centered t values) and has real dimension d=2m-2. Ordered columns make this parameterization injective on Blackwell classes. At any fixed k<d priors, the map from this domain to k mutual information values is smooth. The same is true for k fixed curvature values or k specified local derivatives. Choose a point at which its Jacobian achieves its maximal rank r0. A nonzero maximal minor stays nonzero on a neighborhood; the maximality gives constant rank there (if r0=0 this holds everywhere). The constant-rank theorem produces a local fiber of dimension d-r0>0. Distinct channels on that fiber are not equivalent. Thus no fixed choice of fewer samples can guarantee recovery. This is an existence argument for real channels; no claim of a rational collision at every prescribed set of priors. It does not lower-bound arbitrary discontinuous encodings or adaptive queries.

## Exact curvature-jet collision and reconstruction

The derivatives of orders 2,...,2m-1 at u=0 identify mu. Indeed, the first 2m moments indexed 0,...,2m-1 determine any signed measure with at most 2m nodes: its Vandermonde moment matrix has full column rank. This is a second proof for this measurement contract.

For a constructive sharp counterexample let n=2m-1, choose equally spaced t_j=h(2j-n) with 0<h<1/n, j=0,...,n. Give law A the even-indexed nodes and B the odd-indexed nodes, each with weights binomial(n,j)/2^(n-1). Both have m nodes, total mass one and mean zero. The alternating finite difference of any polynomial of degree <n vanishes, so the moments match through degree 2m-2. The degree n moment differs. Since n is odd, B is the reflection of A, so their fair-prior information also agrees exactly (the integrand at u=0 is even), and I_A(u)=I_B(-u). They are not equivalent. This explicit rational family survives arbitrarily long but finite curvature-jet audits if the support bound is removed. The fair-prior first derivative is NOT claimed equal. For m=2, their rows at h=1/4 are respectively [1,15]/16, [7,9]/16 and [9,7]/16, [15,1]/16 (outputs ordered by contrast; rows + then -). Both are strictly positive.

**Reconstruction.** Given exact moments through degree 2m-1, find s=rank of the m by m Hankel matrix H_ij=M_(i+j) for 0<=i,j<m. Its rank equals the number of distinct support points by its Vandermonde Gram factorization and positive weights. Solve the s by s leading principal system H_s a=-(M_s,...,M_(2s-1))^T. It is positive definite. The monic polynomial z^s+sum_(j=0)^(s-1) a_j z^j vanishes at every support node: the equations imply the vector of its values weighted by the masses is killed by an invertible Vandermonde matrix. Recover its real roots, then solve the Vandermonde weight equations from M_0,...,M_(s-1). Reject nonpositive weights, out-of-range roots, residual mismatches and invalid normalization. This is an exact mathematical algorithm, not a numerical tolerance prescription. The laboratory verifies the annihilating recurrence on known nodes; it does not implement general root recovery.

## Decision-value counterexample and conditioning

Take m=2 and t=(-3h,-h,h,3h) with A masses (1/4,0,3/4,0), B masses (0,3/4,0,1/4). At fair prior, an action whose payoff is +1-k in state + and -1-k in state -, with abstention payoff zero, has optimal expected payoff E[(t-k)_+]. Choose k=h. A obtains zero, B obtains h/2; at k=-h the preference reverses (A obtains 3h/2, B obtains h; check by direct evaluation). More precisely at k=-h: A obtains (3/4)(2h)=3h/2, B obtains (1/4)(4h)=h. Thus the channels are Blackwell-incomparable although their fair-prior Shannon information and curvature agree. At h=1/4, the payoff advantage is 1/8 in either appropriate comparison. Payoffs are bounded by 2 and may be affinely normalized to [0,1].

The power series g(v)=v+sum_(j>=2)(-1)^j v^j/[j(j-1)] has absolute convergence for |v|<1. If two laws match moments through L>=1 and are supported in [-rho,rho], rho<1, their uniform information-curve discrepancy is bounded by

    sup_|u|<=1 |I_A(u)-I_B(u)|
      <=4 sum_(j>L) rho^j/[j(j-1)]
      <=4 rho^(L+1)/[L(L+1)(1-rho)].

The factor 4 follows from the total variation norm <=2 and a coefficient bounded in magnitude by 2. For the two-node collision family L=2 and rho=3h. The first differing moment is M_3(A)-M_3(B)=-12h^3. Its contribution gives uniformly

    I_A(u)-I_B(u)=2h^3(u-u^3)+O(h^5).

All even moments match by reflection, hence the fifth-order remainder. The supremum is asymptotic to 4h^3/(3 sqrt(3)), while the decision gap is exactly h/2. No universal Lipschitz bound of bounded decision-value discrepancy by sup information-curve discrepancy exists even with two posterior values per channel. This does NOT imply that an arbitrarily large absolute decision gap can persist as the whole curve difference tends to zero. For fixed finite input cardinality, compactness of posterior laws and injectivity of the full curve instead imply qualitative continuity of the inverse in the weak topology (the integrands are continuous); quantitative conditioning remains a separate question.

## Beyond binary input

For n input states take the uniform prior p0=(1/n,...,1/n). For each nonzero column define w_y=sum_i K(y|i)/n and b_y=(K(y|i)/w_y-1)_i in the zero-sum subspace. Then sum_y w_y b_y=0, and b_y encodes the uniform-prior posterior vector. Let v be any zero-sum direction and p=p0+uv remain in the interior for u sufficiently small. The marginal output is w_y(1+u v dot b_y). The conditional entropy term in I is affine in u, so

    -d^2 I(p0+uv)/du^2=sum_y w_y (v dot b_y)^2/(1+u v dot b_y).

Suppose two finite channels have identical I(p) on the entire simplex (indeed any open neighborhood of p0 suffices). Choose a direction v outside the finitely many hyperplanes perpendicular to differences between distinct b vectors in the union of their supports. This v separates all those vectors. Equality of the above transforms recovers the projected signed measure by the same rational-pole proof, and injectivity of the projection on the union gives equality of all original masses. Equal posterior laws imply mutual garbling by the same splitting construction. Thus full prior-surface equality is equivalent to Blackwell equivalence for all finite channels. The chosen direction depends on both channels; a single fixed generic-looking line is not a universal multistate certificate. No minimal multivariate sample budget is claimed.

This is an equality result, not an order result. Pointwise inequality of information for all priors need not imply Blackwell dominance (Rauh et al., 2017, section 1 and Proposition 2). There is no contradiction.

## Acoustic interpretation and negative controls

A synthetic acoustic dictionary can realize the two m=2 channels by emitting one of two distinct tones according to the rational row probabilities. At the fair prior each score can be built as an exact 32-episode inventory: 16 labelled + trials and 16 labelled - trials. A's conditional output counts are (1,15) and (7,9); B's are (9,7) and (15,1). The emitted tone labels are arbitrary; the actual posterior is determined by the conditional table. The proposal is to sonify both the tone and the associated posterior decision, not to claim a listener can recover the hidden truth.

Negative controls: raw output identity is not recoverable (proportional columns split freely); input swaps are NOT allowed unless the posterior law is invariant; finite measured equality within tolerance is not exact equality; symmetric capacity is one fair-prior number, not the whole prior curve; prior-dependent decoder behavior breaks the fixed channel assumption; repeated acoustic measurements may be correlated; empirical priors and actual conditional channels must be separately estimated. If the labelled confusion table is available directly, computing its posterior classes or task risks is simpler than estimating entropy derivatives. A universal equivalence test is unnecessary when only a single action question matters.

Interpretation: a scalar summary may be an incomplete sign, yet a controlled family of the same summary can identify the full decision experiment. The difference is variation of the measurement context, not added expressive power of the individual tone. This is a mathematical exaptation, not evidence for any unique cybersemiotic mechanism. Fiction: a clerk certifies two instruments by the same number; an apprentice changes the prior weight of the two possible worlds until the ledgers disagree.

## Source and verification ledger

- Goela, Naveen; Raginsky, Maxim. *Channel Polarization Through the Lens of Blackwell Measures*, arXiv:1809.05073v2 (7 September 2020), https://arxiv.org/pdf/1809.05073 . Read abstract, Sections II.A/B, definitions 3/4, Theorem 1 and equation (5); inspected image of printed page 3 (PDF index 2). Accessed 26 November 2026 by this AI agent. Direct prior ancestry for posterior measure and equivalence; not claiming that definition. **Source caution:** the sentence immediately after equation (5) in this version asserts symmetry of the unconditional centered posterior law without a symmetry assumption. Taken literally for arbitrary BICs this is false: the explicit A law here has mean zero but support {-3/4,1/4} with unequal masses and is not reflection invariant. This is a passage-local mathematical counterexample, not an allegation about the authors or all versions; no published correction search completed. Theorem 1 itself agrees with the general mean-zero law construction.
- Rauh, Johannes et al. (2017), *Coarse-Graining and the Blackwell Order*, Entropy 19(10), 527, https://doi.org/10.3390/e19100527 . Read publisher HTML abstract and Section 1 including Theorem 1 and discussion of more-capable versus Blackwell order. Accessed 26 November 2026. The ordering distinction is established prior art. We do not claim exhaustive novelty for equality or finite sweep results.
- Kunis, Stefan; Peter, Thomas; Römer, Tim; von der Ohe, Ulrich (2016), *A multivariate generalization of Prony's method*, Linear Algebra and its Applications 490, 31–47, https://doi.org/10.1016/j.laa.2015.10.023 . Publisher abstract and opening of introduction only; background for moment reconstruction, not invoked to justify a theorem here.
- Repository ancestry: #638 GENERAL-CHANNELS.md read in full (arbitrary decision envelopes); #676 identified from live issue census and prior expedition context, not a new complete reread. These are synthetic internal research notes, not literature evidence.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity, validation read; 403 branch entries, 100 open issue results and 100 open PR results inspected; targeted issue searches for mutual information/Blackwell, entropy/curvature, posterior/moments and information/fingerprint. No matching active scope found. Previous expedition #683 exact-head workflow 45804492135 reported success. No shared manifests edited. New issue #686 and its empty comment history retrieved. The report, laboratory and receipt are scoped to this issue. The laboratory's function was executed in V8 directly, not a full native repository checkout; the CLI wrapper and repository-wide checks are not established by that run. See execution.json for exact counts. Independent critique and repository qualification remain outstanding. No participant data, human validation or scientific priority asserted.
