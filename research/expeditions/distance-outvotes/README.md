# The Chord That Outvotes Its Own Distance

Refs #759, #754, #750 · 27 November 2026 · Exploratory mathematical DSP. One ChatGPT agent performed source inspection, proofs, computational discovery and verification. No independent peer review, human listening, physical transmission or priority claim.

## A changed observation contract

The two-period result in #754 proved that graph distance and unweighted least absolute deviations (LAD) share a sharp universal correction threshold. Its proof uses a layer-cake decomposition of differences of two vertex potentials. Does this remain true with three periodic voices?

Assume coherent indexed raw observations after demodulation, known pairwise coprime periods p_i >= 2, arbitrary real private waveforms, an unknown constant, flagged erasures and arbitrarily corrupted values. We use the equivalent anchored gauge

    y(t)=b + sum_i f_i(t mod p_i),   f_i(0)=0.

Subtracting each component mean and adding the means to b recovers the zero-mean gauge. CRT ensures uniqueness of the decomposition for the complete signal. For a schedule T (distinct integer times, not necessarily consecutive), form an integer design matrix A with a constant column and one indicator column for each nonzero residue of each period. Its column count D=1+sum_i(p_i-1). Full column rank on T means identifiable clean signals; the minimum Hamming distance of distinct full signals restricted to T is

    d(T)=min_{h != 0} |supp(Ah)|.

Universal exact recovery against e arbitrary errors and f flagged erasures holds iff d(T)>=2e+f+1. Necessity comes from splitting a minimum-support codeword's discrepancies after erasures between two possible worlds; sufficiency is the Hamming triangle inequality. This is an information bound, not a promise of computational efficiency.

Full column rank after every deletion of d-1 rows certifies distance at least d. Necessary observation counts for distance d include N>=D+d-1 (puncture d-1 rows and retain rank) and N>=d max(p_i) (each residue of every period must be observed at least d times, using a one-residue perturbation). Neither bound is asserted sufficient for arbitrary schedules.

For an actual corruption support F, unit-weight LAD has the stronger necessary-and-sufficient uniform recovery condition

    ||(Ah)_F||_1 < ||(Ah)_{F^c}||_1 for every h != 0.

Triangle inequality proves sufficiency; choosing the received data to be the alternative Ah on F and truth zero elsewhere proves necessity. This is the classical sparse-error range/null-space condition, not a new general theorem. #754's coarea proof makes it automatic for a two-part incidence design at the sharp distance threshold. A three-part additive row is not a difference of two potentials; no such implication has been established by that proof.

## Exact one-error obstruction: 22 observations

For periods (3,5,7), D=13, P=105. Use this nonconsecutive schedule:

    T = [1,2,9,11,22,25,26,27,33,47,52,56,63,64,70,72,76,80,83,94,95,98].

In the column ordering constant, then nonzero residues in increasing period/residue order, consider

    h = [1,-1,0,-1,-1,-1,-1,1,0,1,0,0,0].

The output v=Ah vanishes on every sampled position except:

| Time | v |
|---:|---:|
| 76 | -1 |
| 80 | +2 |
| 95 | +1 |

The executable certificate enumerates all 231 ways of deleting two rows and verifies rank 13 over the prime field F_1009. A nonzero integer minor modulo 1009 is necessarily nonzero over the reals. Thus every nonzero codeword has at least three nonzero coordinates; the displayed witness attains three. This establishes exact distance three without floating-point rank thresholds. The counting lower bound for any distance-three schedule is 21, so this fixture is within one observation of that bound, not proved sample-optimal.

Take the true signal to be zero and corrupt only t=80 to +2. The truth has LAD cost 2. The false signal v also has cost 2, because its two surviving discrepancies have absolute values 1 and 1. Universal unique LAD recovery fails, even though the signal is uniquely identifiable from one arbitrary corruption. Native SciPy LP finds optimum 2, confirming an actual tie rather than just a pair of nonoptimal points. The modular rank proof and the candidate comparison are exact; LP confirms the objective numerically.

This is a schedule-level counterexample; it is not a claim that consecutive three-period observations fail at the same distance, or that every three-period design fails.

## Scalable strict failure with equal weights

The tie can be made strict without assigning any artificial confidence weights. For integer k>=1, concatenate k copies of the same 105-tick residue schedule, shifted by 105*j for j=0,...,k-1, but retain t=76 only in the first copy. All observation times are distinct. The resulting schedule has N=21k+1.

Repeating all rows k times would multiply the exact distance by k. Deleting k-1 observations lowers distance by at most k-1, hence the new distance is at least 3k-(k-1)=2k+1. The same witness has k values +2, k values +1 and one value -1, attaining distance exactly 2k+1.

