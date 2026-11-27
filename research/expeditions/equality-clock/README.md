# The Clock That Remembers Equality

Refs #792, #788/#789, #784/#785 and related #292. Exploratory mathematics and synthetic DSP, 27 November 2026, outside frozen Track E/G. One ChatGPT agent performed derivations, source reading, finite search and code checks. No scientific-priority, participant, physical-channel or independent-review claim.

## Observation contract

The preceding zero-free-clock expedition proved a sharp three-survivor count under arbitrary fixed affine gain/offset with a nonzero gain floor. It also recorded a negative result: a strictly increasing quadratic cannot distinguish phase under an unrestricted monotone recalibration. Here the receiver knows a finite scalar pilot x of length N+K-1, and must recover s in {0,...,K-1} from indexed observations y_t=F(x_(t+s)), 0<=t<N, except up to e arbitrary replacements and f flagged missing values. F is unknown, fixed within a window, strictly increasing OR strictly decreasing, and may be different in alternative explanations. Original indices survive erasure; these are not unknown deletions or clock-rate drift. Ties in x are exact deliberate symbols, and the basic contract has no dense noise. The separate noise contract below gives F a lower slope bound. Pilot independently observable; no unrestricted interfering payload.

## Exact distance: weighted monotone chains, not rank distance with arbitrary tie breaking

For two indexed words a,b of length N, define L(a,b) to be the largest size of a common subset T on which a and b have the same weak order up to a global reversal. In other words, every comparison sign including equality agrees after multiplying all signs of b by either +1 or -1. Define L=max over distinct phase pairs. Then the exact universal identification criterion is

    N - L > 2e + f.

Proof, necessity: on a compatible subset, choose target values equally spaced in the common order of distinct levels. Each word admits a strictly monotone piecewise-linear interpolation to these values, extended outside the selected levels; if a positive lower slope bound is required, choose the target gaps large enough for both pilots. Equal inputs map to the same output. Hence both hypotheses agree there. Split the other N-|T| positions into a common erasure set of at most f and two disjoint replacement sets of at most e each. Retain one hypothesis's exact value on the other hypothesis's corruption set. This gives an identical received word for both. Sufficiency: two compatible explanations must agree on at least N-2e-f positions outside their joint replacements and the common erasure set. Strict monotonicity preserves equalities and all inequalities up to global reversal, so that set has size at most L. For a given erasure mask restrict the pair calculation to the remaining positions; the universal formula is over adversarial erasure choices.

The quantity L is efficiently computable even when there are ties. For each orientation d=+1,-1, form cells (a_t,d*b_t), aggregate identical cells with integer multiplicities w, and sort cells by first coordinate then second. A valid subset consists of complete selected cells in a chain strictly increasing in BOTH coordinates. Different cells sharing just one coordinate cannot coexist because one word would contain a tie the other lacks. A chain may take all copies of each chosen cell. Dynamic programming computes

    D_i = w_i + max({D_j : a_j<a_i and d*b_j<d*b_i} union {0}).

The largest D_i over both orientations is L(a,b). O(N^2) time and O(N) space for the simple implementation; faster weighted range-maximum algorithms are possible but unimplemented. For distinct-valued words, sort by a then find longest increasing and decreasing subsequences of b. In rank-list terminology the distance is the minimum Ulam distance to either orientation of the other word. Do not naively break physical ties: equality is part of the signal.

Noiseless candidate-list decoding uses exactly the same algorithm, treating the received values as the second word after deleting flagged positions. Keep phase s iff L(x_s,y)>=N-f_actual-e. The result is the complete feasible phase set, including ambiguity and no-candidate states. A strictly monotone map fitting any compatible subset exists by interpolation; arbitrary other values are allowed on replacement positions. This avoids combinatorial subset enumeration in the noiseless decoder.

## The square-root obstruction for distinct levels

Assume every phase word has distinct levels, even if distant pilot entries repeat. For any pair, sort indices by the first word. The other word is a distinct sequence. The classical Erdős–Szekeres theorem gives max(LIS,LDS)>=ceil(sqrt(N)). Direct proof: associate each index with lengths of the longest increasing and decreasing subsequences ending there. Distinct indices have distinct pairs since one direction extends from the earlier index to the later. If both lengths are <=m there can be at most m^2 indices.

Thus every distinct-level pilot with unknown monotone polarity must leave at least ceil(sqrt(N))+1 effective survivors to ensure phase recovery. This bound is not an assertion that overlapping shift codes attain it for every N. Unlike the affine model, the number of survivors cannot remain three as N grows.

