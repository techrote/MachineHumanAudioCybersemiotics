"""Integrity-only tests for the bounded R005 C9 construction-review navigation ledger.

No test is evidence of study eligibility, source fidelity or full-text reading.
"""
import copy
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/searches/auditory/c9-construction-review-2026-11-10/OBSERVATIONS.json"

def validate_ledger(a):
    assert a["schema_version"] == "mhac-r005-c9-targeted-navigation/1"
    assert a["project"] == "MHAC-R005" and a["issue"] == 5
    assert a["frozen_publication_cutoff"] == "2026-10-04"
    assert a["channel"] == "C9 backward citation chaining via C8 public web navigation"
    assert a["status"] == "bounded_partial"
    assert a["completed_searches_increment"] == 0
    assert a["completed_review_chains_increment"] == 0
    assert a["raw_html_or_pdf_bytes_retained"] is False
    assert a["response_hashes"] is None
    review = a["source_review"]
    assert review["doi"] == "10.3390/s22239135"
    assert review["reference_list_total_exported"] is False
    refs = a["references"]
    assert len(refs) == review["citation_selection_count"] == 5
    assert {x["review_reference_number"] for x in refs} == {33, 38, 39, 101, 102}
    assert len({x["candidate_key"] for x in refs}) == len(refs)
    assert len({x["doi"].lower() for x in refs}) == len(refs)
    for x in refs:
        assert x["candidate_key"] == f'C9-DANG2022-R{x["review_reference_number"]:03}'
        assert re.fullmatch(r'10\.[0-9]{4,9}/\S+', x["doi"])
        assert x["source_url"].startswith("https://")
        assert x["publication_year"] <= 2026
        assert x["eligibility_status"] == "not_screened"
        assert x["full_text_verified"] is False
        assert "read" in x["reading_extent"].lower() or "abstract" in x["reading_extent"].lower()
        assert x["screening_question"]
    assert a["deduplication"].startswith("Not performed")
    assert len(a["claims_not_supported"]) >= 5

class C9ConstructionReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_canonical(self):
        validate_ledger(self.ledger)

    def test_duplicate_reference_rejected(self):
        a = copy.deepcopy(self.ledger)
        a["references"][1]["review_reference_number"] = 33
        with self.assertRaises(AssertionError):
            validate_ledger(a)

    def test_false_full_text_claim_rejected(self):
        a = copy.deepcopy(self.ledger)
        a["references"][0]["full_text_verified"] = True
        with self.assertRaises(AssertionError):
            validate_ledger(a)

    def test_false_screening_acceptance_rejected(self):
        a = copy.deepcopy(self.ledger)
        a["references"][3]["eligibility_status"] = "include"
        with self.assertRaises(AssertionError):
            validate_ledger(a)

    def test_false_completed_search_rejected(self):
        a = copy.deepcopy(self.ledger)
        a["completed_searches_increment"] = 1
        with self.assertRaises(AssertionError):
            validate_ledger(a)

    def test_false_completed_review_chain_rejected(self):
        a = copy.deepcopy(self.ledger)
        a["completed_review_chains_increment"] = 1
        with self.assertRaises(AssertionError):
            validate_ledger(a)

    def test_false_hashed_artifacts_rejected(self):
        a = copy.deepcopy(self.ledger)
        a["raw_html_or_pdf_bytes_retained"] = True
        with self.assertRaises(AssertionError):
            validate_ledger(a)

    def test_cutoff_drift_rejected(self):
        a = copy.deepcopy(self.ledger)
        a["frozen_publication_cutoff"] = "2026-11-10"
        with self.assertRaises(AssertionError):
            validate_ledger(a)

    def test_duplicate_doi_rejected(self):
        a = copy.deepcopy(self.ledger)
        a["references"][1]["doi"] = a["references"][0]["doi"]
        with self.assertRaises(AssertionError):
            validate_ledger(a)


if __name__ == "__main__":
    unittest.main()
