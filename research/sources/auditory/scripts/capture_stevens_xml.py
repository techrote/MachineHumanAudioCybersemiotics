"""Opt-in Stevens 2009 original-JATS acquisition into an owner-approved PRIVATE directory.

Refs #5; R004 owns source manifestation and R006 owns E1–E6 decisions.

Unlike an ephemeral CI probe, this command retains the *same bytes* whose network
response is described in its receipt. Nothing is stored in this public repository.
It is inert until a real, operator-supplied private-location/rights decision exists.

Example (AFTER owner/R004 approval, outside this repository):
  python research/sources/auditory/scripts/capture_stevens_xml.py capture \
    --private-dir /approved/private/mhac/stevens2009 \
    --approval /approved/private/mhac/approval.json \
    --operator ACTUAL_OPERATOR_ID
  python research/sources/auditory/scripts/capture_stevens_xml.py verify \
    --private-dir /approved/private/mhac/stevens2009 \
    --approval /approved/private/mhac/approval.json

approval.json (operator-provided; its authenticity is NOT machine-verified):
  {"approved_private_dir": "/approved/private/mhac/stevens2009",
   "approved_by": "ACTUAL_RIGHTS_DECISION_ACTOR",
   "approved_at_utc": "ACTUAL_APPROVAL_TIME_IN_UTC",
   "retention_basis": "REVIEWED_RIGHTS_BASIS_AND_LIMITS",
   "attribution_policy": "APPROVED_ATTRIBUTION_RULE"}

The operator must not invent an approval. Technical validity of an approval file
is not rights authorization or human scientific review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import attest_primary_xml as xml_attester

URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2865004/fullTextXML"
ROOT = Path(__file__).resolve().parents[4]
XML_NAME = "stevens2009-original.xml"
RECEIPT_NAME = "stevens2009-network-receipt.json"
MAX_BODY = 1_000_000
SCHEMA = "mhac-r005-stevens-xml-private-capture/1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def checked_dir(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_dir() or resolved.is_relative_to(ROOT):
        raise ValueError("An existing private directory outside this repository is required")
    if path.is_symlink():
        raise ValueError("Private destination may not be a symbolic link")
    return resolved


def approval_record(path: Path, directory: Path) -> tuple[dict, str]:
    if not path.is_file() or path.is_symlink():
        raise ValueError("An existing operator-provided approval file is required")
    if path.resolve().is_relative_to(ROOT):
        raise ValueError("Private approval evidence cannot be stored in the public repository")
    raw = path.read_bytes()
    if not raw or len(raw) > 20_000:
        raise ValueError("Private approval file is empty or unreasonably large")
    try:
        record = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("Malformed private approval file") from exc
    if not isinstance(record, dict):
        raise ValueError("Private approval must be a JSON object")
    for k in ("approved_private_dir", "approved_by", "approved_at_utc",
              "retention_basis", "attribution_policy"):
        if not isinstance(record.get(k), str) or not record[k].strip():
            raise ValueError("Missing explicit rights/operator declaration: " + k)
    if Path(record["approved_private_dir"]).resolve() != directory:
        raise ValueError("Approval destination differs from private output directory")
    if xml_attester.require_utc(record["approved_at_utc"]) != record["approved_at_utc"]:
        raise ValueError("Approval time must be canonical UTC")
    return record, hashlib.sha256(raw).hexdigest()


def write_exclusive(path: Path, raw: bytes) -> None:
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def check_original_http_headers(http_date: str, content_type: str,
                                requested_utc: str, received_utc: str) -> None:
    """Syntax and clock-consistency checks only; NOT server authentication.

    Require the RFC 7231 preferred IMF-fixdate shape, including its weekday.
    A five-minute tolerance allows ordinary network/server clock skew but
    rejects dates unrelated to the observed request/receipt interval.
    """
    if not isinstance(http_date, str):
        raise ValueError("Original response HTTP Date missing or malformed")
    try:
        parsed = datetime.strptime(http_date, "%a, %d %b %Y %H:%M:%S GMT")
    except ValueError as exc:
        raise ValueError("Original response HTTP Date is not IMF-fixdate") from exc
    if parsed.strftime("%a, %d %b %Y %H:%M:%S GMT") != http_date:
        raise ValueError("Original response HTTP Date weekday or canonical form differs")
    if not isinstance(content_type, str) or (content_type.lower().split(";")[0].strip()
            not in ("application/xml", "text/xml", "application/jats+xml")):
        raise ValueError("Original response Content-Type is not JATS/XML")
    started = datetime.fromisoformat(
        xml_attester.require_utc(requested_utc).replace("Z", "+00:00"))
    ended = datetime.fromisoformat(
        xml_attester.require_utc(received_utc).replace("Z", "+00:00"))
    server = parsed.replace(tzinfo=timezone.utc)
    if (started > ended or server < started - timedelta(minutes=5)
            or server > ended + timedelta(minutes=5)):
        raise ValueError("Original response HTTP Date is inconsistent with UTC acquisition")


def capture(directory: Path, approval: Path, operator: str, opener=urlopen) -> dict:
    directory = checked_dir(directory)
    rights, rights_sha = approval_record(approval, directory)
    if not operator.strip():
        raise ValueError("Actual acquiring operator ID is required")
    original = directory / XML_NAME
    receipt_file = directory / RECEIPT_NAME
    if original.exists() or receipt_file.exists():
        raise ValueError("Private source/receipt already exists; no overwrite allowed")

    request_start = utc_now()
    req = Request(URL, headers={"User-Agent": "MHAC-R005-source-custody/1"})
    with opener(req, timeout=30) as response:
        status = response.status
        effective_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
        http_date = response.headers.get("Date")
        declared_length = response.headers.get("Content-Length")
        raw = response.read(MAX_BODY + 1)
    received = utc_now()
    if status != 200 or effective_url != URL:
        raise ValueError("Original Europe PMC source refused or redirected elsewhere")
    check_original_http_headers(http_date, content_type, request_start, received)
    if len(raw) > MAX_BODY or (declared_length is not None and
                               int(declared_length) != len(raw)):
        raise ValueError("Original XML truncated or exceeds bounded source size")
    details = xml_attester.inspect_bytes(raw)
    # This is a source-embedded licensing assertion, not an operator rights grant.
    if not any("creativecommons.org/licenses/by/2.5" in s
               for s in details["licence_links_observed_not_independently_verified"]):
        raise ValueError("Expected embedded CC BY 2.5 link absent; manual rights recheck required")

    body_sha = hashlib.sha256(raw).hexdigest()
    write_exclusive(original, raw)
    try:
        base = xml_attester.capture(
            original, source_url=URL,
            edition="Europe PMC original-article JATS/XML; publisher PDF equivalence not checked",
            acquired_at=received, actor=operator,
            access_proof="Direct unauthenticated HTTPS 200; HTTP Date " + http_date,
            rights_note="Operator-supplied approval file SHA-256 " + rights_sha +
                        "; the software cannot verify the signer's authority")
        record = {
            **base,
            "capture_schema": SCHEMA,
            "network_original_response": {
                "request_start_utc": request_start,
                "received_utc": received,
                "http_date_header": http_date,
                "http_status": status,
                "requested_url": URL,
                "effective_url": effective_url,
                "content_type_header": content_type,
                "content_length_header": (int(declared_length)
                                          if declared_length is not None else None),
                "actual_body_bytes": len(raw),
                "actual_body_sha256": body_sha,
                "authenticated_http_exchange_by_operator": False,
            },
            "approval_file_sha256_operator_supplied": rights_sha,
            "approval_actor_operator_supplied_not_authenticated": rights["approved_by"],
            "approval_at_utc_operator_supplied": rights["approved_at_utc"],
            "approval_retention_basis_operator_supplied": rights["retention_basis"],
            "approval_attribution_policy_operator_supplied": rights["attribution_policy"],
            "source_custody_approved_by_software": False,
            "r006_scientific_admission": False,
        }
        write_exclusive(receipt_file, (json.dumps(record, indent=2, sort_keys=True,
                                                 ensure_ascii=False) + "\n").encode())
        return record
    except BaseException:
        # Fail closed: never leave an unreferenced newly acquired private source.
        original.unlink(missing_ok=True)
        raise


def verify(directory: Path, approval: Path) -> dict:
    directory = checked_dir(directory)
    rights, rights_sha = approval_record(approval, directory)
    original = directory / XML_NAME
    receipt_file = directory / RECEIPT_NAME
    if not original.is_file() or not receipt_file.is_file():
        raise ValueError("Original source and receipt must both exist")
    record = json.loads(receipt_file.read_text(encoding="utf-8"))
    if record.get("capture_schema") != SCHEMA:
        raise ValueError("Private network-capture schema was changed")
    v = xml_attester.verify(original, receipt_file)
    n = record.get("network_original_response")
    if not isinstance(n, dict):
        raise ValueError("Missing actual original response fields")
    if (n.get("http_status") != 200 or n.get("requested_url") != URL
            or n.get("effective_url") != URL
            or n.get("authenticated_http_exchange_by_operator") is not False
            or n.get("actual_body_sha256") != v["verified_sha256"]
            or n.get("actual_body_bytes") != v["verified_bytes"]
            or (n.get("content_length_header") is not None and
                n["content_length_header"] != v["verified_bytes"])):
        raise ValueError("Original response receipt does not match retained source")
    started = xml_attester.require_utc(n.get("request_start_utc", ""))
    ended = xml_attester.require_utc(n.get("received_utc", ""))
    check_original_http_headers(
        n.get("http_date_header"), n.get("content_type_header"), started, ended)
    # These two source/provenance fields are independently serialized at
    # capture time; a plausible but edited HTTP Date cannot silently replace
    # the Date header without also changing its operator-reported access proof.
    # This is a consistency check, not tamper-proof HTTP authentication.
    if (record.get("source_url_operator_reported") != URL
            or record.get("access_proof_operator_reported") !=
                "Direct unauthenticated HTTPS 200; HTTP Date " + n["http_date_header"]):
        raise ValueError("Original source URL or Date/access-proof receipt disagrees")
    if (started > ended or
            record.get("acquired_utc_operator_reported_not_network_verified") != ended):
        raise ValueError("Original response chronology mismatched")
    if (record.get("approval_file_sha256_operator_supplied") != rights_sha
            or record.get("approval_actor_operator_supplied_not_authenticated") != rights["approved_by"]
            or record.get("approval_at_utc_operator_supplied") != rights["approved_at_utc"]
            or record.get("approval_retention_basis_operator_supplied") != rights["retention_basis"]
            or record.get("approval_attribution_policy_operator_supplied") != rights["attribution_policy"]
            or record.get("source_custody_approved_by_software") is not False
            or record.get("r006_scientific_admission") is not False):
        raise ValueError("Rights provenance or scientific non-admission guard was changed")
    return {"original_sha256": v["verified_sha256"],
            "original_bytes": v["verified_bytes"],
            "source_and_operator_note_fingerprints_checked": True,
            "rights_authority_and_r006_eligibility_not_verified": True}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for command in ("capture", "verify"):
        p = sub.add_parser(command)
        p.add_argument("--private-dir", required=True, type=Path)
        p.add_argument("--approval", required=True, type=Path)
        if command == "capture":
            p.add_argument("--operator", required=True)
    args = parser.parse_args(argv)
    try:
        if args.cmd == "capture":
            rec = capture(args.private_dir, args.approval, args.operator)
            out = {"private_original_sha256": rec["original_xml_sha256"],
                   "private_original_bytes": rec["original_xml_bytes"],
                   "rights_and_r006_screening_not_machine_approved": True}
        else:
            out = verify(args.private_dir, args.approval)
        print(json.dumps(out, sort_keys=True))
        return 0
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print("Stevens original XML private capture HOLD: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
