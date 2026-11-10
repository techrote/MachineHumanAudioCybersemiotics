"""Adversarial record-integrity checks for a *provisional* R006 full-text triage.

These checks do not replace source fidelity review or the protocol's later
independent-in-time re-examination of full-text exclusions.
"""
from __future__ import annotations

from collections import Counter
import copy
import json
from pathlib import Path
from urllib.parse import urlsplit
import unittest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/screening/r006_fulltext_e2_review_20261110/DECISIONS.json"
FIRST = ROOT / "research/screening/r006_r004_crosslane_20261110/DECISIONS.json"
DOIS = {
    "SRC-REL-KUHNE-2020": "10.3389/fnbot.2020.593732",
    "SRC-REL-ROMEO-2025": "10.1145/3711938",
    "SRC-REL-BECKER-2025": "10.1145/3706066",
}
RULES = {f"E{i}" for i in range(1, 7)}
PROPOSED = {"include", "exclude", "awaiting_text"}


def inspect_ledger(data: dict) -> dict:
    if (data["stage"] != "provisional_source-located_fulltext_eligibility_handoff"
            or data["registry_status"] != "not_registered_no_canonical_SCR"):
        raise ValueError("Unapproved canonical status")
    if data["cutoff"] != "2026-10-04" or data["issue"] != 6:
        raise ValueError("Cutoff/issue altered")
    if (data["actor"]["kind"] != "agent"
            or data["actor"]["id"] != "gpt6-r006-e2-review-20261110"):
        raise ValueError("Invented human or independent reviewer")
    first = json.loads(FIRST.read_text(encoding="utf-8"))
    first_decisions = {row["source_ref"]["id"]: row["decision"] for row in first["decisions"]}
    seen = set()
    outcomes = Counter()
    for row in data["source_reviews"]:
        ref = row["source_ref"]
        sid = ref["id"]
        if sid not in DOIS or sid in seen or ref["rev"] != 1:
            raise ValueError("Unknown, duplicate or repinned source")
        seen.add(sid)
        source = json.loads((ROOT / "research/sources/related/records" / (sid + ".json"))
                            .read_text(encoding="utf-8"))
        if source["id"] != sid or source["kind"] != "source":
            raise ValueError("Missing accepted source identity")
        accepted = next((r for r in source["revisions"] if r["rev"] == ref["rev"]), None)
        if accepted is None or accepted["data"]["validity"] != "active":
            raise ValueError("Invalid source revision")
        identifiers = {x["value"].lower() for x in accepted["data"]["identifiers"]
                       if x["scheme"] == "doi" and x["status"] == "verified"}
        if row["doi"] != DOIS[sid] or row["doi"] not in identifiers:
            raise ValueError("DOI not source-verified")
        if row["prior_title_abstract"] != first_decisions[sid]:
            raise ValueError("Unrecorded first-stage change")
        if set(row["assessment"]) != RULES:
            raise ValueError("Incomplete E1-E6 assessment")
        if row["proposed_decision"] not in PROPOSED:
            raise ValueError("Unsupported full-text disposition")
        if row["proposed_decision"] == "include":
            if row["new_stage"] != "full_text_provisional":
                raise ValueError("Full-text stage missing")
            if any(v != "yes" for v in row["assessment"].values()) or row["rule_failure"]:
                raise ValueError("Unsupported inclusion")
        elif row["proposed_decision"] == "exclude":
            if (row["new_stage"] != "full_text_provisional"
                    or row["assessment"]["E2"] != "no"
                    or row["rule_failure"] != "E-NOT-MACHINE-MESSAGE"
                    or "later" not in row["required_next_action"].lower()):
                raise ValueError("Unwarranted or unverified exclusion")
        else:
            if (row["new_stage"] != "full_text_access_disposition"
                    or row["rule_failure"] is not None
                    or not all(v in {"yes_at_abstract", "yes"}
                               for v in row["assessment"].values())):
                raise ValueError("Access failure recoded as scientific exclusion")
        if row["study_or_sample_identity"] != "not_established":
            raise ValueError("Independent study/sample inferred")
        if len(row["source_evidence"]) != 1:
            raise ValueError("Missing or invented source observations")
        ev = row["source_evidence"][0]
        parsed = urlsplit(ev["url"])
        if parsed.scheme != "https" or not parsed.hostname or not ev["locator"]:
            raise ValueError("Missing stable source/section locator")
        if (ev["access_on"] != "2026-11-10"
                or ev["local_source_bytes_verified"] is not False
                or ev["publisher_pdf_sha_reverified"] is not False
                or ev["page_image_checked"] is not False):
            raise ValueError("Fabricated byte, hash or page-image review")
        if ev["text_sections_consulted"] != (row["proposed_decision"] != "awaiting_text"):
            raise ValueError("Unverified full-text access")
        if not row["observations"] or not row["required_next_action"]:
            raise ValueError("Unexplained evidence or remediation")
        outcomes[row["proposed_decision"]] += 1
    if seen != set(DOIS):
        raise ValueError("Incomplete or unexpected tranche")
    expected = {
        "provisional_full_text_include": outcomes["include"],
        "provisional_full_text_exclude": outcomes["exclude"],
        "awaiting_verified_full_text": outcomes["awaiting_text"],
    }
    totals = data["counts"]
    if totals["sources_reviewed"] != len(seen) or any(
        totals[k] != v for k, v in expected.items()
    ):
        raise ValueError("Decision count drift")
    for key in (
        "canonical_screening_records_added", "study_records_added",
        "sample_records_added", "empirical_studies_selected",
        "independent_samples_counted",
    ):
        if totals[key] != 0:
            raise ValueError("Unjustified canonical corpus or sample count")
    for link in data["dependencies"]:
        if "asserted_independent_samples" in link and link["asserted_independent_samples"] != 0:
            raise ValueError("Fabricated independent samples")
        if "study_or_sample_overlap" in link and link["study_or_sample_overlap"] != "unknown":
            raise ValueError("Unverified cross-publication study identity")
    if data["admission_status"] != "Draft_for_integrator_scientific_review_not_accepted_R006_corpus":
        raise ValueError("Premature scientific acceptance")
    if any(data["gate_status"].values()):
        raise ValueError("False dependency or verification gate completion")
    return dict(outcomes)


