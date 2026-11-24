"""Bounded regression adapter for MHAC-T011; standard-library only."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "research/tangents/mode-action-preconditions/oracle.py"
spec = importlib.util.spec_from_file_location("mhac_t011_oracle", PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ModeActionFalsifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {c["id"]: c for c in module.load_cases()}

    def test_truth_is_independent_and_has_controls(self):
        self.assertEqual(30, len(self.cases))
        self.assertEqual("valid", module.truth(self.cases["M01"]))
        self.assertEqual("wrong_mode", module.truth(self.cases["M02"]))
        self.assertEqual("valid", module.truth(self.cases["M11"]))
        self.assertEqual("not_required", module.truth(self.cases["M30"]))

    def test_unqualified_and_announcements_both_offer_wrong_mode(self):
        for policy in ("A_unqualified", "B_announce_all"):
            self.assertTrue(module.evaluate(self.cases["M02"], policy)["wrong_mode_offer"])
            self.assertTrue(module.evaluate(self.cases["M05"], policy)["false_known_state"])

    def test_guard_rejects_forbidden_and_stale_mode(self):
        for k in ("M02", "M03", "M04", "M05", "M08", "M09", "M10", "M29"):
            for p in ("C_conditional_guard", "D_visual_guard"):
                self.assertFalse(module.evaluate(self.cases[k], p)["sent"], (k, p))

    def test_guard_permits_mode_sensitive_valid_action(self):
        for p in ("C_conditional_guard", "D_visual_guard"):
            self.assertTrue(module.evaluate(self.cases["M01"], p)["sent"])
            self.assertTrue(module.evaluate(self.cases["M28"], p)["sent"])

    def test_guards_do_not_claim_unknown_actor_deadline_or_source(self):
        for k in ("M07", "M16", "M17", "M19", "M20", "M21", "M22"):
            self.assertNotEqual("valid", module.truth(self.cases[k]))
            self.assertFalse(module.guarded(self.cases[k]))

    def test_mode_independence_does_not_require_mode_readback(self):
        self.assertTrue(module.guarded(self.cases["M11"]))
        self.assertTrue(module.guarded(self.cases["M13"]))
        self.assertGreater(module.evaluate(self.cases["M13"], "B_announce_all")["audio_units"], 1)

    def test_acknowledgement_is_not_resolution(self):
        self.assertTrue(module.evaluate(self.cases["M25"], "A_unqualified")["unresolved_ack"])
        self.assertFalse(module.evaluate(self.cases["M26"], "A_unqualified")["unresolved_ack"])

    def test_duplicate_and_no_action_controls(self):
        self.assertTrue(module.evaluate(self.cases["M24"], "A_unqualified")["duplicate_offer"])
        self.assertFalse(module.evaluate(self.cases["M24"], "C_conditional_guard")["sent"])
        self.assertTrue(module.evaluate(self.cases["M30"], "A_unqualified")["invalid_or_unknown_offer"])
        self.assertFalse(module.evaluate(self.cases["M30"], "D_visual_guard")["sent"])

    def test_no_action_baseline_is_not_magic(self):
        self.assertTrue(module.evaluate(self.cases["M01"], "E_no_action")["missed_valid_action"])
        self.assertEqual(0, module.evaluate(self.cases["M23"], "E_no_action")["audio_units"])

    def test_output_deterministic_and_accounts_for_all_policies(self):
        rows = list(self.cases.values())
        self.assertEqual(module.canonical_report_bytes(rows), module.canonical_report_bytes(rows))
        self.assertEqual(set(module.POLICIES), set(module.report(rows)["policies"]))

    def test_manifest_matches_case_and_report_bytes(self):
        import hashlib
        import json
        manifest = json.loads(module.MANIFEST.read_text())
        self.assertEqual(manifest["fixture_sha256"], hashlib.sha256(module.FIXTURE.read_bytes()).hexdigest())
        self.assertEqual(manifest["report_sha256"], hashlib.sha256(module.canonical_report_bytes(list(self.cases.values()))).hexdigest())


if __name__ == "__main__":
    unittest.main()
