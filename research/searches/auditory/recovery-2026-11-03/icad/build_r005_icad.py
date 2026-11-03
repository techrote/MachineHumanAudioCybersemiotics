#!/usr/bin/env python3
"""Rebuild an ICAD series listing manifest from retained public API pages."""
import hashlib
import gzip
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def raw_bytes(relative):
    """Return exact original response bytes from the optional lossless container."""
    storage_path = HERE / "STORAGE.json"
    storage = json.loads(storage_path.read_text()) if storage_path.exists() else {}
    item = storage.get(relative)
    if item is None:
        return (HERE / relative).read_bytes(), relative, None
    blob = (HERE / item["stored_path"]).read_bytes()
    if hashlib.sha256(blob).hexdigest() != item["storage_sha256"]:
        raise ValueError(f"compressed hash mismatch: {relative}")
    payload = gzip.decompress(blob)
    if hashlib.sha256(payload).hexdigest() != item["payload_sha256"]:
        raise ValueError(f"original response hash mismatch: {relative}")
    return payload, item["stored_path"], item

def values(meta, key):
    return [x["value"] for x in meta.get(key, [])]

def build():
    access = [json.loads(line) for line in (HERE / "access.jsonl").read_text().splitlines()]
    by_file = {x["file"]: x for x in access if x.get("status") == 200}
    first = json.loads(raw_bytes("raw/series-page-000.json")[0])
    page_info = first["_embedded"]["searchResult"]["page"]
    total_pages, total_items = page_info["totalPages"], page_info["totalElements"]
    results, pages, uuids = [], [], set()
    for n in range(total_pages):
        candidates = [f"raw/series-page-{n:03}.json", f"raw/series-page-{n:03}-lite.json"]
        rel = next(path for path in candidates if path in by_file)
        provenance = by_file[rel]
        blob, stored_path, storage = raw_bytes(rel)
        if hashlib.sha256(blob).hexdigest() != provenance["sha256"]:
            raise ValueError(f"hash mismatch: {rel}")
        data = json.loads(blob)["_embedded"]["searchResult"]
        info = data["page"]
        if info["number"] != n or info["totalPages"] != total_pages or info["totalElements"] != total_items:
            raise ValueError(f"pagination drift: {rel}")
        objects = data["_embedded"].get("objects", [])
        expected = min(info["size"], total_items - n * info["size"])
        if len(objects) != expected:
            raise ValueError(f"truncated page: {rel}")
        page = dict(provenance)
        page["file"] = str((HERE / stored_path).relative_to(ROOT))
        if storage:
            page["payload_sha256"] = page["sha256"]
            page["payload_bytes"] = page["bytes"]
            page["sha256"] = storage["storage_sha256"]
            page["bytes"] = storage["storage_bytes"]
            page["encoding"] = "gzip; exact original response on decompression"
        page["page"] = info
        pages.append(page)
        for index, result in enumerate(objects):
            item = result["_embedded"]["indexableObject"]
            uuid = item["uuid"]
            if uuid in uuids:
                raise ValueError(f"duplicate item across pages: {uuid}")
            uuids.add(uuid)
            meta = item["metadata"]
            dates = values(meta, "dc.date.issued")
            years = {int(m.group()) for date in dates if (m := re.match(r"\d{4}", date))}
            year = next(iter(years)) if len(years) == 1 else None
            results.append({
                "repository_item_id": uuid,
                "title": values(meta, "dc.title"),
                "authors": values(meta, "dc.contributor.author"),
                "editors": values(meta, "dc.contributor.editor"),
                "issued_dates": dates,
                "issued_year": year,
                "doi": values(meta, "dc.identifier.doi"),
                "identifiers": values(meta, "dc.identifier.uri"),
                "repository_url": f"https://repository.gatech.edu/entities/publication/{uuid}",
                "handle": item.get("handle"),
                "resource_type": values(meta, "dc.type"),
                "genre": values(meta, "dc.type.genre"),
                "language": values(meta, "dc.language.iso"),
                "rights": values(meta, "dc.rights"),
                "metadata_rights": values(meta, "dc.rights.metadata"),
                "raw_path": page["file"],
                "raw_sha256": page.get("payload_sha256", page["sha256"]),
                "storage_sha256": page["sha256"],
                "raw_locator": f"/_embedded/searchResult/_embedded/objects/{index}/_embedded/indexableObject",
                "reading_status": "metadata_only",
                "eligibility_status": "not_screened",
            })
    if len(results) != total_items:
        raise ValueError("retrieved count does not equal advertised count")
    old = json.loads((ROOT / "research/searches/auditory/exports/ICAD-LISTING-2026-10-13.json").read_text())
    old_years = {x["year"]: x for x in old["years_listed"]}
    years = []
    for year in range(1992, 2027):
        rows = [x for x in results if x["issued_year"] == year]
        legacy = old_years.get(year)
        years.append({
            "year": year,
            "year_basis": "dc.date.issued metadata prefix; not inferred conference year",
            "status": "complete_series_listing" if rows else "zero_items_in_complete_series_listing",
            "reason": "All 13 pages of the series index were retained; this is index enumeration, not a guarantee that all conference papers were deposited.",
            "started_at": min(x["started_at"] for x in pages),
            "finished_at": max(x["finished_at"] for x in pages),
            "listing_urls": [x["url"] for x in pages],
            "raw_pages": [{"file": x["file"], "sha256": x["sha256"]} for x in pages],
            "returned_count": len(rows),
            "results": rows,
            "legacy_listing": {"file": legacy["file"], "sha256": legacy["sha256"], "url": legacy["url"], "filename_count": len(legacy["pdf_files"])} if legacy else None,
        })
    manifest = {
        "schema": "mhac-r005-icad-recovery/1",
        "issue": 5,
        "channel": "C5",
        "actor": "ChatGPT GPT-6 Astra Pro, ICAD retrieval subagent",
        "human_verification": "none",
        "method": "Complete public Georgia Tech ICAD series index pagination, then grouping by recorded issue-date year.",
        "route": "Observed public API URLs embedded in raw/series.html, using page size 100 and all pages 0–12.",
        "status": "completed_index_enumeration",
        "reported_total": total_items,
        "retrieved_total": len(results),
        "unique_repository_ids": len(uuids),
        "pages": pages,
        "years": years,
        "unassigned_or_out_of_range": [x for x in results if x["issued_year"] is None or not 1992 <= x["issued_year"] <= 2026],
        "limitations": [
            "No primary paper or numeric study result was read or extracted in this retrieval batch.",
            "Series items include whole proceedings, presentations and ancillary media as well as individual papers; counts are item occurrences, not eligible studies.",
            "Issue-date metadata may differ from conference year: e.g. the ICAD 2025 companion book is dated 2026-07. No conference-year corrections were silently made.",
            "An empty issue-date year is not evidence that a conference or publications did not exist.",
            "The baseline cut-off remains 2026-10-04; date eligibility and any ambiguous dates require screening.",
            "All legacy filename-only occurrences remain preserved and may overlap this metadata inventory; deduplication belongs to R006.",
        ],
    }
    encoded = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    if "--check" in sys.argv:
        if (HERE / "MANIFEST.json").read_text() != encoded:
            raise ValueError("manifest is stale; rebuild from retained pages")
        print(f"Verified {len(results)} item occurrences across {total_pages} pages; {len(years)} year outcomes.")
    else:
        (HERE / "MANIFEST.json").write_text(encoded)
        print(f"Built {len(results)} item occurrences across {total_pages} pages; {len(years)} year outcomes.")

if __name__ == "__main__":
    build()
