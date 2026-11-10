"""Negative controls for R005's source-limited Becker → R006 handoff.

The tests validate source/provenance constraints, not the scientific truth of an
article, a screening judgement, a participant count or a source-file SHA-256.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/sources/auditory/r006-primary-support-2026-11-10/BECKER-2025.json"
RELATED = ROOT / "research/sources/related/records/SRC-REL-BECKER-2025.json"
HITS = (
    "HIT-R004-G06-03",
    "HIT-R004-G06-04",
    "HIT-R004-LK3-VOICE-NATURALNESS-TRUST-01",
)
NO_CANONICAL = (
    "new_canonical_search_runs",
    "new_canonical_search_hits",
)


def load():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def by_key(data, key):
    return next(x for x in data["observations"] if x["key"] == key)


def validate(data):
    assert data["schema"] == "mhac-r005-crosslane-primary-access/1"
    assert data["issue"] == 5 and data["downstream_issue"] == 6
    assert data["status"] == "bounded_source_access_handoff_not_canonical_screening"
    assert data["frozen_search_cutoff"] == "2026-10-04"
    assert data["base_main_sha"] == "d3348fba38f01500a134593f9b64b268d62392af"
    assert data["retrieval_date_utc"] == "2026-11-10"
    assert "not a fabricated HTTP" in data["retrieval_timestamp_note"]
    assert data["record_assembled_at_utc"].startswith("2026-11-10T")
    a = data["assistance"]
    assert a["actor_kind"] == "agent" and not a["independent_human_review"]
    s = data["source"]
    assert s["doi"] == "10.1145/3706066"
    assert s["canonical_related_source_ref"] == {"id": "SRC-REL-BECKER-2025", "rev": 1}
    assert s["lawful_public_pdf_url"].endswith("/3706066.pdf")
    assert s["reading_method"] == "tool_mediated_primary_article_pdf_text_plus_selected_page_images"
    assert s["original_pdf_byte_hash_verified"] is False
    assert s["original_pdf_sha256"] is None
    assert s["original_pdf_saved_to_repo"] is False
    assert s["actual_sound_files_heard"] is False
    assert s["raw_http_response_bytes_retained"] is False
    assert "CC BY 4.0" in s["access_proof"]
    renders = {(p["pdf_zero_based_page"], p["result"]) for p in s["page_image_results"]}
    assert {(7, "rendered_inspected"), (8, "rendered_inspected"),
            (23, "rendered_inspected"), (24, "rendered_inspected"),
            (5, "render_attempt_403_no_image_inspected")} <= renders
    r = data["retrieval"]
    assert r["channel"] == "C8_supplementary_source_navigation_not_ACM_database_search"
    assert r["platform"].startswith("web search")
    assert len(r["queries"]) >= 2
    assert all(r[n] == 0 for n in NO_CANONICAL)
    assert r["no_claim_of_ACM_DL_query_or_EG_search_completion"] is True
    assert {x["id"] for x in r["existing_search_hit_refs"]} == set(HITS)
    assert all(x["rev"] == 1 for x in r["existing_search_hit_refs"])
    observations = data["observations"]
    assert len({x["key"] for x in observations}) == len(observations)
    pre = by_key(data, "prestudy_participant_flow")
    main = by_key(data, "main_participant_flow")
    assert (pre["author_reported_completed"], pre["author_reported_excluded"],
            pre["author_reported_analysed"]) == (62, 2, 60)
    assert (main["author_reported_completed"], main["author_reported_excluded"],
            main["author_reported_analysed"]) == (73, 5, 68)
    assert pre["author_reported_completed"] - pre["author_reported_excluded"] == pre["author_reported_analysed"]
    assert main["author_reported_completed"] - main["author_reported_excluded"] == main["author_reported_analysed"]
    overlap = by_key(data, "prestudy_vs_main_nonoverlap")
    assert overlap["author_statement"] == "prestudy_participants_excluded_from_main"
    assert overlap["r006_verification_required"] is True
    pilot = by_key(data, "pilot_group")
    assert pilot["pilot_overlap"] == "unknown"
    assert pilot["author_reported_pilot_participants"] == 8
    assert by_key(data, "operational_message_e2")["unit"] == "main_experiment"
    assert by_key(data, "prestudy_is_voice_ratings")["unit"] == "online_prestudy"
    assert "Appendix E, Table E1" in by_key(data, "voice_content_affect_confounds")["locators"]
    i = data["identity_disposition"]
    assert i["independent_sample_count_admitted"] == 0
    assert i["canonical_screening_records_added"] == 0
    assert i["canonical_study_records_added"] == 0
    assert i["canonical_sample_records_added"] == 0
    assert i["no_full_text_eligibility_decision_by_R005"]
    assert i["R006_maintains_authority_for_E1_E6_and_identity"]
    assert i["Becker_R006_prior_full_text_access_status"] == "awaiting_text"
    assert len(i["experiments_provisionally_distinguished"]) == 3
    assert not any(data["acceptance"].values())


class BeckerSourceHandoffTests(unittest.TestCase):
    def setUp(self):
        self.data = load()

    def reject(self, modify):
        changed = copy.deepcopy(self.data)
        modify(changed)
        with self.assertRaises(AssertionError):
            validate(changed)

    def test_positive_contract(self):
        validate(self.data)

    def test_existing_source_pin(self):
        source = json.loads(RELATED.read_text(encoding="utf-8"))
        assert source["id"] == self.data["source"]["canonical_related_source_ref"]["id"]
        assert source["revisions"][0]["data"]["identifiers"][0]["value"] == "10.1145/3706066"

    def test_real_existing_hit_ids(self):
        for hit in self.data["retrieval"]["existing_search_hit_refs"]:
            h = ROOT / "research/searches/related/records/hits" / (hit["id"] + ".json")
            record = json.loads(h.read_text(encoding="utf-8"))
            assert record["id"] == hit["id"]
            assert record["revisions"][-1]["data"]["source_ref"] == {"id": "SRC-REL-BECKER-2025", "rev": 1}

    def test_reject_doi_drift(self):
        self.reject(lambda d: d["source"].__setitem__("doi", "10.1145/3711938"))

    def test_reject_unreal_hash(self):
        self.reject(lambda d: d["source"].__setitem__("original_pdf_sha256", "0" * 64))

    def test_reject_false_byte_verification(self):
        self.reject(lambda d: d["source"].__setitem__("original_pdf_byte_hash_verified", True))

    def test_reject_human_review_spoof(self):
        self.reject(lambda d: d["assistance"].__setitem__("independent_human_review", True))

    def test_reject_fake_acm_database(self):
        self.reject(lambda d: d["retrieval"].__setitem__("channel", "C3_ACM_DL_database_completed"))

    def test_reject_new_canonical_hit_count(self):
        self.reject(lambda d: d["retrieval"].__setitem__("new_canonical_search_hits", 1))

    def test_reject_changed_cutoff(self):
        self.reject(lambda d: d.__setitem__("frozen_search_cutoff", "2026-11-10"))

    def test_reject_study_sample_promotion(self):
        self.reject(lambda d: d["identity_disposition"].__setitem__("canonical_sample_records_added", 2))

    def test_reject_participant_inflation(self):
        self.reject(lambda d: by_key(d, "main_participant_flow").__setitem__("author_reported_analysed", 73))

    def test_reject_unknown_pilot_overlap_as_independent(self):
        self.reject(lambda d: by_key(d, "pilot_group").__setitem__("pilot_overlap", "independent"))

    def test_reject_missing_author_nonoverlap_qualification(self):
        self.reject(lambda d: by_key(d, "prestudy_vs_main_nonoverlap").__setitem__("r006_verification_required", False))

    def test_reject_misrepresented_failed_screenshot(self):
        self.reject(lambda d: d["source"]["page_image_results"][-1].__setitem__("result", "rendered_inspected"))

    def test_reject_claim_of_selected_corpus(self):
        self.reject(lambda d: d["acceptance"].__setitem__("R006_issue_complete", True))


if __name__ == "__main__":
    unittest.main()
