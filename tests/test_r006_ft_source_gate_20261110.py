"""Source/identity/negative-control tests for R006 dated FT gate; no live SCR admission."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/screening/r006_ft_source_gate_20261110/check_gate.py"
spec = importlib.util.spec_from_file_location("r006_ft_gate_20261110", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class FullTextSourceGateTests(unittest.TestCase):
    def setUp(self):
        self.data = gate.load(gate.LEDGER)
        self.sources = {sid: gate.load(gate.SOURCES / (sid + ".json"))
                        for sid in gate.DOIS}
        self.titles = {sid: gate.load(gate.SCREEN /
                       ("SCR-R006-" + sid.removeprefix("SRC-") + "-TA.json"))
                       for sid in gate.DOIS}
        self.later = gate.load(gate.LATER)
        self.first_ft = gate.load(gate.FIRST_FT)

    def audit(self):
        return gate.inspect(self.data, sources=self.sources, titles=self.titles,
                            later=self.later, first_ft=self.first_ft)

    def case(self, source):
        return next(x for x in self.data["cases"] if x["source_id"] == source)

    def test_live_four_title_abstract_pins_and_actual_ready_subset(self):
        counts = self.audit()
        self.assertEqual(counts["canonical_title_abstract_at_base"], 4)
        self.assertEqual(counts["canonical_full_text_at_base"], 0)
        self.assertEqual(counts["source_located_ft_exclusion_candidate_pending_integration"], 1)
        self.assertEqual(counts["blocked_ft_candidates"], 3)
        self.assertEqual(counts["proposed_independent_studies_or_samples"], 0)

    def test_duplicate_or_missing_candidate_is_rejected(self):
        self.data["cases"].append(copy.deepcopy(self.data["cases"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.audit()
        self.data["cases"] = self.data["cases"][:3]
        with self.assertRaisesRegex(ValueError, "Missing"):
            self.audit()

    def test_changed_doi_or_source_revision_requires_requalification(self):
        row = self.case("SRC-REL-ROMEO-2023")
        row["doi"] = "10.1145/3711938"
        with self.assertRaisesRegex(ValueError, "DOI collision"):
            self.audit()
        row["doi"] = gate.DOIS[row["source_id"]]
        row["source_rev"] = 2
        with self.assertRaisesRegex(ValueError, "revision"):
            self.audit()

    def test_live_source_verified_doi_cannot_be_replaced(self):
        source = self.sources["SRC-REL-BECKER-2025"]
        source["revisions"][0]["data"]["identifiers"][0]["value"] = "10.1145/incorrect"
        with self.assertRaisesRegex(ValueError, "verified matching DOI"):
            self.audit()

    def test_inactive_source_revision_invalidates_gate(self):
        self.sources["SRC-REL-KUHNE-2020"]["revisions"][0]["data"]["validity"] = "withdrawn"
        with self.assertRaisesRegex(ValueError, "invalidated"):
            self.audit()

    def test_canonical_title_abstract_drift_blocks_admission(self):
        self.titles["SRC-REL-KUHNE-2020"]["revisions"][0]["data"]["decision"] = "exclude"
        with self.assertRaisesRegex(ValueError, "stage or decision drift"):
            self.audit()

    def test_cannot_silently_promote_romeo_2023_from_awaiting_text(self):
        self.case("SRC-REL-ROMEO-2023")["proposed_full_text_decision"] = "include"
        with self.assertRaisesRegex(ValueError, "Forbidden FT transition"):
            self.audit()

    def test_false_original_pdf_hash_or_audio_claim_is_rejected(self):
        k = self.case("SRC-REL-KUHNE-2020")["source_access"]
        k["original_pdf_sha256_reverified"] = True
        with self.assertRaisesRegex(ValueError, "Fabricated full text"):
            self.audit()
        k["original_pdf_sha256_reverified"] = False
        k["sound_played"] = True
        with self.assertRaisesRegex(ValueError, "Fabricated full text"):
            self.audit()

    def test_unverified_page_ranges_and_manifest_rejected(self):
        self.case("SRC-REL-KUHNE-2020")["source_access"]["file_pages_1based"] = [1, 16]
        with self.assertRaisesRegex(ValueError, "Reading locator"):
            self.audit()
        self.case("SRC-REL-KUHNE-2020")["source_access"]["file_pages_1based"] = [1, 4, 5]
        self.case("SRC-REL-ROMEO-2025")["registered_manifestation"] = {"id": "invented"}
        with self.assertRaisesRegex(ValueError, "Unregistered manifestation"):
            self.audit()

    def test_cannot_claim_rehashed_inherited_pdf(self):
        self.case("SRC-REL-KUHNE-2020")["registered_manifestation"]["hash_reverified_this_run"] = True
        with self.assertRaisesRegex(ValueError, "Incorrect inherited"):
            self.audit()

    def test_invented_independent_human_or_blinded_recheck_rejected(self):
        self.later["agent"]["independent_human_reviewer"] = True
        with self.assertRaisesRegex(ValueError, "False exclusion recheck"):
            self.audit()
        self.later["agent"]["independent_human_reviewer"] = False
        self.case("SRC-REL-KUHNE-2020")["separate_later_recheck"]["blinded"] = True
        with self.assertRaisesRegex(ValueError, "impersonated"):
            self.audit()

    def test_no_fake_counts_or_second_reviewer(self):
        self.data["canonical_checkpoint"]["studies"] = 1
        with self.assertRaisesRegex(ValueError, "count inflation"):
            self.audit()
        self.data["canonical_checkpoint"]["studies"] = 0
        self.data["actor"]["human"] = True
        with self.assertRaisesRegex(ValueError, "False human"):
            self.audit()

    def test_invalid_lawful_url_or_lost_section_locator_rejected(self):
        self.case("SRC-REL-BECKER-2025")["source_access"]["url"] = "http://localhost/article"
        with self.assertRaisesRegex(ValueError, "lawful source"):
            self.audit()
        self.case("SRC-REL-BECKER-2025")["source_access"]["url"] = (
            "https://www2.informatik.uni-hamburg.de/wtm/publications/2025/BBCKOAGSFW25/3706066.pdf")
        self.case("SRC-REL-BECKER-2025")["source_access"]["reading_scope"] = ""
        with self.assertRaisesRegex(ValueError, "reading extent"):
            self.audit()

    def test_original_prior_provisional_exclusion_is_not_rewritten(self):
        k = next(r for r in self.first_ft["source_reviews"]
                 if r["source_ref"]["id"] == "SRC-REL-KUHNE-2020")
        k["rule_failure"] = None
        with self.assertRaisesRegex(ValueError, "Unreviewed changed"):
            self.audit()


if __name__ == "__main__":
    unittest.main()
