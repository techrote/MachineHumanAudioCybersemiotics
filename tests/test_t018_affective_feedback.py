"""Discovery bridge for the bounded MHAC-T018 standard-library toy tests."""
from pathlib import Path
import sys

TANGENT = (Path(__file__).resolve().parents[1] / "research" / "tangents"
           / "affective-feedback")
sys.path.insert(0, str(TANGENT))

from test_feedback_toy import AffectiveFeedbackToyTests  # noqa: F401,E402
