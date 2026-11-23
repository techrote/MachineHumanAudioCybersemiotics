#!/usr/bin/env python3
"""MHAC-X004: finite decision-sufficiency audit for collapsed state tables.

Given explicit finite rows, retained fields q(x), and downstream decision fields
D(x), this checks whether D is constant on every fibre of q. If not, it returns
concrete witness pairs that the proposed representation merges even though the
declared decisions differ.

This is an exact finite-table check. It is NOT statistical sufficiency,
Blackwell sufficiency, MDP bisimulation, causal discovery, or human validation.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import argparse
import json
from typing import Iterable, Mapping, Sequence


def _canon(value):
    """Hashable, deterministic representation of JSON-compatible values."""
    if isinstance(value, dict):
        return tuple((k, _canon(value[k])) for k in sorted(value))
    if isinstance(value, list):
        return tuple(_canon(v) for v in value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"unsupported value type: {type(value).__name__}")


def _require_fields(row: Mapping, fields: Sequence[str], *, label: str) -> None:
    missing = [field for field in fields if field not in row]
    if missing:
        raise ValueError(f"{label} row missing fields: {missing}")


def key_for(row: Mapping, fields: Sequence[str]) -> tuple:
    _require_fields(row, fields, label="retained")
    return tuple((field, _canon(row[field])) for field in fields)


def decision_for(row: Mapping, fields: Sequence[str]) -> tuple:
    _require_fields(row, fields, label="decision")
    return tuple((field, _canon(row[field])) for field in fields)


def varying_fields(rows: Sequence[Mapping], excluded: Iterable[str] = ()) -> list[str]:
    excluded = set(excluded)
    fields = sorted(set().union(*(row.keys() for row in rows)) - excluded)
    result = []
    for field in fields:
        values = []
        missing = False
        for row in rows:
            if field not in row:
                missing = True
                break
            values.append(_canon(row[field]))
        if not missing and len(set(values)) > 1:
            result.append(field)
    return result


def audit(
    rows: Sequence[Mapping],
    retained_fields: Sequence[str],
    decision_fields: Sequence[str],
    *,
    id_field: str = "id",
) -> dict:
    if not rows:
        raise ValueError("at least one row is required")
    if not decision_fields:
        raise ValueError("at least one decision field is required")
    if len(set(retained_fields)) != len(retained_fields):
        raise ValueError("retained_fields contains duplicates")
    if len(set(decision_fields)) != len(decision_fields):
        raise ValueError("decision_fields contains duplicates")
    for row in rows:
        _require_fields(row, retained_fields, label="retained")
        _require_fields(row, decision_fields, label="decision")
        if id_field not in row:
            raise ValueError(f"row missing id field {id_field!r}")

    groups: dict[tuple, list[Mapping]] = {}
    for row in rows:
        groups.setdefault(key_for(row, retained_fields), []).append(row)

    conflicts = []
    for key, members in sorted(groups.items(), key=lambda kv: repr(kv[0])):
        by_decision: dict[tuple, list[Mapping]] = {}
        for row in members:
            by_decision.setdefault(decision_for(row, decision_fields), []).append(row)
        if len(by_decision) <= 1:
            continue

        # Small explicit witnesses: first row from every distinct decision class.
        witnesses = []
        for decision, members_for_decision in sorted(
            by_decision.items(), key=lambda kv: repr(kv[0])
        ):
            row = sorted(members_for_decision, key=lambda r: str(r[id_field]))[0]
            witnesses.append({
                "id": row[id_field],
                "decision": dict(decision),
            })
        conflicts.append({
            "retained_key": dict(key),
            "member_ids": sorted(str(row[id_field]) for row in members),
            "decision_classes": len(by_decision),
            "witnesses": witnesses,
            "varying_nonretained_fields": varying_fields(
                members,
                excluded=set(retained_fields) | set(decision_fields) | {id_field},
            ),
        })

    return {
        "schema": "mhac-x004-decision-sufficiency-v1",
        "status": "sufficient" if not conflicts else "insufficient",
        "row_count": len(rows),
        "group_count": len(groups),
        "retained_fields": list(retained_fields),
        "decision_fields": list(decision_fields),
        "conflict_group_count": len(conflicts),
        "conflicts": conflicts,
        "interpretation": (
            "For this explicit finite table, the declared decisions are constant "
            "on every retained-state fibre."
            if not conflicts else
            "At least one retained-state fibre contains rows requiring different "
            "declared decisions; this collapse loses decision-relevant distinctions."
        ),
        "limits": [
            "Passing covers only the supplied finite rows and decision fields.",
            "Hidden real-world states absent from the table are not tested.",
            "A varying omitted field is a candidate witness, not a proven causal variable.",
            "This is deterministic decision sufficiency, not statistical sufficiency.",
            "Dynamic-transition preservation and optimal-control guarantees are not tested.",
        ],
    }


def minimal_sufficient_field_sets(
    rows: Sequence[Mapping],
    candidate_fields: Sequence[str],
    decision_fields: Sequence[str],
    *,
    id_field: str = "id",
    max_candidates: int = 12,
) -> list[list[str]]:
    """Enumerate inclusion-minimal retained-field sets for the supplied finite table."""
    fields = list(dict.fromkeys(candidate_fields))
    if len(fields) > max_candidates:
        raise ValueError(
            f"refusing combinatorial search across {len(fields)} fields; "
            f"max_candidates={max_candidates}"
        )
    sufficient: list[frozenset[str]] = []
    for size in range(len(fields) + 1):
        for combo in combinations(fields, size):
            cset = frozenset(combo)
            if any(previous <= cset for previous in sufficient):
                continue
            result = audit(rows, combo, decision_fields, id_field=id_field)
            if result["status"] == "sufficient":
                sufficient.append(cset)
    return [sorted(x) for x in sorted(sufficient, key=lambda s: (len(s), sorted(s)))]


def analyze_payload(payload: Mapping) -> dict:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError("payload requires list field 'rows'")
    retained = payload.get("retained_fields")
    decisions = payload.get("decision_fields")
    if not isinstance(retained, list) or not all(isinstance(x, str) for x in retained):
        raise ValueError("retained_fields must be a list of strings")
    if not isinstance(decisions, list) or not all(isinstance(x, str) for x in decisions):
        raise ValueError("decision_fields must be a list of strings")
    id_field = payload.get("id_field", "id")
    if not isinstance(id_field, str):
        raise ValueError("id_field must be a string")
    result = audit(rows, retained, decisions, id_field=id_field)
    candidates = payload.get("candidate_fields")
    if candidates is not None:
        if not isinstance(candidates, list) or not all(isinstance(x, str) for x in candidates):
            raise ValueError("candidate_fields must be a list of strings")
        result["minimal_sufficient_field_sets"] = minimal_sufficient_field_sets(
            rows, candidates, decisions, id_field=id_field
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = analyze_payload(payload)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
