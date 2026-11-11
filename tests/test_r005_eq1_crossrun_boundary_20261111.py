"""Negative controls for R005 cross-invocation EQ1 boundary claims."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "research/searches/auditory/eq1-crossrun-boundary-20261111/check_boundary.py"
SPEC = importlib.util.spec_from_file_location("r005_eq1_crossrun_boundary", MOD)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class CrossRunBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = json.loads(CHECK.PREVIOUS.read_text(encoding="utf-8"))
        cls.following = json.loads(CHECK.NEXT.read_text(encoding="utf-8"))

    def test_real_observations_match_pinned_reconciliation(self):
        actual = CHECK.verify()
        self.assertEqual(len(actual["page43_vs_page44_shared_ids"]), 8)
        self.assertTrue(actual["page43_suffix_equals_page44_prefix"])
        self.assertEqual(actual["page44_not_on_pages42_or43_count"], 92)
        self.assertEqual(actual["page42_vs_page44_shared_ids"], [])

    def test_no_assumption_of_new_unique_publications(self):
        record = json.loads(CHECK.CURRENT.read_text(encoding="utf-8"))
        self.assertFalse(record["claim_boundary_contiguous"])
        self.assertFalse(record["claim_completed_eq1"])
        self.assertFalse(record["claim_92_new_publications"])
        self.assertEqual(record["new_admitted_publications_studies_experiments_samples"], [0, 0, 0, 0])

    def test_mutated_frozen_query_rejected(self):
        new = copy.deepcopy(self.following)
        new["pages"][0]["url"] = new["pages"][0]["url"].replace("2026-10-04", "2026-10-05")
        with self.assertRaises(ValueError):
            CHECK.reconcile(self.previous, new)

    def test_mutated_sort_rejected(self):
        new = copy.deepcopy(self.following)
        new["pages"][0]["url"] = new["pages"][0]["url"].replace("publication_date:asc,display_name:asc", "publication_date:desc")
        with self.assertRaises(ValueError):
            CHECK.reconcile(self.previous, new)

    def test_duplicate_within_page_rejected(self):
        new = copy.deepcopy(self.following)
        new["pages"][0]["ordered_ids"][9] = new["pages"][0]["ordered_ids"][0]
        with self.assertRaises(ValueError):
            CHECK.reconcile(self.previous, new)

    def test_rate_limit_absence_rejected(self):
        new = copy.deepcopy(self.following)
        new["failed_requests"][0]["http_status"] = 200
        with self.assertRaises(ValueError):
            CHECK.reconcile(self.previous, new)

    def test_source_count_drift_cannot_be_hidden(self):
        new = copy.deepcopy(self.following)
        new["pages"][0]["reported_total"] = 9275
        with self.assertRaises(ValueError):
            CHECK.reconcile(self.previous, new)

    def test_boundary_id_mutation_changes_computed_overlap(self):
        new = copy.deepcopy(self.following)
        new["pages"][0]["ordered_ids"][0] = "https://openalex.org/W99999999999"
        actual = CHECK.reconcile(self.previous, new)
        self.assertEqual(len(actual["page43_vs_page44_shared_ids"]), 7)
        self.assertNotEqual(actual, CHECK.verify())


if __name__ == "__main__":
    unittest.main()
