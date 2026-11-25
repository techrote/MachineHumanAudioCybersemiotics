# The Interpolator That Needs a Negative Sample

Issue #432 — synthetic/formal expedition, 2026-11-25. AI-assisted derivation, implementation and self-audit; no human review or empirical evidence. Base main: 495a98ca12bae467a507031f04931aa4254b1866. Recent issues and PRs plus searches for fractional delay, interpolation and negative weights were inspected: no direct overlap found; circular-blur inverse and ordinal interpolation expeditions have distinct objectives. No frozen protocol, source registry, shared manifest or production code modified.

## Model and exact objective

A real FIR stencil h on a finite integer grid S containing 0 and 1 evaluates y[n] = sum h[k] x[n-k]. Exact reproduction of polynomials of degree at most d at offset alpha requires sum h[k] k^j = alpha^j for j=0,...,d. Negative tap mass B = sum max(0,-h[k]). With unit DC gain, the l1 norm is 1+2B. For independent sample values in [0,1], the exact achievable range of one output is [-B,1+B]: choose one at all negative or all positive taps respectively. This is a worst-case bounded-sequence guarantee, not necessarily step overshoot or sinusoidal gain.

## Theorem A: quadratic reproduction on irregular grids

Let 0<alpha<1, with at least one extra integer grid point. Put M=max k(k-1) over S, positive. The exact minimum is B*=alpha(1-alpha)/M.

Proof: q(k)=k(k-1)/M lies in [0,1] at every integer node; reproduction forces sum h[k]q(k)=q(alpha)=-alpha(1-alpha)/M. For any h, this sum is >= -B. For any maximizing K, set h[K]=-B*, h[1]=alpha+K B*, h[0]=1-alpha+(1-K)B*, other taps zero. Both central taps are positive: for K>=2, h[0]=(1-alpha)(1-alpha/K); for K<=-1, h[1]=alpha(1-(1-alpha)/(1-K)); the other central tap is plainly positive. The sum and first moment are correct, and the q identity supplies the second moment. Hence equality, including over nonsymmetric signed stencils. With only nodes 0,1 reproduction of the second moment is impossible.

## Theorem B: half-sample cubic and quintic reproduction

Let S={-L,...,L+1}, alpha=1/2. Write t=(2k-1)^2; shell j contains nodes -j,j+1 and has t_j=(2j+1)^2. Reflection symmetry makes all odd centered moments vanish. For even moments, shell totals are a real signed evaluation functional at t=0.

Cubic (L>=1): Theorem A gives B*=1/[4L(L+1)]. A symmetric attaining stencil has central pair each (1+B*)/2, outer pair each -B*/2. The centered fourth moment is exactly -R^2/4 for R=L+1/2, obtained by substituting the weights and simplifying. The centered frequency response near zero is therefore 1-R^2 omega^4/96+O(omega^6) at fixed L, with omega in radians per sample. A larger available support decreases the exact overshoot budget but increases the leading DC approximation error coefficient.

Quintic (L>=2): let T=t_L and M=max_{1<=j<L}(t_j-1)(T-t_j). Then B*=T/M. Proof: q(t)=(t-1)(T-t)/M lies in [0,1] on all shells. The degree-four reproduction condition forces sum h[k]q(t(k))=q(0)=-T/M. Therefore B>=T/M even without a symmetry restriction. Select any maximizing j and use the three Lagrange evaluation weights at t=0 on {1,t_j,T}. Endpoint weights are positive, interior weight is negative with magnitude T/M. Split each shell weight equally between its two nodes. These weights reproduce degree four by interpolation in t and degree five by reflection. Thus they attain the bound. The centered sixth moment is (1/4)(t_j/4)(T/4), from the cubic interpolation remainder on the squared centered coordinates. For L=1 degree five is impossible: a polynomial of degree four vanishes on every node but not at the target.

Both constructions use at most four or six taps respectively, though their support spans can be much larger. Their causal versions require a common delay of L samples in addition to the half-sample target. The present audio experiment evaluates an analytic source with both sides of support available.

## The escaping-moment counterexample

