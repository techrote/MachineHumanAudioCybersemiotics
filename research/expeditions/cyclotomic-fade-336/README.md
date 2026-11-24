# The Fade That Cannot Avoid a Frequency

**Refs #336 · 24 November 2026 · synthetic mathematical/DSP expedition, not Track E/G evidence.**

A gain must transition monotonically from 0 to 1. Its increments are nonnegative and occur on a fixed clock. Can it also leave a chosen ideal undamped mode unexcited after the transition? This is an input-shaping / nonnegative FIR design toy, not a claim about audible clicks, human response or hardware. It concerns the increment train, not the Fourier transform of the gain trajectory itself.

## Model and exact coefficient arithmetic

Let weights w_j ≥ 0, total M > 0, and j=0,...,D. The cumulative sum of w_j/M is a monotone gain. With clock step Δ, DΔ is the span between first and last active increments (leading zeros can be removed). A unit undamped complex resonator at frequency 1/(qΔ) receives an impulse proportional to each increment. Its free-ring amplitude after the last impulse, divided by the unit single-step reference, is |P(ζ_q)|/M, where P(x)=Σ w_j x^j, ζ_q=exp(2πi/q). A zero is exact cancellation in this restricted model.

For rational coefficients, P(ζ_q)=0 implies divisibility by the qth cyclotomic polynomial Φ_q over Q, hence cancellation at *every* primitive qth root. For integer weights the monic divisor gives an integer quotient. For a distinct set Q of orders, the product C=∏ Φ_q divides P. Thus D ≥ deg C=Σ φ(q) and M=P(1) is a positive integer multiple of C(1). These are necessary, not always sufficient. The independent geometric lower bound is max ceil(q/2): if D<q/2, all available phasors lie in an open semicircle and a positive weighted sum cannot be zero.

When C has only nonnegative coefficients, C itself attains both lower bounds on degree and integer mass simultaneously (the geometric lower bound cannot exceed its feasible degree). This includes every set of distinct prime-power orders, even multiple powers of the same prime: Φ_{p^a}(x)=1+x^{p^{a-1}}+...+x^{(p-1)p^{a-1}}, obtained by dividing x^{p^a}-1 by x^{p^{a-1}}-1. Consequently the exact minimum duration in ticks is Σ p^{a-1}(p-1) and the exact minimum integer mass is ∏ p, counting distinct orders once. These facts do not establish priority over known cyclotomic mathematics.

A stronger implementation warning follows. If increments must be integer multiples of 2^{-b} and the total must be exactly one, then M=2^b. No exact zero at an odd prime-power order is possible for *any* finite span, because its prime must divide M. This is not merely a short-filter limitation. Non-dyadic rationals with a suitable denominator, nonuniform timing, signed increments, and approximate rather than exact zeros are different contracts.

The general compiler emits the lower bounds, tests the positive product, and otherwise returns a feasible convolution of individual combs: for each q choose a prime divisor p and use Σ_{j=0}^{p-1}x^{jq/p}. It also supports exact bounded-mass enumeration under a span cap. It searches only mass multiples of C(1), trims leading shifts via a positive first tap, and distinguishes budget exhaustion, finite mass-cap failure, geometric/degree infeasibility, and a witness optimal within the requested span. A failed finite mass search does not prove impossibility at arbitrary mass.

## Real coefficients can purchase a shorter deadline

For a single fundamental order q, arbitrary real nonnegative weights can attain D=ceil(q/2). The open semicircle argument proves necessity. For even q use antipodal endpoints; for odd q center the arc at its midpoint, take equal endpoint weights (negative centered real projection), and put a matching positive centered real projection on the central point or equally on its two nearest grid points. Symmetry cancels imaginary parts. This constructs positive total mass and zero projection. For q=2 the antipodal case works.

For an odd prime p, rational nonnegative weights instead require D=p-1, attained by the uniform p-tap word. For prime powers the corresponding rational minimum is p^{a-1}(p-1). In the prime family the ratio of rational to real span tends to two.

