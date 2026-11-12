# T001 — non-executed discriminating study protocol and synthetic rehearsal

[Overview](README.md) · [Taxonomy](TAXONOMY.md) · [Toy fixture](SYNTHETIC-ONLY.csv)

**Status:** Exploratory design only. Not externally preregistered, human-reviewed, authorized or executed. This does not amend the frozen Track E protocol. Any participant research would require the separate human gate at #20.

## Competing questions and a future design

Can detection, source identification, and **timely correct task action** show different overlap and workload effects, beyond what one action metric already reveals? Alternative: one action metric plus context adequately informs the design decision, so extra stage instrumentation has no incremental value.

If authorized later, consider a **3 × 2 × 2 factorial** with:
- Acoustic configuration: isolated cue / simultaneous but instrumentally audible cues / validated spectrum-overlap masking-risk condition. Use actual calibrated ear-level playback evidence rather than a generic 'overlap' label.
- Task demand: low versus high with independently measured task performance; workload is not inferred from cue misses alone.
- Training: minimal orientation versus structured identity/action mapping practice; match presentation time and content.
- Counterbalanced cue identities, mapped action costs and condition order, with an explicit no-cue catch condition to estimate false alarms and response criterion.

A careful future design must distinguish **prior event prevalence, alarm reliability, true requested-action correctness, urgency rating and deadline**. In some worlds the correct response is *not* to act, even if an alarm was emitted. Audio is not assumed to be the only pathway for correct action. Report any acoustic safety, hearing, multilingual, environmental and physical playback constraints.

No sample size or power result is asserted: the variance, target effect, within-person correlations, minimally meaningful action benefit, model complexity and design dependence must first be specified and reviewed. No simulated 'participants' are substitutes for real participants.

## Outcome and missingness instrumentation

| Outcome | Proposed observation | Essential caution |
|---|---|---|
| Emission and physical exposure | Per-cue event/latency log; calibrated device/SNR/waveform | Acoustic model prediction is not a listener report |
| Reported detection | Present/absent judgment including blank catch trials | Silence may reflect criterion or motor/response latency |
| Source identification | Source/event confusion matrix with wrong response and omission separate | Conditional-on-detection accuracy is selection-biased |
| Requested action comprehension | Independent paraphrase/selection of intended request | Probing can train participants or prime action |
| Decision quality | Choice against a separately specified scenario ground truth | Reject/check can be correct, especially on invalid alarms |
| Timely action | Recorded action completion with predeclared deadline | Missing timestamp is unknown, not a late failure |
| Return-to-task | Optional resumption delay and error | Outside the primary T001 causal claim |
| Urgency / confidence | Separate subjective ratings | Not proxies for accuracy or task consequence |

Use assessment-specific numerator/denominator/unknown fields. Distinguish partial identification from complete failure; do not fill in unobserved stages by implication. If timing is missing for a correctly selected action, timely success is **not assessed**. A knowingly invalid warning can yield a correct non-action.

## Declared-fiction rehearsal and expected result

Twelve entirely invented alert-event rows in [SYNTHETIC-ONLY.csv](SYNTHETIC-ONLY.csv) represent: baseline success, predicted masking with non-report, predicted-audible non-report, ordinary wrong identity, very-high-urgency wrong identity, wrong request, wrong choice, correct but late response, correct selection with missing latency, no audibility estimate with missing detection report, near-deadline success, and detected-but-identity-unassessed.

The independent [analysis.py](analysis.py) parser rejects any row not explicitly tagged **synthetic_fixture**, any malformed value, impossible instrument branching, duplicate IDs and nonfinite or negative latency. It reports descriptive rather than causal categories. An identical rerun on the same bytes yields identical JSON.

Exact expected toy counts, **not empirical percentages**:
- Detection report: 9 positive / 12 assessed.
- Correct source identity: 6 positive / 8 assessed.
- Correct requested-action interpretation: 5 positive / 6 assessed.
- Correct action choice: 4 positive / 5 assessed.
- Timely correct action: 2 positive / 4 assessed; eight trials lack a fully assessed timely endpoint.

The toy contains only **emitted alerts**, with no no-alarm catch trials. Therefore false-alarm rate, specificity, d-prime and decision criterion are not estimable. It is invalid to interpret a 2/12 summary as an observed human end-to-end success rate; eight cases did not have the full outcome tested. Fictional urgency values demonstrate the logical possibility of discordance, not the strength of a real relationship.

## Planned negative/control comparisons

1. Instrumentally masking predicted cue versus an unmasked cue, independently testing presence judgments. A detection change alone does not reveal identity comprehension.
2. Concurrent but independently audible sources, testing whether identity degrades with no measured detection change. If not, a dedicated segregation stage may add little.
3. High urgency ratings alongside identity mistakes, with cue/training balance; do not assume urgency mapping equals a comprehension benefit.
4. High workload with identical calibrated playback and response omissions; do not call this proven inattentional deafness without a mechanism-specific instrument.
5. Valid versus non-actionable warnings plus no-alert catch trials, separating false-positive action from failure to intervene.
6. Correct actions occurring before auditory onset or via external visible information. These should not be credited to auditory communication.
7. Missing measurements and contradictory cue-state predictions; do not quietly coerce them to failure or success.

## Analysis plan to be adjudicated before any human work

Prespecify a primary consequential endpoint, denominator, covariates, uncertainty intervals, correction for multiple comparisons, missingness treatment, and smallest useful effect. Consider repeated-measures mixed models if supported by data and protocol. Compare stage-specific and simple-action-only models on **held-out conditions** under a declared scoring rule and consequence costs; adding parameters without predictive gain is not a success. Separately report detection, conditional identity, action correctness and deadline failure. If stage effects are unidentified, conclude **unknown** and revise the instrument instead of retrodiagnosing sensory or attentional failure. Explicitly retain all null and negative contrasts.

## Boundaries

No EEG, real alarm playback, hospital/aviation experiments, external contact, pilot recruitment, rights-restricted source publication, live register inclusion, paid access, hazard control or production cue-engine implementation is authorized in this prepass. Successful synthetic tests do not validate listening comprehension or safety.
