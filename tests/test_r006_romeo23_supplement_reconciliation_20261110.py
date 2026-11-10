"""R006 append-only correction of Romeo 2023 supplement access.

The genuine R005 public Zenodo receipt must NOT become a fictitious IEEE
full-text reading, new study/sample, human reviewer, or source revision.
This test audits historical revision 2; later legitimate admissions remain
possible through appended source-pinned decisions.
"""
from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path
import unittest

from schemas.v1 import validate_record
from tools.record_graph import validate_graph

ROOT = Path(__file__).resolve().parents[1]
FT = ROOT / "research/screening/records/SCR-R006-REL-ROMEO-2023-FT.json"
TA = ROOT / "research/screening/records/SCR-R006-REL-ROMEO-2023-TA.json"
SRC = ROOT / "research/sources/related/records/SRC-REL-ROMEO-2023.json"
R005 = ROOT / "research/sources/auditory/r006-romeo23-zenodo-script-reading-2026-11-10/OBSERVATIONS.json"
SHA = "53be4375261a22965392f25151ba004392418727a378df42a253d4c22e969aea"
MD5 = "7137b64efa2e75ab9aec951ca03449fe"
IEEE_DOI = "10.1109/ro-man57019.2023.10309631"
SUPPLEMENT_DOI = "10.5281/zenodo.8042317"
ACTOR = "gpt6-r006-screening-supplement-reconciliation-20261110"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def receipt_check(ft, observed):
    """Check immutable second revision; do not constrain future later revisions."""
    revs = ft["revisions"]
    if len(revs) < 2 or revs[0]["rev"] != 1 or revs[1]["rev"] != 2:
        raise ValueError("Missing canonical append-only access revision")
    original, correction = revs[:2]
    if (original["at"] != "2026-11-10T09:28:27Z"
            or original["actor"]["kind"] != "agent"
            or "timeout" not in original["data"]["access_limitation"]):
        raise ValueError("Historical failed download was silently rewritten")
    if (correction["actor"]["kind"] != "agent"
            or correction["actor"]["id"] != ACTOR
            or correction["at"] != "2026-11-10T13:38:30Z"
            or correction["data"]["stage"] != "full_text"
            or correction["data"]["track"] != "empirical"
            or correction["data"]["decision"] != "awaiting_text"
            or correction["data"]["source_ref"] != {"id": "SRC-REL-ROMEO-2023", "rev": 1}
            or correction["data"]["reading_refs"]
            or correction["data"]["review_refs"]):
        raise ValueError("Supplement impersonated a full-text admission or human reader")
    if (IEEE_DOI not in correction["data"]["reason"].lower()
            or SUPPLEMENT_DOI not in correction["data"]["reason"]
            or SHA not in correction["data"]["access_limitation"]
            or MD5 not in correction["data"]["access_limitation"]):
        raise ValueError("Parent/supplement identity or source receipt is missing")
    rec = observed["receipt"]
    src = observed["source"]
    if (src["publication_doi"].lower() != IEEE_DOI
            or src["supplement_version_doi"] != SUPPLEMENT_DOI
            or rec["http_status"] != 200
            or rec["byte_count"] != 103320
            or observed["parser"]["pdf_page_count"] != 4
            or rec["received_md5"] != MD5
            or rec["received_sha256"] != SHA
            or rec["source_bytes_deposited_to_repo"] is not False
            or observed["not_claimed"]["complete_ieee_paper_read"] is not False
            or observed["not_claimed"]["human_screen_or_review"] is not False):
        raise ValueError("Receipt was rewritten or conflated with original IEEE report")
    if datetime.fromisoformat(rec["completed_utc"]) >= datetime.fromisoformat(correction["at"].replace("Z","+00:00")):
        raise ValueError("Correction predates original R005 source acquisition")
    return correction


class Romeo2023ReceiptRevisionTests(unittest.TestCase):
    def setUp(self):
        self.src, self.ta, self.ft, self.observed = map(load, (SRC, TA, FT, R005))

    def test_real_receipt_reconciles_with_append_only_canonical_access(self):
        self.assertEqual(receipt_check(self.ft, self.observed)["data"]["decision"], "awaiting_text")

    def test_live_schema_and_graph_still_validate(self):
        for record in (self.src, self.ta, self.ft):
            validate_record(record, expected_kind="live")
        self.assertIsNotNone(validate_graph([self.src, self.ta, self.ft]))

    def test_first_failed_access_observation_not_erased(self):
        self.assertIn("download timed out", self.ft["revisions"][0]["data"]["reason"])
        self.assertIn("subsequently", self.ft["revisions"][1]["data"]["reason"])

    def test_no_publication_experiment_sample_admission_or_audio_qualification(self):
        self.assertFalse(any(item["kind"] in {"study","experiment","sample"} for item in (self.src,self.ta,self.ft)))
        self.assertFalse(self.observed["not_claimed"]["audio_video_playback"])
        self.assertFalse(self.observed["not_claimed"]["study_or_sample_independence"])

    def test_changed_supplement_checksum_fails_qualification(self):
        x = copy.deepcopy(self.observed)
        x["receipt"]["received_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError,"Receipt"):
            receipt_check(self.ft, x)

    def test_false_human_actor_fails_qualification(self):
        x = copy.deepcopy(self.ft)
        x["revisions"][1]["actor"]["kind"] = "human"
        with self.assertRaisesRegex(ValueError, "Supplement impersonated"):
            receipt_check(x, self.observed)

    def test_improper_fulltext_include_fails_qualification(self):
        x = copy.deepcopy(self.ft)
        x["revisions"][1]["data"]["decision"] = "include"
        with self.assertRaisesRegex(ValueError, "Supplement impersonated"):
            receipt_check(x, self.observed)

    def test_2025_paper_substitution_fails_qualification(self):
        x = copy.deepcopy(self.ft)
        x["revisions"][1]["data"]["source_ref"]["id"] = "SRC-REL-ROMEO-2025"
        with self.assertRaisesRegex(ValueError,"Supplement impersonated"):
            receipt_check(x, self.observed)

    def test_future_legal_revision_is_not_blocked_by_historical_receipt_test(self):
        x = copy.deepcopy(self.ft)
        future = copy.deepcopy(x["revisions"][1])
        future["rev"] = 3
        future["at"] = "2026-11-11T10:00:00Z"
        x["revisions"].append(future)  # only checks historical revision 2, not prospective validity
        self.assertEqual(receipt_check(x, self.observed)["rev"], 2)


if __name__ == "__main__":
    unittest.main()
