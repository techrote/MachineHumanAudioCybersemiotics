"""Synthetic regressions for historical identity and TA prerequisite currency."""
from __future__ import annotations

from copy import deepcopy
import unittest

from schemas import ValidationError
from tools.build_record_fixtures import ref, snapshots
from tools.record_graph import validate_graph
from tools.screening import effective_screening


def rows():
    return {r["id"]: r for r in snapshots()["valid_all_families"]["records"]}


def amendment(template, rid, kind, source_id, at):
    record = deepcopy(template)
    record["id"] = rid
    revision = record["revisions"][0]
    revision["at"] = at
    revision["data"].update(
        kind=kind, target_refs=[ref(source_id)], replacement_refs=[ref(source_id, 2)],
        reason="Synthetic identity or source correction for screening-history regression.",
        prior_exposure="Earlier synthetic title/abstract decisions used the prior source revision.",
        required_rework="Recheck affected synthetic screening decisions without rewriting history.",
    )
    return record


class HistoricalIdentityTests(unittest.TestCase):
    def setUp(self):
        self.examples = rows()
        self.records = [self.examples[rid] for rid in ("SRC-A", "SRC-B", "SCR-A-TA", "SCR-B-FT")]
        for record in self.records[2:]:
            revision = record["revisions"][0]
            revision["data"]["reading_refs"] = []
            revision["basis"] = [revision["data"]["source_ref"]]
        self.examples["SCR-B-FT"]["revisions"][0]["data"]["decision"] = "awaiting_text"

    def merge(self, source_id="SRC-B", target_id="SRC-A", at="2000-01-02T00:00:00Z"):
        source = next(r for r in self.records if r["id"] == source_id)
        revision = deepcopy(source["revisions"][0])
        revision.update(rev=2, at=at)
        revision["data"].update(validity="superseded", alias_of=ref(target_id),
                                alias_reason="Synthetic later adjudicated identity merge.")
        source["revisions"].append(revision)
        self.records.append(amendment(self.examples["AMD-FIX-LAT"], "AMD-MERGE-" + source_id,
                                      "identity_merge", source_id, at))

    def use_b_title_abstract(self):
        ta = self.examples["SCR-A-TA"]
        ta["id"] = "SCR-B-TA"
        revision = ta["revisions"][0]
        revision["data"]["source_ref"] = ref("SRC-B")
        revision["basis"] = [ref("SRC-B")]

    def test_later_alias_cannot_repair_missing_historical_title_abstract(self):
        with self.assertRaisesRegex(ValidationError, "SCREENING_SEQUENCE"):
            validate_graph(self.records)
        self.merge()
        with self.assertRaisesRegex(ValidationError, "SCREENING_SEQUENCE"):
            validate_graph(self.records)

    def test_alias_known_before_full_text_can_supply_the_same_source_scope(self):
        self.merge()
        ft = self.examples["SCR-B-FT"]["revisions"][0]
        ft.update(at="2000-01-02T00:00:01Z", basis=[ref("SRC-B", 2)])
        ft["data"]["source_ref"] = ref("SRC-B", 2)
        graph = validate_graph(self.records)
        self.assertEqual(graph.canonical_id_at("SRC-B", "2000-01-01T23:59:59Z"), "SRC-B")
        self.assertEqual(graph.canonical_id_at("SRC-B", ft["at"]), "SRC-A")
        self.assertNotIn(("SCR-B-FT", 1), graph.stale)
        self.assertEqual(graph.currency_edges[("SCR-B-FT", 1)], {("SCR-A-TA", 1)})

    def test_later_alias_does_not_hide_valid_prior_source_scope(self):
        self.use_b_title_abstract()
        validate_graph(self.records)
        self.merge()
        graph = validate_graph(self.records)
        historical = effective_screening(graph, at="2000-01-01T23:59:59Z")
        current = effective_screening(graph)
        self.assertEqual({scope[0] for scope in historical}, {"SRC-B"})
        self.assertEqual({scope[0] for scope in current}, {"SRC-A"})

    def test_later_alias_cannot_repair_cross_source_supersession(self):
        successor = deepcopy(self.examples["SCR-A-TA"])
        successor["id"] = "SCR-B-RECHECK-TA"
        revision = successor["revisions"][0]
        revision.update(at="2000-01-01T00:20:06Z", basis=[ref("SRC-B")])
        revision["data"].update(source_ref=ref("SRC-B"), supersedes_ref=ref("SCR-A-TA"))
        self.records = self.records[:3] + [successor]
        self.merge()
        with self.assertRaisesRegex(ValidationError, "SCREENING_SUPERSESSION"):
            validate_graph(self.records)

    def test_alias_target_recorded_later_is_unavailable_to_historical_scope(self):
        self.use_b_title_abstract()
        self.examples["SRC-A"]["revisions"][0]["at"] = "2000-01-02T00:00:00Z"
        self.examples["SRC-B"]["revisions"][0]["data"].update(
            validity="superseded", alias_of=ref("SRC-A"),
            alias_reason="Synthetic malformed alias pointing to a future record.",
        )
        with self.assertRaisesRegex(ValidationError, "FUTURE_IDENTITY"):
            validate_graph(self.records)

    def test_each_link_of_alias_chain_uses_its_historical_revision(self):
        self.records = self.records[:2]
        c = deepcopy(self.examples["SRC-B"])
        c["id"] = "SRC-C"
        self.records.append(c)
        self.merge("SRC-C", "SRC-B", "2000-01-02T00:00:00Z")
        self.merge("SRC-B", "SRC-A", "2000-01-03T00:00:00Z")
        graph = validate_graph(self.records)
        for at, expected in (("2000-01-01T23:59:59Z", "SRC-C"),
                             ("2000-01-02T00:00:00Z", "SRC-B"),
                             ("2000-01-03T00:00:00Z", "SRC-A")):
            with self.subTest(at=at):
                self.assertEqual(graph.canonical_id_at("SRC-C", at), expected)


