"""Rebuild explicitly fictional MHAC-R001 fixtures for the versioned record contract.

The prepass event construction is preserved from the recovered, verified package
(proposal/tools/build_r001_fixtures.py, SHA-256
5647aca824e534ed0909bd972e7ed05fb3793b3a734c411bdf379f5233c6da3b).
All five original snapshots are hash checked before the explicit v1 conversion.
The fictional source texts, dates, wrong 8 ms extraction and append-only correction
history are retained; contract enrichment is synthetic schema scaffolding.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

CONTRACT = "mhac-r001-prepass/1"
ACTOR = {"kind": "agent", "id": "SYNTHETIC-AGENT"}
ORIGINAL_SNAPSHOT_SHA256 = {
    "valid_before": "0ecba0d8b580e54563d3b2b72595f1ea752be1de52e59f21a55e3fa10ed0d36b",
    "valid_correction_pending": "5e5bdf2752c9b75bb86dc6f81ec1ddbcd39ad3a13bef1a49901691812e034893",
    "valid_corrected": "7c3a78aade58e657241969d9c35e5770a28b4f16be2b1f716e4f45e0823381e2",
    "valid_source_invalidated": "2b25b11535ebd064a2758e71513a0b2eb19baba38f9387129c03e3e8b5a966cc",
    "valid_empty_live": "13561a44c21090e25a7a8aca8d85257054785fc2c6c8ee649ac80c41f00b685e",
}


def ref(rid, rev=1):
    return {"id": rid, "rev": rev}


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


SOURCE_TEXTS = {
    "A": "SYNTHETIC REPORT A — NO REAL STUDY\nMethods: fictional paired task, fictional n=24.\fSYNTHETIC page 2 (printed 102), Results, Table 1.\nMean response-time difference: 80 ms. Dispersion not reported.\fSYNTHETIC page 3, limitations: no real people or observations.\n",
    "B": "SYNTHETIC REPORT B — NO REAL STUDY\nCompanion report of the same fictional study and 24-person sample.\fSYNTHETIC page 2 (printed 202), Results, Table 2.\nAccuracy difference: 5 percentage points. Same fictional participants as latency.\fSYNTHETIC page 3, methods detail not included in the simulated reading.\fSYNTHETIC page 4, discussion not included in the simulated reading.\n",
}


def _prepass_snapshots():
    hashes = {}
    for name, text in SOURCE_TEXTS.items():
        raw = text.encode("utf-8")
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
    empty = {"contract": CONTRACT, "dataset_kind": "live", "research_state": "not_started",
             "records": [], "release_claims": []}
    cases = {"valid_before": before, "valid_correction_pending": pending,
             "valid_corrected": after, "valid_source_invalidated": invalidated,
             "valid_empty_live": empty}
    for name, content in cases.items():
        digest = hashlib.sha256(dumps(content).encode("utf-8")).hexdigest()
        if digest != ORIGINAL_SNAPSHOT_SHA256[name]:
            raise ValueError(f"Preserved prepass snapshot changed: {name} ({digest})")
    return cases


def _missing(reason="Not applicable to this fictional contract example"):
    return {"state": "not_applicable", "reason": reason}


def _unknown(reason):
    return {"state": "unknown", "reason": reason}


def _not_reported(reason):
    return {"state": "not_reported", "reason": reason}


def _known(value):
    return {"state": "known", "value": value}


def _locator(page, **details):
    return {"manifestation_id": "text-v1", "coordinate": "file_page_1based",
            "start": page, "end": page, **details}


def _enrich_snapshot(original):
    """Convert the historical fixture contract explicitly, without changing its story."""
    data = copy.deepcopy(original)
    data["contract"] = "mhac-records/1"
    data.pop("declared_counts", None)
    data.setdefault("release_requirements", [])
    data["stage_gates"] = []
    for row in data["records"]:
        for revision in row["revisions"]:
            revision["factual_status"] = "synthetic"
            body = revision["data"]
            kind = row["kind"]
            if kind == "source":
                body.update(source_type="report", language=_known("en"),
                            edition=_missing("Original fictional fixture text; no published edition"),
                            metadata_evidence=["Metadata stipulated by the synthetic fixture generator, not verified bibliographic metadata."],
                            access_at=revision["at"], access_reason="The synthetic text is supplied with the fixture.",
                            validity="active", family_links=[])
                body["rights"]["evidence"] = _unknown("No real third-party work or rights decision is represented")
            elif kind == "study":
                body.update(scope="One fictional paired-task study, represented by two fictional reports.",
                            identity_locators=[])
            elif kind == "sample":
                body.update(status="provisional",
                            recruitment=_not_reported("No actual recruitment; synthetic source does not specify a recruitment method"),
                            missingness=_not_reported("No real observations or missingness data exist"))
            elif kind == "experiment":
                body.update(status="extracted", report_label="One fictional paired comparison",
                            assignment="Not specified in the fictional reports; no randomization claim is made.")
            elif kind == "assistance":
                body.update(status="performed", performed_at=_known(revision["at"]),
                            independence="Fictional agent attestation; not independent human review or actual source reading.")
            elif kind == "extraction":
                body.update(status="extracted", conditions=["coded_alert", "control"],
                            contrast="coded_alert minus control", timepoint="not specified in synthetic text",
                            task="Fictional paired task", stimuli=_not_reported("Not specified in the synthetic passage"),
                            training=_not_reported("Not specified in the synthetic passage"),
                            population="Fictional sample; no participants recruited",
                            missingness=_not_reported("No real observations or missingness data exist"),
                            dependence={"relation": "shared_sample", "correlation": _unknown("Not specified by synthetic reports")},
                            field_locators={"value": copy.deepcopy(body["locator"]),
                                            "n": _locator(1), "dispersion": copy.deepcopy(body["locator"])},
                            derivation=_missing("Direct fictional transcription; no computed estimate"))
            elif kind == "appraisal":
                body.update(status="checked", criterion="Record whether the fictional report supplies dispersion.",
                            tool_version=_missing("No appraisal instrument is applied in the fictional example"),
                            evidence=[{"source_ref": ref("SRC-A"), "locator": _locator(2, section="Results", table="1")}],
                            uncertainty="A fictional reporting-completeness example, not a scientific appraisal.")
                if ref("SRC-A") not in revision["basis"]:
                    revision["basis"].append(ref("SRC-A"))
            elif kind == "claim":
                body["argument"] = {
                    "premises": ["The pinned fictional extraction is the stated basis; it is not real evidence."],
                    "inference_steps": ["Keep the claim bounded to the fictional report and the declared claim class."],
                    "revision_criterion": "Reopen when a pinned extraction, appraisal or source changes.",
                }
                if body["class"] == "design_hypothesis":
                    body.update(mechanism="The fictional contrast might transfer to a different task; this is untested.",
                                variables=["response_time_ms", "task"],
                                test_plan="Prepare a prospective protocol and obtain actual authorization before any real study.")
            elif kind == "requirement":
                body.update(**{"class": "design_hypothesis"}, scope="Variable selection for a fictional alert comparison",
                            mechanism="Vary timing to investigate the fictional response-time contrast.",
                            conditions=["Fictional paired task"], risks=["No real evidence establishes task transfer."],
                            test_refs=[], variables=["timing_ms"], result_refs=[])
            elif kind == "amendment":
                body.setdefault("prior_exposure", "The fictional corrected latency extraction has already supported a claim and requirement.")
                body.setdefault("required_rework", "Withhold all source-A-dependent claims and requirements until the invalidation is resolved.")
                body.update(verification="The correction or invalidation is stipulated by the synthetic fixture; no real notice or recheck exists.",
                            materiality="material", status="applied")
    return data


SEARCH_EXPORT = (
    "SYNTHETIC SEARCH EXPORT; NO LIVE SEARCH EXECUTED\n"
    "1\tSRC-A\tFirst occurrence of fictional report A\n"
    "2\tSRC-A\tDuplicate occurrence of fictional report A\n"
    "3\tSRC-B\tFirst occurrence of fictional companion report B\n"
).encode("utf-8")


def _all_families(corrected):
    data = copy.deepcopy(corrected)
    sequence = 0

    def add(rid, kind, body, basis=()):
        nonlocal sequence
        sequence += 1
        data["records"].append({
            "schema_version": 1, "id": rid, "kind": kind, "synthetic": True, "issue": 1,
            "revisions": [{"rev": 1, "at": f"2000-01-01T00:20:{sequence:02d}Z", "actor": copy.deepcopy(ACTOR),
                           "factual_status": "synthetic", "basis": copy.deepcopy(list(basis)), "data": copy.deepcopy(body)}],
        })

    add("SRCH-FIXTURE", "search_run", {
        "lane": "auditory", "protocol_version": "SYNTHETIC-pilot-v1-unfrozen", "mode": "pilot", "status": "completed",
        "platform": "Synthetic offline fixture", "interface": "Deterministic local text export",
        "query": "SYNTHETIC (coded_alert AND control)", "filters": ["Synthetic fixture records only"],
        "coverage": {"start": _missing("No live database coverage"), "end": _missing("No live database coverage")},
        "started_at": _known("2000-01-01T00:10:00Z"), "finished_at": _known("2000-01-01T00:10:01Z"),
        "reported_count": 3, "retrieved_count": 3,
        "export": _known({"path": "sources/search_export.txt", "sha256": hashlib.sha256(SEARCH_EXPORT).hexdigest()}),
        "pagination": {"complete": True, "detail": "All three stipulated synthetic occurrences are in the fixture export."},
        "failures": [], "boundary": "Fictional pilot-search example only; no real platform was queried or protocol frozen.",
    })
    for ordinal, source, duplicate in ((1, "A", False), (2, "A", True), (3, "B", False)):
        rid = f"HIT-FIXTURE-{ordinal}"
        body = {
            "search_ref": ref("SRCH-FIXTURE"), "ordinal": ordinal,
            "raw_metadata": f"SYNTHETIC report {source}; not a real publication", "returned_identifiers": [],
            "status": "duplicate" if duplicate else "resolved", "source_ref": ref("SRC-" + source),
            "resolution_reason": "The fictional export explicitly stipulates this occurrence's source identity.",
        }
        basis = [ref("SRCH-FIXTURE"), ref("SRC-" + source)]
        if duplicate:
            body["duplicate_of"] = ref("HIT-FIXTURE-1")
            basis.append(ref("HIT-FIXTURE-1"))
        add(rid, "search_hit", body, basis)
    for source in ("A", "B"):
        for stage in ("title_abstract", "full_text"):
            partial = source == "B" and stage == "full_text"
            add(f"SCR-{source}-{'TA' if stage == 'title_abstract' else 'FT'}", "screening", {
                "source_ref": ref("SRC-" + source), "stage": stage, "protocol_version": "SYNTHETIC-pilot-v1-unfrozen",
                "rule": "SYNTHETIC-ELIGIBILITY-1: retain fictional coded-alert comparison reports for this example",
                "decision": "uncertain" if partial else "include",
                "reason": "Only pages 1–2 of 4 were read, so full-text eligibility remains uncertain." if partial else
                          "Synthetic inclusion under the fictional eligibility rule; not actual screening evidence.",
                "access_limitation": "Full text is available, but only pages 1–2 of 4 are read in the scenario." if source == "B" else
                                     "All three fictional pages are available and covered by the reading attestation.",
                "reading_refs": [ref("AID-READ-" + source)], "review_refs": [],
            }, [ref("SRC-" + source), ref("AID-READ-" + source)])
    add("TX-CONTEXT", "theoretical_extraction", {
        "source_ref": ref("SRC-B"), "reading_ref": ref("AID-READ-B"), "locator": _locator(1), "status": "extracted",
        "assertion": "The fictional companion report describes the same fictional study and 24-person sample.",
        "definitions": [{"term": "companion report", "definition": "A second fictional publication about the stipulated study."}],
        "premises": ["The fixture text explicitly labels report B a companion report of the same study and sample."],
        "inference": ["A second report does not add an independent study in this stipulated example."],
        "context": "Synthetic identity passage on report B page 1, inside the actual fictional reading range.",
        "objections": ["A real publication-family judgment would require actual evidence and uncertainty assessment."],
        "interpretation": "Separate publication count from study and sample counts within this synthetic example.",
        "rq_refs": ["SYNTHETIC-RQ-IDENTITY"], "boundaries": "A contract example, not a theoretical research conclusion.",
    }, [ref("SRC-B"), ref("AID-READ-B")])
    add("HG-AUTH", "human_gate", {
        "need": "Actual participant authorization and ethics/privacy arrangements for any future real study.",
        "reason": "No real human-study authorization is asserted by this fictional example.",
        "attempted_remedies": ["Prepared a fictional protocol record to demonstrate the blocked readiness state."],
        "owner_action": "Supply appropriate authorization and ethics/privacy evidence only if a real study is separately requested.",
        "evidence": _unknown("No real authorization evidence exists in this synthetic example"),
        "completion_signal": "A real authorized human decision with evidence, outside this fixture context.",
        "stop_condition": "No real recruitment, participant contact or execution while authorization is absent.",
        "status": "blocked", "gate_class": "participants", "authorized_actor": _unknown("No real authorized person is represented"),
    })
    add("TEST-TRANSFER", "experiment_protocol", {
        "hypothesis_refs": [ref("CLM-HYP", 2)], "status": "readiness_blocked",
        "hypotheses": ["SYNTHETIC: test whether the fictional contrast transfers to a different task."],
        "estimands": ["Hypothetical paired response-time difference in a future defined population."],
        "outcomes": ["response_time_ms"], "manipulations": ["Hypothetical coded-alert versus control condition"],
        "checks": ["Define comprehension and manipulation checks before any real protocol freeze."],
        "sampling": "Not specified; no real people are recruited in this fixture.",
        "randomization": "Not specified; no randomization was performed.",
        "analysis": "No analysis is executed; a future authorized protocol must specify the method.",
        "exclusions": "No real exclusions applied; future exclusions require prespecification.",
        "ethics": "No ethics authorization asserted; the participant gate is blocked.",
        "privacy": "No personal data exist in this explicitly fictional example.",
        "gate_refs": [ref("HG-AUTH")], "exposure": "synthetic",
        "limitations": "Demonstrates blocked readiness only; not an executable or accepted human-study protocol.",
    }, [ref("CLM-HYP", 2), ref("REQ-TIMING", 2), ref("HG-AUTH")])
    add("AID-FIXTURE-BUILD", "assistance", {
        "subtype": "assistance", "task": "Demonstrate assistance-record shape using fictional inputs and outputs.",
        "input_refs": [ref("SRC-B")], "output_refs": [ref("TX-CONTEXT")],
        "artifacts": ["Synthetic TX-CONTEXT record"], "verification_steps": ["Structural checks only"],
        "limitations": "This is a fictional event and not the real implementation-assistance log.",
        "status": "performed", "performed_at": _known("2000-01-01T00:10:02Z"),
        "independence": "No real reading or independent human review is represented.",
    }, [ref("SRC-B"), ref("TX-CONTEXT")])
    return data


def snapshots():
    """Return fresh deterministic fixture snapshots; mutating them has no side effects."""
    cases = {name: _enrich_snapshot(data) for name, data in _prepass_snapshots().items()}
    cases["valid_all_families"] = _all_families(cases["valid_corrected"])
    return cases


def _fixture_files():
    snapshots_by_name = snapshots()
    cases = [
        {"name": "valid_before", "exit": 0, "previous": None, "context": "fixture"},
        {"name": "valid_correction_pending", "exit": 0, "previous": "valid_before", "context": "fixture"},
        {"name": "valid_corrected", "exit": 0, "previous": "valid_correction_pending", "context": "fixture"},
        {"name": "valid_source_invalidated", "exit": 0, "previous": "valid_corrected", "context": "fixture"},
        {"name": "valid_empty_live", "exit": 0, "previous": None, "context": "live"},
        {"name": "valid_all_families", "exit": 0, "previous": None, "context": "fixture"},
    ]
    contaminated = copy.deepcopy(snapshots_by_name["valid_empty_live"])
    contaminated.update(dataset_kind="live", research_state="in_progress",
                        records=[copy.deepcopy(snapshots_by_name["valid_before"]["records"][0])])
    empty_complete = copy.deepcopy(snapshots_by_name["valid_empty_live"])
    empty_complete["research_state"] = "complete"
    stale = copy.deepcopy(snapshots_by_name["valid_correction_pending"])
    stale["release_claims"] = [ref("CLM-LAT", 2)]
    unread = copy.deepcopy(snapshots_by_name["valid_before"])
    next(row for row in unread["records"] if row["id"] == "EX-ACC")["revisions"][0]["data"]["locator"].update(start=4, end=4)
    for name, content, context, code in (
            ("invalid_fixture_in_live", contaminated, "live", "CONTAMINATION"),
            ("invalid_empty_complete", empty_complete, "live", "EMPTY_COMPLETION"),
            ("invalid_stale_claim_export", stale, "fixture", "STALE_RELEASE"),
            ("invalid_unread_locator", unread, "fixture", "UNREAD_LOCATOR")):
        snapshots_by_name[name] = content
        cases.append({"name": name, "exit": 1, "previous": None, "context": context, "code": code})
    files = {f"{name}.json": dumps(data).encode("utf-8") for name, data in snapshots_by_name.items()}
    files.update({f"sources/report_{name}.txt": text.encode("utf-8") for name, text in SOURCE_TEXTS.items()})
    files["sources/search_export.txt"] = SEARCH_EXPORT
    files["expected_cases.json"] = dumps(cases).encode("utf-8")
    files["README.md"] = (
        "# Version 1 synthetic record fixtures\n\n"
        "Every report, person, study, result, review and event timestamp here is fictional. "
        "The fixtures exercise the record contract and do not belong in the live research register.\n\n"
        "Rebuild with `python -m tools.build_record_fixtures`; verify byte identity with "
        "`python -m tools.build_record_fixtures --check`. The generator first reproduces and "
        "hash checks all five recovered prepass snapshots, then explicitly converts them "
        "to `mhac-records/1`. `provenance.json` records the actual input identities and "
        "the limits of the conversion.\n\n"
        "## Worked sequence\n\n"
        "| Snapshot | Purpose |\n|---|---|\n"
        "| valid_before | Structurally valid initial 8 ms extraction, deliberately wrong against the source's 80 ms. |\n"
        "| valid_correction_pending | Appended 80 ms correction; dependent claims and requirements await rework. |\n"
        "| valid_corrected | Reappraisal, exact revision recheck, revised claim and requirement. |\n"
        "| valid_source_invalidated | Source A invalidated; dependent releases withheld while source B remains usable. |\n"
        "| valid_empty_live | An empty live register is explicitly not started. |\n"
        "| valid_all_families | All 16 families; three search hits map to two reports; full-text screening includes A and leaves partially read B uncertain; participant readiness is blocked. |\n\n"
        "The source texts are original synthetic fixture text, with form feeds separating "
        "file pages. The preserved example has two publications, one study, one experiment, "
        "one sample and two dependent outcomes. Full text access to report B coexists with "
        "reading only pages 1–2 of 4. A passing structural check proves neither source "
        "fidelity nor research acceptance.\n"
    ).encode("utf-8")
    provenance = {
        "artifact_kind": "synthetic_fixture_conversion",
        "contract": "mhac-records/1",
        "synthetic": True,
        "source_packet": "MHAC-R001-prepass",
        "assessed_prepass_commit": "796151a33ec7a1acc026b239fe5c883312ebf40b",
        "original_generator": {
            "path": "proposal/tools/build_r001_fixtures.py",
            "sha256": "5647aca824e534ed0909bd972e7ed05fb3793b3a734c411bdf379f5233c6da3b",
        },
        "original_snapshots_sha256": ORIGINAL_SNAPSHOT_SHA256,
        "conversion": [
            "Replay the actual preserved prepass event construction and verify each original snapshot hash.",
            "Change the dataset contract explicitly to mhac-records/1; there is no implicit prepass compatibility reader.",
            "Remove declared_counts because counts are derived from current records.",
            "Add revision factual_status=synthetic and explicit v1 contract fields as synthetic schema scaffolding.",
            "Keep original source bytes, all historical revision values, fictional timestamps and prior pins.",
            "Keep the initial incorrect 8 ms value to demonstrate the boundary between structure and source fidelity.",
            "Add a separate all-family fixture with fictional search occurrences, screening decisions, theoretical extraction, blocked protocol/gate and general assistance record.",
            "The added search export has three synthetic occurrences (A, duplicate A, B); it is not a historical or live search output.",
        ],
        "limitations": [
            "No real source retrieval, literature reading, participant observation or independent human review is represented.",
            "Added required fields are fictional implementation examples, not recovered historical evidence.",
            "Structural validity does not imply scientific quality, source truthfulness or readiness for research completion.",
        ],
        "files_sha256": {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(files.items())},
    }
    files["provenance.json"] = dumps(provenance).encode("utf-8")
    return files


def build(root: Path) -> None:
    """Write the fixture set to root; source construction requires no external files."""
    root = Path(root)
    for relative, raw in _fixture_files().items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def check(root: Path) -> list[str]:
    """Return reproducibility differences without modifying any files."""
    root = Path(root)
    generated = _fixture_files()
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    expected = set(generated)
    differences = [f"missing: {path}" for path in sorted(expected - actual)]
    differences += [f"unexpected: {path}" for path in sorted(actual - expected)]
    differences += [f"changed: {path}" for path in sorted(actual & expected)
                    if (root / path).read_bytes() != generated[path]]
    return differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path,
                        default=Path(__file__).resolve().parents[1] / "tests/fixtures/records/v1")
    parser.add_argument("--check", action="store_true", help="Verify the existing fixture bytes without writing")
    args = parser.parse_args()
    if args.check:
        differences = check(args.output)
        for difference in differences:
            print(difference)
        if not differences:
            print("Synthetic v1 fixtures reproduce byte for byte.")
        return int(bool(differences))
    build(args.output)
    print(f"Rebuilt explicitly synthetic v1 fixtures in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
