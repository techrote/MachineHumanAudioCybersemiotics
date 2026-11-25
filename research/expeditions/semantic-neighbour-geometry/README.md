# The Dictionary That Cannot Put Its Neighbours Close

Issue #600 · 2026-11-25 · exploratory formal and synthetic research, not an accepted Track E/G finding. One GPT-6.2 research agent; no independent human review, listener recruitment, physical measurements, or scientific-priority claim.

## The anomaly

Consider two classes A and B of m and n states, with m,n >= 2. Specify a fictional semantic metric: every pair of distinct states in the same class has distance 2; every cross-class pair has distance 1. This is the shortest-path metric of the complete bipartite graph K(m,n). It satisfies every triangle inequality. A hypothetical dictionary requires unlike-context substitutions to be acoustically near, but alternative actions within each context to remain far. These are stipulated relations, not measured similarity or an operational policy.

Can a single dictionary of aligned acoustic waveforms preserve those numerical distances under RMS difference? Adding dimensions does not suffice. There is an exact distortion floor, an additional cost when all tokens must have identical energy, and a surprisingly economical exact representation under a different metric.

## Euclidean distortion and rigidity (proof)

Write x_i and y_j for waveform vectors in a real Hilbert space. Normalize the embedding to be noncontracting: within-class distances >= 2, cross-class distances >= 1, and all distances <= D times the corresponding target distance. This normalization is always available for the usual scale-invariant multiplicative distortion of an injective finite embedding.

Let mu and nu be the class means and let V_A,V_B be their average squared deviations. Expanding the squared norms gives

    V_A = (1/(2m^2)) sum_{i,k} ||x_i-x_k||^2 >= a = 2(1-1/m)
    V_B >= b = 2(1-1/n)
    mean_{i,j} ||x_i-y_j||^2 = V_A+V_B+||mu-nu||^2.

Since every cross distance is at most D, D^2 >= a+b. Attainment: in orthogonal coordinate subspaces take x_i = sqrt(2)(e_i - 1_m/m) and y_j = sqrt(2)(e_j - 1_n/n), with both class means zero. The within distances are exactly 2, cross distances exactly sqrt(a+b) >= 1. Thus

    D_2(K(m,n)) = sqrt(4-2/m-2/n).

This is an elementary specialization of established Hilbert-space distance geometry. No priority claim. For example K(2,6) requires D=sqrt(8/3), about 1.633; K(8,8) requires sqrt(3.5), about 1.871.

**Rigidity:** equality requires V_A=a, V_B=b and mu=nu, and every cross distance attaining its upper bound. The variance equalities force all within distances to equal 2, hence the centered class vectors form regular simplices with spans of dimensions m-1 and n-1 (their Gram blocks are 2(I-J/k)). Their equal cross distances, equal class radii and common centroid force every cross inner product to vanish. Thus the two spans are orthogonal. The minimal affine dimension at optimum is exactly m+n-2. Extra dimensions alone cannot remove the distortion, and a dictionary with fewer dimensions cannot attain even this optimal distortion.

**Distance compression as an alternative contract:** replace each original distance d by d^alpha, with 0<alpha<=1. Now within distance is 2^alpha and cross distance 1. The same mean identity yields necessity 2^(2alpha)(2-1/m-1/n)/2 <= 1. Sufficiency follows by using orthogonal regular simplices of that edge length and separating their centers along an additional axis by the square root of the remaining cross squared distance. Thus the maximum exact exponent is alpha*=log_2(4/(a+b))/2. At the boundary the affine dimension is m+n-2; below it, the exact equidistant cross contract requires one extra affine dimension (the mean difference is nonzero and orthogonal to both centered spans by subtracting the equal cross-distance equations and averaging). This changes the requested metric; it is not lossless translation of the original distances.

## Equal-energy price (proof)

A designer may additionally require every waveform to have squared norm E, in the same fixed units as the within-distance floor of 2. This is digital energy, not subjective loudness. Necessarily E>=max(a,b), since E=V_A+||mu||^2 and E=V_B+||nu||^2.

The mean cross squared distance is now 2E-2<mu,nu>. By Cauchy-Schwarz and the variance lower bounds it is at least

    C(E) = 2E - 2 sqrt((E-a)(E-b))
         = a+b + (sqrt(E-a)-sqrt(E-b))^2.

This is achieved exactly: retain the orthogonal centered simplexes, and add common-axis components of lengths sqrt(E-a), sqrt(E-b), both along the same direction orthogonal to the simplexes. All norms equal sqrt(E), all within distances equal 2, all cross distances equal sqrt(C(E)). Therefore the minimum normalized distortion at energy E is sqrt(C(E)). If a=b the energy cost above the minimum is unnecessary for distortion; if a!=b every finite E gives a strictly positive excess. No finite-energy equal-norm embedding attains the unrestricted optimum for unequal class sizes. This conclusion concerns the fixed distance scale; independently normalizing each waveform generally changes its pair distances.

