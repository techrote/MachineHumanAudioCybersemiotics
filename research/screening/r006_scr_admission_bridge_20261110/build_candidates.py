"""R006: schema-valid *candidate* title/abstract SCR records, not registry admission.

Replays the accepted 2026-11-10 four-source first-pass ledger. Registration,
review/adjudication, generated manifests and FT decisions belong to integration.
The tool refuses to invent a retrospective record timestamp or human reviewer.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from schemas import ValidationError
from schemas.v1 import validate_record

ROOT = Path(__file__).resolve().parents[3]
FIRST = ROOT / "research/screening/r006_r004_crosslane_20261110/DECISIONS.json"
SECOND = ROOT / "research/screening/r006_fulltext_e2_review_20261110/DECISIONS.json"
SOURCE_DIR = ROOT / "research/sources/related/records"
DOIS = {
    "SRC-REL-BECKER-2025": "10.1145/3706066",
    "SRC-REL-ROMEO-2025": "10.1145/3711938",
    "SRC-REL-KUHNE-2020": "10.3389/fnbot.2020.593732",
    "SRC-REL-ROMEO-2023": "10.1109/ro-man57019.2023.10309631",
}
DECISIONS = {
    "SRC-REL-BECKER-2025": "include",
    "SRC-REL-ROMEO-2025": "include",
    "SRC-REL-KUHNE-2020": "uncertain",
    "SRC-REL-ROMEO-2023": "uncertain",
}
PROTOCOL = "MHAC-Track-E-frozen-v1-2026-10-13"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _ref(rid: str, rev: int = 1) -> dict:
    return {"id": rid, "rev": rev}


def check_inputs(first: dict, second: dict, sources: dict[str, dict]) -> list[dict]:
    """Fail closed when accepted original screening, access or identity changes.

    This checks integrity of recorded decisions, not the correctness of the
    scientific interpretation; source-reviewed reclassification requires a
    new explicitly documented tranche, never a silent generator edit.
    """
    if (first.get("issue") != 6 or first.get("evidence_cutoff") != "2026-10-04"
            or first.get("screened_on") != "2026-11-10"
            or first.get("kind") != "provisional_first_pass_screening_handoff_not_registered_mhac_records_v1"
            or first.get("actor", {}).get("kind") != "agent"
            or first.get("actor", {}).get("id") != "gpt6-r006-crosslane-20261110"):
        raise ValueError("First-pass provenance or frozen cutoff changed")
    if (first.get("acceptance", {}).get("canonical_screening_records_created") != 0
            or first["acceptance"].get("included_studies") != 0
            or first["acceptance"].get("independent_samples") != 0
            or first["acceptance"].get("corpus_snapshot_created") is not False):
        raise ValueError("First-pass ledger now claims forbidden research admission")
    if (second.get("registry_status") != "not_registered_no_canonical_SCR"
            or second.get("cutoff") != "2026-10-04"
            or second.get("counts", {}).get("canonical_screening_records_added") != 0
            or second.get("counts", {}).get("independent_samples_counted") != 0
            or second.get("admission_status") !=
                "Draft_for_integrator_scientific_review_not_accepted_R006_corpus"):
        raise ValueError("Full-text handoff unexpectedly promoted or altered")
    rows = first.get("decisions", [])
    if len(rows) != len(DOIS) or {r.get("source_ref", {}).get("id") for r in rows} != set(DOIS):
        raise ValueError("Screening tranche is missing sources or contains duplicates")
    counts = {"include": 0, "uncertain": 0}
    for row in rows:
        pin = row["source_ref"]
        sid = pin["id"]
        decision = row.get("decision")
        if (pin != _ref(sid) or row.get("doi") != DOIS[sid]
                or row.get("track") != "empirical"
                or row.get("stage") != "title_abstract"
                or decision != DECISIONS[sid]
                or set(row.get("rule_assessment", {})) != {f"E{i}" for i in range(1, 7)}
                or not row.get("reason") or not row.get("access_limitation")
                or row.get("reading_scope") != "abstract_only_for_this_screening_pass"
                or row.get("review_status") != "single_agent_first_pass_unverified"
                or row.get("independent_study_count") != "not_established"
                or row.get("sample_overlap") != "not_established"):
            raise ValueError(f"Unverified title/abstract status, scope or source: {sid}")
        if any(value != "yes" for key, value in row["rule_assessment"].items()
               if key != "E2") or row["rule_assessment"]["E2"] != (
                   "uncertain" if decision == "uncertain" else "yes"):
            raise ValueError(f"Mutated frozen E1-E6 assessment: {sid}")
        evidence = row.get("evidence", [])
        if (len(evidence) != 1 or not evidence[0].get("url", "").startswith("https://")
                or not evidence[0].get("locator")
                or evidence[0].get("local_bytes_verified") is not False):
            raise ValueError(f"Unqualified evidence or purported hash: {sid}")
        source = sources[sid]
        if (source.get("id") != sid or source.get("kind") != "source"
                or source.get("synthetic") is not False):
            raise ValueError(f"Source registry identity mismatch: {sid}")
        revision = next((v for v in source.get("revisions", []) if v["rev"] == pin["rev"]), None)
        if not revision or revision["data"]["validity"] != "active":
            raise ValueError(f"Missing active accepted source revision: {sid}")
        verified = {i["value"].lower() for i in revision["data"]["identifiers"]
                    if i["scheme"] == "doi" and i["status"] == "verified"}
        if DOIS[sid] not in verified:
            raise ValueError(f"DOI not verified by accepted source: {sid}")
        counts[decision] += 1
    if counts != {"include": 2, "uncertain": 2}:
        raise ValueError("Title/abstract classification totals drifted")
    return sorted(rows, key=lambda r: r["source_ref"]["id"])


def candidates(*, at: str, actor_id: str, first: dict | None = None,
               second: dict | None = None, sources: dict[str, dict] | None = None) -> dict[str, dict]:
    """Render one immutable first revision per publication, in memory only.

    The caller must provide its *actual* registration timestamp and actual
    agent identity. No file writes and no common registry mutation occur.
    """
    if not actor_id or not actor_id.strip() or actor_id.startswith("human-"):
        raise ValueError("Supply the actual agent's ID; this bridge cannot attest human review")
    first = copy.deepcopy(first if first is not None else _load(FIRST))
    second = copy.deepcopy(second if second is not None else _load(SECOND))
    sources = sources if sources is not None else {
        sid: _load(SOURCE_DIR / (sid + ".json")) for sid in DOIS
    }
    rows = check_inputs(first, second, sources)
    result = {}
    for row in rows:
        sid = row["source_ref"]["id"]
        rid = "SCR-R006-" + sid.removeprefix("SRC-") + "-TA"
        ref = row["source_ref"]
        record = {
            "schema_version": 1, "id": rid, "kind": "screening",
            "synthetic": False, "issue": 6,
            "revisions": [{
                "rev": 1, "at": at,
                "actor": {"kind": "agent", "id": actor_id,
                          "tool": "R006 source-pinned title/abstract admission bridge"},
                "basis": [ref],
                "factual_status": "researcher_interpretation",
                "data": {
                    "source_ref": ref, "stage": "title_abstract",
                    "protocol_version": PROTOCOL,
                    "track": "empirical",
                    "rule": "Frozen protocol v1 E1-E6 and G01; source-limited first-pass title/abstract only",
                    "decision": row["decision"],
                    "reason": ("Transcribed from accepted single-agent 2026-11-10 TA ledger; "
                               "not an independent second review. " + row["reason"]),
                    "access_limitation": row["access_limitation"],
                    "reading_refs": [], "review_refs": [],
                }
            }]
        }
        validate_record(record, expected_kind="live")
        result[rid] = record
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--at", help="actual RFC3339 UTC/offset time of the registration")
    parser.add_argument("--actor-id", help="actual model/agent ID; never a human reviewer")
    parser.add_argument("--record", choices=sorted(
        "SCR-R006-" + sid.removeprefix("SRC-") + "-TA" for sid in DOIS),
        help="emit one candidate v1 record to stdout; does not register it")
    args = parser.parse_args()
    if bool(args.at) != bool(args.actor_id) or bool(args.record) != bool(args.at):
        parser.error("--at and --actor-id must be given together with --record, or omit all for validation")
    if args.record:
        values = candidates(at=args.at, actor_id=args.actor_id)
        print(json.dumps(values[args.record], sort_keys=True, indent=2, ensure_ascii=False))
    else:
        candidates(at="2026-11-10T00:00:00Z", actor_id="test-only-not-registered")
        print("R006 TA inputs consistent; 4 schema-valid candidates, 0 canonical records written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
