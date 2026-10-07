# File-by-file implementation order for issue #1

Assessed base: `796151a33ec7a1acc026b239fe5c883312ebf40b`. This is a prepass and additive proposal, not issue completion. Do not close #1 or start its dependent scientific acceptance gates from these results.

## Acceptance labels (issue order)

A1: schemas/data dictionary cover all types and lifecycle transitions.
A2: reject duplicate IDs, dangling refs, invalid statuses, false full-text assertions, cycles, contamination and unsupported promotion.
A3: empty live registers valid only as not_started; no empty research-completion gate.
A4: positive/negative fixtures and CLI failure exit codes tested.
A5: structural CI distinguished from fidelity, independence and scientific validity.
A6: no flaky network offline gate; any optional resolver separately invoked, cached/logged.

## Ordered changes

| Order | Exact intended path(s) | Implement / preserve | Acceptance |
|---|---|---|---|
| 1 | `docs/DATA_MODEL.md` | Extend existing contract with graph, identity/manifestation rules, exact pin/revision envelope, per-kind dictionary, scope/reading matrix and amendment semantics. Preserve existing integrity obligations. Use prepass doc as input, not a competing authority. | A1, A5 |
| 2 | `schemas/__init__.py`, `schemas/v1.py`, `schemas/README.md` | Stdlib schema functions for common envelope/unknown unions plus all family variants. One public validator dispatcher by schema_version/kind; no fake JSON-Schema compliance or custom schema-language engine. Distinguish factual status from claim class. | A1, A2 |
| 3 | `tests/test_record_schemas.py` | Closed-field/type/enum/number/time/unknown/locator rules; every permitted and forbidden lifecycle transition; all families, not only the example's ten. Require actual integers rather than bools. | A1, A2, A4 |
| 4 | `research/registry/state.json`, `research/registry/README.md` | Explicit versioned live manifest; root allowlist for lane-owned canonical paths; all empty evidence families remain not_started. No synthetic records in live registry; indexes generated, not separately edited. Distinguish records' work state from research-stage acceptance. | A3 |
| 5 | `tools/records.py`, `tests/test_record_loading.py` | Deterministic lane discovery; path containment/symlink policy; global ID/owner and typed revision index; filename/ID agreement; reject mixed synthetic/live; compare accepted prior snapshot for append-only history. Keep the existing read_json/unique_object; extend read_json to reject nonstandard NaN/Infinity with regression tests. | A2, A3, A4 |
| 6 | `tools/record_graph.py`, `tests/test_record_graph.py` | Extract/refine prototype pin index, distinct DAGs, required support edges, identity aliases, source/reading/version/coverage cross-checks, field locators, exact appraisal/review support, correction closure and export currency. Add full sample-overlap and identity split/merge cases rather than claiming exact-same-sample fixture covers them. | A2, A4 |
| 7 | `tests/fixtures/records/v1/` | Migrate frozen synthetic fixtures through an explicit converter/version change. Keep before, correction-pending, corrected and source-invalidated states; add all unimplemented family/lifecycle negatives. Preserve non-synthetic empty-live fixture without any invented evidence. | A1-A4 |
| 8 | `tools/evidence_flow.py`, `tests/test_evidence_flow.py` | Reconcile run-reported/retrieved/search-hit counts, dedup hits, unique reports and report screening by stage, included linked studies/experiments/samples/outcomes; retain unavailable/uncertain reports. Deterministic JSON/CSV/Markdown; derive from canonical IDs, never add a publication count to a study count. Selection/covariance needed for independence claims. | A2-A4; required-work exports |
| 9 | `tools/citations.py`, `tests/test_citations.py` | Resolve bibliography keys/SRC pins, manuscript source/claim sidecar bindings, local artifact locators and stale references offline. Expose unbound citations. Do not assert semantic entailment from syntactic citation resolution. | A2, A4, A5 |
| 10 | `tools/research_gates.py`, `tests/test_research_gates.py` | Stage-scoped structural prerequisites and actual evidence references; missing/unread/stale evidence and unsatisfied human gates block corresponding completion. Non-pooling may be legitimate; avoid universal "must contain meta-analysis" or "all human gates complete" requirements. No source quality inferred from schema pass. | A3, A5 |
| 11 | `tools/validate.py`, `tests/test_validate.py`, `tests/test_record_cli.py` | Preserve required-files/programme/link/JSON checks. Compose new modules. Add `--report`, caller-selected live/fixture context and local prior-snapshot input without network. Keep old CLI behavior compatible; report checked, failed, warning, not-evaluated separately. Tests use temp fixtures, not pretend full repository evidence. | A2-A6 |
| 12 | `docs/VALIDATION.md` | Document commands, error codes, generated-output rebuild, fixture isolation, snapshot comparison, exact implemented coverage and remaining fidelity/scientific gates. Document protocol coverage policy as external to R001. | A4-A6 |
| 13 | `.github/workflows/research-ci.yml` | Keep job/permissions/pinned checkout and baseline commands. Run added offline tests and current-live validation/export-diff. Supply prior accepted state through local checkout data only when history comparison is enabled. Do not invoke resolver in merge gate. No workflow mutation in this prepass. | A4, A6 |
| 14 (optional, not needed to close offline pipeline) | `tools/resolve_bibliography.py`, `research/registry/resolver-log/` | Separately invoked network resolver only if actually needed. Cache/log query, date, result/failure and normalized metadata. Discovery discrepancy creates a review item, not an automatic evidence rewrite. Do not add an unused network dependency. | A6 |

## Exact reuse rather than replacement

`tools/validate.py`: retain ValidationError, unique_object, read_json, string_list, validate_programme and its cycle checks, local_path, markdown_targets, validate_repository's existing checks, and CLI failure semantics. Extract reusable DAG traversal only if needed, preserving existing regression behavior. Do not run the programme DAG over every research relation.

`tests/test_validate.py`: retain all 26 tests unchanged initially; add tests in new modules. A later small parser/CLI extension may warrant additive assertions, not removal of old negatives.

`.github/workflows/research-ci.yml`: retain current read-only contents permission, credential non-persistence and pinned checkout. Only append offline commands after integration. The current CI confirms the bootstrap, not the new design.

`research/templates/README.md`: after schemas land, update examples to point to actual v1 record formats, keeping the warning that templates and synthetic fixtures are not live evidence. No edits to AGENTS.md, RAG.md or RESEARCH_INTEGRITY.md are needed to relax obligations.

## Remaining acceptance boundary

The prepass demonstrates the difficult relationships, provides a dictionary and runnable negatives, and preserves A5/A6 boundaries. It does not deliver every v1 schema, live registry loader, full flow/citation export, complete gate model, repository-integrated CLI/CI or a merged issue. Treat all issue checkboxes as implementation acceptance still to be assessed on the eventual final head, not satisfied merely because this ZIP is verified.
