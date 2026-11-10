"""Bounded public Romeo 2023 *supplement* byte/readability qualification, not the IEEE paper.

Run on the issue-scoped PR only. This test never commits copyrighted file bytes.
Green CI alone proves nothing about access: consume MHAC_R005_ROMEO23 lines.
"""
import datetime
import hashlib
import importlib
import io
import json
import os
import sys
import tempfile
import subprocess
import unittest
from urllib import request

URL = "https://zenodo.org/api/records/8042317/files/ROMAN2023_Ila_Marta.pdf/content"
MD5 = "7137b64efa2e75ab9aec951ca03449fe"
MAX_SIZE = 1024 * 1024
BRANCH = "mhac-r005/romeo23-zenodo-script-reading-20261110-1218"

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")

def inspect():
    row = {
        "source": "Romeo and Torre 2023 supplementary script v1",
        "publication_doi": "10.1109/RO-MAN57019.2023.10309631",
        "supplement_version_doi": "10.5281/zenodo.8042317",
        "source_kind": "supplementary utterance-script PDF, NOT original IEEE report",
        "requested_url": URL,
        "expected_public_md5": MD5,
        "started_utc": now(),
        "access": "unauthenticated public HTTPS; no paywall bypass",
    }
    try:
        req = request.Request(URL, headers={
            "User-Agent": "MHAC-R005-script-qualification/2026-11-10",
            "Accept-Encoding": "identity"})
        with request.urlopen(req, timeout=25) as response:
            row.update({
                "status": response.status, "final_url": response.url,
                "http_date": response.headers.get("Date"),
                "content_type": response.headers.get("Content-Type"),
                "response_opened_utc": now(),
            })
            raw = response.read(MAX_SIZE + 1)
            row["read_completed_utc"] = now()
        if len(raw) > MAX_SIZE:
            row["result"] = "BLOCKED_OVERSIZE"; return row
        row.update({
            "bytes": len(raw),
            "md5": hashlib.md5(raw, usedforsecurity=False).hexdigest(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "pdf_magic": raw.startswith(b"%PDF-"),
        })
        if row["md5"] != MD5 or not row["pdf_magic"]:
            row["result"] = "BLOCKED_CHECKSUM_OR_TYPE"; return row
        try:
            from pypdf import PdfReader, __version__ as parser_version
        except ImportError:
            vendor = tempfile.mkdtemp(prefix="r005_pypdf_")
            proc = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet",
                 "--disable-pip-version-check", "--target", vendor, "pypdf==6.1.1"],
                capture_output=True, timeout=45)
            row["parser_install_code"] = proc.returncode
            if proc.returncode != 0:
                row["result"] = "RECEIVED_BYTES_PARSER_UNAVAILABLE"; return row
            sys.path.insert(0, vendor)
            importlib.invalidate_caches()
            from pypdf import PdfReader, __version__ as parser_version
        reader = PdfReader(io.BytesIO(raw), strict=False)
        row["parser"] = "pypdf " + parser_version
        row["pdf_pages"] = len(reader.pages)
        pages = []
        for i, page in enumerate(reader.pages):
            s = page.extract_text() or ""
            normalized = s.casefold()
            # Structural presence only, not redistributed original scripts.
            pages.append({
                "pdf_page_index_zero_based": i,
                "pdf_page_number_one_based": i + 1,
                "extractable_text_characters": len(s),
                "has_os1_literal": "os1" in normalized,
                "has_os2_literal": "os2" in normalized,
                "has_empathy_term": "empath" in normalized,
                "has_robot_term": "robot" in normalized,
                "has_voice_term": "voice" in normalized,
            })
        row["page_text_inventory"] = pages
        row["result"] = "QUALIFIED_SUPPLEMENT_BYTES_AND_EXTRACTABLE_TEXT"
        row["explicit_non_claims"] = [
            "original RO-MAN 2023 IEEE six-page paper not accessed",
            "audio/video stimuli not played or measured",
            "study/sample identity and overlap with 2025 not adjudicated",
            "PDF page structure is not human primary-reading review",
        ]
    except Exception as exc:
        row["result"] = "BLOCKED: " + type(exc).__name__ + ": " + str(exc)[:200]
        row["read_completed_utc"] = now()
    return row

