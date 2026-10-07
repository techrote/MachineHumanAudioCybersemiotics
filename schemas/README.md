# Executable record contract — mhac-records/1

`v1.py` implements a closed, versioned Python contract using the standard library.
It is not a JSON Schema interpreter. `validate_record(record, *, expected_kind)`
accepts caller-selected `live` or `fixture` context and raises
`schemas.ValidationError`. Cross-record meaning belongs to `tools/record_graph.py`.

## Common forms

Every field below is required unless explicitly marked optional. Objects are
closed: undocumented fields are errors. All lists may be empty unless specified.

| Form | Exact fields and meaning |
|---|---|
| Record | `schema_version: 1`, `id`, `kind`, `synthetic: bool`, `issue: positive int`, `revisions: nonempty list`. |
| Revision | `rev: positive int`, `at: timestamp`, `actor`, `basis: list of unique pins`, `data`, `factual_status`. Revisions are contiguous from 1, timestamps nondecreasing. |
| Actor | `kind: agent/human`, `id: text`; optional `tool` and `model`, each text or a missing value. |
| Pin | Exactly `{id: text, rev: positive int}`. Prefixes match family kinds. |
| Missing value | Exactly `{state: unknown/not_reported/not_applicable, reason: text}`. |
| Tagged value | Either a missing value or exactly `{state: known, value: <specified type>}`. |
| Known numeric value | Existing prepass fields `value` and `n` retain direct finite numbers/exact integers; a missing value is their alternative. Booleans are never numeric values. |
| Timestamp | RFC 3339 date/time with seconds and `Z` or an explicit offset. Dates/read/access/review events are separate from recorded revision times. |
| Text | Nonblank string. String lists contain unique nonblank strings unless documented otherwise. |
| Artifact | Exactly `{path: relative text, sha256: lowercase 64-hex digest}`. Restricted artifacts may instead be cited in descriptive provenance fields; do not fabricate bytes or hashes. |
| Locator | `manifestation_id`, `coordinate`, `start: int`, `end: int`; optional `printed_label`, `section`, `paragraph`, `table`, `figure`, `cell`. Coordinates: `file_page_1based`, `pdf_page_0based`, `html_paragraph_1based`. |
| Located source | Exactly `{source_ref: pin, locator}`. |
| Dependence | Exactly `{relation: shared_sample/repeated_measures/shared_control/overlap/independent/unknown, correlation: tagged finite number in [-1,1]}`. |

`factual_status` is one of `discovery`, `source_reported`,
`researcher_interpretation`, `derived`, `project_decision`, `synthetic`. Fixture
revisions use `synthetic`; live revisions cannot. Creation/update dates are the
first/last revision timestamps. IDs use the family prefixes below followed by a
hyphen and uppercase letters, digits or hyphens.

## Source, discovery and identity families

| Kind / prefix | Required data fields; optional fields follow the semicolon |
|---|---|
| `source` / SRC | `title`, `authors: [{name,role}]` (role author/editor/translator/corporate_author), `publication_date: tagged date` (year, month or day precision), `identifiers: [{scheme,value,status,provenance}]` (scheme doi/isbn/url/other; status candidate/verified/conflict), `source_type` (article/book/chapter/conference_paper/thesis/preprint/report/review/web/correction/other), `language: tagged text`, `edition: tagged text`, `metadata_status` (candidate/verified/conflict), `metadata_evidence: [text]`, `access_status`, `access_at: timestamp`, `access_reason`, `rights: {status,reason,evidence: tagged text}`, `validity` (active/corrected/retracted/withdrawn/superseded), `family_links: [{relation,source_ref,reason}]`, `manifestations: [{id,sha256,extent,coordinate, ...}]`; optional `alias_of: pin`, `alias_reason`. |
| `search_run` / SRCH | `lane`, `protocol_version`, `mode` (pilot/production/update), `status` (planned/running/completed/partial/failed), `platform`, `interface`, `query`, `filters: [text]`, `coverage: {start: tagged date,end: tagged date}`, `started_at: tagged timestamp`, `finished_at: tagged timestamp`, `reported_count: nonnegative int or missing`, `retrieved_count: nonnegative int`, `export: tagged artifact`, `pagination: {complete: bool,detail}`, `failures: [text]`, `boundary`. |
| `search_hit` / HIT | `search_ref`, `ordinal: positive int`, `raw_metadata: text`, `returned_identifiers: [{scheme,value}]`, `status` (unresolved/resolved/duplicate/unresolvable), `resolution_reason`; `source_ref` required for resolved/duplicate; optional `duplicate_of: pin` only for duplicate. Unresolved/unresolvable records have no source_ref. |
| `screening` / SCR | `source_ref`, `stage` (title_abstract/full_text), `protocol_version`, `rule`, `decision` (pending/include/exclude/awaiting_text/uncertain), `reason`, `access_limitation`, `reading_refs: [pin]`, `review_refs: [pin]`; optional `supersedes_ref: pin`. Decision actor is revision.actor. |
| `study` / STUDY | `publications: nonempty [pin]`, `identity_status` (unresolved/provisional/resolved/fixture_asserted_same/alias), `identity_basis`, `identity_locators: [located source]`, `scope`; `alias_of: pin` required only for alias. fixture_asserted_same is fixture-only. |
| `sample` / SAMPLE | `n: nonnegative int or missing`, `population: text or missing`, `recruitment: text or missing`, `missingness: tagged text`, `overlap: [{sample_ref,relation,reason}]` (known_shared/partial_overlap/shared_control/unknown/independent), `uncertainty`, `status` (provisional/checked/withdrawn/superseded); optional `evidence: [located source]`, `collection_dates: {start: tagged date,end: tagged date}`. |
| `experiment` / EXP | `study_ref`, `sample_refs: nonempty [pin]`, `conditions: nonempty [text]`, `outcomes: nonempty keyed object` with `{unit,contrast}` per outcome (optional `timepoints: nonempty [text]`), `dependence`, `status` (provisional/extracted/checked/withdrawn/superseded), `report_label`, `assignment`. |

