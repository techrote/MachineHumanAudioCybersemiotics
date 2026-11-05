# Typed fictional observation → decision → utterance contract

## Independent layers

| Layer | Source in scenario | Truth accessible to policy? | Purpose |
|---|---|---|---|
| World property | `ground_truth.actual_tenths`, `world_conforming` | **NO** | Gold constructed physical truth; separate from decision acceptability |
| Indicated measurement | `measurement.value_tenths`, quantity, unit, current, valid, uncertainty, displayed alternative | Yes | Observed input, possibly misleading or stale; no inference of world truth |
| Specification | `specification.upper_tenths` | Yes | Fictional nominal limit **50.0 PI** for world property |
| Decision rule | `rule.id/version/active/context/quantity/unit/accept_max/reject_min/risk` | Yes | Documented selected **toy** acceptance/rejection bands; may be absent, stale, inapplicable |
| Upstream evidence | `upstream.decision/authorized/current/evidence_trace/rule_id/rule_version` | Yes | Authority to assert a rule-specific class. Does not authorize an action |
| Independently labelled permissible speech | `ground_truth.permitted_class` | **NO** | Predeclared gold claim for scoring; never used in rendering |
| Listener/action outcomes | No data | **NO** | Not tested; `no_action_authorized=false` throughout |

All numeric quantities are integers in fabricated tenths of a **non-physical pressure index (PI)**. No uncertainty distribution is modeled. `uncertainty="declared"` means a relevant uncertainty process was declared, **not** that it was statistically calibrated. Rule `PI-R1` convention: accept <=49.0 PI, reject >=51.0 PI, otherwise report *indeterminate*. `PI-CONS` accept <=48.0; `PI-PERM` accept <=49.0 and reject >=52.0. These rules are **invented scenario premises**, not extracted from a standard. The `risk` label is explicitly not used to derive thresholds or safety actions.

In a constructed case, an **authorized claim can still be wrong about the world** if the observation differs from world truth. `T017-002` is a warranted rule-specific acceptance with actual nonconformity; `T017-006` is a warranted rejection of an actually conforming world. Conversely a lucky correct guess lacking rule authority remains *unsupported*. Do not collapse these into one accuracy measure.

## Contract invariants

1. Policy rendering never reads `ground_truth` or `independent_policy_expectations`.
2. An absent/inactive rule, a quantity or unit mismatch, stale measurement, unknown uncertainty or invalid reading blocks local rule classification.
3. A usable rule alone does **not** authorize rendering its result; upstream decision identity, version, current status, evidential trace and authorization must also match. A contradictory claimed class is refused.
4. Class `conforming` means only *accepted under stated fictional rule*, never **safe**. No policy can infer `no action required` from conformity: the intentionally defective naive comparator violates this.
5. `indeterminate` is a deliberate third label for the **fictional** rule, not a universal metrological requirement; direct categorical events without measurement-class inference are out of this experiment and remain an applicability counterexample.
6. Numerical rendering accuracy, semantic warrant and listener comprehension are different constructs. Token counts are not latency observations.

## Trace/mutation matrix

| Case IDs | Manipulation | Rival issue explicitly not duplicated |
|---|---|---|
| 001–008 | clear measured value; world-truth disagreement in 002/006 | #31 detector validity and alert base rates |
| 009–012 | matched observations in arbitrary indeterminate gap | #36 lifecycle/all-clear |
| 013–016 | nominal specification but **no selected decision rule** | #34 field binding |
| 017–020 | inactive/version drift/unauthorized/stale upstream decision | #47 queue age; #60 causal warrant |
| 021–024 | invalid/stale/unknown uncertainty observation | #58 source corroboration |
| 025–028 | wrong unit/quantity or contradictory upstream result | #38 spoken polarity; #41 acoustic recognition |
| 029–030 | identical measured value with different **declared** decision-risk preferences and acceptance boundaries | #31 Bayesian alert criterion; no invented risk equations |
| 031–032 | separate numeric transcription/rounding corruption | scouting pass 32; not an audio-perception experiment |

`FICTIONAL-CASES.json` contains the complete independently authored expected class for each of four policies, separate from the executable policy and the independent `ground_truth.permitted_class`. This is internally self-checked AI-authored toy truth, **not human independent adjudication**. Mutations in the tests establish that changing world labels cannot secretly change policy output.
