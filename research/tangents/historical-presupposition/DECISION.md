# MHAC-T013 — conditional decision and R014 handoff

**Status:** exploratory, synthetic-only, **not accepted** empirical or theoretical MHAC evidence. 2026-11-04. The fixture author knew the candidate policy designs; no independent human second labeller, participant, or external review is claimed.

## Bounded applicability outcome

**Limited GO for an independent structural falsifier; NO GO for a required production subsystem.** The proposed system includes optional spoken persistence and state-transition language, and existing source/event/action controls do not themselves test historically backgrounded propositions in otherwise truthful statements. This warrants *one* lightweight comparison, not a language-understanding engine. If R012 ultimately excludes retrospective claims, the simpler present-only comparator wins by avoiding an unnecessary problem.

This is a scope-bound overlap check against #30/#33/#34/#36/#38/#47/#49/#51 and PRs #32/#35/#37/#39/#53/#48/#50/#52. Those PRs remain separate and untouched. No accepted R012 semantics exist on the inspected main baseline; no empirical listener failure has been observed.

## Structural comparison, not human-performance measurement

The authored 30 cases include 24 labelled true-current statements, three false-current and three current-unknown cases. The following table is the **independent JavaScript shadow calculation of the Python policy definitions and checked-in fictional labels on 2026-11-04**, not a report of hosted CI or a human study. Confirm through `python replay.py --check` and tests before relying on the exact numbers.

| Metric on fabricated 30-case set | A Present-only | B Naive history | C Warrant-gated + fallback | D Present + optional timeline |
|---|---:|---:|---:|---:|
| Spoken assertions | 24 | 24 | 24 | 24 |
| Historical spoken offers | 0 | 20 | 8 | 0 |
| Historical offers without support | 0 | **12** | 0 | 0 |
| Of those: known contradicted | 0 | 5 | 0 | 0 |
| Of those: past unobserved/unknown | 0 | 7 | 0 | 0 |
| Separately inspectable history labels | 0 | 0 | 0 | 8 |
| Eligible fictional action offers | 15 | 15 | 15 | 15 |
| Missed eligible urgent present claims | 0 | 0 | 0 | 0 |
| Spoken words (not seconds or acoustic effort) | 82 | 92 | 86 | 82 |

Policy B fails the *constructed warrant criterion* because it ignores a label specifically designed to distinguish warranted/unsupported histories. C meets that criterion by construction; the exercise does **not** quantify real-world reduction in mistakes, efficacy, ease of use or safety. A is at least as effective on this set without a new historical-warrant dependency. C may preserve relevant context, but its value over A is not demonstrated. D assumes an accessible display/inspectable route that is not yet designed.

### Essential counterexamples and competing interpretations

- **AG02:** current high is true; the complete earlier interval records no preceding high. “High again” adds a known-contradicted historical proposition. B offers it; A/C/D do not.
- **AG03:** current high and an authorized inspection are true; earlier history is missing. “High again” is **not proven false**—it is unwarranted. C must preserve the present warning and action, rather than withhold all speech; a strict history-dependent alarm gate would create a new problem.
- **ST02:** verified low interval contradicts uninterrupted “still high”, although high is true now. Changing reference intervals (ST01 versus ST04) may legitimately change historical warrant.
- **SP02/RS02:** “has stopped” and “has resumed” express transitions not entailed solely by the current inactive/running state. These are not equivalent to current-state assertions.
- **AG01/ST01/SP01/RS01:** where the relevant earlier conditions and reference times are supported, historical language is **permitted** by the toy contract; a blanket ban is unnecessary.
- **NO05/ST05/RS05:** current condition may be true while an action deadline is expired. None of the four policies independently authorizes the expired action.
- **S246/S250/S251/S252:** pragmatics, cognitive capacity, context and language experience defeat the equation “one temporal word always causes one belief”. Our labels concern *message warrant*, not predicted internal recipient inference.

## Decision consequences for programme owners

| Possible outcome | Implication if separately supported by later evidence |
|---|---|
| Positive independent structural failure with meaningful in-scope wording | Consider an optional historical-proposition provenance guard and a present-only fallback for **R012/R013**, keeping action permission independent. R008 should compare this with ordinary semantics/pragmatics before invoking cybersemiotics. |
| Null/duplicate or present-only always sufficient | **Do not implement temporal logic.** Retain counterexamples as critical material for R008 and negative controls for R014 only if needed. |
| Contradictory: a gate loses true urgent messages or makes message wording too complex | Prefer immediate present-state delivery and optional nonspoken history. Reject suppression based solely on missing history. |
| Inconclusive external evidence | Preserve labels as synthetic research questions; leave R012 schema, accepted claim register and production design unchanged. |

**Working disposition:** recommend the **minimal present-only default (A)** for any future prototyping until a real use case requires historical content. A provenance-gated optional historical phrase (C) is a **candidate** conditional extension, not an accepted standard. A simpler accessible chronology or a deliberate no-history policy may be sufficient.

## Proposed R014 protocol only — explicitly not conducted

**Question:** With identical current state, authorized action and delivery deadline, does introducing historically unsupported temporal phrasing change attribution, correct first/final action, confidence in source history, or response latency compared with neutral present-state phrasing?

**Within-material manipulations to assess for an authorized future study:** (1) neutral vs history-triggered utterance; (2) documented prior history vs known-negative earlier interval vs unobserved interval, carefully distinguishing failure to know from proof of no event; (3) short vs higher secondary-task load; optionally (4) available inspectable history vs no visual route. Counterbalance trigger family (*again/still/stopped/resumed*), reference-time clarity, source/event identity and speech duration. Compare at least one plain-language baseline and a simple explicit chronology; avoid testing just a lexical blacklist.

**Candidate dependent measures:** source-history proposition correctly classified as supported/contradicted/unknown; detection of current state; required-action recognition; actual first and final *fictional interface action*; time to correct response before an assigned deadline; separate workload and subjective clarity. Track comprehension and action separately. Predefine exclusions, a safe listening procedure, screen-reader/text equivalents, hearing-accommodation path, language proficiency and accessibility counterexamples. Use sound-level calibration and stop rules if a future approved physical listening study ever occurs. Avoid assuming visual fallback universally accessible.

**Validity threats and controls:** pragmatic accommodation may be useful; unverified histories may be contextually inferred despite lack of machine proof; corpus triggers are not semantically interchangeable; spoken longer phrases may differ in intelligibility/length; temporal reference can be implicit; sensor provenance may be unreliable; no fictitious source here provides real authenticated telemetry. Actual sample size and detectable effect must be prospectively justified from a meaningful outcome and independent variance/dependence evidence, not a manufactured power figure.

**Unmet human gates:** R012/R013 scope and owner admission, formal R005/R006 source/identity screening if empirical claims are required, R014 experimental design readiness, **R020 explicit ethics/consent/recruitment/access authorization** before any human interaction. No experiment, study registration, paper submission or external contact authorized.

## Acceptance and custody notes

Files added only for this tangent: [cases.json](cases.json), [replay.py](replay.py), [README.md](README.md), [SOURCES.md](SOURCES.md), [DECISION.md](DECISION.md), and `tests/test_historical_presupposition.py`. Structural unit tests and full repository tests must be run; a successful CI would attest software integrity only. Source identity/counterarguments were spot-checked using public web publisher/standards pages on 2026-11-04; readings and unavailability are itemized in SOURCES. No new accepted research registry entries, protocol amendment, human data or production TTS results.
