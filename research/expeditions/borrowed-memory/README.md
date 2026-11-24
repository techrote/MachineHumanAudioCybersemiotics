# The Clock That Borrows a Memory

**Refs #240 — synthetic mathematical expedition, 2026-11-24.** AI-assisted original exposition, implementation and self-check; no independent human review. Neither Track E nor Track G evidence, no change to programme acceptance. This work extends the owner's expressly open exploratory lane.

## Question and boundaries

An instrument exposes a binary state signal rather than its internal Markov state. Is the stationary transition matrix estimated from adjacent observed symbols a valid predictive replacement for the original process? We distinguish three questions: equality of every two-time joint distribution; equality of every finite word probability for the specified initial law; and equality of the outgoing block transition probabilities for all underlying states within a block (strong lumpability). The second implies the first, and the third implies the second, but the converses need conditions. All probabilities below are exact stipulated mathematical probabilities, not estimates from human or machine behavior.

Related prior expeditions #199, #218 and #205 address spectral descriptor collisions, simultaneous marginal disclosure and nondeterministic trace sets respectively. Here the key object is the stochastic projected process and a certificate for temporal probability-law equality; no earlier apparatus is edited.

## Reversible two-step criterion

Let T act on real state functions by conditional expectation of the next state, with strictly positive stationary law pi. The Hilbert inner product is sum_i pi_i f_i g_i. Let P be the orthogonal projection/conditional expectation onto functions constant within observed blocks, and Q=I-P. The one-step stationary macro transition is the restriction of PTP to the block subspace. Its twice-iterated prediction is PTP TP, whereas the true two-step aggregate is PT^2P. Subtraction yields

    PT^2P - (PTP)^2 = PTQTP.

If detailed balance holds, T is self-adjoint. Since Q is an orthogonal projection, the right side is (QTP)* (QTP), positive semidefinite. Thus exact two-step agreement as operators is equivalent to QTP=0, i.e. T maps block-constant functions into themselves. Applying T to block indicator functions yields the usual outgoing-block row-sum criterion for strong lumpability. Conversely that criterion preserves the entire block transition law at every step, for every initial distribution.

For binary observations, it suffices to test the quadratic form on the single nonconstant block indicator, because the constant function is already invariant. The stationary joint probability defect for observing 1 at both times 0 and 2 is exactly the within-block weighted variance of the micro-state one-step probability of observing 1. Hence no cancellation can conceal that variance in the reversible case. This is an elementary derivation under explicit assumptions, not a priority claim. Without detailed balance the product need not be a squared norm, and a zero does not prove strong lumpability. Approximate equality is not exact equality and the result is not a sample-based diagnostic without separate uncertainty analysis.

## Four-state counterexample

Take uniform stationary weights, labels (0,0,1,1), and transition matrix A/2:

    A = [[1,1,0,0],
         [0,1,1,0],
         [1,0,0,1],
         [0,0,1,1]].

This chain is irreducible and aperiodic (strongly connected, self-loops exist), but not reversible. Its two-state surrogate is [[3,1],[1,3]]/4. Let f=(1,1,-1,-1). Direct multiplication gives Tf=(1,0,0,-1), T^2 f=Tf/2, and stationary inner product <f,Tf>=1/2. Consequently for every integer t>=0 the correlation <f,T^t f> equals (1/2)^t, exactly the surrogate value. Both processes have uniform binary marginals, so this fixes all four two-time probabilities at every lag.

Yet the probability of 000 is 1/4 in the original and 9/32 in the surrogate. Conditional on 00, the next 0 has probability 2/3 rather than 3/4. The triple 101 is impossible in the original but has probability 1/32 in the surrogate. This is not a sample collision, nor does the all-lag equality require a finite cutoff assumption. The complete table (numerators over 32):

| Word | Original | Surrogate |
| --- | ---: | ---: |
| 000 | 8 | 9 |
| 001 | 4 | 3 |
| 010 | 2 | 1 |
| 011 | 2 | 3 |
| 100 | 4 | 3 |
| 101 | 0 | 1 |
| 110 | 2 | 3 |
| 111 | 10 | 9 |

A contrary case also matters: a four-state delay line storing (a,b), advancing to (c,a) with fresh fair c and emitting b, is not strongly lumpable but is exactly IID at stationary initialization. Its observed future law can be independent even while the hidden state's outgoing block probabilities differ. The all-word oracle correctly accepts this model against its stationary surrogate.

