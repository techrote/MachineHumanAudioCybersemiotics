"""R005 negative controls: historical partial EQ1 cannot be extended from a shifted live index.

Synthetic mutations below are ONLY validator tests. The unmodified positive
case checks actual retained original November 3 export derivatives and the
genuine November 10 source receipt table.
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research/searches/auditory/eq1-drift-audit-2026-11-10"
mod = runpy.run_path(str(HERE / "audit.py"))
audit = mod["audit"]
load_current = mod["load_current"]
verify_historical_payload = mod["verify_historical_payload"]
read_json = mod["read_json"]
HIST = mod["HIST"]
OBS = mod["OBS"]


class R005ImmutableOverlapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.historical = read_json(HIST)
        cls.observed = read_json(OBS)
        cls.result = audit(cls.historical, cls.observed)

    def test_real_retained_historical_prefix_and_new_receipts_are_distinct(self):
        r = self.result
        self.assertEqual(r["historical_retrieved_occurrences"], 4200)
        self.assertEqual(r["historical_reported_total"], 9368)
        self.assertEqual(r["new_receipt_result_rows"], 200)
        self.assertEqual(r["new_reported_total"], 9275)
        self.assertEqual(r["provider_total_delta"], -93)
        self.assertEqual(r["historical_anchor_current_rank_if_observed"], 4142)
        self.assertEqual(r["anchor_rank_displacement_if_observed"], -58)
        self.assertGreaterEqual(r["current_200_already_in_historical_prefix"], 1)
        self.assertLessEqual(r["current_200_already_in_historical_prefix"], 200)
        self.assertEqual(r["current_page43_already_in_historical_prefix"], 0)
        self.assertFalse(r["can_append_current_page43_as_historical_continuation"])
        self.assertEqual(r["new_canonical_hits_registered"], 0)
        self.assertEqual(r["new_primary_studies_experiments_samples"], [0, 0, 0])

    def test_frozen_query_and_cutoff_cannot_change(self):
        mutated = copy.deepcopy(self.observed)
        mutated["cutoff"] = "2026-11-10"
        with self.assertRaisesRegex(ValueError, "cutoff"):
            load_current(mutated, self.historical["runs"]["EQ1"])

    def test_provider_response_total_mismatch_must_fail(self):
        mutated = copy.deepcopy(self.observed)
        mutated["pages"][1]["reported_total"] += 1
        with self.assertRaisesRegex(ValueError, "provider total"):
            load_current(mutated, self.historical["runs"]["EQ1"])

    def test_duplicate_works_in_two_pages_must_fail(self):
        mutated = copy.deepcopy(self.observed)
        mutated["pages"][1]["records"][0]["openalex_id"] = (
            mutated["pages"][0]["records"][0]["openalex_id"]
        )
        with self.assertRaisesRegex(ValueError, "duplicate current work"):
            load_current(mutated, self.historical["runs"]["EQ1"])

    def test_page_request_must_not_silently_switch_sort_or_source(self):
        mutated = copy.deepcopy(self.observed)
        mutated["pages"][0]["request_url"] = mutated["pages"][0]["request_url"].replace(
            "sort=publication_date:asc,display_name:asc", "sort=cited_by_count:desc"
        )
        with self.assertRaisesRegex(ValueError, "sort changed"):
            load_current(mutated, self.historical["runs"]["EQ1"])

    def test_no_promotion_of_metadata_into_study_or_search_record(self):
        mutated = copy.deepcopy(self.observed)
        mutated["new_selected_studies_or_samples"] = 1
        with self.assertRaisesRegex(ValueError, "forbidden admission"):
            load_current(mutated, self.historical["runs"]["EQ1"])
        mutated = copy.deepcopy(self.observed)
        mutated["provenance"]["new_search_occurrences_registered"] = 100
        with self.assertRaisesRegex(ValueError, "improperly promoted"):
            load_current(mutated, self.historical["runs"]["EQ1"])

    def test_historical_byte_or_payload_tamper_fails_closed(self):
        payload = json.dumps({"results": [{"id": "W1"}]}).encode("utf-8")
        blob = gzip.compress(payload, mtime=0)
        page = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob),
                "payload_sha256": hashlib.sha256(payload).hexdigest(),
                "payload_bytes": len(payload)}
        self.assertEqual(verify_historical_payload(blob, page), json.loads(payload))
        with self.assertRaisesRegex(ValueError, "gzip digest"):
            verify_historical_payload(blob + b"!", page)
        bad = dict(page, payload_sha256="f" * 64)
        with self.assertRaisesRegex(ValueError, "payload digest"):
            verify_historical_payload(blob, bad)


if __name__ == "__main__":
    unittest.main()
