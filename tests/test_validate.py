"""Known-good and negative tests for the bootstrap integrity boundary."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools.validate import (REPOSITORY, REQUIRED, ValidationError, main,
                            markdown_targets, read_json, validate_programme,
                            validate_repository)


def example() -> dict:
    return {
        "schema_version": 1, "repository": REPOSITORY,
        "tasks": [
            {"id": "MHAC-R001", "issue": 1, "title": "Foundation", "phase": "foundation",
             "human_gate": False, "depends_on": [], "docs": ["README.md"], "owns": ["tools/"]},
            {"id": "MHAC-R002", "issue": 2, "title": "Protocol", "phase": "protocol",
             "human_gate": False, "depends_on": ["MHAC-R001"], "docs": ["README.md"], "owns": ["research/"]},
        ],
    }


class ProgrammeTests(unittest.TestCase):
    def test_valid(self):
        validate_programme(example())

    def test_duplicate_id(self):
        data = example()
        data["tasks"][1]["id"] = "MHAC-R001"
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_duplicate_issue(self):
        data = example()
        data["tasks"][1]["issue"] = 1
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_boolean_is_not_issue_number(self):
        data = example()
        data["tasks"][0]["issue"] = True
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_missing_dependency(self):
        data = example()
        data["tasks"][1]["depends_on"] = ["MHAC-R099"]
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_duplicate_dependency(self):
        data = example()
        data["tasks"][1]["depends_on"] *= 2
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_self_dependency(self):
        data = example()
        data["tasks"][0]["depends_on"] = ["MHAC-R001"]
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_cycle(self):
        data = example()
        data["tasks"][0]["depends_on"] = ["MHAC-R002"]
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_invalid_id(self):
        data = example()
        data["tasks"][0]["id"] = "TASK-1"
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_empty_programme(self):
        data = example()
        data["tasks"] = []
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_bad_schema(self):
        for value in (True, "1", 2, None):
            data = example()
            data["schema_version"] = value
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_programme(data)

    def test_bad_repo(self):
        data = example()
        data["repository"] = "other/project"
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_human_gate_mismatch(self):
        data = example()
        data["tasks"][0]["human_gate"] = True
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_missing_docs(self):
        data = example()
        data["tasks"][0]["docs"] = []
        with self.assertRaises(ValidationError):
            validate_programme(data)

    def test_bad_phase_and_gate_types(self):
        for field, value in (("phase", []), ("phase", "done"), ("human_gate", "false")):
            data = example()
            data["tasks"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                validate_programme(data)


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in REQUIRED:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Fixture\n", encoding="utf-8")
        (self.root / "programme.json").write_text(json.dumps(example()), encoding="utf-8")

    def test_valid_repository(self):
        validate_repository(self.root)

    def test_missing_required_file(self):
        (self.root / "AGENTS.md").unlink()
        with self.assertRaises(ValidationError):
            validate_repository(self.root)

    def test_broken_local_link(self):
        (self.root / "README.md").write_text("[missing](missing.md)\n", encoding="utf-8")
        with self.assertRaises(ValidationError):
            validate_repository(self.root)

    def test_external_links_and_fenced_examples(self):
        (self.root / "README.md").write_text(
            "[web](https://example.invalid/no-file)\n[section](#missing-anchor)\n"
            "```text\n[example](not-a-real-file.md)\n```\n", encoding="utf-8")
        validate_repository(self.root)

    def test_link_escape(self):
        (self.root / "README.md").write_text("[escape](../outside.md)\n", encoding="utf-8")
        with self.assertRaises(ValidationError):
            validate_repository(self.root)

    def test_invalid_json(self):
        (self.root / "broken.json").write_text("{broken", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            validate_repository(self.root)

    def test_duplicate_json_key(self):
        path = self.root / "duplicate.json"
        path.write_text('{"a": 1, "a": 2}', encoding="utf-8")
        with self.assertRaises(ValidationError):
            read_json(path)

    def test_missing_authority(self):
        data = example()
        data["tasks"][0]["docs"] = ["absent.md"]
        (self.root / "programme.json").write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValidationError):
            validate_repository(self.root)

    def test_cli_failure_code(self):
        (self.root / "RAG.md").unlink()
        self.assertEqual(main(["--root", str(self.root)]), 1)

    def test_cli_success_code(self):
        self.assertEqual(main(["--root", str(self.root)]), 0)

    def test_target_extraction(self):
        self.assertEqual(markdown_targets("[local](docs/a.md#section) ![img](img.png)"),
                         ["docs/a.md#section", "img.png"])


if __name__ == "__main__":
    unittest.main()
