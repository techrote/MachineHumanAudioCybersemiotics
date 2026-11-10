"""Live R006 nine-publication *admission preflight*, not a scientific decision.

Reads canonical SCR/SRC/AID and Integration's serialized evidence-flow. It neither
writes shared manifests nor substitutes for tools/validate.py, full unit tests,
fixture reproducibility, source verification or scientific adjudication.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = "MHAC-Track-E-frozen-v1-2026-10-13"

# Initial canonical tranche plus five already accepted successor title screens.
# New source batches may be added without changing the historical nine.
CASES = {
    "SRC-REL-BECKER-2025": ("SCR-R006-REL-BECKER-2025", "10.1145/3706066", "related"),
    "SRC-REL-ROMEO-2025": ("SCR-R006-REL-ROMEO-2025", "10.1145/3711938", "related"),
    "SRC-REL-KUHNE-2020": ("SCR-R006-REL-KUHNE-2020", "10.3389/fnbot.2020.593732", "related"),
    "SRC-REL-ROMEO-2023": ("SCR-R006-REL-ROMEO-2023", "10.1109/ro-man57019.2023.10309631", "related"),
    "SRC-R006-NEES-2016-MEMORY": ("SCR-R006-NEES-2016-MEMORY", "10.1177/0018720816629279", "identity"),
    "SRC-R006-EDWORTHY-2014-LEARNING": ("SCR-R006-EDWORTHY-2014-LEARNING", "10.1016/j.apergo.2013.10.003", "identity"),
    "SRC-R006-F-ARRABITO-URGENCY": ("SCR-R006-ARRABITO-2004-URGENCY", "10.1080/0014013042000193282", "identity"),
    "SRC-R006-H-SABIC-UNDERSTANDING": ("SCR-R006-SABIC-2021-NOISE", "10.1177/0018720819879311", "identity"),
    "SRC-R006-E-STEVENS-INFORMATIVE": ("SCR-R006-STEVENS-2009-WARNING", "10.2478/v10053-008-0064-6", "identity"),
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def latest(obj, expected_id, kind):
    if not obj or obj.get("id") != expected_id or obj.get("kind") != kind or obj.get("synthetic") is not False:
        raise ValueError("missing, synthetic or wrong canonical record: " + expected_id)
    revs = obj["revisions"]
    if [r["rev"] for r in revs] != list(range(1, len(revs) + 1)):
        raise ValueError("noncontiguous revision history: " + expected_id)
    for i, rev in enumerate(revs):
        actor = rev.get("actor", {})
        if actor.get("kind") not in ("agent", "human") or not actor.get("id"):
            raise ValueError("missing genuine decision actor: " + expected_id)
        when = datetime.fromisoformat(rev["at"].replace("Z", "+00:00"))
        if when.utcoffset() is None:
            raise ValueError("decision timestamp lacks UTC offset: " + expected_id)
        if i and when < datetime.fromisoformat(revs[i - 1]["at"].replace("Z", "+00:00")):
            raise ValueError("backdated revision: " + expected_id)
    # Previously accepted AI decisions cannot be re-authored as human.
    if revs[0]["actor"]["kind"] != "agent":
        raise ValueError("historical AI assessor was changed: " + expected_id)
    return revs[-1]


def inputs(root=ROOT):
    sources, ta, ft = {}, {}, {}
    for source_id, (prefix, _doi, directory) in CASES.items():
        sdir = (root / "research/sources/related/records" if directory == "related"
                else root / "research/registry/identity/records")
        sources[source_id] = load(sdir / (source_id + ".json"))
        rdir = root / "research/screening/records"
        ta[source_id] = load(rdir / (prefix + "-TA.json"))
        ft[source_id] = load(rdir / (prefix + "-FT.json"))
    reading_dir = root / "research/screening/records"
    aids = {obj["id"]: obj for obj in (load(p) for p in reading_dir.glob("AID-*.json"))}
    flow = load(root / "research/registry/generated/evidence-flow.json")
    return sources, ta, ft, aids, flow


def evaluate(sources, ta, ft, aids, flow):
    rows, actual_ta, actual_ft = {}, {}, {}
    scopes = [s for s in flow.get("screening_coverage", {}).get("decision_scopes", [])
              if s.get("track") == "empirical" and s.get("protocol_version") == PROTOCOL]
    published = {}
    for scope in scopes:
        for item in scope.get("sources", []):
            sid = item["source_id"]
            if sid in published:
                raise ValueError("STALE_EXPORT duplicate source: " + sid)
            published[sid] = item

    for sid, (prefix, doi, _dir) in CASES.items():
        sr = latest(sources[sid], sid, "source")
        s = sr["data"]
        ids = {i["value"].lower() for i in s["identifiers"]
               if i["scheme"] == "doi" and i["status"] == "verified"}
        if s.get("validity") != "active" or doi not in ids:
            raise ValueError("DOI, invalidated source, or publication identity: " + sid)
        t = latest(ta[sid], prefix + "-TA", "screening")
        f = latest(ft[sid], prefix + "-FT", "screening")
        # Immutable historical first passes had real AI actors; later legitimate
        # human review is possible only in newly attributed revisions.
        if t["data"]["source_ref"]["id"] != sid or f["data"]["source_ref"]["id"] != sid:
            raise ValueError("source/publication identity collision: " + sid)
        tr, fr = t["data"]["source_ref"]["rev"], f["data"]["source_ref"]["rev"]
        if not any(x["rev"] == tr for x in sources[sid]["revisions"]) or not any(
            x["rev"] == fr for x in sources[sid]["revisions"]
        ):
            raise ValueError("source correction invalidates pin: " + sid)
        if (t["data"]["stage"] != "title_abstract" or f["data"]["stage"] != "full_text"
                or t["data"]["track"] != "empirical" or f["data"]["track"] != "empirical"
                or t["data"]["protocol_version"] != PROTOCOL
                or f["data"]["protocol_version"] != PROTOCOL):
            raise ValueError("incorrect track, stage or protocol: " + sid)
        if t["data"]["decision"] not in ("include", "uncertain"):
            raise ValueError("unjustified FT after title exclusion: " + sid)
        if datetime.fromisoformat(f["at"].replace("Z", "+00:00")) < datetime.fromisoformat(
            t["at"].replace("Z", "+00:00")
        ):
            raise ValueError("full text precedes title decision: " + sid)
        decision = f["data"]["decision"]
        if decision not in ("include", "exclude", "pending", "awaiting_text", "uncertain"):
            raise ValueError("invalid full-text transition: " + sid)
        manifests = {m["id"]: m for m in next(x for x in sources[sid]["revisions"]
                                               if x["rev"] == fr)["data"].get("manifestations", [])}
        if decision in ("include", "exclude"):
            if fr != sr["rev"]:
                raise ValueError("source correction invalidates final full-text decision: " + sid)
            if not manifests or not f["data"]["reading_refs"]:
                raise ValueError("final FT needs manifested performed reading: " + sid)
            for ref in f["data"]["reading_refs"]:
                aid = latest(aids.get(ref["id"]), ref["id"], "assistance")
                if aid["rev"] != ref["rev"]:
                    raise ValueError("stale performed-reading revision: " + sid)
                d = aid["data"]
                if (d.get("subtype") != "reading" or d.get("status") != "performed"
                        or d.get("source_ref") != {"id": sid, "rev": fr}
                        or d.get("manifestation_id") not in manifests
                        or not d.get("ranges")):
                    raise ValueError("unverified reading or manifestation: " + sid)
                stamp = d.get("performed_at", {})
                if stamp.get("state") != "known" or datetime.fromisoformat(
                    stamp["value"].replace("Z", "+00:00")
                ) > datetime.fromisoformat(f["at"].replace("Z", "+00:00")):
                    raise ValueError("unperformed or postdated reading: " + sid)
                m = manifests[d["manifestation_id"]]
                lo = 0 if m["coordinate"] == "pdf_page_0based" else 1
                hi = m["extent"] - 1 if lo == 0 else m["extent"]
                if any(not (lo <= a <= b <= hi) for a, b in d["ranges"]):
                    raise ValueError("reading exceeds manifested bounds: " + sid)
        row = published.get(sid)
        if not row or row.get("title_abstract") != t["data"]["decision"] or row.get("full_text") != decision:
            raise ValueError("STALE_EXPORT canonical source decision: " + sid)
        actual_ta[t["data"]["decision"]] = actual_ta.get(t["data"]["decision"], 0) + 1
        actual_ft[decision] = actual_ft.get(decision, 0) + 1
        gate = ("accepted_exclusion_never_counts_as_study" if decision == "exclude"
                else "accepted_inclusion_requires_scientific_sample_review" if decision == "include"
                else "original_report_unavailable" if decision == "awaiting_text"
                else "source_owner_register_manifestation" if not manifests
                else "r006_full_text_adjudication")
        rows[sid] = {"doi": doi, "ta": t["data"]["decision"], "full_text": decision,
                     "source_revision": sr["rev"], "registered_manifestations": len(manifests),
                     "last_decision_actor": f["actor"]["id"], "last_decision_at": f["at"],
                     "gate": gate}
    # Exact for these nine, lower bound for global totals (future legitimate batches).
    totals = flow["screening_by_track"]["empirical"]
    for stage, counts in (("title_abstract", actual_ta), ("full_text", actual_ft)):
        if any(totals[stage].get(k, 0) < n for k, n in counts.items()):
            raise ValueError("STALE_EXPORT global screening " + stage)
    for key in ("included_publications", "included_studies", "experiments", "samples",
                "selected_theoretical_publications"):
        val = flow.get(key)
        if type(val) is not int or val < 0:
            raise ValueError("STALE_EXPORT invalid corpus count: " + key)
    if flow["included_publications"] < actual_ft.get("include", 0):
        raise ValueError("STALE_EXPORT full-text includes not in admitted publication count")
    return {
        "scope": "nine_existing_canonical_publications_not_all_discovery_occurrences",
        "frozen_cutoff": "2026-10-04",
        "canonical_ta_in_scope": len(rows),
        "canonical_ft_in_scope": actual_ft,
        "global_admitted_publications": flow["included_publications"],
        "global_included_studies": flow["included_studies"],
        "global_experiments": flow["experiments"],
        "global_samples": flow["samples"],
        "global_selected_track_g": flow["selected_theoretical_publications"],
        "cases": rows,
        "scientific_admission_evaluated": False,
        "note": "This is structural source/decision/export preflight, not original byte custody, independent review or scientific screening."
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(*inputs()), indent=2, sort_keys=True))
