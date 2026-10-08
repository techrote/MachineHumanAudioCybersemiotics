"""Run the retained bootstrap tests and prototype offline in a temporary overlay.

Usage: python run_prepass.py [--output RESULTS_DIRECTORY]
Does not edit the baseline, proposal, any real checkout, or GitHub.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("rerun-results"))
    args = parser.parse_args()
    packet = Path(__file__).resolve().parent
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    records = []
    with tempfile.TemporaryDirectory(prefix="mhac-r001-prepass-") as temp:
        root = Path(temp)
        shutil.copytree(packet / "baseline", root, dirs_exist_ok=True)
        shutil.copytree(packet / "proposal", root, dirs_exist_ok=True)
        (root / "tools/__init__.py").touch(exist_ok=True)
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
        tests = subprocess.run(cmd, cwd=root, capture_output=True, text=True, env=env, timeout=45)
        (output / "unit-tests.txt").write_text(tests.stdout + tests.stderr)
        cases_path = root / "tests/fixtures/mhac_r001"
        cases = json.loads((cases_path / "expected_cases.json").read_text())
        for case in cases:
            arguments = ["-m", "tools.validate_records_prepass", f"tests/fixtures/mhac_r001/{case['name']}.json",
                         "--dataset-kind", case["context"]]
            if case["previous"]:
                arguments += ["--previous", f"tests/fixtures/mhac_r001/{case['previous']}.json"]
            result = subprocess.run([sys.executable] + arguments, cwd=root, capture_output=True, text=True, env=env, timeout=5)
            actual = json.loads(result.stdout)
            code_ok = not case["code"] or actual.get("error", "").startswith(case["code"] + ":")
            records.append({"case": case["name"], "command": ["python"] + arguments,
                            "expected_exit": case["exit"], "actual_exit": result.returncode,
                            "expected_code": case["code"], "matched": result.returncode == case["exit"] and code_ok,
                            "report": actual, "stderr": result.stderr})
        report = {"python": sys.version, "platform": platform.platform(), "network_required": False,
                  "unit_test_exit": tests.returncode, "cases": records,
                  "all_expected_results": tests.returncode == 0 and all(c["matched"] for c in records),
                  "scope": "26 retained bootstrap unit tests plus prepass tests; NOT full-checkout validation or CI"}
        (output / "execution.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
        for name in ("valid_before", "valid_correction_pending", "valid_corrected", "valid_source_invalidated", "valid_empty_live"):
            result = next(r for r in records if r["case"] == name)
            (output / (name + ".report.json")).write_text(json.dumps(result["report"], sort_keys=True, indent=2) + "\n")
        print(json.dumps({"all_expected_results": report["all_expected_results"], "case_count": len(cases),
                          "unit_test_exit": tests.returncode, "output": str(output)}, indent=2))
        return 0 if report["all_expected_results"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
