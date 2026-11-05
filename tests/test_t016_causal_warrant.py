"""No human measurements: exact tests of a fictional causal-warrant oracle."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research" / "tangents" / "causal-claim-warrant"
spec = importlib.util.spec_from_file_location("causal_warrant_t016", HERE / "oracle.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class CausalWarrantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = model.load_cases()
        cls.by_id = {c["id"]: c for c in cls.cases}

    def test_fixture_integrity_against_precommitted_git_blob(self):
        raw = (HERE / "FICTIONAL-CASES.json").read_bytes()
        digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        manifest = json.loads((HERE / "MANIFEST.json").read_text())
        self.assertEqual(digest, manifest["cases_git_blob_sha1"])
        self.assertEqual(manifest["case_count"], 32)
        self.assertEqual(manifest["base_commit"], "423649d18c54cbf90bf7bf79d49ba69b29f03848")

    def test_distinct_truth_independent_of_policy(self):
        self.assertEqual(len(self.cases), 32)
        self.assertEqual(len({c["family"] for c in self.cases}), 8)
        self.assertEqual(sum(c["ground_truth"]["warranted_action_offer"] for c in self.cases), 4)
        self.assertEqual(sum(c["ground_truth"]["warranted_cause"] is not None for c in self.cases), 16)

    def test_no_truth_leakage_into_policy(self):
        c = self.by_id["T016-002"]
        public = model.public_input(c)
        self.assertNotIn("ground_truth", public)
        self.assertNotIn("actual_cause", str(public))
        a = model.render(public, "naive")
        tampered = dict(c, ground_truth={"actual_cause": "feed"})
        self.assertEqual(a, model.render(model.public_input(tampered), "naive"))

    def test_same_observation_different_causes_defeats_naive(self):
        a = self.by_id["T016-001"]
        b = self.by_id["T016-002"]
        self.assertEqual(a["observation"]["anomaly"], b["observation"]["anomaly"])
        self.assertNotEqual(a["ground_truth"]["actual_cause"], b["ground_truth"]["actual_cause"])
        self.assertEqual(model.render(model.public_input(a), "naive")["asserted_cause"],
                         model.render(model.public_input(b), "naive")["asserted_cause"])
        self.assertEqual(model.score(b, model.render(model.public_input(b), "naive"))["factually_wrong_cause"], 1)

    def test_lucky_guess_still_lacks_causal_warrant(self):
        c = self.by_id["T016-001"]
        self.assertEqual(c["ground_truth"]["actual_cause"], c["hypothesis"]["favored"])
        self.assertEqual(model.score(c, model.render(model.public_input(c), "naive"))["unsupported_cause"], 1)

    def test_bad_observation_rejects_diagnosis(self):
        for c in self.cases:
            if not c["observation"]["valid"]:
                result = model.render(model.public_input(c), "warranted")
                self.assertFalse(result["observation_claimed"])
                self.assertIsNone(result["asserted_cause"])
                self.assertFalse(result["offered_action"])

    def test_stale_and_conflicting_tests_are_not_warrant(self):
        for c in self.cases:
            if c["test"]["kind"] in ("stale", "conflicting", "ambiguous"):
                result = model.render(model.public_input(c), "warranted")
                self.assertIsNone(result["asserted_cause"])

    def test_discriminating_test_changes_cause_claim(self):
        a = self.by_id["T016-001"]
        b = self.by_id["T016-005"]
        self.assertEqual(a["observation"]["anomaly"], b["observation"]["anomaly"])
        self.assertIsNone(model.render(model.public_input(a), "warranted")["asserted_cause"])
        self.assertEqual(model.render(model.public_input(b), "warranted")["asserted_cause"], "feed")

    def test_cause_warrant_not_action_warrant(self):
        for identifier in ("T016-021", "T016-022", "T016-023", "T016-024",
                           "T016-025", "T016-026", "T016-031", "T016-032"):
            c = self.by_id[identifier]
            output = model.render(model.public_input(c), "warranted")
            self.assertIsNotNone(output["asserted_cause"])
            self.assertFalse(output["offered_action"])

    def test_four_positive_action_controls(self):
        ids = ["T016-017", "T016-018", "T016-019", "T016-020"]
        self.assertTrue(all(model.render(model.public_input(self.by_id[i]), "warranted")["offered_action"]
                            for i in ids))

    def test_truth_labels_consistent_with_stated_toy_assumptions(self):
        for c in self.cases:
            t = c["test"]
            cause = t["supports"] if (c["observation"]["valid"] and
                    t["kind"] == "diagnostic" and t["current"]) else None
            self.assertEqual(c["ground_truth"]["warranted_cause"], cause)
            e = c["intervention"]
            allowed = bool(cause and e["effect_evidence"] == "validated"
                           and e["actor_authorized"] and e["mode_permits"] and e["deadline_feasible"])
            self.assertEqual(c["ground_truth"]["warranted_action_offer"], allowed)

    def test_policy_error_vs_abstention_separated(self):
        p = model.compare(self.cases)["policies"]
        self.assertGreater(p["naive"]["unsupported_cause"], 0)
        self.assertGreater(p["naive"]["unsupported_action_offer"], 0)
        for name in ("state_only", "alternatives", "warranted"):
            self.assertEqual(p[name]["unsupported_cause"], 0)
            self.assertEqual(p[name]["unsupported_action_offer"], 0)
        self.assertGreater(p["state_only"]["withheld_warranted_diagnosis"], 0)
        self.assertEqual(p["warranted"]["withheld_warranted_diagnosis"], 0)
        self.assertEqual(p["warranted"]["withheld_warranted_action"], 0)

    def test_minimal_state_only_is_not_automatically_inferior(self):
        p = model.compare(self.cases)["policies"]
        self.assertEqual(p["state_only"]["unsupported_cause"], p["warranted"]["unsupported_cause"])
        self.assertEqual(p["state_only"]["unsupported_action_offer"],
                         p["warranted"]["unsupported_action_offer"])
        self.assertLess(p["state_only"]["word_tokens"], p["warranted"]["word_tokens"])

    def test_unknown_policy_rejected(self):
        with self.assertRaises(ValueError):
            model.render(model.public_input(self.cases[0]), "magical_causal_solver")

    def test_no_empirical_rates_or_inferred_listener_state(self):
        self.assertEqual(model.compare(self.cases)["kind"], "constructed_symbolic_only")
        for case in self.cases:
            self.assertNotIn("listener_response", case)
            self.assertNotIn("participant", case)
            self.assertNotIn("confidence", case)


if __name__ == "__main__":
    unittest.main()
