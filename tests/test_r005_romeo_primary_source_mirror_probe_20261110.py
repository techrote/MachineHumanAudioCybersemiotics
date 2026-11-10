"""Bounded source-manifestation probe for R005/R006; not corpus eligibility.

The one-time live observation runs only in its R005 PR branch. Ordinary tests are
offline and may never be treated as an independently repeated original-file read.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import urllib.error
import urllib.request
import unittest

BRANCH = "mhac-r005/romeo-source-mirrors-20261110-1413"
ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "research/sources/auditory/romeo-original-mirror-2026-11-10/OBSERVATIONS.json"
PREFIX = "MHAC_R005_ROMEO_MIRROR_RECEIPT="
MAX_BYTES = 8 * 1024 * 1024
SOURCES = (
    ("romeo25_heriot_watt", "10.1145/3711938",
     "https://researchportal.hw.ac.uk/files/147098646/3711938.pdf"),
    ("romeo25_helsinki", "10.1145/3711938",
     "https://researchportal.helsinki.fi/files/798076089/3711938.pdf"),
    ("romeo23_ieee_original", "10.1109/RO-MAN57019.2023.10309631",
     "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10309631"),
)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def obtain(source_name: str, doi: str, url: str) -> dict:
    item = dict(source=source_name, doi=doi, request_url=url,
                requested_utc=now_utc(), access="public unauthenticated HTTPS",
                publication_body_qualified=False, screened=False,
                original_file_stored=False, human_assessor=False,
                audio_accessed=False)
    req = urllib.request.Request(url, headers={"User-Agent": "MHAC-R005-public-source-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=23) as response:
            item.update(http_status=response.status, response_date=response.headers.get("Date"),
                        content_type=response.headers.get("Content-Type"),
                        final_url=response.geturl(), response_opened_utc=now_utc())
            blob = response.read(MAX_BYTES + 1)
            item["received_utc"] = now_utc()
            item["received_bytes"] = len(blob)
            if len(blob) > MAX_BYTES:
                item["blocker"] = "file exceeds bounded 8 MiB probe limit"
                return item
            item["sha256"] = hashlib.sha256(blob).hexdigest()
            item["pdf_magic"] = blob.startswith(b"%PDF-")
            if not item["pdf_magic"]:
                item["blocker"] = "response is not a PDF source manifestation"
                return item
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(blob))
                item["pdf_pages"] = len(reader.pages)
                # Literal text scan, not complete critical reading or eligibility.
                first_text = reader.pages[0].extract_text() or ""
                second_text = reader.pages[1].extract_text() or "" if len(reader.pages) > 1 else ""
                item["first_two_pages_literal_doi_token"] = doi.lower() in (
                    first_text + second_text).lower()
                item["first_two_pages_literal_title_fragment"] = (
                    "voice and repair strategy" in (first_text + second_text).lower()
                    if source_name.startswith("romeo25") else
                    "putting robots in context" in (first_text + second_text).lower())
                item["parser"] = "pypdf; structural two-page token scan only"
                item["publication_body_qualified"] = (
                    bool(item["first_two_pages_literal_doi_token"]) and
                    bool(item["first_two_pages_literal_title_fragment"]))
                if not item["publication_body_qualified"]:
                    item["blocker"] = "source text identity tokens not both verified; hold"
            except (ImportError, ValueError, Exception) as ex:
                item["blocker"] = "PDF parser unavailable or failed: " + type(ex).__name__
            return item
    except urllib.error.HTTPError as ex:
        item.update(http_status=ex.code, final_url=ex.geturl(),
                    response_date=ex.headers.get("Date"), blocker="HTTP refusal or unavailable")
    except Exception as ex:
        item.update(blocker="transport: " + type(ex).__name__,
                    error_message=str(ex)[:200])
    item["completed_utc"] = now_utc()
    return item


class TestR005RomeoMirrors(unittest.TestCase):
    def test_source_identities_and_safety(self):
        self.assertEqual([x[1] for x in SOURCES],
                         ["10.1145/3711938", "10.1145/3711938",
                          "10.1109/RO-MAN57019.2023.10309631"])
        self.assertEqual(len({x[2] for x in SOURCES}), 3)
        self.assertTrue(all(x[2].startswith("https://") for x in SOURCES))
        self.assertFalse(any("zenodo.org" in x[2] for x in SOURCES))

    def test_saved_receipt_never_promotes_access_to_screening(self):
        if not RECEIPT.exists():
            self.skipTest("No accepted immutable source receipt yet")
        data = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(data["frozen_cutoff"], "2026-10-04")
        self.assertFalse(data["new_search_hits"])
        self.assertFalse(data["new_studies_or_samples"])
        self.assertFalse(data["human_screening_claimed"])
        self.assertEqual({x["source"] for x in data["attempts"]},
                         {x[0] for x in SOURCES})
        for item in data["attempts"]:
            self.assertFalse(item["screened"])
            self.assertFalse(item["human_assessor"])
            self.assertFalse(item["audio_accessed"])
            self.assertFalse(item["original_file_stored"])
            if item["publication_body_qualified"]:
                self.assertEqual(item["http_status"], 200)
                self.assertTrue(item["pdf_magic"])
                self.assertTrue(item["first_two_pages_literal_doi_token"])
                self.assertTrue(item["first_two_pages_literal_title_fragment"])
                self.assertEqual(len(item["sha256"]), 64)

    def test_once_per_branch_original_file_probe(self):
        if RECEIPT.exists():
            self.skipTest("Captured receipt is pinned; no live repeat in CI")
        if not (os.environ.get("GITHUB_ACTIONS") == "true" and
                os.environ.get("GITHUB_HEAD_REF") == BRANCH):
            self.skipTest("Original-file retrieval limited to explicit R005 PR head")
        payload = dict(schema="mhac-r005-romeo-mirror-probe/1", actor="GPT-6 source probe, AI/tool-mediated",
                       frozen_cutoff="2026-10-04", new_search_hits=False,
                       new_studies_or_samples=False, human_screening_claimed=False,
                       observation_date_utc=now_utc(), attempts=[])
        for name, doi, url in SOURCES:
            payload["attempts"].append(obtain(name, doi, url))
        print(PREFIX + json.dumps(payload, sort_keys=True), flush=True)
        self.assertEqual(len(payload["attempts"]), 3)


if __name__ == "__main__":
    unittest.main()
