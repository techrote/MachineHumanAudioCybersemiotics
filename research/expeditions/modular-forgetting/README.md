# The Dial That Cannot Forget by Repetition
**Refs #644 · 26 November 2026 · synthetic mathematics, agent self-review; no human validation or operational security claim.**

## The anomaly

A circular symbol index X in Z_N is incremented by independent random offsets Z_1,...,Z_k. The observer receives only Y=X+sum Z_i mod N. Every offset law is fixed independently of X. The question is whether the final conditional law is identical for every possible X, not whether some selected binary field is hidden or whether a listener can recognize a sound.

Eight symbols provide the first exact example. Three independent fair increments drawn from {0,1} give output offset counts (1,3,3,1,0,0,0,0) among eight equally likely tuples. Three fair increments from {0,1}, {0,2}, {0,4} instead give (1,1,1,1,1,1,1,1). Each stage has the same support size, entropy and equiprobable decision count. Only its placement on the circle changes. The first law has total variation 1/2 from uniform; the second is exactly uniform. This is a final-observation model, not a proposal to conceal real data.

## Fourier certificate and the failure of repetition

Write mu_i for each probability law and F_i(t)=sum_x mu_i(x) exp(2 pi i t x/N). The total increment law is the circular convolution, whose transform is the pointwise product of the F_i. Independence of Y from X for every input (equivalently equality of all conditional rows) holds iff the increment law is invariant under every translation, hence uniform. Fourier inversion makes this equivalent to: **every nonzero frequency must be annihilated by at least one stage**.

For identical stages, F(t)^k vanishes iff F(t) vanishes. Thus no nonuniform law on a finite cyclic group becomes exactly uniform after finitely many identical independent convolutions. This does not deny convergence. Let rho=max_{t != 0}|F(t)|. The Fourier coefficient triangle inequality and Plancherel/Cauchy-Schwarz give

    rho^k/2 <= TV(mu^{*k}, uniform) <= sqrt(N-1)*rho^k/2.

For a fair 0/1 increment, rho=cos(pi/N) for N>=2. The lower bound shows that a fixed error target can require a growing observation horizon as the circle becomes larger. Convergence holds for rho<1, not necessarily for arbitrary stages. Repetition of a deterministic increment is a simple countercontrol.

If any fixed subset of up to e stages may be omitted, while other stages retain their independent stipulated distributions, the exact criterion is that each nonzero frequency be annihilated at least e+1 times. Necessity: remove every annihilator of a frequency if there are at most e. Sufficiency: at least one annihilator survives. This does not cover omission selected after observing draws.

## Prime alphabets: sparse real weights versus rational weights

Let p be an odd prime and h=(p-1)/2. Real probability vectors have conjugate-symmetric Fourier coefficients. Treat each nonzero conjugate pair as a unit of coverage.

Tao's prime cyclic uncertainty inequality (Theorem 1.1) states that a nonzero function and its Fourier transform have combined support size at least p+1. A probability vector supported on s symbols therefore annihilates at most floor((s-1)/2) conjugate pairs. Conversely, ANY stipulated set of t conjugate pairs can be annihilated by a positive probability law supported on exactly 2t+1 points. Map every x to the 2t real sine/cosine features for the selected frequencies. The uniform mean of the features is zero. Starting with the uniform weights, whenever more than 2t+1 positive weights remain, choose a nonzero affine dependence d among their feature points (sum d=0 and sum d*v=0). Subtract the largest feasible positive multiple of d until at least one weight vanishes. This preserves normalization, positivity and the zero feature vector. Iterate. Tao's bound excludes fewer than 2t+1 support points and excludes any extra zeros. This constructive use of the standard Caratheodory argument does not infer positivity from Tao's complex-valued converse.

For a common support cap s between 3 and p, set c=floor((s-1)/2). The exact minimum number of stages resilient to e fixed omissions is

    k_min = ceil((e+1)*h/c).

The lower bound counts the necessary frequency-pair coverages. To attain it, concatenate e+1 copies of the ordered list of all h pairs and split into consecutive blocks of length at most c. Since c<=h, no block repeats a pair. Construct a law for each block as above. For s<=2 no finite bank works on an odd prime. For p=2 the full-support fair bit is required.

**Rational contrast.** If mu has rational coefficients and a nontrivial Fourier zero on Z_p, clear denominators. Its polynomial of degree at most p-1 vanishes at a primitive pth root and must be a scalar multiple of 1+z+...+z^(p-1), the cyclotomic polynomial. Its coefficients are identical: mu was already uniform. Therefore a rational-weight bank on Z_p is exactly uniform iff it includes at least one uniform stage, or at least e+1 uniform stages under fixed omissions. This is true no matter how many nonuniform rational stages are available. In particular, finite rational probability tables with support cap s<p cannot realize the ideal sparse real-weight construction.

