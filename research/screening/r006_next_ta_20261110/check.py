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

def verify_authored_scrs(registry=None, packet=None):
    """Check authored canonical SCR shape, never certify generated-flow admission."""
    packet = load(PACKET) if packet is None else packet
    proposed = packet["post_preparation_registration"]
    if proposed["actor_kind"] != "agent" or proposed["exports_regenerated"] or proposed["accepted_main"]:
        raise ValueError("False actor attribution or admission claim")
    observed = []
    for row in proposed["canonical_scrs_authored"]:
        record = ((registry or {}).get(row["id"]) if registry is not None else None)
        if record is None:
            record = load(ROOT / "research/screening/records" / (row["id"] + ".json"))
        if record["id"] != row["id"] or record["kind"] != "screening" or record["synthetic"] is not False:
            raise ValueError("Authored canonical screening identity mismatch")
        if len(record["revisions"]) != 1:
            raise ValueError("Unreconciled screening revision history")
        r = record["revisions"][0]
        data = r["data"]
        if (r["rev"] != 1 or r["at"] != proposed["at_utc"] or
                r["actor"]["kind"] != "agent" or r["actor"]["id"] != proposed["actor_id"]):
            raise ValueError("False canonical registration actor/time")
        if (data["source_ref"] != {"id":row["source_id"], "rev":1} or
                data["stage"] != "title_abstract" or data["track"] != "empirical" or
                data["decision"] != row["decision"] or
                data["protocol_version"] != "MHAC-Track-E-frozen-v1-2026-10-13" or
                data["reading_refs"] or data["review_refs"]):
            raise ValueError("Invalid or falsely reviewed canonical TA stage")
        observed.append(row["id"])
    return {"authored_unexported":len(observed),"accepted_main_admissions":0,"ids":observed}
