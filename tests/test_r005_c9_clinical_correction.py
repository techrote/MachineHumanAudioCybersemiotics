import json
import unittest
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "research" / "searches" / "auditory" / "c9-clinical-correction-2026-11-10" / "OBSERVATIONS.json"

class TestR005C9ClinicalCorrection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    def test_not_canonical_or_screened(self):
        d = self.data
        self.assertEqual((d["search_hit_records_added"], d["studies_admitted"], d["samples_admitted"]), (0, 0, 0))
        self.assertFalse(d["human_review"])
        self.assertFalse(d["query_specific_complete_exports"])

    def test_no_response_bytes_or_fake_hash(self):
        d = self.data
        self.assertFalse(d["raw_response_bytes_retained"])
        self.assertIsNone(d["response_sha256"])
        self.assertIsNone(d["platform_result_total"])
        self.assertFalse(d["full_text_pdfs_hashed"])

    def test_corrected_four_arm_semantics(self):
        d = self.data
        self.assertEqual(d["parent"]["doi"], "10.1177/00187208221116949")
        self.assertEqual(d["correction"]["doi"], "10.1177/00187208221131795")
        self.assertIn("both", d["parent"]["corrected_labeling"].lower())
        self.assertIn("multi-patient sequences", d["correction"]["verified_publisher_rendered_claim"])
        self.assertIn("Tables 1", d["correction"]["verified_publisher_rendered_claim"])
        self.assertNotEqual(d["parent"]["doi"], d["correction"]["doi"])

    def test_frozen_date_and_provenance(self):
        d = self.data
        self.assertEqual(d["frozen_cutoff"], "2026-10-04")
        self.assertEqual(d["observed_date_utc"], "2026-11-10")
        self.assertIn("NOT C1", d["platform"])
        self.assertEqual(len(d["recorded_queries"]), 4)
        self.assertTrue(all(x["query"] and x["interface"].startswith("C8") for x in d["recorded_queries"]))

    def test_leads_are_existing_and_not_independent_sample_count(self):
        d = self.data
        self.assertEqual(len(d["reference_leads"]), 4)
        self.assertEqual(len({x["doi"] for x in d["reference_leads"]}), 4)
        self.assertTrue(all(x["preexisting_paths"] for x in d["reference_leads"]))
        self.assertTrue(all(x["status"] == "discovery_only" for x in d["reference_leads"]))
        self.assertTrue(all("not full article" in x["reading_extent"] for x in d["reference_leads"]))

    def test_no_confusion_about_correction_year(self):
        d = self.data
        self.assertEqual(d["correction"]["online_date"], "2022-10-26")
        self.assertIn("2025", d["correction"]["journal_issue"])
        self.assertTrue(d["correction"]["online_date"] < d["frozen_cutoff"])

if __name__ == "__main__":
    unittest.main()
