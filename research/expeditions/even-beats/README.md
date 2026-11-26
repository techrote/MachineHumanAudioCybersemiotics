# The Bell That Wins on Even Beats

Refs #698 · 26 November 2026 · additive mathematical exploration, not canonical Track E/G evidence. One ChatGPT agent: proof development, source inspection, exact BigInt and native Fraction cross-checks. No human data, external critique, or priority claim.

## Abstract

A communication instrument need not be the best at every repetition horizon even if it is eventually best for all Bayesian decisions. We derive the exact two-read Blackwell criterion for a variable-reliability ternary symmetric channel versus a binary symmetric channel; construct a rational positive pair whose dominance horizon set is precisely {2,4,5,6,...}; and exhibit positive rational pairs with every even horizon certified but an arbitrarily long finite sequence of odd horizons failing. An independent tagged mixture of the same two experiments can make the one-shot instruments comparable. Unexpectedly a strictly more informative common side experiment can undo this comparison. We prove a general obstruction for sufficiently strong binary symmetric side evidence and identify a passage-local issue in the inspected preprint of Mu et al. The known two-versus-three reversal and catalyst existence are prior art, not claimed here as discoveries.

## Model and exact two-read criterion

One persistent state X is + or -, all reads independent conditional on X. A(a,r) emits +,0,- with row probabilities (r(1+a)/2,1-r,r(1-a)/2) in state +, and the reflected row in state -. Here 0<a,r<1. The neutral symbol is flagged; its probability is state-independent. B(b) emits +,- with correct probability (1+b)/2, 0<b<1. All conditional probabilities are positive. These are probability tables, not measured physical channels.

