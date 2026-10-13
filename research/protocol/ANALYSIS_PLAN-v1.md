# Track E analysis plan — version 1

[Protocol](PROTOCOL-v1.md) · [Glossary](GLOSSARY-v1.md) · [Freeze record](FREEZE.md)

**Frozen with protocol v1 on 2026-10-13, before any Track E production search, selection or effect extraction.** It specifies estimands, synthesis membership, pooling eligibility, dependence and missing-data handling, and the non-pooling route. It adopts, with the modifications listed in §1, the archived [quantitative-methods prepass](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/007559214bf3fe2f2a00f9151fa7e3462cec9bf3/checkpoints/prepass/MHAC-R002/d0a736be70ce/HANDOFF.md) (decisions D01–D14 and proposed clauses, 2026-10-04). That prepass's method sources (Cochrane Handbook v6.5 chapters 5, 6, 9, 10, 12 and 23; ICH E9(R1); Lakens 2013; SWiM; NASA-TLX overview; Heitz 2014; metafor and clubSandwich documentation; Röver et al. 2015) were read in the prepass, not re-read for this freeze. SWiM and Cochrane Handbook chapter 11 were read (tool-mediated) for this freeze.

## Contents

| § | Section | One-line summary |
|---|---|---|
| 1 | [Adoption of the prepass](#1-adoption-of-the-prepass) | Which prepass decisions are adopted, modified or deferred. |
| 2 | [Outcome families](#2-outcome-families) | O1–O12 with default effect scales and non-equivalences. |
| 3 | [Two-pass extraction and cell formation](#3-two-pass-extraction-and-cell-formation) | Cells are fixed from study characteristics before any effect is extracted. |
| 4 | [Effect measures and standardization](#4-effect-measures-and-standardization) | Raw units first; SMD only with a named standardizer. |
| 5 | [Extraction fields](#5-extraction-fields) | COMMON field groups required before numerical synthesis. |
| 6 | [Dependence and missing data](#6-dependence-and-missing-data) | Identity before counting; covariance provenance; no silent imputation. |
| 7 | [Pooling eligibility and model](#7-pooling-eligibility-and-model) | At least five independent components; REML with modified HKSJ after known-answer tests. |
| 8 | [Network meta-analysis](#8-network-meta-analysis) | Not planned, with reasons. |
| 9 | [Non-pooled synthesis](#9-non-pooled-synthesis) | SWiM-structured presentation and reason codes. |
| 10 | [Heterogeneity, sensitivity, multiplicity and reporting bias](#10-heterogeneity-sensitivity-multiplicity-and-reporting-bias) | What is examined, and when it is not. |
| 11 | [Interpretation conventions](#11-interpretation-conventions) | Display-only thresholds declared as unvalidated conventions. |
| 12 | [Implementation and verification](#12-implementation-and-verification) | Code, tests and what CI cannot establish. |

## 1. Adoption of the prepass

| Prepass decision | v1 status | Modification |
|---|---|---|
| D01 recognition | Adopted as O2 | Chance level and set size are mandatory fields. |
| D02 correct action | Adopted as O3 | Deadline and repair policy fixed per task class in pass 1 (§3). |
| D03 detection vs identification | Adopted as O1 vs O2 | — |
| D04 latency | Adopted as O4 | Clock origin coded `onset`, `offset` or `unknown`; `unknown` cells are not pooled with known origins. |
| D05 fixed-dose learning | Adopted within O5 | — |
| D06 training to criterion | Adopted within O5 | Non-learners must be reported or the result is non-pooled. |
| D07 retention | Adopted as O6 | Windows fixed: immediate < 1 h; short 1 h–7 d; long > 7 d (glossary G21). |
| D08 workload | Adopted as O7 | — |
| D09 repeated measures | Adopted | Correlation sensitivity grid fixed (§6.3). |
| D10 shared controls | Adopted | — |
| D11 multiple publications | Adopted | Identity rules in protocol §6.4. |
| D12 missing variance | Adopted | No SD imputation in primary analyses (§6.4). |
| D13 synthesis or non-pooling | Adopted | Five-component threshold retained (§7). |
| D14 multiplicity and dependence-aware models | Adopted as conditional | CR2/Satterthwaite only under §7.4 conditions. |

The prepass's synthetic fixtures, prototype code and proposed patch remain archival. They are not live records and are not applied by this freeze.

## 2. Outcome families

| Code | Family | Default effect scale | Must stay distinct from |
|---|---|---|---|
| O1 | Detection | Hit and false-alarm rates, or a reported sensitivity index with its formula | O2 |
| O2 | Recognition/identification | Marginal risk difference in percentage points (participant-average accuracy unless trial weighting is the reported estimand) | O1, O3 |
| O3 | Correct action within the task deadline and repair policy | Marginal risk difference; wrong, omitted and late actions kept as separate counts | O2 |
| O4 | Response latency | Raw mean difference (ms) for a stated clock origin and response population; mean-log difference as a separate scale | Accuracy outcomes; correct-only latency is labelled a selected-response estimand |
| O5 | Training: fixed-dose performance; burden to criterion | Contrast at a stated dose; trials or time to criterion with non-learners retained | O6 |
| O6 | Retention | Delayed level contrast **or** between-interface difference in change; never merged | O5 |
| O7 | Subjective workload | Raw mean difference on the same instrument and scoring; SMD only for a defended common construct | O8, O12 |
| O8 | Interruption / dual-task cost | Raw difference on the concurrent-task measure | O7 |
| O9 | Perceived urgency and severity | **Mapping fidelity**: rank or slope agreement between designed urgency (or time-to-action/hazard) and perceived urgency. Raw rating differences are reported descriptively only. | Any "higher is better" metric |
| O10 | Certainty interpretation | Accuracy of the listener's judgement of message certainty; calibration where reported | O2 |
| O11 | Source attribution | Identification accuracy of source | O2 |
| O12 | Human likeness, attributed emotion, listener affect, trust/compliance, preference/annoyance | Instrument-specific raw differences; each construct analysed separately | Performance outcomes; preference never substitutes for O2–O8 |

Mapping rules fixed by the pilot: memory for the content of an alerted message after a delay is O6 (retention of message meaning); performance on a concurrent memory or other task while messages occur is O8; recall of the alert itself immediately after exposure is O2.

No composite "total performance" score is formed. Total interpretive effort (glossary G25) remains a multidimensional framing.

## 3. Two-pass extraction and cell formation

**Pass 1 (characteristics only).** For every included experiment, extract population, task class, message content dimensions (G09–G15), representations compared, comparison type, training/exposure, delay, outcomes measured, clock origins, deadlines and design — **without** extracting or viewing effect estimates beyond what is unavoidable on the same page. Record any unavoidable exposure.

**Cell formation.** From pass-1 codes only, assign each experiment–outcome pair to a synthesis cell keyed by:

`(task class, semantic dimension conveyed, comparison type, outcome family, exposure/delay window, effect scale, clock origin or deadline policy where relevant)`

| Key element | Fixed values |
|---|---|
| Task class | `NAV` menus/navigation; `VEH` in-vehicle/driving; `MED` clinical alarms/monitoring; `AVI` aviation/cockpit; `IND` industrial/process control; `NOTIF` desktop/mobile/home notification; `ACC` assistive/accessibility; `LAB` abstract laboratory identification; `OTHER` with description |
| Comparison type | `CT1` between representation families; `CT2` parameter manipulation within a family (e.g. urgency parameters); `CT3` voice property (natural vs synthetic, prosody, human likeness); `CT4` audio vs non-audio/no alert; `CT5` hybrid vs component |
| Semantic dimension | `STATE`, `SOURCE`, `CERTAINTY`, `HAZARD`, `URGENCY`, `ACTION`, `LIFECYCLE`, `MIXED`, `UNSPECIFIED` |

Cell assignments are committed (a dated cell-assignment file under the #9 extraction area) **before pass 2**. Changes after pass 2 begins require an amendment stating the exposure.

**Pass 2 (effects).** Extract all eligible estimates for each assigned cell, plus all other reported outcomes for the evidence map.

## 4. Effect measures and standardization

Raw mean differences are used when units share an interpretation. When standardization is unavoidable, the denominator and small-sample correction are named; paired d_z is never pooled unchanged with between-person g; a mixed-design SMD synthesis is enabled only after the cell's common standardizer is fixed in writing before pass 2. Log RR or marginal log OR are used only in separate compatible cells. Conditional model odds ratios are not relabelled marginal effects. Interface-package comparisons (several properties changed at once) are labelled as such; their effects are not attributed to sound style alone.

## 5. Extraction fields

Adopted from the prepass extraction contract and mapped to v1 records:

| Field group | Content | v1 location |
|---|---|---|
| Identity | Publication/version; study, experiment, sample, arm, cue, outcome, timepoint; publication family; overlap component | `source`, `study`, `experiment`, `sample` |
| Provenance | Locator (page, table, row/column or model contrast); reported vs derived; transformation and version; extractor; verification scope | `extraction.locator`, `field_locators`, `derivation`; `assistance` |
| Population | Language, hearing criteria, expertise, age; exclusions and attrition | `sample`, `extraction.population` |
| Intervention/comparator | Actual exemplars and family labels; semantics and action mapping; number of alternatives; voice/lexical content; duration and level; training and feedback; environment and distractors; matched vs bundled comparison | `extraction.stimuli`, `training`, `task`, `conditions` |
| Design | Randomization unit; parallel/paired/crossover/factorial/observational; counterbalancing; trials per person; repeated blocks; missing pairs | `experiment.assignment`, `dependence` |
| Estimand key | Cell key (§3) plus analysis population and weighting | `experiment.outcomes`, `extraction.contrast`, `timepoint` |
| Estimate | Signed contrast, units, dispersion type and level, df, n for that variance | `extraction.value`, `unit`, `dispersion`, `n` |
| Dependence | SDdiff or paired statistic; within-person correlation; contrast covariances; shared control | `extraction.dependence` |
| Events vs missingness | Wrong, omitted, late, replayed, technical loss, training failure | `extraction.missingness` |
| Selection | All eligible outcomes and timepoints; primary/secondary status; aggregation rule | Cell-assignment file; `extraction.note` |
| Appraisal/transport | Domains D1–D8 (protocol §8) | `appraisal` |

## 6. Dependence and missing data

### 6.1 Identity before counting

Publication, study, experiment, sample and result identities are reconciled before the number of independent components in any cell is counted. Unknown overlap forms one component with the reports it may overlap.

### 6.2 One result per component per cell

Default: one prespecified effect per independent component per cell, chosen by the hierarchy (a) the outcome matching the cell definition most directly, (b) the longest relevant exposure within the cell's window, (c) the all-participant analysis over completers. Selection never uses significance, magnitude or precision. An explicitly weighted within-component aggregate is allowed when weights are written before pass 2, with variance `a'Va`.

### 6.3 Correlations and covariances

No single assumed correlation is presented as observed. When a paired SE cannot be recovered from a reported paired statistic, CI or SDdiff, the within-person correlation is varied over the fixed grid **r ∈ {0.3, 0.5, 0.7, 0.9}**, and conclusions are reported as robust only if they hold across the grid. Shared-control covariances follow the prepass derivations. Person-level correlations are never used as contrast-covariance correlations.

### 6.4 Missing variance and observations

SDs are never imputed in primary analyses; results without a recoverable valid variance stay in the map and in non-pooled displays. A sensitivity analysis may borrow an SD only from the same instrument and task class, with the source recorded. Valid SE recovery uses a CI with its level and df, a test of the exact contrast or SDdiff; an omnibus p or a significance threshold is insufficient. Missing participants, omissions, timeouts, training failures and technical losses are recorded separately; failures are not deleted.

## 7. Pooling eligibility and model

### 7.1 Eligibility

A cell may be pooled only when (a) its members share the cell key, (b) it has **at least five independent components**, (c) each member has a valid variance on the cell's scale, (d) identity and overlap are resolved, and (e) no member's appraisal makes it unusable for that question. Otherwise the cell is non-pooled (§9). Five is a conservative project safeguard, not a sufficiency guarantee.

### 7.2 Model

Random-effects mean with REML heterogeneity estimation and a modified Hartung–Knapp–Sidik–Jonkman interval: t(k−1) quantile and the inverse-total-variance SE multiplied by √max(1, q), with q as defined in the prepass clauses (Röver et al. 2015). The unmodified HKSJ interval is reported as a sensitivity. Prediction intervals are reported only when k ≥ 10 and labelled as poorly identified otherwise. No heterogeneity p-value selects the model.

### 7.3 Before first empirical use

The estimator must pass known-answer tests against published worked examples or an established implementation with pinned versions, recorded in #10. Until then no pooled estimate may be reported.

### 7.4 Multivariate and robust variance

Considered only with at least ten independent components, coefficient-specific Satterthwaite df of at least four and acceptable leverage diagnostics. Failing that, aggregate or select per §6.2, or do not pool.

## 8. Network meta-analysis

Not planned for v1. Reasons: (a) indirect comparisons need transitivity — effect modifiers balanced across comparisons and interventions jointly randomizable — which is implausible across the heterogeneous tasks, message contents and populations in this literature (Cochrane Handbook ch. 11, §11.2.2); (b) cue-family labels are not homogeneous nodes, and node definitions must maximize within-node similarity (§11.3.2.3); (c) ranking by probability of being best is discouraged (§11.4.3.3) and a family ranking is outside MHAC scope (protocol §3); (d) an NMA of these families already exists (Nees & Liebman). Any NMA would require an amendment with a transitivity assessment per network.

## 9. Non-pooled synthesis

Non-pooled cells are reported under SWiM items 1–9: grouping and its rationale; standardized metric per outcome; synthesis method; prioritization criteria (protocol §8 appraisal, design); informal heterogeneity investigation by ordering on prespecified modifiers (task class, training dose, delay, comparison type) and labelled as non-prespecified where it is; certainty (protocol §8 body-of-evidence judgement); presentation (structured tables and effect-direction or forest-style plots without a summary diamond); results stated in the cell's own terms; and limitations.

Permitted summaries: per-component estimates with uncertainty or an explicit "not estimable" label; the range and distribution of observed effects with the unit stated; vote counting **by direction of effect** only with its limited question stated. Vote counting by statistical significance is never used. Inconclusive evidence is not reported as no effect. Dependent rows are not separate votes.

Non-pooling reason codes (one or more): `CONSTRUCT`, `TASK_OR_EXPOSURE`, `CLOCK_OR_FAILURE_POLICY`, `EFFECT_SCALE`, `DESIGN_OR_CARRYOVER`, `UNKNOWN_VARIANCE`, `UNKNOWN_DEPENDENCE`, `DUPLICATE_CONFLICT`, `SPARSE_INDEPENDENT_INFORMATION`, `SELECTION_OR_BIAS`, `INSUFFICIENT_COVERAGE`.

## 10. Heterogeneity, sensitivity, multiplicity and reporting bias

- **Heterogeneity**: τ² and its uncertainty in pooled cells; prespecified modifiers examined descriptively. Meta-regression is not planned in v1; adding it requires an amendment and at least ten components per modifier level.
- **Sensitivity**: correlation grid (§6.3); exclusion of `high concern` appraisals; unmodified HKSJ; alternative result-selection where §6.2 left a tie.
- **Multiplicity**: intervals are marginal and descriptive; no confirmatory family is declared in v1; no universal superiority claim from several unadjusted contrasts.
- **Reporting bias**: outcomes measured but not reported are recorded; funnel-type tests only with at least ten components and are interpreted cautiously; the Nees–Liebman observation that some studies reported nonsignificant effects without statistics is a reason to record such cases as missing results, not to discard them.

## 11. Interpretation conventions

For display only, intervals are compared with ±5 percentage points (O2, O3) and ±10% of the comparator mean (O4). These are **unvalidated conventions** chosen for readability, not minimal important differences, and they never affect eligibility, selection or pooling.

## 12. Implementation and verification

Calculations are implemented in versioned code under `tools/` with unit tests, including known-answer tests (§7.3), and are run on committed inputs. CI can verify reproducibility and structural integrity only. It cannot verify estimand choice, source fidelity, exchangeability or scientific validity.