class ScreeningPrerequisiteCurrencyTests(unittest.TestCase):
    def setUp(self):
        self.examples = rows()
        self.source, self.ta, self.ft, self.read = [self.examples[rid] for rid in
                                                  ("SRC-A", "SCR-A-TA", "SCR-A-FT", "AID-READ-A")]
        correction = deepcopy(self.source["revisions"][0])
        correction.update(rev=2, at="2000-01-02T00:00:00Z")
        correction["data"]["title"] = "Materially corrected synthetic source"
        self.source["revisions"].append(correction)
        change = amendment(self.examples["AMD-FIX-LAT"], "AMD-SOURCE-CORRECTION",
                           "source_correction", "SRC-A", correction["at"])
        self.newread = deepcopy(self.read)
        self.newread["id"] = "AID-NEW-READ"
        read_revision = self.newread["revisions"][0]
        read_revision.update(at="2000-01-02T00:00:01Z", basis=[ref("SRC-A", 2)])
        read_revision["data"].update(source_ref=ref("SRC-A", 2),
                                     performed_at={"state": "known", "value": read_revision["at"]})
        ft_revision = self.ft["revisions"][0]
        ft_revision.update(at="2000-01-02T00:00:02Z",
                           basis=[ref("SRC-A", 2), ref("AID-NEW-READ")])
        ft_revision["data"].update(source_ref=ref("SRC-A", 2), reading_refs=[ref("AID-NEW-READ")])
        self.records = [self.source, self.ta, self.ft, self.read, self.newread, change]

    def test_stale_title_abstract_invalidates_full_text_on_corrected_source(self):
        graph = validate_graph(self.records)
        self.assertIn(("SCR-A-TA", 1), graph.stale)
        self.assertNotIn(("SRC-A", 2), graph.stale)
        self.assertNotIn(("AID-NEW-READ", 1), graph.stale)
        self.assertEqual(graph.currency_edges[("SCR-A-FT", 1)], {("SCR-A-TA", 1)})
        self.assertIn(("SCR-A-FT", 1), graph.stale)
        with self.assertRaisesRegex(ValidationError, "STALE_RELEASE"):
            graph.require_current(ref("SCR-A-FT"), "screening")

    def test_later_title_abstract_revision_does_not_retarget_prior_full_text_dependency(self):
        later = deepcopy(self.ta["revisions"][0])
        later.update(rev=2, at="2000-01-02T00:00:03Z")
        later["data"]["reason"] = "Synthetic later annotation retaining the original source pin."
        self.ta["revisions"].append(later)
        graph = validate_graph(self.records)
        self.assertEqual(graph.currency_edges[("SCR-A-FT", 1)], {("SCR-A-TA", 1)})
        with self.assertRaisesRegex(ValidationError, "STALE_RELEASE"):
            graph.require_current(ref("SCR-A-FT"), "screening")

    def test_usable_recheck_requires_new_title_abstract_then_full_text_revision(self):
        recheck = deepcopy(self.ta)
        recheck["id"] = "SCR-A-RECHECK-TA"
        revision = recheck["revisions"][0]
        revision.update(at="2000-01-02T00:00:03Z",
                        basis=[ref("SRC-A", 2), ref("AID-NEW-READ")])
        revision["data"].update(source_ref=ref("SRC-A", 2), reading_refs=[ref("AID-NEW-READ")],
                                supersedes_ref=ref("SCR-A-TA"))
        self.records.append(recheck)
        graph = validate_graph(self.records)
        self.assertNotIn((recheck["id"], 1), graph.stale)
        with self.assertRaisesRegex(ValidationError, "STALE_RELEASE"):
            graph.require_current(ref("SCR-A-FT"), "screening")
        renewed = deepcopy(self.ft["revisions"][0])
        renewed.update(rev=2, at="2000-01-02T00:00:04Z")
        renewed["data"]["reason"] = "Synthetic full-text recheck after the corrected-source TA decision."
        self.ft["revisions"].append(renewed)
        graph = validate_graph(self.records)
        self.assertIn(("SCR-A-FT", 1), graph.stale)
        self.assertEqual(graph.currency_edges[("SCR-A-FT", 2)], {(recheck["id"], 1)})
        self.assertEqual(graph.require_current(ref("SCR-A-FT", 2), "screening")["decision"], "include")


if __name__ == "__main__":
    unittest.main()
