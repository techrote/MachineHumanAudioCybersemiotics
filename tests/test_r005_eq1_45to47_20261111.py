"""One-shot R005 OpenAlex EQ1 page 45-47 source-provenance probe.

Live network is permitted only on the named PR branch before its immutable
attempt marker exists. The run logs exact response bytes as deterministic
gzip/base64 chunks for later reconstruction into an R005-owned archive.
This never registers search hits, papers, experiments, or samples.
"""
import base64
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PR_BRANCH = "mhac-r005/eq1-45to47-20261111-0708"
BASE_RECORD = ROOT / "research/searches/auditory/eq1-single-snapshot-20261111/OBSERVATIONS.json"
OUT_DIR = ROOT / "research/searches/auditory/eq1-45to47-20261111-0708"
STOP = OUT_DIR / "ATTEMPTED.json"
CUTOFF = "2026-10-04"
FIELDS = "id,doi,display_name,publication_date,publication_year,type,language"
PAGES = (45, 46, 47)


def source_urls():
    accepted = json.loads(BASE_RECORD.read_text(encoding="utf-8"))
    assert accepted["frozen_cutoff"] == CUTOFF
    item = next(p for p in accepted["pages"] if p["page"] == 45)
    url = item["url"]
    parts = urlsplit(url)
    query = parse_qs(parts.query, keep_blank_values=True)
    assert parts.scheme == "https" and parts.netloc == "api.openalex.org"
    assert set(query) == {"filter", "per_page", "select", "page", "sort"}
    assert query["filter"][0].startswith("title_and_abstract.search:")
    assert query["filter"][0].endswith(",to_publication_date:" + CUTOFF)
    assert query["per_page"] == ["100"]
    assert query["select"] == [FIELDS]
    assert query["page"] == ["45"]
    assert query["sort"] == ["publication_date:asc,display_name:asc"]
    return {page: url.replace("&page=45&", "&page=" + str(page) + "&")
            for page in PAGES}


def assess(raw, page):
    assert isinstance(raw, bytes) and len(raw) <= 2_000_000
    doc = json.loads(raw)
    meta = doc["meta"]
    assert meta["page"] == page and meta["per_page"] == 100
    assert isinstance(meta["count"], int) and meta["count"] > 0
    rows = doc["results"]
    assert isinstance(rows, list) and len(rows) == 100
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids))
    assert all(isinstance(i, str) and i.startswith("https://openalex.org/W") for i in ids)
    assert all((row.get("publication_date") is None or row["publication_date"] <= CUTOFF)
               for row in rows)
    return meta["count"], ids


def boundary(records):
    assert len(records) >= 2
    assert [r["page"] for r in records] == list(range(records[0]["page"], records[-1]["page"] + 1))
    count_stable = len({r["count"] for r in records}) == 1
    overlaps = []
    for left, right in zip(records, records[1:]):
        common = sorted(set(left["ids"]) & set(right["ids"]))
        if common:
            overlaps.append({"between": [left["page"], right["page"]], "work_ids": common})
    return {"pages": [r["page"] for r in records],
            "same_invocation_provider_count_stable": count_stable,
            "adjacent_overlaps": overlaps,
            "complete_eq1_coverage": False,
            "admitted_publications_studies_experiments_samples": [0, 0, 0, 0]}


