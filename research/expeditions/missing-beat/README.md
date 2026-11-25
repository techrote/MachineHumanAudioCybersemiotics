# The Rhythm That Cannot Name Its Missing Beat

MHAC expedition #428 · 2026-11-25 · Exploratory mathematics, synthetic computation, original composition and proposed design. AI-authored by one ChatGPT agent; not accepted Track E/G evidence, independent review, a novelty-priority claim or human validation.

## A missing event is not a missing coordinate

Suppose a receiver recognizes a rhythm independently of its starting time and tempo. Losing an onset now merges two intervals, and the receiver does not know which interval was altered. In a four-onset motif with successive gaps (phi,1,phi), where phi=(1+sqrt(5))/2, removing the second onset or the last onset leaves exactly the same relative three-onset shape. Removing the first or the third similarly creates another shared shape. A code may remain recognizable even when the precise damage cannot be diagnosed.

This is different from #404, which assumes indexed log-duration observations and expressly excludes unlabelled onset loss. #292 studies standardized pitch permutations and their deletion posterior; the present state space is ordered time points under positive affine transformations, rather than rank permutations. Both previous reports were inspected at relevant passages, on their existing branches only.

Reconciliation: base main 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, research integrity, validation, foundations; 273 branch names paginated, 100 recent open issue results and 100 open PR results inspected, targeted searches for segmentation/deciphering delay, onset and deletion. #224 already addresses finite decipherability, so that direction was not duplicated. #421 workflow run 45513157010 was completed successfully on the preceding expedition's recorded head. Created fresh issue #428, read entire issue and comment inventory (empty at creation). Only this issue's fresh directory and branch are modified. No accepted corpus dependency is asserted.

## Noiseless affine onset channel

A word X is a strictly increasing n-element set of real time points. Each transmission is transformed by t -> a t+b, a>0, with unknown independent a,b per transmission. Then at most d true onsets are deleted and at most i arbitrary distinct onsets are inserted. The receiver observes the ordered remaining set without identities, known frame markers, pitch labels or onset provenance. A packet's boundary is available as a collection delimiter, not a timestamp anchor; no duration bound on the observation is imposed in this first model. Reflection is excluded.

For two equal-length words define M(X,Y) as the maximum intersection cardinality over positive affine alignments of Y with X. It can be calculated exactly by trying all pairs of distinct onsets in each word, since any two ordered matches fix a positive affine map; if no two exist, use the one-point case. Equivalently, for a sorted k-subset S define its fingerprint for k>=2 as (s_j-s_1)/(s_k-s_1), with constant fingerprints for k=0,1. M is the largest k for which their k-subset fingerprint sets intersect.

**Theorem 1 (proof).** Two n-onset words are confusable iff M(X,Y) >= n-d-i. In a common output Z let A and B be the aligned true points retained from the two worlds. Each has size at least n-d, and at most i points of Z are outside A or outside B. Thus |A intersection B| >= |A|-i >= n-d-i. Conversely, choose an alignment attaining M, write u=n-M, and keep all common points. If u<=d, delete all remaining points. Otherwise select h=u-d distinct noncommon points of each aligned word, and include both selections in the common output. Each world deletes u-h<=d and inserts h<=i. The two exclusive sets are disjoint by construction. This also handles d+i>=n. No assumptions on random faults are made. The criterion is an onset-set version of the standard insertion/deletion confusability principle, combined with affine registration.

**Theorem 2 (proof).** For arbitrary finite alphabet size >=2, the minimum n admitting such an alphabet over unrestricted rational onset coordinates is d+i+3. Necessity: any two two-point subsets can be aligned, and one or zero surviving points are even less informative. Sufficiency: construct arbitrarily many words with disjoint triple-ratio sets. When adding a new rational point larger than the existing points of a new word, avoid the finitely many values that make (y-x)/(z-x) equal to a previously used ratio. Each equation in z has at most one solution for fixed x,y and forbidden ratio. A nonempty rational interval always has points outside this finite set, so a whole new word can be constructed even in a bounded open interval. No two distinct codewords can then have three affine-aligned points. This construction does not provide a uniform minimum separation or finite integer-grid alphabet bound.

