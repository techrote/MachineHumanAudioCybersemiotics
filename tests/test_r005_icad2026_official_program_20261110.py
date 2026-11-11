"""Fail-closed C5 programme-navigation boundary; not a scientific screening oracle."""

import copy
import json
import pathlib
import unittest

PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "research/searches/auditory/icad2026-official-program-2026-11-10/OBSERVATIONS.json"
)


def guard(d):
    assert d["schema"] == "mhac-r005-c5-program-navigation/1"
    assert d["issue"] == 5 and d["downstream_issue"] == 6
    assert d["frozen_publication_cutoff"] == "2026-10-04"
    assert d["provider"]["source_url"] == "https://interactive-sonification.org/icad2026/program/"
    assert d["provider"]["source_format"] == "public_html_rendered_by_web_reader"
    assert "preliminary" in d["provider"]["source_boundary"].lower()
    assert d["provider"]["immutable_raw_capture"] is False
    assert d["exact_http_response_time_utc"] is None
    assert d["raw_http_status"] is None
    assert d["raw_response_bytes_retained"] is False
    assert d["raw_response_sha256"] is None
    assert d["observer"]["human_assessor"] is False
    assert d["observer"]["independent_human_review"] is False
    sessions = d["observed_paper_sessions"]
    assert len(sessions) == 5
    assert [s["presentations_listed"] for s in sessions] == [6, 6, 6, 6, 5]
    assert d["derived_programme_paper_talk_slots"] == sum(
        s["presentations_listed"] for s in sessions
    )
    assert "NOT 29 published reports" in d["count_unit"]
    assert d["poster_demo_lightning_other_entries_counted"] is False
    routes = d["bounded_navigation_routes"]
    assert len(routes) == 2
    assert {r["id"] for r in routes} == {
        "R005-C5-ICAD26-REVIEW-NEES-SMITH",
        "R005-C5-ICAD26-REVIEW-BOEHRINGER",
    }
    for r in routes:
        assert r["status"] == "title_present_on_programme_only"
        assert r["full_review_text_read"] is False
        assert r["bibliography_chained"] is False
        assert r["track_e_included"] is False
    assert len(d["exact_web_search_queries_executed"]) >= 1
    assert d["negative_claims"] and not any(d["negative_claims"].values())
    canonical = d["r006_four_candidate_gate"]
    assert canonical["accepted_title_abstract_decisions"] == 4
    assert canonical["scope"].startswith("historical four-candidate")
    current = d["accepted_main_nine_publication_gate_as_of_20261111"]
    assert current["ta_total"] == 9
    assert current["ft_pending"] == 5 and current["ft_awaiting_text"] == 3
    assert current["ft_exclude"] == 1 and current["ft_include"] == 0
    assert current["ft_missing_status"] == 0
    assert all(current[k] == 0 for k in ("admitted_publications", "admitted_studies", "admitted_experiments", "admitted_independent_samples", "selected_track_e", "selected_track_g"))
    assert all("Zenodo" not in s or "NOT equivalent" in s for s in canonical["source_gates"])
    assert d["integration_review_20261111"]["session_counts_reconfirmed"] == [6, 6, 6, 6, 5]
    assert d["integration_review_20261111"]["independent_human_assessor"] is False
    assert canonical["full_text_included"] == 0
    assert canonical["original_romeo_2023_access_changed"] is False
    assert "R006" in d["handoff"] and "Integration" in d["handoff"]
    return True


class TestICAD2026OfficialProgramNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PATH.read_text(encoding="utf-8"))

    def test_observed_boundary(self):
        self.assertTrue(guard(self.data))

    def test_reject_stale_global_nine_screen_claim(self):
        x = copy.deepcopy(self.data)
        x["accepted_main_nine_publication_gate_as_of_20261111"]["ta_total"] = 4
        with self.assertRaises(AssertionError):
            guard(x)

    def test_reject_supplement_equivalence_to_original_ieee_paper(self):
        x = copy.deepcopy(self.data)
        x["r006_four_candidate_gate"]["source_gates"][0] = "Zenodo source substitutes for the unavailable IEEE original"
        with self.assertRaises(AssertionError):
            guard(x)

    def test_reject_false_integration_human_assessor(self):
        x = copy.deepcopy(self.data)
        x["integration_review_20261111"]["independent_human_assessor"] = True
        with self.assertRaises(AssertionError):
            guard(x)

    def test_reject_claimed_original_response(self):
        x = copy.deepcopy(self.data)
        x["raw_response_sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            guard(x)

    def test_reject_claimed_full_proceedings(self):
        x = copy.deepcopy(self.data)
        x["negative_claims"]["complete_icad_2026_proceedings"] = True
        with self.assertRaises(AssertionError):
            guard(x)

    def test_reject_bibliography_chaining_without_text(self):
        x = copy.deepcopy(self.data)
        x["bounded_navigation_routes"][0]["bibliography_chained"] = True
        with self.assertRaises(AssertionError):
            guard(x)

    def test_reject_programme_published_study_conflation(self):
        x = copy.deepcopy(self.data)
        x["count_unit"] = "29 published independently eligible studies"
        with self.assertRaises(AssertionError):
            guard(x)

    def test_reject_presentation_count_drift(self):
        x = copy.deepcopy(self.data)
        x["observed_paper_sessions"][-1]["presentations_listed"] = 6
        with self.assertRaises(AssertionError):
            guard(x)

    def test_reject_unperformed_canonical_screen(self):
        x = copy.deepcopy(self.data)
        x["negative_claims"]["canonical_screening_or_source_records_added"] = True
        with self.assertRaises(AssertionError):
            guard(x)

    def test_reject_claimed_human_review(self):
        x = copy.deepcopy(self.data)
        x["observer"]["human_assessor"] = True
        with self.assertRaises(AssertionError):
            guard(x)

    def test_reject_frozen_cutoff_shift(self):
        x = copy.deepcopy(self.data)
        x["frozen_publication_cutoff"] = "2026-11-10"
        with self.assertRaises(AssertionError):
            guard(x)


if __name__ == "__main__":
    unittest.main()
