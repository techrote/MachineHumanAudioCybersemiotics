"""R007 2003/2006/2013 source-scope guardrails; not scientific validation."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/extractions/brier/R007-EDITION-BOUND-PRIMARY-CHECKS-20261110.json"
MEMO = ROOT / "research/analysis/brier/R007-2003-2006-2013-MANIFESTATION-CHRONOLOGY-20261110.md"

EXPECTED_IDS = {"R007-MAN-%02d" % n for n in range(1, 9)}
DOIS = {"triplec_2003": "10.31269/triplec.v1i1.6",
        "semiotica_2006": "10.1515/SEM.2006.008",
        "integral_review_2013": None}


def validate_ledger(doc: dict) -> None:
    if doc.get("record_type") != "R007_preparatory_manifestation_observation":
        raise ValueError("not a bounded R007 observation")
    if doc.get("accepted_as_selected_track_g") is not False:
        raise ValueError("R006 has not selected a Track G corpus")
    if doc.get("original_source_bytes_hashed") is not False:
        raise ValueError("no source bytes were independently hashed")
    if doc.get("independent_human_review") != "not_performed":
        raise ValueError("no independent human review occurred")
    rows = doc.get("observations", [])
    if {r.get("id") for r in rows} != EXPECTED_IDS or len(rows) != 8:
        raise ValueError("missing, duplicate or extraneous observation anchors")
    for row in rows:
        item = row.get("manifestation")
        if item not in DOIS or row.get("doi") != DOIS[item]:
            raise ValueError("manifestation / DOI collision")
        if row.get("admission_status") != "preparatory":
            raise ValueError("unjustified selection promotion")
        if row.get("reviewer_status") != "agent_only":
            raise ValueError("false independent assessor")
        if row.get("source_file_sha256") is not None:
            raise ValueError("fabricated original PDF hash")
        if not str(row.get("source_url", "")).startswith("https://"):
            raise ValueError("source URL missing")
        if item == "semiotica_2006":
            if (row.get("printed_page") is not None
                    or row.get("pdf_page_zero_index") is not None
                    or row.get("inspection") != "indexed_publisher_abstract_only_live_html_403"
                    or row.get("kind") != "publisher_article_page"):
                raise ValueError("2006 text was not accessed beyond indexed abstract")
        elif item == "triplec_2003" and row["kind"] == "article_pdf":
            if row["printed_page"] - 71 != row["pdf_page_zero_index"]:
                raise ValueError("2003 printed/PDF page mapping changed")
        elif item == "integral_review_2013":
            if row["printed_page"] - 220 != row["pdf_page_zero_index"]:
                raise ValueError("2013 printed/PDF page mapping changed")

    by_id = {r["id"]: r for r in rows}
    if (by_id["R007-MAN-07"]["printed_page"] != 255
            or by_id["R007-MAN-06"]["printed_page"] != 224
            or by_id["R007-MAN-04"]["manifestation"] != "semiotica_2006"):
        raise ValueError("decisive adverse chronology anchors lost")


class ManifestationChronologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.memo = MEMO.read_text(encoding="utf-8")

    def test_bounded_manifestations_and_pages(self):
        validate_ledger(self.doc)

    def test_human_or_byte_hash_invention_rejected(self):
        for field, fake in (("independent_human_review", "approved"),
                            ("original_source_bytes_hashed", True)):
            modified = copy.deepcopy(self.doc)
            modified[field] = fake
            with self.assertRaises(ValueError):
                validate_ledger(modified)
        modified = copy.deepcopy(self.doc)
        modified["observations"][0]["source_file_sha256"] = "a" * 64
        with self.assertRaises(ValueError):
            validate_ledger(modified)

    def test_publisher_abstract_cannot_be_promoted_to_fulltext(self):
        for field, fake in (("inspection", "full_text"),
                            ("printed_page", 265),
                            ("pdf_page_zero_index", 9)):
            modified = copy.deepcopy(self.doc)
            modified["observations"][3][field] = fake
            with self.assertRaises(ValueError):
                validate_ledger(modified)

    def test_wrong_doi_and_locators_rejected(self):
        for pos, field, fake in ((3, "doi", "10.31269/triplec.v1i1.6"),
                                 (6, "pdf_page_zero_index", 34),
                                 (1, "pdf_page_zero_index", 99)):
            modified = copy.deepcopy(self.doc)
            modified["observations"][pos][field] = fake
            with self.assertRaises(ValueError):
                validate_ledger(modified)

    def test_no_duplicate_or_unrecorded_item(self):
        for mutate in ("duplicate", "drop"):
            modified = copy.deepcopy(self.doc)
            if mutate == "duplicate":
                modified["observations"].append(copy.deepcopy(modified["observations"][0]))
            else:
                modified["observations"].pop()
            with self.assertRaises(ValueError):
                validate_ledger(modified)

    def test_counterreading_and_gates_not_misreported(self):
        required = ("printed p. 255", "printed p. 224", "five levels",
                    "2008-06-12", "HTTP 403", "2006", "not read",
                    "NO SELECTION", "not shown", "Refs #7")
        for phrase in required:
            self.assertIn(phrase.lower(), self.memo.lower())
        self.assertNotIn("Closes #7", self.memo)


if __name__ == "__main__":
    unittest.main()
