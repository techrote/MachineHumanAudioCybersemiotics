"""Bridge issue-scoped T006 tests into repository unittest discovery."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "research/tangents/action-polarity/test_oracle.py"
spec = importlib.util.spec_from_file_location("t006_action_polarity_tests", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
TestActionPolarity = module.TestActionPolarity
