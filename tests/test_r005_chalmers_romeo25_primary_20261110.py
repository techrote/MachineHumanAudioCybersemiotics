"""Fail-closed checks for the R005 Chalmers rendered-source observation; not scientific adjudication."""
import copy
import json
import pathlib
import unittest

PATH = pathlib.Path(__file__).resolve().parents[1] / "research/sources/auditory/r006-romeo25-chalmers-render-2026-11-10/OBSERVATIONS.json"

def guard(d):
    m = d["publication"]
    assert d["frozen_search_cutoff"] == "2026-10-04"
    assert m["doi"] == "10.1145/3711938"
    assert m["access_method"] == "tool_mediated_public_institutional_pdf_text_and_page_images"
    assert m["readable_pages_reproduced"] is True
    assert m["source_files_byte_equivalent_proven"] is False
    assert m["original_pdf_bytes_retained"] is False
    assert m["original_sha256_verified"] is False
    assert d["exact_http_response_timestamp_utc"] is None
    assert d["observer"]["human_second_reader"] is False
    assert d["observer"]["independent_human_review"] is False
    assert d["comparison_2023"]["supplement_file_read"] is False
    assert d["comparison_2023"]["advertised_md5_computed"] is False
    assert d["comparison_2023"]["source_full_text_read"] is False
    assert [p["pdf_page_index_zero_based"] for p in d["inspected_pages"]] == list(range(5, 11))
    assert [p["printed_page"] for p in d["inspected_pages"]] == [f"33:{i}" for i in range(5, 11)]
    assert sorted(p["author_reported_recruited"] for p in d["inspected_pages"] if "author_reported_recruited" in p) == [50, 60]
    assert "HIT-R004-G06-07@1" in d["existing_discovery_links"]
    assert d["negative_claims"] and not any(d["negative_claims"].values())
    return True

class TestChalmersSourceBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PATH.read_text(encoding="utf-8"))

    def test_positive(self):
        self.assertTrue(guard(self.data))

    def test_reject_invented_human(self):
        x = copy.deepcopy(self.data)
        x["observer"]["human_second_reader"] = True
        with self.assertRaises(AssertionError): guard(x)

    def test_reject_unseen_source_bytes(self):
        x = copy.deepcopy(self.data)
        x["publication"]["original_sha256_verified"] = True
        with self.assertRaises(AssertionError): guard(x)

    def test_reject_imaginary_equivalent_manifests(self):
        x = copy.deepcopy(self.data)
        x["publication"]["source_files_byte_equivalent_proven"] = True
        with self.assertRaises(AssertionError): guard(x)

    def test_reject_unchecked_2023_supplement(self):
        x = copy.deepcopy(self.data)
        x["comparison_2023"]["advertised_md5_computed"] = True
        with self.assertRaises(AssertionError): guard(x)

    def test_reject_2023_claimed_read(self):
        x = copy.deepcopy(self.data)
        x["comparison_2023"]["source_full_text_read"] = True
        with self.assertRaises(AssertionError): guard(x)

    def test_reject_index_offset(self):
        x = copy.deepcopy(self.data)
        x["inspected_pages"][0]["pdf_page_index_zero_based"] = 4
        with self.assertRaises(AssertionError): guard(x)

    def test_reject_admission_from_source_navigation(self):
        x = copy.deepcopy(self.data)
        x["negative_claims"]["independent_sample_admission"] = True
        with self.assertRaises(AssertionError): guard(x)

if __name__ == "__main__":
    unittest.main()
