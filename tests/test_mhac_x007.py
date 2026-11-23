"""Run X007's isolated tests during the main repository integrity workflow."""
from pathlib import Path
import importlib.util
import sys

path = (Path(__file__).resolve().parents[1] /
        "research/expeditions/frustrated-choir/test_choir.py")
spec = importlib.util.spec_from_file_location("mhac_x007_tests", path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
FrustratedChoirTests = module.FrustratedChoirTests
