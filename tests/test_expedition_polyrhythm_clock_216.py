"""Discover the issue #216 isolated synthetic experiment in repository CI."""
from pathlib import Path
import subprocess
import sys
import unittest


class PolyrhythmClockExpeditionTests(unittest.TestCase):
    def test_isolated_suite(self):
        directory = Path(__file__).resolve().parents[1] / "research" / "expeditions" / "polyrhythm-clock"
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "-v", "test_clock", "test_band_solver"],
            cwd=directory, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
