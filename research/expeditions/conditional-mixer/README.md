# The Mixer That Forgets Only in the Right Order
**Refs #666 · 26 November 2026 · exploratory mathematical construction, agent self-review.**

## Observation contract

Following #662 (directional replacement) and #644 (cyclic convolution), ask a different question: can operations that are individually reversible, idempotent and stationary nevertheless compose to erase the input in finitely many steps? Can their pairwise spectral qualifications certify that result?

Let a full state x=(A,C,U,V) consist of four signs, each ±1. For a fixed reference probability law π with full support, define the resampling kernel P_L for a label L: retain that label and redraw the complete state from π conditional on the retained value. The three labels are A, B=(U,V), and C. Rows of P_L give conditional output distributions. For a function f on states, P_L f is its conditional expectation given L. Thus P_L is an orthogonal projection in L²(π), a stochastic idempotent, and is reversible by detailed balance. These are separate properties. The target reset kernel J has every row equal to π. We evaluate the final full-state output, not a trace of all intermediate states. Schedules are fixed, or randomized independently of input and redraws as explicitly specified below. This is a synthetic mathematical communication model, not an operational privacy or security certification.

The product convention is chronological: ABC means the row transition P_A P_B P_C, so it acts on column test functions from the right.

## A matched-spectra family

For real α,β with α²+β²=1 and β≥0, define

    π(a,c,u,v) = (1 + au/4 + c(αu+βv)/4 + ac/4)/16.

Its total mass is one; the density factor is at least 1-(2+sqrt(2))/4>0. All four bits are fair, U,V are independent, and summation gives

    E[A|B] = U/4,
    E[C|B] = (αU+βV)/4,
    E[A C] = 1/4.

Let Q_L=P_L-J be the orthogonal projection onto the centered functions of L. Q_A=A⊗A and Q_C=C⊗C (f⊗g maps h to f times E[gh]); Q_B projects onto the span of U,V,UV. In particular Q_B A=U/4 and Q_B C=(αU+βV)/4.

Every pair of different centered projections has a product with exactly one nonzero singular value, 1/4: for AB and BC this is the norm of the corresponding projected unit sign, and for AC it is the absolute scalar correlation. The dimensions and complete principal-angle spectra of each pair are identical across α. All nontrivial alternating pair products have norm (1/4)^(length-1), as follows by successively projecting between the one-dimensional space and its image; their nonzero alternating-cycle eigenvalue is 1/16. This is also a special case of the classical two-projection angle formula. All pairs have only constants in their full intersection because π has full support and their labels are disjoint coordinates. None commutes: commuting orthogonal projections multiply to the intersection projection, but all pair products have a nonzero centered part. No individual stage or two-stage sequence resets.

The audit here is specifically labelled *pairwise singular spectra*, not equality of every labelled joint probability table or every matrix entry. The latter would expose the distinction. For example, E[CU]=α/4 differs across worlds. The reference law also varies across worlds; within each world all three kernels preserve exactly the same π.

## Exact three-stage order and finite-word classification

The centered chronological product for ABC is

    Q_A Q_B Q_C = (α/16) A⊗C.

For CBA the adjoint holds. Hence a one-pass reset in those orders occurs precisely at α=0. In the other four permutations the centered products have rank one with norm 1/16, since their middle projection is rank one and both incident overlaps have norm 1/4. Thus when α=0 precisely two of six permutations reset; when α≠0 none resets. The worst-row TV for ABC is |α|/32, since C is a fair sign and the row density relative to π is 1+(α/16)A(x)C(y). TV of CBA is the same. L² operator norm and worst-row TV need not agree for other permutations.

For any nonempty finite word, first collapse adjacent identical letters (idempotence). If it contains neither A nor C it is simply B and retains information. Otherwise isolate successive occurrences of A or C. Between two such occurrences there is at most one B. A direct A-C or C-A transition contributes scalar 1/4. A-B-A and C-B-C contribute 1/16. A-B-C and C-B-A contribute α/16. The left and right endpoint factors are either the unit A/C functions or their nonzero projections onto B. Therefore:
- At α=0, a fixed word resets iff its reduced form contains ABC or CBA as a contiguous substring.
- At α≠0, **no finite deterministic word in these three operations resets**, no matter how many times every operation has been used.

