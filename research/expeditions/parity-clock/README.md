# The Clock That Cannot Divide Its Extremes

Refs #805, #801/#802, #796/#797. 27 November 2026. Additive exploratory mathematics and synthetic software outside the frozen empirical/theoretical review. One ChatGPT agent; no independent mathematical review, physical channel tests, human observations, or scientific priority claim.

## Contract

A ternary reference x yields K indexed phase words x_s(t)=x(t+s), for s=0,...,K-1 and t=0,...,N-1. A cyclic pilot of length N uses indices modulo N. Each competing phase explanation may fit its own fixed strictly monotone calibration, increasing or decreasing. The q=3 contingency matrix W counts paired input symbols. Its maximum mass L(W) over strictly increasing or strictly decreasing chains is the maximum number of agreements between calibrated words (repeated observations in a cell count with multiplicity). Distinct explanations can agree on exactly such chains: equalities and relative ordering must agree up to reversal, and matching output values can be extended to strictly monotone maps. Let L be the maximum L(W) over phase pairs. The exact Hamming discrimination distance is d=N-L; at most e arbitrary substitutions and f flagged erasures are universally correctable iff 2e+f<d. This is the predecessor's contract, not a noise or listening model.

#801 established optimal relative ambiguity 4/15 for K=5 and K=6 in the large-N limit, a 240-tick exact five-phase cycle, and nonattainment of 4N/15 for finite overlapping six-phase pilots. The question here: how short can an exact five-phase reference be, and can the strict six-phase lower bound actually be attained at useful finite lengths?

## A new divisibility theorem, including nonoverlapping codebooks

**Theorem.** For any five ternary phase words (even independently designed, without overlap), exact attainment of L=4N/15 requires 30 to divide N. Conversely every positive multiple of 30 admits a cyclic overlapping pilot attaining L=4N/15. Thus the shortest positive window attaining the exact unrounded optimum is 30 ticks. This does NOT state that every shorter window has an inferior integer-rounded optimum or that shorter windows cannot decode five phases.

**Proof of necessity.** Since L is an integer, equality implies N=15h and L=4h for a positive integer h. For an unordered pair of words, denote by C the sum of the four corner cells of W, by S the sum of the four side cells, and by c the center cell. Both diagonals are chains, so C+2c<=2L. The four side cells split into two chains, hence S<=2L. Put A=C/2+c and B=S/2; both are at most L for every pair.

At any observation let j count the middle symbols among the five words. Averaging A and B over the ten unordered pairs gives per-tick contributions
    a_j = [(5-j)(4-j)/2 + j(j-1)]/20,
    b_j = j(5-j)/20.
Indeed the both-extreme pairs contribute half each to A, both-middle pairs contribute one each to A, and exactly-one-middle pairs contribute half each to B. Direct calculation for j=0,...,5 gives 2a_j+b_j >= 4/5, with equality only at j=1,2. Therefore the pair-average of 2A+B is at least 4N/5=3L. But every pair has 2A+B<=3L. Equality forces A=B=L in EVERY pair, and j in {1,2} at every tick. This also rederives the predecessor's five-phase lower bound without invoking its construction.

Now C+S+c=N, C+2c=8h and S=8h, so c=h and C=6h in every pair. Both full diagonal sums are 4h, implying W00+W22=W02+W20=3h. If m_s counts the middle symbols in word s, then m_s+m_u=S+2c=10h for every pair. With at least three words this forces all m_s=5h.

The two row-middle side cells W10,W12 sum to 4h; the two column-middle side cells W01,W21 sum to 4h. Any one row-middle side cell and any one column-middle side cell form a monotone two-cell chain (one of the two permitted orientations). Thus max(W10,W12)+max(W01,W21)<=4h; both maxima are at least 2h. All four side cells are exactly 2h.

Let n_s count zeros in word s. Row-zero and column-zero margins now give n_s-n_u=W02-W20. Since W02+W20=3h, their difference has parity h. If h were odd, all five zero-counts would be pairwise opposite in parity. Even three integers cannot have that property. Thus h is even, proving 30|N. No cyclic assumption entered the argument. The contradiction is integer, not numerical or computational.

