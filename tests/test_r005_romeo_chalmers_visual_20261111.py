"""R005 source-boundary guards for the Chalmers Romeo 2025 visual reading.

Offline contract tests: no network request, no inference of scientific validity.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "research/sources/auditory/romeo2025-chalmers-visual-20261111/OBSERVATIONS.json"
DOI = "10.1145/3711938"
URL = "https://research.chalmers.se/publication/546010/file/546010_Fulltext.pdf"

def validate(r):
    assert r["schema"] == "mhac-r005-romeo2025-institutional-visual/1"
    assert (r["issue"], r["downstream_issue"], r["frozen_publication_cutoff"]) == (5, 6, "2026-10-04")
    assert r["source"]["doi"] == DOI and r["source"]["url"] == URL
    assert r["source"]["publication_id"] == "SRC-REL-ROMEO-2025"
    assert r["source"]["publication_revision"] == 1
    assert "CC BY-NC-SA 4.0" in r["source"]["license_statement"]
    a = r["access"]
    assert a["mode"].startswith("public institution-hosted PDF")
    for field in ("request_timestamp_utc", "response_http_date", "original_http_status",
                  "original_response_sha256", "original_response_bytes"):
        assert a[field] is None, field
    for field in ("original_file_retained", "retention_rights_approved",
                  "downloaded_original_bytes", "pdf_audio_listened", "whole_paper_read"):
        assert a[field] is False, field
    assert a["visually_inspected_pdf_page_indices"] == [0, 1, 5, 6, 7, 8, 9]
    w = a["wrapper_provenance"]
    assert w["text_extracted_wrapper_download_label"] == "2026-05-18 07:06 UTC"
    assert w["page_image_wrapper_download_label"] == "2026-11-10 10:58 UTC"
    assert w["text_extracted_wrapper_download_label"] != w["page_image_wrapper_download_label"]
    assert set(x["key"] for x in r["observations"]) == {
        "edition_and_rights", "pilot_procedure", "maze_procedure",
        "voice_manipulation", "wizard_and_listening"}
    assert r["compared_publication"]["doi"] == "10.1109/RO-MAN57019.2023.10309631"
    assert r["compared_publication"]["status"] == "original_six_page_ieee_full_text_unavailable_to_this_run"
    assert r["compared_publication"]["stimulus_overlap"] == "unverified"
    assert r["compared_publication"]["participant_overlap"] == "unverified"
    assert r["actor"]["kind"] == "agent" and r["actor"]["human_reviewer"] is False
    assert r["new_database_query"] is False and r["new_database_export"] is False
    assert (r["new_canonical_searches"], r["new_canonical_hits"]) == (0, 0)
    g = r["scientific_gate"]
    assert g["screening_authority"] == "R006 exclusively"
    assert g["source_custody_complete"] is False
    for k, v in g.items():
        if k.startswith("new_") or k.startswith("selected_"):
            assert v == 0, (k, v)
    return True

class RomeoChalmersVisualBoundary(unittest.TestCase):
    def setUp(self):
        self.r = json.loads(P.read_text(encoding="utf-8"))

    def test_source_exact_positive(self):
        self.assertTrue(validate(self.r))

    def test_doi_and_cutoff_collision_rejected(self):
        for key, value in (("doi", "10.1109/RO-MAN57019.2023.10309631"),):
            bad = deepcopy(self.r)
            bad["source"][key] = value
            with self.subTest(key=key), self.assertRaises(AssertionError):
                validate(bad)
        bad = deepcopy(self.r)
        bad["frozen_publication_cutoff"] = "2026-11-11"
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_no_hash_or_http_timestamp_from_web_renderer(self):
        for field, value in (("original_response_sha256", "0"*64),
                             ("original_http_status", 200),
                             ("request_timestamp_utc", "2026-11-11T03:00:00Z")):
            bad = deepcopy(self.r)
            bad["access"][field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                validate(bad)

    def test_no_fake_retention_human_audio_or_complete_reading(self):
        for field in ("original_file_retained", "retention_rights_approved",
                      "downloaded_original_bytes", "pdf_audio_listened", "whole_paper_read"):
            bad = deepcopy(self.r)
            bad["access"][field] = True
            with self.subTest(field=field), self.assertRaises(AssertionError):
                validate(bad)
        bad = deepcopy(self.r)
        bad["actor"]["human_reviewer"] = True
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_cached_wrapper_not_conflated_with_http_acquisition(self):
        bad = deepcopy(self.r)
        bad["access"]["wrapper_provenance"]["page_image_wrapper_download_label"] = "2026-05-18 07:06 UTC"
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_unverified_2023_identity_never_promoted(self):
        for field in ("stimulus_overlap", "participant_overlap"):
            bad = deepcopy(self.r)
            bad["compared_publication"][field] = "confirmed_identical"
            with self.subTest(field=field), self.assertRaises(AssertionError):
                validate(bad)

    def test_no_canonical_screen_or_sample_from_author_numbers(self):
        for field in ("new_fulltext_decisions", "new_eligible_publications",
                      "new_admitted_studies", "new_admitted_experiments",
                      "new_independent_samples", "new_source_manifestations"):
            bad = deepcopy(self.r)
            bad["scientific_gate"][field] = 1
            with self.subTest(field=field), self.assertRaises(AssertionError):
                validate(bad)
        bad = deepcopy(self.r)
        bad["new_canonical_hits"] = 1
        with self.assertRaises(AssertionError):
            validate(bad)
