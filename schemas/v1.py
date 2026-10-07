"""Closed executable mhac-records/1 schemas; see README.md for the data dictionary.

This module validates one logical record, including its local revision history.
It has no filesystem/network access and does not infer scientific acceptance.
Cross-record support, reading coverage and amendments live in record_graph.py.
"""
from __future__ import annotations

from datetime import date, datetime
import math
from pathlib import PurePosixPath
import re
from typing import Any, Callable, Iterator

from . import ValidationError

CONTRACT = "mhac-records/1"
PREFIXES = {
    "source": "SRC", "search_run": "SRCH", "search_hit": "HIT",
    "screening": "SCR", "study": "STUDY", "experiment": "EXP",
    "sample": "SAMPLE", "theoretical_extraction": "TX", "extraction": "EX",
    "appraisal": "APP", "claim": "CLM", "requirement": "REQ",
    "experiment_protocol": "TEST", "amendment": "AMD", "assistance": "AID",
    "human_gate": "HG",
}
KINDS = set(PREFIXES)
CLASSES = {
    "project_constraint", "source_claim", "empirical_finding",
    "theoretical_interpretation", "synthesis_proposition", "design_hypothesis",
    "unvalidated_convention",
}
ACCESS = {
    "not_attempted", "metadata_only", "abstract_only", "partial_text",
    "full_text_available", "unavailable",
}
READING = {"not_read", "selected_ranges_read", "full_item_read"}
LIFECYCLE = {
    "proposed", "source_checked", "internally_audited", "externally_reviewed",
    "superseded", "withdrawn",
}
TRANSITIONS = {
    "proposed": {"proposed", "source_checked", "superseded", "withdrawn"},
    "source_checked": {"proposed", "source_checked", "internally_audited", "superseded", "withdrawn"},
    "internally_audited": {"proposed", "source_checked", "internally_audited", "externally_reviewed", "superseded", "withdrawn"},
    "externally_reviewed": {"proposed", "source_checked", "externally_reviewed", "superseded", "withdrawn"},
    "superseded": {"superseded"}, "withdrawn": {"withdrawn"},
}
FACTUAL_STATUSES = {
    "discovery", "source_reported", "researcher_interpretation", "derived",
    "project_decision", "synthetic",
}
MISSING_STATES = {"unknown", "not_reported", "not_applicable"}
COORDINATES = {"file_page_1based", "pdf_page_0based", "html_paragraph_1based"}
DEPENDENCE = {"shared_sample", "repeated_measures", "shared_control", "overlap", "independent", "unknown"}
Pin = tuple[str, int]
_ID = re.compile(r"[A-Z][A-Z0-9]*-[A-Z0-9]+(?:-[A-Z0-9]+)*\Z")
_STAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)\Z")


def fail(code: str, message: str) -> None:
    raise ValidationError(f"{code}: {message}")


def _object(value: Any, required: set[str], optional: set[str] = frozenset(), *, field: str = "object") -> None:
    if not isinstance(value, dict):
        fail("SHAPE", f"{field} must be an object")
    missing, extra = required - set(value), set(value) - required - optional
    if missing or extra:
        fail("SHAPE", f"{field} missing {sorted(missing)}; unexpected {sorted(map(str, extra))}")


def nonblank(value: Any, field: str = "text") -> None:
    if not isinstance(value, str) or not value.strip():
        fail("SHAPE", f"{field} must be nonblank text")


def _enum(value: Any, allowed: set[str], field: str, code: str = "STATUS") -> None:
    if not isinstance(value, str) or value not in allowed:
        fail(code, f"Invalid {field}: {value!r}")


def _integer(value: Any, field: str, minimum: int = 0) -> None:
    if type(value) is not int or value < minimum:
        fail("NUMBER", f"{field} must be an integer >= {minimum}")


def _number(value: Any, field: str = "number", minimum: float | None = None, maximum: float | None = None) -> None:
    # Avoid float conversion of arbitrarily large integers: integers are finite.
    if type(value) not in {int, float} or (type(value) is float and not math.isfinite(value)):
        fail("NUMBER", f"{field} must be finite and cannot be boolean")
    if minimum is not None and value < minimum or maximum is not None and value > maximum:
        fail("NUMBER", f"{field} is outside its permitted range")


def _list(value: Any, field: str, minimum: int = 0) -> None:
    if not isinstance(value, list) or len(value) < minimum:
        fail("SHAPE", f"{field} must be a list with at least {minimum} entries")


def _texts(value: Any, field: str, minimum: int = 0) -> None:
    _list(value, field, minimum)
    for item in value:
        nonblank(item, field)
    if len(value) != len(set(value)):
        fail("DUPLICATE_VALUE", field)


def _missing(value: Any, field: str) -> None:
    _object(value, {"state", "reason"}, field=field)
    _enum(value["state"], MISSING_STATES, field + ".state", "MISSING_VALUE")
    nonblank(value["reason"], field + ".reason")


def _tagged(value: Any, field: str, check: Callable[[Any, str], None]) -> None:
    if isinstance(value, dict) and value.get("state") == "known":
        _object(value, {"state", "value"}, field=field)
        check(value["value"], field + ".value")
    else:
        _missing(value, field)


def known_value(value: Any) -> Any | None:
    """Unwrap a schema-validated tagged value; explicit missingness becomes None."""
    return value["value"] if isinstance(value, dict) and value.get("state") == "known" else None


def _text_or_missing(value: Any, field: str) -> None:
    if isinstance(value, str):
        nonblank(value, field)
    else:
        _missing(value, field)


def _numeric_or_missing(value: Any, field: str, *, integer: bool = False) -> None:
    if isinstance(value, dict):
        _missing(value, field)
    elif integer:
        _integer(value, field)
    else:
        _number(value, field)


def stamp(value: Any, field: str = "at") -> datetime:
    if not isinstance(value, str) or _STAMP.fullmatch(value) is None:
        fail("TIME", f"{field} needs an RFC 3339 timestamp with a timezone")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        fail("TIME", f"Invalid {field}")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        fail("TIME", f"Timezone required for {field}")
    return parsed


