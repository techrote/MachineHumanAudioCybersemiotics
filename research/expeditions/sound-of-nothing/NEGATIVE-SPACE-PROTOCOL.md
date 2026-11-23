# MHAC-X005 — candidate negative-space protocol

This is an engineering hypothesis extracted from X005, not an accepted MHAC R012/R013 requirement.

## Objective

Prevent a receiver from silently converting lack of updates into an unsupported positive state such as RESOLVED, SAFE, COMPLETE or FAILED.

## Message classes

### STATUS

A signed/identified observation with:
- source_id;
- event_id;
- semantic state;
- observed_at;
- valid_until;
- provenance/version.

Example meaning: “Event E is ACTIVE according to source S; this status is valid through t=20.”

### RESOLUTION

An explicit event stating that a particular source/event obligation is resolved.

Resolution is not inferred from status expiry.

### UNKNOWN

An explicit state used when evidence is missing, conflicting or stale.

### ERASURE / DELIVERY FAILURE

Optional explicit transport-level evidence that a message or update could not be recovered.

This is distinct from a semantic state.

## Receiver rule

For each tracked event:

1. If a current authenticated RESOLUTION exists, expose RESOLVED.
2. Else if a current valid STATUS exists, expose its declared semantic state.
3. Else expose UNKNOWN/STALE.
4. Never infer RESOLVED merely because an ACTIVE indication disappeared.
5. Never infer CRASHED merely because a heartbeat timeout fires; expose detector suspicion separately unless the system model gives stronger authority.

## Why leases are useful

A lease turns endless ambiguity into a bounded semantic policy without pretending to know the hidden cause.

Before expiry:
- the old state remains usable according to its contract.

After expiry:
- the system knows only that its status evidence is stale.

It does **not** need to decide whether the source crashed, the network failed, the user muted audio or the world changed.

## Audible rendering sketch

A possible auditory renderer could keep semantic and channel state separate:

- event active: learned state motif or continuous sonification;
- explicit resolved: discrete closing gesture;
- stale/unknown: separate low-bandwidth uncertainty marker or fallback display;
- transport failure: diagnostic channel marker not reused as event semantics.

This is only a hypothesis. T005 owns the actual continuous-state/event comparison, and human listening performance remains untested.

## Agentic adaptation

For long-running research agents:

- RUNNING status gets a lease;
- explicit BLOCKED includes blocker provenance;
- explicit COMPLETE includes artifact/commit/checkpoint reference;
- expired lease becomes UNKNOWN;
- silence is never auto-promoted to COMPLETE.

This could reduce ambiguous handoffs without requiring constant verbose chatter.

## Falsifiers

Reject or narrow this protocol if:

- the application has a simpler reliable synchronous contract where cessation already unambiguously means resolution;
- the extra UNKNOWN marker causes more harmful confusion than it prevents;
- an explicit resolution event cannot be reliably authenticated;
- accessibility constraints make the additional state unworkable;
- human testing shows the rendered distinction is not understood;
- another existing lifecycle protocol already supplies the same semantics more economically.
