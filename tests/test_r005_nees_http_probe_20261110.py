"""Bounded R005 Nees 2016 author-hosted PDF acquisition probe and negative controls.

The one-shot GitHub Actions probe reads public bytes without retaining them.
A successful probe is NOT an authenticated source manifestation, legal retention
grant, performed R006 reading, empirical eligibility decision, or human review.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import unittest

BRANCH = "mhac-r005/nees2016-pdf-acquisition-20261110"
URL = (
    "https://static1.squarespace.com/static/51bb699de4b0820e6e77849b/"
    "t/56d63bd2a3360c6369802fc3/1456880594996/"
    "Nees+et+al+Human+Factors+2016+author+preprint.pdf"
)
DOI = "10.1177/0018720816629279"
SOURCE = "SRC-R006-NEES-2016-MEMORY@1"
HITS = (
    "HIT-R005R-C1LOAD-EQ1-04051@1",
    "HIT-R005R-C1RECOVERY-EQ1-00329@1",
    "HIT-R005R-C1RECOVERY-EQ6-00308@1",
)
MAX_BYTES = 16_000_000
MARKER = "MHAC_R005_NEES2016="


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def classify_pdf(data: bytes, *, truncated: bool = False) -> dict:
    """Structural byte observations only, NOT proof of article identity/edition."""
    result = {"bytes_received": len(data), "raw_sha256": hashlib.sha256(data).hexdigest()}
    if truncated or len(data) > MAX_BYTES:
        result["result"] = "BLOCKED_OVERSIZE"
    elif not data.startswith(b"%PDF-"):
        result["result"] = "BLOCKED_NOT_PDF"
    elif b"%%EOF" not in data[-4096:]:
        result["result"] = "BLOCKED_INCOMPLETE_PDF"
    else:
        result["result"] = "PDF_BYTES_RECEIVED"
        result["pdf_header_version"] = data[:8].decode("ascii", errors="replace")
    return result


def direct_probe() -> dict:
    row = {
        "started_utc": utc(),
        "source_id": SOURCE,
        "source_doi": DOI,
        "original_route": URL,
        "prior_2026_11_10_hits": list(HITS),
        "requested_edition": "29-page author-hosted preprint/accepted-labelled manuscript, NOT SAGE VoR",
        "access_basis": "corresponding-author publicly linked PDF; unauthenticated GET",
        "actor_type": "AI-operated GitHub Actions technical probe",
        "raw_bytes_retained": False,
        "rights_for_private_retention_verified": False,
        "redistribution_rights_verified": False,
        "source_manifestation_registered": False,
        "body_pages_or_audio_read_in_this_probe": False,
        "full_text_eligibility_decision": False,
        "study_or_sample_admitted": False,
        "independent_human_reviewer": False,
        "frozen_publication_cutoff": "2026-10-04",
    }
    req = Request(URL, headers={
        "User-Agent": "MHAC-R005-source-integrity/2026-11-10",
        "Accept": "application/pdf",
        "Accept-Encoding": "identity",
    })
    try:
        with urlopen(req, timeout=30) as response:
            row.update({
                "http_status": response.status,
                "final_url": response.geturl(),
                "http_date": response.headers.get("Date"),
                "content_type": response.headers.get("Content-Type"),
                "response_opened_utc": utc(),
            })
            data = response.read(MAX_BYTES + 1)
            row["read_completed_utc"] = utc()
        row.update(classify_pdf(data, truncated=len(data) > MAX_BYTES))
        # Keep original bytes in memory only while verifying their structure.
        del data
    except HTTPError as exc:
        row.update({"result": "BLOCKED_HTTP", "http_status": exc.code,
                    "response_opened_utc": utc(), "http_date": exc.headers.get("Date"),
                    "read_completed_utc": utc()})
    except (URLError, TimeoutError, OSError) as exc:
        row.update({"result": "BLOCKED_TRANSPORT_" + type(exc).__name__,
                    "error_excerpt": str(exc)[:150], "read_completed_utc": utc()})
    return row


class TestNeesOriginalPdfAcquisition(unittest.TestCase):
    def test_exact_identifier_and_discovery_pins(self):
        self.assertEqual(DOI, "10.1177/0018720816629279")
        self.assertEqual(SOURCE, "SRC-R006-NEES-2016-MEMORY@1")
        self.assertEqual(len(HITS), len(set(HITS)))
        self.assertTrue(URL.endswith("2016+author+preprint.pdf"))

    def test_synthetic_positive_is_not_an_actual_source(self):
        fixture = b"%PDF-1.7\n%synthetic test only\n%%EOF\n"
        row = classify_pdf(fixture)
        self.assertEqual(row["result"], "PDF_BYTES_RECEIVED")
        self.assertEqual(row["bytes_received"], len(fixture))

    def test_reject_non_pdf_and_error_body(self):
        self.assertEqual(classify_pdf(b"<html>403</html>")["result"], "BLOCKED_NOT_PDF")

    def test_reject_partial_pdf(self):
        self.assertEqual(classify_pdf(b"%PDF-1.7\ncontent")["result"], "BLOCKED_INCOMPLETE_PDF")

    def test_reject_oversize(self):
        self.assertEqual(classify_pdf(b"%PDF-1.7\n%%EOF\n", truncated=True)["result"],
                         "BLOCKED_OVERSIZE")

    def test_one_scoped_live_public_pdf_probe(self):
        # PR head only; no recurring mainline requests or network in local tests.
        if not (os.getenv("GITHUB_ACTIONS") == "true"
                and os.getenv("GITHUB_HEAD_REF") == BRANCH):
            self.skipTest("scoped one-branch R005 original PDF probe only")
        row = direct_probe()
        print(MARKER + json.dumps(row, sort_keys=True), flush=True)
        self.assertIs(row["independent_human_reviewer"], False)
        self.assertIs(row["full_text_eligibility_decision"], False)
        self.assertIs(row["study_or_sample_admitted"], False)
        self.assertIs(row["raw_bytes_retained"], False)


if __name__ == "__main__":
    unittest.main()
