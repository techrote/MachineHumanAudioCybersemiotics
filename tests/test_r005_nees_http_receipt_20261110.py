"""Immutable R005 original-PDF receipt and no-premature-admission controls.

This checks a historical GitHub Actions observation, not current source access,
source authenticity, legal permission, scientific eligibility, or human review.
"""
import copy
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research/sources/auditory/nees-2016-author-manuscript-2026-11-10/HTTP-RECEIPT.json"
EXPECTED_SHA = "012398a1a81c923c413454d7993e474e7389149b8e4199e2f8241cb35cbc3cfe"
EXPECTED_HEAD = "999b88e73212af3be7ade7b85ee1af519c6c27b9"


def verify_receipt(doc):
    assert doc["schema"] == "mhac-r005-nees2016-original-pdf-response/1"
    assert doc["source_head"] == EXPECTED_HEAD
    assert "/runs/42902552982" in doc["ci_run"]
    assert "/job/130132051244" in doc["ci_job"]
    assert doc["marker"] == "MHAC_R005_NEES2016="
    a = doc["actual_receipt"]
    assert a["result"] == "PDF_BYTES_RECEIVED"
    assert a["http_status"] == 200
    assert a["content_type"] == "application/pdf"
    assert a["bytes_received"] == 851943
    assert a["raw_sha256"] == EXPECTED_SHA
    assert re.fullmatch(r"[0-9a-f]{64}", a["raw_sha256"])
    assert a["pdf_header_version"].startswith("%PDF-")
    assert a["response_opened_utc"] == "2026-11-10T21:11:25.026+00:00"
    assert a["read_completed_utc"] == "2026-11-10T21:11:25.033+00:00"
    assert a["http_date"] == "Tue, 10 Nov 2026 21:11:25 GMT"
    assert a["source_doi"] == "10.1177/0018720816629279"
    assert a["source_id"] == "SRC-R006-NEES-2016-MEMORY@1"
    assert len(a["prior_2026_11_10_hits"]) == 3
    assert a["original_route"] == a["final_url"]
    assert "SAGE VoR" in a["requested_edition"]
    assert a["raw_bytes_retained"] is False
    assert a["rights_for_private_retention_verified"] is False
    assert a["redistribution_rights_verified"] is False
    assert a["source_manifestation_registered"] is False
    assert a["body_pages_or_audio_read_in_this_probe"] is False
    assert a["full_text_eligibility_decision"] is False
    assert a["study_or_sample_admitted"] is False
    assert a["independent_human_reviewer"] is False
    assert all(doc[field] is False for field in (
        "original_bytes_preserved", "publication_version_authenticated_from_bytes",
        "source_custody_accepted", "legal_private_retention_authorized",
        "full_text_eligibility_admitted"))
    assert doc["independent_studies_or_samples_admitted"] == 0
    assert "source-pinned" in doc["r006_next_action"] and "adjudication" in doc["r006_next_action"]
    assert "Re-acquire" in doc["integrator_next_action"]


class NeesPdfReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(PATH.read_text(encoding="utf-8"))

    def test_receipt_check(self):
        verify_receipt(self.doc)

    def test_reject_fabricated_retention(self):
        bad = copy.deepcopy(self.doc)
        bad["original_bytes_preserved"] = True
        with self.assertRaises(AssertionError):
            verify_receipt(bad)

    def test_reject_changed_original_sha(self):
        bad = copy.deepcopy(self.doc)
        bad["actual_receipt"]["raw_sha256"] = "f" * 64
        with self.assertRaises(AssertionError):
            verify_receipt(bad)

    def test_reject_human_second_reviewer(self):
        bad = copy.deepcopy(self.doc)
        bad["actual_receipt"]["independent_human_reviewer"] = True
        with self.assertRaises(AssertionError):
            verify_receipt(bad)

    def test_reject_study_sample_admission(self):
        bad = copy.deepcopy(self.doc)
        bad["independent_studies_or_samples_admitted"] = 1
        with self.assertRaises(AssertionError):
            verify_receipt(bad)

    def test_reject_claimed_authentic_version_of_record(self):
        bad = copy.deepcopy(self.doc)
        bad["publication_version_authenticated_from_bytes"] = True
        with self.assertRaises(AssertionError):
            verify_receipt(bad)


if __name__ == "__main__":
    unittest.main()
