"""Integrity checks for the *supplementary* R005 remainder web navigation audit.

Tests ensure this ledger cannot accidentally masquerade as a source-screened corpus.
They do not assert external metadata truth or reproduce search-engine results.
"""
import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "research/searches/auditory/known-item-remainder-2026-11-10/OBSERVATIONS.json"
HISTORICAL = ROOT / "research/searches/auditory/exports/KNOWN-ITEM-CHECK-R005.csv"
PRIOR = ROOT / "research/searches/auditory/known-item-recheck-2026-11-10/OBSERVATIONS.json"


class R005KnownItemRemainderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(FILE.read_text(encoding="utf-8"))
        cls.prior = json.loads(PRIOR.read_text(encoding="utf-8"))
        with HISTORICAL.open(encoding="utf-8", newline="") as fp:
            cls.historical = list(csv.DictReader(fp))

    def test_historical_baseline_unchanged(self):
        self.assertEqual(len(self.historical), 69)
        from collections import Counter
        self.assertEqual(dict(Counter(r["outcome"] for r in self.historical)),
                         {"located": 38, "possible": 10, "not_located": 21})

    def test_remainder_exact_and_disjoint(self):
        rem = [x["known_item"] for x in self.data["observations"]]
        prior = [x["known_item"] for x in self.prior["observations"]]
        self.assertEqual(rem, [4, 9, 12, 33, 35, 50, 54, 56, 64, 67, 68])
        self.assertEqual(len(set(rem)), len(rem))
        self.assertFalse(set(rem) & set(prior))
        originals = {int(r["entry"]) for r in self.historical if r["outcome"] == "not_located"}
        self.assertEqual(set(rem) | set(prior), originals)

    def test_scope_disclaimers_are_machine_checkable(self):
        d = self.data
        self.assertEqual(d["frozen_publication_cutoff"], "2026-10-04")
        self.assertEqual(d["observation_count"], len(d["observations"]))
        self.assertIn("supplementary", d["production_record_status"])
        self.assertIn("C8", d["channel"])
        for item in d["observations"]:
            self.assertEqual(item["historical_outcome"], "not_located")
            self.assertEqual(item["screening_status"], "not_assessed")
            self.assertFalse(item["full_text_verified"])
            self.assertEqual(item["independent_study_status"], "unknown")
            self.assertTrue(item["as_run_query"])
            self.assertTrue(item["verification_notes"])
            self.assertTrue(item["landing_urls"])
            for url in item["landing_urls"]:
                self.assertTrue(url.startswith("https://"), url)

    def test_metadata_conflicts_not_resolved_by_guessing(self):
        items = {x["known_item"]: x for x in self.data["observations"]}
        self.assertEqual(items[50]["source_identity_status"], "provisional_metadata_conflict")
        self.assertIn("194-199", items[50]["verification_notes"].replace("–", "-"))
        self.assertIn("196-201", items[50]["verification_notes"].replace("–", "-"))
        self.assertIsNone(items[54]["doi_from_historical_citation"])
        self.assertIn("malformed", items[54]["verification_notes"])

    def test_pdf_discovery_not_mislabeled_full_text(self):
        items = {x["known_item"]: x for x in self.data["observations"]}
        for n in [12, 33]:
            self.assertFalse(items[n]["full_text_verified"])
            self.assertNotEqual(items[n]["reading_extent"], "full_text")

if __name__ == "__main__":
    unittest.main()
