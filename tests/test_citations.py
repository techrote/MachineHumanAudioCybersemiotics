"""Real temporary Markdown, exact bibliography pins and hashed evidence bindings."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from schemas import ValidationError
from tools.build_record_fixtures import ref, snapshots
from tools.citations import markers, validate_citations
from tools.record_graph import validate_graph


class CitationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "paper").mkdir()
        self.manuscript = self.root / "paper/manuscript.md"
        self.graph = validate_graph(snapshots()["valid_corrected"]["records"])
        self.bibliography = {"schema_version": 1, "entries": [
            {"key": "report-a", "source_ref": ref("SRC-A")},
            {"key": "report-b", "source_ref": ref("SRC-B")},
        ]}
        self.sidecar = {"schema_version": 1, "artifact": {}, "bindings": [{
            "start_line": 1, "end_line": 1, "citation_keys": ["report-a"],
            "source_refs": [ref("SRC-A")], "claim_refs": [ref("CLM-LAT", 4)],
        }]}
        self.text = "SYNTHETIC latency assertion [@report-a] {{claim:CLM-LAT@4}}\n"
        self.save()

    def save(self):
        raw = self.text.encode("utf-8")
        self.manuscript.write_bytes(raw)
        self.sidecar["artifact"] = {"path": "paper/manuscript.md", "sha256": hashlib.sha256(raw).hexdigest()}
        self.write_json("bibliography.json", self.bibliography)
        self.write_json("bindings.json", self.sidecar)

    def write_json(self, path, data):
        (self.root / path).write_text(json.dumps(data), encoding="utf-8")

    def validate(self):
        return validate_citations(self.root, "bibliography.json", ["bindings.json"], self.graph)

    def test_current_source_claim_and_manuscript_are_explicitly_linked(self):
        result = self.validate()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["documents"], {"paper/manuscript.md": {"citations": 1, "claims": 1}})
        self.assertEqual(result["bindings"], 1)
        self.assertIn("citation_entailment", result["not_evaluated"])

    def test_missing_bibliography_file_is_rejected(self):
        (self.root / "bibliography.json").unlink()
        with self.assertRaisesRegex(ValidationError, "^MISSING_FILE:"):
            self.validate()

    def test_unknown_bibliography_key_is_rejected(self):
        self.bibliography["entries"] = [self.bibliography["entries"][1]]
        self.save()
        with self.assertRaisesRegex(ValidationError, "^MISSING_CITATION:"):
            self.validate()

    def test_duplicate_bibliography_key_cannot_silently_rebind_a_source(self):
        self.bibliography["entries"][1]["key"] = "report-a"
        self.save()
        with self.assertRaisesRegex(ValidationError, "^BIBLIOGRAPHY_KEY:"):
            self.validate()

    def test_wrong_source_pin_for_a_citation_is_rejected(self):
        self.sidecar["bindings"][0]["source_refs"] = [ref("SRC-B")]
        self.save()
        with self.assertRaisesRegex(ValidationError, "^CITATION_SOURCE:"):
            self.validate()

    def test_valid_but_unrelated_source_cannot_be_attached_to_a_claim(self):
        # Every individual pin exists and is current. The source/claim chain is wrong.
        self.text = "SYNTHETIC latency assertion [@report-b] {{claim:CLM-LAT@4}}\n"
        self.sidecar["bindings"][0].update(citation_keys=["report-b"], source_refs=[ref("SRC-B")])
        self.save()
        with self.assertRaisesRegex(ValidationError, "^CITATION_EVIDENCE:"):
            self.validate()

    def test_empirical_claim_marker_needs_a_citation_from_its_evidence(self):
        self.text = "SYNTHETIC latency assertion {{claim:CLM-LAT@4}}\n"
        self.sidecar["bindings"][0].update(citation_keys=[], source_refs=[])
        self.save()
        with self.assertRaisesRegex(ValidationError, "^CITATION_EVIDENCE:"):
            self.validate()

    def test_bound_claims_can_each_use_their_own_source_in_one_range(self):
        self.text = (
            "SYNTHETIC latency [@report-a] {{claim:CLM-LAT@4}}\n"
            "SYNTHETIC accuracy [@report-b] {{claim:CLM-ACC@2}}\n"
        )
        self.sidecar["bindings"][0].update(end_line=2, citation_keys=["report-a", "report-b"],
                                             source_refs=[ref("SRC-A"), ref("SRC-B")],
                                             claim_refs=[ref("CLM-LAT", 4), ref("CLM-ACC", 2)])
        self.save()
        result = self.validate()
        self.assertEqual(result["documents"]["paper/manuscript.md"], {"citations": 2, "claims": 2})

    def test_contextual_source_only_citation_is_allowed(self):
        self.text = "SYNTHETIC companion report metadata [@report-b]\n"
        self.sidecar["bindings"][0].update(citation_keys=["report-b"], source_refs=[ref("SRC-B")], claim_refs=[])
        self.save()
        self.assertEqual(self.validate()["documents"]["paper/manuscript.md"], {"citations": 1, "claims": 0})

    def test_unbound_marker_fails_even_when_the_manuscript_hash_is_updated(self):
        self.text += "SYNTHETIC extra contextual citation [@report-b]\n"
        self.save()
        with self.assertRaisesRegex(ValidationError, "^UNBOUND_CITATION:"):
            self.validate()

    def test_unchanged_sidecar_does_not_accept_a_modified_manuscript(self):
        self.manuscript.write_text(self.text + "Changed manuscript text.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "^ARTIFACT_HASH:"):
            self.validate()

    def test_binding_lines_must_contain_the_actual_markers(self):
        self.text = "# Synthetic manuscript\n" + self.text
        self.save()
        with self.assertRaisesRegex(ValidationError, "^CITATION_LOCATOR:"):
            self.validate()

    def test_stale_extraction_quarantines_its_downstream_manuscript_claim(self):
        self.graph = validate_graph(snapshots()["valid_correction_pending"]["records"])
        self.text = "SYNTHETIC stale latency assertion [@report-a] {{claim:CLM-LAT@2}}\n"
        self.sidecar["bindings"][0]["claim_refs"] = [ref("CLM-LAT", 2)]
        self.save()
        with self.assertRaisesRegex(ValidationError, "^STALE_RELEASE:"):
            self.validate()

    def source_access_observation(self):
        data = snapshots()["valid_before"]
        source = next(row for row in data["records"] if row["id"] == "SRC-A")
        observation = copy.deepcopy(source["revisions"][0])
        observation.update(rev=2, at="2000-01-02T00:00:00Z")
        observation["data"].update(access_at="2000-01-02T00:00:00Z",
                                   access_reason="Synthetic later access observation; the source content and identity are unchanged.")
        source["revisions"].append(observation)
        self.graph = validate_graph(data["records"])
        self.text = "SYNTHETIC retained exact source pin [@report-a] {{claim:CLM-LAT@2}}\n"
        self.sidecar["bindings"][0]["claim_refs"] = [ref("CLM-LAT", 2)]

    def test_nonstale_exact_source_pin_survives_later_access_only_observation(self):
        self.source_access_observation()
        self.save()
        self.assertEqual(self.graph.latest_pin("SRC-A"), ("SRC-A", 2))
        self.assertNotIn(("SRC-A", 1), self.graph.stale)
        self.assertNotIn(("CLM-LAT", 2), self.graph.stale)
        self.assertEqual(self.validate()["status"], "passed")

    def test_same_source_id_does_not_silently_retarget_a_claim_to_a_different_revision(self):
        self.source_access_observation()
        self.bibliography["entries"][0]["source_ref"] = ref("SRC-A", 2)
        self.sidecar["bindings"][0]["source_refs"] = [ref("SRC-A", 2)]
        self.save()
        with self.assertRaisesRegex(ValidationError, "^CITATION_EVIDENCE:"):
            self.validate()

    def test_material_source_invalidation_rejects_the_retained_bibliography_pin(self):
        self.graph = validate_graph(snapshots()["valid_source_invalidated"]["records"])
        self.assertIn(("SRC-A", 1), self.graph.stale)
        with self.assertRaisesRegex(ValidationError, "^STALE_RELEASE:"):
            self.validate()

    def test_initially_withdrawn_source_cannot_be_used_as_current_citation(self):
        data = snapshots()["valid_corrected"]
        next(row for row in data["records"] if row["id"] == "SRC-A")["revisions"][0]["data"]["validity"] = "withdrawn"
        self.graph = validate_graph(data["records"])
        with self.assertRaisesRegex(ValidationError, "^(STALE_RELEASE|UNREADY_RELEASE):"):
            self.validate()

    def test_unregistered_manuscript_with_markers_is_not_ignored(self):
        (self.root / "paper/other.md").write_text("SYNTHETIC other report [@report-b]\n", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "^UNBOUND_MANUSCRIPT:"):
            self.validate()

    def test_two_sidecars_cannot_compete_for_the_same_manuscript(self):
        self.write_json("other-bindings.json", copy.deepcopy(self.sidecar))
        with self.assertRaisesRegex(ValidationError, "^CITATION_MANIFEST:"):
            validate_citations(self.root, "bibliography.json", ["bindings.json", "other-bindings.json"], self.graph)

    def test_code_examples_are_not_treated_as_research_citation_markers(self):
        text = (
            "Use `[@ignored] {{claim:CLM-IGNORED@1}}` as a code example.\n"
            "```text\n[@ignored-too] {{claim:CLM-IGNORED@2}}\n```\n"
            "SYNTHETIC actual marker [@report-a; -@report-b] {{claim:CLM-LAT@4}}\n"
        )
        citations, claims = markers(text)
        self.assertEqual(citations, {(5, "report-a"), (5, "report-b")})
        self.assertEqual(claims, {(5, ("CLM-LAT", 4))})

    def test_malformed_explicit_claim_marker_cannot_disappear_from_prose(self):
        for malformed in ("{{claim:CLM-NO-SUCH-CLAIM@0}}", "{{claim:CLM-LAT@2 }}"):
            with self.subTest(marker=malformed), self.assertRaisesRegex(ValidationError, "^MALFORMED_CLAIM_MARKER:"):
                markers("SYNTHETIC malformed marker " + malformed + "\n")

    def test_malformed_marker_fails_even_with_an_otherwise_valid_source_binding(self):
        for malformed in ("{{claim:CLM-NO-SUCH-CLAIM@0}}", "{{claim:CLM-LAT@2 }}"):
            self.text = "SYNTHETIC marker " + malformed + " [@report-a]\n"
            self.sidecar["bindings"][0]["claim_refs"] = []
            self.save()
            with self.subTest(marker=malformed), self.assertRaisesRegex(ValidationError, "^MALFORMED_CLAIM_MARKER:"):
                self.validate()

    def test_malformed_claim_syntax_inside_code_examples_remains_ignored(self):
        examples = "`{{claim:CLM-LAT@2 }}`\n```text\n{{claim:CLM-NO-SUCH-CLAIM@0}}\n```\n"
        self.assertEqual(markers(examples), (set(), set()))
        self.text += examples
        self.save()
        self.assertEqual(self.validate()["documents"]["paper/manuscript.md"], {"citations": 1, "claims": 1})


if __name__ == "__main__":
    unittest.main()