For cyclic words the margins agree, so W02=W20=3h/2 is an even more direct obstruction. The equality conditions also force the middle-indicator periodic autocorrelation at each candidate lag to equal -h: with m=5h, overlap c=h, binary sign sequence 2z-1 has correlation N-4(m-c)=15h-16h=-h. This is a necessary partial-lag condition, not a sufficient characterization of the full ternary matrices.

## A shortest exact cyclic witness

The following actual cycle was discovered through seeded local stochastic search in C++ (std::mt19937 seed 20261127; cost penalized side and center count deviations, diagonal sums and excess maximum chain mass; swaps or single-symbol mutations with an exponential cooling schedule). The search is heuristic, not an optimality proof. The proof above plus a solver-free certificate establishes optimality independently of the discovery process.

    201200011202122121001010221102

It contains ten of each symbol. For every lag 1,2,3,4 the actual full contingency matrix is

    3 4 3
    4 2 4
    3 4 3

Each of the ten phase pairs consequently has L=8 and d=22. All five-symbol windows have one or two middle symbols, respectively 10 and 20 windows. Each middle-sign autocorrelation is -2 at the four specified lags. There is no assertion of a constant autocorrelation at all 29 nonzero lags. The cycle qualifies all five candidate phases at any effective fault budget <=21 (e.g. ten arbitrary replacements and one erasure).

Repeating this cycle R times multiplies every contingency count by R, giving N=30R, L=8R, d=22R. This supplies sufficiency for every length divisible by 30. The former 240-tick construction was optimal in relative distance but eight times longer than needed to attain that optimum. The new construction trades away the former complete restricted five-tuple inventory, which is stronger than the pairwise condition actually required. The two cycles must not be described as equivalent for tasks needing higher-order window statistics.

The 30-tick reference is not always the correct choice for a given absolute fault budget. Shorter pilots may suffice with less distance, and longer references retain more absolute correction capacity. It also cannot distinguish offsets separated by its full cycle.

## Six phases: sharp finite witnesses

For K=6 the predecessor's strict lower bound L>=floor(4N/15)+1 follows from the same occupancy argument. In detail, if equality with the unrounded 4N/15 were possible, the average of C/2+c must equal L and every six-symbol window must contain exactly two middle symbols: the relevant numerator [(6-j)(5-j)/2+j(j-1)] is uniquely minimized at j=2 with value 8. The consecutive sliding middle indicators would then be six-periodic with two ones. Among the five nonzero shifts of that periodic middle mask, at most two can intersect its support. Choose a disjoint shift d. Among the six ordered phase pairs (s,s+d mod 6), average exactly-one-middle count is 2N/3 because each phase participates twice and total middle occupancy is 2N. At least one pair has side mass >=2N/3, so its chain mass is at least N/3, contradiction. Combined with the integer lower bound this proves strict nonattainment.

This does not prevent attaining the *next* integer. A seeded C++ annealing search minimizing excess chain mass found the following actual cycles. The exact verifier independently checks every phase pair against the lower bound; the search is not the mathematical certificate.

| N | Certified L | d=N-L | Max e (f=0) |
|---:|---:|---:|---:|
| 15 | 5 | 10 | 4 |
| 30 | 9 | 21 | 10 |
| 45 | 13 | 32 | 15 |
| 60 | 17 | 43 | 21 |
| 90 | 25 | 65 | 32 |

All five are globally optimal at their exact lengths even against noncyclic overlapping references, because the strict lower bound holds for all such references. Their explicit cycles and every pair matrix are retained in execution.json. The 90-tick cycle reaches 25/90=27.777...% ambiguity, only 1/90 above the 4/15 asymptote, with no exponential inventory compiler. The six-phase N=60 middle indicator has zero sign autocorrelation at lags 1..5, but that alone does not certify the ordinal distance; the full three-level joint counts remain necessary. Repeating any of these cycles multiplies its excess over the asymptote, so repetition does not establish sharpness at arbitrary larger multiples. General finite attainability beyond the listed lengths remains open.

## Verification, source connection and limits

