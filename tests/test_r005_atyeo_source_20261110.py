"""R005 Atyeo primary publisher HTML provenance — fail-closed integrity checks."""
import copy
import json
import unittest
from pathlib import Path
PATH=Path(__file__).resolve().parents[1]/"research/sources/auditory/r006-original-access-boundary-2026-11-10/ATYEO-2015.json"
def check(d):
    assert d["issue"]==5 and d["downstream_issue"]==6
    assert d["publication"]["doi"]=="10.1111/anae.13020"
    assert d["publication"]["online_publication_date"]=="2015-03-04"
    assert d["reading_method"]=="tool_mediated_original_publisher_html"
    assert d["original_http_acquisition_timestamp"] is None
    assert d["accessed_text"]["authoritative_hashed_source_instance"] is False
    assert d["accessed_text"]["original_html_sha256"] is None
    assert d["accessed_text"]["original_pdf_sha256"] is None
    assert d["accessed_text"]["redistribution_permission_positively_established"] is False
    assert d["auditory_stimuli"]["audio_downloaded"] is False
    assert d["auditory_stimuli"]["audio_heard"] is False
    assert d["auditory_stimuli"]["audio_sha256"] is None
    assert d["route_to_discovery"]["historical_or_new_canonical_hit_id"] is None
    assert d["actual_human_second_reviewer"] is False
    assert all(d[x]==0 for x in ("canonical_new_search_runs","canonical_new_hits","canonical_new_screenings",
    "canonical_admitted_publications","canonical_new_studies","canonical_new_experiments",
    "canonical_new_samples","selected_track_e","selected_track_g"))
    assert d["reported_study_identity"]["publication_count"]==1
    assert "not used in main" in d["reported_study_identity"]["pilot_role"]
class TestAtyeoBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(PATH.read_text(encoding="utf-8"))
    def test_valid(self): check(self.data)
    def test_wrong_publication_identity(self):
        d=copy.deepcopy(self.data);d["publication"]["doi"]="10.1111/anae.13205"
        with self.assertRaises(AssertionError):check(d)
    def test_unverified_original_hash(self):
        d=copy.deepcopy(self.data);d["accessed_text"]["original_html_sha256"]="f"*64
        with self.assertRaises(AssertionError):check(d)
    def test_fabricated_http_time(self):
        d=copy.deepcopy(self.data);d["original_http_acquisition_timestamp"]="2026-11-10T19:20:00Z"
        with self.assertRaises(AssertionError):check(d)
    def test_audio_not_assumed_downloaded(self):
        d=copy.deepcopy(self.data);d["auditory_stimuli"]["audio_downloaded"]=True
        with self.assertRaises(AssertionError):check(d)
    def test_no_human_second_screener(self):
        d=copy.deepcopy(self.data);d["actual_human_second_reviewer"]=True
        with self.assertRaises(AssertionError):check(d)
    def test_no_new_canonical_hit(self):
        d=copy.deepcopy(self.data);d["canonical_new_hits"]=1
        with self.assertRaises(AssertionError):check(d)
    def test_no_sample_inflation(self):
        d=copy.deepcopy(self.data);d["canonical_new_samples"]=12
        with self.assertRaises(AssertionError):check(d)
if __name__=="__main__":unittest.main()