A stronger small-N obstruction appears for K>=3: no three distinct-level rank orders on four indexed ticks can have every triple pairwise distinguishable up to reversal. Relabel indices so the first rank vector is (0,1,2,3). Of the 24 possible other rank vectors, exactly four have LIS and LDS both <=2. Up to reversal their representatives are (1,0,3,2) and (1,3,0,2). Those two share a compatible triple; choosing the same representative also fails. So among three arbitrary orders some pair agrees on three ticks. This is even stronger than an obstruction for shifts of one pilot. For N>=4 apply the argument to any four ticks. Consequently L>=max(3,ceil(sqrt(N))) for K>=3 and N>=4; at N=3 the three distinct middle-index signatures can be attained.

There is also a useful existence bound for actual overlapping shifted pilots. Draw N+K-1 independent continuous random values (equivalently a uniform random permutation of ranks). For phase pair s,u, every compared tick uses two reference indices t+s,t+u. For a set of m ticks the graph of these index pairs is a disjoint union of paths: every edge has the same positive index difference and each vertex has at most two neighbors. A matching has at least ceil(m/2) edges. Hence a compatible subset of size >=2q-1 implies a compatible q-subset whose 2q reference indices are all distinct. For any fixed such q-subset the two rank orders are independent and uniform; probability of identical or reverse orders is 2/q! (q>=2). Union bound over phase pairs and candidate q-subsets shows that if

    K(K-1) * binomial(N,q) < q!,

then some overlapping distinct-level pilot has L<=2q-2. For fixed K take q=ceil(c sqrt(N)) for any c>Euler's e; the bound follows from binomial(N,q)/q! <= (Euler's e squared * N / q squared)^q. Combining the lower and upper bounds gives order sqrt(N) for the smallest attainable L at fixed K as N grows. This is an existence proof, not a claim of constructive optimal constants. Exact integer q-bound calculations for N=100,1000,10000 and K=3,8 are in the receipt. At K=3,N=10000 they give 100<=optimal L<=534; at most 535 survivors suffice by existence, compared with at least 101 required. There is no probability claim about a physical channel.

## Deliberate equality breaks the distinct-level obstruction

For K>=3, two surviving indexed ticks cannot suffice under arbitrary unknown monotone polarity, even allowing ties: each phase is either equal or unequal on that pair, and two of at least three phases share a class. This is a pigeonhole obstruction. On the other hand, repeated levels enable L=2 for N=3 through N=8 in the finite fixtures. In particular the following 10-tick pilot for three offsets and N=8 uses just four levels:

    (1,3,0,0,1,0,3,2,3,3)

All three phase-pair chain lengths, in both orientations, are exactly 2. Thus every 3-index retained subset distinguishes all three phases, and 2e+f<=5 is universally correctable. This attains the absolute two-survivor obstruction, so the 3-survivor count is sharp at this N, even against all real-valued scalar pilots under the stated channel. With e=2,f=1 it is possible to identify phase from 8 scheduled ticks. In the distinct-level contract that would be impossible: L>=3 so at least 4 effective survivors are required. Equality is not missing rank information here; it supplies a different type of information.

The three phase words are

    s=0: 1 3 0 0 1 0 3 2
    s=1: 3 0 0 1 0 3 2 3
    s=2: 0 0 1 0 3 2 3 3

On the retained triple (0,2,3), for example, phase 0 gives (1,0,0), phase 1 gives (3,0,1), phase 2 gives (0,1,0). Phase 0 and phase 2 have different equality partners and phase 1 has all distinct levels. Neither amplitude gain, offset nor any strictly monotone transformation can erase these distinctions. The full certificate checks all masks for each pair (including both signs).

A 14-tick six-level pilot for N=12, K=3,

    (1,5,0,4,0,2,5,4,5,5,2,3,3,0),

has L=3 for all phase pairs and both signs. It guarantees four effective survivors; the distinct-level lower bound requires at least five. This is a feasible witness, not proof of optimality over ties at N=12. These fixtures were discovered by a same-agent exploratory Python enumeration and seeded random/local search; the retained JS laboratory verifies their exact properties independently of the search process but does not reproduce the heuristic search itself. The distinct-level pilot for N=8 in the receipt attains L=3 and the N=12 one L=4, so those distinct-level optima are also sharp. At N=9,16,25 our retained distinct pilots do not attain the lower bound; whether better overlapping pilots exist remains unresolved.

| N | Distinct-level minimum survivors (proved or bounded) | Tied witness survivors |
|---:|---|---:|
| 3 | 3 exact | 3 exact |
| 4 | 4 exact | 3 exact |
| 5 | 4 exact | 3 exact |
| 6 | 4 exact | 3 exact |
| 7 | 4 exact | 3 exact |
| 8 | 4 exact | 3 exact |
| 9 | 4 to 5 | not qualified |
| 12 | 5 exact | 4 feasible |
| 16 | 5 to 6 | not qualified |
| 25 | 6 to 7 | not qualified |