For a finite binary experiment E write the uniform-prior posterior contrast t=(P_+(y)-P_-(y))/(P_+(y)+P_-(y)) and weight w=(P_+(y)+P_-(y))/2. Its law has mean zero. Define C_E(k)=E[(t-k)_+]. A Blackwell-dominates B iff C_A(k)>=C_B(k) for all k, by convex order of posteriors (equivalently the two-action sign criterion of #694). Piecewise-linear calls need only be checked at combined support knots. Reflection symmetry reduces to k>=0. Equivalently compare Bayes accuracy at every prior; for p=(1-k)/2 the accuracy difference equals the call difference. This equivalence is about optimal decision rules, not an arbitrary human or machine classifier.

At one read, A dominates B iff ar>=b; B dominates A iff a<=b (for the interior parameter ranges). Proof: A has posterior atoms -a,0,a with weights r/2,1-r,r/2. B has atoms ±b with equal weights. Evaluate both calls at 0 and their positive support knots.

At two reads, the positive posterior support of A is a and s_a=2a/(1+a²) with respective masses r(1-r) and r²(1+a²)/4; the remaining nonzero atoms are their negatives and the rest is at zero. B has positive atom s_b=2b/(1+b²) with mass (1+b²)/4 and reflection plus zero. This follows by adding the two log likelihood ratios, or multiplying the conditional probabilities literally.

**Theorem.** A² dominates B² iff all of
- a>=b;
- ar(2-r)>=b;
- r²a(1-a²)>=2b-a(1+b²).

Proof: s_a>=s_b is necessary since otherwise B has a strictly more extreme posterior. With this satisfied, C_A-C_B need only be checked on [0,s_b]. At 0 it is [ar(2-r)-b]/2. At s_b it is nonnegative. If a lies inside the interval, its call value is r²a(1-a²)/4 while B's is [2b-a(1+b²)]/4. If a>=s_b the last inequality holds automatically and that knot is outside the interval. There are no other knots in the interior. Outside [0,s_b], B's call vanishes. Reflection completes the proof. All three conditions are non-strict, including equality at a=b. The two-read theorem is exact and requires no limiting estimate.

## An exact horizon semigroup

Use a=9/10, r=7/20, b=1/2. In state +, A's row is [133,260,7]/400; B's row is [3,1]/4. State - reflects them. One-shot A and B are incomparable. The fair-prior accuracy of A is 263/400=0.6575, B is 3/4. A nonetheless has the stronger extreme likelihood ratio (19 vs 3), which prevents B from dominating A at ANY finite horizon n: the maximal likelihood ratio is respectively 19^n vs 3^n, and a state-independent garbling cannot increase the extremal posterior.

The two-read theorem certifies A²>=B²: ar(2-r)=0.51975>b and a>s_b=4/5. The native witness also constructs an exact garbling: in A² keep fraction 2000/2079 of every positive posterior atom and send to B²'s positive atom 4/5; reflect for negative atoms; allocate neutral mass 479/11880 to each sign, and send remaining outputs to zero. It reproduces the entire fair-prior target joint state/posterior table, not merely the classification accuracy. Reinflate target posterior classes by a state-independent random choice if the raw B² sequence is required.

At n=3, fair-prior A accuracy 26504053/32000000 is less than B accuracy 27/32 by 495947/32000000; thus A³ does not dominate. At n=5, all relevant nonnegative call differences are the following exact values:

| k | C_A5(k)-C_B5(k) |
| --- | --- |
| 0 | 58306730629/5120000000000 |
| 1/2 | 62144290651/1280000000000 |
| 9/10 | 5099188523/640000000000 |
| 13/14 | 88720369837/8960000000000 |
| 121/122 | 47444727113/39040000000000 |

Above 121/122, B's call is zero; remaining A knots cannot violate the inequality. Symmetry handles negative k. Hence A⁵>=B⁵ exactly.

The set of successful equal-length horizons is closed under addition: tensor the corresponding state-independent garblings, using the independence contract. This elementary closure also applies to more than two underlying states. Because 2 and 5 generate every positive integer except 1 and 3, the success set of this fixture is exactly {2,4,5,6,...}. It is not an upper interval starting at its first successful horizon. The finite all-prior computation checks both directions for n=1..16; the infinite statement follows from closure, not extrapolation.

This leads to an audit rule: once coprime horizons p,q are qualified, their generated semigroup contains all n>pq-p-q (the two-generator Frobenius number, for p,q>1). This classical number-theoretic fact follows by selecting the unique multiple jq with 0<=j<p matching n modulo p; for n>pq-p-q the remaining multiple of p is nonnegative. For first success at 2 and first odd success at 2h+1, the entire success set is precisely the even positive integers plus all odd integers >=2h+1. This is a horizon certificate, not a probability that a particular observed message is correct.

## Arbitrarily long odd-horizon holes

For any desired integer h>=1 choose integer M>2^(2h+2), and set

    a=1-1/M^4,   b=1-2/M²,   r=1-1/M.

These are strictly interior rational parameters. A has a larger extreme likelihood ratio than B. Since 1-s_b=(1-b)²/(1+b²)>=2/M^4, a>s_b. Further ar(2-r)=(1-M^-4)(1-M^-2)>b. The two-read criterion proves A²>=B², hence every positive even horizon succeeds.

For odd n=2j+1 with 0<=j<=h, compare the fair-prior overlaps O_E=sum_y min(P_+(y),P_-(y))=2(1-accuracy_E). A's all-neutral event alone has overlap M^-n. B's probability of a wrong majority under either state is a binomial upper tail with error q=1/M². Thus

    O_B = 2 sum_(i=j+1)^n binom(n,i) q^i(1-q)^(n-i)
        <= 2^(n+1) M^-(n+1)
        < M^-n <= O_A.

Hence A does not dominate B at any of the odd horizons 1,3,...,2h+1. B never dominates A because its extreme likelihood ratio is smaller. This family proves there is NO universal finite bound on the last failing horizon based only on the fact that horizon two succeeds, even with two states and three versus two strictly positive outputs.

Eventual dominance for each fixed pair follows from the established large-sample theorem of Mu et al., not from our finite enumeration. The pair has distinct extreme log likelihood ratios, and A² strictly dominates B² in Blackwell's sense (not equivalent, due to extremes); strict Rényi ordering for all positive orders follows by strict data processing and additivity, as explained in the source's section 3. Thus its Theorem 1 applies. The odd failures can be arbitrarily delayed across pairs, not infinitely delayed in any fixed pair in this family. The construction approaches nearly revealing channels, and the absolute gaps can be tiny. No claim of a uniform large practical loss.

## Common side evidence: a stronger witness can undo the comparison

This was the unexpected rabbit hole. Let R be the independent experiment which flips a fair, state-independent label A/B and then produces one fresh read from that labeled experiment. The label is part of the output. R can be regarded as five distinct tagged output symbols. All random choices and evidence draws are conditionally independent given X.

A×R is a tagged mixture of A² and A×B. B×R is a tagged mixture of B×A and B². A² dominates B² and A×B is equivalent to B×A by swapping slots. Reorder the tagged components and apply the appropriate garbling. Thus A×R>=B×R although A and B alone are incomparable. This is a small instance of the established catalytic comparison construction (Mu et al., Proposition 4 and appendix Lemma 4); not a priority claim.

Now let S be a single binary symmetric experiment with contrast 9/10, rows [19,1]/20 and its reverse. S dominates R: choose the independent tag, for A retain S with probability 7/20 and otherwise output neutral; for B flip the S symbol with probability 2/9. These exact garblings give the prescribed R table. S is strictly more informative than R (the latter includes neutral and lower-contrast outputs).

Nevertheless A×S DOES NOT dominate B×S. At prior P(+)=1/20, their optimal accuracies are respectively 77197/80000 and 779/800, a shortfall of 703/80000=0.0087875. At fair prior both compound instruments have accuracy 19/20. An apparently stronger common source removes the dominance certificate while keeping the stronger source itself unchanged on the target side.

Here is the more general obstruction. For strictly positive finite E,F define the likelihood-ratio hinge difference

    H(z)=sum_y(P_E+(y)-z P_E-(y))_+
         -sum_y(P_F+(y)-z P_F-(y))_+, z>0.

A negative H(z0) is exactly a loss in Bayesian accuracy at prior 1/(1+z0), after division by 1+z0. For any conditionally independent side experiment R, write L_j=P_R+(j)/P_R-(j), q_j=P_R-(j). Then

    H_(E×R,F×R)(z)=sum_j q_j L_j H(z/L_j).

For a symmetric binary S with likelihood ratios s and 1/s, s>1, take z=s z0. Choose s large enough that s² z0 exceeds the maximum likelihood ratio of either original experiment. The second term vanishes, so the compound hinge difference is s/(1+s) H(z0)<0. At the same time S can be chosen to dominate any prescribed finite strictly positive side experiment R: its posterior support extremes ±(s-1)/(s+1) can enclose R's entire support; the two-point mean-zero law convexly dominates every mean-zero law supported in that interval. This proves that a finite positive catalyst for an otherwise failing comparison is not universally upward-closed in the ordinary Blackwell order. Perfect state revelation is a different limiting case: it makes both compounds equivalent. The prior witnessing the failure moves toward the endpoint as s grows, so no fixed positive lower bound on the operational gap is asserted.

For the explicit fixture H(1)=-37/200, s=19, and s²=361 exceeds the largest original likelihood ratio 19. The resulting H(19)=-703/4000, which after division by 20 gives the stated accuracy gap. Both exact methods reproduce it. The neutral independent tag alone cannot repair a failed comparison; its observation would supply no state information.

**Source-local criticism:** in the inspected arXiv v5, printed p.12, immediately after Proposition 4 in section 3.3, a sentence asserts that replacing a successful common experiment by a more informative one preserves the compound ranking. Taken literally with the same independent side experiment on both sides, the explicit construction above is a counterexample. The proposition's existence equivalence and the large-sample theorem are unaffected. The valid weaker inference is that a more informative side source on the input side can simulate the old target compound with its *weaker* side source; it does not necessarily simulate the compound retaining the stronger side source. The journal version could not be inspected (Caltech repository PDF download failed); no formal erratum search was exhaustive. Record this as a passage-local mathematical concern requiring independent critique, not an allegation about the whole article or a claim of scientific priority.

## Synthetic acoustic experiment and operational interpretation

A one-read exact score inventory encodes 400 episodes per state for each instrument, shuffled deterministically. Left truth carriers 300 and 700 Hz; right report carriers 750,550,350 Hz for A's +,neutral,- and 750,350 for B. Each frame is 320 samples at 8 kHz with Hann taper; stereo PCM16. The neutral is an explicit tone, not a missing or inaudible event. The renderer's count inventory and the read-back templates are exact digital controls. A 32-second file for each instrument contains 800 episodes; all 3,200 state/output symbols across both files decode. These are enumerated inventories, not independent samples of a physical source and not a perceptual trial. The repetition theorems use exact product laws; the one-shot audio scores are illustrative and are not claimed to realize their full joint repetition inventory.

A prospective instrument could alternate two request/receipt policies, expose the number of independent reads rather than replay count, and play an auxiliary context tone with selectable reliability. The composition would explore comparison changes at odd/even horizons and with side evidence. This is a design analogy, not an interface requirement, psychological assertion or safety certificate.

Negative sediment: replay a once-drawn output n times and the entire repeated channel is equivalent to one read, eliminating our horizon success; the product assumption is indispensable (compare #480). If the machine state changes, the common side source is correlated with the primary source beyond the state, errors include unflagged silence, or receiver costs include time/effort, the analysis needs a different model. A larger n can improve each experiment's own value while reversing their relative ranking. No universal scalar or per-symbol confidence is a substitute for the actual joint conditional channel. Direct estimation of those joint tables and task-specific cost is the simpler engineering comparator. No empirical listening advantage or unique explanatory contribution from cybersemiotics has been established.

Fiction: the clerk stamps every second measure with his approval. His apprentice adds a third beat and the approval disappears. Later she brings a stronger witness, and the two instruments again disagree. The certificate was about an ensemble, not about a solitary bell.

## Source ledger, verification, delivery boundary

- Xiaosheng Mu, Luciano Pomatto, Philipp Strack, Omer Tamuz, *From Blackwell Dominance in Large Samples to Rényi Divergences and Back Again*, Econometrica 89(1), 475–506 (2021), DOI https://doi.org/10.3982/ECTA17548 ; publisher abstract and metadata inspected 26 November 2026. Read the arXiv v5 accepted manuscript https://arxiv.org/pdf/1906.02838, printed pp.2,7–8,10,12 (PDF indices 1,6,7,9,11; page images also inspected). Definition 2, Theorem 1, footnote 5, Example 2/Proposition 2, Proposition 4 and immediately following passage. Their Example 2 fixes r=1/2 (from Azrieli); footnote 5 already explicitly gives two-read success and three-read failure. Their main theorem supplies eventual dominance, and their Proposition 4 is prior ancestry for common side information. Azrieli not separately read. The exact two-read variable-r criterion, arbitrary finite odd-horizon construction and stronger-side counterexample are scoped derivations in this report; novelty not exhaustively searched. Caltech repository journal PDF attempt returned HTTP 500 redirect failure; no claim of reading that edition or full preprint.
- Internal ancestry: #694 third-choice report read, including posterior hinge and prior sweep, and #480 repeated-receipt report relevant passages read (truthful subset intersection; different scope, replay control reused). Not independent accepted evidence.
- Reconciliation: main commit 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity, validation, protocol overview and project foundations inspected. 409 branch entries, 100 recent open issues and 100 recent open PR search results reconciled; targeted searches for Blackwell/repetition, erasure/repetition, Bhattacharyya, repeated receipts and catalytic comparison. #694 and #480 issue bodies and empty comments fetched. #695 exact head 5d6cb23f2db176d29ca2d38b994f6396b5cac6be CI run 45832663355 success. #698 created, reread, empty comments. No canonical manifests, other worker branches or accepted study records changed.

Run node laboratory.cjs for exact BigInt multinomial count enumeration and Bayes prior knot comparisons. See [laboratory.cjs](laboratory.cjs) and [execution.json](execution.json): 729 two-read parameter profiles, 10,536 prior-knot comparisons, 135 finite odd failures and 15 two-read certificates in the arbitrary-hole family. Independent-method native witness uses literal ordered products, exact Fraction posterior calls, explicit rational garbling and the PCM renderer. Python 3.13.5 ran twice with identical receipts and WAV hashes. These are same-agent cross-checks, not independent peer review. See [witness.py](witness.py) and [native-execution.json](native-execution.json). The generated WAV files are not committed; original specimens regenerate locally.

Independent critique, full repository validation and promotion remain outstanding. Draft PR for designated integrator. No scientific completion or canonical status changes.
