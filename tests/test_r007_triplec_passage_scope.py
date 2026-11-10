"""Guardrail checks for R007's Brier 2003 preparatory passage observations.

These tests check recorded provenance and non-admission only; they cannot
verify a philosophical interpretation or substitute for original source reading.
"""
from __future__ import annotations

import csv
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/extractions/brier/R007-TRIPLEC-2003-PASSAGE-LEDGER-20261110.csv"
MEMO = ROOT / "research/analysis/brier/R007-TRIPLEC-2003-THRESHOLD-RECONSTRUCTION-20261110.md"

TRIPLEC = "SRC-BRIER-2003-TRIPLEC"
IR2013 = "SRC-BRIER-2013-IR"


def validate_scope(rows: list[dict[str, str]]) -> None:
    """Fail closed if observations are relabelled as admitted or full-text verified."""
    if len(rows) != 13 or len({r["anchor_id"] for r in rows}) != len(rows):
        raise ValueError("Missing or duplicate passage anchor")
    for r in rows:
        if r["source_registry_id"] not in {TRIPLEC, IR2013}:
            raise ValueError("Unknown source manifestation")
        if not r["source_url"].startswith("https://"):
            raise ValueError("Unresolvable source provenance")
        if r["source_file_sha256"]:
            raise ValueError("No original source bytes were hashed by this tranche")
        if r["human_review"] != "not_performed":
            raise ValueError("No human reader was consulted")
        if r["admission_status"] != "preparatory":
            raise ValueError("Only preparatory passages recorded")
        if r["inspection_mode"] not in {"extracted_text", "extracted_text_and_rendered_page"}:
            raise ValueError("Unverified inspection mode")
        year = 2003 if r["source_registry_id"] == TRIPLEC else 2013
        first_page = 71 if year == 2003 else 220
        if r["publication_year"] != str(year) or int(r["printed_page"]) - first_page != int(r["pdf_page_zero_index"]):
            raise ValueError("Wrong edition/year or printed/PDF locator offset")
    secondhand = [r for r in rows if r["claim_type"] == "secondhand_quotation_in_primary"]
    if len(secondhand) != 1 or secondhand[0]["printed_page"] != "83":
        raise ValueError("Noth quotation provenance was lost")
    if len([r for r in rows if r["inspection_mode"].endswith("rendered_page")]) != 9:
        raise ValueError("Rendered versus parser-only inspection drift")


class R007PassageScopeTests(unittest.TestCase):
    def setUp(self):
        with LEDGER.open(encoding="utf-8", newline="") as f:
            self.rows = list(csv.DictReader(f))
        self.memo = MEMO.read_text(encoding="utf-8")

    def test_recorded_passage_scope(self):
        validate_scope(self.rows)
        self.assertEqual(
            {r["anchor_id"] for r in self.rows if r["source_registry_id"] == IR2013},
            {"R007-IR13-01", "R007-IR13-02", "R007-IR13-03"},
        )

    def test_fictional_human_or_forged_hash_must_fail(self):
        for key, fake in (("human_review", "approved"), ("source_file_sha256", "a" * 64),
                          ("admission_status", "source_checked")):
            rows = [dict(r) for r in self.rows]
            rows[0][key] = fake
            with self.assertRaises(ValueError):
                validate_scope(rows)

    def test_invalid_page_mapping_and_source_collision_fail(self):
        for key, fake in (("pdf_page_zero_index", "999"), ("source_registry_id", "SRC-OTHER"),
                          ("publication_year", "2014")):
            rows = [dict(r) for r in self.rows]
            rows[0][key] = fake
            with self.assertRaises(ValueError):
                validate_scope(rows)
        rows = [dict(r) for r in self.rows]
        rows[1]["anchor_id"] = rows[0]["anchor_id"]
        with self.assertRaises(ValueError):
            validate_scope(rows)

    def test_quote_is_secondhand_not_authority(self):
        row = next(r for r in self.rows if r["printed_page"] == "83")
        self.assertEqual(row["claim_type"], "secondhand_quotation_in_primary")
        self.assertIn("Noth original not consulted", row["brief_finding"])

    def test_five_levels_not_miscast_as_four(self):
        self.assertIn("five ontological levels", self.memo.lower())
        self.assertIn("four knowledge interests", self.memo.lower())
        self.assertIn("not a superseded 2013 four-level model", self.memo.lower())
        self.assertIn("remove-brier counterfactual", self.memo.lower())
        self.assertIn("not performed", self.memo.lower() + " " + "not_performed")

    def test_no_selected_corpus_or_empirical_claim(self):
        self.assertIn("no accepted selected Track G corpus", self.memo)
        self.assertIn("No original PDF bytes", self.memo)
        self.assertIn("NONE ADMITTED", self.memo)
        self.assertIn("Refs #7", self.memo)


if __name__ == "__main__":
    unittest.main()
