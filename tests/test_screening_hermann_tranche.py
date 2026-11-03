"""Verify the bounded real identity tranche without deciding eligibility.

Negative cases alter temporary copies only; canonical research stays intact.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools.record_io import dumps, read_json

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "r006_hermann_tranche",
    ROOT / "research/registry/identity/scripts/build_r006_hermann.py",
)
TRANCHE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TRANCHE)


class HermannTrancheTests(unittest.TestCase):
    def setUp(self):
        self.ledger = read_json(ROOT / TRANCHE.LEDGER)
        self.records, self.expected, self.table = TRANCHE.build(ROOT, self.ledger["resolved_at"])

    def temporary_inputs(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        for relative in [TRANCHE.SOURCE_PATH, TRANCHE.LEDGER, TRANCHE.TABLE,
                         *(path for path in self.records if "/hits/" in path)]:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        return root

    def test_frozen_ledger_table_and_record_prefixes_reproduce(self):
        self.assertEqual(self.ledger, self.expected)
        self.assertEqual((ROOT / TRANCHE.TABLE).read_text(encoding="utf-8"), self.table)
        for relative, expected in self.records.items():
            with self.subTest(path=relative):
                actual = read_json(ROOT / relative)
                actual["revisions"] = actual["revisions"][:len(expected["revisions"])]
                self.assertEqual(actual, expected)

    def test_original_discovery_is_retained_and_hash_pinned(self):
        for occurrence in self.ledger["occurrences"]:
            rid = occurrence["hit_id"]
            path = "research/searches/auditory/records/hits/" + rid + ".json"
            record = self.records[path]
            original, resolution = record["revisions"]
            self.assertEqual(TRANCHE.digest(original), occurrence["input_revision_sha256"])
            self.assertEqual(TRANCHE.digest(resolution), occurrence["output_revision_sha256"])
            self.assertEqual(original["data"]["status"], "unresolved")
            # These are the only fields this publication-identity step may change.
            ignored = {"source_ref", "status", "resolution_reason", "duplicate_of"}
            self.assertEqual({k: v for k, v in original["data"].items() if k not in ignored},
                             {k: v for k, v in resolution["data"].items() if k not in ignored})
            self.assertEqual(record["issue"], 5)  # Immutable original discovery envelope.
            self.assertIn(occurrence["input_ref"], resolution["basis"])
            self.assertIn(TRANCHE.ref(TRANCHE.AID), resolution["basis"])

    def test_three_occurrences_link_one_existing_source_without_new_scientific_entities(self):
        kinds = [record["kind"] for record in self.records.values()]
        self.assertCountEqual(kinds, ["search_hit"] * 3 + ["assistance"])
        rows = self.ledger["occurrences"]
        self.assertEqual([r["hit_id"] for r in rows], list(TRANCHE.HITS))
        self.assertEqual([r["status"] for r in rows], ["resolved", "duplicate", "duplicate"])
        for row in rows:
            self.assertEqual(row["source_ref"], TRANCHE.ref(TRANCHE.SOURCE))
            self.assertEqual(row["exact_url"], TRANCHE.URL)
        for duplicate in rows[1:]:
            self.assertEqual(duplicate["duplicate_of"], rows[0]["output_ref"])
        self.assertEqual(self.ledger["counts"]["occurrences"], len(rows))
        self.assertEqual(self.ledger["counts"]["duplicate_occurrences"],
                         sum(r["status"] == "duplicate" for r in rows))
        self.assertEqual(self.ledger["counts"]["existing_publications"],
                         len({r["source_ref"]["id"] for r in rows}))
        for field in ("new_source_records", "screening_decisions_created", "study_records_created", "sample_records_created"):
            self.assertEqual(self.ledger["counts"][field], 0)
        source_revision = read_json(ROOT / TRANCHE.SOURCE_PATH)["revisions"][0]
        self.assertEqual(TRANCHE.digest(source_revision), self.ledger["source"]["revision_sha256"])
        self.assertNotIn(TRANCHE.SOURCE_PATH, self.records)

    def test_unverified_source_url_cannot_support_resolution(self):
        root = self.temporary_inputs()
        source = read_json(root / TRANCHE.SOURCE_PATH)
        for item in source["revisions"][0]["data"]["identifiers"]:
            if item["scheme"] == "url" and item["value"] == TRANCHE.URL:
                item["status"] = "candidate"
        (root / TRANCHE.SOURCE_PATH).write_text(dumps(source), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "exact verified URL"):
            TRANCHE.build(root, self.ledger["resolved_at"])

    def test_similar_filename_is_not_identity_evidence(self):
        root = self.temporary_inputs()
        path = root / ("research/searches/auditory/records/hits/" + TRANCHE.HITS[1] + ".json")
        hit = read_json(path)
        hit["revisions"][0]["data"]["returned_identifiers"][0]["value"] = TRANCHE.URL.replace("Hermann2008", "Hermann2008a")
        path.write_text(dumps(hit), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "exact-URL case"):
            TRANCHE.build(root, self.ledger["resolved_at"])

    def test_frozen_count_drift_blocks_rebuild_before_any_record_write(self):
        root = self.temporary_inputs()
        changed = copy.deepcopy(self.ledger)
        changed["counts"]["existing_publications"] = 3
        (root / TRANCHE.LEDGER).write_text(dumps(changed), encoding="utf-8")
        before = {path: (root / path).read_bytes() for path in self.records if (root / path).exists()}
        with patch.object(TRANCHE, "ROOT", root), patch("sys.argv", ["build_r006_hermann.py"]):
            with self.assertRaisesRegex(SystemExit, "Frozen identity tranche ledger drift"):
                TRANCHE.main()
        self.assertEqual(before, {path: (root / path).read_bytes() for path in before})
        self.assertFalse((root / (TRANCHE.AREA + "/records/" + TRANCHE.AID + ".json")).exists())


if __name__ == "__main__":
    unittest.main()
