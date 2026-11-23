"""Discovery bridge for MHAC-X005's focused standard-library tests."""
from pathlib import Path
import sys

EXPEDITION = Path(__file__).resolve().parents[1] / "research" / "expeditions" / "sound-of-nothing"
sys.path.insert(0, str(EXPEDITION))

from test_silence_oracle import SoundOfNothingTests  # noqa: F401,E402
