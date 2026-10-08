"""Bounded MHAC-R001 cross-record prototype; NOT the completed R001 validator.

Stdlib-only. Run as a module or script in a checkout/packet overlay.
No network, source-fidelity assertion, statistical pooling or real completion gate.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

try:
    from .validate import ValidationError, read_json
except ImportError:  # direct `python tools/validate_records_prepass.py`
    from validate import ValidationError, read_json

CONTRACT = "mhac-r001-prepass/1"
KINDS = {"source", "study", "experiment", "sample", "extraction", "appraisal",
         "claim", "requirement", "amendment", "assistance"}
CLASSES = {"project_constraint", "source_claim", "empirical_finding",
           "theoretical_interpretation", "synthesis_proposition", "design_hypothesis",
           "unvalidated_convention"}
LIFECYCLE = {"proposed", "source_checked", "internally_audited", "externally_reviewed",
             "superseded", "withdrawn"}
ACCESS = {"not_attempted", "metadata_only", "abstract_only", "partial_text",
          "full_text_available", "unavailable"}
READING = {"not_read", "selected_ranges_read", "full_item_read"}
TRANSITIONS = {
    "proposed": {"proposed", "source_checked", "superseded", "withdrawn"},
    "source_checked": {"proposed", "source_checked", "internally_audited", "superseded", "withdrawn"},
    "internally_audited": {"proposed", "source_checked", "internally_audited", "externally_reviewed", "superseded", "withdrawn"},
    "externally_reviewed": {"proposed", "source_checked", "externally_reviewed", "superseded", "withdrawn"},
    "superseded": {"superseded"}, "withdrawn": {"withdrawn"},
}
Pin = tuple[str, int]


def fail(code: str, text: str) -> None:
    raise ValidationError(f"{code}: {text}")


def nonblank(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail("SHAPE", f"{field} must be nonblank text")


def pin(value: Any) -> Pin:
    if (not isinstance(value, dict) or set(value) != {"id", "rev"}
            or not isinstance(value["id"], str) or type(value["rev"]) is not int
            or value["rev"] < 1):
        fail("REFERENCE_SHAPE", repr(value))
    return value["id"], value["rev"]


def references(value: Any):
    """All pins are checked; only explicit basis edges enter the evidence DAG."""
    if isinstance(value, dict):
        if "rev" in value and "id" in value:
            yield pin(value)
        else:
            for item in value.values():
                yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)


def stamp(value: Any) -> datetime:
    nonblank(value, "at")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        fail("TIME", "Invalid ISO timestamp")
    if result.tzinfo is None:
        fail("TIME", "Timezone required")
    return result


def assert_append_only(previous: dict, current: dict) -> None:
    """Snapshot comparison is essential: a single file cannot prove its own history."""
    after = {r["id"]: r for r in current["records"]}
    if previous["dataset_kind"] != current["dataset_kind"]:
        fail("HISTORY", "Dataset kind changed")
    for old in previous["records"]:
        new = after.get(old["id"])
        if new is None:
            fail("HISTORY", f"Deleted record {old['id']}")
        for field in ("id", "kind", "synthetic", "issue", "schema_version"):
            if old[field] != new[field]:
                fail("HISTORY", f"Changed identity field {old['id']}.{field}")
        if new["revisions"][:len(old["revisions"])] != old["revisions"]:
            fail("HISTORY", f"Rewrote retained revisions of {old['id']}")


def validate(data: Any, *, expected_kind: str, previous: dict | None = None) -> dict:
    if not isinstance(data, dict) or data.get("contract") != CONTRACT:
        fail("CONTRACT", "Unsupported prepass contract")
    if expected_kind not in {"live", "fixture"} or data.get("dataset_kind") != expected_kind:
        fail("CONTAMINATION", "Dataset does not match caller-selected context")
    state = data.get("research_state")
    if state not in {"not_started", "in_progress", "complete"}:
        fail("STATUS", "Invalid research_state")
    rows = data.get("records")
    if not isinstance(rows, list):
        fail("SHAPE", "records must be a list")
    if not rows and state != "not_started":
        fail("EMPTY_COMPLETION", "Empty evidence is only valid as not_started")
    if rows and state == "not_started":
        fail("STATUS", "Nonempty fixture cannot claim not_started")
    if state == "complete":
        fail("COMPLETION_NOT_IMPLEMENTED", "This prototype cannot grant research completion")

    records: dict[str, dict] = {}
    versions: dict[Pin, dict] = {}
    graph: dict[Pin, set[Pin]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"schema_version", "id", "kind", "synthetic", "issue", "revisions"}:
            fail("SHAPE", "Unexpected record envelope fields")
        rid = row["id"]
        if not isinstance(rid, str) or re.fullmatch(r"[A-Z][A-Z0-9-]+", rid) is None:
            fail("ID", repr(rid))
        if rid in records:
            fail("DUPLICATE_ID", rid)
        if row["kind"] not in KINDS:
            fail("UNSUPPORTED_KIND", str(row["kind"]))
        if type(row["schema_version"]) is not int or row["schema_version"] != 1:
            fail("SCHEMA_VERSION", rid)
        if type(row["synthetic"]) is not bool or row["synthetic"] != (expected_kind == "fixture"):
            fail("CONTAMINATION", rid)
        if type(row["issue"]) is not int or row["issue"] < 1:
            fail("SHAPE", "issue must be a positive integer")
        if not isinstance(row["revisions"], list) or not row["revisions"]:
            fail("SHAPE", "Nonempty revisions required")
        records[rid] = row
        last_time = None
        last_lifecycle = None
        first_class = None
        for number, revision in enumerate(row["revisions"], 1):
            if not isinstance(revision, dict) or set(revision) != {"rev", "at", "actor", "basis", "data"}:
                fail("SHAPE", "Unexpected revision fields")
            if type(revision["rev"]) is not int or revision["rev"] != number:
                fail("REVISION", f"Noncontiguous revisions for {rid}")
            when = stamp(revision["at"])
            if last_time is not None and when < last_time:
                fail("TIME", f"Backdated revision for {rid}")
            last_time = when
            actor = revision["actor"]
            if not isinstance(actor, dict) or actor.get("kind") not in {"agent", "human"}:
                fail("ACTOR", rid)
            nonblank(actor.get("id"), "actor.id")
            if not isinstance(revision["data"], dict) or not isinstance(revision["basis"], list):
                fail("SHAPE", rid)
            deps = [pin(x) for x in revision["basis"]]
            if len(deps) != len(set(deps)):
                fail("DUPLICATE_REFERENCE", rid)
            key = rid, number
            versions[key] = revision
            graph[key] = set(deps)
            if row["kind"] == "claim":
                body = revision["data"]
                cls, lifecycle = body.get("class"), body.get("lifecycle")
                if cls not in CLASSES or lifecycle not in LIFECYCLE:
                    fail("STATUS", rid)
                if number == 1:
                    if lifecycle != "proposed":
                        fail("TRANSITION", "First claim revision must be proposed")
                    first_class = cls
                elif cls != first_class:
                    fail("CLASS_PROMOTION", f"Create a new claim ID; do not relabel {rid}")
                if last_lifecycle is not None and lifecycle not in TRANSITIONS[last_lifecycle]:
                    fail("TRANSITION", f"{rid}: {last_lifecycle} -> {lifecycle}")
                last_lifecycle = lifecycle

    def lookup(ref: dict | Pin, kind: str | None = None) -> dict:
        key = ref if isinstance(ref, tuple) else pin(ref)
        if key not in versions:
            fail("DANGLING_REFERENCE", str(key))
        if kind and records[key[0]]["kind"] != kind:
            fail("REFERENCE_TYPE", f"{key} is not {kind}")
        return versions[key]["data"]

    def require_basis(key: Pin, refs: list[dict]) -> None:
        for ref in refs:
            if pin(ref) not in graph[key]:
                fail("MISSING_BASIS", f"{key} omits {ref}")

    for key, rev in versions.items():
        for dep in references(rev):
            lookup(dep)
        # Scientific-dependence and ownership links may be cyclic; evidence basis may not.
    active: set[Pin] = set()
    done: set[Pin] = set()

    def visit(key: Pin) -> None:
        if key in active:
            fail("DEPENDENCY_CYCLE", str(key))
        if key in done:
            return
        active.add(key)
        for dep in sorted(graph[key]):
            visit(dep)
        active.remove(key)
        done.add(key)

    for key in sorted(graph):
        visit(key)
    for key, rev in versions.items():
        for dep in graph[key]:
            if stamp(versions[dep]["at"]) > stamp(rev["at"]):
                fail("FUTURE_BASIS", str(key))

    def manifestation(ref: dict, mid: str) -> dict:
        source = lookup(ref, "source")
        matches = [m for m in source["manifestations"] if m["id"] == mid]
        if len(matches) != 1:
            fail("MANIFESTATION", mid)
        return matches[0]

    def ranges(body: dict, m: dict) -> set[int]:
        result: set[int] = set()
        for interval in body["ranges"]:
            if (not isinstance(interval, list) or len(interval) != 2
                    or any(type(x) is not int for x in interval)
                    or not 1 <= interval[0] <= interval[1] <= m["extent"]):
                fail("READ_RANGE", str(interval))
            result.update(range(interval[0], interval[1] + 1))
        return result

    def reviews(body: dict, scope: str) -> list[dict]:
        result = []
        for ref in body.get("review_refs", []):
            review = lookup(ref, "assistance")
            if review.get("subtype") == "review" and review.get("scope") == scope and review.get("outcome") == "pass":
                result.append(review)
        return result

    for key, rev in versions.items():
        kind, b = records[key[0]]["kind"], rev["data"]
        if kind == "source":
            if b.get("access_status") not in ACCESS:
                fail("STATUS", str(key))
            if b.get("metadata_status") not in {"candidate", "verified", "conflict"}:
                fail("STATUS", str(key))
            mids = set()
            for m in b["manifestations"]:
                if m["id"] in mids:
                    fail("MANIFESTATION", "Duplicate manifestation ID")
                mids.add(m["id"])
                if (type(m["extent"]) is not int or not 1 <= m["extent"] <= 100000
                        or re.fullmatch(r"[0-9a-f]{64}", m["sha256"]) is None
                        or m["coordinate"] != "file_page_1based"):
                    fail("MANIFESTATION", "Invalid extent, coordinate or digest")
        elif kind == "study":
            for ref in b["publications"]:
                lookup(ref, "source")
        elif kind == "sample":
            if type(b["n"]) is not int or b["n"] < 1:
                fail("SAMPLE_N", str(key))
        elif kind == "experiment":
            lookup(b["study_ref"], "study")
            for ref in b["sample_refs"]:
                lookup(ref, "sample")
        elif kind == "assistance":
            if b["subtype"] == "reading":
                m = manifestation(b["source_ref"], b["manifestation_id"])
                require_basis(key, [b["source_ref"]])
                if b["reading_status"] not in READING or b["access_at_read"] not in ACCESS:
                    fail("STATUS", str(key))
                covered = ranges(b, m)
                if b["reading_status"] == "not_read" and covered:
                    fail("FALSE_READING", "not_read has ranges")
                if b["reading_status"] != "not_read" and not covered:
                    fail("FALSE_READING", "Read assertion has no ranges")
                if b["reading_status"] == "full_item_read" and (len(covered) != m["extent"] or b["access_at_read"] != "full_text_available"):
                    fail("FALSE_FULL_READING", str(key))
            elif b["subtype"] == "review":
                require_basis(key, b["target_refs"])
                verification = b["verification"]
                if verification not in {"agent_checked", "human_checked", "independent_human_checked", "not_checked"}:
                    fail("STATUS", str(key))
                if verification in {"human_checked", "independent_human_checked"} and rev["actor"]["kind"] != "human":
                    fail("FALSE_HUMAN_REVIEW", str(key))
                if verification == "independent_human_checked" and not b.get("independence_declaration"):
                    fail("FALSE_INDEPENDENCE", str(key))
                if b["outcome"] == "pass" and verification == "not_checked":
                    fail("FALSE_REVIEW", str(key))
            else:
                fail("UNSUPPORTED_ASSISTANCE", str(key))
        elif kind == "extraction":
            if type(b["value"]) not in (int, float) or not math.isfinite(b["value"]):
                fail("OUTCOME_VALUE", "Finite numeric value required by this fixture profile")
            exp = lookup(b["experiment_ref"], "experiment")
            study = lookup(exp["study_ref"], "study")
            sample = lookup(b["sample_ref"], "sample")
            if b["sample_ref"] not in exp["sample_refs"] or b["source_ref"] not in study["publications"]:
                fail("IDENTITY_LINK", str(key))
            if b["outcome"] not in exp["outcomes"] or b["unit"] != exp["outcomes"][b["outcome"]]["unit"]:
                fail("OUTCOME_UNIT", str(key))
            if type(b["n"]) is not int or not 0 < b["n"] <= sample["n"]:
                fail("OUTCOME_N", str(key))
            reading = lookup(b["reading_ref"], "assistance")
            locator = b["locator"]
            m = manifestation(b["source_ref"], locator["manifestation_id"])
            if (reading.get("subtype") != "reading" or reading["source_ref"] != b["source_ref"]
                    or reading["manifestation_id"] != locator["manifestation_id"]):
                fail("READING_SOURCE", str(key))
            start, end = locator["start"], locator["end"]
            if (type(start) is not int or type(end) is not int or not 1 <= start <= end <= m["extent"]
                    or locator["coordinate"] != m["coordinate"]):
                fail("LOCATOR", str(key))
            nonblank(locator.get("section"), "locator.section")
            if not set(range(start, end + 1)) <= ranges(reading, m):
                fail("UNREAD_LOCATOR", str(key))
            if b["scope"] not in {"bounded", "complete_report"}:
                fail("STATUS", str(key))
            if b["scope"] == "complete_report" and reading["reading_status"] != "full_item_read":
                fail("FALSE_FULL_EXTRACTION", str(key))
            require_basis(key, [b["source_ref"], b["reading_ref"], b["experiment_ref"], b["sample_ref"]])
        elif kind == "appraisal":
            lookup(b["target_ref"], "extraction")
            require_basis(key, [b["target_ref"]])
            nonblank(b["rationale"], "appraisal.rationale")
        elif kind == "claim":
            require_basis(key, b["evidence_refs"] + b["appraisal_refs"] + b["review_refs"])
            for ref in b["evidence_refs"]:
                lookup(ref, "extraction")
            for ref in b["appraisal_refs"]:
                lookup(ref, "appraisal")
            lifecycle = b["lifecycle"]
            if lifecycle in {"source_checked", "internally_audited", "externally_reviewed"}:
                if not b["evidence_refs"]:
                    fail("UNSUPPORTED_PROMOTION", str(key))
                checked = {pin(r) for review in reviews(b, "source_fidelity") for r in review["target_refs"]}
                if not {pin(r) for r in b["evidence_refs"]} <= checked:
                    fail("UNSUPPORTED_PROMOTION", "Missing revision-specific source checks")
                if b["class"] == "empirical_finding":
                    appraised = {pin(lookup(r, "appraisal")["target_ref"]) for r in b["appraisal_refs"]}
                    for ref in b["evidence_refs"]:
                        if pin(ref) not in appraised or lookup(ref)["scope"] != "complete_report":
                            fail("UNSUPPORTED_FINDING", "Requires exact appraisal and complete-report coverage in this prototype")
                def reviewed_payload(scope: str) -> list[dict]:
                    # Review the previous exact assertion, not an unrelated paper or stale draft.
                    # Lifecycle and review-log additions are not changes to assertion content.
                    def payload(body: dict) -> dict:
                        return {k: v for k, v in body.items() if k not in {"lifecycle", "review_refs"}}
                    matches = []
                    for review in reviews(b, scope):
                        for target in review["target_refs"]:
                            target_key = pin(target)
                            if (target_key[0] == key[0] and target_key[1] < key[1]
                                    and payload(lookup(target, "claim")) == payload(b)):
                                matches.append(review)
                    return matches
                if lifecycle in {"internally_audited", "externally_reviewed"} and not reviewed_payload("internal_audit"):
                    fail("UNSUPPORTED_PROMOTION", "Missing exact-assertion internal audit")
                if lifecycle == "externally_reviewed":
                    external = reviewed_payload("external_feedback")
                    if not external or any(r["verification"] not in {"human_checked", "independent_human_checked"}
                                           or not r.get("artifact") for r in external):
                        fail("FALSE_EXTERNAL_REVIEW", str(key))
        elif kind == "requirement":
            for ref in b["claim_refs"]:
                lookup(ref, "claim")
            require_basis(key, b["claim_refs"])
        elif kind == "amendment":
            if b["kind"] not in {"extraction_correction", "source_invalidation"}:
                fail("UNSUPPORTED_AMENDMENT", str(key))
            if not b["target_refs"]:
                fail("AMENDMENT", "Empty amendment targets")
            nonblank(b["reason"], "amendment.reason")
            if b["kind"] == "extraction_correction":
                if len(b["target_refs"]) != len(b["replacement_refs"]):
                    fail("AMENDMENT", "Correction pairs must match")
                for old, new in zip(b["target_refs"], b["replacement_refs"]):
                    lookup(old, "extraction")
                    lookup(new, "extraction")
                    if old["id"] != new["id"] or new["rev"] <= old["rev"]:
                        fail("AMENDMENT", "Correction must retain identity and advance revision")
            else:
                for ref in b["target_refs"]:
                    lookup(ref, "source")

    if previous is not None:
        assert_append_only(previous, data)
    invalidated = set()
    for row in rows:
        if row["kind"] == "amendment":
            invalidated.update(pin(ref) for ref in row["revisions"][-1]["data"]["target_refs"])
    stale = set(invalidated)
    changed = True
    while changed:
        old_size = len(stale)
        stale.update(key for key, deps in graph.items() if deps & stale)
        changed = len(stale) != old_size
    exports = data.get("release_claims", [])
    for ref in exports:
        b = lookup(ref, "claim")
        key = pin(ref)
        if key in stale:
            fail("STALE_RELEASE", str(key))
        if key[1] != len(records[key[0]]["revisions"]):
            fail("OLD_RELEASE", str(key))
        if b["lifecycle"] in {"proposed", "withdrawn", "superseded"}:
            fail("UNREADY_RELEASE", str(key))
    for ref in data.get("release_requirements", []):
        lookup(ref, "requirement")
        key = pin(ref)
        if key in stale:
            fail("STALE_REQUIREMENT", str(key))
        if key[1] != len(records[key[0]]["revisions"]):
            fail("OLD_RELEASE", str(key))
    counts = Counter(row["kind"] for row in rows)
    extractions = [r["revisions"][-1]["data"] for r in rows if r["kind"] == "extraction"]
    outcomes = {(e["experiment_ref"]["id"], e["outcome"], e["sample_ref"]["id"]) for e in extractions}
    groups = Counter(e["sample_ref"]["id"] for e in extractions)
    computed = {"publications": counts["source"], "studies": counts["study"],
                "experiments": counts["experiment"], "samples": counts["sample"],
                "outcomes": len(outcomes), "shared_sample_groups": sum(n > 1 for n in groups.values())}
    if data.get("declared_counts", computed) != computed:
        fail("COUNT_MISMATCH", f"Expected {computed}")
    return {"contract": CONTRACT, "structural_result": "pass", "dataset_kind": expected_kind,
            "release_context": "simulation_only" if expected_kind == "fixture" else "live",
            "research_state": state, "counts": computed,
            "stale_revisions": [{"id": rid, "rev": rev} for rid, rev in sorted(stale)],
            "latest_stale_ids": sorted(rid for rid, row in records.items() if (rid, len(row["revisions"])) in stale),
            "not_evaluated": ["source_fidelity", "scientific_validity", "independence_of_real_people",
                              "unknown_between_sample_overlap", "full_search_flow", "research_completion",
                              "all_R001_record_schemas"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--dataset-kind", choices=["live", "fixture"], required=True)
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args(argv)
    try:
        report = validate(read_json(args.input), expected_kind=args.dataset_kind,
                          previous=read_json(args.previous) if args.previous else None)
    except (ValidationError, OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        # Malformed prototype payloads fail closed; full path-aware schemas remain R001 work.
        print(json.dumps({"structural_result": "fail", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