def _date(value: Any, field: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", value) is None:
        fail("DATE", f"{field} must be a year, year-month or ISO calendar date")
    parts = [int(x) for x in value.split("-")]
    try:
        date(parts[0], parts[1] if len(parts) > 1 else 1, parts[2] if len(parts) > 2 else 1)
    except ValueError:
        fail("DATE", f"Invalid {field}")


def _date_window(value: Any, field: str) -> None:
    _object(value, {"start", "end"}, field=field)
    for key in ("start", "end"):
        _tagged(value[key], field + "." + key, _date)
    start, end = known_value(value["start"]), known_value(value["end"])
    # Only compare like precisions; an unknown day must not become an invented day.
    if start is not None and end is not None and len(start) == len(end) and start > end:
        fail("DATE", f"Reversed {field}")


def _actor(value: Any, field: str = "actor") -> None:
    _object(value, {"kind", "id"}, {"tool", "model"}, field=field)
    _enum(value["kind"], {"agent", "human"}, field + ".kind", "ACTOR")
    nonblank(value["id"], field + ".id")
    for key in ("tool", "model"):
        if key in value:
            _text_or_missing(value[key], field + "." + key)


def pin(value: Any) -> Pin:
    _object(value, {"id", "rev"}, field="pin")
    if not isinstance(value["id"], str) or _ID.fullmatch(value["id"]) is None:
        fail("REFERENCE_SHAPE", f"Invalid reference ID {value['id']!r}")
    if type(value["rev"]) is not int or value["rev"] < 1:
        fail("REFERENCE_SHAPE", "Reference revision must be a positive integer")
    return value["id"], value["rev"]


def _pins(value: Any, field: str, minimum: int = 0) -> None:
    _list(value, field, minimum)
    seen = [pin(item) for item in value]
    if len(seen) != len(set(seen)):
        fail("DUPLICATE_REFERENCE", field)


def references(value: Any) -> Iterator[Pin]:
    """Find exact reference objects; evidence edges are revision.basis only."""
    if isinstance(value, dict):
        if "id" in value and "rev" in value:
            yield pin(value)
        else:
            for item in value.values():
                yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)


def _path(value: Any, field: str) -> None:
    nonblank(value, field)
    path = PurePosixPath(value)
    if ("\\" in value or "\x00" in value or ":" in value or path.is_absolute()
            or any(part in {"", ".", ".."} for part in value.split("/"))
            or str(path) != value):
        fail("ARTIFACT", f"{field} must be a normalized relative POSIX path")


def _digest(value: Any, field: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        fail("ARTIFACT", f"{field} must be a lowercase SHA-256 digest")


def _artifact(value: Any, field: str) -> None:
    _object(value, {"path", "sha256"}, field=field)
    _path(value["path"], field + ".path")
    _digest(value["sha256"], field + ".sha256")


def locator(value: Any, field: str = "locator") -> None:
    optional = {"printed_label", "section", "paragraph", "table", "figure", "cell"}
    _object(value, {"manifestation_id", "coordinate", "start", "end"}, optional, field=field)
    nonblank(value["manifestation_id"], field + ".manifestation_id")
    _enum(value["coordinate"], COORDINATES, field + ".coordinate", "LOCATOR")
    minimum = 0 if value["coordinate"] == "pdf_page_0based" else 1
    _integer(value["start"], field + ".start", minimum)
    _integer(value["end"], field + ".end", minimum)
    if value["end"] < value["start"]:
        fail("LOCATOR", f"Reversed {field}")
    for key in optional & set(value):
        nonblank(value[key], field + "." + key)


def _located_sources(value: Any, field: str) -> None:
    _list(value, field)
    for item in value:
        _object(item, {"source_ref", "locator"}, field=field)
        pin(item["source_ref"])
        locator(item["locator"], field + ".locator")


def _dependence(value: Any, field: str = "dependence") -> None:
    _object(value, {"relation", "correlation"}, field=field)
    _enum(value["relation"], DEPENDENCE, field + ".relation")
    _tagged(value["correlation"], field + ".correlation", lambda x, f: _number(x, f, -1, 1))
    if value["relation"] == "unknown" and known_value(value["correlation"]) is not None:
        fail("DEPENDENCE", "Unknown dependence cannot assert a known correlation")


def _source(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"title", "authors", "publication_date", "identifiers", "source_type", "language", "edition", "metadata_status", "metadata_evidence", "access_status", "access_at", "access_reason", "rights", "validity", "family_links", "manifestations"}, {"alias_of", "alias_reason"}, field="source")
    for key in ("title", "access_reason"):
        nonblank(b[key], key)
    _list(b["authors"], "authors")
    for author in b["authors"]:
        _object(author, {"name", "role"}, field="author")
        nonblank(author["name"], "author.name")
        _enum(author["role"], {"author", "editor", "translator", "corporate_author"}, "author.role")
    _tagged(b["publication_date"], "publication_date", _date)
    for key in ("language", "edition"):
        _tagged(b[key], key, nonblank)
    _enum(b["source_type"], {"article", "book", "chapter", "conference_paper", "thesis", "preprint", "report", "review", "web", "correction", "other"}, "source_type")
    _enum(b["metadata_status"], {"candidate", "verified", "conflict"}, "metadata_status")
    _texts(b["metadata_evidence"], "metadata_evidence", 1 if b["metadata_status"] in {"verified", "conflict"} else 0)
    _enum(b["access_status"], ACCESS, "access_status")
    if stamp(b["access_at"], "access_at") > stamp(revision["at"]):
        fail("TIME", "Source access observation is after its recorded revision")
    _list(b["identifiers"], "identifiers")
    seen = set()
    for identifier in b["identifiers"]:
        _object(identifier, {"scheme", "value", "status", "provenance"}, field="identifier")
        _enum(identifier["scheme"], {"doi", "isbn", "url", "other"}, "identifier.scheme")
        _enum(identifier["status"], {"candidate", "verified", "conflict"}, "identifier.status")
        nonblank(identifier["value"], "identifier.value")
        nonblank(identifier["provenance"], "identifier.provenance")
        identity = identifier["scheme"], identifier["value"]
        if identity in seen:
            fail("DUPLICATE_VALUE", "Duplicate source identifier")
        seen.add(identity)
    rights = b["rights"]
    _object(rights, {"status", "reason", "evidence"}, field="rights")
    _enum(rights["status"], {"unknown", "metadata_only", "quotation_limited", "redistribution_permitted"}, "rights.status")
    nonblank(rights["reason"], "rights.reason")
    _tagged(rights["evidence"], "rights.evidence", nonblank)
    if rights["status"] != "unknown" and known_value(rights["evidence"]) is None:
        fail("RIGHTS", "Positive rights status requires supporting evidence")
    _enum(b["validity"], {"active", "corrected", "retracted", "withdrawn", "superseded"}, "validity")
    _list(b["family_links"], "family_links")
    for link in b["family_links"]:
        _object(link, {"relation", "source_ref", "reason"}, field="family_link")
        _enum(link["relation"], {"duplicate_of", "version_of", "translation_of", "companion_of", "correction_of"}, "family_link.relation")
        pin(link["source_ref"])
        nonblank(link["reason"], "family_link.reason")
    if "alias_of" in b or "alias_reason" in b:
        if not {"alias_of", "alias_reason"} <= set(b) or b["validity"] != "superseded":
            fail("ALIAS", "Source alias requires superseded validity, alias_of and alias_reason")
        pin(b["alias_of"])
        nonblank(b["alias_reason"], "alias_reason")
    _list(b["manifestations"], "manifestations")
    mids = set()
    for m in b["manifestations"]:
        _object(m, {"id", "sha256", "extent", "coordinate"}, {"fixture_path", "local_path", "location"}, field="manifestation")
        nonblank(m["id"], "manifestation.id")
        if m["id"] in mids:
            fail("MANIFESTATION", "Duplicate manifestation ID")
        mids.add(m["id"])
        _digest(m["sha256"], "manifestation.sha256")
        _integer(m["extent"], "manifestation.extent", 1)
        _enum(m["coordinate"], COORDINATES, "manifestation.coordinate", "MANIFESTATION")
        if "fixture_path" in m:
            if not synthetic:
                fail("CONTAMINATION", "Live manifestation cannot use fixture_path")
            _path(m["fixture_path"], "manifestation.fixture_path")
        if "local_path" in m:
            _path(m["local_path"], "manifestation.local_path")
            if rights["status"] != "redistribution_permitted":
                fail("RIGHTS", "Retained local source bytes require explicit redistribution permission")
        if "location" in m:
            nonblank(m["location"], "manifestation.location")


