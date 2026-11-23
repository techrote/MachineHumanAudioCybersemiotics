# MHAC-X005 — exaptation ledger: X001's observation fibres become a silence theorem

This expedition contains a concrete example of the kind of intellectual sediment MHAC was designed to preserve.

## Origin

MHAC-X001, *The Observer's Solecism*, introduced a general observation-factorisation theorem while wandering from grammatical context into circle harmonics and Kaluza–Klein-inspired geometry.

In its abstract form:

- X is the set of complete hidden states;
- P maps a hidden state to an observation;
- V is a property/verdict of the hidden state.

A deterministic decoder D with

    V = D ∘ P

exists exactly when V is constant on every fibre of P.

That theorem did not originate as a distributed-systems result. It was developed to formalise the intuition that a judgement can depend on a contextual coordinate the observer never received.

## Reuse in X005

Let X contain two worlds at receiver horizon T:

- x₁: no alert was emitted;
- x₂: an alert was emitted at T/2 but is delivered only at 2T.

Let P_T(x) be the messages delivered to the receiver by T.

Then

    P_T(x₁) = P_T(x₂) = empty trace.

Now define

    V(x₁) = NO_ALERT_EXISTS
    V(x₂) = ALERT_EXISTS.

V is not constant on the empty-trace fibre.

Therefore the verdict cannot factor through P_T. No deterministic decoder of that finite receiver trace alone can always decide whether an alert exists in this two-world model.

After the delayed message arrives, P changes:

    P_3T(x₁) = empty
    P_3T(x₂) = [(2T, ALERT)].

The fibre splits and this particular verdict now factors through the refined observation.

The implementation exposes exactly this finite check through
`partition_by_prefix` and `property_factors_through_prefix`, with tests covering both horizons.

## Why this matters beyond elegance

This is not merely a shared metaphor.

X001's theorem supplies an exact diagnostic question for X005:

> Is the proposed semantic verdict constant across all hidden worlds compatible with the current observation?

That question can be asked of:

- “silence means resolved”;
- “no heartbeat means crashed”;
- “no notification means no obligation”;
- “no agent update means complete”;
- “no returned error means success.”

If compatible hidden worlds disagree on the verdict, the interface needs additional evidence, stronger assumptions or a weaker output such as UNKNOWN.

## What did not transfer

Most of X001 does **not** carry over.

- No Kaluza–Klein physics is needed.
- No circle harmonic or Fourier alias is needed.
- No moving-probe audio mapping is needed.
- No grammatical solecism claim becomes a network claim.

Only the abstract observation-fibre result transfers.

This selective reuse is precisely why preserving strange narrow results can be productive: an idea can shed its original scenery while retaining a useful formal skeleton.

## Intellectual-sediment consequence

X005 therefore provides one observed instance of internal MHAC exaptation:

1. an elementary theorem was produced in a speculative mathematics/philosophy/audio expedition;
2. a later independent expedition encountered a different problem;
3. the theorem gave the later problem a concise exact criterion;
4. code and tests now operationalise that criterion in the new domain.

That does **not** establish a general law that MHAC sprawl produces useful inventions. It is one documented transfer.

It is nevertheless stronger evidence for the value of preserving intellectual sediment than a purely hypothetical claim about future reuse.
