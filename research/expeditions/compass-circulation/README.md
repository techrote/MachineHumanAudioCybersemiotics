# The Compass That Hides Its Circulation

**MHAC expedition #648 · 26 November 2026 · AI-assisted mathematical exploration, outside the frozen empirical/theoretical corpus.**

A stationary acoustic grammar can conceal different transition laws and arbitrarily different statistical time-reversal divergence from *every* same-observable two-time correlation, at *every* lag. This is not just a process-versus-its-reversal ambiguity. A centre-preserving three-time return receipt can repair the divergence estimate without determining the time arrow; four-time reversal-symmetrized words repair the latter up to global reversal in a positive chain.

## Observation contract

Let P be a row-stochastic transition matrix on n labelled states, with known positive stationary distribution pi. All chains here are stationary, first-order and fully observed at the symbolic level. Unless stated otherwise the stationary distribution is uniform. For any real state observable f and nonnegative lag t, the archive stores E[f(X_0)f(X_t)]. In the uniform case this is f^T P^t f/n. By polarization the complete set of these numbers is exactly the symmetric matrix

    H_t = (P^t + (P^t)^T)/2.

Thus this archive knows every unordered labelled two-time joint law, not just one waveform autocorrelation. It does not retain ordered mixed correlations E[f(X_0)g(X_t)] for independent f,g. The latter at lag one recover all of P directly. A global time reversal transposes P in the uniform case, always preserving H_t.

This extends #340 / PR #341 (read full report at c3d99e3a8d4f88a460477f71c4d2c1b10475abdf), which treats contiguous binary block laws, entropy-matched grammars and literal PCM retrograde. Here the obstruction occurs in a stationary *first-order* chain, even for a complete labelled time-symmetric pair audit of unbounded lag. The earlier report's high-order hidden arrow, entropy-spectrum equality and PCM spectrum theorem are not reasserted as new findings.

## The circulant sign-fibre theorem

For an offset law p on Z_n let P_ij=p(j-i). Circulant matrices share the labelled Fourier basis [S1]. Write the eigenvalues as lambda_k=a_k+i b_k, where lambda_(n-k)=conjugate(lambda_k). In that fixed basis H_t has diagonal entries Re(lambda_k^t). In particular H_1 gives a_k, and H_2 gives a_k^2-b_k^2. Hence it determines |b_k|. Conversely independent conjugation of each nonreal conjugate pair leaves every Re(lambda_k^t) unchanged.

**Exact classification within circulant kernels:** the all-lag archive's fibre consists precisely of the independent imaginary-sign assignments to the nonreal conjugate pairs, filtered by nonnegativity of the inverse DFT. H_1 and H_2 suffice for this entire archive. Zero imaginary parts do not provide a choice. The trivial eigenvalue and (for even n) the Nyquist eigenvalue are real.

With r=floor((n-1)/2), choose positive amplitudes c_k with 2 sum c_k<1 and write

    p_s(d) = [1+2 sum_(k=1)^r s_k c_k sin(2 pi k d/n)]/n,
    s_k in {-1,+1}.

The sum of each sine over residues vanishes. Every assignment is strictly positive and normalized; its eigenvalues are purely imaginary off the trivial mode (and possibly the zero Nyquist mode). Fourier uniqueness makes all 2^r laws distinct. All have identical archives; global reversal only pairs opposite sign vectors. Thus the maximal circulant fibre has exactly 2^r labelled laws or 2^(r-1) reversal pairs for r>=1. Relabelling states is not an equivalence in this contract; it could reduce a different unlabelled count. The positivity proviso matters for arbitrary input laws.

## An unbounded KL disparity on eight states

Take the following odd offset vectors (indexed 0 through 7):

    a = [0,1,0,1,0,-1,0,-1]
    b = [0,0,1,0,0,0,-1,0]

For 0<t<1 set p=(1+t*a/sqrt(2))/8 and q=(1+t*b)/8. Both are strictly positive. Direct integer cyclic convolution gives

    a*a = [-4,0,0,0,4,0,0,0] = 2 (b*b).

The corresponding skew matrices therefore have identical squares; each commutes with the constant matrix J whose entries are 1/8, and annihilates J. All symmetrized powers are equal: odd skew powers cancel under transpose, even powers are determined by the square. This is an exact proof, not a floating-point eigensolver result. Equivalently the first and third Fourier sine modes have their relative signs flipped.

