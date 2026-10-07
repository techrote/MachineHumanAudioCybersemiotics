"""Typed record relationships and evidence currency for mhac-records/1.

This module refines the retained MHAC-R001 prepass prototype.  It checks recorded
relationships, not source fidelity, human identity, or scientific validity.
Identity, overlap, prospective tests, and review targets have different meanings;
only explicit, mandatory supporting pins enter the evidence dependency graph.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Iterable

from schemas import ValidationError
from schemas.v1 import pin, references, stamp, validate_record

Pin = tuple[str, int]
Ref = dict[str, Any] | Pin
_READABLE = {"abstract_only", "partial_text", "full_text_available"}
_CLAIM_READY = {"source_checked", "internally_audited", "externally_reviewed"}
_EXTRACTIONS = {"extraction", "theoretical_extraction"}
_SHARED = {"known_shared", "partial_overlap", "shared_control"}


def fail(code: str, message: str) -> None:
    raise ValidationError(f"{code}: {message}")


def known(value: Any) -> Any:
    """Unwrap a tagged value; preserve the prepass's direct known numerics."""
    if isinstance(value, dict) and "state" in value:
        return value.get("value") if value["state"] == "known" else None
    return value


def _key(ref: Ref) -> Pin:
    return pin({"id": ref[0], "rev": ref[1]}) if isinstance(ref, tuple) else pin(ref)


def _ref(key: Pin) -> dict[str, Any]:
    return {"id": key[0], "rev": key[1]}


def _payload(body: dict[str, Any]) -> dict[str, Any]:
    """The checked assertion excludes only its verification/lifecycle log."""
    return {k: v for k, v in body.items() if k not in {"lifecycle", "status", "review_refs"}}


def semantic_dependencies(row: dict, revision: dict) -> set[Pin]:
    """Return mandatory support; callers cannot omit it to escape invalidation.

    Alias, overlap, supersession, amendment disposition and planned-test links
    are deliberately absent.  They are validated as their own relationships.
    """
    kind, body = row["kind"], revision["data"]
    refs: list[dict] = []
    if kind == "search_hit":
        refs.append(body["search_ref"])
        if "source_ref" in body:
            refs.append(body["source_ref"])
        if "duplicate_of" in body:
            refs.append(body["duplicate_of"])
    elif kind == "screening":
        refs = [body["source_ref"], *body["reading_refs"], *body["review_refs"]]
    elif kind == "study":
        # Report membership is not itself a premise. Exact identity evidence is.
        refs = [e["source_ref"] for e in body["identity_locators"]]
    elif kind == "sample":
        refs = [e["source_ref"] for e in body.get("evidence", [])]
    elif kind in _EXTRACTIONS:
        refs = [body["source_ref"], body["reading_ref"]]
        if kind == "extraction":
            refs.extend([body["experiment_ref"], body["sample_ref"]])
            derivation = known(body["derivation"])
            if derivation is not None:
                refs.extend(derivation["input_refs"])
    elif kind == "appraisal":
        refs = [body["target_ref"], *(e["source_ref"] for e in body["evidence"])]
    elif kind == "claim":
        refs = [*body["evidence_refs"], *body["appraisal_refs"], *body["review_refs"]]
    elif kind == "requirement":
        refs = [*body["claim_refs"], *body["result_refs"]]
    elif kind == "experiment_protocol":
        refs = [*body["hypothesis_refs"], *body["gate_refs"]]
    elif kind == "assistance":
        if body["subtype"] == "reading":
            refs = [body["source_ref"]]
        elif body["subtype"] == "review":
            refs = [*body["target_refs"], *body.get("input_refs", [])]
            if "gate_ref" in body:
                refs.append(body["gate_ref"])
        else:
            # Output links describe products; they are not inputs to themselves.
            refs = body["input_refs"]
    return {pin(ref) for ref in refs}


