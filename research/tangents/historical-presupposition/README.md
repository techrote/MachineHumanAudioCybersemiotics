# MHAC-T013 — Historical presupposition versus present-state warrant

**Issue:** [#54](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/54) · **classification:** exploratory synthetic-only prepass · **base:** accepted `main` `423649d18c54cbf90bf7bf79d49ba69b29f03848` (2026-11-04 inspection) · **not** accepted Track E/G evidence, real listener observations, a production message policy, a semantic schema amendment or a safety guarantee.

## Mandatory applicability and duplication gate (limited GO)

The [project foundations](../../../docs/PROJECT_FOUNDATIONS.md) explicitly contemplate human-readable speech, persistence/lifecycle, provenance, time validity and changing machine states. A fictional workstation might say *“Pressure is high again; inspect the feed”* with a verified current high reading but **no verified previous high episode**. Its *present high* proposition can be true even if the extra *prior high* proposition is unknown or contradicted. No factual claim about an actual workstation is made.

Current accepted `main` contains **neither an accepted R012 state-model contract nor a current listener-facing speech implementation**, so this is a *limited, hypothetical applicability*, not a product requirement. Scope audit: #34/PR #37 tests overt source/event binding; #38/PR #39 tests command negation and action polarity; #36/PR #53 tests state and event closure; #47/PR #48 tests queues and deadlines; #49/PR #50 tests operating-mode permissions; #33/PR #35 addresses repair; #30/PR #32 addresses acoustic reception; #51/PR #52 addresses learned codebook migration. Their scopes do not separately label a **historical implication of a truthful current-state utterance**. That difference justifies this bounded negative control, **not** parallel edits to any of those PRs or claims that they fail.

**Stop/merge criterion:** if later R012 explicitly rules out retrospective wording, or formal source review finds it fully covered, archive these synthetic negative controls as a no-go/duplicate and do not create a temporal logic subsystem.

## Reproducible fictional truth contract

[30 manually labelled cases](cases.json) pair a present assertion with a possible temporal variant. Fixed fixture labels are written **independently of** the four policies in [replay.py](replay.py). Names/observations are invented; these are **not** a sample drawn from real-world incidents.

| Field(s) | Distinct meaning and hypothetical authority |
|---|---|
| `source_id`, `event_id` | Fictional source and event namespaces, not a physical device identity. |
| `current_observation`, `current_observed_at`, `current_truth` | Label whether the overt present assertion is `true`, `false`, or `unknown`, at fictional `t0`; truth is **assumed**, not inferred from a sensor. |
| `past_event_interval`, `prior_observation`, `observation_gap`, `temporal_reference` | Invented past evidence and temporal reference; a gap does **not** establish absence. |
| `history_support`, `presupposed_proposition`, `evidence_provenance` | Independent `supported`, `contradicted`, `unknown` or `not_applicable` label and what historical proposition a variant **might** communicate. Lexical effect is not asserted universal. |
| `requested_action`, `urgent`, `deadline_state`, `action_offer_valid` | A separate fictional permission/deadline contract; current factual truth does not by itself authorize an action. |
| `recipient_belief` | Always `not_observed`; there is no surrogate listener, action measurement or pseudo-response. |

**Authority assumptions:** all clocks and timestamps are fictional relative intervals; case labels stipulate source evidence as reliable for the example, but the replay does not verify its authenticity, continuity, revision lineage, clock accuracy or sensor validity. A known-negative historical label is used only when a bounded complete observation interval was explicitly stipulated. Contradictory or invalidated records remain `unknown`.

**Linguistic limits:** *again* here contrasts repeated high periods, *still* continuity over an explicit interval, *stopped* an active→inactive transition, and *resumed* an inactive→running transition. This is a **small illustrative interpretation**, not a comprehensive semantics of aspect, negation, temporal adverbs or conversational presupposition accommodation. The spoken strings are written text templates, not synthesized audio.

## Four predeclared comparators

| Policy | Deliberately narrow rule | Anticipated weakness |
|---|---|---|
| A `current_only` | If current fact true, issue neutral present statement; no historical implication | May omit useful warranted background; not tested on listener comprehension. |
| B `naive_history` | If current fact true and trigger exists, emit historical variant without checking past | Can emit an unwarranted historical claim even with current truth established. |
| C `evidence_guard` | Emit temporal variant only for `supported` history; otherwise issue same neutral present statement | May add complexity with no benefit over A; trust of history labels assumed. |
| D `present_plus_timeline` | Neutral spoken present statement, with optional separately inspectable history when `supported` | Text/visual inspection may be inaccessible or unavailable; not a measured preference. |

All policies independently **suppress false/unknown present factual assertions** and share the *same* declared action eligibility. This design isolates historical wording. Policies must not withhold a true, urgent and authorized present alert merely because its **past** is unknown. A naive `strict_history_suppress` gate would fail that condition on AG03/ST03/SP03/RS03 and is deliberately **not** an adopted comparator.

## Reproduction and adversarial controls

```sh
python research/tangents/historical-presupposition/replay.py --check
python -m unittest tests/test_historical_presupposition.py -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

The replay prints machine-readable metrics for every policy: emitted assertions, spoken **word count only** (not duration or acoustic load), historical offers, unsupported and known-contradicted historical offers, unknown promoted to known, separately inspectable timeline labels, action offers, invalid action offers, unsupported current assertions and missed valid urgent present alerts.

Fixture strata include repeated/continuous states and transitions; verified earlier events, bounded negative observations, gaps, conflicting and invalidated logs; explicit reference-window changes, nonurgent narration, known false or unknown current status, expired action windows, and present-only controls. The fixed set has 30 cases, **not randomized**. Mutation tests cover contradictory labels; case count does not constitute empirical power.

**Negative/positive examples:** AG02 (known-negative earlier high), AG03 (unknown earlier high yet correct urgent current high), ST02 (interrupted continuity), SP02 (no active→inactive change), RS02 (never stopped), AG01/ST01/SP01/RS01 (documented relevant history), NO03 (false current fact), NO05 (true current state but expired action). None predicts what a person believes.

## Traceability, limitations and handoff

- [SOURCES.md](SOURCES.md): eight source identities, verified access and counterpositions, including reading tasks and conditional presupposition accommodation. Formal R005/R006 identity/screening remains untouched.
- [DECISION.md](DECISION.md): policy comparison, conditional/null decisions and **proposed** R014 experiment outline.
- This package depends on [issue #54](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/54) and [scouting snapshot `486b5bb`](https://github.com/techrote/MachineHumanAudioCybersemiotics/commit/486b5bb58a7c88f6a0c3dde55e62add9387aabfe); no edits to research protocol, shared sources, accepted evidence or other issue paths.
- Research execution: GPT-6, 2026-11-04, connected GitHub and public source lookup; synthetic fixtures and comparator code AI-authored; check commands and outcomes must be reported from actual executions, not inferred from this README.
- **Human gate:** no recruitment, consent, recorded voices, real acoustic warning experiment, pilot approval, external review or device control. R020 still governs empirical participation.

**Scientific disposition:** Even if the symbolic replay passes, it proves only that these hand-specified policies obey these hand-specified truths; it cannot establish that historical wording changes recipient understanding, risk, workload, accessibility or response time.
