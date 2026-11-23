#!/usr/bin/env python3
"""Tests for MHAC-X001's synthetic circle-mode observation and sound experiment."""
import io
import json
import math
import struct
import unittest
import wave

try:
    from .mode_alias_lab import (
        make_experiment, make_stereo_wav, max_abs_difference, mode_value, sensor_values
    )
except ImportError:
    from mode_alias_lab import (
        make_experiment, make_stereo_wav, max_abs_difference, mode_value, sensor_values
    )


class SolecismWitnessTests(unittest.TestCase):
    def test_exact_equispaced_alias(self):
        for count in (5, 8, 11, 17):
            for base in (0, 1, 2, 3):
                a = sensor_values(base, count)
                b = sensor_values(base + count, count)
                self.assertLess(max_abs_difference(a, b), 1e-12)

    def test_multiple_winding_alias(self):
        for winding in (1, 2, 3, 10):
            self.assertLess(
                max_abs_difference(sensor_values(2, 8),
                                   sensor_values(2 + winding * 8, 8)),
                1e-12,
            )

    def test_shifted_observer_separates_default_pair(self):
        delta = math.pi / 16
        low = sensor_values(2, 8, delta)
        high = sensor_values(10, 8, delta)
        self.assertGreater(max_abs_difference(low, high), 0.5)

    def test_nonaliasing_pair(self):
        self.assertGreater(
            max_abs_difference(sensor_values(2, 8), sensor_values(3, 8)),
            0.25,
        )

    def test_symmetric_real_cosine_has_extra_aliases(self):
        # Cosine's even symmetry also aliases mode 2 with mode 8-2.
        self.assertLess(
            max_abs_difference(sensor_values(2, 8), sensor_values(6, 8)),
            1e-12,
        )

    def test_literal_zero_mode(self):
        self.assertEqual(sensor_values(0, 8), (1.0,) * 8)

    def test_radius_changes_laplacian_eigenvalues_not_probe_alias(self):
        for radius in (0.5, 1.0, 2.0):
            receipt, _, _, _ = make_experiment(radius=radius, duration=0.05)
            self.assertAlmostEqual(
                receipt["eigenvalue_a_of_minus_d2_dy2"], (2 / radius) ** 2
            )
            self.assertAlmostEqual(
                receipt["eigenvalue_b_of_minus_d2_dy2"], (10 / radius) ** 2
            )
            self.assertLess(receipt["equispaced_max_abs_error"], 1e-12)

    def test_receipt_and_counts(self):
        receipt, exact, shifted, wav = make_experiment(duration=0.125)
        self.assertEqual(receipt["sensor_count"], 8)
        self.assertEqual(receipt["mode_a"], 2)
        self.assertEqual(receipt["mode_b"], 10)
        self.assertEqual(len(exact), 8)
        self.assertEqual(len(shifted), 8)
        self.assertEqual(receipt["tone_a_hz"], 110)
        self.assertEqual(receipt["tone_b_hz"], 550)
        self.assertIn("sha256", receipt["wav_sha256"])
        self.assertEqual(receipt["validity"], {
            "discrete_alias": True,
            "shift_breaks_pair": True,
            "mode_eigenvalues_distinct": True,
        })
        self.assertEqual(json.loads(json.dumps(receipt))["schema"], 1)
        self.assertTrue(wav.startswith(b"RIFF"))

    def test_wav_header_and_channels(self):
        wav = make_stereo_wav(2, 10, sample_rate=24000, duration=0.2)
        with wave.open(io.BytesIO(wav), "rb") as w:
            self.assertEqual(w.getnchannels(), 2)
            self.assertEqual(w.getsampwidth(), 2)
            self.assertEqual(w.getframerate(), 24000)
            self.assertEqual(w.getnframes(), 4800)
            data = w.readframes(w.getnframes())
        pairs = [struct.unpack_from("<hh", data, i) for i in range(0, len(data), 4)]
        self.assertTrue(all(-32767 <= a <= 32767 and -32767 <= b <= 32767
                            for a, b in pairs))
        self.assertNotEqual([x[0] for x in pairs], [x[1] for x in pairs])
        self.assertGreater(max(abs(a) for a, b in pairs), 100)
        self.assertGreater(max(abs(b) for a, b in pairs), 100)

    def test_repeatability(self):
        self.assertEqual(
            make_stereo_wav(2, 10, duration=0.1),
            make_stereo_wav(2, 10, duration=0.1),
        )
        a = make_experiment(duration=0.1)[0]
        b = make_experiment(duration=0.1)[0]
        self.assertEqual(a, b)

    def test_guard_nyquist(self):
        with self.assertRaises(ValueError):
            make_stereo_wav(2, 10, sample_rate=8000, revolutions_per_second=600)

    def test_guard_bad_inputs(self):
        for count in (-1, 0, 1, 2):
            with self.assertRaises(ValueError):
                sensor_values(2, count)
        with self.assertRaises(ValueError):
            mode_value(-1, 0)
        with self.assertRaises(ValueError):
            mode_value(2, float("nan"))
        with self.assertRaises(ValueError):
            make_experiment(radius=0)
        with self.assertRaises(ValueError):
            make_experiment(low_mode=2, sensors=2)
        with self.assertRaises(ValueError):
            make_stereo_wav(2, 10, duration=0)


if __name__ == "__main__":
    unittest.main()
