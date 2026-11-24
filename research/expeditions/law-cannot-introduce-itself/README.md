# The Law That Cannot Introduce Itself
## Version-blind reconstruction, conditional anonymity, and incompatible privacy objectives

**Refs #298 · 24 November 2026.** Original synthetic mathematical and interpretive expedition, AI-authored. No Track E/G admission, empirical results, acoustic measurements, deployed privacy claim or mathematical priority claim.

## Contents

1. [Archaeological premise](#1-archaeological-premise) — recover the missing-law assumption.
2. [Model and exact version-blind recovery](#2-model-and-exact-version-blind-recovery) — quotient classes and hint cost.
3. [Exact conditional leakage](#3-exact-conditional-leakage-and-the-price-of-suppressing-a-law) — sharp bound and coupling.
4. [Incompatibility even without erasure](#4-an-incompatibility-even-without-erasure) — a Pareto frontier.
5. [Exaptation, negative memo and creative witness](#5-exaptation-negative-memo-and-creative-witness) — a bounded practical falsifier.
6. [Sources, execution and limits](#6-sources-execution-and-limits) — reading and test receipt.

## 1. Archaeological premise

[Draft #291, The Rest That Arrives Too Late](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/6dab50fb3685bbed534f017ca6259a29ac6e9304/research/expeditions/rest-arrives-too-late/README.md), §§2–4, assumes the receiver knows the exact affine source law. It explicitly excludes uncertain laws. Its minimum erasure theorem can be read too optimistically: if the erased coordinates are recoverable given the current law, perhaps the instrument can dispense with both the missing symbols and the law's explicit identity. The present report falsifies that inference.

[Draft #269, The Message That Borrows Its Audience](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/a46f7b2924517a378f6a12151740a430ce202c4a/research/expeditions/message-that-borrows-its-audience/README.md), §§1–2, distinguishes missing context, unknown context loss and incorrect context; it does not price the missing version of a source constraint. The [accepted X005 negative-space protocol](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/sound-of-nothing/NEGATIVE-SPACE-PROTOCOL.md), Receiver rule and Falsifiers, makes an explicit synchronous contract an exception to its caution about silence. Here that contract itself becomes a hidden variable. Acceptance of the X005 artifact is not acceptance as an R012/R013 design requirement.

The new question is whether a decoder can learn which law justifies its reconstruction from the remaining local observations, and whether hiding the addressee conditional on the law is the same as hiding it when laws are pooled. Neither question is answered by #291. The answer to both can be no.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, research integrity, validation, project foundations and the above pinned passages inspected. Separate searches returned 90 open issue titles and 72 open PR titles before #298. The recent ordinal-deletion, intermodulation and correction-allocation work concerns different models. #290 issue and comments inspected (none); #291 remains draft/open, exact head Research integrity completed/success. #269 remains draft/open. No upstream draft is treated as accepted evidence. This is bounded title-level overlap reconciliation plus focused source reading, not substantive review of every branch. The live registry remains in progress.

## 2. Model and exact version-blind recovery

All vectors and matrices here are over GF(2). H has n columns. B is a nonempty set of M distinct feasible syndromes, each in the column space of H. A source law b in B is chosen uniformly, independently of the intended recipient g; then X is uniform over the affine coset Hx=b. The encoder knows b before transmission, and sees actual bits causally. The recipient knows H,B and its own coordinate identity but not the actual b unless an explicit hint is supplied. Its local observation is Y=X_K, the delivered positions of its coordinate. A deterministic public erasure set E is fixed across b and g; K is the complement. At each non-erased tick the encoder emits an even-parity word of G coordinates, with G odd and >=3, and coordinate g exactly X_i. Erasures have explicit markers. The observer sees all emitted words, and in the conditional privacy regime is additionally given b, not X. Privacy here protects g, not the content X or the law b. The decoder is deliberately local: other coordinates, choice of encoder randomness, side channels and adaptive timing are excluded.

Write S=span(H_E), e=|E|, r_E=dim S, f=2^(e-r_E). Two syndromes are equivalent when their XOR belongs to S. Let Q be the number of equivalence classes intersecting B, and L the largest class size.

**Theorem A (fiber counting).** The best probability of correctly reconstructing the *whole* block using only Y and the known family is Q/(Mf). The minimum alphabet of a law-only hint for zero-error reconstruction is L, provided f=1; if f>1, no hint depending only on b can resolve the residual within-law ambiguity.

Proof: a delivered word y is feasible under b exactly when b+H_K y belongs to S. Thus it identifies the quotient b+S and no finer distinction among laws in that class. Every feasible pair (b,y) has f completions, by the kernel dimension of H_E. All source words across B have equal probability because the affine cosets have equal size. Each observation in a class containing m laws has mf equally likely completions, so optimal exact-block success is 1/(mf). The class occurs with probability m/M; summing gives Q/(Mf). No special encoder choice improves local observations, which are exact delivered coordinates by definition.

For a hint h(b), all laws in any one class have the same feasible y set. Their labels must be distinct, otherwise at least two different source blocks remain possible. Labels may be reused in different quotient classes because y already distinguishes those classes. Assign labels by enumerating members within each class; L suffice. In the fixed-length binary representation this costs ceil(log2 L) bits. This is an alphabet bound, not a price for synchronizing, authenticating or hearing a hint. An unequal prior changes the success expression to the sum, over quotient classes, of their largest prior mass divided by f. The hint cardinality for zero error is unchanged if all laws remain possible.

## 3. Exact conditional leakage and the price of suppressing a law

For a fixed known b, let P be the projected affine source coset on K. Its law is uniform. Write D_b for the maximum pairwise total variation distance of full transcript distributions under different g, conditioned on b. Then the sharp minimum is

    D_b* = 0                 if b belongs to S,
           1/(G-1)           otherwise.

Proof: if b belongs to S, P is linear and #291's uniform zero-XOR tuple of rows gives perfect privacy. Otherwise P is a nonzero affine translate of a linear space. If all G rows belonged to P, their XOR would also belong to P because G is odd, and could not be zero. Under the law for actual g, some other row therefore lies outside P with probability one. Summing the probabilities of that event over the G-1 other rows gives at least one. For some h the probability is at least 1/(G-1), whereas under actual h its own row is always in P. Total variation dominates the difference in these event probabilities.

Attainment: choose a sacrificial row j uniformly among the G-1 rows other than g. Assign actual g its delivered source row, independently preselect G-2 uniform fake rows from P and set the sacrificial row to their XOR with the actual row. This last row belongs to the linear translation space P+P, disjoint from P. For any fixed j, the law is uniform on zero-XOR tuples with exactly j outside P and all others in P. It does not depend on which g other than j is actual. Two recipient laws share G-2 equally weighted disjoint components and each has one component unavailable to the other. TV is 1/(G-1). Construction causal: the preselected rows and partner are chosen before delivery, with the XOR computed per tick. No future actual bit is used.

**Consequence:** if conditional anonymity is required for every possible b, then B is a subset of S, hence Q=1. The recipient's complete local observation is statistically independent of the law. Even if H_E has independent columns (f=1), version-blind exact-block success is only 1/M. The law-only hint now needs M labels, or ceil(log2 M) fixed-length bits. If a public version hint is attached, it does not add conditional group leakage: given b its value is deterministic and independent of g. It may, however, alter pooled group leakage or violate a separate confidentiality policy for b itself.

For the special case where B is a linear subspace of dimension d, let j=dim(B intersect S). Then Q=2^(d-j). The best mean conditional leakage C* (uniform law prior, maximum pair average, achievable by the symmetric constructions above) and best version-blind block success A* are

    C* = (1-2^(j-d))/(G-1)
    A* = 2^(-j)/f
    (1-(G-1)C*) A* = 1/(Mf).

To justify the lower bound on maximum pair average (not just the average of worst pairs), average the event bound over all ordered pairs for each b outside S; the ordered-pair average TV is at least 1/(G-1). The maximum pair averaged across b dominates this pair average. The symmetric attaining policies attain the same leakage for every pair, separately at each b. No claim is made that the same mask can attain arbitrary j or f for an arbitrary H.

This produces a structural conflict: moving more version distinctions into the erased span can lower conditional leakage, but can also reduce the receiver's version-blind reconstruction ability. The prior-known-law decoder in #291 is not refuted; its assumption is indispensable. For B equal to the full image of H, the pooled source is uniform on all n-bit words. With no erasures, perfect pooled privacy and exact local reconstruction are possible by the linear coupling. Yet conditional privacy generally fails. The two observer views must not be conflated.

## 4. An incompatibility even without erasure

Take the smallest example: one bit, H=[1], B={0,1}, E empty, G=3. The source bit is its syndrome. Exact local utility is automatic. Let C be the maximum over pairs g,h of the average of their two conditional TVs (equal law prior). Let P0 be the maximum pairwise TV when the observer is not supplied b and sees only the pooled transcript. These are different objective functions.

**Theorem B.** The Pareto frontier is C+P0=1/2 with 1/4 <= C <= 1/2. In particular, minimizing conditional leakage yields C=1/4 but forces P0>=1/4; perfect pooled privacy forces C>=1/2. No encoder simultaneously attains the two individual optima.

Proof: average any encoder over all coordinate permutations, relabelling actual recipients correspondingly. Exact utility and parity are preserved; convexity of total variation and maximum ensures both C and P0 do not increase. Thus any lower bound for the symmetrized encoder holds for the original. A symmetric encoder with b=0 emits 000 with probability a, otherwise the word with ones in the two other rows. With b=1 it emits either word with a one in the actual row and one in an alternative row, equiprobably. For each recipient pair, conditional TVs are 1-a and 1/2. The pooled laws differ only in the masses on two swapped weight-two words, giving

    C=(1-a)/2+1/4,
    P0=abs(1-2a)/4.

For 1/2<=a<=1 this is exactly the Pareto frontier. Smaller a is dominated by a=1/2. The endpoints demonstrate genuine conflict, not merely a bound too weak to identify an optimum.

| Policy | C | P0 |
| --- | ---: | ---: |
| a=1; optimize conditional | 0.25 | 0.25 |
| a=0.75; compromise | 0.375 | 0.125 |
| a=0.5; optimize pooled | 0.5 | 0 |

At a=0.5 every pooled transcript is uniform over the four even words, so g is perfectly hidden from an observer without b. Yet conditional on b=0, the nonzero even word singles out the actual zero coordinate; conditional on b=1, a weight-two word excludes one candidate. No contradiction: the auxiliary observation changes the inference problem. This frontier is a one-bit, three-recipient theorem, not a general curve for arbitrary B or G.

The counterargument is decisive for architecture: choosing a policy by minimizing conditional leakage can actually *increase pooled leakage*. Conditional guarantees imply pooled bounds by convexity, but optimizing a bound does not optimize the actual objective under a different observer view. Likewise a policy with perfect pooled anonymity need not be robust to later release of the law. A test suite must explicitly name what is conditioned on.

## 5. Exaptation, negative memo and creative witness

**Interpretive proposal:** a reconstruction-deadline contract should include a version availability field with explicit provenance; an inference is warranted only if every remaining law yields the same target value by the deadline, or an authenticated hint distinguishes the relevant class. Report the count of competing completions as a diagnostic, not a calibrated human confidence value. The source-law prior used for a Bayes score must not be substituted for zero-error authorization. In a distributed system this could be a schema migration, rollback, feature flag, calibration table or procedural-generation contract. A falsifier can remove the version hint, replay the same delivered local row from two legal laws and demand opposite missing values. If the interface asserts either as uniquely known, it fails. The correct status in that test is UNKNOWN or an explicit conditional alternative.

**Negative design memo:** do not introduce blanket version broadcast or mandatory omission infrastructure solely on this result. A receiver may already know a trusted version; distinct quotient classes may identify it for free; a robust action may be identical across multiple possible reconstructed words; a larger observation space may eliminate ambiguity. Conversely version announcements may expose sensitive information in other threat models, and authentication/timing are not accounted for here. Nonuniform within-law sources, group-dependent version priors, adaptive masks, full-chord decoders, noise and state changes are not covered. The theorem is not a privacy guarantee against an observer who sees X. No human listener is assumed to perform binary elimination.

**Artistic symbolic score:** two source laws, H=[1,1], b=0 or b=1. The first tick is delivered as an even chord; the second tick is a marked rest. The first actual bit is zero. A musician with law 0 interprets the rest as zero; a musician with law 1 interprets the same rest as one. The visible local score is identical. A separate version cue of two distinct pitches can disambiguate the interpretation if both musician and composer share its mapping. This is a score, not a listening experiment or actual audio artifact.

**Fiction:** Two copies of a score are identical except for the rule printed on the missing cover. The conservatory grades the musicians on their interpretation of a rest. The old edition says repeat; the new edition says invert. The conductor declares the rest contains enough information. The musicians ask which edition of enough.

## 6. Sources, execution and limits

Source comparison, AI reading on 24 November 2026: Witsenhausen, 1976, *The zero-error side information problem and chromatic numbers*, IEEE Transactions on Information Theory 22(5), 592–593, [publisher record, Abstract](https://ieeexplore.ieee.org/document/1055607/), DOI 10.1109/TIT.1976.1055607. The abstract explicitly treats zero-error alphabet minimization with decoder side information and distinguishes transmitter access to it from a graph-chromatic problem when access is absent. Our hint confusability classes are disjoint cliques: the sender knows b, and the class is determined by b, so the hint problem is a simple special case, not a new general source-coding theorem. No full-text reading claimed. Shannon, 1949, *Communication Theory of Secrecy Systems*, Bell System Technical Journal 28(4), 656–715, [Bell Labs opening summary](https://www.nokia.com/bell-labs/publications-and-media/publications/communication-theory-of-secrecy-systems/), DOI 10.1002/j.1538-7305.1949.tb00928.x. Read opening summary only: its scope is discrete finite-symbol secrecy systems and their mathematical structure. This is historical context, not proof of our recipient-anonymity model or attribution of any MHAC preference. No novelty priority or comprehensive literature survey claimed. The proofs above are self-contained; external source citations do not substitute for them.

Run from repository root:

    node research/expeditions/law-cannot-introduce-itself/lab.js

Actual precommit execution in V8 enumerated every two-row binary matrix with 1–4 columns, every fixed mask and every nonempty subset of feasible syndromes; compared direct source-word buckets against quotient/fiber formulas and verified the hint construction. Separately generated actual full transcript probability masses for 231 distinct projected affine sets of size <=4, for G=3 and 5. Finally enumerated all six conditional binary probability choices on a quarter-step grid for the three-recipient one-bit case, with no symmetry restriction. All exact integer assertions passed.

| Activity | Count |
| --- | ---: |
| Matrices | 340 |
| Masks | 4,680 |
| Law-family comparisons | 58,620 |
| Hint constructions checked | 58,620 |
| Distinct projected cosets | 231 |
| Recipient-pair TV checks | 3,003 |
| Enumerated transcript draws | 618,420 |
| Asymmetric policy-grid points | 15,625 |

Grid endpoints: minimum C=0.25; minimum C at P0=0 is 0.5; minimum P0 at C=0.25 is 0.25. Counts overlap and are not independent scientific experiments. The lab uses small integer bit masks, is not a scalable decoder, and has no external input. Analytic proofs cover arbitrary finite dimensions under their stated assumptions. One AI authored proofs and checks. No external scholarly review or clean-checkout validation claimed; exact-head CI and substantive review remain pending. Isolated draft scope only, no frozen protocol or canonical records altered.

**Conclusion:** knowledge of a source law is not automatically supplied by the symbols it authorizes. Indeed, an anonymity constraint can remove precisely the observations that would distinguish the applicable law. Privacy evaluated after conditioning on that law and privacy evaluated before conditioning on it can be competing objectives. Preserve that disagreement rather than replacing both with a single unqualified word, privacy.
