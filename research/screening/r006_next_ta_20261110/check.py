"""R006 two-source primary-abstract PREPARATION regression; not corpus admission."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKET = ROOT / "research/screening/r006_next_ta_20261110/DECISIONS.json"
SOURCES = ROOT / "research/registry/identity/records"

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def verify(packet=None, source_lookup=None):
    packet = load(PACKET) if packet is None else packet
    if packet["status"] != "prepared_noncanonical_do_not_count_as_admitted":
        raise ValueError("Do not present preparation as canonical admission")
    if (packet["added_canonical_screening_records"] != 0 or
        any(packet[k] != 0 for k in ("added_studies", "added_experiments", "added_samples", "selected_track_e", "selected_track_g"))):
        raise ValueError("Prepared-only packet may not count as selected evidence")
    if packet["human_second_screener"] is not False or packet["decision_actor"]["kind"] != "agent":
        raise ValueError("Untruthful screening actor or human claim")
    if packet["search_cutoff"] != "2026-10-04":
        raise ValueError("Frozen search cutoff drift")
    cases = packet["cases"]
    if len(cases) != 2 or len({x["doi"] for x in cases}) != 2 or len({x["source_id"] for x in cases}) != 2:
        raise ValueError("Source/DOI count and identity conflict")
    for case in cases:
        src = (source_lookup or {}).get(case["source_id"])
        if src is None: src = load(SOURCES / (case["source_id"] + ".json"))
        if src["synthetic"] is not False or src["kind"] != "source" or src["id"] != case["source_id"]:
            raise ValueError("Missing or synthetic publication identity")
        rev = next((r for r in src["revisions"] if r["rev"] == case["source_rev"]), None)
        if rev is None or rev["data"]["validity"] != "active":
            raise ValueError("Unknown source revision or invalid source")
        ids = {i["value"].lower() for i in rev["data"]["identifiers"]
               if i["scheme"] == "doi" and i["status"] == "verified"}
        if (case["doi"].lower() not in ids or
            " ".join(rev["data"]["title"].split()).casefold().rstrip(".") !=
            " ".join(case["title"].split()).casefold().rstrip(".")):
            raise ValueError("Source title/DOI mismatch")
        basis = {b["id"] for b in rev["basis"] if b["id"].startswith("HIT-")}
        if not set(case["source_discovery_hit_ids"]).issubset(basis) or not case["source_discovery_hit_ids"]:
            raise ValueError("Unsubstantiated original discovery path")
        if (case["stage"] != "title_abstract" or case["track"] != "empirical"
                or case["decision"] not in ("include", "uncertain", "exclude")
                or case["decision_scope"] != "proceed_to_full_text_only"
                or set(case["rule_assessment"]) != {"E1", "E2", "E3", "E4", "E5", "E6"}):
            raise ValueError("Unfrozen eligibility or improper stage")
        if not case["original_source_url"].startswith("https://") or "Abstract" not in case["read_locator"]:
            raise ValueError("No original abstract reading locator")
        if (case["original_fulltext_obtained"] or case["original_pdf_bytes_retained"]
                or case["audio_heard"] or case["original_pdf_hash"] is not None):
            raise ValueError("Unverified original text/audio/bytes claim")
    return {"prepared_only":len(cases), "admitted":0, "ids":[c["source_id"] for c in cases]}

if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
