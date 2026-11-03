"""Identity helpers propose exact matches, preserve conflicts and never merge."""
from __future__ import annotations

import copy
import unittest

from schemas import ValidationError
from tools.build_record_fixtures import ref, snapshots
from tools.record_graph import validate_graph
from tools.screening import identity_candidates, normalize_doi, normalize_url, title_author_year


def source(title="A synthetic report", author="Fictional Author", year="2000", doi=None, url=None):
    identifiers = []
    for scheme, value in (("doi", doi), ("url", url)):
        if value is not None:
            identifiers.append({"scheme": scheme, "value": value, "status": "verified", "provenance": "Synthetic test assertion only"})
    return {"title": title, "authors": [{"name": author, "role": "author"}],
            "publication_date": {"state": "known", "value": year},
            "metadata_status": "verified", "identifiers": identifiers}


class IdentityCandidateTests(unittest.TestCase):
    def test_doi_normalization_preserves_actual_suffix_punctuation(self):
        self.assertEqual(normalize_doi(" DOI:10.1234/EXAMPLE.(2) "), "10.1234/example.(2)")
        self.assertEqual(normalize_doi("https://DOI.ORG/10.1234%2FExample%3Fpart?utm_source=test"), "10.1234/example?part")
        self.assertEqual(normalize_doi("10.1234/example."), "10.1234/example.")
        self.assertNotEqual(normalize_doi("10.1234/example."), normalize_doi("10.1234/example"))
        for invalid in ("https://publisher.invalid/doi/10.1234/example", "reported DOI 10.1234/example",
                        "10.1234/example another", "https://name:secret@doi.org/10.1234/example", None):
            with self.subTest(value=invalid):
                self.assertIsNone(normalize_doi(invalid))

    def test_url_normalization_is_conservative(self):
        self.assertEqual(normalize_url("HTTPS://EXAMPLE.ORG:443/Paper?b=2&a=1#part"), "https://example.org/Paper?b=2&a=1#part")
        base = "https://example.org/Paper?a=1&b=2"
        for other in ("http://example.org/Paper?a=1&b=2", "https://example.org/paper?a=1&b=2",
                      "https://example.org/Paper/?a=1&b=2", "https://example.org/Paper?b=2&a=1",
                      "https://example.org/Paper?a=1&b=2#part"):
            self.assertNotEqual(normalize_url(base), normalize_url(other))
        for invalid in ("javascript:alert(1)", "//example.org/Paper", "https://example.org:bad/Paper",
                        "https://name:secret@example.org/Paper", "https://example.org/has space"):
            self.assertIsNone(normalize_url(invalid))

    def test_doi_resolver_controls_are_rejected_before_urlsplit_can_remove_them(self):
        for control, encoded in (("\n", "%0A"), ("\r", "%0D"), ("\t", "%09")):
            with self.subTest(control=repr(control)):
                self.assertIsNone(normalize_doi("https://doi.org/10.1234/a" + control + "b"))
                self.assertIsNone(normalize_doi("https://doi.org/10.1234/a" + encoded + "b"))
        self.assertEqual(normalize_doi(" \nhttps://doi.org/10.1234/AB\t "), "10.1234/ab")

    def test_exact_title_first_author_year_requires_all_fields(self):
        item = source(title="  A   SYNTHETIC report ", author="Fictional Author", year="2000-02-01")
        self.assertEqual(title_author_year(item), ("a synthetic report", "fictional author", "2000"))
        for change in ({"authors": []}, {"publication_date": {"state": "unknown", "reason": "Synthetic unknown"}},
                       {"authors": [{"name": "Fictional Editor", "role": "editor"}]}):
            self.assertIsNone(title_author_year({**item, **change}))

    def test_same_title_different_author_or_year_does_not_match(self):
        self.assertEqual(identity_candidates({"SRC-A": source(), "SRC-B": source(author="Different Author")}), [])
        self.assertEqual(identity_candidates({"SRC-A": source(), "SRC-B": source(year="2001")}), [])

    def test_similar_titles_are_not_fuzzy_identity_evidence(self):
        self.assertEqual(identity_candidates({"SRC-A": source(), "SRC-B": source(title="A synthetic reports")}), [])

    def test_different_verified_dois_cannot_be_overridden_by_title_or_url(self):
        items = {"SRC-A": source(doi="10.1234/a", url="https://example.org/paper"),
                 "SRC-B": source(doi="10.1234/b", url="https://example.org/paper")}
        result = identity_candidates(items)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "conflict")
        self.assertEqual({x["kind"] for x in result[0]["matches"]}, {"title_first_author_year", "verified_resource_url"})

    def test_conflicted_metadata_stays_conflicted_despite_shared_doi(self):
        items = {"SRC-A": source(doi="10.1234/a"), "SRC-B": source(doi="10.1234/a")}
        items["SRC-B"]["metadata_status"] = "conflict"
        self.assertEqual(identity_candidates(items)[0]["status"], "conflict")

    def test_unverified_doi_is_not_an_exact_verified_match(self):
        a, b = source(doi="10.1234/a"), source(title="Another title", doi="10.1234/a")
        b["identifiers"][0]["status"] = "candidate"
        self.assertEqual(identity_candidates({"SRC-A": a, "SRC-B": b}), [])

    def test_identifier_level_doi_conflict_remains_visible(self):
        a, b = source(), source(doi="10.1234/contested")
        b["identifiers"][0]["status"] = "conflict"
        self.assertEqual(identity_candidates({"SRC-A": a, "SRC-B": b})[0]["status"], "conflict")

    def test_candidates_are_deterministic_and_do_not_mutate_or_merge(self):
        items = {"SRC-B": source(doi="10.1234/A"), "SRC-A": source(doi="https://doi.org/10.1234/a")}
        before = copy.deepcopy(items)
        expected = identity_candidates(items)
        self.assertEqual(expected, identity_candidates(dict(reversed(list(items.items())))))
        self.assertEqual(items, before)
        self.assertEqual(expected[0]["source_ids"], ["SRC-A", "SRC-B"])
        self.assertEqual(expected[0]["status"], "candidate")
        self.assertNotIn("merged_source_id", expected[0])


