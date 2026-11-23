"""Run the isolated sleeping-commutator tests in their own interpreter."""
from pathlib import Path
import subprocess
import sys
import unittest


class SleepingCommutatorBridge(unittest.TestCase):
    def test_expedition(self):
        root = Path(__file__).resolve().parents[1]
        folder = root / 'research' / 'expeditions' / 'sleeping-commutator'
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover',
                                 '-s', str(folder), '-v'],
                                cwd=folder, capture_output=True, text=True,
                                timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Ran 8 tests', result.stderr)