def _search_run(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"lane", "protocol_version", "mode", "status", "platform", "interface", "query", "filters", "coverage", "started_at", "finished_at", "reported_count", "retrieved_count", "export", "pagination", "failures", "boundary"}, field="search_run")
    for key in ("lane", "protocol_version", "platform", "interface", "query", "boundary"):
        nonblank(b[key], key)
    _enum(b["mode"], {"pilot", "production", "update"}, "mode")
    _enum(b["status"], {"planned", "running", "completed", "partial", "failed"}, "search status")
    _texts(b["filters"], "filters")
    _date_window(b["coverage"], "coverage")
    for key in ("started_at", "finished_at"):
        _tagged(b[key], key, stamp)
    start, end = known_value(b["started_at"]), known_value(b["finished_at"])
    if start is not None and stamp(start) > stamp(revision["at"]):
        fail("TIME", "Search begins after its recorded revision")
    if end is not None and (start is None or stamp(end) < stamp(start) or stamp(end) > stamp(revision["at"])):
        fail("TIME", "Search finish needs a prior start and cannot postdate its record")
    if b["status"] == "planned" and (start is not None or end is not None):
        fail("STATUS", "Planned search cannot claim actual run dates")
    if b["status"] != "planned" and start is None:
        fail("TIME", "A started search needs its actual start date")
    if b["status"] in {"completed", "partial", "failed"} and end is None:
        fail("TIME", "Finished search needs its actual end date")
    if b["status"] == "running" and end is not None:
        fail("STATUS", "Running search cannot have a finish date")
    _numeric_or_missing(b["reported_count"], "reported_count", integer=True)
    _integer(b["retrieved_count"], "retrieved_count")
    _tagged(b["export"], "export", _artifact)
    _object(b["pagination"], {"complete", "detail"}, field="pagination")
    if type(b["pagination"]["complete"]) is not bool:
        fail("SHAPE", "pagination.complete must be boolean")
    nonblank(b["pagination"]["detail"], "pagination.detail")
    _texts(b["failures"], "failures")
    if b["status"] == "completed" and (not b["pagination"]["complete"] or b["failures"]):
        fail("SEARCH_COMPLETENESS", "Completed search must reconcile pagination and failures")
    if b["status"] == "planned" and (b["retrieved_count"] != 0 or known_value(b["export"]) is not None):
        fail("STATUS", "Planned search cannot contain retrieved results")
    if b["retrieved_count"] and known_value(b["export"]) is None:
        fail("SEARCH_EXPORT", "Retrieved occurrences require a retained export artifact")


