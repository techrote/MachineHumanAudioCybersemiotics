"""R006 Šabić original publisher HTML: pending is not an eligibility/sample admission."""
import copy
import json
from pathlib import Path
import unittest

from schemas.v1 import validate_record
from schemas import ValidationError
from tools.record_graph import validate_graph
from tools.screening import screening_coverage

ROOT = Path(__file__).resolve().parents[1]
SRC = "SRC-R006-H-SABIC-UNDERSTANDING"
TA = "SCR-R006-SABIC-2021-NOISE-TA"
FT = "SCR-R006-SABIC-2021-NOISE-FT"
PROTO = "MHAC-Track-E-frozen-v1-2026-10-13"

def load(folder, rid):
    return json.loads((ROOT / folder / (rid + ".json")).read_text(encoding="utf-8"))

def isolated_stage_graph(source, ta, ft):
    """Project a bounded stage graph without separate R005 discovery/AID nodes.

    This affects only the test's in-memory copy, never the canonical source.
    Whole-history validation remains the Integration-owned task.
    """
    local_source = copy.deepcopy(source)
    local_source["revisions"][0]["basis"] = []
    return validate_graph([local_source, ta, ft])


class SabicPublisherHtmlPendingTests(unittest.TestCase):
    def setUp(self):
        self.source=load("research/registry/identity/records", SRC)
        self.ta=load("research/screening/records", TA)
        self.ft=load("research/screening/records", FT)

    def test_exact_doi_publication_and_predecessor(self):
        for record in (self.source,self.ta,self.ft):
            validate_record(record,expected_kind="live")
        d=self.source["revisions"][0]["data"]
        self.assertIn(("doi","10.1177/0018720819879311"),[(x["scheme"],x["value"]) for x in d["identifiers"] if x["status"]=="verified"])
        self.assertEqual("metadata_only",d["access_status"])
        self.assertEqual([],d["manifestations"])
        f=self.ft["revisions"][0]
        self.assertEqual([{"id":SRC,"rev":1},{"id":TA,"rev":1}],f["basis"])
        self.assertEqual({"id":SRC,"rev":1},f["data"]["source_ref"])
        self.assertEqual("include",self.ta["revisions"][0]["data"]["decision"])
        self.assertEqual(PROTO,f["data"]["protocol_version"])
        self.assertEqual("agent",f["actor"]["kind"])
        self.assertEqual("full_text",f["data"]["stage"])
        self.assertEqual("empirical",f["data"]["track"])
        isolated_stage_graph(self.source,self.ta,self.ft)

    def test_pending_not_admitted_or_human_verified(self):
        d=self.ft["revisions"][0]["data"]
        self.assertEqual("pending",d["decision"])
        self.assertEqual([],d["reading_refs"])
        self.assertEqual([],d["review_refs"])
        graph=isolated_stage_graph(self.source,self.ta,self.ft)
        c=screening_coverage(graph,source_ids=[SRC],protocol_version=PROTO)
        self.assertEqual(["pending"],[x["full_text"] for x in c["sources"]])
        self.assertEqual([],c["missing_required_full_text"])
        self.assertFalse(any(x["kind"] in ("study","experiment","sample") for x in graph.records.values()))

    def test_cannot_infer_inclusion_or_exclusion_from_unhashed_web_view(self):
        for decision in ("include","exclude"):
            altered=copy.deepcopy(self.ft)
            altered["revisions"][0]["data"]["decision"]=decision
            with self.assertRaises(ValidationError):
                isolated_stage_graph(self.source,self.ta,altered)

    def test_source_correction_and_ta_exclusion_fail_closed(self):
        altered_ta=copy.deepcopy(self.ta)
        altered_ta["revisions"][0]["data"]["decision"]="exclude"
        with self.assertRaises(ValidationError):
            isolated_stage_graph(self.source,altered_ta,self.ft)
        altered_ft=copy.deepcopy(self.ft)
        altered_ft["revisions"][0]["data"]["source_ref"]={"id":SRC,"rev":2}
        with self.assertRaises(ValidationError):
            isolated_stage_graph(self.source,self.ta,altered_ft)

    def test_original_source_boundary_is_explicit(self):
        d=self.ft["revisions"][0]["data"]
        for phrase in ("doi/10.1177/0018720819879311","new participants","raw HTML","not"):
            self.assertIn(phrase.lower(),(d["reason"]+" "+d["access_limitation"]).lower())

if __name__=="__main__":
    unittest.main()
