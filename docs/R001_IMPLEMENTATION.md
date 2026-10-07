# MHAC-R001 implementation record

[Issue #1](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/1) · [Data model](DATA_MODEL.md) · [Validation](VALIDATION.md) · [Schemas](../schemas/README.md)

## Scope and assessed base

This change implements the first dependency-ready research-infrastructure issue.
The reconciled base was `796151a33ec7a1acc026b239fe5c883312ebf40b`, with only the
bootstrap PR and no later implementation or checkpoint branch. The original
26 bootstrap tests passed locally before implementation. The issue remained open.

Live research is still **not_started**. The change does not select real studies,
freeze a protocol, execute production literature searches, establish findings,
carry out a participant study or satisfy MHAC-R002.

## Actual prepass reuse

The original `MHAC-R001-prepass-796151a.zip` was recovered and verified:

- Size: **195,264 bytes**; 65 ZIP members; archive CRC check passed.
- SHA-256: `7b71bd0a202694c8000619c68d66dfc510a413678345ffaf2035ad01560f2fc1`.
- All **64 manifest payload hashes** matched.
- The assessed source commit in the packet matches the live bootstrap base.

The implementation reuses the actual prototype's stable record IDs, exact
revision pins, immutable histories, evidence dependency graph, scoped reading and
review checks, and reverse invalidation rule. The complete prepass archive remains
an independent historical artifact; it is not presented as an accepted production
implementation.

The [fixture generator](../tools/build_record_fixtures.py) explicitly migrates the
actual original fixture construction to `mhac-records/1`. It verifies all five
original positive snapshot hashes before conversion. The migration retains the
original historical fields and supplied source bytes, then adds the documented v1
fields. Its [provenance manifest](../tests/fixtures/records/v1/provenance.json)
records the artifact and resulting fixture identities.

## Implementation decisions

| Decision | Reason and resulting behavior |
|---|---|
| Standard-library executable schemas | Sixteen closed Python contracts work from a clean offline checkout without a package install or a custom JSON-Schema interpreter. |
| One canonical file per stable ID | Append-only revision arrays preserve history; exact pins prevent an old check silently attaching to corrected data. |
| Separate evidence and identity relations | Support must be acyclic; reciprocal report membership, shared samples and planned test links retain their distinct meanings. |
| Explicit caller context and canonical roots | Fixture declarations cannot choose live ingestion; path/owner checks reject contamination and omitted canonical records. |
| Conservative correction handling | Material corrections and adverse review changes invalidate affected support; stale records remain inspectable but cannot be exported as current. |
| Identity-level flow counts | Retrieval occurrences, publications, studies, experiments, samples and outcomes are separate quantities. Unknown overlap/covariance is not converted to independence. |
| Exact citation bindings | A manuscript hash and line locator bind source/claim revisions. A valid unrelated source cannot stand in for the bound claim's evidence. |
| Distinct structural stage declarations | Empty/synthetic data cannot complete research. Nonempty records and a passing CI run still do not establish scientific acceptance. |
| Existing CI retained and extended | The job preserves read-only permissions, pinned checkout and credential non-persistence; it adds locally available base-history comparison and fixture regeneration checks. |

## Worked example and verification

The [synthetic examples](../tests/fixtures/records/v1/README.md) retain two
publications describing one study, one sample and two dependent outcomes.
Report B is available in full but only selected ranges were read. Its full-text
screening decision remains uncertain.

The first latency extraction deliberately records **8 ms** while the authored
fictional source says **80 ms**. It passes structural validation. The correction
appends a new revision and amendment, quarantines dependent claims/requirements,
and restores their current use only after revision-specific rechecking.
Subsequent source invalidation quarantines the affected chain while preserving
the unrelated bounded accuracy source claim from report B.

The all-family fixture adds three retrieval hits resolving to those two
publications, explicit screening decisions, a theoretical extraction, a proposed
experiment protocol and blocked human readiness. These records are fictional and
never enter the live registry.

Run the commands in [VALIDATION.md](VALIDATION.md) for unit tests, fixture byte
reproduction, live validation and base-history comparison. Test and CI results on
the final head, PR and merge SHA belong in the actual issue/PR acceptance record;
this document does not manufacture a future landing identity.

## Review and remaining boundaries

The implementation was divided among one integrator and three agent workers:
schema construction, provenance-graph implementation, and fixture migration with
loader/flow/citation regression tests. A separate cross-module review checked
false promotion, terminal evidence, source/citation binding and history behavior.
These were agent implementation/review passes, not independent human screening,
source-fidelity review or external scholarly critique.
The workers inherited the parent session's model and reasoning configuration.
Verification used local Python standard-library tests and Git history fixtures;
repository reconciliation used Git and the GitHub connector. No external model
service or bibliography resolver is required by the implementation.

Scientific work still needs actual sources and justified methods: report/sample
identity, sufficient reading coverage, source entailment, appraisal adequacy,
dependence/estimands, pooling eligibility, critical comparison and uncertainty.
Real external feedback and authorized participants retain their separate gates.
Pilot-result acceptance and richer manuscript build/rendering are explicitly
deferred to their owning issues. No online bibliography resolver or network merge
gate was introduced.

After #1's actual merge and successful main CI are verified, **#2 / MHAC-R002**
is the next dependency-ready issue. Its existing prepasses remain preparation;
their prior access gaps and incomplete novelty work must be reconciled with the
actual artifacts before protocol acceptance.
