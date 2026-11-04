"""MHAC-T005: symbolic cross-domain revision and event binding falsifiers.
No real source verification, sound, participants, or listener data.
"""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "research" / "tangents" / "continuous-state-events"
spec = importlib.util.spec_from_file_location("t005_causality", ROOT / "replay.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


class TestCausalBinding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {c["id"]: c for c in json.loads(
            (ROOT / "STATE-TRACES.json").read_text(encoding="utf-8")
        )}

    def fresh(self):
        return copy.deepcopy(self.cases["fresh-recovery-current-event"])

    def assert_rejected(self, case):
        for policy in oracle.POLICIES:
            with self.subTest(policy=policy):
                result = oracle.evaluate(case, policy)
                self.assertFalse(result["clear_allowed"])
                self.assertFalse(result["clear_audio"])
                self.assertFalse(result["clear_visual"])

    def test_independent_revision_sequences_permit_explicitly_bound_clear(self):
        c = self.fresh()
        c["sources"]["alpha"]["version"] = 0
        c["events"]["E1"]["version"] = 9001
        c["cue"].update(source_version=0, event_version=9001)
        c["recovery_binding"]["source_version"] = 0
        c["recovery_binding"]["closed_events"][0]["event_version"] = 9001
        for policy in oracle.POLICIES:
            with self.subTest(policy=policy):
                self.assertTrue(oracle.evaluate(c, policy)["clear_allowed"])

    def test_missing_mismatched_and_duplicate_attestations_refused(self):
        for mutation in ("missing", "authority", "source", "source_version",
                         "timestamp", "event", "event_version", "empty",
                         "duplicate", "bool_version"):
            c = self.fresh()
            b = c["recovery_binding"]
            if mutation == "missing":
                del c["recovery_binding"]
            elif mutation == "authority":
                b["authority"] = "self_asserted"
            elif mutation == "source":
                b["source_id"] = "beta"
            elif mutation == "source_version":
                b["source_version"] += 1
            elif mutation == "timestamp":
                b["source_observed_at_ms"] += 1
            elif mutation == "event":
                b["closed_events"][0]["event_id"] = "E0"
            elif mutation == "event_version":
                b["closed_events"][0]["event_version"] += 1
            elif mutation == "empty":
                b["closed_events"] = []
            elif mutation == "duplicate":
                b["closed_events"].append(copy.deepcopy(b["closed_events"][0]))
            else:
                b["source_version"] = True
            with self.subTest(mutation=mutation):
                self.assert_rejected(c)

    def test_closed_event_requires_explicit_coverage_not_global_version_order(self):
        c = self.fresh()
        c["events"]["E0"] = {
            "source_id": "alpha", "version": 0, "state": "closed", "deadline_ms": 140
        }
        self.assert_rejected(c)
        c["recovery_binding"]["closed_events"].append(
            {"event_id": "E0", "event_version": 0}
        )
        for policy in oracle.POLICIES:
            with self.subTest(policy=policy):
                self.assertTrue(oracle.evaluate(c, policy)["clear_allowed"])

    def test_open_same_source_event_blocks_even_with_fabricated_closed_proof(self):
        c = self.fresh()
        c["events"]["E2"] = {
            "source_id": "alpha", "version": 0, "state": "open", "deadline_ms": 140
        }
        c["recovery_binding"]["closed_events"].append(
            {"event_id": "E2", "event_version": 0}
        )
        self.assert_rejected(c)

    def test_other_source_open_event_does_not_block(self):
        c = self.fresh()
        c["events"]["B1"] = {
            "source_id": "beta", "version": 999, "state": "open", "deadline_ms": 140
        }
        for policy in oracle.POLICIES:
            with self.subTest(policy=policy):
                self.assertTrue(oracle.evaluate(c, policy)["clear_allowed"])


if __name__ == "__main__":
    unittest.main()
