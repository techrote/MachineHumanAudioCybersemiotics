"""Offline regression guard for an actual, unretained original-JATS source receipt.

The received 2026-11-11 full-text bytes and Method/Results text hashes are
historical observations from the linked Actions job, not synthetic measurements.
No original paper bytes or participant results are stored here. Refs #5/#6.
"""
from __future__ import annotations

import copy
from datetime import datetime
import json
from pathlib import Path
import unittest

RECORD = (Path(__file__).resolve().parents[1] /
          "research/sources/auditory/stevens2009-section-digest-20261111/OBSERVATIONS.json")
DOI = "10.2478/v10053-008-0064-6"
XML_SHA = "1390d7a4def94ad6b0926a5f1ae2608999f31713fb3ee5dad20b9e3fcc52658b"
METHOD_SHA = "0fa7e539fd127505e32d4fb2456be002180fc7813309fbd0258b59a14dbc8f8b"
RESULTS_SHA = "b56553a3a98a167b678c665380320f661b63b458d913f733879d3ba996139038"


def assert_record(row):
    assert row["schema"] == "mhac-r005-stevens2009-source-section-boundary/1"
    assert row["issue"] == 5 and row["downstream_issue"] == 6
    assert row["recorded_from_actual_actions_marker"] is True
    assert row["observed_source_head"] == "73acb54495b1b6e3cf993ee27ddd1596984501a2"
    assert row["source_evidence_ci_run"].endswith("/42965672855")
    assert row["source_evidence_ci_job"].endswith("/130342294257")
    assert row["historic_and_new_byte_hash_match"] is True
    assert row["historical_2026_11_10_same_bytes_sha256"] == XML_SHA
    assert row["original_source_bytes_saved"] is False
    assert row["original_source_bytes_committed"] is False
    assert row["r006_eligibility_adjudicated"] is False
    assert row["r006_canonical_identity_changed"] is False
    assert row["human_assessor"] is False
    assert row["new_search_occurrences"] == 0
    assert row["accepted_empirical_publications_studies_experiments_samples_delta"] == [0, 0, 0, 0]

    receipt = row["actual_receipt"]
    assert receipt["status"] == "ORIGINAL_METHOD_RESULTS_SECTION_FINGERPRINTS_OBSERVED"
    assert receipt["http_status"] == 200
    assert receipt["content_type"].startswith("application/xml")
    assert receipt["response_url"] == receipt["request_url"]
    assert receipt["request_url"] == "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2865004/fullTextXML"
    assert receipt["source_id"] == "SRC-R006-E-STEVENS-INFORMATIVE@1"
    assert receipt["representative_hit_id"] == "HIT-R005R-C1LOAD-EQ1-02138@2"
    assert receipt["frozen_publication_cutoff"] == "2026-10-04"
    assert receipt["doi_in_article"] == DOI
    assert receipt["original_response_bytes"] == 74338
    assert receipt["original_response_sha256"] == XML_SHA
    assert receipt["bytes_retained"] is False
    assert receipt["source_manifestation_registered"] is False
    assert receipt["numeric_outcome_extraction"] is False
    assert receipt["human_or_second_assessor"] is False
    assert receipt["rights_or_retention_approved"] is False
    assert receipt["publication_study_experiment_sample_admissions"] == 0
    assert receipt["does_not_change_r006"] is True

    start, opened, ended = (
        datetime.fromisoformat(receipt[k]) for k in
        ("started_utc", "opened_utc", "finished_utc"))
    assert start.tzinfo and opened.tzinfo and ended.tzinfo
    assert start <= opened <= ended
    assert receipt["http_date"] == "Wed, 11 Nov 2026 05:26:06 GMT"

    sections = receipt["method_results"]
    assert [(s["heading"], s["original_xpath"], s["normalized_text_sha256"])
            for s in sections] == [
                ("Method", "/article/body/sec[2]", METHOD_SHA),
                ("Results", "/article/body/sec[3]", RESULTS_SHA)]
    assert sections[0]["normalized_text_characters"] == 7919
    assert sections[1]["normalized_text_characters"] == 4673
    assert sections[0]["paragraph_elements"] == 11
    assert sections[1]["paragraph_elements"] == 8
    assert {"Participants", "Stimuli", "Procedure"} <= set(
        sections[0]["nested_section_headings"])
    assert {"Learning Phase", "Test Phase"} <= set(
        sections[1]["nested_section_headings"])
    assert all(s["reading"].startswith("machine inventory") for s in sections)


class ReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_actual_original_receipt_is_exactly_pinned(self):
        assert_record(self.row)

    def test_laundered_reading_or_rights_does_not_pass(self):
        for field in ("original_source_bytes_saved", "original_source_bytes_committed",
                      "r006_eligibility_adjudicated", "human_assessor"):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.row)
                changed[field] = True
                with self.assertRaises(AssertionError):
                    assert_record(changed)

    def test_changed_article_or_original_source_hash_is_rejected(self):
        for field, val in (("doi_in_article", "10.0000/wrong"),
                           ("original_response_sha256", "0" * 64),
                           ("original_response_bytes", 0)):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.row)
                changed["actual_receipt"][field] = val
                with self.assertRaises(AssertionError):
                    assert_record(changed)

    def test_section_or_locator_tampering_is_rejected(self):
        for field, val in (("original_xpath", "/article/body/sec[1]"),
                           ("normalized_text_sha256", "0" * 64),
                           ("normalized_text_characters", 0)):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.row)
                changed["actual_receipt"]["method_results"][0][field] = val
                with self.assertRaises(AssertionError):
                    assert_record(changed)

    def test_fake_admission_and_changed_cutoff_rejected(self):
        for field, val in (("publication_study_experiment_sample_admissions", 1),
                           ("frozen_publication_cutoff", "2026-11-11"),
                           ("source_manifestation_registered", True)):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.row)
                changed["actual_receipt"][field] = val
                with self.assertRaises(AssertionError):
                    assert_record(changed)


if __name__ == "__main__":
    unittest.main()