class TestR005Romeo2023ZenodoSupplement(unittest.TestCase):
    def test_offline_provenance_contract(self):
        self.assertEqual(MD5, "7137b64efa2e75ab9aec951ca03449fe")
        self.assertEqual(URL, "https://zenodo.org/api/records/8042317/files/ROMAN2023_Ila_Marta.pdf/content")
        self.assertNotIn("2025", URL)
        self.assertNotIn("RO-MAN57019.2023.10309631", URL)

    def test_ephemeral_original_script_receipt(self):
        if not (os.environ.get("GITHUB_ACTIONS") == "true" and
                os.environ.get("GITHUB_HEAD_REF") == BRANCH):
            self.skipTest("one bounded run on R005 Draft PR only; not a persistent live-network suite")
        row = inspect()
        print("MHAC_R005_ROMEO23 " + json.dumps(row, sort_keys=True), flush=True)
        # Access failures are scientific blockers, not a reason to misreport a
        # structurally green test as original-file acquisition.
        self.assertEqual(row["source_kind"], "supplementary utterance-script PDF, NOT original IEEE report")

# Offline fail-closed contract for the *receipt evidence*, never corpus eligibility.
def validate_saved_receipt(data):
    s, r, q, nc = (data[k] for k in ("source", "receipt", "parser", "not_claimed"))
    assert data["frozen_cutoff"] == "2026-10-04"
    assert s["publication_doi"].casefold() == "10.1109/ro-man57019.2023.10309631"
    assert s["supplement_version_doi"] == "10.5281/zenodo.8042317"
    assert s["supplement_concept_doi"] != s["supplement_version_doi"]
    assert s["publication_full_text_read"] is False
    assert r["request_url"] == URL
    assert r["http_status"] == 200 and r["pdf_magic"] is True
    assert r["advertised_md5"] == MD5 and r["received_md5"] == MD5
    assert r["md5_matches_public_record"] is True
    assert r["byte_count"] == 103320
    assert r["received_sha256"] == "53be4375261a22965392f25151ba004392418727a378df42a253d4c22e969aea"
    assert r["source_bytes_deposited_to_repo"] is False
    assert r["source_text_redistributed"] is False
    assert q["pdf_page_count"] == len(q["pages"]) == 4
    assert [x["page_index"] for x in q["pages"]] == [0, 1, 2, 3]
    assert [x["characters_extracted"] for x in q["pages"]] == [686, 1962, 1687, 2085]
    assert "NOT human" in q["text_extraction_scope"]
    for k in ("complete_ieee_paper_read", "audio_video_playback", "study_or_sample_independence",
              "human_screen_or_review", "frozen_protocol_eligibility",
              "source_manifestation_accepted", "new_database_search_occurrences"):
        assert nc[k] in (False, 0), k
    return True

class TestR005OriginalScriptReceiptOffline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pathlib import Path
        cls.data = json.loads((Path(__file__).resolve().parents[1] /
          "research/sources/auditory/r006-romeo23-zenodo-script-reading-2026-11-10/OBSERVATIONS.json").read_text(encoding="utf-8"))

    def test_saved_receipt(self):
        self.assertTrue(validate_saved_receipt(self.data))

    def _reject(self, path, val):
        import copy
        d = copy.deepcopy(self.data)
        obj = d
        for k in path[:-1]:
            obj = obj[k]
        obj[path[-1]] = val
        with self.assertRaises(AssertionError):
            validate_saved_receipt(d)

    def test_reject_concept_doi_as_version(self):
        self._reject(("source", "supplement_version_doi"), "10.5281/zenodo.8042316")

    def test_reject_parent_publication_doi_swap(self):
        self._reject(("source", "publication_doi"), "10.1145/3711938")

    def test_reject_parent_report_claimed_read(self):
        self._reject(("source", "publication_full_text_read"), True)

    def test_reject_fabricated_pdf_hash(self):
        self._reject(("receipt", "received_sha256"), "0" * 64)

    def test_reject_advertised_hash_as_verified_hash(self):
        self._reject(("receipt", "received_md5"), "0" * 32)

    def test_reject_missing_pdf_magic(self):
        self._reject(("receipt", "pdf_magic"), False)

    def test_reject_wrong_pdf_page_count(self):
        self._reject(("parser", "pdf_page_count"), 6)

    def test_reject_page_offset_drift(self):
        self._reject(("parser", "pages", 0, "page_index"), 1)

    def test_reject_fabricated_human_reading(self):
        self._reject(("not_claimed", "human_screen_or_review"), True)

    def test_reject_study_sample_promotion(self):
        self._reject(("not_claimed", "study_or_sample_independence"), True)

    def test_reject_corpus_eligibility_promotion(self):
        self._reject(("not_claimed", "frozen_protocol_eligibility"), True)

    def test_reject_reported_audio_as_heard(self):
        self._reject(("not_claimed", "audio_video_playback"), True)


if __name__ == "__main__":
    unittest.main()
