"""Historical Romeo 2023 first FT access checkpoint; in-memory negative tests.

The 09:28 UTC revision genuinely lacked the Zenodo PDF. Later source receipt
corrections must append revisions, not erase that earlier truth or permanently
freeze the publication at awaiting_text. No original IEEE report/human review
is claimed. A local pass does not replace live manifest/export validation.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from schemas.v1 import validate_record
from tools.record_graph import validate_graph
from tools.screening import screening_coverage
from schemas import ValidationError

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "research/sources/related/records/SRC-REL-ROMEO-2023.json"
TA = ROOT / "research/screening/records/SCR-R006-REL-ROMEO-2023-TA.json"
FT = ROOT / "research/screening/records/SCR-R006-REL-ROMEO-2023-FT.json"
DOI = "10.1109/ro-man57019.2023.10309631"
PROTOCOL = "MHAC-Track-E-frozen-v1-2026-10-13"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(source, ta, ft):
    """Check immutable initial revision against the original historical state.

    Later legitimate source and FT revisions are not invalidated by this
    historical test. Live/latest screening is governed by the graph validator
    and newer R006 issue-scoped tests, never by dated baseline zero-counts.
    """
    source, ta, ft = copy.deepcopy(source), copy.deepcopy(ta), copy.deepcopy(ft)
    for original in (source, ta, ft):
        original["revisions"] = original["revisions"][:1]
    if (source["id"] != "SRC-REL-ROMEO-2023"
            or source["kind"] != "source"
            or source["synthetic"] is not False
            or len(source["revisions"]) != 1):
        raise ValueError("Source identity or revision changed: reassess disposition")
    sd = source["revisions"][0]["data"]
    dois = {x["value"].casefold() for x in sd["identifiers"]
            if x["scheme"] == "doi" and x["status"] == "verified"}
    if (DOI not in dois or sd["validity"] != "active"
            or sd["access_status"] != "metadata_only" or sd["manifestations"]):
        raise ValueError("Full-text access/DOI/manifestation changed: reassess")
    if (ta["id"] != "SCR-R006-REL-ROMEO-2023-TA"
            or len(ta["revisions"]) != 1
            or ta["revisions"][0]["data"]["decision"] != "uncertain"
            or ta["revisions"][0]["data"]["source_ref"] != {"id": source["id"], "rev": 1}):
        raise ValueError("Canonical title/abstract predecessor changed")
    if ft["id"] != "SCR-R006-REL-ROMEO-2023-FT" or len(ft["revisions"]) != 1:
        raise ValueError("FT identity/history changed")
    rev = ft["revisions"][0]
    data = rev["data"]
    if (rev["actor"]["kind"] != "agent"
            or rev["actor"]["id"] != "gpt6-r006-romeo2023-ft-access-registrar-20261110"
            or rev["basis"] != [{"id": source["id"], "rev": 1}, {"id": ta["id"], "rev": 1}]
            or data["source_ref"] != {"id": source["id"], "rev": 1}
            or data["track"] != "empirical" or data["stage"] != "full_text"
            or data["protocol_version"] != PROTOCOL
            or data["decision"] != "awaiting_text"
            or data["reading_refs"] or data["review_refs"]):
        raise ValueError("FT stage, provenance or actor falsely promoted")
    for needle in (DOI, "Zenodo", "timeout", "2025", "not"):
        if needle.casefold() not in (data["reason"] + " " + data["access_limitation"]).casefold():
            raise ValueError("Access, identity and limitation provenance incomplete")
    for record in (source, ta, ft):
        validate_record(record, expected_kind="live")
    graph = validate_graph([source, ta, ft])
    c = screening_coverage(graph, source_ids=[source["id"]],
                           protocol_version=PROTOCOL, track="empirical")
    if (c["missing_required_full_text"] or c["awaiting_text"] != [source["id"]]
            or c["sources"][0]["title_abstract"] != "uncertain"
            or c["sources"][0]["full_text"] != "awaiting_text"):
        raise ValueError("Source unresolved gate omitted or misclassified")
    return graph


class Romeo2023AwaitingTextTests(unittest.TestCase):
    def setUp(self):
        self.s, self.ta, self.ft = load(SRC), load(TA), load(FT)

    def test_exact_canonical_live_checkpoint_schema_and_graph(self):
        self.assertIsNotNone(check(self.s, self.ta, self.ft))

    def test_not_a_new_study_or_independent_sample(self):
        graph = check(self.s, self.ta, self.ft)
        self.assertFalse(any(x["kind"] in {"study", "experiment", "sample"} for x in graph.records.values()))

    def test_source_change_requires_reassessment(self):
        self.s["revisions"][0]["data"]["access_status"] = "full_text_available"
        with self.assertRaisesRegex(ValueError, "reassess"):
            check(self.s, self.ta, self.ft)

    def test_source_manifestation_change_requires_reassessment(self):
        self.s["revisions"][0]["data"]["manifestations"].append({"id": "invented"})
        with self.assertRaisesRegex(ValueError, "reassess"):
            check(self.s, self.ta, self.ft)

    def test_later_source_revision_does_not_rewrite_historical_gate(self):
        self.s["revisions"].append(copy.deepcopy(self.s["revisions"][0]))
        self.s["revisions"][-1]["rev"] = 2  # isolated snapshot, not a live revision
        self.assertIsNotNone(check(self.s, self.ta, self.ft))

    def test_original_historical_source_revision_cannot_be_rewritten(self):
        self.s["revisions"][0]["data"]["access_status"] = "full_text_available"
        with self.assertRaisesRegex(ValueError, "reassess"):
            check(self.s, self.ta, self.ft)

    def test_wrong_doi_is_not_same_publication(self):
        self.s["revisions"][0]["data"]["identifiers"][0]["value"] = "10.1145/3711938"
        with self.assertRaisesRegex(ValueError, "DOI"):
            check(self.s, self.ta, self.ft)

    def test_no_human_reviewer_impersonation(self):
        self.ft["revisions"][0]["actor"]["kind"] = "human"
        with self.assertRaisesRegex(ValueError, "actor"):
            check(self.s, self.ta, self.ft)

    def test_no_fake_fulltext_reading(self):
        self.ft["revisions"][0]["data"]["reading_refs"] = [{"id": "AID-FAKE", "rev": 1}]
        with self.assertRaisesRegex(ValueError, "provenance"):
            check(self.s, self.ta, self.ft)

    def test_no_silent_fulltext_include_or_exclude(self):
        for verdict in ("include", "exclude"):
            changed = copy.deepcopy(self.ft)
            changed["revisions"][0]["data"]["decision"] = verdict
            with self.assertRaisesRegex(ValueError, "provenance"):
                check(self.s, self.ta, changed)
            with self.assertRaises(ValidationError):
                validate_graph([self.s, self.ta, changed])

    def test_ta_reclassification_invalidates_fulltext_gate(self):
        self.ta["revisions"][0]["data"]["decision"] = "exclude"
        with self.assertRaisesRegex(ValueError, "predecessor"):
            check(self.s, self.ta, self.ft)
        with self.assertRaises(ValidationError):
            validate_graph([self.s, self.ta, self.ft])

    def test_duplicate_unsuperseded_ft_rejected(self):
        duplicate = copy.deepcopy(self.ft)
        duplicate["id"] = "SCR-R006-REL-ROMEO-2023-FT-DUPLICATE"
        with self.assertRaises(ValidationError):
            validate_graph([self.s, self.ta, self.ft, duplicate])

    def test_live_record_not_synthetic_fixture(self):
        self.ft["synthetic"] = True
        with self.assertRaises(ValidationError):
            validate_record(self.ft, expected_kind="live")


if __name__ == "__main__":
    unittest.main()
