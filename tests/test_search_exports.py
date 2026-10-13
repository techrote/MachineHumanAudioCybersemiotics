"""Live search runs point at retained exports whose bytes match, and R005 runs mirror their export."""
from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = json.loads((ROOT / "research/registry/state.json").read_text(encoding="utf-8"))
R005_EXPORT = ROOT / "research/searches/auditory/exports/AUDITORY-WEBSEARCH-2026-10-13.json"
R005_RECORDS = ROOT / "research/searches/auditory/records"
KNOWN_CSV = ROOT / "research/searches/auditory/exports/KNOWN-ITEM-CHECK-R005.csv"
ICAD_LISTING = ROOT / "research/searches/auditory/exports/ICAD-LISTING-2026-10-13.json"
OPENALEX_MANIFEST = ROOT / "research/searches/auditory/exports/openalex/MANIFEST.json"


def latest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["revisions"][-1]["data"]


def live_search_runs():
    for root in STATE["record_roots"]:
        for path in sorted((ROOT / root).rglob("SRCH-*.json")):
            yield path, latest(path)


class SearchExportTests(unittest.TestCase):
    def test_every_retained_export_matches_its_digest(self) -> None:
        checked = 0
        for path, data in live_search_runs():
            export = data["export"]
            if export.get("state") != "known":
                continue
            target = ROOT / export["value"]["path"]
            self.assertTrue(target.is_file(), f"{path.name}: missing {target}")
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), export["value"]["sha256"], path.name)
            checked += 1
        self.assertGreater(checked, 0)

    def test_r005_runs_mirror_export(self) -> None:
        export = json.loads(R005_EXPORT.read_text(encoding="utf-8"))
        labels = [run for batch in export["batches"] for run in batch["runs"]]
        labels += [{"label": rl["label"], "results": rl["entries"]} for rl in export["reference_lists"]]
        for run in labels:
            rid = "SRCH-R005-" + run["label"].replace("-", "")
            data = latest(R005_RECORDS / f"{rid}.json")
            self.assertEqual(data["retrieved_count"], len(run["results"]), rid)
            if "query" in run:
                self.assertEqual(data["query"], run["query"], rid)
        expected = sum(len(run["results"]) for run in labels)
        listing = json.loads(ICAD_LISTING.read_text(encoding="utf-8"))
        listed = sum(len(year["pdf_files"]) for year in listing["years_listed"])
        self.assertEqual(latest(R005_RECORDS / "SRCH-R005-C5LIST.json")["retrieved_count"], listed)
        expected += listed
        if OPENALEX_MANIFEST.exists():
            manifest = json.loads(OPENALEX_MANIFEST.read_text(encoding="utf-8"))
            for label, run in manifest["runs"].items():
                retrieved = sum(page.get("results", 0) for page in run["pages"])
                self.assertEqual(latest(R005_RECORDS / f"SRCH-R005-C1{label}.json")["retrieved_count"], retrieved, label)
                for page in run["pages"]:
                    if page.get("file"):
                        body = (ROOT / page["file"]).read_bytes()
                        self.assertEqual(hashlib.sha256(body).hexdigest(), page["sha256"], page["file"])
                expected += retrieved
        hits = list((R005_RECORDS / "hits").glob("HIT-R005-*.json"))
        self.assertEqual(len(hits), expected)

    def test_gated_channels_have_outcomes(self) -> None:
        for channel in ("C1", "C2", "C3", "C4", "C6", "C7"):
            data = latest(R005_RECORDS / f"SRCH-R005-{channel}.json")
            self.assertIn(data["status"], {"failed", "planned"}, channel)
            self.assertEqual(data["retrieved_count"], 0)
            self.assertTrue(data["failures"], channel)

    def test_known_item_table_covers_reference_list(self) -> None:
        with KNOWN_CSV.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([int(r["entry"]) for r in rows], list(range(1, 70)))
        self.assertTrue({r["outcome"] for r in rows} <= {"located", "possible", "not_located"})
        for row in rows:
            if row["outcome"] == "not_located":
                continue
            self.assertTrue(row["matching_ordinals"] or row["also_in_topic_runs"], row["entry"])


if __name__ == "__main__":
    unittest.main()
