"""Run MHAC-R004 bibliographic identity lookups and keep every response unchanged.

    python3 research/sources/related/scripts/lookup_r004.py            # first round
    python3 research/sources/related/scripts/lookup_r004.py --round2   # field-scoped second round
    python3 research/sources/related/scripts/lookup_r004.py --round3   # counter-position items (Crossref, arXiv API)
    python3 research/sources/related/scripts/lookup_r004.py --round4   # second negative-case batch
    python3 research/sources/related/scripts/lookup_r004.py --abstracts

Crossref REST API (CC0 metadata) for items likely to carry DOIs; Open Library search API (CC0)
for books. Each response is written byte-for-byte with its URL, time, status and SHA-256 in
MANIFEST.json. Lookups establish candidate identity only; they read no source text.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from candidates_r004 import ABSTRACT_DOIS, CANDIDATES, ROUND2, ROUND3, ROUND4  # noqa: E402

OUT = ROOT / "research/searches/related/exports/lookups"
UA = "MHAC-R004 bibliographic identity check (techrote/MachineHumanAudioCybersemiotics)"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def url_for(route: str, query: str) -> str:
    q = urllib.parse.quote(query)
    if route == "crossref":
        return ("https://api.crossref.org/works?rows=3&query.bibliographic=" + q +
                "&select=DOI,title,author,issued,container-title,type,publisher,ISBN,page,volume,issue,editor")
    if route == "openlibrary":
        return ("https://openlibrary.org/search.json?limit=5&q=" + q +
                "&fields=key,title,author_name,first_publish_year,publisher,isbn,edition_count,language")
    if route == "openlibrary-ta":
        title, author = query.split("|")
        return ("https://openlibrary.org/search.json?limit=5&title=" + urllib.parse.quote(title) + "&author=" +
                urllib.parse.quote(author) + "&fields=key,title,author_name,first_publish_year,publisher,isbn,edition_count,language")
    if route == "crossref-doi":
        return ("https://api.crossref.org/works?rows=3&filter=doi:" + query +
                "&select=DOI,title,author,issued,container-title,type,publisher,ISBN,page,volume,issue,editor")
    if route == "arxiv":
        return "https://export.arxiv.org/api/query?id_list=" + q
    raise ValueError(route)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "MANIFEST.json"
    retry = "--retry-failed" in sys.argv
    manifest = (json.loads(manifest_path.read_text(encoding="utf-8")) if retry and manifest_path.exists()
                else {"schema": "mhac-r004-lookups/1", "lookups": {}})
    if "--abstracts" in sys.argv:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.setdefault("work_records", {})
        for key, doi in ABSTRACT_DOIS.items():
            url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
            at = now()
            if manifest["work_records"].get(key, {}).get("http_status") == 200:
                continue
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            status, body = None, b""
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(req, timeout=60) as r:
                        status, body = r.status, r.read()
                    break
                except urllib.error.HTTPError as e:
                    status, body = e.code, e.read()
                    break
                except (urllib.error.URLError, ConnectionError, TimeoutError):
                    time.sleep(5 * (attempt + 1))
            if status is None:
                print(key, "network-error")
                continue
            path = OUT / f"{key}.work.json"
            path.write_bytes(body)
            manifest["work_records"][key] = {"doi": doi, "url": url, "at": at, "http_status": status, "file": str(path.relative_to(ROOT)),
                                             "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}
            print(key, status, len(body))
            manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            time.sleep(1.5)
        manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        return 0
    rounds = {"--round2": ("round2", "r2", ROUND2), "--round3": ("round3", "r3", ROUND3), "--round4": ("round4", "r4", ROUND4)}
    chosen = [rounds[a] for a in sys.argv[1:] if a in rounds]
    round2 = bool(chosen)
    section, suffix, table = chosen[0] if chosen else rounds["--round2"]
    if round2:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.setdefault(section, {})
    items = ([(k, (None, None, r, q, None)) for k, (r, q) in table.items()] if round2 else CANDIDATES.items())
    for key, (cluster, tier, route, query, why) in items:
        if round2:
            url = url_for(route, query)
            at = now()
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    status, body = r.status, r.read()
            except urllib.error.HTTPError as e:
                status, body = e.code, e.read()
            path = OUT / f"{key}.{route}.{suffix}.{'xml' if route == 'arxiv' else 'json'}"
            path.write_bytes(body)
            manifest[section][key] = {"route": route, "query": query, "url": url, "at": at, "http_status": status,
                                       "file": str(path.relative_to(ROOT)), "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}
            print(key, status, len(body))
            time.sleep(3.0)
            continue
        if route == "web":
            continue
        previous = manifest["lookups"].get(key)
        if retry and previous and previous.get("http_status") == 200:
            continue
        if previous and previous.get("http_status") not in (200, None):
            manifest["lookups"].setdefault("_superseded", []).append({key: previous})
        url = url_for(route, query)
        at = now()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        status, body, errors = None, b"", []
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    status, body = r.status, r.read()
                break
            except urllib.error.HTTPError as e:
                status, body = e.code, e.read()
                break
            except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
                errors.append(f"attempt {attempt + 1}: {e}")
                time.sleep(3 * (attempt + 1))
        if status is None:
            manifest["lookups"][key] = {"route": route, "query": query, "url": url, "at": at, "http_status": None, "errors": errors}
            print(key, "network-error")
            continue
        path = OUT / f"{key}.{route}.json"
        path.write_bytes(body)
        manifest["lookups"][key] = {"route": route, "query": query, "url": url, "at": at, "http_status": status,
                                    "file": str(path.relative_to(ROOT)), "bytes": len(body),
                                    "sha256": hashlib.sha256(body).hexdigest(), "errors": errors}
        print(key, status, len(body))
        time.sleep(2.0 if retry else 0.4)
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