For q=5, span 3 permits the symmetric real word [1,r,r,1], r=(3-sqrt(5))/2. Its residual is exactly zero but r is irrational. An integer four-tap word cannot attain zero, no matter how large its total mass. Uniform four taps have residual 1/4; uniform five taps have zero. Also the real short word only zeros the fundamental and its conjugate, not the other primitive pair, which is a negative control against equating real and rational spectral constraints.

## A precision frontier with a number-theoretic obstruction

For integer weights on the four-tap q=5 grid, the algebraic norm N=P(ζ)P(ζ²)P(ζ³)P(ζ⁴)=|P(ζ)|²|P(ζ²)|² is a nonzero positive integer (P(ζ) is a nonzero algebraic integer; the four primitive conjugates exhaust the field). Since |P(ζ²)|≤M, the normalized residual is at least 1/M². This is a bound, not generally attained equality.

Let φ=(1+sqrt(5))/2 and F_0=0,F_1=1. Choose the four-tap integer word [F_{k+2},F_k,F_k,F_{k+2}], k≥1. The Fibonacci recurrence or Binet formula gives F_{k+2}/φ²-F_k=(-1)^k φ^{-(k+2)}. Centering the phases then yields exact normalized residual φ^{-(k+1)}/M. Since M=2(F_{k+2}+F_k)=Theta(φ^k), this family achieves Theta(M^{-2}) along its mass subsequence. Its algebraic norm is exactly one: substituting the conjugate φ'=-1/φ into the centered squared magnitude, or the Fibonacci identity, verifies this. This is an order-sharp lower bound along a subsequence, not a statement of optimality at every mass or every q.

Exact finite search uses the representation 2|P(ζ)|²=A+B sqrt(5), where A=2Σw_j²-C1-C23, B=C1-C23, C1=w0w1+w1w2+w2w3 and C23=w0w2+w1w3+w0w3. Comparing two such values uses signs and integer square comparison; no floating tolerance determines a winner. Python independently derives A,B from centered phase coordinates X=w0+w3,Y=w1+w2,U=w3-w0,V=w2-w1: 4|P|²=(X+(Y-X)φ)²+(3-φ)(Uφ+V)², evaluated in Z[φ]. The complete 64-row canonical integer sequence (mass,A,B,candidate count,ties,lexicographic witness) agrees by FNV-1a digest c34520fd0834cf30. The digest is a reproducibility cross-check, not cryptographic proof of equality.

Examples (minimum within exactly M integer units, four slots):
- M=4: [1,1,0,2], residual 0.0954915.
- M=8 and 16: residual 0.0295085 (doubling the resolution gives no gain at this deadline).
- M=32: [10,7,2,13], residual 0.00605537; optimum need not be symmetric.
- M=58: [21,8,8,21], residual 0.000593825.
- M=64: [23,9,9,23], residual 0.00543006. Fixed exact masses need not improve monotonically unless one divides another; 58 is not a dyadic mass.
A maximum-mass budget is a different monotone objective.

## Two frequencies: duration versus increment count

For Q={3,6}, Φ3 Φ6=1+x²+x⁴. This is jointly optimal at span 4 and mass 3, whereas convolving individually shortest integer schedules (uniform three taps for q=3, antipodal two taps for q=6) takes span 5 and mass 6. Joint planning can be better than independently optimal parts.

For Q={6,10}, C=1-2x+3x²-3x³+3x⁴-2x⁵+x⁶. Degree six cannot give a nonnegative multiple. Degree seven would require quotient a+bx with a,b>0 after leading-zero removal; the x and x^6 coefficients force b≥2a and a≥2b, impossible. At span eight the word 1+x³+x⁵+x⁸=(1+x³)(1+x⁵) is feasible with mass 4. Mass 1 never cancels. Mass 3 cannot cancel at q=10 because three unit vectors summing to zero must be spaced 120 degrees apart, unavailable among tenth roots. Mass 2 needs a single opposite pair for both q=6 and q=10, i.e. distance ≡3 mod 6 and ≡5 mod 10, whose least positive solution is 15. At span 15 the word 1+x^15 works. Therefore the exact nonnegative integer Pareto frontier (span, mass) is {(8,4),(15,2)}. This is not the real-weight frontier. Bounded enumeration independently reproduces the span 6..15 outcomes at mass cap 4. The general compiler does not claim arbitrary-order global optimality when its positive-product and simple lower bounds fail.

