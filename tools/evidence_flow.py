"""Deterministic report/study/sample bookkeeping; never an independence estimate."""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import io
from typing import Any

from tools.record_io import dumps, fail
from tools.screening import DECISIONS, STAGES, TRACKS, effective_screening, screening_coverage


def evidence_flow(graph: Any) -> dict:
    latest = {rid: revision["data"] for rid, revision in graph.latest.items()}
    kinds: dict[str, dict[str, dict]] = defaultdict(dict)
    for rid, row in graph.records.items():
        kinds[row["kind"]][rid] = latest[rid]

    def canonical(rid: str, expected_kind: str) -> str:
        seen = set()
        while rid in kinds[expected_kind] and kinds[expected_kind][rid].get("alias_of"):
            if rid in seen:
                fail("ALIAS_CYCLE", rid)
            seen.add(rid)
            rid = kinds[expected_kind][rid]["alias_of"]["id"]
        return rid

    warnings: list[str] = []
    runs = kinds["search_run"]
    hits = kinds["search_hit"]
    hits_by_run: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for rid, hit in sorted(hits.items()):
        hits_by_run[hit["search_ref"]["id"]].append((rid, hit))
    run_rows = []
    for rid, run in sorted(runs.items()):
        occurrences = hits_by_run[rid]
        ordinals = [hit["ordinal"] for _, hit in occurrences]
        if len(ordinals) != len(set(ordinals)):
            fail("SEARCH_ORDINAL", rid)
        if run["retrieved_count"] != len(occurrences):
            fail("SEARCH_COUNT", f"{rid}: retrieved_count != stored hit occurrences")
        reported = run["reported_count"]
        if isinstance(reported, int) and reported < len(occurrences):
            fail("SEARCH_COUNT", f"{rid}: retrieved more than the recorded reported count")
        if run["status"] == "completed":
            if not run["pagination"]["complete"] or run["failures"]:
                fail("SEARCH_COMPLETION", f"{rid}: incomplete pagination or failures")
            if isinstance(reported, int) and reported != len(occurrences):
                fail("SEARCH_COMPLETION", f"{rid}: reported/retrieved counts differ")
        if run["status"] == "planned" and occurrences:
            fail("SEARCH_COMPLETION", f"{rid}: planned run already has hits")
        resolved = [hit for _, hit in occurrences if "source_ref" in hit]
        run_rows.append({
            "id": rid, "mode": run["mode"], "status": run["status"],
            "reported_count": reported, "stored_hits": len(occurrences),
            "resolved_hits": len(resolved),
            "duplicate_hits": sum(hit["status"] == "duplicate" for _, hit in occurrences),
            "unresolved_hits": sum(hit["status"] in {"unresolved", "unresolvable"}
                                   for _, hit in occurrences),
            "unique_publications": len({canonical(hit["source_ref"]["id"], "source")
                                        for hit in resolved}),
        })
    if any(row["unresolved_hits"] for row in run_rows):
        warnings.append("Unresolved search-hit identities remain; publication coverage is incomplete.")

    decisions = effective_screening(graph)

    def stage_counts(track=None):
        result = {}
        for stage in STAGES:
            counter = Counter(decision["decision"] for key, (_, decision) in decisions.items()
                              if key[2] == stage and (track is None or key[1] == track))
            result[stage] = {status: counter[status] for status in DECISIONS}
        return result

    # Preserve the all-track aggregate used by corpus-completion gates. A
    # theoretical unresolved decision must not disappear from those checks.
    stages = stage_counts()
    by_track = {track: stage_counts(track) for track in TRACKS}
    included_publications = {
        key[0] for key, (_, d) in decisions.items()
        if key[1] == "empirical" and key[2] == "full_text" and d["decision"] == "include"
    }
    selected_theoretical_publications = {
        key[0] for key, (_, d) in decisions.items()
        if key[1] == "theoretical" and key[2] == "full_text" and d["decision"] == "include"
    }
    protocols = sorted({key[3] for key in decisions})
    if len(protocols) > 1:
        warnings.append("Screening includes multiple protocol versions; aggregate inclusion is a union, not a final review flow.")

    publications = {canonical(rid, "source") for rid in kinds["source"]}
    screened_sources = {key[0] for key in decisions}
    resolved_search_sources = {canonical(hit["source_ref"]["id"], "source")
                               for hit in hits.values() if "source_ref" in hit}
    scopes: dict[tuple[str, str], set[str]] = defaultdict(set)
    for source, track, _, protocol in decisions:
        scopes[(track, protocol)].add(source)
    coverage = {
        "scope": "Registered canonical sources and recorded decision scopes; not an empirical eligibility denominator or a completion assertion.",
        "registered_publications_without_screening": sorted(publications - screened_sources),
        "resolved_search_publications_without_screening": sorted(resolved_search_sources - screened_sources),
        "decision_scopes": [screening_coverage(graph, source_ids=sorted(ids), protocol_version=protocol, track=track)
                            for (track, protocol), ids in sorted(scopes.items())],
    }
    if coverage["resolved_search_publications_without_screening"]:
        warnings.append("Resolved search publications without recorded screening remain; source discovery is not corpus selection.")
    studies = {canonical(rid, "study") for rid in kinds["study"]}
    included_studies = {
        canonical(rid, "study") for rid, study in kinds["study"].items()
        if any(canonical(ref["id"], "source") in included_publications
               for ref in study["publications"])
    }
    extractions = kinds["extraction"]

    def outcome_id(value: dict) -> tuple[str, ...]:
        return (value["experiment_ref"]["id"], value["outcome"], value["contrast"],
                value["timepoint"], value["sample_ref"]["id"])

    outcomes = {outcome_id(value) for value in extractions.values()}
    current_outcomes = {outcome_id(value) for rid, value in extractions.items()
                        if (rid, len(graph.records[rid]["revisions"])) not in graph.stale
                        and value["status"] not in {"withdrawn", "superseded", "draft", "disputed"}}
    included_outcomes = {
        outcome_id(value) for value in extractions.values()
        if canonical(value["source_ref"]["id"], "source") in included_publications
    }

    samples = kinds["sample"]
    parent = {rid: rid for rid in samples}

    def find(rid: str) -> str:
        while parent[rid] != rid:
            parent[rid] = parent[parent[rid]]
            rid = parent[rid]
        return rid

    def union(a: str, b: str) -> None:
        first, second = sorted((find(a), find(b)))
        parent[second] = first

    unknown_pairs = set()
    for rid, sample in sorted(samples.items()):
        for relation in sample["overlap"]:
            target = relation["sample_ref"]["id"]
            if relation["relation"] in {"known_shared", "partial_overlap", "shared_control"}:
                union(rid, target)
            elif relation["relation"] == "unknown":
                unknown_pairs.add(tuple(sorted((rid, target))))
    groups: dict[str, list[str]] = defaultdict(list)
    for rid in sorted(samples):
        groups[find(rid)].append(rid)
    outcome_groups: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for value in extractions.values():
        outcome_groups[find(value["sample_ref"]["id"])].add(outcome_id(value))
    if unknown_pairs:
        warnings.append("Recorded unknown sample overlap prevents an independence claim.")
    if len(samples) > 1:
        warnings.append("Absence of an overlap edge does not establish sample independence.")
    if any(exp["dependence"]["correlation"].get("state") != "known"
           for exp in kinds["experiment"].values()):
        warnings.append("Outcome covariance is missing for at least one experiment; no pooling precision is inferred.")

    current_sources = sum(
        (rid, len(graph.records[rid]["revisions"])) not in graph.stale
        and source["validity"] == "active" and not source.get("alias_of")
        for rid, source in kinds["source"].items())
    return {
        "publications": len(publications), "source_record_ids": len(kinds["source"]),
        "studies": len(studies), "experiments": len(kinds["experiment"]),
        "samples": len(samples), "outcomes": len(outcomes),
        "extraction_records": len(extractions),
        "theoretical_extractions": len(kinds["theoretical_extraction"]),
        "current_usable_sources": current_sources,
        "current_extracted_outcomes": len(current_outcomes),
        "shared_sample_groups": sum(len(values) > 1 for values in outcome_groups.values()),
        "known_dependence_groups": [groups[key] for key in sorted(groups)],
        "unknown_overlap_pairs": [list(pair) for pair in sorted(unknown_pairs)],
        "search_runs": len(runs), "search_hits": len(hits),
        "search_details": run_rows, "screening": stages,
        "screening_by_track": by_track,
        "screening_coverage": coverage,
        "screening_scope": "screening aggregates all tracks for unresolved-stage gates; included_* counts use empirical full-text decisions only.",
        "screening_protocols": protocols,
        "included_publications": len(included_publications),
        "selected_theoretical_publications": len(selected_theoretical_publications),
        "included_studies": len(included_studies), "included_outcomes": len(included_outcomes),
        "unavailable_publications": sum(source["access_status"] == "unavailable"
                                         for source in kinds["source"].values()),
        "warnings": sorted(set(warnings)),
        "count_scope": "Logical identities and declared report decisions; no independent-study count or PRISMA completeness claim.",
    }


