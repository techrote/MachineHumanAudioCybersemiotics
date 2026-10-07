"""Stage declarations cannot promote empty, simulated or unfinished research."""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from schemas import ValidationError
from tools.record_io import dumps
from tools.records import empty_dataset, validate_dataset
from tools.research_gates import validate_gates


def ref(rid: str) -> dict:
    return {"id": rid, "rev": 1}


class GateGraph:
    """An explicit in-memory test double; none of these objects is live evidence."""
    def __init__(self):
        self.records = {
            "SRC-TEST": {"kind": "source"},
            "SRCH-TEST": {"kind": "search_run"},
            "AID-AUDIT": {"kind": "assistance"},
            "SCR-TEST": {"kind": "screening"},
        }
        self.bodies = {
            "SRC-TEST": {"validity": "active"},
            "SRCH-TEST": {"status": "completed"},
            "SCR-TEST": {"stage": "full_text", "decision": "uncertain"},
            "AID-AUDIT": {
                "subtype": "review", "status": "performed", "scope": "internal_audit",
                "outcome": "pass", "target_refs": [ref("SRC-TEST"), ref("SRCH-TEST")],
            },
        }
        self.latest = {rid: {"data": body} for rid, body in self.bodies.items()
                       if rid != "SCR-TEST"}

    def lookup(self, value, kind=None):
        if value["rev"] != 1 or value["id"] not in self.bodies:
            raise ValidationError("DANGLING_REFERENCE: test")
        if kind and self.records[value["id"]]["kind"] != kind:
            raise ValidationError("REFERENCE_TYPE: test")
        return self.bodies[value["id"]]

    def require_current(self, value, kind=None, usable=True):
        return self.lookup(value, kind)


class ResearchGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        text = b"SYNTHETIC gate-test artifact. No actual protocol acceptance.\n"
        (self.root / "protocol.md").write_bytes(text)
        self.artifact = {"path": "protocol.md", "sha256": hashlib.sha256(text).hexdigest()}
        self.graph = GateGraph()

    def gate(self, status="complete"):
        return {
            "stage": "protocol", "status": status,
            "evidence_refs": [ref("SRC-TEST"), ref("SRCH-TEST")],
            "review_refs": [ref("AID-AUDIT")], "human_gate_refs": [],
            "artifacts": [self.artifact],
            "limitations": "Synthetic test of structural prerequisites, not real evidence.",
        }

    def declaration(self, gate=None, kind="live"):
        # The isolated double exercises logic; real validate_dataset separately
        # enforces that caller context matches every record's synthetic flag.
        return {"dataset_kind": kind, "research_state": "in_progress",
                "stage_gates": [gate or self.gate()]}

    def test_empty_live_not_started_valid_and_science_not_evaluated(self):
        result = validate_dataset(empty_dataset(), expected_kind="live", root=self.root)
        self.assertEqual(result["record_count"], 0)
        self.assertIn("scientific_validity", result["not_evaluated"])

    def test_empty_complete_and_in_progress_rejected(self):
        for state in ("complete", "in_progress"):
            value = empty_dataset()
            value["research_state"] = state
            with self.subTest(state=state), self.assertRaisesRegex(ValidationError, "EMPTY_COMPLETION"):
                validate_dataset(value, expected_kind="live", root=self.root)

    def test_valid_recorded_protocol_prerequisites_do_not_assert_science(self):
        result = validate_gates(self.declaration(), self.graph, root=self.root)
        self.assertEqual(result[0]["structural_prerequisites"], "passed")
        self.assertEqual(result[0]["scientific_acceptance"], "not_evaluated")

    def test_simulation_cannot_complete_stage(self):
        with self.assertRaisesRegex(ValidationError, "SYNTHETIC_COMPLETION"):
            validate_gates(self.declaration(kind="fixture"), self.graph, root=self.root)

    def test_pending_simulated_stage_is_explicitly_allowed(self):
        result = validate_gates(self.declaration(self.gate("blocked"), "fixture"),
                                self.graph, root=self.root)
        self.assertEqual(result[0]["structural_prerequisites"], "not_asserted")

    def test_empty_gate_evidence_rejected(self):
        gate = self.gate()
        gate["evidence_refs"] = []
        with self.assertRaisesRegex(ValidationError, "EMPTY_COMPLETION"):
            validate_gates(self.declaration(gate), self.graph, root=self.root)

    def test_review_must_cover_exact_revision_pins(self):
        self.graph.bodies["AID-AUDIT"]["target_refs"] = [ref("SRC-TEST")]
        with self.assertRaisesRegex(ValidationError, "GATE_REVIEW"):
            validate_gates(self.declaration(), self.graph, root=self.root)

    def test_review_outcome_or_scope_cannot_be_substituted(self):
        for field, value in (("outcome", "fail"), ("status", "planned"),
                             ("scope", "source_fidelity")):
            graph = copy.deepcopy(self.graph)
            graph.bodies["AID-AUDIT"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValidationError, "GATE_REVIEW"):
                validate_gates(self.declaration(), graph, root=self.root)

    def test_running_search_does_not_complete_protocol(self):
        self.graph.bodies["SRCH-TEST"]["status"] = "running"
        with self.assertRaisesRegex(ValidationError, "GATE_EVIDENCE"):
            validate_gates(self.declaration(), self.graph, root=self.root)

    def test_unresolved_screening_does_not_complete_corpus(self):
        gate = self.gate()
        gate["stage"] = "corpus"
        gate["evidence_refs"].append(ref("SCR-TEST"))
        with self.assertRaisesRegex(ValidationError, "GATE_EVIDENCE"):
            validate_gates(self.declaration(gate), self.graph, root=self.root)

    def test_changed_artifact_hash_blocks_gate(self):
        (self.root / "protocol.md").write_text("Changed", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "ARTIFACT_HASH"):
            validate_gates(self.declaration(), self.graph, root=self.root)

    def test_complete_state_requires_internal_package_gate(self):
        data = self.declaration()
        data["research_state"] = "complete"
        with self.assertRaisesRegex(ValidationError, "RESEARCH_COMPLETION"):
            validate_gates(data, self.graph, root=self.root)

    def test_invalid_gate_and_state_shapes_fail_closed(self):
        for field, value in (("stage", []), ("status", {}), ("artifacts", ""),
                             ("limitations", ""), ("evidence_refs", [ref("MISSING")])):
            gate = self.gate()
            gate[field] = value
            with self.subTest(field=field), self.assertRaises(ValidationError):
                validate_gates(self.declaration(gate), self.graph, root=self.root)
        data = empty_dataset()
        data["research_state"] = []
        with self.assertRaises(ValidationError):
            validate_dataset(data, expected_kind="live")


if __name__ == "__main__":
    unittest.main()
