"""Harvest frozen EQ families using documented keyless basic pagination.

Each invocation uses a new run directory. Public pages are metadata derivatives
with abstract_inverted_index removed. Original bytes are hashed and cached only
outside the repository. No credentials are read or sent. Size 200 is the frozen
protocol's still-accepted legacy size; --per-page 100 selects the supported max.
Incomplete, drifting or duplicate-bearing runs fail closed (process exit 2).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
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
PRIVATE_CACHE = Path("/tmp/mhac-openalex-full")
BASE = "https://api.openalex.org/works"
SELECT = ("id,doi,display_name,publication_year,publication_date,type,language,"
          "primary_location,best_oa_location,locations,authorships,biblio,ids,"
          "referenced_works,is_retracted,abstract_inverted_index")
PER_PAGE = 200
BASIC_LIMIT = 10_000
DATE_LIMIT = "to_publication_date:2026-10-04"
DEFAULT_ORDER = ("EQ3", "EQ7", "EQ6", "EQ2", "EQ4", "EQ5", "EQ8", "EQ1")
DEFAULT_SORT = "publication_date:asc,display_name:asc"
USER_AGENT = "MHAC-R005 research search (techrote/MachineHumanAudioCybersemiotics)"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def query_families() -> dict[str, str]:
    """Read every concept and term unchanged from the frozen protocol block."""
    text = PROTOCOL.read_text(encoding="utf-8")
    block = "EQ1 broad recall" + text.split("EQ1 broad recall", 1)[1].split("```", 1)[0]
    families = {}
    for chunk in re.split(r"\n\s*\n", block.strip()):
        lines = chunk.strip().splitlines()
        families[lines[0].split()[0]] = " ".join(line.strip() for line in lines[1:])
    if list(families) != [f"EQ{i}" for i in range(1, 9)]:
        raise ValueError("Frozen protocol query inventory changed")
    return families


def page_url(query: str, page: int, per_page: int = PER_PAGE, sort: str | None = DEFAULT_SORT) -> str:
    if not isinstance(page, int) or isinstance(page, bool) or page < 1:
        raise ValueError("page must be a positive integer")
    if per_page not in (100, 200):
        raise ValueError("Use supported 100 or documented legacy 200 page size")
    if page * per_page > BASIC_LIMIT:
        raise ValueError("Basic pagination cannot exceed 10,000 results")
    params = [("filter", f"title_and_abstract.search:{query},{DATE_LIMIT}"),
              ("per_page", str(per_page)), ("select", SELECT), ("page", str(page))]
    if sort:
        params.append(("sort", sort))
    return BASE + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote, safe=":,")


def fetch(url: str) -> tuple[int, bytes, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers)


def _write_new(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(body)


def _encode(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def _gzip(body: bytes) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, filename="", mode="wb", mtime=0) as handle:
        handle.write(body)
    return buffer.getvalue()


def _public_urls(value):
    """Do not republish bearer/signed URL parameters returned by third parties."""
    if isinstance(value, dict):
        return {k: _public_urls(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_public_urls(item) for item in value]
    if isinstance(value, str) and value.startswith(("https://", "http://")):
        url = urllib.parse.urlsplit(value)
        names = {name.lower() for name, _ in urllib.parse.parse_qsl(url.query)}
        if any(name in {"api_key", "key", "token", "access_token", "signature", "sig", "awsaccesskeyid", "googleaccessid"}
               or name.startswith(("x-amz-", "x-goog-")) for name in names):
            return urllib.parse.urlunsplit((url.scheme, url.netloc, url.path, "", ""))
    return value


def _number(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) and result >= 0 else None


class RequestBudget:
    def __init__(self, max_requests: int | None = None):
        self.max_requests = max_requests
        self.requests = 0
        self.remaining = None
        self.request_cost = None
        self.stop_reason = None

    def unavailable(self) -> str | None:
        if self.stop_reason:
            return self.stop_reason
        if self.max_requests is not None and self.requests >= self.max_requests:
            return "request_budget_boundary"
        if self.remaining is not None and self.request_cost is not None and self.remaining < self.request_cost:
            return "observed_daily_budget_boundary"
        return None

    def observe(self, headers: dict, status: int) -> dict:
        headers = {k.lower(): v for k, v in headers.items()}
        selected = {k: headers[k] for k in ("content-type", "x-ratelimit-limit", "x-ratelimit-remaining",
                    "x-ratelimit-credits-used", "retry-after") if k in headers}
        remaining = _number(headers.get("x-ratelimit-remaining"))
        previous = self.remaining
        if remaining is not None:
            self.remaining = remaining
        cost = _number(headers.get("x-ratelimit-credits-used"))
        if cost is not None and cost > 0:
            self.request_cost = cost
        elif previous is not None and remaining is not None and previous > remaining:
            # A larger shared-IP delta is a conservative estimate of future cost.
            self.request_cost = max(self.request_cost or 0, previous - remaining)
        if status in (400, 401, 403, 429):
            self.stop_reason = f"HTTP_{status}_access_or_budget_limit"
        return selected


def _retain_response(body, status, label, page, run_dir, private_run, root, attempt=1):
    """Raw bytes stay private; public provenance explicitly describes the derivative."""
    stem = f"p{page:04d}" + (f"-a{attempt}" if attempt > 1 else "")
    raw_path = private_run / label / f"{stem}.json"
    _write_new(raw_path, body)
    entry = {"raw_sha256": hashlib.sha256(body).hexdigest(), "raw_bytes": len(body),
             "private_raw_cache_key": f"{private_run.name}/{label}/{raw_path.name}"}
    try:
        data = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        data = None
    if status == 200 and isinstance(data, dict):
        public = dict(data)
        if isinstance(data.get("results"), list):
            public["results"] = [{k: v for k, v in item.items() if k != "abstract_inverted_index"}
                                 if isinstance(item, dict) else item for item in data["results"]]
        entry["derivation"] = "JSON reserialization; abstract_inverted_index removed; sensitive URL query parameters stripped; deterministic gzip"
    else:
        public = {"http_status": status, "response_excerpt": body[:2000].decode("utf-8", "replace")}
        entry["derivation"] = "Error excerpt; full original bytes retained in private cache"
    public_path = run_dir / label / f"{stem}.json.gz"
    payload = _encode(_public_urls(public))
    public_body = _gzip(payload)
    if gzip.decompress(public_body) != payload:
        raise ValueError("gzip roundtrip failed")
    _write_new(public_path, public_body)
    entry.update(file=public_path.relative_to(root).as_posix(), bytes=len(public_body),
                 sha256=hashlib.sha256(public_body).hexdigest(), compression="gzip; mtime=0; empty filename",
                 payload_bytes=len(payload), payload_sha256=hashlib.sha256(payload).hexdigest())
    return entry, data if isinstance(data, dict) else None


def harvest(label, query, record, *, run_dir, private_run, root, per_page,
            budget, fetcher, checkpoint, delay, sleeper, sort):
    record.update(started_at=now(), status="in_progress")
    seen, page, attempt = set(), 1, 1
    while True:
        reason = budget.unavailable()
        if reason:
            record["failures"].append(reason)
            break
        url = page_url(query, page, per_page, sort)
        entry = {"page": page, "attempt": attempt, "url": url, "fetched_at": now()}
        budget.requests += 1
        try:
            status, body, headers = fetcher(url)
        except (OSError, urllib.error.URLError) as error:
            entry["transport_error"] = f"{type(error).__name__}: {error}"
            record["pages"].append(entry)
            record["failures"].append(f"page {page}: transport_error")
            break
        entry["http_status"] = status
        retained, data = _retain_response(body, status, label, page, run_dir, private_run, root, attempt)
        entry.update(retained)
        meta = data.get("meta", {}) if data else {}
        if not isinstance(meta, dict):
            meta = {}
        entry["response_headers"] = budget.observe(headers, status)
        entry["reported_cost_usd"] = meta.get("cost_usd")
        record["pages"].append(entry)
        if status != 200:
            lower_headers = {k.lower(): v for k, v in headers.items()}
            retry_after = _number(lower_headers.get("retry-after"))
            if retry_after is None and data:
                retry_after = _number(data.get("retryAfter"))
            message = str(data.get("message", "")).lower() if data else ""
            temporary_load = status == 429 and "temporarily" in message and "elevated load" in message
            if temporary_load and retry_after is not None and retry_after <= 30 and attempt < 3:
                budget.stop_reason = None
                if not budget.unavailable():
                    entry["retry_after_seconds"] = retry_after
                    entry["retry_scheduled"] = True
                    checkpoint()
                    sleeper(retry_after)
                    attempt += 1
                    continue
                budget.stop_reason = "HTTP_429_access_or_budget_limit"
            record["failures"].append(f"page {page}: HTTP {status}")
            break
        if not data or not isinstance(data.get("results"), list):
            record["failures"].append(f"page {page}: invalid_json_or_results")
            break
        results = data["results"]
        entry["results"] = len(results)
        count = meta.get("count")
        entry["reported_count"] = count
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            record["failures"].append(f"page {page}: invalid_reported_count")
        elif page == 1:
            record["reported_count"] = count
        elif count != record["reported_count"]:
            record["failures"].append(f"page {page}: count_drift {record['reported_count']} -> {count}")
        if meta.get("page") != page or meta.get("per_page") != per_page:
            record["failures"].append(f"page {page}: response_pagination_mismatch")
        ids = [item.get("id") if isinstance(item, dict) else None for item in results]
        if any(not isinstance(identity, str) or not identity for identity in ids):
            record["failures"].append(f"page {page}: missing_work_id")
        valid_ids = [identity for identity in ids if isinstance(identity, str) and identity]
        duplicates = {identity for identity in valid_ids if identity in seen}
        if len(set(valid_ids)) != len(valid_ids) or duplicates:
            entry["duplicate_ids"] = sorted({identity for identity in valid_ids if valid_ids.count(identity) > 1} | duplicates)
            record["failures"].append(f"page {page}: duplicate_work_ids")
        seen.update(valid_ids)
        record["retrieved"] = sum(p.get("results", 0) for p in record["pages"])
        record["unique_retrieved"] = len(seen)
        if len(results) > per_page:
            record["failures"].append(f"page {page}: oversized_page")
        if record.get("reported_count", 0) > BASIC_LIMIT:
            record["failures"].append("basic_paging_limit: reported_count exceeds 10000")
        if record["failures"]:
            break
        target = record["reported_count"]
        if record["retrieved"] >= target:
            if record["retrieved"] != target or len(seen) != target:
                record["failures"].append("retrieved_count_mismatch")
            break
        if len(results) != per_page:
            record["failures"].append(f"page {page}: premature_short_page")
            break
        checkpoint()
        page += 1
        attempt = 1
        sleeper(delay)
    record["finished_at"] = now()
    record["complete"] = (not record["failures"] and record.get("reported_count") == record["retrieved"]
                          == record["unique_retrieved"])
    record["status"] = "completed" if record["complete"] else ("partial" if record["retrieved"] else "failed")
    checkpoint()


def run_harvest(labels=None, *, out_root=OUT, private_root=PRIVATE_CACHE, root=ROOT,
                run_id=None, per_page=PER_PAGE, max_requests=None, fetcher=fetch,
                delay=1.1, sleeper=time.sleep, sort=DEFAULT_SORT):
    families = query_families()
    labels = list(labels or DEFAULT_ORDER)
    if len(set(labels)) != len(labels) or any(label not in families for label in labels):
        raise ValueError("Choose each frozen EQ label at most once")
    if per_page not in (100, 200) or (max_requests is not None and max_requests < 1):
        raise ValueError("Invalid page size or request budget")
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ValueError("run_id must be a safe directory name")
    run_dir, private_run = out_root / run_id, private_root / run_id
    if run_dir.exists() or private_run.exists():
        raise FileExistsError("Run directory exists; choose a new run id")
    run_dir.mkdir(parents=True)
    private_run.mkdir(parents=True)
    budget = RequestBudget(max_requests)
    manifest = {"schema": "mhac-r005-openalex-harvest/2", "run_id": run_id,
                "protocol": "research/protocol/PROTOCOL-v1.md",
                "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
                "actor": "ChatGPT GPT-6 Astra Pro, database-channel subagent",
                "credential_use": "none", "started_at": now(), "pagination": "basic",
                "basic_paging_limit": BASIC_LIMIT, "page_size": per_page, "sort": sort,
                "page_size_status": "documented deprecated legacy" if per_page == 200 else "supported maximum",
                "private_cache_policy": "Cache keys identify original responses under a caller-configured uncommitted cache root",
                "public_data_policy": "Deterministic gzip metadata derivatives omit abstracts and sensitive URL query parameters",
                "requested_order": labels, "runs": {}}
    for label in labels:
        manifest["runs"][label] = {"label": label, "query": families[label],
            "filter": f"title_and_abstract.search:{families[label]},{DATE_LIMIT}",
            "per_page": per_page, "select": SELECT, "sort": sort, "status": "planned", "pages": [],
            "failures": [], "retrieved": 0, "unique_retrieved": 0, "complete": False}
    manifest_path = run_dir / "MANIFEST.json"

    def checkpoint():
        manifest["requests_made"] = budget.requests
        manifest["last_observed_budget_remaining"] = budget.remaining
        manifest["observed_request_cost_credits"] = budget.request_cost
        temporary = manifest_path.with_suffix(".json.tmp")
        temporary.write_bytes(_encode(manifest))
        temporary.replace(manifest_path)

    checkpoint()
    for index, label in enumerate(labels):
        harvest(label, families[label], manifest["runs"][label], run_dir=run_dir,
                private_run=private_run, root=root, per_page=per_page, budget=budget,
                fetcher=fetcher, checkpoint=checkpoint, delay=delay, sleeper=sleeper, sort=sort)
        result = manifest["runs"][label]
        print(label, result.get("reported_count"), result["retrieved"], result["status"], result["failures"], flush=True)
        if index + 1 < len(labels) and not budget.unavailable():
            sleeper(delay)
    manifest["finished_at"] = now()
    manifest["complete"] = all(run["complete"] for run in manifest["runs"].values())
    manifest["total_query_occurrences"] = sum(run["retrieved"] for run in manifest["runs"].values())
    checkpoint()
    return manifest, manifest_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("families", nargs="*")
    parser.add_argument("--per-page", type=int, choices=(100, 200), default=PER_PAGE)
    parser.add_argument("--max-requests", type=int)
    parser.add_argument("--run-id")
    parser.add_argument("--sort", default=DEFAULT_SORT, help="Recorded sort order; empty string requests provider default")
    args = parser.parse_args(argv)
    manifest, path = run_harvest(args.families or None, per_page=args.per_page,
                                 max_requests=args.max_requests, run_id=args.run_id, sort=args.sort or None)
    print(path.relative_to(ROOT).as_posix())
    return 0 if manifest["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
