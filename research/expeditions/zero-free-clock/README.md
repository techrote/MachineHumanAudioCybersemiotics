# The Clock That Keeps Its Shape Without a Zero

Refs #788, #784/#785 and #780/#781. Exploratory mathematical DSP, 27 November 2026, outside the frozen Track E/G corpus. One ChatGPT agent performed literature reading, derivation, exact synthetic experiments and source replay. No participant, physical transmission, independent human critique or scientific-priority claim.

## Observation contract and an important prior-art correction

The previous mirror-clock expedition treated unknown fixed orthogonal calibration, including scalar sign reversal. A receiver with unknown offset and amplitude gain is a different problem. The literature already contains gain/offset invariant coding: Immink and Weber, *Minimum Pearson Distance Detection for Multilevel Channels with Gain and/or Offset Mismatch*, IEEE TIT 60(10), 5966–5974 (2014), https://doi.org/10.1109/TIT.2014.2342744 . Metadata verified at https://research.tudelft.nl/en/publications/minimum-pearson-distance-detection-for-multilevel-channels-with-g/ and author-site abstract read at https://turing-machines.com/refs.html (entry 70). Blackburn's *Maximum Likelihood Decoding for Multilevel Channels With Gain and Offset Mismatch*, IEEE TIT 62(3), 1144–1149 (2016), https://doi.org/10.1109/TIT.2016.2521658 , explicitly develops an ML rule and a channel-dependent distance; institutional abstract and metadata read at https://pure.royalholloway.ac.uk/en/publications/maximum-likelihood-decoding-for-multilevel-channels-with-gain-and/ . Full manuscript attempts at arXiv:1509.02748 and institutional PDF returned retrieval errors/403. Skachek and Immink's ISIT 2016 work on slowly varying offset is also prior art (metadata only, https://doi.org/10.1109/ISIT.2016.7541288). We do not claim that eliminating offset, gain or drift, Pearson coding or generalized least squares is new. The present question is a particular finite overlapping clock-shift vocabulary, arbitrary signed gain, deterministic noise, mixed sparse faults, and explicit sharp survivor thresholds. Full prior-art comparison remains open.

Let x_j be a known scalar pilot, |x_j|<=A, A>0, on j=0,...,N+K-2. There are K>=3 candidate settled offsets s=0,...,K-1. Clean hypotheses have samples y_t=a x_(t+s)+p(t), t=0,...,N-1, where |a|>=g>0 and p is an arbitrary real polynomial of degree <=d (d=0 means offset). Gain and drift are fixed for a window but independently unknown in alternative explanations; there is no gain upper bound. At most e arbitrary replacements and f flagged erasures, with original indices retained, and dense noise of total L2 norm <=epsilon on surviving uncorrupted samples. Pilot separately observable, no clock-rate error or within-window slip. For r=min(N,2e+f), write n=N-r.

## Exact pair separation after eliminating nuisance drift

For each surviving index subset T of size n, let Q_T be the orthogonal projection onto the complement of evaluations of 1,t,...,t^d on T. Define v_s=Q_T (x_(t+s))_(t in T). For a pair let P=||v_s||^2, R=||v_u||^2, C=|<v_s,v_u>|. Removing the difference of the two nuisance polynomials and choosing the relative sign of the gains gives the objective

P alpha^2 + R beta^2 - 2 C alpha beta, alpha,beta>=g.

Its minimum is attained on at least one boundary alpha=g or beta=g: scale both down to the first boundary, reducing the nonnegative homogeneous quadratic (or retaining zero). If P,R>0, minimize on the two boundaries by clipping the free gain to its floor:
- beta=g, alpha=g max(1,C/P);
- alpha=g, beta=g max(1,C/R).
Take the smaller value. If P or R is zero, the minimum is g^2 times the other squared norm. If both zero, the distance is zero. Thus the minimum exists despite the unbounded nuisance parameters. Define D_r as the smallest such squared distance over all T and s!=u (D_N=0).

The exact mixed-fault distinguishability condition is 4 epsilon^2 < D_r. Proof: two compatible hypotheses must agree up to two noise vectors outside the union of their corrupted/erased indices, leaving at least n indices. Triangle inequality bounds distance there by 2 epsilon. Conversely choose the attaining pair and mask; realize the optimal difference polynomial on the full window. Split the discarded positions into f erasures and two disjoint sets of e corruptions (if r=N, use at most the budgets). On the retained positions take the midpoint; on each corrupt set use the other hypothesis's exact values. Both explanations have dense noise norm sqrt(D_r)/2. At equality universal identification is impossible, including zero distance and zero noise. For a specified erasure mask restrict the search to its surviving indices. This is a deterministic minimax claim, not a statistical ML or Pearson-distance claim.

