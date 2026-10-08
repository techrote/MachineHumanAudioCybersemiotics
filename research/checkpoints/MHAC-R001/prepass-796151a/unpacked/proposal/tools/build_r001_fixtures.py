"""Deterministically build explicitly synthetic R001 prepass fixtures, never live data."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path

CONTRACT = "mhac-r001-prepass/1"
ACTOR = {"kind": "agent", "id": "SYNTHETIC-AGENT"}


def ref(rid, rev=1):
    return {"id": rid, "rev": rev}


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def build(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "sources").mkdir(exist_ok=True)
    texts = {
        "A": "SYNTHETIC REPORT A — NO REAL STUDY\nMethods: fictional paired task, fictional n=24.\fSYNTHETIC page 2 (printed 102), Results, Table 1.\nMean response-time difference: 80 ms. Dispersion not reported.\fSYNTHETIC page 3, limitations: no real people or observations.\n",
        "B": "SYNTHETIC REPORT B — NO REAL STUDY\nCompanion report of the same fictional study and 24-person sample.\fSYNTHETIC page 2 (printed 202), Results, Table 2.\nAccuracy difference: 5 percentage points. Same fictional participants as latency.\fSYNTHETIC page 3, methods detail not included in the simulated reading.\fSYNTHETIC page 4, discussion not included in the simulated reading.\n",
    }
    hashes = {}
    for name, text in texts.items():
        raw = text.encode("utf-8")
        (root / "sources" / f"report_{name}.txt").write_bytes(raw)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    data = {"contract": CONTRACT, "dataset_kind": "fixture", "research_state": "in_progress",
            "records": [], "release_claims": [], "release_requirements": [],
            "declared_counts": {"publications": 2, "studies": 1, "experiments": 1,
                                "samples": 1, "outcomes": 2, "shared_sample_groups": 1}}
    tick = 0

    def row(rid, in_data=None):
        return next(r for r in (in_data or data)["records"] if r["id"] == rid)

    def version(rid, body, basis=(), kind=None):
        nonlocal tick
        tick += 1
        if kind:
            data["records"].append({"schema_version": 1, "id": rid, "kind": kind,
                                     "synthetic": True, "issue": 1, "revisions": []})
        r = row(rid)
        # All story timestamps are fictional, deterministic and explicitly labelled as such.
        at = f"2000-01-01T00:{tick // 60:02d}:{tick % 60:02d}Z"
        r["revisions"].append({"rev": len(r["revisions"]) + 1, "at": at,
                                "actor": copy.deepcopy(ACTOR), "basis": list(copy.deepcopy(basis)),
                                "data": copy.deepcopy(body)})

    for name in ("A", "B"):
        version("SRC-" + name, {"title": f"SYNTHETIC report {name}; not a real publication",
            "authors": [{"name": "Fictional Fixture Author", "role": "author"}],
            "publication_date": {"state": "not_applicable", "reason": "Synthetic report"},
            "identifiers": [], "metadata_status": "candidate", "access_status": "full_text_available",
            "rights": {"status": "unknown", "reason": "Synthetic authored fixture, no third-party source or licence decision"},
            "manifestations": [{"id": "text-v1", "sha256": hashes[name], "extent": 3 if name == "A" else 4,
                                 "coordinate": "file_page_1based", "fixture_path": f"sources/report_{name}.txt"}]}, kind="source")
    version("STUDY-ONE", {"publications": [ref("SRC-A"), ref("SRC-B")],
            "identity_status": "fixture_asserted_same", "identity_basis": "The synthetic story stipulates one study; not an inference about real reports."}, kind="study")
    version("SAMPLE-ONE", {"n": 24, "population": "Fictional sample; no participants recruited",
            "overlap": [], "uncertainty": "No inference about real sample identity"}, kind="sample")
    version("EXP-ONE", {"study_ref": ref("STUDY-ONE"), "sample_refs": [ref("SAMPLE-ONE")],
            "conditions": ["coded_alert", "control"], "outcomes": {
                "latency": {"unit": "ms", "contrast": "coded_alert minus control"},
                "accuracy": {"unit": "percentage_points", "contrast": "coded_alert minus control"}},
            "dependence": {"relation": "shared_sample", "correlation": {"state": "unknown", "reason": "Not specified by synthetic reports"}}}, kind="experiment")
    for name in ("A", "B"):
        version("AID-READ-" + name, {"subtype": "reading", "source_ref": ref("SRC-" + name),
            "manifestation_id": "text-v1", "access_at_read": "full_text_available",
            "reading_status": "full_item_read" if name == "A" else "selected_ranges_read",
            "ranges": [[1, 3]] if name == "A" else [[1, 2]],
            "method": "Synthetic attestation, not real literature reading"}, [ref("SRC-" + name)], kind="assistance")
    for rid, source, outcome, value, unit, scope in (
            ("EX-LAT", "A", "latency", 8.0, "ms", "complete_report"),
            ("EX-ACC", "B", "accuracy", 5.0, "percentage_points", "bounded")):
        version(rid, {"source_ref": ref("SRC-" + source), "experiment_ref": ref("EXP-ONE"),
            "sample_ref": ref("SAMPLE-ONE"), "outcome": outcome, "value": value, "unit": unit, "n": 24,
            "dispersion": {"state": "not_reported", "reason": "Absent in synthetic passage"},
            "scope": scope, "reading_ref": ref("AID-READ-" + source),
            "locator": {"manifestation_id": "text-v1", "coordinate": "file_page_1based",
                        "start": 2, "end": 2, "printed_label": "102" if source == "A" else "202",
                        "section": "Results", "table": "1" if source == "A" else "2", "cell": outcome},
            "note": "Initial latency extraction deliberately wrong: 8 versus 80 in synthetic source; schema does not read for entailment." if source == "A" else "Bounded selected-passage extraction, not full empirical appraisal."},
            [ref("SRC-" + source), ref("AID-READ-" + source), ref("EXP-ONE"), ref("SAMPLE-ONE")], kind="extraction")
    version("APP-LAT", {"target_ref": ref("EX-LAT"), "domain": "reporting_completeness",
            "judgment": "limited", "rationale": "Synthetic dispersion absent; no pooled estimate justified."}, [ref("EX-LAT")], kind="appraisal")
    for name in ("LAT", "ACC"):
        version("AID-CHECK-" + name, {"subtype": "review", "scope": "source_fidelity", "outcome": "pass",
            "verification": "agent_checked", "target_refs": [ref("EX-" + name)],
            "artifact": "Synthetic attestation only; initial LAT check deliberately fails to notice transcription error."}, [ref("EX-" + name)], kind="assistance")
        body = {"class": "empirical_finding" if name == "LAT" else "source_claim", "lifecycle": "proposed",
                "statement": "SYNTHETIC: response-time difference reported as 8 ms." if name == "LAT" else "SYNTHETIC: selected passage reports accuracy difference of 5 percentage points.",
                "boundaries": "One fictional study; no real evidence; outcomes are not independent replications.",
                "counterarguments": "Unknown dispersion/covariance and incomplete companion reading.",
                "uncertainty": "No quantitative certainty assertion", "evidence_refs": [ref("EX-" + name)],
                "appraisal_refs": [ref("APP-LAT")] if name == "LAT" else [], "review_refs": []}
        basis = body["evidence_refs"] + body["appraisal_refs"]
        version("CLM-" + name, body, basis, kind="claim")
        body["lifecycle"] = "source_checked"
        body["review_refs"] = [ref("AID-CHECK-" + name)]
        version("CLM-" + name, body, basis + body["review_refs"])
    version("CLM-HYP", {"class": "design_hypothesis", "lifecycle": "proposed",
            "statement": "SYNTHETIC hypothesis: test whether the contrast transfers to a new task.",
            "boundaries": "Untested", "counterarguments": "No real data", "uncertainty": "Unvalidated",
            "evidence_refs": [ref("EX-LAT")], "appraisal_refs": [], "review_refs": []}, [ref("EX-LAT")], kind="claim")
    version("REQ-TIMING", {"claim_refs": [ref("CLM-LAT", 2)], "status": "proposed",
            "statement": "SYNTHETIC: inspect timing as an experimental variable, not a validated design requirement.",
            "revision_criterion": "Reassess when latency extraction or source changes."}, [ref("CLM-LAT", 2)], kind="requirement")
    data["release_claims"] = [ref("CLM-LAT", 2), ref("CLM-ACC", 2)]
    data["release_requirements"] = [ref("REQ-TIMING")]
    before = copy.deepcopy(data)
    ex = copy.deepcopy(row("EX-LAT")["revisions"][-1]["data"])
    ex["value"] = 80.0
    ex["note"] = "Corrected transcription to 80 ms; original 8 ms preserved as revision 1."
    version("EX-LAT", ex, row("EX-LAT")["revisions"][-1]["basis"])
    version("AMD-FIX-LAT", {"kind": "extraction_correction", "target_refs": [ref("EX-LAT")],
            "replacement_refs": [ref("EX-LAT", 2)], "reason": "Synthetic rereading finds dropped zero (8 -> 80 ms).",
            "prior_exposure": "The fictional initial result had already been used by a claim and requirement.",
            "required_rework": "Reappraise EX-LAT; revise claim and requirement; do not silently retarget."}, kind="amendment")
    data["release_claims"] = [ref("CLM-ACC", 2)]
    data["release_requirements"] = []
    pending = copy.deepcopy(data)
    app = copy.deepcopy(row("APP-LAT")["revisions"][-1]["data"])
    app["target_ref"] = ref("EX-LAT", 2)
    version("APP-LAT", app, [ref("EX-LAT", 2)])
    review = copy.deepcopy(row("AID-CHECK-LAT")["revisions"][-1]["data"])
    review["target_refs"] = [ref("EX-LAT", 2)]
    review["artifact"] = "Synthetic recheck of corrected revision 2, not a transfer of the old attestation."
    version("AID-CHECK-LAT", review, [ref("EX-LAT", 2)])
    claim = copy.deepcopy(row("CLM-LAT")["revisions"][-1]["data"])
    claim.update(statement="SYNTHETIC: response-time difference reported as 80 ms.", lifecycle="proposed",
                 evidence_refs=[ref("EX-LAT", 2)], appraisal_refs=[ref("APP-LAT", 2)], review_refs=[])
    version("CLM-LAT", claim, claim["evidence_refs"] + claim["appraisal_refs"])
    claim.update(lifecycle="source_checked", review_refs=[ref("AID-CHECK-LAT", 2)])
    version("CLM-LAT", claim, claim["evidence_refs"] + claim["appraisal_refs"] + claim["review_refs"])
    req = copy.deepcopy(row("REQ-TIMING")["revisions"][-1]["data"])
    req["claim_refs"] = [ref("CLM-LAT", 4)]
    version("REQ-TIMING", req, req["claim_refs"])
    hyp = copy.deepcopy(row("CLM-HYP")["revisions"][-1]["data"])
    hyp["evidence_refs"] = [ref("EX-LAT", 2)]
    version("CLM-HYP", hyp, hyp["evidence_refs"])
    data["release_claims"] = [ref("CLM-LAT", 4), ref("CLM-ACC", 2)]
    data["release_requirements"] = [ref("REQ-TIMING", 2)]
    after = copy.deepcopy(data)
    version("AMD-SOURCE-INVALID", {"kind": "source_invalidation", "target_refs": [ref("SRC-A")],
            "replacement_refs": [], "reason": "Synthetic source invalidation notice; all dependants quarantined."}, kind="amendment")
    data["release_claims"] = [ref("CLM-ACC", 2)]
    data["release_requirements"] = []
    invalidated = copy.deepcopy(data)
    cases = []

    def case(name, content, expected=0, code=None, prev=None, context="fixture"):
        (root / f"{name}.json").write_text(dumps(content), encoding="utf-8")
        cases.append({"name": name, "exit": expected, "code": code, "previous": prev, "context": context})

    def mutate(name, base, fn, code, prev=None):
        value = copy.deepcopy(base)
        fn(value)
        case(name, value, 1, code, prev)

    def body(d, rid, revision=-1):
        return row(rid, d)["revisions"][revision]["data"]

    case("valid_before", before)
    case("valid_correction_pending", pending, prev="valid_before")
    case("valid_corrected", after, prev="valid_correction_pending")
    case("valid_source_invalidated", invalidated, prev="valid_corrected")
    empty = {"contract": CONTRACT, "dataset_kind": "live", "research_state": "not_started", "records": [], "release_claims": []}
    case("valid_empty_live", empty, context="live")
    mutate("invalid_duplicate_id", before, lambda d: d["records"].append(copy.deepcopy(d["records"][0])), "DUPLICATE_ID")
    mutate("invalid_dangling", before, lambda d: body(d, "EX-ACC").update(source_ref=ref("SRC-MISSING")), "DANGLING_REFERENCE")
    mutate("invalid_reading_status", before, lambda d: body(d, "AID-READ-B").update(reading_status="reviewed"), "STATUS")
    mutate("invalid_false_full_reading", before, lambda d: body(d, "AID-READ-B").update(reading_status="full_item_read"), "FALSE_FULL_READING")
    mutate("invalid_unread_locator", before, lambda d: body(d, "EX-ACC")["locator"].update(start=4, end=4), "UNREAD_LOCATOR")
    mutate("invalid_reading_source", before, lambda d: body(d, "EX-ACC").update(reading_ref=ref("AID-READ-A")), "READING_SOURCE")
    mutate("invalid_false_full_extraction", before, lambda d: body(d, "EX-ACC").update(scope="complete_report"), "FALSE_FULL_EXTRACTION")
    mutate("invalid_identity_link", before, lambda d: body(d, "STUDY-ONE").update(publications=[ref("SRC-A")]), "IDENTITY_LINK")
    mutate("invalid_unit", before, lambda d: body(d, "EX-LAT").update(unit="s"), "OUTCOME_UNIT")
    mutate("invalid_n", before, lambda d: body(d, "EX-LAT").update(n=25), "OUTCOME_N")
    mutate("invalid_missing_basis", before, lambda d: row("EX-LAT", d)["revisions"][0].update(basis=[ref("SRC-A")]), "MISSING_BASIS")
    mutate("invalid_cycle", before, lambda d: row("EX-LAT", d)["revisions"][0]["basis"].append(ref("EX-LAT")), "DEPENDENCY_CYCLE")
    mutate("invalid_fixture_flag", before, lambda d: d["records"][0].update(synthetic=False), "CONTAMINATION")
    contaminated = copy.deepcopy(before)
    contaminated["dataset_kind"] = "live"
    case("invalid_fixture_in_live", contaminated, 1, "CONTAMINATION", context="live")
    mutate("invalid_class_promotion", before, lambda d: body(d, "CLM-LAT").update(**{"class": "design_hypothesis"}), "CLASS_PROMOTION")
    def finding(d):
        for r in row("CLM-ACC", d)["revisions"]:
            r["data"]["class"] = "empirical_finding"
    mutate("invalid_bounded_finding", before, finding, "UNSUPPORTED_FINDING")
    mutate("invalid_no_source_check", before, lambda d: body(d, "CLM-LAT").update(review_refs=[]), "UNSUPPORTED_PROMOTION")
    def wrong_review(d):
        r = row("CLM-LAT", d)["revisions"][-1]
        r["data"]["review_refs"] = [ref("AID-CHECK-LAT")]
        r["basis"] = r["data"]["evidence_refs"] + r["data"]["appraisal_refs"] + r["data"]["review_refs"]
    mutate("invalid_old_revision_check", after, wrong_review, "UNSUPPORTED_PROMOTION")
    mutate("invalid_stale_claim_export", pending, lambda d: d.update(release_claims=[ref("CLM-LAT", 2)]), "STALE_RELEASE")
    mutate("invalid_stale_requirement_export", pending, lambda d: d.update(release_requirements=[ref("REQ-TIMING")]), "STALE_REQUIREMENT")
    mutate("invalid_study_count", before, lambda d: d["declared_counts"].update(studies=2), "COUNT_MISMATCH")
    mutate("invalid_history_rewrite", after, lambda d: body(d, "EX-LAT", 0).update(value=80.0), "HISTORY", "valid_before")
    mutate("invalid_history_delete", after, lambda d: d.update(records=[r for r in d["records"] if r["id"] != "CLM-HYP"]), "HISTORY", "valid_before")
    mutate("invalid_fake_human", before, lambda d: body(d, "AID-CHECK-LAT").update(verification="human_checked"), "FALSE_HUMAN_REVIEW")
    mutate("invalid_source_invalidation_export", invalidated, lambda d: d.update(release_claims=[ref("CLM-LAT", 4)]), "STALE_RELEASE")
    badempty = copy.deepcopy(empty)
    badempty["research_state"] = "complete"
    case("invalid_empty_complete", badempty, 1, "EMPTY_COMPLETION", context="live")
    mutate("invalid_complete_fixture", before, lambda d: d.update(research_state="complete"), "COMPLETION_NOT_IMPLEMENTED")
    mutate("invalid_lifecycle_jump", before, lambda d: body(d, "CLM-LAT").update(lifecycle="externally_reviewed"), "TRANSITION")
    (root / "expected_cases.json").write_text(dumps(cases), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.output)


if __name__ == "__main__":
    main()
