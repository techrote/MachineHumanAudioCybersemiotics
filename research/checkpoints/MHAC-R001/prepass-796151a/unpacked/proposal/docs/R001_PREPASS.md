# MHAC-R001 research-record architecture prepass

**Proposal, not accepted implementation.** Assessed repository: `techrote/MachineHumanAudioCybersemiotics`, main `796151a33ec7a1acc026b239fe5c883312ebf40b`. Issue #1 is open. The current user authorized read-only GitHub and a local prepass, overriding the issue's eventual publication/merge instructions. No real evidence is added by this packet.

## Decision

Keep UTF-8 JSON, one canonical file per stable logical ID, with a small append-only revision array. Add stdlib Python schema functions and a separate cross-record pass. Reuse the existing bootstrap validator, its JSON duplicate-key rejection, exception style, CLI conventions and unittest suite. Do not introduce a database, vector service, network gate, generic event-sourcing framework or a home-grown JSON-Schema interpreter.

A schema here means an executable versioned record contract. For production, use `schemas/v1.py` plus documented field definitions, not a claim of JSON Schema standards compliance. This resolves the tooling choice without adding an offline dependency. The prepass is deliberately labelled `mhac-r001-prepass/1`; its ten implemented kinds are a proof of relationships, not the full v1 schema collection. A migration must explicitly consume this fixture contract rather than treating it as already accepted live data.

## Assessed authority

Read the complete issue and its one current comment; AGENTS.md; RAG.md; docs/PROGRAMME.md; docs/AGENT_RUNBOOK.md; docs/DATA_MODEL.md; docs/VALIDATION.md; docs/RESEARCH_INTEGRITY.md; research/templates/README.md; tools/validate.py; tests/test_validate.py; and .github/workflows/research-ci.yml. The recursive assessed tree contains no schemas/ or research/registry/ directory. Templates are field prompts, not validated records. The bootstrap test module has 26 tests. Its local functions do not validate research records.

At assessment, the only branches were main and bootstrap/research-programme; no open PR was returned. The repository-integrity check on the assessed main SHA was completed/success. That is historical bootstrap CI, not CI for this proposal. Local execution of the preserved tests is separately recorded. The packet is not a full checkout; full repository validation was not rerun against invented placeholder authority files.

## Record graph

```text
SRCH search run -> HIT retrieval occurrence -> SRC publication/report
                                                 ^
STUDY research undertaking --publication links----+   (many-to-many)
  ^                 SAMPLE recruitment/observation cohort
  |                       ^          <-> overlap/uncertainty links
EXP reported experiment --+ sample participation
  | condition keys / outcome keys / contrast definitions
  v
EX empirical extraction ---------> SRC + exact manifestation + locator
  |       |                         ^
  |       +-------------------------+ AID scoped reading attestation
  v
APP appraisal -> CLM claim -> REQ requirement -> TEST planned protocol
                   |                              (not an executed EXP)
                   +-> manuscript citation bindings / generated exports

TX theoretical extraction -> source assertion + separate interpretation
                           -> APP/argument -> CLM interpretation/synthesis

AID review/assistance -> exact input/target revision(s), actor and scope
AMD amendment -> invalidated revision(s), replacement(s), reason and rework
HG human gate -> actual requested action / evidence / pending stop condition
```

Arrows for ownership, report membership, review targets and evidence support are typed. **Do not require the entire graph to be acyclic.** Publication/study membership and sample-overlap relations can legitimately be reciprocal. Require DAGs for issue dependencies, evidence/derivation `basis`, identity aliases and revision succession separately. Compute invalidation along evidence edges, not arbitrary adjacency.

## Common envelope and revision dictionary

Canonical path: the owning lane's directory followed by `<ID>.json`. `research/registry/` owns loader configuration, run state and generated indexes, not a second editable copy of every lane's records. Prototype snapshots bundle the same logical records into one file solely for finite fixture testing.

