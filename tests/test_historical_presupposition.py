"""MHAC-T013 symbolic-only regression checks; not human listening evidence."""
import importlib.util
import json
from pathlib import Path
import unittest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "research/tangents/historical-presupposition/replay.py"
SPEC = importlib.util.spec_from_file_location("mhac_t013_replay", SCRIPT)
replay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(replay)


class HistoricalPresuppositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = replay.load_cases()
        cls.by_id = {case["id"]: case for case in cls.cases}

    def test_fixture_count_and_independent_truth_strata(self):
        self.assertEqual(len(self.cases), 30)
        self.assertEqual(len(self.by_id), 30)
        self.assertEqual(set(replay.TRIGGERS), {c["trigger"] for c in self.cases})
        for label in ("supported", "contradicted", "unknown", "not_applicable"):
            self.assertTrue(any(c["history_support"] == label for c in self.cases))

    def test_all_comparator_invariants(self):
        scores = {p: replay.evaluate(self.cases, p) for p in replay.POLICIES}
        replay.run_checks(self.cases, scores)

    def test_present_true_with_unknown_history_survives_gate(self):
        for case_id in ("AG03", "ST03", "SP03", "RS03"):
            case = self.by_id[case_id]
            self.assertTrue(case["action_offer_valid"])
            out = replay.render(case, "evidence_guard")
            self.assertEqual(out["spoken"], replay.SENTENCES[case["trigger"]][0])
            self.assertFalse(out["history_claim"])
            self.assertTrue(out["action"])

    def test_unknown_past_is_not_false_past(self):
        for case_id in ("AG02", "AG03"):
            case = self.by_id[case_id]
            out = replay.render(case, "naive_history")
            self.assertTrue(out["history_claim"])
        self.assertEqual(self.by_id["AG02"]["history_support"], "contradicted")
        self.assertEqual(self.by_id["AG03"]["history_support"], "unknown")

    def test_known_false_and_unknown_current_never_asserted(self):
        for case in self.cases:
            if case["current_truth"] != "true":
                for policy in replay.POLICIES:
                    self.assertIsNone(replay.render(case, policy)["spoken"])
                    self.assertFalse(replay.render(case, policy)["action"])

    def test_expired_action_not_offered_even_with_true_present(self):
        for case_id in ("ST05", "RS05", "NO05"):
            case = self.by_id[case_id]
            self.assertEqual(case["deadline_state"], "expired")
            self.assertEqual(case["current_truth"], "true")
            for policy in replay.POLICIES:
                self.assertIsNotNone(replay.render(case, policy)["spoken"])
                self.assertFalse(replay.render(case, policy)["action"])

    def test_adverse_mutation_is_caught(self):
        altered = [dict(case) for case in self.cases]
        altered[0]["action_offer_valid"] = True
        altered[0]["current_truth"] = "false"
        temp = self.enterContext(__import__("tempfile").TemporaryDirectory())
        path = Path(temp) / "cases.json"
        path.write_text(json.dumps({"schema": "mhac-t013-fictional-cases-v1",
                                    "cases": altered}), encoding="utf-8")
        with self.assertRaises(ValueError):
            replay.load_cases(path)

    def test_no_history_control_uses_plain_proposition(self):
        for case in self.cases:
            if case["trigger"] == "none":
                for policy in replay.POLICIES:
                    out = replay.render(case, policy)
                    self.assertFalse(out["history_claim"])
                    self.assertFalse(out["timeline"])

    def test_timeline_is_optional_not_audible_claim(self):
        good = replay.render(self.by_id["AG01"], "present_plus_timeline")
        unknown = replay.render(self.by_id["AG03"], "present_plus_timeline")
        self.assertTrue(good["timeline"])
        self.assertFalse(unknown["timeline"])
        self.assertFalse(good["history_claim"])
        self.assertEqual(good["spoken"], unknown["spoken"])


if __name__ == "__main__":
    unittest.main()
