"""T015 synthetic evidence-independence negative and mutation controls."""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "research" / "tangents" / "alarm-evidence-independence"
spec = importlib.util.spec_from_file_location("mhac_t015_oracle", DIR / "oracle.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot import the isolated T015 oracle")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class T015EvidenceIndependence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = mod.load_cases()
        cls.by_id = {c["id"]: c for c in cls.cases}

    def test_case_counts_controls_and_disjoint_truth(self):
        self.assertEqual(len(self.cases), 40)
        self.assertGreaterEqual(sum(c["case_kind"] == "negative" for c in self.cases), 12)
        self.assertEqual({c["dependency_relation"] for c in self.cases}, set(mod.RELATIONS))
        for c in self.cases:
            self.assertEqual(
                sorted(c["gold"]["required_obligations"]),
                sorted({a["event_id"] + "/" + a["action_id"]
                        for a in c["alerts"] if mod.eligible(a)}))

    def test_reproduces_predeclared_shadow_metrics(self):
        mod.check_expected(mod.report())
        self.assertEqual(mod.report(), mod.report())

    def test_known_shared_observation_cannot_be_corroboration(self):
        for id in ("T015-001", "T015-002", "T015-003"):
            c = self.by_id[id]
            self.assertEqual(mod.classify(c, "lineage"), "shared")
            self.assertEqual(mod.classify(c, "proximity"), "verified_independent")
        self.assertEqual(mod.classify(self.by_id["T015-004"], "proximity"), "unasserted")

    def test_nominal_device_ids_do_not_prove_independence(self):
        self.assertEqual(mod.classify(self.by_id["T015-002"], "device_id"), "verified_independent")
        self.assertEqual(mod.classify(self.by_id["T015-022"], "device_id"), "shared")
        self.assertEqual(mod.classify(self.by_id["T015-022"], "lineage"), "verified_independent")

    def test_two_actions_from_one_observation_are_not_discarded(self):
        for id in ("T015-005", "T015-013", "T015-033"):
            c = self.by_id[id]
            self.assertEqual(len(mod.deliver(c, "lineage")), 2)
            self.assertEqual(len(mod.deliver(c, "separate")), 2)

    def test_same_device_independent_second_event_not_suppressed(self):
        c = self.by_id["T015-023"]
        self.assertEqual(len(mod.deliver(c, "device_id")), 1)
        self.assertEqual(len(mod.deliver(c, "lineage")), 2)
        self.assertEqual(len(mod.deliver(c, "separate")), 2)

    def test_true_independent_same_action_preserves_two_observations(self):
        c = self.by_id["T015-021"]
        self.assertEqual(len(mod.deliver(c, "lineage")), 2)
        self.assertEqual(len(mod.deliver(c, "separate")), 2)
        self.assertEqual(len(mod.deliver(c, "proximity")), 1)

    def test_unknown_is_not_a_zero_or_a_verified_second_source(self):
        for id in ("T015-031", "T015-032", "T015-033"):
            c = self.by_id[id]
            self.assertEqual(mod.classify(c, "lineage"), "unknown")
            self.assertTrue(any(a["upstream_lineage_id"] is None for a in c["alerts"]))

    def test_negative_authority_truth_and_expiry_controls(self):
        for id in ("T015-008", "T015-009", "T015-010",
                   "T015-016", "T015-017", "T015-028", "T015-029",
                   "T015-035", "T015-036", "T015-037", "T015-039"):
            c = self.by_id[id]
            self.assertEqual(len(mod.deliver(c, "separate")), 1, id)
        for id in ("T015-007", "T015-020", "T015-030", "T015-040"):
            self.assertEqual(mod.deliver(self.by_id[id], "separate"), [])

    def test_lineage_only_mutation_does_not_change_acoustic_heuristic(self):
        c = copy.deepcopy(self.by_id["T015-021"])
        initial = mod.classify(c, "proximity")
        c["dependency_relation"] = "common_cause"
        c["alerts"][1]["upstream_lineage_id"] = c["alerts"][0]["upstream_lineage_id"]
        c["gold"]["independent_support"] = "shared"
        c["gold"]["independent_eligible_message_ids"] = []
        self.assertEqual(mod.classify(c, "proximity"), initial)
        self.assertEqual(mod.classify(c, "lineage"), "shared")

    def test_proximity_only_mutation_does_not_change_lineage(self):
        c = copy.deepcopy(self.by_id["T015-021"])
        original = mod.classify(c, "lineage")
        c["alerts"][1]["emitted_at_s"] = 122
        c["delivery_proximity"] = "far"
        self.assertEqual(mod.classify(c, "lineage"), original)
        self.assertEqual(mod.classify(c, "proximity"), "unasserted")
        self.assertEqual(len(mod.deliver(c, "lineage")), 2)

    def test_independence_metadata_contradictions_rejected(self):
        d = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        d["cases"][20]["alerts"][1]["upstream_lineage_id"] = "LINE-A"
        with self.assertRaisesRegex(ValueError, "verified-independence metadata"):
            mod.check_cases(d)

    def test_duplicate_message_case_and_truth_contradictions_rejected(self):
        d = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        d["cases"][0]["alerts"][1]["message_id"] = "M1"
        with self.assertRaisesRegex(ValueError, "duplicate message id"):
            mod.check_cases(d)
        d = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        d["cases"][1]["id"] = d["cases"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate or malformed case"):
            mod.check_cases(d)
        d = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        d["cases"][0]["alerts"][1]["event_truth"] = "false"
        with self.assertRaisesRegex(ValueError, "one world event"):
            mod.check_cases(d)

    def test_author_gold_is_not_relabelled_by_policy(self):
        d = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        d["cases"][4]["gold"]["required_obligations"].remove("E1/A2")
        with self.assertRaisesRegex(ValueError, "gold obligations contradict"):
            mod.check_cases(d)

    def test_unknown_obligation_remains_nonrequired(self):
        d = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        d["cases"][1]["alerts"][1]["action_obligation"] = "unknown"
        # First report remains independently eligible, with the same
        # authored E1/A1 obligation; unknown does not become "required".
        mod.check_cases(d)
        c = d["cases"][1]
        self.assertFalse(mod.eligible(c["alerts"][1]))
        self.assertEqual(len(mod.deliver(c, "separate")), 1)

    def test_extra_hidden_lineage_and_gold_fields_are_rejected(self):
        d = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        d["cases"][0]["alerts"][0]["secret_evidence_lineage"] = "LINE-Z"
        with self.assertRaisesRegex(ValueError, "hidden or missing alert provenance"):
            mod.check_cases(d)
        d = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        d["cases"][0]["gold"]["inferred_from_policy"] = True
        with self.assertRaisesRegex(ValueError, "hidden or missing gold label"):
            mod.check_cases(d)

    def test_boolean_and_unknown_input_validation(self):
        d = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        d["cases"][0]["alerts"][0]["deadline_s"] = True
        with self.assertRaisesRegex(ValueError, "integer time"):
            mod.check_cases(d)
        d = json.loads(mod.FIXTURE.read_text(encoding="utf-8"))
        d["cases"][30]["dependency_relation"] = "verified_independent"
        with self.assertRaisesRegex(ValueError, "verified-independence metadata"):
            mod.check_cases(d)

    def test_manifest_hashes(self):
        mod.check_sha_manifest()

    def test_null_nonaggregation_and_burden_visible(self):
        m = mod.report()["policies"]
        self.assertEqual(m["separate"]["false_corroborations"], 0)
        self.assertEqual(m["separate"]["required_actions_missed"], 0)
        self.assertEqual(m["lineage"]["required_actions_missed"], 0)
        self.assertGreater(m["lineage"]["word_tokens_proxy"], m["separate"]["word_tokens_proxy"])
        self.assertGreater(m["proximity"]["false_corroborations"], 0)
        self.assertGreater(m["device_id"]["independent_eligible_alerts_suppressed"], 0)


if __name__ == "__main__":
    unittest.main()