The exact candidate-list decoder enumerates retained clean subsets of size max(0,N-f_actual-e). For each candidate s, project received and reference on each subset. Fit signed gain by choosing sign of their correlation and clipping its absolute least-squares slope to >=g; if reference projection vanishes use the received projected norm. Retain s iff some subset residual squared <=epsilon^2. The exhaustive implementation is an oracle for small N, not a streaming complexity claim. It returns all compatible candidates rather than breaking ties.

## A sharp binary theorem: fitting gain costs nothing extra, but fitting zero does

Consider full-amplitude binary x_j in {-A,+A} and d=0. On any retained mask the centered inner product satisfies C<=min(P,R). To see this normalize to indicator variables I,J with proportions p,q. Their joint covariance is between -min(pq,(1-p)(1-q)) and min(p(1-q),q(1-p)). Both magnitudes are <=min(p(1-p),q(1-q)); multiply by 4A^2 n. Thus both optimal gains can be set to their floor g. For binary words, allowing unknown independent larger gains does not worsen the worst-case distance beyond fixed magnitude g, unknown polarity and offset.

Choose relative polarity to leave h<=N/2 mismatches. At g the difference has values -2gA,0,+2gA. On a mask with retained counts a,b,c respectively, fitting the offset gives squared distance

4g^2 A^2 [a+c-(a-c)^2/n].

If r>=N/2 an adversary can retain only agreeing positions (for odd N replace N/2 by floor(N/2)); D_r=0. For N divisible by 4 and r<N/2 define m=N/2-r and z=min(r,m). The universal bound over binary pilots is

D_r <= 4g^2 A^2 [m-z^2/(N-r)].

Proof: if h<=r delete all mismatches. Otherwise remove r mismatches preferentially from the smaller of the two sign counts. The retained mismatch count m'=h-r<=m and its imbalance has magnitude >=min(r,m'). The function m' - min(r,m')^2/n is nondecreasing for 0<=m'<=m<=n/2, yielding the bound. With r=0 this reduces to 2Ng^2 A^2.

It is sharp simultaneously for all r whenever every candidate pair has all four joint sign configurations exactly N/4 times. Under either relative polarity the original difference inventory has counts q,2q,q with q=N/4. For retained mismatch count M, M>=2q-r and M<=2q. To minimize SSE for fixed M put as many mismatches as possible in one sign, giving min(M,q) and max(0,M-q). For M<=q, the objective M-M^2/n is nondecreasing as n>2q. For M>=q the objective is M-(2q-M)^2/n, also increasing. Hence choose M=2q-r; the most imbalanced allocation is achievable with all original zero differences retained. Its imbalance is min(r,M), giving the claimed bound. If r>=2q retain zeros only. The construction is sharp within binary pilots, not over all real-valued pilots.

A full order-K de Bruijn cycle gives this exact pair balance at N=2^K and multiples, as established in #784. For K=3,N=12 a direct cyclic binary witness is (+,+,+,-,+,+,-,+,-,-,-,-); it is balanced and its lag-1 and lag-2 correlations are zero. N=8 witness (+,+,+,-,+,-,-,-) likewise works. Both were searched and verified in this run; the main lab enumerates every contingency table up to N=20 in steps of four, independently of the sequence construction.

At N=12,g=A=1, the preceding unknown-polarity-only binary distance was 4 max(0,6-r). Under the additional unknown offset it becomes:

| r | Old squared distance | New exact squared distance |
|---:|---:|---:|
| 0 | 24 | 24 |
| 1 | 20 | 216/11 |
| 2 | 16 | 72/5 |
| 3 | 12 | 8 |
| 4 | 8 | 6 |
| 5 | 4 | 24/7 |
| 6 | 0 | 0 |

The offset loss vanishes on complete balanced observations but appears after adversarial trimming, because the remaining difference need not be centered. This is not a conventional random-erasure estimate.

## A sharp survivor threshold, even against polynomial drift