@dataclass
class RecordGraph:
    records: dict[str, dict]
    versions: dict[Pin, dict]
    basis: dict[Pin, set[Pin]]
    latest: dict[str, dict]
    currency_edges: dict[Pin, set[Pin]] = field(default_factory=dict)
    invalidated: set[Pin] = field(default_factory=set)
    stale: set[Pin] = field(default_factory=set)
    aliases: dict[str, str] = field(default_factory=dict)
    sample_groups: list[list[str]] = field(default_factory=list)
    unknown_overlap: set[tuple[str, str]] = field(default_factory=set)

    def lookup(self, ref: Ref, kind: str | None = None) -> dict:
        key = _key(ref)
        if key not in self.versions:
            fail("DANGLING_REFERENCE", repr(key))
        if kind is not None and self.records[key[0]]["kind"] != kind:
            fail("REFERENCE_TYPE", f"{key} is not {kind}")
        return self.versions[key]["data"]

    def latest_pin(self, rid: str) -> Pin:
        if rid not in self.latest:
            fail("DANGLING_REFERENCE", rid)
        return rid, self.latest[rid]["rev"]

    def canonical_id(self, rid: str) -> str:
        if rid not in self.records:
            fail("DANGLING_REFERENCE", rid)
        while rid in self.aliases:
            rid = self.aliases[rid]
        return rid

    def require_current(self, ref: Ref, kind: str | None = None, *, usable: bool = True) -> dict:
        """Check a requested current output, leaving stale WIP valid in storage.

        An explicitly proposed requirement can be exported as an unvalidated
        requirement.  Its supporting claims still need usable, current pins.
        Audit records may target earlier exact assertions; those pins are never
        rewritten to latest merely because a new revision exists.
        """
        key = _key(ref)
        body = self.lookup(key, kind)
        if key in self.stale:
            fail("STALE_RELEASE", repr(key))
        if key != self.latest_pin(key[0]):
            fail("OLD_RELEASE", repr(key))
        if not usable:
            return body
        record_kind = self.records[key[0]]["kind"]
        status = body.get("lifecycle", body.get("status", body.get("validity")))
        if status in {"withdrawn", "superseded", "retracted", "rejected", "rescinded"}:
            fail("UNREADY_RELEASE", repr(key))
        if record_kind == "claim":
            if status not in _CLAIM_READY:
                fail("UNREADY_RELEASE", repr(key))
            for evidence in body["evidence_refs"]:
                if self.records[pin(evidence)[0]]["kind"] == "claim":
                    self.require_current(evidence, "claim")
        elif record_kind == "requirement":
            for claim_ref in body["claim_refs"]:
                self.require_current(claim_ref, "claim")
        elif record_kind == "experiment_protocol" and status == "ready_for_authorized_execution":
            for gate_ref in body["gate_refs"]:
                self.require_current(gate_ref, "human_gate")
        elif record_kind == "human_gate" and status != "satisfied":
            fail("UNSATISFIED_GATE", repr(key))
        return body


def _dag(graph: dict[Any, set[Any]], code: str) -> None:
    """Kahn traversal avoids recursion limits on long retained revision chains."""
    pending = {node: len(deps) for node, deps in graph.items()}
    reverse: dict[Any, set[Any]] = defaultdict(set)
    for node, deps in graph.items():
        for dependency in deps:
            if dependency not in graph:
                fail("DANGLING_REFERENCE", repr(dependency))
            reverse[dependency].add(node)
    queue = deque(sorted(node for node, count in pending.items() if not count))
    seen = 0
    while queue:
        node = queue.popleft()
        seen += 1
        for child in sorted(reverse[node]):
            pending[child] -= 1
            if not pending[child]:
                queue.append(child)
    if seen != len(graph):
        fail(code, repr(sorted(node for node, count in pending.items() if count)[:4]))


def _bounds(manifestation: dict) -> tuple[int, int]:
    first = 0 if manifestation["coordinate"] == "pdf_page_0based" else 1
    return first, first + manifestation["extent"] - 1


def _manifestation(graph: RecordGraph, source_ref: Ref, mid: str) -> dict:
    source = graph.lookup(source_ref, "source")
    matches = [m for m in source["manifestations"] if m["id"] == mid]
    if len(matches) != 1:
        fail("MANIFESTATION", f"{_key(source_ref)}: {mid}")
    return matches[0]


def _ranges(body: dict, manifestation: dict) -> list[tuple[int, int]]:
    lower, upper = _bounds(manifestation)
    merged: list[tuple[int, int]] = []
    for start, end in sorted(body["ranges"]):
        if not lower <= start <= end <= upper:
            fail("READ_RANGE", f"{start}..{end} outside {lower}..{upper}")
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = merged[-1][0], max(end, merged[-1][1])
        else:
            merged.append((start, end))
    return merged


def _contains(ranges: Iterable[tuple[int, int]], start: int, end: int) -> bool:
    return any(left <= start <= end <= right for left, right in ranges)


