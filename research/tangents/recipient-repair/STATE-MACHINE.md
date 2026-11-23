# MHAC-T003 — proposed symbolic lifecycle and tests

**Status: unvalidated convention / hypothesis, not R012 authority.** No listener studies, real clocks, speech synthesis, sensing, safety policy or safe-action recommendation. Every numeric bound in the Python rehearsal is a fictional unit chosen to falsify logical mistakes, **not a calibrated human deadline**.

## Separated state dimensions

- **Message identity:** message_id, source_id, event_id, state_version, issued_at, expires_at, nullable latest_safe_action, fallback_available. Null source/event/deadline means unknown, never a guessed value.
- **Delivery report:** emitted vs reported_received (does not prove hearing).
- **Interpretation report:** unknown, unclear, understood (does not prove correct comprehension).
- **Acknowledgement:** independent boolean, never implies interpretation, action or resolution.
- **Action report:** not_reported, attempted, completed, unable; late action is not timely action.
- **Resolution report:** unverified, resolved, unresolved, requiring an explicit fictional evidence_ref; action, receipt and acknowledgement cannot promote it.
- **Repair:** unique request_id, named type (repeat, which_source, which_event, what_action, why), and speech/button/text input channel. Responses are existing_info or cannot_answer; neither implies comprehension.
- **Control:** pending, reply available, cannot answer, version changed, explicit deadline/unknown/timeout/expired fallback, fallback unavailable.

## Transition and rejection rules

Every request/reply/acknowledgement is bound to the current message/version; replies also bind **source and event**. Pending requests are invalidated on a version update. A version update must increment by one, include provenance and reset all previously reported understanding, acknowledgement, resolution and action (a provenance token is *not* physical truth). An existing-info reply cannot silently upgrade an unknown source or event. Stale/wrong-source responses, reused request IDs, non-monotonic fictional timestamps and unsupported intents are rejected **transactionally**, leaving state unchanged.

A repair request is refused if the message is expired or if a deadline is unknown/too close for the fictional reply budget. Per-version and total request limits, one outstanding request, and an arbitrary response timeout prevent synthetic resend loops. On timeout, expired message or late response, the model enters terminal symbolic fallback for that version. Unavailable fallback is explicitly represented, **not replaced with an invented safe action**. Version change may reopen the candidate path; old replies cannot become current. A tick can mark a missed deadline, including omissions; an action completion after it remains late.

The fixture covers 39 invented cases, including receipt/ack without comprehension, separate resolution/action, source/event ambiguity, source binding mismatch, unknown promotion, stale answer after state update, conflicting versions, deadline, missing fallback, repeat budget, response loss, retry loops, text channel and atomic invalid events. Tests use the Python standard library and integrate with repository unittest discovery; they are not formal exhaustive verification.

## Fields, objections, rejection conditions, owner

| Field or rule | Evidence status | Counterposition and criterion for revising/rejecting | Downstream owner |
|---|---|---|---|
| message_id and event/source identity | Provisional convention / project distinction | One-shot alerts may need less state; field misbinding or excessive training could invalidate composition | #12/#13/#30 |
| state_version / provenance | Conservative convention | Tokens alone do not verify world state; reject if real data paths cannot preserve provenance/ordering | #12 |
| issued_at, expires_at, latest_safe_action | Unvalidated validity/deadline hypothesis | Real deadline might be unknown; a fixed timing assumption must never be claimed safe | #12/#14/#20 |
| fallback_available | Unvalidated convention | Fallback may itself be inaccessible/unsafe; reject deployment where no appropriate alternative exists | #13/#14/#20 |
| delivery / interpretation / ack | Proposed measurement separation | Self-reported understanding may diverge from accuracy; test against objective interpretation and action | #14/#30 |
| action / timely_action / resolution | Project semantic distinction | Correctness and consequence are not proved by completed action; require independent verification | #12/#14 |
| repair kind / input channel | S26/S27 analogy, not validated MHAC finding | ASR, hearing, language, motor and visual access costs may dominate; prefer button/text or reject | #13/#14 |
| request_id + reply source/event/version binding | Conservative test convention | Concurrent alarms and communication faults may defeat the simplification; run fault-injection | #12/#14 |
| cannot_answer / unknown | Project evidence-integrity distinction | A fluent answer without support can mislead; retain unknown unless verified update available | #12/#31 |
| max turns / timeout / reply budget | **Fictional numeric conventions** | No effect-size/threshold evidence; reject numbers and derive task-specific hypotheses if needed | #14/#20 |
| terminal fallback after timeout/deadline | Safety-oriented hypothesis, not certification | Fallback may waste scarce attention; compare correct action-by-deadline against simple conditions | #13/#14/#20 |

## Fundamental omissions

Only one current message/version is represented, not multiple concurrent alerts, network replay/security, distributed sensor consensus, causal correctness of real-world state updates or actual human interpretation. The fixture set is author-selected, finite and non-exhaustive; tests establish only deterministic consistency of the declared fictional transitions.
