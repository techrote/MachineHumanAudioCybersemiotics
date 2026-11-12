"""MHAC-T017: closed-world fictional measurement/decision/speech-authority falsifier.

No metrology algorithm, real-world decision rule, human outcome, or live source input.
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICIES = ("value_only", "naive", "local_rule", "upstream_warrant")
CLASSES = ("conforming", "nonconforming", "indeterminate")


def load_cases():
    data = json.loads((HERE / "FICTIONAL-CASES.json").read_text(encoding="utf-8"))
    if data.get("kind") != "fictional_t017_not_participant_data":
        raise ValueError("Only declared fictional input accepted")
    cases = data["cases"]
    if len(cases) != 32 or len({case["id"] for case in cases}) != 32:
        raise ValueError("Required 32 unique independent scenario labels")
    return cases


def public_input(case):
    """Policies cannot inspect world truth or pre-authored expected outputs."""
    return {k: v for k, v in case.items()
            if k not in ("ground_truth", "independent_policy_expectations")}


def valid_rule(observable):
    m, spec, r = observable["measurement"], observable["specification"], observable["rule"]
    return bool(
        r and r["active"] and m["valid"] and m["current"]
        and m["uncertainty"] == "declared"
        and m["quantity"] == spec["quantity"] == r["quantity"]
        and m["unit"] == spec["unit"] == r["unit"]
        and r["context"] == "fictional_bench"
        and r["accept_max"] < r["reject_min"]
    )


def rule_label(observable):
    if not valid_rule(observable):
        return None
    m, r = observable["measurement"], observable["rule"]
    value = m["value_tenths"]
    if value <= r["accept_max"]:
        return "conforming"
    if value >= r["reject_min"]:
        return "nonconforming"
    return "indeterminate"


def render(observable, policy):
    if policy not in POLICIES:
        raise ValueError("Unknown policy")
    m, spec, upstream = observable["measurement"], observable["specification"], observable["upstream"]
    claim = None
    no_action = False
    reported = m["value_tenths"] if policy != "naive" else m["spoken_value_tenths"]
    # One-tenth integer representation is a fabricated unit for the toy ledger.
    words = ["Reading", f"{reported / 10:.1f}", m["unit"] + "."]
    if policy == "naive":
        claim = "conforming" if reported <= spec["upper_tenths"] else "nonconforming"
        no_action = claim == "conforming"
        words.extend(["Within", "tolerance."] if no_action else ["Outside", "tolerance."])
        if no_action:
            words.extend(["No", "action", "needed."])
    elif policy == "local_rule":
        claim = rule_label(observable)
        words.extend(["Local", "classification:", claim + "."] if claim else ["Class", "unknown."])
    elif policy == "upstream_warrant":
        candidate = rule_label(observable)
        r = observable["rule"]
        if (candidate is not None and upstream["authorized"] and upstream["current"]
                and upstream["evidence_trace"] and upstream["rule_id"] == r["id"]
                and upstream["rule_version"] == r["version"]
                and upstream["decision"] == candidate):
            claim = candidate
            words.extend(["Upstream", "decision:", claim + "."])
        else:
            words.extend(["Conformity", "not", "established."])
    return {"claim": claim, "no_action": no_action, "reported_tenths": reported,
            "word_tokens": len(words), "message": " ".join(words)}


def score(case, output):
    truth = case["ground_truth"]
    claim = output["claim"]
    permitted = truth["permitted_class"]
    world = truth["world_conforming"]
    m = case["measurement"]
    return {
        "unsupported_class": int(claim is not None and claim != permitted),
        "false_accept_world": int(claim == "conforming" and not world),
        "false_reject_world": int(claim == "nonconforming" and world),
        "withheld_warranted_binary_class": int(
            permitted in ("conforming", "nonconforming") and claim != permitted),
        "withheld_warranted_indeterminate": int(
            permitted == "indeterminate" and claim != "indeterminate"),
        "unsupported_no_action": int(output["no_action"] and not truth["no_action_authorized"]),
        "misreported_numeric_value": int(output["reported_tenths"] != m["value_tenths"]),
        "class_while_rule_unavailable": int(claim is not None and not valid_rule(public_input(case))),
        "word_tokens": output["word_tokens"],
    }


def compare(cases=None):
    cases = load_cases() if cases is None else cases
    policies = {}
    per_case = {}
    for policy in POLICIES:
        totals = Counter()
        per_case[policy] = {}
        for case in cases:
            output = render(public_input(case), policy)
            result = score(case, output)
            totals.update(result)
            per_case[policy][case["id"]] = {"claim": output["claim"], "metrics": result}
        policies[policy] = dict(sorted(totals.items()))
    return {"kind": "constructed_logical_cases_not_human_observation", "case_count": len(cases),
            "policies": policies, "per_case": per_case}


if __name__ == "__main__":
    print(json.dumps(compare(), sort_keys=True, indent=2))