Define E(p)=sum_d p(d) ln[p(d)/p(-d)] (nats per transition). This equals the KL divergence rate between forward and reversed stationary paths for these chains: the initial uniform distributions cancel and each transition adds the same expected log ratio. The general first-order relation is established in [S2, Eq.5]. Define phi(u)=u ln[(1+u)/(1-u)]. Then

    E(p) = phi(t/sqrt(2))/2,
    E(q) = phi(t)/4.

Since phi(u)=2 sum_(k>=1) u^(2k)/(2k-1), the quadratic terms coincide, but every higher term is strictly larger for q. Thus E(q)>E(p) for t>0. As t tends to one, E(p) tends to phi(1/sqrt(2))/2 (approximately 0.623225 nats), while E(q) diverges logarithmically. Their ratio diverges too. The discrepancy is not explained by global reversal, which preserves KL rate. At t=0.99 the rates are approximately 0.607190 and 1.310093. At t=0.999999 they are approximately 0.623224 and 3.627161.

This result concerns an informational path divergence, not measured thermodynamic entropy production. [S2] gives physical interpretations under additional assumptions; none are stipulated for the acoustic generator. A fixed strictly positive lower bound on all transition probabilities would bound the divergence; this family approaches a zero reverse-transition probability. It is not a claim that the two chains have the same Shannon entropy rate, or the same finite sampled trajectory autocorrelation.

## Beyond circulant kernels: a symmetrized resolvent certificate

For any real doubly stochastic P write P=S+A where S^T=S and A^T=-A. Then H_1=S and H_2=S^2+A^2. For small formal variable z set B=I-zS and C=zA. Direct multiplication establishes

    ((B-C)^(-1)+(B+C)^(-1))/2
      = (B-C)^(-1) B (B+C)^(-1)
      = (B-C B^(-1) C)^(-1).

The left side is sum_(t>=0) H_t z^t. Hence

    sum H_t z^t = [I-zS-z^2 A(I-zS)^(-1)A]^(-1).

**Exact general criterion:** two candidates S+A and S+A' have equal all-lag archives iff A S^k A = A' S^k A' for all k>=0. By Cayley-Hamilton it is sufficient to test k=0,...,n-1. Equivalently H_t through t=n+1 are sufficient: formal inversion recursively recovers the coefficients through that order. This theorem does not rely on normality.

If the nonzero eigenvalues of -A^2 are distinct except for their required twofold multiplicities, the associated planes E_i are fixed by H_2; the skew action on each plane is determined up to sign. (The kernel of A^2 is the kernel of A, since x^T(-A^2)x=||Ax||^2.) Any candidate skew square root must commute with A^2 and preserve these planes. A real skew map on a two-dimensional plane with prescribed nonzero square has just two orientations.

Construct a graph on the active planes: join i,j if E_i S^k E_j is nonzero for some k=0,...,n-1 (E_i denotes the orthogonal projector). Since the nonzero restrictions of A are invertible on those planes, the cross block of A S^k A changes by the product of the two sign choices. All-lag equivalence therefore requires and suffices that the relative sign flips be constant on each connected component, subject to candidate nonnegativity. This is a classification for simple skew planes, not for repeated singular values, where continuous orientation freedoms may remain.

**Delayed-coupling witness.** In a real orthonormal Walsh basis on N=2^ceil(log2(h+5)) states, take w_0 constant, two skew planes spanned by w_1,w_2 and w_3,w_4, and h intermediate directions w_5,...,w_(h+4) in the skew kernel. Here w_j(i)=(-1)^(popcount(i & j))/sqrt(N). Set

    A = (w_1 w_2^T - w_2 w_1^T)/16
        +/- (w_3 w_4^T - w_4 w_3^T)/8
    S = J + sum over consecutive u,v of path
        (w_u w_v^T + w_v w_u^T)/(16(h+1))
    path = [2,5,6,...,h+4,3].

For h=0 the path is just [2,3]. The row and column sums of every nonconstant term vanish. The total correction to any entry of J is bounded by 1/(2N), so both sign choices are strictly positive. In the Walsh basis, S is a path coupling on these directions, with a separate constant eigenvector. Its first nonzero cross-plane block of S^k occurs at k=h+1: no shorter walk joins the endpoints. The corresponding block of A S^k A is nonzero and flips sign. By the resolvent identity, H_t first differs at t=h+3; all earlier H_t agree. This provides arbitrarily delayed pair-archive disambiguation with increasing state dimension. It falsifies general two-lag sufficiency outside the circulant class.

## Repair without naming the arrow