class FullTextE2ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_current_tranche_and_pinned_sources(self):
        self.assertEqual(inspect_ledger(self.data),
                         {"exclude": 1, "include": 1, "awaiting_text": 1})

    def test_duplicate_or_unverified_source_rejected(self):
        changed = copy.deepcopy(self.data)
        changed["source_reviews"][1]["source_ref"] = changed["source_reviews"][0]["source_ref"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            inspect_ledger(changed)

    def test_false_full_text_inclusion_rejected(self):
        changed = copy.deepcopy(self.data)
        row = next(r for r in changed["source_reviews"]
                   if r["source_ref"]["id"] == "SRC-REL-KUHNE-2020")
        row["proposed_decision"] = "include"
        with self.assertRaisesRegex(ValueError, "Unsupported inclusion"):
            inspect_ledger(changed)

    def test_unverified_full_text_exclusion_rejected(self):
        changed = copy.deepcopy(self.data)
        row = next(r for r in changed["source_reviews"]
                   if r["source_ref"]["id"] == "SRC-REL-KUHNE-2020")
        row["required_next_action"] = "Done"
        with self.assertRaisesRegex(ValueError, "unverified exclusion"):
            inspect_ledger(changed)

    def test_access_failure_cannot_be_exclusion(self):
        changed = copy.deepcopy(self.data)
        row = next(r for r in changed["source_reviews"]
                   if r["source_ref"]["id"] == "SRC-REL-BECKER-2025")
        row["proposed_decision"] = "exclude"
        with self.assertRaisesRegex(ValueError, "exclusion"):
            inspect_ledger(changed)

    def test_missing_source_locator_rejected(self):
        changed = copy.deepcopy(self.data)
        changed["source_reviews"][1]["source_evidence"][0]["locator"] = ""
        with self.assertRaisesRegex(ValueError, "source/section"):
            inspect_ledger(changed)

    def test_unchecked_pdf_image_cannot_be_claimed(self):
        changed = copy.deepcopy(self.data)
        changed["source_reviews"][1]["source_evidence"][0]["page_image_checked"] = True
        with self.assertRaisesRegex(ValueError, "page-image"):
            inspect_ledger(changed)

    def test_human_reviewer_cannot_be_invented(self):
        changed = copy.deepcopy(self.data)
        changed["actor"]["kind"] = "human"
        with self.assertRaisesRegex(ValueError, "reviewer"):
            inspect_ledger(changed)

    def test_independent_samples_cannot_be_inferred(self):
        changed = copy.deepcopy(self.data)
        changed["dependencies"][1]["asserted_independent_samples"] = 2
        with self.assertRaisesRegex(ValueError, "independent samples"):
            inspect_ledger(changed)

    def test_doi_reassignment_rejected(self):
        changed = copy.deepcopy(self.data)
        changed["source_reviews"][1]["doi"] = DOIS["SRC-REL-KUHNE-2020"]
        with self.assertRaisesRegex(ValueError, "DOI"):
            inspect_ledger(changed)

    def test_counts_and_protocol_gate_cannot_drift(self):
        changed = copy.deepcopy(self.data)
        changed["counts"]["empirical_studies_selected"] = 1
        with self.assertRaisesRegex(ValueError, "corpus"):
            inspect_ledger(changed)
        changed = copy.deepcopy(self.data)
        changed["gate_status"]["R006_complete"] = True
        with self.assertRaisesRegex(ValueError, "gate"):
            inspect_ledger(changed)


if __name__ == "__main__":
    unittest.main()
