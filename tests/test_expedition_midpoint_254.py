"""Discover the isolated issue #254 suite without changing shared test infrastructure."""
import importlib.util
from pathlib import Path
import sys
import unittest

def load_tests(loader, tests, pattern):
    folder = Path(__file__).resolve().parents[1] / "research/expeditions/midpoint-without-name"
    return loader.discover(str(folder), pattern="test_midpoint_lab.py", top_level_dir=str(folder))
