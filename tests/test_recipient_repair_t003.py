"""Integrate T003's fictional-only tests with repository unittest discovery."""
import importlib.util
import sys
from pathlib import Path

FOLDER = Path(__file__).resolve().parents[1] / 'research' / 'tangents' / 'recipient-repair'


def load_tests(loader, tests, pattern):
    sys.path.insert(0, str(FOLDER))
    try:
        spec = importlib.util.spec_from_file_location('t003_issue_scoped_tests', FOLDER / 'test_protocol.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return loader.loadTestsFromModule(module)
    finally:
        sys.path.pop(0)