Corrupt the true zero signal to +2 at its k high-valued witness locations. The true LAD cost is 2k. The alternative costs k+1. For every k>=2, the false signal costs strictly less, while distance proves that every k-error input is uniquely identifiable. The cost ratio of alternative to truth tends to 1/2, not 1. Scaling the amplitude of this witness by any positive number gives the same counterexample with arbitrarily large corruption magnitudes.

| Copies k | Observations | Distance | Correctable errors | True cost | Alternative cost |
|---:|---:|---:|---:|---:|---:|
| 1 | 22 | 3 | 1 | 2 | 2 |
| 2 | 43 | 5 | 2 | 4 | 3 |
| 3 | 64 | 7 | 3 | 6 | 4 |
| 10 | 211 | 21 | 10 | 20 | 11 |
| 20 | 421 | 41 | 20 | 40 | 21 |

These counts are scheduled sample observations, not the elapsed span: e.g. k=2 uses times 1 through 203 inclusive, with gaps. The witness family is verified exactly for k=1..20; its proof holds for all positive integers k. No optimality of the arbitrary schedule length, consecutive prefix or LAD objective for k>3 is claimed.

Native LP actually minimizes the full residual objective for k=1,2,3 and returns 2,3,4, respectively. It does not identify truth for k>=2.

## Repair without trusting LAD: an exact syndrome decoder

Let F be any full-row-rank left annihilator of A, with ker(F)=range(A). Then Fz=Fe for error vector e. If distance exceeds 2k, no two distinct k-sparse vectors have the same syndrome: their difference would be a nonzero codeword of support at most 2k. Every set of at most 2k columns of F is linearly independent by the same argument. Enumerate candidate supports of size k (smaller supports are contained in them), solve the restricted linear system, reject inconsistent candidates and remove the reconstructed error. This is exact, but combinatorial; do not use it as a blanket real-time method.

The native lab independently constructs F using SymPy rational nullspace and tests all size-k supports for k=1,2,3 using exact rational normal equations and equality. Since the actual witnesses have exactly k corruptions, exactly one support matches for each. Counts: 22, 903, 41664, respectively; total 42589. The recovered errors are precisely the injected +2 values. This is a working finite witness of the difference between identifiability and convex decodability, not a claim that exhaustive search is efficient for arbitrary large fault budgets. The general sparse-error syndrome method is established prior art.

## A constructive positive theorem: full Cartesian observation

For any number m of pairwise coprime private periods, let P=product(p_i) and M=max(p_i). One complete period is a full Cartesian grid under CRT. The exact distance is

    d_full=P/M.

Proof: if a nonzero additive signal has any nonconstant component i, choose two residues whose component values differ. For each fixed tuple of other coordinates, the two resulting output values differ; at least one is nonzero. The pairs are disjoint and there are P/p_i >= P/M of them. If all components are constant, a nonzero signal is constant and has P nonzeros. The indicator of a single residue of a largest-period component attains P/M. Thus the exact fault contract is 2e+f < P/M.

A direct median decoder attains this optimum without a linear program or support enumeration. For component i and each residue r !=0, form all P/p_i differences between cells with residue r and cells with residue 0, holding every other coordinate fixed. Every clean pair gives the same private contrast f_i(r)-f_i(0). For any fixed r, the pairs are disjoint as sets of observations. Each erasure spoils at most one pair and each corrupted sample spoils at most one pair. After discarding flagged pairs, a strict majority is good because P/p_i-f>2e. Take the median of these differences. Once all anchored components are recovered, take the median of surviving observations minus their fitted component sums to recover b. The same majority argument applies. This algorithm works for arbitrary real component values and corruption sizes. Pair sets for different target contrasts can reuse observations; only within each median vote must they be disjoint.

Bounded good-sample error epsilon gives contrast error <=2 epsilon, as every good pair has two errors. The anchored intercept error is <=(2m+1)epsilon, and centering the private shapes gives a safe <=4 epsilon per-residue error bound. The algorithm uses one complete grid, which grows multiplicatively with the number of components. It is not a solution to the small-prefix deadline problem. It gives a practical correctness baseline, and suggests smaller schedules with a separately certified number of disjoint paired contrasts.

| Periods | Complete observations | Exact distance |
|---|---:|---:|
| 2,3,5 | 30 | 6 |
| 3,5,7 | 105 | 15 |
| 3,5,11 | 165 | 15 |
| 2,3,5,7 | 210 | 30 |

For (3,5,7), this allows any combination with 2e+f<=14; for example seven arbitrary errors. No assertion that LAD also attains this threshold on the complete grid.

