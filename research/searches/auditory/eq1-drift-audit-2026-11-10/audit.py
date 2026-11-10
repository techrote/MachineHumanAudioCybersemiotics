"""Offline, fail-closed reconciliation of two *different* OpenAlex EQ1 observations.

No network requests, new canonical hits, abstracts, full-text readings or eligibility
decisions. The historical compressed derivatives are SHA-256 checked against the
original harvest manifest. The November 10 HTTP receipts have no retained raw body:
their claimed original-response digests are provenance, not reverified bytes.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[4]
HIST = ROOT / "research/searches/auditory/exports/openalex/20261103-database-load-recovery/MANIFEST.json"
OBS = ROOT / "research/searches/auditory/eq1-boundary-2026-11-10/OBSERVATIONS.json"
CUTOFF = "2026-10-04"
SORT = "publication_date:asc,display_name:asc"
HISTORICAL_RUN = "20261103-database-load-recovery"


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_historical_payload(blob: bytes, page: dict) -> dict:
    """Check the archived *derivative*, not the unavailable original HTTP bytes."""
    require(sha256(blob) == page["sha256"], "historical gzip digest mismatch")
    require(len(blob) == page["bytes"], "historical gzip byte count mismatch")
    raw = gzip.decompress(blob)
    require(sha256(raw) == page["payload_sha256"], "historical payload digest mismatch")
    require(len(raw) == page["payload_bytes"], "historical payload length mismatch")
    return json.loads(raw)


def load_historical(manifest: dict, root: Path = ROOT) -> tuple[list[str], dict]:
    require(manifest["run_id"] == HISTORICAL_RUN, "wrong historical invocation")
    require(manifest["sort"] == SORT, "historical sort changed")
    require(manifest["page_size"] == 200, "historical legacy pagination changed")
    eq1 = manifest["runs"]["EQ1"]
    require(eq1["status"] == "partial" and not eq1["complete"], "historical EQ1 status changed")
    require(eq1["reported_count"] == 9368, "historical reported count changed")
    ids = []
    successful_pages = []
    for p in eq1["pages"]:
        # The original 429 error responses remain in the manifest and derivative
        # archive; they are checked but never mistaken for pages of results.
        require(p.get("file"), "historical response file missing")
        file = root / p["file"]
        require(file.is_file(), "missing retained historical derivative: " + str(file))
        payload = verify_historical_payload(file.read_bytes(), p)
        if p["http_status"] != 200:
            require(p["http_status"] == 429 and not payload.get("results"),
                    "unexpected historical error response")
            continue
        rows = payload.get("results")
        require(isinstance(rows, list) and len(rows) == p["results"],
                "historical page result count mismatch")
        successful_pages.append(p["page"])
        ids.extend(item["id"] for item in rows)
    require(successful_pages == list(range(1, 22)), "historical page order or gap")
    require(len(ids) == eq1["retrieved"] == 4200, "historical retrieval count changed")
    require(len(set(ids)) == eq1["unique_retrieved"] == 4200,
            "duplicate historical work ID")
    return ids, eq1


def request_fields(page: dict) -> dict:
    u = urlsplit(page["request_url"])
    require(u.scheme == "https" and u.netloc == "api.openalex.org"
            and u.path == "/works", "not original OpenAlex works API")
    q = parse_qs(u.query, strict_parsing=True)
    require(all(len(v) == 1 for v in q.values()), "ambiguous request parameter")
    require(set(q) == {"filter", "per_page", "select", "page", "sort"},
            "unexpected or missing query parameters")
    require(q["page"] == [str(page["page"])], "request page inconsistent")
    require(q["per_page"] == ["100"], "current page size is not 100")
    require(q["sort"] == [SORT], "current sort changed")
    require("abstract_inverted_index" in q["select"][0].split(","),
            "requested field selection changed")
    return {k: v[0] for k, v in q.items()}


def load_current(obs: dict, eq1: dict) -> list[str]:
    require(obs["schema"] == "mhac-r005-eq1-boundary/1", "wrong observation schema")
    require(obs["cutoff"] == CUTOFF, "frozen publication cutoff changed")
    require(obs["historical_count"] == 4200, "historical boundary count changed")
    require(obs["claim_complete_eq1"] is False, "false EQ1 completion claim")
    require(obs["new_selected_studies_or_samples"] == 0
            and obs["human_screening_claimed"] is False
            and obs["source_full_text_reviewed"] is False, "forbidden admission/reading claim")
    provenance = obs["provenance"]
    require(provenance["historical_reported_total"] == eq1["reported_count"],
            "old reported total not pinned")
    require(provenance["new_search_occurrences_registered"] == 0
            and provenance["count_added_to_canonical_search_records"] == 0,
            "metadata improperly promoted to canonical search hits")
    pages = obs["pages"]
    require(len(pages) == 2 and [p["page"] for p in pages] == [42, 43],
            "not the two genuine boundary pages")
    ids = []
    dates = []
    for p in pages:
        q = request_fields(p)
        require(q["filter"] == eq1["filter"], "frozen Boolean/field search changed")
        require(q["filter"].endswith(",to_publication_date:" + CUTOFF),
                "cutoff absent from executed API request")
        require(p["interface"] == "OpenAlex works REST API"
                and p["source_class"] == "API discovery metadata, not primary full text",
                "source class inaccurate")
        require(p["http_status"] == 200 and p["results_returned"] == 100,
                "not a complete successful 100-row result page")
        require(p["reported_page"] == p["page"] and p["reported_page_size"] == 100,
                "provider page information inconsistent")
        require(len(p["records"]) == p["results_returned"],
                "metadata rows inconsistent with response receipt")
        require(p["reported_total"] == provenance["current_reported_total"],
                "provider total changed between observations")
        require(p["raw_bytes_read"] > 0 and len(p["raw_sha256"]) == 64
                and all(c in "0123456789abcdef" for c in p["raw_sha256"]),
                "missing/malformed original HTTP receipt hash")
        require(p["response_date"] and p["received_utc"] and p["completed_utc"],
                "missing HTTP date or acquisition boundary")
        for row in p["records"]:
            require(row["openalex_id"].startswith("https://openalex.org/W"),
                    "malformed OpenAlex work ID")
            require(row["publication_date"] <= CUTOFF,
                    "publication later than frozen search cutoff")
            ids.append(row["openalex_id"])
            dates.append(row["publication_date"])
    require(len(ids) == len(set(ids)) == 200, "duplicate current work ID")
    require(dates == sorted(dates), "current sort date monotonicity violated")
    return ids


def audit(manifest: dict, obs: dict, root: Path = ROOT) -> dict:
    old, eq1 = load_historical(manifest, root)
    current = load_current(obs, eq1)
    prior = set(old)
    overlap = [wid for wid in current if wid in prior]
    anchor = obs["historical_boundary_openalex_id"]
    require(old[-1] == anchor, "historical 4200th hit does not match observed anchor")
    index = current.index(anchor) if anchor in current else None
    new_rank = (41 * 100 + index + 1) if index is not None else None
    return {
        "historical_run": HISTORICAL_RUN,
        "historical_retrieved_occurrences": len(old),
        "historical_reported_total": eq1["reported_count"],
        "new_receipt_pages": [42, 43],
        "new_receipt_result_rows": len(current),
        "new_reported_total": obs["provenance"]["current_reported_total"],
        "provider_total_delta": obs["provenance"]["current_reported_total"] - eq1["reported_count"],
        "historical_4200th_work_id": anchor,
        "historical_anchor_current_rank_if_observed": new_rank,
        "anchor_rank_displacement_if_observed": new_rank - 4200 if new_rank else None,
        "current_200_already_in_historical_prefix": len(overlap),
        "current_200_not_in_historical_prefix": len(current) - len(overlap),
        "current_page43_already_in_historical_prefix":
            len([wid for wid in current[100:] if wid in prior]),
        "can_append_current_page43_as_historical_continuation": False,
        "new_canonical_hits_registered": 0,
        "new_primary_studies_experiments_samples": [0, 0, 0],
        "boundary": "Derived metadata checked against original preserved historical gzip bytes; "
                    "November 10 original HTTP response bodies not retained; "
                    "no new API retrieval, eligibility or human review was performed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-append-safe", action="store_true",
                        help="Explicitly fail rather than silently treating changed page 43 as continuation")
    args = parser.parse_args()
    result = audit(read_json(HIST), read_json(OBS))
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.require_append_safe and not result["can_append_current_page43_as_historical_continuation"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