def _locator(graph: RecordGraph, source_ref: Ref, locator: dict) -> dict:
    manifestation = _manifestation(graph, source_ref, locator["manifestation_id"])
    lower, upper = _bounds(manifestation)
    if locator["coordinate"] != manifestation["coordinate"] or not lower <= locator["start"] <= locator["end"] <= upper:
        fail("LOCATOR", f"{_key(source_ref)}: incompatible coordinate or extent")
    return manifestation


def _reading(graph: RecordGraph, source_ref: Ref, reading_ref: Ref, locator: dict) -> dict:
    reading = graph.lookup(reading_ref, "assistance")
    if (reading["subtype"] != "reading" or reading["source_ref"] != _ref(_key(source_ref))
            or reading["manifestation_id"] != locator["manifestation_id"]):
        fail("READING_SOURCE", repr(_key(reading_ref)))
    if reading["status"] != "performed" or reading["reading_status"] == "not_read":
        fail("FALSE_READING", repr(_key(reading_ref)))
    manifestation = _locator(graph, source_ref, locator)
    if not _contains(_ranges(reading, manifestation), locator["start"], locator["end"]):
        fail("UNREAD_LOCATOR", repr(_key(source_ref)))
    return reading


def _passing_reviews(graph: RecordGraph, body: dict, scope: str) -> list[tuple[Pin, dict]]:
    result = []
    for ref in body["review_refs"]:
        review = graph.lookup(ref, "assistance")
        if (review["subtype"] == "review" and review["scope"] == scope
                and review["status"] == "performed" and review["outcome"] == "pass"
                and review["verification"] != "not_checked"):
            result.append((pin(ref), review))
    return result


def _exact_reviews(graph: RecordGraph, key: Pin, body: dict, scope: str) -> list[tuple[Pin, dict]]:
    result = []
    for review_key, review in _passing_reviews(graph, body, scope):
        for target in review["target_refs"]:
            target_key = pin(target)
            if (target_key[0] == key[0] and target_key[1] < key[1]
                    and _payload(graph.lookup(target_key, "claim")) == _payload(body)):
                result.append((review_key, review))
                break
    return result


def _validate_claim(graph: RecordGraph, key: Pin, body: dict) -> None:
    cls, lifecycle = body["class"], body["lifecycle"]
    evidence = [(pin(ref), graph.records[pin(ref)[0]]["kind"]) for ref in body["evidence_refs"]]
    allowed = {
        "project_constraint": {"claim"},
        "source_claim": _EXTRACTIONS,
        "empirical_finding": {"extraction"},
        "theoretical_interpretation": {"theoretical_extraction", "claim"},
        "synthesis_proposition": _EXTRACTIONS | {"claim"},
        "design_hypothesis": _EXTRACTIONS | {"claim"},
        "unvalidated_convention": _EXTRACTIONS | {"claim"},
    }[cls]
    for _, kind in evidence:
        if kind not in allowed:
            fail("CLAIM_EVIDENCE_TYPE", f"{key}: {cls} cannot use {kind} as its asserted evidence")
    for ref in body["appraisal_refs"]:
        graph.lookup(ref, "appraisal")
    for ref in body["review_refs"]:
        graph.lookup(ref, "assistance")
    for ref in body.get("test_refs", []):
        graph.lookup(ref, "experiment_protocol")
    if lifecycle not in _CLAIM_READY:
        return
    if cls not in {"project_constraint", "unvalidated_convention"} and not evidence:
        fail("UNSUPPORTED_PROMOTION", repr(key))
    if cls in {"theoretical_interpretation", "synthesis_proposition"}:
        if not body["argument"]["premises"] or not body["argument"]["inference_steps"]:
            fail("UNSUPPORTED_ARGUMENT", repr(key))
    checked = {pin(target) for _, review in _passing_reviews(graph, body, "source_fidelity") for target in review["target_refs"]}
    if cls in {"source_claim", "empirical_finding", "theoretical_interpretation", "synthesis_proposition", "design_hypothesis"}:
        for target, kind in evidence:
            if kind in _EXTRACTIONS and target not in checked:
                fail("UNSUPPORTED_PROMOTION", f"{key}: missing exact source check for {target}")
            if kind == "claim" and graph.lookup(target)["lifecycle"] not in _CLAIM_READY:
                fail("UNSUPPORTED_PROMOTION", f"{key}: unsupported input claim {target}")
    if cls == "empirical_finding":
        appraisals = [graph.lookup(ref, "appraisal") for ref in body["appraisal_refs"]]
        appraised = {pin(a["target_ref"]) for a in appraisals if a["status"] in {"checked", "revised"}}
        for target, _ in evidence:
            ex = graph.lookup(target, "extraction")
            if target not in appraised or ex["scope"] != "complete_report":
                fail("UNSUPPORTED_FINDING", f"{key}: exact appraisal and declared complete_report coverage required")
            if graph.lookup(ex["source_ref"], "source")["source_type"] == "review":
                fail("NONPRIMARY_FINDING", repr(target))
    if lifecycle in {"internally_audited", "externally_reviewed"} and not _exact_reviews(graph, key, body, "internal_audit"):
        fail("UNSUPPORTED_PROMOTION", f"{key}: missing exact-assertion internal audit")
    if lifecycle == "externally_reviewed" and not _exact_reviews(graph, key, body, "external_feedback"):
        fail("FALSE_EXTERNAL_REVIEW", f"{key}: missing exact-assertion human feedback")