def _search_hit(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"search_ref", "ordinal", "raw_metadata", "returned_identifiers", "status", "resolution_reason"}, {"source_ref", "duplicate_of"}, field="search_hit")
    pin(b["search_ref"])
    _integer(b["ordinal"], "ordinal", 1)
    nonblank(b["raw_metadata"], "raw_metadata")
    nonblank(b["resolution_reason"], "resolution_reason")
    _enum(b["status"], {"unresolved", "resolved", "duplicate", "unresolvable"}, "search_hit.status")
    _list(b["returned_identifiers"], "returned_identifiers")
    for identifier in b["returned_identifiers"]:
        _object(identifier, {"scheme", "value"}, field="returned_identifier")
        _enum(identifier["scheme"], {"doi", "isbn", "url", "other"}, "returned_identifier.scheme")
        nonblank(identifier["value"], "returned_identifier.value")
    if b["status"] in {"resolved", "duplicate"}:
        if "source_ref" not in b:
            fail("RESOLUTION", "Resolved occurrence needs a canonical source")
        pin(b["source_ref"])
    elif "source_ref" in b:
        fail("RESOLUTION", "Unresolved occurrence cannot identify a canonical source")
    if "duplicate_of" in b:
        if b["status"] != "duplicate":
            fail("RESOLUTION", "duplicate_of is only valid for duplicate occurrences")
        pin(b["duplicate_of"])


def _screening(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"source_ref", "stage", "protocol_version", "rule", "decision", "reason", "access_limitation", "reading_refs", "review_refs"}, {"supersedes_ref"}, field="screening")
    pin(b["source_ref"])
    _enum(b["stage"], {"title_abstract", "full_text"}, "screening.stage")
    _enum(b["decision"], {"pending", "include", "exclude", "awaiting_text", "uncertain"}, "screening.decision")
    for key in ("protocol_version", "rule", "reason", "access_limitation"):
        nonblank(b[key], key)
    for key in ("reading_refs", "review_refs"):
        _pins(b[key], key)
    if "supersedes_ref" in b:
        pin(b["supersedes_ref"])


def _study(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"publications", "identity_status", "identity_basis", "identity_locators", "scope"}, {"alias_of"}, field="study")
    _pins(b["publications"], "publications", 1)
    _enum(b["identity_status"], {"unresolved", "provisional", "resolved", "fixture_asserted_same", "alias"}, "identity_status")
    for key in ("identity_basis", "scope"):
        nonblank(b[key], key)
    _located_sources(b["identity_locators"], "identity_locators")
    if b["identity_status"] == "fixture_asserted_same" and not synthetic:
        fail("CONTAMINATION", "Fixture assertion cannot identify a live study")
    if b["identity_status"] == "alias":
        if "alias_of" not in b:
            fail("ALIAS", "Aliased study needs its successor")
        pin(b["alias_of"])
    elif "alias_of" in b:
        fail("ALIAS", "Study alias_of requires alias state")


def _sample(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"n", "population", "recruitment", "missingness", "overlap", "uncertainty", "status"}, {"evidence", "collection_dates"}, field="sample")
    _numeric_or_missing(b["n"], "sample.n", integer=True)
    for key in ("population", "recruitment"):
        _text_or_missing(b[key], key)
    _tagged(b["missingness"], "missingness", nonblank)
    nonblank(b["uncertainty"], "uncertainty")
    _enum(b["status"], {"provisional", "checked", "withdrawn", "superseded"}, "sample.status")
    _list(b["overlap"], "overlap")
    seen = set()
    for relation in b["overlap"]:
        _object(relation, {"sample_ref", "relation", "reason"}, field="overlap")
        key = pin(relation["sample_ref"])
        if key in seen:
            fail("DUPLICATE_REFERENCE", "Multiple overlap assertions for one sample revision")
        seen.add(key)
        _enum(relation["relation"], {"known_shared", "partial_overlap", "shared_control", "unknown", "independent"}, "overlap.relation")
        nonblank(relation["reason"], "overlap.reason")
    if "evidence" in b:
        _located_sources(b["evidence"], "evidence")
    if "collection_dates" in b:
        _date_window(b["collection_dates"], "collection_dates")


def _experiment(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"study_ref", "sample_refs", "conditions", "outcomes", "dependence", "status", "report_label", "assignment"}, field="experiment")
    pin(b["study_ref"])
    _pins(b["sample_refs"], "sample_refs", 1)
    _texts(b["conditions"], "conditions", 1)
    if not isinstance(b["outcomes"], dict) or not b["outcomes"]:
        fail("SHAPE", "outcomes must be a nonempty keyed object")
    for key, outcome in b["outcomes"].items():
        nonblank(key, "outcome key")
        _object(outcome, {"unit", "contrast"}, {"timepoints"}, field="outcome")
        nonblank(outcome["unit"], "outcome.unit")
        nonblank(outcome["contrast"], "outcome.contrast")
        if "timepoints" in outcome:
            _texts(outcome["timepoints"], "outcome.timepoints", 1)
    _dependence(b["dependence"])
    _enum(b["status"], {"provisional", "extracted", "checked", "withdrawn", "superseded"}, "experiment.status")
    nonblank(b["report_label"], "report_label")
    nonblank(b["assignment"], "assignment")


def _extraction_status(value: Any) -> None:
    _enum(value, {"draft", "extracted", "source_checked", "disputed", "withdrawn", "superseded"}, "extraction.status")


def _theoretical(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"source_ref", "reading_ref", "locator", "status", "assertion", "definitions", "premises", "inference", "context", "objections", "interpretation", "rq_refs", "boundaries"}, field="theoretical_extraction")
    for key in ("source_ref", "reading_ref"):
        pin(b[key])
    locator(b["locator"])
    _extraction_status(b["status"])
    for key in ("assertion", "context", "interpretation", "boundaries"):
        nonblank(b[key], key)
    for key in ("premises", "inference", "objections"):
        _texts(b[key], key)
    _texts(b["rq_refs"], "rq_refs", 1)
    _list(b["definitions"], "definitions")
    seen = set()
    for definition in b["definitions"]:
        _object(definition, {"term", "definition"}, field="definition")
        for key in ("term", "definition"):
            nonblank(definition[key], key)
        if definition["term"] in seen:
            fail("DUPLICATE_VALUE", "A theoretical extraction defines a term twice")
        seen.add(definition["term"])


