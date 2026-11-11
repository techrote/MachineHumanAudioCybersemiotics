"""R005 private original-PDF attestation. Not full-text screening or rights approval.
Refs #5; downstream #6. No network fetching or original PDF redistribution.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SCHEMA = "mhac-r005-original-pdf-private-attestation/1"


def parse_utc(text):
    try:
        value = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid acquisition timestamp") from exc
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Acquisition time must include timezone")
    return value.astimezone(timezone.utc)


def require_url(text, field):
    parsed = urlparse(text)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(field + " must be HTTPS without embedded credentials, query tokens or fragments")
    return text


def hash_pdf(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError("Original local PDF is unavailable")
    digest = hashlib.sha256()
    total, header, tail = 0, b"", b""
    with path.open("rb") as stream:
        while block := stream.read(1048576):
            if total == 0:
                header = block[:8]
            digest.update(block)
            total += len(block)
            tail = (tail + block)[-4096:]
    if total < 64 or not header.startswith(b"%PDF-") or b"%%EOF" not in tail:
        raise ValueError("Input lacks recognizable PDF header/end marker")
    return digest.hexdigest(), total


def capture(args):
    if not re.fullmatch(r"10\.\d{4,9}/\S+", args.doi, flags=re.I):
        raise ValueError("DOI format is invalid")
    now = datetime.now(timezone.utc)
    acquisition = parse_utc(args.acquired_at)
    if acquisition > now:
        raise ValueError("Acquisition timestamp is in the future")
    for field in ("edition", "access_proof", "rights_note", "reading_boundary", "actor"):
        if not getattr(args, field).strip():
            raise ValueError("Required provenance missing: " + field)
    require_url(args.source_url, "source URL")
    require_url(args.rights_url, "rights evidence URL")
    sha, size = hash_pdf(args.file)
    return {
        "schema": SCHEMA, "issue": 5, "downstream_issue": 6,
        "frozen_cutoff": "2026-10-04",
        "status": "operator_attested_local_pdf_bytes_not_canonical_screening",
        "publication_doi": args.doi.lower(),
        "edition_manifestation": args.edition,
        "original_source_url": args.source_url,
        "acquisition_utc_operator_reported": acquisition.isoformat().replace("+00:00", "Z"),
        "attestation_utc": now.isoformat().replace("+00:00", "Z"),
        "attester_operator_reported": args.actor,
        "access_proof_operator_reported": args.access_proof,
        "rights_evidence_url": args.rights_url,
        "rights_limit_operator_reported": args.rights_note,
        "source_reading_boundary_operator_reported": args.reading_boundary,
        "original_pdf_sha256": sha, "original_pdf_bytes": size,
        "original_pdf_retained_in_manifest": False,
        "verified_licence_or_source_URL": False,
        "human_reviewer_claimed": False,
        "original_audio_inspected": False,
        "admitted_studies_experiments_samples": [0, 0, 0],
        "caution": "This is a hash of a local PDF, not proof of where/when it was acquired, its licence, that the operator read it, or eligibility. Original bytes stay in rights-compliant private storage."
    }


def verify(path, receipt):
    data = json.loads(Path(receipt).read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA or data.get("status") != "operator_attested_local_pdf_bytes_not_canonical_screening":
        raise ValueError("Wrong or promoted receipt schema")
    # The receipt is a byte hash and operator statement, not a scientific or
    # rights gate. A matching PDF must never validate an altered admission flag.
    fixed = {
        "issue": 5, "downstream_issue": 6, "frozen_cutoff": "2026-10-04",
        "original_pdf_retained_in_manifest": False,
        "verified_licence_or_source_URL": False,
        "human_reviewer_claimed": False,
        "original_audio_inspected": False,
        "admitted_studies_experiments_samples": [0, 0, 0],
    }
    for key, expected in fixed.items():
        actual = data.get(key)
        if (type(actual) is not type(expected) or actual != expected
                or (isinstance(expected, list) and
                    any(type(item) is not int for item in actual))):
            raise ValueError("Receipt research-state/identity guard failed: " + key)
    if not isinstance(data.get("publication_doi"), str) or not re.fullmatch(
            r"10\.\d{4,9}/\S+", data["publication_doi"], flags=re.I):
        raise ValueError("Invalid operator-reported DOI")
    for key in ("original_source_url", "rights_evidence_url"):
        if not isinstance(data.get(key), str):
            raise ValueError("Missing operator-reported URL: " + key)
        require_url(data[key], key)
    for key in ("edition_manifestation", "attester_operator_reported",
                "access_proof_operator_reported", "rights_limit_operator_reported",
                "source_reading_boundary_operator_reported"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError("Missing operator-reported provenance: " + key)
    for key in ("acquisition_utc_operator_reported", "attestation_utc"):
        if not isinstance(data.get(key), str):
            raise ValueError("Missing receipt timestamp: " + key)
        parsed = parse_utc(data[key])
        if parsed.isoformat().replace("+00:00", "Z") != data[key]:
            raise ValueError("Receipt timestamp is not canonical UTC: " + key)
        if parsed > datetime.now(timezone.utc):
            raise ValueError("Receipt timestamp is in the future: " + key)
    if parse_utc(data["acquisition_utc_operator_reported"]) > parse_utc(data["attestation_utc"]):
        raise ValueError("Operator-reported acquisition postdates attestation")
    if not re.fullmatch(r"[0-9a-f]{64}", str(data.get("original_pdf_sha256", ""))):
        raise ValueError("Missing original PDF SHA256")
    digest, size = hash_pdf(path)
    if (digest, size) != (data["original_pdf_sha256"], data.get("original_pdf_bytes")):
        raise ValueError("Original PDF bytes do not match receipt")
    return {"verified_sha256": digest, "verified_bytes": size, "source_rights_and_reading_not_verified": True}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="operation", required=True)
    record = sub.add_parser("capture")
    record.add_argument("--file", required=True, type=Path)
    record.add_argument("--manifest", required=True, type=Path)
    for name in ("doi", "edition", "source-url", "rights-url", "acquired-at",
                 "access-proof", "rights-note", "reading-boundary", "actor"):
        record.add_argument("--" + name, required=True)
    check = sub.add_parser("verify")
    check.add_argument("--file", required=True, type=Path)
    check.add_argument("--manifest", required=True, type=Path)
    args = ap.parse_args(argv)
    try:
        if args.operation == "capture":
            receipt = capture(args)
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            with args.manifest.open("x", encoding="utf-8") as file:
                json.dump(receipt, file, indent=2, sort_keys=True, ensure_ascii=False)
                file.write("\n")
            print(json.dumps({"sha256": receipt["original_pdf_sha256"], "bytes": receipt["original_pdf_bytes"], "receipt": str(args.manifest)}))
        else:
            print(json.dumps(verify(args.file, args.manifest), sort_keys=True))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("PDF attestation blocked: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
