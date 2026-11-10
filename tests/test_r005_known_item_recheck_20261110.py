"""R005 C8 known-item recheck audit integrity; never a screening or source-verification proof."""
import csv
import json
import pathlib
import unittest
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT / "research/searches/auditory"
LEDGER = BASE / "known-item-recheck-2026-11-10/OBSERVATIONS.json"
HISTORICAL = BASE / "exports/KNOWN-ITEM-CHECK-R005.csv"


class R005KnownItemRecheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(LEDGER.read_text(encoding="utf-8"))
        with HISTORICAL.open(newline="", encoding="utf-8") as handle:
            cls.historical = {int(row["entry"]): row for row in csv.DictReader(handle)}

    def test_frozen_baseline_and_no_database_search_claim(self):
        self.assertEqual(self.audit["frozen_publication_cutoff"], "2026-10-04")
        self.assertEqual(self.audit["schema_version"], "mhac-r005-known-item-recheck/1")
        self.assertIn("not a v1 search_run", self.audit["production_record_status"])
        self.assertIn("C8", self.audit["channel"])
        self.assertEqual(len(self.historical), 69)
        self.assertEqual(sum(r["outcome"] == "not_located" for r in self.historical.values()), 21)

    def test_observations_are_originally_unlocated_and_unique(self):
        rows = self.audit["observations"]
        ids = [r["known_item"] for r in rows]
        self.assertEqual(len(rows), self.audit["observation_count"])
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {2, 7, 29, 34, 38, 42, 44, 45, 52, 53})
        for r in rows:
            old = self.historical[r["known_item"]]
            self.assertEqual(old["outcome"], "not_located")
            self.assertEqual(r["historical_outcome"], "not_located")
            self.assertEqual(r["new_outcome"], "located_bibliographic_candidate")
            self.assertTrue(r["as_run_query"])
            self.assertIn(r["web_mode"], {"fast", "slow"})
            self.assertTrue(r["record_type"])
            self.assertTrue(r["verification_notes"])
            self.assertEqual(r["screening_status"], "not_assessed")
            self.assertFalse(r["full_text_verified"])
            self.assertEqual(r["independent_study_status"], "unknown")
            self.assertTrue(r["landing_urls"])
            for url in r["landing_urls"]:
                parsed = urlsplit(url)
                self.assertEqual(parsed.scheme, "https")
                self.assertTrue(parsed.netloc)

    def test_doi_conflict_not_promoted(self):
        k29 = next(r for r in self.audit["observations"] if r["known_item"] == 29)
        self.assertIn("10.1518/107118109X12524443346194", k29["verification_notes"])
        self.assertEqual(k29["doi_from_historical_citation"], "10.1177/154193120905301831")
        self.assertEqual(k29["source_identity_status"], "candidate_matched_to_historical_citation")


if __name__ == "__main__":
    unittest.main()
