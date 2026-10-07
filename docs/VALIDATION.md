# Validation and acceptance

[Runbook](AGENT_RUNBOOK.md) · [Data model](DATA_MODEL.md) · [Executable schemas](../schemas/README.md)

## Offline commands

Use Python 3.11 or newer and the standard library. From a clean checkout:

```sh
python3 -m unittest discover -s tests -v
python3 tools/validate.py
python3 -m tools.build_record_fixtures --check
```

The normal validator checks the live manifest and verifies the exact generated
JSON, CSV and Markdown bytes. It does not ingest fixture directories. It prints
a deterministic machine-readable report with `structural_result`, performed
checks, counts, currency, warnings and `not_evaluated` fields.

To save that same report and compare immutable history against a locally
available accepted base, use:

```sh
python3 tools/validate.py --previous-ref FULL_ACCEPTED_COMMIT_SHA --report build/validation.json
```

Replace `FULL_ACCEPTED_COMMIT_SHA` with the actual complete commit SHA. The command
reads existing Git objects and never fetches. Alternatively, `--previous PATH`
accepts a prior portable v1 snapshot. A prior commit without a registry is accepted
as an empty bootstrap only if it contains no canonical record objects. Without a
prior input, the report explicitly says `history_comparison: not_supplied`; a
standalone file cannot prove its own history.

After an authorized canonical record change, rebuild the four generated views:

```sh
python3 tools/validate.py --write-exports
```

This first validates records, references, artifact hashes, stage declarations and
citations. Ordinary validation compares the results without changing them.
A stale or missing generated file fails; it is not silently regenerated in CI.

## Synthetic demonstrations

The [v1 fixture corpus](../tests/fixtures/records/v1/README.md) is explicitly
fictional. It is an explicit migration from the verified R001 prepass, preserving
the supplied source bytes, original fields and append-only correction story.

```sh
python3 tools/validate.py --records tests/fixtures/records/v1/valid_before.json --dataset-kind fixture
python3 tools/validate.py --records tests/fixtures/records/v1/valid_corrected.json --dataset-kind fixture --previous tests/fixtures/records/v1/valid_correction_pending.json
```

The caller must choose live or fixture context; changing a field in a file cannot
choose its validation context. Live registry loading is a different route with
approved record roots. There is also an empty live/not-started fixture. Synthetic
records, artificial reviewers and fabricated participant results cannot satisfy
live completion gates.

Exit codes are **0** for structural pass, **1** for failed validation or inaccessible
input/output, and **2** for invalid CLI usage. Failure reports contain
`structural_result: fail` and an error beginning with the rule code where a record
rule failed. Excessive input nesting fails closed. Duplicate JSON keys,
nonstandard NaN/Infinity and numeric overflow are rejected.

## Checks implemented

| Layer | Current checks |
|---|---|
| Repository structure | Retains the bootstrap required-file, programme metadata/dependency DAG, local Markdown file-target and JSON checks. Required registry files cannot be removed to revert to bootstrap-only validation. |
| Individual records | Sixteen closed versioned Python schemas, typed IDs/pins, strict types, finite numbers, explicit unknowns, qualified times, rights/access/reading separation, local transitions and immutable claim class. |
| Loading and history | Manifest roots, path containment, no symlinks, filename/ID agreement, one owner per global ID, no unregistered records, live/fixture separation, and append-only comparison when a prior accepted snapshot is supplied. |
| Reference graph | Exact revision and type checks, mandatory support edges, an evidence DAG distinct from membership/overlap links, source manifestations and covered locators, outcome/sample/unit consistency, aliases and sample overlap. |
| Support and currency | Class-specific claim support, exact appraisal/review targets, actual recorded human-gate relationships, material amendment requirements and transitive invalidation. Stale work can remain in progress but cannot enter selected current outputs. |
| Local artifacts | Actual SHA-256 comparisons for retained fixture sources, known artifact objects, derivation artifacts, protocol amendments and manuscript/stage artifacts. A bare source digest with an external location is not falsely claimed to have been locally rehashed. |
| Evidence flow | Run-reported versus stored retrieval counts, duplicate hits, distinct publications/studies/experiments/samples/outcomes, effective screening decisions, unavailable reports, known overlap groups and explicit unknown-dependence warnings. |
| Exports | Exact deterministic JSON/CSV/Markdown count views and an index of latest record revisions. No estimated independent-study count or pooled statistic. |
| Citations | Bibliography keys, exact source revisions, document hashes, source/claim line bindings, unbound Markdown markers, stale references and source membership in a bound claim's evidence chain. |
| Stage declarations | Empty/synthetic completion refusals, typed current inputs, scoped review coverage and required artifacts. Internal-package declarations need protocol/corpus/analysis declarations; the independent human extensions remain separate. |

