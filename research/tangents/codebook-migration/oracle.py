"""T012 synthetic-only longitudinal cue mapping falsifier (stdlib, no human data)."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

DIR = Path(__file__).resolve().parent
POLICIES = ("silent_replacement", "frozen_legacy", "versioned_manifest", "alternate_family_unknown")

def truth(row):
    """Independent fictional eligibility; not inferred from decoded cue."""
    if not row["required"]:
        return "not_required"
    if row["resolved"] is True:
        return "resolved"
    if row["revoked"] is True:
        return "revoked"
    if row["resolved"] is None or row["revoked"] is None or row["deadline"] is None:
        return "unknown"
    return "expired" if row["received_at"] > row["deadline"] else "valid"

def load():
    doc = json.loads((DIR / "TRACES.json").read_text(encoding="utf8"))
    if doc["schema"] != "mhac-t012-fictional-v1":
        raise ValueError("invalid_fixture_schema")
    rows = doc["cases"]
    if len(rows) < 24 or len({r["id"] for r in rows}) != len(rows):
        raise ValueError("duplicate_or_insufficient_cases")
    for row in rows:
        if truth(row) != row["expected_truth"]:
            raise ValueError("truth_label_mismatch:" + row["id"])
        if row["label_status"] == "trusted" and row["claimed_generation_version"] != row["generation_codebook_version"]:
            raise ValueError("contradictory_trusted_label:" + row["id"])
        if row["nonaudio_verified"] and row["nonaudio"] != row["truth"]:
            raise ValueError("contradictory_nonaudio_attestation:" + row["id"])
    return doc

def mapping(doc, version, asset):
    return doc["codebooks"].get(str(version), {}).get(asset)

def compatible(a, b):
    return a is not None and b is not None and a == b

def decision(doc, row, policy):
    """Policy input excludes independent truth referent/action/priority fields."""
    if policy == "alternate_family_unknown":
        return ("unresolved", "listener_transfer_unmeasured", None)
    if policy in ("silent_replacement", "frozen_legacy"):
        v = row["receiver_codebook_version"] if policy == "silent_replacement" else 1
        item = mapping(doc, v, row["cue_asset_id"])
        return ("offer", "receiver_or_legacy_legend", item) if item else ("unresolved", "unmapped_asset", None)
    if policy != "versioned_manifest":
        raise ValueError("unknown_policy")
    # A hypothetical, ideal independently attested state/clock is available only when declared.
    if not row["state_attested"] or truth(row) != "valid":
        return ("unresolved", "unattested_or_invalid_obligation", None)
    if row["nonaudio_verified"] and row["nonaudio"] is not None:
        return ("offer", "verified_nonaudio_fallback", list(row["nonaudio"].values()))
    if row["label_status"] != "trusted" or row["claimed_generation_version"] is None:
        return ("unresolved", "untrusted_version", None)
    original = mapping(doc, row["claimed_generation_version"], row["cue_asset_id"])
    current = mapping(doc, row["receiver_codebook_version"], row["cue_asset_id"])
    if not compatible(original, current):
        return ("unresolved", "mapping_conflict", None)
    return ("offer", "versioned_mapping_compatible", current)

def summarize(doc):
    out = {}
    for policy in POLICIES:
        s = dict(offers=0, wrong_referent=0, wrong_priority=0, wrong_action=0,
                 invalid_or_unknown_offers=0, expired_or_revoked_offers=0,
                 false_compatibility_offers=0, unresolved=0, omitted_valid=0)
        for row in doc["cases"]:
            kind, reason, fields = decision(doc, row, policy)
            status = truth(row)
            if kind == "unresolved":
                s["unresolved"] += 1
                if status == "valid":
                    s["omitted_valid"] += 1
                continue
            s["offers"] += 1
            for index, field in enumerate(("referent", "priority", "action")):
                if fields[index] != row["truth"][field]:
                    s["wrong_" + field] += 1
            if status != "valid":
                s["invalid_or_unknown_offers"] += 1
            if status in ("expired", "revoked"):
                s["expired_or_revoked_offers"] += 1
            original = mapping(doc, row["generation_codebook_version"], row["cue_asset_id"])
            current = mapping(doc, row["receiver_codebook_version"], row["cue_asset_id"])
            if original is not None and not compatible(original, current):
                s["false_compatibility_offers"] += 1
        out[policy] = s
    return dict(schema="mhac-t012-results-v1", cases=len(doc["cases"]), policies=out,
                warning="fictional symbolic offers only; listener recognition and actual action unmeasured")

def check():
    doc = load()
    m = json.loads((DIR / "MANIFEST.json").read_text(encoding="utf8"))
    digest = hashlib.sha256((DIR / "TRACES.json").read_bytes()).hexdigest()
    if m["schema"] != "mhac-t012-manifest-v1" or m["sha256"] != digest or m["case_count"] != len(doc["cases"]):
        raise ValueError("stale_or_corrupt_manifest")
    return summarize(doc)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    print(json.dumps(check() if args.check else summarize(load()), indent=2, sort_keys=True))