def _validate_relations(graph: RecordGraph) -> None:
    screening: dict[tuple[str, str, str], list[Pin]] = defaultdict(list)
    hit_ordinals: dict[tuple[str, int], str] = {}
    for key, revision in graph.versions.items():
        kind, body = graph.records[key[0]]["kind"], revision["data"]
        if kind == "source":
            if "alias_of" in body:
                graph.lookup(body["alias_of"], "source")
            for link in body["family_links"]:
                graph.lookup(link["source_ref"], "source")
                if pin(link["source_ref"])[0] == key[0]:
                    fail("IDENTITY_LINK", f"{key}: self publication-family link")
        elif kind == "search_hit":
            graph.lookup(body["search_ref"], "search_run")
            identity = pin(body["search_ref"])[0], body["ordinal"]
            if identity in hit_ordinals and hit_ordinals[identity] != key[0]:
                fail("DUPLICATE_HIT", repr(identity))
            hit_ordinals[identity] = key[0]
            if "source_ref" in body:
                graph.lookup(body["source_ref"], "source")
            if "duplicate_of" in body:
                other = graph.lookup(body["duplicate_of"], "search_hit")
                if pin(body["duplicate_of"])[0] == key[0]:
                    fail("IDENTITY_LINK", f"{key}: duplicate of itself")
                if "source_ref" not in other or graph.canonical_id(pin(other["source_ref"])[0]) != graph.canonical_id(pin(body["source_ref"])[0]):
                    fail("DUPLICATE_IDENTITY", repr(key))
        elif kind == "screening":
            graph.lookup(body["source_ref"], "source")
            for ref in body["reading_refs"]:
                reading = graph.lookup(ref, "assistance")
                if reading["subtype"] != "reading" or reading["source_ref"] != body["source_ref"]:
                    fail("READING_SOURCE", repr(key))
            for ref in body["review_refs"]:
                graph.lookup(ref, "assistance")
            if body["stage"] == "full_text" and body["decision"] in {"include", "exclude"}:
                if not any(graph.lookup(ref)["status"] == "performed" and graph.lookup(ref)["reading_status"] != "not_read"
                           and graph.lookup(ref)["access_at_read"] in {"partial_text", "full_text_available"} for ref in body["reading_refs"]):
                    fail("FALSE_FULL_TEXT_SCREENING", repr(key))
            if "supersedes_ref" in body:
                old = graph.lookup(body["supersedes_ref"], "screening")
                if (graph.canonical_id(pin(old["source_ref"])[0]), old["stage"], old["protocol_version"]) != (graph.canonical_id(pin(body["source_ref"])[0]), body["stage"], body["protocol_version"]):
                    fail("SCREENING_SUPERSESSION", repr(key))
            if key == graph.latest_pin(key[0]):
                scope = graph.canonical_id(pin(body["source_ref"])[0]), body["stage"], body["protocol_version"]
                screening[scope].append(key)
        elif kind == "study":
            for ref in body["publications"]:
                graph.lookup(ref, "source")
            publication_ids = {graph.canonical_id(pin(ref)[0]) for ref in body["publications"]}
            for located in body["identity_locators"]:
                _locator(graph, located["source_ref"], located["locator"])
                if graph.canonical_id(pin(located["source_ref"])[0]) not in publication_ids:
                    fail("IDENTITY_LINK", repr(key))
            if body["identity_status"] == "resolved" and not body["identity_locators"]:
                fail("UNSUPPORTED_IDENTITY", f"{key}: resolved study identity needs located source evidence")
            if "alias_of" in body:
                graph.lookup(body["alias_of"], "study")
        elif kind == "sample":
            for located in body.get("evidence", []):
                _locator(graph, located["source_ref"], located["locator"])
            for overlap in body["overlap"]:
                graph.lookup(overlap["sample_ref"], "sample")
                if pin(overlap["sample_ref"])[0] == key[0]:
                    fail("SAMPLE_OVERLAP", f"{key}: self overlap")
        elif kind == "experiment":
            graph.lookup(body["study_ref"], "study")
            for ref in body["sample_refs"]:
                graph.lookup(ref, "sample")
            if len({pin(ref)[0] for ref in body["sample_refs"]}) != len(body["sample_refs"]):
                fail("IDENTITY_LINK", f"{key}: same sample repeated at different revisions")
        elif kind in _EXTRACTIONS:
            reading = _reading(graph, body["source_ref"], body["reading_ref"], body["locator"])
            if kind == "theoretical_extraction":
                continue
            exp = graph.lookup(body["experiment_ref"], "experiment")
            study = graph.lookup(exp["study_ref"], "study")
            sample = graph.lookup(body["sample_ref"], "sample")
            if pin(body["sample_ref"])[0] not in {pin(ref)[0] for ref in exp["sample_refs"]}:
                fail("IDENTITY_LINK", f"{key}: sample is not used by experiment")
            if graph.canonical_id(pin(body["source_ref"])[0]) not in {graph.canonical_id(pin(ref)[0]) for ref in study["publications"]}:
                fail("IDENTITY_LINK", f"{key}: report is not linked to study")
            outcome = exp["outcomes"].get(body["outcome"])
            if outcome is None or body["unit"] != outcome["unit"]:
                fail("OUTCOME_UNIT", repr(key))
            if not set(body["conditions"]) <= set(exp["conditions"]) or body["contrast"] != outcome["contrast"]:
                fail("OUTCOME_CONTRAST", repr(key))
            if "timepoints" in outcome and body["timepoint"] not in outcome["timepoints"]:
                fail("OUTCOME_TIMEPOINT", repr(key))
            n, sample_n, value = known(body["n"]), known(sample["n"]), known(body["value"])
            if (n is not None and sample_n is not None and n > sample_n) or (n == 0 and value is not None):
                fail("OUTCOME_N", repr(key))
            if body["dependence"]["relation"] == "independent" and exp["dependence"]["relation"] in {"shared_sample", "repeated_measures", "shared_control", "overlap"}:
                fail("FALSE_INDEPENDENCE", repr(key))
            for locator in body["field_locators"].values():
                _reading(graph, body["source_ref"], body["reading_ref"], locator)
            if body["scope"] == "complete_report" and reading["reading_status"] != "full_item_read":
                fail("FALSE_FULL_EXTRACTION", repr(key))
            dispersion = known(body["dispersion"])
            if dispersion is not None and dispersion["measure"] in {"sd", "se", "ci95"} and dispersion["unit"] != body["unit"]:
                fail("DISPERSION_UNIT", repr(key))
            derivation = known(body["derivation"])
            if derivation is not None:
                for ref in derivation["input_refs"]:
                    graph.lookup(ref, "extraction")
        elif kind == "appraisal":
            target_kind = graph.records[pin(body["target_ref"])[0]]["kind"]
            if target_kind not in _EXTRACTIONS | {"source", "study", "experiment", "claim"}:
                fail("APPRAISAL_TARGET", repr(key))
            for located in body["evidence"]:
                _locator(graph, located["source_ref"], located["locator"])
        elif kind == "claim":
            _validate_claim(graph, key, body)
        elif kind == "requirement":
            for ref in body["claim_refs"]:
                graph.lookup(ref, "claim")
            for ref in body["test_refs"]:
                graph.lookup(ref, "experiment_protocol")
            for ref in body["result_refs"]:
                graph.lookup(ref, "extraction")
            if body["status"] == "evidence_supported" and not body["result_refs"]:
                fail("UNSUPPORTED_REQUIREMENT", repr(key))
        elif kind == "experiment_protocol":
            for ref in body["hypothesis_refs"]:
                graph.lookup(ref, "claim")
            for ref in body["gate_refs"]:
                graph.lookup(ref, "human_gate")
            if body["status"] == "ready_for_authorized_execution":
                if not body["gate_refs"] or not any(graph.lookup(ref)["gate_class"] == "participants" for ref in body["gate_refs"]):
                    fail("UNSATISFIED_GATE", f"{key}: actual participant readiness gate required")
                for ref in body["gate_refs"]:
                    if graph.lookup(ref)["status"] != "satisfied":
                        fail("UNSATISFIED_GATE", repr(key))
        elif kind == "assistance":
            if body["subtype"] == "reading":
                m = _manifestation(graph, body["source_ref"], body["manifestation_id"])
                covered = _ranges(body, m)
                if body["reading_status"] == "not_read":
                    if covered:
                        fail("FALSE_READING", repr(key))
                elif body["status"] != "performed" or body["access_at_read"] not in _READABLE or not covered:
                    fail("FALSE_READING", repr(key))
                if body["reading_status"] == "full_item_read" and (covered != [_bounds(m)] or body["access_at_read"] != "full_text_available"):
                    fail("FALSE_FULL_READING", repr(key))
            elif body["subtype"] == "review" and body["scope"] == "external_feedback":
                gate = graph.lookup(body["gate_ref"], "human_gate")
                if body["status"] == "performed":
                    if (gate["status"] != "satisfied" or gate["gate_class"] != "external_review"
                            or revision["actor"]["kind"] != "human"
                            or body["verification"] not in {"human_checked", "independent_human_checked"}):
                        fail("FALSE_EXTERNAL_REVIEW", repr(key))
    for scope, current in screening.items():
        superseded = {pin(graph.lookup(key)["supersedes_ref"]) for key in current if "supersedes_ref" in graph.lookup(key)}
        effective = [key for key in current if key not in superseded]
        if len(effective) > 1:
            fail("SCREENING_CONFLICT", repr(scope))