def _dispersion(value: Any, field: str) -> None:
    if not isinstance(value, dict):
        fail("SHAPE", "Known dispersion must be an object")
    _enum(value.get("measure"), {"sd", "se", "variance", "ci95"}, "dispersion.measure")
    if value["measure"] == "ci95":
        _object(value, {"measure", "lower", "upper", "unit"}, field=field)
        _number(value["lower"], "dispersion.lower")
        _number(value["upper"], "dispersion.upper")
        if value["lower"] > value["upper"]:
            fail("NUMBER", "Confidence interval endpoints are reversed")
    else:
        _object(value, {"measure", "value", "unit"}, field=field)
        _number(value["value"], "dispersion.value", 0)
    nonblank(value["unit"], "dispersion.unit")


def _derivation(value: Any, field: str) -> None:
    _object(value, {"input_refs", "transformation", "version", "assumptions", "output", "artifact"}, field=field)
    _pins(value["input_refs"], "derivation.input_refs", 1)
    nonblank(value["transformation"], "derivation.transformation")
    nonblank(value["version"], "derivation.version")
    _texts(value["assumptions"], "derivation.assumptions")
    _number(value["output"], "derivation.output")
    _artifact(value["artifact"], "derivation.artifact")


def _extraction(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"source_ref", "experiment_ref", "sample_ref", "outcome", "value", "unit", "n", "dispersion", "scope", "reading_ref", "locator", "note", "status", "conditions", "contrast", "timepoint", "task", "stimuli", "training", "population", "missingness", "dependence", "field_locators", "derivation"}, field="extraction")
    for key in ("source_ref", "experiment_ref", "sample_ref", "reading_ref"):
        pin(b[key])
    for key in ("outcome", "unit", "note", "contrast", "timepoint"):
        nonblank(b[key], key)
    _numeric_or_missing(b["value"], "value")
    _numeric_or_missing(b["n"], "n", integer=True)
    _tagged(b["dispersion"], "dispersion", _dispersion)
    _enum(b["scope"], {"bounded", "complete_report"}, "extraction.scope")
    locator(b["locator"])
    _extraction_status(b["status"])
    _texts(b["conditions"], "conditions", 1)
    for key in ("task", "stimuli", "training", "population"):
        _text_or_missing(b[key], key)
    _tagged(b["missingness"], "missingness", nonblank)
    _dependence(b["dependence"])
    _object(b["field_locators"], {"value", "n", "dispersion"}, field="field_locators")
    for key, item in b["field_locators"].items():
        locator(item, "field_locators." + key)
    _tagged(b["derivation"], "derivation", _derivation)
    derivation = known_value(b["derivation"])
    if derivation is not None:
        if derivation["output"] != b["value"]:
            fail("DERIVATION", "Derived output must equal the recorded estimate")
        if revision["factual_status"] not in {"derived", "synthetic"}:
            fail("FACTUAL_STATUS", "Computed extraction needs derived factual status")


def _appraisal(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"target_ref", "domain", "judgment", "rationale", "status", "criterion", "tool_version", "evidence", "uncertainty"}, field="appraisal")
    pin(b["target_ref"])
    for key in ("domain", "judgment", "rationale", "criterion", "uncertainty"):
        nonblank(b[key], key)
    _enum(b["status"], {"proposed", "checked", "disputed", "revised", "withdrawn", "superseded"}, "appraisal.status")
    _tagged(b["tool_version"], "tool_version", nonblank)
    _located_sources(b["evidence"], "evidence")


def _claim(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"class", "lifecycle", "statement", "boundaries", "counterarguments", "uncertainty", "evidence_refs", "appraisal_refs", "review_refs", "argument"}, {"decision_artifact", "mechanism", "variables", "test_plan", "test_refs", "convention_reason"}, field="claim")
    _enum(b["class"], CLASSES, "claim.class")
    _enum(b["lifecycle"], LIFECYCLE, "claim.lifecycle")
    for key in ("statement", "boundaries", "counterarguments", "uncertainty"):
        nonblank(b[key], key)
    for key in ("evidence_refs", "appraisal_refs", "review_refs"):
        _pins(b[key], key)
    _object(b["argument"], {"premises", "inference_steps", "revision_criterion"}, field="argument")
    _texts(b["argument"]["premises"], "argument.premises")
    _texts(b["argument"]["inference_steps"], "argument.inference_steps")
    nonblank(b["argument"]["revision_criterion"], "argument.revision_criterion")
    variants = {
        "project_constraint": {"decision_artifact"},
        "design_hypothesis": {"mechanism", "variables", "test_plan"},
        "unvalidated_convention": {"convention_reason"},
    }
    required = variants.get(b["class"], set())
    optional = {"test_refs"} if b["class"] == "design_hypothesis" else set()
    special = {"decision_artifact", "mechanism", "variables", "test_plan", "test_refs", "convention_reason"}
    if not required <= set(b) or (set(b) & special) - required - optional:
        fail("CLAIM_VARIANT", f"Wrong class-specific fields for {b['class']}")
    for key in required - {"variables"}:
        nonblank(b[key], key)
    if "variables" in b:
        _texts(b["variables"], "variables", 1)
    if "test_refs" in b:
        _pins(b["test_refs"], "test_refs")


def _requirement(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"claim_refs", "status", "statement", "revision_criterion", "class", "scope", "mechanism", "conditions", "risks", "test_refs", "variables", "result_refs"}, field="requirement")
    _pins(b["claim_refs"], "claim_refs", 1)
    _enum(b["status"], {"proposed", "specified", "internally_checked", "evidence_supported", "superseded", "rejected"}, "requirement.status")
    _enum(b["class"], {"project_constraint", "design_hypothesis", "unvalidated_convention", "evidence_informed"}, "requirement.class")
    for key in ("statement", "revision_criterion", "scope", "mechanism"):
        nonblank(b[key], key)
    for key in ("conditions", "risks", "variables"):
        _texts(b[key], key)
    for key in ("test_refs", "result_refs"):
        _pins(b[key], key)
    if b["status"] == "evidence_supported" and not b["result_refs"]:
        fail("UNSUPPORTED_REQUIREMENT", "Evidence-supported requirement requires actual result references")