| Field | Type / rule |
|---|---|
| schema_version | Integer 1; booleans are not integers; unknown versions rejected, no silent coercion. |
| id | Stable nonblank prefixed ID; globally unique logical record owner. Never recycled or derived from a DOI, title or list position. |
| kind | Discriminated record type. Unknown kinds fail until an explicit schema migration exists. |
| synthetic | Boolean; live loaders require false; fixture loaders require true. Caller/path selects context, not the record itself. |
| issue | Positive issue number; production also binds repository identity in the registry manifest. |
| revisions | Nonempty list of immutable revision objects with contiguous 1-based rev. |
| revision.rev | Integer revision number; identity remains stable across corrected content. |
| revision.at | Actual timezone-qualified recorded-at timestamp; append times nondecreasing. Fixture story times are explicitly fictional. Production event dates (read/access/publication) remain separate fields. |
| revision.actor | Actual identity and kind (agent/human); unavailable model version recorded as unknown, not invented. |
| revision.basis | Unique exact `{id, rev}` support/derivation pins. Every semantically required supporting reference must be present; users cannot opt out of invalidation by omitting it. |
| revision.data | Kind-specific closed object, with discriminated optional variants rather than arbitrary extra properties. |
| factual status | Production common value: discovery, source_reported, researcher_interpretation, derived, project_decision or synthetic. In the prototype it is represented only by explicit synthetic context and content; the complete common field remains v1 work. |
| creation/update | Derive record creation and latest update from first/last revision; do not maintain conflicting duplicate timestamps. |
| missing value | Production tagged union: `{state: known, value: ...}` OR `{state: unknown/not_reported/not_applicable, reason: ...}`. No made-up zero, empty string or unqualified null. Prototype has numeric values for its finite example and explicit missing dispersion/correlation. |
| exact reference | `{id, rev}`; wrong kind and missing revision rejected. No unqualified "latest" in evidence-bearing records. |

Append-only history requires comparison with the previous accepted dataset: a self-contained record cannot prove it has not rewritten its past. V1's normal incremental check loads prior canonical records supplied as a local snapshot/checked-out base; no network fetch is required. Deletion is replaced by superseded/withdrawn revisions or identity aliases. Schema migrations have their own recorded migration artifact and old/new checksums.

## Record-family data dictionary

The following covers all required work, including families intentionally not implemented in the small prototype.

| Family / ID | Required specific fields and relationships | Lifecycle |
|---|---|---|
| Source/publication / SRC | Exact title; author/editor roles; publication date precision; source type; language; edition/version; verified/unverified identifiers with metadata evidence; family/version/alias links; manifestations; metadata, access and rights observations. Reading is derived from AID sessions, not presumed from access. | Metadata candidate -> verified/conflict -> resolved revision. Access is a dated observation, not a one-way ladder. Source validity is separate from access. |
| Search run / SRCH | Lane, exact protocol revision, pilot/production/update, platform/interface, query, filters, coverage window, actual run dates, pagination, raw reported count, retrieved hit count, export location/hash, failures and completion boundary. | planned -> running -> completed/partial/failed; rerun gets a new run ID, not revised historical hit counts. |
| Search hit / HIT | Search-run pin; original raw record ordinal and metadata; returned identifiers; resolution state; canonical SRC pin or explicit unresolved reason; dedup/adjudication history. Multiple hits may map to one publication. | unresolved -> resolved/duplicate/unresolvable; new resolution revision keeps raw occurrence. |
| Screening / SCR | Source pin; stage; rule/protocol revision; decision and reason; actual actor; reading/access references; verification/adjudication; decision supersession. One current decision per source/stage/protocol scope after adjudication. | pending -> include/exclude/awaiting_text/uncertain; amend/reopen through new revision, never overwrite. Abstract screening is not full-text screening. |
| Study / STUDY | Source/report links (many-to-many); identity decision and locators; scope; unresolved same-study hypotheses and alias history. Not itself a publication or necessarily an independent sample. | unresolved/provisional -> resolved; merge via retained alias, split with amendment and reassignment history. |
| Reported experiment / EXP | Study pin; report-specific experiment label; sample refs; condition keys; assignment/crossover/repeated-measures structure; outcome definitions, contrast/timepoint keys and units. | provisional -> extracted -> checked; corrections by new revision. This is an observed literature experiment, NOT an authorized new study protocol. |
| Sample / SAMPLE | Recruitment/cohort identity; population; dates; counts/missingness; sample/subset/shared-control relations and supporting locators; overlap known/unknown. One sample can participate in several experiments/studies. No personal participant IDs in public records. | provisional -> checked, with uncertainty retained. Unknown overlap is not independence. |
| Theoretical extraction / TX | Source/manifestation/locator and reading pins; source assertion and definitions; premises; inference; context; objections; separate interpretation; RQ relation and coverage limits. | draft -> extracted -> source_checked; disputed/corrected via amendment. |
| Empirical extraction / EX | Experiment/sample/outcome/condition/contrast/timepoint identifiers; source locator for each reported datum; estimate/units/n/dispersion; task/stimuli/training/population; missingness; dependence; reading coverage profile; derivation inputs/formula/version/assumptions where derived. | draft -> extracted -> source_checked; old revisions retained, corrections invalidate dependants. Repeated reporting of one outcome is not a new outcome identity. |
| Appraisal / APP | Exact target revision; domain/criterion/tool version; judgment; evidence locators; rationale; assessor; uncertainty. No universal forced scalar score. Multiple domains/assessors may target the same extraction. | proposed -> checked/disputed -> revised; an appraisal does not silently follow a corrected target. |
| Claim / CLM | Immutable class; exact statement; typed evidence/argument refs; premises and inference; boundaries; counterarguments; uncertainty; revision criterion; review refs; lifecycle. | proposed -> source_checked -> internally_audited -> externally_reviewed; rework can return to proposed/source_checked; superseded/withdrawn terminal except explicit successor. |
| Design requirement / REQ | Requirement class; state/communication scope; exact claim refs; mechanism; conditions; risks; proposed tests; operational variables and rejection/revision criterion. | proposed -> specified -> internally_checked; evidence-supported status requires referenced actual results, not protocol readiness. superseded/rejected retained. |
| Experiment protocol / TEST | Hypotheses; estimands; outcomes; manipulations/checks; sampling/randomization; analysis/exclusions; ethics/privacy; readiness/HG refs; prospective versus retrospective exposure. | draft -> internally_checked -> readiness_blocked/ready_for_authorized_execution. A prepared or synthetic protocol never becomes a real empirical result. |
| Amendment / AMD | Kind; old/new artifact or rule pins; actual date; reason; prior exposure; affected scope; materiality; required rework; verification/disposition. Derived impact list is rebuilt from graph, not an independently editable truth. | proposed -> applied -> verified; rescission/reinstatement needs a later explicit record and new checking. |
| Assistance/review / AID | Discriminator reading, source_check, internal_audit, external_feedback or assistance; actor/tool/model; task/date; exact input/output pins; permitted artifact reference; observed result; actual scope; independence declaration/limits. Reading sessions add manifestation and ranges. | planned -> performed/failed; verification is an actual scoped observation, not a record-class promotion. |
| Human gate / HG | Need/reason; remedies tried; owner action; evidence reference; completion signal; stop condition; status; authorized human actor. Private evidence stays in controlled storage; public metadata does not expose it. | proposed -> waiting -> satisfied/declined/blocked; reopening requires recorded reason. A model must not manufacture satisfaction. |