def _identity(graph: RecordGraph) -> None:
    aliases: dict[str, set[str]] = {rid: set() for rid in graph.records}
    for rid, revision in graph.latest.items():
        body = revision["data"]
        if "alias_of" in body:
            target = pin(body["alias_of"])[0]
            graph.lookup(body["alias_of"], graph.records[rid]["kind"])
            if target == rid:
                fail("IDENTITY_ALIAS_CYCLE", rid)
            aliases[rid].add(target)
            graph.aliases[rid] = target
    _dag(aliases, "IDENTITY_ALIAS_CYCLE")
    samples = sorted(rid for rid, row in graph.records.items() if row["kind"] == "sample")
    relations: dict[tuple[str, str], set[str]] = defaultdict(set)
    adjacency: dict[str, set[str]] = {rid: set() for rid in samples}
    for rid in samples:
        for overlap in graph.latest[rid]["data"]["overlap"]:
            other = pin(overlap["sample_ref"])[0]
            graph.lookup(overlap["sample_ref"], "sample")
            pair = tuple(sorted((rid, other)))
            relations[pair].add(overlap["relation"])
    for pair, declared in relations.items():
        if "independent" in declared and declared & _SHARED:
            fail("SAMPLE_OVERLAP_CONFLICT", repr(pair))
        if declared & _SHARED:
            left, right = pair
            adjacency[left].add(right)
            adjacency[right].add(left)
    for position, left in enumerate(samples):
        for right in samples[position + 1:]:
            pair = left, right
            if not relations.get(pair) or "unknown" in relations[pair]:
                graph.unknown_overlap.add(pair)
    remaining = set(samples)
    while remaining:
        stack = [min(remaining)]
        group = set()
        while stack:
            node = stack.pop()
            if node not in group:
                group.add(node)
                stack.extend(sorted(adjacency[node] - group))
        remaining -= group
        graph.sample_groups.append(sorted(group))


