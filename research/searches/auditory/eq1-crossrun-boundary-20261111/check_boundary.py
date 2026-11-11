"""Recompute a bounded EQ1 cross-invocation overlap from accepted observations.

No network requests, source downloads, screening or registry mutation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PREVIOUS = ROOT / "research/searches/auditory/eq1-boundary-2026-11-10/OBSERVATIONS.json"
NEXT = ROOT / "research/searches/auditory/eq1-pages44-47-20261111/OBSERVATIONS.json"
CURRENT = HERE / "OBSERVATIONS.json"

EXPECTED_BLOBS = {
    "previous": "443d3702bda94cb4fcd0cbfeda8b92354ec8b381",
    "next": "b61a018a7ec8888811e918611e55ebd584bb8fdf",
}


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _query(url: str) -> dict[str, list[str]]:
    split = urlsplit(url)
    if split.scheme != "https" or split.netloc != "api.openalex.org" or split.path != "/works":
        raise ValueError("not the expected OpenAlex works endpoint")
    return parse_qs(split.query, keep_blank_values=True)


def reconcile(previous: dict, following: dict) -> dict:
    older = {p["page"]: p for p in previous["pages"]}
    newer = {p["page"]: p for p in following["pages"]}
    if 42 not in older or 43 not in older or 44 not in newer:
        raise ValueError("missing one of the pinned boundary pages")
    p42, p43, p44 = older[42], older[43], newer[44]

    queries = [_query(p42["request_url"]), _query(p43["request_url"]), _query(p44["url"])]
    for q, page in zip(queries, (42, 43, 44)):
        if q.get("page") != [str(page)]:
            raise ValueError("page/query mismatch")
        if q.get("per_page") != ["100"] or q.get("sort") != ["publication_date:asc,display_name:asc"]:
            raise ValueError("page size or order changed")
    # Select only reduces returned columns; it is not a query or eligibility change.
    for field in ("filter", "per_page", "sort"):
        if not (queries[0].get(field) == queries[1].get(field) == queries[2].get(field)):
            raise ValueError("frozen search semantics differ")
    if "to_publication_date:2026-10-04" not in queries[0]["filter"][0]:
        raise ValueError("missing frozen literature cutoff")
    if "title_and_abstract.search:" not in queries[0]["filter"][0]:
        raise ValueError("missing scoped EQ1 search")
    if previous["cutoff"] != following["cutoff"] or following["cutoff"] != "2026-10-04":
        raise ValueError("cutoff mismatch")
    if p44["raw_sha256"] != "24e4a8c62087b489ea9e038c8ca22cfa8d8b07ba93e0152c9d8ec19114d4103b":
        raise ValueError("original page44 response pin changed")
    if p44["http_status"] != 200 or following["failed_requests"][0]["page"] != 45 or following["failed_requests"][0]["http_status"] != 429:
        raise ValueError("observed HTTP boundary changed")
    if following["not_attempted_pages"] != [46, 47]:
        raise ValueError("attempt status changed")

    ids42 = [r["openalex_id"] for r in p42["records"]]
    ids43 = [r["openalex_id"] for r in p43["records"]]
    ids44 = p44["ordered_ids"]
    if any(len(ids) != 100 or len(set(ids)) != 100 for ids in (ids42, ids43, ids44)):
        raise ValueError("source pages are not 100 distinct identifiers apiece")
    if (p42["reported_total"], p43["reported_total"], p44["reported_total"]) != (9275, 9275, 9280):
        raise ValueError("observed provider counts changed")
    set42, set43 = set(ids42), set(ids43)
    intersect42 = [identifier for identifier in ids44 if identifier in set42]
    intersect43 = [identifier for identifier in ids44 if identifier in set43]
    return {
        "page42_source_count": p42["reported_total"],
        "page43_source_count": p43["reported_total"],
        "page44_source_count": p44["reported_total"],
        "page42_entries": len(ids42),
        "page43_entries": len(ids43),
        "page44_entries": len(ids44),
        "page42_vs_page44_shared_ids": intersect42,
        "page43_vs_page44_shared_ids": intersect43,
        "page43_suffix_equals_page44_prefix": ids43[-len(intersect43):] == ids44[:len(intersect43)] if intersect43 else False,
        "duplicated_boundary_entries": [
            {
                "openalex_id": identifier,
                "previous_page43_ordinal": ids43.index(identifier) + 1,
                "new_page44_ordinal": ids44.index(identifier) + 1,
                "previous_page43_publication_date": next(r["publication_date"] for r in p43["records"] if r["openalex_id"] == identifier),
            }
            for identifier in intersect43
        ],
        "page44_not_on_pages42_or43_count": len(set(ids44) - set42 - set43),
    }


def verify() -> dict:
    if git_blob_sha(PREVIOUS) != EXPECTED_BLOBS["previous"]:
        raise ValueError("source historical observation Git blob changed")
    if git_blob_sha(NEXT) != EXPECTED_BLOBS["next"]:
        raise ValueError("source page44 observation Git blob changed")
    old, new = json.loads(PREVIOUS.read_text(encoding="utf-8")), json.loads(NEXT.read_text(encoding="utf-8"))
    actual = reconcile(old, new)
    saved = json.loads(CURRENT.read_text(encoding="utf-8"))
    if saved["crossrun_observations"] != actual:
        raise ValueError("boundary observations do not reproduce")
    if len(actual["page43_vs_page44_shared_ids"]) != 8 or not actual["page43_suffix_equals_page44_prefix"]:
        raise ValueError("expected cross-invocation eight-ID overlap not reproduced")
    pins = saved["source_pins"]
    if [p["git_blob_sha1"] for p in pins] != [EXPECTED_BLOBS["previous"], EXPECTED_BLOBS["next"]]:
        raise ValueError("stored source pins diverged")
    if saved["claim_boundary_contiguous"] or saved["claim_completed_eq1"] or saved["claim_92_new_publications"]:
        raise ValueError("scientific/noncontiguous status was falsely promoted")
    return actual


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True, indent=2))
