"""Contract tests for scientific-record shapes, variants and local histories.

These tests intentionally accept the fixture's initial transcription error:
schemas validate its provenance shape, not whether a source says 8 or 80 ms.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from schemas import ValidationError
from schemas.v1 import CLASSES, KINDS, known_value, pin, references, validate_record

FIXTURE = Path(__file__).parent / "fixtures" / "records" / "v1" / "valid_all_families.json"


def unknown(reason="Unknown in this explicitly synthetic test"):
    return {"state": "unknown", "reason": reason}


def known(value):
    return {"state": "known", "value": value}


class RecordSchemasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {r["id"]: r for r in json.loads(FIXTURE.read_text(encoding="utf-8"))["records"]}

    def row(self, rid, *, latest=False):
        row = copy.deepcopy(self.records[rid])
        if latest:
            last = row["revisions"][-1]
            last["rev"] = 1
            row["revisions"] = [last]
        return row

    def validate(self, row, context="fixture"):
        validate_record(row, expected_kind=context)

    def invalid(self, row, code=None, context="fixture"):
        if code:
            with self.assertRaisesRegex(ValidationError, code):
                self.validate(row, context)
        else:
            with self.assertRaises(ValidationError):
                self.validate(row, context)

    def append(self, row, **changes):
        revision = copy.deepcopy(row["revisions"][-1])
        revision["rev"] += 1
        revision["at"] = "2000-01-02T00:00:00Z"
        revision["data"].update(changes)
        row["revisions"].append(revision)
        return revision

    def test_all_sixteen_families_and_retained_revisions(self):
        self.assertEqual({row["kind"] for row in self.records.values()}, KINDS)
        for rid, row in self.records.items():
            with self.subTest(id=rid):
                self.validate(row)

    def test_closed_envelope_revision_actor_and_data(self):
        for target in ("envelope", "revision", "actor", "data", "rights"):
            row = self.row("SRC-A")
            obj = {"envelope": row, "revision": row["revisions"][0],
                   "actor": row["revisions"][0]["actor"], "data": row["revisions"][0]["data"],
                   "rights": row["revisions"][0]["data"]["rights"]}[target]
            obj["unrecognized"] = "must not silently disappear"
            with self.subTest(target=target):
                self.invalid(row, "SHAPE")

    def test_record_ids_versions_and_caller_context(self):
        for field, value, code in (("id", "EX-WRONG", "ID"), ("id", "SRC-has-lowercase", "ID"),
                                   ("schema_version", True, "SCHEMA_VERSION"), ("schema_version", 2, "SCHEMA_VERSION"),
                                   ("kind", "future_source", "UNSUPPORTED_KIND"), ("synthetic", 1, "CONTAMINATION"),
                                   ("issue", False, "NUMBER")):
            row = self.row("SRC-A")
            row[field] = value
            with self.subTest(field=field, value=value):
                self.invalid(row, code)
        self.invalid(self.row("SRC-A"), "CONTAMINATION", context="live")

    def test_malformed_json_types_report_validation_errors_without_tracebacks(self):
        def paths(value, path=()):
            yield path
            if isinstance(value, dict):
                for key, item in value.items():
                    yield from paths(item, path + (key,))
            elif isinstance(value, list):
                for key, item in enumerate(value):
                    yield from paths(item, path + (key,))

        # A nested list/object in an enum, pin or numeric field must not escape
        # as an unhashable TypeError or a missing-key traceback through the CLI.
        for row in self.records.values():
            for path in paths(row):
                for replacement in (None, [], {"state": []}):
                    candidate = copy.deepcopy(row)
                    if path:
                        obj = candidate
                        for key in path[:-1]:
                            obj = obj[key]
                        obj[path[-1]] = copy.deepcopy(replacement)
                    else:
                        candidate = copy.deepcopy(replacement)
                    try:
                        self.validate(candidate)
                    except ValidationError:
                        pass
                    except Exception as error:
                        self.fail(f"{row['id']} {path}: unexpected {type(error).__name__}: {error}")

    def test_empty_missing_and_noncontiguous_revisions_fail(self):
        row = self.row("SRC-A")
        row["revisions"] = []
        self.invalid(row, "SHAPE")
        for number in (True, 0, 2, 1.0):
            row = self.row("SRC-A")
            row["revisions"][0]["rev"] = number
            with self.subTest(number=number):
                self.invalid(row, "REVISION")

    def test_factual_status_and_actor_are_explicit(self):
        for value in ("source_reported", "evidence_verified", None):
            row = self.row("SRC-A")
            row["revisions"][0]["factual_status"] = value
            with self.subTest(value=value):
                self.invalid(row)
        row = self.row("SRC-A")
        row["revisions"][0]["actor"]["model"] = unknown("Model version unavailable")
        self.validate(row)

    def test_actual_dates_are_qualified_and_ordered(self):
        for value in ("2000-01-01", "2000-01-01T00:00:00", "2000-02-30T00:00:00Z",
                      "2000-01-01 00:00:00Z", "2000-01-01T00:00:00+00:99", True):
            row = self.row("SRC-A")
            row["revisions"][0]["at"] = value
            with self.subTest(value=value):
                self.invalid(row, "TIME")
        row = self.row("SRC-A")
        self.append(row)["at"] = "1999-12-31T00:00:00Z"
        self.invalid(row, "TIME")
        row = self.row("SRC-A")
        row["revisions"][0]["data"]["access_at"] = "2001-01-01T00:00:00Z"
        self.invalid(row, "TIME")

    def test_unknown_values_need_reasons_and_reject_disguised_null(self):
        for value in (None, "", {"state": "unknown"}, {"state": "unknown", "reason": ""},
                      {"state": "known", "value": "English", "reason": "ambiguous variant"}):
            row = self.row("SRC-A")
            row["revisions"][0]["data"]["language"] = value
            with self.subTest(value=value):
                self.invalid(row)
        self.assertIsNone(known_value(unknown()))
        self.assertEqual(known_value(known(0)), 0)

    def test_date_precision_does_not_invent_unknown_days(self):
        for value in ("2000", "2000-02", "2000-02-29"):
            row = self.row("SRC-A")
            row["revisions"][0]["data"]["publication_date"] = known(value)
            self.validate(row)
        for value in ("0000", "2000-00", "2001-02-29", "2000/01/01"):
            row = self.row("SRC-A")
            row["revisions"][0]["data"]["publication_date"] = known(value)
            with self.subTest(value=value):
                self.invalid(row, "DATE")

    def test_metadata_only_source_is_representable_without_invented_hashes(self):
        row = self.row("SRC-A")
        row["synthetic"] = False
        r = row["revisions"][0]
        r["factual_status"] = "discovery"
        r["data"].update(manifestations=[], access_status="metadata_only")
        self.validate(row, "live")
        r["data"]["reading_status"] = "full_item_read"
        self.invalid(row, "SHAPE", "live")

    def test_verified_metadata_and_positive_rights_need_provenance(self):
        row = self.row("SRC-A")
        b = row["revisions"][0]["data"]
        b.update(metadata_status="verified", metadata_evidence=[])
        self.invalid(row)
        b["metadata_evidence"] = ["Explicitly synthetic metadata verification record"]
        self.validate(row)
        b["rights"]["status"] = "redistribution_permitted"
        b["rights"]["evidence"] = unknown()
        self.invalid(row, "RIGHTS")
        b["rights"]["evidence"] = known("Synthetic permission statement; no real license is granted")
        self.validate(row)

    def test_manifestation_and_coordinate_shapes(self):
        for change in ({"extent": True}, {"sha256": "not-a-hash"}, {"coordinate": "page"},
                       {"fixture_path": "../outside.txt"}):
            row = self.row("SRC-A")
            row["revisions"][0]["data"]["manifestations"][0].update(change)
            with self.subTest(change=change):
                self.invalid(row)
        row = self.row("SRC-A")
        b = row["revisions"][0]["data"]
        b["manifestations"].append(copy.deepcopy(b["manifestations"][0]))
        self.invalid(row, "MANIFESTATION")

    def test_retained_live_source_bytes_require_redistribution_rights(self):
        row = self.row("SRC-A")
        row["synthetic"] = False
        revision = row["revisions"][0]
        revision["factual_status"] = "discovery"
        b = revision["data"]
        manifestation = b["manifestations"][0]
        manifestation.pop("fixture_path")
        manifestation["local_path"] = "research/sources/permitted.txt"
        self.invalid(row, "RIGHTS", "live")
        b["rights"].update(status="redistribution_permitted",
                           evidence=known("Permission-safe test reference; this is a schema test, not a license grant"))
        self.validate(row, "live")  # Loader, separately, verifies file bytes.
        for path in ("/outside.txt", "../outside.txt", "./source.txt", "sources//item.txt",
                     "sources/", "C:/outside.txt", "sources\\item.txt"):
            manifestation["local_path"] = path
            with self.subTest(path=path):
                self.invalid(row, "ARTIFACT", "live")
        manifestation.pop("local_path")
        manifestation["location"] = "Restricted external holding; not retained in the repository"
        b["rights"].update(status="unknown", evidence=unknown())
        self.validate(row, "live")

    def test_numeric_known_and_missing_values_keep_boolean_distinction(self):
        for field in ("value", "n"):
            for value in (True, False, float("nan"), float("inf"), float("-inf")):
                row = self.row("EX-ACC")
                row["revisions"][0]["data"][field] = value
                with self.subTest(field=field, value=value):
                    self.invalid(row, "NUMBER")
        row = self.row("EX-ACC")
        row["revisions"][0]["data"].update(value=unknown(), n=unknown())
        self.validate(row)

    def test_dispersion_variants_and_real_interval_endpoints(self):
        variants = [{"measure": m, "value": 2.5, "unit": "percentage_points"} for m in ("sd", "se", "variance")]
        variants.append({"measure": "ci95", "lower": -2, "upper": 7, "unit": "percentage_points"})
        for variant in variants:
            row = self.row("EX-ACC")
            row["revisions"][0]["data"]["dispersion"] = known(variant)
            with self.subTest(variant=variant):
                self.validate(row)
        for variant in ({"measure": "sd", "value": -1, "unit": "ms"},
                        {"measure": "ci95", "value": 5, "unit": "ms"},
                        {"measure": "ci95", "lower": 9, "upper": 4, "unit": "ms"}):
            row = self.row("EX-ACC")
            row["revisions"][0]["data"]["dispersion"] = known(variant)
            with self.subTest(variant=variant):
                self.invalid(row)

    def test_dependence_retains_unknown_correlation_and_rejects_impossible_values(self):
        for value in (-1.01, 1.01, True, float("nan")):
            row = self.row("EXP-ONE")
            row["revisions"][0]["data"]["dependence"]["correlation"] = known(value)
            with self.subTest(value=value):
                self.invalid(row, "NUMBER")
        row = self.row("EXP-ONE")
        row["revisions"][0]["data"]["dependence"] = {"relation": "unknown", "correlation": known(0)}
        self.invalid(row, "DEPENDENCE")

    def test_derivation_names_inputs_method_artifact_and_matching_output(self):
        row = self.row("EX-ACC")
        b = row["revisions"][0]["data"]
        derivation = {"input_refs": [{"id": "EX-INPUT", "rev": 1}], "transformation": "identity(x)",
                      "version": "synthetic-v1", "assumptions": ["Explicit test only"],
                      "output": b["value"], "artifact": {"path": "calculation.py", "sha256": "0" * 64}}
        b["derivation"] = known(derivation)
        self.validate(row)  # File bytes and referenced inputs are graph/loader work.
        derivation["output"] += 1
        self.invalid(row, "DERIVATION")
        derivation["output"] = b["value"]
        derivation["input_refs"] = []
        self.invalid(row)

    def test_field_provenance_is_not_an_untyped_extra_dictionary(self):
        row = self.row("EX-ACC")
        del row["revisions"][0]["data"]["field_locators"]["n"]
        self.invalid(row, "SHAPE")
        row = self.row("EX-ACC")
        row["revisions"][0]["data"]["field_locators"]["value"]["coordinate"] = "printed_page"
        self.invalid(row, "LOCATOR")

    def test_all_claim_classes_have_closed_distinct_variants(self):
        for cls in CLASSES:
            row = self.row("CLM-HYP")
            row["revisions"] = row["revisions"][:1]
            b = row["revisions"][0]["data"]
            for field in ("mechanism", "variables", "test_plan", "test_refs"):
                b.pop(field, None)
            b["class"] = cls
            if cls == "project_constraint":
                b["decision_artifact"] = "Explicit synthetic project decision locator"
            elif cls == "design_hypothesis":
                b.update(mechanism="Fictional mechanism", variables=["latency"], test_plan="Planned discriminating test")
            elif cls == "unvalidated_convention":
                b["convention_reason"] = "Provisional arbitrary fixture choice"
            with self.subTest(cls=cls):
                self.validate(row)
                b["unexpected_argument_evidence"] = "must be explicit"
                self.invalid(row, "SHAPE")

    def test_claim_class_never_changes_and_first_state_is_proposed(self):
        row = self.row("CLM-LAT")
        row["revisions"][1]["data"]["class"] = "source_claim"
        self.invalid(row, "CLASS_PROMOTION")
        row = self.row("CLM-LAT")
        row["revisions"][0]["data"]["lifecycle"] = "source_checked"
        self.invalid(row, "TRANSITION")
        row = self.row("CLM-LAT")
        row["revisions"][1]["data"]["lifecycle"] = "externally_reviewed"
        self.invalid(row, "TRANSITION")

    def test_final_claim_cannot_revive(self):
        row = self.row("CLM-LAT")
        self.append(row, lifecycle="withdrawn")
        self.validate(row)
        self.append(row, lifecycle="proposed")
        self.invalid(row, "TRANSITION")

    def test_search_occurrence_identity_and_terminal_run_are_retained(self):
        row = self.row("HIT-FIXTURE-1")
        self.append(row, raw_metadata="Replaced original discovery bytes")
        self.invalid(row, "HISTORY")
        for change in ({"query": "quietly replaced query"}, {"retrieved_count": 4}):
            row = self.row("SRCH-FIXTURE")
            self.append(row, **change)
            with self.subTest(change=change):
                self.invalid(row, "HISTORY")

    def test_run_status_does_not_manufacture_execution(self):
        row = self.row("SRCH-FIXTURE")
        b = row["revisions"][0]["data"]
        b["status"] = "planned"
        self.invalid(row, "STATUS")
        b.update(started_at=unknown(), finished_at=unknown(), retrieved_count=0, reported_count=unknown(), export=unknown())
        self.validate(row)
        b["status"] = "completed"
        self.invalid(row, "TIME")

    def test_hit_resolution_variants(self):
        row = self.row("HIT-FIXTURE-1")
        b = row["revisions"][0]["data"]
        b["status"] = "unresolved"
        self.invalid(row, "RESOLUTION")
        del b["source_ref"]
        self.validate(row)
        b["status"] = "unresolvable"
        self.validate(row)
        b["status"] = "resolved"
        self.invalid(row, "RESOLUTION")

    def test_local_screening_scope_cannot_change_in_place(self):
        row = self.row("SCR-A-TA")
        self.append(row, stage="full_text")
        self.invalid(row, "HISTORY")

    def test_terminal_states_across_record_families(self):
        examples = [
            ("SRC-A", "validity", "retracted", "active"),
            ("SAMPLE-ONE", "status", "withdrawn", "provisional"),
            ("EXP-ONE", "status", "withdrawn", "extracted"),
            ("EX-ACC", "status", "withdrawn", "extracted"),
            ("TX-CONTEXT", "status", "withdrawn", "extracted"),
            ("APP-LAT", "status", "withdrawn", "proposed"),
            ("REQ-TIMING", "status", "rejected", "proposed"),
            ("TEST-TRANSFER", "status", "withdrawn", "draft"),
            ("AMD-FIX-LAT", "status", "rescinded", "applied"),
        ]
        for rid, field, terminal, revived in examples:
            row = self.row(rid)
            self.append(row, **{field: terminal})
            self.validate(row)
            self.append(row, **{field: revived})
            with self.subTest(id=rid):
                self.invalid(row, "TRANSITION")

    def test_state_progress_cannot_skip_required_intermediate_stage(self):
        for rid, field, initial, skipped in (
            ("EX-ACC", "status", "draft", "source_checked"),
            ("EXP-ONE", "status", "provisional", "checked"),
            ("REQ-TIMING", "status", "proposed", "internally_checked"),
            ("AMD-FIX-LAT", "status", "proposed", "verified"),
        ):
            row = self.row(rid, latest=True)
            row["revisions"][0]["data"][field] = initial
            self.append(row, **{field: skipped})
            with self.subTest(id=rid):
                self.invalid(row, "TRANSITION")

    def test_assistance_variants_cannot_create_fake_performed_work(self):
        for rid in ("AID-READ-A", "AID-CHECK-ACC", "AID-FIXTURE-BUILD"):
            row = self.row(rid)
            row["revisions"][0]["data"]["performed_at"] = unknown()
            with self.subTest(id=rid):
                self.invalid(row, "TIME")
        row = self.row("AID-READ-B")
        b = row["revisions"][0]["data"]
        b.update(status="planned", performed_at=unknown(), reading_status="not_read", ranges=[])
        self.validate(row)
        b["ranges"] = [[1, 1]]
        self.invalid(row, "FALSE_FULL_READING")

    def test_agent_review_cannot_assert_human_or_external_approval(self):
        for verification in ("human_checked", "independent_human_checked"):
            row = self.row("AID-CHECK-ACC")
            row["revisions"][0]["data"]["verification"] = verification
            with self.subTest(verification=verification):
                self.invalid(row, "FALSE_HUMAN_REVIEW")
        row = self.row("AID-CHECK-ACC")
        b = row["revisions"][0]["data"]
        b.update(scope="external_feedback", gate_ref={"id": "HG-EXTERNAL", "rev": 1})
        self.invalid(row, "FALSE_HUMAN_REVIEW")
        row["revisions"][0]["actor"] = {"kind": "human", "id": "FICTIONAL-REVIEWER"}
        b["verification"] = "human_checked"
        self.validate(row)  # Actual gate evidence remains a graph check.
        b["verification"] = "not_checked"
        self.invalid(row, "FALSE_REVIEW")

    def test_gate_satisfaction_requires_actual_human_identity_and_evidence(self):
        row = self.row("HG-AUTH")
        b = row["revisions"][0]["data"]
        b["status"] = "satisfied"
        self.invalid(row, "FALSE_HUMAN_GATE")
        actor = {"kind": "human", "id": "FICTIONAL-AUTHORIZER"}
        row["revisions"][0]["actor"] = actor
        b["authorized_actor"] = known(actor)
        b["evidence"] = known("Synthetic authorization illustration; no actual permission is asserted")
        self.validate(row)
        self.append(row, status="waiting")
        self.invalid(row, "TRANSITION")
        row["revisions"][-1]["data"]["reopen_reason"] = "Synthetic change of planned scope"
        self.validate(row)

    def test_protocol_and_requirements_do_not_claim_results_from_readiness(self):
        row = self.row("TEST-TRANSFER")
        row["revisions"][0]["data"].update(status="ready_for_authorized_execution", gate_refs=[])
        self.invalid(row, "READINESS")
        row = self.row("REQ-TIMING", latest=True)
        row["revisions"][0]["data"].update(status="evidence_supported", result_refs=[])
        self.invalid(row, "UNSUPPORTED_REQUIREMENT")
        row = self.row("TEST-TRANSFER")
        row["revisions"][0]["data"]["exposure"] = "prospective"
        self.invalid(row, "CONTAMINATION")

    def test_amendment_effect_identifies_targets_replacements_and_materiality(self):
        for change in ({"target_refs": []}, {"replacement_refs": []}, {"materiality": "nonmaterial"}):
            row = self.row("AMD-FIX-LAT")
            row["revisions"][0]["data"].update(change)
            with self.subTest(change=change):
                self.invalid(row, "AMENDMENT")

    def test_protocol_rule_change_pins_actual_old_and_new_artifacts(self):
        row = self.row("AMD-FIX-LAT")
        b = row["revisions"][0]["data"]
        b.update(kind="protocol_change", target_refs=[], replacement_refs=[])
        self.invalid(row, "AMENDMENT")
        b["rule_change"] = {
            "previous": {"version": "synthetic-v1", "artifact": {"path": "protocol/v1.md", "sha256": "0" * 64}},
            "replacement": {"version": "synthetic-v2", "artifact": {"path": "protocol/v2.md", "sha256": "1" * 64}},
        }
        self.validate(row)
        for field, value in (("version", "synthetic-v1"),
                             ("artifact", {"path": "protocol/v2.md", "sha256": "0" * 64}),
                             ("artifact", {"path": "protocol/v2.md"}),
                             ("artifact", {"path": "../private.md", "sha256": "1" * 64})):
            invalid = copy.deepcopy(row)
            invalid["revisions"][0]["data"]["rule_change"]["replacement"][field] = value
            with self.subTest(field=field, value=value):
                self.invalid(invalid)
        b["kind"] = "source_invalidation"
        self.invalid(row, "AMENDMENT")

    def test_reference_shape_and_duplicates_are_unambiguous(self):
        self.assertEqual(pin({"id": "SRC-A", "rev": 1}), ("SRC-A", 1))
        self.assertEqual(list(references({"nested": [{"id": "SRC-A", "rev": 1}]})), [("SRC-A", 1)])
        for value in ({"id": "SRC-A", "rev": True}, {"id": "SRC-A", "rev": 1, "latest": True}):
            with self.assertRaises(ValidationError):
                pin(value)
        row = self.row("EX-ACC")
        row["revisions"][0]["basis"].append(copy.deepcopy(row["revisions"][0]["basis"][0]))
        self.invalid(row, "DUPLICATE_REFERENCE")


if __name__ == "__main__":
    unittest.main()