class CanonicalDoiCollisionTests(unittest.TestCase):
    def test_malformed_verified_doi_cannot_escape_collision_checks(self):
        for value in ("not a DOI", "https://doi.org/10.1234/a\nb", "https://doi.org/10.1234/a\rb", "https://doi.org/10.1234/a\tb"):
            data = snapshots()["valid_all_families"]
            source_row = next(record for record in data["records"] if record["id"] == "SRC-A")
            source_row["revisions"][0]["data"]["identifiers"] = [
                {"scheme": "doi", "value": value, "status": "verified", "provenance": "Synthetic malformed assertion"}]
            with self.subTest(value=value), self.assertRaisesRegex(ValidationError, "SOURCE_IDENTIFIER"):
                validate_graph(data["records"])

    def test_verified_collision_is_rejected_but_explicit_alias_is_allowed(self):
        data = snapshots()["valid_all_families"]
        rows = {record["id"]: record for record in data["records"]}
        identifier = {"scheme": "doi", "value": "10.1234/SYNTHETIC", "status": "verified", "provenance": "Synthetic identity collision test"}
        for rid in ("SRC-A", "SRC-B"):
            rows[rid]["revisions"][0]["data"]["identifiers"] = [copy.deepcopy(identifier)]
        rows["SRC-B"]["revisions"][0]["data"]["identifiers"][0]["value"] = "https://doi.org/10.1234/synthetic"
        with self.assertRaisesRegex(ValidationError, "SOURCE_IDENTITY_COLLISION"):
            validate_graph(data["records"])
        rows["SRC-B"]["revisions"][0]["data"]["identifiers"] = []
        alias = copy.deepcopy(rows["SRC-A"])
        alias["id"] = "SRC-ALIAS"
        alias["revisions"][0]["data"].update(validity="superseded", alias_of=ref("SRC-A"),
                                             alias_reason="Synthetic explicitly adjudicated duplicate.")
        data["records"].append(alias)
        validate_graph(data["records"])


if __name__ == "__main__":
    unittest.main()
