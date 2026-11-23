# T015 fictional truth and communication contract

## Distinct variables

Each of 40 authored cases has **two** hypothetical messages, not real alarms. Event and actor labels are constructed, and the validator rejects silent unknown promotion.

| Field | Meaning / must not be conflated with |
|---|---|
| `message_id` | This particular emitted message identity; not a sensor reading or truth |
| `source_device` | Annunciator/device identity; different devices may relay one observation |
| `observation_id` | Identity of a reading; distinct readings may share a failure cause |
| `upstream_lineage_id` | *Assumed* causal provenance known for a fictional case, else `null`; does not authenticate itself |
| `dependency_relation` | **same_observation**, **common_cause**, **verified_independent**, **unknown**: separate from spatial/acoustic grouping |
| `event_id`, `event_truth` | Fictional world event and true/false/unknown; not the credibility of the spoken claim |
| `action_id`, `action_obligation` | Desired distinct action and required/none/unknown; separate from hazard or evidence count |
| `authorized_actor` | Fictional action authority, not automatically inferred from who hears audio |
| `emitted_at_s`, `deadline_s`, `expires_at_s` | Emission time, action deadline and temporal validity; no clock synchronization modeled |
| `delivery_group`, `cue_identity` | Audible co-presentation and code identity, not epistemic independence |
| `gold.required_obligations` | Author-labelled action keys `event_id/action_id`; one action key can be supported by two reports |
| `gold.independent_eligible_message_ids` | Author-labelled independently warranted *message identities*, including independent observations of the same event/action |
| `case_kind` | Positive target or explicit negative/control; there are 20 negative/control cases |

**Relation constraints:** same observation requires equal observation + known lineage; common cause distinct observations + shared known lineage; verified independent distinct observation + different known lineages; unknown **at least one unresolved lineage**. Identical source IDs do not imply same observation. Distinct IDs do not prove independence. Fictitious "verified" means stipulated by the author, not independently certified sensor truth. The truth validator requires same event ID to have consistent world truth within a case.

**Idealized applicability restriction:** all four comparators receive a *perfect fictional eligibility filter* (`event_truth=true`, `action_obligation=required`, actor `OP-A`, emission before deadline and expiration). This factor isolation is purposely unrealistic; a real machine may not know truth or actor authority. Therefore unsupported offers and deadline-expired offers are structurally zero by construction, not demonstrated safety properties. An unreliable/unknown source must not become known merely from dual audible occurrence.

## Pre-authored cases and controls

The `gold` fields were entered in the case specifications independently of the policy functions and frozen alongside scenarios. Their internal consistency is checked against the typed fictional contract but **their correctness is not independent human annotation**. Contradictory mutations must be rejected. Cases cover same observation, common cause, verified independence and unknown provenance; simultaneity vs 22-second separation; one/two devices, one/two symbolic cues; distinct events and same-event multiple actions; wrong actor, false/unknown world truth, expired messages, no action and short deadlines. Voice personas, acoustic waveforms, posterior probabilities and sensor authentication are **absent**.

## Four policies

- **A — proximity:** two messages within 3 fictitious seconds are counted as independent; within that window deduplication retains only first message of an event, ignoring distinct actions. Both shortcuts are deliberately defective.
- **B — device-ID:** two nominal devices counted as independent; a short-window duplicate from one device is suppressed even when another event/action obligation exists. Deliberately defective.
- **C — lineage:** preserve unknown; claim independent only for `verified_independent`; suppress only same observation + event + action. Assumes trustworthy, complete lineage metadata and a **four-word per message** verbal annotation proxy, not a production audio format.
- **D — separate:** deliver every independently eligible message, never claim corroboration or automatically suppress. D is the **minimal nonaggregation null comparator**. Its failure to *announce* a true independent relation is not the same as false corroboration.

**Metrics:** false corroboration is an independence *assertion* on nonverified cases; unreported independence means policy abstention or underreporting, not necessarily listener harm; missed required action means an authored action key loses all eligible offers; lost independent alert means a distinct verified observation fails to be reported; message count and token/delay proxies assume eight or twelve fictional words/message and 2.5 words/second **serially**. These are arbitrary work-budget conventions, not audibility, time-on-task or human decision outcomes.