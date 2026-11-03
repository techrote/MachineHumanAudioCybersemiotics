"""Integrity checks for the MHAC-R004 related-theory corpus (Track G).

These tests check provenance and internal consistency only. They cannot show that a
role statement, concept-map relation or reading is correct.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
RELATED = ROOT / "research/sources/related"
SEARCHES = ROOT / "research/searches/related"
EXPORTS = SEARCHES / "exports"
LOOKUPS = EXPORTS / "lookups"


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def latest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["revisions"][-1]["data"]


def record_path(rid: str) -> Path | None:
    for lane in ("research/sources/related/records", "research/novelty/records", "research/sources/brier/records",
                 "research/searches/related/records"):
        path = ROOT / lane / f"{rid}.json"
        if path.exists():
            return path
    return None


class LookupProvenanceTests(unittest.TestCase):
    def test_retained_lookup_responses_match_manifest_hashes(self):
        manifest = json.loads((LOOKUPS / "MANIFEST.json").read_text(encoding="utf-8"))
        count = 0
        for section in ("lookups", "round2", "round3", "round4"):
            for key, entry in manifest[section].items():
                path = ROOT / entry["file"]
                self.assertTrue(path.is_file(), f"{section}/{key}")
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"], f"{section}/{key}")
                self.assertEqual(entry["http_status"], 200, f"{section}/{key}")
                count += 1
        self.assertEqual(count, 81)

    def test_work_records_with_abstracts_are_hashed_but_not_committed(self):
        manifest = json.loads((LOOKUPS / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["work_records"]), 34)
        for key, entry in manifest["work_records"].items():
            self.assertFalse(entry["retained"], key)
            self.assertNotIn("file", entry, key)
            self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(list(LOOKUPS.glob("*.work.json")), [])

    def test_no_source_files_are_committed_in_the_lane(self):
        for base in (RELATED, SEARCHES):
            for suffix in ("*.pdf", "*.html", "*.txt"):
                self.assertEqual(list(base.rglob(suffix)), [], f"{base}/{suffix}")


class SearchLogTests(unittest.TestCase):
    def setUp(self):
        self.web = json.loads((EXPORTS / "RELATED-WEBSEARCH-2026-10-13.json").read_text(encoding="utf-8"))
        self.runs = [run for batch in self.web["batches"] for run in batch["runs"]]

    def test_web_runs_have_records_and_hits(self):
        self.assertEqual([r["label"] for r in self.runs], [f"G-{n:02d}" for n in range(1, 32)])
        for run in self.runs:
            rid = "SRCH-R004-" + run["label"].replace("-", "")
            data = latest(SEARCHES / "records" / f"{rid}.json")
            self.assertEqual(data["query"], run["query"])
            self.assertEqual(data["retrieved_count"], len(run["results"]))
            for res in run["results"]:
                hit = SEARCHES / "records/hits" / f"HIT-R004-{run['label'].replace('-', '')}-{res['ordinal']:02d}.json"
                self.assertTrue(hit.is_file(), hit.name)

    def test_every_sampled_cluster_has_a_negative_case_search(self):
        negative = {run["cluster"] for run in self.runs if run["purpose"] == "negative"}
        clusters = {row["cluster"] for row in rows(RELATED / "SOURCE-MAP-R004.csv")}
        self.assertEqual(clusters - negative, set())

    def test_brier_reference_lists_match_their_search_records_and_ledger(self):
        lists = json.loads((EXPORTS / "BRIER-REFLISTS-R004.json").read_text(encoding="utf-8"))["lists"]
        ledger = (EXPORTS / "ACCESS-LEDGER-R004-2026-10-13.csv").read_text(encoding="utf-8")
        for lst in lists:
            data = latest(SEARCHES / "records" / f"SRCH-R004-{lst['label'].replace('-', '')}.json")
            self.assertEqual(data["retrieved_count"], len(lst["entries"]))
            self.assertIn(lst["sha256"], ledger)
            self.assertIsNotNone(record_path(lst["source_record"]), lst["source_record"])

    def test_access_ledger_is_contiguous(self):
        ledger = rows(EXPORTS / "ACCESS-LEDGER-R004-2026-10-13.csv")
        self.assertEqual([int(r["seq"]) for r in ledger], list(range(1, len(ledger) + 1)))
        for r in ledger:
            self.assertRegex(r["time_utc"], r"^2026-10-13T\d\d:\d\d:\d\dZ$")
            self.assertTrue(r["outcome"].strip(), r["seq"])


class SourceMapTests(unittest.TestCase):
    def setUp(self):
        self.map = rows(RELATED / "SOURCE-MAP-R004.csv")
        self.ids = {r["source_record"] for r in self.map}

    def test_every_related_source_record_is_mapped_with_role_and_provenance(self):
        records = {p.stem for p in (RELATED / "records").glob("SRC-*.json")}
        self.assertEqual(records - self.ids, set())
        for row in self.map:
            self.assertTrue(row["role"].strip(), row["source_record"])
            self.assertTrue(row["search_provenance"].strip(), row["source_record"])
            for token in row["search_provenance"].split():
                if token.startswith("SRCH-"):
                    self.assertIsNotNone(record_path(token), token)

    def test_map_agrees_with_records(self):
        for row in self.map:
            if not row["source_record"].startswith("SRC-REL-"):
                continue
            data = latest(RELATED / "records" / f"{row['source_record']}.json")
            self.assertEqual(row["metadata_status"], data["metadata_status"], row["source_record"])
            self.assertEqual(row["access_status"], data["access_status"], row["source_record"])
            self.assertEqual(row["rights"], data["rights"]["status"], row["source_record"])

    def test_resolved_hits_point_at_existing_sources(self):
        resolved = 0
        for path in (SEARCHES / "records/hits").glob("HIT-R004-*.json"):
            data = latest(path)
            if data["status"] == "resolved":
                resolved += 1
                self.assertIsNotNone(record_path(data["source_ref"]["id"]), path.name)
        self.assertGreater(resolved, 100)

    def test_memo_lists_every_mapped_source(self):
        memo = (RELATED / "README.md").read_text(encoding="utf-8")
        for rid in self.ids:
            self.assertIn(f"`{rid}`", memo, rid)


class ConceptMapTests(unittest.TestCase):
    REQUIRED = ("Grounding", "Feedback", "Situated interpretation", "System boundaries", "Non-human audio design",
                "Interpretant", "Information", "Urgency", "Human-likeness", "Persistence and lifecycle")

    def setUp(self):
        self.map = rows(RELATED / "CONCEPT-MAP-R004.csv")

    def test_required_concepts_are_covered(self):
        concepts = {r["project_concept"] for r in self.map}
        for concept in self.REQUIRED:
            self.assertIn(concept, concepts)

    def test_every_row_cites_existing_sources_and_flags_a_question(self):
        for row in self.map:
            self.assertRegex(row["map_id"], r"^CM\d\d$")
            for rid in row["source_records"].split(";"):
                self.assertIsNotNone(record_path(rid), f"{row['map_id']}: {rid}")
            for field in ("evidence_read", "apparent_relation_for_8", "question_for_8"):
                self.assertTrue(row[field].strip(), f"{row['map_id']}: {field}")

    def test_register_ids_exist_in_the_concept_register_or_glossary(self):
        register = (ROOT / "research/protocol/CONCEPT_REGISTER.md").read_text(encoding="utf-8")
        glossary = (ROOT / "research/protocol/GLOSSARY-v1.md").read_text(encoding="utf-8")
        for row in self.map:
            for cid in row["register_ids"].split(";"):
                self.assertTrue(re.search(rf"\| {re.escape(cid)} \|", register + glossary), f"{row['map_id']}: {cid}")


if __name__ == "__main__":
    unittest.main()
