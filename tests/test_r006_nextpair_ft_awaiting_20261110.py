"""R006: two lawful full-text access gates, no empirical admission.

Live source and TA pins are checked; external R005 search bases are omitted only
from a test-local graph projection. Full manifest, history, exports and CI remain
Integration-owned gates. Later legitimate revisions are not frozen by this test.
"""
import copy
import json
from pathlib import Path
import unittest

from schemas import ValidationError
from schemas.v1 import validate_record
from tools.record_graph import validate_graph
from tools.screening import screening_coverage

ROOT = Path(__file__).resolve().parents[1]
PROTO = "MHAC-Track-E-frozen-v1-2026-10-13"
CASES = (
    ("SRC-R006-EDWORTHY-2014-LEARNING", "SCR-R006-EDWORTHY-2014-LEARNING-TA",
     "SCR-R006-EDWORTHY-2014-LEARNING-FT", "10.1016/j.apergo.2013.10.003"),
    ("SRC-R006-F-ARRABITO-URGENCY", "SCR-R006-ARRABITO-2004-URGENCY-TA",
     "SCR-R006-ARRABITO-2004-URGENCY-FT", "10.1080/0014013042000193282"),
)


def record(folder, rid):
    return json.loads((ROOT / folder / (rid + ".json")).read_text(encoding="utf-8"))


def first_revision(record):
    item = copy.deepcopy(record)
    item["revisions"] = item["revisions"][:1]
    return item


def projection(source, ta, ft):
    source = first_revision(source)
    ta = first_revision(ta)
    ft = first_revision(ft)
    # R005 cross-lane original discovery pins are separately checked in live
    # history; do not invent external HIT/AID objects in this isolated graph.
    source["revisions"][0]["basis"] = []
    return validate_graph([source, ta, ft])


class NextPairAwaitingTextTests(unittest.TestCase):
    def setUp(self):
        self.cases = []
        for sid, tid, fid, doi in CASES:
            s = record("research/registry/identity/records", sid)
            t = record("research/screening/records", tid)
            f = record("research/screening/records", fid)
            self.cases.append((sid, tid, fid, doi, s, t, f))

    def test_live_schema_valid(self):
        for _, _, _, _, s, t, f in self.cases:
            for item in (s, t, f):
                validate_record(item, expected_kind="live")

    def test_exact_verified_publication_and_original_parent(self):
        for sid, tid, fid, doi, s, t, f in self.cases:
            with self.subTest(doi=doi):
                source = s["revisions"][0]["data"]
                self.assertIn(doi, {x["value"].lower() for x in source["identifiers"]
                                   if x["scheme"] == "doi" and x["status"] == "verified"})
                self.assertEqual("metadata_only", source["access_status"])
                self.assertEqual([], source["manifestations"])
                self.assertEqual("include", t["revisions"][0]["data"]["decision"])
                r = f["revisions"][0]
                self.assertEqual([{"id": sid, "rev": 1}, {"id": tid, "rev": 1}], r["basis"])
                self.assertEqual({"id": sid, "rev": 1}, r["data"]["source_ref"])
                self.assertEqual("agent", r["actor"]["kind"])
                self.assertEqual("full_text", r["data"]["stage"])
                self.assertEqual("empirical", r["data"]["track"])
                self.assertEqual(PROTO, r["data"]["protocol_version"])

    def test_access_not_eligibility_and_not_three_studies(self):
        for sid, tid, fid, doi, s, t, f in self.cases:
            with self.subTest(doi=doi):
                r = f["revisions"][0]["data"]
                self.assertEqual("awaiting_text", r["decision"])
                self.assertEqual([], r["reading_refs"])
                self.assertEqual([], r["review_refs"])
                self.assertIn(doi, r["access_limitation"])
                graph = projection(s, t, f)
                cov = screening_coverage(graph, source_ids=[sid],
                                         protocol_version=PROTO, track="empirical")
                self.assertEqual([sid], cov["awaiting_text"])
                self.assertEqual([], cov["missing_required_full_text"])
                self.assertFalse(any(row["kind"] in ("study", "experiment", "sample")
                                     for row in graph.records.values()))

    def test_no_final_fulltext_decision_without_actual_reading(self):
        for sid, tid, fid, doi, s, t, f in self.cases:
            for decision in ("include", "exclude"):
                changed = copy.deepcopy(f)
                changed["revisions"][0]["data"]["decision"] = decision
                with self.subTest(doi=doi, decision=decision):
                    with self.assertRaises(ValidationError):
                        projection(s, t, changed)

    def test_no_fulltext_after_ta_exclusion(self):
        for sid, tid, fid, doi, s, t, f in self.cases:
            changed = copy.deepcopy(t)
            changed["revisions"][0]["data"]["decision"] = "exclude"
            with self.subTest(doi=doi):
                with self.assertRaises(ValidationError):
                    projection(s, changed, f)

    def test_no_duplicate_unsuperseded_fulltext(self):
        for sid, tid, fid, doi, s, t, f in self.cases:
            ss = first_revision(s)
            ss["revisions"][0]["basis"] = []
            dup = first_revision(f)
            dup["id"] = fid + "-DUPLICATE"
            with self.subTest(doi=doi), self.assertRaises(ValidationError):
                validate_graph([ss, first_revision(t), first_revision(f), dup])

    def test_wrong_source_revision_invalidates_gate(self):
        for sid, tid, fid, doi, s, t, f in self.cases:
            changed = copy.deepcopy(f)
            changed["revisions"][0]["data"]["source_ref"]["rev"] = 2
            with self.subTest(doi=doi), self.assertRaises(ValidationError):
                projection(s, t, changed)

    def test_historical_first_revision_not_overwritten_by_later_progress(self):
        for sid, tid, fid, doi, s, t, f in self.cases:
            future = copy.deepcopy(f)
            rev2 = copy.deepcopy(future["revisions"][0])
            rev2["rev"] = 2  # never asserted live
            future["revisions"].append(rev2)
            with self.subTest(doi=doi):
                self.assertIsNotNone(projection(s, t, future))

    def test_not_human_review_or_performed_reading(self):
        for sid, tid, fid, doi, s, t, f in self.cases:
            r = f["revisions"][0]
            with self.subTest(doi=doi):
                self.assertNotIn("human", r["actor"]["kind"])
                self.assertEqual([], r["data"]["review_refs"])
                self.assertEqual([], r["data"]["reading_refs"])
                self.assertIn("No ", r["data"]["access_limitation"])
                self.assertIn("2026-11-10", r["data"]["access_limitation"])

    def test_cross_pair_identity_collision_rejected(self):
        sid, tid, fid, doi, s, t, f = self.cases[0]
        wrong = copy.deepcopy(f)
        wrong["revisions"][0]["data"]["source_ref"] = {
            "id": self.cases[1][0], "rev": 1
        }
        with self.assertRaises(ValidationError):
            projection(s, t, wrong)


if __name__ == "__main__":
    unittest.main()
