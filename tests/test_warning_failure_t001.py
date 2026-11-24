"""Load the isolated T001 synthetic-only tests into the repository's normal CI suite.

The implementation and fixtures live in the tangent-owned research directory;
this wrapper avoids importing them as canonical empirical records.
"""
from importlib import util
from pathlib import Path

TANGENT = (Path(__file__).resolve().parents[1] / "research" / "tangents"
           / "warning-failure-paths" / "test_analysis.py")
spec = util.spec_from_file_location("mhac_t001_test_analysis", TANGENT)
module = util.module_from_spec(spec)
spec.loader.exec_module(module)
SyntheticFailurePathTests = module.SyntheticFailurePathTests