The energy frontier is monotone decreasing for unequal sizes: the difference of the square roots equals (b-a)/(sqrt(E-a)+sqrt(E-b)). At E=max(a,b), C=2max(a,b). As E tends to infinity, C approaches a+b. For tolerance epsilon in squared cross distance, with 0<epsilon<=|a-b|, the sharp required energy is

    E_min = (a+b)/2 + epsilon/4 + (a-b)^2/(4epsilon).

Derivation: put u=sqrt(E-min(a,b)), v=sqrt(E-max(a,b)), then u-v=sqrt(epsilon) and u+v=|a-b|/sqrt(epsilon); square u and add min(a,b). For epsilon>=|a-b| the minimum energy is max(a,b). For unequal sizes, epsilon=0 is impossible at finite E. This is an exact inverse, not an empirical energy requirement. Divergence is a common-mode cost, which in a physical system may run into dynamic range or clipping; no claim that increasing acoustic level is desirable.

Example K(2,6): a=1,b=5/3. Unrestricted squared cross distance = 8/3. With equal E=5/3 it is 10/3; at E=8 it is about 2.68334. The squared excess declines from 2/3 to about 0.01668, at a large energy cost. A shared reference component can carry considerable energy without increasing within-class differences.

## Exact maximum-coordinate representation (proof)

Change the observation metric to max_j |x_j-y_j|, rather than Euclidean distance. This is a different, explicit feature-receiver contract, not a transformation of hearing.

Construction: use p=ceil(log2 m) binary coordinates for class A and q=ceil(log2 n) for B. Each A state has a distinct sign word (+/-1) on its p coordinates and zeros on B's q coordinates; B uses the opposite allocation. Within-class pairs differ by 2 in at least one coordinate, cross-class pairs differ by exactly 1 in max norm. Hence the dimension p+q suffices.

Lower bound for arbitrary real coordinates: every coordinate ranges over at most 2 on the whole dictionary. A coordinate that witnesses a distance-2 A pair must take opposite range endpoints on those two points; every B coordinate value is constrained by its distance <=1 to each of those endpoints, so all B values are their midpoint. Such a coordinate cannot witness a distance-2 B pair. For A, threshold every A-witnessing coordinate at the midpoint of its range, breaking midpoint ties consistently. Every distinct A pair must disagree on one of these binary tests, so there must be at least p A-witnessing coordinates. Similarly at least q disjoint B-witnessing coordinates. Therefore the exact real max-norm dimension is p+q. Middle coordinate values do not evade the bound.

K(8,8) needs just six max-norm coordinates for exact geometry, versus fourteen Euclidean dimensions even to attain distortion sqrt(3.5). K(32,32) needs ten versus sixty-two. The two contracts measure different functions of the same features. The sign-word construction is not Euclidean-isometric, and its variable energy is not automatically appropriate for an acoustic dictionary.

## Local audit failure

The distortion floor is increasing in both class sizes. A four-state subset of a large dictionary can at worst contain two members of each class and requires only sqrt(2) distortion; three or fewer states are isometric (a two-leaf star is a line). For a subset cap k>=4 with both class sizes at least ceil(k/2), the worst subset distortion is

    D_k = sqrt(4 - 2/floor(k/2) - 2/ceil(k/2)).

Proof: for fixed positive group sum s, 1/u+1/v is minimized at balanced sizes; increasing s increases that maximum. Single-class subsets are regular simplexes; a one-versus-j subset is the same centroid construction with a=0 and b=2(1-1/j), valid for j>=2, and the 1-versus-1 subset is a single segment. This covers all edge cases. Each subset may use its own embedding. For K(8,8), every subset of up to four states can separately meet distortion 1.5, while the entire dictionary cannot. This is not a claim about a *single* fixed embedding that passes all pairs; it is an obstruction to inferring global realizability from locally fitted prototypes.

An alternative explicit symbolic feature table or context-conditioned decoder may avoid demanding a single global metric at all. Such alternatives require their own engineering and semantic validation.

## Execution and negative sediment

Run the committed standalone JavaScript: node laboratory.cjs. The retained execution receipt reports 1,805 Euclidean construction profiles (19x19 class sizes, 5 energy settings including unconstrained), 565,326 coordinate-pair checks across Euclidean and max-norm constructions, 1,710 inverse-energy cases, 2,470 balanced-subset checks, 613,396 total assertions and maximum absolute numerical error about 4e-15. The first trial exposed floating-point sensitivity in evaluating the inverse at the minimal-energy endpoint: tiny rounding above max(a,b) produced a square-root perturbation of order 1e-8. The endpoint is now explicitly selected, and nonfinite errors are rejected. This is numerical implementation sediment, not a counterexample to the proof.