This follows from the rank-one factorization, not from bounded enumeration. For α=0 the shortest reset has length three. For α≠0 there is no finite shortest reset, although cyclic products converge.

For any permutation W of ABC, let T=P_W-J. Its rank is at most one. The trace of T is α/64: cyclic invariance and reversal (adjoint) reduce all six traces to that of (α/16)A⊗C, which is (α/16)E[AC]. A rank-one operator satisfies T²=tr(T)T, so

    P_W^k - J = (α/64)^(k-1) (P_W-J),   k≥1.

The four incorrect orders at α=0 erase exactly on the second complete cycle, despite each of their one-cycle operators being nonzero. Their residual is nilpotent of index two. At nonzero α all cycles converge geometrically but never erase exactly; negative α alternates the sign of the residual. The eigenvalue inventory alone cannot distinguish zero residual from nonzero nilpotent residual. This extends #662: each *constituent* stage here is self-adjoint and idempotent, not a nonnormal shift.

## Omission resilience

At α=0, a fixed schedule robust to deletion of any at most e individual operations has exact minimum length 3(e+1). Necessity: each of A,B,C must occur at least e+1 times, or an adversary can remove that entire letter; the reduced word cannot contain ABC or CBA. Sufficiency: A^(e+1) B^(e+1) C^(e+1) retains at least one of each in the right order. Omissions are chosen independently of the input and redraws. This is a deletion guarantee for the fixed three-stage dictionary, not a bound on arbitrary stochastic resets. A direct draw from π would trivially erase in one stage if available.

## Hidden schedule cancellation: the surprising escape

At α=-1, β=0, no finite fixed word resets. Nevertheless let the controller choose AAC with probability 1/5 or ABC with probability 4/5, before observing any data. The first retains positive dependence and the second negative:

    P_A P_A P_C - J = (1/4) A⊗C,
    P_A P_B P_C - J = -(1/16) A⊗C.

The convex combination is exactly J. Equivalently, the middle stage is the reversible stochastic mixture (P_A+4P_B)/5, with A before and C after. The full final state (not only a chosen bit) is independent of the initial state. The schedule is not a per-input adversarial choice.

For any α<0 the analogous mixing weight on AAC is -α/(4-α), with the remainder on ABC. The weights are exact rationals for rational α. Yet the hidden-schedule result disappears when the observer receives the schedule identity: conditional on either schedule the channel is not a reset. At α=-1 the worst-row TV of the joint (schedule, final state) versus schedule-independent π is (1/5)(1/8)+(4/5)(1/32)=1/20. The residual disappears by marginalization, not by erasure of every conditional relationship.

Conversely, for α≥0 and β≥0, no convex mixture of finite non-reset words can reset, even with unequal lengths. At the all-positive state, every rank-one endpoint factor is positive and every scalar factor of a nonzero residual is positive; the single B projection also has positive centered diagonal. Thus all non-reset words have strictly positive centered diagonal at that state; they cannot cancel in a positive mixture. Words that do reset contribute zero. This establishes the sign-dependent existence of a hidden-schedule reset for this family, not a general classification of arbitrary channels.

Independent identically distributed random choice of stage at every step is another contract. The averaged operator on the centered space is a nonzero positive-semidefinite sum of orthogonal projections, and no positive integer power can vanish. The successful random schedule deliberately uses different choices at different positions; it is not mere random repetition. Revealing intermediate states similarly invalidates the final-only erasure guarantee (the first A stage retains the initial A sign). No claim about previously emitted information follows.

## Evidence and executable qualification

