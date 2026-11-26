# The Ear That Needs a Third Choice

MHAC expedition #694, 26 November 2026. Additive mathematical exploration and synthetic acoustics; not canonical Track E/G evidence. AI-agent proofs, source inspection, exact rational computation and same-agent independent-method LP cross-check. Independent critique outstanding.

## Abstract

A binary acoustic confusion channel can be reconstructed from an exact prior-dependent Shannon-information curve (#686), yet entropy identification is badly conditioned. We instead quantify the largest operational discrepancy for a fixed fair prior and **all** finite action menus with payoffs in [0,1]. An exact compiler requires at most three actions; the best two-action audit can underestimate the discrepancy by a factor arbitrarily close to two. A classical Bayes-accuracy sweep supplies a particularly well-conditioned alternative receipt: a grid of prior probabilities with maximum spacing h estimates the unrestricted decision gap to additive error at most h/2 plus the error in the measured accuracy differences, without any alphabet-size assumption. This is approximate decision qualification, not exact channel identification. We also show that the inherited binomial moment-matched family has exponentially small complete Shannon-curve discrepancy but only polynomially small decision discrepancy. We give original enumerated stereo specimens, not human listening trials.

## Observation and payoff contract

Let K be a fixed binary-input row-stochastic channel with labelled states + and -. At the fair prior its nonzero output columns give weights w=(K(+)+K(-))/2 and signed posterior contrast t=(K(+)-K(-))/(K(+)+K(-)). Here the two K entries refer to the same output column. The corresponding probability law mu on [-1,1] has mean zero. Conversely any finite such law defines a channel with rows w(1+t), w(1-t). Proportional output columns may be merged. See #686 and #690 for the canonical posterior representation and entropy tomography.

For a finite action menu U of payoff pairs (u_+,u_-) in [0,1]^2, the optimal expected reward is

    V_mu(U) = integral max_(a in U) [ (1+t)u_+(a)/2 + (1-t)u_-(a)/2 ] dmu(t).

The directional bounded decision gap is D(mu,nu)=sup_U(V_mu(U)-V_nu(U)). Let D2 restrict the menu to at most two actions, and D3 to three. The symmetric discrepancy is max(D(mu,nu),D(nu,mu)); zero directional gap is dominance in the corresponding direction. Rewards are bounded absolute utilities; do not confuse them with the normalized risk *ratios* in #638, or with worst-state rather than prior-weighted deficiency. We keep the same prior and payoff matrix when comparing a particular decision. Prior changes used later are an interrogation, not a change of that decision contract.

Define the call or hinge difference

    H(k) = integral (t-k)_+ d(mu-nu)(t).

H is continuous, piecewise linear for finite laws, zero at both endpoints; it is not the difference in threshold crossing probabilities. The full call function determines a law by the jumps of its derivative. H=0 everywhere is posterior equivalence. A single H sign controls directional dominance, but its magnitude has the normalization issue below.

## Three-action theorem and exact compiler

Each decision envelope is convex piecewise affine in t. Remove actions that never maximize over [-1,1] (endpoint-only ties add no hinge). Its active affine lines, in increasing slope order, have switches k_i and strictly positive slope increments g_i. For adjacent active lines, their payoff difference in state + is g_i(1-k_i), and in state - it is -g_i(1+k_i). The plus payoffs therefore increase and the minus payoffs decrease along the active sequence. Since every payoff is between zero and one, telescoping yields exactly the two resource constraints

    sum_i g_i(1-k_i) <= 1,
    sum_i g_i(1+k_i) <= 1.

Conversely any finite nonnegative hinge weights satisfying these constraints define an admissible menu. Start with state payoffs (0,sum_i g_i(1+k_i)); append the successive increments (g_i(1-k_i),-g_i(1+k_i)) in increasing k order. All coordinates stay in [0,1]. The upper envelope is the first affine line plus sum_i g_i(t-k_i)_+, since the resulting lines are its supporting segments. Integrals of the initial affine line cancel for common-mean probability laws. Thus D is precisely the maximum of sum_i g_i H(k_i) subject to the two resource constraints.

Let S be the union of the two support sets, together with -1,0,1. An arbitrary k between adjacent S knots may be replaced by a convex combination of those two knots, preserving its contribution to both resource constraints and to the objective because H is affine there. We have reduced to a finite LP over nonnegative hinge masses on S. A vertex with more than two positive coordinates has a nonzero perturbation annihilating both resource rows, so cannot be extreme. A maximum exists at a vertex of the compact polytope (sum g_i<=1). Therefore at most two hinges and hence at most three actions suffice.

**Exact formulas.** The one-hinge optimum is

    D2 = max(0, max_(k in S) H(k)/(1+|k|)).

For unrestricted k, H(k)/(1+|k|) is linear-fractional on each interval between S knots, hence monotone or constant there. This verifies the formula for two actions without accidentally turning one hinge into two. At a two-positive-coordinate vertex both constraints must be tight, implying sum g=1 and sum gk=0. Thus the two knots must straddle zero, and their masses at k<0<l are l/(l-k), -k/(l-k). Consequently

    D = D3 = max(D2, max_(k<0<l in S) [l H(k)-k H(l)]/(l-k)).

The empty maximum contributes zero. This is a finite O(|S|²) candidate compiler once H is computed, and the winning payoff menu is recovered from the constructive proof. The second term has a financial-style geometric interpretation: the maximum chord height at zero obtained by mixing opposite threshold locations. No finance model is necessary to justify it.

**Two is not enough for magnitude.** Since sum g<=1, D<=max(0,sup H); since 1+|k|<=2, D2>=max(0,sup H)/2. Thus D2<=D<=2D2. In particular D2=0 iff D=0. Binary menus already settle exact dominance, but their worst *normalized gap* need not equal the unrestricted gap. This is a quantitative distinction, not a counterexample to the binary-state Blackwell order.

## Sharpness and the third choice

Choose 0<d<min(b,1-b), 0<b<1. Let mu have equal masses at -b-d,-b+d,b-d,b+d; let nu have equal masses at -b,b. Both laws have mean zero and strictly interior supports. Both yield strictly positive channels. H consists of two triangular peaks of height d/4 centered at -b and b; outside their disjoint widths 2d it is zero. On a peak, the normalized height H(k)/(1+|k|) increases to the peak then decreases, as follows by differentiating the linear-fractional expression. Therefore

    D2 = d/[4(1+b)],    D = D3 = d/4.

The upper bound is reached by equal hinge masses 1/2 at -b,b. The ratio is 1+b and tends to two as b approaches one with e.g. d=(1-b)/2. The absolute gap in that sharp-ratio limit tends to zero; no claim of a large absolute gap at ratio two.

Take b=1/2,d=3/10. The four-output channel A has row counts [1,4,6,9] and [9,6,4,1] divided by 20, and B has rows [1,3] and [3,1] divided by 4. Every entry is positive. At fair prior both have optimal binary state-classification accuracy 3/4. The three-action menu consists of choose -, accept a state-independent reward 3/4, and choose + (payoff pairs (0,1),(3/4,3/4),(1,0)). It attains 33/40 for A and 3/4 for B. The exact unrestricted gap is 3/40, whereas the maximum of ANY bounded two-action comparison at the fair prior is 1/20. The reverse directional gap is zero. A third option is needed to see the largest absolute gap even though the latent state is binary.

This is not an example of three actions needed to detect the sign of dominance. It contrasts #638 (state-support arity and relative baseline risk) rather than contradicting it.

## Operational equivalence: prior-weighted garbling deficiency

For finite K_mu,K_nu let J_mu,J_nu denote their fair-prior joint state-output tables (K/2). Define G=min_T TV(J_mu,J_nu T), where T is any row-stochastic map from nu outputs to mu outputs and TV is half the entrywise L1 norm. Then G=D(mu,nu).

Proof of D<=G: any decision rule on mu can be simulated on nu by first sampling T then applying that decision rule. For each bounded payoff, its expected difference is at most TV of the two joint tables. Optimize and minimize over T.

For G<=D: finite minimax for the compact polytopes of T and payoff tables U in [0,1]^(2 by |Y_mu|) yields

    G = max_U [ sum J_mu U - max_T sum (J_nu T) U ].

The first term uses the output label as the action, which is feasible but not necessarily optimal for mu. The second term is the optimum for nu over the menu of mu-labelled actions: each row of T can choose a maximizing action. Hence each bracket is <=D. This gives equality without assuming a particular LP solver, and explains the native computational comparison to a direct primal garbling LP. G is a prior-weighted TV approximation, not the maximum over state-conditional TV distances.

In addition, every payoff envelope is 1/2-Lipschitz in t (all affine slopes lie in [-1/2,1/2]). Any coupling of posterior laws therefore gives D<=W1(mu,nu)/2, where W1 is the infimum of expected |t-t'| over couplings. TV of posterior laws themselves is not required to be small (disjoint but nearby supports can have TV=1, as in #690).

## The stable receipt: vary the prior for ordinary Bayes accuracy

Instead of estimating entropy derivatives, measure optimal binary state-classification accuracy A_mu(p) under each input prior p. The conditional channel must stay fixed. At p=(1-k)/2,

    A_mu(p) = integral max(p(1+t),(1-p)(1-t)) dmu(t)
            = (1+integral |t-k| dmu(t))/2.

The identity follows from the sum and difference of the two products and the mean-zero condition. Thus A_mu(p)-A_nu(p)=H(k). The established decision-theoretic relation between optimal risk curves and ROC curves is direct ancestry; see Reid and Williamson below. A complete optimal-accuracy curve identifies the posterior law, just as a complete entropy curve does. But finite noisy accuracy observations can certify an operational gap without reconstructing the posterior alphabet.

Let a< b be adjacent measured k values with width Delta=b-a. For a single hinge C_x(k)=(x-k)_+, the chord joining C_x(a),C_x(b) lies above the function, with maximum deficit at k=x if x is inside the interval, equal to (x-a)(b-x)/Delta<=Delta/4; if x is outside, the deficit is zero. Averaging over any law yields the same nonnegative deficit bound. Subtracting two laws leaves an error of either sign, with magnitude <=Delta/4, not Delta/2. Therefore the piecewise linear interpolant H_hat of exact difference receipts has uniform error <=max Delta/4. If each measured difference differs from its truth by at most eta, interpolation adds at most eta. With a prior grid maximum spacing h (including endpoints), Delta=2h, so

    ||H_hat-H||_infinity <= eta+h/2.

The finite compiler applied to H_hat (use its knots plus zero) produces D_hat. Since every admissible hinge measure has total mass <=1,

    |D_hat-D| <= eta+h/2.

This applies equally to the reverse direction and the symmetric maximum. In particular if the grid difference receipts all have magnitude <=eta, the true symmetric bounded decision discrepancy is <=eta+h/2. This latter statement uses eta as a bound on actual discrepancies at grid knots; if noisy observed discrepancies are <=tau and measurement error <=eta, use tau+eta+h/2. When each of the two accuracy measurements has error <=e, their difference has error <=2e. Endpoints p=0,1 are known exactly. For L equally spaced interior priors, h=1/(L+1), so with zero observed discrepancies and per-difference error eta, all bounded decision gaps are at most eta+1/[2(L+1)].

**Sharp interpolation constant.** Use a uniform prior grid with an odd number n of intervals, so the central k interval is [-1/n,1/n]. Let mu place half mass at either endpoint of this interval, nu all mass at zero. Their call functions agree at all grid knots, yet H(0)=1/(2n) and D=1/(2n) by the symmetric classification action. Thus the mesh-only term h/2 cannot universally be improved. Both corresponding channels have positive entries for n>=3, even though nu has one output. The native witness checks ten such grids.

**No finite fixed accuracy grid universally identifies even two-atom channels.** Given any finite grid in [-1,1], choose r>0 smaller than every nonzero absolute grid location and <=1. Take mu with equal masses at ±r/2 and nu with masses 1/3 at -3r/4 and 2/3 at 3r/8. Their means are zero, and their C(0) values are both r/4. All other grid values lie outside both supports, where the common mass and mean fix C. But H(3r/8)=r/16>0. Thus the finite exact identification theorem of #686 for entropy samples does not transfer to accuracy samples. This is not a defect in the stable approximate decision certificate: approximation and exact identification are different goals.

**Engineering constraint.** Accuracy here is the optimal Bayes value for the stipulated confusion matrix, not the accuracy of an arbitrary trained or human decoder. If estimated from finite data, the error tolerance must account for sampling, adaptation, estimation of optimal rules, prior changes, and model mismatch. The theorem supplies no automatic confidence interval. If the full conditional table is available, compute H directly; the receipt sweep is useful only under the restricted observation contract.

## Exponential conditioning of entropy receipts

Reuse, rather than re-claim, the explicit alternating binomial family of #686. For m>=2, N=2m-1, 0<r<1, nodes t_j=r(2j-N)/N for j=0,...,N. The even and odd laws respectively assign weights binomial(N,j)/2^(N-1) to nodes of the corresponding parity. Each has m atoms, mean zero, all moments through degree N-1 equal, reflected supports, and equal fair-prior information. All entries are positive. The first distinct moment is degree N.

The information formula of #686 uses g(v)=(1+v)log(1+v), u=2p-1:

    I_mu(u) = integral [(1+u)g(t)/2+(1-u)g(-t)/2-g(ut)] dmu(t).

Expand g in its convergent power series on [-r,r]; after cancellation of all moments of degree below N, the conservative inherited uniform bound is

    E = sup_|u|<=1 |I_mu(u)-I_nu(u)| <= 4 r^N/[N(N-1)(1-r)].

The factor 4 is conservative: the coefficient magnitude bound 2 and signed-measure norm <=2 suffice. The alternating family now gives an exact threshold gap: for 1<=k<=N-1,

    H(t_k) = (-1)^(k+1) (2r/N) binomial(N-2,k-1)/2^(N-1).

Indeed sum_(j>k)(-1)^j binomial(N,j)(j-k)=(-1)^(k+1)binomial(N-2,k-1), by using j binomial(N,j)=N binomial(N-1,j-1) and the alternating partial-sum identity. Consequently the symmetric bounded decision discrepancy is at least

    L = [2r/(N+r)] binomial(N-2,m-2)/2^(N-1).

This is the normalized single-hinge witness at k=m-1 (contrast -r/N), with direction chosen by its sign. It is an exact lower bound, not a claim that three actions never improve upon it in this family. At fixed r and large N, central binomial asymptotics give L asymptotic to r sqrt(2/pi) N^(-3/2), while E decreases exponentially. Therefore for unrestricted alphabet sizes **no positive Hölder exponent** alpha can bound the symmetric decision gap by C E^alpha for any uniform finite C. At fixed m, taking r to zero instead proves that a uniform exponent greater than 1/(2m-1) is impossible even within that support cap. This is an obstruction, not a matching upper stability theorem.

For completeness the one-dimensional W1 distance of this family is exactly 2r/N. On consecutive node intervals the signed CDF difference equals (-1)^j binomial(N-1,j)/2^(N-1). Multiplying its absolute integral by node spacing and summing gives the formula (or use monotone quantile coupling). The matched law construction was already in #686; the bounded decision normalization, explicit threshold gaps and comparison with stable accuracy certificates are the present extension. Jin et al.'s moment-noise research is related background; no claim that their moment lower bound is new or that our entropy certificate directly follows from it.

At r=1/2 and m=18, all 34 moments match, the complete entropy-curve discrepancy is <=1.956560030704787e-13 nats, yet the bounded decision discrepancy is >=0.0019131515430889918. These are analytic upper/lower guarantees, not floating-point differences between two nearly equal entropy values. The lower gap tends to zero with increasing m; this does not refute qualitative inverse continuity.

## Acoustic score and countercontrols

The positive four-vs-two-output fixture above is rendered by the included witness as 40 exact inventory episodes per instrument. Left channel encodes true state with 300/700 Hz, right channel encodes the posterior contrast with f=500+250t Hz (A: 300,450,550,700; B: 375,625). Each frame is 640 samples at 8 kHz, Hann tapered, stereo PCM16. The truth channel is a laboratory reference, not evidence that the actual receiver is given truth. Read-back matched-template decoding recovers all 160 state/output symbols across both files. The inventories and mathematical values are exact; no physical transmission or listener response is measured.

A prospective interactive instrument could expose a prior control, a bounded state-independent fallback value, and the shape of the posterior alphabet; the third action becomes an audible abstention/alternative, rather than treating every decision as a forced yes/no. This is a design analogy and hypothesis, not evidence that abstention improves human performance. The two files deliberately differ in emitted pitch alphabet; they are not perceptually indistinguishable or an experiment on sound similarity. Pitch labels are arbitrary and known in the model.

Negative sediment: exact sign comparisons from two-action audits remain sufficient in binary state spaces; three actions are only needed for the worst bounded fixed-prior magnitude. The factor-two limit has vanishing absolute discrepancy. The stable grid guarantee requires optimal accuracy, a fixed channel and certified measurement errors. The entropy obstruction is not a matching logarithmic upper bound. Extension to more than two states, correlated repeated decisions, payoff uncertainty and interactive clarification remains open. Direct logging of conditional confusion tables and task-specific utility is the simplest comparator. Conventional probability, convex geometry and statistical decision theory suffice to explain these results. No unique explanatory contribution from cybersemiotics is established.

Fiction: the clerk's two buttons say yes and no. His apprentice adds a third button marked keep the reserve. Both clerks were equally good at naming the world; only then did one of the instruments become worth more.

## Source and verification ledger

- Reid, Mark D.; Williamson, Robert C. (2011), *Information, Divergence and Risk for Binary Experiments*, JMLR 12, 731–817, https://www.jmlr.org/papers/volume12/reid11a/reid11a.pdf . Accessed 26 November 2026. Read Theorems 14–17 and their surrounding Section 5.3 integral-representation discussion, equations (31)–(34), and Section 6.3 Theorem 21 equations (42)–(43), including actual PDF images of printed pp. 756 and 765 (indices 25,34). Direct prior ancestry for primitive cost-sensitive decisions, weighted risk representations and prior-dependent optimal risk curves; not citing the source as proving our three-action normalization or grid constant. Full-paper reading not claimed.
- Torgersen, Erik (1991), *Comparison of Statistical Experiments*, chapter 6, Deficiencies, pp. 222–328, https://doi.org/10.1017/CBO9780511666353.007 . Publisher summary and metadata read, not chapter full text. Established general deficiency comparison motivation. Our finite fair-prior TV identity proved directly above; no claim of priority.
- Jin, Yujia; Musco, Christopher; Sidford, Aaron; Singh, Apoorv Vikram (2023), *Moments, Random Walks, and Limits for Spectrum Approximation*, PMLR 195, 5373–5394, https://proceedings.mlr.press/v195/jin23a.html . Publisher abstract and metadata read, not full paper. Related lower bounds for noisy moment access in Wasserstein distance; no direct claim of an entropy/decision theorem in that paper.
- Repository ancestry: #686 entropy-fingerprint README and #690 spoke-tomography README read, including their conditioning and affine-term limits. #638 smaller-menu GENERAL-CHANNELS.md inspected in full: distinct relative risk envelope against a reveal-or-erase reference, not the bounded absolute gap between arbitrary binary channels. These internal notes are synthetic mathematical context, not independently accepted scientific evidence. No exhaustive novelty audit.

Reconciliation: main SHA 495a98ca12bae467a507031f04931aa4254b1866. AGENTS, RAG, programme, runbook, integrity, validation, protocol overview and project foundations read. 407 live branch entries reviewed; recent open issue search 100 results, explicit recent open PR list 100 results; searches for entropy curvature, decision/deficiency, Wasserstein, stop-loss and related topics. Issue #690 and PR #691 bodies read; #690 comments empty; preceding exact-head workflow 45822921190 success. Target #694 created and reread with empty comments. Only fresh issue-scoped directory changed, no shared manifests. Main repo checkout attempt failed DNS resolution; no full repository validation claimed. No separate agents or human reviewers were involved.

## Qualification and reproduction

Run python witness.py using Python 3.11+ with NumPy and SciPy (native execution: Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0). It writes native-execution.json and two WAV files locally. See [witness.py](witness.py) and [native-execution.json](native-execution.json). The finite compiler and menus are exact Fraction arithmetic; the independent-method direct garbling optimization is SciPy HiGHS floating-point LP. Across 320 directional LPs the maximum discrepancy was 2.858824288409778e-15; 3,840 random menu comparisons, 3,450 grid-receipt checks, five sharp-ratio profiles, ten sharp central-grid profiles, 323 exact moment and 306 exact hinge checks passed. The compiler produced feasible normalized menus attaining each computed exact objective. Two native runs gave identical structured receipts and PCM hashes. Committed witness blob f9e415c97b4a16c22ea9c511c639d0a66ac60447 matched native git hash-object; source SHA-256 7df758844ead3b7f9e1df9f5763bd4bffa10ac31c4f7941f6d0dc3e7cbfc6deb. No requirement to commit generated audio blobs; original specimens regenerate via the script and hashes are retained in the receipt.

Independent mathematical critique and repository exact-head qualification remain outstanding. The issue is intentionally open and delivery is additive; designated mergedown owns promotion, no claim of canonical acceptance.