## Arbitrarily delayed higher-order failure

For integer k>=3, generate independent blocks of length k, each uniformly distributed over the even-parity bit strings. Choose the time origin with uniformly random phase. Every subset of at most k-1 coordinates within a block is independently fair: fixing r<k bits leaves 2^(k-r-1) completions. Conditional on any phase, any collection of at most k-1 distinct time coordinates therefore consists of independent fair bits across the independent blocks. Averaging over phase preserves that same law. In particular, all pairwise distributions at nonzero lags match IID forever.

But a consecutive k-bit all-zero word occurs with probability 2^(-k)(1+1/k), since the observation window aligns with a complete block with probability 1/k, giving twice the IID probability there; in all other cases it crosses independent partial blocks. This proves a shortest distinguishing length of k for each family member. The code realizes the process as a finite chain with phase and sampled block as hidden state. Fixed-length construction is periodic, so we also implement a second family selecting lengths k and k+1 with equal probability at each new block. Its stationary state weights are proportional to block selection probability per codeword. All subsets of fewer than k coordinates are still IID. The aligned length-k probability is now 1/(2k+1), so P(0^k)=2^(-k)(1+1/(2k+1)). This chain is irreducible and aperiodic: every block can lead to every subsequent block, and return paths have lengths whose gcd is gcd(k,k+1)=1 (a return of length k or k+1 for a state in its own block type is possible, and a return via one other type gives sum 2k+1). Thus periodicity is not the explanation.

## Exact certificate machinery

[Core module](memory.mjs) accepts finite binary-labelled stochastic matrices as nonnegative integer rows with common positive denominator and strictly positive integer stationary weights. It rejects nonstationarity; zero-support cases are outside the interface. Construct the stationary coarse surrogate by summing stationary probability flow between blocks and dividing by source-block probability.

For two models of dimensions n and m, all pair-lag discrepancies have the form u B^t v where B is block diagonal with the two transition matrices. The Cayley-Hamilton theorem gives a recurrence of order at most n+m. Checking t=0 through n+m-1 is sufficient for equality at every subsequent lag. This is a finite algebraic certificate, not a claim about finite time-series observations.

For full word equivalence, define emission selection D_b and advance row r by r D_b T. Combine two models into a signed direct-sum initial row, rescale both transition matrices to a common integer denominator, and compare each word row against the all-ones column. Explore reachable prefix rows breadth-first, keeping a rational row-span basis via fraction-free elimination with BigInt. Any dependent row is a linear combination of retained rows, so all future extensions of it are combinations of their extensions. If every retained row has zero sum, the closed reachable subspace annihilates the output functional, proving equality for all words. If a nonzero sum is found, its word is an exact counterexample. Breadth-first order preserves minimum witness length: pruning a dependent prefix replaces it by retained prefixes no longer than it; if an extension distinguishes, at least one replacement extension also distinguishes. There are at most n+m independent rows, hence a distinguishing word if present has length at most n+m-1. This code is deliberately simple exact arithmetic, not a claim of practical polynomial bit complexity or a new equivalence theorem.

[Extension](extension.mjs) includes a second, direct recursive hidden-path enumerator, avoiding the row-advance and span pruning machinery; it checks every word through the finite bound until the first difference for each tested small model. The model probabilities and the finite bound remain shared mathematical assumptions.

## Census and actual qualification

The [first executed receipt](results.synthetic.txt) covers 15,834 symmetric graph/partition configurations (each labelled simple undirected graph of sizes 2-5, diagonal filled to make row sum n, every nontrivial binary partition up to complement). There are 1,086 zero-defect/lumpable configurations and 14,748 positive-defect cases. The scaled variance expression was checked against explicit two-step path sums for every case. This includes disconnected chains with a specified positive uniform stationary law; no claim about random networks follows.

A second census checks all 8,166 nonconstant binary labellings of fixed directed cycles of sizes 2-12, without identifying rotations or complements. The first lag-2 false acceptance occurs at six states, word 101000: lag 3 differs (joint 00 probability 1/3 vs 5/12). There are 12, 16, 36 and 372 such false acceptances at n=6,8,9,12 respectively; no others in the enumerated range. These are exact counts for the stipulated ensemble.

