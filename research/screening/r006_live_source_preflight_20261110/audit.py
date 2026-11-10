"""Read-only, LIVE R006 four-candidate gate audit against canonical files.

This deliberately does not write records, exports, or change any screening verdict.
Unlike archived dated handoffs it follows latest current revisions. Full structural
and history validation is still owned by tools/validate.py and Integration.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCES = ROOT / "research/sources/related/records"
SCREEN = ROOT / "research/screening/records"
FLOW = ROOT / "research/registry/generated/evidence-flow.json"

DOIS = {
    "SRC-REL-BECKER-2025": "10.1145/3706066",
    "SRC-REL-KUHNE-2020": "10.3389/fnbot.2020.593732",
    "SRC-REL-ROMEO-2023": "10.1109/ro-man57019.2023.10309631",
    "SRC-REL-ROMEO-2025": "10.1145/3711938",
}
TA_EXPECTED = {
    "SRC-REL-BECKER-2025": "include",
    "SRC-REL-KUHNE-2020": "uncertain",
    "SRC-REL-ROMEO-2023": "uncertain",
    "SRC-REL-ROMEO-2025": "include",
}
PROTOCOL = "MHAC-Track-E-frozen-v1-2026-10-13"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_inputs(root: Path = ROOT):
    source_dir = root / "research/sources/related/records"
    screen_dir = root / "research/screening/records"
    sources, ta, ft, readings = {}, {}, {}, {}
    for sid in DOIS:
        suffix = sid.removeprefix("SRC-")
        sources[sid] = load(source_dir / (sid + ".json"))
        ta[sid] = load(screen_dir / ("SCR-R006-" + suffix + "-TA.json"))
        path = screen_dir / ("SCR-R006-" + suffix + "-FT.json")
        ft[sid] = load(path) if path.is_file() else None
    for path in screen_dir.glob("AID-*.json"):
        record = load(path)
        readings[record["id"]] = record
    return sources, ta, ft, readings, load(root / "research/registry/generated/evidence-flow.json")


def latest(record):
    if not record or not record.get("revisions"):
        raise ValueError("Missing canonical record or revisions")
    revs = record["revisions"]
    if [r["rev"] for r in revs] != list(range(1, len(revs) + 1)):
        raise ValueError("Non-contiguous canonical record history")
    return revs[-1]


def record_checked(record, rid, kind):
    if (record is None or record.get("id") != rid or record.get("kind") != kind
            or record.get("synthetic") is not False):
        raise ValueError("Absent, synthetic or identity-mismatched live record: " + rid)
    return latest(record)


def verify_reading(source_id, source_revision, refs, readings):
    manifests = {m["id"]: m for m in source_revision["data"]["manifestations"]}
    if not refs:
        raise ValueError("FT inclusion/exclusion has no performed reading AID: " + source_id)
    for ref in refs:
        rec = readings.get(ref["id"])
        r = record_checked(rec, ref["id"], "assistance")
        if r["rev"] != ref["rev"]:
            raise ValueError("Reading pin revision drift: " + ref["id"])
        data = r["data"]
        if (data.get("subtype") != "reading" or data.get("status") != "performed"
                or data.get("source_ref") != {"id": source_id, "rev": source_revision["rev"]}
                or data.get("reading_status") not in ("selected_ranges_read", "full_item_read")
                or data.get("access_at_read") not in ("partial_text", "full_text_available")):
            raise ValueError("False or unpinned full-text reading: " + ref["id"])
        m = manifests.get(data.get("manifestation_id"))
        if not m:
            raise ValueError("Reading references a missing source manifestation: " + ref["id"])
        extent = m["extent"]
        lower = 0 if m["coordinate"] == "pdf_page_0based" else 1
        upper = extent - 1 if lower == 0 else extent
        if not data.get("ranges") or any(
            not (lower <= a <= b <= upper) for a, b in data["ranges"]
        ):
            raise ValueError("Reading out of declared manifestation bounds: " + ref["id"])


def evaluate(sources, ta, ft, readings, flow):
    rows = {}
    for sid, doi in DOIS.items():
        src_rev = record_checked(sources.get(sid), sid, "source")
        source = src_rev["data"]
        verified = {i["value"].lower() for i in source["identifiers"]
                    if i["scheme"] == "doi" and i["status"] == "verified"}
        if doi not in verified or source["validity"] != "active":
            raise ValueError("Active source or exact DOI not verified: " + sid)
        ta_id = "SCR-R006-" + sid.removeprefix("SRC-") + "-TA"
        ta_rev = record_checked(ta.get(sid), ta_id, "screening")
        t = ta_rev["data"]
        if (t.get("source_ref") != {"id": sid, "rev": 1} or t.get("stage") != "title_abstract"
                or t.get("track") != "empirical" or t.get("protocol_version") != PROTOCOL
                or t.get("decision") != TA_EXPECTED[sid]):
            raise ValueError("Title/abstract source pin, protocol or decision drift: " + sid)
        if ta_rev.get("actor", {}).get("kind") not in ("agent", "human"):
            raise ValueError("Missing TA decision actor: " + sid)
        manifests = source.get("manifestations", [])
        decision = "not_recorded"
        if ft.get(sid) is not None:
            ft_id = "SCR-R006-" + sid.removeprefix("SRC-") + "-FT"
            f_rev = record_checked(ft[sid], ft_id, "screening")
            f = f_rev["data"]
            decision = f["decision"]
            pinned = next((r for r in sources[sid]["revisions"]
                           if r["rev"] == f.get("source_ref", {}).get("rev")), None)
            if (f["stage"] != "full_text" or f.get("track") != "empirical"
                    or f["protocol_version"] != PROTOCOL
                    or f["source_ref"].get("id") != sid or pinned is None
                    or f_rev["at"] < ta_rev["at"] or f_rev["at"] < pinned["at"]):
                raise ValueError("FT source revision/protocol/chronology drift: " + sid)
            if decision in ("include", "exclude"):
                verify_reading(sid, pinned, f["reading_refs"], readings)
            elif decision not in ("uncertain", "pending", "awaiting_text"):
                raise ValueError("Unrecognized full-text disposition: " + sid)
        rows[sid] = {
            "doi": doi,
            "source_revision": src_rev["rev"],
            "source_manifestations": len(manifests),
            "title_abstract": t["decision"],
            "full_text": decision,
            "ta_actor_kind": ta_rev["actor"]["kind"],
            "gate": (
                "accepted_full_text_decision_requires_scientific_review" if decision in ("include", "exclude")
                else "original_full_text_access" if sid == "SRC-REL-ROMEO-2023"
                else "source_owner_register_hashed_manifestation" if not manifests
                else "r006_full_text_screening"
            ),
        }
    actual_ta = {k: sum(x["title_abstract"] == k for x in rows.values())
                 for k in ("include", "uncertain")}
    actual_ft = {k: sum(x["full_text"] == k for x in rows.values())
                 for k in ("include", "exclude", "awaiting_text", "uncertain", "pending")}
    generated = flow["screening_by_track"]["empirical"]
    if (any(actual_ta[k] != generated["title_abstract"][k] for k in actual_ta)
            or any(actual_ft[k] != generated["full_text"][k] for k in actual_ft)):
        raise ValueError("STALE_EXPORT: generated screening flow differs from canonical four-candidate records")
    if any(flow.get(k) != 0 for k in ("included_publications", "included_studies", "experiments", "samples")):
        # A future legitimate corpus change requires a separately reviewed, updated scoped audit.
        raise ValueError("Corpus now contains records outside this zero-admission checkpoint; refresh audit")
    return {
        "issue": 6,
        "protocol": PROTOCOL,
        "frozen_publication_cutoff": "2026-10-04",
        "canonical_title_abstract": 4,
        "canonical_full_text_decisions": sum(x["full_text"] != "not_recorded" for x in rows.values()),
        "canonical_full_text_includes": actual_ft["include"],
        "canonical_eligible_studies": flow["included_studies"],
        "canonical_experiments": flow["experiments"],
        "canonical_samples": flow["samples"],
        "theoretical_full_text_includes": flow["screening_by_track"]["theoretical"]["full_text"]["include"],
        "source_gate_rows": rows,
        "scientific_acceptance": "not_evaluated",
        "note": "Static source/decision/manifest checks; no original PDF hash, reviewer independence or scientific eligibility certified.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = evaluate(*canonical_inputs(args.root))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
