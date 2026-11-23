"""Synthetic numerical tests for MHAC-T018's linear interaction-feedback analogy."""
from dataclasses import replace
import math
import unittest

try:
    from .feedback_toy import Coupling, PRESETS, analytical_pressure, output_report, simulate
except ImportError:
    from feedback_toy import Coupling, PRESETS, analytical_pressure, output_report, simulate


class AffectiveFeedbackToyTests(unittest.TestCase):
    def test_gain_formula(self):
        p = PRESETS["amplifying"]
        self.assertAlmostEqual(p.gain, .72 + .6 * .9 * .7)
        self.assertGreater(p.gain, 1)

    def test_stable_vs_unstable_distinction(self):
        self.assertEqual(PRESETS["amplifying"].classification(), "unstable_if_perturbed")
        for name in ("bounded", "decoupled", "helpful"):
            self.assertEqual(PRESETS[name].classification(), "asymptotically_stable")

    def test_analytical_equals_iterative(self):
        for p in PRESETS.values():
            trace = simulate(p, 24)
            for row in trace:
                self.assertAlmostEqual(
                    row["pressure"], analytical_pressure(p, row["tick"]), places=8
                )

    def test_abrupt_responses_not_needed_for_feedback(self):
        # This model's feedback is continuous and deterministic; no emotional
        # state inference, model panic, or user intention is involved.
        p = PRESETS["amplifying"]
        trace = simulate(p, 20)
        self.assertGreater(trace[-1]["pressure"], trace[0]["pressure"])
        self.assertGreater(trace[-1]["failure_cost_signal"], trace[0]["failure_cost_signal"])

    def test_decoupling_reduces_amplification(self):
        unstable = simulate(PRESETS["amplifying"], 22)
        decoupled = simulate(PRESETS["decoupled"], 22)
        self.assertGreater(unstable[-1]["pressure"], decoupled[-1]["pressure"])

    def test_helpful_response_negative_coupling_is_allowed(self):
        helpful = PRESETS["helpful"]
        neutral = replace(helpful, response_to_failure=0.0)
        self.assertLess(helpful.gain, neutral.gain)
        self.assertLess(simulate(helpful, 20)[-1]["pressure"],
                        simulate(neutral, 20)[-1]["pressure"])

    def test_unstable_gain_without_seed_can_stay_zero(self):
        p = replace(PRESETS["amplifying"], background_pressure=0.0,
                    baseline_failure=0.0, initial_pressure=0.0)
        trace = simulate(p, 15)
        self.assertEqual([x["pressure"] for x in trace], [0.0] * 15)
        self.assertEqual(p.classification(), "unstable_if_perturbed")

    def test_boundary_one_is_not_called_exponentially_unstable(self):
        p = Coupling("boundary", .5, .5, 1.0, 1.0, .1, .1, .1)
        self.assertEqual(p.classification(), "marginal_or_boundary")
        self.assertIsNone(p.fixed_point())
        trace = simulate(p, 4)
        self.assertAlmostEqual(trace[-1]["pressure"], .1 + 3 * .15)

    def test_invalid_coefficients_fail_closed(self):
        with self.assertRaises(ValueError):
            simulate(replace(PRESETS["helpful"], retention=1.4))
        with self.assertRaises(ValueError):
            simulate(replace(PRESETS["helpful"], response_to_failure=float("nan")))
        with self.assertRaises(ValueError):
            simulate(replace(PRESETS["helpful"], response_sensitivity=-.3))
        with self.assertRaises(ValueError):
            simulate(PRESETS["helpful"], steps=0)

    def test_report_identifies_its_synthetic_status(self):
        report = output_report(PRESETS["bounded"], 4)
        self.assertEqual(report["status"], "synthetic_only")
        self.assertEqual(report["schema"], "mhac-t018-feedback-v1")
        self.assertEqual(len(report["trace"]), 4)
        self.assertIn("No measurement", report["warning"])

    def test_parameter_sign_not_a_real_error_probability(self):
        p = replace(PRESETS["helpful"], response_to_failure=-5)
        trace = simulate(p, 2)
        self.assertLess(trace[0]["failure_cost_signal"], 0)
        # Signed cost signals are permitted; these are *not* measured error probabilities.


if __name__ == "__main__":
    unittest.main()
