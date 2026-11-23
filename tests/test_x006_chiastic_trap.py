"""X006 exact finite-state, negative-control and deterministic-audio tests."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import wave

EXPEDITION = Path(__file__).resolve().parents[1] / "research" / "expeditions" / "chiastic-trap"
sys.path.insert(0, str(EXPEDITION))
import chiastic_lab as lab


class ChiasticTrapTests(unittest.TestCase):
    def test_token_level_palindrome_is_only_syntax(self):
        self.assertTrue(lab.is_palindrome(lab.CHI))
        self.assertFalse(lab.is_palindrome(("A", "A", "B", "B")))
        self.assertTrue(lab.is_palindrome(tuple()))
        self.assertTrue(lab.is_palindrome(("A",)))

    def test_two_involutions_are_noncommuting(self):
        for action in lab.INVOLUTIVE_ACTIONS.values():
            self.assertTrue(lab.involution(action))
        self.assertFalse(lab.commute(lab.INVOLUTIVE_ACTIONS))
        self.assertNotEqual(
            lab.effects(("A", "B"), lab.INVOLUTIVE_ACTIONS),
            lab.effects(("B", "A"), lab.INVOLUTIVE_ACTIONS),
        )

    def test_abba_closes_every_state_with_two_involutions(self):
        self.assertEqual(lab.effects(lab.CHI, lab.INVOLUTIVE_ACTIONS), (0, 1, 2))
        self.assertTrue(lab.is_identity(lab.CHI, lab.INVOLUTIVE_ACTIONS))
        for state in range(3):
            self.assertEqual(lab.execute(lab.CHI, lab.INVOLUTIVE_ACTIONS, state), state)

    def test_abba_does_not_close_under_noninvolutive_a(self):
        self.assertFalse(lab.involution(lab.NONINVOLUTIVE_ACTIONS["A"]))
        self.assertFalse(lab.is_identity(lab.CHI, lab.NONINVOLUTIVE_ACTIONS))
        self.assertEqual(lab.effects(lab.CHI, lab.NONINVOLUTIVE_ACTIONS), (2, 0, 1))
        self.assertEqual(lab.state_history(lab.CHI, lab.NONINVOLUTIVE_ACTIONS, 0)[-1], 2)

    def test_same_codebook_can_close_one_initial_state_but_not_others(self):
        actions = lab.CONDITIONAL_ACTIONS
        self.assertEqual(lab.effects(lab.CHI, actions), (2, 0, 1, 3))
        self.assertNotEqual(lab.execute(lab.CHI, actions, 0), 0)
        self.assertEqual(lab.execute(lab.CHI, actions, 3), 3)
        self.assertFalse(lab.is_identity(lab.CHI, actions))
        self.assertEqual(
            lab.provenance_record("conditional", actions)["wav_sha256"],
            lab.provenance_record("closed", lab.INVOLUTIVE_ACTIONS)["wav_sha256"],
        )

    def test_abab_is_not_abba_when_noncommuting(self):
        self.assertFalse(lab.is_identity(("A", "B", "A", "B"), lab.INVOLUTIVE_ACTIONS))
        self.assertNotEqual(
            lab.effects(("A", "B", "A", "B"), lab.INVOLUTIVE_ACTIONS),
            lab.effects(lab.CHI, lab.INVOLUTIVE_ACTIONS),
        )

    def test_nonpalindromic_state_return_exists(self):
        seq = ("A", "A", "B", "B")
        self.assertFalse(lab.is_palindrome(seq))
        self.assertTrue(lab.is_identity(seq, lab.INVOLUTIVE_ACTIONS))

    def test_inverse_noninvolutive_cycles_can_still_return(self):
        # The sufficient condition "both tokens involutive" is not necessary.
        actions = {"A": (1, 2, 0), "B": (2, 0, 1)}
        self.assertFalse(lab.involution(actions["A"]))
        self.assertFalse(lab.involution(actions["B"]))
        self.assertTrue(lab.is_identity(lab.CHI, actions))
        self.assertEqual(lab.effects(lab.CHI, actions), (0, 1, 2))

    def test_noncommutativity_is_not_necessary_for_control(self):
        actions = {"A": (1, 0, 2), "B": (0, 1, 2)}
        self.assertTrue(lab.commute(actions))
        self.assertTrue(lab.is_identity(("A", "B", "A", "B"), actions))

    def test_invalid_transitions_are_rejected(self):
        with self.assertRaises(ValueError):
            lab.execute(("C",), lab.INVOLUTIVE_ACTIONS, 0)
        with self.assertRaises(ValueError):
            lab.execute(("A",), lab.INVOLUTIVE_ACTIONS, 3)
        with self.assertRaises(ValueError):
            lab.execute(("A",), {"A": (0, 0, 2), "B": (0, 2, 1)}, 0)
        with self.assertRaises(ValueError):
            lab.execute(("A",), {"A": (1, 0, 2)}, 0)
        with self.assertRaises(ValueError):
            lab.render_wav(("Z",))

    def test_pcm_structure_and_exact_repeatability(self):
        wav_data = lab.render_wav(lab.CHI)
        self.assertEqual(wav_data, lab.render_wav(lab.CHI))
        with wave.open(io.BytesIO(wav_data), "rb") as reader:
            self.assertEqual(reader.getnchannels(), 2)
            self.assertEqual(reader.getsampwidth(), 2)
            self.assertEqual(reader.getframerate(), 16000)
            self.assertEqual(reader.getnframes(), 16000)
            self.assertEqual(len(reader.readframes(16000)), 64000)
        self.assertEqual(len(wav_data), 64044)

    def test_different_semantics_identical_audio(self):
        self.assertNotEqual(
            lab.effects(lab.CHI, lab.INVOLUTIVE_ACTIONS),
            lab.effects(lab.CHI, lab.NONINVOLUTIVE_ACTIONS),
        )
        x = lab.provenance_record("closure", lab.INVOLUTIVE_ACTIONS)
        y = lab.provenance_record("departure", lab.NONINVOLUTIVE_ACTIONS)
        self.assertEqual(x["wav_sha256"], y["wav_sha256"])
        self.assertTrue(x["returns_every_state"])
        self.assertFalse(y["returns_every_state"])
        self.assertNotEqual(x["state_history_from_zero"], y["state_history_from_zero"])

    def test_outputs_self_consistent_and_independent_of_outdir(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            result_a = lab.run_lab(Path(a))
            result_b = lab.run_lab(Path(b))
            for name in ("closed_involutions", "open_rotation", "conditional_four_states"):
                audio_a = (Path(a) / (name + ".wav")).read_bytes()
                audio_b = (Path(b) / (name + ".wav")).read_bytes()
                self.assertEqual(audio_a, audio_b)
                recorded = json.loads((Path(a) / (name + ".json")).read_text())
                self.assertEqual(recorded["wav_sha256"], hashlib.sha256(audio_a).hexdigest())
            self.assertTrue(result_a["all_three_wavs_identical"])
            self.assertEqual(result_a["conditional_returning_states"], [3])
            self.assertEqual(result_a["conditional_case"]["effects_all_states"], [2, 0, 1, 3])
            self.assertTrue(result_a["rendered_byte_identity"])
            self.assertFalse(result_a["effect_identity"])
            self.assertEqual(result_a, result_b)
            self.assertFalse(result_a["nonpalindromic_identity_witness"]["is_palindrome"])
            self.assertTrue(result_a["nonpalindromic_identity_witness"]["returns_every_state"])
            self.assertFalse(result_a["noncommutativity_control"]["returns_every_state"])


if __name__ == "__main__":
    unittest.main()
