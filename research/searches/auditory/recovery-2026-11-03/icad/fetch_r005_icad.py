#!/usr/bin/env python3
"""Capture public ICAD listing responses and an append-only access log."""
import hashlib
import json
import pathlib
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent

def fetch(name, url):
    if pathlib.Path(name).name != name:
        raise ValueError("output name must be a basename")
    target = HERE / "raw" / name
    if target.exists():
        raise FileExistsError(f"refusing to overwrite retained response: {target}")
    start = datetime.now(timezone.utc).isoformat()
    rec = {"name": name, "url": url, "started_at": start,
           "method": "GET", "actor": "ChatGPT GPT-6 Astra Pro ICAD subagent"}
    request = urllib.request.Request(url, headers={"User-Agent": "MHAC-R005-literature-index-retrieval/1.0", "Accept": "text/html,application/json,application/xml;q=0.9,*/*;q=0.5"})
    try:
        response = urllib.request.urlopen(request, timeout=25)
    except urllib.error.HTTPError as exc:
        response = exc
    except Exception as exc:
        rec.update({"status": None, "error": f"{type(exc).__name__}: {exc}"})
        response = None
    if response is not None:
        body = response.read()
        rec.update({"status": response.code, "final_url": response.url,
                    "content_type": response.headers.get("Content-Type"),
                    "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                    "file": f"raw/{name}"})
        target.write_bytes(body)
    rec["finished_at"] = datetime.now(timezone.utc).isoformat()
    with (HERE / "access.jsonl").open("a") as file:
        file.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(json.dumps(rec, ensure_ascii=False))
    return rec

if __name__ == "__main__":
    fetch(sys.argv[1], sys.argv[2])
