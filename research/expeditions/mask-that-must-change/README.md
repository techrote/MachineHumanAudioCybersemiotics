# The Mask That Must Change Its Tune
## Why a private sign may have to be random, and why repetition can destroy that privacy

**Refs #266 · 24 November 2026 · exploratory mathematical and interpretive research.** One ChatGPT author, no independent scholarly or human review, no human data, no production privacy guarantee, no new accepted Track E/G evidence. Main observed and rechecked before branch creation: 495a98ca12bae467a507031f04931aa4254b1866.

## Contents

1. Archaeology — recover a concrete contradiction between useful signs and non-disclosure.
2. Model — define contextual admissibility and perfect single-release privacy.
3. Separation — two-group negative control and a sharp three-group stochastic construction.
4. Repetition — exact transcript leakage and a general finite identifiability argument.
5. Exaptation and fiction — a scoped design hypothesis, not a universal prescription.
6. Sources, tests and disposition — bounded reading and actual computational evidence.

## 1. Archaeology: not all ambiguity is a defect

The accepted X004 [quotient guard](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/QUOTIENT-GUARD.md) tests deterministic sufficiency of a declared downstream decision vector. Its valuable principle is that distinctions must earn their complexity, not that every distinction must be retained. It does not model random encoders. Draft [#210](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/210) explicitly supplies a deterministic, context-late, set-valued action model. Draft [#219](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/219) demonstrates joint leakage under equal marginal distributions. Draft [#237](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/237) distinguishes stochastic experiment equivalence from literal reconstruction and exposes the limitations of testing proper state supports. Each is a useful but different object; the present work does not declare any of these drafts accepted.

The seam: can we deliberately preserve precisely enough information for a later decision while withholding a protected distinction from a listener who does not have that decision context? Must a sound have one reproducible mapping from its originating state? A stronger demand is that a sequence of sound events remain private, not merely one. An audible interface is particularly exposed to repetition, replay and audience differences.

Read AGENTS, RAG, programme, runbook, integrity, validation and the quotient guard on main; inspected the three working-branch reports' model and main-result passages, their issue bodies and comments (empty), changed paths, PR metadata and checks. The fetched PR heads 38ec85c218a43474164530c4efa9227ab276872b, 673e1dc9f1ede8c9e6dc919d01eda255f7d21fb8 and 0bd86578cc7dd27ce6ec176ab04c631b8f9e4a7d each had a successful completed PR workflow, but remained drafts. Open-work searches returned 74 issues and 56 PRs in the snapshot, including the latest quantized-decay, correlated-chronology and constitution-of-instrument expeditions. Scope comparison is at title/description level for the other open works, not a complete technical review. R005/R006 and their downstream acceptance gates remain open; nothing here advances them. Issue #266 owns only this directory, based on main; no changes to these other branches or central manifests.

## 2. Exact model: a stochastic cover instead of a partition

Let the state be (g,b), where g in {1,...,G} is a protected group and b in {0,...,m-1} is an equiprobable within-group state. Every group has positive prior probability. Let K(z|g,b) be a finite alphabet stochastic encoder, known to the decoder and observer. The encoder sees the full state but not the later context. Context supports and allowed actions are declared as in #210. Every positive-probability symbol must enable a common acceptable decoder action in every context intersecting its support; zero-error utility means exactly that. The feasible support family is downward closed. Include a within-group context demanding distinct b, so no symbol may cover two states of the same group. The group variable is protected from an observer of z alone, not from a recipient who also knows a context that may reveal it.

Perfect privacy means P(z|g) is identical across g, i.e.

    (1/m) sum_b K(z|g,b) = p_z for every g.

For every used symbol p_z>0, each group must contribute exactly one state b_g(z). Its emission probability there is m p_z. Thus a symbol identifies an admissible transversal w=(b_1,...,b_G); symbols with identical transversals may be merged without changing utility or one-release privacy. Conversely any nonnegative weights p_w summing to one on admissible transversals with every coordinate marginal uniform define a valid channel via K(w|g,b)=m p_w if b=w_g and zero otherwise. Row normalization follows from the marginal condition, and the support admits a decoder by construction. This is a fractional matching / balanced coupling condition, not a partition criterion.

A deterministic private encoder requires m disjoint admissible transversals covering all states. Proof: every used label has p_z=1/m, and every row has exactly one positive label. Conversely such a partition gives an immediate deterministic encoder. For binary b the stochastic criterion is that the cube center belongs to the convex hull of the admissible binary words; the deterministic criterion is that the family contains complementary words. These statements are finite and depend on the explicit within-group distinction obligation and uniform conditionals.

Without the mandatory within-group distinction, a universal common action could make a constant symbol valid; without privacy, simply issuing a separate label per state always works for the stipulated nonempty action sets. Both are useful controls. Neither removes the conflict by redefining it.

## 3. A sharp separation

**Two-group control.** For G=2, admissible transversals are edges of a balanced bipartite graph. If a stochastic solution exists, for any left subset L its incident edge weights sum to |L|/m and are supported on its neighbor set N(L), whose total weight is |N(L)|/m. Hence |N(L)|>=|L|. Hall's theorem yields a perfect matching, which gives a deterministic solution. Randomization buys no feasibility in this equal-size uniform two-group model. It may alter other objectives, e.g. distribution or cardinality under other assumptions, which are not asserted here. For unequal or nonuniform group populations the Hall argument no longer has this form.

**Three-group separation.** Take G=3, m=2. Allow precisely the four even-parity transversals 000, 011, 101, 110. This is realizable in the actual context-late model, not an assumed magical hyperedge: create three contexts each supported on the two states of one group with distinct singleton actions. For every odd word create a context supported on its three states, with the state from group i allowed all of {0,1,2} except i. Every proper subset has a common action; the full triple has none. These seven contexts make precisely the even full transversals legal; all partial transversals are legal. The encoder need not know which of the seven contexts is actual.

Assign mass 1/4 to each even word. At any state two words are compatible, so emit each with probability 1/2. The single-release distribution is uniform over the four labels for every group. In each context all supports satisfy the exact action-intersection rule. No deterministic private encoder exists: the complement of each even word is odd.

The four-label alphabet is minimal. For any G with binary equiprobable states, a balanced distribution on two distinct words requires them to be complementary and equally weighted. A balanced distribution on three distinct words with strictly positive masses must, in every coordinate, split the labels into a singleton and the other two, each side of mass 1/2. The same unique label of mass 1/2 must be isolated in every coordinate (two such labels leave zero mass for the third). The other two words then coincide, contradicting distinctness. Thus without complements, at least four labels are necessary. The four even words' weights are uniquely 1/4: sum-to-one and the three coordinate-marginal equations are an invertible four-by-four system. Duplicate labels cannot reduce the alphabet or the conditional entropy of the merged word; the latter is one bit at each state.

The laboratory finds exactly two stochastic-only families among all 256 subsets of the 3-cube: the even and odd tetrahedra. This is a finite exhaustive census, not a count for larger cubes.

**If forced to be deterministic:** choose the valid partition {000 full transversal}, {remaining states of groups 1 and 2}, {remaining state of group 3}. Each group's label probabilities are 0, 1/2 or 1. Any nonzero pairwise total variation (TV) is at least 1/2, since the signed differences sum to zero and each is an integer multiple of 1/2. Zero maximum TV would imply perfect privacy, already impossible. The displayed partition attains max pairwise TV=1/2, so this is sharp. All 203 partitions of six labeled states are enumerated, 67 context-valid. Stochastic encoding achieves zero instead. This does not say deterministic interfaces are in general worse.

## 4. The mask that changes its tune

Hold the same (g,b) fixed, and issue k conditionally independent draws from the four-word encoder. Each state has two eligible words, and different even words differ in exactly two positions. A nonconstant transcript therefore contains both eligible words and reveals the unique common group/bit coordinate. A constant transcript is equally likely under all groups. The probability of a constant transcript is 2^(1-k), independent of g. For any distinct groups, their transcript laws coincide on constant transcripts and have disjoint nonconstant supports. Thus the sharp pairwise TV is

    TV_k = 1 - 2^(1-k).

For uniform group priors, optimal group classification succeeds with probability 1 - (2/3) 2^(1-k): certainty on nonconstant transcripts and 1/3 on constant ones. These are mathematical distinguishability values, not measurements of listener ability.

This is stronger than a demonstration for one particular encoder. Any finite-alphabet, private, zero-error channel for these contexts can be merged into the four words by the support mapping of Section 2. Their weights are forced to 1/4. With fresh independent draws at the same state the merged transcript has exactly the preceding law. Since deterministic coarsening cannot increase TV (triangle inequality over fibres), the formula is a lower bound for any such original channel and is attained by the four-label channel.

| k | Minimum pairwise transcript TV under those conditions | Group accuracy for the four-label channel |
| ---: | ---: | ---: |
| 1 | 0 | 1/3 |
| 2 | 1/2 | 2/3 |
| 3 | 3/4 | 5/6 |
| 4 | 7/8 | 11/12 |
| 10 | 511/512 | 767/768 |

A cached original draw repeated verbatim instead of fresh independent samples retains the one-release conditional law on the diagonal transcript and hence zero group leakage in this model. This is a different temporal stochastic process, not a stronger universal privacy guarantee; stale reuse after state change may break correctness, and it can reveal other facts such as continuity if those are included as protected variables. Likewise if b is independently resampled uniformly on every release, the original independent emissions have group-independent joint laws; the persistent-state assumption matters.

**General theorem (finite equal-uniform group model).** If a conditionally independent repeat channel with a fixed state satisfies group privacy for m releases, then a deterministic private zero-error channel exists, assuming the within-group distinction and context model in Section 2.

Proof: let r_(g,b) be the row probability vector over the finite alphabet. Conditional on g, the m-transcript law is the equally weighted mixture of m product measures r_(g,b) raised to the m-fold tensor power. If these laws coincide across g, their marginals through all orders j<=m coincide. Choose a real linear functional v separating every distinct row vector in the finite collection (the bad choices lie in a finite union of proper hyperplanes). Contract the order-j tensor with v in every factor: this shows that the power sums sum_b (v·r_(g,b))^j agree for j=1,...,m. Newton's identities determine all m elementary symmetric polynomials from these sums recursively, so the monic polynomial whose roots are these m scalars, with multiplicities, is identical across g. The multisets of scalars are identical. Injectivity of v on the row collection gives identical multisets of row vectors. Within-group distinct states have disjoint supports by the stipulated decoder context; in particular the m rows are distinct. Match the identical rows across groups, then choose one positive-probability symbol per matched row. The support of each chosen symbol is precisely the matched transversal (disjoint supports within each group), so assigning it deterministically is legal. The m choices induce uniform label mass per group. This proves existence. The converse also holds: if the deterministic private partition exists, emitting its fixed label for the same state yields privacy for every k.

For m=2 this can be checked without polynomial identities: equal first and second moments imply the common mean and equal rank-one matrices d_g d_g^T, where d_g is half the difference of the two rows. Thus d_g agrees up to sign, identifying the unordered pair. The parity example proves that one release cannot generally replace two in this theorem. For larger m we give a sufficient bound, not a sharp lower-bound theorem. In particular the grid census's m-1 collision examples need not satisfy the disjoint-support condition; they validate mixture algebra, not zero-error counterexamples. There may be shorter bounds in restricted admissibility families.

These identifiability arguments connect to grouped-sample mixture literature (see Section 6); they do not require learning the exact group from a finite observed transcript. Equality of laws is a mathematical property, not what any specific finite noisy test can certify.

## 5. Exaptation: the temporal disclosure contract

The productive conflict is between meaningful context-late decoding, nondisclosure to a specified audience, and a demand that the encoder choose a stable deterministic sign. In the three-group case one can preserve the first two only by sacrificing the third for the single release; fresh randomness then sacrifices the second over time. Neither maximal transparency nor maximal ambiguity is a universal answer.

A hypothetical test interface can record: state roster and protected variable; group conditional law; feasible decoder contexts and actions; encoder observation access; audience's complete observable view; time coupling (fresh, persistent, cached, reset, state changes); exact objective (zero error or bounded loss); and the declared privacy metric. Reject incomplete contracts as unqualified, not necessarily insecure. The finite model is an appropriate synthetic fixture for detecting an erroneous assumption that validating marginal privacy once validates repeated announcements. It is not a proposed mechanism for safety-critical real alerts. Do not add randomized masking to production audio merely to satisfy a toy proof. Sound discriminability, latency, accessibility, context delivery, distributions and actual privacy risks are separate research problems.

A useful negative memo: **do not make the randomizer a universal layer**. The two-group matching theorem and the repeat-privacy theorem both show circumstances where a deterministic scheme is enough, or is forced to exist if the stronger privacy objective is attainable. Seek counterexamples before extending the architecture. Do not deploy the cached variant as a security recommendation; it only falsifies the inference that repeated output necessarily has fresh independent variation.

### Original fictional afterword: The four bells of the observatory

The observatory had four bells and six rooms. Three different custodians each knew only their own part of the map. Every ring could guide a custodian without announcing which custodian was on duty. The archivist loved the beautiful uniformity of the register and ordered the bell to ring anew every minute.

A visitor who heard only one ring could not name the custodian. A visitor who listened through the afternoon gradually learned the duty roster. The archivist replaced the register's heading: it had said *private announcement*. It now said *private announcement, once*.

This is fiction; no claim about historical bells, real listeners or cultural interpretation follows.

## 6. Sources, execution and disposition

- H. Witsenhausen, 1976, *The zero-error side information problem and chromatic numbers*, IEEE TIT 22(5), 592–593, DOI 10.1109/TIT.1976.1055607, [publisher abstract](https://ieeexplore.ieee.org/document/1055607/). Abstract and metadata read 24 Nov 2026. Established graph coloring equivalence in the specified encoder/decoder information case; no full-text reading or priority claim. Our set-valued contexts and privacy constraints go beyond the abstract's described task.
- B. Rassouli and D. Gundüz, *On Perfect Privacy*, [arXiv:1712.08500](https://arxiv.org/abs/1712.08500), first posted 22 Dec 2017. Abstract, accessible rendering Introduction and opening System model inspected (I and II through equation (1); rendering has alternate title *On Perfect Privacy and Maximal Correlation*). Distinguishes privacy as independence and data observation access; no claim to reproduce the general utility LP. Our zero-error admissibility objective is not their mutual-information objective. Published bibliographic identifier 10.1109/JSAIT.2021.3053432 verified in metadata, published text not separately inspected.
- Hall's theorem: D. Yogesh, [Discrete Mathematics notes §6.1, Theorem 6.2](https://www.isibang.ac.in/~d.yogesh/Course_Notes/DM1/Ch6.S1.html), theorem statement inspected, proof not read. The necessity argument above plus the established theorem supplies the two-group control.
- R. A. Vandermeulen and C. D. Scott, *On The Identifiability of Mixture Models from Grouped Samples*, [arXiv:1502.06644](https://arxiv.org/abs/1502.06644), 2015 first submission; abstract inspected. States the 2m−1 grouped-sample identifiability bound in the general mixture setting and a matching impossibility. Our finite, equally weighted model has extra assumptions; the self-contained power-sum proof gives a sufficient m bound there and a deterministic decoder consequence. Do not claim improvement to the unrestricted literature or priority. No comprehensive novelty search conducted.

All source access is public, source wording not reproduced wholesale. Same AI performed reading, derivations, implementation and self-review.

Execution on 24 Nov 2026: exact bounded integer arithmetic in V8, no libraries or random numerical tolerances. Run from this directory with Node: `node lab.js` and `node moment-check.js`. The source functions themselves were executed in V8 prior to writing; Node wrapper/full repository checks are not yet asserted.

| Check | Actual result |
| --- | --- |
| All 1-, 2-, 3-cube families, exact positive-support Cramer search vs quarter-grid multiset oracle | 276, all agree |
| 3-cube outcomes | 79 infeasible, 175 deterministic, 2 stochastic-only |
| Context construction vs direct parity/block rule | 64 subsets, all agree |
| Six-state partitions | 203, 67 valid, sharp deterministic max pairwise TV=1/2 |
| Balanced bipartite graphs sizes 1–3, Hall subsets vs permutation oracle | 530, 255 matchable, all agree |
| Transcript laws for k=1–10 | 30 pairwise TV checks, 10 classification checks, 30 row normalizations |
| Three-symbol row probability grid, denominator 4, equal mixtures of m=2,3,4 | 120 + 680 + 3060 = 3860 multisets; full m-fold signatures all distinct within each m |
| Shorter m−1 signature counts | 45/120, 670/680, 3060/3060; no general sharpness conclusion |
| Invalid cube inputs | 5 refused |

The exact convex search is bounded to dimension <=4 in code and tested exhaustively through dimension 3. It enumerates positive supports of size <=G+1, which suffices because any feasible convex representation with affinely dependent active columns permits a nonzero null-vector perturbation of weights, eliminating at least one while preserving the center and positivity of remaining weights; repeat. Cramer's rule solves independent row minors and the candidate is checked against all rows. The separate quarter-grid oracle is exhaustive only on its stated grid; it corroborates the finite 3-cube results, not general rational feasibility. Moment-check enumerates ordered transcript numerators by direct products, no numerical root finding; the general theorem rests on the proof above. No performance benchmarking, human perception, acoustic rendering, clinical relevance or normative ethics result is claimed.

**Remaining acceptance:** exact-head repository CI, actual independent substantive review and normal landing only if accepted. Issue remains open; no human gate is represented as satisfied. Falsifiers include an admissible complement pair in the claimed parity family, a valid <4-label private channel, a counterexample to the transcript lower bound under the specified fresh conditional-iid model, or two distinct equally weighted finite row multisets with identical m-fold product mixture laws. Relaxing assumptions is a new problem, not a disproof. Preserve other workers' branches and the live research stage.
