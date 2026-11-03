"""MHAC-T004: symbolic field-binding oracle, NOT acoustic perception or safety evidence.

All tokens, pairs and thresholds are fictional research conventions.
"""
from __future__ import annotations

from copy import deepcopy

SOURCES = {"pump": "s:pump", "door": "s:door", "fan": "s:fan"}
EVENTS = {"fault": "e:fault", "open": "e:open", "stopped": "e:stopped"}
LEGAL = {("pump", "fault"), ("pump", "stopped"),
         ("door", "open"), ("door", "fault"),
         ("fan", "fault"), ("fan", "stopped")}
TRAINED = {("pump", "fault"), ("door", "open"), ("fan", "stopped")}
FLAT = {("pump", "fault"): "flat:1", ("door", "open"): "flat:2",
        ("fan", "stopped"): "flat:3"}
MECHANISMS = {"flat", "serial", "parallel", "hybrid"}


def _outcome(status: str, reason: str, held_out: bool = False) -> dict:
    return {"status": status, "reason": reason, "held_out": held_out}


def _one(message: object, seen: dict) -> dict:
    if not isinstance(message, dict):
        return _outcome("reject", "malformed")
    required = {"source", "event", "source_token", "event_token",
                "event_id", "version", "mechanism"}
    if not required.issubset(message):
        return _outcome("reject", "malformed")
    source, event = message["source"], message["event"]
    if not isinstance(source, str) or not isinstance(event, str):
        return _outcome("reject", "malformed")
    if not isinstance(message["event_id"], str) or not message["event_id"].strip():
        return _outcome("reject", "malformed")
    if type(message["version"]) is not int or message["version"] < 1:
        return _outcome("reject", "malformed")
    mechanism = message["mechanism"]
    if not isinstance(mechanism, str) or mechanism not in MECHANISMS:
        return _outcome("reject", "mechanism")
    if source == "unknown" or event == "unknown":
        return _outcome("unresolved", "unknown-field")
    if source not in SOURCES or event not in EVENTS:
        return _outcome("reject", "out-of-vocabulary")
    if (source, event) not in LEGAL:
        return _outcome("reject", "illegal-pair")
    if message["source_token"] != SOURCES[source] or message["event_token"] != EVENTS[event]:
        return _outcome("reject", "field-binding-mismatch")
    identity = (source, message["event_id"])
    if identity in seen:
        last_version, last_event = seen[identity]
        if last_event != event:
            return _outcome("reject", "event-identity-reuse")
        if message["version"] <= last_version:
            return _outcome("reject", "stale-or-replay")
    held_out = (source, event) not in TRAINED
    if mechanism == "flat":
        if message.get("flat_token") != FLAT.get((source, event)):
            return _outcome("unresolved", "flat-untrained", held_out)
    elif mechanism == "parallel":
        if message.get("binding") != "tagged":
            return _outcome("unresolved", "parallel-binding-underdetermined", held_out)
    elif mechanism == "serial":
        if message.get("order") != ["source", "event"]:
            return _outcome("reject", "serial-order", held_out)
    elif mechanism == "hybrid":
        if message.get("fallback") != "explicit":
            return _outcome("unresolved", "fallback-unavailable", held_out)
    seen[identity] = (message["version"], event)
    return _outcome("accept", "symbolic-parse-only", held_out)


def evaluate(case: dict) -> dict:
    """Atomic batch oracle: reject/unresolved leaves no committed state.

    'accept' asserts syntactic consistency only, not perception or correct action.
    """
    if not isinstance(case, dict):
        return _outcome("reject", "malformed-case")
    previous = case.get("previous", [])
    messages = case.get("messages")
    if not isinstance(previous, list) or not isinstance(messages, list) or not messages:
        return _outcome("reject", "malformed-case")
    seen = {}
    for message in previous:
        result = _one(message, seen)
        if result["status"] != "accept":
            return _outcome("reject", "invalid-prior-state")
    staged = deepcopy(seen)
    identities = set()
    held_out = False
    for message in messages:
        if not isinstance(message, dict):
            return _outcome("reject", "malformed")
        identity = (message.get("source"), message.get("event_id"), message.get("version"))
        try:
            if identity in identities:
                return _outcome("reject", "batch-identity-collision")
            identities.add(identity)
        except TypeError:
            return _outcome("reject", "malformed")
        result = _one(message, staged)
        if result["status"] != "accept":
            return result
        held_out |= result["held_out"]
    return _outcome("accept", "symbolic-batch-only", held_out)


def audit_cases(cases: list) -> list:
    """Raises on incorrect expected outcomes; never returns human statistics."""
    results = []
    for case in cases:
        result = evaluate(case)
        if {k: result[k] for k in ("status", "reason")} != case["expected"]:
            raise AssertionError(f'{case.get("id")}: {result} != {case["expected"]}')
        results.append({"id": case["id"], **result})
    return results
