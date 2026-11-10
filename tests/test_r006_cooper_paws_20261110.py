"""R006 PAWS publication-family adverse identity and screening tests."""
import copy
import json
import sys
import unittest
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "research/registry/identity/cooper_paws_20261110"
spec = spec_from_file_location("r006_cooper_paws_guard", FOLDER / "validate.py")
guard = module_from_spec(spec)
spec.loader.exec_module(guard)


class CooperPAWSIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((FOLDER / "EVIDENCE.json").read_text(encoding="utf-8"))

    def invalid(self, edit):
        item = copy.deepcopy(self.data)
        edit(item)
        with self.assertRaises(ValueError):
            guard.validate(item)

    def test_valid_source_bound_handoff(self):
        self.assertTrue(guard.validate(self.data))

    def test_reject_wrong_cutoff(self):
        self.invalid(lambda d: d.__setitem__("evidence_cutoff", "2026-11-10"))

    def test_reject_fictional_human_reviewer(self):
        self.invalid(lambda d: d["actor"].__setitem__("kind", "human"))

    def test_reject_canonical_screening_promotion(self):
        self.invalid(lambda d: d["canonical_admission"].__setitem__("screening_records_added", 3))

    def test_reject_selected_corpus_promotion(self):
        self.invalid(lambda d: d["canonical_admission"].__setitem__("selected_corpus_ready", True))

    def test_reject_unverified_original_pdf_hash(self):
        self.invalid(lambda d: d["source_consultation"][2].__setitem__("original_pdf_bytes_hashed", True))

    def test_reject_invented_thesis_doi(self):
        self.invalid(lambda d: d["source_consultation"][1].__setitem__("doi", "10.1108/ocj-03-2021-0006"))

    def test_reject_aliasing_distinct_journals(self):
        self.invalid(lambda d: d["source_consultation"][0].__setitem__("doi", "10.1108/ocj-03-2021-0006"))

    def test_reject_unread_2021_full_text(self):
        self.invalid(lambda d: d["source_consultation"][2].__setitem__("full_item_read", True))

    def test_reject_32_sme_counted_three_times(self):
        self.invalid(lambda d: d["cross_report_phase_map"][0].__setitem__("n_as_reported", 96))

    def test_reject_205_users_counted_twice(self):
        self.invalid(lambda d: d["cross_report_phase_map"][2].__setitem__("n_as_reported", 410))

    def test_reject_missing_pilot_phase(self):
        self.invalid(lambda d: d["cross_report_phase_map"].pop(1))

    def test_reject_independent_cohort_assertion(self):
        self.invalid(lambda d: d["cross_report_phase_map"][2].__setitem__("independent_sample_status", "resolved_independent"))

    def test_reject_premature_2020_screening_exclusion(self):
        self.invalid(lambda d: d["track_e_provisional"][0].__setitem__("decision", "exclude"))

    def test_reject_fake_independent_sample_count(self):
        self.invalid(lambda d: d["decision"].__setitem__("independent_empirical_sample_count", 242))

    def test_reject_source_lost(self):
        self.invalid(lambda d: d["source_consultation"].pop(0))


if __name__ == "__main__":
    unittest.main()
