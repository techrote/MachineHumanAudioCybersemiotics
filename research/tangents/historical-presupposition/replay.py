#!/usr/bin/env python3
"""MHAC-T013: fictional proposition-warrant comparison; no human response model."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICIES = ("current_only", "naive_history", "evidence_guard", "present_plus_timeline")
STATES = {"true", "false", "unknown"}
HISTORIES = {"supported", "contradicted", "unknown", "not_applicable"}
TRIGGERS = {"again", "still", "stopped", "resumed", "none"}

SENTENCES = {
    "again": ("Pressure is high.", "Pressure is high again."),
    "still": ("Pressure is high.", "Pressure is still high."),
    "stopped": ("The conveyor is inactive.", "The conveyor has stopped."),
    "resumed": ("The conveyor is running.", "The conveyor has resumed."),
    "none": ("Pressure is high.", None),
}


def load_cases(path: Path = HERE / "cases.json") -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data["schema"] != "mhac-t013-fictional-cases-v1":
        raise ValueError("wrong case schema")
    cases = data["cases"]
    if len(cases) < 24 or len({c["id"] for c in cases}) != len(cases):
        raise ValueError("missing or duplicate independent fictional labels")
    for case in cases:
        if case["current_truth"] not in STATES or case["history_support"] not in HISTORIES:
            raise ValueError("invalid truth labels: " + case["id"])
        if case["trigger"] not in TRIGGERS:
            raise ValueError("invalid trigger")
        if (case["trigger"] == "none") != (case["history_support"] == "not_applicable"):
            raise ValueError("history scope mismatch")
        if case["recipient_belief"] != "not_observed":
            raise ValueError("invented recipient belief")
        if case["action_offer_valid"] and not (
            case["urgent"] and case["current_truth"] == "true"
            and case["deadline_state"] == "open"
        ):
            raise ValueError("contradictory action label")
        if case["history_support"] == "supported" and (
            case["observation_gap"] and case["prior_observation"] == "monitoring_gap"
        ):
            raise ValueError("gap cannot establish history")
    return cases


def render(case: dict, policy: str) -> dict:
    if policy not in POLICIES:
        raise ValueError("unknown comparator " + policy)
    # Never render an asserted current fact for contradicted/unknown current truth.
    if case["current_truth"] != "true":
        return dict(spoken=None, history_claim=False, timeline=False, action=False)
    plain, historic = SENTENCES[case["trigger"]]
    claim = False
    timeline = False
    if historic is not None:
        if policy == "naive_history":
            claim = True
        elif policy == "evidence_guard":
            claim = case["history_support"] == "supported"
        elif policy == "present_plus_timeline":
            timeline = case["history_support"] == "supported"
    # Action eligibility is held fixed across all four language policies;
    # it is a labelled fictional contract, not inferred from the wording.
    action = bool(case["action_offer_valid"] and case["urgent"])
    return dict(
        spoken=historic if claim else plain,
        history_claim=claim,
        timeline=timeline,
        action=action,
    )


def evaluate(cases: list[dict], policy: str) -> dict:
    counts = Counter()
    counts["cases"] = len(cases)
    for case in cases:
        out = render(case, policy)
        if out["spoken"] is not None:
            counts["assertions"] += 1
            counts["spoken_words"] += len(out["spoken"].split())
        if out["history_claim"]:
            counts["historical_offers"] += 1
            if case["history_support"] != "supported":
                counts["unsupported_history"] += 1
            if case["history_support"] == "contradicted":
                counts["contradicted_history"] += 1
            if case["history_support"] == "unknown":
                counts["unknown_promoted"] += 1
        if out["timeline"]:
            counts["inspectable_timelines"] += 1
        if out["spoken"] is not None and case["current_truth"] != "true":
            counts["unsupported_current"] += 1
        if out["action"] and not case["action_offer_valid"]:
            counts["invalid_actions"] += 1
        if (case["urgent"] and case["action_offer_valid"]
                and case["current_truth"] == "true" and not out["spoken"]):
            counts["missed_valid_urgent"] += 1
        if out["action"]:
            counts["action_offers"] += 1
    # Explicit zeros make serialised check evidence unambiguous.
    for key in ("assertions", "spoken_words", "historical_offers", "unsupported_history",
                "contradicted_history", "unknown_promoted", "inspectable_timelines",
                "unsupported_current", "invalid_actions", "missed_valid_urgent", "action_offers"):
        counts.setdefault(key, 0)
    return dict(counts)


def run_checks(cases: list[dict], scores: dict) -> None:
    assert len(cases) == 30
    assert set(scores) == set(POLICIES)
    assert scores["naive_history"]["unsupported_history"] > 0
    assert scores["naive_history"]["contradicted_history"] > 0
    assert scores["naive_history"]["unknown_promoted"] > 0
    assert scores["evidence_guard"]["historical_offers"] > 0
    assert scores["evidence_guard"]["unsupported_history"] == 0
    for policy in POLICIES:
        for key in ("unsupported_current", "invalid_actions", "missed_valid_urgent"):
            assert scores[policy][key] == 0, (policy, key)
        assert scores[policy]["action_offers"] == scores["current_only"]["action_offers"]
    # Unknown history must not erase a valid present warning.
    for case_id in ("AG03", "ST03", "SP03", "RS03"):
        case = next(c for c in cases if c["id"] == case_id)
        assert case["history_support"] == "unknown" and case["action_offer_valid"]
        assert render(case, "evidence_guard")["spoken"] == SENTENCES[case["trigger"]][0]
        assert render(case, "evidence_guard")["action"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="enforce authored invariants")
    args = parser.parse_args()
    cases = load_cases()
    results = {p: evaluate(cases, p) for p in POLICIES}
    if args.check:
        run_checks(cases, results)
    print(json.dumps({"status": "fictional-structural-only", "results": results},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
