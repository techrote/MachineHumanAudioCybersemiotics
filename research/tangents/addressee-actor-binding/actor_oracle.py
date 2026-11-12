"""MHAC-T008: deterministic fictional actor-binding falsification, not human performance.
Python 3.11+ standard library. Names, events, observations and labels are fabricated.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ACTORS=("alpha","alfa","beta","gamma")
POLICIES=("source_event_only","external_authorization","audience_gate","confirmation_gate","accessible_fallback_gate")

def case(name, *, scope="explicit", targets=("alpha",), heard=("alpha",),
         authorized=("alpha",), auth_version=2, message_version=2,
         expiry=100, deadline=80, ack=(), actions=(), fallback=(),
         valid=True, presentation="clean", expected=()):
    return dict(name=name,source_id="synth-machine-1",event_id="event-1",
                message_id="message-1",state_version=1,requested_action="inspect",
                message_valid=valid,audience_scope=scope,target_audience=list(targets),
                heard_by=list(heard),authorized_actors=list(authorized),
                authorization_version=auth_version,message_auth_version=message_version,
                expires_at=expiry,deadline=deadline,address_presentation=presentation,
                fallback_received_by=list(fallback),
                acknowledgements=[dict(actor=a,time=t,authorization_version=v) for a,t,v in ack],
                actions=[dict(actor=a,time=t,authorization_version=v) for a,t,v in actions],
                expected_authorized=list(expected[0]) if expected else [],
                expected_misrouted_ack=list(expected[1]) if expected else [])

# Hand-declared expected labels are independent of the evaluation model.
CASES=[
 case("direct_success",ack=(("alpha",2,2),),actions=(("alpha",3,2),),expected=([0],[])),
 case("broadcast_external_permission",scope="broadcast",targets=(),heard=("alpha","beta"),actions=(("alpha",3,2),),expected=([0],[])),
 case("broadcast_wrong_actor",scope="broadcast",targets=(),heard=("alpha","beta"),actions=(("beta",3,2),),expected=([],[])),
 case("two_listeners_wrong_first",heard=("alpha","beta"),actions=(("beta",4,2),("alpha",7,2)),expected=([1],[])),
 case("near_homophone",heard=("alpha","alfa"),presentation="near_homophone",actions=(("alfa",5,2),),expected=([],[])),
 case("clipped_address",heard=("alpha","beta"),presentation="clipped",actions=(("beta",5,2),),expected=([],[])),
 case("missing_address",scope="unknown",targets=(),actions=(("alpha",5,2),),expected=([0],[])),
 case("group_scope",scope="group",targets=("alpha","beta"),authorized=("alpha","beta"),heard=("alpha","beta"),actions=(("beta",5,2),),expected=([0],[])),
 case("wrong_group_member",scope="group",targets=("alpha","beta"),authorized=("alpha","beta"),heard=("alpha","gamma"),actions=(("gamma",5,2),),expected=([],[])),
 case("simultaneous_other_message",heard=("alpha","beta"),presentation="competing_message",actions=(("beta",6,2),),expected=([],[])),
 case("handover_old_actor",authorized=("beta",),targets=("alpha",),heard=("alpha","beta"),actions=(("alpha",8,2),),expected=([],[])),
 case("handover_new_actor",authorized=("beta",),targets=("beta",),heard=("beta",),actions=(("beta",8,2),),expected=([0],[])),
 case("stale_message_authority",message_version=1,actions=(("alpha",6,2),),expected=([],[])),
 case("stale_action_authority",actions=(("alpha",6,1),),expected=([],[])),
 case("expired_authority",expiry=5,actions=(("alpha",7,2),),expected=([],[])),
 case("no_authorized_actors",authorized=(),actions=(("alpha",6,2),),expected=([],[])),
 case("non_target_ack",heard=("alpha","beta"),ack=(("beta",3,2),),actions=(("alpha",6,2),),expected=([0],[0])),
 case("correct_ack_wrong_action",heard=("alpha","beta"),ack=(("alpha",2,2),),actions=(("beta",4,2),),expected=([],[])),
 case("correct_action_without_ack",actions=(("alpha",4,2),),expected=([0],[])),
 case("late_corrective_readback",ack=(("alpha",85,2),),actions=(("alpha",88,2),),expected=([0],[])),
 case("silent_recipient",actions=(),expected=([],[])),
 case("wrong_then_correct_after_deadline",heard=("alpha","beta"),actions=(("beta",4,2),("alpha",90,2)),expected=([1],[])),
 case("repair_after_handover",authorized=("beta",),targets=("beta",),ack=(("alpha",5,1),),actions=(("beta",7,2),),expected=([0],[0])),
 case("fallback_non_audio",heard=(),fallback=("alpha",),actions=(("alpha",8,2),),expected=([0],[])),
 case("audio_unavailable_no_fallback",heard=(),actions=(("alpha",8,2),),expected=([0],[])),
 case("unknown_audience_wrong_actor",scope="unknown",targets=(),heard=("alpha","beta"),actions=(("beta",8,2),),expected=([],[])),
 case("actor_irrelevant_broadcast",scope="broadcast",targets=(),authorized=ACTORS,heard=ACTORS,actions=(("gamma",9,2),),expected=([0],[])),
 case("presentation_only_unchanged_truth",presentation="spectrally_shifted",actions=(("alpha",3,2),),expected=([0],[])),
 case("invalid_message",valid=False,actions=(("alpha",3,2),),expected=([],[])),
 case("multiple_acks_first_wrong",heard=("alpha","beta"),ack=(("beta",2,2),("alpha",4,2)),actions=(("alpha",5,2),),expected=([0],[0])),
]

def validate(c):
    keys=("name","source_id","event_id","message_id","state_version","requested_action",
          "message_valid","audience_scope","target_audience","heard_by","authorized_actors",
          "authorization_version","message_auth_version","expires_at","deadline",
          "address_presentation","fallback_received_by","acknowledgements","actions",
          "expected_authorized","expected_misrouted_ack")
    if set(c)!=set(keys):raise ValueError("fixture fields differ from closed contract")
    if c["audience_scope"] not in ("explicit","broadcast","group","unknown"):raise ValueError("invalid audience_scope")
    if (c["audience_scope"] in ("broadcast","unknown"))!=(not c["target_audience"]):raise ValueError("ambiguous audience")
    if c["audience_scope"] in ("explicit","group") and not c["target_audience"]:raise ValueError("empty audience")
    if type(c["message_valid"]) is not bool:raise ValueError("message_valid type")
    if not all(type(c[x]) is int and c[x]>=0 for x in ("authorization_version","message_auth_version","deadline","expires_at")):raise ValueError("invalid versions/times")
    for field in ("target_audience","heard_by","authorized_actors","fallback_received_by"):
        if not isinstance(c[field],list) or len(set(c[field]))!=len(c[field]) or any(a not in ACTORS for a in c[field]):raise ValueError("invalid actor set: "+field)
    if any(type(x) is not int or x<0 or x>=len(c["actions"]) for x in c["expected_authorized"]):raise ValueError("bad truth action index")
    if any(type(x) is not int or x<0 or x>=len(c["acknowledgements"]) for x in c["expected_misrouted_ack"]):raise ValueError("bad truth ack index")
    for kind in ("acknowledgements","actions"):
        for x in c[kind]:
            if set(x)!={"actor","time","authorization_version"} or x["actor"] not in ACTORS or type(x["time"]) is not int or x["time"]<0 or type(x["authorization_version"]) is not int or x["authorization_version"]<0:raise ValueError("invalid observation")

def ground_truth(c,item):
    return bool(c["message_valid"] and c["message_auth_version"]==c["authorization_version"]
                and item["authorization_version"]==c["authorization_version"]
                and item["actor"] in c["authorized_actors"] and item["time"]<=c["expires_at"])

def addressed(c,actor):
    return c["audience_scope"]=="broadcast" or (c["audience_scope"] in ("explicit","group") and actor in c["target_audience"])

def delivered(c,actor):
    return actor in c["heard_by"] or actor in c["fallback_received_by"]

def permit(c,action,policy):
    if not c["message_valid"]:return False
    if policy=="source_event_only":return True # intentionally unsafe baseline
    if not ground_truth(c,action):return False
    if policy=="external_authorization":return True
    if not addressed(c,action["actor"]):return False
    if policy=="audience_gate":return action["actor"] in c["heard_by"]
    if policy=="confirmation_gate":
        return action["actor"] in c["heard_by"] and any(
            a["actor"]==action["actor"] and a["time"]<=action["time"] and
            a["authorization_version"]==c["authorization_version"] for a in c["acknowledgements"])
    if policy=="accessible_fallback_gate":return delivered(c,action["actor"])
    raise ValueError("unknown policy")

def run():
    if len({c["name"] for c in CASES})!=len(CASES):raise ValueError("duplicate names")
    results=[]
    for c in CASES:
        validate(c)
        true_actions=[i for i,a in enumerate(c["actions"]) if ground_truth(c,a)]
        wrong_acks=[i for i,a in enumerate(c["acknowledgements"]) if not ground_truth(c,a) or (c["audience_scope"]!="unknown" and not addressed(c,a["actor"]))]
        if true_actions!=c["expected_authorized"] or wrong_acks!=c["expected_misrouted_ack"]:
            raise AssertionError("independent fixture truth disagreement: "+c["name"])
        predictions={p:[i for i,a in enumerate(c["actions"]) if permit(c,a,p)] for p in POLICIES}
        results.append({"case":c["name"],"ground_truth_authorized":true_actions,
                        "wrong_actor_attempts":[i for i in range(len(c["actions"])) if i not in true_actions],
                        "misrouted_acknowledgements":wrong_acks,
                        "deadline_misses":[i for i in true_actions if c["actions"][i]["time"]>c["deadline"]],
                        "first_attempt_authorized":(0 in true_actions if c["actions"] else None),
                        "final_attempt_authorized":(len(c["actions"])-1 in true_actions if c["actions"] else None),
                        "policy_allowed":predictions})
    return results

def canonical(o):return (json.dumps(o,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode("utf-8")

def artifacts():
    outputs={"FICTIONAL-TRACES.json":canonical({"fictional":True,"source":"MHAC-T008 declared fixture labels","cases":CASES}),
             "RESULTS.json":canonical({"fictional":True,"metric_type":"symbolic_rule_comparison_not_listener_performance","results":run()})}
    hashes={name:hashlib.sha256(data).hexdigest() for name,data in sorted(outputs.items())}
    outputs["MANIFEST.json"]=canonical({"algorithm":"sha256","artifacts":hashes,"fixture_count":len(CASES),"version":1})
    return outputs

def main():
    p=argparse.ArgumentParser(description=__doc__)
    x=p.add_mutually_exclusive_group(required=True);x.add_argument("--write",action="store_true");x.add_argument("--check",action="store_true")
    args=p.parse_args();outputs=artifacts()
    for name,data in outputs.items():
        path=HERE/name
        if args.write:path.write_bytes(data)
        elif (name=="MANIFEST.json" and not path.exists()) or (path.exists() and path.read_bytes()!=data):raise SystemExit("FAIL stale or missing: "+name)
    print(f"PASS {len(CASES)} fictional cases, {len(POLICIES)} models; deterministic artifacts {'written' if args.write else 'verified'}")

if __name__=="__main__":main()
