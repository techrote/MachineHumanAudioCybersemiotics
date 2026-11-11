"""R005 EQ1 bounded *live* retrieval and offline original-response qualification.

The one-time CI acquisition prints HTTP evidence and base64 gzip response chunks.
After the genuine bytes are collected into R005-owned paths, offline checks replace
the live probe. No canonical hit, selection, source, or sample record is authored.
"""
import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import time
from datetime import datetime, timezone
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT / "research/searches/auditory/eq1-boundary-2026-11-10/OBSERVATIONS.json"
TARGET = ROOT / "research/searches/auditory/eq1-pages44-47-20261111"
RECEIPT = TARGET / "OBSERVATIONS.json"
PAGES = (44, 45, 46, 47)
FIELDS = "id,doi,display_name,publication_date,publication_year,type,language"
CUT_OFF = "2026-10-04"


def _urls():
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    assert previous["cutoff"] == CUT_OFF
    base = previous["pages"][0]["request_url"]
    assert "&page=42&sort=" in base
    assert "to_publication_date:2026-10-04" in base
    assert "title_and_abstract.search:" in base
    assert "&sort=publication_date:asc,display_name:asc" in base
    assert "&per_page=100" in base
    base = re.sub(r"(?<=&)select=[^&]*", "select=" + FIELDS, base)
    return {p:base.replace("&page=42&", "&page=" + str(p) + "&") for p in PAGES}


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _validate_original(page, raw, expected):
    assert _sha256(raw) == expected["raw_sha256"]
    assert len(raw) == expected["raw_bytes"]
    payload = json.loads(raw)
    assert payload["meta"]["page"] == page
    assert payload["meta"]["per_page"] == 100
    results = payload["results"]
    assert len(results) == expected["result_count"]
    assert len(results) <= 100
    assert all(item.get("id", "").startswith("https://openalex.org/W") for item in results)
    assert all(not item.get("publication_date") or item["publication_date"] <= CUT_OFF for item in results)
    assert [x["id"] for x in results] == expected["ordered_ids"]
    return payload


class Eq1PostBoundary(unittest.TestCase):
    def test_existing_frozen_query_reused_without_concept_changes(self):
        urls = _urls()
        self.assertEqual(list(urls), list(PAGES))
        for n, url in urls.items():
            self.assertIn("&page=" + str(n) + "&sort=", url)
            self.assertIn("to_publication_date:2026-10-04", url)
            self.assertIn("title_and_abstract.search:", url)
            self.assertIn("sort=publication_date:asc,display_name:asc", url)
            self.assertIn("&select=" + FIELDS + "&", url)

    def test_replay_retained_original_responses_when_available(self):
        if not RECEIPT.exists():
            self.skipTest("No original response acquisition accepted yet")
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["schema"], "mhac-r005-eq1-raw-pages/1")
        self.assertEqual(receipt["cutoff"], CUT_OFF)
        self.assertFalse(receipt["claim_complete_eq1"])
        self.assertEqual(receipt["admitted_studies"], 0)
        for entry in receipt["pages"]:
            page = entry["page"]
            self.assertIn(page, PAGES)
            raw_gz = (TARGET / entry["file"]).read_bytes()
            self.assertEqual(_sha256(raw_gz), entry["gzip_sha256"])
            self.assertEqual(len(raw_gz), entry["gzip_bytes"])
            self.assertEqual(_validate_original(page, gzip.decompress(raw_gz), entry)["meta"]["count"], entry["reported_total"])

    def test_negative_mutated_response_hash_rejected(self):
        sample = b'{"meta":{"page":44,"per_page":100,"count":1},"results":[]}'
        bogus = {"raw_sha256":_sha256(sample), "raw_bytes":len(sample), "result_count":0, "ordered_ids":[]}
        with self.assertRaises(AssertionError):
            _validate_original(44, sample + b" ", bogus)

    def test_one_time_live_acquisition_on_unqualified_pr_head(self):
        if RECEIPT.exists() or os.environ.get("GITHUB_ACTIONS") != "true":
            self.skipTest("Live read restricted to first PR CI; accepted pages replay offline")
        # No credentials, anonymous quota workaround, or publisher/database relabelling.
        urls = _urls()
        for index, (page, url) in enumerate(urls.items()):
            if index:
                time.sleep(1.2)  # provider's Boolean-query pacing
            started = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            try:
                req = Request(url, headers={
                    "User-Agent": "MHAC-R005-methodological-audit/1",
                    "Accept": "application/json",
                })
                with urlopen(req, timeout=50) as res:
                    status = res.status
                    header_date = res.headers.get("Date")
                    content_type = res.headers.get("Content-Type")
                    raw = res.read()
            except (HTTPError, URLError, TimeoutError) as exc:
                print("MHAC_R005_EQ1_UNAVAILABLE=" + json.dumps({
                    "page":page, "url":url, "request_started_utc":started,
                    "error_type":type(exc).__name__, "detail":str(exc)[:240],
                    "http_status":getattr(exc,"code",None)
                },separators=(",",":")),flush=True)
                self.skipTest("source request unavailable; no page invented")
            received = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            if status != 200:
                self.skipTest("HTTP non-200; no page invented")
            payload = json.loads(raw)
            meta = payload["meta"]
            items = payload["results"]
            blob = gzip.compress(raw,compresslevel=9,mtime=0)
            ids = [x["id"] for x in items]
            rec = {
                "page":page, "file":"page-" + str(page) + ".json.gz",
                "url":url,"request_started_utc":started,
                "received_utc":received,"http_status":status,
                "response_date":header_date,"content_type":content_type,
                "raw_sha256":_sha256(raw),"raw_bytes":len(raw),
                "gzip_sha256":_sha256(blob),"gzip_bytes":len(blob),
                "reported_total":meta["count"],"reported_page":meta["page"],
                "result_count":len(items),"distinct_ids":len(set(ids)),
                "ordered_ids":ids,"cutoff":CUT_OFF,
                "scope":"OpenAlex discovery metadata; not primary text or screened sources"
            }
            print("MHAC_R005_EQ1_OBSERVATION="+json.dumps(rec,separators=(",",":")),flush=True)
            b64=base64.b64encode(blob).decode("ascii")
            chunks=[b64[i:i+2800] for i in range(0,len(b64),2800)]
            for n,chunk in enumerate(chunks):
                print("MHAC_R005_EQ1_GZIP="+str(page)+":"+str(n)+"/"+str(len(chunks))+":"+chunk,flush=True)


if __name__ == "__main__":
    unittest.main()
