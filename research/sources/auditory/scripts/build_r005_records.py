"""Write the MHAC-R005 auditory-lane search records deterministically.

Run from the repository root:

    python3 research/sources/auditory/scripts/build_r005_records.py

Inputs are the retained export (titles, URLs and reference-list entries copied from the
session's tool-call log) and the adjudications written below. The script fetches nothing.
It writes search_run, search_hit and assistance records plus a known-item check table.
Later changes must append revisions to the written records rather than rerun this over them.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.record_io import dumps  # noqa: E402

AT = "2026-10-13T06:30:12Z"
ACTOR = {"kind": "agent", "id": "claude-r005-session",
         "tool": "Claude in a claude.ai cloud session (WebSearch, WebFetch, shell)",
         "model": "claude-opus-5-5"}
EXPORT = "research/searches/auditory/exports/AUDITORY-WEBSEARCH-2026-10-13.json"
ICAD_LISTING = "research/searches/auditory/exports/ICAD-LISTING-2026-10-13.json"
OPENALEX_MANIFEST = "research/searches/auditory/exports/openalex/MANIFEST.json"
LEDGER = "research/searches/auditory/exports/ACCESS-LEDGER-R005-2026-10-13.csv"
KNOWN_CSV = "research/searches/auditory/exports/KNOWN-ITEM-CHECK-R005.csv"
MEMO = "research/sources/auditory/README.md"
SEARCH_DIR = "research/searches/auditory/records"
SOURCE_DIR = "research/sources/auditory/records"
NL = "SRC-NOV-NEES-LIEBMAN-2023-PREPRINT"
FRA = "SRC-NOV-FRA-IVAA-2022"


def missing(state: str, reason: str) -> dict:
    return {"state": state, "reason": reason}


def known(value) -> dict:
    return {"state": "known", "value": value}


def ref(rid: str) -> dict:
    return {"id": rid, "rev": 1}


def record(rid, kind, data, basis=(), factual="discovery"):
    return {"schema_version": 1, "id": rid, "kind": kind, "synthetic": False, "issue": 5,
            "revisions": [{"rev": 1, "at": AT, "actor": ACTOR, "basis": list(basis), "data": data,
                           "factual_status": factual}]}


# --- Known-item check of the 68 reports in the Nees & Liebman list (RL-NL) -------------------
# outcome: located = a result title or a persistent identifier in a result URL matches the entry;
# possible = only a file name, host or record key suggests it; not_located = neither.
# Ordinals refer to the K-run with the same number. "Also in" lists topic runs whose result
# title matched the entry's opening words. Title-level only; identity is left to #6.
KNOWN = {
    1: ("located", [1], "", ["A-W1-ES:9"]),
    2: ("not_located", [], "", []),
    3: ("located", [1, 2, 3, 4], "IDEAS record gives volume 14, issue 4, pages 95-109.", []),
    4: ("not_located", [], "Results concern serendipity in general.", []),
    5: ("located", [1, 2, 4], "", []),
    6: ("located", [2], "", []),
    7: ("not_located", [], "", []),
    8: ("possible", [2], "Only the file name CHI93.PDF on the first author's site suggests the paper.", []),
    9: ("not_located", [], "Other digital-talking-book papers by the same authors were returned.", []),
    10: ("located", [1], "", []),
    11: ("located", [1], "", []),
    12: ("not_located", [], "", []),
    13: ("located", [1], "", ["I-W1:6"]),
    14: ("located", [2, 7], "Matched by the DOI in OpenAlex and Crossref URLs; titles not shown.", []),
    15: ("located", [1, 2, 4], "", []),
    16: ("located", [4, 6], "", []),
    17: ("located", [2], "", ["A-W1-DE:7"]),
    18: ("possible", [1], "Only the record key glatzkbc2018 suggests the paper.", []),
    19: ("located", [2, 6, 7], "", []),
    20: ("located", [1], "", []),
    21: ("located", [4], "Title matches, but the result is a third-party proxy URL (not opened) and its record key says 2014 where the list says 2016.", []),
    22: ("located", [1], "", []),
    23: ("possible", [1, 2], "Repository record of an author's institution; title not shown.", []),
    24: ("located", [1], "Repository title adds 'while Playing a Game'.", []),
    25: ("possible", [3, 4], "Only departmental news posts announcing the publication were returned.", []),
    26: ("located", [1, 2], "", []),
    27: ("located", [1, 2, 3], "", []),
    28: ("located", [2, 3, 9], "", []),
    29: ("not_located", [], "", []),
    30: ("located", [1], "", ["T-W8:5"]),
    31: ("located", [1], "Repository title adds 'The bigger picture'.", []),
    32: ("located", [1, 2], "", []),
    33: ("not_located", [], "", []),
    34: ("not_located", [], "", []),
    35: ("not_located", [], "Results are HRTF patents and unrelated records.", []),
    36: ("possible", [2], "Only the file name chi11-mcgee1 suggests the paper.", []),
    37: ("located", [1], "", ["I-W2:2", "I-W8:1", "I-W9:5"]),
    38: ("not_located", [], "", []),
    39: ("located", [1], "Repository title adds 'of a driving-like dual task'.", ["T-W1:8"]),
    40: ("located", [1, 2, 3], "", []),
    41: ("located", [1], "", ["T-W2:8", "T-W8:9", "T-W9:5"]),
    42: ("not_located", [], "", []),
    43: ("possible", [1], "Repository record at the first author's institution; title not shown.", []),
    44: ("not_located", [], "Related working-memory and alarm studies were returned instead.", []),
    45: ("not_located", [], "Related curve-warning items by the same group (different titles) were returned.", []),
    46: ("located", [1, 2], "Two repository records carry the same title.", []),
    47: ("located", [1, 2], "", ["A-W1-ES:3", "A-W1-ES:5", "A-W1-ZH:3", "A-W1-JA:4", "A-W1-JA:6"]),
    48: ("possible", [2], "Only the dblp record key conf/fdg/RamosF11 suggests the paper.", []),
    49: ("located", [1], "", []),
    50: ("not_located", [], "Other multimodal-browsing papers by the first author were returned.", []),
    51: ("located", [1, 2, 4], "", []),
    52: ("not_located", [], "", []),
    53: ("not_located", [], "", []),
    54: ("not_located", [], "", []),
    55: ("located", [1], "", []),
    56: ("not_located", [], "The known-item query missed it, but topic runs returned a matching title.", ["T-W1:1", "T-W2:4", "T-W5:3", "T-W7:10", "T-W9:2"]),
    57: ("located", [1, 2], "", []),
    58: ("located", [1, 4], "", []),
    59: ("located", [1], "Result 1 is untitled here; the same URL carries the full title in run T-W1.", ["T-W1:5"]),
    60: ("located", [5], "Matched by the DOI in the URL; title not shown.", []),
    61: ("located", [1, 2], "", ["I-W1:9", "I-W7:8"]),
    62: ("located", [2, 3], "", []),
    63: ("located", [1, 2], "", []),
    64: ("not_located", [], "Only the 2006 ICAD paper with a similar title was returned (result 3); see the duplicate flags.", []),
    65: ("possible", [2, 3], "Only a repository record and the first author's PhD thesis were returned.", []),
    66: ("possible", [1, 3], "Only file names ICMI 2011_warnock / icmi11-warnock suggest the paper.", []),
    67: ("not_located", [], "A related auditory-cueing item from another institution was returned.", []),
    68: ("not_located", [], "The RL-NL entry was truncated; the full title comes from RL-NLAM.", []),
    69: ("possible", [1, 4], "Only the containing proceedings volume (publisher page, dblp table of contents) was returned.", []),
}

OPENED = "The agent fetched this URL in R005 and the page printed this report's number and title (R005 access ledger row 6)."
SAME_URL = "The URL is an identifier already recorded on this source record."
DOI_IN_URL = "The URL carries this source record's DOI; the page was not opened."


def channel_text(channel: str, run: dict) -> tuple[str, str, list[str]]:
    mode = run["mode"]
    doms = run.get("allowed_domains")
    filters = ["No user-set filters; tool default US-only results"]
    if doms:
        filters = [f"allowed_domains restricted to: {', '.join(doms)}", "Tool default US-only results"]
    interface = f"WebSearch tool, {mode} mode, US-only results" + (", domain-restricted" if doms else "")
    platform = {
        "C8": "General web search engine via the agent's WebSearch tool (protocol channel C8)",
        "C9": "General web search engine via the agent's WebSearch tool, used for C9 known-item lookup",
        "C5": "General web search engine via the agent's WebSearch tool restricted to ICAD hosts (protocol channel C5 route)",
        "C10": "General web search engine via the agent's WebSearch tool restricted to grey-literature hosts (protocol channel C10 route)",
    }[channel]
    return platform, interface, filters


BOUNDARY = {
    "A1": "Frozen C8 set under protocol v1 §5.2. Supplementary discovery only: titles and URLs, not a bibliographic database search; C8 cannot establish coverage.",
    "A2": "C9 known-item lookup for one entry of the Nees & Liebman reference list (RL-NL), quoted title phrase plus author. Tests findability, not topical recall.",
    "A4": "C9 known-item lookup for entry 69 of the accepted-manuscript list (RL-NLAM), missing from RL-NL. Run after the owner opened network access.",
    "A3-C5": "C5 route under the §5.3 fallback: frozen W string restricted to repository.gatech.edu and icad.org. Not a browse of the proceedings; no per-year coverage is implied.",
    "A3-C10G": "C10 technical-report route under the §5.3 fallback: frozen W string restricted to ROSA P, NASA NTRS and DTIC hosts. Engine-indexed pages only, not the repositories' own search.",
    "A3-C10T": "C10 thesis route under the §5.3 fallback: frozen W string restricted to OATD and three purposively chosen institutional repositories of auditory-display groups. Purposive, not a thesis database search.",
    "A3-OTHER": "Navigational lookup (ICAD proceedings archive or the process-industry review), not a topical search.",
}


def main() -> int:
    export_path = ROOT / EXPORT
    export = json.loads(export_path.read_text(encoding="utf-8"))
    digest = hashlib.sha256(export_path.read_bytes()).hexdigest()
    exp_ref = known({"path": EXPORT, "sha256": digest})

    # Existing source records: resolve occurrences only by identical identifier.
    by_url, by_doi = {}, {}
    for root in json.loads((ROOT / "research/registry/state.json").read_text(encoding="utf-8"))["record_roots"]:
        for f in (ROOT / root).rglob("SRC-*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))["revisions"][-1]["data"]
            for ident in data["identifiers"]:
                if ident["scheme"] == "url":
                    by_url[ident["value"].rstrip("/")] = f.stem
                elif ident["scheme"] == "doi":
                    by_doi[ident["value"].lower()] = f.stem
    explicit = {"https://railroads.dot.gov/sites/fra.dot.gov/files/2022-02/In-Vehicle%20Auditory%20Lit%20Review.pdf": (FRA, OPENED)}

    def resolve(url: str):
        if url in explicit:
            return explicit[url]
        if url.rstrip("/") in by_url:
            return by_url[url.rstrip("/")], SAME_URL
        flat = url.lower().replace("%2f", "/")
        for doi, rid in by_doi.items():
            if doi in flat:
                return rid, DOI_IN_URL
        return None

    out, run_ids = {}, []
    lists = {rl["label"]: rl for rl in export["reference_lists"]}
    nl_entries = {e["ordinal"]: e["text"] for e in lists["RL-NLAM"]["entries"]}
    resolved_count = 0
    for batch in export["batches"]:
        for run in batch["runs"]:
            label = run["label"]
            ch = run["channel"]
            run_id = "SRCH-R005-" + label.replace("-", "")
            run_ids.append(run_id)
            platform, interface, filters = channel_text(ch, run)
            if batch["batch"] == "A3":
                key = {"C5": "A3-C5", "C10": "A3-C10G" if label.startswith("G-") else "A3-C10T"}.get(ch, "A3-OTHER")
                if label in ("I-IDX", "R-PSLR"):
                    key = "A3-OTHER"
            else:
                key = batch["batch"]
            extra = ""
            if "language" in run:
                extra = f" Translation of W1 into {run['language']} produced at execution (not a frozen string)."
            if label == "A-W1X":
                extra = " W1 in extended mode."
            boundary = f"Run {label}, batch {batch['batch']}. {BOUNDARY[key]}{extra} Started/finished are the call's log time and the batch's closing shell reading."
            basis = [ref(NL)] if ch == "C9" and "known_item" in run else []
            out[f"{SEARCH_DIR}/{run_id}.json"] = record(run_id, "search_run", {
                "lane": "auditory", "protocol_version": "v1", "mode": "production", "status": "partial",
                "platform": platform, "interface": interface, "query": run["query"], "filters": filters,
                "coverage": {"start": missing("unknown", "The engine does not state its index coverage"),
                             "end": missing("unknown", "The engine does not state its index coverage")},
                "started_at": known(run["called_at"]), "finished_at": known(batch["window_end"]),
                "reported_count": missing("not_reported", "The engine reports no total hit count"),
                "retrieved_count": len(run["results"]), "export": exp_ref,
                "pagination": {"complete": False, "detail": "One page of top results only; the tool exposes no further pages."},
                "failures": [], "boundary": boundary,
            }, basis)
            kinfo = KNOWN.get(run.get("known_item"))
            for result in run["results"]:
                n = result["ordinal"]
                hid = f"HIT-R005-{label.replace('-', '')}-{n:02d}"
                data = {"search_ref": ref(run_id), "ordinal": n,
                        "raw_metadata": f"{result['title']} | {result['url']}",
                        "returned_identifiers": [{"scheme": "url", "value": result["url"]}]}
                hbasis = [ref(run_id)]
                hit = resolve(result["url"])
                if hit:
                    data.update(status="resolved", resolution_reason=hit[1], source_ref=ref(hit[0]))
                    hbasis.append(ref(hit[0]))
                    resolved_count += 1
                elif kinfo and n in kinfo[1]:
                    word = "matches" if kinfo[0] == "located" else "may correspond to"
                    data.update(status="unresolved", resolution_reason=(
                        f"Title-level check: {word} {'RL-NLAM' if run['known_item'] == 69 else 'RL-NL'} entry {run['known_item']} ({kinfo[0]}). "
                        "Publication identity not verified; canonical source record left to #6."))
                else:
                    data.update(status="unresolved", resolution_reason="Publication identity not checked for this occurrence.")
                out[f"{SEARCH_DIR}/hits/{hid}.json"] = record(hid, "search_hit", data, hbasis)

    # Reference lists read for backward chaining (C9).
    times = {"RL-NL": ("2026-10-13T00:59:21Z", "2026-10-13T00:59:54Z"),
             "RL-FRA": ("2026-10-13T02:13:37Z", "2026-10-13T02:15:21Z"),
             "RL-NLAM": ("2026-10-13T06:19:08Z", "2026-10-13T06:19:35Z"),
             "RL-FRAPDF": ("2026-10-13T06:19:08Z", "2026-10-13T06:19:35Z")}
    for rl in export["reference_lists"]:
        label = rl["label"]
        run_id = "SRCH-R005-" + label.replace("-", "")
        run_ids.append(run_id)
        start, end = times[label]
        hashed = "manifestation" in rl
        if hashed:
            mf = rl["manifestation"]
            platform = f"Reference list of {rl['review']}, parsed from the downloaded file (protocol channel C9, backward chaining)"
            interface = f"Direct HTTPS download from {rl['url']} (SHA-256 {mf['sha256']}, {mf['bytes']} bytes) and pdftotext text extraction"
            status, complete, failures = "completed", True, []
            boundary = (f"C9 backward chaining from {rl['source_record']}. {rl['method']} {mf['integrity']}. Licence: {mf['licence']}. "
                        f"Bytes retained: {mf['retained']}. Entry text is parsed PDF text and may carry extraction artefacts (hyphenation, ligatures).")
        else:
            platform = f"Reference list of {rl['review']}, read through the agent's WebFetch tool (protocol channel C9, backward chaining)"
            interface = "WebFetch tool: an unidentified intermediary model renders the page; no bytes are returned"
            status, complete = "partial", label == "RL-FRA"
            failures = [] if label == "RL-FRA" else ["Final entry truncated in the tool output; the last 2,096 page characters were not read."]
            boundary = (f"C9 backward chaining from {rl['source_record']}. {rl['method']} Entries are tool-rendered and abbreviated; "
                        "status is partial because only opening title words were captured.")
        out[f"{SEARCH_DIR}/{run_id}.json"] = record(run_id, "search_run", {
            "lane": "auditory", "protocol_version": "v1", "mode": "production", "status": status,
            "platform": platform, "interface": interface,
            "query": f"Every entry of the '{rl['section']}' section",
            "filters": ["None: every entry requested"],
            "coverage": {"start": missing("not_applicable", "A reference list has no search date window"),
                         "end": missing("not_applicable", "A reference list has no search date window")},
            "started_at": known(start), "finished_at": known(end),
            "reported_count": missing("not_reported", "The list prints no entry count"),
            "retrieved_count": len(rl["entries"]), "export": exp_ref,
            "pagination": {"complete": complete, "detail": rl["completeness"]},
            "failures": failures, "boundary": boundary,
        }, [ref(rl["source_record"])])
        width = 3
        for e in rl["entries"]:
            n = e["ordinal"]
            hid = f"HIT-R005-{label.replace('-', '')}-{n:0{width}d}"
            idents, seen_ids = [], set()
            for doi in re.findall(r"(?:doi:|doi\.org/)(10\.\d{4,9}/[^\s;]+)", e["text"]):
                doi = doi.rstrip(".,)")
                if doi.lower() not in seen_ids:
                    seen_ids.add(doi.lower())
                    idents.append({"scheme": "doi", "value": doi})
            for handle in re.findall(r"(?:smartech |handle/)(1853/\d+)", e["text"]):
                if handle not in seen_ids:
                    seen_ids.add(handle)
                    idents.append({"scheme": "other", "value": "SMARTech handle " + handle})
            raw = e["text"] if "outcome_letters" not in e else f"[{e['outcome_letters']}] {e['text']}"
            hit_data = {"search_ref": ref(run_id), "ordinal": n, "raw_metadata": raw,
                        "returned_identifiers": idents, "status": "unresolved",
                        "resolution_reason": ("Reference-list entry parsed from the hashed file; not matched to a source record (left to #6)." if hashed
                                              else "Reference-list entry as rendered by the fetch tool; not matched to a source record (left to #6).")}
            hbasis = [ref(run_id)]
            for ident in idents:
                if ident["scheme"] == "doi" and ident["value"].lower() in by_doi:
                    hit_data.update(status="resolved", source_ref=ref(by_doi[ident["value"].lower()]),
                                    resolution_reason="The entry's DOI equals the DOI on this source record.")
                    hbasis.append(ref(by_doi[ident["value"].lower()]))
                    resolved_count += 1
                    break
            out[f"{SEARCH_DIR}/hits/{hid}.json"] = record(hid, "search_hit", hit_data, hbasis)

    # C5: ICAD year listings captured after the network change.
    listing_path = ROOT / ICAD_LISTING
    listing = json.loads(listing_path.read_text(encoding="utf-8"))
    listing_ref = known({"path": ICAD_LISTING, "sha256": hashlib.sha256(listing_path.read_bytes()).hexdigest()})
    files = [(y["year"], name, y["url"]) for y in listing["years_listed"] for name in y["pdf_files"]]
    run_ids.append("SRCH-R005-C5LIST")
    out[f"{SEARCH_DIR}/SRCH-R005-C5LIST.json"] = record("SRCH-R005-C5LIST", "search_run", {
        "lane": "auditory", "protocol_version": "v1", "mode": "production", "status": "partial",
        "platform": "ICAD proceedings directory listings on www.icad.org (protocol channel C5 browse)",
        "interface": "Apache directory index pages fetched with curl from the workspace shell; raw pages retained under exports/icad-listing/",
        "query": "Every PDF file listed for each year directory under https://www.icad.org/Proceedings/",
        "filters": ["None"],
        "coverage": {"start": known("1994"), "end": known("2010")},
        "started_at": known(listing["captured"]["start"]), "finished_at": known(listing["captured"]["end"]),
        "reported_count": missing("not_reported", "Directory pages print no totals"),
        "retrieved_count": len(files), "export": listing_ref,
        "pagination": {"complete": False, "detail": "Every listed year directory was read in full, but no listing exists for 1992 or 2011 onward on this host."},
        "failures": [listing["not_listed"]],
        "boundary": ("C5 year-by-year browse. File names identify author surnames and year only; titles need the paper or another channel. "
                     "Per-year coverage: " + "; ".join(f"{y['year']}: {len(y['pdf_files'])} files" for y in listing["years_listed"]) + "."),
    }, [])
    for n, (year, name, base) in enumerate(files, 1):
        hid = f"HIT-R005-C5LIST-{n:04d}"
        out[f"{SEARCH_DIR}/hits/{hid}.json"] = record(hid, "search_hit", {
            "search_ref": ref("SRCH-R005-C5LIST"), "ordinal": n,
            "raw_metadata": f"ICAD {year} proceedings file {name} | {base}{name}",
            "returned_identifiers": [{"scheme": "url", "value": base + name}],
            "status": "unresolved", "resolution_reason": "Listing entry (file name only); publication identity not checked.",
        }, [ref("SRCH-R005-C5LIST")])

    # C1: OpenAlex EQ1-EQ8, when the harvest manifest exists.
    manifest_path = ROOT / OPENALEX_MANIFEST
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_ref = known({"path": OPENALEX_MANIFEST, "sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest()})
        for label, run in sorted(manifest["runs"].items(), key=lambda kv: int(kv[0][2:])):
            rid = f"SRCH-R005-C1{label}"
            run_ids.append(rid)
            works = []
            for page in run["pages"]:
                if page.get("file"):
                    page_bytes = (ROOT / page["file"]).read_bytes()
                    assert hashlib.sha256(page_bytes).hexdigest() == page["sha256"], page["file"]
                    works.extend(json.loads(page_bytes)["results"])
            status = "completed" if run["complete"] else ("failed" if not works else "partial")
            out[f"{SEARCH_DIR}/{rid}.json"] = record(rid, "search_run", {
                "lane": "auditory", "protocol_version": "v1", "mode": "production", "status": status,
                "platform": "OpenAlex works API (protocol channel C1)",
                "interface": (f"HTTPS API from the workspace shell via research/sources/auditory/scripts/openalex_harvest.py; cursor paging, "
                              f"per-page {run['per_page']}, select={run['select']}; key attached outside the session by the environment's network secret"),
                "query": run["filter"],
                "filters": ["title_and_abstract.search field scope", "to_publication_date:2026-10-04", "No language, type or open-access filter"],
                "coverage": {"start": missing("not_applicable", "No lower date bound (protocol E6)"), "end": known("2026-10-04")},
                "started_at": known(run["started_at"]), "finished_at": known(run["finished_at"]),
                "reported_count": known(run["reported_count"]) if run.get("reported_count") is not None else missing("not_reported", "No first page"),
                "retrieved_count": len(works), "export": manifest_ref,
                "pagination": {"complete": run["complete"], "detail": f"{len(run['pages'])} page(s); per-page hashes in the manifest."},
                "failures": run["failures"],
                "boundary": f"Protocol v1 query family {label} executed on C1 as specified in §5.2 (concept blocks read from the frozen protocol file).",
            }, [ref("HG-R002-DATABASE-ACCESS")], "source_reported")
            for n, work in enumerate(works, 1):
                hid = f"HIT-R005-C1{label}-{n:05d}"
                doi = (work.get("doi") or "").replace("https://doi.org/", "")
                idents = [{"scheme": "url", "value": work["id"]}]
                if doi:
                    idents.insert(0, {"scheme": "doi", "value": doi})
                venue = ((work.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
                first = (work.get("authorships") or [{}])[0].get("author", {}).get("display_name", "") if work.get("authorships") else ""
                raw = f"{work.get('display_name') or '[no title]'} | {first} | {work.get('publication_year')} | {venue} | {work.get('type')} | {work['id']}"
                hit_data = {"search_ref": ref(rid), "ordinal": n, "raw_metadata": raw, "returned_identifiers": idents,
                            "status": "unresolved", "resolution_reason": "OpenAlex work record; deduplication and identity left to #6."}
                hbasis = [ref(rid)]
                if doi and doi.lower() in by_doi:
                    hit_data.update(status="resolved", source_ref=ref(by_doi[doi.lower()]),
                                    resolution_reason="The work's DOI equals the DOI on this source record.")
                    hbasis.append(ref(by_doi[doi.lower()]))
                    resolved_count += 1
                out[f"{SEARCH_DIR}/hits/{hid}.json"] = record(hid, "search_hit", hit_data, hbasis)

    # Channels that could not run, or ran only as probes.
    c1_failures = ["Owner's desktop built-in browser: blocked by the owner's site permissions (02:05:11Z and 06:13Z; an access request for the site was refused)",
                   "Workspace shell: session proxy refused the host, HTTP status 000 (02:05:17Z and 02:16:02Z)",
                   "Workspace shell after the owner opened network access: HTTP 429, free key-less budget for the shared IP used up (06:12:19Z to 06:28:27Z)"]
    gated = [
        ("SRCH-R005-C1", "failed", "OpenAlex works API (protocol channel C1): availability probes", "HTTPS API",
         "Probes only, not EQ1-EQ8: https://api.openalex.org/works?search=earcon (variants with per_page/per-page=1, select=id, title_and_abstract.search:earcon)",
         ("2026-10-13T02:05:11Z", "2026-10-13T06:28:27Z"), c1_failures),
        ("SRCH-R005-C2", "planned", "Crossref REST API (protocol channel C2)", "HTTPS API",
         "Not used for EQ1-EQ8; reserved for DOI resolution in #6", None,
         ["Refused by the session proxy at 02:16:02Z (CONNECT 403); reachable from 06:12:19Z",
          "The API's free-text query cannot express the protocol's AND between concept blocks: query=earcon returned 11 records and query=earcon+experiment 273,635 (06:20Z), so terms are matched with OR relevance ranking"]),
        ("SRCH-R005-C3", "planned", "ACM Digital Library, Guide to Computing Literature (protocol channel C3)", "Owner-run web interface export",
         "EQ1-EQ8 translated to ACM DL syntax (not yet run)", None,
         ["Not attempted by the agent: the channel is owner-run export only (protocol §5.1); no export supplied"]),
        ("SRCH-R005-C4", "planned", "IEEE Xplore (protocol channel C4)", "Owner-run web interface export",
         "EQ1-EQ8 translated to IEEE Xplore syntax (not yet run)", None,
         ["Not attempted by the agent: owner-run export only; no export supplied"]),
        ("SRCH-R005-C6", "planned", "SAGE Human Factors/HFES and Taylor & Francis (Ergonomics) platforms (protocol channel C6)", "Publisher search interfaces",
         "EQ1-EQ8 translated to each platform (not yet run)", None,
         ["Not attempted: publisher search interfaces are not automated by the agent (protocol §5.1); pages surfaced through C8 are not a C6 search"]),
        ("SRCH-R005-C7", "planned", "PsycINFO, Web of Science and Scopus (protocol channel C7)", "Subscription databases",
         "EQ1-EQ8 translated to each database (not yet run)", None,
         ["Not accessible: subscription required; no owner exports supplied"]),
        ("SRCH-R005-C5BROWSE", "failed", "ICAD archive routes that returned no usable listing (protocol channel C5 browse)", "WebFetch tool, then workspace shell",
         "Year-by-year proceedings listing 1992-2026",
         ("2026-10-13T02:12:36Z", "2026-10-13T06:18:41Z"),
         ["icad.org/proceedings lists no years; it says all past proceedings are in the Georgia Tech SMARTech repository (ledger row 4)",
          "dblp ICAD index and dblp search API: bot-protection challenge, not bypassed (ledger rows 5, 18)",
          "Georgia Tech repository REST API: HTTP 400 for discovery searches and HTTP 500 for item and relationship requests; OAI-PMH ListRecords HTTP 500, GetRecord connection reset (ledger rows 19-20)"]),
        ("SRCH-R005-RLPSLR", "failed", "Reference list of 'Design Considerations for Auditory Alarms in the Process Industry: A Systematic Literature Review' (protocol channel C9)", "WebFetch tool",
         "Every entry of the review's reference list",
         ("2026-10-13T02:15:11Z", "2026-10-13T02:15:21Z"),
         ["The USN open archive record now shows only a notice that the archive moved to NVA (ledger row 8); lookup R-PSLR surfaced no other copy"]),
    ]
    if manifest_path.exists():
        gated = [g for g in gated if g[0] != "SRCH-R005-C1"] + [
            ("SRCH-R005-C1", "failed", "OpenAlex works API (protocol channel C1): availability probes before the key was available", "HTTPS API",
             "Probes only: https://api.openalex.org/works?search=earcon (variants with per_page/per-page=1, select=id, title_and_abstract.search:earcon)",
             ("2026-10-13T02:05:11Z", "2026-10-13T06:28:27Z"), c1_failures)]
    for rid, status, platform, interface, query, window, failures in gated:
        run_ids.append(rid)
        db = rid[-2:] in ("C1", "C2", "C3", "C4", "C6", "C7")
        out[f"{SEARCH_DIR}/{rid}.json"] = record(rid, "search_run", {
            "lane": "auditory", "protocol_version": "v1", "mode": "production", "status": status,
            "platform": platform, "interface": interface, "query": query,
            "filters": ["Protocol §5.2 field scope and date limit <= 2026-10-04 would apply"] if db else ["None"],
            "coverage": {"start": missing("not_applicable", "No search executed"), "end": missing("not_applicable", "No search executed")},
            "started_at": known(window[0]) if window else missing("not_applicable", "Not started"),
            "finished_at": known(window[1]) if window else missing("not_applicable", "Not started"),
            "reported_count": missing("not_applicable", "No search executed"),
            "retrieved_count": 0,
            "export": missing("not_applicable", "Nothing retrieved"),
            "pagination": {"complete": False, "detail": "No results were obtained."},
            "failures": failures,
            "boundary": ("Access gap or probe record, not an eligibility decision; see the R005 coverage memo for its impact."
                         + (" Gate: HG-R002-DATABASE-ACCESS." if db else "")),
        }, [ref("HG-R002-DATABASE-ACCESS")] if db else [], "source_reported")

    # Known-item check table (derived artifact for #6).
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["entry", "rl_nlam_text", "known_item_run", "outcome", "matching_ordinals", "also_in_topic_runs", "note"])
    for n in range(1, 70):
        outcome, ords, note, also = KNOWN[n]
        w.writerow([n, nl_entries[n], f"K{n:02d}", outcome, " ".join(map(str, ords)), " ".join(also), note])
    (ROOT / KNOWN_CSV).write_text(buf.getvalue(), encoding="utf-8")

    counts = {o: sum(1 for v in KNOWN.values() if v[0] == o) for o in ("located", "possible", "not_located")}
    topic_any = sum(1 for v in KNOWN.values() if v[3])
    artifacts = [EXPORT, ICAD_LISTING, LEDGER, KNOWN_CSV, MEMO] + ([OPENALEX_MANIFEST] if manifest_path.exists() else [])
    out[f"{SOURCE_DIR}/AID-R005-AUDITORY-SEARCH.json"] = record("AID-R005-AUDITORY-SEARCH", "assistance", {
        "subtype": "assistance",
        "task": ("Execute the Track E search under protocol v1: re-check database access, run the §5.3 fallback channels (C8, C5 and C10 routes, "
                 "C9 backward chaining with known-item lookups), then, after the owner opened network access, re-derive the review lists from hashed files, "
                 "list ICAD proceedings by year and run EQ1-EQ8 on OpenAlex where reachable; record every channel's outcome."),
        "input_refs": [ref(NL), ref(FRA), ref("HG-R002-DATABASE-ACCESS")],
        "output_refs": [ref(i) for i in run_ids],
        "artifacts": artifacts,
        "verification_steps": [
            "Titles, URLs and reference entries copied programmatically from the session tool-call log; four earlier hand transcriptions (K01-K24) compared with the log and found identical.",
            "Tool-rendered reference lists checked against lists parsed from hashed files: RL-NL entries 1-68 match RL-NLAM on first author, year and outcome letters; all 115 RL-FRA entries match RL-FRAPDF.",
            "The accepted manuscript's SHA-256 equals the value published by the OSF API; OpenAlex page hashes are re-verified by this script before records are written.",
            f"Known-item outcomes adjudicated by the agent from result titles and URL identifiers: {counts['located']} located, {counts['possible']} possible, {counts['not_located']} not located of 69; {topic_any} entries also surfaced in topic runs.",
            f"{resolved_count} occurrences resolved to existing source records by identical URL, DOI or an opened page.",
        ],
        "limitations": ("Single agent; no citation index or librarian; web results unpaginated and possibly personalised; tool-rendered lists are paraphrase; "
                        "downloaded files are not committed; no study full text was retrieved for screening or extraction."),
        "status": "performed", "performed_at": known(AT),
        "independence": "Single executing agent. Not a human check and not independent of the work it describes.",
    }, [ref(NL), ref(FRA), ref("HG-R002-DATABASE-ACCESS")], "researcher_interpretation")

    for path, row in sorted(out.items()):
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(dumps(row), encoding="utf-8")
    print(f"wrote {len(out)} records; resolved {resolved_count}; known-item {counts}; topic {topic_any}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
