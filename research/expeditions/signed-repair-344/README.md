# The Echo That Demands Negative Time Weights

Refs #344 · 24 November 2026 · synthetic mathematics and artistic DSP demonstration, not Track E/G evidence.

## Scope and reconciliation

Base 495a98ca12bae467a507031f04931aa4254b1866 (live main checked before branch creation). Read README, AGENTS, RAG, programme, runbook, integrity and validation instructions; inspected recent open issue/PR titles and searched for deconvolution, positive inverse and quasiprobability. Earlier blind convolution, erasure and all-pass expeditions address different problems: here the blur is known, and the permitted sign budget of a mass-preserving circular inverse is the variable. Search is not an exhaustive novelty audit. No shared or frozen records changed. "Negative time weights" means negative coefficients on shifted copies, not negative elapsed time.

## Exact frontier

On the cyclic group Z/n, n>=2, let h=p delta_0+q delta_1, p=1-q, 0<=q<=1/2. A repair g is any real circular kernel with sum(g)=1 and negative mass nu(g)=sum max(-g_j,0)=(||g||_1-1)/2. Minimize E=||delta_0-h*g||_1 subject to nu(g)<=v. All convolutions are circular, and the model does not assume causality on an infinite stream.

For q>0 except q=p=1/2 with even n, h has the unique inverse
b_k=(-r)^k/[p(1-(-r)^n)], r=q/p, k=0,...,n-1.
This follows by multiplying the finite geometric series, using shift^n=I. Sum b=1. Put L=||b||_1 and v*=(L-1)/2. The exact frontier is

    E(v)=2q max(0,1-v/v*).

A witness is g=(1-lambda)delta_0+lambda b, lambda=min(1,v/v*). Its negative mass is lambda v* and its residual equals (1-lambda)q(delta_0-delta_1).

Proof of optimality: let e=delta_0-h*g. Then sum e=0 and b-g=b*e. Let s_i=(-1)^i=sign(b_i), and t_j=sum_i s_i b_(i-j mod n). We have L-||g||_1 <= <s,b-g>=<t,e> <= (max t-min t)||e||_1/2. For even n, t_j=(-1)^j L. For odd n, t_j=(-1)^j(L-2 sum_{k=n-j}^{n-1}|b_k|). The maximum is t_0=L. Among odd j the minimum is t_1; among even j, t_j>=-L+2|b_0|>=t_1 because magnitudes of b decrease weakly. Since h*b=delta_0, p t_0+q t_1=1. Thus max t-min t=(L-1)/q and E>=2q max(0,1-v/v*). The witness attains the bound, including budgets beyond v*.

For even n and q<1/2, L=1/(1-2q), v*=q/(1-2q). For odd n and q<1/2, L=(1-r^n)/[(1-2q)(1+r^n)]. At q=1/2 and odd n, b_k=(-1)^k, L=n and v*=(n-1)/2. At q=1/2 and even n the alternating Fourier mode is annihilated; |sum (-1)^j e_j|=1 implies E>=1, attained by delta_0 for every budget. At q=0 identity needs no negative mass.

For any probability kernel h on a finite cyclic group, if a nonnegative normalized g inverts it exactly, the support of h*g must be the singleton zero. Every support pair contributes positive mass, hence both supports must be singletons. This is an elementary support argument, not a claim of priority.

## Noise cost and robust choice

For an unknown bounded clean x with ||x||_infinity<=1 and independent admissible additive observation error eta with ||eta||_infinity<=epsilon, the exact worst-case pointwise reconstruction error for fixed g is E(g)+epsilon||g||_1. The upper bound is the convolution triangle inequality; choose the signs of the two independent input vectors at a single output coordinate to attain both terms. This is an adversarial amplitude bound, not a random-noise variance result.

Consequently the two-tap budget frontier gives a sharp robust optimum without a budget cap: use the full inverse when epsilon<q/v*, identity when epsilon>q/v*, and any witness on the frontier at equality. With a cap, replace full by the largest permitted useful budget. This is because the objective along the frontier is 2q(1-v/v*)+epsilon(1+2v), and beyond v* the residual is zero but coefficient mass only grows. In the singular case identity remains optimal. At q=0 identity is optimal. A different noise norm or coupling between signal and noise changes the optimization.

For n=8, q=2/5, the full inverse has negative mass 2 and noise amplification 5, while half repair has mass 1, residual 2/5 and noise amplification 3. The break-even bound is epsilon=1/5.

## Preserved falsifier: not a general multi-tap rule

For h=(1/2,3/10,1/5) on Z/3, b=(19,-11,-1)/7 and v*=12/7. At v=6/7, the chord between identity and b has residual 1/2, whereas g=(13,-6,0)/7 has the same budget and residual 17/35<1/2. Exact convolution verifies the strict improvement. A numerical LP also returned 17/35 within 1e-8; no exact optimality claim is made for that LP beyond the witnessed strict counterexample. Thus simple convex interpolation is not universally optimal.

## Reproduction and sound

Run from this directory:

    python verify.py
    python verify.py --lp > results.synthetic.txt

The first uses only the standard library; the second requires NumPy and SciPy and checks the rational frontier against a separately formulated numerical LP with split positive/negative repair and residual variables. Both produce original two-second stereo PCM16 WAVs in run/. The receipt records the rational coefficients, SHA-256 and numerical check error. The 2,144 exact cases include repeated budgets for trivial identity, not distinct empirical observations. 638 numerical LP comparisons and three invalid-argument refusals passed; maximum LP discrepancy 8.673327764330274e-08. The exact certificate, not the floating LP, establishes the theorem.

Clean-repair: left is the blurred pulse [3/5,2/5,0,...], right its exact inverse [1,0,...]. Noise-debt: left half repair and right full repair of the same noisy block; alternating input noise amplitude 1/25 becomes 3/25 or 1/5 respectively. Each coefficient controls an identical windowed 400 Hz burst on a 50 ms grid. This is a linear embedding of circular block arithmetic in a repeated waveform, not a measured room, causal live filter or listening trial. Common PCM scaling keeps the examples below clipping. The noisy example isolates the noise penalty but does not establish that half repair is better overall: at this epsilon the full inverse minimizes the specified worst-case objective. Both WAVs and receipt reproduced byte-for-byte on repeated execution on the same local environment.

## Provenance, interpretation and gates

Related prior machinery: Tian-Ren Jin, Kai Xu, Yu-Ran Zhang, Heng Fan, *Noisy Probabilistic Error Cancellation and Generalized Physical Implementability*, arXiv:2409.01000 (2 September 2024), https://arxiv.org/abs/2409.01000 . Read the abstract, introduction and Results equations (1)-(5) through the accessible text rendering on 24 November 2026; the signed affine decomposition and sum of coefficient magnitudes as a cost are established there in quantum-channel context. The publisher page could not be opened directly. This expedition uses only a classical circular shift model; no quantum experimental or general novelty claim. All mathematical proofs here are self-contained derivations. No human data or external authorship claims.

Proposed exaptations: a bounded-negativity delay instrument; configurable inverse correction on periodic modulation tables; signed correction of finite cyclic categorical confusion under explicit shift assumptions; diagnostic witnesses for noise amplification. Negative weights are not probabilities and do not imply a physical negative event. Exact restoration may require leaving the positive vocabulary of the original channel, but that is a formal analogy, not a conclusion about human understanding.

AI-assisted implementation, derivation and software self-check by ChatGPT; no independent human review. Local full checkout failed because github.com DNS resolution was unavailable; repository-wide CI and review remain pending. Draft only. Do not merge automatically or treat the expedition as accepted scientific evidence.