Conditions/outcomes are experiment-local keyed objects until they need independent ownership; identity is `(EXP logical ID, outcome key, contrast key, timepoint key, SAMPLE ID)`. Do not invent a separate standalone record for every field. Manifestations and locators are source-local objects; reading/review events use the already required AID family. Thus the design adds no heavyweight helper registry.

Manuscript citation bindings can be a versioned sidecar in `paper/`: manuscript artifact hash/locator -> exact claim/source refs. This is an output manifest, not a second claim store. Bibliography keys resolve to canonical sources and versions. Missing bindings, missing bibliography entries and stale refs are mechanical failures; whether the cited passage entails the sentence remains a source-fidelity question.

## Identity decisions

A **publication/report** is a bibliographic object. A preprint and journal article, materially revised edition, translation or companion report have distinct SRC IDs with typed family/version links. An exact duplicate catalogue hit resolves to the same SRC ID. A different PDF encoding of the same report is a manifestation with its own hash, not another publication. A materially corrected document requires a new manifestation/version plus a correction notice/AMD; an independently published correction notice can also have its own SRC.

A **study** is the research undertaking represented by one or more reports. One report may contain more than one study. Linkage is a documented judgment, not a DOI heuristic. A **reported experiment** belongs to a study and carries experimental structure. A **sample** represents recruitment/observational units and can cross experiment and study boundaries. Sample overlap edges are symmetric relations; they are not derivation cycles.

Never name the count of STUDY nodes "independent studies". Report publication, study, experiment, distinct sample and outcome counts separately. For selection/synthesis, build dependence groups from known shared samples, overlap, repeated observations and shared controls. Unknown overlap is a warning/blocker for asserting independence; it is not an empty edge meaning independence. The prototype demonstrates the exact-same-sample case only and explicitly does not resolve arbitrary between-sample overlap.

