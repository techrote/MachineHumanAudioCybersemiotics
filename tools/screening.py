"""Conservative identity candidates and explicit screening-coverage diagnostics.

No function here screens a paper, invents a source identity, changes stable IDs,
or merges records. Candidate matches require recorded adjudication. Coverage is
bookkeeping over an explicit scope, never a declaration of corpus acceptance.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations
import re
import unicodedata
from typing import Any, Callable, Iterable
from urllib.parse import unquote, urlsplit, urlunsplit

from schemas.v1 import stamp
from tools.record_io import fail

TRACKS = ("empirical", "theoretical")
STAGES = ("title_abstract", "full_text")
DECISIONS = ("pending", "include", "exclude", "awaiting_text", "uncertain")
_DOI = re.compile(r"10\.\d{4,9}/[^\s]+\Z", re.IGNORECASE)
_CONTROL = re.compile(r"[\x00-\x20\x7f]")


def normalize_doi(value: str) -> str | None:
    """Normalize a DOI or DOI-resolver URL without trimming suffix punctuation.

    A publisher URL or a DOI embedded in prose is not a DOI assertion. In a
    resolver URL, query/fragment delimiters are URL components, not DOI suffixes;
    percent-encoded delimiters in the path remain part of the decoded DOI.
    """
    if not isinstance(value, str):
        return None
    value = value.strip()
    if value.lower().startswith("doi:"):
        value = value[4:].strip()
    elif value.lower().startswith(("https://", "http://")):
        # urlsplit silently removes embedded LF, CR and TAB. Reject them before
        # parsing so a malformed asserted DOI cannot become a different DOI.
        if _CONTROL.search(value):
            return None
        try:
            parsed = urlsplit(value)
            if (parsed.hostname or "").lower() not in {"doi.org", "dx.doi.org"}:
                return None
            if parsed.username is not None or parsed.password is not None or parsed.port not in {None, 80, 443}:
                return None
        except ValueError:
            return None
        value = unquote(parsed.path.lstrip("/"))
    if _CONTROL.search(value) or not _DOI.fullmatch(value):
        return None
    return value.lower()


def normalize_url(value: str) -> str | None:
    """Normalize only scheme/host case and the matching default port.

    Preserve path case, slash, escapes, query order, query values and fragments.
    An exact resource match is still not proof that the resource is a paper.
    """
    if not isinstance(value, str) or _CONTROL.search(value):
        return None
    try:
        parsed = urlsplit(value)
        scheme = parsed.scheme.lower()
        if scheme not in {"http", "https"} or not parsed.hostname:
            return None
        if parsed.username is not None or parsed.password is not None:
            return None
        host = parsed.hostname.lower()
        if ":" in host:
            host = "[" + host + "]"
        port = parsed.port
        if port is not None and (scheme, port) not in {("http", 80), ("https", 443)}:
            host += ":" + str(port)
        return urlunsplit((scheme, host, parsed.path, parsed.query, parsed.fragment))
    except ValueError:
        return None


def _text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).casefold().split())


def title_author_year(source: dict) -> tuple[str, str, str] | None:
    """Return an exact normalized key only when all fields are actually known."""
    date = source["publication_date"]
    authors = [a["name"] for a in source["authors"]
               if a["role"] in {"author", "corporate_author"}]
    if date.get("state") != "known" or not authors or not source["title"].strip():
        return None
    value = date.get("value")
    if not isinstance(value, str) or re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", value) is None:
        return None
    return _text(source["title"]), _text(authors[0]), value[:4]


def verified_dois(source: dict) -> set[str]:
    return {value for item in source["identifiers"]
            if item["scheme"] == "doi" and item["status"] == "verified"
            and (value := normalize_doi(item["value"])) is not None}


def identity_candidates(sources: dict[str, dict]) -> list[dict]:
    """Return auditable pair candidates; no transitive/fuzzy merge is applied.

    ``sources`` maps stable source IDs to current source bodies. A matched URL
    or title key cannot override distinct verified DOIs. Conflicted metadata is
    carried as a conflict even if another field happens to match.
    """
    index: dict[tuple[str, Any], set[str]] = defaultdict(set)
    dois = {rid: verified_dois(source) for rid, source in sources.items()}
    for rid, source in sorted(sources.items()):
        for doi in dois[rid]:
            index[("verified_doi", doi)].add(rid)
        for item in source["identifiers"]:
            if item["scheme"] == "url" and item["status"] == "verified":
                normalized = normalize_url(item["value"])
                if normalized is not None:
                    index[("verified_resource_url", normalized)].add(rid)
        key = title_author_year(source)
        if key is not None:
            index[("title_first_author_year", key)].add(rid)
    pairs: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for (kind, value), ids in sorted(index.items()):
        for pair in combinations(sorted(ids), 2):
            pairs[pair].append({"kind": kind, "value": list(value) if isinstance(value, tuple) else value})
    result = []
    for (left, right), matches in sorted(pairs.items()):
        conflict = bool(dois[left] and dois[right] and dois[left] != dois[right])
        conflict = conflict or any(sources[rid]["metadata_status"] == "conflict" or len(dois[rid]) > 1
                                   or any(item["scheme"] == "doi" and item["status"] == "conflict"
                                          for item in sources[rid]["identifiers"])
                                   for rid in (left, right))
        result.append({"source_ids": [left, right], "matches": matches,
                       "status": "conflict" if conflict else "candidate",
                       "verified_dois": {left: sorted(dois[left]), right: sorted(dois[right])},
                       "action": "Retain separate IDs; adjudicate against source evidence before any alias or family link."})
    return result


def validate_verified_doi_uniqueness(sources: dict[str, dict], canonical: Callable[[str], str]) -> None:
    """Reject the same verified DOI owned by distinct canonical publications."""
    owners: dict[str, set[str]] = defaultdict(set)
    for rid, source in sorted(sources.items()):
        for item in source["identifiers"]:
            if item["scheme"] == "doi" and item["status"] == "verified" and normalize_doi(item["value"]) is None:
                fail("SOURCE_IDENTIFIER", f"{rid}: verified DOI cannot be normalized; preserve it as candidate/conflict until resolved")
        for doi in verified_dois(source):
            owners[doi].add(canonical(rid))
    for doi, ids in sorted(owners.items()):
        if len(ids) > 1:
            fail("SOURCE_IDENTITY_COLLISION", f"{doi}: {sorted(ids)}; reconcile identity or mark the disputed identifier as conflict")


def screening_scope(body: dict, canonical: Callable[[str], str]) -> tuple[str, str, str, str]:
    return (canonical(body["source_ref"]["id"]), body.get("track", "empirical"),
            body["stage"], body["protocol_version"])


def effective_screening(graph: Any, *, at: str | None = None,
                        record_ids: Iterable[str] | None = None) -> dict[tuple[str, str, str, str], tuple[str, dict]]:
    """Select the effective logical decision per source/track/stage/protocol.

    Historical selection uses only decisions and source aliases recorded by
    ``at``. Supersession disposes a logical predecessor even when it pins an
    earlier revision of it. The graph separately validates source/scope
    agreement and reference types.
    """
    cutoff = stamp(at) if at is not None else None
    canonical = graph.canonical_id if at is None else lambda rid: graph.canonical_id_at(rid, at)
    grouped: dict[tuple[str, str, str, str], dict[str, dict]] = defaultdict(dict)
    superseded = set()
    selected = sorted(graph.records if record_ids is None else record_ids)
    for rid in selected:
        row = graph.records[rid]
        if row["kind"] != "screening":
            continue
        eligible = [r for r in row["revisions"] if cutoff is None or stamp(r["at"]) <= cutoff]
        if not eligible:
            continue
        body = eligible[-1]["data"]
        grouped[screening_scope(body, canonical)][rid] = body
        if "supersedes_ref" in body:
            superseded.add(body["supersedes_ref"]["id"])
    result = {}
    for scope, decisions in sorted(grouped.items()):
        remaining = sorted(set(decisions) - superseded)
        if len(remaining) != 1:
            fail("SCREENING_CONFLICT", f"{scope}: {sorted(decisions)}")
        rid = remaining[0]
        result[scope] = rid, decisions[rid]
    return result


def screening_coverage(graph: Any, *, source_ids: Iterable[str], protocol_version: str,
                       track: str = "empirical") -> dict:
    """Diagnose an explicitly named source scope without declaring it complete."""
    if track not in TRACKS or not isinstance(protocol_version, str) or not protocol_version.strip():
        fail("SCREENING_SCOPE", "Specify empirical/theoretical and a nonblank protocol version")
    ids = list(source_ids)
    if len(set(ids)) != len(ids):
        fail("SCREENING_SCOPE", "Repeated source ID in the requested scope")
    canonical_ids = set()
    for rid in ids:
        if rid not in graph.records or graph.records[rid]["kind"] != "source":
            fail("SCREENING_SCOPE", f"Not a source: {rid}")
        canonical_ids.add(graph.canonical_id(rid))
    decisions = effective_screening(graph)
    rows = []
    for rid in sorted(canonical_ids):
        ta = decisions.get((rid, track, "title_abstract", protocol_version))
        ft = decisions.get((rid, track, "full_text", protocol_version))
        rows.append({"source_id": rid,
                     "title_abstract": ta[1]["decision"] if ta else "not_recorded",
                     "full_text": ft[1]["decision"] if ft else "not_recorded",
                     "full_text_required": bool(ta and ta[1]["decision"] in {"include", "uncertain"})})
    return {"track": track, "protocol_version": protocol_version,
            "source_count": len(rows), "sources": rows,
            "missing_title_abstract": [r["source_id"] for r in rows if r["title_abstract"] == "not_recorded"],
            "missing_required_full_text": [r["source_id"] for r in rows if r["full_text_required"] and r["full_text"] == "not_recorded"],
            "awaiting_text": [r["source_id"] for r in rows if r["full_text"] == "awaiting_text"],
            "acceptance": "not_evaluated",
            "boundary": "Only the explicitly supplied source scope is counted; retrieval, verification, source fidelity and search completeness are not inferred."}