Exhaustive distinct-pilot search for N=3..7 enumerates (N+2)!/2 rank permutations, quotienting by global rank reversal. Receipt includes exact histograms. These are rank-level exhaustive searches, not floating-point searches of continuous values.

## A sharp dense-noise boundary for the four-level witness

Unrestricted strictly monotone transforms permit arbitrary compression of output levels, so no positive uniform dense-noise radius exists even for a perfectly identifiable ordinal pilot. Add a contract: a fixed known g>0 such that |F(u)-F(v)|>=g|u-v| for all pilot levels u,v (orientation remains unknown, no slope upper bound). Let Delta be the smallest positive gap between distinct pilot levels. Add dense noise of total L2 norm <=epsilon on surviving uncorrupted samples. The exact noiseless criterion above remains valid because the common target gaps in its necessity proof can be made sufficiently large.

For any pair of incompatible restricted weak orders, under either choice of relative orientation there is a pair of ticks i,j at which comparison signs differ. If one hypothesis ties and the other strictly orders them, the difference vector h between clean hypotheses satisfies |h_i-h_j|>=g Delta. If both strictly order them oppositely, the lower bound is 2g Delta. Cauchy–Schwarz yields ||h||_2>=g Delta/sqrt(2). For every pair after adversarial union trimming with N-2e-f>L this gives the universal sufficient radius

    epsilon < g Delta/(2 sqrt(2)).

For the N=8 four-level witness at r=2e+f=5 this is sharp. On T=(0,2,3) choose phase-0 transformed levels 0->0,1->4,2->5,3->6 and phase-1 levels 0->-1/2,1->1/2,2->3/2,3->4, all increasing with slope floor g=1. The clean triple predictions are (4,0,0) and (4,-1/2,1/2); squared distance is 1/2, hence half-distance squared is 1/8. At e=2,f=1 erase tick 1; for phase 0 corrupt 4,5, and for phase 1 corrupt 6,7. Take midpoint on T and the other hypothesis's clean values on each respective corruption set. Both explanations produce exactly the same observation vector with dense noise norm sqrt(1/8). The receipt retains all arrays in integer quarter units and the candidate-list output [0,1] at equality and [] just below. Since any allocation satisfying r=5 permits a corresponding partition, the same pair construction works at all such budgets. If levels are evenly scaled to peak A=1 in [-1,1], Delta=2/3, so the sharp radius is g/(3 sqrt(2)), about 0.23570226 at g=1, in total observed L2 units. No noise distribution or acoustic performance estimate is implied.

For exact bounded-noise candidate lists, enumerate candidate clean subsets of size max(0,N-f_actual-e), fit each orientation separately. Sort by oriented pilot value z=d*x, aggregate equal z, and write F(d*z)=g*z+b(z), where b must be nondecreasing. Fit b to y-g*z by weighted least-squares isotonic regression (pool adjacent violators). For a constant fitted block, the residual is sum of squared data minus square of the sum divided by count. Retain a phase iff some subset and orientation attains residual squared <=epsilon^2. The laboratory uses integer data scaled by four and multiplies costs by 840 (divisible by each block size 1..8), so decisions in the tested profiles are exact, not tolerance-dependent. This is a bounded N<=8 fixture implementation and an exponential subset oracle for the mixed-fault/noise problem, not a general streaming receiver. Unlike the noiseless weighted-chain decoder, no polynomial time mixed-noise algorithm is claimed.

Negative sediment: if the transmitter breaks exact ties before the channel by an unknown perturbation, the three-survivor guarantee can disappear; the deterministic jitter x_i'=100*x_i+i makes the N=8 witness's L rise from 2 to 5. Quantization that collapses distinct levels, clipping, a non-strict or time-varying channel, unknown index alignment, and arbitrary payload cancellation also violate the stated contract. A lower slope bound is not an upper bound, a calibration measurement, or evidence of a physical link. In an application tie motifs need a verified level-generation and noise model, rather than blind numerical comparison.

## Source ledger and intellectual connection

