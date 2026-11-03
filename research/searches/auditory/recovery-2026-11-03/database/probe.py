"""Bounded unauthenticated availability probes; not production searches."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location("harvester", ROOT / "research/sources/auditory/scripts/openalex_harvest.py")
harvester = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harvester)

eq4 = harvester.query_families()["EQ4"]
requests = [
    ("openalex_eq4_first", "https://api.openalex.org/works?" + urllib.parse.urlencode({"filter": "title_and_abstract.search:" + eq4 + ",to_publication_date:2026-10-04", "per_page": 1, "select": "id,doi,display_name", "cursor": "*"})),
    ("crossref_metadata", "https://api.crossref.org/works?" + urllib.parse.urlencode({"query.bibliographic": '"auditory icons"', "rows": 1, "select": "DOI,title,type,published"})),
]
manifest = {"purpose": "Availability and syntax probes only; no production search completion asserted", "actor": "ChatGPT GPT-6 Astra Pro database-channel subagent", "credential_use": "none", "probes": []}
for label, url in requests:
    entry = {"label": label, "url": url, "requested_at": datetime.now(timezone.utc).isoformat()}
    req = urllib.request.Request(url, headers={"User-Agent": "MHAC-R005 availability audit (techrote/MachineHumanAudioCybersemiotics)", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status, body, headers = response.status, response.read(), response.headers
    except urllib.error.HTTPError as error:
        status, body, headers = error.code, error.read(), error.headers
    except (OSError, urllib.error.URLError) as error:
        entry["transport_error"] = str(error)
        manifest["probes"].append(entry)
        continue
    path = HERE / (label + ".json")
    path.write_bytes(body)
    entry.update(http_status=status, file=path.name, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), headers={k: v for k, v in headers.items() if k.lower() in {"content-type", "x-ratelimit-limit", "x-ratelimit-remaining", "retry-after"}})
    if status == 200:
        data = json.loads(body)
        entry["summary"] = data.get("meta", {"total_results": data.get("message", {}).get("total-results")})
    else:
        entry["response_excerpt"] = body[:600].decode("utf-8", "replace")
    manifest["probes"].append(entry)
(HERE / "probe-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
print(json.dumps(manifest, indent=2, ensure_ascii=False))
