"""Independent T010 fictional dispatch policy regression tests."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / 'research/tangents/freshness-action-deadlines/oracle.py'
spec = importlib.util.spec_from_file_location('t010_oracle', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestT010SyntheticPolicies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {case['id']: case for case in module.load_cases()}

    def report(self, key, policy):
        return module.dispatch(self.cases[key], policy)

    def test_complete_independent_fictional_truth_ledger(self):
        self.assertEqual(len(self.cases), 30)
        self.assertEqual(sum(len(x['truth']['required']) for x in self.cases.values()), 26)
        self.assertTrue(all(x['fictional'] for x in self.cases.values()))
        self.assertEqual(len(module.run_all(list(self.cases.values()))), 30 * len(module.POLICIES))

    def test_event_deadline_deferral_fails_but_override_passes(self):
        self.assertEqual(self.report('T04', 'fixed_deferral')['expired_event_dispatch'], 1)
        self.assertEqual(self.report('T04', 'task_boundary')['missed_required'], 0)
        self.assertEqual(self.report('T16', 'task_boundary')['missed_required'], 0)
        self.assertEqual(self.report('T17', 'task_boundary')['missed_required'], 0)

    def test_latest_wins_loses_durable_obligation(self):
        self.assertGreater(self.report('T24', 'latest_wins_naive')['missed_required'], 0)
        self.assertEqual(self.report('T24', 'protected_coalesce')['missed_required'], 0)
        self.assertGreater(self.report('T14', 'latest_wins_naive')['missed_required'], 0)

    def test_status_replacement_keeps_separate_semantic_groups(self):
        self.assertEqual(self.report('T02', 'protected_coalesce')['discarded'], 1)
        self.assertEqual(self.report('T03', 'protected_coalesce')['discarded'], 0)
        self.assertEqual(self.report('T27', 'protected_coalesce')['notifications'], 2)

    def test_release_and_ack_are_not_equivalent(self):
        self.assertEqual(self.report('T08', 'fixed_deferral')['obsolete_event_dispatch'], 1)
        self.assertEqual(self.report('T09', 'fixed_deferral')['obsolete_event_dispatch'], 1)
        self.assertEqual(self.report('T10', 'immediate_fifo')['timely_authorized'], 1)
        self.assertEqual(self.report('T28', 'protected_coalesce')['timely_authorized'], 1)

    def test_wrong_actor_and_unknown_states_are_not_false_success(self):
        self.assertEqual(self.report('T11', 'fixed_deferral')['wrong_actor_dispatch'], 1)
        self.assertEqual(self.report('T11', 'immediate_fifo')['timely_authorized'], 1)
        for case_id, key in [('T18', 'unknown_deadline'), ('T19', 'unknown_authority'), ('T20', 'unknown_clock')]:
            r = self.report(case_id, 'immediate_fifo')
            self.assertEqual(r[key], 1)
            self.assertEqual(r['missed_required'], 1)

    def test_duplicate_packets_counted_not_silent_completion(self):
        self.assertEqual(self.report('T15', 'immediate_fifo')['duplicate_action_risk'], 1)
        self.assertEqual(self.report('T15', 'immediate_fifo')['timely_authorized'], 1)

    def test_no_inferred_human_outcome_and_status_age_only_proxy(self):
        report = self.report('T21', 'fixed_deferral')
        self.assertEqual(report['stale_status'], 1)
        self.assertEqual(report['mean_status_sample_latency'], 3)
        self.assertNotIn('comprehension', report)
        self.assertNotIn('participant_response_time', report)

    def test_malformed_truth_labels_fail_closed(self):
        path = MODULE_PATH.parent / 'FICTIONAL-TRACES.json'
        original = json.loads(path.read_text())
        original['cases'][3]['truth']['required'] = []
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            fixture = pathlib.Path(tmp) / 'invalid.json'
            fixture.write_text(json.dumps(original))
            with self.assertRaises(ValueError):
                module.load_cases(fixture)


if __name__ == '__main__':
    unittest.main()
