"""Count each frozen family without harvesting it; preserves all response bytes."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location("harvester", ROOT / "research/sources/auditory/scripts/openalex_harvest.py")
harvester = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harvester)
manifest = {"purpose": "Count and basic-page feasibility probes only; not complete production searches", "actor": "ChatGPT GPT-6 Astra Pro database-channel subagent", "credential_use": "none", "probes": []}
families = harvester.query_families()
requests = [(label, query, 1) for label, query in families.items()]
requests.append(("EQ4_PAGE2", families["EQ4"], 2))
for label, query, page in requests:
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode({"filter": "title_and_abstract.search:" + query + ",to_publication_date:2026-10-04", "per_page": 1, "select": "id,doi,display_name", "page": page})
    entry = {"label": label, "query": query, "page": page, "url": url, "requested_at": datetime.now(timezone.utc).isoformat()}
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
    path = HERE / (label.lower() + "-probe.json")
    path.write_bytes(body)
    entry.update(http_status=status, file=path.name, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), headers={k: v for k, v in headers.items() if k.lower() in {"content-type", "x-ratelimit-limit", "x-ratelimit-remaining", "retry-after"}})
    if status == 200:
        data = json.loads(body)
        meta = data.get("meta", {})
        entry["summary"] = {k: meta.get(k) for k in ["count", "page", "per_page", "cost_usd"]}
    else:
        entry["response_excerpt"] = body[:600].decode("utf-8", "replace")
    manifest["probes"].append(entry)
    (HERE / "count-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(label, status, entry.get("summary"), flush=True)
    if status == 429:
        break
    time.sleep(1.1)
