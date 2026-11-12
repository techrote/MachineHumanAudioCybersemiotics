#!/usr/bin/env python3
"""Deterministic illustration ONLY; never import these cases as human evidence.

Run from repository root:
    python research/tangents/warning-failure-paths/analysis.py
    python -m unittest discover -s research/tangents/warning-failure-paths -p 'test_*.py'
"""
from __future__ import annotations

import csv
import io
import json
import math
from collections import Counter
from pathlib import Path

FIXTURE = Path(__file__).with_name("SYNTHETIC-ONLY.csv")
COLUMNS = [
    "case_id", "dataset_kind", "scenario", "emitted", "measured_audible",
    "reported_detection", "identified_correctly", "interpreted_request_correctly",
    "selected_correct_action", "action_latency_s", "deadline_s", "urgency_rating",
]
FLAGS = [
    "measured_audible", "reported_detection", "identified_correctly",
    "interpreted_request_correctly", "selected_correct_action",
]


def flag(value: str, field: str) -> bool | None:
    if value == "":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValueError(f"{field}: use true, false or empty (not {value!r})")


def positive_float(value: str, field: str, allow_zero: bool) -> float | None:
    if value == "":
        return None
    try:
        result = float(value)
    except ValueError as exc:
        raise ValueError(f"{field}: not a number") from exc
    if not math.isfinite(result) or result < 0 or (not allow_zero and result == 0):
        raise ValueError(f"{field}: finite positive value required")
    return result


def parse_cases(text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != COLUMNS:
        raise ValueError("Unexpected fixture columns; schema is intentionally fixed")
    rows: list[dict] = []
    seen: set[str] = set()
    for raw in reader:
        if None in raw or any(v is None for v in raw.values()):
            raise ValueError("Invalid or short CSV row")
        case_id = raw["case_id"]
        if not case_id or case_id in seen:
            raise ValueError("case_id must be nonempty and unique")
        seen.add(case_id)
        if raw["dataset_kind"] != "synthetic_fixture":
            raise ValueError("Only explicitly synthetic_fixture rows are permitted")
        if not raw["scenario"]:
            raise ValueError("scenario required")
        if raw["emitted"] != "true":
            raise ValueError("This toy demonstrates emitted-alert trials only; catch trials are absent")
        row = {key: flag(raw[key], key) for key in FLAGS}
        row["case_id"] = case_id
        row["scenario"] = raw["scenario"]
        row["action_latency_s"] = positive_float(raw["action_latency_s"], "action_latency_s", True)
        row["deadline_s"] = positive_float(raw["deadline_s"], "deadline_s", False)
        if row["deadline_s"] is None:
            raise ValueError("deadline_s is required")
        urgency = raw["urgency_rating"]
        if urgency != "":
            if urgency not in {"1", "2", "3", "4", "5", "6", "7"}:
                raise ValueError("urgency_rating must be an integer 1..7 or empty")
            row["urgency_rating"] = int(urgency)
        else:
            row["urgency_rating"] = None

        # These constraints represent how this illustrative instrument branches.
        # They do NOT assert that real human cognition passes through a linear chain.
        if row["reported_detection"] is not True and row["identified_correctly"] is not None:
            raise ValueError(f"{case_id}: identity test unavailable without positive detection response")
        if row["identified_correctly"] is not True and row["interpreted_request_correctly"] is not None:
            raise ValueError(f"{case_id}: request test unavailable without correct identity")
        if row["interpreted_request_correctly"] is not True and row["selected_correct_action"] is not None:
            raise ValueError(f"{case_id}: selected action test unavailable without correct request")
        if row["selected_correct_action"] is not True and row["action_latency_s"] is not None:
            raise ValueError(f"{case_id}: action latency requires correct selected action")
        rows.append(row)
    if not rows:
        raise ValueError("No synthetic examples provided")
    return rows


def classify(row: dict) -> str:
    """Descriptive observed endpoints, not diagnoses or causal attribution."""
    detected = row["reported_detection"]
    if detected is False:
        if row["measured_audible"] is False:
            return "miss_with_modelled_masking"  # consistency only, not proven cause
        if row["measured_audible"] is True:
            return "audible_prediction_with_no_report"  # NOT 'inattentional deafness'
        return "miss_unattributed"
    if detected is None:
        return "detection_unassessed"
    if row["identified_correctly"] is False:
        return "identification_error"
    if row["identified_correctly"] is None:
        return "identity_unassessed"
    if row["interpreted_request_correctly"] is False:
        return "request_interpretation_error"
    if row["interpreted_request_correctly"] is None:
        return "request_unassessed"
    if row["selected_correct_action"] is False:
        return "action_selection_error"
    if row["selected_correct_action"] is None:
        return "selection_unassessed"
    latency = row["action_latency_s"]
    if latency is None:
        return "timing_unassessed"
    return "timely_correct_action" if latency <= row["deadline_s"] else "late_correct_action"


def timely_correct(row: dict) -> bool | None:
    if row["selected_correct_action"] is False:
        return False
    if row["selected_correct_action"] is None or row["action_latency_s"] is None:
        return None
    return row["action_latency_s"] <= row["deadline_s"]


def summarize(rows: list[dict]) -> dict:
    endpoint_results = {}
    for field in [
        "reported_detection", "identified_correctly",
        "interpreted_request_correctly", "selected_correct_action",
    ]:
        observed = [row[field] for row in rows if row[field] is not None]
        endpoint_results[field] = {
            "positive": sum(value is True for value in observed),
            "assessed": len(observed),
            "unassessed": len(rows) - len(observed),
        }
    timely = [v for row in rows if (v := timely_correct(row)) is not None]
    endpoint_results["timely_correct_action"] = {
        "positive": sum(v is True for v in timely),
        "assessed": len(timely),
        "unassessed": len(rows) - len(timely),
    }
    classifications = [classify(row) for row in rows]
    return {
        "dataset_kind": "synthetic_fixture",
        "human_participants": 0,
        "source_of_truth": "invented demonstration only; not an empirical estimate",
        "emitted_trials": len(rows),
        "endpoint_counts": endpoint_results,
        "descriptive_labels": dict(sorted(Counter(classifications).items())),
        "cases": [{"id": row["case_id"], "label": label}
                  for row, label in zip(rows, classifications)],
        "limitations": [
            "No no-alert catch trials; false alarms, SDT sensitivity and specificity are not estimable.",
            "Observed omission does not identify masking, inattentional deafness or decision policy.",
            "Denominators are assessment-specific and must not be compared as matched effects.",
            "Synthetic urgency values illustrate a possible discordance, not measured relationships.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(summarize(parse_cases(FIXTURE.read_text(encoding="utf-8"))),
                     sort_keys=True, indent=2))
