"""Recovery cannot alter original history or silently trust truncated exports."""
from __future__ import annotations

import copy
import gzip
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "r005_recovery", ROOT / "research/sources/auditory/scripts/build_r005_recovery_records.py")
recovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recovery)


class RecoveryIntegrityTests(unittest.TestCase):
    def test_gzip_container_and_payload_are_independently_verified(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory) / "response.json.gz"
            payload = b'{"results": []}\n'
            blob = gzip.compress(payload, mtime=0)
            path.write_bytes(blob)
            page = {"file": str(path.relative_to(ROOT)),
                    "sha256": hashlib.sha256(blob).hexdigest(),
                    "payload_sha256": hashlib.sha256(payload).hexdigest()}
            self.assertEqual(recovery.verified_payload(page), {"results": []})
            page["payload_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "Uncompressed response hash"):
                recovery.verified_payload(page)
            page["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "Stored response hash"):
                recovery.verified_payload(page)

    def test_generator_preserves_later_identity_revisions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "HIT-EXAMPLE.json"
            first = {"schema_version": 1, "id": "HIT-EXAMPLE", "kind": "search_hit",
                     "synthetic": False, "issue": 5, "revisions": [{"rev": 1, "data": "original"}]}
            later = copy.deepcopy(first)
            later["revisions"].append({"rev": 2, "data": "later adjudication"})
            path.write_text(json.dumps(later))
            before = path.read_bytes()
            self.assertEqual(recovery.safe_write_records({path: first}), 0)
            self.assertEqual(path.read_bytes(), before)

    def test_batch_preflight_cannot_partially_write_before_history_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = {"schema_version": 1, "id": "HIT-EXAMPLE", "kind": "search_hit",
                        "synthetic": False, "issue": 5, "revisions": [{"rev": 1, "data": "original"}]}
            old = root / "existing.json"
            old.write_text(json.dumps(existing))
            changed = copy.deepcopy(existing)
            changed["revisions"][0]["data"] = "rewritten past"
            new = root / "new.json"
            with self.assertRaisesRegex(ValueError, "rewrite recorded history"):
                recovery.safe_write_records({new: existing, old: changed})
            self.assertFalse(new.exists())

    def test_registered_recovery_reproduces_when_finalized(self):
        stamp = recovery.RECOVERY / "INTEGRATION.json"
        if not stamp.exists():
            self.skipTest("Recovery is not finalized yet")
        at = json.loads(stamp.read_text())["recorded_at"]
        records = recovery.build(at)
        recovery.safe_write_records(records, check=True)
        searches = {r["id"]: r["revisions"][0]["data"] for r in records.values() if r["kind"] == "search_run"}
        hits = [r["revisions"][0]["data"] for r in records.values() if r["kind"] == "search_hit"]
        for rid, search in searches.items():
            ordinals = sorted(h["ordinal"] for h in hits if h["search_ref"]["id"] == rid)
            self.assertEqual(ordinals, list(range(1, search["retrieved_count"] + 1)), rid)
        self.assertTrue(all(h["status"] == "unresolved" for h in hits))


if __name__ == "__main__":
    unittest.main()
