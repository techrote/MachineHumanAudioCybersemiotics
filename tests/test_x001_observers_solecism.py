"""Tiny stdlib-only discovery bridge for MHAC-X001's focused mathematical tests.

The research code remains isolated in its own expedition directory.
"""
from pathlib import Path
import sys

EXPEDITION = (Path(__file__).resolve().parents[1] / "research" / "expeditions"
              / "observers-solecism")
sys.path.insert(0, str(EXPEDITION))

from test_mode_alias_lab import SolecismWitnessTests  # noqa: F401,E402