For any scalar pilot and K>=3, n<=d+2 cannot universally identify the phase under this channel. For n<=d+1 the polynomial nuisance spans the entire retained sample space by interpolation. At n=d+2 its orthogonal complement has dimension one. Every projected phase is either zero or nonzero; two of K>=3 share a class. Two zeros coincide; two nonzeros can be aligned exactly by signed gains with magnitudes >=g (scale both as much as necessary). Thus their clean hypothesis sets intersect on that mask. The impossibility is for arbitrary unknown gain with no upper bound. For K=2 the pigeonhole step need not hold.

The bound is attained by an extremely simple polynomial pilot:

x_j=A(2(j/L)^(d+2)-1), L=N+K-2.

On any >=d+3 distinct retained ticks, after projection the two independent vectors are the projected evaluations of t^(d+2) and t^(d+1). They are independent by polynomial interpolation: a nonzero polynomial of degree <=d+2 cannot vanish at d+3 distinct real points. The projected shifted pilot is proportional to

Q_T t^(d+2) + (d+2)s Q_T t^(d+1).

Distinct s therefore produce distinct nonzero projective lines. Their truncated gain rays have strictly positive minimum separation; by finite masks and phase pairs, D_r>0. This proves the sharp observation-count threshold, over all scalar pilots under the stated K>=3 nuisance model,

N >= 2e+f+d+3.

The result concerns positivity and hence noiseless universal recovery plus existence of a positive bounded-noise margin. It does not claim that polynomial pilots maximize the margin, nor that their margin is useful at a particular ADC resolution. The pilot is finite, nonperiodic, and must be re-anchored or redesigned for repeated use. With d=0 any three effective surviving samples suffice; with linear drift d=1 any four; with quadratic drift d=2 any five.

A degree-(d+1) polynomial fails because its shift difference is exactly degree <=d and can be absorbed in drift. An exponential pilot fails already for d=0: shifting is indistinguishable from a gain change. If all strictly monotone recalibrations are allowed instead of affine ones, all shifts of the increasing polynomial have identical order; a monotone map between their finite values can erase phase entirely. These are exact model-mismatch obstructions. No gain floor means arbitrarily small distances for any bounded pilot. A fixed positive floor and no gain ceiling are crucial to the minimax statements.

## Exact noise boundary for the quadratic pilot with three survivors

Set d=0. Write T=(t1,t2,t3), t1<t2<t3 and s<u. Use the unnormalized quadratic q_s(t)=(t+s)^2. After centering, let v_s, v_u denote q_s,q_u. Their difference is 2(u-s) centered t. Since both q_s and t are increasing for nonnegative t,s, their covariance is strictly positive (sum pair products of differences). Thus <v_s,v_u> > ||v_s||^2. The best gains for the pair are beta=g on the larger phase u and alpha=g <v_s,v_u>/||v_s||^2 on s. For each beta the unconstrained best alpha is feasible and the remaining nonnegative squared residual grows as beta^2. Opposite relative signs cannot improve the distance.

The Gram determinant of centered t and t^2 equals [(t2-t1)(t3-t1)(t3-t2)]^2/3, by the three-row Vandermonde determinant and removal of the constant column. The norm squared of centered q_s is one third the sum of squared pair differences. Therefore, restoring normalization 2A/L^2, the minimum pair squared distance is

(16g^2 A^2/L^4) * (u-s)^2 * [(t2-t1)(t3-t1)(t3-t2)]^2 / sum_(i<j) [ (t_j+s)^2-(t_i+s)^2 ]^2.

To minimize, divide the denominator by the squared Vandermonde. Writing a=t2-t1,b=t3-t2, this quotient is

(t1+t2+2s)^2/[b^2(a+b)^2] +
(t1+t3+2s)^2/[a^2 b^2] +
(t2+t3+2s)^2/[a^2(a+b)^2].

Each term is maximized simultaneously by the latest consecutive three ticks (N-3,N-2,N-1) and s=K-2: each numerator is bounded by its latest-tick counterpart, all denominators have their minimum at a=b=1. The factor (u-s)^2 is minimized at one, attained by u=K-1. Thus at r=N-3 the exact quadratic-pilot distance is

D_(N-3) = 64 g^2 A^2 / { L^4 [ (2L-5)^2 + 4(2L-4)^2 + (2L-3)^2 ] }.

It scales as Theta(L^-6) in squared distance, hence the sharp radius scales as Theta(L^-3) at fixed g,A. The formally optimal survivor threshold is expensive in precision. At N=12,K=3,g=A=1, L=13, D=32/41499133 and radius 0.0004390616263. At N=3,K=3 it is 1/392 and radius about 0.02525. These are exact worst-case total L2 noise bounds for this specific quadratic pilot, not global optimum margins for all pilots.

