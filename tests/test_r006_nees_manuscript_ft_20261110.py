"""R006 Nees original-author manuscript: fail-closed full-text decision preflight.

This exercises only R006's source/TA/FT graph projection. The repository-wide
history and generated aggregates remain Integration-owned validation.
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
SRC = "SRC-R006-NEES-2016-MEMORY"
TA = "SCR-R006-NEES-2016-MEMORY-TA"
FT = "SCR-R006-NEES-2016-MEMORY-FT"
PROTO = "MHAC-Track-E-frozen-v1-2026-10-13"


def load(folder, rid):
    return json.loads((ROOT / folder / (rid + ".json")).read_text(encoding="utf-8"))


def bounded_graph(source, ta, ft):
    """Remove only unrelated pinned R005 export basis from a test-local copy."""
    isolated_source = copy.deepcopy(source)
    isolated_source["revisions"][0]["basis"] = []
    return validate_graph([isolated_source, ta, ft])


class NeesManuscriptPreflightTests(unittest.TestCase):
    def setUp(self):
        self.source = load("research/registry/identity/records", SRC)
        self.ta = load("research/screening/records", TA)
        self.ft = load("research/screening/records", FT)

    def test_exact_publication_identity_and_frozen_track_e(self):
        for record in (self.source, self.ta, self.ft):
            validate_record(record, expected_kind="live")
        src = self.source["revisions"][0]["data"]
        self.assertEqual("Speech Auditory Alerts Promote Memory for Alerted Events in a Video-Simulated Self-Driving Car Ride", src["title"])
        self.assertIn(("doi", "10.1177/0018720816629279"),
                      [(x["scheme"], x["value"]) for x in src["identifiers"]
                       if x["status"] == "verified"])
        self.assertEqual("metadata_only", src["access_status"])
        self.assertEqual([], src["manifestations"])
        ta = self.ta["revisions"][0]["data"]
        ft = self.ft["revisions"][0]
        self.assertEqual("uncertain", ta["decision"])
        self.assertEqual({"id": SRC, "rev": 1}, ft["data"]["source_ref"])
        self.assertEqual([{"id": SRC, "rev": 1}, {"id": TA, "rev": 1}], ft["basis"])
        self.assertEqual("full_text", ft["data"]["stage"])
        self.assertEqual("empirical", ft["data"]["track"])
        self.assertEqual(PROTO, ft["data"]["protocol_version"])
        bounded_graph(self.source, self.ta, self.ft)

    def test_pending_does_not_become_admission_or_human_review(self):
        revision = self.ft["revisions"][0]
        self.assertEqual("agent", revision["actor"]["kind"])
        self.assertEqual("pending", revision["data"]["decision"])
        self.assertEqual([], revision["data"]["reading_refs"])
        self.assertEqual([], revision["data"]["review_refs"])
        graph = bounded_graph(self.source, self.ta, self.ft)
        coverage = screening_coverage(graph, source_ids=[SRC], protocol_version=PROTO)
        self.assertEqual(["pending"], [x["full_text"] for x in coverage["sources"]])
        self.assertEqual([], coverage["missing_required_full_text"])
        self.assertFalse(any(row["kind"] in ("study", "experiment", "sample")
                             for row in graph.records.values()))

    def test_no_fabricated_final_full_text_decision(self):
        for decision in ("include", "exclude"):
            altered = copy.deepcopy(self.ft)
            altered["revisions"][0]["data"]["decision"] = decision
            with self.subTest(decision=decision), self.assertRaises(ValidationError):
                bounded_graph(self.source, self.ta, altered)

    def test_full_text_requires_real_preceding_ta(self):
        changed = copy.deepcopy(self.ta)
        changed["revisions"][0]["data"]["decision"] = "exclude"
        with self.assertRaises(ValidationError):
            bounded_graph(self.source, changed, self.ft)

    def test_unauthorized_source_revision_fails_closed(self):
        changed = copy.deepcopy(self.ft)
        changed["revisions"][0]["data"]["source_ref"] = {"id": SRC, "rev": 2}
        with self.assertRaises(ValidationError):
            bounded_graph(self.source, self.ta, changed)

    def test_edition_access_and_single_sample_boundaries_explicit(self):
        text = " ".join(str(v) for v in self.ft["revisions"][0]["data"].values()).lower()
        for required in ("author manuscript", "submitted", "sha256", "not",
                         "one described experiment", "three arms", "90",
                         "85", "frozen", "10.1177/0018720816629279",
                         "not an http acquisition timestamp"):
            with self.subTest(required=required):
                self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
