"""R006 live four-candidate screening/manifest preflight: negative controls.

These tests inspect canonical text records. They do not certify primary
publication reading, author-reported participants, or human assessment.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/screening/r006_live_source_preflight_20261110/audit.py"
spec = importlib.util.spec_from_file_location("r006_live_source_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class LiveFourCandidatePreflightTests(unittest.TestCase):
    def setUp(self):
        inputs = audit.canonical_inputs()
        self.sources, self.ta, self.ft, self.readings, self.flow = copy.deepcopy(inputs)

    def run_gate(self):
        return audit.evaluate(self.sources, self.ta, self.ft, self.readings, self.flow)

    def test_four_source_decisions_match_live_graph_without_freezing_future_counts(self):
        result = self.run_gate()
        self.assertEqual(result["canonical_title_abstract"], len(audit.DOIS))
        self.assertEqual(result["canonical_full_text_decisions"],
                         sum(record is not None for record in self.ft.values()))
        self.assertEqual(result["canonical_full_text_includes"],
                         sum(record is not None and
                             audit.latest(record)["data"]["decision"] == "include"
                             for record in self.ft.values()))
        self.assertEqual(result["canonical_eligible_studies"], self.flow["included_studies"])
        self.assertEqual(result["canonical_samples"], self.flow["samples"])
        self.assertEqual(set(result["source_gate_rows"]), set(audit.DOIS))

    def test_canonical_abstract_and_doi_cannot_drift(self):
        self.sources["SRC-REL-BECKER-2025"]["revisions"][0]["data"]["identifiers"][0]["value"] = "10.1145/other"
        with self.assertRaisesRegex(ValueError, "DOI"):
            self.run_gate()

    def test_title_abstract_cannot_be_rewritten_as_exclusion(self):
        self.ta["SRC-REL-ROMEO-2025"]["revisions"][0]["data"]["decision"] = "exclude"
        with self.assertRaisesRegex(ValueError, "Title/abstract"):
            self.run_gate()

    def test_fulltext_include_requires_real_reading_event(self):
        rec = copy.deepcopy(self.ft["SRC-REL-KUHNE-2020"])
        rec["id"] = "SCR-R006-REL-ROMEO-2025-FT"
        rec["revisions"][0]["data"].update({
            "source_ref": {"id": "SRC-REL-ROMEO-2025", "rev": 1},
            "decision": "include", "reading_refs": [],
        })
        self.ft["SRC-REL-ROMEO-2025"] = rec
        with self.assertRaisesRegex(ValueError, "reading AID"):
            self.run_gate()

    def test_reading_cannot_use_unregistered_manifestation(self):
        self.sources["SRC-REL-KUHNE-2020"]["revisions"][0]["data"]["manifestations"] = []
        with self.assertRaisesRegex(ValueError, "missing source manifestation"):
            self.run_gate()

    def test_new_reading_revision_after_decision_fails(self):
        reading = self.readings["AID-R006-KUHNE-2020-FT-PAGES"]
        later = copy.deepcopy(reading["revisions"][-1])
        later["rev"] = 2
        later["at"] = "2026-11-10T09:07:00Z"
        reading["revisions"].append(later)
        self.ft["SRC-REL-KUHNE-2020"]["revisions"][0]["data"]["reading_refs"][0]["rev"] = 2
        with self.assertRaisesRegex(ValueError, "chronology"):
            self.run_gate()

    def test_actual_reading_event_after_decision_fails(self):
        self.readings["AID-R006-KUHNE-2020-FT-PAGES"]["revisions"][0]["data"]["performed_at"] = {
            "state": "known", "value": "2026-11-10T09:07:00Z"
        }
        with self.assertRaisesRegex(ValueError, "chronology"):
            self.run_gate()

    def test_missing_reading_event_time_fails(self):
        self.readings["AID-R006-KUHNE-2020-FT-PAGES"]["revisions"][0]["data"]["performed_at"] = {
            "state": "unknown", "reason": "Original reading time cannot be established"
        }
        with self.assertRaisesRegex(ValueError, "chronology"):
            self.run_gate()

    def test_first_ft_exclusion_actor_cannot_be_upgraded_to_human(self):
        self.ft["SRC-REL-KUHNE-2020"]["revisions"][0]["actor"]["kind"] = "human"
        with self.assertRaisesRegex(ValueError, "FT historical AI provenance"):
            self.run_gate()

    def test_first_ft_access_decision_actor_cannot_be_upgraded_to_human(self):
        self.ft["SRC-REL-ROMEO-2023"]["revisions"][0]["actor"]["kind"] = "human"
        with self.assertRaisesRegex(ValueError, "FT historical AI provenance"):
            self.run_gate()

    def test_first_reading_actor_cannot_be_upgraded_to_human(self):
        self.readings["AID-R006-KUHNE-2020-FT-PAGES"]["revisions"][0]["actor"]["kind"] = "human"
        with self.assertRaisesRegex(ValueError, "Reading historical AI provenance"):
            self.run_gate()

    def test_reading_cannot_claim_outside_file_extent(self):
        record = self.readings["AID-R006-KUHNE-2020-FT-PAGES"]
        record["revisions"][0]["data"]["ranges"] = [[1, 16]]
        with self.assertRaisesRegex(ValueError, "bounds"):
            self.run_gate()

    def test_generated_flow_must_match_actual_screening(self):
        self.flow["screening_by_track"]["empirical"]["full_text"]["exclude"] = 0
        with self.assertRaisesRegex(ValueError, "STALE_EXPORT"):
            self.run_gate()

    def test_global_counts_can_grow_without_breaking_four_source_audit(self):
        # These synthetic aggregate values deliberately are NOT a certified
        # sample graph. Actual cross-record integrity is tools/validate.py's job.
        self.flow["included_studies"] += 1
        self.flow["experiments"] += 1
        self.flow["samples"] += 1
        result = self.run_gate()
        self.assertEqual(result["canonical_eligible_studies"], self.flow["included_studies"])
        self.assertEqual(result["canonical_samples"], self.flow["samples"])
        self.assertEqual(result["scientific_acceptance"], "not_evaluated")

    def test_fictional_positive_fulltext_transition_does_not_freeze_exclusion(self):
        # Structural hypothetical ONLY: no claim that Kühne meets E2. Reuse
        # the already registered performed page-reading AID and manifestation;
        # source/reading integrity is real, scientific interpretation fictional.
        sid = "SRC-REL-KUHNE-2020"
        self.ft[sid]["revisions"][-1]["data"]["decision"] = "include"
        coverage = self.flow["screening_coverage"]["decision_scopes"]
        for scope in coverage:
            for row in scope.get("sources", []):
                if row["source_id"] == sid:
                    row["full_text"] = "include"
        self.flow["screening_by_track"]["empirical"]["full_text"]["exclude"] -= 1
        self.flow["screening_by_track"]["empirical"]["full_text"]["include"] += 1
        self.flow["included_publications"] += 1
        result = self.run_gate()
        self.assertEqual(result["canonical_full_text_includes"], 1)
        self.assertEqual(result["source_gate_rows"][sid]["full_text"], "include")
        self.assertEqual(result["scientific_acceptance"], "not_evaluated")

    def test_a_per_source_export_disagreement_still_fails_closed(self):
        scoped = self.flow["screening_coverage"]["decision_scopes"]
        for scope in scoped:
            for row in scope.get("sources", []):
                if row["source_id"] == "SRC-REL-KUHNE-2020":
                    row["full_text"] = "include"
        with self.assertRaisesRegex(ValueError, "STALE_EXPORT"):
            self.run_gate()

    def test_invalid_generated_global_count_is_rejected(self):
        self.flow["samples"] = -1
        with self.assertRaisesRegex(ValueError, "STALE_EXPORT"):
            self.run_gate()

    def test_missing_decision_actor_id_rejected(self):
        # The initial accepted registrar is immutable; test a bad append instead.
        history = self.ta["SRC-REL-BECKER-2025"]["revisions"]
        new_revision = copy.deepcopy(history[-1])
        new_revision["rev"] += 1
        new_revision["at"] = "2026-11-10T09:45:00Z"
        new_revision["actor"]["id"] = ""
        history.append(new_revision)
        with self.assertRaisesRegex(ValueError, "Missing TA decision actor"):
            self.run_gate()

    def test_original_agent_registrar_cannot_be_relabelled_human(self):
        initial = self.ta["SRC-REL-BECKER-2025"]["revisions"][0]
        initial["actor"]["kind"] = "human"
        with self.assertRaisesRegex(ValueError, "historical registration provenance"):
            self.run_gate()

    def test_original_agent_registration_timestamp_cannot_be_rewritten(self):
        initial = self.ta["SRC-REL-BECKER-2025"]["revisions"][0]
        initial["at"] = "2026-11-10T08:11:17Z"
        with self.assertRaisesRegex(ValueError, "historical registration provenance"):
            self.run_gate()

    def test_original_title_abstract_pin_survives_later_source_revision(self):
        row = self.sources["SRC-REL-ROMEO-2025"]
        revision = copy.deepcopy(row["revisions"][0])
        revision["rev"] = 2
        revision["at"] = "2026-11-10T10:20:00Z"
        revision["data"]["manifestations"] = [{
            "id": "DUMMY-ONLY-SYNTHETIC-TEST",
            "sha256": "a" * 64,
            "extent": 23,
            "coordinate": "pdf_page_0based",
        }]
        row["revisions"].append(revision)
        result = self.run_gate()
        self.assertEqual(result["source_gate_rows"]["SRC-REL-ROMEO-2025"]["source_revision"], 2)
        if self.ft["SRC-REL-ROMEO-2025"] is None:
            self.assertEqual(result["source_gate_rows"]["SRC-REL-ROMEO-2025"]["gate"],
                             "r006_full_text_screening")
        else:
            self.assertEqual(result["source_gate_rows"]["SRC-REL-ROMEO-2025"]["gate"],
                             "accepted_full_text_decision_requires_scientific_review")


if __name__ == "__main__":
    unittest.main()