Source access: `not_attempted`, `metadata_only`, `abstract_only`, `partial_text`,
`full_text_available`, `unavailable`. Rights: `unknown`, `metadata_only`,
`quotation_limited`, `redistribution_permitted`. Positive rights require a known
supporting reference. A source can have no manifestations when bytes are
unavailable. Each manifestation adds optional `fixture_path` (fixtures only) or
`location` (permission-safe description). `extent` is the number of coordinates,
not the last PDF index. Family relations: `duplicate_of`, `version_of`,
`translation_of`, `companion_of`, `correction_of`. A source alias has validity
superseded and an explicit alias_reason. Source reading is exclusively AID data;
there is no source-level field claiming a reader read the item.

A manifestation may also have `local_path`, a normalized relative POSIX path to
retained, permission-safe source bytes. It requires source rights status
`redistribution_permitted` with supporting evidence; the loader checks the actual
file against the manifestation hash. Keep restricted external holdings in the
descriptive `location` field with no local_path. This record does not itself grant
permission to redistribute material.

## Extraction, argument and design families

| Kind / prefix | Required data fields; optional fields follow the semicolon |
|---|---|
| `theoretical_extraction` / TX | `source_ref`, `reading_ref`, `locator`, `status` (draft/extracted/source_checked/disputed/withdrawn/superseded), `assertion`, `definitions: [{term,definition}]`, `premises: [text]`, `inference: [text]`, `context`, `objections: [text]`, `interpretation`, `rq_refs: nonempty [text]`, `boundaries`. |
| `extraction` / EX | All preserved fields `source_ref`, `experiment_ref`, `sample_ref`, `outcome`, `value: finite number or missing`, `unit`, `n: nonnegative int or missing`, `dispersion`, `scope` (bounded/complete_report), `reading_ref`, `locator`, `note`; plus `status` (draft/extracted/source_checked/disputed/withdrawn/superseded), `conditions: nonempty [text]`, `contrast`, `timepoint`, `task`, `stimuli`, `training`, `population` (these four text or missing), `missingness: tagged text`, `dependence`, `field_locators: {value: locator,n: locator,dispersion: locator}`, `derivation`. |
| `appraisal` / APP | `target_ref`, `domain`, `judgment`, `rationale`, `status` (proposed/checked/disputed/revised/withdrawn/superseded), `criterion`, `tool_version: tagged text`, `evidence: [located source]`, `uncertainty`. Assessor is revision.actor. |
| `claim` / CLM | Preserved `class`, `lifecycle`, `statement`, `boundaries`, `counterarguments`, `uncertainty`, `evidence_refs`, `appraisal_refs`, `review_refs`; plus `argument: {premises: [text],inference_steps: [text],revision_criterion}`. Class project_constraint adds `decision_artifact`; design_hypothesis adds `mechanism`, `variables: nonempty [text]`, `test_plan` and optional `test_refs: [pin]`; unvalidated_convention adds `convention_reason`. Other class-specific fields are rejected. |
| `requirement` / REQ | `claim_refs: nonempty [pin]`, `status` (proposed/specified/internally_checked/evidence_supported/superseded/rejected), `statement`, `revision_criterion`, `class` (project_constraint/design_hypothesis/unvalidated_convention/evidence_informed), `scope`, `mechanism`, `conditions: [text]`, `risks: [text]`, `test_refs: [pin]`, `variables: [text]`, `result_refs: [pin]`. |
| `experiment_protocol` / TEST | `hypothesis_refs: [pin]`, `status` (draft/internally_checked/readiness_blocked/ready_for_authorized_execution/superseded/withdrawn), `hypotheses: nonempty [text]`, `estimands: nonempty [text]`, `outcomes: nonempty [text]`, `manipulations: [text]`, `checks: [text]`, `sampling`, `randomization`, `analysis`, `exclusions`, `ethics`, `privacy`, `gate_refs: [pin]`, `exposure` (prospective/retrospective/synthetic), `limitations`. |

