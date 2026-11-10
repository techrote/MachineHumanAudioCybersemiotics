"""Offline, local original JATS/XML byte attestation for R005; not corpus admission.

Requires an already lawfully held private local copy. This tool neither fetches a
paper nor grants retention, redistribution, scientific reading or source identity.
Refs #5; source-registration and screening handoff to #4/#6.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SCHEMA = "mhac-r005-original-xml-local-attestation/1"
MAX_BYTES = 30_000_000
DOI = "10.2478/v10053-008-0064-6"
PMCID = "PMC2865004"


def require_utc(value: str) -> str:
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Malformed reported acquisition timestamp") from exc
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError("Acquisition timestamp lacks timezone")
    if d.astimezone(timezone.utc) > datetime.now(timezone.utc):
        raise ValueError("Acquisition timestamp is in the future")
    return d.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def require_url(value: str) -> str:
    u = urlparse(value)
    if (u.scheme != "https" or not u.netloc or u.username or u.password
            or u.query or u.fragment):
        raise ValueError("Source URL must be HTTPS with no credentials/query/fragment")
    return value


def inspect_bytes(raw: bytes) -> dict:
    if len(raw) < 120 or len(raw) > MAX_BYTES:
        raise ValueError("XML source size outside bounded range")
    if b"<!ENTITY" in raw.upper():
        raise ValueError("Entity declarations are prohibited")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("Invalid XML original file") from exc
    if root.tag != "article":
        raise ValueError("Expected unnamespaced original JATS article root")
    ids = [(node.get("pub-id-type", "").lower(), (node.text or "").strip())
           for node in root.findall("./front/article-meta/article-id")]
    dois = [v.lower() for k, v in ids if k == "doi"]
    pmcids = [v.upper() for k, v in ids if k in ("pmc", "pmcid")]
    if DOI not in dois:
        raise ValueError("Exact Stevens 2009 DOI missing")
    normalized_pmcids = [v.removeprefix("PMC") for v in pmcids]
    if normalized_pmcids and "2865004" not in normalized_pmcids:
        raise ValueError("Conflicting embedded PMCID")
    if root.find("./body") is None or root.find("./back") is None:
        raise ValueError("Original article body/back is absent")
    sections = ["".join(t.itertext()).strip() for t in root.findall(".//sec/title")]
    licences = []
    for node in root.findall(".//license"):
        url = (node.get("{http://www.w3.org/1999/xlink}href")
               or node.get("href") or "").strip()
        if url.startswith(("https://", "http://")) and not urlparse(url).query:
            licences.append(url)
    return {
        "doi_in_local_xml": DOI,
        "pmcid_in_local_xml": PMCID if normalized_pmcids else None,
        "article_body_present": True,
        "article_back_present": True,
        "section_heading_inventory_not_reading": sections[:150],
        "licence_links_observed_not_independently_verified": sorted(set(licences)),
    }


def hash_local(path: Path) -> dict:
    if not path.is_file():
        raise ValueError("Private original XML file is unavailable")
    raw = path.read_bytes()
    details = inspect_bytes(raw)
    details["original_xml_sha256"] = hashlib.sha256(raw).hexdigest()
    details["original_xml_bytes"] = len(raw)
    return details


def capture(path: Path, *, source_url: str, edition: str, acquired_at: str,
            actor: str, access_proof: str, rights_note: str) -> dict:
    for key, value in {"edition": edition, "actor": actor,
                       "access_proof": access_proof, "rights_note": rights_note}.items():
        if not value.strip():
            raise ValueError("Required operator-supplied provenance missing: " + key)
    provenance = hash_local(path)
    return {
        "schema": SCHEMA,
        "issue": 5, "downstream_issue": 6, "frozen_cutoff": "2026-10-04",
        "status": "local_xml_bytes_attested_not_manifestation_or_screening",
        "source_id": "SRC-R006-E-STEVENS-INFORMATIVE@1",
        "hit_id": "HIT-R005R-C1LOAD-EQ1-02138@2",
        "reported_edition": edition,
        "source_url_operator_reported": require_url(source_url),
        "acquired_utc_operator_reported_not_network_verified": require_utc(acquired_at),
        "operator_id_operator_reported": actor,
        "access_proof_operator_reported": access_proof,
        "rights_note_operator_reported_not_authorization": rights_note,
        "attestation_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        **provenance,
        "raw_xml_bytes_in_receipt": False,
        "original_pdf_equivalence_verified": False,
        "private_retention_rights_approved_by_tool": False,
        "source_manifestation_registered": False,
        "performed_semantic_reading": False,
        "human_review_performed": False,
        "screening_and_independent_sample_admissions": 0,
        "warning": "A local byte hash and embedded article identifiers do not establish acquisition provenance, rights approval, full reading, DOI publication equivalence, sample independence or corpus admission."
    }


def verify(path: Path, manifest: Path) -> dict:
    receipt = json.loads(manifest.read_text(encoding="utf-8"))
    if (receipt.get("schema") != SCHEMA
            or receipt.get("status") != "local_xml_bytes_attested_not_manifestation_or_screening"
            or receipt.get("source_id") != "SRC-R006-E-STEVENS-INFORMATIVE@1"
            or receipt.get("raw_xml_bytes_in_receipt") is not False
            or receipt.get("private_retention_rights_approved_by_tool") is not False
            or receipt.get("original_pdf_equivalence_verified") is not False
            or receipt.get("source_manifestation_registered") is not False
            or receipt.get("performed_semantic_reading") is not False
            or receipt.get("human_review_performed") is not False
            or receipt.get("screening_and_independent_sample_admissions") != 0):
        raise ValueError("Receipt schema or fail-closed research state was changed")
    fresh = hash_local(path)
    for field in ("original_xml_sha256", "original_xml_bytes",
                  "doi_in_local_xml", "pmcid_in_local_xml"):
        if fresh[field] != receipt.get(field):
            raise ValueError("Private XML bytes or claimed publication identity disagree with receipt")
    return {"verified_sha256": fresh["original_xml_sha256"],
            "verified_bytes": fresh["original_xml_bytes"],
            "rights_reading_screening_and_custody_not_verified": True}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("capture")
    c.add_argument("--file", type=Path, required=True)
    c.add_argument("--manifest", type=Path, required=True)
    for field in ("source-url", "edition", "acquired-at", "actor",
                  "access-proof", "rights-note"):
        c.add_argument("--" + field, required=True)
    v = sub.add_parser("verify")
    v.add_argument("--file", type=Path, required=True)
    v.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "capture":
            rec = capture(args.file, source_url=args.source_url, edition=args.edition,
                          acquired_at=args.acquired_at, actor=args.actor,
                          access_proof=args.access_proof, rights_note=args.rights_note)
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            with args.manifest.open("x", encoding="utf-8") as stream:
                json.dump(rec, stream, ensure_ascii=False, indent=2, sort_keys=True)
                stream.write("\n")
            print(json.dumps({"receipt": str(args.manifest),
                              "sha256": rec["original_xml_sha256"],
                              "bytes": rec["original_xml_bytes"]}))
        else:
            print(json.dumps(verify(args.file, args.manifest), sort_keys=True))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("Local original XML attestation blocked: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