For the example the defensible bookkeeping is **2 reports, 1 study, 1 experiment, 1 sample, 2 outcomes, 1 shared-sample group**. The two outcomes are not two replications. Their covariance is unknown; no numerical pooling or variance correction is performed.

## Access, reading, locators and rights

Retain the authority's access vocabulary: not_attempted, metadata_only, abstract_only, partial_text, full_text_available, unavailable. Retain reading vocabulary: not_read, selected_ranges_read, full_item_read. Full availability permits a reading opportunity; it does not assert an event happened. Losing access later does not erase an earlier reading of the same version. Reading a different hash or edition does not inherit the first version's attestation.

Each reading attestation pins SRC revision and manifestation, records what was actually accessible at reading time, actor/date and covered ranges. A generated source view can summarize the best established coverage without rewriting source metadata whenever a reader adds a session. Production supports union of compatible sessions by the same identified reader or explicitly attributed aggregate; it must not credit one person with another's reading. The prototype checks one session per extraction.

A decisive locator includes manifestation identity; coordinate system; start/end; printed page label separately; section/paragraph/table/figure/cell where applicable. For a PDF use `pdf_page_0based` plus optional printed label; for HTML use captured version/hash and headings/paragraph anchors; for the plain-text fixture use `file_page_1based` with form-feed page boundaries. Never silently turn printed page 102 into PDF index 102. Field-level locators identify estimate, n and dispersion separately when they differ. Hashes bind bytes, not interpretation or lawful rights.

Bounded reading may support a **bounded source claim** from the read passage. It must not assert whole-report extraction completeness or whole-book understanding. Production extraction completeness should bind a frozen protocol's coverage profile (methods, population, denominators, outcome definitions, relevant results, supplements/corrections and appraisal domains), not simply "read all pages". No protocol exists at the assessed base; the prototype therefore uses an explicitly conservative `complete_report` guard for promoted empirical findings, and `bounded` for the partial companion extraction. This is a prototype policy, not a scientific law or the finalized R002 coverage policy.

Unavailable/unknown rights remain expressible. Do not fabricate content hashes for inaccessible documents. Keep restricted text outside this public repository. A rights observation is supported by an actual rights source/artifact; neither a DOI nor a full-text download grants redistribution. Production schema accepts metadata-only source records with no manifestation bytes, while evidence-use gates apply the stronger locator/coverage requirements.

## Claim class is not lifecycle

Never mutate a design_hypothesis into empirical_finding on the same CLM ID. A later finding gets its own ID and explicit relation to the hypothesis it tested. The original hypothesis remains visible. Likewise an audited project_constraint remains a project choice.

| Class | Required support when presented for use |
|---|---|
| project_constraint | Exact user/project decision artifact and scope, not purported experimental proof. |
| source_claim | TX/EX with exact source/version/locator and scoped reading/check; bounded passage use is allowed. |
| empirical_finding | Primary empirical extraction(s), identity/dependence, exact appraisals, coverage profile, uncertainty and boundaries. An abstract or review summary alone does not become a primary result. |
| theoretical_interpretation | Source premises plus an explicit argument, contested readings and boundaries. |
| synthesis_proposition | Versioned inputs/analysis or claims, inferential steps, counterarguments and revision criterion. |
| design_hypothesis | Mechanism, operational variables, basis and discriminating planned test; remains unvalidated without actual results. |
| unvalidated_convention | Explicit provisional/arbitrary choice, reason and revision criterion. |

Promotion within lifecycle requires new revision-specific checking, not mere presence of an AID ID. Source checks target exact extractions; internal/external reviews target the exact claim payload (statement, support and boundaries). Replacing the evidence or statement after a review does not preserve its coverage. Human_checked requires a recorded human actor; independent_human_checked additionally needs actual independence evidence. Mechanical consistency cannot prove an actor is human or independent, or that the review was competently done. External review means documented feedback was obtained, not endorsement; substantive concerns can still block use. The prototype is conservative and handles passing reviews only; it does not model the full critical-feedback disposition lifecycle.

`currency` is separately derived: current/stale/invalidated/unresolved. It is not scientific confidence and not another lifecycle rung. Historical source_checked records may remain source_checked historically while being stale now. In-progress registries may retain them; a current release must not export them as usable evidence.

## Correction and invalidation rules

