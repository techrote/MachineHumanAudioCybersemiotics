"""Fictional T004 syntactic invariants; no participants or waveforms."""
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mhac_t004_oracle", HERE / "protocol.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)
audit_cases, evaluate = oracle.audit_cases, oracle.evaluate
SOURCES, EVENTS = oracle.SOURCES, oracle.EVENTS

class TestCompositionalMessages(unittest.TestCase):
    def test_fixture_expectations(self):
        cases = json.loads((HERE / "SYNTHETIC-CASES.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 12)
        self.assertEqual(len({c["id"] for c in cases}), len(cases))
        self.assertEqual(len(audit_cases(cases)), len(cases))
        self.assertTrue(any(evaluate(c)["held_out"] for c in cases))
        self.assertEqual({"accept", "reject", "unresolved"},
                         {evaluate(c)["status"] for c in cases})

    def test_token_namespace_disjoint(self):
        self.assertFalse(set(SOURCES.values()) & set(EVENTS.values()))
        self.assertEqual(len(set(SOURCES.values())), len(SOURCES))
        self.assertEqual(len(set(EVENTS.values())), len(EVENTS))

    def test_invalid_nested_and_bool_versions_fail_closed(self):
        for version in (True, False, 0, -1, "1", [], None):
            msg = {"source":"pump","event":"fault","source_token":"s:pump",
                   "event_token":"e:fault","event_id":"a","version":version,
                   "mechanism":"serial","order":["source","event"]}
            self.assertEqual("reject", evaluate({"messages":[msg]})["status"])

    def test_batch_is_atomic_for_invalid_second_message(self):
        good = {"source":"pump","event":"fault","source_token":"s:pump",
                "event_token":"e:fault","event_id":"a","version":1,
                "mechanism":"serial","order":["source","event"]}
        bad = {**good,"source_token":"e:fault","event_id":"b"}
        failed = evaluate({"messages":[good, bad]})
        clean = evaluate({"messages":[good]})
        self.assertEqual("reject", failed["status"])
        self.assertEqual("accept", clean["status"])

    def test_unhashable_mechanism_fails_closed(self):
        msg = {"source":"pump","event":"fault","source_token":"s:pump",
               "event_token":"e:fault","event_id":"a","version":1,
               "mechanism":["serial"],"order":["source","event"]}
        self.assertEqual("reject", evaluate({"messages":[msg]})["status"])

    def test_not_a_human_result(self):
        good = {"source":"pump","event":"fault","source_token":"s:pump",
                "event_token":"e:fault","event_id":"a","version":1,
                "mechanism":"serial","order":["source","event"]}
        result = evaluate({"messages":[good]})
        self.assertNotIn("human_accuracy", result)
        self.assertEqual("symbolic-batch-only", result["reason"])

if __name__ == "__main__":
    unittest.main()
