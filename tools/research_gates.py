"""Structural stage prerequisites, kept separate from scientific acceptance."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from schemas.v1 import pin
from tools.record_io import fail, verify_artifact

STAGES = {"protocol", "corpus", "analysis", "internal_package",
          "external_review", "participant_study"}
FIELDS = {"stage", "status", "evidence_refs", "review_refs",
          "human_gate_refs", "artifacts", "limitations"}


def validate_gates(data: dict, graph: Any, *, root: Path | None) -> list[dict]:
    gates = {}
    results = []
    for gate in data["stage_gates"]:
        if not isinstance(gate, dict) or set(gate) != FIELDS:
            fail("GATE_SHAPE", "Unexpected or missing stage gate fields")
        stage, status = gate["stage"], gate["status"]
        if not isinstance(stage, str) or stage not in STAGES or stage in gates:
            fail("GATE_STAGE", str(stage))
        if not isinstance(status, str) or status not in {"not_started", "in_progress", "blocked", "complete"}:
            fail("GATE_STATUS", str(status))
        if not isinstance(gate["limitations"], str) or not gate["limitations"].strip():
            fail("GATE_LIMITATIONS", stage)
        for field in ("evidence_refs", "review_refs", "human_gate_refs", "artifacts"):
            if not isinstance(gate[field], list):
                fail("GATE_SHAPE", field)
        for field in ("evidence_refs", "review_refs", "human_gate_refs"):
            refs = [pin(value) for value in gate[field]]
            if len(set(refs)) != len(refs):
                fail("DUPLICATE_REFERENCE", f"{stage}.{field}")
            for ref in gate[field]:
                graph.lookup(ref)
        for ref in gate["review_refs"]:
            graph.lookup(ref, kind="assistance")
        for ref in gate["human_gate_refs"]:
            graph.lookup(ref, kind="human_gate")
        for artifact in gate["artifacts"]:
            if root is None:
                fail("ARTIFACT_ROOT", stage)
            verify_artifact(root, artifact)
        gates[stage] = gate

    for stage, gate in sorted(gates.items()):
        if gate["status"] != "complete":
            results.append({"stage": stage, "status": gate["status"],
                            "structural_prerequisites": "not_asserted",
                            "scientific_acceptance": "not_evaluated"})
            continue
        if data["dataset_kind"] != "live":
            fail("SYNTHETIC_COMPLETION", stage)
        if not gate["evidence_refs"] or not gate["artifacts"]:
            fail("EMPTY_COMPLETION", f"{stage} needs actual evidence and an artifact")
        kinds = set()
        evidence_pins = set()
        for ref in gate["evidence_refs"]:
            kind = graph.records[ref["id"]]["kind"]
            body = graph.require_current(ref, kind=kind, usable=True)
            if kind == "search_run" and body["status"] not in {"completed", "partial"}:
                fail("GATE_EVIDENCE", f"{stage}: search has not reached a recorded outcome")
            if stage == "corpus" and kind == "screening" and body["decision"] not in {"include", "exclude"}:
                fail("GATE_EVIDENCE", f"{stage}: unresolved screening decision")
            if stage in {"analysis", "internal_package"} and kind in {"extraction", "theoretical_extraction"}:
                if body["status"] not in {"extracted", "source_checked"}:
                    fail("GATE_EVIDENCE", f"{stage}: unfinished or disputed extraction")
            if stage == "analysis" and kind == "appraisal" and body["status"] not in {"checked", "revised"}:
                fail("GATE_EVIDENCE", f"{stage}: appraisal is not checked")
            kinds.add(kind)
            evidence_pins.add(pin(ref))
        required = {
            "protocol": {"source", "search_run"},
            "corpus": {"source", "search_run", "screening"},
            "analysis": {"source", "appraisal", "claim"},
            "internal_package": {"source", "claim"},
            "external_review": {"claim"},
            "participant_study": {"experiment_protocol", "experiment", "sample"},
        }[stage]
        if not required <= kinds:
            fail("GATE_EVIDENCE", f"{stage}: missing families {sorted(required - kinds)}")
        if stage in {"analysis", "internal_package"} and not (
                {"extraction", "theoretical_extraction"} & kinds):
            fail("GATE_EVIDENCE", f"{stage}: no empirical or theoretical extraction")
        if stage == "participant_study":
            fail("PARTICIPANT_COMPLETION_DEFERRED",
                 "R001 does not implement pilot-result acceptance; literature EXP records cannot stand in for actual execution")
        if stage == "internal_package" and any(
                gates.get(prereq, {}).get("status") != "complete"
                for prereq in ("protocol", "corpus", "analysis")):
            fail("GATE_DEPENDENCY", "Internal package requires protocol, corpus and analysis declarations")
        if stage == "corpus":
            from tools.evidence_flow import evidence_flow
            screening = evidence_flow(graph)["screening"]
            if any(counts[status] for counts in screening.values()
                   for status in ("pending", "uncertain", "awaiting_text")):
                fail("GATE_EVIDENCE", "Corpus still has unresolved effective screening decisions")
        if stage == "external_review" and gates.get("internal_package", {}).get("status") != "complete":
            fail("GATE_DEPENDENCY", "External review follows the internal package")
        checked = set()
        eligible_reviews = []
        for ref in gate["review_refs"]:
            review = graph.require_current(ref, kind="assistance")
            if (review["subtype"] != "review" or review["status"] != "performed"
                    or review["outcome"] != "pass"):
                fail("GATE_REVIEW", f"{stage}: an unperformed or failed review cannot pass a gate")
            required_scope = "external_feedback" if stage == "external_review" else "internal_audit"
            if review["scope"] != required_scope:
                fail("GATE_REVIEW", f"{stage}: requires {required_scope}")
            checked.update(pin(target) for target in review["target_refs"])
            eligible_reviews.append(review)
        if not evidence_pins <= checked:
            fail("GATE_REVIEW", f"{stage}: review does not cover exact evidence revisions")
        for ref in gate["human_gate_refs"]:
            human = graph.require_current(ref, kind="human_gate")
            if human["status"] != "satisfied":
                fail("UNSATISFIED_HUMAN_GATE", f"{stage}: {ref['id']}")
        if stage == "external_review":
            eligible_gates = [
                graph.lookup(ref, kind="human_gate")
                for ref in gate["human_gate_refs"]
                if graph.lookup(ref, kind="human_gate")["gate_class"] == "external_review"
            ]
            if not eligible_gates or not eligible_reviews or any(
                    review["verification"] not in {"human_checked", "independent_human_checked"}
                    for review in eligible_reviews):
                fail("FALSE_EXTERNAL_REVIEW", stage)
        results.append({"stage": stage, "status": "complete",
                        "structural_prerequisites": "passed",
                        "scientific_acceptance": "not_evaluated"})
    if data["research_state"] == "complete" and gates.get(
            "internal_package", {}).get("status") != "complete":
        fail("RESEARCH_COMPLETION", "A nonempty corpus alone cannot complete the internal research package")
    return results
