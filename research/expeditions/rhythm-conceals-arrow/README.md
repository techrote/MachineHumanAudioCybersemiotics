# The Rhythm That Conceals Its Arrow
## Stationary symbolic irreversibility, sharp reversal distance and entropy-matched grammars

**MHAC expedition #340 · 24 November 2026 · AI-assisted formal exploration, not Track E/G evidence.**

**Scope:** a symbolic stochastic process can possess a statistical time arrow even when every short word looks like independent fair noise, every block entropy agrees with a reversible comparator, and a particular rendered recording has the same global power spectrum as its retrograde. These are three distinct statements, not a claim about a listener's perception or physical entropy production.

## Contents

1. **The anomaly** — a direction hidden in a vocabulary of two sounds.
2. **Stationarity and four-word sharpness** — exact bound and periodic witnesses.
3. **An arbitrarily delayed arrow** — characterize all uniform-block binary Markov laws.
4. **The entropy-matched grammars** — identical probability spectra with different reversal laws.
5. **The spectral mirror** — reproducible exact PCM experiment.
6. **Interpretation and refusal** — proposed diagnostic and artistic transfer, countercases.
7. **Source ledger and execution** — reading limits, receipts and ownership.
8. **Afterword** — an explicitly fictional short score.

## 1. The anomaly

Imagine an archivist with access to every possible word in an acoustic alphabet, the frequencies of all words up to a chosen length, and a plot of entropy versus word length. He is asked whether the machine has a direction-dependent grammar. The first two questions to ask are *what has been retained about word identity?* and *how long a context was admitted?* In a stationary sequence, a persistent direction is not the same thing as a changing mean.