def _protocol(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"hypothesis_refs", "status", "hypotheses", "estimands", "outcomes", "manipulations", "checks", "sampling", "randomization", "analysis", "exclusions", "ethics", "privacy", "gate_refs", "exposure", "limitations"}, field="experiment_protocol")
    for key in ("hypothesis_refs", "gate_refs"):
        _pins(b[key], key)
    _enum(b["status"], {"draft", "internally_checked", "readiness_blocked", "ready_for_authorized_execution", "superseded", "withdrawn"}, "protocol.status")
    for key in ("hypotheses", "estimands", "outcomes"):
        _texts(b[key], key, 1)
    for key in ("manipulations", "checks"):
        _texts(b[key], key)
    for key in ("sampling", "randomization", "analysis", "exclusions", "ethics", "privacy", "limitations"):
        nonblank(b[key], key)
    _enum(b["exposure"], {"prospective", "retrospective", "synthetic"}, "exposure")
    if synthetic != (b["exposure"] == "synthetic"):
        fail("CONTAMINATION", "Protocol exposure must match its live/fixture context")
    if b["status"] == "ready_for_authorized_execution" and not b["gate_refs"]:
        fail("READINESS", "Execution readiness requires actual authorization gates")


def _amendment(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"kind", "target_refs", "replacement_refs", "reason", "prior_exposure", "required_rework", "verification", "materiality", "status"}, {"rule_change"}, field="amendment")
    _enum(b["kind"], {"extraction_correction", "record_correction", "source_invalidation", "source_correction", "protocol_change", "identity_merge", "identity_split", "nonmaterial"}, "amendment.kind")
    for key in ("target_refs", "replacement_refs"):
        _pins(b[key], key)
    for key in ("reason", "prior_exposure", "required_rework", "verification"):
        nonblank(b[key], key)
    _enum(b["materiality"], {"material", "nonmaterial"}, "materiality")
    _enum(b["status"], {"proposed", "applied", "verified", "rescinded"}, "amendment.status")
    if b["kind"] == "protocol_change":
        if "rule_change" not in b:
            fail("AMENDMENT", "Protocol amendment requires exact previous/replacement rule artifacts")
        change = b["rule_change"]
        _object(change, {"previous", "replacement"}, field="rule_change")
        for key in ("previous", "replacement"):
            _object(change[key], {"version", "artifact"}, field="rule_change." + key)
            nonblank(change[key]["version"], "rule_change." + key + ".version")
            _artifact(change[key]["artifact"], "rule_change." + key + ".artifact")
        if (change["previous"]["version"] == change["replacement"]["version"]
                or change["previous"]["artifact"]["sha256"] == change["replacement"]["artifact"]["sha256"]):
            fail("AMENDMENT", "Protocol change requires different version labels and changed artifact bytes")
    elif "rule_change" in b:
        fail("AMENDMENT", "rule_change is specific to protocol_change amendments")
    if (b["kind"] == "nonmaterial") != (b["materiality"] == "nonmaterial"):
        fail("AMENDMENT", "Amendment kind and materiality disagree")
    if b["status"] in {"applied", "verified"} and not b["target_refs"] and b["kind"] != "protocol_change":
        fail("AMENDMENT", "Applied amendment must identify its exact targets")
    if b["kind"] in {"extraction_correction", "record_correction", "source_correction", "identity_merge", "identity_split"} and b["status"] in {"applied", "verified"} and not b["replacement_refs"]:
        fail("AMENDMENT", "Applied correction or identity change requires replacement references")
    if b["kind"] == "source_invalidation" and b["replacement_refs"]:
        fail("AMENDMENT", "Source invalidation does not silently supply a replacement source")


def _assistance(b: dict, revision: dict, synthetic: bool) -> None:
    if not isinstance(b, dict) or not isinstance(b.get("subtype"), str):
        fail("SHAPE", "Assistance needs a subtype")
    common = {"subtype", "status", "performed_at", "independence"}
    _enum(b["subtype"], {"reading", "review", "assistance"}, "assistance.subtype")
    variants = {
        "reading": {"source_ref", "manifestation_id", "access_at_read", "reading_status", "ranges", "method"},
        "review": {"scope", "outcome", "verification", "target_refs", "artifact"},
        "assistance": {"task", "input_refs", "output_refs", "artifacts", "verification_steps", "limitations"},
    }
    optional = {"gate_ref", "input_refs"} if b["subtype"] == "review" else set()
    _object(b, common | variants[b["subtype"]], optional, field="assistance")
    _enum(b["status"], {"planned", "performed", "failed"}, "assistance.status")
    _tagged(b["performed_at"], "performed_at", stamp)
    when = known_value(b["performed_at"])
    if b["status"] in {"performed", "failed"}:
        if when is None or stamp(when) > stamp(revision["at"]):
            fail("TIME", "Performed/failed activity requires an actual date no later than its record")
    elif when is not None:
        fail("STATUS", "Planned activity cannot claim a performed date")
    nonblank(b["independence"], "independence")
    if b["subtype"] == "reading":
        pin(b["source_ref"])
        for key in ("manifestation_id", "method"):
            nonblank(b[key], key)
        _enum(b["access_at_read"], ACCESS, "access_at_read")
        _enum(b["reading_status"], READING, "reading_status")
        _list(b["ranges"], "ranges")
        for interval in b["ranges"]:
            if not isinstance(interval, list) or len(interval) != 2:
                fail("READ_RANGE", "Reading range must be [start,end]")
            _integer(interval[0], "reading range start")
            _integer(interval[1], "reading range end")
            if interval[1] < interval[0]:
                fail("READ_RANGE", "Reading range is reversed")
        if b["reading_status"] == "not_read" and b["ranges"]:
            fail("FALSE_FULL_READING", "not_read cannot claim read ranges")
        if b["reading_status"] != "not_read" and (not b["ranges"] or b["status"] != "performed"):
            fail("FALSE_FULL_READING", "Reading assertion requires a performed event and ranges")
    elif b["subtype"] == "review":
        _enum(b["scope"], {"source_fidelity", "internal_audit", "external_feedback"}, "review.scope")
        _enum(b["outcome"], {"pass", "fail", "inconclusive"}, "review.outcome")
        _enum(b["verification"], {"not_checked", "agent_checked", "human_checked", "independent_human_checked"}, "review.verification")
        _pins(b["target_refs"], "target_refs", 1)
        nonblank(b["artifact"], "artifact")
        if "input_refs" in b:
            _pins(b["input_refs"], "input_refs")
        if b["status"] != "performed" and (b["outcome"] != "inconclusive" or b["verification"] != "not_checked"):
            fail("FALSE_REVIEW", "Unperformed review cannot assert an outcome or verification")
        if b["verification"] == "not_checked" and b["outcome"] != "inconclusive":
            fail("FALSE_REVIEW", "Unchecked review cannot assert a pass or fail result")
        if b["verification"] in {"human_checked", "independent_human_checked"} and revision["actor"]["kind"] != "human":
            fail("FALSE_HUMAN_REVIEW", "Agent activity cannot become human review")
        if b["verification"] == "agent_checked" and revision["actor"]["kind"] != "agent":
            fail("ACTOR", "Agent check must identify the actual agent actor")
        if b["scope"] == "external_feedback":
            if "gate_ref" not in b:
                fail("EXTERNAL_FEEDBACK", "External feedback requires an actual human gate")
            pin(b["gate_ref"])
            if b["status"] == "performed" and (revision["actor"]["kind"] != "human" or b["verification"] not in {"human_checked", "independent_human_checked"}):
                fail("FALSE_HUMAN_REVIEW", "Performed external feedback must identify actual human verification")
        elif "gate_ref" in b:
            fail("SHAPE", "gate_ref is specific to external_feedback reviews")
    else:
        for key in ("task", "limitations"):
            nonblank(b[key], key)
        for key in ("input_refs", "output_refs"):
            _pins(b[key], key)
        for key in ("artifacts", "verification_steps"):
            _texts(b[key], key)
        if b["status"] == "planned" and (b["output_refs"] or b["artifacts"] or b["verification_steps"]):
            fail("STATUS", "Planned assistance cannot claim completed outputs or checks")


