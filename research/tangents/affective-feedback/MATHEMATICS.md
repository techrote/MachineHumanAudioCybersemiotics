# A toy model of self-reinforcing corrective interaction

**Status:** exact elementary mathematics for an *invented* dynamical system; no empirical parameters or calibrated psychological interpretation.

## 1. Variables, not diagnoses

Define a scalar p_t representing an abstract accumulation of **interaction pressure** at turn t. It is **not** the user's measured frustration, emotional state or sleep condition.

Let a_t be the assistant's synthetic degree of **accommodation**, e_t a signed **failure-cost signal**, and p_{t+1} the next pressure value.

Choose constant coefficients:

- r: pressure retention between turns, 0 ≤ r < 1.
- b: contribution of a failure signal to next-turn pressure, b ≥ 0.
- k: accommodation response to pressure, k ≥ 0.
- c: how accommodation changes future failure cost; c may be negative.
- q: fixed background pressure term.
- e0: fixed baseline failure-cost term.

The very simple update is

    a_t = k p_t
    e_t = e0 + c a_t
    p_(t+1) = q + r p_t + b e_t.

This is a **signed linear bookkeeping model**. Its values are not probabilities, event counts, sentiments, or error rates; p may exceed 1 and e can be negative. Such trajectories are analytically useful but cannot represent a complete human interaction.

## 2. Closed-loop gain and exact result

Substitute the first two equations into the third:

    p_(t+1) = (q + b e0) + (r + bck) p_t.

Let d = q + b e0 and g = r + bck. Then

    p_(t+1) = d + g p_t.

For g ≠ 1 and t ≥ 0,

    p_t = g^t p_0 + d (1 − g^t) / (1 − g).

For g = 1, p_t = p_0 + t d.

**Exact stability statement:** for the *homogeneous perturbation* p_t − p_t*, a constant equilibrium p*=d/(1−g) attracts all initial points exactly when |g|<1. At |g|>1, nonzero perturbations grow in magnitude; for |g|=1, asymptotic contraction fails. When g>1 and d,p0≥0 with some positive seed, the pressure can grow monotonically. This is a property of **these equations**, not of LLMs or users.

The case g>1 does *not* imply that a trajectory starting at exactly p0=d=0 will spontaneously grow. No seed, no motion—an important negative control.

## 3. Four contrasting invented worlds

| Scenario | r | b | k | c | Gain g | Interpretation limited to this toy |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Amplifying accommodation | 0.72 | 0.60 | 0.90 | 0.70 | **1.098** | positive-feedback unstable if perturbed |
| Bounded accommodation | 0.55 | 0.45 | 0.35 | 0.30 | **0.59725** | stable even though accommodation adds cost |
| Decoupled response | 0.55 | 0.45 | 0.00 | 0.70 | **0.55** | no pressure-driven accommodation |
| Useful accommodation | 0.60 | 0.40 | 0.50 | −0.30 | **0.54** | extra accommodation *reduces* failure-cost signal |

All have invented q=0.025, e0=0.05, p0=0.2, with other fields as in the generator source.

The useful-accommodation countercase matters: a model that treats emotional cues as signals to clarify requirements without abandoning judgement may improve task recovery. Our chosen sign c<0 permits that behaviour mathematically. There is no universal rule to set k=0.

## 4. What empirical work would have to prove

A real experiment would first have to measure whether expressed user affect **changes the assistant's substantive action policy** when task content is held constant, and whether any such change increases objectively measurable implementation errors or scope violations.

It must then distinguish long-run loops from serially correlated difficulties, new requirements, effects of user-supplied corrections, and assistant competency. Longitudinal causal identification is considerably harder than fitting the toy recurrence.

Even if an interaction displays escalation, the gain coefficients above cannot be estimated directly from a brief dialogue without a measurement model and assumptions.

## 5. Counterfactuals and stopping points

- If strong criticism produces better factual correction, then c<0 rather than c>0 may be appropriate; the bad loop is falsified in that task family.
- If the model shows no task-performance change under emotional framing, k≈0 and/or c≈0 could be adequate descriptions, even if prose style changes.
- If failures are independent of previous interactions, a simple capability deficit or ambiguous task specification may dominate.
- If the user explicitly *requests* an expanded scope, a larger diff is not necessarily a violation.
- If all responses are equally error-prone regardless of sentiment, adapting tone may be harmless in substantive terms, and suppressing empathy is not warranted.

**Takeaway:** the toy shows one precise way a frustration–accommodation–failure loop could be self-reinforcing *if* three proposed couplings exist and have sufficient gain. Its purpose is to force testable distinctions, not to anthropomorphise a model or psychologise the user.
