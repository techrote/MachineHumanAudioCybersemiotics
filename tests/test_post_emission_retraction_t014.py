"""MHAC-T014 fictional retraction comparison: repository-discoverable tests."""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "research" / "tangents" / "post-emission-retraction"
spec = importlib.util.spec_from_file_location("t014_replay", DIR / "replay.py")
if spec is None or spec.loader is None:
    raise RuntimeError("unable to load T014 replay module")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PostEmissionRetractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = mod.load_cases()
        cls.by_id = {c["id"]: c for c in cls.cases}

    def test_case_count_and_independent_labels(self):
        self.assertEqual(len(self.cases), 36)
        self.assertEqual(sum(c["expected_need"] for c in self.cases), 22)
        for c in self.cases:
            self.assertEqual(mod.requires_offer(c), c["expected_need"], c["id"])

    def test_all_policy_expectations(self):
        report = mod.build_report()
        mod.check_report(report)
        self.assertEqual(report["dataset_kind"], "fictional")
        self.assertEqual(len(report["policies"]), 4)

    def test_unknown_action_is_not_rewritten_by_safe_policies(self):
        c = self.by_id["T014-001"]
        self.assertEqual(c["action_state"], "unknown")
        for p in ("bound-minimal", "bound-uncertainty"):
            out = mod.emit(c, p)
            self.assertTrue(out["offer"])
            self.assertEqual(out["action"], "unknown")
            self.assertFalse(out["closed"])
            self.assertEqual(out["delivery"], "pending_or_failed")

    def test_known_correction_delivery_does_not_establish_undo(self):
        c = self.by_id["T014-003"]
        self.assertEqual(c["correction_delivery"], "confirmed")
        self.assertEqual(c["reversible"], "no")
        out = mod.emit(c, "bound-uncertainty")
        self.assertTrue(out["offer"])
        self.assertFalse(out["closed"])
        self.assertFalse(out["claims_undone"])

    def test_explicit_independent_restoration_can_close(self):
        c = self.by_id["T014-012"]
        self.assertTrue(c["resolution_verified"])
        self.assertTrue(mod.emit(c, "bound-minimal")["closed"])
        changed = dict(c, correction_delivery="unknown")
        self.assertFalse(mod.emit(changed, "bound-minimal")["closed"])

    def test_unrelated_event_actor_source_and_message_rejected(self):
        for suffix in (26, 27, 28, 29, 33, 35):
            c = self.by_id[f"T014-{suffix:03d}"]
            self.assertFalse(mod.valid_target(c))
            self.assertFalse(mod.emit(c, "bound-minimal")["offer"])

    def test_undelivered_original_and_never_emitted_are_negative(self):
        for suffix in (23, 24, 31):
            c = self.by_id[f"T014-{suffix:03d}"]
            self.assertFalse(mod.emit(c, "bound-uncertainty")["offer"])

    def test_superseded_or_still_valid_are_negative(self):
        for suffix in (25, 30, 34, 36):
            c = self.by_id[f"T014-{suffix:03d}"]
            self.assertFalse(mod.requires_offer(c))

    def test_binding_mutation_cannot_authorize_wrong_target(self):
        good = self.by_id["T014-002"]
        self.assertTrue(mod.requires_offer(good))
        for field in ("correction_for", "correction_source",
                      "correction_event", "correction_actor"):
            bad = dict(good, **{field: "UNRELATED-ID"})
            self.assertFalse(mod.requires_offer(bad), field)
            self.assertFalse(mod.emit(bad, "bound-uncertainty")["offer"])

    def test_unknown_case_no_synthetic_success_from_retraction(self):
        c = self.by_id["T014-005"]
        self.assertEqual(c["correction_delivery"], "unknown")
        self.assertFalse(mod.emit(c, "bound-minimal")["closed"])
        self.assertFalse(mod.emit(c, "bound-uncertainty")["claims_receipt"])
        self.assertTrue(mod.emit(c, "generic-closure")["claims_receipt"])

    def test_negative_control_reveals_invalid_closure(self):
        report = mod.build_report()
        by_policy = {x["policy"]: x["metrics"] for x in report["policies"]}
        self.assertGreater(by_policy["generic-closure"]["unsupported_action_claims"], 0)
        self.assertGreater(by_policy["generic-closure"]["unsupported_receipt_claims"], 0)
        self.assertGreater(by_policy["generic-closure"]["unnecessary_offers"], 0)
        # Policy self-declarations must not rewrite the independent world oracle:
        self.assertEqual(by_policy["generic-closure"]["unresolved_required_obligations"], 21)
        self.assertEqual(by_policy["generic-closure"]["false_clear_for_unresolved"], 21)
        self.assertEqual(by_policy["bound-minimal"]["unresolved_required_obligations"], 21)
        self.assertEqual(by_policy["bound-minimal"]["false_clear_for_unresolved"], 0)
        self.assertEqual(by_policy["bound-minimal"]["premature_closure"], 0)
        self.assertEqual(by_policy["silent"]["offers"], 0)

    def test_brevity_null_and_urgent_tradeoff_are_visible(self):
        report = mod.build_report()
        by_policy = {x["policy"]: x["metrics"] for x in report["policies"]}
        self.assertEqual(by_policy["bound-minimal"]["missing_offers"], 0)
        self.assertEqual(by_policy["bound-uncertainty"]["missing_offers"], 0)
        self.assertGreater(by_policy["bound-uncertainty"]["tokens"],
                           by_policy["bound-minimal"]["tokens"])
        self.assertGreater(by_policy["bound-uncertainty"]["urgent_interruption_tokens_proxy"],
                           by_policy["bound-minimal"]["urgent_interruption_tokens_proxy"])

    def test_gold_label_remains_independent_of_policy_mutation(self):
        copy_cases = copy.deepcopy(self.cases)
        row = copy_cases[0]
        self.assertTrue(row["expected_need"])
        row["correction_for"] = "MSG-OTHER"
        self.assertFalse(mod.requires_offer(row))
        with self.assertRaisesRegex(ValueError, "golden eligibility contradiction"):
            mod.assess(copy_cases, "bound-minimal")

    def test_fixture_rejects_duplicates_and_invalid_types(self):
        fixture = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        fixture["cases"][0]["emitted"] = "true"
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "fixtures.json"
            p.write_text(json.dumps(fixture), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "boolean type invalid"):
                mod.load_cases(p)
        fixture = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        fixture["cases"][1]["id"] = fixture["cases"][0]["id"]
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "fixtures.json"
            p.write_text(json.dumps(fixture), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate case id"):
                mod.load_cases(p)

    def test_independent_expected_metrics_are_exact(self):
        expected = json.loads((DIR / "EXPECTED-METRICS.json").read_text(encoding="utf-8"))
        self.assertEqual(expected["case_count"], len(self.cases))
        report = mod.build_report()
        actual = {item["policy"]: item["metrics"] for item in report["policies"]}
        self.assertEqual(actual, expected["metric_expectations"])

    def test_repeatability(self):
        first = json.dumps(mod.build_report(), sort_keys=True)
        second = json.dumps(mod.build_report(), sort_keys=True)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
