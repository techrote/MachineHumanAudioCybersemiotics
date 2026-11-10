"""Adversarial checks for the provisional R004-to-R006 abstract screening handoff.

These tests do not turn the four proposed decisions into canonical SCR records,
reconstruct independent participant samples, or verify source scientific claims.
"""
from __future__ import annotations

import copy
from collections import Counter
import json
from pathlib import Path
from urllib.parse import urlsplit
import unittest

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "research/screening/r006_r004_crosslane_20261110/DECISIONS.json"
RULES = {f"E{i}" for i in range(1, 7)}
IDS = {
    "SRC-REL-BECKER-2025": "10.1145/3706066",
    "SRC-REL-ROMEO-2025": "10.1145/3711938",
    "SRC-REL-KUHNE-2020": "10.3389/fnbot.2020.593732",
    "SRC-REL-ROMEO-2023": "10.1109/ro-man57019.2023.10309631",
}
DECISIONS = {"include", "exclude", "uncertain"}
RULE_VALUES = {"yes", "no", "uncertain"}


def evaluate(data: dict) -> dict:
    """Fail closed for this exact evidence-limited and not-yet-registered tranche."""
    if (data["kind"]
            != "provisional_first_pass_screening_handoff_not_registered_mhac_records_v1"):
        raise ValueError("Attempted canonicalisation without registry integration")
    if data["evidence_cutoff"] != "2026-10-04":
        raise ValueError("Frozen search cutoff altered")
    if data["actor"]["kind"] != "agent" or "human" in data["actor"]["id"].lower():
        raise ValueError("Cannot imply human screening")
    rows = data["decisions"]
    if len(rows) != len(IDS):
        raise ValueError("Tranche membership drift")
    seen = set()
    totals = Counter()
    for row in rows:
        ref = row["source_ref"]
        source_id = ref["id"]
        if source_id not in IDS or source_id in seen or ref["rev"] != 1:
            raise ValueError("Duplicate, unknown, or repinned publication")
        seen.add(source_id)
        source_file = ROOT / "research/sources/related/records" / (source_id + ".json")
        record = json.loads(source_file.read_text(encoding="utf-8"))
        if record["id"] != source_id or record["kind"] != "source":
            raise ValueError("Source record disagreement")
        rev = next((rev for rev in record["revisions"]
                    if rev["rev"] == ref["rev"]), None)
        if rev is None or rev["data"]["validity"] != "active":
            raise ValueError("Source pin not active")
        verified_dois = {item["value"].lower() for item in rev["data"]["identifiers"]
                         if item["scheme"] == "doi" and item["status"] == "verified"}
        if row["doi"] != IDS[source_id] or row["doi"] not in verified_dois:
            raise ValueError("Source DOI disagreement")
        if row["track"] != "empirical" or row["stage"] != "title_abstract":
            raise ValueError("Screening track/stage drift")
        assessment = row["rule_assessment"]
        if set(assessment) != RULES or any(v not in RULE_VALUES
                                            for v in assessment.values()):
            raise ValueError("Incomplete E1–E6 assessment")
        if row["decision"] not in DECISIONS:
            raise ValueError("Unsupported decision")
        if row["decision"] == "include" and set(assessment.values()) != {"yes"}:
            raise ValueError("Uncertain rule cannot be silently included")
        if row["decision"] == "uncertain" and (
                "uncertain" not in assessment.values() or "no" in assessment.values()):
            raise ValueError("Uncertain decision must preserve actual rule uncertainty")
        if row["decision"] == "exclude" and "no" not in assessment.values():
            raise ValueError("Exclusion requires evidence of a failed rule")
        if (row["reading_scope"] != "abstract_only_for_this_screening_pass"
                or row["review_status"] != "single_agent_first_pass_unverified"
                or row["independent_study_count"] != "not_established"
                or row["sample_overlap"] != "not_established"):
            raise ValueError("Invented reading, verification or independent-sample status")
        if not row["reason"].strip() or not row["next_action"].strip():
            raise ValueError("Missing decision provenance/next step")
        if len(row["evidence"]) != 1:
            raise ValueError("First-pass abstract witness count drift")
        ev = row["evidence"][0]
        parsed = urlsplit(ev["url"])
        if (parsed.scheme != "https" or not parsed.hostname
                or ev["locator"] != "Abstract"
                or ev["access_method"] != "web_publisher_or_institutional_abstract"
                or ev["access_date"] != "2026-11-10"
                or ev["local_bytes_verified"] is not False):
            raise ValueError("Invalid abstract evidence or fabricated file verification")
        totals[row["decision"]] += 1

    relation = data["publication_identity_review"]
    if (set(relation["pair"])
            != {"SRC-REL-ROMEO-2023", "SRC-REL-ROMEO-2025"}
            or relation["publication_identity"] != "distinct_publications_by_verified_doi"
            or relation["shared_study_or_sample"] != "unknown_pending_full_report_comparison"
            or set(relation["verified_distinct_dois"])
            != {IDS["SRC-REL-ROMEO-2023"], IDS["SRC-REL-ROMEO-2025"]}):
        raise ValueError("DOI identity cannot determine study/sample independence")

    acceptance = data["acceptance"]
    expected = acceptance["decisions_by_stage"]["title_abstract"]
    if (expected != {key: totals[key] for key in ("include", "uncertain", "exclude")}
            or acceptance["decisions_by_stage"]["full_text"] != {"recorded": 0}):
        raise ValueError("Misstated screening counts")
    for key in ("source_records_created", "canonical_screening_records_created",
                "study_records_created", "sample_records_created",
                "included_studies", "independent_samples"):
        if acceptance[key] != 0:
            raise ValueError("Unwarranted record or participant count: " + key)
    if acceptance["corpus_snapshot_created"] or acceptance["track_e_gate_satisfied"]:
        raise ValueError("Corpus or Track E gate cannot be claimed complete")
    return dict(totals)


class CrosslaneFirstPassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(HANDOFF.read_text(encoding="utf-8"))

    def test_current_provisional_handoff_and_source_pins(self):
        self.assertEqual(evaluate(self.data),
                         {"include": 2, "uncertain": 2})

    def test_no_registry_manifest_or_generated_views_modified_by_handoff(self):
        manifest = json.loads((ROOT / "research/registry/state.json")
                              .read_text(encoding="utf-8"))
        self.assertNotIn("research/screening", manifest["record_roots"])
        self.assertEqual(manifest["research_state"], "in_progress")

    def test_duplicate_source_fails(self):
        edited = copy.deepcopy(self.data)
        edited["decisions"][1]["source_ref"] = edited["decisions"][0]["source_ref"]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            evaluate(edited)

    def test_doi_reassignment_or_pseudo_publication_merge_fails(self):
        edited = copy.deepcopy(self.data)
        edited["decisions"][0]["doi"] = IDS["SRC-REL-ROMEO-2025"]
        with self.assertRaisesRegex(ValueError, "DOI"):
            evaluate(edited)
        edited = copy.deepcopy(self.data)
        edited["publication_identity_review"]["shared_study_or_sample"] = "independent"
        with self.assertRaisesRegex(ValueError, "study/sample"):
            evaluate(edited)

    def test_uncertainty_cannot_be_silently_excluded_or_included(self):
        for new_decision in ("include", "exclude"):
            edited = copy.deepcopy(self.data)
            row = next(r for r in edited["decisions"]
                       if r["source_ref"]["id"] == "SRC-REL-KUHNE-2020")
            row["decision"] = new_decision
            with self.subTest(decision=new_decision), self.assertRaises(ValueError):
                evaluate(edited)

    def test_abstract_cannot_become_full_text(self):
        edited = copy.deepcopy(self.data)
        edited["decisions"][0]["stage"] = "full_text"
        with self.assertRaisesRegex(ValueError, "stage"):
            evaluate(edited)
        edited = copy.deepcopy(self.data)
        edited["decisions"][0]["evidence"][0]["local_bytes_verified"] = True
        with self.assertRaisesRegex(ValueError, "file verification"):
            evaluate(edited)

    def test_independent_samples_cannot_be_fabricated(self):
        edited = copy.deepcopy(self.data)
        edited["acceptance"]["independent_samples"] = 4
        with self.assertRaisesRegex(ValueError, "participant count"):
            evaluate(edited)
        edited = copy.deepcopy(self.data)
        edited["decisions"][0]["independent_study_count"] = 2
        with self.assertRaisesRegex(ValueError, "independent-sample"):
            evaluate(edited)

    def test_count_drift_fails(self):
        edited = copy.deepcopy(self.data)
        edited["acceptance"]["decisions_by_stage"]["title_abstract"]["include"] = 3
        with self.assertRaisesRegex(ValueError, "counts"):
            evaluate(edited)

    def test_no_claim_of_corpus_acceptance(self):
        edited = copy.deepcopy(self.data)
        edited["acceptance"]["corpus_snapshot_created"] = True
        with self.assertRaisesRegex(ValueError, "gate"):
            evaluate(edited)


if __name__ == "__main__":
    unittest.main()
