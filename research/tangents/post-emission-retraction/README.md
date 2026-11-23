# MHAC-T014 — Post-emission retraction versus unknown recipient action

**Scope:** [issue #56](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/56). **Status:** bounded exploratory, synthetic-only prepass. Not an accepted R012 lifecycle, sound code, empirical Track E/G finding or real action controller.

## Stage G0: applicability and deduplication (limited GO)

A hypothetical, explicitly *non-operational* workshop/desktop machine speaks an actionable instruction to begin a calibration check. After its speech output has left the sender, a new diagnostic invalidates the original instruction. The machine does not observe whether the operator heard or started it. This fits the **proposed** functional chain and the explicit “correction after a wrong diagnosis” question in [PROJECT_FOUNDATIONS.md](../../../docs/PROJECT_FOUNDATIONS.md). It does **not** establish that any accepted product will require that workflow.

Deduplicated against live authority on **2026-11-04** (base `423649d18c54cbf90bf7bf79d49ba69b29f03848`):
- #33 / PR #35: recipient **requests** clarification/repair; the initiating event differs.
- #36 / PR #53: ongoing source condition and recovery/all-clear; an all-clear is not a receipt of withdrawn action.
- #47 / PR #48: queue **before original delivery**, freshness and unsent message coalescing. Here the original instruction was already *emitted* and action may have begun.
- #34 / #43 / #49 and PR #37/#44/#50: existing identity, addressee and mode controls are not replaced.
- #54 / PR #55: historical presupposition in speech, not sender-initiated post-emission action withdrawal.

The limited GO is to **try to falsify a naive closure inference** using authored fictional cases; no acceptance as a normative R012 specification is implied. A fully equivalent accepted R012 oracle, an outbound-only no-correction use case or a simpler valid countermodel remains a valid stop/revision reason. The hypothetical applicability is narrower than real medical, industrial or physical safety use.

## Semantic variables and guardrails

A case declares independent `original_message_id`, `source_id`, `event_id`, `intended_actor`, matching correction identity, original **emission**, original **delivery** (confirmed/unknown/failed), **current validity**, separately observed actor `action_state`, independent reversibility, *potential* correction-delivery result, and independent `resolution_verified`.

- `original_delivery=confirmed` is only a toy receipt proxy; it never implies comprehension or execution.
- `correction_delivery` is the **counterfactual channel result if a policy actually offers a correction**; it is not an observation for silent controls.
- `resolution_verified` is declared **independent synthetic world evidence**; it cannot be inferred from issuance, received speech or a task-status label. The one positive recovery case is intentionally artificial, not a guaranteed practical recovery protocol.
- `action_state=unknown` must remain unknown. Completed ≠ reversible; action not started ≠ instruction not heard; correction offered ≠ delivered; cancellation ≠ undo.
- Identity authority is *assumed* truthful in these fixtures; this is **not** a production security, identity or causally atomic evidence model.
- Deadlines and independent urgent messages are controlled scenario dimensions for a **text-token burden proxy**, not clocks, listener delays, audio overlaps or quantitative harms.
- No negative case authorizes a potentially unsafe "stop machinery" action. The toy speaks of messages, not physical operating steps.

### Four matched policy comparators

| Policy | Behavior | Failure it tests |
|---|---|---|
| `silent` | Never offers post-emission correction. | Minimal non-interference baseline; lacks withdrawal notification when genuinely due. |
| `generic-closure` | **Intentionally defective**: for any emitted, subsequently invalidated message, says to cancel the unspecified prior instruction and asserts receipt, stopped action and undone consequences. | Exposes wrong-target cancellation, erased unknowns and falsely closed obligations. It is a **negative control**, not an empirical model of typical commercial systems. |
| `bound-minimal` | Offers only a correctly source/event/actor/message-bound withdrawal, without a claim of action or restoration. | Simple lower-verbosity alternative that can falsify the need for additional correction narration. |
| `bound-uncertainty` | Same binding and conservative closure, plus an explicit caveat that listener action and consequences are unverified. | Tests whether more words yield any **symbolic** gain versus the simpler bound version; possible excess interruption burden. |

The only eligible correction offer in this rehearsal is: original emitted; original receipt not **known failed**; subsequently invalidated; matching *all four* correction identity fields; not already superseded. This is an **unvalidated convention** for a falsifier, not an empirical authorization rule. Corrections for a known-undelivered original could be optional status notifications in another system; this toy excludes them from the target obligation.

A policy's own `closed` declaration **cannot** satisfy the ground-truth obligation metric. The independent labels `expected_need` were authored with the fictional rows before the oracle was written, and `EXPECTED-METRICS.json` was separately calculated using JavaScript arithmetic; neither is independent scientific annotation. Mutation tests deliberately make authored expected labels disagree with eligibility logic and demand failure.

## Reproduce

From the repository root (Python 3.11+, standard library):

```sh
python -m unittest tests.test_post_emission_retraction_t014 -v
python -m unittest discover -s tests -v
python research/tangents/post-emission-retraction/replay.py --check --output /tmp/mhac-t014.json
python tools/validate.py
python -m tools.build_record_fixtures --check
```

`replay.py --check` performs structural assertions. The report is sorted-key, indented, stable JSON containing per-case outputs, policy-level metrics and explicit limitation statements. Do not commit a report from an unchecked execution or confuse a JavaScript cross-check with a Python test pass.

The attached material consists of **36 manually enumerated fictional cases**, **22 separately marked correction-offer positives** and **14 negative controls**, with receipt uncertainties, action underway/completed/unknown, irreversible consequences, wrong source/event/actor/old-message, missing emission, known failed delivery, already superseded instructions and an unrelated urgent message.

## Evidence, decision and ownership

[SOURCES.md](SOURCES.md) separates S267–S274 from accepted research, records bibliographic/identity caveats and contrasts helpful corrections against continued influence. [DECISION.md](DECISION.md) states the competing positive/null/negative findings, the token-cost proxy and possible later R008/R012–R014 handoff; no programme issue is amended.

Future listener comparison, **only if the R020 human gate is actually met**, would need an independently justified design with counterbalanced lexical content, verified actual audibility, intelligibility, response opportunities, delivery latency, interruption, hearing/language variability and an explicit action outcome. None of those are simulated observations here.

**AI disclosure:** GPT-6 developed the fictional fixtures, code, JS metric cross-check and manuscript text on 2026-11-04; linked GitHub repository and public original-source landing pages were consulted. No human participant, independent screener/reviewer, ethics approval, external submission, source ingestion, device control or production integration occurred.