At half delay the simple two-tap linear stencil has weights 1/2 at 0 and 1. For either compiled family the central shell has total >1 and all other positive taps lie outside it, so the l1 distance from the linear stencil is exactly 2B*. Consequently the frequency-response difference from linear interpolation is uniformly bounded by 2B*. For cubic B*=O(L^-2); for quintic the shell nearest T/2 has t_j/T tending to 1/2, so M/T^2 tends to 1/4 and B*=O(L^-2). Thus both high-order families converge uniformly in frequency to the LOW-order linear response despite preserving their higher moment conditions at every finite L. Unbounded support makes differentiation of the limiting response invalid here; the constraints are not closed under this limit.

This is a deliberately preserved counterexample to treating more taps, smaller coefficient negativity, or exact low-frequency moments as guarantees of finite-band fidelity. At f=0.05 cycles/sample the centered cubic response for L=1 is 0.9997735676459839, versus 0.9881788716988653 for L=16. The latter's negative mass is 136 times smaller, yet absolute amplitude error is about 52 times larger. This is an illustrative constructed family, not a claim that increasing allowable support worsens every optimal filter: a different optimization objective can simply retain the short stencil.

## Verification and artifacts

- stencil.cjs: BigInt rational compiler, exact moment and dual checks, exhaustive candidate-basis comparisons and invalid input tests. Run node stencil.cjs (CLI not yet qualified; executed in V8 via Function). Receipt results.synthetic.json: 5,355 irregular-grid targets, 134,400 three-node bases, 255 half-grid cases, 17,550 shell bases, 40,596 dual checks, 5 refusal cases. These are test counts, not independent observations.
- independent.py: separate full-grid SciPy LP with positive/negative variables and no imposed symmetry; 252 cases, maximum absolute difference from exact bound 1.0881053003064522e-15. Run python independent.py with NumPy/SciPy. Also evaluates 2,001 frequency points and generates two four-second 48 kHz stereo PCM16 WAVs. No clipping; repeated renders byte-identical locally.
- cubic-sweep.wav: left short cubic, right distant cubic; same analytic chirp (100 to 18,000 Hz), identical requested delay. SHA256 47c810b0c9d8cba819d8e147ce0e3e921e80af2aef0dc806dcc7933e3ad4fd30.
- cubic-residual.wav: same channels after subtracting ideal analytic half-delay, both multiplied by 0.7, not separately normalized. SHA256 01b1c04e94cd5873fe8655d520a90fdd2a3aca5f1ad90cc6994065b6265a2c89.
- Audio files generated locally, not committed. Exact compiler and numerical oracle are committed. Numerical receipt generated by running Python, not an empirical dataset. Python 3.13.5; native repository access failed with GitHub DNS resolution, so no repository-wide qualification claimed.

## Source provenance and transfer

Background: Julius O. Smith III, *Physical Audio Signal Processing*, “Lagrange Interpolation,” section “Lagrange Interpolation Optimality” and symmetry: https://www.dsprelated.com/freebooks/pasp/Lagrange_Interpolation.html (retrieved 2026-11-25, search-returned section excerpts; not entire book). MathWorks, “Design Fractional Delay FIR Filters,” Lagrange-Based Fractional Delay Filters section, https://ch.mathworks.com/help/dsp/ug/design-of-fractional-delay-fir-filters.html (search-returned section excerpt, moment constraints). These are background for standard polynomial reproduction and maximal flatness, not sources for the particular signed-mass formulas. Self-contained proofs above; priority not established. No quotations or restricted materials copied.

Potential transfers: interpolation of bounded simulation quantities, numerical reconstruction with explicit undershoot budget, sparse resampling, control envelopes, procedural geometry and a delay-line instrument whose locality and coefficient-negativity controls trade against each other. A nonnegative normalized interpolator is range preserving, but cannot exactly reproduce a quadratic at a noninteger location. A signed stencil is not a probability distribution. For physical streaming, fixed-point quantization, noise, bandwidth, aliasing, buffer latency and actual input constraints require separate qualification. No human effect or preference inferred.
