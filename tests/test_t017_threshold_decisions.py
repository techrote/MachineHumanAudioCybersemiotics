"""MHAC-T017: pre-authored expected claims versus logic; no listener measurements."""
from pathlib import Path
import hashlib
import importlib.util
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research" / "tangents" / "threshold-decision-warrant"
spec = importlib.util.spec_from_file_location("mhac_t017_oracle", HERE / "oracle.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


class TestThresholdClaimWarrant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = oracle.load_cases()
        cls.by_id = {c["id"]: c for c in cls.cases}

    def test_ledger_integrity_and_scope(self):
        raw = (HERE / "FICTIONAL-CASES.json").read_bytes()
        manifest = json.loads((HERE / "MANIFEST.json").read_text())
        self.assertEqual(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(), manifest["git_blob_sha1"])
        self.assertEqual(manifest["count"], 32)
        self.assertEqual(manifest["base_commit"], "423649d18c54cbf90bf7bf79d49ba69b29f03848")
        self.assertGreaterEqual(len({c["family"] for c in self.cases}), 8)

    def test_ground_truth_is_not_public_input(self):
        for c in self.cases:
            public = oracle.public_input(c)
            self.assertNotIn("ground_truth", public)
            self.assertNotIn("independent_policy_expectations", public)
            self.assertNotIn("actual_tenths", str(public))
            self.assertNotIn("world_conforming", str(public))

    def test_all_128_policy_cases_against_predeclared_claims(self):
        for c in self.cases:
            for policy in oracle.POLICIES:
                with self.subTest(case=c["id"], policy=policy):
                    actual = oracle.render(oracle.public_input(c), policy)["claim"]
                    expected = c["independent_policy_expectations"][policy]
                    self.assertEqual(actual, expected)

    def test_mutating_ground_truth_cannot_affect_any_policy(self):
        c = self.by_id["T017-002"]
        changed = dict(c, ground_truth={"world_conforming": True, "permitted_class": None})
        for policy in oracle.POLICIES:
            self.assertEqual(oracle.render(oracle.public_input(c), policy),
                             oracle.render(oracle.public_input(changed), policy))

    def test_false_accept_is_distinct_from_authority_error(self):
        c = self.by_id["T017-002"]
        self.assertFalse(c["ground_truth"]["world_conforming"])
        out = oracle.render(oracle.public_input(c), "upstream_warrant")
        scores = oracle.score(c, out)
        self.assertEqual((scores["false_accept_world"], scores["unsupported_class"]), (1, 0))

    def test_false_reject_is_distinct_from_authority_error(self):
        c = self.by_id["T017-006"]
        self.assertTrue(c["ground_truth"]["world_conforming"])
        out = oracle.render(oracle.public_input(c), "upstream_warrant")
        scores = oracle.score(c, out)
        self.assertEqual((scores["false_reject_world"], scores["unsupported_class"]), (1, 0))

    def test_same_measurement_different_rule_selection(self):
        c = self.by_id["T017-029"]
        d = self.by_id["T017-030"]
        self.assertEqual(c["measurement"]["value_tenths"], d["measurement"]["value_tenths"])
        self.assertNotEqual(c["rule"]["risk"], d["rule"]["risk"])
        self.assertEqual(oracle.render(oracle.public_input(c), "upstream_warrant")["claim"], "indeterminate")
        self.assertEqual(oracle.render(oracle.public_input(d), "upstream_warrant")["claim"], "conforming")

    def test_rule_exists_but_authority_is_missing(self):
        for identifier in ("T017-019", "T017-020", "T017-027", "T017-028"):
            c = self.by_id[identifier]
            self.assertIsNotNone(oracle.render(oracle.public_input(c), "local_rule")["claim"])
            self.assertIsNone(oracle.render(oracle.public_input(c), "upstream_warrant")["claim"])

    def test_invalid_measurement_or_binding_never_authorizes_upstream_class(self):
        for identifier in range(21, 27):
            c = self.by_id[f"T017-{identifier:03d}"]
            self.assertIsNone(oracle.render(oracle.public_input(c), "upstream_warrant")["claim"])

    def test_missing_and_inactive_rules(self):
        for identifier in range(13, 18):
            c = self.by_id[f"T017-{identifier:03d}"]
            self.assertIsNone(oracle.render(oracle.public_input(c), "upstream_warrant")["claim"])

    def test_value_only_null_baseline(self):
        for c in self.cases:
            out = oracle.render(oracle.public_input(c), "value_only")
            self.assertIsNone(out["claim"])
            self.assertFalse(out["no_action"])

    def test_no_action_is_never_inferred_from_conformity(self):
        for c in self.cases:
            out = oracle.render(oracle.public_input(c), "upstream_warrant")
            self.assertFalse(out["no_action"])
        self.assertGreater(oracle.compare()["policies"]["naive"]["unsupported_no_action"], 0)

    def test_rounding_is_separate_from_authority(self):
        for identifier in ("T017-031", "T017-032"):
            c = self.by_id[identifier]
            self.assertEqual(oracle.score(c, oracle.render(oracle.public_input(c), "naive"))
                             ["misreported_numeric_value"], 1)
            self.assertEqual(oracle.score(c, oracle.render(oracle.public_input(c), "upstream_warrant"))
                             ["misreported_numeric_value"], 0)

    def test_indeterminate_is_not_a_safe_all_clear(self):
        c = self.by_id["T017-010"]
        self.assertEqual(oracle.render(oracle.public_input(c), "upstream_warrant")["claim"], "indeterminate")
        self.assertEqual(oracle.render(oracle.public_input(c), "naive")["claim"], "conforming")

    def test_predeclared_count_and_independent_expected_totals(self):
        actual = oracle.compare()
        ledger = json.loads((HERE / "EXPECTED-COUNTS.json").read_text())
        self.assertEqual(actual["case_count"], ledger["count"])
        for name, expected in ledger["constraints"].items():
            for metric, value in expected.items():
                self.assertEqual(actual["policies"][name][metric], value)

    def test_unknown_policy_rejected(self):
        c = oracle.public_input(self.cases[0])
        with self.assertRaises(ValueError):
            oracle.render(c, "magic")

    def test_world_labels_are_explicit_not_policy_generated(self):
        for c in self.cases:
            truth = c["ground_truth"]
            self.assertEqual(truth["world_conforming"], truth["actual_tenths"] <= 500)
            self.assertFalse(truth["no_action_authorized"])
            self.assertNotIn("participants", c)


if __name__ == "__main__":
    unittest.main()
