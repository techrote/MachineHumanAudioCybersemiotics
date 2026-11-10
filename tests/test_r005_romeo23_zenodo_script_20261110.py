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

if __name__ == "__main__":
    unittest.main()
