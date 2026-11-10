"""Negative controls for R007 primary-source citation identity; no scientific attestation."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/extractions/brier/R007-2013-CITATION-IDENTITY-CHECK-20261110.json"
EXPECTED = {"R007-REF-%02d" % i for i in range(1, 6)}


def validate(payload):
    if payload.get("record_type") != "R007_bounded_reference_identity_audit":
        raise ValueError("wrong record type")
    for key in ("source_bytes_obtained", "full_item_read",
                "independent_human_review", "canonical_track_g_admission"):
        if payload.get(key) is not False:
            raise ValueError("false promotion of " + key)
    if payload.get("source_file_sha256") is not None:
        raise ValueError("fabricated source hash")
    m = payload["manifestations"]
    if m["semiotica_2006"]["doi"] != "10.1515/SEM.2006.008":
        raise ValueError("Semiotica identity mismatch")
    if m["triplec_2003"]["doi"] != "10.31269/triplec.v1i1.6":
        raise ValueError("tripleC identity mismatch")
    if m["semiotica_2006"]["reading_mode"] != "publisher_metadata_and_abstract_only":
        raise ValueError("unverified 2006 full text")
    if any(v["source_hash"] is not None for v in m.values()):
        raise ValueError("fabricated manifestation hash")
    rows = payload["observations"]
    if len(rows) != 5 or {r.get("id") for r in rows} != EXPECTED:
        raise ValueError("incorrect/duplicate observation identity")
    idx = {(r["source"], r["printed_page"]): r["pdf_page_zero_index"] for r in rows}
    if idx[("integral_review_2013", 223)] != 3 or idx[("integral_review_2013", 259)] != 39:
        raise ValueError("2013 edition/page mapping error")
    if idx[("triplec_2003", 81)] != 11:
        raise ValueError("CBS repository cover offset lost")
    if idx[("semiotica_2006", None)] is not None:
        raise ValueError("invented 2006 page locator")


class CitationIdentityGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(LEDGER.read_text(encoding="utf8"))

    def test_actual_ledger(self):
        validate(self.data)

    def test_no_human_promotion(self):
        bad = copy.deepcopy(self.data)
        bad["independent_human_review"] = True
        with self.assertRaises(ValueError):
            validate(bad)

    def test_no_fulltext_promotion(self):
        bad = copy.deepcopy(self.data)
        bad["full_item_read"] = True
        with self.assertRaises(ValueError):
            validate(bad)

    def test_no_doi_collision(self):
        bad = copy.deepcopy(self.data)
        bad["manifestations"]["semiotica_2006"]["doi"] = "10.31269/triplec.v1i1.6"
        with self.assertRaises(ValueError):
            validate(bad)

    def test_no_2006_body_claim(self):
        bad = copy.deepcopy(self.data)
        bad["manifestations"]["semiotica_2006"]["reading_mode"] = "full_text"
        with self.assertRaises(ValueError):
            validate(bad)

    def test_no_invented_hash(self):
        bad = copy.deepcopy(self.data)
        bad["source_file_sha256"] = "a" * 64
        with self.assertRaises(ValueError):
            validate(bad)

    def test_no_pdf_index_transfer(self):
        bad = copy.deepcopy(self.data)
        next(r for r in bad["observations"] if r["id"] == "R007-REF-05")["pdf_page_zero_index"] = 10
        with self.assertRaises(ValueError):
            validate(bad)

    def test_no_fake_2006_page_locator(self):
        bad = copy.deepcopy(self.data)
        next(r for r in bad["observations"] if r["id"] == "R007-REF-04")["pdf_page_zero_index"] = 100
        with self.assertRaises(ValueError):
            validate(bad)

    def test_no_duplicate_ids(self):
        bad = copy.deepcopy(self.data)
        bad["observations"][1]["id"] = bad["observations"][0]["id"]
        with self.assertRaises(ValueError):
            validate(bad)


if __name__ == "__main__":
    unittest.main()
