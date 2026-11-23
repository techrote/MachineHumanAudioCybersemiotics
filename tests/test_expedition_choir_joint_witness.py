"""Tests for the independent finite witness expedition."""
import importlib.util
from pathlib import Path
import io
import unittest
import wave

FILE = Path(__file__).resolve().parents[1] / "research/expeditions/choir-that-cannot-meet/choir.py"
SPEC = importlib.util.spec_from_file_location("choir_joint_witness", FILE)
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)


class JointWitnessTests(unittest.TestCase):
    def test_parity_all_proper_moments(self):
        for n in range(2, 13):
            a, b = (C.moments(n, C.parity_hist(n, p)) for p in (0, 1))
            self.assertEqual(a[:-1], b[:-1])
            self.assertEqual({a[-1], b[-1]}, {0, 1})
            self.assertEqual(C.bounds(n, a[:-1]), (0, 1))
            for s, v in enumerate(a[:-1]):
                self.assertEqual(v, 1 << (n - s.bit_count() - 1))

    def test_exhaustive(self):
        receipt = C.exhaustive()
        self.assertEqual(receipt["histograms"], 1287)
        self.assertEqual(receipt["summary_groups"], 1278)
        self.assertEqual(receipt["ambiguous_groups"], 9)

    def test_scope_reversal(self):
        m = C.moments(3, C.parity_hist(3, 0))
        self.assertTrue(all(m[s] > 0 for s in (1, 2, 4)))
        self.assertTrue(all(m[s] > 0 for s in (3, 5, 6)))
        self.assertEqual(m[7], 0)

    def test_guaranteed_and_impossible(self):
        self.assertEqual(C.status(2, (3, 3, 2)), "GUARANTEED_EXISTENCE")
        self.assertEqual(C.bounds(2, (3, 3, 2)), (2, 2))
        self.assertEqual(C.status(2, (3, 0, 2)), "IMPOSSIBLE")
        self.assertEqual(C.status(2, (3, 2, 2)), "GUARANTEED_EXISTENCE")
        self.assertEqual(C.bounds(2, (3, 2, 2)), (1, 2))
        self.assertEqual(C.status(2, (3, 1, 1)), "UNDETERMINED")
        self.assertEqual(C.status(2, (0, 0, 0)), "IMPOSSIBLE")

    def test_iterator_and_single_constraint(self):
        self.assertEqual(C.reconstruct(2, iter((3, 1, 1)), 1), (2, 0, 0, 1))
        self.assertEqual(C.bounds(1, (3,)), (0, 3))
        self.assertEqual(C.bounds(1, (0,)), (0, 0))

    def test_invalid(self):
        for n, p in [(2, (1, 2, 0)), (2, (2, -1, 1)), (2, (2, True, 1)),
                     (2, (3, 1)), (0, ()), (13, ())]:
            with self.assertRaises(ValueError):
                C.bounds(n, p)
        with self.assertRaises(ValueError):
            C.reconstruct(2, (3, 1, 1), 2)
        with self.assertRaises(ValueError):
            C.reconstruct(2, (3, 1, 1), True)
        # Pairwise numbers are individually plausible but jointly impossible.
        with self.assertRaises(ValueError):
            C.bounds(3, (3, 1, 1, 1, 1, 1, 0))

    def test_audio(self):
        receipt, audio = C.experiment()
        self.assertEqual(audio["proper_even"], audio["proper_odd"])
        self.assertNotEqual(audio["full_even"], audio["full_odd"])
        for k, data in audio.items():
            with wave.open(io.BytesIO(data), "rb") as w:
                self.assertEqual((w.getnchannels(), w.getsampwidth(), w.getframerate()), (1,2,16000))
                self.assertEqual(w.getnframes(), (7 if k.startswith("proper") else 8)*1600)
        print("CHOIR_RECEIPT", receipt)
