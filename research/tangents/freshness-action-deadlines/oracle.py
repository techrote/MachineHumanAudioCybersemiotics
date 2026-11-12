"""T010 synthetic dispatch falsifier; no simulated listeners, audio, or real actions."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

POLICIES = ("immediate_fifo", "fixed_deferral", "task_boundary", "protected_coalesce", "latest_wins_naive")
HERE = Path(__file__).resolve().parent


def load_cases(path: Path = HERE / "FICTIONAL-TRACES.json") -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "t010-fictional-v1":
        raise ValueError("Unrecognized fictional schema")
    cases = data["cases"]
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("Duplicate case ids")
    for case in cases:
        items = case["messages"]
        if any(x["kind"] not in ("status", "obligation") for x in items):
            raise ValueError(f"Invalid message kind: {case['id']}")
        known = {m["id"] for m in items if m["kind"] == "obligation"}
        changes = case.get("changes", [])
        released = {c["target"] for c in changes if c["kind"] in ("resolve", "revoke")}
        if not released <= known or any(c["kind"] not in ("resolve", "revoke", "ack", "handover") for c in changes):
            raise ValueError(f"Invalid truth changes: {case['id']}")
        # An explicitly asserted truth ledger, not computed by dispatch-policy code.
        truth = case["truth"]
        if set(truth) != {"required", "released"} or set(truth["required"]) | set(truth["released"]) != known:
            raise ValueError(f"Incomplete independent labels: {case['id']}")
        if set(truth["required"]) & set(truth["released"]) or set(truth["released"]) != released:
            raise ValueError(f"Contradictory independent labels: {case['id']}")
        for m in items:
            if not isinstance(m["at"], int) or m["at"] < 0:
                raise ValueError("Noninteger or negative model time")
            if m["kind"] == "obligation" and m.get("deadline") is not None and m["deadline"] < m["at"]:
                raise ValueError("Deadline precedes event")
    return cases


def next_boundary(message: dict, case: dict, *, fallback: int) -> int:
    options = [b for b in case.get("boundaries", []) if b >= message["at"]]
    return min(options) if options else message["at"] + fallback


def planned_time(message: dict, case: dict, policy: str) -> int:
    t = message["at"]
    if policy == "immediate_fifo":
        return t
    if policy == "fixed_deferral":
        return t + 3
    if policy == "task_boundary":
        boundary = next_boundary(message, case, fallback=3)
        deadline = message.get("deadline")
        # Explicit latest-safe-time override, not a model of actual cognition.
        return t if message["kind"] == "obligation" and deadline is not None and boundary > deadline else boundary
    if policy == "protected_coalesce":
        return t if message["kind"] == "obligation" else next_boundary(message, case, fallback=2)
    if policy == "latest_wins_naive":
        return next_boundary(message, case, fallback=3)
    raise ValueError(f"Unknown policy {policy}")


def dispatch(case: dict, policy: str) -> dict:
    if policy not in POLICIES:
        raise ValueError(policy)
    candidates = [{**m, "sent_at": planned_time(m, case, policy)} for m in case["messages"]]
    discarded = []
    # All candidates are planned *before* coalescing. This intentionally tests policy
    # decisions, not a runtime concurrency/queue implementation.
    if policy in ("protected_coalesce", "latest_wins_naive"):
        pending = {}
        kept = []
        for m in sorted(candidates, key=lambda v: (v["at"], v["id"])):
            if policy == "protected_coalesce" and m["kind"] == "obligation":
                kept.append(m)
                continue
            key = (m["source"], m.get("group", "default")) if policy == "protected_coalesce" else (m["source"],)
            previous = pending.get(key)
            if previous is not None and m["at"] <= previous["sent_at"]:
                kept.remove(previous)
                discarded.append(previous["id"])
            kept.append(m)
            pending[key] = m
        candidates = kept
    delivered = sorted(candidates, key=lambda m: (m["sent_at"], m["at"], m["id"]))
    statuses = Counter()
    seen = Counter()
    correct = set()
    for m in delivered:
        t = m["sent_at"]
        if m["kind"] == "status":
            statuses["status_deliveries"] += 1
            statuses["status_latency_sum"] += t - m["at"]
            if m.get("expires") is not None and t > m["expires"]:
                statuses["stale_status"] += 1
            continue
        seen[m["id"]] += 1
        if seen[m["id"]] > 1:
            statuses["duplicate_action_risk"] += 1
        released_at = [c["at"] for c in case.get("changes", []) if c["kind"] in ("resolve", "revoke") and c["target"] == m["id"]]
        if any(at <= t for at in released_at):
            statuses["obsolete_event_dispatch"] += 1
            continue
        handovers = sorted((c for c in case.get("changes", []) if c["kind"] == "handover" and c["at"] <= t), key=lambda c: c["at"])
        actor = handovers[-1]["actor"] if handovers else case.get("initial_actor", "operator-A")
        if m.get("actor") is None or actor is None:
            statuses["unknown_authority"] += 1
            continue
        if m["actor"] != actor:
            statuses["wrong_actor_dispatch"] += 1
            continue
        if case.get("clock_valid", True) is False:
            statuses["unknown_clock"] += 1
            continue
        deadline = m.get("deadline")
        if deadline is None:
            statuses["unknown_deadline"] += 1
            continue
        if t > deadline:
            statuses["expired_event_dispatch"] += 1
            continue
        correct.add(m["id"])
    required = set(case["truth"]["required"])
    report = {
        "case": case["id"], "policy": policy,
        "required": len(required), "timely_authorized": len(required & correct),
        "missed_required": len(required - correct),
        "notifications": len(delivered), "discarded": len(discarded),
        "status_deliveries": statuses["status_deliveries"],
        "mean_status_sample_latency": (round(statuses["status_latency_sum"] / statuses["status_deliveries"], 3)
                                       if statuses["status_deliveries"] else None),
        **{key: statuses[key] for key in ("stale_status", "obsolete_event_dispatch", "expired_event_dispatch",
                                         "wrong_actor_dispatch", "duplicate_action_risk", "unknown_authority",
                                         "unknown_deadline", "unknown_clock")},
    }
    # No listening/acknowledgement/completion metric is inferred from dispatch.
    return report


def run_all(cases: list[dict]) -> list[dict]:
    return [dispatch(case, policy) for case in cases for policy in POLICIES]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run registered negative and positive controls")
    args = parser.parse_args()
    cases = load_cases()
    by_id = {c["id"]: c for c in cases}
    reports = run_all(cases)
    if args.check:
        assert len(cases) >= 24
        assert dispatch(by_id["T04"], "fixed_deferral")["expired_event_dispatch"] == 1
        assert dispatch(by_id["T04"], "task_boundary")["timely_authorized"] == 1
        assert dispatch(by_id["T24"], "latest_wins_naive")["missed_required"] >= 1
        assert dispatch(by_id["T24"], "protected_coalesce")["missed_required"] == 0
        assert dispatch(by_id["T11"], "fixed_deferral")["wrong_actor_dispatch"] == 1
    summary = {p: {k: sum(r[k] for r in reports if r["policy"] == p)
                   for k in ("required", "timely_authorized", "missed_required", "notifications", "discarded",
                             "stale_status", "obsolete_event_dispatch", "expired_event_dispatch", "wrong_actor_dispatch",
                             "duplicate_action_risk", "unknown_authority", "unknown_deadline", "unknown_clock")}
               for p in POLICIES}
    fixture_hash = hashlib.sha256((HERE / "FICTIONAL-TRACES.json").read_bytes()).hexdigest()
    print(json.dumps({"synthetic_only": True, "fixture_sha256": fixture_hash, "cases": len(cases),
                      "policies": summary, "per_case": reports}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