A triple {6,10,15} test with 100 candidates intentionally exhausts its budget; no infeasibility claim follows.

## Reproducible artifacts and audio

Run from this directory:
    node verify.mjs
    python3 check_audio.py --out /tmp/mhac-fade-336

The JS verification was executed in tool V8 against fetched source (module import/export wrapper adapted), not native Node. It evaluates 5,021 primitive roots through q=128, 276 order pairs 2..24 (including duplicate singleton cases), 161 positive products, and exactly 814,384 four-tap integer candidates over 64 masses; all assertions passed. The largest numerical normalized residual among joint witnesses was 2.45e-15; exact divisibility is the certificate, not that floating check. Fifteen Fibonacci witnesses have exact unit norms. Five invalid input cases and the budget refusal passed. Python 3.13.5 independently reproduced the integer census and rendered twice with byte-identical output. No subagents or independent human review. Repository-wide checkout was blocked by DNS. See results.synthetic.txt and audio-verification.synthetic.txt for actual outputs.

The WAVs are generated, not committed as binaries. They directly render the specified ideal undamped 400 Hz resonator at 16 kHz, with clock step 8 samples=0.5 ms; eight isolated 0.25 s segments, identical end tapers and resets. Short-vs-exact compares four uniform increments to five uniform increments. Same-deadline compares the uniform four-tap word to [21,8,8,21]. Untapered tail PCM peak pairs are (4500,0) and (4500,11). The initial transient is *not* zero even when the tail is; this is not click-free switching. Rendering is finite, floating-point and PCM16, not a hardware measurement. The residual is a normalized complex coefficient, not a perceptual metric.

## Exaptation and falsification

An instrument could expose protected resonant modes, clock span and increment denominator as independently chosen parameters. The compiler outputs feasible monotone control trajectories or explicit limits. Applications worth testing include command input shaping, small fixed-point fader control, mechanical mode-aware motion and deliberately imperfect cancellation in musical envelopes. The cost of protection can be paid in duration, coefficient granularity, or relaxed residual. This is a design hypothesis, not a demonstrated product improvement.

Damping changes the target root's radius; a nominal unit-circle zero then need not cancel. Off-grid frequency, clock jitter, finite edge bandwidth, time-varying or nonlinear dynamics and independently phased repeated events can likewise leave a residual. The guarantee concerns a single finite increment schedule in a specified linear undamped model; it says nothing about subjective audio quality. A real mode's actual transfer function and timing would need validation. The two-frequency result is not a statement about the number of actual pulses after coincident increments are combined.

## Provenance and isolation

- Laura De Carli and Maurizio Laporta, "Divisibility criteria and coefficient formulas for cyclotomic polynomials", The Ramanujan Journal 70, article 44 (2026), https://doi.org/10.1007/s11139-026-01421-6 . Accessed 24 November 2026, HTML introduction §1 and §1.1, definition, equation (1.1), and irreducibility statement. Not a full article reading. Used for standard cyclotomic facts only.
- T. Y. Lam and K. H. Leung, "On vanishing sums for roots of unity", preprint 1995, https://arxiv.org/abs/math/9511209 . Accessed 24 November 2026, abstract only: establishes prior work on admissible integer weights; no full-text reading or priority claim. The specific small frontier proof above is self-contained given cyclotomic facts.
- Input shaping, FIR notch filters and algebraic approximation are established fields; no comprehensive novelty review was conducted. The operational combination here is a scoped original exercise and reusable implementation, not a new scientific theory.

Base main 495a98ca12bae467a507031f04931aa4254b1866. Recent issue and draft titles plus targeted notch/fade searches checked before edits. Existing #288 studies bipolar moment-null blocks, distinct from nonnegative monotone increments at nonzero frequencies. Existing #332-era transient command research motivates caution about overlap; this work is specifically on arithmetic constraints in notch design. All changes confined to this issue's expedition directory; no frozen method, shared records, participants, production interface or empirical claims changed. Draft review required. AI-generated code, proofs and audio; not independently reviewed.
