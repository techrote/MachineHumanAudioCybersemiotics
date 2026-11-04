"""MHAC-T014: fictional, structural-only post-emission retraction comparisons.

No real recipient, sound playback, delivery evidence, observed action, or safety
efficacy is represented. Case labels were authored separately from this oracle.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "TRACE-CASES.json"
POLICIES = ("silent", "generic-closure", "bound-minimal", "bound-uncertainty")
ACTION_STATES = {"unknown", "not_started", "in_progress", "completed"}
DELIVERIES = {"unknown", "confirmed", "failed"}
REVERSIBILITY = {"yes", "no", "unknown"}


def load_cases(path: Path = FIXTURE) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data["schema_version"] != 1:
        raise ValueError("unrecognized fixture schema")
    cases = data["cases"]
    if data["case_count"] != len(cases) or len(cases) < 28:
        raise ValueError("wrong declared case count")
    ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate case id")
    needed = {
        "id", "category", "emitted", "invalidated", "original_delivery",
        "action_state", "reversible", "correction_delivery", "original_message_id",
        "source_id", "event_id", "intended_actor", "correction_for",
        "correction_source", "correction_event", "correction_actor",
        "already_superseded", "deadline", "urgent_other", "visible_previous",
        "expected_need", "resolution_verified",
    }
    for c in cases:
        if set(c) != needed:
            raise ValueError("missing/extra field: " + c["id"])
        if any(type(c[k]) is not bool for k in (
            "emitted", "invalidated", "already_superseded", "urgent_other",
            "expected_need", "resolution_verified"
        )):
            raise ValueError("boolean type invalid: " + c["id"])
        if c["original_delivery"] not in DELIVERIES or c["correction_delivery"] not in DELIVERIES:
            raise ValueError("delivery status invalid: " + c["id"])
        if c["action_state"] not in ACTION_STATES or c["reversible"] not in REVERSIBILITY:
            raise ValueError("action/reversibility status invalid: " + c["id"])
        if c["deadline"] not in {"open", "expired"}:
            raise ValueError("deadline invalid: " + c["id"])
        if type(c["visible_previous"]) is not int or c["visible_previous"] < 0:
            raise ValueError("previous-message count invalid: " + c["id"])
        if not all(isinstance(c[k], str) and c[k] for k in (
            "id", "category", "original_message_id", "source_id", "event_id",
            "intended_actor", "correction_for", "correction_source",
            "correction_event", "correction_actor"
        )):
            raise ValueError("identity invalid: " + c["id"])
    return cases


def valid_target(c: dict) -> bool:
    """Only *within-field* identity equality; no numeric revision ordering."""
    return (
        c["correction_for"] == c["original_message_id"]
        and c["correction_source"] == c["source_id"]
        and c["correction_event"] == c["event_id"]
        and c["correction_actor"] == c["intended_actor"]
    )


def requires_offer(c: dict) -> bool:
    """A proposed synthetic obligation, not an established operational rule."""
    return (
        c["emitted"] and c["invalidated"]
        and c["original_delivery"] != "failed"
        and not c["already_superseded"]
        and valid_target(c)
    )


def emit(c: dict, policy: str) -> dict:
    """Compute policy output, preserving unknown delivery/action separately."""
    if policy not in POLICIES:
        raise ValueError("invalid policy: " + policy)
    if policy == "silent":
        offer = False
    elif policy == "generic-closure":
        # Deliberately defective negative comparator: ignores binding, reception,
        # prior supersession and action evidence.
        offer = bool(c["emitted"] and c["invalidated"])
    else:
        offer = requires_offer(c)

    if not offer:
        return {
            "offer": False, "text": "", "bound": False, "claims_receipt": False,
            "claims_action_stopped": False, "claims_undone": False,
            "closed": False, "delivery": "not_sent", "action": c["action_state"],
        }

    if policy == "generic-closure":
        text = "Cancel that instruction. Correction received. Task stopped and consequences undone."
        return {
            "offer": True, "text": text, "bound": False, "claims_receipt": True,
            "claims_action_stopped": True, "claims_undone": True,
            "closed": True, "delivery": "assumed_confirmed",
            "action": "stopped",
        }

    text = (
        "Withdraw instruction " + c["original_message_id"] + " for source "
        + c["source_id"] + ", event " + c["event_id"] + ", actor "
        + c["intended_actor"] + "."
    )
    if policy == "bound-uncertainty":
        text += (
            " A revised instruction does not establish that the prior instruction"
            " was heard or stopped. Verify action status and consequences separately."
        )
    delivered = c["correction_delivery"] == "confirmed"
    # An action/completion claim requires separate, positive *synthetic*
    # restoration evidence. Even verified correction delivery alone is insufficient.
    closed = bool(delivered and c["resolution_verified"])
    return {
        "offer": True, "text": text, "bound": True, "claims_receipt": False,
        "claims_action_stopped": False, "claims_undone": False,
        "closed": closed,
        "delivery": "confirmed" if delivered else "pending_or_failed",
        "action": c["action_state"],
    }


def assess(cases: list[dict], policy: str) -> dict:
    metrics: Counter = Counter()
    observations: list[dict] = []
    for c in cases:
        out = emit(c, policy)
        required = c["expected_need"]
        # Keep the independent gold label distinct from the policy itself.
        if requires_offer(c) != required:
            raise ValueError("golden eligibility contradiction: " + c["id"])
        if required:
            metrics["required"] += 1
        if out["offer"]:
            metrics["offers"] += 1
            metrics["tokens"] += len(out["text"].split())
            if c["urgent_other"]:
                metrics["urgent_interruption_tokens_proxy"] += len(out["text"].split())
            if not required:
                metrics["unnecessary_offers"] += 1
            if not out["bound"] and c["visible_previous"] > 1:
                metrics["unbound_ambiguous"] += 1
            if out["claims_receipt"] and c["correction_delivery"] != "confirmed":
                metrics["unsupported_receipt_claims"] += 1
            if out["claims_action_stopped"] and not c["resolution_verified"]:
                metrics["unsupported_action_claims"] += 1
            if out["claims_undone"] and not c["resolution_verified"]:
                metrics["unsupported_undo_claims"] += 1
            if out["closed"] and (
                not c["resolution_verified"] or c["correction_delivery"] != "confirmed"
            ):
                metrics["premature_closure"] += 1
            if c["action_state"] == "unknown" and out["action"] != "unknown":
                metrics["erased_unknown_action"] += 1
        elif required:
            metrics["missing_offers"] += 1
        if required and (not out["offer"] or not out["closed"]):
            metrics["unresolved_required_obligations"] += 1
        observations.append({
            "id": c["id"], "required": required, "offer": out["offer"],
            "bound": out["bound"], "delivery": out["delivery"],
            "action": out["action"], "closed": out["closed"],
        })

    names = (
        "required", "offers", "missing_offers", "unnecessary_offers",
        "unbound_ambiguous", "unsupported_receipt_claims",
        "unsupported_action_claims", "unsupported_undo_claims",
        "premature_closure", "erased_unknown_action",
        "unresolved_required_obligations", "tokens",
        "urgent_interruption_tokens_proxy",
    )
    return {"policy": policy, "cases": len(cases),
            "metrics": {name: metrics[name] for name in names},
            "observations": observations}


def build_report(path: Path = FIXTURE) -> dict:
    cases = load_cases(path)
    return {
        "status": "fictional_structural_comparison_only",
        "dataset_kind": "fictional",
        "case_count": len(cases),
        "policies": [assess(cases, name) for name in POLICIES],
        "limits": [
            "No acoustic delivery, comprehension, observed human behavior or elapsed-time estimates",
            "Synthetic delivery and world-resolution fields are declared, not measured",
            "The generic comparator is deliberately invalid; its metrics do not estimate real systems",
            "Tokens/urgent interruption tokens are text-length proxies, not listening or safety costs",
        ],
    }


def check_report(report: dict) -> None:
    if report["case_count"] < 28:
        raise AssertionError("not enough cases")
    m = {row["policy"]: row["metrics"] for row in report["policies"]}
    for name in ("bound-minimal", "bound-uncertainty"):
        for key in (
            "missing_offers", "unnecessary_offers", "unsupported_receipt_claims",
            "unsupported_action_claims", "unsupported_undo_claims",
            "premature_closure", "erased_unknown_action",
        ):
            if m[name][key] != 0:
                raise AssertionError(name + " violates " + key)
    if m["silent"]["missing_offers"] != m["silent"]["required"]:
        raise AssertionError("silent control fails to omit offers")
    if m["generic-closure"]["unsupported_undo_claims"] == 0:
        raise AssertionError("negative comparator no longer provides a counterexample")
    if m["bound-uncertainty"]["tokens"] <= m["bound-minimal"]["tokens"]:
        raise AssertionError("verbosity comparator not differentiated")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true", help="apply structural expectations")
    p.add_argument("--output", type=Path, help="write deterministic JSON report")
    args = p.parse_args()
    report = build_report()
    if args.check:
        check_report(report)
    data = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
