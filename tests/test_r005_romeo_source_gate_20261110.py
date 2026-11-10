"""Fail-closed provenance guards for bounded R005 Romeo source-access observations.

These are structural tests, not source verification or eligibility adjudication.
Refs #5; downstream #6.
"""
from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

OBS = (
    Path(__file__).resolve().parents[1]
    / "research/sources/auditory/r006-romeo-source-gate-2026-11-10/OBSERVATIONS.json"
)


def validate_record(d):
    if d["schema"] != "mhac-r005-romeo-access-boundary/1" or d["issue"] != 5 or d["downstream_issue"] != 6:
        raise ValueError("incorrect bounded R005 provenance identity")
    if d["status"] != "source_access_checkpoint_not_search_export_or_canonical_screen":
        raise ValueError("source observation promoted to accepted screening")
    if not re.fullmatch(r"[0-9a-f]{40}", d["base_main_sha"]):
        raise ValueError("base SHA absent")
    if d["frozen_search_cutoff"] != "2026-10-04":
        raise ValueError("frozen cutoff changed")
    if not d["record_assembled_at_utc"].startswith("2026-11-10T") or "not an HTTP Date" not in d["time_note"]:
        raise ValueError("timestamp provenance missing")
    actor = d["researcher"]
    if actor["kind"] != "agent" or actor["independent_human_review"] is not False:
        raise ValueError("false human-review attribution")
    sources = {s["id"]: s for s in d["sources"]}
    if set(sources) != {"romeo_2023_ieee", "romeo_2023_supplement", "romeo_2025_acm"}:
        raise ValueError("publication and file identities conflated")
    if sources["romeo_2023_ieee"]["doi"] != "10.1109/ro-man57019.2023.10309631":
        raise ValueError("wrong conference DOI")
    if sources["romeo_2025_acm"]["doi"] != "10.1145/3711938":
        raise ValueError("wrong journal DOI")
    supplement = sources["romeo_2023_supplement"]
    if supplement["doi"] != "10.5281/zenodo.8042317" or supplement["parent_publication"] != "romeo_2023_ieee":
        raise ValueError("Zenodo identity or provenance changed")
    if supplement["advertised_filename"] != "ROMAN2023_Ila_Marta.pdf":
        raise ValueError("unverified different file")
    if supplement["advertised_md5"] != "7137b64efa2e75ab9aec951ca03449fe":
        raise ValueError("repository-listed hash changed; refresh source first")
    for flag in ("advertised_md5_independently_verified", "full_file_read", "original_file_bytes_retained", "raw_response_hashed"):
        if supplement[flag] is not False:
            raise ValueError("supplementary file verification invented")
    for src in (sources["romeo_2023_ieee"], sources["romeo_2025_acm"]):
        for flag in ("full_text_read", "original_file_bytes_retained", "source_sha256_verified"):
            if src[flag] is not False:
                raise ValueError("reading or source bytes upgraded without evidence")
    if sources["romeo_2025_acm"]["page_images_verified"] is not False:
        raise ValueError("2025 image verification falsely claimed")
    if sources["romeo_2025_acm"]["audio_files_heard"] is not False:
        raise ValueError("audio evidence invented")
    if "33:5" not in sources["romeo_2025_acm"]["locator"] or "33:21" not in sources["romeo_2025_acm"]["locator"]:
        raise ValueError("primary-text locators lost")
    attempts = d["access_attempts"]
    if len(attempts) < 6 or not all(a["date_utc"] == "2026-11-10" for a in attempts):
        raise ValueError("retrieval-attempt coverage incomplete")
    if not any("Unicode decoding error" in a["result"] for a in attempts):
        raise ValueError("failed Zenodo source access hidden")
    if not any("page-image" in a["result"] and "403" in a["result"] for a in attempts):
        raise ValueError("image-based source verification wrongly implied")
    if not any("download tool failed" in a["result"] for a in attempts):
        raise ValueError("failed original-byte acquisition hidden")
    ids = {x["id"] for x in d["existing_discovery_ids"]}
    if ids != {
        "HIT-R004-LK3-VOICE-NATURALNESS-TRUST-02@1",
        "HIT-R004-G06-07@1",
        "HIT-R004-LK3-VOICE-REPAIR-TRUST-01@1",
    }:
        raise ValueError("existing discovery identities distorted")
    b = d["source_boundary"]
    expected = {
        "publications_distinct_dois": True,
        "supplement_is_independent_publication": False,
        "supplement_is_new_study": False,
        "stimulus_reuse_proven": False,
        "participant_overlap_known": False,
        "independent_sample_admission": False,
        "accepted_eligibility_decision": False,
        "canonical_scr_created": 0,
        "canonical_study_created": 0,
        "canonical_sample_created": 0,
        "new_database_search_occurrences": 0,
        "publisher_database_export_obtained": False,
    }
    if b != expected:
        raise ValueError("unsupported scientific count, study identity or eligibility promotion")
    if "R006" not in d["R006_handoff"] or "Integration" not in d["Integration_handoff"]:
        raise ValueError("cross-lane handoff absent")


class Romeo2023SourceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(OBS.read_text(encoding="utf-8"))

    def test_valid_observation_is_noncanonical(self):
        validate_record(self.record)

    def assert_rejects_mutation(self, mutate):
        d = copy.deepcopy(self.record)
        mutate(d)
        with self.assertRaises(ValueError):
            validate_record(d)

    def test_no_fabricated_human_screening(self):
        self.assert_rejects_mutation(lambda d: d["researcher"].update(independent_human_review=True))

    def test_no_source_pdf_fulltext_promotion(self):
        self.assert_rejects_mutation(lambda d: d["sources"][0].update(full_text_read=True))

    def test_no_zenodo_md5_hash_fabrication(self):
        self.assert_rejects_mutation(lambda d: d["sources"][1].update(advertised_md5_independently_verified=True))

    def test_no_supplement_as_study(self):
        self.assert_rejects_mutation(lambda d: d["source_boundary"].update(supplement_is_new_study=True))

    def test_no_unproven_stimulus_reuse(self):
        self.assert_rejects_mutation(lambda d: d["source_boundary"].update(stimulus_reuse_proven=True))

    def test_no_unverified_sample_independence(self):
        self.assert_rejects_mutation(lambda d: d["source_boundary"].update(independent_sample_admission=True))

    def test_no_fabricated_scr(self):
        self.assert_rejects_mutation(lambda d: d["source_boundary"].update(canonical_scr_created=1))

    def test_no_invented_c1_export(self):
        self.assert_rejects_mutation(lambda d: d["source_boundary"].update(publisher_database_export_obtained=True))

    def test_no_wrong_version_doi(self):
        self.assert_rejects_mutation(lambda d: d["sources"][1].update(doi="10.5281/zenodo.8042316"))

    def test_no_vanishing_download_failure(self):
        self.assert_rejects_mutation(lambda d: d["access_attempts"].pop(4))

    def test_no_fabricated_page_image_check(self):
        self.assert_rejects_mutation(lambda d: d["sources"][2].update(page_images_verified=True))

    def test_no_changed_frozen_cutoff(self):
        self.assert_rejects_mutation(lambda d: d.update(frozen_search_cutoff="2026-11-10"))

    def test_no_relabelled_original_hits(self):
        self.assert_rejects_mutation(lambda d: d["existing_discovery_ids"][0].update(id="HIT-R005-FAKE@1"))


if __name__ == "__main__":
    unittest.main()
