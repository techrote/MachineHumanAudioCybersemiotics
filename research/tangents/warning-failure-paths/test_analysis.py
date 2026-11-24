"""Negative and invariant tests for explicitly synthetic warning examples."""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mhac_warning_failure_demo", HERE / "analysis.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
RAW = (HERE / "SYNTHETIC-ONLY.csv").read_text(encoding="utf-8")


class SyntheticFailurePathTests(unittest.TestCase):
    def test_fixed_inventory_and_conditional_denominators(self):
        summary = demo.summarize(demo.parse_cases(RAW))
        self.assertEqual(summary["dataset_kind"], "synthetic_fixture")
        self.assertEqual(summary["human_participants"], 0)
        self.assertEqual(summary["emitted_trials"], 12)
        self.assertEqual(summary["endpoint_counts"]["reported_detection"]["positive"], 9)
        self.assertEqual(summary["endpoint_counts"]["identified_correctly"]["assessed"], 8)
        self.assertEqual(summary["endpoint_counts"]["timely_correct_action"],
                         {"positive": 2, "assessed": 4, "unassessed": 8})

    def test_high_urgency_identity_error_not_success(self):
        cases = {r["case_id"]: r for r in demo.parse_cases(RAW)}
        self.assertEqual(cases["S05"]["urgency_rating"], 7)
        self.assertEqual(demo.classify(cases["S05"]), "identification_error")
        self.assertIsNone(demo.timely_correct(cases["S05"]))

    def test_audible_prediction_does_not_diagnose_attention(self):
        cases = {r["case_id"]: r for r in demo.parse_cases(RAW)}
        self.assertEqual(demo.classify(cases["S03"]), "audible_prediction_with_no_report")
        self.assertEqual(demo.classify(cases["S10"]), "miss_unattributed")

    def test_unknown_time_not_counted_as_late_or_success(self):
        cases = {r["case_id"]: r for r in demo.parse_cases(RAW)}
        self.assertEqual(demo.classify(cases["S09"]), "timing_unassessed")
        self.assertIsNone(demo.timely_correct(cases["S09"]))

    def test_deterministic_output(self):
        self.assertEqual(demo.summarize(demo.parse_cases(RAW)),
                         demo.summarize(demo.parse_cases(RAW)))

    def test_reject_non_synthetic_row(self):
        with self.assertRaisesRegex(ValueError, "synthetic_fixture"):
            demo.parse_cases(RAW.replace("S01,synthetic_fixture", "S01,live_data"))

    def test_reject_invalid_boolean(self):
        with self.assertRaisesRegex(ValueError, "true, false"):
            demo.parse_cases(RAW.replace("S02,synthetic_fixture,modelled_masking,true,false,false",
                                         "S02,synthetic_fixture,modelled_masking,true,maybe,false"))

    def test_reject_downstream_answer_after_non_detection(self):
        with self.assertRaisesRegex(ValueError, "identity test"):
            demo.parse_cases(RAW.replace("S03,synthetic_fixture,audible_prediction_omission,true,true,false,,,,,3.0,4",
                                         "S03,synthetic_fixture,audible_prediction_omission,true,true,false,true,,,,3.0,4"))

    def test_reject_duplicate_case_id(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            demo.parse_cases(RAW.replace("S12,synthetic_fixture", "S11,synthetic_fixture"))

    def test_reject_nonfinite_latency(self):
        with self.assertRaisesRegex(ValueError, "finite positive"):
            demo.parse_cases(RAW.replace("S08,synthetic_fixture,late_correct_action,true,true,true,true,true,true,4.5",
                                         "S08,synthetic_fixture,late_correct_action,true,true,true,true,true,true,nan"))


if __name__ == "__main__":
    unittest.main()
