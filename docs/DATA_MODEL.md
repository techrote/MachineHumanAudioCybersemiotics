# Research data and provenance contract

[Programme](PROGRAMME.md) · [Templates](../research/templates/README.md) · [Integrity](RESEARCH_INTEGRITY.md)

## Status and implementation boundary

This document specifies the record system MHAC-R001 must implement. The bootstrap provides `programme.json`, document/link checks and test scaffolding only. Do not imply that the full schemas, transition checks, evidence-flow export or citation validator already exist.

Prefer versioned UTF-8 JSON records with human-readable generated Markdown/CSV views. Use one stable record per file or bounded issue/source shards to reduce merge collisions. Canonical records have one owner; generated aggregates are rebuilt, not independently edited. Avoid a database/vector service unless a demonstrated need justifies its additional reproducibility cost.

## Record families

| Family | Essential fields beyond common provenance |
|---|---|
| Source/publication | Title, actual author/editor roles, date, DOI/ISBN/URL if verified, version/edition/language, publication-family links, source type, metadata/access/reading/rights states. |
| Search run | Lane, protocol version, pilot/production/update flag, platform/interface, exact query and filters, coverage and actual run dates, hit count/export/hash, pagination and failures. |
| Search hit | Search ID, original identifier/metadata, canonical source reference or unresolved identity, duplicate-resolution history. |
| Screening decision | Source ID, stage, eligibility rule/version, decision/reason, decision actor, verification/adjudication and access limitation. |
| Study identity | Publication links, study/experiment/condition/sample IDs, overlap/shared-control relations and uncertainty. |
| Theoretical extraction | Source/locator, source assertion, definitions, premises/inference, context, objections, interpretation and relation to RQs. |
| Empirical extraction | Study/outcome/condition/sample IDs, task/stimulus/training/population, reported estimate/units/dispersion/n, missingness, dependence, timing, derivation and locator. |
| Appraisal | Target record, criterion/domain, judgment, rationale, source evidence, assessor and uncertainty; no forced universal score. |
| Claim | Class, exact statement, evidence/argument IDs, boundaries, counterarguments, inference steps, uncertainty, lifecycle and verification level. |
| Design requirement | Class, state/communication scope, claim IDs, mechanism, conditions, risks, test IDs and revision/rejection criterion. |
| Experiment protocol | Hypotheses, estimands, outcomes, manipulations/checks, sampling/randomization, analysis/exclusions, ethics/privacy and readiness gates. |
| Amendment | Previous/new rule or artifact, actual date, rationale, prior exposure, affected records/claims, required rework and verification. |
| Assistance/review | Actual actor/tool/model where known, task/date, source/input IDs, artifacts, verification and independence limits. |
| Human gate | Need, reason, attempted remedies, owner action, evidence location, completion signal, stop condition and current status. |

## Common provenance

Each record needs schema version, unique stable ID, record type, creation/update date, originating issue, actor, source or basis, factual status, and synthetic flag. Use explicit unknown/not-reported/not-applicable values with reasons instead of made-up zeros or default certainty. Distinguish publication date, access date, actual reading date and review date. IDs are stable across corrected metadata; merge aliases with history rather than recycling IDs.

Suggested prefixes: `SRC`, `SRCH`, `HIT`, `SCR`, `STUDY`, `EXP`, `SAMPLE`, `TX`, `EX`, `APP`, `CLM`, `REQ`, `TEST`, `AMD`, `AID`, `HG`. Prefixes do not by themselves validate meaning. Define exact field types and transitions in schemas and tests in #1.

## Separate statuses

Metadata: candidate / verified / conflict. Access: not_attempted / metadata_only / abstract_only / partial_text / full_text_available / unavailable. Reading: not_read / selected_ranges_read / full_item_read. Verification actor: agent_checked / human_checked / independent_human_checked / not_checked, with identity and actual scope. Rights: unknown / metadata_only / quotation_limited / redistribution_permitted, with a supporting rights record.

`full_text_available` does not entail `full_item_read`. `human_checked` cannot be set from model agreement. A source record with a DOI does not imply the DOI resolves or that the text was read. Source excerpts may support bounded interpretation when honestly scoped; empirical full extraction and whole-book claims have stricter requirements.

## Integrity invariants

Unique IDs and valid references; acyclic issue dependencies; legitimate state transitions; complete source locators for decisive extractions; clear synthetic/live separation; no full-reading assertion without reading evidence; no external-review state without real feedback; no unsupported promotion of hypothesis to finding. Report inconsistent units, impossible counts, shared-sample ambiguity and missing dependency evidence.

Search-hit, publication, report, study, experiment and sample counts differ. Flow outputs must reconcile the correct level and retain unavailable reports. Multiple outcomes and reprints must not inflate independent-study counts. All derived values need input references, transformation/version, assumptions and reproducible output. Hashes identify files, not scientific validity.

## Storage and safe collaboration

Issue lanes own `research/sources/{brier,related,auditory}/`, corresponding search/extraction shards and later analysis/design directories. Shared exports and global index generation are serialized by the integrator. Test fixtures belong under `tests/fixtures/` or explicitly marked simulation paths; they never enter live source/evidence registers. Keep rights-restricted material and personal data outside this public repository.

## Release traceability

For a final claim, traverse `source → extraction → appraisal/argument → claim → requirement/proposition → experiment → manuscript locator`. Record breaks and unresolved evidence rather than auto-filling them. Completion validators must reject an empty corpus presented as completed research, but accept an empty, explicitly not-started bootstrap. Mechanical validation has a separate status from scientific acceptance.
