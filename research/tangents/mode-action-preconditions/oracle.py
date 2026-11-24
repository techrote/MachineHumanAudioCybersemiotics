"""MHAC-T011 fictional, symbolic-only mode/action falsifier; no audio or human model."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "FICTIONAL-TRACES.tsv"
MANIFEST = ROOT / "MANIFEST.json"
POLICIES = ("A_unqualified", "B_announce_all", "C_conditional_guard", "D_visual_guard", "E_no_action")
UNKNOWN = {"?", "conflict"}


def load_cases(path: Path = FIXTURE) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) >= 24 and len({r["id"] for r in rows}) == len(rows)
    for r in rows:
        assert r["source_truth"] in ("true", "false", "unknown")
        assert r["required"] in ("yes", "no")
        assert r["clock"] in ("known", "unknown")
        assert r["allowed"] in ("*", "paused", "maintenance")
        assert r["actor"] and r["authorized"]
        assert r["attested"] in ("yes", "no")
        assert r["source_id"] and r["event_id"] and r["message_ver"].isdigit()
        if r["attested"] == "yes" and mode_sensitive(r):
            assert r["observed_ver"] == r["true_ver"]
            assert r["observed_mode"] == r["action_mode"]
        assert r["action_time"].isdigit()
    return rows


def mode_sensitive(c: dict[str, str]) -> bool:
    return c["allowed"] != "*"


def authorized(c: dict[str, str]) -> bool | None:
    if c["actor"] in UNKNOWN or c["authorized"] in UNKNOWN:
        return None
    return c["actor"] in c["authorized"].split(",")


def truth(c: dict[str, str]) -> str:
    """Externally declared fictional ground truth, never inferred from a policy output."""
    if c["required"] == "no":
        return "not_required"
    if c["source_truth"] == "false":
        return "invalid_source"
    if c["source_truth"] == "unknown":
        return "unknown_source"
    auth = authorized(c)
    if auth is None:
        return "unknown_actor"
    if not auth:
        return "wrong_actor"
    if c["clock"] != "known" or c["deadline"] in UNKNOWN:
        return "unknown_clock_or_deadline"
    if int(c["action_time"]) > int(c["deadline"]):
        return "expired"
    if mode_sensitive(c):
        if c["action_mode"] in UNKNOWN:
            return "unknown_mode"
        if c["action_mode"] not in c["allowed"].split(","):
            return "wrong_mode"
    return "valid"


def transition_count(c: dict[str, str]) -> int:
    stages = [c[k] for k in ("event_mode", "compile_mode", "delivery_mode", "action_mode")]
    return sum(a != b and a not in UNKNOWN and b not in UNKNOWN for a, b in zip(stages, stages[1:]))


def guarded(c: dict[str, str]) -> bool:
    """Idealized *external* checks; NOT a model of auditory comprehension.

    This assumes an authenticated source/actor/clock and an authoritative monotone
    version token for the observer. No guard reads the action-time truth field.
    """
    if c["required"] != "yes" or c["source_truth"] != "true":
        return False
    if authorized(c) is not True or c["clock"] != "known":
        return False
    if c["deadline"] in UNKNOWN or int(c["action_time"]) > int(c["deadline"]):
        return False
    if c["duplicate"] == "yes":
        return False
    if mode_sensitive(c):
        if c["attested"] != "yes" or c["observed_mode"] in UNKNOWN or c["observed_ver"] in UNKNOWN:
            return False
        if c["observed_ver"] != c["true_ver"]:
            return False
        if c["observed_mode"] not in c["allowed"].split(","):
            return False
    return True


def evaluate(c: dict[str, str], policy: str) -> dict[str, object]:
    assert policy in POLICIES
    sent = policy in POLICIES[:2] or (policy in POLICIES[2:4] and guarded(c))
    t = truth(c)
    # Structural message units, not actual word counts, duration or listening burden.
    transitions = transition_count(c) if policy == "B_announce_all" else 0
    audio_units = (int(sent) + transitions) if policy in POLICIES[:2] else (
        int(sent) * (2 if mode_sensitive(c) else 1) if policy == "C_conditional_guard" else 0
    )
    visual_units = (int(sent) * (2 if mode_sensitive(c) else 1)) if policy == "D_visual_guard" else 0
    stale = mode_sensitive(c) and (c["observed_ver"] != c["true_ver"] or c["observed_mode"] in UNKNOWN or c["attested"] != "yes")
    return {
        "id": c["id"], "policy": policy, "sent": sent, "truth": t,
        "wrong_mode_offer": sent and t == "wrong_mode",
        "wrong_actor_offer": sent and t == "wrong_actor",
        "expired_offer": sent and t == "expired",
        "false_known_state": sent and (stale or c["action_mode"] in UNKNOWN) and mode_sensitive(c),
        "invalid_or_unknown_offer": sent and t != "valid",
        "missed_valid_action": not sent and t == "valid" and c["duplicate"] != "yes",
        "duplicate_offer": sent and c["duplicate"] == "yes",
        "audio_units": audio_units, "visual_units": visual_units,
        "unresolved_ack": c["ack"] == "yes" and c["completed"] != "yes",
    }


def report(cases: list[dict[str, str]]) -> dict[str, object]:
    counters = ("wrong_mode_offer", "wrong_actor_offer", "expired_offer", "false_known_state",
                "invalid_or_unknown_offer", "missed_valid_action", "duplicate_offer",
                "audio_units", "visual_units")
    result = {"fixture_cases": len(cases), "truth_class_counts": {}, "policies": {}}
    for c in cases:
        k = truth(c)
        result["truth_class_counts"][k] = result["truth_class_counts"].get(k, 0) + 1
    for policy in POLICIES:
        rows = [evaluate(c, policy) for c in cases]
        result["policies"][policy] = {key: sum(int(r[key]) for r in rows) for key in counters}
        result["policies"][policy]["sent"] = sum(int(r["sent"]) for r in rows)
    return result


def canonical_report_bytes(cases: list[dict[str, str]]) -> bytes:
    return (json.dumps(report(cases), sort_keys=True, separators=(",", ":")) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate stored input and output hashes")
    args = parser.parse_args()
    cases = load_cases()
    blob = canonical_report_bytes(cases)
    if args.check:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        assert manifest["fixture_sha256"] == hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
        assert manifest["report_sha256"] == hashlib.sha256(blob).hexdigest()
        assert manifest["case_count"] == len(cases)
        print("MHAC-T011 synthetic manifest verified: %d cases" % len(cases))
    else:
        print(json.dumps(report(cases), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
