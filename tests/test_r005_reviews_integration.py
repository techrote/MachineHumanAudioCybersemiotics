"""C9 provenance and OpenAlex retry/planning observations stay distinguishable.

The integration build below is in memory only: no INTEGRATION timestamp, live
records or generated aggregate is written by these tests.
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from schemas.v1 import validate_record

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "r005_reviews_integration", ROOT / "research/sources/auditory/scripts/build_r005_recovery_records.py")
recovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recovery)
STAMP = recovery.RECOVERY / "INTEGRATION.json"
AT = recovery.read_json(STAMP)["recorded_at"] if STAMP.exists() else "2026-11-03T02:00:00Z"


class ReviewRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # build() proposes dictionaries only; main() owns timestamp/file writes.
        cls.records = recovery.build(AT)
        cls.by_id = {r["id"]: r for r in cls.records.values()}
        cls.manifest = recovery.read_json(recovery.RECOVERY / "reviews/MANIFEST.json")

    def test_all_312_original_citations_have_correct_source_and_reading_pins(self):
        observed = 0
        for source in self.manifest["reviews"]:
            key = source["review_key"]
            label = key.split("-")[0].upper()
            rid = f"SRCH-R005R-C9{label}"
            search = self.by_id[rid]
            body = search["revisions"][0]["data"]
            bibliography = recovery.read_json(recovery.RECOVERY / "reviews" / source["reference_export"]["path"])
            self.assertEqual(body["retrieved_count"], len(bibliography["references"]))
            self.assertEqual(body["status"], "completed")
            self.assertEqual(search["revisions"][0]["actor"], recovery.REVIEW_ACTOR)
            reading = self.by_id[f"AID-R005R-{label}-REFERENCES"]
            rd = reading["revisions"][0]["data"]
            self.assertEqual(rd["ranges"], [[1, 1], bibliography["reference_pdf_pages_inclusive"]])
            self.assertEqual(rd["performed_at"]["value"], self.manifest["created_at"])
            self.assertEqual(rd["reading_status"], "selected_ranges_read")
            self.assertEqual(reading["revisions"][0]["actor"], recovery.REVIEW_ACTOR)
            sr = self.by_id[rd["source_ref"]["id"]]
            sd = sr["revisions"][rd["source_ref"]["rev"] - 1]["data"]
            self.assertIn(rd["source_ref"], search["revisions"][0]["basis"])
            self.assertEqual(sd["manifestations"][-1]["sha256"], bibliography["source_sha256"])
            self.assertEqual(sd["manifestations"][-1]["extent"], bibliography["source_pdf_pages"])
            self.assertFalse(any("local_path" in m for m in sd["manifestations"]))
            for row in [sr, reading, search]:
                validate_record(row, expected_kind="live")
            for entry in bibliography["references"]:
                hid = rid.replace("SRCH-", "HIT-", 1) + f"-{entry['ordinal']:05d}"
                hit = self.by_id[hid]
                hd = hit["revisions"][0]["data"]
                self.assertEqual(hd["raw_metadata"].split(" | ", 1)[0], entry["citation_text"])
                self.assertIn(entry["occurrence_id"], hd["raw_metadata"])
                self.assertEqual(hd["status"], "unresolved")
                self.assertNotIn("source_ref", hd)
                self.assertEqual(hit["revisions"][0]["actor"], recovery.REVIEW_ACTOR)
                validate_record(hit, expected_kind="live")
                observed += 1
        self.assertEqual(observed, 312)

    def test_c1_preserves_15_entries_with_two_truthful_unattempted_plans(self):
        rows = {rid: r["revisions"][0]["data"] for rid, r in self.by_id.items()
                if rid.startswith("SRCH-R005R-C1")}
        self.assertEqual(len(rows), 15)
        planned = {rid for rid, body in rows.items() if body["status"] == "planned"}
        self.assertEqual(planned, {"SRCH-R005R-C1SORT-EQ1", "SRCH-R005R-C1SORT-EQ8"})
        for rid in planned:
            data = rows[rid]
            for field in ("started_at", "finished_at", "export"):
                self.assertNotEqual(data[field]["state"], "known")
            self.assertEqual(data["retrieved_count"], 0)
            self.assertEqual(data["failures"], [])
            self.assertIn("planned but not attempted", data["boundary"])
            validate_record(self.by_id[rid], expected_kind="live")
        self.assertEqual(recovery.openalex_run_id("20261103-database-recovery", "EQ1"),
                         "SRCH-R005R-C1RECOVERY-EQ1")
        with self.assertRaisesRegex(ValueError, "explicit stable"):
            recovery.openalex_run_id("new-unassigned-manifest", "EQ1")

    def _edworthy(self):
        return copy.deepcopy(self.by_id["SRC-R005R-EDWORTHY-2013"])

    def test_existing_verified_doi_is_revised_without_duplicate_or_history_rewrite(self):
        fresh = self._edworthy()
        incoming = copy.deepcopy(fresh["revisions"][0]["data"])
        old = copy.deepcopy(fresh)
        old.update(id="SRC-REL-EDWORTHY-2013", issue=4)
        old["revisions"][0].update(at="2026-10-13T07:00:00Z", actor={
            "kind": "agent", "id": "synthetic-prior-observer-for-test",
            "tool": "isolated test fixture", "model": "fixture"})
        previous_data = old["revisions"][0]["data"]
        previous_data.update(access_at="2026-10-13T06:00:00Z", access_status="metadata_only",
                             access_reason="Isolated fixture's earlier observation", manifestations=[])
        previous_data["identifiers"] = [i for i in previous_data["identifiers"] if i["scheme"] == "doi"]
        previous_data["publication_date"] = recovery.known("2013-05")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing_path = root / "research/sources/related/records/SRC-REL-EDWORTHY-2013.json"
            existing_path.parent.mkdir(parents=True)
            existing_path.write_text(json.dumps(old))
            with patch.object(recovery, "ROOT", root), patch.object(recovery, "SOURCE", root / "research/sources/auditory/records"):
                proposed = {}
                ref = recovery._review_source(AT, fresh["id"], incoming, proposed)
                self.assertEqual(ref, {"id": "SRC-REL-EDWORTHY-2013", "rev": 2})
                self.assertEqual(set(proposed), {existing_path})
                revised = proposed[existing_path]
                self.assertEqual(revised["revisions"][:1], old["revisions"])
                self.assertEqual(revised["issue"], 4)
                self.assertEqual(revised["revisions"][1]["data"]["publication_date"], recovery.known("2013-05"))
                validate_record(revised, expected_kind="live")
                with self.assertRaisesRegex(ValueError, "Missing generated recovery revision"):
                    recovery.safe_write_records(proposed, check=True)
                self.assertEqual(recovery.safe_write_records(proposed), 1)
                later = copy.deepcopy(revised)
                future = copy.deepcopy(later["revisions"][-1])
                future.update(rev=3, at="2026-12-01T00:00:00Z")
                future["actor"]["id"] = "synthetic-later-observer-for-test"
                future["data"]["title"] = "Later identity correction in isolated fixture"
                later["revisions"].append(future)
                existing_path.write_text(json.dumps(later))
                saved = existing_path.read_bytes()
                replay = {}
                replay_ref = recovery._review_source(AT, fresh["id"], incoming, replay)
                self.assertEqual(replay_ref, ref)
                self.assertEqual(replay, proposed)
                self.assertEqual(recovery.safe_write_records(replay), 0)
                self.assertEqual(existing_path.read_bytes(), saved)

    def test_append_preflight_still_rejects_a_changed_earlier_revision(self):
        first = self._edworthy()
        with tempfile.TemporaryDirectory() as directory:
            old_path = Path(directory) / "existing.json"
            new_path = Path(directory) / "must-not-be-written.json"
            old_path.write_text(json.dumps(first))
            changed = copy.deepcopy(first)
            changed["revisions"][0]["data"]["access_reason"] = "Rewritten history"
            changed["revisions"].append(copy.deepcopy(changed["revisions"][0]))
            changed["revisions"][1]["rev"] = 2
            with self.assertRaisesRegex(ValueError, "rewrite recorded history"):
                recovery.safe_write_records({new_path: first, old_path: changed})
            self.assertFalse(new_path.exists())
            self.assertEqual(json.loads(old_path.read_text()), first)


class OpenAlexErrorPageTests(unittest.TestCase):
    def test_error_responses_are_hash_checked_but_never_counted_as_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def save(name, payload, **metadata):
                blob = gzip.compress(json.dumps(payload).encode(), mtime=0)
                (root / name).write_bytes(blob)
                return {"file": name, "sha256": hashlib.sha256(blob).hexdigest(), **metadata}

            error = save("error.json.gz", {"error": "retained 429 excerpt"}, http_status=429)
            result = save("result.json.gz", {"results": [{"id": "https://openalex.org/W1"}]},
                          http_status=200, results=1)
            with patch.object(recovery, "ROOT", root):
                self.assertEqual(recovery.openalex_result_pages([error, result]),
                                 [{"id": "https://openalex.org/W1"}])
                with self.assertRaisesRegex(ValueError, "Unclassified"):
                    recovery.openalex_result_pages([{**error, "http_status": 200}])
                with self.assertRaisesRegex(ValueError, "Page count mismatch"):
                    recovery.openalex_result_pages([{**result, "results": 2}])
                (root / "error.json.gz").write_bytes(b"corrupted retained error response")
                with self.assertRaisesRegex(ValueError, "Stored response hash"):
                    recovery.openalex_result_pages([error, result])


if __name__ == "__main__":
    unittest.main()
