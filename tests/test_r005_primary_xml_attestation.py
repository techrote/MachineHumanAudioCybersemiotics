"""R005 local-source attestation invariants; entirely synthetic XML, no network."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "research/sources/auditory/scripts/attest_primary_xml.py"
spec = importlib.util.spec_from_file_location("r005_attest_primary_xml", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

GOOD = b"""<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink">
<front><article-meta>
<article-id pub-id-type="doi">10.2478/v10053-008-0064-6</article-id>
<article-id pub-id-type="pmc">PMC2865004</article-id>
<permissions><license xlink:href="https://creativecommons.org/licenses/by/2.5/"/></permissions>
</article-meta></front>
<body><sec><title>Method</title><p>synthetic test text, not an actual study</p></sec>
<sec><title>Results</title><p>fixture only</p></sec></body>
<back><ref-list/></back></article>"""

ARGS = dict(
    source_url="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2865004/fullTextXML",
    edition="Europe PMC original article XML (operator-reported)",
    acquired_at="2026-11-10T20:15:16Z",
    actor="test-synthetic-agent",
    access_proof="synthetic fixture; not a live HTTP receipt",
    rights_note="synthetic fixture; no copyright or archival rights established",
)


class AttestationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.xml = self.home / "local.xml"
        self.xml.write_bytes(GOOD)

    def test_capture_and_verify_local_bytes(self):
        rec = mod.capture(self.xml, **ARGS)
        self.assertEqual(rec["doi_in_local_xml"], mod.DOI)
        self.assertEqual(rec["pmcid_in_local_xml"], mod.PMCID)
        self.assertEqual(rec["original_xml_bytes"], len(GOOD))
        self.assertIn("Method", rec["section_heading_inventory_not_reading"])
        self.assertIn("https://creativecommons.org/licenses/by/2.5/",
                      rec["licence_links_observed_not_independently_verified"])
        for key in ("source_manifestation_registered", "performed_semantic_reading",
                    "human_review_performed", "private_retention_rights_approved_by_tool",
                    "original_pdf_equivalence_verified", "raw_xml_bytes_in_receipt"):
            self.assertIs(rec[key], False)
        manifest = self.home / "receipt.json"
        manifest.write_text(json.dumps(rec), encoding="utf-8")
        result = mod.verify(self.xml, manifest)
        self.assertEqual(result["verified_bytes"], len(GOOD))
        self.xml.write_bytes(GOOD + b" ")
        with self.assertRaisesRegex(ValueError, "bytes"):
            mod.verify(self.xml, manifest)

    def test_missing_or_conflicting_doi_rejected(self):
        self.xml.write_bytes(GOOD.replace(b"10.2478/v10053-008-0064-6", b"10.9999/incorrect-doi"))
        with self.assertRaisesRegex(ValueError, "DOI missing"):
            mod.hash_local(self.xml)

    def test_other_pmcid_rejected(self):
        self.xml.write_bytes(GOOD.replace(b"PMC2865004", b"PMC1111111"))
        with self.assertRaisesRegex(ValueError, "Conflicting embedded PMCID"):
            mod.hash_local(self.xml)

    def test_optional_pmcid_is_not_fabricated(self):
        self.xml.write_bytes(GOOD.replace(b'<article-id pub-id-type="pmc">PMC2865004</article-id>', b''))
        rec = mod.capture(self.xml, **ARGS)
        self.assertIsNone(rec["pmcid_in_local_xml"])

    def test_numeric_pmcid_normalized(self):
        self.xml.write_bytes(GOOD.replace(b'PMC2865004', b'2865004'))
        rec = mod.capture(self.xml, **ARGS)
        self.assertEqual(rec["pmcid_in_local_xml"], mod.PMCID)

    def test_dtd_rejected(self):
        self.xml.write_bytes(b'<!DOCTYPE article [<!ENTITY fake "no">]>' + GOOD)
        with self.assertRaisesRegex(ValueError, "Entity"):
            mod.hash_local(self.xml)

    def test_abstract_only_source_rejected(self):
        self.xml.write_bytes(GOOD.replace(b"<back><ref-list/></back>", b""))
        with self.assertRaisesRegex(ValueError, "body/back"):
            mod.hash_local(self.xml)

    def test_credentials_or_query_tokens_rejected(self):
        for bad in ("http://example.org/a", "https://user:pwd@example.org/a",
                    "https://example.org/a?token=abc", "https://example.org/a#v"):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "HTTPS"):
                mod.capture(self.xml, **{**ARGS, "source_url": bad})

    def test_unverified_timestamp_rejected(self):
        for bad in ("2026-11-10T20:15:16", "garbled", "2099-01-01T00:00:00Z"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                mod.capture(self.xml, **{**ARGS, "acquired_at": bad})

    def test_empty_provenance_rejected(self):
        for fld in ("edition", "actor", "rights_note", "access_proof"):
            with self.subTest(field=fld), self.assertRaises(ValueError):
                mod.capture(self.xml, **{**ARGS, fld: "  "})

    def test_promoted_or_falsified_receipt_rejected(self):
        rec = mod.capture(self.xml, **ARGS)
        for field, value in [
            ("source_manifestation_registered", True),
            ("private_retention_rights_approved_by_tool", True),
            ("original_pdf_equivalence_verified", True),
            ("performed_semantic_reading", True),
            ("human_review_performed", True),
            ("screening_and_independent_sample_admissions", 2),
            ("schema", "some-other-schema"),
            ("source_id", "SRC-R006-UNRELATED@1"),
        ]:
            with self.subTest(field=field):
                changed = {**rec, field: value}
                manifest = self.home / "receipt.json"
                manifest.write_text(json.dumps(changed), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "fail-closed"):
                    mod.verify(self.xml, manifest)

    def test_verified_bytes_cannot_inherit_tampered_source_derived_claims(self):
        original = mod.capture(self.xml, **ARGS)
        changes = (
            ("section_heading_inventory_not_reading", ["Fictitious clinical conclusion"]),
            ("licence_links_observed_not_independently_verified",
             ["https://example.org/false-licence"]),
            ("article_body_present", False),
            ("article_back_present", False),
        )
        for field, value in changes:
            with self.subTest(field=field):
                changed = {**original, field: value}
                manifest = self.home / "receipt.json"
                manifest.write_text(json.dumps(changed), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "source-derived receipt field"):
                    mod.verify(self.xml, manifest)

    def test_receipt_operator_provenance_and_source_pins_fail_closed(self):
        original = mod.capture(self.xml, **ARGS)
        changes = (
            ("hit_id", "HIT-R005R-UNRELATED@1"),
            ("issue", 6),
            ("downstream_issue", 5),
            ("frozen_cutoff", "2026-11-10"),
            ("reported_edition", ""),
            ("operator_id_operator_reported", None),
            ("access_proof_operator_reported", ""),
            ("rights_note_operator_reported_not_authorization", " "),
            ("source_url_operator_reported", "https://example.org/file?token=abc"),
            ("acquired_utc_operator_reported_not_network_verified", "nonsense"),
            ("attestation_utc", "2020-01-01T00:00:00Z"),
        )
        for field, value in changes:
            with self.subTest(field=field):
                changed = {**original, field: value}
                manifest = self.home / "receipt.json"
                manifest.write_text(json.dumps(changed), encoding="utf-8")
                with self.assertRaises(ValueError):
                    mod.verify(self.xml, manifest)

    def test_receipt_attestation_utc_is_canonical_and_ordered(self):
        original = mod.capture(self.xml, **ARGS)
        for field, value in (
            ("attestation_utc", "2026-11-10T23:00:00+01:00"),
            ("acquired_utc_operator_reported_not_network_verified",
             "2026-11-10T20:15:16+00:00"),
        ):
            with self.subTest(field=field):
                changed = {**original, field: value}
                manifest = self.home / "receipt.json"
                manifest.write_text(json.dumps(changed), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "canonical UTC"):
                    mod.verify(self.xml, manifest)

    def test_cli_no_overwriting_earlier_receipt(self):
        dest = self.home / "receipt.json"
        dest.write_text("immutable preexisting receipt", encoding="utf-8")
        params = ["capture", "--file", str(self.xml), "--manifest", str(dest)]
        for k, v in ARGS.items():
            params.extend(["--" + k.replace("_", "-"), v])
        self.assertEqual(mod.main(params), 2)
        self.assertEqual(dest.read_text(encoding="utf-8"), "immutable preexisting receipt")

    def test_no_network_used_in_module(self):
        # Neither capture nor verify should open network connections.
        self.assertNotIn("urllib.request", SCRIPT.read_text(encoding="utf-8"))
        self.assertNotIn("requests.get", SCRIPT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
