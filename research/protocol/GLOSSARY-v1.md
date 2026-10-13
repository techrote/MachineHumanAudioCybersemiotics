# Operational glossary — protocol v1

[Protocol](PROTOCOL-v1.md) · [Analysis plan](ANALYSIS_PLAN-v1.md) · [Pilot report](PILOT_REPORT.md)

These are working definitions for screening, coding and analysis under protocol v1. They are project conventions, not claims about how Brier or any other author uses a term. Track G (theory) may revise conceptual definitions through the [concept register](PROTOCOL-v1.md#7-track-g-theoretical-sampling-and-concept-revision); a revision that would change Track E eligibility or coding requires a protocol amendment and impact assessment.

## Message and signal terms

| ID | Term | Operational definition | Notes and exclusions |
|---|---|---|---|
| G01 | Machine–human audio message | A discrete or state-coupled sound produced by a technical system to inform a person about system/task state or to request an action. | Includes speech (recorded or synthetic) and non-speech sound. Excludes human-to-human speech, music for its own sake and environmental sound not produced by the system. |
| G02 | Cue family | The authors' representational category: auditory icon, earcon, spearcon or other compressed-speech cue, speech, abstract tone/alarm, parameter-mapped sonification, hybrid. | Coded as the study reports it **and** by the operational descriptions G03–G08. Disagreements are retained, not resolved silently. A family label never defines a homogeneous treatment. |
| G03 | Auditory icon | A non-speech sound designed to resemble an everyday sound associated with the referent. | Resemblance is a design claim; perceived resemblance is an outcome. |
| G04 | Earcon | A structured abstract non-speech motif whose mapping to the referent is learned. | Includes families/hierarchies of motifs. |
| G05 | Spearcon / compressed speech cue | Speech accelerated or otherwise compressed, with or without remaining intelligibility. | Record compression factor if reported. |
| G06 | Speech message | Natural or synthetic spoken words or phrases. | Record voice source, synthesis method, language, rate and prosody manipulation where reported. |
| G07 | Parameter-mapped sonification | Sound whose parameters are continuously or repeatedly coupled to a data or state variable. | In scope only when used to communicate system/task state for monitoring or action; exploratory data analysis or art without a communication-task outcome is out of scope for Track E. |
| G08 | Hybrid | A message combining families, e.g. earcon followed by speech. | Coded as a package; effects are not attributed to a single component. |

## Message content dimensions (RQ4)

| ID | Term | Operational definition | Notes |
|---|---|---|---|
| G09 | Source attribution | Which system, component or agent the message is about or comes from, as identifiable by the listener. | Distinguish designed source cues from listener attribution. |
| G10 | Message certainty | The system's confidence or probability concerning the state it reports. | Distinct from G24 (certainty of a body of evidence) and from listener confidence. |
| G11 | Hazard and severity | The magnitude of potential harm to people, equipment or task if the state is not handled. | Safety hazard and non-safety consequence are coded separately when distinguishable. |
| G12 | Urgency | Three distinct quantities: **designed urgency** (intended priority), **perceived urgency** (listener rating or behaviour) and **time-to-action** (the actual window before consequence). | Perceived urgency is analysed as mapping fidelity to designed urgency or time-to-action, never as "higher is better". |
| G13 | Persistence and lifecycle | Whether the state is new, continuing, escalating, resolved or stale, and the message's repetition/acknowledgement behaviour. | Acknowledgement is not understanding or resolution. |
| G14 | Sign relation | Whether a sound–referent relation is treated as resembling (iconic), causally/spatiotemporally connected (indexical) or conventional (symbolic) **in a particular use**. | A relation-dependent hypothesis, not a fixed property of a sound. Peircean terms are used only with source-checked meaning in Track G. |
| G15 | Requested action | The behaviour the system asks for, including "no action". | Coded separately from the state reported. |

## Outcome terms (RQ3, RQ5)

| ID | Term | Operational definition | Notes |
|---|---|---|---|
| G16 | Detection | Noticing that a message occurred. | Hit/false-alarm measures stay distinct from identification. |
| G17 | Recognition / identification | Selecting the correct referent or meaning from a defined set. | Record set size, chance level and first-attempt scoring. |
| G18 | Correct action | Performing the appropriate task action within the task's deadline and repair policy. | A keypress naming the referent is identification, not action, unless the task defines it as the action. |
| G19 | Response latency | Time from a defined clock origin to a defined response event. | Clock origin (onset/offset), inclusion of errors and trimming must be recorded. |
| G20 | Training dose and burden | Exposure before test (fixed dose), or exposure needed to reach a criterion (burden). | Different estimands; see analysis plan D05–D06. |
| G21 | Retention | Performance after a delay without intervening retraining. | Windows: immediate (< 1 h), short (1 h – 7 days), long (> 7 days). |
| G22 | Workload and interruption cost | Subjective workload instrument scores; performance cost on a concurrent task. | Instrument and scoring variants are not interchangeable. |
| G23 | Human likeness, attributed emotion, listener affect | Perceived human-likeness of a voice or sound; emotion the listener attributes to the system; the listener's own affective state. | Three separate constructs. Linguistic prosody that aids intelligibility is not performed emotion. |
| G24 | Certainty of evidence | Confidence in a synthesised estimate or conclusion. | Not the same as G10. |
| G25 | Situated understanding | The project's working success criterion: the listener's interpretation is adequate for appropriate action or coordination in context, counting total interpretive effort (training, interruption, repetition, repair). | Project framing subject to Track G refinement; not a measured construct by itself. |

## Evidence-unit terms

| ID | Term | Definition |
|---|---|---|
| G26 | Search occurrence (hit) | One result returned by one search run. |
| G27 | Publication / report | A bibliographically distinct document. A conference paper and its journal extension are two publications. |
| G28 | Study | A research project with a defined sample; may span several publications. |
| G29 | Experiment | A design unit with its own conditions and outcomes within a study. |
| G30 | Sample | The people measured; samples may be shared across experiments or publications. |
| G31 | Independent component | A set of results connected by shared or uncertain sample overlap, treated as one unit of independent information. |
| G32 | Synthesis cell | A prespecified combination of population/task/semantic content, comparison, outcome family, timing and effect scale within which results may be compared or pooled. |

## Provenance terms

| ID | Term | Definition |
|---|---|---|
| G33 | Hashed manifestation | Source bytes whose SHA-256 is recorded in a source record (retained locally only when redistribution is permitted). Required for locator-bound extraction. |
| G34 | Tool-mediated reading | Reading through a tool that returns an intermediary model's paraphrase (e.g. WebFetch) without retained bytes. Permitted for discovery, scoping and overlap mapping; never for numeric extraction, quotation or decisive claims. |
| G35 | Decisive claim | A statement on which a synthesis proposition, design requirement or manuscript conclusion depends. Requires a hashed manifestation and exact locator. |
