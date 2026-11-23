# MHAC-X005 — absence and negative-space type discipline

This is a **candidate conceptual type system**, not an accepted MHAC schema or production API.

Its purpose is to make illegal a common family of silent substitutions.

## Core types

### `PRESENT(value, provenance, valid_until)`

A positive observation or state report actually received.

It may later become stale without becoming false or resolved.

### `NO_DELIVERY(interval)`

The receiver observed no relevant delivery during a declared interval.

This is an observation about the channel/receiver history.

It is not automatically:

- NO_EVENT;
- RESOLVED;
- SAFE;
- CRASHED.

### `ERASURE(reference)`

The receiver has explicit evidence that a particular transmission/value was erased or unrecoverable.

Unlike bare NO_DELIVERY, erasure is itself a received/established event.

It still does not reveal the erased semantic value.

### `STALE(last_value, expired_at)`

A previously usable report whose declared validity has expired.

STALE retains historical information while refusing to pretend it is current.

### `UNKNOWN(reason?)`

The system lacks enough warranted information to choose among semantic alternatives.

UNKNOWN is not a world state. It is an epistemic state of the interface/receiver.

### `SUSPECTED_FAILURE(detector, score, evidence)`

A detector's graded or binary failure suspicion.

It should not be silently cast to CRASHED unless the surrounding model grants that detector such authority.

### `RESOLVED(event_id, provenance, observed_at)`

An explicit semantic resolution event or a conclusion licensed by a separately declared strong contract.

Resolution is about an event/obligation, not merely acoustic cessation.

### `MUTED / DISCONNECTED / RENDER_FAILURE`

Channel or presentation states, when independently observable.

These belong to a different namespace from source-event semantics.

## Illegal implicit casts

The following conversions are forbidden unless an application declares and justifies the additional contract:

    NO_DELIVERY -> RESOLVED
    NO_DELIVERY -> NO_EVENT
    NO_DELIVERY -> CRASHED
    STALE       -> RESOLVED
    SUSPECTED_FAILURE -> CRASHED
    MUTED       -> SOURCE_SILENT
    ERASURE     -> semantic zero
    acoustic_zero -> UNKNOWN

The last rule matters: even UNKNOWN is not “contained in silence.” UNKNOWN is a policy conclusion when the evidence is insufficient.

## Legal examples with explicit assumptions

### Bounded reliable slot

Contract:
- sender emits exactly one bit per slot;
- channel is reliable;
- delivery completes before slot end;
- clocks/slot boundaries are valid;
- silence within a completed slot is defined as bit 0.

Then:

    completed_slot + NO_TONE -> BIT_0

The information comes from the full contract plus observation.

### Lease expiry

Contract:
- ACTIVE is valid through T;
- no renewal observed by T;
- no explicit resolution.

Then:

    PRESENT(ACTIVE, valid_until=T) + now>T -> STALE/UNKNOWN

not RESOLVED.

### Explicit erasure

Contract:
- transport produces authenticated E when symbol recovery fails.

Then:

    E -> ERASURE

not 0 and not 1.

## Why a type discipline helps

Many communication failures are not caused by a bad inference algorithm but by allowing semantically different categories to share the same representational slot.

If a renderer accepts one generic enum:

    {ON, OFF}

it may be forced to collapse:

- inactive;
- cleared;
- unknown;
- disconnected;
- muted;
- expired;
- failed.

A richer internal type system can remain explicit even if the user-facing output later compresses states for a particular context.

## Compression rule

Compression is allowed only after declaring which distinctions are irrelevant **for that task**.

That is the opposite of beginning with an impoverished acoustic/display vocabulary and pretending the world contains only what the vocabulary can express.

## Relationship to existing MHAC

This type discipline is aligned with several established MHAC research habits:

- acknowledgement != understanding != resolution;
- observation != diagnosis;
- urgency != consequence;
- physical cue independence != semantic/perceptual independence;
- source state != channel state.

But X005 does not claim these parallels create one universal ontology.

The candidate types are merely a compact reusable engineering artifact produced by this expedition.