Explicit p=5 example: put c0=cos(pi/5), A(x)=(1+cos(2*pi*x/5)/c0)/5, and B(0)=c0/(1+c0), B(2)=B(3)=1/[2(1+c0)], others zero. A is nonnegative with support {0,1,4}, and has Fourier support {0,1,4}. B has support {0,2,3}; its transform vanishes at +/-1, since cos(4*pi/5)=-c0. Their convolution is uniform. Each stage is nonuniform. Both supports have size three. In fact each of the probabilities is irrational where required by the obstruction. This is an exact analytic result; floating-point execution can only approximate it.

## Rational prime-power alphabet: a different sharp resource law

Let N=p^a, stage support cap s, and fixed denominator D (probabilities are nonnegative integer multiples of 1/D). For each stage, an annihilated order j means vanishing at a primitive p^j root, j=1,...,a. Because coefficients are rational, vanishing at one such root annihilates every frequency of that order.

**Order test.** Aggregate integer counts into residues modulo p^j, giving a polynomial R of degree below p^j. It vanishes at a primitive p^j root iff divisible by Phi_{p^j}(z)=sum_{l=0}^{p-1}z^(l*p^(j-1)). This polynomial is irreducible: its shift by 1 is Eisenstein at p (mod p it is a pure power of z and its constant is p). Since the quotient has degree below p^(j-1), divisibility is precisely the condition that counts at residues b+l*p^(j-1) are equal for every b<p^(j-1). In other words, whenever a prefix of the low-order p-adic digits carries positive mass, the next digit is balanced among all p options.

If a stage annihilates t distinct orders, two independent constraints follow:
- Its integer count polynomial is divisible by the product of those t distinct monic cyclotomic factors. The quotient is integral (monic division). Evaluation at 1 gives p^t divides D.
- The tree of low-order digit prefixes has at least p-fold branching at each of those t levels for every occupied parent; it has at least one child at all other levels. Therefore at least p^t occupied complete residues are necessary.

Set c=min(a, floor(log_p s), v_p(D)). Every stage covers at most c orders. If c=0 no finite bank can mix exactly; otherwise the sharp resilient stage count is

    k_min = ceil((e+1)*a/c).

Attainment: assign orders to blocks using the same cyclic repeated-list construction as for prime real weights. For a block J of order indices choose a random offset sum_{j in J} U_j*p^(j-1) with independent uniform p-ary digits U_j. Its support has p^|J| distinct residues, compatible with denominator D, and its Fourier zeros occur at exactly the assigned orders. To check the last fact, a uniform p-digit factor at position j-1 vanishes on a character precisely when that character has order p^j; lower orders give all ones, higher orders give a geometric sum with nontrivial numerator and denominator. Multiplication handles multiple digits. All selected blocks can be sampled independently. Omission resilience follows from the cover condition. No analogous general composite-N support theorem is claimed.

Example: N=256, s=4, D=4, e=1 gives a=8,c=2,k_min=8. Sixteen separate fair bit stages also work, but grouping two digits at a time halves that count. In Z_8, one missing digit in the unrepeated bank leaves TV=1/2 from uniform; duplicating all three digits protects against any one fixed omitted stage.

## Negative controls and precision

1. If the product denominator T of all rational stages is not divisible by N, exact uniformity is impossible even without a support cap. Let r=T mod N. Among ALL laws with integer counts summing to T, the sharp minimum TV is r(N-r)/(NT): moving one count from an overly large entry to an overly small one cannot increase the objective, leaving r ceil(T/N) entries and N-r floor(T/N) entries. This is a universal grid lower bound, not a claim that a constrained convolution attains it. Even when r=0 the cyclotomic or support obstruction can persist.
2. Numerical rounding of the real prime construction does not make the exact theorem implementable. The native experiment rounds A and B to denominator D and convolves integer counts; TV is 0.04 at D=10, 0.0041 at 100, 0.000372 at 1000, 0.00001216 at 10000 and 0.0000057284 at 100000. All are nonzero; monotonicity for arbitrary D is not asserted.
3. Adaptive omission is different: two independent fair bits, with one retained after inspecting both, can yield min(Z1,Z2), whose counts are 3:1. The fixed-omission theorem is not contradicted.
4. Correlated stages break Fourier multiplication. In Z_2, two copies of the SAME fair draw sum to zero, though independent copies would be uniform.
5. If a prefix receipt P=X+sum_{i<=j}Z_i is visible, the final receipt cannot remove what the observer already knows. Given P, the independent suffix and final value provide no further information about X; the joint observation has exactly the information in P under this model. An audience hearing all intermediate acoustic shifts is not the final-only observer. Revealed random seeds are also outside scope.
6. Uniformization is the strongest possible loss of state distinctions. If a target must remain recoverable, or if X has restricted support, a smaller masking task may be appropriate. Do not equate this with a practical privacy/security guarantee, differential privacy or authorized communication.

