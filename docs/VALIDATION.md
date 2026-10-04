# Validation and acceptance

[Runbook](AGENT_RUNBOOK.md) · [Data model](DATA_MODEL.md) · [Integrity](RESEARCH_INTEGRITY.md)

## Bootstrap checks implemented now

From the repository root with Python 3.11+:

```sh
python -m unittest discover -s tests -v
python tools/validate.py
```

The stdlib-only baseline checks required authority files, programme metadata and unique issue IDs, valid dependencies and cycles, local Markdown file targets and JSON syntax. Unit tests exercise positive and negative graph cases and missing-file/JSON/link failures. Anchor validity, full Markdown parsing, live GitHub issue state and source availability are not asserted by this baseline.

CI runs the same commands in the `repository-integrity` job on pull requests and pushes to main. External source retrieval is not part of the offline gate. A pinned checkout action and read-only workflow permissions limit unnecessary CI authority. No network service, API key, GPU or participant is needed for baseline checks.

## Required expansion in MHAC-R001

Implement versioned research schemas, IDs and reference checks, state-transition constraints, source/access/reading separation, claim class and promotion rules, source/claim/manuscript linkage, count reconciliation, deterministic export/rebuild checks, synthetic/live separation and truthful human-review/readiness gates. Add positive fixtures and negative tests for each rule. A fully empty research set is valid only as not-started, never as a completed review.

Optional online bibliography/link verification must be separately invoked, rate-limit-aware and cached/logged; do not claim a flaky network check is deterministic. A resolving DOI is metadata evidence, not proof the source supports a claim. No automatic checker replaces reading.

## Quantitative and manuscript checks

Later analysis code needs known-answer tests, explicit input identities, units and assumptions, reproducible seeds/dependencies, handling of missing/dependent observations and output reconciliation. Test more than a successful process exit. Meta-analysis is conditional; a documented non-pooling decision can satisfy the scientific work package without manufacturing a numerical estimate.

Manuscript builds must resolve bibliography/claim references, regenerate tables/figures and expose stale counts. Visually inspect any rendered output. Record what is and is not automated. Citation syntax checks cannot verify that a citation entails the accompanying statement; a source-fidelity audit must do that.

## Distinct acceptance layers

| Layer | What evidence is needed |
|---|---|
| Repository integrity | Actual successful local and CI results on the relevant commit. |
| Record/provenance integrity | Validated records and traced inputs, with truthful status. |
| Source fidelity | Direct checking of decisive passages, figures, data and attribution, with actor/scope recorded. |
| Analytical adequacy | Appropriate methods, transparent assumptions and critical review; not inferred from tests alone. |
| External scholarly critique | Actual human feedback and provenance under #19. |
| Human communication performance | Actual authorized study evidence under #20 or an appropriate later study. |

## Merge evidence

Check the exact final PR head, all required check-runs and statuses, approvals and mergeability. Zero returned checks is not success. Squash merge with expected head where available and then inspect the main push run for the merge SHA. Do not bypass restrictions, approve yourself as a fictional independent reviewer or close unmet research gates. Record PR/head/merge SHA, check outcomes, relevant artifacts and remaining limitations.
