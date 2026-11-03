#!/usr/bin/env python3
"""Retain review source bytes outside Git and their public-access provenance."""
import hashlib
import json
import pathlib
import sys
import urllib.error
import urllib.request
import urllib.parse
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
TEMP = pathlib.Path("/tmp/mhac-r005-reviews")

def public_url(url):
    """Do not commit temporary signed-download credentials from redirects."""
    parts = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    signed = any(key.lower().startswith("x-amz-") or key.lower() in
                 {"signature", "token", "awsaccesskeyid"} for key, _ in query)
    return (urllib.parse.urlunsplit(parts._replace(query="")), True) if signed else (url, False)

def fetch(name, url, accept=None):
    if pathlib.Path(name).name != name:
        raise ValueError("basename required")
    target = TEMP / name
    if target.exists():
        raise FileExistsError(f"retained source already exists: {target}")
    start = datetime.now(timezone.utc).isoformat()
    record = {"name": name, "requested_url": url, "started_at": start,
              "actor": "ChatGPT GPT-6 Astra Pro C9 retrieval subagent", "method": "GET"}
    headers = {"User-Agent": "MHAC-R005-literature-retrieval/1.0"}
    if accept:
        headers["Accept"] = accept
        record["accept"] = accept
    request = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=30)
    except urllib.error.HTTPError as exc:
        response = exc
    except Exception as exc:
        record.update(status=None, error=f"{type(exc).__name__}: {exc}")
        response = None
    if response is not None:
        body = response.read()
        TEMP.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        final_url, redacted = public_url(response.url)
        record.update(status=response.code, final_url=final_url,
                      signed_redirect_query_omitted=redacted,
                      content_type=response.headers.get("Content-Type"),
                      bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                      source_file_local=str(target), redistributable_copy_committed=False)
    record["finished_at"] = datetime.now(timezone.utc).isoformat()
    with (HERE / "access.jsonl").open("a") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps(record, ensure_ascii=False), flush=True)
    return record

if __name__ == "__main__":
    fetch(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
