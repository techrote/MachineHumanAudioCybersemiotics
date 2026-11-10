"""Prepared R006 next-pair assertions: identity and forbidden scientific count transitions."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"research/screening/r006_next_ta_20261110/check.py"
spec=importlib.util.spec_from_file_location("r006_next_ta", FILE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class NextTAQualification(unittest.TestCase):
    def setUp(self):
        self.packet=copy.deepcopy(mod.load(mod.PACKET))
    def check(self):
        return mod.verify(self.packet)
    def test_prepared_not_admitted(self):
        result=self.check()
        self.assertEqual(result["prepared_only"],2)
        self.assertEqual(result["admitted"],0)
    def test_source_doi_collision_rejected(self):
        self.packet["cases"][1]["doi"]=self.packet["cases"][0]["doi"]
        with self.assertRaisesRegex(ValueError,"identity conflict"):self.check()
    def test_verified_doi_pin_required(self):
        self.packet["cases"][0]["doi"]="10.0000/fake"
        with self.assertRaisesRegex(ValueError,"DOI mismatch"):self.check()
    def test_discovery_hit_fabrication_rejected(self):
        self.packet["cases"][0]["source_discovery_hit_ids"].append("HIT-FAKE")
        with self.assertRaisesRegex(ValueError,"discovery path"):self.check()
    def test_fictitious_full_text_rejected(self):
        self.packet["cases"][1]["original_fulltext_obtained"]=True
        with self.assertRaisesRegex(ValueError,"Unverified"):self.check()
    def test_human_reviewer_spoof_rejected(self):
        self.packet["decision_actor"]["kind"]="human"
        with self.assertRaisesRegex(ValueError,"actor"):self.check()
    def test_sample_counts_are_not_screening_evidence(self):
        self.packet["added_samples"]=1
        with self.assertRaisesRegex(ValueError,"count"):self.check()
    def test_cutoff_cannot_shift(self):
        self.packet["search_cutoff"]="2026-11-10"
        with self.assertRaisesRegex(ValueError,"cutoff"):self.check()
    def test_stale_source_title_rejected(self):
        self.packet["cases"][0]["title"]="A totally different article"
        with self.assertRaisesRegex(ValueError,"title/DOI"):self.check()

if __name__=="__main__":unittest.main()
