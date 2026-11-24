# The Histogram That Changed Nobody

**MHAC #252 | 24 November 2026 | exploratory, mathematical and synthetic only**

## Abstract

A software upgrade, auditory interface revision or fictional intervention can leave every outcome histogram exactly unchanged while improving the outcomes of many individual units and worsening those of a minority. Reversing the coupling reverses the majority without moving any marginal statistic. This is not sampling error, nor a change of ordinal scoring rule: it is a failure to identify the joint correspondence. We reconstruct the equal-margin special case of published ordinal-effect bounds and derive a cycle-layer construction for arbitrary nonnegative benefit and harm weights. A compact formula, an explicit integer witness, a finite census and a paired stereo score make the limitation inspectable. No priority, human perceptual result, or canonical MHAC advancement is claimed.

## A three-unit counterexample

Take ordered categories 0, 1, 2 (larger is better). Three fictional test cases each start in a different category. Consider candidate outcomes matched to those same cases:

| Baseline | Identity | Ascending cycle | Descending cycle |
|---:|---:|---:|---:|
| 0 | 0 | 1 | 2 |
| 1 | 1 | 2 | 0 |
| 2 | 2 | 0 | 1 |

All candidate histograms equal (1,1,1). Every marginal statistic, including the mean under *any* fixed numerical encoding, is identical. Yet the three worlds contain (benefit,harm,tie) counts (0,0,3), (2,1,0), (1,2,0). No unit in either cyclic world remains unchanged. The two cyclic worlds have opposite strict majority directions.

Do not infer that the upward cycle is socially preferable: a single severe deterioration may outweigh several improvements. Ordinal comparisons alone do not fix magnitudes. The example also does not establish that real randomized samples have exactly equal population margins; this is a known-margin mathematical model.

## Model and proof

Let h_i be nonnegative integer counts on k ordered categories, N their sum. Assume both condition margins equal h exactly. A compatible coupling M has nonnegative integer entries M_ij, row sums and column sums h_i. Rows are baseline, columns candidate. Define B as the sum above the diagonal, H below, T on the diagonal. For fixed nonnegative weights a,b, let U = aB - bH. All are counts, not rates. Divide by N only for N>0.

**Theorem (equal margins, weighted strict direction).** Sort counts in nonincreasing order s_1,...,s_k. Define k_j = number of h_i >= j. Then the sharp upper bound is

    F(h;a,b) = sum_{j=1}^{max h} max(0, a(k_j-1)-b).

The sharp lower bound is -F(h;b,a). For a>0, put q=floor(1+b/a) and r=b-a*floor(b/a). If q>=k the maximum is zero; otherwise

    F = a*(N - sum_{i=1}^q s_i) - r*s_{q+1}.

For a=0 the maximum is zero. In particular max(B-H)=N-s_1-s_2 (pad missing counts with zero); min is its negative. With uniform positive counts across k>=2 categories the normalized range is [-(1-2/k), +(1-2/k)]. For k=1 both endpoints zero.

**Upper certificate.** View M as a balanced directed multigraph on categories, with M_ij edges from i to j. Every vertex has indegree=outdegree=h_i. A finite balanced graph decomposes into simple directed cycles (including loops): follow unused outgoing edges until a vertex repeats, remove that simple cycle, repeat; balance remains. Every nontrivial cycle of length ell has at least one ascending edge and one descending edge. Hence its weighted value is at most a(ell-1)-b; loops contribute zero.

For a>0 and q<k assign vertex charges zero to the q largest-count vertices, a-r to the next, a to all remaining vertices. Charges are nonnegative. Any simple cycle uses each vertex at most once, so its charge sum is at least a*ell-(aq+r)=a(ell-1)-b. It also bounds zero for loops. Across the cycle decomposition every vertex occurs h_i times. The sum of charges is precisely the displayed sorted-count formula, proving the bound. If q>=k, every nontrivial cycle has nonpositive value and identity attains zero. If a=0 the same conclusion is immediate.

**Attainment.** At layer j, include exactly the categories with h_i>=j. If a(k_j-1)>b, make a cycle passing through the included categories in increasing order and then wrapping from highest to lowest. It has k_j-1 improvements and one harm. Otherwise use one self-loop at each included category. Summing layer matrices gives the prescribed integer row and column margins and achieves the layer formula. Each layer has positive value precisely when its size exceeds 1+b/a. Summing those layer sizes yields the sorted-count formula, since the first q largest counts cover q vertices of every active layer and the next count covers the partially charged vertex. Transpose the maximizing witness with weights swapped for the lower endpoint. No relaxation or fractional rounding required.

