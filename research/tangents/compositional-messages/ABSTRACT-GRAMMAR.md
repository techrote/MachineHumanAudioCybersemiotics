# Fictional abstract grammar and binding oracle (v0, not sound design)

## Normative status

All tokens, legal pairs and training examples are **made-up research conventions**. Syntactic acceptance in `protocol.py` means only that a known token and labelled field agree. It does *not* imply a listener recognises either component, retains the message, binds it correctly or acts safely.

## Envelope / fields

```text
Message = (source, event, source_token, event_token, event_id, version, mechanism, mode_specific)
source ∈ {pump, door, fan, unknown}
event ∈ {fault, open, stopped, unknown}
source_token = 's:' + named_source; event_token = 'e:' + named_event
event_id = nonblank event identifier within source namespace
version = positive integer, strictly increasing for each (source,event_id)
mechanism ∈ {flat, serial, parallel, hybrid}
```

Legal fictional pairs: `pump/fault`, `pump/stopped`, `door/open`, `door/fault`, `fan/fault`, `fan/stopped`. Training exemplars: `pump/fault`, `door/open`, `fan/stopped`. The other three are **held-out legal pairs**. All other known pairs are illegal; unknown values return **unresolved**, never a successful assignment. No production meaning attaches to “fault”, “open” or “stopped”.

Mechanism-specific rules: serial must declare ordered fields `["source","event"]`; parallel must explicitly declare `binding:"tagged"` (otherwise undecidable by this oracle, not a validated acoustic tag); hybrid must declare an `explicit` fallback; flat has only three trained whole-pair tokens and cannot represent held-out pairs without inventing training. Parallel tagging is a symbolic **assumption**, *not* a technique established as perceptually disambiguating.

## Identity and transactions

A message's **event identity** is `(source,event_id)`; a reused identity with a different event fails closed; versions cannot regress or repeat. An independent concurrent alarm is a **separate message envelope**, not the two components of one composed message. A batch with the same identity+version twice fails collision checking. A rejected/unresolved batch cannot commit partial in-memory state. State is ephemeral to each fictional case; this is **not** an implementation of actual alarm handling.

The `accept` / `reject` / `unresolved` labels report a formal oracle decision. They are not human response scores, and `reject` does not mean a human would reject the signal. A label `held_out:true` only means *not in the invented training set*, never that a participant generalised successfully.

## Adversarial inventory and invariants

[SYNTHETIC-CASES.json](SYNTHETIC-CASES.json) declares 24 fictional examples: trained and held-out serial/parallel/hybrid, trained/held-out flat, token swaps, missing fields, illegal pairs, unknowns, absent parallel binding, incorrect order, missing accessible fallback, two truly independent concurrent messages, duplicate identities, stale/replayed versions, legitimate version advance, event-ID reuse for conflicting events, atomic batch failure and type errors. The automated tests assert the declared oracle outcomes.

**Not modelled:** auditory discriminability, signal synthesis, sound energy, hearing aids, culture, urgency, listener learning, true latency, error probability, hazard resolution, real-life concurrency or security-resistant ID generation. An eventual empirical protocol must address these before adopting any semantic code.
