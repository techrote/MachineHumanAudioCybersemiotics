"""One-time bounded R005 publisher-layout PDF acquisition probe (no PDF storage).

This test is intentionally temporary. It runs once in GitHub Actions on a
Draft PR, emits a receipt from direct HTTP observations, and is replaced by an
offline verified receipt and negative tests before any integration.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import unittest
import urllib.error
import urllib.request

URL = "https://www2.informatik.uni-hamburg.de/wtm/publications/2025/BBCKOAGSFW25/3706066.pdf"
DOI = "10.1145/3706066"
MAX_BYTES = 12_000_000


class PrimaryBeckerAcquisitionProbe(unittest.TestCase):
    @unittest.skipUnless(os.getenv("GITHUB_ACTIONS") == "true",
                         "one-time original HTTP acquisition only in source-probe CI")
    def test_exact_original_host_response(self):
        receipt = {
            "schema": "mhac-r005-public-pdf-direct-probe/1",
            "issue": 5,
            "r006_issue": 6,
            "publication_doi": DOI,
            "url": URL,
            "source_edition": "Hamburg author-hosted ACM THRI 14(2) Article 29 PDF",
            "frozen_cutoff": "2026-10-04",
            "method": "unauthenticated urllib GET, no redirects to restricted hosts, no saved PDF",
            "actor": "GitHub Actions Python urllib test (AI-authored)",
            "human_reader": False,
            "source_text_read_by_this_test": False,
            "study_eligibility_decision": None,
        }
        start = dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")
        receipt["request_utc"] = start
        request = urllib.request.Request(URL, headers={"User-Agent": "MHAC-R005-auditory-source-verification/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=18) as response:
                data = response.read(MAX_BYTES + 1)
                receipt.update({
                    "effective_url": response.url,
                    "http_status": response.status,
                    "http_date": response.headers.get("Date"),
                    "content_type": response.headers.get("Content-Type"),
                    "content_length_reported": response.headers.get("Content-Length"),
                    "bytes_received": len(data),
                    "exceeded_size_cap": len(data) > MAX_BYTES,
                    "pdf_magic_confirmed": data.startswith(b"%PDF-"),
                    "original_response_sha256": hashlib.sha256(data).hexdigest()
                        if len(data) <= MAX_BYTES else None,
                })
        except urllib.error.HTTPError as exc:
            receipt.update({
                "http_status": exc.code,
                "http_date": exc.headers.get("Date"),
                "content_type": exc.headers.get("Content-Type"),
                "error": "HTTP access refused; no original PDF bytes confirmed",
            })
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            receipt.update({"network_error_type": type(exc).__name__,
                            "original_pdf_acquired": False})
        receipt["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")
        receipt["original_pdf_acquired"] = bool(receipt.get("http_status") == 200
            and receipt.get("pdf_magic_confirmed")
            and not receipt.get("exceeded_size_cap"))
        print("MHAC_R005_BECKER_PDF_DIRECT_RECEIPT=" + json.dumps(receipt, sort_keys=True), flush=True)
        self.assertTrue(receipt["url"] == URL)
        self.assertIsNone(receipt["study_eligibility_decision"])
        self.assertFalse(receipt["human_reader"])


if __name__ == "__main__":
    unittest.main()