The question overlaps but is not identical to X006 (#188, merged #190): X006 demonstrates that formal symmetry does not certify restoration of a hidden world state. Here there are no action transformers or restoration semantics; the asymmetry belongs to the probability law of the observable symbols. #260 addresses feasibility of physical chronologies; #302 explores novelty exhaustion in graph trails; here we retain a single stationary process and test its forward and backward block distributions.

Arola-Fernández and Lacasa [S1] establish a known no-go for short binary words and caution that symbolization may hide irreversibility. They explicitly exhibit a four-letter asymmetry in a string containing repetitions of 001011 (preprint p.5). The witness below therefore has direct published ancestry; no discovery priority is claimed. Our additions are sharp TV bounds, the uniform-block family, an entropy frontier, a matched spectrum construction, and a mechanically reproducible sound illustration. These are independently derived here, not represented as new-to-literature theorems.

## 2. Stationarity and four-word sharpness

Let P_L(w) denote the stationary probability of a contiguous length-L binary word, and Rw its reversal. Define D_L = (1/2) sum_w |P_L(w)-P_L(Rw)|. This is total variation, not relative entropy. Under equally probable forward/reverse hypotheses, the best one-block classification success is (1+D_L)/2: choose the larger probability at each word and sum half the maxima. Stationarity gives both prefix and suffix consistency: sum_b P_{L+1}(wb) = sum_b P_{L+1}(bw) = P_L(w).

**Known short-word no-go, reconstructed for exact stationary laws.** For L=2 use stationarity at 0 to get P(01)=P(10). For L=3 use stationarity at 00 and 11 to get P(001)=P(100), P(011)=P(110); the remaining words are palindromes. Hence D_1=D_2=D_3=0 for every stationary binary process. This does not assert that arbitrary finite open-ended traces have equal counts; boundaries can break them.

**Sharp four-word theorem.** Abbreviate p_w=P_4(w), delta=p_0010-p_0100. The conservation equations at triples 000 and 111 imply p_0001=p_1000 and p_0111=p_1110. At 010 and 101 they give respectively p_0101-p_1010=delta and p_1011-p_1101=delta. Subtract the equations at 001 and 100, using p_0001=p_1000, to get p_1100-p_0011=delta. The six nonpalindromic reversal pairs are exhausted. Thus D_4=4|delta|; a single signed coordinate specifies all four asymmetries.

By replacing the law with its reverse if needed suppose delta>=0. Four distinct words 0010,0101,1100,1011 have mass at least delta each. Conservation at 001 gives p_0001+p_1001=p_0010+p_0011>=delta. Conservation at 011 gives p_0110+p_0111=p_0011+p_1011>=delta. These last two pairs are disjoint from one another and the four preceding words. Thus 1>=6delta, and D_4<=2/3.

Equality: choose a uniform random phase of the period 001011. Its six cyclic four-words are 0010,0101,1011,0110,1100,1001; only the two palindromes overlap with the reversed support. All phases have weight 1/6. D_4=2/3 and equal-prior one-block classification success is 5/6, compared with 1/2 for any of the shorter block lengths.

**Finite-period refinement.** For a circular binary word of length N (not necessarily its fundamental period), N delta is an integer; the upper bound becomes 4 floor(N/6)/N. For N>=6 write N=6r+j, 0<=j<6. Repeat 001011 r times and insert j additional zeros at the beginning of its first length-two zero run. There are exactly r occurrences of 0010, one at the end of each long zero run, and no occurrences of 0100: every isolated one preceded by zero is followed by a single zero and then a one. The inserted zeros do not change those counts. Thus the bound is attained. For N<6 the bound is zero. The census checks all circular words through N=12 and these constructive witnesses through N=200. No assertion about sample size or statistical power in measured data follows.

## 3. An arbitrarily delayed arrow

Fix k>=1 and assume all length-k blocks have equal stationary probability 2^-k. Consider order-k binary Markov grammars: a context is a u where a is one bit and u a binary word of length k-1, and the next bit is b. The complete family compatible with uniform k-block probabilities is

    P(b | a u) = theta_u       if b=a
                 1-theta_u     otherwise,

with 0<=theta_u<=1 independently for every u. Necessity: for fixed u the 2-by-2 transition probabilities, indexed by a,b, have row sums one by normalization and column sums one by stationarity with the uniform distribution. A 2-by-2 doubly stochastic matrix has equal diagonal entries and equal off-diagonal entries. Sufficiency: direct column sums preserve the uniform k-block law on the shift-register states. If all theta are strictly between zero and one, every shift-register edge exists; any state reaches any other by appending its target k bits, and the all-zero state has a self-loop. The chain is then irreducible and aperiodic. Endpoint parameters still define stationary laws when initialized uniformly, though ergodicity is not guaranteed.

Under symbol reversal, a u b becomes b R(u) a. The reversed conditional transition rule is theta^R_u=theta_R(u) because the uniform initial block cancels in Bayes' rule. Hence a grammar is reversible iff theta_u=theta_R(u) for every u (the transition law and initial stationary distribution then agree for every block). All D_L vanish for L<=k, and

    D_{k+1} = 2^{-(k-1)} sum_u |theta_u-theta_R(u)|.

To see the factor: each u contributes four words whose absolute differences are each 2^-k |theta_u-theta_R(u)|. Multiply by 1/2.

Let alpha_k=1-2^{-floor((k-1)/2)}. This is the fraction of nonpalindromic contexts: a palindrome is determined by its first ceil((k-1)/2) bits. Each nonpalindromic context contributes at most one to the normalized sum, and each palindrome contributes zero. Thus the sharp maximum is alpha_k. Attain it by setting one member of every reversal pair to 1 and the other to 0. If theta is restricted to [epsilon,1-epsilon], 0<=epsilon<=1/2, the sharp maximum is (1-2epsilon)alpha_k, with the same pairing construction at the two endpoints. For k>=3 and 0<epsilon<1/2 this supplies a stationary, full-support, mixing process whose first distinguishable contiguous block length is k+1, with a controllable positive reversal distance.

This formula is specific to the uniform k-block model. At k=3 it gives 1/2 rather than the unrestricted 2/3. The stronger bound is the price of retaining an exactly uniform short-word distribution, not a contradiction.

**Entropy frontier.** Write h_2(p) for binary Shannon entropy in bits. Entropy rate H is the mean of h_2(theta_u) over contexts. For alpha_k>0 and a specified d=D_{k+1},

    H <= (1-alpha_k)+alpha_k h_2((1+d/alpha_k)/2).

Proof: take a reversal pair with x>=y and difference t=x-y. Concavity and symmetry give (h_2(x)+h_2(y))/2 <= h_2((x+1-y)/2)=h_2((1+t)/2). Average this concave function over nonpalindromic pairs; their average difference is d/alpha_k. Palindromic contexts contribute at most one bit each. Equality for all 0<=d<=alpha_k follows by using the same contrast d/alpha_k in all nonpalindromic pairs, centered on 1/2, and theta=1/2 on palindromes. With the epsilon restriction, the feasible d range contracts but the equality construction still fits. For k<=2 all contexts are palindromic, so d=0 and H<=1. High entropy constrains the size of the first-block arrow, but a nonmaximal scalar entropy alone does not identify whether it exists.

## 4. The entropy-matched grammars

Choose 1/2<p<1, k>=3. Construct A by setting theta=p in every context. Construct B by setting theta=p for u<=R(u) in lexicographic order and theta=1-p otherwise. Both have full support. A is reversible, B attains the maximum d=alpha_k(2p-1) under the stipulated interval [1-p,p].

Every conditional state in both grammars has two possible next bits, one with probability p and one with probability 1-p. For any initial k-word, specifying a sequence of "high-probability" and "low-probability" transition choices specifies exactly one longer word. Conversely, any longer word determines those choices. For L=k+j the word-probability multiset is therefore exactly

    2^-k p^i (1-p)^(j-i), with multiplicity 2^k binom(j,i), i=0,...,j.

For L<=k both are uniform. Thus the *entire multiset*, not merely its mean entropy, agrees at every length. All symmetric functions of the block probability vector, including Shannon and Rényi entropies, agree. In particular H_L=k+(L-k)h_2(p) for L>=k. No collection of these entropy values, even an exact infinite collection, distinguishes A from B. This is stronger than noting that a distribution and its reversal have the same entropy: here one law is reversible and the other is not.

For the full-support order-k chain define K_L = KL(P_L || P_L^R) in bits. The block law factors into a uniform initial k-word times L-k transitions. The reverse has the same initial k-law and reversed theta. Stationarity makes the expected log likelihood ratio of each transition identical, so K_L=(L-k)K_{k+1} for L>=k; K_L=0 below k. The rate for B equals

    alpha_k(2p-1) log2(p/(1-p)),

since each nonpalindromic context compares Bernoulli probabilities p and 1-p, while palindromic contexts contribute zero. A has rate zero. This is a direct derivation using our order convention (k previous symbols); see [S2] for the established block-divergence methodology. It is statistical distinguishability in bits, not joules or thermodynamic entropy production. No physical implementation with local detailed balance is specified.

Example with p=3/4:

| k | First arrow length | D at first arrow | K rate (bits/step, approx.) | A and B entropy rate |
|---:|---:|---:|---:|---:|
| 3 | 4 | 1/4 | 0.396241 | 0.811278 |
| 4 | 5 | 1/4 | 0.396241 | 0.811278 |
| 5 | 6 | 3/8 | 0.594361 | 0.811278 |
| 6 | 7 | 3/8 | 0.594361 | 0.811278 |
| 7 | 8 | 7/16 | 0.693421 | 0.811278 |

A possible machine grammar can appear perfectly fair to every short-word auditor and have every entropy summary agree with a reversible grammar. The information resides in the *assignment* of probabilities to named words and their reversed partners, not in the unlabelled set of probabilities.

## 5. The spectral mirror

A separate deterministic signal experiment translates the six-period witness into two sounds, 0 and 1, using original symmetric 320-sample integer pulses at 8 kHz. The forward word 001011 and retrograde 110100 render to distinct signed 16-bit mono PCM arrays that are exact sample reversals. For a real finite sequence x of length N and y[n]=x[N-1-n],

    Y(omega) = exp(-i omega (N-1)) conjugate(X(omega)).

Therefore |Y|=|X| at every frequency, including any common zero-padded DFT. The aperiodic autocorrelation r(lag)=sum_n x[n]x[n+lag] is likewise invariant by reversing the summation order. This is exact, not a claim of numerical similarity. The script calculates and compares all 1920 nonnegative-lag values using integer arithmetic; it also verifies the symbolic circular block counts up to length three and their difference at length four. The same spectrum theorem holds for any real sequence and its literal sample reversal; symmetry of the local pulses ensures that *token* retrograde in this construction is literal sample reversal.

The broader relation between phase, magnitude and signal representation is established in Oppenheim and Lim [S3]; our small rendering is not a replication of their speech or image experiments. It deliberately tests a global magnitude-only representation, not an STFT sequence retaining time labels. A time-resolved spectrum may show the order.

Reproduce (from this directory):

    python3 laboratory.py --out build
    cmp execution.json build/execution.json

The two WAVs are 3884 bytes each, 1920 frames, with distinct SHA-256 digests retained in [execution.json](execution.json). They are original 0.24-second demonstrations, not recordings of people. No listening or intelligibility experiment was undertaken. The generation command writes WAVs locally; binaries are intentionally not committed.

## 6. Interpretation and refusal

**Design hypothesis:** a diagnostic grammar could make the distinction between an action and its reversed ordering legible through asymmetric word relations without modifying the marginal tonal palette. A proposed instrument, the Grammar Mirror, takes k, p and a reversal-pair orientation table as controls. One player varies uncertainty p; another flips orientations of context pairs while preserving all block entropy values. A third player chooses the measurement lens: tone counts, short-word law, global magnitude spectrum (on a paired retrograde recording), or a signed reversal-pair score. This is a proposal, not a validated instrument interface. A software prototype would show the pair table and cumulative log likelihood; an audible score may use an orientation-selective countermelody.

A machine telemetry auditor could preserve labelled word counts, context length, synchronization and boundary policy, and compare reversal partners explicitly rather than certify direction from entropy. A reversal certificate should state the null model, observable, reversal operation, context horizon, sign and magnitude, sample size and estimator uncertainty. It should not call "no significant evidence" a proof of reversibility. The analytic model above is not a statistical hypothesis test for dependent finite samples.

**Contrary cases and limitations.**

- With three symbols, uniform random phase of 012 gives disjoint forward and backward adjacent-pair laws (01,12,20 vs 10,21,02), so D_2=1. Binary short-word impossibility is alphabet-specific.
- Finite open-ended words have unmatched boundary counts. Exact stationary or explicitly circular conventions are essential.
- Block order and sample reversal are different from operational reversibility, causal inference, grammatical human semantics and listener interpretation. None follows here.
- Equal probability spectra do not imply equal labelled laws; equal entropy rates need not even imply equal probability spectra. Our special matched family proves only existence.
- Full-support chains avoid infinite KL from forbidden reverse words; the deterministic six-period witness has infinite KL at length four, even though its TV is only 2/3. TV and KL are different metrics. Our KL function is only called on positive-weight matched laws.
- Uniform k-blocks do not certify independence beyond k. Conversely genuine iid laws are reversible. The k-block restriction is imposed, not discovered empirically.
- Global spectrum equivalence does not ensure acoustic or perceptual equivalence; the WAVs differ. Windowed analyses retaining order, phase-sensitive analyses, external timestamps or learned grammatical structure may break a chosen ambiguity.
- The sources establish links between statistical time asymmetry and physical entropy production under explicit physical assumptions. No measured dissipation, human validation, safety or universal auditory language claim is made.
- No claim about novelty relative to all literature. An independent mathematical reviewer should try to find a stronger overlap with stationary circulation polytopes and entropy-rate extremal problems.

## 7. Source ledger and execution

| ID | Source and actual access | Reading extent and role |
|---|---|---|
| S1 | L. Arola-Fernández, L. Lacasa, *Irreversibility of symbolic time series: a cautionary tale*, Phys. Rev. E 108, 014201 (2023), [DOI](https://doi.org/10.1103/PhysRevE.108.014201), [author preprint](https://arxiv.org/pdf/2303.11868) | Publisher abstract and preprint v1 §§I, III.A–C (printed pp.4–5, PDF indices 3–4), page images checked. Known short-word no-go, four-word example, larger alphabet and finite sample cautions. No full-paper or priority review asserted. |
| S2 | É. Roldán, J. M. R. Parrondo, *Entropy production and Kullback-Leibler divergence between stationary trajectories of discrete systems* (2012), [arXiv:1201.5613](https://arxiv.org/abs/1201.5613), [PDF](https://arxiv.org/pdf/1201.5613) | Preprint §§II.A–B, II.D and IV.A, Eqs.1–3,13–15,28–29; printed pp.2,4,6, images pp.2 and 6 checked. Established relative entropy methodology and physical qualification. Own factorization proof above rather than assuming an order-index convention. |
| S3 | A. V. Oppenheim, J. S. Lim, *The Importance of Phase in Signals*, Proc. IEEE 69(5), 529–541 (1981), [DOI](https://doi.org/10.1109/PROC.1981.12022), [MIT-hosted PDF](https://dsp-group.mit.edu/wp-content/uploads/2024/11/ImportancePhaseSignals_1981.pdf) | Abstract and §I, printed p.529 (PDF image index 0 checked); beginning of §II text, Eqs.1–2. General magnitude/phase distinction; no reuse of images or experimental stimuli. |

All readings were performed by one ChatGPT/GPT-6.2 agent on 2026-11-24. Public source URLs and original derivations only; no restricted copies retained. No independent agent or human review, new empirical extraction or protocol amendment.

**Run receipt:** Python 3.13.5 standard-library CLI executed twice (initial run and final run after adding the exact-period checks); the latter yielded the committed JSON. All assertions passed: 8,190 circular words, 195 further constructive period checks, 13,308 transition-table instances, 63,478 word weights per arm over five entropy-matched configurations, and 1,920 integer autocorrelation lags. Counts are test instances, not independent empirical observations. The floating-point entropy and KL checks use explicit tolerances; word weights, TV, cycle counts, PCM and autocorrelation are exact integers or rational fractions.

**Reconciliation:** live main 495a98ca12bae467a507031f04931aa4254b1866; read AGENTS, RAG, programme, runbook, integrity and validation; checked recent issue/PR listings and branch inventory, searched overlap for reversal and entropy; examined #188 comments and its actual accepted README; prior draft #333 remains outside this work (its exact-head workflow 45397135793 succeeded). Other recent issues #334/#336/#338 have separate scopes. No other branch or shared canonical path changed. This issue #340 and branch mhac-340/rhythm-conceals-arrow own only this directory. Draft PR pending independent mathematical review and exact-head structural checks. No production or corpus stage advanced.

## 8. Afterword (fiction)

*At the Conservatory of Clocks, the two ensembles were given the same scales, identical measures of uncertainty and precisely the same number of possible phrases. One orchestra rehearsed the order in which a phrase might become its opposite. The other rehearsed a law that had no preference.*

*Their bursar issued two identical reports. Their accountant issued an infinite series of identical reports.*

*The apprentice did not ask how many phrases there were. She asked which phrase each number belonged to.*

Original text score: two performers repeat the six-slot motif in opposite directions; the third announces only the common autocorrelation until the fourth slot. Then name one directed word and its reverse. Stop on the first unequal count. This is a proposed artistic instruction, not an observed audience response.
