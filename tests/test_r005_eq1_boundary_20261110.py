"""One-off, source-bound EQ1 boundary recheck. No live network on main.

The historical immutable 2026-11-03 sorted prefix ended at item 4200.
Current OpenAlex documentation caps per_page at 100, so examine the 42/43
boundary in a NEW retrieval, not as though it extends the old export.
Every HTTP outcome is printed; no response or hit is fabricated.
"""
from __future__ import annotations

import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import time
import unittest
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
HARVESTER = ROOT / "research/sources/auditory/scripts/openalex_harvest.py"
BRANCH = "mhac-r005/eq1-boundary-20261110-1312"
FROZEN_CUTOFF = "2026-10-04"
PAGES = (42, 43)
BOUNDARY_HISTORICAL_ID = "https://openalex.org/W2520134007"
LOG_PREFIX = "MHAC_R005_EQ1_BOUNDARY "
RECEIPT = ROOT / "research/searches/auditory/eq1-boundary-2026-11-10/OBSERVATIONS.json"


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")


def harvester():
    spec = importlib.util.spec_from_file_location("r005_eq1_harvester", HARVESTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def query_url(page):
    h = harvester()
    return h.page_url(h.query_families()["EQ1"], page, per_page=100,
                      sort="publication_date:asc,display_name:asc")


def receive(page):
    url = query_url(page)
    observed = {
        "page": page, "page_size": 100, "request_url": url,
        "request_started_utc": utc_now(), "interface": "OpenAlex works REST API",
        "access": "public unauthenticated HTTPS, no credentials or account",
        "source_class": "API discovery metadata, not primary full text",
    }
    req = request.Request(url, headers={
        "User-Agent": "MHAC-R005-EQ1-boundary/2026-11-10 (research)",
        "Accept": "application/json", "Accept-Encoding": "identity",
    })
    try:
        try:
            response = request.urlopen(req, timeout=40)
        except error.HTTPError as exc:
            response = exc
        with response:
            observed.update({
                "http_status": response.status if hasattr(response, "status") else response.code,
                "response_date": response.headers.get("Date"),
                "content_type": response.headers.get("Content-Type"),
                "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining"),
                "rate_limit_credits_used": response.headers.get("X-RateLimit-Credits-Used"),
                "retry_after": response.headers.get("Retry-After"),
                "received_utc": utc_now(),
            })
            raw = response.read(5_000_001)
            observed["completed_utc"] = utc_now()
        observed["raw_bytes_read"] = len(raw)
        observed["raw_sha256"] = hashlib.sha256(raw).hexdigest()
        if len(raw) > 5_000_000:
            observed["disposition"] = "BLOCKED_RESPONSE_OVERSIZE"; return observed
        try:
            obj = json.loads(raw)
        except (UnicodeError, ValueError) as exc:
            observed["disposition"] = "BLOCKED_INVALID_JSON_" + type(exc).__name__
            return observed
        if observed["http_status"] != 200:
            observed["disposition"] = "BLOCKED_HTTP_" + str(observed["http_status"])
            observed["error_summary"] = str(obj.get("message", ""))[:220] if isinstance(obj, dict) else "unknown"
            return observed
        meta = obj.get("meta", {})
        results = obj.get("results", [])
        observed["reported_total"] = meta.get("count")
        observed["reported_page"] = meta.get("page")
        observed["reported_page_size"] = meta.get("per_page")
        observed["api_cost_usd"] = meta.get("cost_usd")
        observed["results_returned"] = len(results)
        observed["records"] = [
            {"openalex_id": x.get("id"), "doi": x.get("doi"),
             "publication_date": x.get("publication_date"),
             "title": x.get("display_name"), "type": x.get("type"),
             "language": x.get("language")}
            for x in results
            if isinstance(x, dict)
        ]
        ids = [x["openalex_id"] for x in observed["records"]]
        observed["unique_ids"] = len(set(ids))
        observed["disposition"] = (
            "PAGE_RETURNED_UNADJUDICATED"
            if len(ids) == 100 and len(set(ids)) == 100
            and meta.get("page") == page and meta.get("per_page") == 100
            else "BLOCKED_PAGINATION_OR_DUPLICATE"
        )
        if page == 42:
            observed["matches_historical_4200_boundary"] = bool(
                ids and ids[-1] == BOUNDARY_HISTORICAL_ID
            )
    except Exception as exc:
        observed["disposition"] = "BLOCKED_TRANSPORT_" + type(exc).__name__
        observed["error_summary"] = str(exc)[:220]
        observed["completed_utc"] = utc_now()
    return observed