## Evidence, sources and reproducibility

- Terence Tao, *An uncertainty principle for cyclic groups of prime order*, Mathematical Research Letters 12 (2005), 121–127, DOI https://doi.org/10.4310/MRL.2005.V12.N1.A11. Public author preprint https://arxiv.org/abs/math/0308286, v6 dated 22 July 2004. Read introduction, Theorem 1.1, Lemma 1.2, proof of theorem and subsequent sparse-polynomial consequence; visually inspected PDF pages 2–3 (one-based). The prime support lower bound is directly attributable to this source. The positive upper construction is an elementary convexity argument, not a claimed discovery of Caratheodory's theorem.
- T. Y. Lam and K. H. Leung, *On Vanishing Sums of Roots of Unity*, Journal of Algebra 224 (2000), 91–109, https://doi.org/10.1006/jabr.1999.8089. Publisher abstract read: possible lengths of vanishing sums are nonnegative combinations of prime factors. General theory is established prior art; the prime-power order test and schedule result above are proved separately. Full paper not read.
- A. L. Vyshnevetskiy and E. M. Zhmud, *Random walks on finite groups converging after finite number of steps* (2008), https://admjournal.luguniv.edu.ua/index.php/adm/article/view/814/0 . Publisher abstract read; notably non-Abelian groups can behave differently. The no-finite-repetition result is restricted to cyclic (and by the same scalar argument finite Abelian) groups; no unrestricted finite-group claim.
- MHAC #218, *Secret in the Chord*, working-branch report read through its acoustic model; #410, *Receipt That Protects the Wrong Secret*, working-branch report read. Both issue bodies and empty comment lists retrieved. These concern joint observation and target-specific privacy, not independent cyclic convolution or its stage budget. Their limitations motivate our final-only observer and declared protected variable.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme, runbook, integrity and validation instructions inspected; 382 branch entries paged; first 100 open issue results and 100 open PR results surveyed; targeted searches for additive noise, modular noise, Fourier masking, perfect secrecy and related terms. No matching active scope found. Prior #639 exact-head Actions run 45738870464 completed successfully. Fresh #644 issue body/comments read before branching. No shared files modified.

Run node laboratory.cjs. Same-agent V8 execution examined 29,946 rational count profiles (106,353 order tests), 72 exact digit schedules and 692 exact omission profiles; constructed 366 sparse prime real-weight profiles, 75 real schedules and 1,224 numerical omission profiles. Maximum absolute floating-point residual 6.210310043996969e-16, no assertion failures. Integer convolution uses BigInt, rational order tests use integer residue counts; the real solver uses affine elimination, not an exact algebraic-number engine. The analytic proofs establish the exact result, not a floating-point threshold.

Native companion (local distribution, not an additional committed test): standard-library Python literal tuple enumeration returned 258 digit checks, explicit five-symbol real construction residual 5.55e-17 and exact rational rounded-law TV measurements. It generated two 8 kHz, mono PCM16, 0.64-second specimens by enumerating three independent binary stage outcomes; recovered all 16 output symbols by matched templates. Output histograms were (1,3,3,1,0,0,0,0) and (1,1,1,1,1,1,1,1). Both WAVs and receipt reproduced byte-identically. These are synthetic enumerated score inventories, not random security trials. Full native repository checkout attempted and failed DNS resolution. Standalone checks are not full repository CI or independent review.

## Interpretation and application boundary

A useful research instrument would let the performer manipulate a circular symbol vocabulary, successive independent stochastic transformations, per-stage support/precision and fixed omission patterns, and display the surviving Fourier modes. The compositional idea is a distinction between repeated smearing and complementary erasure. The numerical observer is stipulated, and the audible output is a conventional tone per residue. An actual listener may recover intermediate cues, exploit time correlations, or fail to distinguish even the intended residues. No perceptual evidence, production security advice, Brier-specific explanatory contribution, or Track E/G advancement. A direct lookup or a single uniform offset is an essential baseline; distributed stages are interesting only under resource or omission constraints. Independent critique and exact-head CI remain separate gates. No scientific priority claimed.

Fiction: a clerk keeps turning a circular dial by a fair small step. His apprentice changes the size of each successive step instead. The first sequence grows more difficult to predict; the second exhausts the entire dial exactly. The clerk had mistaken repeated uncertainty for the disappearance of a distinction.
