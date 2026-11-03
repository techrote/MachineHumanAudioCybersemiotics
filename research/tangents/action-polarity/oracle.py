"""MHAC-T006: fictional, non-acoustic logical-operator and source-truth oracle.

No participant data, auditory intelligibility, action latency or safety inference.
Only explicitly typed propositions are checked against a fictional authority.
"""
from __future__ import annotations

VALID_STATES = {"active", "inactive", "unknown"}
VALID_AUTH = {"required", "prohibited", "permitted", "unknown"}
ACTION_KINDS = {"require", "prohibit", "correction"}
KINDS = ACTION_KINDS | {"status", "all_clear", "ack"}
SCOPE = {"require": "action", "prohibit": "action", "correction": "action",
         "status": "factual", "all_clear": "clearance", "ack": "acknowledgement"}
CLAIMS = {"active", "inactive", "unknown", "not_cleared", "clearance_unconfirmed"}


def outcome(status: str, reason: str) -> dict:
    return {"status": status, "reason": reason}


def number(value: object) -> bool:
    # bool is an int in Python; a boolean clock or version must not be accepted.
    return type(value) is int and value >= 0


def identity(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 80


def truth_valid(t: object) -> bool:
    if not isinstance(t, dict):
        return False
    if not all(identity(t.get(k)) for k in ("source", "event")):
        return False
    if not number(t.get("version")) or t["version"] < 1:
        return False
    if not all(number(t.get(k)) for k in ("issued_at", "expires_at")):
        return False
    if t["expires_at"] <= t["issued_at"] or t.get("state") not in VALID_STATES:
        return False
    actions = t.get("actions")
    return (isinstance(actions, dict) and bool(actions)
            and all(identity(k) and v in VALID_AUTH for k, v in actions.items()))


def expected_tokens(m: dict) -> list[str] | None:
    kind = m.get("kind")
    action = m.get("action")
    avoid = m.get("avoid_action")
    if kind in ACTION_KINDS and not identity(action):
        return None
    if kind == "require":
        return ["DO", action]
    if kind == "prohibit":
        return ["DO", "NOT", action]
    if kind == "correction":
        if not identity(avoid) or action == avoid:
            return None
        return ["DO", action, "NOT", avoid]
    if kind == "status":
        return {"active": ["HAZARD", "ACTIVE"],
                "inactive": ["HAZARD", "CLEARED"],
                "unknown": ["HAZARD", "UNKNOWN"],
                "not_cleared": ["HAZARD", "NOT", "CLEARED"],
                "clearance_unconfirmed": ["CLEARANCE", "NOT", "CONFIRMED"]
                }.get(m.get("claim"))
    if kind == "all_clear":
        return ["ALL", "CLEAR"]
    if kind == "ack":
        return ["ACKNOWLEDGED"]
    return None


def evaluate(case: object) -> dict:
    """Verify single current-version message against a fictional authority.

    No implicit inference from silence, acknowledgements, an old version or
    absent truth. Reject = known contradiction/malformed; unresolved = cannot
    establish a positive claim from supplied authoritative information.
    """
    if not isinstance(case, dict) or case.get("fictional") is not True:
        return outcome("reject", "not-declared-fictional")
    t = case.get("truth")
    if not truth_valid(t):
        return outcome("reject", "invalid-truth")
    now = case.get("now")
    if not number(now):
        return outcome("reject", "invalid-clock")
    m = case.get("message")
    if m is None:
        return outcome("unresolved", "silence-is-not-clearance")
    if not isinstance(m, dict):
        return outcome("reject", "invalid-message")
    if not all(identity(m.get(k)) for k in ("source", "event")):
        return outcome("reject", "invalid-message")
    if not number(m.get("version")) or m["version"] < 1:
        return outcome("reject", "invalid-message")
    if not all(number(m.get(k)) for k in ("issued_at", "expires_at")):
        return outcome("reject", "invalid-message")
    if m["expires_at"] <= m["issued_at"] or m.get("kind") not in KINDS:
        return outcome("reject", "invalid-message")
    if m["source"] != t["source"] or m["event"] != t["event"]:
        return outcome("reject", "source-event-mismatch")
    if m["version"] < t["version"]:
        return outcome("reject", "stale-version")
    if m["version"] > t["version"]:
        return outcome("reject", "future-version")
    if m["issued_at"] < t["issued_at"]:
        return outcome("reject", "predates-authority")
    if m["expires_at"] > t["expires_at"]:
        return outcome("reject", "unsupported-expiry")
    if now < m["issued_at"] or now < t["issued_at"]:
        return outcome("reject", "future-message")
    if now >= m["expires_at"] or now >= t["expires_at"]:
        return outcome("reject", "expired-message")
    kind = m["kind"]
    if m.get("operator_scope") != SCOPE[kind]:
        return outcome("reject", "operator-scope-mismatch")
    tokens = expected_tokens(m)
    if tokens is None:
        return outcome("reject", "invalid-message")
    rendered = m.get("tokens")
    if not isinstance(rendered, list) or any(not identity(x) for x in rendered):
        return outcome("reject", "invalid-message")
    if rendered != tokens:
        return outcome("reject", "operator-token-mismatch")
    if kind == "ack":
        return outcome("reject", "ack-not-resolution")
    if kind in ACTION_KINDS:
        policy = t["actions"]
        action = m["action"]
        if action not in policy:
            return outcome("unresolved", "unknown-action")
        actual = policy[action]
        if actual == "unknown":
            return outcome("unresolved", "unknown-authorization")
        if kind == "require":
            return (outcome("accept", "symbolic-truth-only") if actual == "required"
                    else outcome("reject", "unauthorized-positive-action"))
        if kind == "prohibit":
            return (outcome("accept", "symbolic-truth-only") if actual == "prohibited"
                    else outcome("reject", "unsupported-prohibition"))
        avoid = m["avoid_action"]
        if avoid not in policy or policy[avoid] == "unknown":
            return outcome("unresolved", "unknown-contrast-target")
        return (outcome("accept", "symbolic-truth-only")
                if actual == "required" and policy[avoid] == "prohibited"
                else outcome("reject", "unsupported-correction"))
    if kind == "all_clear":
        if t["state"] == "unknown":
            return outcome("unresolved", "unknown-clearance")
        return (outcome("accept", "symbolic-truth-only")
                if t["state"] == "inactive" else outcome("reject", "false-all-clear"))
    claim = m["claim"]
    if claim == "clearance_unconfirmed":
        # No independent clearance-evidence field exists in this provisional
        # truth schema. Unknown source-state != proof of no clearance record.
        return outcome("unresolved", "no-clearance-evidence")
    if claim == "not_cleared":
        if t["state"] == "unknown":
            return outcome("unresolved", "unknown-clearance")
        return (outcome("accept", "symbolic-truth-only")
                if t["state"] == "active" else outcome("reject", "false-state-claim"))
    return (outcome("accept", "symbolic-truth-only")
            if claim == t["state"] else outcome("reject", "false-state-claim"))


def audit_cases(cases: list) -> list:
    if not isinstance(cases, list) or len(cases) < 24:
        raise AssertionError("24 or more fictional cases required")
    seen = set()
    output = []
    for case in cases:
        case_id = case.get("id")
        if not identity(case_id) or case_id in seen:
            raise AssertionError("duplicate or invalid fixture ID")
        seen.add(case_id)
        actual = evaluate(case)
        if actual != case.get("expected"):
            raise AssertionError(f"{case_id}: {actual} != {case.get('expected')}")
        output.append({"id": case_id, **actual})
    return output
