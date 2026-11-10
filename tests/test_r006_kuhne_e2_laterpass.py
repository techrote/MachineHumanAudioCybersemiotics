"""R006 Kühne later-pass audit: noncanonical decision safeguards."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECHECK = ROOT / "research/screening/r006_kuhne_e2_laterpass_20261110/RECHECK.json"
FIRST = ROOT / "research/screening/r006_r004_crosslane_20261110/DECISIONS.json"
SECOND = ROOT / "research/screening/r006_fulltext_e2_review_20261110/DECISIONS.json"
SOURCE = ROOT / "research/sources/related/records/SRC-REL-KUHNE-2020.json"


def validate_recheck(value, first, second, source):
    if value.get("issue") != 6 or value.get("evidence_cutoff") != "2026-10-04":
        raise ValueError("Frozen issue/cutoff drift")
    if value.get("kind") != "issue_scoped_noncanonical_later_pass_eligibility_audit":
        raise ValueError("False canonical status")
    if value["agent"].get("kind") != "agent" or value["agent"].get("independent_human_reviewer") is not False:
        raise ValueError("Human reviewer spoofing")
    if value["agent"].get("blinded_to_prior_screening") is not False:
        raise ValueError("Misrepresented blinded review")
    prior = next(x for x in first["decisions"] if x["source_ref"]["id"] == "SRC-REL-KUHNE-2020")
    previous = next(x for x in second["source_reviews"] if x["source_ref"]["id"] == "SRC-REL-KUHNE-2020")
    if prior["decision"] != "uncertain" or prior["source_ref"] != {"id":"SRC-REL-KUHNE-2020","rev":1}:
        raise ValueError("Prior TA history mismatch")
    if (previous["proposed_decision"] != "exclude" or previous["rule_failure"] != "E-NOT-MACHINE-MESSAGE"
            or previous["verification"] != "single_agent_preliminary_full_text_exclusion_not_second_pass"):
        raise ValueError("Prior FT history mismatch")
    s = value["source"]
    if s["id"] != "SRC-REL-KUHNE-2020" or s["rev"] != 1 or s["doi"] != "10.3389/fnbot.2020.593732":
        raise ValueError("Source identity drift")
    if (source["id"] != s["id"] or source["kind"] != "source" or source.get("synthetic") is not False
            or source["revisions"][-1]["rev"] != s["rev"]):
        raise ValueError("Accepted source revision changed")
    rev = source["revisions"][-1]["data"]
    if rev["metadata_status"] != "verified" or rev["validity"] != "active":
        raise ValueError("Source status not independently stable")
    if s["doi"] not in {i["value"].lower() for i in rev["identifiers"] if i["scheme"] == "doi" and i["status"] == "verified"}:
        raise ValueError("DOI provenance no longer accepted")
    if s["local_original_bytes_obtained"] is not False or s["local_sha256_reverified"] is not False or s["pdf_or_figures_inspected_this_pass"] is not False:
        raise ValueError("Fabricated source access or hash")
    if (len(s["locators"]) < 4 or len(value["hard_negative_cases"]) != 3
            or any(not x.get("finding") or not x.get("section") for x in s["locators"])
            or any(not x.get("why_not_G01_here") for x in value["hard_negative_cases"])):
        raise ValueError("Missing source-grounded E2 adversarial checks")
    if value["later_pass_rule_assessment"] != {f"E{i}": ("no" if i == 2 else "yes") for i in range(1, 7)}:
        raise ValueError("Frozen E1-E6 judgement changed")
    outcome = value["result"]
    if outcome["rechecked_proposed_fulltext_decision"] != "exclude" or outcome["rechecked_frozen_reason"] != "E-NOT-MACHINE-MESSAGE":
        raise ValueError("Unreviewed admission or exclusion change")
    if (outcome["verification_status"] != "same_model_class_AI_assisted_later_pass_not_independent_human"
            or outcome["canonical_fulltext_SCR_created"] is not False or outcome["selected_corpus_ready"] is not False
            or outcome["track_G_voice_affect_relevance_preserved"] is not True):
        raise ValueError("Scientific verification/selection falsely promoted")
    for name in ("canonical_SCR_created","canonical_STUDY_created","canonical_SAMPLE_created",
                 "admitted_empirical_studies","independent_samples_counted"):
        if outcome[name] != 0:
            raise ValueError("Unadjudicated units counted")
    return True


class KuhneE2LaterPassTests(unittest.TestCase):
    def setUp(self):
        self.value = json.loads(RECHECK.read_text(encoding="utf-8"))
        self.first = json.loads(FIRST.read_text(encoding="utf-8"))
        self.second = json.loads(SECOND.read_text(encoding="utf-8"))
        self.source = json.loads(SOURCE.read_text(encoding="utf-8"))

    def assert_invalid(self, changed):
        with self.assertRaises(ValueError):
            validate_recheck(changed, self.first, self.second, self.source)

    def test_actual_checkpoint_valid(self):
        self.assertTrue(validate_recheck(self.value, self.first, self.second, self.source))

    def test_source_revision_invalidation(self):
        edited = copy.deepcopy(self.source)
        edited["revisions"][-1]["rev"] = 2
        with self.assertRaises(ValueError):
            validate_recheck(self.value, self.first, self.second, edited)

    def test_doi_collision_rejected(self):
        changed = copy.deepcopy(self.value)
        changed["source"]["doi"] = "10.1145/3711938"
        self.assert_invalid(changed)

    def test_new_cutoff_rejected(self):
        changed = copy.deepcopy(self.value)
        changed["evidence_cutoff"] = "2026-11-10"
        self.assert_invalid(changed)

    def test_independent_human_claim_rejected(self):
        changed = copy.deepcopy(self.value)
        changed["agent"]["independent_human_reviewer"] = True
        self.assert_invalid(changed)

    def test_unblinded_review_not_relabelled_blinded(self):
        changed = copy.deepcopy(self.value)
        changed["agent"]["blinded_to_prior_screening"] = True
        self.assert_invalid(changed)

    def test_pdf_hash_claim_rejected(self):
        changed = copy.deepcopy(self.value)
        changed["source"]["local_sha256_reverified"] = True
        self.assert_invalid(changed)

    def test_e2_inclusion_rejected(self):
        changed = copy.deepcopy(self.value)
        changed["later_pass_rule_assessment"]["E2"] = "yes"
        self.assert_invalid(changed)

    def test_unverified_independent_sample_rejected(self):
        changed = copy.deepcopy(self.value)
        changed["result"]["independent_samples_counted"] = 1
        self.assert_invalid(changed)

    def test_false_live_scr_admission_rejected(self):
        changed = copy.deepcopy(self.value)
        changed["result"]["canonical_SCR_created"] = 1
        self.assert_invalid(changed)

    def test_adversarial_counterexample_removed_rejected(self):
        changed = copy.deepcopy(self.value)
        changed["hard_negative_cases"].pop()
        self.assert_invalid(changed)

    def test_prior_history_change_rejected(self):
        changed_first = copy.deepcopy(self.first)
        next(x for x in changed_first["decisions"] if x["source_ref"]["id"] == "SRC-REL-KUHNE-2020")["decision"] = "include"
        with self.assertRaises(ValueError):
            validate_recheck(self.value, changed_first, self.second, self.source)


if __name__ == "__main__":
    unittest.main()
