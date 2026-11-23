# MHAC-X005 — negative information: three different ways silence can matter

The phrase “absence of evidence is not evidence of absence” is too blunt for X005.

Sometimes non-observation is logically inconclusive. Sometimes an application adopts a closed-world convention and treats missing information as false. Sometimes repeated non-detection is legitimate **probabilistic evidence** against a hypothesis. These are different inference regimes.

## Temporal eventuality: finite silence and liveness

Alpern and Schneider's 1985 definition captures a liveness property as one for which **every finite partial execution can still be extended to satisfy the property**.

Take the property:

    EVENTUALLY_DELIVERED = “an ALERT is eventually delivered”

with no deadline.

After any finite silent receiver prefix, it remains possible to append a later ALERT. Therefore that finite prefix does not refute the eventuality.

The X005 implementation exposes a tiny three-valued monitor:

- ALERT already delivered by the observation horizon -> SATISFIED;
- no ALERT yet and no deadline -> INCONCLUSIVE;
- no ALERT by a declared hard deadline -> VIOLATED.

This is deliberately narrower than general temporal logic. It shows why adding a deadline changes the epistemic character of silence.

### Deadline as assumption

A deadline is not a magic property of time. The application must have authority to say that delivery *after* the deadline no longer satisfies the requirement.

Thus:

    “nothing yet” at t=4.9, deadline 5.0 -> INCONCLUSIVE
    “nothing yet” at t=5.0, deadline 5.0 -> VIOLATED

for that bounded requirement.

The unbounded liveness statement remains a different property.

## Open world: missing assertion is not negation

Reiter's closed-world database work makes the convention explicit.

Under an open-world reading, if the database cannot prove

    ALERT_EXISTS

and cannot prove

    NOT ALERT_EXISTS

then the query is unresolved.

A closed-world system may instead adopt a rule that a positive ground literal not derivable from the database is treated as false.

That can be useful. It is also an **assumption about completeness**.

The W3C's OWL material gives the complementary intuition: failing to assert that an individual belongs to a class does not by itself imply membership in the complement class. The ontology may simply lack the information.

X005's tiny open_world_query helper is not an OWL or deductive-database engine. It merely makes the policy switch visible:

    missing ALERT_EXISTS, open world   -> UNKNOWN
    missing ALERT_EXISTS, closed world -> FALSE

The output changed because the reasoning contract changed, not because a new observation arrived.

## Statistical silence: non-detection can update belief

Now suppose silence is not interpreted deductively at all.

Let:

- H1: an event is present;
- H0: the event is absent;
- q = probability of a detection opportunity firing when H1 is true;
- f = false-positive probability per opportunity under H0;
- n = conditionally independent opportunities.

For n observations containing **no detections**:

    P(no detections | H1) = (1-q)^n
    P(no detections | H0) = (1-f)^n

With prior probability p = P(H1), Bayes gives

    P(H1 | no detections)
      = p(1-q)^n
        / [p(1-q)^n + (1-p)(1-f)^n].

If q > f, repeated non-detection usually pushes probability downward.

For p=0.5, q=0.8, f=0.05:

- one non-detection reduces the event probability substantially below 0.5;
- five independent non-detections reduce it further;
- the probability remains above zero unless assumptions make the no-detection likelihood under H1 exactly zero.

If q=f, non-detection has equal likelihood under both hypotheses and leaves the prior unchanged.

The Python implementation tests both cases.

### Why this does not contradict the finite-prefix theorem

The finite-prefix theorem says the observation does not **deductively distinguish** two possible worlds when both can generate the same prefix.

Bayesian inference says the same observation can have **different likelihood** under those worlds and therefore rationally change relative belief.

A world can remain possible while becoming unlikely.

This is a productive distinction for MHAC:

    impossible / ruled out
    improbable under model
    unsupported
    unknown

should not be collapsed.

## Four notions of “negative information”

X005 therefore distinguishes at least four mechanisms.

| Mechanism | What supplies the negative information? | Example |
| --- | --- | --- |
| Logical contradiction | premises entail the negation | explicit incompatible state |
| Closed-world convention | declared completeness rule | fact absent from complete table |
| Temporal contract | deadline/bound turns future possibility into violation | no required delivery by t=D |
| Statistical evidence | non-detection likelihood differs across hypotheses | sensitive detector stays quiet |

A fifth case—**explicit negative message**—is simpler still: the sender directly reports “no event.”

All differ from raw, unstructured acoustic silence.

## Design implication

A user interface should ideally expose which kind of negative conclusion it is presenting.

Examples:

- “No alert recorded” — observation/report.
- “No alert exists” — strong world claim.
- “No alert expected before deadline” — predictive claim.
- “Alert unlikely (detector quiet)” — probabilistic claim.
- “Status unknown” — epistemic result.
- “Resolved” — lifecycle claim.

They may be rendered compactly, but the internal representation should not erase the distinction before rendering.

## Counterexample to X005's own rhetorical instinct

If a sensor is known to have perfect sensitivity, zero false positives, instantaneous reliable delivery, and complete coverage for a declared interval, then silence during that interval **does** prove absence under the model.

The correct X005 response is not to object that silence can never prove anything.

It is to ask:

> Which assumptions made that proof possible, and how are violations of those assumptions represented?

That is the actual far-horizon lesson.