Now permit any known positive stationary pi, not necessarily uniform. Define stationary flow F_ij=pi_i P_ij, symmetric flow M=(F+F^T)/2 and skew flow A=(F-F^T)/2 (the symbol A in this section refers to flow, not the previous transition matrix). The pair archive at lag one determines the sum s=F_ij+F_ji. A three-time return i,j,i is itself invariant under path reversal. Its probability is pi_i P_ij P_ji=F_ij F_ji/pi_j. Thus the return receipt gives the product r=F_ij F_ji. The two unordered flow values are exactly

    (s +/- sqrt(s^2-4r))/2.

Consequently the forward/reverse KL rate of any stationary first-order chain is exactly recoverable from one-step unordered pair sums and three-time return receipts, with no global orientation labels. For each unordered pair the contribution is

    delta ln[(s+delta)/(s-delta)], delta=sqrt(s^2-4r).

A zero pair contributes zero; a positive one-way pair contributes infinity. This follows by grouping the two ordered terms in sum F_ij ln(F_ij/F_ji). The proof also works for zeros with these conventions. For finite data, discriminants can become negative by estimation error; these formulas are population identities, not a calibrated estimator or a guarantee of sample efficiency.

**Full three-time symmetrized classification.** The half-sum of probabilities of words i,j,k and k,j,i equals

    (M_ij M_jk + A_ij A_jk)/pi_j.

All skew magnitudes are known from returns. Every pair of adjacent nonzero skew edges has a determined relative orientation (fix a reference orientation per edge and account for its traversal sign). Therefore the nonzero current graph's connected components each have at most one free global sign. Conversely flipping all skew edges in any component preserves every such product, all pair sums, nonnegativity and stationarity (the divergence of each component's skew flow is zero). Thus symmetrized words of lengths up to three identify the chain up to exactly independent reversals of its nonzero-current components, including isolated zero-current vertices which supply no choices.

**Four-time repair for strictly positive P.** Choose nonzero current edges i->j and k->l from two different components. The cross edge j,k has A_jk=0 and M_jk>0. The symmetrized four-time word is

    M_jk (M_ij M_kl + A_ij A_kl)/(pi_j pi_k).

This fixes their relative orientation. Thus all symmetrized words through length four determine the entire strictly positive first-order stationary chain up to *one global reversal*. The bound is sharp for this observation class: two disjoint directed triangle currents on a common positive symmetric background can have one component flipped, leaving all one-, two- and three-time reversal-symmetrized words unchanged but not all four-time words. The exact six-state witness in the laboratory uses numerator 12 for all entries, skew additions +/-2 and +/-3 on the respective cycles, and denominator 72. It yields zero differences at lengths 2 and 3, and 72 differing indexed words of length 4. These are indexed words rather than distinct unordered reversal orbits. With missing cross edges, longer words may be needed; no four-time theorem is claimed for arbitrary sparse or hidden-state chains.

This result concerns consecutive words with the middle state retained, not unordered bags of three or four symbols. A receiver needing only KL rate need not recover all signs. A receiver needing direction must add an ordered receipt (or an external time-reference convention). No set of purely reversal-symmetric observations can distinguish a law from its global time reversal.

## Evidence, computational scope and negative sediment

Run 'node laboratory.cjs' from this directory and compare the JSON to execution.json. The committed source was executed as the same function in the tool's JavaScript runtime. The census covered 764 positive circulant sign assignments for n=3..17, 6,112 floating-point lag checks (maximum error 4.44e-16), the exact eight-state integer convolution identity and 160 numerical lag comparisons, eight exact BigInt delayed-coupling profiles with first differing lags 3..10, 1,548 indexed words across the three/four-word counterexample census, and 4,935 return / reversal checks. All assertions passed. The positivity, lag and word counts are synthetic test instances, not participant observations. The mathematical proofs establish unbounded statements; finite computation is not their substitute.

A separate standard-library Python witness executed locally twice. It tested the delayed-coupling construction with integer outer products, 1,362 exact rational unordered flow reconstructions across 100 nonuniform stationary positive models, and literal forward/reverse block KL for the two eight-state laws at lengths 2,3,4. It generated two 10.24-second seeded synthetic Markov scores (128 symbols each, 8 kHz PCM16 mono, carriers 250+50k Hz, 80 ms tapered pulses) and decoded all 256 symbols by nearest template. Both executions produced byte-identical JSON and audio. These local specimens are illustrative samples: their observed histograms and sample autocorrelations are NOT identical; the theorem is at population level. They are not human audition results. Local Python source and receipt are in the delivered native package; the committed JS implementation is independently runnable. Same-agent cross-check only.

