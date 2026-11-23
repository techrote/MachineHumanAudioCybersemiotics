"""Discovery bridge for MHAC-X005's focused standard-library tests."""
from pathlib import Path
import sys

EXPEDITION = Path(__file__).resolve().parents[1] / "research" / "expeditions" / "sound-of-nothing"
sys.path.insert(0, str(EXPEDITION))

from test_silence_oracle import SoundOfNothingTests  # noqa: F401,E402


import unittest

class SoundOfNothingArtifactTests(unittest.TestCase):
    def test_observatory_is_self_contained_and_offline(self):
        html = (EXPEDITION / "silence_observatory.html").read_text(encoding="utf-8")
        self.assertIn("The Silence Observatory", html)
        self.assertIn("shared interval", html)
        self.assertNotIn("<script src=", html.lower())
        self.assertNotIn("<link rel=", html.lower())
        self.assertNotIn("http://", html.lower())
        self.assertNotIn("https://", html.lower())

    def test_research_bundle_contains_exaptation_and_type_discipline(self):
        for name in ("EXAPTATION.md", "TYPE-SYSTEM.md", "ADVERSARIAL.md"):
            self.assertTrue((EXPEDITION / name).is_file(), name)
