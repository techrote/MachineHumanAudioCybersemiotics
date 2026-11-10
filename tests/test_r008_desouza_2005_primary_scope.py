"""Structural guards for R008's 2005 de Souza noncanonical reading ledger.

Tests cannot verify primary-source truth, full reading or independent human review.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/extractions/related/R008-DESOUZA-2005-SELECTED-PASSAGES-20261110.json"
MEMO = ROOT / "research/analysis/comparisons/R008-DESOUZA-2005-PRIMARY-ARGUMENT-COUNTERFACTUAL-20261110.md"


def validate_scope(doc: dict) -> None:
    if doc.get("record_type") != "preparatory_passage_navigation_not_canonical_extraction":
        raise ValueError("Noncanonical status lost")
    if doc.get("issue") != "Refs #8":
        raise ValueError("Partial shard may not close issue #8")
    source = doc.get("source", {})
    if (source.get("doi") != "10.1016/j.intcom.2005.01.007"
            or source.get("year") != 2005
            or source.get("not_the_2005_book") is not True
            or source.get("printed_pages") != "317-341"):
        raise ValueError("Publication identity or edition collision")
    method = doc.get("method", {})
    if method.get("actor_kind") != "AI_assisted":
        raise ValueError("AI provenance absent")
    forbidden_truth = ("bytes_obtained", "physical_manifestation_verified",
                       "human_reviewer", "full_item_read", "selected_track_g_corpus",
                       "passage_quotes_reproduced", "figures_verified",
                       "source_claim_promotion")
    if any(method.get(k) is not False for k in forbidden_truth):
        raise ValueError("Unverified reading, science or reviewer promoted")
    if method.get("sha256") is not None:
        raise ValueError("No original PDF was hashed")
    attempts = method.get("render_attempts")
    if not isinstance(attempts, list) or len(attempts) != 3 or any(
        a.get("result") != "timeout" for a in attempts
    ):
        raise ValueError("Figure-render failures must not be erased")
    rows = doc.get("observations")
    if not isinstance(rows, list) or len(rows) != 8 or len({r.get("id") for r in rows}) != 8:
        raise ValueError("Missing or duplicated passage navigation")
    for row in rows:
        first, last = (row.get("printed_pages") or "").split("-")
        if not (317 <= int(first) <= int(last) <= 341):
            raise ValueError("Impossible printed-page locator")
        if not row.get("section") or not row.get("paraphrase"):
            raise ValueError("Empty passage context")
        if (row.get("reading_route") != "web_intermediary_text"
                or row.get("locator_kind") != "printed_page_from_parsed_pdf"
                or row.get("evidence_status") != "non_decisive"
                or row.get("classification") not in {"author_argument", "author_illustration"}
                or row.get("manifestation_sha256") is not None
                or row.get("original_bytes_verified") is not False
                or row.get("human_checked") is not False
                or row.get("study_or_sample_count") is not None):
            raise ValueError("False source authority or study/sample inflation")


class R008DeSouza2005Tests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(LEDGER.read_text(encoding="utf-8"))
        self.memo = MEMO.read_text(encoding="utf-8")

    def test_landed_scope(self):
        validate_scope(self.doc)

    def test_source_collision_and_out_of_bounds_rejected(self):
        for key, val in (("doi", "10.invalid/book"), ("year", 2013),
                         ("not_the_2005_book", False), ("printed_pages", "1-100")):
            bad = copy.deepcopy(self.doc)
            bad["source"][key] = val
            with self.assertRaises(ValueError):
                validate_scope(bad)
        bad = copy.deepcopy(self.doc)
        bad["observations"][0]["printed_pages"] = "350-351"
        with self.assertRaises(ValueError):
            validate_scope(bad)

    def test_no_forged_human_hash_or_full_read(self):
        for key, val in (("human_reviewer", True), ("bytes_obtained", True),
                         ("physical_manifestation_verified", True),
                         ("full_item_read", True), ("figures_verified", True),
                         ("selected_track_g_corpus", True),
                         ("source_claim_promotion", True), ("sha256", "a" * 64)):
            bad = copy.deepcopy(self.doc)
            bad["method"][key] = val
            with self.assertRaises(ValueError):
                validate_scope(bad)

    def test_duplicate_or_missing_rows_rejected(self):
        bad = copy.deepcopy(self.doc)
        bad["observations"][1]["id"] = bad["observations"][0]["id"]
        with self.assertRaises(ValueError):
            validate_scope(bad)
        bad = copy.deepcopy(self.doc)
        bad["observations"].pop()
        with self.assertRaises(ValueError):
            validate_scope(bad)

    def test_no_empirical_sample_or_fake_render(self):
        bad = copy.deepcopy(self.doc)
        bad["observations"][0]["study_or_sample_count"] = 12
        with self.assertRaises(ValueError):
            validate_scope(bad)
        bad = copy.deepcopy(self.doc)
        bad["method"]["render_attempts"][0]["result"] = "success"
        with self.assertRaises(ValueError):
            validate_scope(bad)

    def test_subtraction_and_contrary_voice_claims_present(self):
        assert "Refs #8" in self.memo
        assert "source-bounded" in self.memo.lower()
        assert "no brier-specific" in self.memo.lower() or "no brier" in self.memo.lower()
        assert "Emotion-free wording" in self.memo
        assert "Figure" in self.memo and "timed out" in self.memo
        assert "OPEN" in self.memo


if __name__ == "__main__":
    unittest.main()