def _human_gate(b: dict, revision: dict, synthetic: bool) -> None:
    _object(b, {"need", "reason", "attempted_remedies", "owner_action", "evidence", "completion_signal", "stop_condition", "status", "gate_class", "authorized_actor"}, {"reopen_reason"}, field="human_gate")
    for key in ("need", "reason", "owner_action", "completion_signal", "stop_condition"):
        nonblank(b[key], key)
    _texts(b["attempted_remedies"], "attempted_remedies")
    _tagged(b["evidence"], "evidence", nonblank)
    _tagged(b["authorized_actor"], "authorized_actor", _actor)
    _enum(b["status"], {"proposed", "waiting", "satisfied", "declined", "blocked"}, "human_gate.status")
    _enum(b["gate_class"], {"source_access", "repository_approval", "authorship_license", "external_review", "participants", "other"}, "gate_class")
    actor = known_value(b["authorized_actor"])
    if actor is not None and actor["kind"] != "human":
        fail("FALSE_HUMAN_GATE", "A human gate's authorized actor must be human")
    if b["status"] == "satisfied":
        if revision["actor"]["kind"] != "human" or actor is None or known_value(b["evidence"]) is None:
            fail("FALSE_HUMAN_GATE", "Gate satisfaction needs a human actor, authorization identity and actual evidence")
    if "reopen_reason" in b:
        nonblank(b["reopen_reason"], "reopen_reason")


_VALIDATORS = {
    "source": _source, "search_run": _search_run, "search_hit": _search_hit,
    "screening": _screening, "study": _study, "sample": _sample,
    "experiment": _experiment, "theoretical_extraction": _theoretical,
    "extraction": _extraction, "appraisal": _appraisal, "claim": _claim,
    "requirement": _requirement, "experiment_protocol": _protocol,
    "amendment": _amendment, "assistance": _assistance, "human_gate": _human_gate,
}


