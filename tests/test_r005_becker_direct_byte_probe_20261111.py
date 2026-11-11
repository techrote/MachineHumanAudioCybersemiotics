"""Offline R005 bounded original HTTP response attestation and negative guards.

Only the immutable GitHub Actions source job proves the real 2026-11-11
HTTP acquisition. These tests verify that its published receipt cannot
silently drift into claims of custody, human reading, screening or samples.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "research/sources/auditory/becker-original-byte-2026-11-11/OBSERVATIONS.json"
OLDER = ROOT / "research/sources/auditory/r006-primary-support-2026-11-10/BECKER-2025.json"
URL = "https://www2.informatik.uni-hamburg.de/wtm/publications/2025/BBCKOAGSFW25/3706066.pdf"
SHA = "e5a2429e47e15208e285c4f3c1aa35e86529b0591139ff36d46e94babe42f230"


def validate_receipt(r):
    assert r["schema"] == "mhac-r005-public-pdf-direct-probe/1"
    assert (r["issue"], r["downstream_issue"], r["doi"], r["frozen_cutoff"]) == (
        5, 6, "10.1145/3706066", "2026-10-04")
    assert r["url"] == URL
    assert r["http"]["effective_url"] == URL
    assert r["http"]["status"] == 200
    assert r["http"]["content_type"] == "application/pdf"
    assert r["http"]["pdf_magic"] is True
    assert r["http"]["raw_body_sha256"] == SHA
    assert len(bytes.fromhex(r["http"]["raw_body_sha256"])) == 32
    assert r["http"]["original_body_bytes"] == r["http"]["content_length_header"] == 10436314
    assert r["http"]["request_utc"] == "2026-11-11T01:20:21.272933+00:00"
    assert r["http"]["response_http_date"] == "Wed, 11 Nov 2026 01:20:21 GMT"
    assert r["receipt_source"]["exact_probe_head"] == "33b25580a347e4866c0ce4a92a8faf8c8831f8a8"
    assert r["access_boundary"]["full_original_retained"] is False
    assert r["access_boundary"]["private_retention_authorized"] is False
    assert r["access_boundary"]["original_contents_read_by_direct_probe"] is False
    assert r["access_boundary"]["audio_files_listened"] is False
    assert r["access_boundary"]["source_hash_confirms_edition_text_semantics"] is False
    assert r["source_custody_final_gate"] is False
    assert r["canonical_screen_changed"] is False
    assert r["actor"]["human_reviewer"] is False
    assert r["new_canonical_hit_count"] == 0
    assert all(value == 0 for value in r["research_outcomes"].values())
    return True


class R005BeckerDirectReceipt(unittest.TestCase):
    def setUp(self):
        self.r = json.loads(RECEIPT.read_text(encoding="utf8"))

    def test_real_source_receipt_pinned_without_online_request(self):
        self.assertTrue(validate_receipt(self.r))
        prior = json.loads(OLDER.read_text(encoding="utf8"))
        self.assertEqual(prior["source"]["doi"], self.r["doi"])
        self.assertEqual(prior["source"]["lawful_public_pdf_url"], self.r["url"])

    def test_mutated_original_response_hash_fails(self):
        bad = deepcopy(self.r)
        bad["http"]["raw_body_sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            validate_receipt(bad)

    def test_partial_original_bytes_cannot_masquerade_as_full(self):
        bad = deepcopy(self.r)
        bad["http"]["original_body_bytes"] = 5000001
        with self.assertRaises(AssertionError):
            validate_receipt(bad)

    def test_no_promoted_custody_or_source_reading(self):
        for field in ("full_original_retained", "private_retention_authorized",
                      "original_contents_read_by_direct_probe", "audio_files_listened"):
            bad = deepcopy(self.r)
            bad["access_boundary"][field] = True
            with self.subTest(field=field), self.assertRaises(AssertionError):
                validate_receipt(bad)

    def test_no_fake_human_or_canonical_admission(self):
        for path in (("actor", "human_reviewer"), ("research_outcomes", "new_admitted_studies"),
                     ("research_outcomes", "new_independent_samples"),
                     ("research_outcomes", "new_eligible_publications")):
            bad = deepcopy(self.r)
            bad[path[0]][path[1]] = True if path[0] == "actor" else 1
            with self.subTest(path=path), self.assertRaises(AssertionError):
                validate_receipt(bad)

    def test_no_relabelled_identity_or_new_hits(self):
        for field, change in (("doi", "10.1145/3711938"), ("frozen_cutoff", "2026-11-11"),
                              ("new_canonical_hit_count", 100)):
            bad = deepcopy(self.r)
            bad[field] = change
            with self.subTest(field=field), self.assertRaises(AssertionError):
                validate_receipt(bad)
