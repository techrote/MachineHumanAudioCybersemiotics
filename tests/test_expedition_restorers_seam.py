"""Run the expedition tests through standard repository unittest discovery."""
import importlib.util
from pathlib import Path
import sys
import unittest

def load_tests(loader, tests, pattern):
    directory = Path(__file__).resolve().parents[1] / 'research' / 'expeditions' / 'restorers-seam'
    sys.path.insert(0, str(directory))
    try:
        spec = importlib.util.spec_from_file_location('mhac_restorers_seam_local_tests', directory / 'test_seam_lab.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return loader.loadTestsFromModule(module)
    finally:
        sys.path.remove(str(directory))
