"""R006 primary-PDF bounded FT preassessment: no false admission/identity."""
import copy
import json
from pathlib import Path
import unittest
from schemas import ValidationError
from schemas.v1 import validate_record
from tools.record_graph import validate_graph
from tools.screening import screening_coverage

ROOT=Path(__file__).resolve().parents[1]
PROTO="MHAC-Track-E-frozen-v1-2026-10-13"
CASES=(
 ("BECKER","SRC-REL-BECKER-2025","SCR-R006-REL-BECKER-2025-TA","SCR-R006-REL-BECKER-2025-FT","10.1145/3706066"),
 ("ROMEO","SRC-REL-ROMEO-2025","SCR-R006-REL-ROMEO-2025-TA","SCR-R006-REL-ROMEO-2025-FT","10.1145/3711938"),
)
def load(path):
 return json.loads((ROOT/path).read_text(encoding="utf-8"))
def source_path(sid):
 return "research/sources/related/records/"+sid+".json"
def scr_path(sid):
 return "research/screening/records/"+sid+".json"
def check_chain(src,ta,ft,doi):
 for item in (src,ta,ft):
  validate_record(item,expected_kind="live")
 s=src["revisions"][0]["data"]
 if not any(x["scheme"]=="doi" and x["status"]=="verified" and x["value"].casefold()==doi for x in s["identifiers"]):
  raise ValueError("verified DOI/identity changed")
 if s["manifestations"] or s["access_status"]!="abstract_only":
  raise ValueError("source manifestation/access changed: reassess evidence")
 t=ta["revisions"][0]["data"]; f=ft["revisions"][0]; d=f["data"]
 if t["source_ref"]!={"id":src["id"],"rev":1} or t["decision"] not in ("include","uncertain"):
  raise ValueError("title-abstract predecessor/identity changed")
 if f["basis"]!=[{"id":src["id"],"rev":1},{"id":ta["id"],"rev":1}] or f["actor"]["kind"]!="agent":
  raise ValueError("actor/basis provenance changed")
 if d["source_ref"]!={"id":src["id"],"rev":1} or d["stage"]!="full_text" or d["track"]!="empirical" or d["protocol_version"]!=PROTO:
  raise ValueError("scope/version changed")
 if d["decision"]!="pending" or d["reading_refs"] or d["review_refs"]:
  raise ValueError("false admission/reviewer/reading evidence")
 if doi not in (d["reason"]+" "+d["access_limitation"]).casefold():
  raise ValueError("original DOI missing in provenance")
 return validate_graph([src,ta,ft])

class PrimaryPdfPendingTests(unittest.TestCase):
 def setUp(self):
  self.cases=[(c,[load(source_path(c[1])),load(scr_path(c[2])),load(scr_path(c[3]))]) for c in CASES]
 def test_schema_and_stage_chain_each_source(self):
  for c,(s,t,f) in self.cases:
   with self.subTest(c=c[0]): self.assertIsNotNone(check_chain(s,t,f,c[4]))
 def test_current_coverage_pending_not_included(self):
  records=[item for _,triplet in self.cases for item in triplet]
  graph=validate_graph(records)
  coverage=screening_coverage(graph,source_ids=[c[1] for c in CASES],protocol_version=PROTO)
  self.assertEqual([],coverage["missing_required_full_text"])
  self.assertEqual([],coverage["awaiting_text"])
  self.assertEqual(["pending","pending"],[x["full_text"] for x in coverage["sources"]])
  self.assertFalse(any(x["kind"] in ("study","experiment","sample") for x in graph.records.values()))
 def test_cannot_promote_to_include_without_reader(self):
  for c,(s,t,f) in self.cases:
   fake=copy.deepcopy(f);fake["revisions"][0]["data"]["decision"]="include"
   with self.assertRaises(ValidationError):validate_graph([s,t,fake])
 def test_cannot_promote_to_exclude_without_reader(self):
  for c,(s,t,f) in self.cases:
   fake=copy.deepcopy(f);fake["revisions"][0]["data"]["decision"]="exclude"
   with self.assertRaises(ValidationError):validate_graph([s,t,fake])
 def test_ta_exclusion_invalidates_ft(self):
  for c,(s,t,f) in self.cases:
   bad=copy.deepcopy(t);bad["revisions"][0]["data"]["decision"]="exclude"
   with self.assertRaises(ValidationError):validate_graph([s,bad,f])
 def test_source_correction_requires_reassessment(self):
  for c,(s,t,f) in self.cases:
   bad=copy.deepcopy(s);bad["revisions"][0]["data"]["manifestations"]=[{"id":"fake","sha256":"0"*64,"extent":1,"coordinate":"file_page_1based"}]
   with self.assertRaisesRegex(ValueError,"reassess"):check_chain(bad,t,f,c[4])
 def test_false_human_assessor_rejected(self):
  for c,(s,t,f) in self.cases:
   bad=copy.deepcopy(f);bad["revisions"][0]["actor"]["kind"]="human"
   with self.assertRaisesRegex(ValueError,"actor"):check_chain(s,t,bad,c[4])
 def test_false_reading_reference_rejected(self):
  for c,(s,t,f) in self.cases:
   bad=copy.deepcopy(f);bad["revisions"][0]["data"]["reading_refs"]=[{"id":"AID-FAKE","rev":1}]
   with self.assertRaisesRegex(ValueError,"reading"):check_chain(s,t,bad,c[4])
 def test_distinct_publications_not_duplicate_doi(self):
  self.assertNotEqual(CASES[0][-1],CASES[1][-1])
  self.assertNotEqual(CASES[0][1],CASES[1][1])
 def test_read_scope_is_not_full_item_claim(self):
  for c,(s,t,f) in self.cases:
   note=f["revisions"][0]["data"]["access_limitation"].casefold()
   self.assertIn("not",note)
   self.assertIn("no current",note) if c[0]=="ROMEO" else self.assertIn("no local",note)
if __name__=="__main__":unittest.main()
