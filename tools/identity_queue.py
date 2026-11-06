"""Print a read-only R006 candidate queue from the live registry.

Run ``python -m tools.identity_queue > build/identity-queue.json`` after creating
build/. Identifier equality proposes review work; it never resolves a hit,
screens a source or establishes publication/study/sample identity.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
from pathlib import Path

from tools.record_io import dumps
from tools.records import load_registry, validate_dataset
from tools.screening import normalize_doi, normalize_url, verified_dois


def identifier_key(item: dict) -> tuple[str, str] | None:
    scheme, value = item["scheme"], item["value"]
    # Resolver URLs are DOI assertions, but publisher URLs are only resources.
    doi = normalize_doi(value) if scheme in {"doi", "url"} else None
    if doi is not None:
        return "doi", doi
    if scheme == "url" and (url := normalize_url(value)) is not None:
        return "url", url
    return None


def build_queue(records: list[dict]) -> dict:
    """Consume already validated records; preserve exact latest revision pins."""
    sources = defaultdict(set)
    by_id = {row["id"]: row for row in records}
    for row in records:
        body = row["revisions"][-1]["data"]
        if row["kind"] != "source" or body.get("validity") != "active" or body.get("alias_of"):
            continue
        for item in body["identifiers"]:
            if item["status"] == "verified" and (key := identifier_key(item)) is not None:
                sources[key].add(row["id"])
    candidates = []
    unresolved = 0
    for row in sorted(records, key=lambda r: r["id"]):
        revision = row["revisions"][-1]
        body = revision["data"]
        if row["kind"] != "search_hit" or body["status"] != "unresolved":
            continue
        unresolved += 1
        matches = defaultdict(set)
        for item in body["returned_identifiers"]:
            key = identifier_key(item)
            for rid in sources.get(key, ()):
                matches[rid].add(key)
        if not matches:
            continue
        evidence = []
        for rid, keys in sorted(matches.items()):
            source_revision = by_id[rid]["revisions"][-1]
            source = source_revision["data"]
            conflict = source["metadata_status"] == "conflict" or len(verified_dois(source)) > 1 or any(
                item["status"] == "conflict" for item in source["identifiers"])
            evidence.append({"source_ref": {"id": rid, "rev": source_revision["rev"]},
                             "source_metadata_conflict": conflict,
                             "matches": [{"scheme": k, "value": v} for k, v in sorted(keys)]})
        candidates.append({"hit_ref": {"id": row["id"], "rev": revision["rev"]},
                           "search_ref": body["search_ref"], "ordinal": body["ordinal"],
                           "status": "conflict_review" if len(matches) > 1 or any(
                               e["source_metadata_conflict"] for e in evidence) else "candidate_review",
                           "source_candidates": evidence})
    # Hash the entire ordered input, including history, rather than claiming that
    # current pins alone establish the report's input provenance.
    digest = hashlib.sha256(dumps(sorted(records, key=lambda r: r["id"])).encode()).hexdigest()
    return {"artifact_kind": "unadjudicated_identity_work_queue", "issue": 6,
            "input_records_sha256": digest,
            "counts": {"unresolved_hits": unresolved, "candidate_hits": len(candidates),
                       "unmatched_hits": unresolved - len(candidates),
                       "conflict_review_hits": sum(c["status"] == "conflict_review" for c in candidates)},
            "candidates": candidates, "acceptance": "not_evaluated",
            "limitations": ["Returned identifiers are discovery assertions, not verified hit identity.",
                            "Exact resource equality can match a shared page rather than a publication.",
                            "Multiple candidate sources remain separate; no transitive or fuzzy merging.",
                            "No source retrieval, screening, corpus acceptance or study/sample inference."]}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data, _ = load_registry(root)
    validate_dataset(data, expected_kind="live", root=root)
    print(dumps(build_queue(data["records"])), end="")


if __name__ == "__main__":
    main()
