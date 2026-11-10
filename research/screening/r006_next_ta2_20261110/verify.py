"""R006 source-identity and first-revision guard for the next two title/abstract records.

This is not corpus/export admission and does not assess scientific correctness.
Later append-only revisions are allowed. Integration owns the generated exports.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCES = ROOT / "research/registry/identity/records"
SCREENS = ROOT / "research/screening/records"

CASES = {
    "SCR-R006-SABIC-2021-NOISE-TA": (
        "SRC-R006-H-SABIC-UNDERSTANDING",
        "10.1177/0018720819879311",
        {"HIT-R005R-C1RECOVERY-EQ1-00046"},
    ),
    "SCR-R006-ARRABITO-2004-URGENCY-TA": (
        "SRC-R006-F-ARRABITO-URGENCY",
        "10.1080/0014013042000193282",
        {"HIT-R005R-C1LOAD-EQ1-01348", "HIT-R005R-C1RECOVERY-EQ1-00109",
         "HIT-R005R-C1RECOVERY-EQ2-00074"},
    ),
}
ACTOR_ID = "gpt6-r006-ta-noise-urgency-20261110"
PROTOCOL = "MHAC-Track-E-frozen-v1-2026-10-13"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify(records=None, sources=None):
    """Verify only authored historical TA decisions, not generated corpus acceptance."""
    records = {} if records is None else records
    sources = {} if sources is None else sources
    source_ids = set()
    dois = set()
    for scr_id, (src_id, doi, hits) in CASES.items():
        scr = records.get(scr_id)
        if scr is None:
            scr = read(SCREENS / (scr_id + ".json"))
        if (scr["kind"] != "screening" or scr["synthetic"] is not False
                or scr["id"] != scr_id or scr["issue"] != 6):
            raise ValueError("Incorrect screening record identity")
        first = scr["revisions"][0]
        d = first["data"]
        if (first["rev"] != 1 or first["actor"]["kind"] != "agent"
                or first["actor"]["id"] != ACTOR_ID
                or first["at"] != "2026-11-10T15:33:58.305Z"):
            raise ValueError("Historical AI actor/time changed")
        if (d["source_ref"] != {"id":src_id, "rev":1}
                or first["basis"] != [{"id":src_id, "rev":1}]
                or d["protocol_version"] != PROTOCOL
                or d["track"] != "empirical" or d["stage"] != "title_abstract"
                or d["decision"] != "include"
                or d["reading_refs"] or d["review_refs"]):
            raise ValueError("Screening scope, source pin or review claim changed")
        if ("No human" not in d["access_limitation"]
                and "no human" not in d["access_limitation"]):
            raise ValueError("Missing human-review limitation")
        src = sources.get(src_id)
        if src is None:
            src = read(SOURCES / (src_id + ".json"))
        if src["id"] != src_id or src["synthetic"] is not False:
            raise ValueError("Incorrect source identity")
        source_rev1 = next((r for r in src["revisions"] if r["rev"] == 1), None)
        if source_rev1 is None or source_rev1["data"]["validity"] != "active":
            raise ValueError("Source revision is missing or invalid")
        verified = {
            i["value"].lower() for i in source_rev1["data"]["identifiers"]
            if i["scheme"] == "doi" and i["status"] == "verified"
        }
        basis_hits = {x["id"] for x in source_rev1["basis"] if x["id"].startswith("HIT-")}
        if doi not in verified or hits != basis_hits:
            raise ValueError("DOI or original discovery-hit provenance mismatch")
        if doi not in d["access_limitation"]:
            raise ValueError("Publisher DOI locator missing")
        if source_rev1["data"]["source_type"] not in ("article", "conference_paper"):
            raise ValueError("Publication/report identity not corroborated")
        source_ids.add(src_id)
        dois.add(doi)
    if len(source_ids) != 2 or len(dois) != 2:
        raise ValueError("Publication collision")
    return {
        "canonical_ta_files_authored": len(CASES),
        "scientifically_admitted_studies": 0,
        "scientifically_admitted_experiments": 0,
        "scientifically_admitted_samples": 0,
        "generated_exports_verified": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
