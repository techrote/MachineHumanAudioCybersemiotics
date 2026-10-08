"""Positive/negative fixtures and actual CLI exit codes for the bounded prepass."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tools.build_r001_fixtures import build
from tools.validate import ValidationError, read_json
from tools.validate_records_prepass import validate

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/mhac_r001"
CASES = read_json(FIXTURES / "expected_cases.json")


class RecordTests(unittest.TestCase):
    def test_fixture_rebuild_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp:
            rebuilt = Path(temp)
            build(rebuilt)
            expected = sorted(p.relative_to(FIXTURES) for p in FIXTURES.rglob("*") if p.is_file())
            self.assertEqual(expected, sorted(p.relative_to(rebuilt) for p in rebuilt.rglob("*") if p.is_file()))
            for path in expected:
                self.assertEqual((FIXTURES / path).read_bytes(), (rebuilt / path).read_bytes(), str(path))

    def test_source_hashes_identify_actual_synthetic_bytes(self):
        data = read_json(FIXTURES / "valid_before.json")
        for row in data["records"]:
            if row["kind"] == "source":
                for m in row["revisions"][0]["data"]["manifestations"]:
                    raw = (FIXTURES / m["fixture_path"]).read_bytes()
                    self.assertEqual(m["sha256"], hashlib.sha256(raw).hexdigest())
                    self.assertEqual(m["extent"], len(raw.split(b"\x0c")))

    def test_wrong_extraction_can_pass_structure_before_source_fidelity_check(self):
        data = read_json(FIXTURES / "valid_before.json")
        self.assertEqual(validate(data, expected_kind="fixture")["structural_result"], "pass")
        ex = next(r for r in data["records"] if r["id"] == "EX-LAT")
        self.assertEqual(ex["revisions"][0]["data"]["value"], 8.0)
        self.assertIn("80 ms", (FIXTURES / "sources/report_A.txt").read_text())
        # Deliberate boundary test: source-content entailment is NOT asserted by validate().

    def test_correction_propagates_without_changing_independent_counts(self):
        pending = read_json(FIXTURES / "valid_correction_pending.json")
        report = validate(pending, expected_kind="fixture")
        self.assertIn("CLM-LAT", report["latest_stale_ids"])
        self.assertIn("REQ-TIMING", report["latest_stale_ids"])
        self.assertNotIn("CLM-ACC", report["latest_stale_ids"])
        self.assertEqual(report["counts"], {"publications": 2, "studies": 1, "experiments": 1,
                         "samples": 1, "outcomes": 2, "shared_sample_groups": 1})
        after = validate(read_json(FIXTURES / "valid_corrected.json"), expected_kind="fixture", previous=pending)
        self.assertEqual(after["latest_stale_ids"], [])
        self.assertIn({"id": "CLM-LAT", "rev": 2}, after["stale_revisions"])

    def test_full_access_does_not_imply_full_reading(self):
        data = read_json(FIXTURES / "valid_corrected.json")
        source = next(r for r in data["records"] if r["id"] == "SRC-B")
        reading = next(r for r in data["records"] if r["id"] == "AID-READ-B")
        self.assertEqual(source["revisions"][0]["data"]["access_status"], "full_text_available")
        self.assertEqual(reading["revisions"][0]["data"]["reading_status"], "selected_ranges_read")

    def test_malformed_json_cli_is_nonzero_machine_readable(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text('{"contract": 1, "contract": 2}')
            result = subprocess.run([sys.executable, "-m", "tools.validate_records_prepass", str(path),
                                     "--dataset-kind", "fixture"], cwd=ROOT, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["structural_result"], "fail")

    def test_boolean_is_not_revision(self):
        data = read_json(FIXTURES / "valid_before.json")
        data["records"][0]["revisions"][0]["rev"] = True
        with self.assertRaisesRegex(ValidationError, "REVISION"):
            validate(data, expected_kind="fixture")

    def test_outside_working_directory_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(ROOT / "tools/validate_records_prepass.py"),
                                     str(FIXTURES / "valid_before.json"), "--dataset-kind", "fixture"],
                                    cwd=temp, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


    def audit_example(self, wrong_target=False, changed_statement=False):
        data = read_json(FIXTURES / "valid_corrected.json")
        target = {"id": "CLM-ACC" if wrong_target else "CLM-LAT", "rev": 2 if wrong_target else 4}
        data["records"].append({"schema_version": 1, "id": "AID-INTERNAL", "kind": "assistance",
            "synthetic": True, "issue": 1, "revisions": [{"rev": 1, "at": "2000-01-01T00:10:00Z",
                "actor": {"kind": "agent", "id": "SYNTHETIC-AGENT"}, "basis": [target],
                "data": {"subtype": "review", "scope": "internal_audit", "outcome": "pass",
                         "verification": "agent_checked", "target_refs": [target], "artifact": "Synthetic exact-payload review"}}]})
        claim = next(r for r in data["records"] if r["id"] == "CLM-LAT")
        new = copy.deepcopy(claim["revisions"][-1])
        new.update(rev=5, at="2000-01-01T00:11:00Z")
        audit = {"id": "AID-INTERNAL", "rev": 1}
        new["basis"].append(audit)
        new["data"]["review_refs"].append(audit)
        new["data"]["lifecycle"] = "internally_audited"
        if changed_statement:
            new["data"]["statement"] = "SYNTHETIC materially changed claim, not the reviewed assertion."
        claim["revisions"].append(new)
        data["release_claims"] = [{"id": "CLM-LAT", "rev": 5}]
        return data

    def test_internal_audit_binds_exact_claim_payload(self):
        result = validate(self.audit_example(), expected_kind="fixture",
                          previous=read_json(FIXTURES / "valid_corrected.json"))
        self.assertEqual(result["structural_result"], "pass")

    def test_unrelated_internal_audit_does_not_promote(self):
        with self.assertRaisesRegex(ValidationError, "UNSUPPORTED_PROMOTION"):
            validate(self.audit_example(wrong_target=True), expected_kind="fixture")

    def test_changed_claim_does_not_inherit_internal_audit(self):
        with self.assertRaisesRegex(ValidationError, "UNSUPPORTED_PROMOTION"):
            validate(self.audit_example(changed_statement=True), expected_kind="fixture")


def fixture_test(case):
    def test(self):
        args = [sys.executable, "-m", "tools.validate_records_prepass",
                str(FIXTURES / f"{case['name']}.json"), "--dataset-kind", case["context"]]
        if case["previous"]:
            args += ["--previous", str(FIXTURES / f"{case['previous']}.json")]
        process = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=5)
        self.assertEqual(process.returncode, case["exit"], process.stdout + process.stderr)
        result = json.loads(process.stdout)
        if case["code"]:
            self.assertTrue(result["error"].startswith(case["code"] + ":"), result)
        else:
            self.assertEqual(result["structural_result"], "pass")
    return test


for _case in CASES:
    setattr(RecordTests, "test_cli_" + _case["name"], fixture_test(_case))


if __name__ == "__main__":
    unittest.main()
