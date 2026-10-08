# Synthetic example: exact records and allowed transitions

**Every person, report, study, event time and numerical result in this example is fictional.** These are test fixtures, not scientific evidence. The source texts themselves are supplied under `proposal/tests/fixtures/mhac_r001/sources/`, with actual SHA-256 digests in source records. The text files use form-feed-separated pages; they are not PDFs.

## Identities and reading

| Logical record | Exact meaning |
|---|---|
| SRC-A@1 | Fictional report A, three text pages. Full text available. |
| SRC-B@1 | Fictional companion report B of the same study, four text pages. Full text available. |
| STUDY-ONE@1 | One study with publications SRC-A@1 and SRC-B@1. |
| EXP-ONE@1 | One paired experimental comparison; latency and accuracy outcome keys. |
| SAMPLE-ONE@1 | One fictional 24-person sample used for both outcomes; no actual participants. |
| AID-READ-A@1 | Full-item reading, ranges [[1,3]], pinned to SRC-A@1/text-v1. |
| AID-READ-B@1 | Selected ranges only, [[1,2]], pinned to SRC-B@1/text-v1; pages 3–4 not read in the scenario. |
| EX-LAT@1 | Latency difference 8 ms, n=24, complete-report scope; source A, file page 2, printed label 102, Results/Table 1/latency. Deliberate extraction error: source text actually says 80 ms. |
| EX-ACC@1 | Accuracy difference 5 percentage points, n=24; source B page 2, printed 202, Results/Table 2/accuracy; bounded extraction. |
| APP-LAT@1 | Reporting-completeness appraisal of EX-LAT@1; dispersion not reported. |
| CLM-LAT@1 -> @2 | Empirical-finding-class candidate moves proposed -> source_checked, exact evidence EX-LAT@1, appraisal APP-LAT@1, AID-CHECK-LAT@1. Synthetic checker initially misses transcription error. |
| CLM-ACC@1 -> @2 | Source-claim-class candidate moves proposed -> source_checked, exact bounded EX-ACC@1 and AID-CHECK-ACC@1. It is not promoted to an empirical finding. |
| CLM-HYP@1 | Proposed design hypothesis; not a finding despite its evidence references. |
| REQ-TIMING@1 | Proposed requirement referencing CLM-LAT@2; no real design performance asserted. |

References in the actual JSON are objects such as `{"id":"EX-LAT","rev":1}`, not the shorthand used here. Each stable record ID occurs once and contains its ordered revisions. Full record objects, including dates, basis and actors, are supplied in the fixture snapshots, not omitted behind this summary.

The two outcomes share SAMPLE-ONE. Their dependence is recorded at EXP-ONE, with correlation explicitly unknown. Counts are 2 publications / 1 study / 1 experiment / 1 sample / 2 outcomes / 1 shared-sample group. No "2 independent studies" count or pooled statistic is generated.

## Snapshot 1: before correction

`valid_before.json` is structurally consistent. It includes the initial 8 ms error. A dedicated test establishes that this incorrect extraction can pass structural checks. The old AID pass is a fictional imperfect review, not proof of source fidelity.

Source B is fully available but only partly read. Its bounded accuracy source claim is permissible. Changing its reading status to full_item_read while retaining [[1,2]] fails; changing its locator to page 4 fails; marking its extraction complete_report fails; relabelling its bounded source claim as a promoted empirical finding fails.

## Snapshot 2: correction known, downstream rework pending

`valid_correction_pending.json` is append-only relative to snapshot 1:

```json
{"id":"EX-LAT", "new_revision":2, "value":80.0, "unit":"ms"}
```

The complete revision preserves the same source, experiment, sample and locator. `AMD-FIX-LAT@1` pins target EX-LAT@1 and replacement EX-LAT@2, explains the dropped zero, discloses prior use, and requires reappraisal and claim/requirement revision.

Derived currency marks APP-LAT@1, AID-CHECK-LAT@1, CLM-LAT@1/@2, CLM-HYP@1 and REQ-TIMING@1 stale. EX-LAT@1 is retained but invalidated for current support; EX-LAT@2 is current. CLM-ACC@2 remains unaffected. The pending snapshot is valid work-in-progress, with no claim that stale records are current; it exports only the unaffected accuracy source claim and no timing requirement. Requesting either stale claim or stale requirement export fails.

## Snapshot 3: corrected and rechecked

`valid_corrected.json` is append-only relative to snapshot 2. It adds:

```text
APP-LAT@2          -> EX-LAT@2, newly appraised
AID-CHECK-LAT@2    -> EX-LAT@2, new scoped check
CLM-LAT@3         -> proposed, statement now 80 ms, EX-LAT@2 + APP-LAT@2
CLM-LAT@4         -> source_checked, same new evidence + AID-CHECK-LAT@2
REQ-TIMING@2      -> CLM-LAT@4
CLM-HYP@2         -> proposed design_hypothesis, EX-LAT@2
```

Latest records are current; old invalidated/stale revisions remain visible. The corrected value is not a new outcome, so counts do not change. Source B remains partially read throughout. Reusing AID-CHECK-LAT@1 for the new evidence fails exact-revision promotion checks. Overwriting EX-LAT@1 with 80 instead of appending a revision fails comparison against the prior snapshot.

Supplementary unit tests construct an internally_audited CLM-LAT@5 from an audit of the exact CLM-LAT@4 payload. An audit of CLM-ACC does not qualify; neither does changing the statement after reviewing CLM-LAT@4. These tests add no fake independent human reviewer.

## Snapshot 4: subsequent source invalidation

`valid_source_invalidated.json` appends AMD-SOURCE-INVALID@1 targeting SRC-A@1. Every evidence path dependent on that source revision is quarantined, including corrected latency records and timing requirement; accuracy from SRC-B remains available. The snapshot is a valid archive/work state with the affected exports withheld. Requesting the apparently corrected latency claim for current use now fails. Neither re-reading nor a previously passing check overrides a source invalidation.

## Actual executable cases

The frozen matrix has 33 CLI cases: five positive states (including empty live/not_started) and 28 negative cases. It includes duplicate/dangling IDs, invalid reading statuses, false full reading/extraction, unread locators, mismatched reading source, report membership, units/counts, missing basis, cycles, fixture contamination, class relabelling, insufficient finding support, missing/old revision checks, stale exports, double-counted studies, history rewrite/deletion, fake human review, source invalidation and empty/completed research assertions.

The final suite combines 26 unchanged bootstrap tests and 44 prepass tests: **70 tests pass**. The final machine-readable CLI matrix has every expected exit/error code matched. See results/unit-tests-final.txt, results/unit-tests-final.exit.json and results/execution.json. These are local tests, not remote CI, source-fidelity review or issue acceptance.
