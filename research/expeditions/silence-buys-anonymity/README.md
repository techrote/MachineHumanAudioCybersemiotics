# The Silence That Buys Anonymity
## A sharp cost of concealing the addressee when every complete transcript must disagree

**Refs #282 · 24 November 2026 · bounded mathematical, interpretive and artistic expedition.** AI-authored derivation and software; no participants, empirical estimates, independent scholarly review, accepted Track E/G evidence, mathematical priority claim or operational privacy assurance.

## Contents

1. [Excavation](#1-excavation) — make the conflict between erasure, truth and privacy explicit.
2. [Model and lower bound](#2-model-and-lower-bound) — arbitrary odd group count, finite horizon, unequal policy costs.
3. [Sharp causal witnesses](#3-sharp-causal-witnesses) — exact optimal frontier and negative controls.
4. [What the metrics hide](#4-what-the-metrics-hide) — denominator dilution, conditional privacy, fallback and side information.
5. [Source comparison and design consequences](#5-source-comparison-and-design-consequences) — reject inappropriate transfer of mathematical guarantees.
6. [Execution and disposition](#6-execution-and-disposition) — exact reproducibility and scope.

## 1. Excavation

The accepted [X005 negative-space protocol](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/sound-of-nothing/NEGATIVE-SPACE-PROTOCOL.md), sections Message classes and Receiver rule, separates explicit erasure from resolution. It is a candidate engineering hypothesis, not an accepted R012/R013 design. Draft [#235, Examiner of Silences](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/7d5bdf86/research/expeditions/examiner-of-silences/README.md), sections The conflict and A finite model, identifies the loss displaced by abstention, assuming policy-independent fallback. Draft [#275, Mask That Keeps a Partner](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/d0be377e/research/expeditions/mask-keeps-partner/README.md), §4a, proves a delayed three-group odd-parity privacy obstruction when exact decoding is mandatory. Its §1 notes that omission is not free if every tick must be decoded. This is an unresolved design choice, not an inconsistency in that theorem.

The question is whether a *priced* erasure can remove the obstruction, and how it compares to permitting incorrect delivered symbols. The answer is an exact frontier. It makes the conflict sharper, not weaker: some combinations of all three specifications cannot be achieved. This is not a general recommendation to suppress or falsify messages.

The [X004 atlas](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/495a98ca12bae467a507031f04931aa4254b1866/research/expeditions/intellectual-sediment/README.md), section Why anti-collapse is measured, distinguishes recurring research style from emergent subjectivity. Its anti-collapse motif survives here as a distinction between coverage, correctness and disclosure; however, the theorem also places them in a common constraint, so there is a legitimate *task-specific* scalar budget. Neither insisting on complete separation nor indiscriminate scalarization is defensible.

Base main inspected: 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, research integrity and validation. Live searches returned 82 open issues and 64 open PRs before creation of this issue (title-level scope triage, not full review of every item). Read issue bodies/comments for #218, #234, #274 (no issue comments returned) and corresponding PR metadata/diff or report sections, plus X004 and X005 main artifacts. The nearby #267/#275 topics concern exact per-tick correctness; the present work deliberately relaxes it and introduces erasure and error budgets. The latest open expeditions on reversible preset locality, quotation and consensus stopping debt have different questions. No shared paths are owned here. R005/R006 remain open and the live registry remains in progress. Workflow queries using abbreviated earlier heads returned no runs; this is not evidence of failure or successful exact-head CI. Earlier draft results are premises to inspect, not accepted scientific facts.

## 2. Model and lower bound

Let G>=3 be odd. The protected group g is one of G indices. A source B=(B_1,...,B_L) is uniformly drawn from the binary words of length L>=1 having odd XOR parity, independently of g. At each tick the encoder either emits an even-parity word in {0,1}^G or an explicit erasure E, which has no decoded value. The receiver knows g and reads coordinate g of any emitted word. The outside observer sees the complete ordered transcript, including E at its original tick, but not g or B. The encoder sees g, current and past source bits, and its random choices. The lower bound even permits offline encoders; the attaining policies will be causal.

Let Q_g be the distribution of the observer's transcript under group g. Define the leakage

    delta = max over g,h TV(Q_g,Q_h).

TV is half the L1 difference between two finite laws, equivalently the supremum of their probability difference over events. Let u_g be the expected number of erased ticks and v_g the expected number of wrongly decoded delivered ticks in a block, conditional on g. The objective budgets are mean counts across groups, u=(sum u_g)/G and v=(sum v_g)/G. This is a uniform group weighting for *utility costs*, not a prior needed for worst-pair TV. A wrong delivered tick and erasure are distinct. Count errors against the true stipulated source, not what the encoder asserts.

**Theorem.** Under upper budgets U,V>=0 on u,v respectively, the minimum possible delta is

    delta*(U,V) = max(0, 1-U-G V)/(G-1).

For G even, delta*=0 even at U=V=0. This is a theorem about these finite constraints and this observer. It does not apply to arbitrary codes, source laws, side channels, action semantics or privacy definitions.

**Lower bound.** Write e_g=P_g(at least one erasure), and w_g=P_g(no erasure and at least one wrong delivered tick). Thus e_g<=u_g and w_g<=v_g. Let A_i be the observer-visible event of a full unerased transcript whose XOR in coordinate i is odd. Under Q_i, a correct full transcript must satisfy A_i, so Q_i(A_i)>=1-e_i-w_i.

For any transcript with no erasure, XOR of the emitted even words is even. Since G is odd, it contains at most G-1 ones. For any transcript with an erasure, none of the A_i holds. Consequently

    sum_i Q_g(A_i) <= (G-1)(1-e_g).

For i != g, Q_g(A_i)>=Q_i(A_i)-delta. Summing, retaining the stronger direct bound when i=g, gives

    G - sum_i(e_i+w_i) - (G-1)delta <= (G-1)(1-e_g).

Rearrange and average over g:

    (G-1)delta >= 1 - mean(e_i) - G mean(w_i)
                 >= 1 - u - G v
                 >= 1 - U - G V.

TV is nonnegative. No symmetry, independent policy coins, Markov assumption, equal conditional error counts, or causality restriction was used in the lower bound. The only source property needed for this half is odd parity with probability one for every group. In particular, an asymmetric policy cannot evade the result by concentrating errors or omissions in particular groups under the stated mean budgets. Uniform source prefixes are needed for the simple causal attainment below.

## 3. Sharp causal witnesses

Let M=2^(G-1) be the number of even words. Every proper projection of the uniform odd source is uniform. On ticks 1,...,L-1, emit uniformly among the even words compatible with the current source bit at g. Each prefix is therefore uniform on the M^(L-1) word sequences and its distribution is group-independent. Denote its wordwise XOR by P. The actual last bit is 1 XOR P_g.

Three modes, chosen independently of the source and group before the block, suffice:

| Mode | Final tick | Expected erased ticks | Expected wrong ticks | Max pair TV |
| --- | --- | ---: | ---: | ---: |
| C, correct complete | Choose missing coordinate h uniformly outside g; emit (all-ones XOR unit_h) XOR P | 0 | 0 | 1/(G-1) |
| E, explicit erasure | Emit E | 1 | 0 | 0 |
| W, possibly wrong | Choose h uniformly among all G coordinates; emit (all-ones XOR unit_h) XOR P | 0 | 1/G | 0 |

The target all-ones-except-h is even for odd G; XOR P is also even. In C, the actual coordinate g is not missing, so the last bit is exactly correct. In W, all groups have the same full transcript law, but the last bit is wrong exactly when h=g. No future bits are needed. In E, the common prefix is followed by a group-independent erasure marker. For L=1 the prefix is empty and all constructions remain defined.

For C, the output laws for two different groups share all prefix/missing-coordinate pairs except the one excluded by each respective group. Their equal masses on the shared support cancel, giving TV=1/(G-1). Both E and W have laws common across groups. Consequently, a mixture with probabilities c,e,w (sum 1) has pair TV exactly c/(G-1): the E and W common laws cancel even when C and W supports overlap. Its cost is u=e, v=w/G for each group.

Choose e=min(U,1); w=min(G V,1-e); c=1-e-w. This attains the lower bound for all nonnegative budgets. It also attains the result under per-group upper budgets of the same U,V, because all group costs are equal. No claim is made for arbitrary unequal group-specific budgets. For L=1, all-erasure means issued-message accuracy is undefined.

**Sharp special cases.** With zero errors, perfect privacy requires one expected erased tick per block. In fact the proof with delta=v=0 forces mean(e_i)>=1, so every group must have at least one erasure almost surely. Mode E meets that stronger requirement with exactly one. With zero erasures, perfect privacy requires at least 1/G expected errors per block; mode W meets this with at most one actual error per block. Neither is an ethically interchangeable relaxation: the error case can be a confidently wrong instruction. If truth is nonnegotiable and the erased tick has no lawful fallback, the task may be infeasible.

With G even, the all-ones target is itself even, so choose it deterministically and emit target XOR P: the last bit is correct for every group and the complete transcript law is common. For an even-parity source of any G, target all-zero similarly attains perfect correctness and privacy. If the alphabet includes odd words, the trivial all-coordinate repetition of the source bit also hides group identity with exact utility; the result is not a universal law of communication.

Another erasure witness: omit *any fixed known tick* and emit the other ticks independently and uniformly compatible with the actual bit. Those source bits form a proper projection and hence are jointly uniform. The observed word sequence is common across groups. This may be causal even when the omission comes before the final bit. The error and utility costs of different omitted positions need not be equivalent in an actual application.

## 4. What the metrics hide

For G=3 and L=1000, perfect group privacy can be obtained with zero erroneous delivered ticks and just one explicit erasure in every block. Coverage is 99.9%, with 100% issued accuracy. But at least one bit in *every* block is missing. On the no-erasure alternative, the expected per-tick error rate is 1/(3L)=0.0333...%, while an entire third of blocks have a wrong last bit. The numbers are arithmetic consequences of a fictional source model, not measured rates. Changing the horizon changes the denominator without removing the obstruction.

If the actual receiver knows the odd-parity source law and all other bits are correct, it can reconstruct a missing bit. This does **not** invalidate the theorem: its decoder is fixed to local coordinate decoding or E at each tick. It does challenge the operational interpretation of the erasure cost. A receiver allowed to infer a missing bit after the block, with validated knowledge of the global law, achieves exact *eventual* block recovery under E and perfect group privacy. It cannot necessarily recover an earlier erased bit before the final tick. For an omitted last tick it can recover immediately from the previous bits if it knows the fixed boundary and source constraint. Thus the theorem measures missing explicit local reports, not inherently missing knowledge or irreversible task loss. The same objection applies to W: because the construction never errs before the last tick, a receiver authorized to use the true parity law and that error-location promise can override its final received bit by computing the parity completion. Thus a wrong delivered symbol need not imply a wrong final decision. Without the error-location promise, a detected parity violation does not identify the erroneous position. These qualifications preserve the difference between raw-symbol correctness and task correctness; under the enlarged decoder the original lower-bound premise no longer holds for task error. This is a consequential boundary, not an inconvenience to hide. A legitimate deterministic inference rule can eliminate the fallback cost, while a real world in which the law is uncertain may not support it.

Conditional privacy is also different from transcript privacy. Suppose two groups emit the same word whenever they issue a message, but erase with probabilities 1/4 and 3/4 respectively. The conditional law among issued messages is identical. The complete visible law has TV=1/2. Deleting erased cases from a privacy audit is the analogue of the missing denominator in #235.

Side information changes the result. At L=2, mode E emits one word then erases. If an observer additionally knows B_1=0, the first word is uniform among the even words with coordinate g zero. For G>=3, two distinct groups have half of each such support in common (two independent coordinate constraints on the even-word subspace), so conditional TV=1/2. Unconditional group privacy is not privacy in that augmented view. Nor is the theorem about hiding B itself. If the observer also receives the encoder's mode coin, an auditor must recompute the joint law; in this particular mixture the coin is independent of g and the other two modes are group-private, so TV remains c/(G-1). Extra context may hurt, help, or leave the result unchanged.

The no-error full-coverage mode excludes precisely one group from the observer's posterior under uniform group priors: optimal identification success becomes 1/(G-1) versus 1/G before observation. Small max-pair TV for large G does not establish that no group can be definitively ruled out. A likelihood-ratio or other privacy requirement would require its own proof.

## 5. Source comparison and design consequences

Source inspection by the executing AI on 24 November 2026; this is not a systematic novelty audit or accepted theoretical reconstruction.

- Ran El-Yaniv and Yair Wiener (2010), *On the Foundations of Noise-free Selective Classification*, JMLR 11, 1605–1641, [publisher page](https://www.jmlr.org/beta/papers/v11/el-yaniv10a.html), abstract read. The authors frame rejection as a risk/coverage tradeoff. Our example adds a group-disclosure constraint and distinguishes a missing explicit report from an unhandled task. No classifier learning or human performance theorem is imported.
- Borzoo Rassouli and Deniz Gündüz (2018 preprint), *Optimal Utility-Privacy Trade-off with Total Variation Distance as a Privacy Measure*, [arXiv:1801.02505](https://arxiv.org/abs/1801.02505), abstract, Introduction equations (1)-(2), and System model equations (3) plus following paragraph inspected in public text. The paper's leakage is a prior-weighted average TV between posterior and prior distributions; ours is the maximum TV between group-conditional transcript laws. These are different positive-leakage metrics, although zero has the common independence interpretation when every group has positive prior. Their general optimization uses a different observation model and utility functions. Our special parity construction is a self-contained finite inequality and explicit witness, not an attribution to or claimed improvement on their LP results. No full-paper reading claim.

**Exaptation (unvalidated design hypothesis).** A transcript evaluation contract can record: the intended receiver decoder, local versus eventual decision deadline, whether omissions are observable, expected and worst-block erasure/error counts, missing-case fallback, protected group, observer side information and complete-view privacy metric. Test the local and global decoder separately. In a safety-relevant design require independently justified error/erasure limits rather than converting privacy into permission to lie. If a simpler admissible vocabulary or a reliable inference rule removes the obstruction, prefer testing that before adding a randomizer. A uniformly selected erasure can still coincide with the most urgent bit; the equal-cost model cannot resolve urgency-weighted placement. The proof does not optimize semantic harm, temporal action, or cost of delays.

**Negative recommendation.** Do not certify privacy on emitted messages alone; do not use small per-tick error as a proxy for complete-block correctness; do not claim an absent message is absent knowledge. Do not introduce any deployed masking layer based on this toy experiment.

**Artistic score, not rendered or evaluated:** G=3, three parts, permitted chords are silence-of-all-parts or two-note chords (even word); use a separate unmistakable rest marker E for a missing entire chord. A complete correct score's total parity leaves one part excluded; a score with a deliberately marked absent chord can permit the listener to reconstruct it if the parity rule is known. These are symbolic instructions only, not acoustic perceptibility claims. The all-zero chord and E must not be conflated: one is a complete data word and the other an explicit unavailable value.

**Fiction — The conductor's missing bar.** An archivist commissions a score that identifies no performer but faithfully records every gesture. The composer demonstrates that one bar cannot coexist with the other requirements. The archivist replaces it with a rest and declares the problem solved. A pupil who knows the score's construction recovers the omitted bar. A second pupil, who does not know that rule, performs silence. The archivist's ledger has exactly one missing bar in both cases; the audience has experienced two different pieces. The ledger had measured printing, not understanding.

## 6. Execution and disposition

Run from the repository root:

    node research/expeditions/silence-buys-anonymity/lab.js

Dependency-free JS, exact integer mass arithmetic over bounded fixtures. The same AI authored the proof and both computational formulations. The principal construction enumerates actual uniformly distributed source prefixes, every compatible output prefix, final choices, mode probabilities and group-specific decoding errors. It compares complete transcript maps using exact L1 distance. The second oracle enumerates arbitrary unrelated rational output laws at G=3,L=1, including erasure and all four even words; it computes costs from output coordinates and checks the lower inequality without imposing the attaining policy. It is a distinct enumeration, not independent human review or a general optimization proof.

Actual execution in the V8 isolate before committing the serialized function bodies:

| Test activity | Count |
| --- | ---: |
| Odd-group mixture models (G=3,5,7; listed horizons; denominator 6) | 252 |
| Pairwise sharp frontier comparisons | 2,352 |
| Enumerated prefix rows across constructed group laws | 58,100 |
| Arbitrary triples of group laws, denominators 1–3 | 46,375 |
| Even-group, even-source and conditional-delivery controls | 16 |
| Malformed/bounded-input refusals | 5 |

All assertions passed. Counts describe overlapping computational activities, not independent experiments. The arbitrary-law oracle tests one-tick fixtures only, whereas the proof covers all finite L. The constructor tests symmetric witnesses and validates their cost separately for every group. No Monte Carlo estimates, participants, source bit measurements, acoustic rendering, or production privacy assessment. Full clean-checkout repository tests not executed in this environment; exact-head CI and substantive review remain outstanding. No protocol amendments, central registry changes, or work on another branch.

Remaining acceptance: inspect the complete additive diff, exact-head integrity run, and independent substantive review; address any findings before landing. No human data or external outreach required for this bounded work; it does not satisfy the core programme's scientific gates.