Prior art and reading boundaries, all checked 26 November 2026 by this agent:
- Reich and Zalas, *The Optimal Error Bound for the Method of Simultaneous Projections*, arXiv:1704.00308 (2017), https://arxiv.org/abs/1704.00308 . Read the rendered introduction, Theorems 1–4 and equations (3)–(4), including the attribution to Aronszajn and Kayalar–Weinert. These establish the cyclic-convergence setting and exact two-projection norm. Their simultaneous-projection results are not needed for our construction. No originality claimed for alternating-projection theory.
- Kayalar and Weinert, *Error bounds for the method of alternating projections*, 1988, DOI https://doi.org/10.1007/BF02551235 . Bibliographic metadata and accessible abstract read; the exact formula is read through Reich–Zalas rather than asserted to be independently checked against the full original.
- Liu, Wong and Kong, *Covariance Structure and Convergence Rate of the Gibbs Sampler with Various Scans*, JRSS B 57(1), 157–169 (1995), https://doi.org/10.1111/j.2517-6161.1995.tb02021.x . Publisher summary and metadata read; full text subscriber-gated. Related use of iterative conditional expectations and systematic/random scan distinctions; not direct proof of the present finite-reset examples.
- #662 issue, comment, PR metadata and complete branch report inspected, and #663 exact-head workflow endpoint returned successful completion at 0f534504fb0b22feb4e90e03dee7cb94738ab759. No change to that branch. The new witness differs from its shift-register model; no correction asserted.
- Targeted repo searches for conditional expectation, alternating projections, principal angles, Gibbs and partition/forget returned no matching expedition. Search cannot certify global research novelty. No priority claim.

Reconciliation: main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, README, RAG, programme, runbook, research integrity and validation read. Paged 393 branch entries and inspected 100 recent open issue and 100 open PR titles. New #666 scope and empty comments read. All work is in this additive directory; canonical manifests, protocol records and other worker branches are unchanged.

Run **node laboratory.cjs**: exact BigInt block multiplication, all 3,825 nonempty reduced words of length ≤8 across five rational-circle profiles (α=0, ±3/5, ±1); 61,200 exact row-sum checks, 30 cyclic profiles, 2,294 fixed-omission checks through e=4 and 256 full-state hidden-mixture cell equalities. Zero assertion failures. Executed the core in a V8 isolate; native Node not claimed. The receipt includes the six-order worst-row TV values for each profile.

Run **python witness.py**: native Python 3.13.5, independently constructs conditional rows from fractions and uses literal rational matrix multiplication; 60 pair/permutation checks and explicit detailed-balance, idempotence, cycle scalar and hidden-mixture assertions. This is a different implementation by the same agent, not independent review. Two runs reproduced the JSON and generated audio; native source and receipt Git blob hashes match the locally executed files. The native receipt records per-order TV and actual PCM hashes. Full native checkout attempted but DNS resolution of github.com failed; repository-wide validation not run locally.

## Acoustic interpretation, negative sediment and design hypothesis

Three stereo enumerated scores project the negative-α example onto the initial A sign and final C sign. Each sign is represented by 300 or 500 Hz, with 40 ms frames, 8 kHz PCM16. The AAC score has 20 of each same-sign pair and 12 of each different-sign pair (64 frames, 2.56 s). ABC has 15 and 17 respectively (64 frames, 2.56 s). The hidden mixture pools one AAC inventory and four ABC inventories, then reproducibly shuffles: each pair occurs 80 times (320 frames, 12.8 s). All 896 acoustic sign bits are recovered from actual integer PCM samples with matched sinusoidal templates. Each channel separately has the same uniform frequency proportions; the relationship changes sign and then disappears. These are exact score inventories, not samples of real acoustic transmission, and do not instantiate the entire four-bit physical state as sound. WAVs are regenerated on demand, not committed.

A possible performance instrument would let the performer choose a reference coupling, switch the conditional-resampling stages, and monitor both signed input-output covariance and schedule-conditioned leakage. A 'forget' control could show separate meters for unconditional and conditional dependence, with a third display for the pairwise principal angles. Direct unconditional redraw is the essential baseline. Do not infer that a listener can discriminate the sound relationships, that any statistical reset is secure or that a human forgets a previous state. The mathematical model is fully explained by conditional probabilities and operator geometry; no extra explanatory contribution from Brier has been established. No production integration, live experiment, human screening or empirical evidence promotion.

Fiction: three clerks are each permitted to keep one part of a record and replace the rest. Every pair has the same measured capacity to preserve an inscription. In one office the order matters; in another even an endless procession cannot erase it. A hidden coin chooses between two incomplete erasures whose residual inscriptions have opposite signs. The observer sees a blank ledger only because the coin's ledger remains closed.