The lab also exhaustively computes the full finite subset minima at N=8 and 12, K=3, d=0. At N=12, radii at r=0,3,5,6,7,8,9 are respectively 0.0323753, 0.0128525, 0.00599804, 0.00379454, 0.00221013, 0.00112606, 0.000439062. The minimum always occurs on the latest consecutive retained ticks and largest adjacent phase pair in these two profiles; no general proof for more than three survivors is claimed. Binary has much stronger margins when r<6; quadratic alone among these two examples survives r=6..9. Both fail with two survivors, as does any scalar pilot for K>=3 under unrestricted affine gain and offset. Larger margins at three survivors and hybrid design remain open.

## Execution and limits

Run node laboratory.cjs. All decisions use exact BigInt rational arithmetic. Only radius displays use floating-point square roots. The lab independently enumerates 57,844 binary contingency/trim profiles (60 balanced equality cases) and 3,395 centered covariance checks; 13,984 polynomial phase-pair tests with d=0..3, K=3..5 on d+3 retained ticks; 2,676 one-short zero-distance checks; 15 sharp quadratic formula profiles; full finite trim profiles for N=8,12; 72 unique strict-radius candidate-list decodes with signed gains and degree-d drift (d=0..2); 12 explicit mixed-fault ambiguity midpoints; four executable degree/exponential alias controls. The actual receipt is execution.json. One agent, V8 exact checks and committed-source replay identical. This is not independent mathematical peer review. No native full-repository test run or physical channel qualification claimed.

The general oracle is exponential in the fault budget due to mask enumeration; a practical decoder may need robust regression or structured search. The gain floor, known indexed ticks, exact polynomial drift class, no within-window clock slip, known pilot and separate payload visibility are essential. Unbounded arbitrary additive payload can cancel the entire pilot. ADC clipping, finite dynamic range, gain drift, frequency response, clock-rate error, spectral/RMS constraints and quantization remain unqualified. The large mathematical peak-to-precision gap is not a demonstrated perceptual effect. The three-survivor bound is a sharp count, not a proof of optimal sound design.

## Intellectual connection and next experiment

S. S. Stevens, *On the Theory of Scales of Measurement*, Science 103(2684), 677–680 (7 June 1946), https://doi.org/10.1126/science.103.2684.677 . Original article retrieved at https://static1.1.sqspcdn.com/static/f/221758/26986815/1461271683467/Stevens1946ScalesOfMeasurement.pdf ; read pp.677–680 extracted text; visually inspected printed pp.678–679 including Table 1 and interval-scale section. Stevens distinguishes measurement types by allowed transformations and provides examples of affine changes of units and zero. The current signed-gain engineering model is broader than the usual positive interval-scale transformation; polynomial drift is not one of Stevens's ordinary scale transformations. The historical connection is an interpretation, not an endorsement of this DSP design. No claims about human loudness measurement are imported from that article. Compare the more directly relevant gain/offset coding work above, and #288's separate moment-null approach to additive drift leakage. This expedition uses the quotient to identify overlapping phases, not to design a drift-null pulse.

Design hypothesis: a receiver should expose its declared nuisance class, gain floor, observed mask, candidate list and guaranteed margin; do not treat a phase label as a calibrated amplitude measurement. The phase compiler could compare the balanced binary and finite polynomial references under matched peak/range and explicit drift, corruptions and erasures. A later experiment could optimize mixed-fault margins instead of only the count threshold, and investigate how calibration priors (finite upper gain, fixed sign, bounded drift) alter the lower bound. Conventional linear algebra, coding theory and measurement invariance account for these results. No incremental cybersemiotic mechanism or human interpretation benefit demonstrated.

Repository checkpoint: base main 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, README, RAG, programme, runbook, research integrity, validation, experiments, human gates; no nested research AGENTS found. Reconciled 457 branch entries, 30 recent open issues and 30 open PR results, targeted searches for gain, affine pilot, quadratic clock and polynomial drift. Inspected #784 issue/comments and its complete report, successful predecessor exact-head workflow, and #288 issue scope. Fresh #788 issue/comments read. Only this directory is mutable. Draft/HOLD per issue for integrator critique and exact-head checks. No human gate required for synthetic work; no canonical records or other workers' branches changed.

Fiction: The clockmaker's zero is stolen and her ruler stretched. The apprentice can still recognize a curve from three marks. She writes the tiny distance between the possible curves next to the recovered time, so nobody confuses recognition with precision.
