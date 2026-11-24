# T001 — observable warning endpoints and attribution limits

[Overview](README.md) · [Protocol sketch](PROTOCOL-SKETCH.md) · [Decisions](DECISION-LOG.md)

## Observation model (not a psychological law)

Emitted cue and world state -> physical acoustic field -> possible detection report -> identity test -> requested-action interpretation -> action choice -> actual completion/deadline.

These are **possible instruments in a proposed test**, not a compulsory serial neural pipeline. People may act via visual checks, prior knowledge, guessing, deliberate refusal or other simultaneous routes. Not assessed is not synonymous with failure.

## Endpoint matrix

| Construct | Minimal proposed observation | Manipulated factors | What is NOT established |
|---|---|---|---|
| Emission | Logged cue onset/offset and channel | Trigger, delivery delay | Reached listener or ear |
| Acoustic presence/masking | Calibrated at-ear waveform/SNR or audited model | Overlap, spectral content, device | Individual perceived signal |
| Detection/report | Yes/no present judgment and no-alarm catch trials | Masker, workload, criterion | Nonresponse due to sensory masking or attention |
| Awareness report | Contemporaneous report with response timing | Probe, retrospective order | Conscious awareness mechanism |
| Identity | Confusion matrix including omission/wrong labels | Similarity, concurrent streams, training | Comprehension of request |
| Request understanding | Independently interpreted requested task action | Language, mapping, context | Decision to comply |
| Choice/criterion | Task decision against independent world state and costs | Alert validity, workload, consequence | Cue heard or believed |
| Timely correct task action | Instrumented action, correctness and deadline | Deadline, competing task, verification | That audio caused the action |
| Recovery | Return-to-task interval and errors if observed | Interruption schedule | Earlier stages succeeded |

Represent observed, instrument-inferred, not assessed and unknown distinctly. Forced choice may reflect guessing. Conditional identity correctness among detectors has a different denominator from unconditional detection or action correctness.

## Non-causal descriptive labels

| Toy output label | Observable pattern | Why attribution is still uncertain |
|---|---|---|
| miss_with_modelled_masking | Model forecasts masking and detection absent | Model error, attention and criterion not excluded |
| audible_prediction_with_no_report | Model predicts presence but report absent | Hearing, attention, policy and measurement remain possibilities |
| miss_unattributed | Missing detection and unknown audibility | No mechanism identified |
| identification_error | Positive detection report, wrong source identity | Interference, training, memory or guessing |
| request_interpretation_error | Correct identity, incorrect request explanation | Context, language or confusion |
| action_selection_error | Correct interpretation, wrong choice | Decision policy, verification, cost or refusal |
| late_correct_action | Correct action but after recorded deadline | Not a timely success; cause unknown |
| timing_unassessed | Correct selected action, missing timestamp | Neither late nor timely can be established |
| timely_correct_action | Correct action before deadline | Attribution to audio still unproven |

## Negative and rival cases

- **Audible but unanswered:** model predicts the cue is present, but no response. Do not diagnose inattentional deafness from omission.
- **High urgency, wrong identity:** a rated-urgent cue may remain difficult to name or act on. Sanderson et al. 2006 reported different directions for rated urgency versus identity accuracy in their tested alarm set.
- **Overlap versus masking:** two alarms can be separately audible yet their source labels confused. Compare Lacherez et al. 2007 identity outcomes with Bolton et al. 2020 detection outcomes without assuming a shared mechanism.
- **Wrong choice despite understanding:** recipient understands a request but declines, checks independently or prioritizes competing costs.
- **Right action without cue interpretation:** visual feedback or prior knowledge produces a correct action before the alert is understood.
- **Missing timestamps:** correctness cannot establish timeliness when no deadline measurement exists.

## Competing explanatory models

**M0: consequential action alone is enough.** If action correctness and time are sufficiently predictive for a particular task and stage measures add no decision value, the simplest useful model wins.

**M1: separable endpoints add discriminatory power.** If overlap changes identity independently of detection, or workload changes action latency independently of identification, targeted intervention hypotheses differ. M1 needs prospectively differentiated measurements and out-of-sample decision benefit, not simply more conceptual stages.

If studies measure only recognition or combined report/action, either model may be underidentified. Use **unattributed**, not a forced cognitive diagnosis. If no measurable gain arises from stages, reduce the T001 vocabulary.

## Confounders and transfer bounds

Musical training, hearing profiles, ambient spectrum, speaker hardware, response task, experiment order, language, speed/urgency mappings, repeated exposure, false-alert history and action deadlines can affect several endpoints simultaneously. Neither general-aviation pilots nor nurses are a representative sample of unspecified future MHAC users. No causal conclusions or safety certification follow from this taxonomy.