For comparison, a fixed known temporal frame needs d+i+1 points (use disjoint sets); unknown translation without tempo scaling needs d+i+2 (one point can always align, and disjoint positive-difference sets are constructed by avoiding finitely many forbidden differences). An unknown positive affine transform therefore consumes two points before any shape information remains. This is a sharp minimum-length theorem for an unrestricted noiseless alphabet, not a human timing recommendation.

Example: X=(0,1,2,3) has triple ratios {1/3,1/2,2/3}; Y=(0,1,4,9) has {1/4,1/9,4/9,3/8}. They share no ratio. Four onsets correct one deletion OR one insertion (not one of each); five are needed for both budgets simultaneously.

## The four-onset golden anomaly

Write four onsets as (0,a,a+b,a+b+c), with all gaps positive. The four deletion fingerprints, enumerating the triples (123),(124),(134),(234), are

    r1=a/(a+b)
    r2=a/(a+b+c)
    r3=(a+b)/(a+b+c)
    r4=b/(b+c).

**Theorem 3 (proof).** The minimum number of distinct single-deletion fingerprints is two over the reals. Exactly two occur iff a=c=phi*b. Over rational gaps the minimum is three, attained by equal gaps.

Since r2<r1 and r2<r3, two distinct values force r1=r3, hence ac=ab+b². The remaining r4 must be r1 or r2. If r4=r1, then ac=b², impossible with a,b>0 and the previous equality. If r4=r2, then ac=b²+bc; equating the expressions gives a=c and a²=ab+b², whose unique positive root ratio is phi. Conversely those gaps give r1=r3=1/phi and r2=r4=1/phi². The irrationality of phi excludes rational equality. With equal gaps the fingerprint set is {1/3,1/2,2/3}. This proof does not establish any special perceptual property of golden-ratio rhythms.

A motif can therefore minimize its number of possible damaged shapes at the price of making the identity of the removed onset ambiguous. Under uniform deletion of one of the four onsets, the optimal index-guessing success probability is exactly |{r1,r2,r3,r4}|/4 if only the normalized receipt is observed. Each fingerprint has probability proportional to its multiplicity; each compatible index has equal posterior. The golden motif permits success 1/2, the equal-gap motif 3/4, a generic motif 1. In the rational setting exact golden ambiguity is impossible, yet arbitrarily close timing collisions remain possible.

**Fibonacci refinement.** Take palindromic gaps (p,q,p), p>q consecutive Fibonacci numbers. Then r1-r3=r2-r4=(p²-pq-q²)/((p+q)(2p+q)). The numerator has magnitude one: the step (p,q)->(p+q,p) changes its sign, starting with (2,1). There are four distinct ratios; the two pairs lie on opposite sides of 1/2. The two within-pair gaps are exactly 1/((p+q)(2p+q)). With total span L=2p+q, their separation is of order L^-2. No two different reduced fractions of denominators at most L can be closer than 1/(L(L-1)) for L>=2, by the integer cross-product bound (equal denominators are farther apart). Thus the near-collision rate has the sharp order in grid resolution. The ratio sequence is exactly distinguishable in rational arithmetic, but its distinction shrinks quadratically in normalized timing coordinates.

## Bounded timestamp jitter: exact separation and a failed shortcut

Now allow no spurious onsets, at most d deletions, and independently bounded additive errors on each surviving timestamp. Require a>=s0>0; there is no upper scale bound or offset bound. The receiver sees a strictly increasing set. Let m=max(0,n-d). For each pair of m-element increasing subsets U,V, define

    J(U,V) = (1/4) min_{a,b>=s0} range_j(a U_j - b V_j).

The range of an empty or singleton sequence is zero.

**Theorem 4 (proof).** Two words are confusable at timestamp-error radius eps iff min_{U,V} J(U,V)<=eps. Necessity follows by considering a common output, discarding additional matched points until m remain, and subtracting the two error vectors; the translation difference is free. Conversely, an offset can center the differences at their midrange. If the maximum centered discrepancy is <=2eps, choose the common timestamps as the midpoints of the two aligned noiseless sequences. Midpoints remain strictly increasing. The errors in both worlds are <=eps. Delete all other points. Minimization is attained: for >=2 points, simultaneous scaling down preserves feasibility until one scale equals s0; with that scale fixed the range is coercive in the other scale. One-point and empty cases are trivial. This proof assumes deletion-only in the jittered model; unmarked insertions plus jitter are not claimed here.

