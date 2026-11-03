"""Portable adapter: repository unittest discovery for exploratory T005 traces."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "research" / "tangents" / "continuous-state-events"
spec = importlib.util.spec_from_file_location("mhac_t005", ROOT / "replay.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestT005(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((ROOT / "STATE-TRACES.json").read_text(encoding="utf-8"))

    def test_fixture_oracles_across_four_policies(self):
        self.assertGreaterEqual(mod.run_cases(ROOT / "STATE-TRACES.json"), 12)

    def test_all_clear_requires_fresh_inactive_exact_identity(self):
        for case in self.cases:
            for policy in mod.POLICIES:
                with self.subTest(case=case["id"], policy=policy):
                    result = mod.evaluate(case, policy)
                    if result["clear_allowed"]:
                        self.assertEqual(result["truth"], "inactive")
                        self.assertEqual(case["cue"]["source_version"], case["sources"][case["target_source"]]["version"])
                        self.assertFalse(any(e["state"] == "open" and e["source_id"] == case["target_source"] for e in case["events"].values()))

    def test_silence_is_not_hazard_resolution(self):
        for case in self.cases:
            if case["playback"] in ("failed", "silenced", "ducked"):
                for policy in mod.POLICIES:
                    result = mod.evaluate(case, policy)
                    self.assertFalse(result["clear_audio"])
                    self.assertFalse(result["event_audio"])

    def test_policy_separation_and_visual_fallback(self):
        case = next(c for c in self.cases if c["id"] == "urgent-event-while-status-persists")
        self.assertFalse(mod.evaluate(case, "discrete_visual")["status_audio"])
        self.assertTrue(mod.evaluate(case, "persistent_discrete")["status_audio"])
        result = mod.evaluate(case, "ducked_hybrid")
        self.assertFalse(result["status_audio"])
        self.assertTrue(result["status_ducked"])
        self.assertTrue(result["event_audio"])
        self.assertTrue(result["event_visual"])

    def test_ack_action_completion_do_not_change_source_truth(self):
        for name in ("ack-not-recovery", "action-complete-not-recovery"):
            case = next(c for c in self.cases if c["id"] == name)
            for policy in mod.POLICIES:
                res = mod.evaluate(case, policy)
                self.assertEqual(res["truth"], "active")
                self.assertFalse(res["clear_allowed"])

    def test_fail_closed_on_bad_inputs(self):
        import copy
        case = self.cases[0]
        bad = [("playback", "invalid"), ("now_ms", True), ("now_ms", -1)]
        for key, value in bad:
            malformed = copy.deepcopy(case)
            malformed[key] = value
            with self.assertRaises(ValueError):
                mod.evaluate(malformed, "discrete_visual")
        with self.assertRaises(ValueError):
            mod.evaluate(case, "made_up_policy")


if __name__ == "__main__":
    unittest.main()
