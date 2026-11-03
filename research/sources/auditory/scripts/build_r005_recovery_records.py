"""Register retained R005 recovery evidence without rewriting historical discovery.

The network harvesters retain responses independently. This offline integrator
checks hashes and counts, records every occurrence (including repeated retrievals)
and never turns an API work or a proceedings item into an included study.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.record_io import dumps

RECOVERY = ROOT / "research/searches/auditory/recovery-2026-11-03"
SEARCH = ROOT / "research/searches/auditory/records"
SOURCE = ROOT / "research/sources/auditory/records"
ACTOR = {"kind": "agent", "id": "chatgpt-r005-recovery-integrator",
         "tool": "ChatGPT; GitHub connector, web search, Python and Poppler",
         "model": "GPT-6 Astra Pro"}
REVIEW_ACTOR = {"kind": "agent", "id": "chatgpt-r005-icad-coverage",
                "tool": "ChatGPT subagent /root/icad_coverage; public HTTPS retrieval, pdfplumber and Poppler bibliography extraction",
                "model": "GPT-6 Astra Pro"}
OPENALEX_RUN_TOKENS = {
    "20261103-database-recovery": "RECOVERY",
    "20261103-database-sort-recovery": "SORT",
    "20261103-database-load-recovery": "LOAD",
}


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def read_json(path):
    blob = path.read_bytes()
    return json.loads(gzip.decompress(blob) if path.suffix == ".gz" else blob)


def known(value):
    return {"state": "known", "value": value}


def missing(reason, state="unknown"):
    return {"state": state, "reason": reason}


def pin(rid, rev=1):
    return {"id": rid, "rev": rev}


def artifact(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def verified_payload(page):
    path = ROOT / page["file"]
    blob = path.read_bytes()
    if digest(blob) != page["sha256"]:
        raise ValueError(f"Stored response hash mismatch: {path}")
    payload = gzip.decompress(blob) if path.suffix == ".gz" else blob
    if page.get("payload_sha256") and digest(payload) != page["payload_sha256"]:
        raise ValueError(f"Uncompressed response hash mismatch: {path}")
    return json.loads(payload)


def openalex_result_pages(pages):
    """Verify every retained response, but count only actual result pages."""
    works = []
    for page in pages:
        if not page.get("file"):
            if page.get("results"):
                raise ValueError("OpenAlex results have no retained response")
            continue
        payload = verified_payload(page)
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid OpenAlex response object: {page['file']}")
        if "results" not in page:
            status = page.get("http_status")
            if not isinstance(status, int) or status < 400 or payload.get("results"):
                raise ValueError(f"Unclassified OpenAlex response: {page['file']}")
            # Error excerpts are retained and hash-checked, not empty result pages.
            continue
        rows = payload.get("results")
        if (not isinstance(rows, list) or type(page["results"]) is not int
                or len(rows) != page["results"] or page.get("http_status", 200) >= 400):
            raise ValueError(f"Page count mismatch: {page['file']}")
        works.extend(rows)
    return works


def openalex_run_id(run_id, label):
    """Adding another manifest must never renumber recorded search identities."""
    if run_id not in OPENALEX_RUN_TOKENS:
        raise ValueError(f"Assign an explicit stable OpenAlex run token: {run_id}")
    return f"SRCH-R005R-C1{OPENALEX_RUN_TOKENS[run_id]}-{label}"


def _instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _review_identity_key(identifier):
    scheme, value = identifier["scheme"], identifier["value"].strip()
    if scheme == "doi":
        value = unquote(re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.I)).lower()
    return scheme, value


def _review_source_snapshot(at, proposed):
    """Exclude later sources and this integration's own source revisions."""
    rows = {path: read_json(path) for path in sorted((ROOT / "research").glob("**/records/SRC-*.json"))}
    rows.update({path: row for path, row in proposed.items() if row["kind"] == "source"})
    result = []
    cutoff = _instant(at)
    for path, row in rows.items():
        if row.get("kind") != "source" or row.get("synthetic"):
            continue
        prior = []
        for revision in row["revisions"]:
            when = _instant(revision["at"])
            if when > cutoff or (when == cutoff and revision["actor"]["id"] == REVIEW_ACTOR["id"]):
                break
            prior.append(revision)
        if prior:
            retained = copy.deepcopy(row)
            retained["revisions"] = copy.deepcopy(prior)
            result.append((path, retained))
    return result