def validate_receipt(s):
    assert s["cutoff"] == FROZEN_CUTOFF
    assert s["historical_count"] == 4200
    assert s["historical_boundary_openalex_id"] == BOUNDARY_HISTORICAL_ID
    assert s["claim_complete_eq1"] is False
    assert s["new_selected_studies_or_samples"] == 0
    assert s["source_full_text_reviewed"] is False
    assert s["human_screening_claimed"] is False
    assert len(s["pages"]) == 2
    for p, n in zip(s["pages"], PAGES):
        assert p["page"] == n
        assert p["page_size"] == 100
        assert p["request_url"] == query_url(n)
        assert p["request_started_utc"]
        if p.get("disposition") == "PAGE_RETURNED_UNADJUDICATED":
            assert p["http_status"] == 200
            assert p["results_returned"] == p["unique_ids"] == len(p["records"]) == 100
            assert len(p["raw_sha256"]) == 64
            assert p["reported_page"] == n and p["reported_page_size"] == 100
            assert all(x["openalex_id"].startswith("https://openalex.org/W") for x in p["records"])
    return True


class TestR005EQ1Boundary(unittest.TestCase):
    def test_frozen_query_and_page_bounds(self):
        h = harvester()
        self.assertEqual(h.DATE_LIMIT, "to_publication_date:" + FROZEN_CUTOFF)
        self.assertIn("title_and_abstract.search:", query_url(43))
        self.assertIn("per_page=100", query_url(43))
        self.assertIn("page=43", query_url(43))
        self.assertIn("publication_date:asc,display_name:asc", query_url(43))
        self.assertNotIn("api_key", query_url(43))

    def test_saved_observation_and_negative_controls(self):
        if not RECEIPT.exists():
            self.skipTest("Actual HTTP observations not yet published; live receipt in exact-head run")
        data = json.loads(RECEIPT.read_text())
        self.assertTrue(validate_receipt(data))
        import copy
        for key, wrong in (
            ("cutoff", "2026-11-10"),
            ("claim_complete_eq1", True),
            ("new_selected_studies_or_samples", 100),
            ("human_screening_claimed", True),
            ("source_full_text_reviewed", True),
        ):
            bad = copy.deepcopy(data)
            bad[key] = wrong
            with self.assertRaises(AssertionError, msg=key):
                validate_receipt(bad)

    def test_once_per_issue_branch_live_source(self):
        if not (os.getenv("GITHUB_ACTIONS") == "true"
                and os.getenv("GITHUB_HEAD_REF") == BRANCH):
            self.skipTest("Live OpenAlex fetch restricted to issue-scoped PR; never on main")
        observations = {
            "schema": "mhac-r005-eq1-boundary/1",
            "actor": "GPT-6 R005 automation via GitHub Actions; AI-assisted, not human",
            "cutoff": FROZEN_CUTOFF,
            "historical_count": 4200,
            "historical_boundary_openalex_id": BOUNDARY_HISTORICAL_ID,
            "claim_complete_eq1": False,
            "new_selected_studies_or_samples": 0,
            "source_full_text_reviewed": False,
            "human_screening_claimed": False,
            "pages": [],
        }
        for page in PAGES:
            observations["pages"].append(receive(page))
            if page == 42:
                time.sleep(1.2)
        print(LOG_PREFIX + json.dumps(observations, separators=(",", ":"), ensure_ascii=False), flush=True)
        self.assertTrue(validate_receipt(observations))


if __name__ == "__main__":
    unittest.main()
