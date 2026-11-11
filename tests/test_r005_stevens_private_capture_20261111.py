"""Synthetic-only tests for opt-in private Stevens original XML custody (Refs #5)."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "research/sources/auditory/scripts"
sys.path.insert(0, str(SCRIPTS))
import capture_stevens_xml as mod  # noqa: E402

ORIGINAL = b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.1 20151215//EN" "JATS-journalpublishing1.dtd">
<article xmlns:xlink="http://www.w3.org/1999/xlink">
<front><article-meta>
<article-id pub-id-type="doi">10.2478/v10053-008-0064-6</article-id>
<article-id pub-id-type="pmc">PMC2865004</article-id>
<permissions><license xlink:href="https://creativecommons.org/licenses/by/2.5/"/></permissions>
</article-meta></front>
<body><sec><title>Introduction</title><p>Test fixture, not a study.</p></sec>
<sec><title>Method</title><p>Artificial fixture.</p></sec>
<sec><title>Results</title><p>No actual observations.</p></sec></body>
<back><ref-list><title>References</title></ref-list></back>
</article>"""


class FakeResponse:
    status = 200
    def __init__(self, raw=ORIGINAL, *, status=200, url=mod.URL,
                 content_type="application/xml", length=None, http_date=None):
        self.raw = raw
        self.status = status
        self.url = url
        self.headers = {"Content-Type": content_type,
                        "Date": (http_date if http_date is not None
                                 else datetime.now(timezone.utc).strftime(
                                     "%a, %d %b %Y %H:%M:%S GMT")),
                        "Content-Length": str(len(raw) if length is None else length)}
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        return False
    def geturl(self):
        return self.url
    def read(self, size=-1):
        return self.raw[:size]


class PrivateCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.private = base / "private"
        self.private.mkdir()
        self.approval = base / "rights.json"
        self.rights = {
            "approved_private_dir": str(self.private.resolve()),
            "approved_by": "SYNTHETIC-RIGHTS-OPERATOR-NOT-A-REAL-APPROVAL",
            "approved_at_utc": "2026-11-10T20:00:00Z",
            "retention_basis": "SYNTHETIC-CC-BY-FIXTURE-NO-AUTHORIZATION",
            "attribution_policy": "SYNTHETIC-ATTRIBUTION-ONLY",
        }
        self.save_rights()

    def save_rights(self):
        self.approval.write_text(json.dumps(self.rights), encoding="utf-8")

    def fetch(self, response=None):
        return mod.capture(self.private, self.approval, "synthetic-test-actor",
                           opener=lambda req, timeout: response or FakeResponse())

    def receipt_path(self):
        return self.private / mod.RECEIPT_NAME

    def change_receipt(self, fn):
        receipt = json.loads(self.receipt_path().read_text())
        fn(receipt)
        self.receipt_path().write_text(json.dumps(receipt), encoding="utf-8")

    def test_retained_original_is_byte_identical_and_receipt_verified(self):
        receipt = self.fetch()
        self.assertEqual((self.private / mod.XML_NAME).read_bytes(), ORIGINAL)
        self.assertEqual(receipt["original_xml_bytes"], len(ORIGINAL))
        self.assertEqual(receipt["network_original_response"]["http_status"], 200)
        self.assertEqual(receipt["network_original_response"]["actual_body_sha256"],
                         receipt["original_xml_sha256"])
        self.assertFalse(receipt["source_custody_approved_by_software"])
        self.assertFalse(receipt["human_review_performed"])
        self.assertFalse(receipt["r006_scientific_admission"])
        self.assertTrue(mod.verify(self.private, self.approval)
                        ["source_and_operator_note_fingerprints_checked"])

    def test_unapproved_or_misrouted_private_dir_never_fetches(self):
        self.approval.unlink()
        def forbidden(req, timeout):
            self.fail("Network request must not occur without approval")
        with self.assertRaises(ValueError):
            mod.capture(self.private, self.approval, "actor", opener=forbidden)
        self.save_rights()
        self.rights["approved_private_dir"] = "/some/different/location"
        self.save_rights()
        with self.assertRaises(ValueError):
            mod.capture(self.private, self.approval, "actor", opener=forbidden)

    def test_missing_approval_fields_or_fake_future_time_fail_closed(self):
        for field, replacement in (("approved_by", ""),
                                   ("retention_basis", None),
                                   ("approved_at_utc", "2999-01-01T00:00:00Z")):
            with self.subTest(field=field):
                baseline = copy.deepcopy(self.rights)
                self.rights[field] = replacement
                self.save_rights()
                with self.assertRaises(ValueError):
                    mod.capture(self.private, self.approval, "actor",
                                opener=lambda req, timeout: self.fail("Unexpected fetch"))
                self.rights = baseline
        self.save_rights()

    def test_no_overwrite_or_false_success_on_repeat(self):
        self.fetch()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.fetch()
        self.assertEqual((self.private / mod.XML_NAME).read_bytes(), ORIGINAL)

    def test_bad_original_doi_and_missing_license_do_not_leave_source(self):
        for raw in (ORIGINAL.replace(b"10.2478/v10053-008-0064-6",
                                     b"10.9999/wrong"),
                    ORIGINAL.replace(b"/licenses/by/2.5/", b"/licenses/by-nc/4.0/")):
            with self.subTest(raw=raw[-35:]), self.assertRaises(ValueError):
                self.fetch(FakeResponse(raw=raw))
            self.assertFalse((self.private / mod.XML_NAME).exists())
            self.assertFalse(self.receipt_path().exists())

    def test_wrong_http_identity_and_truncation_refused(self):
        cases = [
            FakeResponse(status=403),
            FakeResponse(url="https://attacker.example/article.xml"),
            FakeResponse(content_type="text/html"),
            FakeResponse(http_date="not-a-date"),
            FakeResponse(http_date="Mon, 01 Jan 2000 00:00:00 GMT"),
            FakeResponse(http_date="Sat, 01 Jan 2000 00:00:00 GMT"),
            FakeResponse(length=len(ORIGINAL)+1),
            FakeResponse(raw=ORIGINAL + b"x" * (mod.MAX_BODY+1)),
        ]
        for response in cases:
            with self.subTest(case=response.url + str(response.status)):
                with self.assertRaises(ValueError):
                    self.fetch(response)
                self.assertFalse((self.private / mod.XML_NAME).exists())

    def test_tampered_source_or_network_receipt_fails(self):
        self.fetch()
        self.change_receipt(lambda r: r["network_original_response"].update(
            actual_body_sha256="0"*64))
        with self.assertRaises(ValueError):
            mod.verify(self.private, self.approval)
        self.fetch_receipt_reset()
        self.change_receipt(lambda r: r.update(r006_scientific_admission=True))
        with self.assertRaises(ValueError):
            mod.verify(self.private, self.approval)

    def fetch_receipt_reset(self):
        self.receipt_path().unlink()
        (self.private / mod.XML_NAME).unlink()
        self.fetch()

    def test_network_header_receipt_mutations_fail_closed(self):
        self.fetch()
        malformed = [
            ("http_date_header", "not-a-date"),
            ("http_date_header", "Mon, 01 Jan 2000 00:00:00 GMT"),
            ("http_date_header", "Sat, 01 Jan 2000 00:00:00 GMT"),
            ("content_type_header", "text/html"),
            ("content_type_header", ""),
            ("content_type_header", None),
        ]
        for field, value in malformed:
            with self.subTest(field=field, value=value):
                self.change_receipt(lambda r: r["network_original_response"].update(
                    {field: value}))
                with self.assertRaises(ValueError):
                    mod.verify(self.private, self.approval)
                self.fetch_receipt_reset()

    def test_source_headers_and_utc_chronology_round_trip(self):
        self.fetch()
        receipt = json.loads(self.receipt_path().read_text())
        response = receipt["network_original_response"]
        self.assertEqual(response["content_type_header"], "application/xml")
        self.assertTrue(mod.verify(self.private, self.approval)
                        ["source_and_operator_note_fingerprints_checked"])
        self.change_receipt(lambda r: r["network_original_response"].update(
            http_date_header="Fri, 01 Jan 1999 00:00:00 GMT"))
        with self.assertRaisesRegex(ValueError, "inconsistent"):
            mod.verify(self.private, self.approval)

    def test_plausible_mutated_date_disagrees_with_original_access_proof(self):
        self.fetch()
        recorded = json.loads(self.receipt_path().read_text())
        observed = recorded["network_original_response"]["http_date_header"]
        from datetime import timedelta
        altered = (datetime.strptime(observed, "%a, %d %b %Y %H:%M:%S GMT")
                   + timedelta(seconds=45)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        self.change_receipt(lambda r: r["network_original_response"].update(
            http_date_header=altered))
        with self.assertRaisesRegex(ValueError, "Date/access-proof"):
            mod.verify(self.private, self.approval)

    def test_rights_note_change_invalidates_stored_receipt(self):
        self.fetch()
        self.rights["attribution_policy"] = "CHANGED-NOTE"
        self.save_rights()
        with self.assertRaises(ValueError):
            mod.verify(self.private, self.approval)

    def test_mutated_edition_and_approval_claims_are_not_verified(self):
        # These fields were previously mutable while the original XML SHA held.
        self.fetch()
        for field, false_value in (
                ("reported_edition", "publisher-certified edition of record"),
                ("rights_note_operator_reported_not_authorization",
                 "Verified owner permission and unrestricted redistribution")):
            with self.subTest(field=field):
                self.change_receipt(lambda r: r.update({field: false_value}))
                with self.assertRaisesRegex(ValueError, "edition or approval-note"):
                    mod.verify(self.private, self.approval)
                self.fetch_receipt_reset()

    def test_approval_must_predate_original_network_request(self):
        from unittest.mock import patch
        # No network activity is warranted when the approval is dated after
        # the purported original request start, even if it is now in the past.
        with patch.object(mod, "utc_now", return_value="2026-11-10T19:59:00Z"):
            with self.assertRaisesRegex(ValueError, "must precede"):
                mod.capture(self.private, self.approval, "synthetic-operator",
                            opener=lambda req, timeout: self.fail("Unexpected fetch"))

    def test_verify_rejects_later_substituted_approval(self):
        import hashlib
        self.fetch()
        r = json.loads(self.receipt_path().read_text())
        # It is genuinely later than request_start but already in the past by
        # the time this offline verification takes place.
        self.rights["approved_at_utc"] = r["network_original_response"]["received_utc"]
        self.save_rights()
        note_sha = hashlib.sha256(self.approval.read_bytes()).hexdigest()
        def replace_rights_note(receipt):
            receipt["approval_file_sha256_operator_supplied"] = note_sha
            receipt["approval_at_utc_operator_supplied"] = self.rights["approved_at_utc"]
            receipt["rights_note_operator_reported_not_authorization"] = (
                mod.operator_rights_note(note_sha))
        self.change_receipt(replace_rights_note)
        with self.assertRaisesRegex(ValueError, "postdates original acquisition"):
            mod.verify(self.private, self.approval)

    def test_custody_source_and_receipt_must_not_be_symlinks(self):
        self.fetch()
        for name in (mod.XML_NAME, mod.RECEIPT_NAME):
            with self.subTest(name=name):
                path = self.private / name
                copy_path = self.private / ("indirect-" + name)
                path.rename(copy_path)
                try:
                    path.symlink_to(copy_path)
                except OSError:
                    self.skipTest("Symlinks unavailable on this platform")
                with self.assertRaisesRegex(ValueError, "symbolic links"):
                    mod.verify(self.private, self.approval)
                path.unlink()
                copy_path.rename(path)

    def test_source_change_invalidates_stored_receipt(self):
        self.fetch()
        (self.private / mod.XML_NAME).write_bytes(
            ORIGINAL.replace(b"Artificial fixture.", b"Tampered fixture. "))
        with self.assertRaises(ValueError):
            mod.verify(self.private, self.approval)


if __name__ == "__main__":
    unittest.main()