This argument also extends to finite nonnegative real masses by using layer *thicknesses* between distinct count levels, or a weighted cycle decomposition. It is not necessary to assume independent outcomes. The implemented oracle restricts to safe integer counts and weights; rational weights can be scaled to integers.

**Published ancestry check.** Lu, Zhang and Ding (2019), Theorem 1, use general unequal margins and an ordered-index minimum of delta terms for gamma=P(benefit)-P(harm). Under equal margins their delta_jm expression simplifies to 1-p_(j-1)-p_(j+m-1): the minimization removes the two largest masses, exactly our a=b=1 result. This is a reconstruction, not a novel claim to that bound. The cycle-layer method for general a,b and the acoustic/qualification transfer are this expedition's derivations; no literature-wide novelty audit has been performed.

## Contrary cases and stratification

* With only two occupied levels, B=H, so equal margins identify zero relative effect. This does not imply no changes: a swap can change everyone.
* If the unit-level monotonicity assumption Y_candidate>=Y_baseline is independently justified, equal margins force identity. Proof: sum category ranks is preserved, and each increment is nonnegative, so every increment is zero. Marginal equality alone cannot justify monotonicity.
* If b >= a(k-1), the maximum weighted utility is zero, regardless of counts. The bound does not say every coupling has zero utility; identity is one admissible maximizer.
* For h=(5,1,1), max(B-H)=1, not the uniform-three-level bound N/3. Concentration matters.
* At a=b=1, separate bounds on B and H cannot simply be combined as though their extremizing couplings were independent. The balanced graph proof enforces joint feasibility.
* Repeated same-unit measurements may identify a realized paired table in deterministic software replay. They do not automatically identify human counterfactual outcomes under intervention, because ordering, learning, carryover, interference and changing circumstances may matter.

**Stratification theorem.** Suppose stable pre-condition stratum labels are retained and each stratum independently has equal margins h^(s). Then the sharp upper bound is sum_s F(h^(s);a,b). The sum is at most F(sum_s h^(s);a,b) because any sum of valid stratum matrices is a valid pooled matrix. It is sharp within the restricted stratum model by combining the stratum extremizers. The analogous lower bound follows by transposition. For strata (1,1,0) and (0,1,1), the pooled max(B-H)=1 but stratified max=0. No assumption that stratification always strictly improves a bound: if strata are identical up to scale, equality holds. If unequal margins within strata, this special formula is inapplicable; use a general transportation method, not the equal-margin shortcut.

## Executable experiment and acoustic witness

Run from this directory:

    node laboratory.js
    node laboratory.js --wav-dir ./generated-audio

The first command enumerates all equal-margin integer tables over all weak compositions of N=0..6 into k=1..5 categories. The search recursively assigns row allocations subject to remaining column capacities; it does not use the cycle theorem to choose feasible tables. It independently obtains min and max weighted values for nine nonnegative integer weight pairs, then checks the sorted formula, transposed lower bound and explicit layer witness. It checks row/column sums. The second command additionally writes six original PCM files; do not commit generated binaries.

Actual execution: the exact function bodies committed in laboratory.js ran in the JavaScript code-mode isolate (not the Node command-line wrapper), with results in execution.json. 791 histograms, 8,680 compatible integer tables, 21,357 bound/witness comparisons, no assertion failures. Of these histograms, 396 admit positive and negative relative direction while retaining equal margins. 11,025 two-stratum/weight combinations passed the pooled-versus-stratified inequality; 2,742 were strict. Four malformed histogram controls were rejected. Census counts weight each ordered histogram once, not each physically labelled population equally. These are bounded verification results, not estimated frequencies.

**The Counterfactual Carillon**: stereo signed 16-bit PCM at 8 kHz, with 20 ms per pair, integer square-wave pitch 200+100*category Hz and fixed silent edges. Left channel encodes baseline; right encodes candidate. The paired score orders baseline category then candidate category (a canonical contingency-table representation, not temporal chronology). The marginal score independently sorts both channels; that alignment is only an artistic encoding of independent histograms, not evidence for actual identity. Three different couplings yield byte-identical marginal WAV arrays and pairwise distinct paired arrays, checked bytewise. FNV-1a fingerprints in execution.json are reproduction aids, not cryptographic provenance. Each 1,964-byte array is an original synthetic construction. No listeners, intelligibility results, acoustic-channel calibration, or psychoacoustic inference.

