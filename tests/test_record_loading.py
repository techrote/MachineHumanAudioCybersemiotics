"""Canonical ownership, local artifact safety and independent Git history anchors."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from schemas import ValidationError
from tools.build_record_fixtures import snapshots
from tools.record_io import contained_path, loads, verify_artifact
from tools.records import (
    assert_append_only,
    empty_dataset,
    load_registry,
    load_snapshot,
    snapshot_from_git,
    validate_dataset,
)


def state():
    return {
        **{key: value for key, value in empty_dataset().items() if key != "records"},
        "record_roots": ["research/registry/records"],
        "bibliography": "research/registry/bibliography.json",
        "citation_manifests": [], "exports": "research/registry/generated",
    }


def live_gate_sentinel():
    """A test-only live-context envelope; never installed as a research record."""
    row = copy.deepcopy(next(row for row in snapshots()["valid_all_families"]["records"]
                             if row["id"] == "HG-AUTH"))
    row.update(id="HG-LOADER-TEST", synthetic=False)
    row["revisions"][0].update(factual_status="project_decision")
    row["revisions"][0]["data"]["reason"] = "Isolated loader sentinel; no real gate is asserted."
    return row


class RecordLoadingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = state()
        self.write("research/registry/state.json", self.manifest)
        self.write("research/registry/bibliography.json", {"schema_version": 1, "entries": []})

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def add_gate(self, area="research/registry/records"):
        row = live_gate_sentinel()
        return self.write(f"{area}/{row['id']}.json", row)

    def load_and_validate(self):
        data, manifest = load_registry(self.root)
        return validate_dataset(data, expected_kind="live", root=self.root), manifest

    def test_explicit_empty_live_manifest_is_valid_and_not_started(self):
        report, manifest = self.load_and_validate()
        self.assertEqual(report["structural_result"], "pass")
        self.assertEqual(report["research_state"], "not_started")
        self.assertEqual(report["record_count"], 0)
        self.assertEqual(report["counts"]["publications"], 0)
        self.assertEqual(manifest, self.manifest)

    def test_canonical_record_filename_must_match_its_id(self):
        row = live_gate_sentinel()
        self.write("research/registry/records/HG-WRONG.json", row)
        with self.assertRaisesRegex(ValidationError, "^RECORD_FILENAME:"):
            load_registry(self.root)

    def test_same_global_id_cannot_be_owned_by_two_disjoint_lanes(self):
        self.manifest["record_roots"].append("research/gates/other-lane")
        self.write("research/registry/state.json", self.manifest)
        self.add_gate()
        self.add_gate("research/gates/other-lane")
        with self.assertRaisesRegex(ValidationError, "^DUPLICATE_ID:"):
            self.load_and_validate()

    def test_unregistered_record_cannot_escape_validation_by_omitting_its_lane(self):
        self.add_gate("research/gates/unregistered")
        with self.assertRaisesRegex(ValidationError, "^UNREGISTERED_RECORD:"):
            load_registry(self.root)

    def test_overlapping_or_outside_record_roots_are_rejected(self):
        variants = (
            ["research/registry/records", "research/registry/records/child"],
            ["tests/fixtures/records/v1"],
            ["paper/records"],
        )
        for roots in variants:
            with self.subTest(roots=roots):
                self.manifest["record_roots"] = roots
                self.write("research/registry/state.json", self.manifest)
                with self.assertRaisesRegex(ValidationError, "^RECORD_ROOT:"):
                    load_registry(self.root)

    def test_traversal_absolute_and_windows_style_paths_are_rejected(self):
        for path in ("../outside.json", "/etc/passwd", "research/../other.json", "research//file.json",
                     "research/./file.json", "C:/outside.json", "research\\outside.json"):
            with self.subTest(path=path), self.assertRaisesRegex(ValidationError, "^PATH:"):
                contained_path(self.root, path, must_exist=False)

    def test_symlinked_record_and_parent_directory_are_rejected(self):
        record_path = self.add_gate()
        target = self.root / "sentinel.json"
        target.write_bytes(record_path.read_bytes())
        record_path.unlink()
        record_path.symlink_to(target)
        with self.assertRaisesRegex(ValidationError, "^SYMLINK:"):
            load_registry(self.root)
        record_path.unlink()
        directory = record_path.parent
        directory.rmdir()
        external = self.root / "detached-records"
        external.mkdir()
        directory.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValidationError, "^SYMLINK:"):
            load_registry(self.root)

    def test_synthetic_record_cannot_enter_a_live_manifest(self):
        row = copy.deepcopy(snapshots()["valid_before"]["records"][0])
        self.write(f"research/registry/records/{row['id']}.json", row)
        self.manifest["research_state"] = "in_progress"
        self.write("research/registry/state.json", self.manifest)
        with self.assertRaisesRegex(ValidationError, "^CONTAMINATION:"):
            self.load_and_validate()

    def test_snapshot_context_is_selected_by_the_caller(self):
        path = self.write("snapshot.json", snapshots()["valid_before"])
        with self.assertRaisesRegex(ValidationError, "^CONTAMINATION:"):
            load_snapshot(path, expected_kind="live")

    def test_json_rejects_duplicate_keys_and_nonfinite_extensions(self):
        with self.assertRaisesRegex(ValidationError, "^JSON_DUPLICATE_KEY:"):
            loads('{"id":"first","id":"second"}')
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value), self.assertRaisesRegex(ValidationError, "^JSON_NONFINITE:"):
                loads('{"value":' + value + "}")

    def test_artifact_hash_binds_actual_bytes_and_disallows_symlinks(self):
        path = self.root / "evidence.txt"
        raw = b"Explicitly synthetic test artifact\n"
        path.write_bytes(raw)
        artifact = {"path": "evidence.txt", "sha256": hashlib.sha256(raw).hexdigest()}
        self.assertEqual(verify_artifact(self.root, artifact), path)
        path.write_bytes(raw + b"altered\n")
        with self.assertRaisesRegex(ValidationError, "^ARTIFACT_HASH:"):
            verify_artifact(self.root, artifact)
        target = self.root / "other.txt"
        target.write_bytes(raw)
        path.unlink()
        path.symlink_to(target)
        with self.assertRaisesRegex(ValidationError, "^SYMLINK:"):
            verify_artifact(self.root, artifact)


class SnapshotHistoryTests(unittest.TestCase):
    def test_append_only_corrections_pass_against_the_prior_snapshot(self):
        examples = snapshots()
        assert_append_only(examples["valid_before"], examples["valid_correction_pending"])
        assert_append_only(examples["valid_correction_pending"], examples["valid_corrected"])

    def test_rewriting_an_old_extraction_is_rejected(self):
        examples = snapshots()
        current = examples["valid_corrected"]
        next(row for row in current["records"] if row["id"] == "EX-LAT")["revisions"][0]["data"]["value"] = 80.0
        with self.assertRaisesRegex(ValidationError, "^HISTORY:"):
            assert_append_only(examples["valid_before"], current)

    def test_deletion_of_a_record_or_revision_is_rejected(self):
        for remove_record in (True, False):
            examples = snapshots()
            current = examples["valid_corrected"]
            row = next(row for row in current["records"] if row["id"] == "CLM-HYP")
            if remove_record:
                current["records"].remove(row)
            else:
                row["revisions"].clear()
            with self.subTest(remove_record=remove_record), self.assertRaisesRegex(ValidationError, "^HISTORY:"):
                assert_append_only(examples["valid_before"], current)

    def test_immutable_record_envelope_cannot_be_reassigned(self):
        examples = snapshots()
        examples["valid_corrected"]["records"][0]["issue"] = 2
        with self.assertRaisesRegex(ValidationError, "^HISTORY:"):
            assert_append_only(examples["valid_before"], examples["valid_corrected"])


class GitHistoryTests(unittest.TestCase):
    """Real offline disposable Git objects; no mutation of the project repository."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q", "-b", "main")

    def git(self, *args):
        process = subprocess.run(
            ["git", "-c", "user.name=MHAC fixture test", "-c", "user.email=fixture@example.invalid",
             "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
            cwd=self.root, capture_output=True, text=True, timeout=15)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        return process.stdout.strip()

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def commit(self):
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "Synthetic offline history fixture")
        return self.git("rev-parse", "HEAD")

    def test_actual_bootstrap_commit_without_registry_is_an_empty_prior_snapshot(self):
        (self.root / "README.md").write_text("# Isolated bootstrap fixture\n", encoding="utf-8")
        base = self.commit()
        self.assertEqual(snapshot_from_git(self.root, base), empty_dataset())

    def test_missing_registry_manifest_cannot_hide_records_in_prior_git_tree(self):
        self.write("research/gates/HG-LOADER-TEST.json", live_gate_sentinel())
        base = self.commit()
        with self.assertRaisesRegex(ValidationError, "^HISTORY_STATE:"):
            snapshot_from_git(self.root, base)

    def test_prior_snapshot_reads_committed_bytes_despite_worktree_rewrite(self):
        self.write("research/registry/state.json", state())
        original = live_gate_sentinel()
        path = self.write("research/registry/records/HG-LOADER-TEST.json", original)
        base = self.commit()
        changed = copy.deepcopy(original)
        changed["revisions"][0]["data"]["reason"] = "Rewritten test history, not the committed reason."
        path.write_text(json.dumps(changed), encoding="utf-8")
        previous = snapshot_from_git(self.root, base)
        self.assertEqual(previous["records"], [original])
        current, _ = load_registry(self.root)
        with self.assertRaisesRegex(ValidationError, "^HISTORY:"):
            assert_append_only(previous, current)

    def test_missing_or_mutable_git_ref_is_not_treated_as_an_empty_base(self):
        for ref in ("0" * 40, "HEAD", "main", "--help"):
            with self.subTest(ref=ref), self.assertRaisesRegex(ValidationError, "^HISTORY_REF:"):
                snapshot_from_git(self.root, ref)


if __name__ == "__main__":
    unittest.main()
