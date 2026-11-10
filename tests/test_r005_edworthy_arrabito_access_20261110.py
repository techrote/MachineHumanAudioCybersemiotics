"""Negative integrity controls for the R005 original-article access boundary (no science gate)."""
import copy
import json
import unittest
from pathlib import Path

ARTIFACT = Path(__file__).resolve().parents[1] / "research/sources/auditory/r006-original-access-boundary-2026-11-10/OBSERVATIONS.json"

def require_limited_scope(d):
    assert d["issue"] == 5 and d["refs_issue"] == 6
    assert d["frozen_publication_cutoff"] == "2026-10-04"
    assert d["reviewer"]["kind"] == "agent"
    assert d["reviewer"]["actual_human_second_assessor"] is False
    assert all(v == 0 for v in d["canonical_delta"].values())
    assert len(d["cases"]) == 2
    for c in d["cases"]:
        assert c["existing_screening_stage"] == "title_abstract"
        assert c["existing_screening_decision"] == "include_to_fulltext_only"
        assert c["source_rev"] == 1 and c["original_search_hit_ids"]
        assert c["doi"] and c["pmid"]
        assert c["publisher_or_author_full_text_accessed"] is False
        assert c["original_binary_retained"] is False
        assert c["original_binary_sha256"] is None
        assert c["exact_http_acquisition_time"] is None
        assert c["original_audio_accessed"] is False
        assert c["article_redistribution_permission_verified"] is False
        assert all(o["raw_response_sha256"] is None for o in c["observed"])
    assert d["citation_chain_observation"]["original_html_sha256"] is None
    assert "no new canonical HIT" in d["citation_chain_observation"]["result_status"]

class AccessBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_bounded_ledger(self):
        require_limited_scope(self.ledger)

    def test_existing_ids_and_dois(self):
        cases = {c["source_id"]: c for c in self.ledger["cases"]}
        self.assertEqual(set(cases), {"SRC-R006-EDWORTHY-2014-LEARNING", "SRC-R006-F-ARRABITO-URGENCY"})
        self.assertEqual(cases["SRC-R006-EDWORTHY-2014-LEARNING"]["doi"], "10.1016/j.apergo.2013.10.003")
        self.assertEqual(cases["SRC-R006-F-ARRABITO-URGENCY"]["doi"], "10.1080/0014013042000193282")

    def test_no_false_fulltext(self):
        altered = copy.deepcopy(self.ledger)
        altered["cases"][0]["publisher_or_author_full_text_accessed"] = True
        with self.assertRaises(AssertionError):
            require_limited_scope(altered)

    def test_no_fabricated_original_binary_digest(self):
        altered = copy.deepcopy(self.ledger)
        altered["cases"][1]["original_binary_sha256"] = "a" * 64
        with self.assertRaises(AssertionError):
            require_limited_scope(altered)

    def test_no_unobserved_http_timestamp(self):
        altered = copy.deepcopy(self.ledger)
        altered["cases"][0]["exact_http_acquisition_time"] = "2026-11-10T19:07:25Z"
        with self.assertRaises(AssertionError):
            require_limited_scope(altered)

    def test_no_human_reviewer(self):
        altered = copy.deepcopy(self.ledger)
        altered["reviewer"]["actual_human_second_assessor"] = True
        with self.assertRaises(AssertionError):
            require_limited_scope(altered)

    def test_no_sample_or_hit_inflation(self):
        altered = copy.deepcopy(self.ledger)
        altered["canonical_delta"]["independent_samples"] = 5
        with self.assertRaises(AssertionError):
            require_limited_scope(altered)
        altered = copy.deepcopy(self.ledger)
        altered["canonical_delta"]["search_hits"] = 1
        with self.assertRaises(AssertionError):
            require_limited_scope(altered)

    def test_c9_correspondence_not_canonical_hit(self):
        altered = copy.deepcopy(self.ledger)
        altered["citation_chain_observation"]["result_status"] = "new canonical HIT created"
        with self.assertRaises(AssertionError):
            require_limited_scope(altered)

if __name__ == "__main__":
    unittest.main()
