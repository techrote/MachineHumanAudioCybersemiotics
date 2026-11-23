"""Focused tests for MHAC-X005's absent-message oracle and silence quartet."""
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave

try:
    from .silence_oracle import (
        DURATION, SAMPLE_RATE, LeaseState, World, async_counterexample,
        bec_output, build_quartet, classify_lease, heartbeat_suspicion,
        indistinguishable_at, observed_prefix, receipt, scene_samples,
        silence_window_pcm, timeout_claim_sound,
    )
except ImportError:
    from silence_oracle import (
        DURATION, SAMPLE_RATE, LeaseState, World, async_counterexample,
        bec_output, build_quartet, classify_lease, heartbeat_suspicion,
        indistinguishable_at, observed_prefix, receipt, scene_samples,
        silence_window_pcm, timeout_claim_sound,
    )


class SoundOfNothingTests(unittest.TestCase):
    def test_no_emit_and_delayed_are_same_finite_prefix(self):
        no_emit, delayed = async_counterexample(5.0)
        self.assertEqual(observed_prefix(no_emit, 5.0), ())
        self.assertEqual(observed_prefix(delayed, 5.0), ())
        self.assertTrue(indistinguishable_at(no_emit, delayed, 5.0))
        self.assertFalse(indistinguishable_at(no_emit, delayed, 11.0))

    def test_counterexample_scales_with_any_positive_horizon(self):
        for horizon in (0.1, 1.0, 9.0, 1000.0):
            a, b = async_counterexample(horizon)
            self.assertTrue(indistinguishable_at(a, b, horizon))
            self.assertLess(b.emit_time, horizon)
            self.assertGreater(b.deliver_time, horizon)

    def test_timeout_requires_explicit_delay_bound(self):
        self.assertFalse(timeout_claim_sound(
            last_possible_emit=5.0, max_delay=None, observation_time=1000.0
        ))
        self.assertFalse(timeout_claim_sound(
            last_possible_emit=5.0, max_delay=2.0, observation_time=6.99
        ))
        self.assertTrue(timeout_claim_sound(
            last_possible_emit=5.0, max_delay=2.0, observation_time=7.0
        ))

    def test_erasure_symbol_is_not_zero_or_one(self):
        self.assertEqual(bec_output(0, False), "0")
        self.assertEqual(bec_output(1, False), "1")
        self.assertEqual(bec_output(0, True), "E")
        self.assertEqual(bec_output(1, True), "E")
        self.assertNotEqual(bec_output(0, True), bec_output(0, False))
        self.assertNotEqual(bec_output(1, True), bec_output(1, False))

    def test_lease_expiry_degrades_to_unknown_not_resolved(self):
        messages = [LeaseState("ACTIVE", observed_at=1.0, valid_until=5.0)]
        self.assertEqual(classify_lease(messages, 4.99), "ACTIVE")
        self.assertEqual(classify_lease(messages, 5.0), "ACTIVE")
        self.assertEqual(classify_lease(messages, 5.01), "UNKNOWN")
        self.assertNotEqual(classify_lease(messages, 100.0), "RESOLVED")

    def test_explicit_resolution_stays_explicit(self):
        messages = [
            LeaseState("ACTIVE", observed_at=1.0, valid_until=5.0),
            LeaseState("RESOLVED", observed_at=4.0),
        ]
        self.assertEqual(classify_lease(messages, 4.0), "RESOLVED")
        self.assertEqual(classify_lease(messages, 20.0), "RESOLVED")

    def test_future_status_is_not_used_early(self):
        messages = [LeaseState("RESOLVED", observed_at=10.0)]
        self.assertEqual(classify_lease(messages, 5.0), "UNKNOWN")

    def test_timeout_heartbeat_is_suspicion_not_ground_truth(self):
        arrivals = [0.0, 1.0, 2.0]
        self.assertFalse(heartbeat_suspicion(arrivals, 2.8, 1.0, 1.5))
        self.assertTrue(heartbeat_suspicion(arrivals, 3.6, 1.0, 1.5))
        # A heartbeat arriving late would remove the practical suspicion even
        # though the earlier timeout fired; therefore this function is not a
        # truth oracle for crash status.
        late = arrivals + [3.8]
        self.assertFalse(heartbeat_suspicion(late, 3.9, 1.0, 1.5))

    def test_four_wavs_share_identical_literal_silence(self):
        quartet = build_quartet()
        self.assertEqual(len(quartet), 4)
        windows = [silence_window_pcm(data) for data in quartet.values()]
        self.assertTrue(all(w == windows[0] for w in windows[1:]))
        self.assertEqual(set(windows[0]), {0})
        self.assertEqual(len({hashlib.sha256(x).hexdigest() for x in quartet.values()}), 4)

    def test_quartet_receipt_is_self_consistent(self):
        quartet = build_quartet()
        rec = receipt(quartet)
        self.assertTrue(rec["shared_window_identical"])
        self.assertTrue(rec["shared_window_all_zero"])
        self.assertEqual(rec["sample_rate"], SAMPLE_RATE)
        self.assertEqual(rec["duration_seconds"], DURATION)
        for filename, meta in rec["files"].items():
            name = filename.removesuffix(".wav")
            self.assertEqual(meta["sha256"], hashlib.sha256(quartet[name]).hexdigest())

    def test_wav_contract(self):
        for data in build_quartet().values():
            with wave.open(io.BytesIO(data), "rb") as w:
                self.assertEqual(w.getnchannels(), 1)
                self.assertEqual(w.getsampwidth(), 2)
                self.assertEqual(w.getframerate(), SAMPLE_RATE)
                self.assertEqual(w.getnframes(), round(DURATION * SAMPLE_RATE))

    def test_scene_refuses_unknown_name(self):
        with self.assertRaises(ValueError):
            scene_samples("magic_means_resolved")

    def test_invalid_worlds_and_times_fail_closed(self):
        bad = World("bad", None, 1.0, None, "bad", "invalid")
        with self.assertRaises(ValueError):
            bad.validate()
        with self.assertRaises(ValueError):
            async_counterexample(0)
        with self.assertRaises(ValueError):
            timeout_claim_sound(
                last_possible_emit=0, max_delay=-1, observation_time=2
            )
        with self.assertRaises(ValueError):
            bec_output(2, False)

    def test_invalid_leases_fail_closed(self):
        with self.assertRaises(ValueError):
            classify_lease([LeaseState("ACTIVE", 1.0, None)], 2.0)
        with self.assertRaises(ValueError):
            classify_lease([LeaseState("MAGIC", 1.0, 2.0)], 2.0)

    def test_cli_materialises_quartet_and_counterexample(self):
        script = Path(__file__).with_name("silence_oracle.py")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            proc = subprocess.run(
                [sys.executable, str(script), "--out", str(out)],
                check=True, capture_output=True, text=True,
            )
            parsed = json.loads(proc.stdout)
            self.assertTrue(parsed["proof"]["indistinguishable"])
            self.assertTrue(parsed["proof"]["later_distinguishable"])
            expected = {
                "explicit_resolved.wav", "channel_failed.wav",
                "alert_delayed.wav", "intentional_rest.wav",
                "receipt.json", "trace-counterexample.json",
            }
            self.assertEqual({p.name for p in out.iterdir()}, expected)
            rec = json.loads((out / "receipt.json").read_text(encoding="utf-8"))
            self.assertTrue(rec["shared_window_all_zero"])
            self.assertTrue(rec["shared_window_identical"])


if __name__ == "__main__":
    unittest.main()
