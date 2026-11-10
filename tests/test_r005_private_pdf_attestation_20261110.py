"""R005 private source attestation negative controls; synthetic fake PDF only. Refs #5."""
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/sources/auditory/scripts/attest_primary_pdf.py"
spec = importlib.util.spec_from_file_location("r005_attest_primary_pdf", SCRIPT)
attest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(attest)


class PrivatePdfAttestationTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.pdf = self.root / "SYNTHETIC-NOT-A-SCHOLARLY-SOURCE.pdf"
        self.pdf.write_bytes(b"%PDF-1.4\n" + b"fictional test only\n" * 6 + b"%%EOF\n")
        self.receipt = self.root / "receipt.json"
        self.argv = [
            "capture", "--file", str(self.pdf), "--manifest", str(self.receipt),
            "--doi", "10.1145/3706066", "--edition", "Fictional test file, no article",
            "--source-url", "https://example.org/fake.pdf",
            "--rights-url", "https://example.org/rights",
            "--acquired-at", (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
            "--access-proof", "synthetic fixture only", "--rights-note", "synthetic",
            "--reading-boundary", "no research reading", "--actor", "unit-test-agent",
        ]

    def arg_changed(self, key, value):
        args = self.argv.copy()
        args[args.index("--" + key) + 1] = value
        return args

    def test_capture_then_verify_no_source_bytes_or_local_path(self):
        self.assertEqual(attest.main(self.argv), 0)
        record = json.loads(self.receipt.read_text())
        self.assertEqual(record["schema"], attest.SCHEMA)
        self.assertEqual(record["frozen_cutoff"], "2026-10-04")
        self.assertEqual(record["admitted_studies_experiments_samples"], [0, 0, 0])
        self.assertFalse(record["human_reviewer_claimed"])
        self.assertFalse(record["original_pdf_retained_in_manifest"])
        self.assertFalse(record["verified_licence_or_source_URL"])
        self.assertNotIn(str(self.pdf), self.receipt.read_text())
        self.assertEqual(attest.main(["verify", "--file", str(self.pdf), "--manifest", str(self.receipt)]), 0)

    def test_capture_is_append_only(self):
        self.assertEqual(attest.main(self.argv), 0)
        self.assertEqual(attest.main(self.argv), 2)

    def test_altered_original_bytes_refused(self):
        self.assertEqual(attest.main(self.argv), 0)
        self.pdf.write_bytes(self.pdf.read_bytes() + b"extra data")
        self.assertEqual(attest.main(["verify", "--file", str(self.pdf), "--manifest", str(self.receipt)]), 2)

    def test_non_pdf_rejected(self):
        self.pdf.write_bytes(b"not a PDF" * 30)
        self.assertEqual(attest.main(self.argv), 2)

    def test_missing_original_rejected(self):
        self.pdf.unlink()
        self.assertEqual(attest.main(self.argv), 2)

    def test_naive_timestamp_rejected(self):
        self.assertEqual(attest.main(self.arg_changed("acquired-at", "2026-11-10T12:00:00")), 2)

    def test_future_acquisition_rejected(self):
        value = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        self.assertEqual(attest.main(self.arg_changed("acquired-at", value)), 2)

    def test_missing_rights_rejected(self):
        self.assertEqual(attest.main(self.arg_changed("rights-note", " ")), 2)

    def test_insecure_url_rejected(self):
        self.assertEqual(attest.main(self.arg_changed("source-url", "http://example.org/fake.pdf")), 2)

    def test_url_with_credentials_rejected(self):
        self.assertEqual(attest.main(self.arg_changed("rights-url", "https://user:secret@example.org")), 2)

    def test_hash_tamper_rejected(self):
        self.assertEqual(attest.main(self.argv), 0)
        data = json.loads(self.receipt.read_text())
        data["original_pdf_sha256"] = "0" * 64
        self.receipt.write_text(json.dumps(data))
        self.assertEqual(attest.main(["verify", "--file", str(self.pdf), "--manifest", str(self.receipt)]), 2)

    def test_unrecognized_receipt_schema_rejected(self):
        self.assertEqual(attest.main(self.argv), 0)
        data = json.loads(self.receipt.read_text())
        data["status"] = "canonical_screening_include"
        self.receipt.write_text(json.dumps(data))
        self.assertEqual(attest.main(["verify", "--file", str(self.pdf), "--manifest", str(self.receipt)]), 2)


if __name__ == "__main__":
    unittest.main()