Separate native Python witness (distributed with this run's local package) uses exact rational centered Gram matrices and symmetric Schur elimination, testing 64 class profiles, 320 centered-matrix certificates and 320 equal-energy Gram profiles with rational centroid components. Literal ternary-grid search examined 46,298 first-class subsets across 27 (m,n,dimension) profiles, agreeing with the max-norm formula on that finite grid. The analytic argument, not that grid, covers arbitrary real coordinates. Same-agent checks, not independent peer review.

Four original synthetic PCM dictionaries for K(2,6) are generated by the native witness: free-energy orthogonal simplexes, equal low energy E=5/3, equal high energy E=8, and max-coordinate sign words. Each contains eight 200-ms tokens separated by 50-ms silence, in class order, with a common fixed gain 0.08; 8 kHz mono signed PCM16. Coefficients modulate RMS-orthonormal sine basis tones at 200+100j Hz. Exact real coefficient geometry is approximated by rounded PCM; normalized squared RMS distances were computed directly from integer samples and differ from coefficient Euclidean distances by at most 0.000406 across all four banks. All tokens avoid clipping. The max-coordinate bank has actual squared RMS cross distance about 4 rather than the intended max-coordinate distance squared of 1: explicit negative control against confusing the receiver metrics. Audio files remain local, not a physical experiment, not equal perceived loudness, not an actual semantic decoding task. The common gain is arbitrary and no safety or level calibration is claimed.

## Source ledger and contrary constraint

- I. J. Schoenberg (1938), *Metric Spaces and Positive Definite Functions*, Trans. AMS 44, 522-536, https://doi.org/10.2307/1989894. Read the university-hosted scan, printed p. 522 introduction and p. 527 Theorem 1/Corollary 1 with original page images (https://pages.stat.wisc.edu/~wahba/stat860public/pdf1/schoenberg.1938.pdf). Mathematical ancestry: the Euclidean/Hilbert distance realizability problem has an established positive-definiteness characterization. The present centroid proofs do not rely on unverified generalization of that theorem. No novelty priority search beyond targeted discovery.
- J. M. Grey (1977), *Multidimensional perceptual scaling of musical timbres*, JASA 61, 1270-1277, https://doi.org/10.1121/1.381428. Read printed p. 1270 abstract/introduction in Columbia-hosted scan, original page image inspected (https://sites.music.columbia.edu/cmc/courses/g6610/fall2019/week3/Grey_1977_Multidimensional_perceptual_scaling_of_musical_timbres.pdf). Author reports a multidimensional scaling study of synthesized instrumental tones and a separate label-learning task. The geometry was fitted to judgments; it was not the same as RMS waveform distance. No full empirical appraisal or accepted MHAC result.
- A. Tversky (1977), *Features of Similarity*, Psychological Review 84, 327-352, https://doi.org/10.1037/0033-295x.84.4.327. Read abstract and introductory discussion on pp. 327-329, including metric axioms and caveats about ordinal evidence, via https://worthylab.org/wp-content/uploads/2021/08/tversky1977_featuresofsimilarity_psychreview.pdf. Original screenshot retrieval failed on initial reference; text sufficient for the limited claim. Tversky challenges treating similarity as a symmetric metric and proposes feature matching. This is a contrary theoretical constraint, not evidence that human listeners use max norm.

All source readings were by the same AI agent on 2026-11-25, passage-level rather than complete critical extraction. No source PDFs copied into the repository. No claims of independent review, endorsement, human validation or study inclusion. The task-dependent dissimilarities of actual users might be asymmetric, ordinal, context-varying or nonmetric; the fictional bipartite relation is merely one stress test.

## Exaptation and next falsifier

The proposed engineering audit begins by writing down exactly which notion of similarity must be preserved, which pair distances must hold jointly, and whether RMS energy normalization is mandated. If the desired dissimilarities are only ordinal, a nonlinear remapping may be acceptable; if cardinal, the exact obstruction can prune a renderer before any audition. Compare a direct symbolic table, an RMS metric renderer, and a max-feature-distance renderer at matched task and calibrated signal level. Record feature recovery and class-specific confusion separately; human action/perception remains gated. A nonlinear compression or context-specific feature map is not a universal remedy; the evidence should specify what relation was changed. Ordinary geometry and feature-based alternatives explain this anomaly without requiring a cybersemiotic theory. No remove-Brier test result is asserted for the wider programme.

A fictional afterword: a clerk builds two drawers of signs. Every sign must sit next to every sign in the other drawer, but far away from its own neighbours. He adds another dimension. The apprentices add a second ruler. The drawers finally fit, but they have changed what it means to be near.

## Custody

Main observed at 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity and validation; surveyed 360 branch entries, 100 recent open issue results and 100 open PR results; targeted searches for metric embedding, Euclidean, distortion, Ptolemy and ultrametric; read #254 and #41 bodies/comments and #600 scope/comments. #593 exact-head workflow 45669140334 completed successfully, but is still a draft. No shared manifests, existing worker branches or canonical evidence changed. Git native checkout failed DNS resolution. This is a Refs-only draft pending full repository CI and independent critique, not accepted research.
