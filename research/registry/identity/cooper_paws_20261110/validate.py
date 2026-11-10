"""Fail-closed guard for source-limited, noncanonical Cooper PAWS identity analysis.

Run standalone: python research/registry/identity/cooper_paws_20261110/validate.py
No source files, screening records or shared aggregates are modified.
"""
import json
from pathlib import Path

PATH = Path(__file__).with_name("EVIDENCE.json")
KEYS = ("cooper_2020_paper", "cooper_2020_thesis", "cooper_2021_paper")
PHASES = {
    "expert_panel": (32, set(KEYS)),
    "prototype_pilot": (5, set(KEYS[1:])),
    "end_user_intervention": (205, set(KEYS[1:])),
}
DOIS = {"cooper_2020_paper": "10.36965/ojakm.2020.8(2)107-121",
        "cooper_2020_thesis": None,
        "cooper_2021_paper": "10.1108/ocj-03-2021-0006"}


def validate(data):
    if (data.get("kind") != "r006_noncanonical_cross_publication_identity_adjudication_v1"
        or data.get("issue") != 6 or data.get("evidence_cutoff") != "2026-10-04"
        or data.get("actor", {}).get("kind") != "agent"
        or data["actor"].get("review_type", "").find("not human") < 0):
        raise ValueError("Unqualified identity scope, cutoff or reviewer")
    admission = data.get("canonical_admission", {})
    if (any(admission.get(k) != 0 for k in ("screening_records_added",
           "study_records_added", "sample_records_added"))
        or admission.get("selected_corpus_ready") is not False
        or admission.get("independent_human_screening") is not False
        or admission.get("manifest_or_R005_history_modified") is not False):
        raise ValueError("Illegal canonical or human promotion")
    sources = data.get("source_consultation", [])
    if len(sources) != 3 or {s.get("key") for s in sources} != set(KEYS):
        raise ValueError("Wrong or repeated publication identities")
    for s in sources:
        key = s["key"]
        if (s.get("doi", "").lower() if s.get("doi") else None) != DOIS[key]:
            raise ValueError("DOI changed, aliased or invented")
        if (s.get("original_pdf_bytes_hashed") is not False
            or s.get("full_item_read") is not False
            or s.get("source_correction_checked") is not False
            or not s.get("locators") or not s.get("observations")
            or any(not u.startswith("https://") for u in s.get("urls", []))):
            raise ValueError("Unsupported reading or source verification")
        if key == "cooper_2020_paper":
            if "pp.110-111" not in s.get("reading_extent", ""):
                raise ValueError("Source-located PDF page evidence lost")
        elif "abstract" not in s.get("reading_extent", "").lower():
            raise ValueError("Unread full text promoted")
    phases = data.get("cross_report_phase_map", [])
    if len(phases) != 3 or {p.get("phase") for p in phases} != set(PHASES):
        raise ValueError("Phase omitted or duplicated")
    for p in phases:
        n, expected = PHASES[p["phase"]]
        if (p.get("n_as_reported") != n or set(p.get("reports", [])) != expected
            or p.get("overlap_status") != "probable_reuse_not_verified"
            or p.get("independent_sample_status") != "unresolved_do_not_count"
            or not p.get("evidence") or not p.get("inference")):
            raise ValueError("Participant overlap or repeated measures falsely adjudicated")
    screens = data.get("track_e_provisional", [])
    if len(screens) != 3 or {x.get("publication") for x in screens} != set(KEYS):
        raise ValueError("Missing first-stage eligibility scope")
    if any(x.get("decision") != "uncertain" or "not_canonical" not in x.get("stage", "")
           or not x.get("reason") for x in screens):
        raise ValueError("Premature scientific eligibility")
    decision = data.get("decision", {})
    if (decision.get("publication_count") != 3
        or decision.get("named_procedural_phases") != 3
        or decision.get("independent_empirical_sample_count") != "not_established"
        or decision.get("automatic_doi_aliasing_permitted") is not False
        or decision.get("admissibility") != "R006_source_identity_handoff_only_not_selected_corpus"
        or not decision.get("next_action")):
        raise ValueError("Overcount, DOI collision or selected-corpus inflation")
    if len(data.get("scientific_limits", [])) < 5:
        raise ValueError("Loss of access/sampling limitations")
    return True


if __name__ == "__main__":
    validate(json.loads(PATH.read_text(encoding="utf-8")))
    print("Cooper PAWS noncanonical identity evidence consistent; 3 reports, 3 phases, 0 admitted samples")
