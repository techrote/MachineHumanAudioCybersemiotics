"""Bridge exploratory T004 tests into ordinary repository discovery."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "research/tangents/compositional-messages/test_protocol.py"
spec = importlib.util.spec_from_file_location("t004_protocol_tests", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
TestCompositionalMessages = module.TestCompositionalMessages
