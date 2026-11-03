"""Synthetic screening sequences, track separation and canonical-history guards."""
from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from schemas import ValidationError
from schemas.v1 import validate_record
from tools.build_record_fixtures import ref, snapshots
from tools.evidence_flow import evidence_flow
from tools.record_graph import validate_graph
from tools.record_io import dumps
from tools.records import load_registry, write_generated_records
from tools.screening import screening_coverage


def row(data, rid):
    return next(record for record in data["records"] if record["id"] == rid)


def body(data, rid):
    return row(data, rid)["revisions"][-1]["data"]


def append(record, **changes):
    revision = copy.deepcopy(record["revisions"][-1])
    revision.update(rev=revision["rev"] + 1, at="2000-01-02T00:00:00Z")
    revision["data"].update(changes)
    record["revisions"].append(revision)


class ScreeningIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.data = snapshots()["valid_all_families"]

    def graph(self):
        return validate_graph(self.data["records"])

    def test_legacy_absence_and_explicit_empirical_are_same_scope(self):
        before = evidence_flow(self.graph())
        for record in self.data["records"]:
            if record["kind"] == "screening":
                record["revisions"][0]["data"]["track"] = "empirical"
        self.assertEqual(before, evidence_flow(self.graph()))
        append(row(self.data, "SCR-A-TA"), track="empirical")
        self.graph()

    def test_screening_track_is_closed_and_cannot_change_in_place(self):
        for invalid in ("both", None, [], {}):
            record = copy.deepcopy(row(self.data, "SCR-A-TA"))
            record["revisions"][0]["data"]["track"] = invalid
            with self.subTest(track=invalid), self.assertRaises(ValidationError):
                validate_record(record, expected_kind="fixture")
        append(row(self.data, "SCR-A-TA"), track="theoretical")
        with self.assertRaisesRegex(ValidationError, "HISTORY"):
            self.graph()

    def test_theory_does_not_inflate_empirical_inclusions(self):
        for record in self.data["records"]:
            if record["kind"] == "screening":
                record["revisions"][0]["data"]["track"] = "theoretical"
        result = evidence_flow(self.graph())
        for key in ("included_publications", "included_studies", "included_outcomes"):
            self.assertEqual(result[key], 0)
        self.assertEqual(result["selected_theoretical_publications"], 1)
        self.assertEqual(result["screening_by_track"]["empirical"]["full_text"]["include"], 0)
        self.assertEqual(result["screening_by_track"]["theoretical"]["full_text"]["include"], 1)
        # Preserve the stronger all-track unresolved completion gate.
        self.assertEqual(result["screening"]["full_text"]["uncertain"], 1)

    def test_same_source_can_have_separate_track_decisions(self):
        for stage in ("TA", "FT"):
            record = copy.deepcopy(row(self.data, "SCR-A-" + stage))
            record["id"] = "SCR-A-THEORY-" + stage
            record["revisions"][0]["data"]["track"] = "theoretical"
            self.data["records"].append(record)
        result = evidence_flow(self.graph())
        self.assertEqual(result["included_publications"], 1)
        self.assertEqual(result["selected_theoretical_publications"], 1)
        self.assertEqual(result["screening"]["full_text"]["include"], 2)

    def test_full_text_requires_matching_prior_title_abstract(self):
        for field, value in (("decision", "exclude"), ("decision", "pending"),
                             ("track", "theoretical"), ("protocol_version", "OTHER-v1")):
            with self.subTest(field=field, value=value):
                self.data = snapshots()["valid_all_families"]
                body(self.data, "SCR-A-TA")[field] = value
                with self.assertRaisesRegex(ValidationError, "SCREENING_SEQUENCE"):
                    self.graph()
        self.data = snapshots()["valid_all_families"]
        self.data["records"].remove(row(self.data, "SCR-A-TA"))
        with self.assertRaisesRegex(ValidationError, "SCREENING_SEQUENCE"):
            self.graph()

    def test_title_abstract_decision_after_full_text_is_not_prior(self):
        row(self.data, "SCR-A-TA")["revisions"][0]["at"] = "2000-01-02T00:00:00Z"
        with self.assertRaisesRegex(ValidationError, "SCREENING_SEQUENCE"):
            self.graph()

    def test_later_inclusion_cannot_repair_invalid_historical_sequence(self):
        body(self.data, "SCR-A-TA")["decision"] = "exclude"
        append(row(self.data, "SCR-A-TA"), decision="include")
        with self.assertRaisesRegex(ValidationError, "SCREENING_SEQUENCE"):
            self.graph()

    def test_later_exclusion_cannot_leave_current_full_text_included(self):
        append(row(self.data, "SCR-A-TA"), decision="exclude")
        with self.assertRaisesRegex(ValidationError, "SCREENING_SEQUENCE"):
            self.graph()

    def test_uncertain_title_abstract_can_proceed_and_unavailable_text_is_preserved(self):
        body(self.data, "SCR-A-TA")["decision"] = "uncertain"
        body(self.data, "SCR-A-FT").update(decision="awaiting_text", reading_refs=[])
        result = evidence_flow(self.graph())
        self.assertEqual(result["screening"]["full_text"]["awaiting_text"], 1)
        self.assertEqual(result["included_publications"], 0)

    def test_supersession_cannot_cross_tracks(self):
        record = copy.deepcopy(row(self.data, "SCR-A-TA"))
        record["id"] = "SCR-A-OTHER"
        record["revisions"][0]["data"].update(track="theoretical", supersedes_ref=ref("SCR-A-TA"))
        self.data["records"].append(record)
        with self.assertRaisesRegex(ValidationError, "SCREENING_SUPERSESSION"):
            self.graph()

    def test_superseding_older_revision_disposes_logical_predecessor(self):
        original = row(self.data, "SCR-A-TA")
        append(original, reason="Synthetic later recheck of the same decision.")
        # Put the second revision before the existing full-text decision.
        original["revisions"][-1]["at"] = original["revisions"][0]["at"]
        replacement = copy.deepcopy(original)
        replacement["id"] = "SCR-A-RECHECK-TA"
        replacement["revisions"] = [copy.deepcopy(original["revisions"][0])]
        replacement["revisions"][0]["data"]["supersedes_ref"] = ref("SCR-A-TA", 1)
        self.data["records"].append(replacement)
        result = evidence_flow(self.graph())
        self.assertEqual(result["screening"]["title_abstract"]["include"], 2)

    def test_explicit_scope_reports_missing_decisions_without_completion(self):
        self.data["records"] = [r for r in self.data["records"]
                                if r["id"] not in {"SCR-B-TA", "SCR-B-FT"}]
        graph = self.graph()
        report = screening_coverage(graph, source_ids=["SRC-B", "SRC-A"],
                                    protocol_version=body(self.data, "SCR-A-TA")["protocol_version"])
        self.assertEqual(report["source_count"], 2)
        self.assertEqual(report["missing_title_abstract"], ["SRC-B"])
        self.assertEqual(report["acceptance"], "not_evaluated")
        self.assertEqual(evidence_flow(graph)["screening_coverage"]["resolved_search_publications_without_screening"], ["SRC-B"])
        with self.assertRaisesRegex(ValidationError, "SCREENING_SCOPE"):
            screening_coverage(graph, source_ids=["SRC-A", "SRC-A"], protocol_version="v1")
        with self.assertRaisesRegex(ValidationError, "SCREENING_SCOPE"):
            screening_coverage(graph, source_ids=["STUDY-ONE"], protocol_version="v1")

    def test_coverage_and_track_counts_are_order_independent(self):
        expected = evidence_flow(self.graph())
        self.data["records"].reverse()
        self.assertEqual(expected, evidence_flow(self.graph()))


class GeneratorHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.record = copy.deepcopy(row(snapshots()["valid_all_families"], "HIT-FIXTURE-1"))
        self.path = "research/searches/example/HIT-FIXTURE-1.json"

    def test_rebuild_preserves_later_hit_resolution_and_exact_bytes(self):
        current = copy.deepcopy(self.record)
        append(current, resolution_reason="Synthetic later identity adjudication; old discovery is retained.")
        target = self.root / self.path
        target.parent.mkdir(parents=True)
        target.write_text(dumps(current), encoding="utf-8")
        before = target.read_bytes()
        write_generated_records(self.root, {self.path: self.record})
        self.assertEqual(target.read_bytes(), before)

    def test_rebuild_rejects_rewritten_original_before_any_record_is_written(self):
        write_generated_records(self.root, {self.path: self.record})
        changed = copy.deepcopy(self.record)
        changed["revisions"][0]["data"]["raw_metadata"] = "Rewritten synthetic discovery"
        extra = copy.deepcopy(self.record)
        extra["id"] = "HIT-AAA"
        before = (self.root / self.path).read_bytes()
        with self.assertRaisesRegex(ValidationError, "HISTORY"):
            write_generated_records(self.root, {self.path: changed, "research/searches/example/HIT-AAA.json": extra})
        self.assertEqual((self.root / self.path).read_bytes(), before)
        self.assertFalse((self.root / "research/searches/example/HIT-AAA.json").exists())

    def test_explicit_append_preserves_old_revision(self):
        write_generated_records(self.root, {self.path: self.record})
        extended = copy.deepcopy(self.record)
        append(extended, resolution_reason="Synthetic later identity adjudication.")
        write_generated_records(self.root, {self.path: extended})
        self.assertEqual((self.root / self.path).read_text(encoding="utf-8"), dumps(extended))

    def test_identity_root_is_allowed_without_widening_registry_access(self):
        from tests.test_record_loading import live_gate_sentinel, state
        manifest = state()
        manifest["record_roots"] = ["research/registry/identity"]
        target = self.root / "research/registry/state.json"
        target.parent.mkdir(parents=True)
        target.write_text(dumps(manifest), encoding="utf-8")
        sentinel = live_gate_sentinel()
        record_path = self.root / "research/registry/identity" / (sentinel["id"] + ".json")
        record_path.parent.mkdir()
        record_path.write_text(dumps(sentinel), encoding="utf-8")
        data, _ = load_registry(self.root)
        self.assertEqual([r["id"] for r in data["records"]], [sentinel["id"]])
        manifest["record_roots"] = ["research/registry"]
        target.write_text(dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "RECORD_ROOT"):
            load_registry(self.root)


if __name__ == "__main__":
    unittest.main()
