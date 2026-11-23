# The Observer's Solecism: formal note

**Epistemic classification:** the propositions and proofs in §§1–3 are elementary original deductions from definitions; the Kaluza–Klein Fourier result in §4 is attributed to a source, and all communication/music links are analogies or proposals. This document makes no claim of fundamental new physics.

## 1. The grammatical defect that belongs to a relation

Quintilian, *Institutio Oratoria* I.5.34–38, distinguishes an isolated lexical item from an error arising in its **combination** with other elements or a speech context. Among his examples, a command morphology addressed to the wrong number of people may be problematic even when the word itself is well formed. His analysis is richer than a modern binary grammar oracle; correctness depends on the relevant usage norm and interaction.

A toy abstraction (not a historical Latin grammar engine) has a state x = (utterance, addressee_number). Let a validity predicate V(x) depend on *both*. If an observer receives only the utterance, it may not be possible to determine V(x) correctly. This is **not** the same as ordinary syntactic ambiguity, where one string legitimately allows multiple analyses; nor must every variation be called a solecism.

## 2. Observational factorisation theorem

Let X be a set of complete states, O a set of observable messages, P:X→O an observation function, and V:X→Y any verdict, property or action decision.

**Claim.** There exists a deterministic function D:O→Y with V = D ∘ P *if and only if* V is constant on every fibre P⁻¹(o).

**Necessity.** If P(x₁)=P(x₂)=o then V(x₁)=D(o)=V(x₂), so V is constant on the fibre.

**Sufficiency.** Suppose V is constant on each nonempty fibre. Define D(o)=V(x) for any x with P(x)=o; the result is well defined. Extend D arbitrarily to observations outside P(X). Thus V=D∘P.

**Consequence.** If two complete states with the *same observed surface* require different judgements, no deterministic decoder of that surface alone can be correct on both. A second observation capable of separating those states can restore that particular distinction. This is not a universal lower bound on all language comprehension.

This theorem is valid for arbitrary sets and total functions; it needs no probability distribution, cognition hypothesis, physical geometry or extra spatial dimension. If distributions are supplied instead, a Bayesian predictor may do better *on average* without eliminating the indistinguishability.

## 3. Eight stationary witnesses and a moving witness

Let S¹ be a circle with angular coordinate θ modulo 2π. Define a family of real functions

    f_n(θ) = cos(nθ),  n = 0, 1, 2, ...

For integer N≥3, a deliberately limited observer samples the values at

    θ_j = 2πj/N,  j = 0,...,N−1.

Write P_N(f) for the N-element vector of samples.

**Exact alias theorem.** For every integer n≥0 and k≥1,

    P_N(f_n) = P_N(f_{n+kN}).

**Proof.** At sensor j,

    cos((n+kN)2πj/N)
      = cos(2πnj/N + 2πkj)
      = cos(2πnj/N).

The last equality uses 2π-periodicity of cosine. All N coordinates agree. QED.

The continuous functions are nevertheless distinct for distinct nonnegative integer mode indices (up to the trivial cosine sign symmetry for negative indices). Therefore the observation is *not injective* even on this simple restricted set.

**Specific example.** N=8; n=2 and n+N=10. At all eight fixed probes the difference is zero mathematically (floating-point evaluation introduces rounding-level residuals).

Now shift every probe by δ=π/(2N)=π/16. Already at j=0,

    f_2(δ) = cos(π/8) ≈ 0.9238795325,
    f_10(δ) = cos(5π/8) ≈ −0.3826834324.

The absolute difference is approximately 1.3065629649. A single additional probe at **that particular point** separates this particular pair. A random or unlucky additional probe need not; full reconstruction of unrestricted arbitrary modes needs stronger observation assumptions.

**Important countercases.**
- Real cosine also aliases n with N−n at these probes; the equivalence classes are wider than simple n mod N.
- If the candidate set is bounded to a known band and sampled adequately, unique reconstruction can be possible.
- If probe positions are freely chosen, the specific n versus n+N alias can be broken.
- If measurement noise is admitted, small observed differences may not be practically resolvable.
- For continuous arbitrary functions, any finite sample set still leaves vast unobserved degrees of freedom.
- If n=0, the moving-observer audio contains a DC component, not a pitched tone. This is permitted mathematically but not a suitable listening comparator.

## 4. What Kaluza–Klein actually contributes

In Jan Louis (2016), *Introduction to Supersymmetry and Supergravity*, **§17.1, printed p. 64, equations (17.3)–(17.6)**, a scalar field on a background of the form four-dimensional Minkowski spacetime × a compact circle is periodic in the coordinate y with period 2πR. The circle dependence admits Fourier modes exp(iny/R). In the simplest massless five-dimensional scalar example, after separating variables the four-dimensional modes have squared masses

    m_n² = n²/R²

in natural units and the stated sign conventions. Equivalently, the circle eigenfunctions have eigenvalues (n/R)² under minus the second derivative in y.

Our real cosine f_n(θ) is a permissible combination of complex circle harmonics for θ=y/R. In this mathematical toy, modes 2 and 10 have different eigenvalues, 4/R² and 100/R², **even though our separately invented eight-probe observation operator confuses their spatial samples**.

**Boundaries that must not disappear in retellings:**
- These aliasing probes are **not** a standard Kaluza–Klein dimensional reduction, quantum measurement or physical detector.
- The example uses a scalar field and a chosen compact circle, not a new five-dimensional gravitational solution.
- Distinct Fourier indices and eigenvalues here do not prove an experimental hidden dimension, new particle mass or unresolved gap in physical theory.
- Nothing in this proof reconciles, refutes or strengthens any open Kaluza–Klein conjecture.
- The probe-rotation → sound-frequency mapping in our generator is an **arbitrary art instrument**. Its tones (n times an invented rotation rate) are not the KK masses.

## 5. The one-way philosophical move

The safe analogy is not *meaning is a hidden dimension*. It is *a verdict about a system may fail to descend to a compressed observation of that system*.

This accounts for a useful family of failures: a speech form observed without an addressee, an audio code received without a declared grammar version, a machine instruction received without current mode or authorization, or a physical mode observed through too few positions.

But the analogy has counterexamples. Correct interpretation can rely on rich priors even from a sparse message; human language norms can change; and no observation operator alone defines what counts as legitimate meaning. An observer's ignorance is not a proof that reality contains an additional spatial coordinate.

**Research wager:** the residue of a failed classification can sometimes reveal the missing *kind* of contextual variable. This is a heuristic for instrument design and literary investigation, not a proven law of semiotic systems.
