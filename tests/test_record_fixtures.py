"""Migration fidelity, explicit fiction, deterministic builds and executable fixtures."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.build_record_fixtures import (
    ORIGINAL_SNAPSHOT_SHA256,
    _prepass_snapshots,
    build,
    check,
    dumps,
    snapshots,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/records/v1"
SOURCE_SHA256 = {
    "A": "a150186a4f5dc6bb0f798b831d6f3735a2de9276aa2728dcce1d0b9130a6083c",
    "B": "4b6977cdab4532305c243150f06b108c95006878f465e0c662090cb2804e34f4",
}
REQUIRED_FAMILY_FIELDS = {
    "source": "access_status",
    "search_run": "query",
    "search_hit": "search_ref",
    "screening": "decision",
    "study": "identity_basis",
    "experiment": "dependence",
    "sample": "missingness",
    "theoretical_extraction": "assertion",
    "extraction": "field_locators",
    "appraisal": "criterion",
    "claim": "argument",
    "requirement": "revision_criterion",
    "experiment_protocol": "gate_refs",
    "amendment": "verification",
    "assistance": "status",
    "human_gate": "owner_action",
}


def read_fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def record(data, rid):
    return next(row for row in data["records"] if row["id"] == rid)


class FixturePreservationTests(unittest.TestCase):
    def assert_preserved(self, original, migrated, path="data"):
        """Allow explicit new contract fields, but preserve every old payload value."""
        if isinstance(original, dict):
            self.assertIsInstance(migrated, dict, path)
            for key, value in original.items():
                self.assertIn(key, migrated, path)
                self.assert_preserved(value, migrated[key], f"{path}.{key}")
        elif isinstance(original, list):
            self.assertIsInstance(migrated, list, path)
            self.assertEqual(len(original), len(migrated), path)
            for index, (old, new) in enumerate(zip(original, migrated)):
                self.assert_preserved(old, new, f"{path}[{index}]")
        else:
            self.assertEqual(original, migrated, path)

    def test_original_prepass_snapshots_match_verified_artifact_hashes(self):
        originals = _prepass_snapshots()
        self.assertEqual(set(originals), set(ORIGINAL_SNAPSHOT_SHA256))
        for name, content in originals.items():
            with self.subTest(snapshot=name):
                raw = dumps(content).encode("utf-8")
                self.assertEqual(hashlib.sha256(raw).hexdigest(), ORIGINAL_SNAPSHOT_SHA256[name])

    def test_explicit_conversion_preserves_all_historical_record_values(self):
        migrated = snapshots()
        for name, old_data in _prepass_snapshots().items():
            with self.subTest(snapshot=name):
                current = migrated[name]
                self.assertEqual(current["contract"], "mhac-records/1")
                self.assertNotIn("declared_counts", current)
                self.assertEqual(old_data["research_state"], current["research_state"])
                self.assertEqual(old_data["release_claims"], current["release_claims"])
                self.assertEqual(old_data.get("release_requirements", []), current["release_requirements"])
                self.assertEqual(len(old_data["records"]), len(current["records"]))
                for old in old_data["records"]:
                    new = record(current, old["id"])
                    for field in ("schema_version", "id", "kind", "synthetic", "issue"):
                        self.assertEqual(old[field], new[field])
                    self.assertEqual(len(old["revisions"]), len(new["revisions"]))
                    for old_revision, new_revision in zip(old["revisions"], new["revisions"]):
                        for field in ("rev", "at", "actor"):
                            self.assertEqual(old_revision[field], new_revision[field])
                        self.assertEqual(new_revision["factual_status"], "synthetic")
                        self.assertEqual(new_revision["basis"][:len(old_revision["basis"])], old_revision["basis"])
                        self.assert_preserved(old_revision["data"], new_revision["data"], old["id"])

    def test_all_frozen_fixture_bytes_rebuild_exactly(self):
        self.assertEqual(check(FIXTURES), [])
        with tempfile.TemporaryDirectory() as directory:
            rebuilt = Path(directory)
            build(rebuilt)
            expected = sorted(p.relative_to(FIXTURES) for p in FIXTURES.rglob("*") if p.is_file())
            actual = sorted(p.relative_to(rebuilt) for p in rebuilt.rglob("*") if p.is_file())
            self.assertEqual(expected, actual)
            for path in expected:
                with self.subTest(path=str(path)):
                    self.assertEqual((FIXTURES / path).read_bytes(), (rebuilt / path).read_bytes())

    def test_rebuild_check_detects_altered_and_unexpected_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build(root)
            (root / "sources/report_A.txt").write_text("tampered fixture", encoding="utf-8")
            (root / "unexpected.txt").write_text("unregistered artifact", encoding="utf-8")
            differences = check(root)
            self.assertIn("changed: sources/report_A.txt", differences)
            self.assertIn("unexpected: unexpected.txt", differences)

    def test_original_synthetic_source_bytes_hashes_and_page_counts_are_preserved(self):
        data = read_fixture("valid_before")
        for suffix, digest in SOURCE_SHA256.items():
            with self.subTest(source=suffix):
                source = record(data, "SRC-" + suffix)["revisions"][0]["data"]
                manifestation = source["manifestations"][0]
                raw = (FIXTURES / manifestation["fixture_path"]).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
                self.assertEqual(manifestation["sha256"], digest)
                self.assertEqual(manifestation["extent"], len(raw.split(b"\x0c")))
                self.assertTrue(raw.startswith(b"SYNTHETIC REPORT"))

    def test_provenance_manifest_covers_actual_deliverable_bytes(self):
        manifest = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["synthetic"])
        self.assertEqual(manifest["original_snapshots_sha256"], ORIGINAL_SNAPSHOT_SHA256)
        all_files = {p.relative_to(FIXTURES).as_posix() for p in FIXTURES.rglob("*") if p.is_file()}
        self.assertEqual(set(manifest["files_sha256"]), all_files - {"provenance.json"})
        for path, digest in manifest["files_sha256"].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((FIXTURES / path).read_bytes()).hexdigest(), digest)

    def test_fixtures_never_claim_real_completed_research(self):
        for name, data in snapshots().items():
            with self.subTest(snapshot=name):
                self.assertIn(data["research_state"], {"not_started", "in_progress"})
                for row in data["records"]:
                    self.assertTrue(row["synthetic"])
                    self.assertTrue(all(revision["factual_status"] == "synthetic" for revision in row["revisions"]))


class FixtureContractTests(unittest.TestCase):
    def validate(self, name, previous=None):
        from tools.records import validate_dataset
        data = read_fixture(name)
        return validate_dataset(data, expected_kind=data["dataset_kind"], root=FIXTURES,
                                previous=read_fixture(previous) if previous else None)

    def test_all_six_positive_snapshots_validate_in_their_explicit_contexts(self):
        predecessors = {"valid_correction_pending": "valid_before", "valid_corrected": "valid_correction_pending",
                        "valid_source_invalidated": "valid_corrected"}
        for name in snapshots():
            with self.subTest(snapshot=name):
                self.assertEqual(self.validate(name, predecessors.get(name))["structural_result"], "pass")

    def test_incorrect_8_ms_extraction_passes_structure_but_source_says_80_ms(self):
        result = self.validate("valid_before")
        self.assertEqual(result["structural_result"], "pass")
        data = read_fixture("valid_before")
        self.assertEqual(record(data, "EX-LAT")["revisions"][0]["data"]["value"], 8.0)
        self.assertIn("80 ms", (FIXTURES / "sources/report_A.txt").read_text(encoding="utf-8"))

    def test_correction_keeps_both_values_without_adding_an_outcome(self):
        values = [revision["data"]["value"] for revision in record(read_fixture("valid_corrected"), "EX-LAT")["revisions"]]
        self.assertEqual(values, [8.0, 80.0])
        before = self.validate("valid_before")
        after = self.validate("valid_corrected", previous="valid_correction_pending")
        self.assertEqual(before["counts"], after["counts"])

    def test_worked_example_counts_publications_studies_and_dependent_outcomes_separately(self):
        counts = self.validate("valid_all_families")["counts"]
        expected = {"publications": 2, "studies": 1, "experiments": 1, "samples": 1,
                    "outcomes": 2, "shared_sample_groups": 1, "search_runs": 1, "search_hits": 3,
                    "included_publications": 1, "included_studies": 1, "unavailable_publications": 0}
        for field, value in expected.items():
            with self.subTest(measure=field):
                self.assertEqual(counts[field], value)
        self.assertEqual(counts["search_details"][0]["duplicate_hits"], 1)
        self.assertEqual(counts["screening"]["full_text"]["include"], 1)
        self.assertEqual(counts["screening"]["full_text"]["uncertain"], 1)

    def test_correction_pending_quarantines_latency_support_and_preserves_accuracy(self):
        result = self.validate("valid_correction_pending", previous="valid_before")
        latest_stale = result["currency"]["latest_stale_ids"]
        for rid in ("APP-LAT", "AID-CHECK-LAT", "CLM-LAT", "CLM-HYP", "REQ-TIMING"):
            self.assertIn(rid, latest_stale)
        self.assertNotIn("CLM-ACC", latest_stale)
        self.assertIn({"id": "EX-LAT", "rev": 1}, result["currency"]["invalidated"])
        corrected = self.validate("valid_corrected", previous="valid_correction_pending")
        self.assertEqual(corrected["currency"]["latest_stale_ids"], [])

    def test_source_invalidation_preserves_unaffected_accuracy_source_claim(self):
        result = self.validate("valid_source_invalidated", previous="valid_corrected")
        self.assertIn("CLM-LAT", result["currency"]["latest_stale_ids"])
        self.assertIn("REQ-TIMING", result["currency"]["latest_stale_ids"])
        self.assertNotIn("CLM-ACC", result["currency"]["latest_stale_ids"])
        self.assertEqual(read_fixture("valid_source_invalidated")["release_claims"], [{"id": "CLM-ACC", "rev": 2}])
        self.assertEqual(result["counts"]["current_extracted_outcomes"], 1)

    def test_source_access_and_partial_reading_remain_distinct(self):
        data = read_fixture("valid_all_families")
        source = record(data, "SRC-B")["revisions"][0]["data"]
        reading = record(data, "AID-READ-B")["revisions"][0]["data"]
        screening = record(data, "SCR-B-FT")["revisions"][0]["data"]
        self.assertEqual(source["access_status"], "full_text_available")
        self.assertEqual(reading["reading_status"], "selected_ranges_read")
        self.assertEqual(reading["ranges"], [[1, 2]])
        self.assertEqual(source["manifestations"][0]["extent"], 4)
        self.assertEqual(screening["decision"], "uncertain")

    def test_all_sixteen_families_and_three_assistance_variants_are_exercised(self):
        from schemas.v1 import validate_record
        data = read_fixture("valid_all_families")
        self.assertEqual({row["kind"] for row in data["records"]}, set(REQUIRED_FAMILY_FIELDS))
        self.assertEqual({row["revisions"][0]["data"]["subtype"] for row in data["records"] if row["kind"] == "assistance"},
                         {"reading", "review", "assistance"})
        for row in data["records"]:
            with self.subTest(record=row["id"]):
                validate_record(row, expected_kind="fixture")

    def test_each_family_rejects_an_essential_missing_contract_field(self):
        from schemas import ValidationError
        from schemas.v1 import validate_record
        data = read_fixture("valid_all_families")
        for kind, field in REQUIRED_FAMILY_FIELDS.items():
            with self.subTest(kind=kind, missing=field):
                row = copy.deepcopy(next(row for row in data["records"] if row["kind"] == kind))
                del row["revisions"][0]["data"][field]
                with self.assertRaises(ValidationError):
                    validate_record(row, expected_kind="fixture")

    def test_participant_readiness_stays_explicitly_blocked(self):
        data = read_fixture("valid_all_families")
        protocol = record(data, "TEST-TRANSFER")["revisions"][0]["data"]
        gate = record(data, "HG-AUTH")["revisions"][0]["data"]
        self.assertEqual(protocol["status"], "readiness_blocked")
        self.assertEqual(protocol["exposure"], "synthetic")
        self.assertEqual(gate["status"], "blocked")
        self.assertEqual(gate["authorized_actor"]["state"], "unknown")

    def test_cli_works_outside_repository_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            process = subprocess.run([sys.executable, str(ROOT / "tools/validate.py"), "--records",
                                      str(FIXTURES / "valid_before.json"), "--dataset-kind", "fixture"],
                                     cwd=directory, capture_output=True, text=True, timeout=30)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["structural_result"], "pass")


def fixture_cli_test(case):
    def test(self):
        args = [sys.executable, str(ROOT / "tools/validate.py"), "--records",
                str(FIXTURES / f"{case['name']}.json"), "--dataset-kind", case["context"]]
        if case["previous"]:
            args.extend(["--previous", str(FIXTURES / f"{case['previous']}.json")])
        process = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(process.returncode, case["exit"], process.stdout + process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(result["structural_result"], "pass" if case["exit"] == 0 else "fail")
        if case["exit"] != 0:
            self.assertIsInstance(result["error"], str)
            self.assertTrue(result["error"].startswith(case["code"] + ":"), result["error"])
    return test


for _case in json.loads((FIXTURES / "expected_cases.json").read_text(encoding="utf-8")):
    setattr(FixtureContractTests, "test_cli_" + _case["name"], fixture_cli_test(_case))


if __name__ == "__main__":
    unittest.main()