**Sharp triple formula.** For triples U,V of spans L_U,L_V and internal normalized positions r,s, respectively,

    J(U,V) = s0 * max(L_U,L_V) * |r-s| / 4.

Subtract the first timestamp. For scaled spans A,B and r>=s, the differences are (0,Ar-Bs,A-B). If A>=B, the middle difference is >=A(r-s). If B>=A, the middle minus final difference is >=B(r-s). Swap worlds for r<s. Hence the range is at least max(A,B)|r-s|. Equality holds at A=B=s0 max(L_U,L_V), which both scale constraints permit. Division by four gives the result. In particular, if each whole motif is normalized to span one, the two Fibonacci deletion pairs (one triple of full span and one shorter triple in each pair) become confusable at eps=s0/(4(p+q)(2p+q)). With raw integer time units the threshold instead is s0/(4(p+q)). An unrestricted scale tending to zero destroys all positive-jitter separation: any fixed two finite words can be shrunk near one common timestamp and midpoint matched.

For three-onset words normalized to span one, the entire nontrivial shape space is r in (0,1). The exact maximum continuous alphabet at positive jitter eps is max(1,ceil(s0/(4eps))). Indeed the spacing must be strictly greater than delta=4eps/s0. K points need (K-1)delta<1; whenever that inequality holds, equally spaced interior points can be chosen. The formula is not a finite-grid or psychophysical capacity. On a finite ratio grid the optimal spacing code is obtained greedily from the smallest available ratio, then the smallest ratio exceeding the previous by more than delta: replacing the first point of an optimal packing by the earliest eligible point cannot make future choices worse, and induction proves optimality.

**Negative result: endpoints need not match optimally for four or more points.** X=(0,1,2,3), Y=(0,1,3,4), s0=1, no deletions. Equalizing the scaled spans gives best radius 1/6. But choosing scales 3/2 and 1 yields differences (0,1/2,0,1/2), radius 1/8. This is optimal: the range is at least max(|a-b|,|a-2b|)>=b/2>=1/2, so its quarter is >=1/8. A receiver must not automatically normalize both endpoints before conducting a full jittered registration. The triple formula's simple structure does not extend unchanged.

## Finite-grid alphabets: exact packing and certificates

Permit integer nominal positions 0..L, modulo translation and positive scaling. Canonical words start at zero and have gcd of positive coordinates one. Every integer-grid orbit has such a primitive representative of span <=L; two primitive representatives in the same orbit must be identical (their reduced scaling must preserve gcd one). The possible normalized triple ratios form R_L={a/b:0<a<b<=L}, cardinality sum_{b=2}^L phi_Euler(b). Three-onset words realize each ratio exactly, so this is their exact noiseless vocabulary size without losses.

A four-onset vocabulary correcting one actual deletion is a set packing of triple-ratio sets in R_L. The same vocabulary corrects one actual insertion by Theorem 1. Every edge has at least three distinct ratios, so floor(|R_L|/3) is an upper bound, often loose. If each word's ratios have assigned nonnegative resource weights summing to at least one, the sum of all resource weights is another upper bound: disjoint words use disjoint resources. This standard fractional-cover argument turns a numerical search into an exactly checkable upper certificate.

The laboratory enumerated all primitive words for L=3..18 and found feasible packings with a MILP. Then the separate stdlib-only verifier established optimality exactly for every one of the 16 grid sizes: for 3..8, use exhaustive recurrence that branches on whether an available resource is unused or used by exactly one eligible edge; for 9..18, use stored packings and rational resource weights. In the latter range every ratio receives 1/4, with the following extra 1/4 bonuses:

| L | Bonus ratios |
|---|---|
| 9..12 | 1/3, 2/3 |
| 13..14 | 1/13, 1/3, 12/13, 2/3 |
| 15..18 | 1/3, 1/4, 2/3, 3/4 |