def _source_signature(body: dict) -> dict:
    observation_fields = {"access_status", "access_at", "access_reason", "metadata_status", "metadata_evidence", "rights"}
    result = {name: value for name, value in body.items() if name not in observation_fields}
    result["identifiers"] = [{"scheme": item["scheme"], "value": item["value"]} for item in body["identifiers"]]
    return result


def _material_signature(kind: str, body: dict) -> dict:
    if kind == "source":
        return _source_signature(body)
    result = _payload(body)
    if kind == "study":
        result.pop("identity_status", None)
    return result


def _amendments(graph: RecordGraph) -> None:
    corrections: dict[tuple[Pin, Pin], list[dict]] = defaultdict(list)
    invalidated_sources: set[Pin] = set()
    quarantined_source_bytes: set[Pin] = set()
    for key, revision in graph.versions.items():
        kind, body = graph.records[key[0]]["kind"], revision["data"]
        if kind == "source" and body["validity"] in {"retracted", "withdrawn"}:
            # The first recorded observation may already be a retraction.
            # Missing earlier local history must not make it usable evidence.
            graph.invalidated.add(key)
            invalidated_sources.add(key)
            quarantined_source_bytes.add(key)
        if kind in {"extraction", "theoretical_extraction", "appraisal", "claim", "requirement", "experiment", "sample"}:
            status = body.get("lifecycle", body.get("status"))
            if status in {"withdrawn", "superseded", "rejected", "disputed"}:
                graph.invalidated.add(key)
            if key == graph.latest_pin(key[0]) and status in {"withdrawn", "superseded", "rejected"}:
                graph.invalidated.update((key[0], rev["rev"]) for rev in graph.records[key[0]]["revisions"])
    for rid, latest in graph.latest.items():
        kind, current = graph.records[rid]["kind"], latest["data"]
        if kind == "study" and current["identity_status"] in {"unresolved", "provisional"}:
            for earlier in graph.records[rid]["revisions"][:-1]:
                if earlier["data"]["identity_status"] in {"resolved", "fixture_asserted_same"}:
                    graph.invalidated.add((rid, earlier["rev"]))
        elif kind == "appraisal":
            for earlier in graph.records[rid]["revisions"][:-1]:
                old = earlier["data"]
                if (old["target_ref"] == current["target_ref"] and
                        (current["status"] == "disputed" or _payload(old) != _payload(current))):
                    graph.invalidated.add((rid, earlier["rev"]))
        elif kind == "assistance" and current["subtype"] == "review":
            adverse = current["status"] != "performed" or current["outcome"] != "pass" or current["verification"] == "not_checked"
            if adverse:
                targets = {pin(ref) for ref in current["target_refs"]}
                for earlier in graph.records[rid]["revisions"][:-1]:
                    old = earlier["data"]
                    if (old["subtype"] == "review" and old["scope"] == current["scope"]
                            and targets & {pin(ref) for ref in old["target_refs"]}):
                        graph.invalidated.add((rid, earlier["rev"]))
    for key, revision in graph.versions.items():
        if graph.records[key[0]]["kind"] != "amendment":
            continue
        body = revision["data"]
        targets = [pin(ref) for ref in body["target_refs"]]
        replacements = [pin(ref) for ref in body["replacement_refs"]]
        applied = body["status"] in {"applied", "verified"}
        if applied and not targets and body["kind"] != "protocol_change":
            fail("AMENDMENT", f"{key}: applied amendment has no targets")
        for ref in [*targets, *replacements]:
            graph.lookup(ref)
            if stamp(graph.versions[ref]["at"]) > stamp(revision["at"]):
                fail("FUTURE_AMENDMENT", repr(key))
        correction_kinds = {"extraction_correction", "source_correction", "record_correction", "nonmaterial"}
        if body["kind"] in correction_kinds:
            if len(targets) != len(replacements):
                fail("AMENDMENT", f"{key}: correction pairs differ in length")
            for old, new in zip(targets, replacements):
                if old[0] != new[0] or old[1] >= new[1]:
                    fail("AMENDMENT", f"{key}: correction must retain ID and advance revision")
                if body["kind"] == "extraction_correction":
                    graph.lookup(old, "extraction")
                elif body["kind"] == "source_correction":
                    graph.lookup(old, "source")
                if applied:
                    corrections[(old, new)].append(body)
        elif body["kind"] == "source_invalidation":
            for target in targets:
                graph.lookup(target, "source")
        elif body["kind"] in {"identity_merge", "identity_split"}:
            kinds = {graph.records[ref[0]]["kind"] for ref in [*targets, *replacements]}
            if kinds and (len(kinds) != 1 or not kinds <= {"source", "study", "sample"}):
                fail("AMENDMENT", f"{key}: identity amendment mixes record families")
            if applied:
                for old in targets:
                    for new in replacements:
                        if old[0] == new[0] and old[1] < new[1]:
                            corrections[(old, new)].append(body)
        if applied and body["materiality"] == "material":
            graph.invalidated.update(targets)
            invalidated_sources.update(target for target in targets if graph.records[target[0]]["kind"] == "source")
            if body["kind"] == "source_invalidation":
                quarantined_source_bytes.update(targets)
    # A later amendment revision cannot silently remove a previously applied
    # invalidation. A rescission keeps the historical quarantine; explicit new
    # records and new evidence are necessary to restore usable support.
    for target in invalidated_sources:
        source = graph.lookup(target, "source")
        hashes = {m["sha256"] for m in source["manifestations"]}
        for candidate, revision in graph.versions.items():
            if candidate[0] != target[0]:
                continue
            candidate_hashes = {m["sha256"] for m in revision["data"]["manifestations"]}
            same_invalid_version = candidate_hashes == hashes if target in quarantined_source_bytes else _source_signature(revision["data"]) == _source_signature(source)
            if same_invalid_version:
                graph.invalidated.add(candidate)
    for rid, row in graph.records.items():
        if row["kind"] not in {"source", "extraction", "theoretical_extraction", "sample", "experiment", "study"}:
            continue
        for index in range(1, len(row["revisions"])):
            before, after = row["revisions"][index - 1], row["revisions"][index]
            previous, current = (rid, index), (rid, index + 1)
            changed = _material_signature(row["kind"], before["data"]) != _material_signature(row["kind"], after["data"])
            if not changed:
                continue
            amendments = corrections.get((previous, current), [])
            if row["kind"] == "source" and after["data"]["validity"] in {"retracted", "withdrawn", "superseded"} and previous in graph.invalidated:
                continue
            if not amendments:
                fail("MISSING_CORRECTION_AMENDMENT", f"{previous} -> {current}")
            if row["kind"] != "source" and not any(a["materiality"] == "material" for a in amendments):
                fail("FALSE_NONMATERIAL_CORRECTION", repr(current))
            if row["kind"] == "source" and not any(a["materiality"] == "material" for a in amendments):
                protected = {"manifestations", "validity", "edition", "language", "source_type", "alias_of", "family_links"}
                if any(before["data"].get(name) != after["data"].get(name) for name in protected):
                    fail("FALSE_NONMATERIAL_CORRECTION", repr(current))
    reverse: dict[Pin, set[Pin]] = defaultdict(set)
    for key, dependencies in graph.basis.items():
        for dependency in dependencies | graph.currency_edges.get(key, set()):
            reverse[dependency].add(key)
    graph.stale = set(graph.invalidated)
    queue = deque(sorted(graph.invalidated))
    while queue:
        for dependent in sorted(reverse[queue.popleft()]):
            if dependent not in graph.stale:
                graph.stale.add(dependent)
                queue.append(dependent)


