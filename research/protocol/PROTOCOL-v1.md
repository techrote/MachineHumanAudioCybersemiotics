# MHAC research protocol — version 1

[Protocol index](README.md) · [Freeze record](FREEZE.md) · [Analysis plan](ANALYSIS_PLAN-v1.md) · [Glossary](GLOSSARY-v1.md) · [Pilot report](PILOT_REPORT.md) · [Reporting applicability](REPORTING_APPLICABILITY.md) · [Overlap matrix](../novelty/OVERLAP_MATRIX.md)

**Protocol v1, frozen 2026-10-13 under issue #2 (MHAC-R002).** This is an internal, versioned repository protocol. It is **not** an external preregistration, has no registry identifier and has not been peer reviewed. The executing agent, Claude (Anthropic), prepared it with no independent human review. The baseline literature cut-off is **2026-10-04**.

## Contents

| § | Section | One-line summary |
|---|---|---|
| 1 | [Status, authority and freeze](#1-status-authority-and-freeze) | What is frozen, what governs what, and what freezing does not mean. |
| 2 | [Questions and tracks](#2-questions-and-tracks) | RQ1–RQ6 mapped to Track E (empirical map), Track G (theory) and downstream derivation. |
| 3 | [Novelty and scope consequences](#3-novelty-and-scope-consequences) | What the overlap audit rules out and which questions remain open. |
| 4 | [Track E eligibility](#4-track-e-eligibility) | Frozen inclusion and exclusion rules for empirical reports. |
| 5 | [Track E sources and searches](#5-track-e-sources-and-searches) | Channels, exact query families, gated database access and the predeclared fallback. |
| 6 | [Screening, identity, retrieval and extraction](#6-screening-identity-retrieval-and-extraction) | Decision procedure, verification, unit-of-evidence rules and extraction fields. |
| 7 | [Track G theoretical sampling and concept revision](#7-track-g-theoretical-sampling-and-concept-revision) | Purposive/theoretical sampling, concept register, negative cases and stopping. |
| 8 | [Appraisal](#8-appraisal) | Separate empirical and theoretical appraisal; no universal score. |
| 9 | [Synthesis](#9-synthesis) | Evidence map, conditional pooling and non-pooling, by reference to the analysis plan. |
| 10 | [Reading, locators and AI assistance](#10-reading-locators-and-ai-assistance) | What counts as reading, what tool-mediated reading may support, and disclosure. |
| 11 | [Completion and stopping](#11-completion-and-stopping) | Coverage-based search completion and saturation-based theoretical stopping. |
| 12 | [Priority corpus and execution batches](#12-priority-corpus-and-execution-batches) | Batches for #3/#4/#5 without narrowing to open access or favourable studies. |
| 13 | [Access gaps and human gates](#13-access-gaps-and-human-gates) | Known access limits and the minimal owner actions that would close them. |
| 14 | [Amendments](#14-amendments) | How rules change after freeze and how rework is propagated. |
| 15 | [Reporting and limitations](#15-reporting-and-limitations) | Reporting commitments and the limits this protocol carries forward. |

## 1. Status, authority and freeze

Frozen artifacts are this file, the [analysis plan](ANALYSIS_PLAN-v1.md) and the [glossary](GLOSSARY-v1.md). Their SHA-256 digests and the freeze date are in the [freeze record](FREEZE.md); the commit that lands them on `main` is recorded on issue #2 and in the freeze record's post-merge addendum. Pilot and reporting documents are supporting records, not rules.

Authority inside the repository follows [AGENTS.md](../../AGENTS.md): user instructions and platform rules first; then the runbook for execution; **this protocol and its recorded amendments for method**; issue scope for work packages; provenance-backed records for factual claims. `docs/RESEARCH_PROTOCOL.md`, `docs/SEARCH_STRATEGY.md` and `docs/SYNTHESIS_METHOD.md` remain the instructions this protocol implements. Where this protocol is more specific, it governs. Where it is silent, those documents apply.

Freezing fixes empirical eligibility, search plans, outcome families, analysis decision rules, appraisal and verification plans, and stopping rules before production selection and extraction. It does **not** freeze Track G's sensitizing concepts, which evolve through the governed concept register (§7). No registration, submission or external contact accompanies this freeze; an external registration would need separate owner authorization (§13).

## 2. Questions and tracks

| RQ | Question (from `docs/RESEARCH_PROTOCOL.md`) | Track | Primary owner issues |
|---|---|---|---|
| RQ1 | What does cybersemiotics claim about information, meaning, observers and communication, and how does Brier's account develop? | G | #3, #7 |
| RQ2 | What does it add relative to competing explanations, and where are alternatives stronger or more economical? | G (+ E boundary evidence) | #4, #8, #11 |
| RQ3 | What is known about comprehension, action, learning, retention and workload for speech and non-speech audio? | E | #5, #6, #9, #10 |
| RQ4 | How should source, certainty, hazard, consequence, urgency, persistence and action remain distinct? | Derivation from G + E | #11, #12, #13 |
| RQ5 | Which functions can be retained without performing human emotion, with what trade-offs? | E (construct evidence) + G (concepts) | #9, #10, #11, #13 |
| RQ6 | What design contracts and evaluation criteria follow, and what would cause revision? | Derivation | #12, #13, #14 |

**Track E** is a systematic evidence map with nested, conditionally pooled comparisons (§4–§6, §9). Its organising framework follows evidence-and-gap-map practice (rows: message representation and manipulated property; columns: outcome families) adapted from White et al. (2020), with within-cell synthesis questions governed by the analysis plan. It is not a scoping review and not a single meta-analysis.

**Track G** is a critical interpretive synthesis adapted from Dixon-Woods et al. (2006): purposive and theoretical sampling, versioned concepts, refutational and lines-of-argument synthesis, and documented negative cases (§7). It is never described as an exhaustive census of philosophy or semiotics.

**Derivation** (RQ4–RQ6) uses only accepted outputs of both tracks plus explicit project constraints. It has no search channel of its own.

The working success criterion — situated understanding with total interpretive effort counted (glossary G25) — is a project framing. The project preference for intelligible, perceptually non-human audio without performed emotion is a **project constraint**, not an eligibility rule, a weighting rule or a claim attributed to Brier.

## 3. Novelty and scope consequences

The [overlap matrix](../novelty/OVERLAP_MATRIX.md) treats novelty as an open question. Its consequences are binding scope rules for v1:

1. **No new cue-family ranking.** Nees & Liebman (2023; preprint 9.8.22 read) already compare auditory icons, earcons, spearcons and speech on accuracy, response time, preference, workload and dual-task cost with searches to mid-2021. Track E will not rank cue families as its aim. Where its data permit a family comparison, it is labelled an update or sensitivity check against that review (matrix N01, N13).
2. **The map is organised by message semantics and outcome, not by family.** Primary axes are the content dimension conveyed (G09–G15), the outcome family (O1–O12 in the analysis plan), training/exposure and delay. Cue family is a descriptive coding field (matrix N02–N06).
3. **Urgency, human likeness and semiotic-engineering overlaps are unresolved.** R004/R005 must locate and read urgency-mapping reviews, voice-anthropomorphism reviews and de Souza's core semiotic-engineering chapters before any synthesis proposition claims a contribution there (N04, N07, N09).
4. **Applying cybersemiotics is not itself a contribution.** The inspected material shows no cybersemiotic treatment of machine–human audio (N10), but whether that matters is decided only by the remove-Brier test in #11. A null result is acceptable.
5. **Peircean classification of interface sounds is not new.** Prior work already applies Peircean sign classes to interface sounds (N08); sign relations are coded as use-dependent hypotheses (G14).

These rules may be revised only by amendment (§14) after the named comparators are actually read.

## 4. Track E eligibility

A report is eligible when it satisfies **all** of E1–E6. Access, open-access status, statistical significance, direction of results, the cue family's resemblance to the project's preferred style, and citation of Brier or semiotics are **not** criteria.

| Rule | Include | Exclude (reason code) |
|---|---|---|
| E1 Participants | Human participants of any age, language, hearing status or expertise. Hearing status, language and expertise are coded. | No human participants, or only algorithmic/simulated listeners (`E-NO-HUMANS`). |
| E2 Messages | Machine-generated audio messages (G01) of any family (G02–G08), including state-coupled sonification used for monitoring or action. Multimodal interfaces qualify when an audio component is manipulated or separately compared. | No audio component manipulated or compared, e.g. tactile- or visual-only warnings (`E-NOT-AUDIO`). Human-to-human speech; music or sound not acting as a system message; exploratory data sonification without a communication-task outcome; audio used only as background (`E-NOT-MACHINE-MESSAGE`). |
| E3 Comparison | At least two conditions that differ in audio representation or in a manipulated audio property (e.g. urgency parameter, voice type, prosody, compression), **or** audio versus a non-audio/no-alert condition. Within- and between-participant comparisons qualify. | A single condition with no comparison (`E-NO-COMPARISON`). Such reports may still inform Track G or design examples, but not the evidence map. |
| E4 Outcomes | At least one outcome in families O1–O12 of the [analysis plan](ANALYSIS_PLAN-v1.md#2-outcome-families): detection, identification, correct action, latency, training burden, retention, workload, interruption/dual-task cost, perceived urgency or severity, certainty interpretation, source attribution, human likeness/attributed emotion/listener affect, trust/compliance, preference/annoyance. | No eligible outcome measured (`E-NO-OUTCOME`). Outcomes measured but not reported are **not** an exclusion; they are recorded as missing results. |
| E5 Design and report type | Experimental or quasi-experimental studies in laboratory, simulator or field settings; observational field studies of message response (flagged as non-experimental); journal articles, full conference papers, theses, technical reports, preprints and extended abstracts that report method and results. | Purely conceptual, design-description or review papers (`E-NOT-PRIMARY`); reviews are retained for discovery and overlap only. Reports without any method or results description (`E-NO-METHOD-RESULTS`). |
| E6 Date | Publicly available on or before 2026-10-04, with no lower bound. | Available only after the cut-off (`E-AFTER-CUTOFF`); retained for the mandatory #17 refresh. |

**Languages.** No language restriction. Non-English reports are screened and extracted when text is accessible. AI-assisted translation is permitted, disclosed per item and flagged as unverified translation. An inaccessible or untranslatable report is `awaiting_text`, never excluded for language.

**Duplicates and identity** are not eligibility criteria; they are resolved under §6.

**Uncertain eligibility** stays `uncertain` with a reason and next action until the full text decides it.

## 5. Track E sources and searches

### 5.1 Channels

| Code | Channel and interface | Status at freeze | Role |
|---|---|---|---|
| C1 | OpenAlex works API (`api.openalex.org`) | **Gated**: this agent's workspace and the owner's built-in browser both refused the host on 2026-10-13 (§13, HG-R002-DATABASE-ACCESS) | Primary broad bibliographic database; exportable, reproducible counts; forward citations |
| C2 | Crossref REST API | Gated, as C1 | Complementary metadata and DOI resolution |
| C3 | ACM Digital Library (Guide to Computing Literature) | Gated: owner-run export only | HCI venues (CHI, AutoUI, ASSETS, IUI) |
| C4 | IEEE Xplore | Gated: owner-run export only | Engineering and automotive venues |
| C5 | ICAD proceedings: Georgia Tech repository (`repository.gatech.edu`) and `icad.org` proceedings pages | Reachable through web search results and fetch | Core auditory-display venue |
| C6 | SAGE Human Factors / HFES proceedings; Taylor & Francis (Ergonomics) | Gated for search; individual pages sometimes reachable | Human-factors venues |
| C7 | PsycINFO, Web of Science, Scopus | **Not accessible** (subscription); recorded as access gaps unless the owner supplies exports | Psychology and broad citation coverage |
| C8 | General web search engine (the agent's WebSearch tool, standard and extended modes) | Reachable | Supplementary discovery only; never described as a database search |
| C9 | Backward citation chaining from included reports and from relevant reviews (Nees & Liebman 2023, FRA 2022 review, process-industry alarm SLR); forward chaining through C1 when available | Backward reachable when reference lists are readable; forward gated | Recall safeguard |
| C10 | Grey literature: theses (institutional repositories), technical reports (NTL ROSA P, NASA NTRS, DTIC), standards documents as context | Reachable through C8/C5 routes | Grey and non-journal evidence |

Searching a publisher site through C8 is not a C3/C4/C6 database search. A result preview is not an export.

### 5.2 Query families

The concept blocks below are frozen. Translation to a platform's syntax (field tags, wildcard, phrase handling, character limits) is execution detail and does **not** require an amendment if every concept block and term is preserved; the exact as-run string is recorded in the search record. Dropping, adding or narrowing terms requires an amendment.

```text
EQ1 broad recall — message families × participants
("auditory icon" OR "auditory icons" OR earcon OR earcons OR spearcon OR spearcons
 OR "auditory alert" OR "auditory alerts" OR "audio alert" OR "audio alerts"
 OR "auditory warning" OR "auditory warnings" OR "auditory alarm" OR "auditory alarms"
 OR "auditory notification" OR "auditory notifications" OR "audio notification"
 OR "audio notifications" OR "speech warning" OR "speech warnings" OR "verbal warning"
 OR "verbal warnings" OR "voice alert" OR "voice alerts" OR "voice warning"
 OR "voice warnings" OR "auditory cue" OR "auditory cues" OR "audio cue" OR "audio cues"
 OR "auditory display" OR "auditory displays" OR "auditory menu" OR "auditory menus"
 OR lyricon OR lyricons OR spindex OR musicon OR musicons OR "auditory beacon"
 OR "auditory beacons" OR "acoustic beacon" OR "acoustic beacons")
AND (experiment OR experimental OR participants OR study OR evaluation OR user)

EQ2 urgency, hazard and severity
("perceived urgency" OR "urgency mapping" OR "hazard matching" OR "warning urgency"
 OR "alarm urgency" OR "perceived hazard" OR "perceived severity")
AND (auditory OR sound OR sounds OR speech OR alarm OR alarms OR warning OR warnings)

EQ3 voice, human likeness and affect
("synthetic speech" OR "synthesized speech" OR "text-to-speech" OR "speech synthesis"
 OR "robot voice" OR "voice interface" OR "voice assistant" OR "speech interface")
AND (warning OR warnings OR alert OR alerts OR alarm OR alarms OR notification
 OR notifications)
AND (anthropomorphism OR anthropomorphic OR "human-likeness" OR "human likeness"
 OR humanlike OR "human-like" OR emotion OR emotional OR prosody OR naturalness
 OR trust OR compliance)

EQ4 uncertainty and certainty in sound
(sonification OR sonified OR "auditory display" OR "auditory displays" OR "auditory graph"
 OR "audio cue" OR "auditory cue")
AND (uncertainty OR uncertain OR probability OR confidence OR likelihood)

EQ5 learning and retention
("auditory icon" OR "auditory icons" OR earcon OR earcons OR spearcon OR spearcons
 OR "auditory alarm" OR "auditory alarms" OR "auditory warning" OR "auditory warnings"
 OR "auditory cue" OR "auditory cues" OR "auditory alert" OR "auditory alerts")
AND (learning OR learnability OR training OR retention OR memorability OR "long-term"
 OR forgetting)

EQ6 state-coupled monitoring sonification
(sonification OR sonified OR "auditory display" OR "auditory displays")
AND (monitoring OR "situation awareness" OR "situational awareness" OR anesthesia
 OR anaesthesia OR "patient monitoring" OR "process control" OR "vital signs")

EQ7 interruption and workload
("auditory alert" OR "auditory alerts" OR "auditory notification" OR "auditory notifications"
 OR "audio notification" OR "audio notifications" OR earcon OR earcons OR "auditory icon"
 OR "auditory icons" OR "speech alert" OR "speech alerts")
AND (interruption OR interruptions OR "dual task" OR "dual-task" OR workload
 OR distraction OR multitasking)

EQ8 existing reviews (overlap and chaining only)
("systematic review" OR "meta-analysis" OR "scoping review" OR "literature review")
AND (alarm OR alarms OR "auditory warning" OR "auditory warnings" OR "auditory display"
 OR "auditory displays" OR earcon OR earcons OR "auditory icon" OR "auditory icons"
 OR sonification OR "audio notification" OR "audio notifications")
```

**Field scope and limits.** On C1–C4 and C6–C7, search title and abstract (and author keywords where the platform supports a combined field). Apply no language, document-type or open-access filter. Apply the publication-date limit `<= 2026-10-04` only where the platform supports it; otherwise date-screen at title/abstract.

**Reference OpenAlex form** (for the owner gate and for C1 execution): `https://api.openalex.org/works?filter=title_and_abstract.search:<EQn as one line, URL-encoded>,to_publication_date:2026-10-04&per-page=200&cursor=*`, iterating `cursor` to completion and retaining every page. The as-run URL and every page's bytes and hash are recorded.

**C8 web search (supplementary).** Run the natural-language query set W1–W9 listed in the [pilot report](PILOT_REPORT.md#query-revisions-and-the-c8-query-set) in standard mode, plus W1 in extended mode, plus W1 concept translations in German, French, Spanish, Portuguese, Chinese, Japanese and Korean. The W1–W9 English strings are frozen; translations are produced at execution, recorded verbatim and are not frozen terms. Record every returned title and URL; there is no pagination. C8 cannot establish coverage.

**C5 ICAD.** Browse or search the ICAD proceedings by year from 1992 to 2026 through whatever repository listing is reachable, and record each year's coverage status.

**C9 chaining.** Backward chaining for every included Track E report and for each review located by EQ8. Forward chaining requires C1 and is otherwise recorded as not performed.

**Search peer review.** No librarian or information-specialist PRESS review is available. The strategies above received only the executing agent's own check against the six PRESS elements ([reporting applicability](REPORTING_APPLICABILITY.md#press-2015)). This is a disclosed limitation, not a substitute review.

### 5.3 Gated execution and predeclared fallback

R005 first checks whether C1–C4/C6–C7 have become available (gate satisfied, network policy changed, or owner-supplied exports). If they have, it executes EQ1–EQ8 there. If not, R005 executes C5, C8, C9 (backward) and C10 and records C1–C4, C6–C7 as `failed` or `planned` search runs with explicit access-gap reasons. In that case Track E's coverage statement must say that **no bibliographic database was searched**, that discovery relied on web search, ICAD browsing, reference lists and grey literature, and that the map is coverage-limited. This fallback is declared now, so its use is not a silent narrowing; it nonetheless limits every completeness claim.

## 6. Screening, identity, retrieval and extraction

### 6.1 Records

Every search run, occurrence, source, screening decision, identity link, extraction, appraisal and assistance event is a v1 record ([schemas](../../schemas/README.md)). Every search run keeps its raw export and a search-run record, and every returned occurrence has a `search_hit` record whose count must equal the run's retrieved count. Pilot occurrences stay `unresolved` unless their publication identity was actually checked.

### 6.2 Screening procedure

1. **Deduplicate** occurrences into publications by DOI, then normalized title + first author + year, keeping every discovery path (§6.4).
2. **Title/abstract stage.** The executing agent applies E1–E6. Decisions: `include` (proceed), `exclude` with one or more reason codes, `uncertain` (proceed to full text). When in doubt, retain.
3. **Full-text stage.** Each `include`/`uncertain` item is sought (§6.3) and rescreened against E1–E6 with the full text. Unavailable text yields `awaiting_text`, never `exclude`.
4. **Verification.** (a) Every full-text exclusion is re-examined in a separate later pass with the reason re-derived from the text. (b) A seeded random 10% sample (seed recorded) of title/abstract exclusions, minimum 20 items, is rescreened in a separate pass. (c) Disagreements go to full text. Agreement is reported as **intra-agent consistency**, not inter-rater reliability. No dual independent human screening exists; this is reported as a limitation in every downstream claim. If the owner or another human screens any items, those decisions are recorded as human decisions with their scope.
5. **Calibration.** The [pilot calibration set](PILOT_REPORT.md#eligibility-calibration) defines worked examples for borderline categories.

### 6.3 Retrieval

Seek lawful full texts through publisher open access, author/institutional repositories, preprint servers and theses. Never bypass paywalls, create accounts, purchase access or contact authors. Record each attempt in an access ledger. Paywalled items are not dropped: they enter the full-text request list for the owner gate (§13). An item read only by tool-mediated reading may be screened but not numerically extracted (§10).

### 6.4 Identity rules

- Publication, study, experiment and sample are separate levels (glossary G27–G31).
- A conference paper and its journal extension are two publications; they share a study unless the extension reports a new sample.
- Theses and papers from the same work share a study by default when author, design and N match; otherwise `provisional`.
- Reports from one laboratory reusing a participant pool without stating overlap are `unknown` overlap, not independent.
- A review never contributes primary observations; studies in it are retrieved individually.
- Corrections supersede; they are never averaged with the original.

### 6.5 Extraction

Track E extraction uses the v1 `extraction`, `study`, `experiment` and `sample` families plus the COMMON field groups adopted in the [analysis plan](ANALYSIS_PLAN-v1.md#5-extraction-fields): identity, provenance, population, intervention/comparator (actual sound exemplars, semantics and action mapping, alternatives, voice/lexical content, duration, level, training, environment), design, estimand key, estimate, dependence, outcome events versus missingness, selection/multiplicity, and appraisal/transport. Each numeric value needs a locator into a hashed manifestation. All eligible outcomes are extracted, not only those entering a synthesis.

Track G extraction uses the `theoretical_extraction` family: assertion, definitions, premises, inference, context, objections, interpretation and RQ links, with source wording, researcher interpretation and design implication kept in separate fields.

## 7. Track G theoretical sampling and concept revision

### 7.1 Sampling tiers

| Tier | Content | Selection basis |
|---|---|---|
| T1 | Brier's primary texts across versions (1996 onward) | Verified bibliography (#3); chronological coverage of core formulations |
| T2 | Sources Brier's arguments depend on: Peirce (sign/interpretant, categories), Luhmann (social systems/communication), Maturana and Varela (autopoiesis), Bateson, von Foerster, Shannon (on his own terms) | Actual citation dependency in T1 passages read |
| T3 | Comparator accounts: semiotic engineering (de Souza), grounding and common ground (Clark and colleagues), symbol grounding (Harnad), semantic information (Kolchinsky and Wolpert), ecological and cognitive human-factors accounts of alarms and auditory displays, anthropomorphism and voice interfaces | Address the same explanatory problem as an RQ1–RQ6 claim |
| T4 | Reception and criticism of cybersemiotics and of each T3 comparator | Substantive objection, not mere citation |
| T5 | Semiotics of auditory display and interface sound (e.g. Peircean analyses of interface sounds, modes of listening) | Direct overlap with the applied question |

Each addition records why it was added, which concept or argument it tests, and how it was found. Secondary interpretation never substitutes for an unavailable T1 or T2 primary text; it is recorded as such.

### 7.2 Concept register

The [concept register](CONCEPT_REGISTER.md) holds versioned sensitizing concepts (v1 at freeze). Each revision records the date, the triggering source and passage, the old and new formulation, the reason, and an **impact check**: does the revision change any Track E eligibility rule, coding field or outcome family? If yes, a protocol amendment (§14) with rescreening/recoding assessment is mandatory before the change takes effect. If no, the revision is logged as nonmaterial to Track E.

### 7.3 Negative cases

For every concept cluster, run and log at least one targeted search for disconfirming or rival positions (e.g. critiques of autopoiesis transfer to social or technical systems; arguments that human-like voices improve compliance; evidence that abstract sounds outperform speech in specific conditions). Record what was found and how it changed or failed to change the interpretation.

### 7.4 Stopping

A concept cluster stops when **all** of the following hold: (a) every T1 text identified by #3 as core has been read to the extent its claims require, or has an access-gap record; (b) the last two sampling additions for that cluster produced no new construct, premise or objection relevant to RQ1/RQ2; (c) its negative-case search has been executed and logged; (d) a scope statement says what was not sampled and why. Paper counts are not a stopping criterion. Interpretive products are not claimed to be reproducible; their provenance is.

## 8. Appraisal

**Empirical (Track E).** Domain-based judgements per experiment and outcome, each `low concern`, `some concern`, `high concern` or `unclear`, with rationale and locator; no summed score. Domains: (D1) assignment and order — randomization, counterbalancing, carryover; (D2) stimulus equivalence and confounding — content, duration, level, training equated or not; (D3) outcome measurement validity — definitions, scoring, chance level, clock origin; (D4) missing data and exclusions; (D5) selective reporting — outcomes measured versus reported; (D6) exposure and training comparability; (D7) transfer — task, population and setting relative to the synthesis question; (D8) statistical reporting sufficiency. This is a project instrument. It is not RoB 2 or any other published tool and claims no equivalence with one; adopting a published tool would require an amendment.

**Body of evidence.** For each synthesis cell, a GRADE-informed narrative judgement of risk of bias, inconsistency, indirectness, imprecision and possible reporting bias, as recommended for non-pooled syntheses by SWiM item 6. No formal GRADE rating is claimed.

**Theoretical (Track G).** Fidelity to the source, coherence of premises and inference, explanatory scope, economy relative to alternatives, and strength of objections. Theory and experiments are never scored on one scale.

## 9. Synthesis

Track E produces an evidence map (counts of independent components by representation × outcome family × semantic dimension × training/delay), descriptive tables, and conditional within-cell syntheses under the [analysis plan](ANALYSIS_PLAN-v1.md). Pooling is decided per cell; non-pooled synthesis follows SWiM items 1–9. Network meta-analysis is **not** planned (analysis plan §8). Track G produces reconstruction, comparison and refutational memos and the remove-Brier test inputs. Integration (#11) records, for every proposition, its strongest counterexample, alternative explanation, boundary conditions and revision criterion.

## 10. Reading, locators and AI assistance

| Reading route | What it may support | What it may not support |
|---|---|---|
| Hashed manifestation (bytes with SHA-256; local only if redistribution is permitted) read by page/section | Locator-bound extraction, quotation within rights limits, decisive claims | — |
| Tool-mediated reading (G34): an intermediary model's paraphrase without bytes | Discovery, identity checks, eligibility screening, overlap mapping, bounded non-decisive descriptive statements labelled as tool-mediated | Numeric extraction, quotations, decisive claims, `full_item_read` reading records |
| Abstract or landing page | Title/abstract screening and bounded statements about stated scope | Methods, results or conclusions |
| Search-result title | Discovery only | Any content claim |

A decisive claim (G35) without a hashed manifestation is blocked until bytes are lawfully obtained (via the owner gate in §13) or the claim is narrowed.

**AI assistance disclosure** follows the 2025 Cochrane/Campbell/JBI/CEE position statement: for every AI tool that makes or suggests judgements, record the tool name and version (or unknown), dates of use, purpose and affected stages, justification including piloting, verification steps and limitations, in `assistance` records. At freeze, the AI roles are:

| Role | Actor | Verification available |
|---|---|---|
| Searching, screening, extraction, appraisal, synthesis drafting | Claude (Anthropic), the executing agent; model as reported by the session | Same-agent rechecks only (§6.2) |
| Web reading | WebSearch and WebFetch tools; WebFetch passes content through an unidentified intermediary model | Cross-checks against a second fetch or a hashed source where obtainable |
| Calculations | Versioned Python code with known-answer tests | Deterministic re-execution |
| Human review | None at freeze | Owner checks only if the owner performs them; external review only under #19 |

Repeated model passes, subagents or tools are correlated checks, never independent human screening, peer review or validation.

## 11. Completion and stopping

**Track E search completion** is coverage-based: every channel in §5.1 has a recorded outcome (`completed`, `partial` with reason, or `failed`/`planned` with an access-gap record); all occurrences are deduplicated with provenance; all screening decisions are resolved or explicitly `awaiting_text`; backward chaining is complete for all included reports and EQ8 reviews. There is no target number of papers. A sparse or entirely non-pooled result is acceptable.

**Track G stopping** follows §7.4 per concept cluster.

**Refresh.** #17 must rerun the executed channels from 2026-10-04 to the actual refresh date and screen new hits under this protocol or its amendments.

## 12. Priority corpus and execution batches

These batches order work; they do not narrow eligibility. Paywalled and non-English items are retained in every batch with access records.

| Issue | Batch | Content |
|---|---|---|
| #3 Brier | B1 | Verify bibliography and editions: the 1996 formulation; *Cybersemiotics: Why Information Is Not Enough* (University of Toronto Press; first-edition year and later printings to verify); *Entropy* 12(8) 2010; *Integral Review* foundation article; *Studia kulturoznawcze* 2015; Brier-authored chapters in Vidales and Brier (2021). Distinguish Thomsen, Vidales and other authors. |
| #3 | B2 | Lawful access for each core text; chronology and priority-reading map; reception leads (e.g. Cobley 2010; Thomsen and Brier 2014). |
| #4 Related | R-A | T2 dependencies actually cited by T1 passages. |
| #4 | R-B | T3 comparators, prioritising de Souza (semiotic engineering), urgency-mapping and alarm-design reviews, voice anthropomorphism work, Clark common ground, Harnad, Kolchinsky and Wolpert. |
| #4 | R-C | T4 reception and criticism; T5 semiotics of auditory display. |
| #5 Auditory | A0 | Gate check (§5.3) and channel decision. |
| #5 | A1 | Backward chaining from the Nees–Liebman included-study list, re-derived from a verifiable manifestation or verified item by item. |
| #5 | A2 | EQ1–EQ8 in available channels (C1–C7 if gated open; otherwise C5, C8, C10). |
| #5 | A3–A6 | Targeted clusters: urgency/hazard (EQ2), voice and affect (EQ3), uncertainty (EQ4), learning/retention (EQ5), plus monitoring sonification (EQ6) and interruption (EQ7). |
| #5 | A7 | Update window 2021-04-01 to 2026-10-04 for the cue-family comparison (N13). |
| #5 | A8 | Grey literature and non-English discovery (C10, C8 translations). |

## 13. Access gaps and human gates

Known at freeze (details in [pilot report](PILOT_REPORT.md#access-gaps)):

- **No bibliographic database is reachable** by the agent (C1–C4, C6–C7). Human gate `HG-R002-DATABASE-ACCESS` describes the smallest owner action: either allow the session to reach `api.openalex.org` and `api.crossref.org`, or open the prepared OpenAlex URLs and save the JSON pages into a connected folder. Optional: ACM/IEEE/Scopus/Web of Science exports if the owner has lawful access. The gate does not block protocol acceptance; the §5.3 fallback applies until it is satisfied.
- **No source bytes can be retained** for web-reachable texts, because the workspace cannot download from publishers or repositories and WebFetch returns paraphrase only. Locator-bound extraction in #7/#9 therefore needs lawful PDFs supplied by the owner (a full-text request list will be prepared by #3/#5) or a network-policy change. This will be raised as a separate source-access gate when the first list exists.
- **Nees–Liebman VoR** was not readable; the preprint was used with version limits. Not gated, because the overlap judgement does not depend on VoR-only details; a VoR reading would upgrade the comparator record.

No gate authorizes purchase, account creation, paywall bypass, author contact, registration or submission.

## 14. Amendments

Any change to a frozen rule creates a new versioned file (e.g. `PROTOCOL-v1.1.md`), keeps the previous file unchanged, and adds an `amendment` record of kind `protocol_change` binding both artifacts by hash, with reason, prior exposure to evidence, affected records and claims, required rework and verification. Concept-register revisions follow §7.2. Changes made after seeing results must say so. Syntax translation that preserves concept blocks (§5.2) is not an amendment. The [amendment register](amendments/README.md) lists all amendments.

## 15. Reporting and limitations

Final reports will use PRISMA 2020 and PRISMA-S items where applicable and SWiM for non-pooled synthesis, with an item-by-item applicability record rather than a compliance claim ([reporting applicability](REPORTING_APPLICABILITY.md)). The flow will distinguish occurrences, publications, studies, experiments, samples and unavailable reports.

Limitations carried by every downstream claim unless later removed by evidence: single-agent conduct with no independent human screening or extraction; no PRESS-reviewed searches; possible absence of any bibliographic database search; tool-mediated reading for scoping; English-language bias of the web channel; exposure to the Nees–Liebman results and to the project's preferred direction before freeze; and laboratory-to-field transfer limits of the empirical literature.