## Negative control: connected hypergraph does not mean identifiable

On the (2,3,5) grid observe only tuples satisfying x=1_{y=0}, with all third-coordinate values included. This is 15 distinct times. Every residue is represented and the ordinary 2-section graph (connect vertices that share an observed tuple) is connected: the third coordinate connects the two restrictions.

Nevertheless the nonzero full-signal perturbation x-1_{y=0} vanishes on every observation. The design has D=8, and the exact relation supplies an upper rank bound 7; modular rank 7 supplies the matching lower bound. This is a failure even with no corrupted samples. A connected hypergraph is not a substitute for an identifiability certificate. This fixture uses a period of two as a private component after demodulation; it does not simultaneously claim a separate alternating nuisance term.

The conceptual distinction is between counting independent relationships and measuring their amplitude geometry. At distance 2k+1, the number of false samples is provably insufficient to change the true signal under Hamming decoding. Yet an amplitude-weighted residual sum can prefer a false explanation. No choice of a prettier graph representation eliminates this counterexample.

## Provenance, computation and boundaries

- E. Candès and T. Tao, *Decoding by Linear Programming*, IEEE Transactions on Information Theory 51(12), 4203–4215 (2005). Public Caltech record https://authors.library.caltech.edu/records/pxr5b-3zf41 and preprint https://arxiv.org/abs/math/0502327 (v1 PDF, https://arxiv.org/pdf/math/0502327). Inspected abstract, §1.1–1.3, equations (1.2)–(1.6), and original printed page 4 image. Established source for real-valued sparse error correction, annihilator and convex-versus-combinatorial distinction. The present periodic fixture and family are not attributed to that paper.
- X. Chen, H. Wang and R. Wang, *A null space analysis of the l1-synthesis method in dictionary-based compressed sensing*, Applied and Computational Harmonic Analysis 37(3), 492–515 (2014), https://doi.org/10.1016/j.acha.2014.01.006. Publisher Introduction, equation (2), read for standard null-space criterion; not full article. Its dictionary setting is different from our additive periodic design.
- R stats documentation, *Median Polish (Robust Two-way Decomposition) of a Matrix*, https://www.stat.ethz.ch/R-manual/R-patched/RHOME/library/stats/html/medpolish.html, Description and Details read. Attributes iterative median polish to Tukey (1977, book not inspected). The full-grid contrast decoder here is noniterative and uses disjoint paired votes; it is not an implementation of median polish. This is conceptual ancestry, not evidence of a new statistical method's priority.
- #754 complete report inspected, predecessor issue and comments checked; exact head 8834c0c5713a824f7c2e3d9488812bc17d30e593 workflow 45930920173 completed success. #750 supplies local reconstruction context.

Replay: node laboratory.cjs (dependency-free). Exact integer computations in V8, committed source retrieved and replayed byte-identically against execution.json: 231 finite-field deletion ranks, 20 scalable witness profiles, 408 exact complete-grid decodes, 408 bounded-noise checks, four full-grid sharp witnesses and connected-rank negative control. All integer operations stay within exact JS Number range. Native native.py (NumPy 2.3.5, SciPy 1.17.0, SymPy 1.14.0) independently constructs exact rational syndromes and solves the numerical LAD problem. Native source blob 61496c23c92f2c84d64c5fb8d1fb908fe4a9e181 and native-execution.json blob f7596566d415b4d9a286bfdd9514b41501c1914a match locally executed files. Native LP tolerance is not part of the mathematical distance certificate. No failed final assertions. Same-agent different formulations, not independent review.

Reconciliation: live main 495a98ca12bae467a507031f04931aa4254b1866. AGENTS, README, RAG, programme, runbook, integrity and validation inspected; nested research/AGENTS and research/expeditions/AGENTS absent. 442 branch entries paginated, 30 recent issues and 30 recent PR results inspected; targeted hypergraph, null space and cospark searches. #759 scoped fresh branch; native git ls-remote failed DNS, so no full local repository validation claimed. Additive files only, Draft/HOLD for critique and integrator. No canonical state modified.

Design hypothesis: an Observatory inspector could distinguish Hamming-distance certification, LAD range balance, paired-contrast redundancy and actual decoder behavior rather than displaying a single confidence meter. A playable synthetic fault instrument could let a performer increase only the magnitudes on one side of an amplitude-weighted vote. Test human interpretation separately. Conventional coding theory, exact linear algebra and robust statistics explain all demonstrated results; no incremental explanatory contribution from cybersemiotics established.

Fiction: three clerks agree that only two witnesses have lied. The arithmetic clerk still chooses the false account, because the lies have larger numbers. The apprentice asks how many statements would need to change, not how large those changes would be.