The [second receipt](extension.synthetic.txt) covers 4,144 ordered pairs of permutation matrices averaged with weight 1/2, times nontrivial binary partitions up to complement, for n=2-4. Each full-law result and shortest witness length agrees with the independent path enumerator. Among 4,032 four-state configurations, 672 match the full stationary word law, 144 of these are weak-only, and 96 match every pair-lag law but fail the word law. All 96 have shortest witness length three. The reversible subset in this separate census also passes the strong-lumpability equivalence assertion. The explicit four-state example above is one of these 96, not a claim that 4 is minimal over all stochastic models.

Fixed block lengths 3,4,5 and mixed minimum lengths 3,4 were executed; the exact all-lag certificate passed and the shortest word witness matched the analytic construction in every case. Independent direct enumeration of all shorter words was also performed for the fixed blocks. The V8 execution of the two modules was repeated from fetched GitHub source; both result receipts matched byte-for-byte. A Node entry point [verify.mjs](verify.mjs) is provided; full clean-checkout execution and repository CI are separate gates.

## Acoustic artifact and exaptation

[render.py](render.py) generates a deterministic 16 kHz stereo PCM16 score of the eight three-bit words: left repeats each motif according to its original probability numerator over 32; right according to the surrogate numerator. Each bit is mapped to a triangle-wave note at 250 or 400 Hz; groups align and missing repetitions are silent. Both channels contain 32 motifs in total. This is a probability-mass score, not a simulated time series. The forbidden 101 motif is present only on the surrogate channel. Actual local rendering twice produced byte-identical 161,280-frame WAVs, SHA-256 d8740c6ef251f59ce4f237df9d1f27c60eed457de03b89ee3d4f37e45fe21f7a. The renderer's tested Git blob equals the published blob. No listening test, perceptual equivalence or application reliability claim.

Potential transfers: qualify state reductions in agentic simulations, create stochastic sequencers that share a complete second-order correlation structure yet exhibit different phrase grammars, and generate adversarial models for telemetry pipelines that incorrectly assume a first-order Markov state. The reusable machinery is a certificate generator that distinguishes stationary all-word equality from equality of every two-time statistic. It works on the exact supplied model, not unknown real-world dynamics. For real logs, estimation uncertainty, interventions, nonstationarity and model misspecification need separate treatment. A listener may or may not distinguish the scores.

## Source custody and intellectual debt

- Geiger and Temmel, *Lumpings of Markov chains, entropy rate preservation, and higher-order lumpability*, arXiv:1212.4375 (2012 preprint): [author preprint](https://arxiv.org/abs/1212.4375), inspected abstract, introduction and section 2.2 setting (not the entire paper). Establishes the literature distinction between stationary/weak and all-initial-law strong lumpability; its assumptions include irreducibility and aperiodicity in the stated setting. Our fixed-block and disconnected census models are explicitly broader algebraic examples.
- Gurvits and Ledoux, *Markov property for a function of a Markov chain: A linear algebra approach*, Linear Algebra and its Applications 404 (2005), 85–117, [DOI](https://doi.org/10.1016/j.laa.2005.02.007). Discovery and abstract-level reading via author-hosted index/search excerpt only. This is prior linear-algebraic work on detecting the Markov property. No theorem-level reconstruction from unread passages.
- Tzeng, *A Polynomial-Time Algorithm for the Equivalence of Probabilistic Automata*, SIAM J. Comput. 21(2), 216–227 (1992), [publisher abstract](https://doi.org/10.1137/0221017). Abstract and metadata inspected only. Prior exact automata-equivalence algorithms mean the row-span instrument is an application/implementation, not claimed discovery.
- The parity-block construction uses elementary finite parity independence; the reversible identity uses conditional expectation and detailed balance; the lag certificate uses standard Cayley-Hamilton; all decisive calculations are proved in this report. No priority search sufficient to establish novelty has been conducted.

No third-party text or audio is redistributed. The audio and code are original synthetic artifacts; no new license is selected.

## Reproduce and review

From this directory, run Node 20+ with verify.mjs and Python 3 with render.py --out borrowed-memory.wav. The source files have no package dependencies. Check the two printed receipts and the audio hash above. A wrong stationary law, negative transition, or inconsistent denominator should be rejected. The remaining review items are clean-checkout reproduction, actual exact-head repository CI, scrutiny of the proof and source comparison, and optional human artistic evaluation. The Draft PR is not scientific acceptance. No frozen manifests or central records were touched.
