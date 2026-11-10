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

    def test_current_main_is_two_fulltext_decisions_zero_included_studies(self):
        result = self.run_gate()
        self.assertEqual(result["canonical_title_abstract"], 4)
        self.assertEqual(result["canonical_full_text_decisions"], 2)
        self.assertEqual(result["canonical_full_text_includes"], 0)
        self.assertEqual(result["canonical_eligible_studies"], 0)
        self.assertEqual(result["canonical_samples"], 0)
        self.assertEqual(result["source_gate_rows"]["SRC-REL-KUHNE-2020"]["full_text"], "exclude")
        self.assertEqual(result["source_gate_rows"]["SRC-REL-ROMEO-2023"]["full_text"], "awaiting_text")
        for sid in ("SRC-REL-BECKER-2025", "SRC-REL-ROMEO-2025"):
            self.assertEqual(result["source_gate_rows"][sid]["gate"],
                             "source_owner_register_hashed_manifestation")

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

    def test_reading_cannot_claim_outside_file_extent(self):
        record = self.readings["AID-R006-KUHNE-2020-FT-PAGES"]
        record["revisions"][0]["data"]["ranges"] = [[1, 16]]
        with self.assertRaisesRegex(ValueError, "bounds"):
            self.run_gate()

    def test_generated_flow_must_match_actual_screening(self):
        self.flow["screening_by_track"]["empirical"]["full_text"]["exclude"] = 0
        with self.assertRaisesRegex(ValueError, "STALE_EXPORT"):
            self.run_gate()

    def test_study_or_sample_counts_are_not_inferred_from_reported_n(self):
        self.flow["samples"] = 2
        with self.assertRaisesRegex(ValueError, "outside this zero-admission"):
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
        self.assertEqual(result["source_gate_rows"]["SRC-REL-ROMEO-2025"]["gate"], "r006_full_text_screening")


if __name__ == "__main__":
    unittest.main()