Every primitive word was checked to have weight >=1 in exact Fraction arithmetic. Every stored packing consists of eligible words with disjoint ratio sets. The floor of the rational upper bound equals the witness size in each case; no trust in MILP convergence tolerances is necessary for those ten profiles. The verifier's finite recurrence gives exact certificates for the remaining six.

| L | Candidate words | Triple ratios | Exact four-onset vocabulary | Simple upper bound |
|---:|---:|---:|---:|---:|
| 3 | 1 | 3 | 1 | 1 |
| 4 | 4 | 5 | 1 | 1 |
| 5 | 10 | 9 | 2 | 3 |
| 6 | 19 | 11 | 2 | 3 |
| 7 | 34 | 17 | 4 | 5 |
| 8 | 52 | 21 | 5 | 7 |
| 9 | 79 | 27 | 7 | 9 |
| 10 | 109 | 31 | 8 | 10 |
| 11 | 154 | 41 | 10 | 13 |
| 12 | 196 | 45 | 11 | 15 |
| 13 | 262 | 57 | 15 | 19 |
| 14 | 325 | 63 | 16 | 21 |
| 15 | 409 | 71 | 18 | 23 |
| 16 | 493 | 79 | 20 | 26 |
| 17 | 613 | 95 | 24 | 31 |
| 18 | 712 | 101 | 26 | 33 |

The bonus weights are finite-grid certificates, not a claimed universal formula for all L. In particular, the existence of three-fingerprint degeneracies does not mean the simple resource-count upper bound can be attained. At L=18 the proof bounds the optimum at floor(105/4)=26, and the supplied 26-word witness attains it. This is exact for the stipulated model and grid, not an experimentally validated code.

## Reproduction and acoustic witness

Run `python laboratory.py` with Python 3.13.5, SciPy 1.17.0 (NumPy transitively required), then `python verify_packing.py` (stdlib-only; numerical libraries are not imported by the verifier). The first writes full execution.json and three 8-kHz mono PCM16 WAVs in its own directory; run in a scratch copy if preserving a clean checkout. The full JSON is generated rather than committed; qualification.json records its hash and condensed outcomes. Repeated native runs reproduced the receipt byte-for-byte, including the waveform fingerprints. The exact verifier ran successfully after the numerical search and checks the committed compact packing-proof.json. Same-agent calculation methods, not independent review.

The census: 1,326 distinct pairs of primitive four-onset words through span 8 checked by both literal affine registration and normalized subset fingerprints; 1,680 fixed-frame pair/error-budget comparisons against literal output-set enumeration; 64,000 positive integer gap triples checked (0 two-fingerprint, 222 three-fingerprint, 63,778 four-fingerprint); 17 consecutive Fibonacci profiles; 400 direct numerical LP comparisons of the triple jitter formula, maximum discrepancy 2.665e-15; 64 finite-grid greedy spacing profiles (separation checked, optimality follows from the exchange proof). All assertions passed. The separate exact packing verifier uses integer recurrence and Fraction arithmetic, not the LP/MILP status, to check all 16 optima.

The original rational motif has gaps (144,89,144). Its distinct delete-last and delete-second fingerprints are 144/233 and 233/377, difference 1/87841. Normalize each surviving receipt to 0.8 seconds, with first onset at 0.1 s. Render each onset with a 20 ms tapered 500 Hz pulse. The two receipts produce identical sample onset indices [800,4755,7200] and byte-identical WAVs. The full original motif has [800,3245,4755,7200]. This is actual computed quantization equivalence, not a claim of equal human perception or of equivalence under arbitrary waveform resampling. The renderer selects a different affine frame after each deletion; a fixed external packet clock would change the situation.

Native Git checkout was attempted but DNS could not resolve github.com. Source files and certificate data were instead written using the repository connector and their Git blob hashes verified against the locally executed files. Full repo tests, exact-head CI and external critique remain outstanding at report preparation.

## Source ledger, cross-domain bridge and contrary evidence