Negative cases: if ordered mixed-observable correlations are retained, the whole transition law is already identified at lag one. If the chain is symmetric then A=0, and H_2 fixes this uniquely in the uniform first-order model. A nonzero time arrow can thus be detected from the full pair archive (A^2 nonzero), even though its *magnitude in KL* and its orientation are not generally identified. A single scalar waveform autocorrelation is weaker still. State lumping can destroy Markovity; unknown stationarity, nonstationary acquisition, hidden states, history-dependent transitions and finite sampling invalidate direct transfer of these proofs. Repeated skew singular values are outside the simple-plane classification. No assertion is made that an arbitrary observed pair archive is generated by some valid stochastic chain.

## Exaptation and counterposition

**Design hypothesis:** a telemetry receipt should distinguish unordered co-occurrence at a lag, a return event with its centre identity retained, a directed transition, and a full ordered context. The return receipt might be an economical diagnostic when direction is irrelevant but statistical reversibility is important. Its usefulness depends on sample requirements and uncertainty; no such advantage has been measured. A direct ordered event log is the simpler baseline whenever available, and is cheaper than an elaborate all-lag audit.

**Artistic interpretation:** a Compass Organ presents eight equal-frequency states on a circle. One performer changes the relative orientations of circulation modes while the observer's entire same-observable autocorrelation display stays fixed; another controls closeness to the one-way boundary; a third introduces return events or symmetrized three/four-time words. The two native scores are finite realizations of its eight-state demonstration, not a live instrument. The proposed compositional variable is the assignment of direction within a fixed second-order population signature. No perceptual equivalence, intrinsic semantics, thermodynamic dissipation or additional explanatory contribution of cybersemiotics has been established.

## Sources, access and reconciliation

- S1: Robert M. Gray, *Toeplitz and Circulant Matrices: A Review*, Foundations and Trends in Communications and Information Theory 2(3), 155–239 (2006), [author-hosted published PDF](https://ee.stanford.edu/~gray/CIT006-journal.pdf). Read §3.1–3.2, printed pp.186–188, equations 3.5–3.13 and Theorem 7 (published numbering); inspected PDF page images 32–33. Established DFT diagonalization and common Fourier basis, not the present stochastic inverse/repair claims.
- S2: Édgar Roldán and Juan M. R. Parrondo, *Estimating Dissipation from Single Stationary Trajectories*, Physical Review Letters 105, 150607 (2010), [DOI](https://doi.org/10.1103/PhysRevLett.105.150607), [author-hosted PDF](https://www.edgarroldan.com/wp-content/uploads/2016/01/roldan2010estimating.pdf). Read introduction, equations 1–5 and surrounding Markov and partial-observation discussion, printed pp.150607-1–2; inspected PDF image index 1. Established path KL and one-step Markov rate, physical qualifications. Not a claim that the present results are novel to the literature.
- S3: C. S. Daw, C. E. A. Finney, M. B. Kennel, *Symbolic approach for measuring temporal “irreversibility”*, Physical Review E 62, 1912 (2000), [publisher abstract](https://doi.org/10.1103/PhysRevE.62.1912). Abstract only: symbolic time-asymmetry methods and model discrimination. No full-text reading or extraction claimed.

All readings and derivations by one ChatGPT/GPT-6.2 agent, 26 November 2026. No restricted source copies, external reviewer, empirical extraction, protocol amendment or scientific priority asserted. The proofs are independently derived here, not independently peer-reviewed.

Reconciliation: default main 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, README, RAG, programme, runbook, integrity and validation; inspected root directory and attempted nested agent instructions (not found); 384 branch entries, 100 recent open issue results and 100 recent open PR results; searched zero-error/side information first (substantial overlap), then entropy production, time reversal, autocorrelation, circulant, probability current and irreversibility. Read #340 issue/comments and the full PR #341 report. Previous #645 exact-head 52e9dd7c195dda2104613e64d0367c20f95c2f75 workflow 45744971445 completed successfully; not scientific review. New #648 and its comments were read back (none). Native full checkout attempt failed with GitHub DNS resolution; repository-wide commands not executed locally. No canonical manifest, accepted programme path or active other branch modified. This directory belongs solely to #648. Draft/HOLD pending exact-head structural checks and independent mathematical critique; no parallel-work merge.

**Fiction:** The clerk records how often each needle returns to every other mark, at every interval. Two compasses pass every inspection, although one has nearly forgotten how to travel backwards. The apprentice asks for a journey that comes home through a named intermediate station. The register can finally measure the cost of reversing the journey without knowing which way it was made.
