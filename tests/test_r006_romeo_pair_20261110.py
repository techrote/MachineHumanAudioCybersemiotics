"""R006 identity constraints; all deliberately corrupted cases are in-memory test inputs."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "research/registry/identity/romeo_pair_20261110/validate.py"
spec = importlib.util.spec_from_file_location("r006_romeo_validator", VALIDATOR)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class RomeoPublicationExperimentBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = mod.load()
        cls.sources = mod.read_sources()

    def check_mutation(self, mutate):
        value = copy.deepcopy(self.baseline)
        mutate(value)
        with self.assertRaises(ValueError):
            mod.check(value, self.sources)

    def test_source_pinned_candidate_counts_not_corpus_counts(self):
        self.assertEqual(
            mod.check(self.baseline, self.sources),
            {"publications_checked": 2, "experiment_candidates": 4,
             "verified_independent_samples": 0, "canonical_screenings_added": 0}
        )

    def test_doi_collision_cannot_collapse_distinct_publications(self):
        self.check_mutation(
            lambda d: d["publications"][1].update(doi=d["publications"][0]["doi"])
        )

    def test_four_experiments_cannot_be_four_independent_samples(self):
        self.check_mutation(
            lambda d: d["experiment_candidates"][3].update(counted_independent_sample=True)
        )

    def test_reported_participants_cannot_become_accepted_corpus_count(self):
        self.check_mutation(lambda d: d["decisions"].update(admitted_independent_samples=110))

    def test_abstract_and_supplement_listing_are_not_2023_full_text(self):
        self.check_mutation(
            lambda d: d["evidence"][1].update(reading="full_item_read")
        )

    def test_cannot_claim_stimulus_reuse_without_file_comparison(self):
        self.check_mutation(
            lambda d: d["identity_assessment"].update(stimuli="same_audio_verified")
        )

    def test_cannot_assume_conference_paper_extended_into_journal(self):
        self.check_mutation(
            lambda d: d["identity_assessment"].update(family_relation="confirmed_extension")
        )

    def test_cannot_invent_participant_overlap_adjudication(self):
        self.check_mutation(
            lambda d: d["identity_assessment"].update(samples="independent")
        )

    def test_cannot_invent_independent_human_review(self):
        self.check_mutation(
            lambda d: d["verification_gates"].update(independent_human_screening=True)
        )

    def test_source_correction_invalidates_pinned_review(self):
        srcs = copy.deepcopy(self.sources)
        srcs["SRC-REL-ROMEO-2025"]["revisions"][0]["data"]["validity"] = "corrected"
        with self.assertRaises(ValueError):
            mod.check(self.baseline, srcs)

    def test_new_source_revision_invalidates_pinned_review(self):
        srcs = copy.deepcopy(self.sources)
        srcs["SRC-REL-ROMEO-2023"]["revisions"].append(
            copy.deepcopy(srcs["SRC-REL-ROMEO-2023"]["revisions"][0])
        )
        srcs["SRC-REL-ROMEO-2023"]["revisions"][-1]["rev"] = 2
        with self.assertRaises(ValueError):
            mod.check(self.baseline, srcs)

    def test_source_reference_swap_rejected(self):
        self.check_mutation(
            lambda d: d["experiment_candidates"][1].update(publication="SRC-REL-ROMEO-2025")
        )


if __name__ == "__main__":
    unittest.main()
