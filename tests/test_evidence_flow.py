"""Known flow identities, incomplete searches and honest dependence bookkeeping."""
from __future__ import annotations

import copy
import csv
import io
import json
import unittest

from schemas import ValidationError
from tools.build_record_fixtures import ref, snapshots
from tools.evidence_flow import evidence_flow, render_exports
from tools.record_graph import validate_graph


def row(data, rid):
    return next(record for record in data["records"] if record["id"] == rid)


def body(data, rid):
    return row(data, rid)["revisions"][-1]["data"]


def flow(data):
    return evidence_flow(validate_graph(data["records"]))


class EvidenceFlowTests(unittest.TestCase):
    def test_known_occurrences_reports_studies_and_outcomes_are_distinct(self):
        result = flow(snapshots()["valid_all_families"])
        expected = {"search_runs": 1, "search_hits": 3, "publications": 2,
                    "studies": 1, "experiments": 1, "samples": 1, "outcomes": 2,
                    "shared_sample_groups": 1, "included_publications": 1,
                    "included_studies": 1, "included_outcomes": 1}
        for key, value in expected.items():
            with self.subTest(measure=key):
                self.assertEqual(result[key], value)
        self.assertEqual(result["search_details"][0]["duplicate_hits"], 1)
        self.assertEqual(result["screening"]["title_abstract"]["include"], 2)
        self.assertEqual(result["screening"]["full_text"]["uncertain"], 1)

    def test_recorded_retrieval_count_must_match_actual_occurrence_records(self):
        data = snapshots()["valid_all_families"]
        body(data, "SRCH-FIXTURE")["retrieved_count"] = 2
        with self.assertRaisesRegex(ValidationError, "^SEARCH_COUNT:"):
            flow(data)

    def test_reported_count_cannot_be_less_than_retained_hits(self):
        data = snapshots()["valid_all_families"]
        body(data, "SRCH-FIXTURE")["reported_count"] = 2
        with self.assertRaisesRegex(ValidationError, "^SEARCH_COUNT:"):
            flow(data)

    def test_completed_search_cannot_omit_a_reported_occurrence(self):
        data = snapshots()["valid_all_families"]
        body(data, "SRCH-FIXTURE")["reported_count"] = 4
        with self.assertRaisesRegex(ValidationError, "^SEARCH_COMPLETION:"):
            flow(data)

    def test_partial_search_retains_the_reported_unretrieved_remainder(self):
        data = snapshots()["valid_all_families"]
        search = body(data, "SRCH-FIXTURE")
        search.update(status="partial", reported_count=4, failures=["SYNTHETIC final page unavailable"])
        search["pagination"] = {"complete": False, "detail": "Three of four fictional occurrences are retained."}
        result = flow(data)
        self.assertEqual(result["search_details"][0]["status"], "partial")
        self.assertEqual(result["search_details"][0]["reported_count"], 4)
        self.assertEqual(result["search_details"][0]["stored_hits"], 3)

    def test_unresolved_search_identity_does_not_become_a_canonical_publication(self):
        data = snapshots()["valid_all_families"]
        hit = row(data, "HIT-FIXTURE-3")["revisions"][0]
        hit["data"].update(status="unresolved", resolution_reason="Synthetic occurrence awaits an identity decision.")
        del hit["data"]["source_ref"]
        hit["basis"] = [ref("SRCH-FIXTURE")]
        result = flow(data)
        detail = result["search_details"][0]
        self.assertEqual(detail["stored_hits"], 3)
        self.assertEqual(detail["resolved_hits"], 2)
        self.assertEqual(detail["unresolved_hits"], 1)
        self.assertEqual(detail["unique_publications"], 1)
        self.assertTrue(any("Unresolved search-hit" in warning for warning in result["warnings"]))

    def test_publication_alias_preserves_occurrences_without_inflating_publications(self):
        data = snapshots()["valid_all_families"]
        alias = copy.deepcopy(row(data, "SRC-A"))
        alias["id"] = "SRC-ALIAS-A"
        alias["revisions"][0]["data"].update(validity="superseded", alias_of=ref("SRC-A"),
                                                alias_reason="Synthetic duplicate identity; not another publication.")
        data["records"].append(alias)
        duplicate = row(data, "HIT-FIXTURE-2")["revisions"][0]
        duplicate["data"]["source_ref"] = ref("SRC-ALIAS-A")
        duplicate["basis"] = [ref("SRCH-FIXTURE"), ref("SRC-ALIAS-A"), ref("HIT-FIXTURE-1")]
        result = flow(data)
        self.assertEqual(result["source_record_ids"], 3)
        self.assertEqual(result["publications"], 2)
        self.assertEqual(result["search_hits"], 3)
        self.assertEqual(result["search_details"][0]["unique_publications"], 2)

    def test_repeat_extraction_of_one_outcome_does_not_create_an_independent_outcome(self):
        data = snapshots()["valid_all_families"]
        duplicate = copy.deepcopy(row(data, "EX-ACC"))
        duplicate["id"] = "EX-ACC-SECOND-RECORD"
        data["records"].append(duplicate)
        result = flow(data)
        self.assertEqual(result["extraction_records"], 3)
        self.assertEqual(result["outcomes"], 2)
        self.assertEqual(result["current_extracted_outcomes"], 2)
        self.assertEqual(result["studies"], 1)

    def test_unavailable_report_stays_visible_in_flow(self):
        data = snapshots()["valid_all_families"]
        source = copy.deepcopy(row(data, "SRC-A"))
        source["id"] = "SRC-UNAVAILABLE"
        source["revisions"][0]["data"].update(
            title="SYNTHETIC unavailable report; no real source", manifestations=[],
            access_status="unavailable", access_reason="Fictional access limitation for the flow test.")
        data["records"].append(source)
        screening = copy.deepcopy(row(data, "SCR-B-FT"))
        screening["id"] = "SCR-UNAVAILABLE-FT"
        revision = screening["revisions"][0]
        revision["basis"] = [ref("SRC-UNAVAILABLE")]
        revision["data"].update(source_ref=ref("SRC-UNAVAILABLE"), decision="awaiting_text", reading_refs=[],
                                reason="Synthetic full text unavailable.", access_limitation="No text obtained in the fictional scenario.")
        data["records"].append(screening)
        result = flow(data)
        self.assertEqual(result["publications"], 3)
        self.assertEqual(result["unavailable_publications"], 1)
        self.assertEqual(result["screening"]["full_text"]["awaiting_text"], 1)
        self.assertEqual(result["included_publications"], 1)

    def test_conflicting_screening_owners_need_explicit_supersession(self):
        data = snapshots()["valid_all_families"]
        conflicting = copy.deepcopy(row(data, "SCR-A-FT"))
        conflicting["id"] = "SCR-A-OTHER-FT"
        conflicting["revisions"][0]["data"].update(decision="exclude", reason="Synthetic competing decision.")
        data["records"].append(conflicting)
        with self.assertRaisesRegex(ValidationError, "^SCREENING_CONFLICT:"):
            flow(data)

    def test_screening_supersession_chain_is_not_dependent_on_id_sort_order(self):
        data = snapshots()["valid_all_families"]
        original = row(data, "SCR-A-FT")
        for rid, previous, timestamp, decision in (
                ("SCR-Z-FT", "SCR-A-FT", "2000-01-01T00:30:00Z", "exclude"),
                ("SCR-M-FT", "SCR-Z-FT", "2000-01-01T00:31:00Z", "include")):
            replacement = copy.deepcopy(original)
            replacement["id"] = rid
            replacement["revisions"][0]["at"] = timestamp
            replacement["revisions"][0]["data"].update(supersedes_ref=ref(previous), decision=decision,
                                                        reason="Synthetic sequential adjudication supersedes its immediate predecessor.")
            data["records"].append(replacement)
        result = flow(data)
        self.assertEqual(result["screening"]["full_text"]["include"], 1)
        self.assertEqual(result["screening"]["full_text"]["exclude"], 0)
        self.assertEqual(result["screening"]["full_text"]["uncertain"], 1)

    def test_known_shared_samples_form_one_dependence_group(self):
        data = snapshots()["valid_all_families"]
        extra = copy.deepcopy(row(data, "SAMPLE-ONE"))
        extra["id"] = "SAMPLE-TWO"
        extra["revisions"][0]["data"]["overlap"] = [
            {"sample_ref": ref("SAMPLE-ONE"), "relation": "known_shared", "reason": "Synthetic shared sample labels."}]
        body(data, "SAMPLE-ONE")["overlap"] = [
            {"sample_ref": ref("SAMPLE-TWO"), "relation": "known_shared", "reason": "Synthetic shared sample labels."}]
        data["records"].append(extra)
        result = flow(data)
        self.assertEqual(result["samples"], 2)
        self.assertEqual(result["known_dependence_groups"], [["SAMPLE-ONE", "SAMPLE-TWO"]])
        self.assertEqual(result["outcomes"], 2)
        self.assertNotIn("independent_studies", result)

    def test_unknown_sample_overlap_and_covariance_remain_explicit(self):
        data = snapshots()["valid_all_families"]
        extra = copy.deepcopy(row(data, "SAMPLE-ONE"))
        extra["id"] = "SAMPLE-TWO"
        extra["revisions"][0]["data"]["overlap"] = [
            {"sample_ref": ref("SAMPLE-ONE"), "relation": "unknown", "reason": "The fictional text does not resolve overlap."}]
        data["records"].append(extra)
        result = flow(data)
        self.assertEqual(result["unknown_overlap_pairs"], [["SAMPLE-ONE", "SAMPLE-TWO"]])
        self.assertTrue(any("independence" in warning for warning in result["warnings"]))
        self.assertTrue(any("covariance" in warning for warning in result["warnings"]))
        self.assertNotIn("independent_sample_count", result)

    def test_deterministic_exports_preserve_numeric_identity_and_currency(self):
        data = snapshots()["valid_correction_pending"]
        graph = validate_graph(data["records"])
        counts = evidence_flow(graph)
        report = {"counts": counts, "currency": {
            "latest_stale_ids": sorted(rid for rid in graph.records if graph.latest_pin(rid) in graph.stale)}}
        first = render_exports(data, report)
        reordered = copy.deepcopy(data)
        reordered["records"].reverse()
        second = render_exports(reordered, report)
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first["evidence-flow.json"]), counts)
        csv_counts = {entry["measure"]: int(entry["count"]) for entry in csv.DictReader(io.StringIO(first["evidence-flow.csv"]))}
        self.assertEqual(csv_counts["publications"], 2)
        self.assertEqual(csv_counts["studies"], 1)
        index = {entry["id"]: entry for entry in json.loads(first["records-index.json"])["records"]}
        self.assertEqual(index["CLM-LAT"]["currency"], "stale")
        self.assertEqual(index["CLM-ACC"]["currency"], "current")


if __name__ == "__main__":
    unittest.main()