def validate_graph(records: list[dict]) -> RecordGraph:
    """Validate typed relationships and return a reusable deterministic index."""
    if not isinstance(records, list):
        fail("SHAPE", "records must be a list")
    rows: dict[str, dict] = {}
    versions: dict[Pin, dict] = {}
    basis: dict[Pin, set[Pin]] = {}
    latest: dict[str, dict] = {}
    contexts = set()
    for row in records:
        if not isinstance(row, dict) or type(row.get("synthetic")) is not bool:
            fail("SHAPE", "record requires a Boolean synthetic flag")
        expected = "fixture" if row["synthetic"] else "live"
        contexts.add(expected)
        validate_record(row, expected_kind=expected)
        rid = row["id"]
        if rid in rows:
            fail("DUPLICATE_ID", rid)
        rows[rid], latest[rid] = row, row["revisions"][-1]
        for revision in row["revisions"]:
            key = rid, revision["rev"]
            versions[key] = revision
            basis[key] = {pin(ref) for ref in revision["basis"]}
            missing = semantic_dependencies(row, revision) - basis[key]
            if missing:
                fail("MISSING_BASIS", f"{key}: {sorted(missing)}")
    if len(contexts) > 1:
        fail("CONTAMINATION", "mixed synthetic and live records")
    graph = RecordGraph(rows, versions, basis, latest)
    for key, revision in versions.items():
        for ref in references(revision):
            graph.lookup(ref)
        for dependency in basis[key]:
            if stamp(versions[dependency]["at"]) > stamp(revision["at"]):
                fail("FUTURE_BASIS", repr(key))
        if rows[key[0]]["kind"] == "experiment":
            body = revision["data"]
            # Revising an actual study/sample identity invalidates experimental
            # context that pins it. Bare publication membership still conveys
            # no source-evidence premise and never propagates SRC retraction to
            # a study by itself.
            graph.currency_edges[key] = {pin(body["study_ref"]), *(pin(ref) for ref in body["sample_refs"])}
    _dag(basis, "DEPENDENCY_CYCLE")
    _identity(graph)
    _validate_relations(graph)
    _amendments(graph)
    return graph
