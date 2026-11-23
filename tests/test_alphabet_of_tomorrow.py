"""Run the scoped MHAC #209 finite oracle when Node is available."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "research" / "expeditions" / "alphabet-of-tomorrow" / "lab.js"

class AlphabetOfTomorrowTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node unavailable for optional JS expedition")
    def test_exact_oracle_and_controls(self):
        run = subprocess.run(["node", str(LAB)], check=True, capture_output=True,
                             text=True, timeout=90)
        result = json.loads(run.stdout)
        self.assertEqual(result["totalOracleComparisons"], 5538)
        self.assertEqual(result["graphs"], 1099)
        self.assertEqual(result["setCases"], 343)
        self.assertEqual(result["supportCases"], 4096)
        self.assertEqual(result["odd"]["alphabet"], 3)
        self.assertEqual(result["path"]["alphabet"], 2)
        self.assertEqual(result["higher"]["minimalForbidden"], [[0, 1, 2]])
        self.assertEqual(result["higher"]["alphabet"], 2)
        self.assertEqual(result["negative"]["alphabet"], 1)
        self.assertTrue(all(c["n"] == c["alphabet"] for c in result["clique"]))

if __name__ == "__main__":
    unittest.main()
