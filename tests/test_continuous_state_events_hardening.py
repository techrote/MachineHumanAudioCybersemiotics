"""Negative/mutation controls for MHAC-T005 fictional state/event oracle.

These tests validate symbolic rules only, not physical signals or human performance.
"""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "research" / "tangents" / "continuous-state-events"
spec = importlib.util.spec_from_file_location("mhac_t005_mutations", ROOT / "replay.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


class TestT005Hardening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cases = json.loads((ROOT / "STATE-TRACES.json").read_text(encoding="utf-8"))
        cls.by_id = {case["id"]: case for case in cases}
        assert len(cls.by_id) == len(cases), "duplicate fictional fixture ID"

    def fresh(self):
        return copy.deepcopy(self.by_id["fresh-recovery-current-event"])

    def assert_rejected_all(self, case):
        for policy in oracle.POLICIES:
            with self.subTest(policy=policy):
                result = oracle.evaluate(case, policy)
                self.assertFalse(result["clear_allowed"])
                self.assertFalse(result["clear_audio"])
                self.assertFalse(result["clear_visual"])

    def test_fixture_expected_truth_labels_are_explicit_fields(self):
        self.assertEqual(len(self.by_id), 25)
        for case in self.by_id.values():
            with self.subTest(case=case["id"]):
                self.assertEqual(set(case["expected"]), {"truth", "event_due", "clear_allowed"})
                for policy in oracle.POLICIES:
                    actual = oracle.evaluate(case, policy)
                    self.assertEqual(
                        {key: actual[key] for key in case["expected"]}, case["expected"]
                    )

    def test_playback_silence_never_means_source_recovery(self):
        case = copy.deepcopy(self.by_id["ack-not-recovery"])
        for playback in ("playing", "silenced", "failed", "ducked"):
            case["playback"] = playback
            for policy in oracle.POLICIES:
                with self.subTest(playback=playback, policy=policy):
                    result = oracle.evaluate(case, policy)
                    self.assertEqual(result["truth"], "active")
                    self.assertFalse(result["clear_allowed"])

    def test_recovery_guards_fail_closed_on_state_and_freshness_mutation(self):
        for condition, online, observed_at, ttl in (
            ("active", True, 90, 50),
            ("unknown", True, 90, 50),
            ("inactive", False, 90, 50),
            ("inactive", True, 49, 50),
            ("inactive", True, 101, 50),
        ):
            case = self.fresh()
            source = case["sources"]["alpha"]
            source.update(
                condition=condition, online=online, observed_at_ms=observed_at, ttl_ms=ttl
            )
            with self.subTest(condition=condition, online=online, observed_at=observed_at):
                self.assert_rejected_all(case)

    def test_recovery_at_exact_ttl_boundary_is_not_arbitrarily_expired(self):
        case = self.fresh()
        case["sources"]["alpha"]["observed_at_ms"] = 50
        case["sources"]["alpha"]["ttl_ms"] = 50
        for policy in oracle.POLICIES:
            with self.subTest(policy=policy):
                result = oracle.evaluate(case, policy)
                self.assertEqual(result["truth"], "inactive")
                self.assertTrue(result["clear_allowed"])

    def test_no_replay_of_mismatched_identity_revision_or_open_event(self):
        mutants = []
        for field, value in (("source_id", "beta"), ("event_id", "E0"),
                             ("source_version", 1), ("event_version", 0)):
            case = self.fresh()
            case["cue"][field] = value
            mutants.append(case)
        unclosed = self.fresh()
        unclosed["events"]["E1"]["state"] = "open"
        mutants.append(unclosed)
        conflict = self.fresh()
        conflict["events"]["E2"] = {
            "source_id": "alpha", "version": 3, "state": "open", "deadline_ms": 150
        }
        mutants.append(conflict)
        for i, case in enumerate(mutants):
            with self.subTest(mutation=i):
                self.assert_rejected_all(case)

    def test_due_event_survives_active_state_and_acknowledgement(self):
        case = copy.deepcopy(self.by_id["urgent-event-while-status-persists"])
        case["acknowledged_events"] = ["E1"]
        case["completed_events"] = ["E1"]
        for policy in oracle.POLICIES:
            with self.subTest(policy=policy):
                result = oracle.evaluate(case, policy)
                self.assertEqual(result["truth"], "active")
                self.assertTrue(result["event_due"])
                self.assertTrue(result["event_visual"])
                self.assertTrue(result["event_audio"])

    def test_ducking_is_priority_rule_not_recovery(self):
        case = copy.deepcopy(self.by_id["urgent-event-while-status-persists"])
        normal = oracle.evaluate(case, "persistent_discrete")
        ducked = oracle.evaluate(case, "ducked_hybrid")
        self.assertTrue(normal["status_audio"])
        self.assertFalse(normal["status_ducked"])
        self.assertFalse(ducked["status_audio"])
        self.assertTrue(ducked["status_ducked"])
        self.assertEqual(normal["truth"], ducked["truth"])
        self.assertEqual(normal["event_due"], ducked["event_due"])
        self.assertEqual(normal["event_audio"], ducked["event_audio"])


if __name__ == "__main__":
    unittest.main()