- Christoph Bandt and Bernd Pompe, *Permutation Entropy: A Natural Complexity Measure for Time Series*, Phys. Rev. Lett. 88, 174102 (2002), https://doi.org/10.1103/PhysRevLett.88.174102 . Publisher metadata and abstract read; PDF extracted text opening and Sec. II defining discussion read at https://wiki.santafe.edu/images/b/b8/2002_Bandt_PRE.pdf ; page image attempt returned HTTP 502. Their ordinal-pattern representation is invariant to monotone changes. Their basic definition explicitly sets aside equal values and discusses artificial perturbation of equalities; that is not a prescription for our intentional equalities. We use indexed order patterns for discrimination, not entropy as a phase decoder.
- Farzad Farnoud (Hassanzadeh), Vitaly Skachek and Olgica Milenkovic, *Error-Correction in Flash Memories via Codes in the Ulam Metric*, IEEE TIT 59(5), 3003–3020 (2013), https://doi.org/10.1109/TIT.2013.2239700 . Institutional abstract and source PDF https://fhfarnoud.github.io/docs/papers/06410424.pdf read introduction and discussion through Proposition 3; printed p.3005 image inspected, including figures and the translocation/Ulam distance equivalence. This supplies the direct prior art for rank-coded error correction and longest common subsequences. Their permutation codewords are not constrained to overlapping shifts of one acoustic pilot and ordinarily use distinct ranks. No novelty claim for Ulam distance, rank modulation or isotonic regression.
- P. Erdős and G. Szekeres, *A combinatorial problem in geometry*, Compositio Mathematica 2 (1935), 463–470, https://numdam.org/item/CM_1935__2__463_0/ . Original scan https://www.numdam.org/item/CM_1935__2__463_0.pdf retrieved; printed pp.467–468 (second proof, theorem and Eqs.7–8) read and visually inspected. Their weak monotone subsequence convention allows equal ordinates with distinct abscissae; our matching condition requires both words' equality relationships to agree, so it is not an unqualified extension of the theorem to ties. The article acknowledges Richard Rado's independent consideration in a footnote. The short rank-pair proof here is a standard proof, not claimed as original.

All source reading by one ChatGPT agent; not full-paper reading or independent review. No primary empirical outcomes imported. #292's issue body and comments concern missing rank notes and candidate-count bias under different deletion observations; attempted branch report path returned 404, so no claim based on unread report. The #788 branch report and complete issue/comment state were inspected and its exact-head workflow 45985036452 completed successfully. This expedition builds on its explicit arbitrary-monotone counterexample and changes the design contract. The distinct-level lower bound, overlapping-shift existence argument, weak-order chain criterion, tie witnesses and sharp noise boundary are derived here; scientific priority unassessed.

Interpretation: preserving equality can make a signal more informative under coarse calibration even though it reduces the number of numerical levels. This is a specific coding-theoretic result, not a demonstration that human listeners understand equality as a particular semantic concept. Design hypothesis: an experimental receiver could compare exact level-repetition motifs to distinct-rank and affine pilots under calibrated slope floors and indexed dropout, reporting candidate sets and explicit violated assumptions. Brier subtraction: conventional order theory, rank modulation, monotone interpolation and coding theory explain all demonstrated phenomena. No additional cybersemiotic explanatory mechanism or human benefit established.

## Reproduction, qualification and checkpoint

Run node laboratory.cjs. No dependencies. Source and receipt committed and retrieved; V8 replay matched receipt bytes exactly (source blob de679c50e675eace6d6624d6af84ad14625812ca, receipt blob d86cf6d6d71868f51aedc5123c88ae7e307fe601). 204,540 exhaustive reversal-reduced distinct-rank pilots for N=3..7; 28,416 mask-loop cases for finite witness profiles (smaller masks pruned when already dominated); 600 seeded chain vs exhaustive mask comparisons; 600 noiseless unique phase/candidate-list tests with brute-oracle agreement; 600 slope-floor strict-radius tests; exact rational midpoint at radius, jittered negative control, six integer existence bounds and four-tick order obstruction. No final assertion failures. Seeded trials are finite synthetic checks; the universal guarantees rest on the proofs. Full native repository validation, independent mathematical critique, real audio transmission, quantization and human testing not performed. The source code uses integer arithmetic within safe range for these small fixtures and BigInt for large binomial bounds. No external packages, device control, or licensing decisions.

Base main 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, README, RAG, programme, runbook, research integrity, validation, experiments and human gates. No nested research/expeditions AGENTS found. Reconciled 459 branch entries and 30 recent issue/PR results, targeted ordinal and monotone-pilot duplicate searches; fresh #792 issue/comments read. Scope only research/expeditions/equality-clock/ on mhac-792/equality-clock. Draft/HOLD for integrator critique and exact-head CI; no canonical registry or other worker branch changed. No human gate required for synthetic work.

Fiction: An apprentice has lost her ruler, her zero and the direction of her scale. She learns that two marks made at the same height remain equal under any strictly monotone ruler. She refuses the master's instruction to jitter them apart merely to simplify the ledger.
