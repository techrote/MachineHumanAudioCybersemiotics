"""T005: fictional, symbolic source/event-policy oracle; not an auditory simulator."""
from __future__ import annotations

import json
from pathlib import Path

POLICIES = (
    "discrete_visual",
    "persistent_discrete",
    "persistent_transition",
    "ducked_hybrid",
)


def _integer(value):
    return type(value) is int and value >= 0


def evaluate(trace: dict, policy: str) -> dict:
    if policy not in POLICIES:
        raise ValueError("unknown candidate policy")
    now = trace["now_ms"]
    if not _integer(now):
        raise ValueError("invalid evaluation time")
    sources = trace["sources"]
    events = trace["events"]
    target = trace["target_source"]
    playback = trace["playback"]
    if playback not in {"playing", "silenced", "failed", "ducked"}:
        raise ValueError("invalid playback status")
    source = sources.get(target)
    truth = "unknown"
    if source is not None:
        if source["condition"] not in {"active", "inactive", "unknown"}:
            raise ValueError("invalid source condition")
        if not all(_integer(source[k]) for k in ("version", "observed_at_ms", "ttl_ms")):
            raise ValueError("invalid source stamp")
        if not isinstance(source["online"], bool):
            raise ValueError("invalid link status")
        if source["observed_at_ms"] > now or now - source["observed_at_ms"] > source["ttl_ms"]:
            truth = "stale"
        elif source["online"]:
            truth = source["condition"]
    event_id = trace.get("target_event")
    event = events.get(event_id) if event_id is not None else None
    event_valid = False
    event_due = False
    if event is not None:
        if not all(_integer(event[k]) for k in ("version", "deadline_ms")):
            raise ValueError("invalid event stamp")
        if event["state"] not in {"open", "closed"}:
            raise ValueError("invalid event state")
        event_valid = event["source_id"] == target
        event_due = event_valid and event["state"] == "open" and now <= event["deadline_ms"]
    cue = trace.get("cue")
    clear_allowed = False
    if cue is not None:
        if cue.get("kind") != "clear":
            raise ValueError("unsupported cue type")
        for field in ("source_version", "event_version"):
            if not _integer(cue.get(field)):
                raise ValueError("invalid clear cue version")
        conflicting_event = any(
            e["source_id"] == target and (
                e["state"] == "open" or e["version"] > (event["version"] if event_valid else 0)
            ) for e in events.values()
        )
        clear_allowed = bool(
            truth == "inactive" and source is not None
            and event_valid and event is not None and event["state"] == "closed"
            and cue.get("source_id") == target
            and cue.get("event_id") == event_id
            and cue["source_version"] == source["version"]
            and cue["event_version"] == event["version"]
            and source["version"] >= event["version"]
            and not conflicting_event
        )
    sound_available = playback == "playing"
    persistent = policy != "discrete_visual" and truth in {"active", "inactive"}
    duck_status = policy == "ducked_hybrid" and event_due and sound_available
    return {
        "truth": truth,
        "event_due": bool(event_due),
        "event_audio": bool(event_due and sound_available),
        "event_visual": bool(event_due),
        "status_audio": bool(persistent and sound_available and not duck_status),
        "status_visual": truth,
        "status_ducked": bool(duck_status),
        "clear_allowed": bool(clear_allowed),
        "clear_audio": bool(clear_allowed and sound_available and policy in {"persistent_transition", "ducked_hybrid"}),
        "clear_visual": bool(clear_allowed and policy in {"discrete_visual", "persistent_transition", "ducked_hybrid"}),
        "acknowledged": event_id in trace.get("acknowledged_events", []),
        "action_completed": event_id in trace.get("completed_events", []),
    }


def run_cases(path: Path) -> int:
    cases = json.loads(path.read_text(encoding="utf-8"))
    for case in cases:
        for policy in POLICIES:
            got = evaluate(case, policy)
            for field, expected in case["expected"].items():
                if got[field] != expected:
                    raise AssertionError(f"{case['id']} ({policy}) {field}: {got[field]} != {expected}")
            if got["clear_allowed"] and got["truth"] != "inactive":
                raise AssertionError(f"{case['id']}: false all-clear")
            if (got["clear_audio"] or got["clear_visual"]) and not got["clear_allowed"]:
                raise AssertionError(f"{case['id']}: unsupported clear published")
            if got["event_audio"] and not got["event_due"]:
                raise AssertionError(f"{case['id']}: unsupported alert published")
    return len(cases)


if __name__ == "__main__":
    n = run_cases(Path(__file__).with_name("STATE-TRACES.json"))
    print(f"PASS: {n} fictional cases × {len(POLICIES)} candidate policies (symbolic only)")
