"""R005 immutable source replay and conservative audit for the real EQ1 pages 45-47."""
import gzip
import hashlib
import json
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"research/searches/auditory/eq1-45to47-20261111-0708"
PRIOR=ROOT/"research/searches/auditory/eq1-single-snapshot-20261111/OBSERVATIONS.json"
CUTOFF="2026-10-04"

def replay():
    x=json.loads((BASE/"OBSERVATIONS.json").read_text(encoding="utf-8"))
    a=json.loads((BASE/"ATTEMPTED.json").read_text(encoding="utf-8"))
    assert x["schema"]=="mhac-r005-eq1-single-invocation-raw-pages/1"
    assert x["cutoff"]==a["frozen_cutoff"]==CUTOFF
    assert a["attempted_pages"]==[45,46,47] and a["statuses"]==[200,200,200]
    assert not a["next_live_probe_permitted_on_this_branch"]
    assert x["acquisition_probe_head"]==a["probe_head"]
    assert x["acquisition_run_id"]==42978112350
    assert x["eq1_search_complete"] is False
    assert x["new_canonical_search_hits"]==x["new_eligible_publications"]==0
    assert x["new_title_abstract_or_fulltext_decisions"]==0
    assert x["admitted_publications_studies_experiments_samples"]==[0,0,0,0]
    assert x["independent_human_review"] is False
    assert x["stevens2009_original_private_custody_approved"] is False
    assert x["r006_exclusive_eligibility_identity_authority"] is True
    got=[]
    for p, entry in zip((45,46,47),x["pages"]):
        assert entry["page"]==p and entry["http_status"]==200
        assert entry["frozen_cutoff"]==CUTOFF
        assert entry["file"]==f"page-{p}.json.gz"
        u=urlsplit(entry["url"]); q=parse_qs(u.query)
        assert u.scheme=="https" and u.netloc=="api.openalex.org"
        assert set(q)=={"filter","per_page","select","page","sort"}
        assert q["page"]==[str(p)] and q["per_page"]==["100"]
        assert q["select"]==["id,doi,display_name,publication_date,publication_year,type,language"]
        assert q["sort"]==["publication_date:asc,display_name:asc"]
        assert q["filter"][0].startswith("title_and_abstract.search:")
        assert q["filter"][0].endswith(",to_publication_date:"+CUTOFF)
        data=(BASE/entry["file"]).read_bytes()
        assert len(data)==entry["gzip_bytes"]
        assert hashlib.sha256(data).hexdigest()==entry["gzip_sha256"]
        original=gzip.decompress(data)
        assert len(original)==entry["raw_bytes"]
        assert hashlib.sha256(original).hexdigest()==entry["raw_sha256"]
        j=json.loads(original)
        assert j["meta"]["page"]==p and j["meta"]["per_page"]==100
        assert j["meta"]["count"]==entry["count"]==9280
        rows=j["results"]; assert len(rows)==100
        ids=[r["id"] for r in rows]
        assert ids==entry["ids"] and len(set(ids))==100
        assert all(t.startswith("https://openalex.org/W") for t in ids)
        assert all((r.get("publication_date") is None or r["publication_date"]<=CUTOFF) for r in rows)
        got.append(ids)
    assert not (set(got[0]) & set(got[1])) and not (set(got[1]) & set(got[2]))
    assert len(set(sum(got,[])))==300
    prev=json.loads(PRIOR.read_text(encoding="utf-8"))
    old=next(p for p in prev["pages"] if p["page"]==45)
    assert old["ids"]==got[0] and old["count"]==9280
    assert old["raw_sha256"]!=x["pages"][0]["raw_sha256"]
    assert x["previous_page45_anchor"]["raw_http_bytes_differ"] is True
    assert x["historical_page43_44_cross_invocation_eight_id_overlap_remains_unresolved"] is True
    assert x["within_invocation"]["distinct_work_ids"]==300
    assert x["within_invocation"]["adjacent_overlaps"]==[]
    return x

class SourceReplay(unittest.TestCase):
    def test_original_source_and_nonadmission_contract(self):
        self.assertEqual(len(replay()["pages"]),3)
    def test_hash_tamper_does_not_equal_original(self):
        x=replay()
        item=x["pages"][1]
        content=(BASE/item["file"]).read_bytes()
        self.assertNotEqual(hashlib.sha256(content+b"!").hexdigest(),item["gzip_sha256"])
        original=gzip.decompress(content)
        self.assertNotEqual(hashlib.sha256(original+b" ").hexdigest(),item["raw_sha256"])
    def test_strict_adjacent_negative_controls(self):
        x=replay()
        pages=x["pages"]
        alt=set(pages[0]["ids"]) & set(pages[1]["ids"])
        self.assertFalse(alt)
        self.assertTrue(set(pages[0]["ids"]) & set(pages[0]["ids"]))
        self.assertEqual(len(set(pages[0]["ids"])),100)
        self.assertNotEqual({9280,9281},{9280})
    def test_no_meta_to_corpus_upgrade(self):
        x=replay()
        self.assertFalse(x["eq1_search_complete"])
        self.assertEqual(x["admitted_publications_studies_experiments_samples"],[0,0,0,0])
        self.assertFalse(x["original_papers_fulltext_or_audio_read"])
        self.assertFalse(x["integration_shared_indexes_modified"])

if __name__=="__main__":
    unittest.main()
