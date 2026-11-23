"""Run the isolated epistemic-score laboratory and verify its exported PCM files."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "research/expeditions/rehearsal-of-doubt/lab.mjs"


class RehearsalOfDoubtTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node runtime not installed")
    def test_exact_policy_counts_and_pcm_witnesses(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = subprocess.run(
                ["node", str(LAB), str(out)], check=True, text=True,
                capture_output=True, timeout=90
            )
            result = json.loads(proc.stdout)
            self.assertEqual(result, json.loads((out / "results.json").read_text()))
            self.assertEqual(result["assertions"], 113306)
            self.assertEqual(result["private_n8"]["nontrivial"], 0)
            self.assertEqual(result["public_n8"]["nontrivial"], 1)
            self.assertEqual((out / "private-unison.wav").read_bytes(),
                             (out / "public-unison.wav").read_bytes())
            for name in ("private-unison", "public-unison", "private-solo", "absent"):
                with wave.open(str(out / (name + ".wav")), "rb") as wav:
                    self.assertEqual((wav.getnchannels(), wav.getsampwidth(),
                                      wav.getframerate(), wav.getnframes()),
                                     (2, 2, 16000, 32000))
                    payload = wav.readframes(32000)
                    if name == "absent":
                        self.assertEqual(set(payload), {0})
                    if name == "private-solo":
                        self.assertTrue(any(payload[0::4]) or any(payload[1::4]))
                        self.assertFalse(any(payload[2::4]) or any(payload[3::4]))


if __name__ == "__main__":
    unittest.main()
