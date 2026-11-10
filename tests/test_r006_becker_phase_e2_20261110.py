"""Fail-closed checks for a source-limited R006 Becker phase recheck.

This JSON is NOT a canonical screening record and tests do not perform scientific
review. The source blob pin deliberately invalidates the recheck after edits.
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research/screening/r006_becker_phase_e2_20261110/RECHECK.json"
SOURCE = ROOT / "research/sources/related/records/SRC-REL-BECKER-2025.json"


def check(data, source_bytes):
    assert data["issue"] == 6
    assert data["artifact_kind"] == "noncanonical_primary_source_phase_eligibility_audit"
    assert data["source_ref"] == {"id": "SRC-REL-BECKER-2025", "rev": 1}
    git_blob = b"blob " + str(len(source_bytes)).encode() + b"\\0" + source_bytes
    assert hashlib.sha1(git_blob).hexdigest() == data["source_record_git_blob_sha"]
    source = json.loads(source_bytes)
    assert source["id"] == data["source_ref"]["id"]
    assert source["kind"] == "source" and source["synthetic"] is False
    rev = next(x for x in source["revisions"] if x["rev"] == 1)
    assert rev["data"]["validity"] == "active"
    assert any(
        i["scheme"] == "doi" and i["status"] == "verified" and
        i["value"].lower() == data["doi"]
        for i in rev["data"]["identifiers"]
    )
    assert data["doi"] == "10.1145/3706066"
    assert data["frozen_cutoff"] == "2026-10-04"
    assert data["actor"]["kind"] == "agent"
    assert data["actor"]["independence"].find("NOT independent human") >= 0
    access = data["source_access"]
    assert access["url"].startswith("https://www2.informatik.uni-hamburg.de/")
    assert access["locally_downloaded_original_pdf"] is False
    assert access["original_pdf_sha256_verified"] is False
    assert access["audio_stimuli_checked"] is False
    assert access["reviewer_human"] is False
    assert access["visually_checked_printed_pages"] == ["29:8", "29:24"]
    assert data["first_stage"]["proposed_publication_decision"] == "include_for_full_text_only"
    assert data["first_stage"]["canonical_scr_registered_by_this_artifact"] is False
    phases = {x["id"]: x for x in data["phases"]}
    assert len(phases) == 3
    assert phases["online_voice_selection_prestudy"]["reported_analyzed_n"] == 60
    assert phases["online_voice_selection_prestudy"]["rule_assessment"]["E2"] == "no_provisional"
    assert phases["online_voice_selection_prestudy"]["proposed_track_e_phase_status"].startswith("not_eligible")
    assert phases["eight_person_setup_pilot"]["reported_n"] == 8
    assert phases["eight_person_setup_pilot"]["rule_assessment"]["E3"] == "unknown"
    assert phases["eight_person_setup_pilot"]["proposed_track_e_phase_status"].startswith("uncertain")
    main = phases["in_person_battleship_main"]
    assert main["reported_analyzed_n"] == 68
    assert main["reported_completed_n"] == 73
    assert main["rule_assessment"] == {f"E{i}": "yes" for i in range(1, 7)}
    assert main["proposed_track_e_phase_status"].startswith("provisional_full_text")
    identity = data["participant_identity"]
    assert identity["pre_study_to_main"] == "author_explicitly_excludes_prestudy_participants_from_main"
    assert identity["setup_pilot_overlap_with_main"] == "unknown"
    assert identity["setup_pilot_overlap_with_prestudy"] == "unknown"
    assert identity["distinct_humans_independently_verified"] is False
    for field in ("independent_sample_records_admitted", "canonical_study_records_admitted",
                  "canonical_experiment_records_admitted"):
        assert identity[field] == 0
    gate = data["governance"]
    for field in ("claims_empirical_extraction", "selected_corpus_ready",
                  "human_second_assessor", "source_material_bytes_verified"):
        assert gate[field] is False
    for field in ("canonical_SCR_added", "included_studies_added"):
        assert gate[field] == 0
    assert gate["issue_status_required"] == "open"


class TestBeckerPhaseRecheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.source_bytes = SOURCE.read_bytes()

    def test_live_source_pinned(self):
        check(self.evidence, self.source_bytes)

    def rejected(self, fn):
        value = copy.deepcopy(self.evidence)
        fn(value)
        with self.assertRaises((AssertionError, KeyError, StopIteration)):
            check(value, self.source_bytes)

    def test_rejects_human_review_promotion(self):
        self.rejected(lambda x: x["source_access"].update(reviewer_human=True))

    def test_rejects_original_pdf_hash_promotion(self):
        self.rejected(lambda x: x["source_access"].update(original_pdf_sha256_verified=True))

    def test_rejects_fake_audio_check(self):
        self.rejected(lambda x: x["source_access"].update(audio_stimuli_checked=True))

    def test_rejects_ta_to_canonical_promotion(self):
        self.rejected(lambda x: x["first_stage"].update(canonical_scr_registered_by_this_artifact=True))

    def test_rejects_source_doi_drift(self):
        self.rejected(lambda x: x.update(doi="10.1145/3711938"))

    def test_rejects_forced_prestudy_e2(self):
        self.rejected(lambda x: x["phases"][0]["rule_assessment"].update(E2="yes"))

    def test_rejects_pilot_overlap_invention(self):
        self.rejected(lambda x: x["participant_identity"].update(setup_pilot_overlap_with_main="independent"))

    def test_rejects_independent_sample_inflation(self):
        self.rejected(lambda x: x["participant_identity"].update(independent_sample_records_admitted=2))

    def test_rejects_study_inflation(self):
        self.rejected(lambda x: x["governance"].update(included_studies_added=1))

    def test_rejects_full_text_acceptance_promotion(self):
        self.rejected(lambda x: x["governance"].update(selected_corpus_ready=True))

    def test_rejects_wrong_source_revision(self):
        self.rejected(lambda x: x["source_ref"].update(rev=2))


if __name__ == "__main__":
    unittest.main()