class Eq1Pages45To47(unittest.TestCase):
    def test_exact_source_query_only_changes_page(self):
        urls = source_urls()
        self.assertEqual(sorted(urls), list(PAGES))
        for page in PAGES:
            self.assertIn("&page=" + str(page) + "&", urls[page])
        self.assertEqual(urls[46], urls[45].replace("&page=45&", "&page=46&"))
        self.assertEqual(urls[47], urls[45].replace("&page=45&", "&page=47&"))

    def test_changed_date_and_duplicate_work_ids_are_rejected(self):
        p = {"meta": {"page": 45, "per_page": 100, "count": 9280},
             "results": [{"id": "https://openalex.org/W1", "publication_date": "2026-10-05"}] * 100}
        with self.assertRaises(AssertionError):
            assess(json.dumps(p).encode(), 45)
        p["results"] = [{"id": "https://openalex.org/W" + str(i),
                         "publication_date": "2026-10-05"} for i in range(100)]
        with self.assertRaises(AssertionError):
            assess(json.dumps(p).encode(), 45)
        p["results"][0]["publication_date"] = "2026-10-04"
        with self.assertRaises(AssertionError):
            assess(json.dumps(p).encode(), 45)
        with self.assertRaises(AssertionError):
            assess(json.dumps(p).encode(), 46)

    def test_synthetic_adjacent_overlap_and_count_drift_not_suppressed(self):
        a = {"page": 45, "count": 9280, "ids": ["https://openalex.org/W1"]}
        b = {"page": 46, "count": 9281, "ids": ["https://openalex.org/W1"]}
        out = boundary([a, b])
        self.assertFalse(out["same_invocation_provider_count_stable"])
        self.assertEqual(out["adjacent_overlaps"][0]["work_ids"], a["ids"])
        self.assertFalse(out["complete_eq1_coverage"])
        self.assertEqual(out["admitted_publications_studies_experiments_samples"], [0, 0, 0, 0])

    def test_exact_one_shot_public_http_retrieval(self):
        if (os.environ.get("GITHUB_ACTIONS") != "true"
                or os.environ.get("GITHUB_EVENT_NAME") != "pull_request"
                or os.environ.get("GITHUB_HEAD_REF") != PR_BRANCH
                or STOP.exists()):
            self.skipTest("Live request allowed only for the first named R005 PR attempt")
        urls = source_urls()
        observed = []
        for page in PAGES:
            if observed:
                time.sleep(1.4)
            started = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            url = urls[page]
            try:
                request = Request(url, headers={
                    "User-Agent": "MHAC-R005-frozen-EQ1-source-receipt/1",
                    "Accept": "application/json",
                })
                with urlopen(request, timeout=30) as response:
                    status = response.status
                    headers = {"date": response.headers.get("Date"),
                               "content_type": response.headers.get("Content-Type")}
                    raw = response.read(2_000_001)
                if status != 200:
                    raise ValueError("received non-200 source response")
                count, ids = assess(raw, page)
            except (HTTPError, URLError, TimeoutError, ValueError, AssertionError) as error:
                print("MHAC_R005_EQ1_45_47_BLOCKER=" + json.dumps({
                    "page": page, "url": url, "started_utc": started,
                    "exception": type(error).__name__, "http_status": getattr(error, "code", None),
                    "detail": str(error)[:240], "successful_pages": [r["page"] for r in observed],
                    "no_retry": True}, sort_keys=True), flush=True)
                self.skipTest("Public service refused or invalid response; no retry, no invented results")
            received = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            packed = gzip.compress(raw, compresslevel=9, mtime=0)
            obs = {
                "page": page, "url": url, "started_utc": started, "received_utc": received,
                "http_status": status, "headers": headers,
                "raw_bytes": len(raw), "raw_sha256": hashlib.sha256(raw).hexdigest(),
                "gzip_bytes": len(packed), "gzip_sha256": hashlib.sha256(packed).hexdigest(),
                "count": count, "ids": ids, "frozen_cutoff": CUTOFF,
                "only_metadata_not_screening_or_studies": True}
            observed.append(obs)
            print("MHAC_R005_EQ1_45_47_RESPONSE=" + json.dumps(obs, separators=(",", ":")), flush=True)
            b64 = base64.b64encode(packed).decode("ascii")
            chunks = [b64[i:i + 2400] for i in range(0, len(b64), 2400)]
            for ix, chunk in enumerate(chunks):
                print("MHAC_R005_EQ1_45_47_GZIP=" +
                      str(page) + ":" + str(ix) + "/" + str(len(chunks)) + ":" + chunk, flush=True)
        if len(observed) >= 2:
            print("MHAC_R005_EQ1_45_47_BOUNDARY=" +
                  json.dumps(boundary(observed), separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
