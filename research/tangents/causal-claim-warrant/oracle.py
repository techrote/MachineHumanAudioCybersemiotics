"""MHAC-T016: deliberately fictional, closed-world policy comparison."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICIES = ("naive", "state_only", "alternatives", "warranted")


def load_cases():
    document = json.loads((HERE / "FICTIONAL-CASES.json").read_text(encoding="utf-8"))
    if document["kind"] != "fictional_constructed_cases_not_people":
        raise ValueError("non-fictional input is prohibited")
    cases = document["cases"]
    if len(cases) != 32 or len({c["id"] for c in cases}) != 32:
        raise ValueError("expected 32 distinct predeclared fictional cases")
    return cases


def public_input(case):
    """Exclude both actual-cause truth and independently labelled warrant."""
    return {k: v for k, v in case.items() if k != "ground_truth"}


def render(observable, policy):
    """Return policy's claims. No access to ground truth."""
    if policy not in POLICIES:
        raise ValueError("unknown policy")
    obs, hypo, test = observable["observation"], observable["hypothesis"], observable["test"]
    eff = observable["intervention"]
    valid = obs["valid"]
    asserted = None
    candidates = []
    offer = False
    parts = ["Extrusion anomaly observed." if (valid or policy == "naive")
             else "Extrusion reading unverified."]
    if policy == "naive":
        asserted = hypo["favored"]
        parts.append("Cause is " + asserted + ".")
        offer = True
    elif policy == "alternatives" and valid:
        candidates = list(hypo["candidates"])
        parts.append("Possible causes are " + " or ".join(candidates) + "; not established.")
    elif policy == "warranted" and valid and test["kind"] == "diagnostic" and test["current"]:
        asserted = test["supports"]
        parts.append("Diagnostic test supports cause " + asserted + ".")
        offer = (eff["effect_evidence"] == "validated" and eff["actor_authorized"]
                 and eff["mode_permits"] and eff["deadline_feasible"])
    if offer:
        action_cause = asserted if policy == "warranted" else hypo["favored"]
        parts.append("Offer " + ("inspect feed path." if action_cause == "feed" else "clear nozzle."))
    message = " ".join(parts)
    return {"message": message, "asserted_cause": asserted,
            "candidate_causes": candidates, "offered_action": offer,
            "observation_claimed": valid or policy == "naive",
            "words": len(message.split())}


def score(case, output):
    """Score against labels prepared independently of all four policies."""
    truth = case["ground_truth"]
    asserted = output["asserted_cause"]
    budget = 10 if case["urgency"] == "urgent" else 26
    return {
        "unsupported_cause": int(asserted is not None and asserted != truth["warranted_cause"]),
        "factually_wrong_cause": int(asserted is not None and asserted != truth["actual_cause"]),
        "invalid_observation_claim": int(output["observation_claimed"] and not truth["warranted_observation"]),
        "omitted_valid_observation": int(not output["observation_claimed"] and truth["warranted_observation"]),
        "unsupported_action_offer": int(output["offered_action"] and not truth["warranted_action_offer"]),
        "withheld_warranted_diagnosis": int(truth["warranted_cause"] is not None and asserted is None),
        "withheld_warranted_action": int(truth["warranted_action_offer"] and not output["offered_action"]),
        "candidate_narrations": int(bool(output["candidate_causes"])),
        "word_tokens": output["words"],
        "over_constructed_word_budget": int(output["words"] > budget),
    }


def compare(cases=None):
    cases = load_cases() if cases is None else cases
    summaries = {}
    for policy in POLICIES:
        aggregate = Counter()
        for case in cases:
            aggregate.update(score(case, render(public_input(case), policy)))
        summaries[policy] = dict(sorted(aggregate.items()))
    return {"case_count": len(cases), "kind": "constructed_symbolic_only",
            "policies": summaries}


if __name__ == "__main__":
    print(json.dumps(compare(), indent=2, sort_keys=True))
