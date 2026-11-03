"""T006 synthetic consistency regression tests; no acoustic or human outcome data."""
from __future__ import annotations

from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = spec_from_file_location("t006_oracle", HERE / "oracle.py")
oracle = module_from_spec(spec)
spec.loader.exec_module(oracle)


class TestActionPolarity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((HERE / "SCENARIOS.json").read_text(encoding="utf-8"))
        cls.by_id = {case["id"]: case for case in cls.cases}

    def test_full_labelled_fictional_fixture_set(self):
        self.assertGreaterEqual(len(self.cases), 24)
        self.assertEqual(len(self.by_id), len(self.cases))
        self.assertTrue(all(c.get("fictional") is True for c in self.cases))
        self.assertEqual(len(oracle.audit_cases(self.cases)), len(self.cases))

    def test_negator_removal_never_becomes_truthful_prohibition(self):
        case = deepcopy(self.by_id["simple-prohibition"])
        case["message"]["tokens"].remove("NOT")
        self.assertEqual(oracle.evaluate(case),
                         {"status": "reject", "reason": "operator-token-mismatch"})

    def test_relabelled_operator_cannot_authorize_forbidden_action(self):
        case = deepcopy(self.by_id["simple-prohibition"])
        case["message"].update(kind="require", operator_scope="action",
                               tokens=["DO", "restart"])
        self.assertEqual(oracle.evaluate(case)["reason"], "unauthorized-positive-action")

    def test_unknown_is_not_false_all_clear(self):
        case = deepcopy(self.by_id["truthful-unknown"])
        case["message"].update(kind="all_clear", operator_scope="clearance",
                               tokens=["ALL", "CLEAR"])
        self.assertEqual(oracle.evaluate(case),
                         {"status": "unresolved", "reason": "unknown-clearance"})

    def test_version_and_identity_bound_to_current_source(self):
        case = deepcopy(self.by_id["simple-direct"])
        case["message"]["version"] -= 1
        self.assertEqual(oracle.evaluate(case)["reason"], "stale-version")
        case = deepcopy(self.by_id["simple-direct"])
        case["message"]["source"] = "pump-B"
        self.assertEqual(oracle.evaluate(case)["reason"], "source-event-mismatch")

    def test_boolean_clock_and_truth_not_accepted(self):
        case = deepcopy(self.by_id["simple-direct"])
        case["now"] = True
        self.assertEqual(oracle.evaluate(case)["reason"], "invalid-clock")
        case["now"] = 120
        case["truth"]["version"] = True
        self.assertEqual(oracle.evaluate(case)["reason"], "invalid-truth")

    def test_acknowledgement_not_hazard_resolution(self):
        case = deepcopy(self.by_id["simple-direct"])
        case["message"].update(kind="ack", operator_scope="acknowledgement",
                               tokens=["ACKNOWLEDGED"])
        self.assertEqual(oracle.evaluate(case)["reason"], "ack-not-resolution")

    def test_not_confirmed_is_not_proof_of_clearance_status(self):
        case = deepcopy(self.by_id["simple-direct"])
        case["message"].update(kind="status", operator_scope="factual",
                               claim="clearance_unconfirmed",
                               tokens=["CLEARANCE", "NOT", "CONFIRMED"])
        self.assertEqual(oracle.evaluate(case),
                         {"status": "unresolved", "reason": "no-clearance-evidence"})

    def test_malformed_unhashable_fields_fail_closed(self):
        case = deepcopy(self.by_id["simple-direct"])
        case["truth"]["state"] = []
        self.assertEqual(oracle.evaluate(case)["reason"], "invalid-truth")
        case = deepcopy(self.by_id["simple-direct"])
        case["truth"]["actions"]["stop"] = []
        self.assertEqual(oracle.evaluate(case)["reason"], "invalid-truth")
        case = deepcopy(self.by_id["simple-direct"])
        case["message"]["kind"] = []
        self.assertEqual(oracle.evaluate(case)["reason"], "invalid-message")
        case = deepcopy(self.by_id["active-status"])
        case["message"]["claim"] = []
        self.assertEqual(oracle.evaluate(case)["reason"], "invalid-message")


if __name__ == "__main__":
    unittest.main()
