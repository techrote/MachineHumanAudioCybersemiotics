"""R005 bounded single-invocation OpenAlex EQ1 adjacent-page source probe.

Only the named R005 PR's first CI acquisition invokes the public service.
Every received original response is gzip-captured in Actions log chunks.
A later source-pinned R005 patch must commit and replay the authentic bytes;
these live observations alone are not accepted search-hit registration.
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
PR_BRANCH = "mhac-r005/eq1-single-snapshot-20261111-0615"
PREVIOUS = ROOT / "research/searches/auditory/eq1-pages44-47-20261111/OBSERVATIONS.json"
STOP = ROOT / "research/searches/auditory/eq1-single-snapshot-20261111/ATTEMPTED.json"
CUTOFF = "2026-10-04"
FIELDS = "id,doi,display_name,publication_date,publication_year,type,language"


def source_urls():
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    assert previous["cutoff"] == CUTOFF
    page44 = next(p for p in previous["pages"] if p["page"] == 44)
    url = page44["url"]
    pieces = urlsplit(url)
    params = parse_qs(pieces.query)
    assert pieces.netloc == "api.openalex.org" and pieces.scheme == "https"
    assert len(params) == 5 and set(params) == {"filter", "per_page", "select", "page", "sort"}
    assert params["filter"][0].startswith("title_and_abstract.search:")
    assert ",to_publication_date:2026-10-04" in params["filter"][0]
    assert params["per_page"] == ["100"]
    assert params["select"] == [FIELDS]
    assert params["sort"] == ["publication_date:asc,display_name:asc"]
    assert params["page"] == ["44"]
    return (url, url.replace("&page=44&", "&page=45&"))


def evaluate(page, raw):
    assert isinstance(raw, bytes) and len(raw) <= 2_000_000
    payload = json.loads(raw)
    meta = payload["meta"]
    assert meta["page"] == page and meta["per_page"] == 100
    assert isinstance(meta["count"], int) and meta["count"] > 0
    results = payload["results"]
    assert isinstance(results, list) and 0 < len(results) <= 100
    ids = [x["id"] for x in results]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("https://openalex.org/W") for i in ids)
    assert all(not item.get("publication_date") or item["publication_date"] <= CUTOFF for item in results)
    return meta["count"], ids


def adjacent(first, second):
    assert first["page"] == 44 and second["page"] == 45
    assert first["count"] == second["count"], "provider count changed within invocation"
    assert not set(first["ids"]).intersection(second["ids"]), "provider duplicated IDs across adjacent pages"
    return {"same_invocation_count": first["count"],
            "adjacent_page_duplicates": 0,
            "no_corpus_or_hit_admission": True}


class Eq1SingleSnapshot(unittest.TestCase):
    def test_exact_existing_query_and_cutoff(self):
        a, b = source_urls()
        self.assertIn("&page=44&", a)
        self.assertEqual(b, a.replace("&page=44&", "&page=45&"))
        self.assertEqual(urlsplit(a).query.replace("&page=44&", "&page=45&"),
                         urlsplit(b).query)

    def test_synthetic_identity_overlap_fails_closed(self):
        a = {"page": 44, "count": 100, "ids": ["https://openalex.org/W1"]}
        b = {"page": 45, "count": 100, "ids": ["https://openalex.org/W1"]}
        with self.assertRaisesRegex(AssertionError, "duplicated"):
            adjacent(a, b)
        b["ids"] = ["https://openalex.org/W2"]
        b["count"] = 101
        with self.assertRaisesRegex(AssertionError, "count"):
            adjacent(a, b)

    def test_wrong_page_and_cutoff_rejected(self):
        raw = json.dumps({"meta":{"page":44,"per_page":100,"count":1},
                          "results":[{"id":"https://openalex.org/W1",
                                      "publication_date":"2026-10-05"}]}).encode()
        with self.assertRaises(AssertionError):
            evaluate(44, raw)
        clean = raw.replace(b"2026-10-05", b"2026-10-04")
        with self.assertRaises(AssertionError):
            evaluate(45, clean)

    def test_one_bounded_real_source_acquisition(self):
        if (os.environ.get("GITHUB_ACTIONS") != "true"
                or os.environ.get("GITHUB_EVENT_NAME") != "pull_request"
                or os.environ.get("GITHUB_HEAD_REF") != PR_BRANCH
                or STOP.exists()):
            self.skipTest("Live access only for this exact R005 PR, until attempted checkpoint is committed")
        observed = []
        for page, url in zip((44, 45), source_urls()):
            if observed:
                time.sleep(1.2)
            started = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            try:
                req = Request(url, headers={"User-Agent":"MHAC-R005-evidence-provenance/1",
                                            "Accept":"application/json"})
                with urlopen(req, timeout=40) as response:
                    status = response.status
                    headers = {"date":response.headers.get("Date"),
                               "content_type":response.headers.get("Content-Type")}
                    raw = response.read(2_000_001)
                if status != 200:
                    raise RuntimeError("non-200 HTTP response")
                count, ids = evaluate(page, raw)
            except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError, AssertionError) as exc:
                print("MHAC_R005_EQ1_SINGLE_BLOCKER="+json.dumps({
                    "page":page, "url":url, "started_utc":started,
                    "error_type":type(exc).__name__,
                    "http_status":getattr(exc,"code",None),
                    "detail":str(exc)[:220], "attempted_pages":[o["page"] for o in observed]
                },sort_keys=True),flush=True)
                self.skipTest("real source unavailable or invalid; no fabricated response")
            received = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            packed = gzip.compress(raw, compresslevel=9, mtime=0)
            observation = {
                "page":page,"url":url,"started_utc":started,"received_utc":received,
                "http_status":status,"headers":headers,"raw_sha256":hashlib.sha256(raw).hexdigest(),
                "raw_bytes":len(raw),"gzip_sha256":hashlib.sha256(packed).hexdigest(),
                "gzip_bytes":len(packed),"count":count,"ids":ids,"frozen_cutoff":CUTOFF,
                "classification":"metadata_only_unscreened",
                "source_response_retained_in_repo":False,
                "admitted_publications_studies_experiments_samples":[0,0,0,0]
            }
            observed.append(observation)
            print("MHAC_R005_EQ1_SINGLE_RESPONSE="+json.dumps(observation,separators=(",",":")),flush=True)
            b64=base64.b64encode(packed).decode()
            chunks=[b64[i:i+2600] for i in range(0,len(b64),2600)]
            for index,part in enumerate(chunks):
                print(f"MHAC_R005_EQ1_SINGLE_GZIP={page}:{index}/{len(chunks)}:{part}",flush=True)
        try:
            summary=adjacent({"page":44,"count":observed[0]["count"],"ids":observed[0]["ids"]},
                             {"page":45,"count":observed[1]["count"],"ids":observed[1]["ids"]})
        except AssertionError as exc:
            print("MHAC_R005_EQ1_SINGLE_DISCONTINUITY="+str(exc),flush=True)
            self.skipTest("real provider changed count or repeated IDs; never claim continuity")
        print("MHAC_R005_EQ1_SINGLE_ADJACENCY="+json.dumps(summary),flush=True)


if __name__ == "__main__":
    unittest.main()
