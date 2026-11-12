# Fictional truth and policy contract

Every `FICTIONAL-TRACES.tsv` row declares independent **fictional assumptions**, not measurements. `source_id` and `event_id` label the source and incident; `message_ver` is the illustrative instruction version; `true_ver` is the scripted action-time machine-state epoch; `observed_ver` is potentially stale. `attested=yes` declares an ideal trustworthy action-time readback; the fixture loader checks its consistency with scripted actual mode/version. **This is not a physical interlock, secure clock or real API.**

`event_mode`, `compile_mode`, `delivery_mode` and `action_mode` explicitly separate real fictional state at different times. `origin` records commanded, uncommanded, conflicting, unknown or external transition origin. `observed_mode` and `observed_ver` represent accessible readback; `?` and `conflict` cannot be silently made certain. `allowed` is the authored action-mode permission (`*` denotes mode independence). `actor` and `authorized` are fictional actor/permission fields. `source_truth`, `required`, `clock`, `deadline`, `action_time`, `ack`, `completed`, `duplicate` and `visual_sufficient` are separate. **Actual listener belief, detection, understanding, attention and executed action remain unknown in every case.**

The oracle `truth()` evaluates the scripted obligation, source, authorization, deadline and action-time mode **without using the result of any comparator**. Its exclusive categories are `valid`, `not_required`, `invalid_source`, `unknown_source`, `wrong_actor`, `unknown_actor`, `expired`, `unknown_clock_or_deadline`, `wrong_mode` and `unknown_mode`. This is a specified truth table, not observed human or field data.

## Hypothetical comparators

| Policy | Definition and deliberate limitations |
|---|---|
| A unqualified imperative | Always offer one audible instruction; intentionally unsafe negative comparator. |
| B narrate all mode transitions | Same unguarded imperative, plus one audible unit for every known stage-to-stage true mode change. **Optimistic access to transition truth**, no proof of reception. |
| C conditional precondition + guard | Offer a mode-sensitive two-unit spoken instruction only with externally attested current mode/version, known source/actor/deadline and unresolved nonduplicate obligation; otherwise abstain. For mode-independent actions, mode readback is irrelevant. |
| D visual/peripheral + guard | Same conditional eligibility as C but inspectable *visual* information, no added audio; no assumption the user actually sees it or that visual accessibility is superior. |
| E no-action control | Offer nothing; prevents bad offers but misses obligations. Not an endorsed global solution. |

C/D assume verified source/actor authority, an accurate monotone epoch, consistent current-mode attestation and trustworthy clock **at the decisive moment**. The policy guard does not read the scripted `action_mode` field, although the fixture's externally declared attestation is idealized. If real state changes after readback or a sensor reports a false epoch, its symbolic guarantee fails; no control of real actions is provided.

## Non-overlapping measures

`wrong_mode_offer`, `wrong_actor_offer`, `expired_offer`, `invalid_or_unknown_offer` and `false_known_state` count **fictional offers** with problematic scripted truth, not actual actions. `missed_valid_action` excludes duplicate obligations and counts valid actions withheld. `duplicate_offer` is reported separately. `audio_units` and `visual_units` are declared semantic chunks, **not** words, sound pressure, workload, speech duration, accessibility, user effort or reaction time. Categories can overlap; do not add them as mutually exclusive events. The `unresolved_ack` per-case flag is not an independent behavioral outcome or evidence of completed action.
