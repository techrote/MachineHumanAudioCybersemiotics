"""Check R006's dated four-publication full-text admission gates against canonical v1 records.

Read-only. This validates traceability and eligibility preconditions, NOT scientific
truth, the original publication bytes, or registry/export admission. No human
review, sample independence or canonical full-text decision is asserted.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEDGER = HERE / "QUALIFICATION.json"
SOURCES = ROOT / "research/sources/related/records"
SCREEN = ROOT / "research/screening/records"
LATER = ROOT / "research/screening/r006_kuhne_e2_laterpass_20261110/RECHECK.json"
FIRST_FT = ROOT / "research/screening/r006_fulltext_e2_review_20261110/DECISIONS.json"

DOIS = {
    "SRC-REL-BECKER-2025": "10.1145/3706066",
    "SRC-REL-ROMEO-2025": "10.1145/3711938",
    "SRC-REL-KUHNE-2020": "10.3389/fnbot.2020.593732",
    "SRC-REL-ROMEO-2023": "10.1109/ro-man57019.2023.10309631",
}
TA = {"SRC-REL-BECKER-2025": "include", "SRC-REL-ROMEO-2025": "include",
      "SRC-REL-KUHNE-2020": "uncertain", "SRC-REL-ROMEO-2023": "uncertain"}
PROPOSALS = {
    "SRC-REL-BECKER-2025": ("include_main_phase_provisional_only",
                            "blocked_on_source_manifestation_before_canonical_FT"),
    "SRC-REL-ROMEO-2025": ("include_provisional_only",
                           "blocked_on_source_manifestation_and_stable_article_access"),
    "SRC-REL-KUHNE-2020": ("exclude",
                          "source_located_candidate_for_integrator_scr_admission_not_yet_canonical"),
    "SRC-REL-ROMEO-2023": ("awaiting_text", "blocked_on_original_report_access"),
}

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def inspect(ledger: dict, *, sources: dict | None = None, titles: dict | None = None,
            later: dict | None = None, first_ft: dict | None = None) -> dict:
    """Fail closed on source pins, historical decisions, access and stage inflation."""
    if (ledger.get("issue") != 6 or ledger.get("cutoff") != "2026-10-04"
            or ledger.get("kind") != "noncanonical_source_and_admission_qualification"
            or ledger.get("observed_date_utc") != "2026-11-10"):
        raise ValueError("Issue, frozen cutoff or dated noncanonical stage changed")
    agent = ledger.get("actor", {})
    if (agent.get("kind") != "agent" or agent.get("human") is not False
            or agent.get("independent_human") is not False
            or ledger.get("exact_http_response_timestamp_captured") is not False):
        raise ValueError("False human, independence or HTTP timestamp assertion")
    expected = dict(title_abstract=4, ta_include_to_ft=2, ta_uncertain_to_ft=2,
                    full_text=0, studies=0, experiments=0, samples=0,
                    selected_empirical_publications=0, selected_theoretical_corpus=0)
    if ledger.get("canonical_checkpoint") != expected:
        raise ValueError("Canonical count inflation or dated checkpoint drift")
    rows = ledger.get("cases", [])
    if len(rows) != 4 or {r.get("source_id") for r in rows} != set(DOIS):
        raise ValueError("Missing, duplicate or unrelated four-candidate scope")
    sources = sources if sources is not None else {
        sid: load(SOURCES / (sid + ".json")) for sid in DOIS
    }
    titles = titles if titles is not None else {
        sid: load(SCREEN / ("SCR-R006-" + sid.removeprefix("SRC-") + "-TA.json"))
        for sid in DOIS
    }
    later = later if later is not None else load(LATER)
    first_ft = first_ft if first_ft is not None else load(FIRST_FT)
    if (later["result"]["rechecked_proposed_fulltext_decision"] != "exclude"
            or later["result"]["rechecked_frozen_reason"] != "E-NOT-MACHINE-MESSAGE"
            or later["agent"]["independent_human_reviewer"] is not False
            or later["agent"]["blinded_to_prior_screening"] is not False
            or first_ft["counts"]["canonical_screening_records_added"] != 0):
        raise ValueError("False exclusion recheck or earlier canonical promotion")
    first_k = next(r for r in first_ft["source_reviews"]
                   if r["source_ref"]["id"] == "SRC-REL-KUHNE-2020")
    if (first_k["proposed_decision"] != "exclude"
            or first_k["rule_failure"] != "E-NOT-MACHINE-MESSAGE"):
        raise ValueError("Unreviewed changed original full-text exclusion")
    ready, gated = [], []
    for row in rows:
        sid = row["source_id"]
        if row.get("source_rev") != 1 or row.get("doi") != DOIS[sid]:
            raise ValueError("Publication source revision or DOI collision")
        proposal, status = PROPOSALS[sid]
        if (row.get("proposed_full_text_decision") != proposal
                or row.get("disposition") != status
                or row.get("ta_decision") != TA[sid]
                or row.get("ta_id") != "SCR-R006-" + sid.removeprefix("SRC-") + "-TA"
                or row.get("track") != "empirical"):
            raise ValueError("Forbidden FT transition or TA mismatch")
        source = sources[sid]
        if (source.get("id") != sid or source.get("synthetic") is not False
                or source.get("kind") != "source"):
            raise ValueError("Publication identity or synthetic truth-label conflict")
        revision = next((r for r in source["revisions"] if r["rev"] == 1), None)
        if not revision or revision["data"]["validity"] != "active":
            raise ValueError("Missing or invalidated historical source revision")
        identifiers = {i["value"].lower() for i in revision["data"]["identifiers"]
                       if i["scheme"] == "doi" and i["status"] == "verified"}
        if DOIS[sid] not in identifiers:
            raise ValueError("Source identity has no verified matching DOI")
        ta = titles[sid]
        if (ta.get("id") != row["ta_id"] or ta.get("kind") != "screening"
                or len(ta["revisions"]) != 1):
            raise ValueError("Canonical TA missing or rewritten")
        decision = ta["revisions"][0]["data"]
        if (decision["source_ref"] != {"id": sid, "rev": 1}
                or decision["stage"] != "title_abstract"
                or decision["track"] != "empirical"
                or decision["decision"] != TA[sid]):
            raise ValueError("Canonical TA identity, stage or decision drift")
        ev = row["source_access"]
        url = urlsplit(ev["url"])
        if url.scheme != "https" or not url.hostname or not ev["reading_scope"]:
            raise ValueError("Missing lawful source route or exact reading extent")
        if (ev["whole_article_read"] is not False or ev["sound_played"] is not False
                or ev["local_original_pdf_bytes_retained"] is not False
                or ev["original_pdf_sha256_reverified"] is not False):
            raise ValueError("Fabricated full text, audio or original-byte verification")
        manifest = row["registered_manifestation"]
        pinned = revision["data"]["manifestations"]
        if sid == "SRC-REL-KUHNE-2020":
            if (manifest is None or len(pinned) != 1 or
                    manifest["id"] != "FRONTIERS-PDF" or
                    manifest["sha256_inherited_from_R004"] != pinned[0]["sha256"] or
                    manifest["extent"] != pinned[0]["extent"] or
                    manifest["coordinate"] != pinned[0]["coordinate"] or
                    manifest["hash_reverified_this_run"] is not False):
                raise ValueError("Incorrect inherited Kühne manifestation claim")
            pages = ev["file_pages_1based"]
            if pages != [1, 4, 5] or any(p < 1 or p > manifest["extent"] for p in pages):
                raise ValueError("Reading locator not supported by publisher PDF extent")
            recheck = row["separate_later_recheck"]
            if (recheck is None or recheck["performed_at_utc"] != later["performed_at_utc"]
                    or recheck["outcome"] != "E2_no"
                    or recheck["human"] is not False
                    or recheck["blinded"] is not False):
                raise ValueError("Later exclusion verification missing or impersonated")
            ready.append(sid)
        else:
            if manifest is not None or pinned or ev["file_pages_1based"]:
                raise ValueError("Unregistered manifestation or invented page ranges")
            if row["separate_later_recheck"] is not None:
                raise ValueError("Invented later pass")
            gated.append(sid)
        if not row["gate_to_close"] or not row["source_observation"]:
            raise ValueError("Missing actionable source-integrity handoff")
    return {"canonical_title_abstract_at_base": 4,
            "canonical_full_text_at_base": 0,
            "source_located_ft_exclusion_candidate_pending_integration": len(ready),
            "blocked_ft_candidates": len(gated),
            "proposed_independent_studies_or_samples": 0}

def main() -> None:
    print(json.dumps(inspect(load(LEDGER)), sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
