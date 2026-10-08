# Issue #1 assessed contract

MHAC-R001 — Research registries, provenance validators and reproducible CI.
Issue open, one comment read. See PROVENANCE.json for identifiers and source URLs.

## Purpose (verbatim issue text)
Turn the bootstrap's minimal integrity checks into a usable, fail-closed research-record pipeline. This is infrastructure, not evidence synthesis.

## Required work (verbatim issue text)
Implement versioned, documented records for source/publication identity, search runs and hits, screening decisions, study/experiment/sample identity, theoretical extractions, empirical outcomes and appraisal, claims, design requirements, amendments, AI assistance and human gates. Start from the data contract rather than creating a heavyweight database or RAG service. Use stable IDs, cross-record validation, provenance locators, explicit unknowns, rights/access/reading status and reproducible exports. Separate fixture data from live records. Provide a clean-checkout command that works without network access or secrets. Add deterministic evidence-flow counts, citation/reference-integrity checks and a machine-readable validation report; clearly identify checks deferred to later stages.

## Acceptance (verbatim issue text)
- [ ] Schemas and a data dictionary cover the required record types and permitted lifecycle transitions.
- [ ] Tests reject duplicate IDs, dangling references, invalid statuses, false full-text-review assertions, dependency cycles, synthetic/live-data contamination and unsupported claim promotion.
- [ ] Empty live registers remain valid only as `not_started`; empty evidence cannot satisfy research-completion gates.
- [ ] Positive fixtures, negative fixtures and CLI failure exit codes are tested.
- [ ] Documentation distinguishes structural CI from source fidelity, independent review and scientific validity.
- [ ] No network-dependent check is made a flaky offline merge gate; any bibliography resolver is separately invoked, cached and logged.

## Comment read (verbatim plain text)
## Dependency-ready after bootstrap

The programme bootstrap is merged via #21 at `796151a33ec7a1acc026b239fe5c883312ebf40b`. Final PR checks and the post-merge main run passed.

This issue is the first implementation task. Read its full body plus `AGENTS.md`, `RAG.md`, `docs/PROGRAMME.md`, `docs/AGENT_RUNBOOK.md`, `docs/DATA_MODEL.md`, `docs/VALIDATION.md` and `docs/RESEARCH_INTEGRITY.md` from live main. A paste-ready prompt is in `KICKOFF.md`.

The existing validator is intentionally only a bootstrap structural check with 26 unit tests. Full research-record schemas, provenance/lifecycle checks, evidence-flow exports and scientific-stage integrity gates are NOT already implemented. Complete this issue's actual acceptance criteria before starting #2. No literature study or manuscript work has been executed by the bootstrap.

## This turn's override
The user's read-only prepass instruction overrides the issue execution prompt's eventual PR/merge/publication actions. No ownership announcement or comment was posted.
