"""Offline bibliography and hash-bound Markdown citation-sidecar checks."""
from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from schemas.v1 import pin
from tools.record_io import contained_path, fail, read_json, verify_artifact

KEY = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]*\Z")
CITE = re.compile(r"(?<![A-Za-z0-9_])[-]?@([A-Za-z][A-Za-z0-9_.:-]*)")
CLAIM = re.compile(r"\{\{claim:([A-Z][A-Z0-9-]*)@([1-9][0-9]*)\}\}")
TICK = chr(96)


def markers(text: str) -> tuple[set[tuple[int, str]], set[tuple[int, tuple[str, int]]]]:
    """Supported manuscript syntax: Pandoc bracket citations and exact claim markers."""
    citations, claims = set(), set()
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith((TICK * 3, "~~~")):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is not None:
            continue
        line = re.sub("(" + TICK + r"+).*?\1", "", line)
        if "{{claim:" in CLAIM.sub("", line):
            fail("MALFORMED_CLAIM_MARKER", f"line {number}")
        for bracket in re.findall(r"\[([^\]\n]*)\]", line):
            for key in CITE.findall(bracket):
                citations.add((number, key))
        for rid, rev in CLAIM.findall(line):
            claims.add((number, (rid, int(rev))))
    return citations, claims


def validate_citations(root: Path, bibliography: str, manifests: list[str],
                       graph: Any) -> dict:
    def evidence_source(ref: dict) -> dict:
        # Bibliography pins identify the exact source used, including a retained
        # version after a harmless metadata/access observation. Never silently
        # retarget that evidence to latest.
        source = graph.lookup(ref, kind="source")
        if pin(ref) in graph.stale:
            fail("STALE_RELEASE", repr(pin(ref)))
        if source["validity"] not in {"active", "corrected"}:
            fail("UNREADY_RELEASE", repr(pin(ref)))
        return source

    bib = read_json(contained_path(root, bibliography))
    if (not isinstance(bib, dict) or set(bib) != {"schema_version", "entries"}
            or type(bib["schema_version"]) is not int or bib["schema_version"] != 1
            or not isinstance(bib["entries"], list)):
        fail("BIBLIOGRAPHY", "Expected schema_version 1 and entries")
    entries = {}
    for entry in bib["entries"]:
        if not isinstance(entry, dict) or set(entry) != {"key", "source_ref"}:
            fail("BIBLIOGRAPHY", "Each entry needs key and source_ref")
        key = entry["key"]
        if not isinstance(key, str) or KEY.fullmatch(key) is None or key in entries:
            fail("BIBLIOGRAPHY_KEY", str(key))
        evidence_source(entry["source_ref"])
        entries[key] = pin(entry["source_ref"])
    documents = {}
    count_bindings = 0
    for manifest_path in manifests:
        manifest = read_json(contained_path(root, manifest_path))
        if (not isinstance(manifest, dict)
                or set(manifest) != {"schema_version", "artifact", "bindings"}
                or type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1
                or not isinstance(manifest["bindings"], list)):
            fail("CITATION_MANIFEST", manifest_path)
        path = verify_artifact(root, manifest["artifact"])
        if path.suffix != ".md":
            fail("CITATION_FORMAT", "v1 supports Markdown manuscripts only")
        relative = path.relative_to(root.resolve()).as_posix()
        if relative in documents:
            fail("CITATION_MANIFEST", f"Duplicate document binding: {relative}")
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        citations, claims = markers(text)
        bound_citations, bound_claims = set(), set()
        for binding in manifest["bindings"]:
            if not isinstance(binding, dict) or set(binding) != {
                    "start_line", "end_line", "citation_keys", "source_refs", "claim_refs"}:
                fail("CITATION_BINDING", relative)
            start, end = binding["start_line"], binding["end_line"]
            if (type(start) is not int or type(end) is not int
                    or not 1 <= start <= end <= len(lines)):
                fail("CITATION_LOCATOR", relative)
            keys = binding["citation_keys"]
            if not isinstance(keys, list) or any(not isinstance(key, str) for key in keys):
                fail("CITATION_BINDING", "citation_keys must be a string array")
            if len(set(keys)) != len(keys):
                fail("CITATION_BINDING", "Duplicate citation key")
            refs = binding["source_refs"]
            claim_refs = binding["claim_refs"]
            if not isinstance(refs, list) or not isinstance(claim_refs, list):
                fail("CITATION_BINDING", "References must be arrays")
            sources = {pin(ref) for ref in refs}
            claim_pins = {pin(ref) for ref in claim_refs}
            if len(sources) != len(refs) or len(claim_pins) != len(claim_refs):
                fail("CITATION_BINDING", "Duplicate reference")
            for ref in refs:
                evidence_source(ref)
            for ref in claim_refs:
                graph.require_current(ref, kind="claim")
            if any(key not in entries for key in keys):
                fail("MISSING_CITATION", next(key for key in keys if key not in entries))
            cited_sources = {entries[key] for key in keys}
            if sources != cited_sources:
                fail("CITATION_SOURCE", "Bound source pins must match the cited bibliography entries")
            if claim_refs:
                closures = {}
                for target in claim_pins:
                    visited, pending, source_pins = set(), [target], set()
                    while pending:
                        dependency = pending.pop()
                        if dependency in visited:
                            continue
                        visited.add(dependency)
                        if graph.records[dependency[0]]["kind"] == "source":
                            source_pins.add(dependency)
                        pending.extend(graph.basis[dependency])
                    closures[target] = source_pins
                    claim = graph.lookup(target, kind="claim")
                    if (claim["class"] not in {"project_constraint", "unvalidated_convention"}
                            and not source_pins & cited_sources):
                        fail("CITATION_EVIDENCE", f"{target}: no cited source belongs to this claim's evidence")
                supported_sources = set().union(*closures.values())
                if not cited_sources <= supported_sources:
                    fail("CITATION_EVIDENCE", "A cited source is unrelated to the bound claims' evidence")
            for key in keys:
                if key not in entries:
                    fail("MISSING_CITATION", key)
                if entries[key] not in sources:
                    fail("CITATION_SOURCE", f"{key} is not bound to its exact source revision")
                matches = {(line, found) for line, found in citations
                           if start <= line <= end and found == key}
                if not matches:
                    fail("CITATION_LOCATOR", f"{key} does not occur in the bound lines")
                bound_citations |= matches
            for target in claim_pins:
                matches = {(line, found) for line, found in claims
                           if start <= line <= end and found == target}
                if not matches:
                    fail("CLAIM_LOCATOR", f"{target} does not occur in the bound lines")
                bound_claims |= matches
            if not keys and not claim_pins:
                fail("CITATION_BINDING", "A binding must resolve a citation or claim marker")
            count_bindings += 1
        if citations != bound_citations or claims != bound_claims:
            fail("UNBOUND_CITATION", f"{relative}: manuscript markers lack bindings")
        documents[relative] = {"citations": len(citations), "claims": len(claims)}
    paper = root / "paper"
    if paper.exists():
        for path in sorted(paper.rglob("*.md")):
            relative = path.relative_to(root).as_posix()
            contained_path(root, relative)
            cites, claims = markers(path.read_text(encoding="utf-8"))
            if (cites or claims) and relative not in documents:
                fail("UNBOUND_MANUSCRIPT", relative)
    return {"status": "passed", "bibliography_entries": len(entries),
            "documents": documents, "bindings": count_bindings,
            "not_evaluated": ["citation_entailment", "unmarked_prose_claims",
                              "non_Markdown_manuscript_formats"]}
