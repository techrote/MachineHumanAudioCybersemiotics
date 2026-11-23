"""MHAC-T008: deterministic fictional actor-binding contract, no listeners."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"research/tangents/addressee-actor-binding/actor_oracle.py"
spec=importlib.util.spec_from_file_location("mhac_t008_oracle",SCRIPT)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ActorBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results={r["case"]:r for r in m.run()}
        cls.cases={c["name"]:c for c in m.CASES}

    def test_independent_truth_and_count(self):
        self.assertEqual(len(m.CASES),30)
        self.assertEqual(len(self.results),30)
        for c in m.CASES:
            m.validate(c)
            self.assertEqual(c["expected_authorized"],
                             [i for i,a in enumerate(c["actions"]) if m.ground_truth(c,a)])
        r=self.results["two_listeners_wrong_first"]
        self.assertEqual(r["ground_truth_authorized"],[1])
        self.assertFalse(r["first_attempt_authorized"])
        self.assertTrue(r["final_attempt_authorized"])

    def test_source_only_wrong_actor_and_broadcast_null(self):
        r=self.results["near_homophone"]
        self.assertEqual(r["policy_allowed"]["source_event_only"],[0])
        self.assertEqual(r["policy_allowed"]["external_authorization"],[])
        for name in ("broadcast_external_permission","actor_irrelevant_broadcast"):
            self.assertEqual(self.results[name]["policy_allowed"]["external_authorization"],[0])

    def test_ack_never_grants_permission(self):
        self.assertEqual(self.results["correct_ack_wrong_action"]["policy_allowed"]["confirmation_gate"],[])
        self.assertEqual(self.results["non_target_ack"]["misrouted_acknowledgements"],[0])
        self.assertEqual(self.results["multiple_acks_first_wrong"]["misrouted_acknowledgements"],[0])

    def test_stale_unknown_expired(self):
        for name in ("stale_message_authority","stale_action_authority","expired_authority","no_authorized_actors","invalid_message"):
            r=self.results[name]
            self.assertEqual(r["ground_truth_authorized"],[])
            self.assertEqual(r["policy_allowed"]["external_authorization"],[])
        self.assertEqual(self.results["missing_address"]["policy_allowed"]["audience_gate"],[])
        self.assertEqual(self.results["missing_address"]["policy_allowed"]["external_authorization"],[0])

    def test_delivery_vs_authorization(self):
        self.assertEqual(self.results["fallback_non_audio"]["policy_allowed"]["accessible_fallback_gate"],[0])
        self.assertEqual(self.results["fallback_non_audio"]["policy_allowed"]["audience_gate"],[])
        self.assertEqual(self.results["audio_unavailable_no_fallback"]["policy_allowed"]["audience_gate"],[])
        self.assertEqual(self.results["correct_action_without_ack"]["policy_allowed"]["confirmation_gate"],[])

    def test_deadline_and_presentation_invariance(self):
        self.assertEqual(self.results["late_corrective_readback"]["deadline_misses"],[0])
        self.assertEqual(self.results["wrong_then_correct_after_deadline"]["deadline_misses"],[1])
        a=self.cases["direct_success"]
        b=dict(a,address_presentation="masked")
        self.assertEqual([m.ground_truth(a,x) for x in a["actions"]],[m.ground_truth(b,x) for x in b["actions"]])

    def test_five_policy_regression_matrix(self):
        expected={"source_event_only":(16,0,14,1),"external_authorization":(16,0,0,15),
                  "audience_gate":(12,4,0,15),"confirmation_gate":(3,13,0,15),
                  "accessible_fallback_gate":(13,3,0,15)}
        for policy in m.POLICIES:
            tp=fn=fp=tn=0
            for c in m.CASES:
                r=self.results[c["name"]]
                for i in range(len(c["actions"])):
                    truth=i in r["ground_truth_authorized"]
                    pred=i in r["policy_allowed"][policy]
                    tp+=int(truth and pred);fn+=int(truth and not pred)
                    fp+=int(not truth and pred);tn+=int(not truth and not pred)
            self.assertEqual((tp,fn,fp,tn),expected[policy])

    def test_closed_schema_and_boolean_as_integer(self):
        for update in ({"heard_by":["alpha","alpha"]},{"authorization_version":True},{"rogue":"field"}):
            with self.subTest(update=update):
                with self.assertRaises(ValueError):
                    m.validate(dict(self.cases["direct_success"],**update))

    def test_sha_manifest_and_tamper_detection(self):
        artifacts=m.artifacts()
        manifest=json.loads((SCRIPT.parent/"MANIFEST.json").read_text())
        self.assertEqual(artifacts["MANIFEST.json"],(SCRIPT.parent/"MANIFEST.json").read_bytes())
        self.assertEqual(manifest["fixture_count"],30)
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)
            (dest/"actor_oracle.py").write_bytes(SCRIPT.read_bytes())
            (dest/"MANIFEST.json").write_bytes(artifacts["MANIFEST.json"])
            cmd=[sys.executable,str(dest/"actor_oracle.py")]
            good=subprocess.run(cmd+["--check"],capture_output=True,text=True)
            self.assertEqual(good.returncode,0,good.stderr)
            write=subprocess.run(cmd+["--write"],capture_output=True,text=True)
            self.assertEqual(write.returncode,0,write.stderr)
            for name,data in artifacts.items():self.assertEqual((dest/name).read_bytes(),data)
            (dest/"RESULTS.json").write_text("tampered",encoding="utf-8")
            bad=subprocess.run(cmd+["--check"],capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)

if __name__=="__main__":unittest.main()
