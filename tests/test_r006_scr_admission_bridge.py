"""Negative tests for R006 admission candidates, not independent source review."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

from schemas import ValidationError
from schemas.v1 import validate_record
from tools.evidence_flow import evidence_flow
from tools.record_graph import validate_graph

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research/screening/r006_scr_admission_bridge_20261110/build_candidates.py"
spec = importlib.util.spec_from_file_location("r006_scr_admission_candidates", PATH)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
AT = "2026-11-10T08:00:00Z"  # TEST-ONLY time, never committed into live records
ACTOR = "test-agent-only-never-a-human-reviewer"


class SCRAdmissionBridgeTests(unittest.TestCase):
    def setUp(self):
        self.first = json.loads(bridge.FIRST.read_text(encoding="utf-8"))
        self.second = json.loads(bridge.SECOND.read_text(encoding="utf-8"))
        self.sources = {
            sid: json.loads((bridge.SOURCE_DIR / (sid + ".json")).read_text(encoding="utf-8"))
            for sid in bridge.DOIS
        }

    def render(self):
        return bridge.candidates(at=AT, actor_id=ACTOR, first=self.first,
                                 second=self.second, sources=self.sources)

    def test_four_schema_valid_ta_only_records(self):
        data = self.render()
        self.assertEqual(len(data), 4)
        self.assertEqual(len(set(data)), 4)
        self.assertEqual({r["revisions"][0]["data"]["decision"] for r in data.values()},
                         {"include", "uncertain"})
        for key, record in data.items():
            self.assertEqual(key, record["id"])
            self.assertEqual(record["kind"], "screening")
            self.assertEqual(record["issue"], 6)
            self.assertFalse(record["synthetic"])
            self.assertEqual(len(record["revisions"]), 1)
            rev = record["revisions"][0]
            self.assertEqual(rev["actor"]["kind"], "agent")
            self.assertEqual(rev["data"]["stage"], "title_abstract")
            self.assertEqual(rev["data"]["track"], "empirical")
            self.assertEqual(rev["data"]["reading_refs"], [])
            self.assertEqual(rev["data"]["review_refs"], [])
            validate_record(record, expected_kind="live")
        self.assertEqual(sorted(x["revisions"][0]["data"]["decision"] for x in data.values()),
                         ["include", "include", "uncertain", "uncertain"])

    def test_subset_graph_is_consistent_but_not_an_accepted_corpus(self):
        data = self.render()
        graph = validate_graph([*self.sources.values(), *data.values()])
        flow = evidence_flow(graph)
        self.assertEqual(flow["included_publications"], 0)
        self.assertEqual(flow["included_studies"], 0)
        self.assertEqual(flow["screening"]["title_abstract"]["include"], 2)
        self.assertEqual(flow["screening"]["title_abstract"]["uncertain"], 2)

    def test_decisions_cannot_be_mutated_to_full_text(self):
        self.first["decisions"][0]["stage"] = "full_text"
        with self.assertRaisesRegex(ValueError, "title/abstract"):
            self.render()

    def test_unresolved_e2_cannot_be_silently_admitted(self):
        row = next(r for r in self.first["decisions"] if r["source_ref"]["id"] == "SRC-REL-ROMEO-2023")
        row["decision"] = "include"
        with self.assertRaises(ValueError):
            self.render()

    def test_authority_cannot_be_upgraded_to_human(self):
        self.first["actor"]["kind"] = "human"
        with self.assertRaises(ValueError):
            self.render()
        self.first["actor"]["kind"] = "agent"
        self.assertEqual(self.render()[next(iter(self.render()))]["revisions"][0]["actor"]["kind"],
                         "agent")

    def test_fake_source_identity_or_doi_is_rejected(self):
        self.first["decisions"][0]["doi"] = "10.1145/invalid"
        with self.assertRaises(ValueError):
            self.render()
        self.first = json.loads(bridge.FIRST.read_text(encoding="utf-8"))
        self.sources["SRC-REL-ROMEO-2025"]["revisions"][0]["data"]["identifiers"][0]["value"] = "10.1145/no"
        with self.assertRaisesRegex(ValueError, "DOI"):
            self.render()

    def test_missing_or_duplicate_publication_rejected(self):
        self.first["decisions"].append(copy.deepcopy(self.first["decisions"][0]))
        with self.assertRaises(ValueError):
            self.render()
        self.first["decisions"].pop()
        self.first["decisions"].pop()
        with self.assertRaises(ValueError):
            self.render()

    def test_fake_fulltext_or_independent_sample_count_rejected(self):
        self.second["counts"]["independent_samples_counted"] = 1
        with self.assertRaises(ValueError):
            self.render()
        self.second = json.loads(bridge.SECOND.read_text(encoding="utf-8"))
        self.first["decisions"][0]["evidence"][0]["local_bytes_verified"] = True
        with self.assertRaises(ValueError):
            self.render()

    def test_wrong_protocol_cutoff_rejected(self):
        self.first["evidence_cutoff"] = "2026-11-10"
        with self.assertRaisesRegex(ValueError, "cutoff"):
            self.render()

    def test_invalid_registration_time_cannot_pass_closed_schema(self):
        with self.assertRaises(ValidationError):
            bridge.candidates(at="yesterday", actor_id=ACTOR, first=self.first,
                              second=self.second, sources=self.sources)

    def test_generated_id_source_and_revision_pinned(self):
        data = self.render()
        for sid in bridge.DOIS:
            rid = "SCR-R006-" + sid.removeprefix("SRC-") + "-TA"
            self.assertEqual(data[rid]["revisions"][0]["data"]["source_ref"],
                             {"id": sid, "rev": 1})
            self.assertEqual(data[rid]["revisions"][0]["basis"], [{"id": sid, "rev": 1}])

    def test_absent_noncanonical_ledger_is_not_implicitly_registered(self):
        state = json.loads((ROOT / "research/registry/state.json").read_text(encoding="utf-8"))
        roots = state["record_roots"]
        self.assertNotIn("research/screening/r006_scr_admission_bridge_20261110", roots)
        self.assertNotIn("research/screening/r006_scr_admission_bridge_20261110/candidates", roots)


if __name__ == "__main__":
    unittest.main()
