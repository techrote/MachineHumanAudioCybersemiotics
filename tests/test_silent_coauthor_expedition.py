"""Run the isolated Silent Coauthor synthetic expedition checks."""
import pathlib
import subprocess
import sys
import unittest


class SilentCoauthorTests(unittest.TestCase):
    def test_expedition(self):
        lab = pathlib.Path(__file__).resolve().parents[1] / "research" / "expeditions" / "silent-coauthor"
        for name, expected in (("lab.py", "assertions: 12741"), ("partial.py", "partial audit assertions: 2921")):
            with self.subTest(script=name):
                result = subprocess.run([sys.executable, str(lab / name)], capture_output=True, text=True, check=True)
                self.assertIn(expected, result.stdout)
