# MHAC-X004 — genealogies through accepted and shadow sediment

This note follows a few concepts manually across current main and open historical branches. It is intentionally not an automated genealogy claim. Explicit citations, issue relationships and shared instructions make inheritance likely; the point is to record **how the operational role changes**.

Branch-only material is labelled shadow sediment and is not promoted to accepted MHAC research.

## Repair: from conversational recovery to obligation-preserving lifecycle

### Foundational main

PROJECT_FOUNDATIONS already treats response/repair as part of the communication chain and states that:
- signal emission does not prove reception;
- acknowledgement does not prove understanding;
- acknowledgement does not prove resolution.

This establishes the initial typed separation.

### T003 shadow branch — recipient-initiated repair

Open PR #35 turns that distinction into a proposed state machine.

Its STATE-MACHINE separates:
- delivery;
- interpretation report;
- acknowledgement;
- action report;
- resolution report;
- repair request/control state.

The branch explicitly says acknowledgement never implies interpretation, action or resolution, and that action/receipt/acknowledgement cannot promote resolution.

This is a transformation from a prose distinction into executable state-transition invariants and fictional adversarial traces.

Status: unmerged shadow sediment.

### T014 shadow branch — sender-initiated correction after emission

Open PR #57 changes the repair direction. The recipient does not ask for clarification; the sender discovers that an already-emitted instruction became invalid.

The branch now separates:
- emission from confirmed delivery;
- heard from acted upon;
- cancellation from undo;
- completion from reversibility;
- correction offered from correction delivered;
- policy-declared closure from independently verified resolution.

The inherited anti-collapse posture is applied to **obligation correction under unknown action**, not merely conversational misunderstanding.

Status: unmerged shadow sediment.

### T018 main — social repair versus task repair

The affect-feedback tangent applies “repair” to agentic collaboration:

> social repair success is not task repair success.

An apology can calm an interaction without repairing the implementation. Conversely, a blunt technical correction can be accurate while worsening communication.

The motif has migrated from warning lifecycle semantics into human–agent work coordination.

### Genealogical disposition

This is not independent convergence. T014 explicitly names T003; T018 was written with earlier MHAC repair work available.

It is nevertheless more than repeated vocabulary: each stage introduces a different state space and different failure conditions.

**Classification: L2 transformed reuse** under X004's evidence ladder.

## Unknown: from epistemic field to conserved state

### Protocol/main

The concept register separates message certainty, evidence certainty and listener confidence. PROJECT_FOUNDATIONS instructs that unknowns remain unknown.

### T003 shadow branch

Unknown becomes an explicit state-machine value. A fluent reply may be cannot_answer; lack of evidence must not silently promote unknown to known.

### T013 shadow branch — historical presupposition

Open PR #55 adds a subtle distinction:
- historically unsupported does not necessarily mean historically false.

Its negative cases treat an unobserved earlier interval as unknown rather than known-negative. Present-state truth can coexist with unsupported wording such as “again.”

The concept of unknown has moved from a confidence field to a **temporal-provenance constraint on linguistic presupposition**.

### T014 shadow branch

Unknown becomes an actor-state invariant: action_state=unknown must remain unknown even if a corrective message is emitted. A policy cannot manufacture evidence of whether the recipient acted.

### T018 main

The same restraint is applied to human interpretation: text may display frustration, praise or vulnerability, but the assistant should not treat that as authenticated measurement of private emotional state, sleep status or capacity.

### Genealogical disposition

Across these uses, “unknown” becomes less a scalar lack of confidence and more a **conserved epistemic status that downstream fluency must not erase**.

That is a substantive transformation.

Classification: **L2 transformed reuse**, with explicit/common programme ancestry.

## Binding: from source identity to contextual coordinates

### Early programme

MHAC repeatedly distinguishes source identity, event identity, action and addressee.

### T003 / T014 shadow branches

Repair and correction messages are bound to message/source/event/version/actor identities. A correction with the wrong binding cannot close the obligation.

### X001 main

The observation-fibre theorem generalises a related formal problem: two full states can map to one observation even though a downstream verdict differs. The missing variable is not called binding, but the mathematical structure supplies a test for insufficient observable state.

### X002 main

Directional deixis makes the missing variable a coordinate frame. Knowing the addressee is insufficient if the frame used to interpret “left” is unknown. A frame label itself is insufficient if its transform is stale.

Identity binding has migrated into **reference-frame binding plus validity of the transform**.

Classification: between L1 distributed reuse and L2 transformed reuse. X002 explicitly cites X001, while its robotics-frame machinery is genuinely different.

## Separation as a reusable problem-solving operator

Across these genealogies, the recurring object may not be a doctrine at all. It may be an operator:

1. identify two quantities being treated as one;
2. construct a case where they diverge;
3. represent them separately;
4. test whether the separation changes an action, inference or failure;
5. retain the simpler collapsed model if no discriminating case exists.

This operator appears in rigorous and speculative work alike.

It resembles a **research move** more than a proposition. That may explain why lexical concept tracking alone performs poorly: the stable object is partly procedural.

A future X004 method should therefore track transformations of argumentative operations, not only nouns.

## Why shadow sediment matters

If X004 had read accepted main only, T003/T013/T014 would largely disappear from the genealogy even though later work can cite their issues/PRs and scheduled agents may inspect them.

This creates a repository-specific kind of selection bias:
- main shows what landed;
- branches show explored alternatives and rejected/incomplete machinery;
- issue bodies show intended questions;
- later work may inherit from any of them.

A far-horizon intellectual archaeology therefore needs at least two authorities:
- accepted-main sediment for what the programme currently endorses structurally;
- shadow sediment for what the programme has *thought through* without accepting.

Confusing those authorities would be worse than ignoring the branches entirely.

## Provisional conclusion

The strongest genealogy X004 can currently defend is not “the agents independently discovered a philosophy.”

It is:

> A typed-distinction problem-solving operator is repeatedly inherited, specialized and operationalized across MHAC's accepted and unmerged work.

That is a much narrower claim, but it has source paths, branch history, concrete transformations and falsifiers.

It is also exactly the kind of intellectual sediment that can later exapt into software tooling.
