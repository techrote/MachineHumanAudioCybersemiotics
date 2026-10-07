"""Relationship regressions built from the preserved, explicitly synthetic case."""
from __future__ import annotations

from copy import deepcopy
import unittest

from schemas import ValidationError
from tools.build_record_fixtures import snapshots
from tools.record_graph import pin, validate_graph


def ref(rid: str, rev: int = 1) -> dict:
    return {"id": rid, "rev": rev}


class GraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples = snapshots()

    def setUp(self):
        self.data = deepcopy(self.examples["valid_before"])

    def record(self, rid):
        return next(row for row in self.data["records"] if row["id"] == rid)

    def body(self, rid, number=-1):
        return self.record(rid)["revisions"][number]["data"]

    def basis(self, rid, number=-1):
        return self.record(rid)["revisions"][number]["basis"]

    def graph(self):
        return validate_graph(self.data["records"])

    def append(self, rid, changes, *, at="2000-01-01T01:00:00Z"):
        row = self.record(rid)
        revision = deepcopy(row["revisions"][-1])
        revision["rev"] += 1
        revision["at"] = at
        revision["data"].update(changes)
        row["revisions"].append(revision)
        return revision

    def amendment(self, rid, *, kind, targets, replacements=(), status="applied", materiality="material", at="2000-01-01T02:00:00Z"):
        row = deepcopy(next(row for row in self.examples["valid_corrected"]["records"] if row["id"] == "AMD-FIX-LAT"))
        row["id"] = rid
        revision = row["revisions"][0]
        revision["at"] = at
        revision["data"].update(kind=kind, target_refs=list(targets), replacement_refs=list(replacements), status=status, materiality=materiality)
        self.data["records"].append(row)
        return row

    def assert_invalid(self, code):
        with self.assertRaisesRegex(ValidationError, code):
            self.graph()

    def audit_claim(self, *, target="CLM-LAT", change_statement=False):
        audit = deepcopy(self.record("AID-CHECK-LAT"))
        audit["id"] = "AID-AUDIT"
        revision = audit["revisions"][0]
        revision["at"] = "2000-01-01T00:30:00Z"
        revision["basis"] = [ref(target, 2)]
        revision["data"].update(scope="internal_audit", target_refs=[ref(target, 2)], performed_at={"state": "known", "value": revision["at"]})
        self.data["records"].append(audit)
        claim = self.append("CLM-LAT", {"lifecycle": "internally_audited"})
        claim["data"]["review_refs"].append(ref("AID-AUDIT"))
        claim["basis"].append(ref("AID-AUDIT"))
        if change_statement:
            claim["data"]["statement"] = "A materially changed synthetic assertion not covered by the prior audit."
        return claim

    def test_duplicate_logical_owner_rejected(self):
        self.data["records"].append(deepcopy(self.record("SRC-A")))
        self.assert_invalid("DUPLICATE_ID")

    def test_missing_semantic_basis_cannot_disable_invalidation(self):
        self.record("EX-LAT")["revisions"][0]["basis"].remove(ref("SRC-A"))
        self.assert_invalid("MISSING_BASIS")

    def test_dangling_exact_revision_rejected(self):
        self.basis("SRC-A").append(ref("SRC-MISSING", 9))
        self.assert_invalid("DANGLING_REFERENCE")

    def test_wrong_typed_sample_reference_rejected(self):
        self.body("EX-LAT")["sample_ref"] = ref("STUDY-ONE")
        self.basis("EX-LAT").append(ref("STUDY-ONE"))
        self.assert_invalid("REFERENCE_TYPE")

    def test_evidence_cycle_rejected(self):
        source = self.record("SRC-A")["revisions"][0]
        source["at"] = self.record("AID-READ-A")["revisions"][0]["at"]
        source["basis"].append(ref("AID-READ-A"))
        self.assert_invalid("DEPENDENCY_CYCLE")

    def test_future_recorded_support_rejected(self):
        self.basis("SRC-A").append(ref("EX-ACC"))
        self.assert_invalid("FUTURE_BASIS")

    def test_reciprocal_publication_membership_is_not_an_evidence_cycle(self):
        self.body("SRC-A")["family_links"] = [{"relation": "companion_of", "source_ref": ref("SRC-B"), "reason": "Synthetic companion report."}]
        self.body("SRC-B")["family_links"] = [{"relation": "companion_of", "source_ref": ref("SRC-A"), "reason": "Synthetic companion report."}]
        self.assertFalse(self.graph().stale)

    def test_resolved_identity_requires_located_support(self):
        self.body("STUDY-ONE")["identity_status"] = "resolved"
        self.assert_invalid("UNSUPPORTED_IDENTITY")

    def test_explicit_identity_evidence_propagates_correction(self):
        self.data = deepcopy(self.examples["valid_source_invalidated"])
        locator = deepcopy(self.body("EX-LAT", 0)["locator"])
        self.body("STUDY-ONE")["identity_locators"] = [{"source_ref": ref("SRC-A"), "locator": locator}]
        self.basis("STUDY-ONE").append(ref("SRC-A"))
        # An explicit supported EXP interpretation can depend on that decision;
        # bare membership alone remains non-evidential.
        self.basis("EXP-ONE").append(ref("STUDY-ONE"))
        graph = self.graph()
        self.assertIn(("CLM-ACC", 2), graph.stale)

    def test_material_extraction_change_needs_applied_amendment(self):
        self.data = deepcopy(self.examples["valid_corrected"])
        self.data["records"] = [row for row in self.data["records"] if row["kind"] != "amendment"]
        self.assert_invalid("MISSING_CORRECTION_AMENDMENT")

    def test_material_sample_correction_cannot_leave_older_support_current(self):
        self.append("SAMPLE-ONE", {"n": 12})
        self.assert_invalid("MISSING_CORRECTION_AMENDMENT")
        self.amendment("AMD-SAMPLE-FIX", kind="record_correction", targets=[ref("SAMPLE-ONE")], replacements=[ref("SAMPLE-ONE", 2)])
        graph = self.graph()
        self.assertIn(("EXP-ONE", 1), graph.stale)
        with self.assertRaisesRegex(ValidationError, "STALE_RELEASE"):
            graph.require_current(ref("CLM-LAT", 2), "claim")

    def test_material_experiment_definition_change_requires_correction(self):
        new = self.append("EXP-ONE", {})
        new["data"]["outcomes"]["latency"]["unit"] = "s"
        self.assert_invalid("MISSING_CORRECTION_AMENDMENT")
        self.amendment("AMD-EXPERIMENT-FIX", kind="record_correction", targets=[ref("EXP-ONE")], replacements=[ref("EXP-ONE", 2)])
        graph = self.graph()
        self.assertIn(("EX-LAT", 1), graph.stale)

    def test_theoretical_assertion_correction_requires_same_history_discipline(self):
        self.data = deepcopy(self.examples["valid_all_families"])
        self.append("TX-CONTEXT", {"assertion": "A corrected fictional theoretical assertion."})
        self.assert_invalid("MISSING_CORRECTION_AMENDMENT")
        self.amendment("AMD-THEORY-FIX", kind="record_correction", targets=[ref("TX-CONTEXT")], replacements=[ref("TX-CONTEXT", 2)])
        graph = self.graph()
        self.assertIn(("TX-CONTEXT", 1), graph.invalidated)
        self.assertNotIn(("TX-CONTEXT", 2), graph.stale)

    def test_explicit_study_identity_change_quarantines_its_experiments(self):
        self.append("STUDY-ONE", {"publications": [ref("SRC-A")]})
        self.assert_invalid("MISSING_CORRECTION_AMENDMENT")
        self.amendment("AMD-STUDY-SPLIT", kind="identity_split", targets=[ref("STUDY-ONE")], replacements=[ref("STUDY-ONE", 2)])
        graph = self.graph()
        self.assertNotIn(("STUDY-ONE", 1), graph.basis[("EXP-ONE", 1)])
        self.assertIn(("STUDY-ONE", 1), graph.currency_edges[("EXP-ONE", 1)])
        self.assertIn(("CLM-LAT", 2), graph.stale)
        self.assertIn(("CLM-ACC", 2), graph.stale)

    def test_withdrawn_identity_resolution_is_not_ignored_by_old_pins(self):
        self.append("STUDY-ONE", {"identity_status": "unresolved"})
        graph = self.graph()
        self.assertIn(("STUDY-ONE", 1), graph.invalidated)
        self.assertIn(("CLM-ACC", 2), graph.stale)

    def test_proposed_invalidation_is_pending_without_quarantine(self):
        self.amendment("AMD-PENDING", kind="source_invalidation", targets=[ref("SRC-A")], status="proposed")
        self.assertFalse(self.graph().stale)

    def test_later_amendment_revision_cannot_erase_applied_invalidation(self):
        self.data = deepcopy(self.examples["valid_corrected"])
        correction = self.append("EX-ACC", {"value": 99.0})
        amendment = self.append("AMD-FIX-LAT", {"target_refs": [ref("EX-ACC")], "replacement_refs": [ref("EX-ACC", 2)], "status": "verified"}, at="2000-01-01T02:00:00Z")
        self.assertGreater(amendment["at"], correction["at"])
        graph = self.graph()
        self.assertIn(("EX-LAT", 1), graph.invalidated)
        self.assertIn(("EX-ACC", 1), graph.invalidated)

    def test_initially_withdrawn_source_cannot_support_current_claim(self):
        self.body("SRC-A")["validity"] = "withdrawn"
        graph = self.graph()
        self.assertIn(("SRC-A", 1), graph.invalidated)
        with self.assertRaisesRegex(ValidationError, "STALE_RELEASE"):
            graph.require_current(ref("CLM-LAT", 2), "claim")
        graph.require_current(ref("CLM-ACC", 2), "claim")

    def test_initially_withdrawn_extraction_quarantines_support(self):
        self.body("EX-LAT")["status"] = "withdrawn"
        graph = self.graph()
        with self.assertRaisesRegex(ValidationError, "STALE_RELEASE"):
            graph.require_current(ref("CLM-LAT", 2), "claim")

    def test_current_claim_withdrawal_cannot_be_evaded_with_older_pin(self):
        self.append("CLM-LAT", {"lifecycle": "withdrawn"})
        graph = self.graph()
        self.assertIn(("CLM-LAT", 2), graph.invalidated)
        with self.assertRaisesRegex(ValidationError, "STALE_RELEASE"):
            graph.require_current(ref("REQ-TIMING"), "requirement")

    def test_source_invalidation_applies_to_same_bytes_at_older_revision(self):
        self.append("SRC-A", {"access_status": "unavailable", "access_at": "2000-01-01T01:00:00Z", "access_reason": "Synthetic later loss of access."})
        self.amendment("AMD-RETRACTION", kind="source_invalidation", targets=[ref("SRC-A", 2)])
        graph = self.graph()
        self.assertIn(("SRC-A", 1), graph.invalidated)
        self.assertIn(("CLM-LAT", 2), graph.stale)

    def test_losing_access_does_not_erase_prior_reading(self):
        self.append("SRC-A", {"access_status": "unavailable", "access_at": "2000-01-01T01:00:00Z", "access_reason": "Synthetic later access loss."})
        graph = self.graph()
        self.assertFalse(graph.stale)
        graph.require_current(ref("CLM-LAT", 2), "claim")

    def test_changed_source_bytes_cannot_be_marked_nonmaterial(self):
        source = self.append("SRC-A", {})
        source["data"]["manifestations"][0]["sha256"] = "f" * 64
        self.amendment("AMD-TYPO", kind="nonmaterial", targets=[ref("SRC-A")], replacements=[ref("SRC-A", 2)], materiality="nonmaterial")
        self.assert_invalid("FALSE_NONMATERIAL_CORRECTION")

    def test_corrected_source_metadata_can_replace_an_invalid_assertion_with_same_bytes(self):
        self.append("SRC-A", {"title": "Corrected synthetic report identity, with the same retained source bytes."})
        self.amendment("AMD-SOURCE-FIX", kind="source_correction", targets=[ref("SRC-A")], replacements=[ref("SRC-A", 2)])
        graph = self.graph()
        self.assertIn(("SRC-A", 1), graph.invalidated)
        self.assertNotIn(("SRC-A", 2), graph.invalidated)
        graph.require_current(ref("SRC-A", 2), "source")
        with self.assertRaisesRegex(ValidationError, "STALE_RELEASE"):
            graph.require_current(ref("CLM-LAT", 2), "claim")

    def test_selected_reading_requires_actual_readable_access(self):
        self.body("AID-READ-B")["access_at_read"] = "metadata_only"
        self.assert_invalid("FALSE_READING")

    def test_each_numeric_field_locator_must_be_in_read_ranges(self):
        self.body("EX-ACC")["field_locators"]["n"].update(start=3, end=3)
        self.assert_invalid("UNREAD_LOCATOR")

    def test_another_source_reading_does_not_cover_this_extraction(self):
        self.body("EX-LAT")["reading_ref"] = ref("AID-READ-B")
        self.basis("EX-LAT").append(ref("AID-READ-B"))
        self.assert_invalid("READING_SOURCE")

    def test_pdf_coordinate_extent_is_count_not_last_index(self):
        mid = self.body("SRC-A")["manifestations"][0]["id"]
        self.body("SRC-A")["manifestations"][0]["coordinate"] = "pdf_page_0based"
        self.body("AID-READ-A")["ranges"] = [[start - 1, end - 1] for start, end in self.body("AID-READ-A")["ranges"]]
        def convert(value, source_id=None):
            if isinstance(value, dict):
                if "source_ref" in value:
                    source_id = value["source_ref"]["id"]
                if source_id == "SRC-A" and value.get("manifestation_id") == mid and "coordinate" in value:
                    value["coordinate"] = "pdf_page_0based"
                    value["start"] -= 1
                    value["end"] -= 1
                else:
                    for child in value.values():
                        convert(child, source_id)
            elif isinstance(value, list):
                for child in value:
                    convert(child, source_id)
        convert(self.data["records"])
        self.graph()
        self.body("AID-READ-A")["ranges"][-1][1] += 1
        self.assert_invalid("READ_RANGE")

    def test_outcome_n_cannot_exceed_exact_referenced_sample(self):
        self.body("EX-LAT")["n"] = self.body("SAMPLE-ONE")["n"] + 1
        self.assert_invalid("OUTCOME_N")

    def test_unknown_n_is_explicitly_representable(self):
        self.body("EX-LAT")["n"] = {"state": "not_reported", "reason": "Synthetic source does not report the denominator."}
        self.graph()

    def test_zero_participants_cannot_have_known_outcome_estimate(self):
        self.body("EX-LAT")["n"] = 0
        self.assert_invalid("OUTCOME_N")

    def test_conditions_and_timepoints_are_experiment_specific(self):
        self.body("EX-LAT")["conditions"] = ["undeclared-condition"]
        self.assert_invalid("OUTCOME_CONTRAST")
        self.setUp()
        ex = self.body("EX-LAT")
        self.body("EXP-ONE")["outcomes"][ex["outcome"]]["timepoints"] = [ex["timepoint"]]
        ex["timepoint"] = "undeclared-timepoint"
        self.assert_invalid("OUTCOME_TIMEPOINT")

    def test_known_dispersion_cannot_use_an_unrelated_unit(self):
        self.body("EX-LAT")["dispersion"] = {"state": "known", "value": {"measure": "sd", "value": 1.0, "unit": "Hz"}}
        self.assert_invalid("DISPERSION_UNIT")

    def test_known_dependence_cannot_be_relabelled_independent(self):
        self.body("EX-LAT")["dependence"]["relation"] = "independent"
        self.assert_invalid("FALSE_INDEPENDENCE")

    def test_bounded_source_claim_is_not_promoted_to_empirical_finding(self):
        for revision in self.record("CLM-ACC")["revisions"]:
            revision["data"]["class"] = "empirical_finding"
        self.assert_invalid("UNSUPPORTED_FINDING")

    def test_project_constraint_can_be_checked_without_fake_empirical_evidence(self):
        for revision in self.record("CLM-LAT")["revisions"]:
            revision["data"].update({"class": "project_constraint", "decision_artifact": "fixture: explicitly stated project preference", "evidence_refs": [], "appraisal_refs": [], "review_refs": []})
            revision["basis"] = []
        self.graph().require_current(ref("CLM-LAT", 2), "claim")

    def test_exact_internal_audit_preserves_class_and_earlier_target(self):
        self.audit_claim()
        graph = self.graph()
        result = graph.require_current(ref("CLM-LAT", 3), "claim")
        self.assertEqual(result["class"], "empirical_finding")
        self.assertNotIn(("CLM-LAT", 2), graph.stale)

    def test_changed_assertion_does_not_inherit_audit(self):
        self.audit_claim(change_statement=True)
        self.assert_invalid("UNSUPPORTED_PROMOTION")

    def test_unrelated_claim_audit_cannot_promote_this_claim(self):
        self.audit_claim(target="CLM-ACC")
        self.assert_invalid("UNSUPPORTED_PROMOTION")

    def test_rechecked_claim_must_use_corrected_extraction_check(self):
        self.data = deepcopy(self.examples["valid_corrected"])
        claim = self.record("CLM-LAT")["revisions"][-1]
        claim["data"]["review_refs"] = [ref("AID-CHECK-LAT")]
        claim["basis"] = [ref("AID-CHECK-LAT") if pin(p) == ("AID-CHECK-LAT", 2) else p for p in claim["basis"]]
        self.assert_invalid("UNSUPPORTED_PROMOTION")

    def test_new_disputed_appraisal_blocks_older_positive_support(self):
        self.append("APP-LAT", {"status": "disputed"})
        graph = self.graph()
        self.assertIn(("APP-LAT", 1), graph.invalidated)
        with self.assertRaisesRegex(ValidationError, "STALE_RELEASE"):
            graph.require_current(ref("CLM-LAT", 2), "claim")

    def test_changed_appraisal_judgment_requires_downstream_reassessment(self):
        self.append("APP-LAT", {"judgment": "New synthetic concern about the same exact extraction.", "status": "revised"})
        graph = self.graph()
        with self.assertRaisesRegex(ValidationError, "STALE_RELEASE"):
            graph.require_current(ref("CLM-LAT", 2), "claim")

    def test_new_failed_source_check_blocks_older_positive_attestation(self):
        self.append("AID-CHECK-LAT", {"outcome": "fail", "performed_at": {"state": "known", "value": "2000-01-01T01:00:00Z"}})
        graph = self.graph()
        self.assertIn(("AID-CHECK-LAT", 1), graph.invalidated)
        with self.assertRaisesRegex(ValidationError, "STALE_RELEASE"):
            graph.require_current(ref("CLM-LAT", 2), "claim")

    def test_requirement_cannot_export_an_obsolete_claim_pin(self):
        self.audit_claim()
        graph = self.graph()
        with self.assertRaisesRegex(ValidationError, "OLD_RELEASE"):
            graph.require_current(ref("REQ-TIMING"), "requirement")

    def test_requirement_evidence_status_requires_results(self):
        self.body("REQ-TIMING")["status"] = "evidence_supported"
        self.assert_invalid("UNSUPPORTED_REQUIREMENT")

    def test_sample_overlap_group_does_not_require_redundant_reciprocal_records(self):
        second = deepcopy(self.record("SAMPLE-ONE"))
        second["id"] = "SAMPLE-TWO"
        self.data["records"].append(second)
        self.body("SAMPLE-ONE")["overlap"] = [{"sample_ref": ref("SAMPLE-TWO"), "relation": "shared_control", "reason": "Synthetic shared control cohort."}]
        graph = self.graph()
        self.assertEqual(graph.sample_groups, [["SAMPLE-ONE", "SAMPLE-TWO"]])
        self.assertFalse(graph.unknown_overlap)
        self.body("SAMPLE-TWO")["overlap"] = [{"sample_ref": ref("SAMPLE-ONE"), "relation": "independent", "reason": "Contradictory synthetic assertion."}]
        self.assert_invalid("SAMPLE_OVERLAP_CONFLICT")

    def test_absent_overlap_relation_is_unknown_not_independence(self):
        second = deepcopy(self.record("SAMPLE-ONE"))
        second["id"] = "SAMPLE-TWO"
        self.data["records"].append(second)
        self.assertEqual(self.graph().unknown_overlap, {("SAMPLE-ONE", "SAMPLE-TWO")})

    def test_identity_alias_is_canonical_and_alias_cycle_rejected(self):
        alias = deepcopy(self.record("SRC-A"))
        alias["id"] = "SRC-ALIAS"
        alias["revisions"][0]["data"].update(validity="superseded", alias_of=ref("SRC-A"), alias_reason="Synthetic duplicate identity.")
        self.data["records"].append(alias)
        self.assertEqual(self.graph().canonical_id("SRC-ALIAS"), "SRC-A")
        self.body("SRC-A").update(validity="superseded", alias_of=ref("SRC-ALIAS"), alias_reason="Synthetic cyclic duplicate.")
        self.assert_invalid("IDENTITY_ALIAS_CYCLE")

    def test_full_text_decision_cannot_be_inferred_from_abstract_access(self):
        self.data = deepcopy(self.examples["valid_all_families"])
        self.body("SCR-A-FT")["reading_refs"] = []
        self.assert_invalid("FALSE_FULL_TEXT_SCREENING")

    def test_duplicate_hit_must_resolve_to_same_canonical_publication(self):
        self.data = deepcopy(self.examples["valid_all_families"])
        self.body("HIT-FIXTURE-2")["source_ref"] = ref("SRC-B")
        self.basis("HIT-FIXTURE-2").append(ref("SRC-B"))
        self.assert_invalid("DUPLICATE_IDENTITY")

    def test_ready_protocol_cannot_ignore_blocked_human_gate(self):
        self.data = deepcopy(self.examples["valid_all_families"])
        self.body("TEST-TRANSFER")["status"] = "ready_for_authorized_execution"
        self.assert_invalid("UNSATISFIED_GATE")


if __name__ == "__main__":
    unittest.main()