1. Never edit an old EX value in place. Append EX revision 2 and an applied AMD identifying old/new exact pins, reason and prior exposure. Keep the old source byte identity and record even when erroneous.
2. Compute reverse evidence closure: old EX -> appraisal -> claim -> requirement -> analysis/manuscript/citation bindings. Any requested current export reaching that invalidated revision fails. Do not automatically rewrite references to "latest".
3. Re-extract/reappraise as necessary; revise claims and requirements; reset material claim revisions to proposed or rechecked status; record new checks against the new pins. Merely acknowledging an AMD cannot make unsupported evidence current.
4. A source retraction/correction targets the precise affected SRC revision/manifestation/locator. Where scope is unknown, conservatively quarantine the whole implicated source version. Retain the source and all prior records, including unfavorable results. Metadata-only spelling fixes may be nonmaterial only with explicit reason and an auditable scope; do not use that exception to excuse changed outcomes.
5. A reinstatement is a new reviewed disposition; it does not erase the original invalidation. The prototype supports correction and source invalidation, not reinstatement or granular nonmaterial exceptions; it fails conservatively rather than inventing reinstatement authority.

## What validates where

| Layer | Responsibilities | It does NOT establish |
|---|---|---|
| Individual schema | Closed fields; types; tagged unknowns; date formats; enums; finite numbers; nonnegative counts; syntactically complete locator; claim class; legal adjacent lifecycle states within one revision list. | Existence of a referenced source; that a page was read; meaning of an extracted value. |
| Cross-record / snapshot validator | Unique IDs/owners; typed exact pins; immutable history against previous snapshot; basis completeness and DAGs; membership; compatible outcomes/units/n; reading/version/range consistency; provenance closure; revision-specific review prerequisites; synthetic/live paths; invalidation propagation; export currency; count and citation reconciliation; explicit empty not_started state. | Correct study matching where evidence is ambiguous; real human identity/independence; source entailment; valid methods. |
| Later source-fidelity review | Inspect actual passages/tables/figures and edition; confirm numbers/units/denominators and attribution; evaluate report linkage/overlap evidence; ensure context, corrections, translations and contrary findings were not omitted. Record actor and scope. | By itself, adequacy of synthesis, causal inference, external peer review, ethics approval or human communication performance. |
| Scientific/methodological and human gates | Protocol-specific appraisal, dependence/estimand/method decisions, sensitivity analyses, external critique and authorized participant work. | Not replaceable by a schema, model consensus or green CI. |

The deliberate 8-versus-80 fixture proves this separation: both structurally consistent snapshots can pass, although the earlier extracted value is wrong relative to the synthetic text. A test explicitly demonstrates that limit rather than presenting green checks as successful extraction fidelity.

## Prototype boundary and extension points

`tools/validate_records_prepass.py` imports the unchanged `ValidationError` and `read_json`; it indexes pins, checks an explicit support DAG, validates the hard relationships above, compares prior revisions, computes stale closure and outputs sorted JSON. It uses the bootstrap's stdlib/unittest approach. Normal malformed input exits 1 with machine-readable failure; bad CLI usage follows argparse's exit 2. No bibliography or network calls occur.

Implemented record kinds: source, study, experiment, sample, extraction, appraisal, claim, requirement, amendment, assistance. This is not a complete schema for every field even in those kinds. Full closed body schemas, general TX/claim support, search/screening, rights, protocol/readiness, human gates, source aliases, cross-sample overlap, granular/reinstated invalidation, full citation parsing and evidence-flow exports remain explicit R001 integration work. Complete research state is deliberately rejected by the prototype; empty live/not_started is accepted. Source file hash consistency is exercised by a separate fixture test, not falsely inferred from a hash-shaped string in the cross-record validator.

Keep `tools/validate.py`'s bootstrap functions and all 26 tests. Add narrow schema/graph/export modules and call them from `validate_repository()` after existing checks. Its JSON scan may parse fixture syntax but must not ingest tests/fixtures as live records. Keep existing workflow job, permission boundary and pinned checkout; extend commands only when live manifests and all acceptance tests exist. The additive prepass patch does not wire itself into main CI or create a live register.

## Scientific questions deliberately not settled

What exact reading coverage is sufficient for each R002/R009 extraction domain? Which source passages establish that two real reports share a sample? Are outcomes sufficiently compatible to pool, and what is their covariance? Which appraisal domains fit each design? Do source statements support a proposed interpretation rather than just share terminology? Which claims survive contrary evidence, and what uncertainty belongs in the final paper? What actual independent human critique and authorized participant evidence will be available? These need sources, protocol work and real review. No amount of structural consistency in this packet answers them.
