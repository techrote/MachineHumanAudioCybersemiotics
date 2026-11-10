"""Regression guards for source-limited Stevens original-body preassessment (Refs #6).

These tests check truthful record structure and the preserved incomplete gate.
They are not a substitute for reviewing the original publication, or an empirical
eligibility / sample-independence verdict.
"""
import copy
import json
import unittest
from pathlib import Path

from schemas import ValidationError
from schemas.v1 import validate_record


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research/screening/records/SCR-R006-STEVENS-2009-WARNING-FT.json"
TA = ROOT / "research/screening/records/SCR-R006-STEVENS-2009-WARNING-TA.json"
REVIEW = ROOT / "research/screening/stevens_2009_full_text_preassessment_20261110/README.md"


class StevensOriginalBodyBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.ta = json.loads(TA.read_text(encoding="utf-8"))
        cls.review = REVIEW.read_text(encoding="utf-8")

    def test_live_v1_and_append_only_revision(self):
        validate_record(self.record, expected_kind="live")
        self.assertGreaterEqual(len(self.record["revisions"]), 2)
        old, new = self.record["revisions"][0:2]
        self.assertEqual((old["rev"], new["rev"]), (1, 2))
        self.assertLess(old["at"], new["at"])
        self.assertEqual(old["data"]["decision"], "pending")
        self.assertEqual(new["data"]["decision"], "pending")

    def test_exact_source_first_pass_and_protocol_pins(self):
        old, new = self.record["revisions"][0:2]
        for key in ("source_ref", "stage", "track", "protocol_version"):
            self.assertEqual(old["data"][key], new["data"][key])
        self.assertEqual(new["data"]["source_ref"],
                         {"id": "SRC-R006-E-STEVENS-INFORMATIVE", "rev": 1})
        self.assertEqual(new["data"]["stage"], "full_text")
        self.assertEqual(new["data"]["track"], "empirical")
        self.assertEqual(self.ta["revisions"][0]["data"]["decision"], "include")
        self.assertIn({"id": "SCR-R006-STEVENS-2009-WARNING-TA", "rev": 1},
                      new["basis"])

    def test_no_unsupported_manifestation_review_or_final_admission(self):
        new = self.record["revisions"][1]
        self.assertEqual(new["actor"]["kind"], "agent")
        self.assertEqual(new["data"]["decision"], "pending")
        self.assertEqual(new["data"]["reading_refs"], [])
        self.assertEqual(new["data"]["review_refs"], [])
        self.assertNotIn("supersedes_ref", new["data"])
        self.assertIn("no registered manifestation", self.review.lower())

    def test_distinct_rating_task_is_not_main_experiment_or_independent_study(self):
        reason = self.record["revisions"][1]["data"]["reason"]
        self.assertIn("36 adults", reason)
        self.assertIn("N=40", reason)
        self.assertIn("stimulus-selection", reason)
        self.assertIn("UNKNOWN", reason)
        self.assertIn("not two independent studies", reason)
        self.assertIn("must not be added to", self.review.lower())

    def test_original_html_and_r005_xml_are_not_conflated(self):
        limitation = self.record["revisions"][1]["data"]["access_limitation"]
        self.assertIn("pmc.ncbi.nlm.nih.gov/articles/PMC2865004/", limitation)
        self.assertIn("not this agent", limitation.lower())
        self.assertIn("74,338", limitation)
        self.assertIn("1390d7a4def94ad6b0926a5f1ae2608999f31713fb3ee5dad20b9e3fcc52658b", limitation)
        self.assertIn("NOT verified", limitation)
        self.assertIn("web intermediary", limitation.lower())
        self.assertIn("Methods", self.review)
        self.assertIn("Results", self.review)

    def test_tampering_earlier_provenance_is_detected_by_v1(self):
        altered = copy.deepcopy(self.record)
        altered["revisions"][1]["rev"] = 3
        with self.assertRaisesRegex(ValidationError, "REVISION"):
            validate_record(altered, expected_kind="live")

    def test_human_impersonation_is_not_part_of_our_record(self):
        actor = self.record["revisions"][1]["actor"]
        self.assertEqual(actor["kind"], "agent")
        self.assertIn("GPT-6", actor["model"])
        self.assertIn("independent human", self.review.lower())


if __name__ == "__main__":
    unittest.main()
