"""Synthetic-only T012 regression tests; no accepted records are modified."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "research" / "tangents" / "codebook-migration"
spec = importlib.util.spec_from_file_location("t012_oracle", ROOT / "oracle.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class CodebookMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = mod.load()
        cls.rows = {r["id"]: r for r in cls.doc["cases"]}

    def test_sha256_manifest_and_replay(self):
        self.assertEqual(mod.check(), mod.summarize(self.doc))
    def test_independent_truth(self):
        self.assertEqual(len(self.rows), 34)
        self.assertEqual(mod.truth(self.rows["T13"]), "expired")
        self.assertEqual(mod.truth(self.rows["T20"]), "revoked")
        self.assertEqual(mod.truth(self.rows["T22"]), "unknown")
    def test_same_asset_new_referent_misbind(self):
        r = self.rows["T04"]
        self.assertEqual(mod.decision(self.doc, r, "silent_replacement")[2][0], "door")
        self.assertEqual(mod.decision(self.doc, r, "versioned_manifest")[0], "unresolved")
    def test_action_change_without_referent_change(self):
        r = self.rows["T06"]
        self.assertEqual(mod.decision(self.doc, r, "silent_replacement")[2][2], "ack")
        self.assertEqual(mod.decision(self.doc, r, "versioned_manifest")[0], "unresolved")
    def test_compatible_rollback_and_no_version_value(self):
        for case in ("T08", "T29"):
            self.assertEqual(mod.decision(self.doc, self.rows[case], "versioned_manifest")[0], "offer")
    def test_unknown_or_forged_version_not_trusted(self):
        for case in ("T14", "T15", "T16"):
            self.assertEqual(mod.decision(self.doc, self.rows[case], "versioned_manifest")[0], "unresolved")
    def test_trusted_external_authority_fallback(self):
        for case in ("T27", "T28", "T32"):
            self.assertEqual(mod.decision(self.doc, self.rows[case], "versioned_manifest")[1], "verified_nonaudio_fallback")
    def test_invalid_source_status_not_offered_by_guard(self):
        for case in ("T13", "T20", "T21", "T22", "T23", "T24", "T30", "T33"):
            self.assertEqual(mod.decision(self.doc, self.rows[case], "versioned_manifest")[0], "unresolved")
    def test_expected_failing_negative_control(self):
        s = mod.summarize(self.doc)["policies"]
        self.assertGreater(s["silent_replacement"]["wrong_referent"], 0)
        self.assertGreater(s["silent_replacement"]["expired_or_revoked_offers"], 0)
        self.assertGreater(s["frozen_legacy"]["wrong_action"], 0)
    def test_ideal_guard_symbolic_invariants_and_omissions(self):
        s = mod.summarize(self.doc)["policies"]["versioned_manifest"]
        for key in ("wrong_referent", "wrong_priority", "wrong_action", "invalid_or_unknown_offers", "false_compatibility_offers"):
            self.assertEqual(s[key], 0)
        self.assertGreater(s["omitted_valid"], 0)
    def test_alt_family_has_no_invented_human_performance(self):
        s = mod.summarize(self.doc)["policies"]["alternate_family_unknown"]
        self.assertEqual(s["offers"], 0)
        self.assertEqual(s["unresolved"], len(self.rows))

if __name__ == "__main__":
    unittest.main()
