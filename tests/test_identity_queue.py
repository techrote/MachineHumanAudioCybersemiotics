"""Fictional input contracts for the read-only R006 work queue."""
import copy
import unittest

from tools.identity_queue import build_queue


def source(rid="SRC-A", value="10.1234/toy", scheme="doi", **changes):
    body = {"validity": "active", "metadata_status": "verified", "identifiers": [
        {"scheme": scheme, "value": value, "status": "verified"}]}
    body.update(changes)
    return {"id": rid, "kind": "source", "revisions": [{"rev": 1, "data": body}]}


def hit(value="https://doi.org/10.1234/TOY", scheme="url", **changes):
    body = {"status": "unresolved", "search_ref": {"id": "SRCH-TOY", "rev": 1},
            "ordinal": 3, "returned_identifiers": [{"scheme": scheme, "value": value}]}
    body.update(changes)
    return {"id": "HIT-TOY", "kind": "search_hit", "revisions": [{"rev": 1, "data": body}]}


class IdentityQueueTests(unittest.TestCase):
    def test_doi_resolver_matches_explicit_doi_and_retains_pins(self):
        result = build_queue([source(), hit()])
        self.assertEqual(result["counts"], {"unresolved_hits": 1, "candidate_hits": 1,
                                         "unmatched_hits": 0, "conflict_review_hits": 0})
        row = result["candidates"][0]
        self.assertEqual(row["hit_ref"], {"id": "HIT-TOY", "rev": 1})
        self.assertEqual(row["source_candidates"][0]["source_ref"], {"id": "SRC-A", "rev": 1})
        self.assertEqual(row["status"], "candidate_review")

    def test_latest_revision_disposition_removes_candidate(self):
        item = hit()
        item["revisions"].append({"rev": 2, "data": {**item["revisions"][0]["data"], "status": "resolved"}})
        self.assertEqual(build_queue([source(), item])["counts"]["unresolved_hits"], 0)

    def test_withdrawn_alias_and_unverified_sources_not_proposed(self):
        for change in ({"validity": "withdrawn"}, {"validity": "superseded", "alias_of": {"id": "SRC-B", "rev": 1}},
                       {"identifiers": [{"scheme": "doi", "value": "10.1234/toy", "status": "candidate"}]}):
            with self.subTest(change=change):
                self.assertEqual(build_queue([source(**change), hit()])["counts"]["candidate_hits"], 0)

    def test_conflicted_source_and_ambiguous_resource_remain_conflicts(self):
        inputs = ([source(metadata_status="conflict"), hit()],
                  [source(value="https://example.invalid/shared", scheme="url"),
                   source("SRC-B", value="https://example.invalid/shared", scheme="url"),
                   hit(value="https://example.invalid/shared")])
        for rows in inputs:
            with self.subTest(rows=rows):
                result = build_queue(rows)
                self.assertEqual(result["counts"]["conflict_review_hits"], 1)
                self.assertEqual(len(result["candidates"][0]["source_candidates"]), len(rows) - 1)

    def test_conflicted_identifier_not_hidden_by_other_verified_match(self):
        item = source()
        item["revisions"][0]["data"]["identifiers"].append(
            {"scheme": "doi", "value": "10.1234/other", "status": "conflict"})
        self.assertEqual(build_queue([item, hit()])["candidates"][0]["status"], "conflict_review")

    def test_multiple_verified_dois_remain_conflicted(self):
        item = source()
        item["revisions"][0]["data"]["identifiers"].append(
            {"scheme": "doi", "value": "10.1234/other", "status": "verified"})
        self.assertEqual(build_queue([item, hit()])["candidates"][0]["status"], "conflict_review")

    def test_publisher_path_and_invalid_identifier_do_not_become_doi(self):
        for value in ("https://publisher.invalid/10.1234/toy", "https://doi.org/10.1234/a\nb", "10.1234/else"):
            with self.subTest(value=value):
                self.assertEqual(build_queue([source(), hit(value=value)])["counts"]["unmatched_hits"], 1)

    def test_url_path_case_and_query_order_remain_distinct(self):
        for value in ("https://example.invalid/paper?a=1&b=2", "https://example.invalid/Paper?b=2&a=1"):
            result = build_queue([source(value="https://example.invalid/Paper?a=1&b=2", scheme="url"), hit(value=value)])
            self.assertEqual(result["counts"]["candidate_hits"], 0)

    def test_deterministic_nonmutating_and_history_bound(self):
        rows = [source(), hit()]
        original = copy.deepcopy(rows)
        expected = build_queue(rows)
        self.assertEqual(expected, build_queue(list(reversed(rows))))
        self.assertEqual(rows, original)
        rows[1]["revisions"][0]["data"]["ordinal"] = 4
        self.assertNotEqual(expected["input_records_sha256"], build_queue(rows)["input_records_sha256"])
        self.assertEqual(expected["acceptance"], "not_evaluated")


if __name__ == "__main__":
    unittest.main()
