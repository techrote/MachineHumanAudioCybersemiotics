# The Midpoint That Has No Name

*Research expedition #254 — 24 November 2026. Original interpretation, bounded mathematics and sound art; not a Track E/G result, not a production requirement.*

## The hand, the knob and the word “half”

An instrument has two perfectly familiar sounds. The musician is told to move halfway from the first to the second. Their hand stops at the physical midpoint, the automation lane reports 50%, and yet there is no agreement about which sound should emerge. One engineer has interpolated frequency, another has interpolated logarithmic frequency, and a third has interpolated a perceptually motivated control law. All may be doing precisely what their designs specify. The error is not necessarily in the calculation but in the unspoken identification of three different relations: order, distance and appropriateness.

Aristotle distinguishes an arithmetic intermediate from one appropriate to a particular person in *Nicomachean Ethics* II.6, 1106a26–1106b15. Six is equally distant from two and ten; it does not thereby become the appropriate ration for both a novice and an athlete. In 1106b36–1107a8 he discusses the ethically appropriate mean, and in the following passage he explicitly denies that every kind of action admits one. [Rackham translation, Perseus, Book II](https://beta.perseus.tufts.edu/urn:cts:greekLit:tlg0086.tlg010.perseus-eng2:2/). The distinction gives this expedition a vocabulary, not its proof. Aristotle is not proposing measurement-theoretic transformation groups or a synthesis algorithm. Nor is ethical appropriateness an unknown coordinate to be recovered by calibrating a machine. These are three different notions of intermediate: equal metric increments, position in an ordering, and what a practice demands.

The mathematical literature already provides a better formal ancestor. Marichal and Mesiar, *Meaningful aggregation functions mapping ordinal scales into an ordinal scale* (2009), author preprint [arXiv:0903.2434v1](https://arxiv.org/abs/0903.2434), introduction pp. 2–4 (PDF indices 1–3), distinguish admissible scale transformations and state their same-input/output-scale invariance equation (3). Their review establishes that this is an existing area of aggregation theory, not a new discovery of this expedition. Our special case is a gesture with endpoint constraints and an unknown calibration law. The novel-to-this-repository design question is how to expose the law, its uncertainty, and its sound as separate artistic material.

Hunt, Wanderley and Paradis, *The Importance of Parameter Mapping in Electronic Instrument Design*, Journal of New Music Research 32(4), 429–440 (2003), [publisher abstract](https://www.tandfonline.com/doi/abs/10.1076/jnmr.32.4.429.18853), treat the mapping layer as potentially defining an instrument. We use that proposal as a prompt to compose the mapping itself, not as evidence of a particular listener or performer response. Abstract-level reading only; no reported experiments are extracted. Hunt and Wanderley's [Mapping performer parameters to synthesis engines](https://www.cambridge.org/core/journals/organised-sound/article/abs/mapping-performer-parameters-to-synthesis-engines/BD8AAF4BC582D3DCACB5AEC5BF49F8FE) likewise motivates the distinction at abstract level.

An instructive counterposition is the [NIST exact temperature conversion table](https://www.nist.gov/pml/owm/si-units-temperature), where Celsius and Fahrenheit differ by a positive affine map. In a specified temperature scale, equal differences are not arbitrary merely because the display units change. A refusal of all interpolations would throw away legitimate structure.

## A word whose meaning is an orbit (formal)

Let x denote a normalized state in [0,1] and t a declared numeric gesture coordinate in [0,1]. A calibration f is a strictly increasing homeomorphism from [0,1] onto itself, with f(0)=0 and f(1)=1. To realize t in the x coordinate, use x=f⁻¹(t). Endpoints are authenticated; absent further facts, only their order and the monotonicity of f are known. This deliberately assumes a single scalar with no direction-dependent hysteresis.

Two separate operations must not be confused:

* **Representation change:** re-express an already specified physical state and transport the original mapping accordingly. This can preserve the actual output.
* **Recomputed interpolation:** take the same numeric fraction in the new chart without transporting the interpolation law. The physical output may change.

For any interior t and any interior x, the piecewise linear function through (0,0), (x,t), (1,1) is an admissible calibration. Hence every interior x is possible for the same t. Endpoints remain exactly identifiable. This is an identified set, not a probability distribution: no claim that all states are equally likely.

A complementary impossibility result is useful. Suppose a rule M(a,b,t) uses only ordinal endpoint information, produces a state between a and b, and is equivariant for every increasing homeomorphism g:
   
    M(g(a),g(b),t) = g(M(a,b,t)).

For a<b, assume its output c is strictly interior. Choose g fixing a,b but moving c to another interior point (a piecewise linear interpolation suffices, identity outside [a,b]). The left side stays c and the right side changes. Contradiction. For fixed t the output must be an endpoint. If M must additionally be continuous in t and take different endpoint values at t=0 and t=1, no such M exists: a continuous image of an interval cannot jump between two distinct points. This elementary stabilizer argument is a special case of existing order-invariance theory, not a claim of mathematical priority.

Extra anchors change the result but do not abolish it. A homeomorphism fixing a finite ordered list of anchors can still move any point strictly between adjacent anchors. Thus an equivariant selector may choose an existing anchor (for instance a rank statistic), but cannot create a new strictly interior state in that gap using order alone. A quantile defined by selecting an observed order statistic commutes with monotone transforms, including ties. A numerical average of two middle values need not. On a finite ordered set, a fixed-index choice from known labels is legitimate; there is no requirement that its physical spacing be uniform.

This impossibility does **not** forbid a physical interpolation law, a known metric, a declared reference chart, an empirically fitted mapping, a deterministic convention, or a randomized endpoint selection. In particular, an affine combination is equivariant under positive affine coordinate transformations. For a ratio scale both arithmetic and geometric interpolation are equivariant under common positive rescaling; the additional desire for equal ratios selects the latter, not ratio-scale status alone. At 200 and 800 Hz the two midpoint values are 500 and 400 Hz. Neither is a claim of equal perceived pitch distance. The instrument designer is entitled to choose, but should not present the choice as an implication of endpoint ordering.

## A bounded world (exact partial identification)

Let every secant of f satisfy 0<L≤(f(v)-f(u))/(v-u)≤U for u<v. These are assumptions about calibration in a particular reference x chart, not ordinally invariant facts. Equivalently a piecewise linear witness may have every segment slope in [L,U]. Let authenticated ordered anchors include (0,0),(1,1) and possibly intermediate pairs. Reject incompatible anchors: each adjacent pair must satisfy the slope bounds. For t between adjacent anchor ordinates y,w at points (a,y),(b,w), write p=t-y, q=w-t.

The candidate x must satisfy:

    L(x-a) ≤ p ≤ U(x-a)
    L(b-x) ≤ q ≤ U(b-x)

Taking the intersection gives the exact closed interval

    max(a+p/U, b-q/L) ≤ x ≤ min(a+p/L, b-q/U).

Necessity follows directly from the two secants. Sufficiency is constructive: insert (x,t) as an anchor, and linearly interpolate every segment. At an existing anchor, use the anchor itself rather than a zero-length segment. All slopes satisfy the constraints, and any secant crossing segments is a weighted average of their slopes. Thus every point in the interval is feasible, not merely bounded by a relaxation. No differentiability assumption is used.

With only endpoints and L=1/2, U=2, t=1/2, x lies in [1/4,3/4]. The lower endpoint is witnessed by slopes 2 then 2/3, the upper by 2/3 then 2. These are very different instruments despite identical end behavior and positive monotonicity. An authenticated (1/2,1/2) collapses the central range to a point; (1/2,3/8) shifts and narrows it to [9/16,3/4]. An inconsistent anchor is rejected, not silently repaired.

The width within a segment of horizontal span D and vertical span H is a concave symmetric function of p: the upper envelope here is the minimum of two affine functions, the lower the maximum of two. Its maximum occurs at p=H/2, yielding

    W = min(H/L - D, D - H/U).

For a family of identity anchors, H=D, with L=1/2,U=2, W=D/2. Among n intervals with such anchors, the largest span is at least 1/n, and equal spacing attains that lower bound. Thus the best worst-case interval width in this **identity-anchor setting** is 1/(2n). This does not establish optimal calibration when anchor ordinates are unknown in advance, nor an adaptive experiment strategy. Calibrating x where an uncertainty band is wide is a reasonable further hypothesis, not the result proved here.

Negative cases: if L=U=1 the mapping is fixed; if slope bounds are removed, interior ambiguity returns; if one chooses non-monotone or hysteretic maps, the inverse may cease to be single-valued. If the uncertainty derives from noisy anchor measurements rather than exact anchors, their compatibility cannot be treated as certain. The displayed interval is conditional on the declared class, not a confidence interval.

## Executed finite rehearsal and composition

The standard-library implementation uses exact fractions. A separate discrete census enumerates all 4^8=65,536 vectors of increments 1–4 in sixteenths of chart output across eight equally spaced x cells. Endpoint normalization retains 3,823 charts. It computes inverse positions by walking cumulative sums, independently of the continuous bound implementation. The centered and displaced anchor filters retain 961 and 440 charts respectively. Across 17 targets in each of three settings, all 51 enumerated intervals were contained in the analytical bounds; 39 attained both bounds exactly. The remaining 12 are useful negative evidence against treating grid enumeration as a proof of the continuum formula. The constructive witness is what establishes sharpness.

Run from the repository root:
    
    python research/expeditions/midpoint-without-name/midpoint_lab.py build/midpoint-254
    python -m unittest discover -s research/expeditions/midpoint-without-name -v

The original score uses nine identical gesture positions t=0,1/8,…,1 and maps x to the frequency parameter 200+800x Hz. Identity calibration gives 600 Hz at the center, the two extremizers 400 and 800 Hz. Each file is a 1.8 second 16 kHz mono PCM composition of nine enveloped triangular-wave notes. Integer arithmetic and phase resets make the opening and closing note samples exactly identical across files; the interior differs. Identical endpoints are deliberately an auditory anchor, not proof of perceptual equality. No participant study was conducted. “Early” and “late” in the file names mean lower or higher x at a fixed chart t, not measured timing.

Listen in any order. Then listen again with the score in view. It may be artistically preferable to stop thinking of one recording as the faithful middle and the others as errors. Here the calibration law is itself the score. Another composition could hold the pitch path fixed and move the control coordinates instead; that would test a different proposition.

## Exaptation: the morph-law patch bay (proposed)

Presets usually store enough information to produce sounds, but a pair of stored sounds does not necessarily specify a transition between them. The proposed editor stores a domain, endpoints, typed coordinate units, reference law, optional anchors, slope or metric assumptions, and version/provenance. It exposes three different notions of position: the performer's physical control fraction, the chart fraction and a selected state/parameter value.

A musician may attach several morph laws to the same endpoints. A second performer can play the law without touching the endpoints. Constrain its slopes if bounded deviation is desired; audition the two extreme legal mappings and the chosen realization. A law change can be audible while the named endpoints stay invariant. Use explicit transport when changing representation rather than automatically recomputing a numeric midpoint. For parameters with order but no meaningful metric, use discrete anchor selection or expose the missing law; do not manufacture distance. For filters with meaningful frequency ratios, a log-law choice can be a declared design convention.

For MHAC, an urgency scale can be ordered without licensing statements about twice the urgency, half the action cost or equal intervals in required response time. Conversely, measured durations with units support appropriate arithmetic; treating every quantity as merely ordinal would remove useful information. Do not infer a safety mapping from this toy. A hypothetical design contract would require a scale type, an admissible transform family, the physical variable, the intended invariant and the failure behavior. Any listener comprehension benefit is an untested design hypothesis.

The richer artistic question is whether a performer can improvise *a geometry* rather than a note. Imagine a duo with one player selecting endpoints and the other reassigning the internal distances of the continuum. Their disagreement is not discord in the ordinary harmonic sense: it is disagreement about where the same hand movement leads. A third performer might control the constraint on that disagreement. This is a compositional proposal, not a claim about how humans actually experience control.

## Boundaries, sources and review

See [SOURCES.md](SOURCES.md) for exact reading extent and objections. [AFTERWORD.md](AFTERWORD.md) is fiction. No new canonical evidence, Brier claim, selected empirical corpus or human gate. No outside reviewer or participant. This expedition is AI-authored and self-tested (GPT-6.2, 2026-11-24); code checks and source inspection are not independent scholarly review. Related issues #197 (identity drift under a fixed metric), #228 (inconsistent pairwise magnitudes), #244 (unknown voting score convention), #252 (unobserved individual pairings) ask different questions. Here the same gesture fraction and same endpoints are known while the intermediate coordinate law is not. Base 495a98ca12bae467a507031f04931aa4254b1866. Scope additive only; no core programme gates advanced.