def _transition(kind: str, old: dict, new: dict) -> None:
    """Record-local transitions; amendment authorization is cross-record work."""
    status_field = {"source": "validity", "study": "identity_status", "screening": "decision", "claim": "lifecycle"}.get(kind, "status")
    old_status, new_status = old[status_field], new[status_field]
    if kind == "claim":
        if old["class"] != new["class"]:
            fail("CLASS_PROMOTION", "A new claim class requires a new logical ID")
        allowed = TRANSITIONS[old_status]
    elif kind == "source":
        allowed = {"active": {"active", "corrected", "retracted", "withdrawn", "superseded"}, "corrected": {"corrected", "retracted", "withdrawn", "superseded"}}.get(old_status, {old_status})
        if "alias_of" in old and old.get("alias_of") != new.get("alias_of"):
            fail("ALIAS", "An identity alias cannot silently retarget")
    elif kind == "search_run":
        allowed = {"planned": {"planned", "running", "failed"}, "running": {"running", "completed", "partial", "failed"}}.get(old_status, {old_status})
        immutable = {"lane", "protocol_version", "mode", "platform", "interface", "query", "filters", "coverage"}
        if old_status in {"completed", "partial", "failed"}:
            immutable |= set(old)
        if any(old[field] != new[field] for field in immutable):
            fail("HISTORY", "Search identity and finished run results are immutable; record a new run or explicit corrected record")
    elif kind == "search_hit":
        allowed = {"unresolved", "resolved", "duplicate", "unresolvable"}
        if any(old[field] != new[field] for field in ("search_ref", "ordinal", "raw_metadata", "returned_identifiers")):
            fail("HISTORY", "A search occurrence's raw identity is immutable")
    elif kind == "screening":
        allowed = {"pending", "include", "exclude", "awaiting_text", "uncertain"}
        if any(old[field] != new[field] for field in ("source_ref", "stage", "protocol_version", "rule")):
            fail("HISTORY", "Changed screening scope requires a successor screening record")
    elif kind == "study":
        allowed = {old_status} if old_status == "alias" else {"unresolved", "provisional", "resolved", "fixture_asserted_same", "alias"}
        if old_status == "alias" and old["alias_of"] != new["alias_of"]:
            fail("ALIAS", "An identity alias cannot silently retarget")
    elif kind == "sample":
        allowed = {"provisional", "checked", "withdrawn", "superseded"} if old_status not in {"withdrawn", "superseded"} else {old_status}
    elif kind in {"extraction", "theoretical_extraction"}:
        allowed = {
            "draft": {"draft", "extracted", "withdrawn", "superseded"},
            "extracted": {"draft", "extracted", "source_checked", "disputed", "withdrawn", "superseded"},
            "source_checked": {"draft", "extracted", "source_checked", "disputed", "withdrawn", "superseded"},
            "disputed": {"draft", "extracted", "disputed", "withdrawn", "superseded"},
        }.get(old_status, {old_status})
    elif kind == "experiment":
        allowed = {"provisional": {"provisional", "extracted", "withdrawn", "superseded"}, "extracted": {"provisional", "extracted", "checked", "withdrawn", "superseded"}, "checked": {"provisional", "extracted", "checked", "withdrawn", "superseded"}}.get(old_status, {old_status})
    elif kind == "appraisal":
        allowed = {"proposed", "checked", "disputed", "revised", "withdrawn", "superseded"} if old_status not in {"withdrawn", "superseded"} else {old_status}
    elif kind == "requirement":
        allowed = {
            "proposed": {"proposed", "specified", "superseded", "rejected"},
            "specified": {"proposed", "specified", "internally_checked", "superseded", "rejected"},
            "internally_checked": {"proposed", "specified", "internally_checked", "evidence_supported", "superseded", "rejected"},
            "evidence_supported": {"proposed", "specified", "evidence_supported", "superseded", "rejected"},
        }.get(old_status, {old_status})
    elif kind == "experiment_protocol":
        allowed = {
            "draft": {"draft", "internally_checked", "readiness_blocked", "withdrawn", "superseded"},
            "internally_checked": {"draft", "internally_checked", "readiness_blocked", "ready_for_authorized_execution", "withdrawn", "superseded"},
            "readiness_blocked": {"draft", "internally_checked", "readiness_blocked", "ready_for_authorized_execution", "withdrawn", "superseded"},
            "ready_for_authorized_execution": {"draft", "internally_checked", "readiness_blocked", "ready_for_authorized_execution", "withdrawn", "superseded"},
        }.get(old_status, {old_status})
    elif kind == "amendment":
        allowed = {"proposed": {"proposed", "applied", "rescinded"}, "applied": {"applied", "verified", "rescinded"}, "verified": {"verified", "rescinded"}}.get(old_status, {old_status})
    elif kind == "assistance":
        if old["subtype"] != new["subtype"]:
            fail("TRANSITION", "An assistance ID cannot change activity subtype")
        allowed = {"planned", "performed", "failed"} if old_status == "planned" else {old_status}
    elif kind == "human_gate":
        allowed = {"proposed", "waiting", "satisfied", "declined", "blocked"}
        if old_status in {"satisfied", "declined", "blocked"} and new_status != old_status and "reopen_reason" not in new:
            fail("TRANSITION", "Reopening a gate requires a recorded reason")
        if old["gate_class"] != new["gate_class"]:
            fail("TRANSITION", "A human gate cannot change its class")
    else:  # Every family must explicitly define its state semantics.
        fail("UNSUPPORTED_KIND", kind)
    if new_status not in allowed:
        fail("TRANSITION", f"{kind}: {old_status} -> {new_status}")


def validate_record(record: Any, *, expected_kind: str) -> None:
    """Validate one record in caller-selected live or synthetic-fixture context."""
    _enum(expected_kind, {"live", "fixture"}, "caller context", "CONTAMINATION")
    _object(record, {"schema_version", "id", "kind", "synthetic", "issue", "revisions"}, field="record")
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        fail("SCHEMA_VERSION", "Only schema_version integer 1 is supported")
    _enum(record["kind"], KINDS, "kind", "UNSUPPORTED_KIND")
    kind = record["kind"]
    rid = record["id"]
    if not isinstance(rid, str) or _ID.fullmatch(rid) is None or not rid.startswith(PREFIXES[kind] + "-"):
        fail("ID", f"{kind} requires a stable {PREFIXES[kind]}-prefixed ID")
    if type(record["synthetic"]) is not bool or record["synthetic"] != (expected_kind == "fixture"):
        fail("CONTAMINATION", "Record synthetic flag disagrees with caller-selected context")
    _integer(record["issue"], "issue", 1)
    _list(record["revisions"], "revisions", 1)
    last = None
    for number, revision in enumerate(record["revisions"], 1):
        _object(revision, {"rev", "at", "actor", "basis", "data", "factual_status"}, field="revision")
        if type(revision["rev"]) is not int or revision["rev"] != number:
            fail("REVISION", f"{rid} revisions must be contiguous from 1")
        when = stamp(revision["at"])
        if last is not None and when < stamp(last["at"]):
            fail("TIME", f"{rid} revision timestamp moves backward")
        _actor(revision["actor"])
        _pins(revision["basis"], "basis")
        _enum(revision["factual_status"], FACTUAL_STATUSES, "factual_status", "FACTUAL_STATUS")
        if record["synthetic"] != (revision["factual_status"] == "synthetic"):
            fail("CONTAMINATION", "Factual status disagrees with synthetic/live context")
        _VALIDATORS[kind](revision["data"], revision, record["synthetic"])
        if kind == "claim" and number == 1 and revision["data"]["lifecycle"] != "proposed":
            fail("TRANSITION", "First claim revision must be proposed")
        if last is not None:
            _transition(kind, last["data"], revision["data"])
        last = revision
