# Competing provisional models and negative results

Five rules are compared against the *same* 31 declared fictional action attempts (30 cases). Their outputs are decisions a hypothetical policy **would allow**, not measurements of people taking those actions.

| Rule | TP | FN | FP | TN | Design assumption |
|---|---:|---:|---:|---:|---|
| `source_event_only` | 16 | 0 | 14 | 1 | Message valid ⇒ accept regardless of actor; deliberately unsafe straw baseline |
| `external_authorization` | 16 | 0 | 0 | 15 | Reliable up-to-date external role truth available (oracle advantage) |
| `audience_gate` | 12 | 4 | 0 | 15 | Authorization plus addressed & audio-received actor |
| `confirmation_gate` | 3 | 13 | 0 | 15 | Above plus timely same-actor acknowledged message |
| `accessible_fallback_gate` | 13 | 3 | 0 | 15 | Authorization plus addressed & audio **or** alternative-channel delivery |

Counts are **mechanically asserted regression values**, not empirical sensitivity/specificity estimates; they are strongly shaped by hand-chosen cases. A TP means a rule permits a truth-authorized attempted action; a false negative means a rule disallows one. This table must not be interpreted as comparative human, clinical, aviation or cybersecurity effectiveness.

### Diagnostic contrasts

- **Independent falsifier:** `near_homophone` and `broadcast_wrong_actor` retain valid source/event content, but the source/event-only rule permits actions by unauthorised actors.
- **Simpler model can suffice:** for `broadcast_external_permission` and `actor_irrelevant_broadcast`, external role control suffices without acoustic address grammar. No demonstrated value from adding explicit acoustic targeting here.
- **More checks can cost availability:** `correct_action_without_ack` and `missing_address` pass external actor-truth but fail confirmation or target-based gates. Acknowledgement cannot be assumed universally mandatory.
- **Delivery is not permission:** `fallback_non_audio` is permitted by the fictional fallback gate, but absence of audio without a fallback does not imply permission loss. Conversely, hearing a message does not confer authority.
- **Role and time conflicts:** stale message/action version or expired authority must fail even when the fictional recipient name matches. `late_corrective_readback` and `wrong_then_correct_after_deadline` contain authorized but overdue actions.
- **Unknown/uncertainty:** address metadata is not a synthesised waveform or a measured recognition probability. Similar-sounding, clipped, masked or translated recipient labels remain conjectural human confounders.

**Negative result:** under perfect external authorization, adding an acoustic audience gate has no improvement in false accepts on these fictional fixtures and increases false rejects. This is a meaningful null/scope-narrowing result **within the stated synthetic contract**, not a general conclusion against addressing. Independent receiver-state ground truth and actual listener trials would be needed to support a human inference.
