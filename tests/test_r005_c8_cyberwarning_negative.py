"""R005 C8 provenance-only cyberwarning case; synthetic negative mutations.

These tests verify *record integrity*, not primary-source scientific truth.
"""
from __future__ import annotations

import copy
import json
import pathlib
import unittest
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parents[1]
OBS = ROOT / "research/searches/auditory/c8-cyberwarning-negative-2026-11-10/OBSERVATIONS.json"
EXPECTED_DOIS = {
    "10.1177/10711813241275518",
    "10.1007/s42452-021-04703-4",
    "10.36965/OJAKM.2020.8(2)107-121",
}


def audit(record: dict) -> list[str]:
    """Refuse science- or search-state promotions unsupported by the C8 evidence."""
    faults: list[str] = []
    if record.get("schema") != "mhac-r005-c8-primary-comparator-navigation/1":
        faults.append("schema")
    if record.get("issue") != 5 or record.get("protocol") != "PROTOCOL-v1":
        faults.append("authority")
    if record.get("cutoff") != "2026-10-04" or record.get("protocol_controls", {}).get("frozen_corpus_cutoff") != "2026-10-04":
        faults.append("cutoff")
    exp = record.get("export_scope", {})
    for key in ("canonical_search_hits_added", "canonical_screening_records_added",
                "independent_studies_admitted", "independent_samples_admitted"):
        if exp.get(key) != 0:
            faults.append(key)
    for key in ("ordered_search_results_retained", "raw_http_bytes_retained", "baseline_counts_recomputed"):
        if exp.get(key) is not False:
            faults.append(key)
    for key in ("raw_response_sha256", "source_file_sha256", "verified_http_status", "provider_result_total"):
        if exp.get(key) is not None:
            faults.append(key)
    actor = record.get("actor", {})
    if actor.get("human_verification") is not False or actor.get("independent_review") is not False:
        faults.append("human_review")
    ctrl = record.get("protocol_controls", {})
    if ctrl.get("completed_protocol_c9") is not False:
        faults.append("c9_promotion")
    if ctrl.get("baseline_c1_eq1") != "as of 2026-11-03 sorted prefix 4,200/9,368; not remeasured":
        faults.append("eq1_checkpoint")
    probe = record.get("c1_access_probe", {})
    if (probe.get("eq1_executed") is not False or probe.get("production_query") is not False
            or probe.get("server_http_status") is not None or probe.get("quota_remaining") is not None
            or probe.get("response_sha256") is not None):
        faults.append("api_truth")
    sources = record.get("source_routes", [])
    dois = [source.get("doi") for source in sources]
    if len(sources) != 3 or set(dois) != EXPECTED_DOIS or len(dois) != len(set(dois)):
        faults.append("source_identity")
    for source in sources:
        if source.get("year", 9999) > 2026 or not source.get("locators"):
            faults.append("source_locator_or_date")
        if not source.get("publisher_url", "").startswith("https://"):
            faults.append("publisher_url")
        if "not" not in source.get("access_extent", "").lower():
            faults.append("reading_extent")
        if not source.get("cautions"):
            faults.append("counterposition")
    z = next((s for s in sources if s.get("doi") == "10.1177/10711813241275518"), {})
    if z.get("prior_retained_path") != "research/searches/auditory/records/hits/HIT-R005R-C1RECOVERY-EQ1-00611.json":
        faults.append("duplicate_hit_pin")
    stats = z.get("author_reported", {})
    if stats.get("participants_recruited") != 142 or stats.get("participants_analyzed") != 113 or stats.get("attention_excluded") != 29:
        faults.append("participant_denominator")
    if stats.get("participants_recruited", 0) != stats.get("participants_analyzed", 0) + stats.get("attention_excluded", 0):
        faults.append("attrition")
    if any(r.get("evidence_class") != "author_reported_not_independently_extracted" for r in stats.get("findings", [])):
        faults.append("unearned_extraction")
    if not record.get("negative_interpretations") or not record.get("handoffs"):
        faults.append("critical_handoff")
    return faults


class R005C8CyberwarningNegative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(OBS.read_text(encoding="utf-8"))

    def test_current_record_audits(self):
        self.assertEqual(audit(self.record), [])

    def test_duplicate_existing_eq1_hit_pinned(self):
        self.assertIn("HIT-R005R-C1RECOVERY-EQ1-00611.json",
                      self.record["source_routes"][0]["prior_retained_path"])

    def test_prohibits_corpus_admission(self):
        for key in ("canonical_search_hits_added", "canonical_screening_records_added",
                    "independent_studies_admitted", "independent_samples_admitted"):
            with self.subTest(key=key):
                bad = copy.deepcopy(self.record)
                bad["export_scope"][key] = 1
                self.assertIn(key, audit(bad))

    def test_prohibits_claimed_unrecorded_response_hash(self):
        bad = copy.deepcopy(self.record)
        bad["export_scope"]["raw_response_sha256"] = "0" * 64
        self.assertIn("raw_response_sha256", audit(bad))

    def test_prohibits_claimed_approval(self):
        bad = copy.deepcopy(self.record)
        bad["actor"]["human_verification"] = True
        self.assertIn("human_review", audit(bad))

    def test_prohibits_mislabelled_c9_chain(self):
        bad = copy.deepcopy(self.record)
        bad["protocol_controls"]["completed_protocol_c9"] = True
        self.assertIn("c9_promotion", audit(bad))

    def test_prohibits_api_success_claim(self):
        bad = copy.deepcopy(self.record)
        bad["c1_access_probe"]["quota_remaining"] = 700
        self.assertIn("api_truth", audit(bad))

    def test_prohibits_frozen_cutoff_shift(self):
        bad = copy.deepcopy(self.record)
        bad["cutoff"] = "2026-11-10"
        self.assertIn("cutoff", audit(bad))

    def test_prohibits_duplicate_publication_count(self):
        bad = copy.deepcopy(self.record)
        bad["source_routes"][1]["doi"] = bad["source_routes"][0]["doi"]
        self.assertIn("source_identity", audit(bad))

    def test_prohibits_lost_existing_hit_pin(self):
        bad = copy.deepcopy(self.record)
        bad["source_routes"][0]["prior_retained_path"] = None
        self.assertIn("duplicate_hit_pin", audit(bad))

    def test_prohibits_false_participant_denominator(self):
        bad = copy.deepcopy(self.record)
        bad["source_routes"][0]["author_reported"]["attention_excluded"] = 28
        self.assertIn("participant_denominator", audit(bad))

    def test_prohibits_independently_verified_effect_promotion(self):
        bad = copy.deepcopy(self.record)
        bad["source_routes"][0]["author_reported"]["findings"][0]["evidence_class"] = "verified_effect"
        self.assertIn("unearned_extraction", audit(bad))


if __name__ == "__main__":
    unittest.main()
