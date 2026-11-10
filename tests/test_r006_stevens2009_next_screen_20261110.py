"""R006: Stevens 2009 source-pinned next empirical screening; no FT admission."""
import copy
import json
from pathlib import Path
import unittest
from schemas.v1 import validate_record
from schemas import ValidationError
from tools.record_graph import validate_graph

ROOT = Path(__file__).resolve().parents[1]
SRC_ID = "SRC-R006-E-STEVENS-INFORMATIVE"
TA_ID = "SCR-R006-STEVENS-2009-WARNING-TA"
FT_ID = "SCR-R006-STEVENS-2009-WARNING-FT"
DOI = "10.2478/v10053-008-0064-6"
PROTO = "MHAC-Track-E-frozen-v1-2026-10-13"
R005_RECEIPT_SHA = "1390d7a4def94ad6b0926a5f1ae2608999f31713fb3ee5dad20b9e3fcc52658b"

def load(folder, name):
    return json.loads((ROOT / folder / (name + ".json")).read_text(encoding="utf-8"))

def project(src, ta, ft):
    src, ta, ft = (copy.deepcopy(x) for x in (src, ta, ft))
    # External R005 HIT and AID bases are checked by the canonical validator.
    # Omit only from isolated graph test; never rewrite the repository source.
    src["revisions"][0]["basis"] = []
    return validate_graph([src, ta, ft])

class Stevens2009NextScreen(unittest.TestCase):
    def setUp(self):
        self.src = load("research/registry/identity/records", SRC_ID)
        self.ta = load("research/screening/records", TA_ID)
        self.ft = load("research/screening/records", FT_ID)

    def test_live_schema_and_graph(self):
        for r in (self.src, self.ta, self.ft):
            validate_record(r, expected_kind="live")
        self.assertIsNotNone(project(self.src, self.ta, self.ft))

    def test_verified_doi_and_existing_hit_only(self):
        base = self.src["revisions"][0]
        self.assertIn(DOI, {x["value"].lower() for x in base["data"]["identifiers"]
                           if x["scheme"] == "doi" and x["status"] == "verified"})
        self.assertIn({"id": "HIT-R005R-C1LOAD-EQ1-02138", "rev": 1}, base["basis"])
        self.assertEqual([], base["data"]["manifestations"])
        self.assertEqual("metadata_only", base["data"]["access_status"])

    def test_no_human_or_imaginary_reading(self):
        for item in (self.ta, self.ft):
            rev = item["revisions"][0]
            self.assertEqual("agent", rev["actor"]["kind"])
            self.assertEqual("2026-11-10T20:28:14Z", rev["at"])
            self.assertEqual([], rev["data"]["reading_refs"])
            self.assertEqual([], rev["data"]["review_refs"])
            self.assertEqual("empirical", rev["data"]["track"])
            self.assertEqual(PROTO, rev["data"]["protocol_version"])
            self.assertIn(DOI, rev["data"]["access_limitation"])

    def test_stage_and_r005_provenance_boundary(self):
        self.assertEqual("include", self.ta["revisions"][0]["data"]["decision"])
        self.assertEqual("title_abstract", self.ta["revisions"][0]["data"]["stage"])
        self.assertEqual("pending", self.ft["revisions"][0]["data"]["decision"])
        self.assertEqual("full_text", self.ft["revisions"][0]["data"]["stage"])
        self.assertEqual([{"id": SRC_ID, "rev": 1}, {"id": TA_ID, "rev": 1}],
                         self.ft["revisions"][0]["basis"])
        for r in (self.ta, self.ft):
            self.assertIn(R005_RECEIPT_SHA, r["revisions"][0]["data"]["access_limitation"])

    def test_forbidden_ft_inclusion_without_performed_reading(self):
        for decision in ("include", "exclude"):
            ft = copy.deepcopy(self.ft)
            ft["revisions"][0]["data"]["decision"] = decision
            with self.subTest(decision=decision), self.assertRaises(ValidationError):
                project(self.src, self.ta, ft)

    def test_invalidated_ta_parent_rejected(self):
        ta = copy.deepcopy(self.ta)
        ta["revisions"][0]["data"]["decision"] = "exclude"
        with self.assertRaises(ValidationError):
            project(self.src, ta, self.ft)

    def test_cross_publication_identity_swap_rejected(self):
        ft = copy.deepcopy(self.ft)
        ft["revisions"][0]["data"]["source_ref"] = {"id": "SRC-REL-BECKER-2025", "rev": 1}
        with self.assertRaises(ValidationError):
            project(self.src, self.ta, ft)

    def test_wrong_source_revision_rejected(self):
        ft = copy.deepcopy(self.ft)
        ft["revisions"][0]["data"]["source_ref"]["rev"] = 2
        with self.assertRaises(ValidationError):
            project(self.src, self.ta, ft)

    def test_double_fulltext_without_supersession_rejected(self):
        dup = copy.deepcopy(self.ft)
        dup["id"] = "SCR-R006-STEVENS-2009-WARNING-FT-DUPLICATE"
        with self.assertRaises(ValidationError):
            src, ta, ft = (copy.deepcopy(x) for x in (self.src, self.ta, self.ft))
            src["revisions"][0]["basis"] = []
            validate_graph([src, ta, ft, dup])

if __name__ == "__main__":
    unittest.main()
