"""Reproducibility and fail-closed identity guards for noncanonical R006 Romeo handoff.

This is a provenance precheck only. It does not add live mhac-records/1 objects
or decide whether any experiment is an independently eligible sample.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = Path(__file__).with_name("EVIDENCE.json")
SOURCES = ROOT / "research/sources/related/records"
DOIS = {
    "SRC-REL-ROMEO-2023": "10.1109/ro-man57019.2023.10309631",
    "SRC-REL-ROMEO-2025": "10.1145/3711938",
}
EXPECTED_EXPERIMENTS = {
    "ROMEO23-OS1", "ROMEO23-OS2", "ROMEO25-PILOT", "ROMEO25-MAZE"
}
ALLOWED_E2 = {
    "unresolved_abstract_only", "unresolved_until_supplement_and_paper_read",
    "provisional_robot_navigation_message"
}


def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def read_sources() -> dict:
    return {
        sid: json.loads((SOURCES / (sid + ".json")).read_text(encoding="utf-8"))
        for sid in DOIS
    }


def check(ledger: dict | None = None, sources: dict | None = None) -> dict:
    doc = load() if ledger is None else ledger
    srcs = read_sources() if sources is None else sources
    if (doc.get("issue") != 6 or doc.get("cutoff") != "2026-10-04"
            or doc.get("type") != "noncanonical_preselection_publication_experiment_sample_boundary"
            or doc.get("produced_on") != "2026-11-10"
            or doc.get("actor", {}).get("kind") != "agent"
            or doc.get("review_status") != "single_agent_no_independent_human_review"
            or doc.get("source_bytes_retained") is not False):
        raise ValueError("Provenance or frozen source limitations drifted")
    rows = doc["publications"]
    if (len(rows) != 2 or {p["id"] for p in rows} != set(DOIS)
            or len({p["doi"].lower() for p in rows}) != 2):
        raise ValueError("Publication identity collision or unreviewed item")
    for p in rows:
        sid = p["id"]
        if (p["doi"].lower() != DOIS[sid] or p["rev"] != 1
                or p["manuscript_full_text_read"] is not False):
            raise ValueError("DOI/pinned reading status drift: " + sid)
        src = srcs[sid]
        if (src.get("id") != sid or src.get("kind") != "source"
                or src.get("synthetic") is not False):
            raise ValueError("Source ID/type collision: " + sid)
        revs = src["revisions"]
        # Fail closed on later source corrections: this audit has not examined them.
        if len(revs) != 1 or revs[0]["rev"] != p["rev"]:
            raise ValueError("Source revision changed; re-review required: " + sid)
        d = revs[0]["data"]
        if d["validity"] != "active" or d["metadata_status"] != "verified":
            raise ValueError("Corrected/inactive source needs re-review: " + sid)
        verified = {i["value"].lower() for i in d["identifiers"]
                    if i["scheme"] == "doi" and i["status"] == "verified"}
        if DOIS[sid] not in verified:
            raise ValueError("Verified DOI drifted: " + sid)
    evidence = doc["evidence"]
    ev = {e["id"]: e for e in evidence}
    if (len(evidence) != 4 or len(ev) != 4
            or set(ev) != {"E23-ABSTRACT", "E23-SUPPLEMENT",
                           "E25-METHODS", "E25-REFERENCE"}):
        raise ValueError("Missing/duplicated source evidence")
    for item in evidence:
        if (item["source_id"] not in DOIS or not item["url"].startswith("https://")
                or not item["locator"] or item["bytes_verified"] is not False):
            raise ValueError("Invented source file/hash or unsupported locator")
    if ev["E23-ABSTRACT"]["reading"] != "abstract_only" or ev["E23-SUPPLEMENT"]["reading"] != "metadata_only":
        raise ValueError("2023 full-text access incorrectly promoted")
    if ev["E25-METHODS"]["reading"] != "selected_sections_no_numeric_extraction":
        raise ValueError("2025 evidence scope incorrectly promoted")
    items = doc["experiment_candidates"]
    if len(items) != 4 or {x["id"] for x in items} != EXPECTED_EXPERIMENTS:
        raise ValueError("Experiment candidate identity drift")
    for item in items:
        if (item["publication"] not in DOIS or item["reference"] not in ev
                or ev[item["reference"]]["source_id"] != item["publication"]
                or item["e2"] not in ALLOWED_E2
                or item["sample_relation"] != "unknown"
                or item["counted_independent_sample"] is not False):
            raise ValueError("Unsupported candidate-to-sample transition")
        if (item["id"].startswith("ROMEO23") and item["n_reported"] is not None):
            raise ValueError("Invented 2023 participant count")
    for exp_id, n in (("ROMEO25-PILOT", 50), ("ROMEO25-MAZE", 60)):
        if next(x for x in items if x["id"] == exp_id)["n_reported"] != n:
            raise ValueError("2025 author's reported participants misrepresented")
    ia = doc["identity_assessment"]
    if (ia["publications"] != "distinct_verified_dois"
            or ia["family_relation"] != "unknown_not_a_confirmed_conference_extension"
            or ia["stimuli"] != "candidate_overlap_not_verified"
            or ia["samples"] != "unknown_not_independent_not_shared"
            or ia["study_relationship"] != "unknown"
            or ia["no_silent_collapse"] is not True):
        raise ValueError("Unproven publication/study/stimulus/sample identity promoted")
    if doc["decisions"] != {
        "new_title_abstract": 0, "new_full_text": 0,
        "new_canonical_scr": 0, "admitted_studies": 0,
        "admitted_independent_samples": 0, "selected_corpus": False
    }:
        raise ValueError("Preselection evidence cannot claim canonical admission")
    if doc["verification_gates"] != {
        "paper_2023_full_text": False, "supplement_2023_pdf_read": False,
        "paper_2025_source_bytes_hash": False, "paper_2025_page_image": False,
        "participant_overlap_crosschecked": False,
        "independent_human_screening": False
    }:
        raise ValueError("Source/reviewer verification gate was silently satisfied")
    return {"publications_checked": 2, "experiment_candidates": 4,
            "verified_independent_samples": 0, "canonical_screenings_added": 0}


if __name__ == "__main__":
    print(json.dumps(check(), sort_keys=True))