Run node laboratory.cjs from this directory. It enumerates all 511 nonempty cell subsets, retaining 29 legal chains. It checks all 85 actual phase-pair matrices with both explicit chain enumeration and a separate weighted-chain DP. The 30-tick five-phase matrix, middle occupancy and all five six-phase distances are asserted exactly. The laboratory also searches all 32768 possible middle masks at N=15 cyclic, K=5. Exactly 303 satisfy the necessary equality occupancy constraints (five ones; ten windows with two middle symbols), giving 310272 assignments of the extreme symbols. None has L<=4; minimum among this occupancy-qualified subspace is 5. This is NOT an exhaustive minimum search over all 3^15 pilots; the parity proof handles all independent and overlapping words. A separate local native C++ loop enumerated the complete 3^15 ternary words and applied the same necessary occupancy filter, reproducing 310272 candidates and zero equality witnesses.

A synthetic exact candidate-list decoder runs 40 cases per witness at e,f satisfying 2e+f=d-1. It enumerates phases, constructs the contingency matrix against received value ranks excluding flagged erasures, and keeps all phases having at least N-f-e compatible observations. The 240 synthetic trials all returned exactly the injected phase; the fault values are particular outliers and the mathematical proof, not the trials, establishes universality. The fixtures contain no human data. The deterministic receipt was generated by executing the actual committed JavaScript retrieved from GitHub in V8. No full-repository native test is claimed.

Source ledger, read 27 November 2026 by the same agent: Koji Momihara, Qi Wang and Qing Xiang, *Cyclotomy, difference sets, sequences with low correlation, strongly regular graphs, and related geometric substructures*, author-hosted survey PDF https://bpb-us-w2.wpmucdn.com/sites.udel.edu/dist/a/6387/files/2018/08/article_Momihara_Wang_Xiang-1zwtlfm.pdf . Read introduction through the definition of cyclotomic classes, especially pp.1–2 and Eq.(1.1); visually inspected printed p.2 (PDF index 1). Publication year/edition not independently resolved from this proof PDF. The cited passage explains the equivalence between complete cyclic difference sets and binary two-level periodic autocorrelation. This expedition uses the elementary correlation identity only at selected lags. The discovered middle masks are NOT claimed to be difference sets, and binary autocorrelation does not determine the full ordinal chain distance. The specific divisibility obstruction and finite witnesses are derived here; priority unassessed. Predecessor #801 complete report, issue body/comments, PR and exact-head workflow status were also inspected. Its workflow was completed successfully. No independent critique.

Interpretation: maximizing a collection of local distinctions can impose a global arithmetic constraint invisible in an individual comparison. The 15-tick impossibility is an example of an integer obstruction that cannot be repaired by a more expensive optimizer. This is coding theory and combinatorics; it is not a theory of human meaning. No extra explanatory contribution from cybersemiotics is demonstrated (Brier subtraction).

Design hypothesis: expose the candidate vocabulary, absolute correction distance and required reference length as independent controls in a synthetic Observatory receiver. Offer the 30-tick pilot as a compact five-phase alternative, and the five certified six-phase profiles as independent design choices, not as a universal repetition rule. Use the predecessor's guard spacing for plateau-limited quantization only when that channel contract is independently established. Test lower output-gap, dense noise, spectral occupancy, channel stability and clock errors separately. No VST, physical channel, real-time performance, perceptual or human validation is established.

Checkpoint: base main 495a98ca12bae467a507031f04931aa4254b1866; branch mhac-805/parity-clock. AGENTS, RAG, programme, runbook, integrity, validation, experiments and human gates read; nested research/AGENTS and research/expeditions/AGENTS absent. Reconciled 466 branch entries, 30 recent issue and 30 PR results, targeted ordinal/parity duplicate searches, #801/#802 and exact-head workflow status, new #805 and empty comments. Fresh additive path only, no canonical manifests or other workers' branches. Draft/HOLD pending independent critique and exact-head CI. No human gate required for synthetic work. Full repository native validation not performed.

Fiction: Five clerks try to divide fifteen marks into mutually consistent ledgers. Each pair demands that their zero counts have opposite parity. The apprentice needs no new ink to see that three such clerks cannot coexist. She doubles the paper, then measures exactly what has been gained.