- Daniel Cullina and Negar Kiyavash, *An Improvement to Levenshtein's Upper Bound on the Cardinality of Deletion Correcting Codes*, arXiv:1302.6562 (2013), [author preprint](https://arxiv.org/abs/1302.6562). Read rendered §§I, I-A, opening II-B; input/output packing and mixed insertion-deletion equivalence are established antecedents. Their string model does not include unknown affine temporal registration. We apply the packing principle, not claim a new general coding theorem.
- Haim J. Wolfson and Isidore Rigoutsos, *Geometric Hashing: An Overview*, IEEE Computational Science & Engineering 4(4), 10–21 (1997), [DOI](https://doi.org/10.1109/99.641604), [author-uploaded text](https://www.researchgate.net/publication/3344381_Geometric_Hashing_An_Overview). Inspected printed pp.10–13 introductory/Underlying ideas passages in HTML-rendered text, not the page images or complete paper. Their shape indexing under partial visibility and pose transformations motivates the temporal-constellation analogy; their discussion of noise and nonuniform invariant occupancy is a caution against treating every ratio as equally useful.
- David Meredith, *Geometric Representations for Transformed Pattern Matching in Music*, [arXiv:2610.08236](https://arxiv.org/abs/2610.08236), 2026-10-06. Abstract only; attempted HTML full-text retrieval failed. Post frozen cutoff, exploratory discovery only. The source explicitly treats augmentation/diminution as time scaling of musical point sets. No claim that the present proof is absent from its full text.
- Peter Desain and Henkjan Honing, *The Formation of Rhythmic Categories and Metric Priming*, Perception 32(3), 341–365 (2003), [DOI](https://doi.org/10.1068/p3370). Publisher abstract only, full text restricted at access. Reports categorical rhythm perception and effects of preceding meter. Contrary constraint: a human receiver may not use a homogeneous timing space or lack contextual metrical anchors. Do not substitute our bounded error model for their data.
- Jeffrey R. Chasnov, *Mathematical Biology*, §2.2, [The Golden Ratio](https://math.libretexts.org/Bookshelves/Applied_Mathematics/Mathematical_Biology_(Chasnov)/02:_Age-structured_Populations/2.02:_The_Golden_Ratio), educational source; inspected continued-fraction/Fibonacci passage. The irrationality and Fibonacci connection are established mathematics, not evidence for auditory significance.

Access and reading occurred on 2026-11-25 by the same ChatGPT agent; no external reader, participant, priority search or source-byte archive. Only original paraphrase and mathematical derivations committed. Source metadata and coverage are exploratory, not admitted frozen-corpus records. No scientific validation or rights grant implied.

Interpretation: the unknown start and tempo act as two discarded coordinate degrees of freedom. An onset constellation can retain its identity while losing information about its own damaged part. A machine reporting receipt of a motif should separate message identification from fault localization. The geometric-hashing analogy is one-dimensional partial recognition, not proof of human parsing. Proposed experiment: compare anchored versus unanchored delivery of motifs with equivalent message separation but differing self-deletion fingerprint diversity; hold timbre and duration range fixed, test machine decoder first, and only later assess real listener performance under approved protocol. Reject the perceptual hypothesis if contextual/metrical cues dominate the predicted geometric effect. No production integration is authorized.

An arbitrary global tempo range that approaches zero invalidates positive jitter guarantees. A finite grid, hard playback duration bounds, non-affine time warp, overlapping or merged physical pulses, pitch cues, unknown packet segmentation, and uncertain event-count semantics require new analyses. The present results do not solve those cases. For safety-relevant communication a mathematically ambiguous motif must not silently turn into an invented missing-onset label; retain the compatible candidates, then ask for a distinguishing anchor or use another qualified modality.

## Original fiction: The four knocks

An apprentice took four knocks from the wall and placed them on a strip of paper. The first gap and the last were the same; the middle gap was shorter. A visitor removed one knock while the apprentice was looking away. When the three remaining knocks were stretched to the length of the old strip, their proportions named the rhythm but not the absent stroke.

The apprentice wrote two answers in the ledger. One was the name of the rhythm. The other was a pair of possible places where the silence had entered.

The master did not correct the second answer. He put a clock beside the wall.
