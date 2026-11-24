"""R005 C8 clinical priority tradeoff: provenance and adversarial state guards.

Fixtures are manipulated *synthetically*. Passing tests is not scientific review.
"""
from __future__ import annotations

import copy
import json
import pathlib
import unittest
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parents[1]
OBS = ROOT / "research/searches/auditory/c8-clinical-priority-tradeoff-2026-11-10/OBSERVATIONS.json"
DOIS = {"10.3390/healthcare13233033", "10.1016/j.bjao.2025.100379"}


def audit(obs: dict) -> list[str]:
    errors: list[str] = []
    if obs.get("schema") != "mhac-r005-c8-clinical-priority-tradeoff/1" or obs.get("issue") != 5:
        errors.append("record_identity")
    if obs.get("protocol") != "PROTOCOL-v1" or obs.get("cutoff") != "2026-10-04":
        errors.append("frozen_protocol")
    actor = obs.get("actor", {})
    if actor.get("human_verification") is not False or actor.get("independent_human_review") is not False:
        errors.append("human_provenance")
    ret = obs.get("retrieval_integrity", {})
    for field in ("canonical_search_runs_added", "canonical_search_hits_added",
                  "canonical_screening_decisions_added", "independent_studies_admitted",
                  "independent_samples_admitted"):
        if ret.get(field) != 0:
            errors.append("unearned_admission:" + field)
    for field in ("ordered_web_result_export", "original_http_response_bytes",
                  "original_pdf_bytes", "server_http_status_confirmed",
                  "complete_primary_pdf_read", "baseline_counts_recomputed"):
        if ret.get(field) is not False:
            errors.append("access_overclaim:" + field)
    for field in ("original_http_sha256", "source_pdf_sha256"):
        if ret.get(field) is not None:
            errors.append("invented_hash:" + field)
    p = obs.get("protocol_controls", {})
    if (p.get("channel") != "C8 only" or p.get("formal_c9_complete") is not False
            or p.get("frozen_cutoff") != "2026-10-04"
            or p.get("eq1_checkpoint") != "2026-11-03 final sorted EQ1 prefix 4200/9368; not remeasured"):
        errors.append("channel_promotion")
    attempt = obs.get("c1_attempt", {})
    if (attempt.get("server_http_status") is not None or attempt.get("quota_remaining") is not None
            or attempt.get("response_sha256") is not None or attempt.get("eq1_executed") is not False):
        errors.append("fabricated_api_success")
    sources = obs.get("source_routes", [])
    dois = [s.get("doi") for s in sources]
    if len(sources) != 2 or set(dois) != DOIS or len(dois) != len(set(dois)):
        errors.append("publication_identity")
    else:
        for source in sources:
            if date.fromisoformat(source["publication_date"]) > date(2026, 10, 4):
                errors.append("future_publication")
            if not source.get("locators") or not source.get("reading_extent"):
                errors.append("missing_source_scope")
        h = next(s for s in sources if s["doi"] == "10.3390/healthcare13233033")
        sr = next(s for s in sources if s["doi"] == "10.1016/j.bjao.2025.100379")
        data = h.get("author_reported_not_independently_extracted", {})
        npre, npost, missing = (data.get("participants_pre"), data.get("participants_paired_post"),
                                 data.get("not_paired_post"))
        if (npre, npost, missing) != (90, 77, 13) or npre != npost + missing:
            errors.append("participant_attrition")
        if data.get("same_people_two_phases") is not True or data.get("distinct_experimental_samples_claimed") is not None:
            errors.append("duplicate_people")
        if data.get("per_priority_sound_trials_per_phase") != 77 * 3:
            errors.append("trial_denominator")
        outcomes = data.get("outcomes", [])
        if len(outcomes) != 6 or any(o.get("truth_class") != "author_reported_only" for o in outcomes):
            errors.append("unearned_outcome_verification")
        groups = [o for o in outcomes if "per_phase_trials" in o]
        if (len(groups) != 3 or any(o.get("per_phase_trials") != 231 for o in groups)
                or any(not (0 <= o["old_correct"] <= 231 and 0 <= o["new_correct"] <= 231)
                       for o in groups)):
            errors.append("per_priority_integrity")
        rr = next((o for o in outcomes if o.get("label") == "all-priority recognition rate ratio"), {})
        ci = rr.get("ci_95", [])
        if not (len(ci) == 2 and ci[0] < 1 < ci[1]):
            errors.append("overall_null_ambiguity")
        shin = sr.get("author_reported_not_independently_extracted", {})
        if shin.get("participants_total") != 45 or shin.get("clinicians", 0) + shin.get("nonclinicians", 0) != 45:
            errors.append("shins_sample")
        if "abstract" not in sr.get("reading_extent", "").lower() or "no complete PDF" not in sr.get("reading_extent", ""):
            errors.append("shins_access")
    contrast = obs.get("cross_source_interpretation", {})
    if contrast.get("classification") != "hypothesis-generating contrast, not a meta-analysis, matched replication, or cross-paper pooled study":
        errors.append("unsupported_comparison")
    if not obs.get("handoff"):
        errors.append("missing_downstream_handoff")
    return errors


class R005ClinicalPriorityTradeoffTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(OBS.read_text(encoding="utf-8"))

    def bad(self, mutate, expected):
        data = copy.deepcopy(self.original)
        mutate(data)
        self.assertIn(expected, audit(data))

    def test_original_bounded_shard_is_structurally_valid(self):
        self.assertEqual(audit(self.original), [])

    def test_no_fabricated_independent_samples(self):
        self.bad(lambda d: d["retrieval_integrity"].__setitem__("independent_samples_admitted", 2),
                 "unearned_admission:independent_samples_admitted")

    def test_no_unverified_human_review(self):
        self.bad(lambda d: d["actor"].__setitem__("human_verification", True), "human_provenance")

    def test_no_fictional_source_bytes(self):
        self.bad(lambda d: d["retrieval_integrity"].__setitem__("source_pdf_sha256", "0" * 64),
                 "invented_hash:source_pdf_sha256")

    def test_no_fabricated_original_pdf_reading(self):
        self.bad(lambda d: d["retrieval_integrity"].__setitem__("complete_primary_pdf_read", True),
                 "access_overclaim:complete_primary_pdf_read")

    def test_no_completing_c9_from_unselected_report(self):
        self.bad(lambda d: d["protocol_controls"].__setitem__("formal_c9_complete", True), "channel_promotion")

    def test_no_fake_openalex_run_or_quota(self):
        self.bad(lambda d: d["c1_attempt"].__setitem__("quota_remaining", 999), "fabricated_api_success")

    def test_cutoff_does_not_move(self):
        self.bad(lambda d: d.__setitem__("cutoff", "2026-11-10"), "frozen_protocol")

    def test_no_collision_between_two_dois(self):
        self.bad(lambda d: d["source_routes"][1].__setitem__("doi", d["source_routes"][0]["doi"]),
                 "publication_identity")

    def test_same_seventy_seven_not_doubled(self):
        self.bad(lambda d: d["source_routes"][0]["author_reported_not_independently_extracted"].__setitem__(
            "distinct_experimental_samples_claimed", 2), "duplicate_people")

    def test_sound_trials_are_not_people(self):
        self.bad(lambda d: d["source_routes"][0]["author_reported_not_independently_extracted"].__setitem__(
            "per_priority_sound_trials_per_phase", 77), "trial_denominator")

    def test_absent_participant_not_silently_added(self):
        self.bad(lambda d: d["source_routes"][0]["author_reported_not_independently_extracted"].__setitem__(
            "not_paired_post", 12), "participant_attrition")

    def test_unearned_quantitative_extraction(self):
        self.bad(lambda d: d["source_routes"][0]["author_reported_not_independently_extracted"]["outcomes"][0].__setitem__(
            "truth_class", "verified_effect"), "unearned_outcome_verification")

    def test_overall_interval_not_promoted_to_clear_superiority(self):
        self.bad(lambda d: d["source_routes"][0]["author_reported_not_independently_extracted"]["outcomes"][2].__setitem__(
            "ci_95", [1.02, 1.04]), "overall_null_ambiguity")

    def test_cross_publication_pooling_is_prohibited(self):
        self.bad(lambda d: d["cross_source_interpretation"].__setitem__(
            "classification", "meta-analysis"), "unsupported_comparison")

    def test_abstract_is_not_fulltext(self):
        self.bad(lambda d: d["source_routes"][1].__setitem__(
            "reading_extent", "full original PDF with figures"), "shins_access")


if __name__ == "__main__":
    unittest.main()
