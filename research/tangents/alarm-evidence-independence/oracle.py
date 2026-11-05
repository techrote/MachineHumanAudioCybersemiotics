"""MHAC-T015: exploratory, deterministic fictional two-alert evidence-dependence oracle.

Not a source authentication system, Bayesian calculation, listener experiment,
production policy or record from the accepted Track E/G evidence corpus.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "FICTIONAL-CASES.json"
EXPECTED = ROOT / "EXPECTED-METRICS.json"
POLICIES = ("proximity", "device_id", "lineage", "separate")
RELATIONS = ("same_observation", "common_cause", "verified_independent", "unknown")
CLAIMS = ("true", "false", "unknown")
OBLIGATIONS = ("required", "none", "unknown")


def eligible(alert: dict) -> bool:
    """Externally *authored fictional* truth/actor/deadline eligibility.

    All comparators receive the same idealized eligibility information: this
    is an isolation experiment on message grouping, not realistic detection.
    """
    return (alert["event_truth"] == "true"
            and alert["action_obligation"] == "required"
            and alert["authorized_actor"] == "OP-A"
            and alert["emitted_at_s"] <= alert["expires_at_s"]
            and alert["emitted_at_s"] <= alert["deadline_s"])


def check_cases(document: dict) -> list[dict]:
    if not isinstance(document, dict) or document.get("dataset_kind") != "fictional_constructed_not_listener_data":
        raise ValueError("fictional dataset classification required")
    cases = document.get("cases")
    if not isinstance(cases, list) or len(cases) < 32 or document.get("case_count") != len(cases):
        raise ValueError("case count/fixture metadata invalid")
    if sum(c.get("case_kind") == "negative" for c in cases) < 12:
        raise ValueError("at least 12 explicit controls are required")
    ids = set()
    for c in cases:
        name = c.get("id")
        if not isinstance(name, str) or not name.startswith("T015-") or name in ids:
            raise ValueError("duplicate or malformed case id")
        ids.add(name)
        if c.get("dependency_relation") not in RELATIONS:
            raise ValueError("unrecognised dependency relation")
        if c.get("delivery_proximity") not in ("near", "far"):
            raise ValueError("invalid proximity label")
        if c.get("case_kind") not in ("test", "negative"):
            raise ValueError("invalid case kind")
        alerts = c.get("alerts")
        if not isinstance(alerts, list) or len(alerts) != 2:
            raise ValueError("exactly two messages required")
        for a in alerts:
            for key in ("message_id", "source_device", "observation_id", "event_id",
                        "action_id", "delivery_group", "cue_identity"):
                if not isinstance(a.get(key), str) or not a[key]:
                    raise ValueError("missing identity field " + key)
            for key in ("emitted_at_s", "expires_at_s", "deadline_s"):
                if type(a.get(key)) is not int or a[key] < 0:
                    raise ValueError("invalid nonnegative integer time field " + key)
            if a.get("event_truth") not in CLAIMS or a.get("action_obligation") not in OBLIGATIONS:
                raise ValueError("unknown truth and obligation must remain typed")
            if a.get("authorized_actor") not in ("OP-A", "OP-B", "unknown"):
                raise ValueError("invalid actor authority")
            if a.get("upstream_lineage_id") is not None and (
                    not isinstance(a["upstream_lineage_id"], str) or not a["upstream_lineage_id"]):
                raise ValueError("invalid upstream lineage identifier")
        if len({a["message_id"] for a in alerts}) != 2:
            raise ValueError("duplicate message id")
        x, y = alerts
        relation = c["dependency_relation"]
        same_observation = x["observation_id"] == y["observation_id"]
        same_lineage = x["upstream_lineage_id"] == y["upstream_lineage_id"]
        known = x["upstream_lineage_id"] is not None and y["upstream_lineage_id"] is not None
        if relation == "same_observation" and not (known and same_observation and same_lineage):
            raise ValueError("same-observation metadata contradiction")
        if relation == "common_cause" and not (known and not same_observation and same_lineage):
            raise ValueError("common-cause metadata contradiction")
        if relation == "verified_independent" and not (known and not same_observation and not same_lineage):
            raise ValueError("verified-independence metadata contradiction")
        if relation == "unknown" and known:
            raise ValueError("unknown relation requires unresolved lineage")
        near = abs(x["emitted_at_s"] - y["emitted_at_s"]) <= 3
        if (c["delivery_proximity"] == "near") != near:
            raise ValueError("proximity label inconsistent with emission times")
        truth_by_event = {}
        for a in alerts:
            ev = a["event_id"]
            if ev in truth_by_event and truth_by_event[ev] != a["event_truth"]:
                raise ValueError("one world event cannot have two truth labels")
            truth_by_event[ev] = a["event_truth"]
        gold = c.get("gold")
        expected_support = ("verified_independent" if relation == "verified_independent"
                            else "unknown" if relation == "unknown" else "shared")
        if not isinstance(gold, dict) or gold.get("independent_support") != expected_support:
            raise ValueError("author gold independence contradicted by contract")
        offered = sorted({a["event_id"] + "/" + a["action_id"] for a in alerts if eligible(a)})
        gold_obligations = gold.get("required_obligations")
        if not isinstance(gold_obligations, list) or len(set(gold_obligations)) != len(gold_obligations):
            raise ValueError("invalid gold obligations")
        if sorted(gold_obligations) != offered:
            raise ValueError("gold obligations contradict authored actor/truth/deadline labels")
        independent_ids = ([a["message_id"] for a in alerts if eligible(a)]
                           if relation == "verified_independent" else [])
        if gold.get("independent_eligible_message_ids") != independent_ids:
            raise ValueError("gold eligible independent observations contradicted")
    return cases


def load_cases(path: Path = FIXTURE) -> list[dict]:
    return check_cases(json.loads(path.read_text(encoding="utf-8")))


def classify(c: dict, policy: str) -> str:
    if policy not in POLICIES:
        raise ValueError("unknown comparator")
    x, y = c["alerts"]
    near = abs(x["emitted_at_s"] - y["emitted_at_s"]) <= 3
    if policy == "proximity":
        return "verified_independent" if near else "unasserted"
    if policy == "device_id":
        return "verified_independent" if x["source_device"] != y["source_device"] else "shared"
    if policy == "lineage":
        return ("verified_independent" if c["dependency_relation"] == "verified_independent"
                else "unknown" if c["dependency_relation"] == "unknown" else "shared")
    return "unasserted"


def deliver(c: dict, policy: str) -> list[dict]:
    """All comparators share the same *fictional* eligible-message input."""
    if policy not in POLICIES:
        raise ValueError("unknown comparator")
    x, y = c["alerts"]
    near = abs(x["emitted_at_s"] - y["emitted_at_s"]) <= 3
    chosen, seen = [], set()
    for a in c["alerts"]:
        if not eligible(a):
            continue
        if policy == "proximity":
            key = a["event_id"] if near else a["message_id"]
        elif policy == "device_id":
            key = a["source_device"] if near else a["message_id"]
        elif policy == "lineage":
            key = (a["observation_id"], a["event_id"], a["action_id"])
        else:
            key = a["message_id"]
        if key not in seen:
            seen.add(key)
            chosen.append(a)
    return chosen


def assessment(cases: list[dict], policy: str) -> dict:
    if policy not in POLICIES:
        raise ValueError("unknown comparator")
    m = dict.fromkeys(("false_corroborations", "verified_independence_unreported",
                       "required_actions_missed", "independent_eligible_alerts_suppressed",
                       "eligible_alerts_suppressed", "unsupported_action_offers",
                       "offers_after_deadline", "delivered_messages", "word_tokens_proxy",
                       "serial_delay_tenths_seconds_proxy"), 0)
    for c in cases:
        chosen = deliver(c, policy)
        chosen_ids = {a["message_id"] for a in chosen}
        keys = {a["event_id"] + "/" + a["action_id"] for a in chosen}
        gold = c["gold"]
        support = classify(c, policy)
        m["false_corroborations"] += int(
            support == "verified_independent" and gold["independent_support"] != "verified_independent")
        m["verified_independence_unreported"] += int(
            support != "verified_independent" and gold["independent_support"] == "verified_independent")
        m["required_actions_missed"] += len(set(gold["required_obligations"]) - keys)
        m["independent_eligible_alerts_suppressed"] += len(
            set(gold["independent_eligible_message_ids"]) - chosen_ids)
        m["eligible_alerts_suppressed"] += sum(eligible(a) for a in c["alerts"]) - len(chosen)
        m["unsupported_action_offers"] += sum(not eligible(a) for a in chosen)
        m["offers_after_deadline"] += sum(a["emitted_at_s"] > a["deadline_s"] for a in chosen)
        m["delivered_messages"] += len(chosen)
        m["word_tokens_proxy"] += len(chosen) * (12 if policy == "lineage" else 8)
        # 2.5 hypothetical words/s; tenths-of-seconds in a serial stream.
        m["serial_delay_tenths_seconds_proxy"] += len(chosen) * (
            48 if policy == "lineage" else 32)
    return m


def report() -> dict:
    cases = load_cases()
    return {
        "dataset_kind": "fictional_constructed_not_listener_data",
        "case_count": len(cases),
        "policies": {policy: assessment(cases, policy) for policy in POLICIES},
        "measurement_warning": ("Outputs are counts and arbitrary length/delay proxies on "
                                "constructed traces, never human, sensor or safety outcomes"),
    }


def check_expected(r: dict) -> None:
    x = json.loads(EXPECTED.read_text(encoding="utf-8"))
    if (r["policies"] != x["metric_expectations"] or
            r["case_count"] != x["case_count"] or
            [c["id"] for c in load_cases()] != x["case_ids"]):
        raise ValueError("expected fictional metric ledger mismatch")


def check_sha_manifest() -> None:
    for line in (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        f = ROOT / name
        if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != expected:
            raise ValueError("SHA-256 mismatch for " + name)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    r = report()
    if args.check:
        check_expected(r)
        check_sha_manifest()
    print(json.dumps(r, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