def _review_source(at, preferred_id, data, proposed):
    """Reuse exact known identity and append the genuine new access observation."""
    incoming = {_review_identity_key(x) for x in data["identifiers"] if x["status"] == "verified"}

    def title_key(value):
        return re.sub(r"\s+", " ", value.casefold()).strip().rstrip(".")

    def author_key(authors):
        # Permit only name punctuation/order normalization, not fuzzy similarity.
        return sorted(re.findall(r"\w+", authors[0]["name"].casefold())) if authors else []

    matches = []
    snapshot = _review_source_snapshot(at, proposed)
    for path, row in snapshot:
        prior = row["revisions"][-1]["data"]
        ids = {_review_identity_key(x) for x in prior["identifiers"] if x["status"] == "verified"}
        same_metadata = (title_key(prior["title"]) == title_key(data["title"])
                         and author_key(prior["authors"]) == author_key(data["authors"])
                         and prior["publication_date"].get("state") == "known"
                         and prior["publication_date"]["value"][:4] == data["publication_date"]["value"][:4])
        if incoming & ids or same_metadata:
            matches.append((path, row))
    if len(matches) > 1:
        raise ValueError(f"Multiple existing source identities need adjudication: {preferred_id}")
    if not matches:
        if any(row["id"] == preferred_id for _, row in snapshot):
            raise ValueError(f"Review source ID already names another identity: {preferred_id}")
        path, row = SOURCE / f"{preferred_id}.json", {
            "schema_version": 1, "id": preferred_id, "kind": "source",
            "synthetic": False, "issue": 5, "revisions": []}
        basis = []
    else:
        path, row = matches[0]
        previous = row["revisions"][-1]
        old = previous["data"]
        if old.get("alias_of"):
            raise ValueError(f"Review source identity is an alias; resolve canonical source first: {row['id']}")
        merged = copy.deepcopy(old)
        merged.update(copy.deepcopy(data))
        # Access does not rescind prior rights, validity or family assertions.
        for field in ("validity", "family_links"):
            merged[field] = old[field]
        if old["rights"]["status"] != "unknown":
            merged["rights"] = old["rights"]
        if (old["publication_date"].get("state") == "known"
                and old["publication_date"]["value"].startswith(data["publication_date"]["value"])):
            merged["publication_date"] = old["publication_date"]
        identifiers = {(x["scheme"], x["value"]): x for x in old["identifiers"]}
        identifiers.update({(x["scheme"], x["value"]): x for x in data["identifiers"]})
        merged["identifiers"] = list(identifiers.values())
        manifestations = {m["id"]: m for m in old["manifestations"]}
        for manifestation in data["manifestations"]:
            if manifestation["id"] in manifestations and manifestations[manifestation["id"]] != manifestation:
                raise ValueError(f"Review manifestation ID conflict: {row['id']}")
            manifestations[manifestation["id"]] = manifestation
        merged["manifestations"] = list(manifestations.values())
        merged["metadata_evidence"] = list(dict.fromkeys(old["metadata_evidence"] + data["metadata_evidence"]))
        if old["metadata_status"] == "conflict":
            merged["metadata_status"] = "conflict"
        data, basis = merged, previous["basis"]
    revision = {"rev": len(row["revisions"]) + 1, "at": at, "actor": REVIEW_ACTOR,
                "basis": basis, "data": data, "factual_status": "source_reported"}
    row["revisions"].append(revision)
    proposed[path] = row
    return pin(row["id"], revision["rev"])