def render_exports(data: dict, report: dict) -> dict[str, str]:
    counts = report["counts"]
    scalar_counts = {key: value for key, value in counts.items() if type(value) is int}
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["measure", "count"])
    writer.writerows(sorted(scalar_counts.items()))
    lines = ["# Evidence flow", "",
             f"Research state: {data['research_state']}. Context: {data['dataset_kind']}.",
             "", "These are record counts. They do not establish source fidelity,",
             "review completeness, sample independence or scientific validity.", "",
             "| Measure | Count |", "|---|---:|"]
    lines.extend(f"| {key.replace('_', ' ')} | {value} |"
                 for key, value in sorted(scalar_counts.items()))
    lines += ["", "## Coverage and dependence", "",
              counts["count_scope"], ""]
    lines.extend("- " + warning for warning in counts["warnings"])
    if not counts["warnings"]:
        lines.append("No data-dependent warning was generated; scientific checks remain unevaluated.")
    index = [{
        "id": row["id"], "kind": row["kind"], "synthetic": row["synthetic"],
        "created_at": row["revisions"][0]["at"], "updated_at": row["revisions"][-1]["at"],
        "latest_revision": len(row["revisions"]),
        "currency": "stale" if row["id"] in report["currency"]["latest_stale_ids"] else "current",
    } for row in sorted(data["records"], key=lambda value: value["id"])]
    return {
        "evidence-flow.json": dumps(counts), "evidence-flow.csv": buffer.getvalue(),
        "evidence-flow.md": "\n".join(lines).rstrip() + "\n",
        "records-index.json": dumps({"contract": data["contract"], "records": index}),
    }
