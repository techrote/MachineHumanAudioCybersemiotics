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


def _matching_synthetic_recovery_binding(trace, target, source, event_id, event):
    """Assumed trusted fictional attestation, never deployable source authority."""
    binding = trace.get("recovery_binding")
    if not isinstance(binding, dict) or binding.get("authority") != "synthetic_fixture_only":
        return False
    if (binding.get("source_id") != target
            or not _integer(binding.get("source_version"))
            or binding["source_version"] != source["version"]
            or not _integer(binding.get("source_observed_at_ms"))
            or binding["source_observed_at_ms"] != source["observed_at_ms"]):
        return False
    attested = binding.get("closed_events")
    if not isinstance(attested, list):
        return False
    witnessed = []
    for identity, record in trace["events"].items():
        if record.get("source_id") != target:
            continue
        if record.get("state") != "closed" or not _integer(record.get("version")):
            return False
        witnessed.append((identity, record["version"]))
    claimed = []
    for entry in attested:
        if (not isinstance(entry, dict)
                or not isinstance(entry.get("event_id"), str)
                or not _integer(entry.get("event_version"))):
            return False
        claimed.append((entry["event_id"], entry["event_version"]))
    return (len(claimed) == len(witnessed)
            and len(claimed) == len(set(claimed))
            and set(claimed) == set(witnessed)
            and (event_id, event["version"]) in claimed)


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
        clear_allowed = bool(
            truth == "inactive" and source is not None
            and event_valid and event is not None and event["state"] == "closed"
            and cue.get("source_id") == target
            and cue.get("event_id") == event_id
            and cue["source_version"] == source["version"]
            and cue["event_version"] == event["version"]
            and _matching_synthetic_recovery_binding(trace, target, source, event_id, event)
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
