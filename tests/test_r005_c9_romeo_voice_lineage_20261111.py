"""Offline provenance and scientific non-admission guards for R005 C9 citation observations.

This tests the observation contract, not external source authenticity or human screening.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest

PATH = (Path(__file__).resolve().parents[1] /
        "research/searches/auditory/c9-romeo2025-voice-lineage-20261111/OBSERVATIONS.json")
DOIS = {
    61: "10.1109/RO-MAN57019.2023.10309631",
    74: "10.1016/j.chb.2019.106215",
    75: "10.1145/3183654.3183691",
    76: "10.1109/RO-MAN47096.2020.9223449",
}


def validate(o):
    assert o["schema"] == "mhac-r005-c9-romeo-voice-lineage/1"
    assert (o["issue"], o["downstream_issue"]) == (5, 6)
    assert o["base_sha"] == "2a5c480daa5f0ade8f0d76df66cf499174c60fa1"
    assert o["publication_cutoff"] == "2026-10-04"
    assert o["channel"].startswith("C9 selected backward citations")
    assert o["actor"]["human_reviewer"] is False
    assert o["actor"]["screening_decisions"] is False
    assert o["parent"]["doi"] == "10.1145/3711938"
    assert o["parent"]["source_id"] == "SRC-REL-ROMEO-2025"
    assert o["parent"]["examined_pdf_page_indices"] == [4, 20, 21]
    assert o["parent"]["examined_printed_page_numbers"] == ["33:4", "33:20", "33:21"]
    assert len(o["discovery_queries"]) >= 4
    cap = o["capture"]
    for k in ("raw_web_search_response_bytes_retained", "raw_article_pdf_bytes_retained",
              "direct_external_api_export", "complete_reference_list_transcribed"):
        assert cap[k] is False, k
    for k in ("original_http_response_sha256", "original_http_date",
              "original_http_status", "individual_access_timestamps"):
        assert cap[k] is None, k
    assert cap["page_images_visually_examined"] is True
    assert set(DOIS) == {x["reference_number"] for x in o["links"]}
    assert len({x["candidate_key"] for x in o["links"]}) == len(DOIS)
    for x in o["links"]:
        n = x["reference_number"]
        assert x["candidate_key"] == f"C9-ROMEO2025-REF{n:03d}"
        assert x["doi"] == DOIS[n], n
        assert "33:" in x["donor_locator"]
        assert x["verification_urls"] and all(s.startswith("https://") for s in x["verification_urls"])
        assert "not screened" in x["status"].lower() or "not screened" in x["verification_extent"].lower() or "requires R006" in x["status"]
    link61 = next(x for x in o["links"] if x["reference_number"] == 61)
    assert "original six-page IEEE paper was NOT accessed" in link61["verification_extent"]
    assert "participant/stimulus independence unknown" in link61["r006_identity"]
    assert o["related_2023_supplement"]["doi"] == "10.5281/zenodo.8042317"
    h = o["canonical_hit_handling"]
    assert h["new_canonical_hit_ids"] == []
    assert h["candidate_keys_are_not_HIT_ids"] is True
    for k in ("claimed_unique_new_publications", "screening_changes",
              "eligibility_changes", "independent_samples_added"):
        assert h[k] == 0, k
    assert h["identity_adjudication"] == "R006 only"
    g = o["scientific_gate"]
    assert g["r006_title_abstract_accepted_before"] == 9
    assert g["r006_title_abstract_after"] == 9
    for key, value in g.items():
        if key.startswith("r006_full_text_included") or key.startswith("r006_admitted_") or key.endswith("_selected_after"):
            assert value == 0, (key, value)
    return True


class RomeoCitationChain(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(PATH.read_text(encoding="utf-8"))

    def test_current_observations_valid(self):
        self.assertTrue(validate(self.record))

    def test_distinct_2023_and_2025_publication_do_is(self):
        for bad_doi in ("10.1145/3711938", "10.1109/ROMAN.2016.7745162"):
            bad = deepcopy(self.record)
            bad["links"][0]["doi"] = bad_doi
            with self.subTest(doi=bad_doi), self.assertRaises(AssertionError):
                validate(bad)

    def test_reference_numbers_and_candidate_keys_not_fabricated_hits(self):
        bad = deepcopy(self.record)
        bad["links"][1]["candidate_key"] = "HIT-R005-MADE-UP"
        with self.assertRaises(AssertionError):
            validate(bad)
        bad = deepcopy(self.record)
        bad["canonical_hit_handling"]["new_canonical_hit_ids"] = ["HIT-R005-FALSE"]
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_no_original_http_hash_or_unrecorded_export(self):
        for key, val in (("original_http_response_sha256", "0"*64),
                         ("original_http_status", 200),
                         ("individual_access_timestamps", ["2026-11-11T04:12:28Z"])):
            bad = deepcopy(self.record)
            bad["capture"][key] = val
            with self.subTest(key=key), self.assertRaises(AssertionError):
                validate(bad)
        bad = deepcopy(self.record)
        bad["capture"]["raw_article_pdf_bytes_retained"] = True
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_no_human_screening_or_new_empirical_units(self):
        bad = deepcopy(self.record)
        bad["actor"]["human_reviewer"] = True
        with self.assertRaises(AssertionError):
            validate(bad)
        bad = deepcopy(self.record)
        bad["canonical_hit_handling"]["independent_samples_added"] = 2
        with self.assertRaises(AssertionError):
            validate(bad)
        bad = deepcopy(self.record)
        bad["scientific_gate"]["r006_admitted_studies_after"] = 1
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_frozen_cutoff_and_edition_not_silently_changed(self):
        bad = deepcopy(self.record)
        bad["publication_cutoff"] = "2026-11-11"
        with self.assertRaises(AssertionError):
            validate(bad)
        bad = deepcopy(self.record)
        bad["parent"]["examined_pdf_page_indices"] = [0, 1, 4, 20, 21]
        with self.assertRaises(AssertionError):
            validate(bad)
