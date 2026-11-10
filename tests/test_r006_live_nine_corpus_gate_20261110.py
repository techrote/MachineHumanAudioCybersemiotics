"""Negative controls for the live nine-publication R006 corpus preflight.

These are *synthetic mutations of in-memory copies*; no participant/sample
data, primary-source access or reviewer identity is established by a PASS.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research/screening/r006_live_corpus_gate_20261110/check_live.py"
spec = importlib.util.spec_from_file_location("r006_nine_live_gate", PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class NineCanonicalAdmissionGateTests(unittest.TestCase):
    def setUp(self):
        self.source, self.ta, self.ft, self.aid, self.flow = copy.deepcopy(gate.inputs())

    def check(self):
        return gate.evaluate(self.source, self.ta, self.ft, self.aid, self.flow)

    def test_real_canonical_nine_are_serialized_in_live_exports(self):
        report = self.check()
        self.assertEqual(report["canonical_ta_in_scope"], 9)
        self.assertEqual(len(report["cases"]), 9)
        self.assertEqual(
            sum(report["canonical_ft_in_scope"].values()), 9
        )
        self.assertFalse(report["scientific_admission_evaluated"])
        self.assertEqual(report["global_included_studies"], self.flow["included_studies"])
        self.assertEqual(report["global_samples"], self.flow["samples"])

    def test_original_four_are_not_recreated_as_new_screening_records(self):
        self.assertEqual(
            set(gate.CASES) & {
                "SRC-REL-BECKER-2025", "SRC-REL-KUHNE-2020",
                "SRC-REL-ROMEO-2023", "SRC-REL-ROMEO-2025"
            },
            {
                "SRC-REL-BECKER-2025", "SRC-REL-KUHNE-2020",
                "SRC-REL-ROMEO-2023", "SRC-REL-ROMEO-2025"
            },
        )
        self.assertEqual(self.check()["cases"]["SRC-REL-KUHNE-2020"]["full_text"], "exclude")

    def test_unmanifested_stevens_cannot_become_ft_inclusion(self):
        sid = "SRC-R006-E-STEVENS-INFORMATIVE"
        self.ft[sid]["revisions"][-1]["data"]["decision"] = "include"
        with self.assertRaisesRegex(ValueError, "manifested performed reading"):
            self.check()

    def test_unmanifested_becker_cannot_become_ft_inclusion(self):
        sid = "SRC-REL-BECKER-2025"
        self.ft[sid]["revisions"][-1]["data"]["decision"] = "include"
        with self.assertRaisesRegex(ValueError, "manifested performed reading"):
            self.check()

    def test_romeo_2023_supplement_does_not_license_parent_article_include(self):
        sid = "SRC-REL-ROMEO-2023"
        self.ft[sid]["revisions"][-1]["data"]["decision"] = "include"
        with self.assertRaisesRegex(ValueError, "manifested performed reading"):
            self.check()

    def test_invented_human_first_assessor_is_refused(self):
        sid = "SRC-R006-H-SABIC-UNDERSTANDING"
        self.ta[sid]["revisions"][0]["actor"]["kind"] = "human"
        with self.assertRaisesRegex(ValueError, "historical AI assessor"):
            self.check()

    def test_wrong_doi_fails_not_merely_renames_experiment(self):
        sid = "SRC-REL-ROMEO-2025"
        self.source[sid]["revisions"][-1]["data"]["identifiers"][0]["value"] = "10.1145/3706066"
        with self.assertRaisesRegex(ValueError, "DOI"):
            self.check()

    def test_duplicate_revision_is_not_permitted(self):
        sid = "SRC-R006-NEES-2016-MEMORY"
        self.ft[sid]["revisions"][-1]["rev"] = 2
        with self.assertRaisesRegex(ValueError, "noncontiguous"):
            self.check()

    def test_missing_original_kuhne_manifest_blocks_decisive_exclusion(self):
        sid = "SRC-REL-KUHNE-2020"
        self.source[sid]["revisions"][-1]["data"]["manifestations"] = []
        with self.assertRaisesRegex(ValueError, "manifested performed reading"):
            self.check()

    def test_unknown_kuhne_reading_ref_fails_closed(self):
        sid = "SRC-REL-KUHNE-2020"
        self.ft[sid]["revisions"][-1]["data"]["reading_refs"] = [{"id":"AID-FAKE-READER", "rev":1}]
        with self.assertRaisesRegex(ValueError, "missing, synthetic or wrong canonical record"):
            self.check()

    def test_canonical_export_status_disagreement_is_rejected(self):
        coverage = self.flow["screening_coverage"]["decision_scopes"]
        for scope in coverage:
            for item in scope.get("sources", []):
                if item["source_id"] == "SRC-R006-E-STEVENS-INFORMATIVE":
                    item["full_text"] = "include"
        with self.assertRaisesRegex(ValueError, "STALE_EXPORT"):
            self.check()

    def test_global_export_underreport_rejected(self):
        self.flow["screening_by_track"]["empirical"]["full_text"]["pending"] = 0
        with self.assertRaisesRegex(ValueError, "STALE_EXPORT"):
            self.check()

    def test_future_other_source_addition_does_not_freeze_global_counts(self):
        # Purely synthetic counter increments; scientific admission is NOT inferred.
        self.flow["included_studies"] += 2
        self.flow["experiments"] += 2
        self.flow["samples"] += 2
        report = self.check()
        self.assertEqual(report["global_included_studies"], self.flow["included_studies"])
        self.assertFalse(report["scientific_admission_evaluated"])


if __name__ == "__main__":
    unittest.main()
