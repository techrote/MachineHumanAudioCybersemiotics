"""Synthetic-only negative controls for R005 original MATLAB method-source audit.

No actual human, waveform, effect or R006 scientific decision is represented.
"""
import copy
import json
import math
import unittest
from pathlib import Path


RECORD = (Path(__file__).resolve().parents[1] / "research" / "sources" /
          "auditory" / "sabic2021-original-matlab-audit-20261111" /
          "OBSERVATIONS.json")


def rms(samples):
    if not samples:
        raise ValueError("Empty synthetic signal")
    return math.sqrt(sum(float(x) ** 2 for x in samples) / len(samples))


def normalized_peak(samples):
    value = rms(samples)
    if value == 0:
        raise ValueError("Silent synthetic signal has undefined normalization")
    return max(abs(float(x)) / value for x in samples)


def check_nonadmission(record):
    assert record["issue"] == 5
    assert record["downstream_issue"] == 6
    assert record["frozen_publication_cutoff"] == "2026-10-04"
    assert record["publication"]["doi"] == "10.1177/0018720819879311"
    assert record["publication"]["source_id"] == "SRC-R006-H-SABIC-UNDERSTANDING@1"
    source = record["author_code"]
    assert source["commit_sha"] == "e5f8bf29ad225fa15d8969db40ce2b03b4295821"
    assert source["git_blob_sha1"] == "3ff7a5d2da362cc2d3d332432c9d41b3606b628e"
    assert source["lines"]["first_pass_hardcoded_read"] == 13
    assert source["lines"]["second_pass_indexed_read"] == 35
    finding = record["finding"]
    for key in ("source_code_executed_for_study",):
        assert finding[key] == "unknown"
    for key in ("original_audio_bytes_available", "original_audio_played",
                "published_results_recomputed", "scientific_eligibility_decided",
                "independent_human_review", "rights_approval_granted"):
        assert finding[key] is False
    assert "synthetic" in finding["synthetic_counterexample"].lower() or "File 1" in finding["synthetic_counterexample"]
    canonical = record["canonical_r006_checkpoint"]
    assert canonical["title_abstract"] == 9
    assert (canonical["full_text_pending"], canonical["awaiting_text"],
            canonical["full_text_exclude"], canonical["full_text_include"]) == (5, 3, 1, 0)
    assert canonical["delta"] == 0
    assert sum(canonical[k] for k in ("admitted_publications", "admitted_studies",
                                     "admitted_experiments", "admitted_samples")) == 0


class PrimaryMethodSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observed = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_original_publication_and_blob_pins_without_added_study(self):
        check_nonadmission(self.observed)

    def test_synthetic_peak_failure_for_nonfirst_file(self):
        first = [1.0, -1.0]
        second = [1.0, 0.0, 0.0, 0.0]
        self.assertEqual(rms(first), 1.0)
        self.assertEqual(rms(second), 0.5)
        first_loop_global_scale = normalized_peak(first)  # 1.wav in EVERY slot
        actual_global_scale = max(normalized_peak(first), normalized_peak(second))
        self.assertEqual(first_loop_global_scale, 1.0)
        self.assertEqual(actual_global_scale, 2.0)
        self.assertGreater(normalized_peak(second) / first_loop_global_scale, 1.0)
        self.assertEqual(normalized_peak(second) / actual_global_scale, 1.0)

    def test_negative_control_falsely_claiming_original_audio(self):
        modified = copy.deepcopy(self.observed)
        modified["finding"]["original_audio_played"] = True
        with self.assertRaises(AssertionError):
            check_nonadmission(modified)

    def test_negative_control_falsely_claiming_screening_or_licence(self):
        for flag in ("scientific_eligibility_decided", "rights_approval_granted",
                     "independent_human_review"):
            with self.subTest(flag=flag):
                modified = copy.deepcopy(self.observed)
                modified["finding"][flag] = True
                with self.assertRaises(AssertionError):
                    check_nonadmission(modified)

    def test_negative_control_source_or_protocol_drift(self):
        for path, replacement in (
            (("author_code", "git_blob_sha1"), "0" * 40),
            (("publication", "doi"), "10.0000/fabricated"),
            (("canonical_r006_checkpoint", "admitted_samples"), 1),
            (("frozen_publication_cutoff",), "2026-11-11")
        ):
            with self.subTest(path=path):
                modified = copy.deepcopy(self.observed)
                node = modified
                for segment in path[:-1]:
                    node = node[segment]
                node[path[-1]] = replacement
                with self.assertRaises(AssertionError):
                    check_nonadmission(modified)


if __name__ == "__main__":
    unittest.main()