Dispersion is missing or `{state: known, value: {measure: sd/se/variance,
value: nonnegative finite number, unit}}`. The `ci95` variant instead has
`{measure: ci95, lower: finite number, upper: finite number, unit}` with ordered
endpoints. Derivation is missing or
`{state: known, value: {input_refs: nonempty [pin], transformation, version,
assumptions: [text], output: finite number, artifact}}`. A recorded derived output
must equal the extraction value and use factual_status `derived` or `synthetic`.
The exact source locators for all three reported numeric fields are explicit even
when a passage states a quantity was not reported.

Claim classes: `project_constraint`, `source_claim`, `empirical_finding`,
`theoretical_interpretation`, `synthesis_proposition`, `design_hypothesis`,
`unvalidated_convention`. A class never changes within one ID. First revision
lifecycle must be `proposed`; ordinary progression is `proposed` → `source_checked`
→ `internally_audited` → `externally_reviewed`. Rework can return to proposed or
source_checked. `superseded`/`withdrawn` are terminal. Argument adequacy and source
fidelity are separate checks; nonempty prose is not proof that an argument works.

## Correction, assistance and human gates

| Kind / prefix | Required data fields; optional fields follow the semicolon |
|---|---|
| `amendment` / AMD | `kind` (extraction_correction/record_correction/source_invalidation/source_correction/protocol_change/identity_merge/identity_split/nonmaterial), `target_refs: [pin]`, `replacement_refs: [pin]`, `reason`, `prior_exposure`, `required_rework`, `verification`, `materiality` (material/nonmaterial), `status` (proposed/applied/verified/rescinded). Effect comes from applied/verified records only. `protocol_change` additionally requires the exact `rule_change` variant below. |
| `assistance` / AID, reading | `subtype: reading`, preserved `source_ref`, `manifestation_id`, `access_at_read`, `reading_status` (not_read/selected_ranges_read/full_item_read), `ranges: [[start,end]]`, `method`; plus `status` (planned/performed/failed), `performed_at: tagged timestamp`, `independence`. |
| `assistance` / AID, review | `subtype: review`, preserved `scope` (source_fidelity/internal_audit/external_feedback), `outcome` (pass/fail/inconclusive), `verification` (not_checked/agent_checked/human_checked/independent_human_checked), `target_refs: nonempty [pin]`, `artifact`; plus `status`, `performed_at`, `independence`; `gate_ref: pin` required for external_feedback. Optional `input_refs: [pin]`. |
| `assistance` / AID, general | `subtype: assistance`, `task`, `input_refs: [pin]`, `output_refs: [pin]`, `artifacts: [text]`, `verification_steps: [text]`, `limitations`, `status`, `performed_at`, `independence`. Tool/model are revision.actor fields if known. |
| `human_gate` / HG | `need`, `reason`, `attempted_remedies: [text]`, `owner_action`, `evidence: tagged text`, `completion_signal`, `stop_condition`, `status` (proposed/waiting/satisfied/declined/blocked), `gate_class` (source_access/repository_approval/authorship_license/external_review/participants/other), `authorized_actor: tagged actor`; optional `reopen_reason`. |

An AID performed event has a known performed_at at or before its revision time;
planned events have no performed result. An agent cannot write human_checked or
independent_human_checked review results. External feedback additionally requires
a human actor and a referenced real satisfied external-review gate; synthetic
feedback never satisfies a live gate. Satisfaction of HG requires a human revision
actor, a known authorized human actor and known evidence. Agent-maintained pending
gate records remain valid. Reopening a finished/blocked gate requires reopen_reason.

A `protocol_change` amendment has `rule_change: {previous: {version, artifact},
replacement: {version, artifact}}`, using the hash-bound artifact form above.
Both version labels and artifact hashes must differ. Retain both versioned files
so that their bytes remain independently verifiable. This is the only applied
amendment variant allowed to have empty target_refs: the previous rule artifact is
its explicit target, and affected record pins are included when any already exist.
All other applied amendments need target record pins. `rule_change` is rejected
for all other amendment kinds. Search and screening retain their protocol_version
labels; protocol freeze and amendments bind accepted versions to exact artifacts.

## Transition and validation boundaries

Each stateful family rejects unsupported transition edges and revival from
terminal states. A corrected record is a new revision; material corrections and
their affected dependent records also require the cross-record amendment checks.
A captured source access observation can improve or worsen independently of prior
reading. Search occurrence identity and the original query are immutable across
revisions; terminal search runs do not acquire different historical counts.

The schema checks shape, enums, closed variants, finite values, local numeric/date
consistency and per-record state history. The graph checks typed references,
required evidence pins, source/reading identity, coverage, experiment identity,
dependence, claim support, amendment impact and actual gate relationships. The
loader checks duplicate IDs, caller-selected live/fixture boundaries, artifact
bytes and append-only history against a prior accepted snapshot. None of these
mechanical checks establishes source entailment, scientific quality, independent
human review or participant performance.