def register_recovered_reviews(at, proposed, record, run, hit):
    """Register the three hash-identified, ordered bibliographies (312 entries)."""
    directory = RECOVERY / "reviews"
    manifest = read_json(directory / "MANIFEST.json")
    observations = {row["name"]: row for row in
                    (json.loads(line) for line in (directory / "access.jsonl").read_text().splitlines())}
    specs = {
        "totland-2021": ("TOTLAND", "2021-06", "thesis", "Master thesis, University of South-Eastern Norway, June 2021; 52-page repository PDF"),
        "edworthy-2013": ("EDWORTHY", "2013", "review", "JAMIA 20(3), 584–589; six-page PDF; online-first date 2012-10-25 differs from 2013 issue year"),
        "ruskin-2020": ("RUSKIN", "2020-09-01", "report", "FAA final report phase 1; 79-page ROSA P PDF; title-page authors Ruskin, Corvin, Rice; repository order differs"),
    }
    if {s["review_key"] for s in manifest["reviews"]} != set(specs):
        raise ValueError("Recovered review set changed")
    total = 0
    for source in manifest["reviews"]:
        key = source["review_key"]
        label, date, source_type, edition = specs[key]
        export = source["reference_export"]
        path = directory / export["path"]
        blob = path.read_bytes()
        if digest(blob) != export["sha256"] or len(blob) != export["bytes"]:
            raise ValueError(f"Review bibliography export hash/size mismatch: {path}")
        bibliography = json.loads(blob)
        capture = observations[source["fulltext_capture"]]
        pdf = source["source_pdf"]
        if (capture["status"] != 200 or capture["content_type"].split(";")[0] != "application/pdf"
                or capture["sha256"] != bibliography["source_sha256"]
                or capture["sha256"] != pdf["sha256"] or capture["bytes"] != pdf["bytes"]):
            raise ValueError(f"Review source capture mismatch: {key}")
        entries = bibliography["references"]
        count = len(entries)
        page_range = bibliography["reference_pdf_pages_inclusive"]
        if (count != source["reference_count"] or count != bibliography["reference_count"]
                or [e["ordinal"] for e in entries] != list(range(1, count + 1))
                or page_range != source["reference_pdf_pages_inclusive"]):
            raise ValueError(f"Review bibliography count/order mismatch: {key}")
        for entry in entries:
            pages = sorted({line["pdf_page"] for line in entry["citation_lines"]})
            if (pages != entry["pdf_pages"] or not pages
                    or any(not page_range[0] <= page <= page_range[1] for page in pages)):
                raise ValueError(f"Review reference locator mismatch: {key} {entry['ordinal']}")
        if key == "edworthy-2013" and [e["source_number"] for e in entries] != list(range(1, 81)):
            raise ValueError("Edworthy bibliography numbering changed")
        total += count
        provenance = f"reviews/MANIFEST.json {key}; source title-page/identity inspection; capture SHA256 {capture['sha256']}"
        urls = list(dict.fromkeys([source["landing_url"], capture["requested_url"]]
                                 + ([source["original_handle"]] if source.get("original_handle") else [])))
        identifiers = [{"scheme": "url", "value": url, "status": "verified", "provenance": provenance} for url in urls]
        if source.get("doi"):
            identifiers.append({"scheme": "doi", "value": source["doi"], "status": "verified", "provenance": provenance})
        manifestation_id = "C9-RECOVERED-PDF-20261103"
        source_ref = _review_source(at, "SRC-R005R-" + key.upper(), {
            "title": source["title"],
            "authors": [{"name": name, "role": "author"} for name in source["authors_in_pdf_title_page_order"]],
            "publication_date": known(date), "identifiers": identifiers,
            "source_type": source_type, "language": known("en"), "edition": known(edition),
            "metadata_status": "verified", "metadata_evidence": source["identity_evidence"] + source["identity_notes"] + [provenance],
            "access_status": "full_text_available", "access_at": capture["finished_at"],
            "access_reason": "Complete PDF lawfully retrieved; identity block and bibliography ranges only inspected. Failed routes and exact times remain in reviews/access.jsonl. No empirical extraction or full-report reading asserted.",
            "rights": {"status": "unknown", "reason": source["rights_note"],
                       "evidence": missing("No blanket redistribution permission established; bytes held outside Git")},
            "validity": "active", "family_links": [],
            "manifestations": [{"id": manifestation_id, "sha256": capture["sha256"],
                                "extent": bibliography["source_pdf_pages"], "coordinate": "file_page_1based",
                                "location": capture["requested_url"] + " (exact bytes held outside repository; stable retrieval route and hashes in reviews/MANIFEST.json)"}],
        }, proposed)
        aid = f"AID-R005R-{label}-REFERENCES"
        record(aid, "assistance", {
            "subtype": "reading", "source_ref": source_ref, "manifestation_id": manifestation_id,
            "access_at_read": "full_text_available", "reading_status": "selected_ranges_read",
            "ranges": [[1, 1], page_range],
            "method": "Identity block on PDF page 1 only; complete bibliography range via pdfplumber with retained line boxes and Poppler checks. No empirical results extracted. Separate AI subagent checked counts and layout; this is not human review.",
            "status": "performed", "performed_at": known(manifest["created_at"]),
            "independence": "Executed by ChatGPT subagent /root/icad_coverage; correlated AI technical boundary check by /root/icad_coverage/review_boundary_check; no independent human review.",
        }, [source_ref], "source_reported", actor=REVIEW_ACTOR)
        rid = f"SRCH-R005R-C9{label}"
        run(rid, path, count, capture["started_at"], manifest["created_at"],
            "Every entry in the source bibliography, in original order, PDF pages " + "–".join(map(str, page_range)),
            "Reference list of " + source["title"] + ", protocol C9",
            "Hash-identified PDF bibliography; ordered line/column extraction; source identity and raw citation text retained",
            complete=True, basis=[source_ref, pin(aid)], actor=REVIEW_ACTOR,
            boundary="Complete source bibliography only. Every original occurrence retained, including duplicates and context sources; all remain unscreened. No study/sample independence or empirical result reading inferred.",
            filters=["No reference-level eligibility filter; publication cutoff and identity adjudication deferred to screening"])
        for entry in entries:
            # Never use unverified parser title/author/date hints as raw metadata.
            raw = entry["citation_text"] + " | " + entry["occurrence_id"] + " | source PDF pp. " + ",".join(map(str, entry["pdf_pages"]))
            raw += "; printed pp. " + ",".join(entry["printed_pages"]) + "; exact line/column boxes in retained export"
            # Keep only complete literal DOI URL tokens; no reference identity is verified here.
            identifiers = [{"scheme": "doi", "value": value} for value in
                           re.findall(r"https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/\S+)", entry["citation_text"], re.I)]
            hit(rid, entry["ordinal"], raw, identifiers, actor=REVIEW_ACTOR)
    if total != manifest["total_reference_occurrences"] or total != 312:
        raise ValueError("Recovered review occurrence total changed")


