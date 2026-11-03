"""Derive the frozen A7 date window from retained OpenAlex occurrences, offline.

No search is executed, no duplicate occurrence is removed, and no eligibility
decision is made. Unknown or malformed metadata dates are retained separately.
"""
from __future__ import annotations

import argparse
from datetime import date
import gzip
import hashlib
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
EXPORTS = ROOT / "research/searches/auditory/exports/openalex"
START = date(2021, 4, 1)
END = date(2026, 10, 4)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def encode(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def compress(body):
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, filename="", mode="wb", mtime=0) as out:
        out.write(body)
    result = buffer.getvalue()
    if gzip.decompress(result) != body:
        raise ValueError("gzip roundtrip mismatch")
    return result


def classify(value):
    if not isinstance(value, str) or len(value) != 10:
        return "unknown"
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return "unknown"
    if START <= parsed <= END:
        return "within_window"
    return "before_window" if parsed < START else "after_window"


def build():
    selected, unknown = [], []
    manifests, family_counts, run_counts = [], {}, {}
    total = {key: 0 for key in ("within_window", "unknown", "before_window", "after_window")}
    all_ids, selected_ids, unknown_ids = set(), set(), set()
    complete_families = set()
    total_successful_pages, total_error_attempts = 0, 0
    for manifest_path in sorted(EXPORTS.glob("20261103-database*/MANIFEST.json")):
        manifest_body = manifest_path.read_bytes()
        manifest = json.loads(manifest_body)
        if not manifest.get("finished_at"):
            raise ValueError(f"Unfinished source invocation: {manifest_path.name}")
        manifests.append({"path": manifest_path.relative_to(ROOT).as_posix(),
                          "sha256": digest(manifest_body), "run_id": manifest["run_id"]})
        for family, run in manifest["runs"].items():
            if run["complete"]:
                complete_families.add(family)
            counts = {key: 0 for key in total}
            count = 0
            unique_ids = set()
            for page in run["pages"]:
                if not page.get("file"):
                    continue
                path = ROOT / page["file"]
                body = path.read_bytes()
                if digest(body) != page["sha256"]:
                    raise ValueError(f"Retained response digest mismatch: {page['file']}")
                payload = gzip.decompress(body) if path.suffix == ".gz" else body
                if page.get("payload_sha256") and digest(payload) != page["payload_sha256"]:
                    raise ValueError(f"Payload digest mismatch: {page['file']}")
                data = json.loads(payload)
                rows = data.get("results", [])
                if page.get("http_status") != 200:
                    total_error_attempts += 1
                    if rows:
                        raise ValueError("Failed response unexpectedly contains results")
                    continue
                total_successful_pages += 1
                if len(rows) != page.get("results"):
                    raise ValueError(f"Page cardinality mismatch: {page['file']}")
                for position, work in enumerate(rows):
                    if not isinstance(work.get("id"), str):
                        raise ValueError("Missing work ID in retained successful page")
                    count += 1
                    unique_ids.add(work["id"])
                    all_ids.add(work["id"])
                    status = classify(work.get("publication_date"))
                    counts[status] += 1
                    total[status] += 1
                    if status not in {"within_window", "unknown"}:
                        continue
                    occurrence = {
                        "occurrence_id": f"{manifest['run_id']}:{family}:p{page['page']:04d}:a{page.get('attempt', 1)}:r{position + 1:03d}",
                        "run_id": manifest["run_id"], "family": family,
                        "source_page": page["file"], "source_page_sha256": page["sha256"],
                        "json_pointer": f"/results/{position}",
                        "openalex_id": work["id"], "doi": work.get("doi"),
                        "title": work.get("display_name"), "publication_date_as_supplied": work.get("publication_date"),
                        "date_classification": status,
                    }
                    if status == "within_window":
                        selected.append(occurrence)
                        selected_ids.add(work["id"])
                    else:
                        unknown.append(occurrence)
                        unknown_ids.add(work["id"])
            if count != run["retrieved"] or len(unique_ids) != run["unique_retrieved"]:
                raise ValueError(f"Run cardinality mismatch: {manifest['run_id']} {family}")
            run_counts[f"{manifest['run_id']}:{family}"] = counts
            family_counts.setdefault(family, {key: 0 for key in total})
            for key in total:
                family_counts[family][key] += counts[key]
    occurrence_body = encode({"schema": "mhac-r005-a7-occurrences/1", "scope": "Retained C1 metadata occurrences in the inclusive A7 date window; no deduplication or screening", "occurrences": selected})
    unknown_body = encode({"schema": "mhac-r005-a7-unknown-dates/1", "scope": "Retained C1 occurrences with missing, partial or malformed publication_date metadata; not excluded", "occurrences": unknown})
    artifacts = {"A7-OCCURRENCES.json.gz": compress(occurrence_body),
                 "A7-UNKNOWN-DATES.json.gz": compress(unknown_body)}
    inventory = {
        "schema": "mhac-r005-a7-derived-inventory/1", "derived_on": "2026-11-03",
        "actor": "ChatGPT GPT-6 Astra Pro database-channel subagent",
        "method": "Offline inclusive date selection over every retained successful C1 response; original query terms unchanged; no new requests",
        "date_field": "OpenAlex publication_date as supplied, not a verified primary-source publication or availability date",
        "window": {"start_inclusive": START.isoformat(), "end_inclusive": END.isoformat()},
        "source_manifests": manifests, "counts": total,
        "all_retained_occurrences": sum(total.values()), "distinct_api_ids_in_all_retained_occurrences": len(all_ids),
        "distinct_api_ids_within_window": len(selected_ids), "distinct_api_ids_with_unknown_dates": len(unknown_ids),
        "counts_by_family": dict(sorted(family_counts.items())), "counts_by_invocation_family": run_counts,
        "successful_response_pages": total_successful_pages, "retained_error_attempts": total_error_attempts,
        "complete_query_families": sorted(complete_families),
        "incomplete_query_families": sorted(set(family_counts) - complete_families),
        "coverage_complete": False,
        "limitations": [
            "EQ1 remains incomplete: sorted recovery retained 4200 of 9368 reported matches; cross-attempt union is 4549 distinct API IDs.",
            "This A7 derivative covers retained C1 metadata only, not all C1 matches or all repository search channels.",
            "Search families and recovery attempts overlap; every occurrence is retained, and unique API IDs are not independent studies or samples.",
            "A date-selected inventory is not a newly executed date-filtered search, an eligibility decision or an update to the frozen cutoff.",
            "No language, access, outcome-direction or study-design exclusion is applied here; records outside the A7 window remain in the source exports.",
            "Unknown publication dates are retained separately for adjudication, and known metadata dates may still be inaccurate.",
        ],
        "artifacts": [],
    }
    for name, body in artifacts.items():
        payload = gzip.decompress(body)
        inventory["artifacts"].append({"path": (HERE / name).relative_to(ROOT).as_posix(), "sha256": digest(body),
                                       "bytes": len(body), "payload_sha256": digest(payload), "payload_bytes": len(payload)})
    artifacts["A7-INVENTORY.json"] = encode(inventory)
    return artifacts, inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifacts, inventory = build()
    for name, body in artifacts.items():
        path = HERE / name
        if args.check:
            if not path.exists() or path.read_bytes() != body:
                raise ValueError(f"Derived A7 artifact drift: {name}")
        else:
            path.write_bytes(body)
    print(json.dumps({key: inventory[key] for key in ("all_retained_occurrences", "counts", "distinct_api_ids_within_window", "distinct_api_ids_with_unknown_dates", "incomplete_query_families")}, indent=2))


if __name__ == "__main__":
    main()
