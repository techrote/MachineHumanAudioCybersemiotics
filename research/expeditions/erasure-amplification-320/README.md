# The Sample That Survives Its Absence

Refs #320. Synthetic mathematics and audio only; no change to frozen protocol, accepted evidence, or empirical claims. AI-generated research and code, locally checked with separate numerical formulations, not independent human review. Base 495a98ca12bae467a507031f04931aa4254b1866.

## Model and exact certificate

Let p(t) be a real trigonometric polynomial of degree m, and y_j=p(2πj/M). Let E be the known erased index set, J its complement, r=|E| and M-r=2m+1. All observed values obey |y_j|<=1. The target e belongs to E. A polynomial of degree m is uniquely specified by these 2m+1 distinct values: multiplying its Laurent representation by z^m gives an ordinary polynomial of degree at most 2m, and a nonzero polynomial cannot vanish at 2m+1 distinct points.

The real cardinal basis at j is the product over l in J except j of sin(π(t_index-l)/M)/sin(π(j-l)/M). Each product has 2m factors, hence is a periodic trig polynomial of degree m, and is 1 at j and 0 at all other retained nodes. For an erased grid target e the expression simplifies to

    w_j(e)=(-1)^(j-e+1) ∏_{h in E except e} sin(π(j-h)/M)/sin(π(e-h)/M).

Proof: the full product P_i=∏_{l!=i}sin(π(i-l)/M) has magnitude M/2^(M-1) (roots of unity derivative), and sign (-1)^(M-1-i). Express the cardinal numerator as P_e divided by factors for j and other erasures, and denominator as P_j divided by factors for all erasures. The e-j and j-e factors cancel with sign -1. This gives the stated formula. Thus

    max |y_e| = G_e = Σ_{j in J}|w_j(e)|.

Triangle inequality gives the upper bound; assigning y_j=sign(w_j) gives a valid unique interpolant attaining it. Also G_e is the sharp pointwise worst-case error for retained sample noise bounded by one: linear interpolation attains it; the two opposite extremal polynomials can both generate the same zero observation under admissible errors. No amplitude prior on the unobserved signal. This is pointwise, not continuous global peak certification.

## Exact two-erasure law and restoring one probe

For odd M>=5, m=(M-3)/2, and E={0,d}, the preceding formula reduces to

    G_0 = cot(π/(2M))/sin(πd/M) - 1.

Indeed Σ_{j=0}^{M-1}|sin(π(j-d)/M)|=Σ_{k=1}^{M-1}sin(πk/M)=cot(π/(2M)), by the finite geometric series, with the target contribution removed. Adjacent erasures maximize this gain, and separations d=(M±1)/2 minimize it.

If one missing point is restored while the degree stays fixed, rotational symmetry allows the only remaining missing point to be zero. The excluded DFT harmonic k=(M-1)/2 implies Σ y_j exp(2πikj/M)=0. Its real part yields y_0=-Σ_{j>0} y_j cos(2πkj/M). Choosing the retained values to be minus the signs of these cosines satisfies the imaginary part by reflection, hence attains the bound. Since gcd(k,M)=1, these cosines permute the M evenly spaced cosines. Summing the absolute values gives csc(π/(2M)) (sum the positive cosine arc as a geometric series, and use total sum zero). Thus the new gain is exactly csc(π/(2M))-1, the same as the best-separated pair case. For adjacent erasures, the amplification changes from asymptotically 2M²/π² to 2M/π. One extra measurement makes an order-of-growth difference, not just one more data point.

## General clustered-erasure growth

For fixed positive r and admissible parity M-r odd, all factors in the denominator have magnitude >=sin(π/M)>=2/M. Therefore G_e <= M(M/2)^(r-1). For E={0,...,r-1}, e=0, the denominator is <=(π/M)^(r-1)(r-1)!; on a middle-third interval of j, all numerator factors are uniformly bounded below by a positive constant as M grows. There are Θ(M) such j. Hence for fixed r the worst placement has G_e=Θ(M^r). For fixed r with all erased points separated by a circular fraction δ>0 of the grid, denominators are bounded below by sin(πδ)^(r-1) and gain is O(M). No assertion about uniform constants when r grows, or an exact optimal cluster for r>=3. For r=1, the formula gives M-1.

If fewer than 2m+1 distinct values survive, reconstruction is nonunique in general; rank-nullity yields a nonzero invisible signal, which can be scaled without bound at some missing grid point if M>=2m+1. The negative control uses M=9,m=3 and six retained points. Known erasures, exact bandlimit and periodicity are essential. Unknown corruptions, amplitude constraints, nonperiodic streams, physical reconstruction filters and perceptual effects are outside scope.

## Reproduction

Core uses only Python standard library. Verification needs numpy and scipy. From this directory run `python verify.py` (without -O); generates run/results.synthetic.txt and run/erasure-witness.wav. The independent Fourier-basis solve evaluates each weight vector, and LP solves the redundant single-erasure problem without the closed-form gain. Audio renders two degree-three periodic polynomials with M=9, erasures (0,1) and (0,4), each chosen to maximize target zero. Both retained sample sets have unit magnitude; common PCM scale avoids clipping; 200 Hz fundamental, 16 kHz sample rate, two seconds. Different retained sample sets are used; this is not a same-observation experiment, a physical dropout recording or a listening study. The dense sampled peaks differ from the on-grid target gains; no continuous peak claim. Output reproducibility is local, not guaranteed byte-identical across numerical libraries.

## Provenance and exaptation

Established context, no priority claim: Sørevik and Nome, “Trigonometric interpolation on lattice grids”, BIT (2016), §2 (Dirichlet/Lebesgue interpolation amplification), https://doi.org/10.1007/s10543-015-0562-0 (section inspected); J. Selva, “FFT Interpolation from Nonuniform Samples Lying in a Regular Grid”, arXiv:1408.3717, https://arxiv.org/abs/1408.3717 (abstract inspected, missing-sample stability context); “Recovery of Missing Samples with Sparse Approximations”, https://doi.org/10.1155/2013/830723, §2 (periodic finite DFT recovery context, inspected). The proofs above are self-contained specializations; no novelty search beyond these sources and repo overlap screening.

Candidate uses: dropout-aware audio synthesis, sensor placement diagnostics, missing-keyframe uncertainty, adversarial tests for interpolation and error-concealment algorithms. A deliberately fragile oscillator bank could use erased-node geometry as a control of crest factor. These are engineering hypotheses, not participant findings. Neither uniqueness nor an erasure count by itself certifies robust reconstruction.