def safe_write_records(records, check=False):
    """Preflight the whole batch before writing; retain later appended revisions."""
    changes = []
    for path, proposed in records.items():
        if path.exists():
            existing = read_json(path)
            fields = ("schema_version", "id", "kind", "synthetic", "issue")
            if any(existing.get(k) != proposed[k] for k in fields):
                raise ValueError(f"Record identity changed: {path}")
            common = min(len(existing["revisions"]), len(proposed["revisions"]))
            if existing["revisions"][:common] != proposed["revisions"][:common]:
                raise ValueError(f"Refusing to rewrite recorded history: {path}")
            if len(proposed["revisions"]) > len(existing["revisions"]):
                if check:
                    raise ValueError(f"Missing generated recovery revision: {path}")
                changes.append((path, dumps(proposed)))
        elif check:
            raise ValueError(f"Missing generated recovery record: {path}")
        else:
            changes.append((path, dumps(proposed)))
    for path, content in changes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return len(changes)


def build(at):
    out, run_ids = {}, []

    def record(rid, kind, data, basis=(), factual="discovery", *, actor=None):
        path = (SEARCH / "hits" if kind == "search_hit" else SEARCH if kind == "search_run" else SOURCE) / (rid + ".json")
        out[path] = {"schema_version": 1, "id": rid, "kind": kind,
                     "synthetic": False, "issue": 5,
                     "revisions": [{"rev": 1, "at": at, "actor": actor or ACTOR,
                                    "basis": list(basis), "data": data,
                                    "factual_status": factual}]}

    def run(rid, path, count, start, finish, query, platform, interface,
            *, complete, reported=None, failures=(), basis=(), boundary, filters=(), actor=None, planned=False):
        if planned and (count or complete):
            raise ValueError("A planned query cannot contain retrieved results or completed pagination")
        run_ids.append(rid)
        record(rid, "search_run", {
            "lane": "auditory", "protocol_version": "v1", "mode": "production",
            "status": "planned" if planned else "completed" if complete else "partial" if count else "failed",
            "platform": platform, "interface": interface, "query": query,
            "filters": list(filters),
            "coverage": {"start": missing("No lower date bound", "not_applicable"),
                         "end": known("2026-10-04")},
            "started_at": missing("No query-specific network request recorded") if planned else known(start),
            "finished_at": missing("No query-specific network request recorded") if planned else known(finish),
            "reported_count": reported if reported is not None else missing("No independently reported total", "not_reported"),
            "retrieved_count": count,
            "export": missing("No query-specific response export; planning context retained in the batch manifest") if planned else known(artifact(path)),
            "pagination": {"complete": complete, "detail": boundary},
            "failures": list(failures), "boundary": boundary,
        }, basis, "source_reported", actor=actor)

    def hit(run_id, number, raw, identifiers, *, actor=None):
        hid = run_id.replace("SRCH-", "HIT-", 1) + f"-{number:05d}"
        # Keep original metadata and identifiers; identity is R006's adjudication.
        identifiers = list({(x["scheme"], x["value"]): x for x in identifiers}.values())
        record(hid, "search_hit", {
            "search_ref": pin(run_id), "ordinal": number, "raw_metadata": raw,
            "returned_identifiers": identifiers, "status": "unresolved",
            "resolution_reason": "Retained discovery occurrence; publication identity, eligibility and study/sample relationships require R006 adjudication.",
        }, [pin(run_id)], actor=actor)

    # C1: each historical attempt remains its own run; retries are not overwritten.
    manifests = sorted((ROOT / "research/searches/auditory/exports/openalex").glob("*/MANIFEST.json"))
    for path in manifests:
        manifest = read_json(path)
        if not manifest.get("finished_at"):
            raise ValueError(f"Harvest still running: {path}")
        for label, entry in sorted(manifest["runs"].items()):
            planned = not entry["pages"]
            if not planned and not entry.get("started_at"):
                raise ValueError(f"Actual OpenAlex attempts lack start time: {path} {label}")
            works = openalex_result_pages(entry["pages"])
            count = len(works)
            unique = len({w["id"] for w in works})
            if count != entry["retrieved"] or unique != entry["unique_retrieved"]:
                raise ValueError(f"Harvest count mismatch: {path} {label}")
            complete = bool(entry["complete"])
            if complete and (count != unique or count != entry["reported_count"] or entry["failures"]):
                raise ValueError(f"False completed harvest: {path} {label}")
            rid = openalex_run_id(manifest["run_id"], label)
            boundary = (f"Run {manifest['run_id']}, query {label}: {count} retained occurrences, {unique} distinct OpenAlex IDs. "
                        "An OpenAlex ID is not a verified independent study. Every retrieval attempt is preserved and requires cross-run deduplication. "
                        "Public gzip metadata derivatives omit abstracts; raw-response hashes and transient private cache keys are retained. "
                        "Index updates and tied sorting can cause paging duplicates; these prevent completed status.")
            if planned:
                boundary = (f"Run {manifest['run_id']}, query {label}: planned but not attempted; zero network pages. "
                            "The batch stopped after a different query's HTTP 429. The manifest's copied orchestration timestamps and failure label are not this query's retrieval observation. "
                            f"Planning provenance: {path.relative_to(ROOT)} /runs/{label}.")
            run(rid, path, count, entry["started_at"], entry["finished_at"], entry["filter"],
                "OpenAlex works API, protocol C1", "Unauthenticated HTTPS; documented basic paging; per_page=200 legacy support; exact per-page URLs and sort in manifest",
                complete=complete, reported=entry.get("reported_count"), failures=[] if planned else entry["failures"], boundary=boundary, planned=planned,
                basis=[pin("HG-R002-DATABASE-ACCESS")],
                filters=["Frozen title/abstract Boolean concept blocks preserved", "Publication date <= 2026-10-04", "No language, type or open-access restriction"])
            for number, work in enumerate(works, 1):
                ids = [{"scheme": "url", "value": work["id"]}]
                if work.get("doi"):
                    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", work["doi"], flags=re.I)
                    ids.append({"scheme": "doi", "value": unquote(doi)})
                first = next((a.get("author", {}).get("display_name", "") for a in work.get("authorships", [])), "")
                raw = f"{work.get('display_name') or '[title not supplied]'} | first author: {first or '[not supplied]'} | {work.get('publication_date')} | {work.get('type')} | {work['id']}"
                hit(rid, number, raw, ids)

    # C5: enumerate the available series, including explicit empty-year outcomes.
    path = RECOVERY / "icad/MANIFEST.json"
    icad = read_json(path)
    for page in icad["pages"]:
        verified_payload(page)
    items = [item for year in icad["years"] for item in year["results"]] + icad["unassigned_or_out_of_range"]
    if len(items) != icad["retrieved_total"] or len({i["repository_item_id"] for i in items}) != icad["unique_repository_ids"]:
        raise ValueError("ICAD item count or identity mismatch")
    rid = "SRCH-R005R-C5SERIES"
    run(rid, path, len(items), min(p["started_at"] for p in icad["pages"]), max(p["finished_at"] for p in icad["pages"]),
        "Enumerate every page of Georgia Tech ICAD series 6cb90d00-3311-4767-954d-415c9341a358; record issued-year outcomes 1992–2026",
        "Georgia Tech public ICAD series index, protocol C5", "Public repository HTTPS API; 13 advertised pages; complete index enumeration",
        complete=True, reported=icad["reported_total"], boundary="The available index was completely enumerated. This does not establish complete venue coverage: 1992 is absent and the 2026 bin is a 2025 companion book issued in 2026. Items include proceedings and media. Date eligibility is screened later.",
        filters=["ICAD series membership only; publication-date cut-off applied later at screening"])
    for number, item in enumerate(items, 1):
        ids = [{"scheme": "url", "value": item["repository_url"]}]
        ids.extend({"scheme": "doi", "value": d} for d in item["doi"])
        ids.extend({"scheme": "url", "value": u} for u in item["identifiers"] if u.startswith(("https://", "http://")))
        raw = f"{' / '.join(item['title']) or '[title not supplied]'} | {'; '.join(item['authors'])} | issued: {', '.join(item['issued_dates'])} | {'; '.join(item['resource_type'])} | {item['repository_url']}"
        hit(rid, number, raw, ids)

    # Supplemental C9 navigation is a tool batch, not a bibliographic database.
    path = RECOVERY / "references/NAVIGATION.json"
    navigation = read_json(path)
    rid = "SRCH-R005R-C9NAV"
    run(rid, path, len(navigation["results"]), navigation["started_at"], navigation["finished_at"],
        "\n".join(navigation["queries"]), "Web search, C9 known-item recovery", navigation["engine"], complete=False,
        boundary=navigation["boundary"])
    for result in navigation["results"]:
        hit(rid, result["ordinal"], f"{result['title']} | {result['url']}", [{"scheme": "url", "value": result["url"]}])

    # Actual source identity/reading is bounded to metadata and reference sections.
    access = {row["label"]: row for row in read_json(RECOVERY / "references/access.json")["access"]}
    reference_export = RECOVERY / "references/REFERENCE-LISTS.json"
    source_specs = {
        "nees-liebman-am": {
            "title": "Auditory icons, earcons, spearcons, and speech: A systematic review and meta-analysis of brief audio alerts in human-machine interfaces",
            "authors": ["Nees, Michael A.", "Liebman, Eliana"], "date": "2023", "type": "preprint",
            "edition": "52-page accepted manuscript labelled 3.16.23; cover states acceptance 5.24.23. Distinct from the older 47-page 9.8.22 preprint and the Version of Record.",
            "links": [{"relation": "version_of", "source_ref": pin("SRC-NOV-NEES-LIEBMAN-2023-PREPRINT"), "reason": "Same authors/title, later manuscript version; no statistical equivalence assumed."},
                      {"relation": "version_of", "source_ref": pin("SRC-NOV-NEES-LIEBMAN-2023"), "reason": "The accepted-manuscript cover explicitly identifies the Version of Record DOI."}],
            "rights": {"status": "unknown", "reason": "Full source retained privately; no redistribution permission newly asserted by this access check.", "evidence": missing("No new licence inspection")},
        },
        "sleep-review": {
            "title": "Alarm Tones, Voice Warnings, and Musical Treatments: A Systematic Review of Auditory Countermeasures for Sleep Inertia in Abrupt and Casual Awakenings",
            "authors": ["McFarlane, Stuart J.", "Garcia, Jair E.", "Verhagen, Darrin S.", "Dyer, Adrian G."],
            "date": "2020-10-20", "type": "review", "edition": "Clocks & Sleep 2(4), 416–433, publisher PDF v2", "links": [],
            "doi": "10.3390/clockssleep2040031",
            "rights": {"status": "redistribution_permitted", "reason": "The source's last page states CC BY 4.0; only bibliographic metadata is committed here.", "evidence": known("Publisher PDF file page 18, copyright/licence statement; http://creativecommons.org/licenses/by/4.0/")},
        },
    }
    for source in read_json(reference_export)["sources"]:
        label, sid = source["label"], source["source_id"]
        spec, observation = source_specs[label], access[label]
        mids = "RECOVERED-PDF-20261103"
        ids = [{"scheme": "url", "value": source["url"], "status": "verified", "provenance": "Direct PDF retrieval, hash and header inspection in recovery access ledger"}]
        if spec.get("doi"):
            ids.append({"scheme": "doi", "value": spec["doi"], "status": "verified", "provenance": "Publisher PDF header/footer, file page 1"})
        record(sid, "source", {
            "title": spec["title"], "authors": [{"name": a, "role": "author"} for a in spec["authors"]],
            "publication_date": known(spec["date"]), "identifiers": ids, "source_type": spec["type"],
            "language": known("en"), "edition": known(spec["edition"]), "metadata_status": "verified",
            "metadata_evidence": ["Downloaded source header inspected; exact bytes/hash and retrieval time in recovery reference access ledger."],
            "access_status": "full_text_available", "access_at": observation["finished_at"],
            "access_reason": "Complete PDF retrieved lawfully. Reading was limited to header/identity and reference-list ranges; no primary experimental result extracted.",
            "rights": spec["rights"], "validity": "active", "family_links": spec["links"],
            "manifestations": [{"id": mids, "sha256": source["sha256"], "extent": source["pages"],
                                "coordinate": "file_page_1based", "location": source["url"] + " (downloaded bytes held outside the public repository)"}],
        }, [x["source_ref"] for x in spec["links"]], "source_reported")
        aid = "AID-R005R-" + ("NLAM" if label == "nees-liebman-am" else "SLEEP") + "-REFERENCES"
        record(aid, "assistance", {
            "subtype": "reading", "source_ref": pin(sid), "manifestation_id": mids,
            "access_at_read": "full_text_available", "reading_status": "selected_ranges_read",
            "ranges": [[1, 1], source["range"]],
            "method": "Poppler pdftotext -layout; header and bibliography inspected; rendered reference pages checked. Bibliographic entries only, not a whole-report reading or numerical extraction.",
            "status": "performed", "performed_at": known(at),
            "independence": "AI-assisted reading by the executing ChatGPT agent; no human or external review.",
        }, [pin(sid)], "source_reported")
        rid = "SRCH-R005R-C9" + ("NLGENERAL" if label == "nees-liebman-am" else "SLEEP")
        run(rid, reference_export, len(source["entries"]), observation["started_at"], at,
            "Every entry in " + source["section"], "Reference list of " + spec["title"] + ", protocol C9",
            "Hash-identified PDF; deterministic ordered bibliographic extraction with file-page locators",
            complete=True, basis=[pin(sid), pin(aid)],
            boundary="Complete enumeration of this reference section. Entries remain unscreened discovery occurrences; methods/context sources are retained and no sample independence is inferred.")
        for entry in source["entries"]:
            ids = []
            for doi in re.findall(r"https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/\S+)", entry["text"], re.I):
                ids.append({"scheme": "doi", "value": doi})
            raw = f"{entry['text']} | source PDF pp.{entry['file_page_start']}–{entry['file_page_end']}, reference {entry['ordinal']}"
            hit(rid, entry["ordinal"], raw, ids)

    register_recovered_reviews(at, out, record, run, hit)

    record("AID-R005R-RECOVERY", "assistance", {
        "subtype": "assistance", "task": "Resume preserved R005, recover available bibliographic/ICAD/reference-list channels, preserve access gaps and register all actual retrieval occurrences.",
        "input_refs": [pin("HG-R002-DATABASE-ACCESS")], "output_refs": [pin(rid) for rid in run_ids],
        "artifacts": [str(RECOVERY.relative_to(ROOT)), "research/sources/auditory/scripts/build_r005_recovery_records.py"],
        "verification_steps": ["Hash-check retained responses and gzip payloads", "Reconcile run counts and unique API/repository IDs", "Preserve historical observations and separate retrieval attempts", "Inspect actual source headers and reference sections; keep unread experimental reports unscreened"],
        "limitations": "ChatGPT agents performed retrieval, code review and record checks. No independent human screening, scholarly review or empirical validation occurred. Access and paging gaps remain explicit; repository integrity does not establish scientific validity.",
        "status": "performed", "performed_at": known(at),
        "independence": "Parent integrator plus disjoint database and ICAD/reference-recovery subagents; correlated AI checks, not independent human review.",
    }, [pin("HG-R002-DATABASE-ACCESS")], "researcher_interpretation")
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stamp_path = RECOVERY / "INTEGRATION.json"
    if stamp_path.exists():
        at = read_json(stamp_path)["recorded_at"]
    elif args.check:
        raise SystemExit("Missing integration timestamp")
    else:
        at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        stamp_path.write_text(dumps({"recorded_at": at, "base_main": "17744bafca1297e8b94a0684d9011489506ba319",
                                    "preserved_branch_head": "d3869293c90f4a1c136041dd5144ae1c057fa4dc"}))
    records = build(at)
    written = safe_write_records(records, args.check)
    print(f"{'Verified' if args.check else 'Registered'} {len(records)} recovery records; {written} new files.")


if __name__ == "__main__":
    main()
