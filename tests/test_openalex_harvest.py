"""Synthetic responses test coverage/provenance failure modes without network use."""
from __future__ import annotations
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("openalex_harvest", ROOT / "research/sources/auditory/scripts/openalex_harvest.py")
HARVEST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HARVEST)


def response(count, page=1, ids=None, per_page=200, headers=None, abstract=False):
    ids = ids if ids is not None else [f"W{i}" for i in range(min(count, per_page))]
    works = [{"id": identity, "display_name": f"SYNTHETIC TEST {identity}", "referenced_works": ["W-ref"]} for identity in ids]
    if abstract:
        works[0]["abstract_inverted_index"] = {"SYNTHETIC": [0], "PRIVATE": [1]}
    body = json.dumps({"meta": {"count": count, "page": page, "per_page": per_page, "cost_usd": 0.001}, "results": works}).encode()
    return 200, body, headers or {}


class OpenAlexHarvestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root, self.calls = Path(self.tmp.name), []

    def tearDown(self):
        self.tmp.cleanup()

    def run_mock(self, responses, labels=None, **kwargs):
        responses = iter(responses)
        def fetcher(url):
            self.calls.append(url)
            result = next(responses)
            if isinstance(result, BaseException):
                raise result
            return result
        with contextlib.redirect_stdout(io.StringIO()):
            return HARVEST.run_harvest(labels or ["EQ4"], out_root=self.root / "public", private_root=self.root / "private",
                                      root=self.root, run_id="test", fetcher=fetcher, delay=0, sleeper=lambda _: None, **kwargs)

    def test_query_roundtrip_preserves_all_frozen_terms_and_scope(self):
        families = HARVEST.query_families()
        self.assertEqual(set(families), {f"EQ{i}" for i in range(1, 9)})
        for query in families.values():
            params = urllib.parse.parse_qs(urllib.parse.urlsplit(HARVEST.page_url(query, 2)).query)
            self.assertEqual(params["filter"], ["title_and_abstract.search:" + query + ",to_publication_date:2026-10-04"])
            self.assertEqual(params["page"], ["2"])
            self.assertNotIn("cursor", params)
            self.assertNotIn("api_key", params)
            self.assertEqual(params["sort"], ["publication_date:asc,display_name:asc"])

    def test_complete_multi_page_run_has_exact_count_and_verified_files(self):
        manifest, _ = self.run_mock([response(203), response(203, 2, ["W200", "W201", "W202"])])
        run = manifest["runs"]["EQ4"]
        self.assertTrue(manifest["complete"])
        self.assertEqual((run["retrieved"], run["unique_retrieved"]), (203, 203))
        for page in run["pages"]:
            self.assertEqual(hashlib.sha256((self.root / page["file"]).read_bytes()).hexdigest(), page["sha256"])

    def test_public_derivative_omits_abstract_and_private_path(self):
        reply = response(1, abstract=True)
        manifest, _ = self.run_mock([reply])
        page = manifest["runs"]["EQ4"]["pages"][0]
        public = json.loads(gzip.decompress((self.root / page["file"]).read_bytes()))
        self.assertNotIn("abstract_inverted_index", public["results"][0])
        self.assertEqual(public["results"][0]["referenced_works"], ["W-ref"])
        self.assertEqual((self.root / "private" / page["private_raw_cache_key"]).read_bytes(), reply[1])
        self.assertEqual(hashlib.sha256(reply[1]).hexdigest(), page["raw_sha256"])
        self.assertNotIn(str(self.root), json.dumps(manifest))

    def test_gzip_integrity_is_deterministic_and_payload_is_bound(self):
        manifest, _ = self.run_mock([response(1)])
        page = manifest["runs"]["EQ4"]["pages"][0]
        compressed = (self.root / page["file"]).read_bytes()
        payload = gzip.decompress(compressed)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), page["payload_sha256"])
        self.assertEqual(len(payload), page["payload_bytes"])
        self.assertEqual(HARVEST._gzip(payload), compressed)
        self.assertEqual(compressed[4:8], bytes(4))

    def test_transient_load_retry_preserves_each_attempt(self):
        failure = (429, b'{"message":"Anonymous search is temporarily rate-limited while the search cluster is under elevated load.","retryAfter":11}', {"Retry-After": "11"})
        manifest, _ = self.run_mock([response(203), failure, response(203, 2, ["W200", "W201", "W202"])])
        run = manifest["runs"]["EQ4"]
        self.assertTrue(run["complete"])
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(run["pages"][1]["http_status"], 429)
        self.assertTrue(run["pages"][1]["retry_scheduled"])
        self.assertEqual(run["pages"][2]["attempt"], 2)
        self.assertNotEqual(run["pages"][1]["file"], run["pages"][2]["file"])
        self.assertEqual(run["retrieved"], 203)

    def test_no_more_than_two_transient_retries(self):
        failure = (429, b'{"message":"temporarily limited by elevated load","retryAfter":1}', {})
        manifest, _ = self.run_mock([failure, failure, failure])
        self.assertFalse(manifest["complete"])
        self.assertEqual(len(self.calls), 3)

    def test_signed_url_parameters_are_not_republished(self):
        value = {"url": "https://example.test/paper.pdf?X-Amz-Signature=synthetic-secret&X-Amz-Expires=3600"}
        self.assertEqual(HARVEST._public_urls(value), {"url": "https://example.test/paper.pdf"})

    def test_count_drift_cannot_pass_as_complete(self):
        manifest, _ = self.run_mock([response(203), response(204, 2, ["W200", "W201", "W202", "W203"])])
        self.assertFalse(manifest["complete"])
        self.assertIn("count_drift", str(manifest["runs"]["EQ4"]["failures"]))

    def test_duplicate_ids_within_and_across_pages_fail(self):
        manifest, _ = self.run_mock([response(203), response(203, 2, ["W0", "W201", "W201"])])
        run = manifest["runs"]["EQ4"]
        self.assertFalse(run["complete"])
        self.assertEqual((run["retrieved"], run["unique_retrieved"]), (203, 201))
        self.assertEqual(run["pages"][1]["duplicate_ids"], ["W0", "W201"])

    def test_early_short_page_is_not_completion(self):
        manifest, _ = self.run_mock([response(203, ids=["W0"])])
        self.assertIn("premature_short_page", str(manifest["runs"]["EQ4"]["failures"]))
        self.assertFalse(manifest["complete"])

    def test_no_truncation_at_service_basic_paging_limit(self):
        manifest, _ = self.run_mock([response(10001)])
        self.assertEqual(len(self.calls), 1)
        self.assertIn("basic_paging_limit", str(manifest["runs"]["EQ4"]["failures"]))
        self.assertFalse(manifest["complete"])

    def test_rate_limit_preserves_partial_and_unstarted_families(self):
        manifest, _ = self.run_mock([response(203), (429, b'{"error":"synthetic budget limit"}', {})], labels=["EQ4", "EQ5"])
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(manifest["runs"]["EQ4"]["status"], "partial")
        self.assertEqual(manifest["runs"]["EQ5"]["retrieved"], 0)
        self.assertFalse(manifest["complete"])

    def test_observed_budget_boundary_avoids_extra_request(self):
        manifest, _ = self.run_mock([response(203, headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Credits-Used": "10"})])
        self.assertEqual(len(self.calls), 1)
        self.assertIn("observed_daily_budget_boundary", manifest["runs"]["EQ4"]["failures"])
        self.assertEqual(manifest["runs"]["EQ4"]["retrieved"], 200)

    def test_explicit_budget_never_becomes_false_completion(self):
        manifest, _ = self.run_mock([response(203)], max_requests=1)
        self.assertFalse(manifest["complete"])
        self.assertIn("request_budget_boundary", manifest["runs"]["EQ4"]["failures"])

    def test_transport_failure_is_persisted(self):
        manifest, path = self.run_mock([TimeoutError("synthetic timeout")])
        self.assertFalse(manifest["complete"])
        self.assertIn("transport_error", manifest["runs"]["EQ4"]["pages"][0])
        self.assertEqual(json.loads(path.read_text())["runs"]["EQ4"]["status"], "failed")

    def test_missing_identity_or_wrong_pagination_fail(self):
        manifest, _ = self.run_mock([response(1, page=9, ids=[None])])
        failures = str(manifest["runs"]["EQ4"]["failures"])
        self.assertIn("response_pagination_mismatch", failures)
        self.assertIn("missing_work_id", failures)

    def test_existing_run_is_never_overwritten(self):
        self.run_mock([response(1)])
        with self.assertRaises(FileExistsError):
            self.run_mock([response(1)])

    def test_empty_query_is_complete_with_zero_service_total(self):
        manifest, _ = self.run_mock([response(0, ids=[])])
        self.assertTrue(manifest["complete"])
        self.assertEqual(manifest["total_query_occurrences"], 0)


if __name__ == "__main__":
    unittest.main()