Design speculation: a modular synth could use transitions as its actual notes, preserving individual pitch trajectories while retaining the same global pitch-class distribution. Opposite directional worlds have identical pitch histograms but different cross-channel pairings. A listener might or might not hear the distinction; only deterministic output inequality has been established.

## Research-to-engineering transfer

For MHAC, the sentence "the new warning interface changed nobody's performance" is stronger than "the new interface has the same distribution of performance." "More people improved than declined" is a third estimand. An auditory summary should not silently promote one to another. This is a candidate semantic contract, not an accepted requirement.

For deterministic software comparison, retain stable test IDs and identical input/state/environment identity, baseline and candidate revision IDs, ordered outcome rubric/version, paired transition counts, missing/unmatchable cases, strata, and any authorized benefit/harm weights. If only equal margins are available, announce the bound instead of an invented paired count. If labels or cases are missing, use a different model; see #250. Avoid interpreting an unpaired scoreboard as an individual regression ledger. For human trials, preserve appropriate privacy and design constraints; no recruitment or real-world application is authorized here.

This differs from #195 (missing joint conjunction of constraints), #220 (forecast pooling), #226 (outcomes responding to policy), #244 (uncertain positional scoring), #250 (missing evaluation labels) and #56 (retraction). Here the marginals and order are fixed, all cases exist, but their cross-condition association is not known. The weighted functional explicitly declares its weights, rather than assuming a scoring-family ambiguity.

## Source ledger, scope and verification limits

* Lu, J., Ding, P., Dasgupta, T. (2018), *Treatment Effects on Ordinal Outcomes: Causal Estimands and Sharp Bounds*, Journal of Educational and Behavioral Statistics 43(5), 540–567, DOI 10.3102/1076998618776435. [Author preprint](https://arxiv.org/abs/1507.01542), accessed 2026-11-24: Introduction, sections 2.1–2.2 and 3.1 (Theorem 2 equation 5 and Corollary 1). Publisher abstract/metadata checked. The authors separate marginal effects and paired potential outcomes and derive sharp bounds. Their equal-margin strict-benefit upper bound reduces to 1-max_i p_i, matching our b=0 case. Not a complete paper or supplement reading.
* Lu, J., Zhang, Y., Ding, P. (2019 online), *Sharp bounds on the relative treatment effect for ordinal outcomes*, DOI 10.1111/biom.13148. [Author preprint](https://arxiv.org/abs/1907.10287), accessed 2026-11-24: section Causal inference with ordinal outcomes, equations 1 and 2, section 2.2 Theorem 1 equation 3, Corollary 1 and Remark 1, section 3.2 introductory covariate discussion. Publisher abstract/metadata checked. They derive sharp general-margin relative-effect bounds; their supplementary proof was not read. Independent equal-margin algebra is above. Their discussion of plausible association assumptions is not taken as a universal constraint.
* Source role: mathematical ancestry and counterpoint only. Original paraphrases and derivations, not copied article content or a literature-wide systematic review. No actual human studies were extracted. No new Track E/G records or protocol amendments, no license selection. One ChatGPT agent performed source reading, derivation, coding and execution; no external or independent human review.

Reconciliation: read AGENTS, RAG, programme, runbook, integrity, validation, protocol and amendment indexes; inspected current issues, open PRs, branch list and recursive main tree. Base 495a98ca12bae467a507031f04931aa4254b1866. Many earlier expeditions are still open; none is treated as accepted scientific upstream. Fresh issue #252 had no comments at creation. This directory is disjoint from the active branches. Preserve frozen protocol, canonical manifests and human gates. Review and exact-head CI remain separate from local evidence.

## Fictional afterword — The Clerk of Identical Shelves

The clerk counted the books before the move and counted them afterwards. Every shelf contained the same number of books as before. He therefore announced that no book had moved.

The apprentice knew that the lightest books had climbed one shelf, the middle books another, and the heaviest had come down to the bottom. She offered to demonstrate. The clerk asked for a second histogram.

Instead she built a small organ with two manuals, one for the old shelf and one for the new. The notes were the same in either hand. Only the pairing differed.

The clerk finally amended his report. Nothing had changed in the counting of the books. This was not, he conceded, a statement about the books.
