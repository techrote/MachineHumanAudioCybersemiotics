"""Isolated truth-table and cost invariants for exploratory T002 rehearsal."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'research' / 'tangents' / 'epistemic-calibration' / 'rehearsal.py'
spec = importlib.util.spec_from_file_location('mhac_t002_rehearsal', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestEpistemicCalibration(unittest.TestCase):
    def test_grid_and_nonnegative_costs(self):
        cases = module.sweep()
        self.assertEqual(len(cases), 24)
        for case in cases:
            self.assertTrue(case['synthetic'])
            self.assertAlmostEqual(sum(z['observation_probability'] for z in case['observations'].values()), 1)
            losses = case['expected_loss']
            self.assertTrue(all(v >= 0 for v in losses.values()))
            self.assertLessEqual(losses['bayes'], losses['alarm_compliance'] + 1e-8)
            self.assertLessEqual(losses['selective_verify'], losses['bayes'] + 1e-8)
            self.assertLessEqual(losses['selective_verify'], losses['forced_verify'] + 1e-8)

    def test_ppv_is_not_sensitivity(self):
        row = module.evaluate(.02, .9, .4, 5, 2)
        self.assertLess(row['alert_ppv'], .05)
        self.assertNotEqual(row['alert_ppv'], row['hit'])

    def test_alarm_compliance_can_worsen_loss(self):
        row = module.evaluate(.02, .75, .35, 5, 3)
        self.assertGreater(row['expected_loss']['alarm_compliance'], row['expected_loss']['bayes'])

    def test_check_can_help(self):
        row = module.evaluate(.2, .8, .2, 8, 2, check_hit=.99,
                              check_false=.01, check_cost=0, delay_cost=0)
        self.assertLess(row['expected_loss']['forced_verify'], row['expected_loss']['bayes'])

    def test_check_delay_can_harm(self):
        row = module.evaluate(.5, .8, .1, 8, 1, check_hit=.9,
                              check_false=.1, check_cost=.5, delay_cost=2)
        self.assertGreater(row['expected_loss']['forced_verify'], row['expected_loss']['bayes'])

    def test_safe_zero_probability_observation(self):
        row = module.evaluate(0, 0, 0, 5, 1)
        self.assertIsNone(row['alert_ppv'])
        self.assertEqual(row['observations']['alert']['bayes_action'], 'unobserved')

    def test_all_states_have_valid_mass(self):
        for p in (0, 1):
            row = module.evaluate(p, 1, 0, 3, 1)
            self.assertAlmostEqual(sum(v['observation_probability'] for v in row['observations'].values()), 1)

    def test_rejects_invalid_hypotheses(self):
        for override in ({'prevalence': -0.1}, {'hit': 1.1}, {'false_alarm': float('nan')},
                         {'delay_cost': float('inf')}, {'check_cost': -1}, {'miss_cost': -1},
                         {'prevalence': True}):
            values = dict(prevalence=.1, hit=.9, false_alarm=.2, miss_cost=5, false_action_cost=1)
            values.update(override)
            with self.subTest(override=override), self.assertRaises(ValueError):
                module.evaluate(**values)

    def test_equal_consequence_cost_tie_ignores(self):
        loss, action = module.minimum_loss(.5, .5, 1, 1)
        self.assertEqual((loss, action), (.5, 'ignore'))


if __name__ == '__main__':
    unittest.main()
