"""Run protocol v1 query families EQ1-EQ8 on OpenAlex (channel C1) and keep every page.

Run from the repository root:

    python3 research/sources/auditory/scripts/openalex_harvest.py [EQ1 EQ2 ...]

The concept blocks are read from the frozen protocol file, joined into one line exactly as in
the database gate's reference URLs, and sent as `title_and_abstract.search` with the protocol's
`to_publication_date:2026-10-04` limit. Pages are fetched with `cursor` paging until OpenAlex
returns no next cursor, and each page's bytes are written unchanged, with its URL, HTTP status,
time and SHA-256 in `MANIFEST.json`.

The script holds no credential. When the cloud environment has an OpenAlex network secret,
Anthropic's agent proxy adds it to the request outside this session. Abstracts are not
requested, so no abstract text is stored in the repository.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROTOCOL = ROOT / "research/protocol/PROTOCOL-v1.md"
OUT = ROOT / "research/searches/auditory/exports/openalex"
BASE = "https://api.openalex.org/works"
SELECT = ("id,doi,display_name,publication_year,publication_date,type,language,"
          "primary_location,authorships,biblio,ids")
PER_PAGE = 200
DATE_LIMIT = "to_publication_date:2026-10-04"
USER_AGENT = "MHAC-R005 research search (techrote/MachineHumanAudioCybersemiotics)"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def query_families() -> dict[str, str]:
    """EQ label -> one-line boolean string, from the frozen protocol code block."""
    text = PROTOCOL.read_text(encoding="utf-8")
    block = text.split("EQ1 broad recall", 1)[1]
    block = "EQ1 broad recall" + block.split("```", 1)[0]
    families: dict[str, str] = {}
    for chunk in re.split(r"\n\s*\n", block.strip()):
        lines = chunk.strip().splitlines()
        label = lines[0].split()[0]
        families[label] = " ".join(line.strip() for line in lines[1:])
    assert list(families) == [f"EQ{i}" for i in range(1, 9)], list(families)
    return families


def page_url(query: str, cursor: str) -> str:
    flt = f"title_and_abstract.search:{query},{DATE_LIMIT}"
    params = [("filter", flt), ("per-page", str(PER_PAGE)), ("select", SELECT), ("cursor", cursor)]
    return BASE + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote, safe=":,*")


def fetch(url: str) -> tuple[int, bytes, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers)


def harvest(label: str, query: str) -> dict:
    folder = OUT / label
    folder.mkdir(parents=True, exist_ok=True)
    record = {"label": label, "query": query, "filter": f"title_and_abstract.search:{query},{DATE_LIMIT}",
              "per_page": PER_PAGE, "select": SELECT, "started_at": now(), "pages": [], "failures": []}
    cursor, n = "*", 0
    while cursor:
        n += 1
        url = page_url(query, cursor)
        fetched_at = now()
        status, body, headers = fetch(url)
        entry = {"page": n, "url": url, "fetched_at": fetched_at, "http_status": status,
                 "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                 "ratelimit_remaining": headers.get("x-ratelimit-remaining") or headers.get("X-RateLimit-Remaining")}
        if status != 200:
            entry["error_body"] = body[:600].decode("utf-8", "replace")
            record["pages"].append(entry)
            record["failures"].append(f"page {n}: HTTP {status}")
            break
        path = folder / f"p{n:04d}.json"
        path.write_bytes(body)
        entry["file"] = str(path.relative_to(ROOT))
        data = json.loads(body)
        meta = data.get("meta", {})
        entry["results"] = len(data.get("results", []))
        if n == 1:
            record["reported_count"] = meta.get("count")
        record["pages"].append(entry)
        cursor = meta.get("next_cursor")
        if entry["results"] == 0:
            cursor = None
        time.sleep(0.25)
    record["finished_at"] = now()
    record["retrieved"] = sum(p.get("results", 0) for p in record["pages"])
    record["complete"] = not record["failures"] and record.get("reported_count") == record["retrieved"]
    return record


def main(argv: list[str]) -> int:
    families = query_families()
    wanted = argv or list(families)
    manifest_path = OUT / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {
        "schema": "mhac-r005-openalex-harvest/1", "protocol": "research/protocol/PROTOCOL-v1.md",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(), "runs": {}}
    for label in wanted:
        result = harvest(label, families[label])
        manifest["runs"][label] = result
        manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(label, result.get("reported_count"), result["retrieved"], "complete" if result["complete"] else result["failures"])
        if result["failures"] and any("HTTP 429" in f for f in result["failures"]):
            print("rate limited; stopping")
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
