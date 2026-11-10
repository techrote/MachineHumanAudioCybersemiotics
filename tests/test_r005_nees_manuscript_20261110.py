"""Structural anti-promotion controls for R005's Nees author-manuscript source route.

No live network, source authentication, human screening or empirical verification.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
OBS = ROOT / "research/sources/auditory/nees-2016-author-manuscript-2026-11-10/OBSERVATIONS.json"

EXPECTED_HITS = {
    "HIT-R005R-C1LOAD-EQ1-04051@1",
    "HIT-R005R-C1RECOVERY-EQ1-00329@1",
    "HIT-R005R-C1RECOVERY-EQ6-00308@1",
}


def validate_record(rec: dict) -> None:
    assert rec["schema_version"] == "mhac-r005-primary-manuscript-source-navigation/1"
    assert rec["issue"] == 5 and rec["downstream_issue"] == 6
    assert rec["frozen_publication_cutoff"] == "2026-10-04"
    s = rec["source"]
    assert s["doi"] == "10.1177/0018720816629279"
    assert "preprint" in s["edition_label"].lower()
    assert "not established identical" in s["edition_label"].lower()
    assert s["pdf_pages_reported_by_web_reader"] == 29
    assert s["author_manuscript_pdf_url"].startswith("https://static1.squarespace.com/")
    assert s["vor_url"] != s["author_manuscript_pdf_url"]
    assert s["original_bytes_retained"] is False
    assert s["original_response_headers_retained"] is False
    assert s["original_sha256"] is None and s["raw_pdf_archive_ref"] is None
    assert s["licensed_redistribution"] is False
    assert "not verified" in s["rights"].lower()
    assert s["visual_page_indices_checked"] == [9, 10, 13, 14]
    assert "No full 29-page" in s["source_reading"]
    assert rec["observed_time"]["precision"].startswith("Clock reading obtained after")
    assert len(rec["source"]["text_section_locators"]) >= 4
    assert rec["observer"]["human_second_reviewer"] is False
    assert rec["canonical_source"] == "SRC-R006-NEES-2016-MEMORY@1"
    assert rec["canonical_ta"] == "SCR-R006-NEES-2016-MEMORY-TA@1"
    assert set(rec["original_search_provenance"]) == EXPECTED_HITS
    a = rec["verified_excerpts_as_author_reports"]
    assert a["participants_recruited"] == 90
    assert a["participants_excluded_from_analyses"] == 5
    assert a["participants_analyzed"] == 85
    assert a["participants_recruited"] - a["participants_excluded_from_analyses"] == a["participants_analyzed"]
    assert sum(a["per_condition_analyzed"].values()) == a["participants_analyzed"]
    assert "not three independent samples" in a["protocol_note"].lower()
    assert "R006 alone" in rec["r006_decision_authority"]
    assert all(v is False for v in rec["status"].values())
    assert "R004/Integration" in rec["further_action"]
    assert "R006" in rec["further_action"]


class TestNeesSourceRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(OBS.read_text(encoding="utf-8"))

    def test_source_record_invariants(self) -> None:
        validate_record(self.record)

    def test_forbid_automatic_full_text_inclusion(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["status"]["full_text_included"] = True
        with self.assertRaises(AssertionError):
            validate_record(bad)

    def test_forbid_independent_sample_from_three_conditions(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["status"]["independent_sample_admitted"] = True
        with self.assertRaises(AssertionError):
            validate_record(bad)

    def test_forbid_human_review_claim(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["observer"]["human_second_reviewer"] = True
        with self.assertRaises(AssertionError):
            validate_record(bad)

    def test_forbid_unretained_binary_fabricated_hash(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["source"]["original_sha256"] = "a" * 64
        with self.assertRaises(AssertionError):
            validate_record(bad)

    def test_forbid_version_of_record_promotion(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["source"]["edition_label"] = "SAGE Version of Record"
        with self.assertRaises(AssertionError):
            validate_record(bad)

    def test_forbid_hidden_hit_identity_change(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["original_search_provenance"].append("HIT-NEW-FICTIONAL@1")
        with self.assertRaises(AssertionError):
            validate_record(bad)

    def test_forbid_claimed_redistribution_licence(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["source"]["licensed_redistribution"] = True
        with self.assertRaises(AssertionError):
            validate_record(bad)

    def test_forbid_arm_count_as_total_sample(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["verified_excerpts_as_author_reports"]["per_condition_analyzed"]["speech"] = 85
        with self.assertRaises(AssertionError):
            validate_record(bad)


if __name__ == "__main__":
    unittest.main()
