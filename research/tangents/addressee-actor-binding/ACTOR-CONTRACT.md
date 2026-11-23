# Provisional fictional actor/message contract

**Not an MHAC schema amendment, access-control specification or recommended production API.** See [README](README.md).

## Independent dimensions

| Field | Meaning and boundary |
|---|---|
| `source_id`, `event_id`, `message_id`, `state_version`, `requested_action`, `message_valid` | Fictional event/content truth; correct machine source does **not** imply addressee or actor authorization. |
| `audience_scope` | One of `explicit`, `group`, `broadcast`, `unknown`. Broadcast has no acoustic target; unknown is **not** silently broadcast. |
| `target_audience` | Declared intended acoustic recipients, empty for broadcast or unknown. A target is not necessarily authorized. |
| `heard_by`, `address_presentation` | Hypothetical audibility/presentation labels. They are **input assumptions**, never inferred listener detection. Labels such as clipped or near-homophone **do not** model acoustic physics. |
| `authorized_actors`, `authorization_version`, `message_auth_version` | Fictional externally supplied role truth and versions. A version mismatch invalidates action despite a valid source and observed address. |
| `acknowledgements`, `actions` | Separate actor/time/version observations; acknowledgement never grants permission. |
| `fallback_received_by` | Fictional non-audio delivery only, not a claim about accessible usability. |
| `expires_at`, `deadline` | Authority expiry and consequence deadline are different: an authorized but late action is possible. All times synthetic integer ticks. |
| `expected_authorized`, `expected_misrouted_ack` | **Independent declared fixture-label indices**, checked rather than inferred from a policy's output. |

## Truth oracle

A proposed action is authorized when message validity is true, the message and action both match current authorization version, actor belongs to the externally declared authorized set and action time is no later than authority expiry. This rule intentionally omits auditory delivery, audience recognition, acknowledgements and deadline: those remain independent outcomes. In particular, `audio_unavailable_no_fallback` may have a *permission-valid* attempt yet no known delivery. No human would be claimed to have made it.

A misrouted acknowledgement is by an actor not authorized under the same rule **or** outside a known target audience. Audience `unknown` does not manufacture a target. A successful actor can miss the deadline without losing permission truth. Wrong-first/correct-final is retained, rather than compressed into one success.

## Fail-closed and control invariants

A closed-field validator rejects duplicates/unknown actors, invalid scopes, malformed observations, Boolean-as-integer versions, invalid indices or contradictory scope/target declaration. Source labels and presentation metadata must not change symbolic permission truth. Explicit unknown targets are not silently treated as all actors. Cases with permission valid but no delivery must remain distinguishable. No model treats speaker identity, being addressed, noticing a word or acknowledgement as sufficient authorization.

**Construct threat:** the external authorized-actor set is a hypothetical oracle supplied with ground truth. Its apparent superiority may be tautological and proves **nothing** about real systems acquiring reliable permissions.
