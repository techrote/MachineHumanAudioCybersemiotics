"""Fail-closed first-revision identity tests for the two original-publisher TA decisions."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/screening/r006_next_ta2_20261110/verify.py"
spec = importlib.util.spec_from_file_location("r006_noise_urgency_ta", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class R006NextTASourcePin(unittest.TestCase):
    def setUp(self):
        self.records = {
            sid: copy.deepcopy(mod.read(mod.SCREENS / (sid + ".json")))
            for sid in mod.CASES
        }
        self.sources = {
            src: copy.deepcopy(mod.read(mod.SOURCES / (src + ".json")))
            for src, _, _ in mod.CASES.values()
        }

    def check(self):
        return mod.verify(self.records, self.sources)

    def test_real_original_doi_and_hit_pins(self):
        result = self.check()
        self.assertEqual(result["canonical_ta_files_authored"], 2)
        self.assertTrue(result["scientific_admission_not_assessed"])
        self.assertTrue(result["generated_exports_not_assessed"])

    def test_human_reviewer_fabrication_rejected(self):
        sid = next(iter(self.records))
        self.records[sid]["revisions"][0]["actor"]["kind"] = "human"
        with self.assertRaisesRegex(ValueError, "actor/time"):
            self.check()

    def test_historical_decision_time_rewriting_rejected(self):
        sid = next(iter(self.records))
        self.records[sid]["revisions"][0]["at"] = "2026-11-10T14:30:00Z"
        with self.assertRaisesRegex(ValueError, "actor/time"):
            self.check()

    def test_wrong_doi_identity_rejected(self):
        sid, (source, _, _) = next(iter(mod.CASES.items()))
        self.sources[source]["revisions"][0]["data"]["identifiers"][0]["value"] = "10.0000/wrong"
        with self.assertRaisesRegex(ValueError, "DOI or original discovery"):
            self.check()

    def test_fabricated_discovery_path_rejected(self):
        sid, (source, _, _) = next(iter(mod.CASES.items()))
        self.sources[source]["revisions"][0]["basis"].append({"id": "HIT-NONEXISTENT", "rev": 1})
        with self.assertRaisesRegex(ValueError, "DOI or original discovery"):
            self.check()

    def test_false_full_text_stage_rejected(self):
        sid = next(iter(self.records))
        self.records[sid]["revisions"][0]["data"]["stage"] = "full_text"
        with self.assertRaisesRegex(ValueError, "scope"):
            self.check()

    def test_fictitious_verification_rejected(self):
        sid = next(iter(self.records))
        self.records[sid]["revisions"][0]["data"]["review_refs"] = [{"id": "AID-FAKE", "rev": 1}]
        with self.assertRaisesRegex(ValueError, "scope"):
            self.check()

    def test_fictitious_reader_rejected(self):
        sid = next(iter(self.records))
        self.records[sid]["revisions"][0]["data"]["reading_refs"] = [{"id": "AID-FAKE", "rev": 1}]
        with self.assertRaisesRegex(ValueError, "scope"):
            self.check()

    def test_later_additive_revisions_do_not_break_historical_check(self):
        sid = next(iter(self.records))
        fake_later = copy.deepcopy(self.records[sid]["revisions"][0])
        fake_later["rev"] = 2
        fake_later["at"] = "2026-11-11T00:00:00Z"
        self.records[sid]["revisions"].append(fake_later)
        self.check()  # Never freezes future valid corpus transitions.


if __name__ == "__main__":
    unittest.main()