The record schemas are executable Python contracts, **not JSON Schema**.
See [schemas/README.md](../schemas/README.md) for the exact field dictionary and
per-family transition rules.

## Citation convention and limits

`research/registry/bibliography.json` contains
`{"schema_version": 1, "entries": [{"key": "...", "source_ref": {"id": "SRC-...", "rev": 1}}]}`.
Keys are unique and resolve to an exact nonstale source revision. A retained
source pin remains valid after a harmless metadata/access update; it is never
silently retargeted to the latest revision. Corrections and invalidations still
quarantine affected pins.

Each path in the live manifest's `citation_manifests` names a JSON sidecar:

```json
{
  "schema_version": 1,
  "artifact": {"path": "paper/manuscript.md", "sha256": "ACTUAL_SHA256"},
  "bindings": [{
    "start_line": 12,
    "end_line": 14,
    "citation_keys": ["example"],
    "source_refs": [{"id": "SRC-EXAMPLE", "rev": 1}],
    "claim_refs": [{"id": "CLM-EXAMPLE", "rev": 2}]
  }]
}
```

This is an illustrative form, not a valid live record or invented digest. The
supported Markdown markers are Pandoc-style bracket citations such as
`[@example, p. 2]` and exact claim markers such as `{{claim:CLM-EXAMPLE@2}}`.
Code fences and inline code are excluded. Every marker in a manuscript under
`paper/` needs a hash-bound sidecar. All cited source pins in a claim binding must
belong to its transitive evidence chain; source-only contextual bindings are
allowed. Project constraints and explicit conventions need their declared basis
rather than invented literature.

This grammar does not claim full CommonMark/Pandoc/LaTeX parsing. It does not
detect unmarked unsupported prose, establish quotation accuracy or prove citation
entailment. Richer manuscript build/render checks remain part of MHAC-R016.
A separate citation for historical discussion may require a future explicit
historical-use profile; v1 current-output checks are deliberately conservative.

## Stage declarations and scientific limits

A stage entry has exactly `stage`, `status`, `evidence_refs`, `review_refs`,
`human_gate_refs`, `artifacts` and `limitations`. Stages are protocol, corpus,
analysis, internal_package, external_review and participant_study. Status is
not_started, in_progress, blocked or complete. Pins have the ordinary exact
`{id, rev}` form; artifacts have an actual relative path and SHA-256.

Completed declarations require live, nonempty, usable current evidence, retained
artifacts and performed passing reviews of the exact evidence revisions.
Unfinished searches, unresolved effective screening decisions, draft/disputed
extractions and unchecked appraisal cannot meet the relevant gate. A non-pooling
analysis is permitted; no meta-analysis is required merely to obtain a pass.

The report's stage result says **structural prerequisites**, never scientific
acceptance. Protocol-specific reading sufficiency, source fidelity, actual report
identity, methodological adequacy and genuine human identity/independence remain
separate judgments. R001 conservatively requires a full recorded report reading
for promoted empirical findings; MHAC-R002 must justify any more specific coverage
profile before adopting it.

Participant-study completion is explicitly deferred: a literature experiment
record or a ready experiment protocol cannot prove a new pilot was executed.
R001 rejects that completion declaration until actual pilot-result acceptance is
implemented under MHAC-R020. Real external feedback requires actual human-gate
provenance; multiple agent passes never count as independent human review.

## CI and merge evidence

The `repository-integrity` job runs the full offline tests, validates live data
and deterministic exports, and checks fixture regeneration. Checkout retains its
pinned action, read-only permissions and credential non-persistence. It now makes
history available and supplies the actual PR base SHA or preceding push SHA to the
validator. Manual workflow execution compares against the local parent commit.
No online resolver, secret, GPU or participant is needed.

Any optional online bibliography resolver remains separately invoked, cached and
logged; none is introduced by R001. Online DOI resolution would not establish
reading or source support.

Inspect check-runs and legacy statuses on the exact final PR head, required
approvals and mergeability. Squash merge normally and verify push-triggered CI for
the merged main SHA. Empty check lists are not green CI. Record actual landing
evidence on the [issue](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/1)
and PR, separately from the current research state.
