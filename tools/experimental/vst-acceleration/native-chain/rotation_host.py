"""ACCEL-021: pinned 0.3.1 vs 0.3.0 Windows host rotation witness.
Whole-render wall time includes Python/host overhead; never callback deadlines.
"""
import argparse
import json
from pathlib import Path
import time
import unittest
import numpy as np

A31 = ("MHACAfterimage", "d09540c3870ef3684022ed17358c3d5556d70064",
       "ff3ee494ff663515347000342c5ac9eeccbd7754b595d0d35fa2c64fb9273502",
       "BD0B8CB3B82E43EB9613F0C9A37FBA83", "0.3.1")
RATES = (48000, 96000)
BLOCKS = (32, 257, 1024)
EPS = 2e-6


def score():
    # Eight-note chords, alternating disjoint pitches; old notes release
    # after the new onsets, exercising bounded voice replacement/fading.
    events = []
    for i in range(40):
        pitches = range(48 + 12*(i % 2), 56 + 12*(i % 2))
        t = (8+i*12)/1000
        events.extend((bytes((0x90, n, 90)), t) for n in pitches)
        events.extend((bytes((0x80, n, 0)), t+.013) for n in pitches)
    return sorted(events, key=lambda e: e[1])


def compare(a, b, rate):
    for x in (a,b):
        if x.shape != (2,rate) or not np.isfinite(x).all():
            raise ValueError("shape or nonfinite")
        if not .005 < np.max(np.abs(x)) <= .521:
            raise ValueError("silent or excessive peak")
        if np.max(np.abs(x[:,-rate//10:])) > EPS or np.max(np.abs(x[0]-x[1])) > EPS:
            raise ValueError("release or stereo")
    delta = float(np.max(np.abs(a-b)))
    if delta > EPS:
        raise ValueError("rotation regression")
    return delta


class Tests(unittest.TestCase):
    def test_score(self):
        active = set()
        peak = 0
        events = score()
        self.assertEqual(len(events),640)
        for message,t in events:
            self.assertTrue(0 < t < .5)
            n = message[1]
            if message[0] == 0x90:
                self.assertNotIn(n,active);active.add(n)
            else:
                self.assertIn(n,active);active.remove(n)
            peak=max(peak,len(active))
        self.assertEqual(peak,16)
        self.assertFalse(active)

    def test_compare(self):
        for rate in RATES:
            a=np.zeros((2,rate),np.float32);a[:,rate//10:rate//2]=.1
            self.assertEqual(compare(a,a.copy(),rate),0)
            b=a.copy();b[:,rate//4]+=1e-6
            self.assertLess(compare(a,b,rate),EPS)
            for bad in (a*0,a*np.nan,a*10,a[:,:-1],a+.01,a*.9):
                with self.assertRaises(ValueError):compare(a,bad,rate)


def run(old,new,out):
    import afterimage_receipt_host as chain
    import phase_balanced_host as pb
    import host_audition as h
    out.mkdir(parents=True,exist_ok=True)
    report={"scope":__doc__,"cases":[]}
    def persist():
        (out/"rotation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    try:
        ob,report["old"]=chain.package(old,out/"old",pb.A3)
        nb,report["new"]=chain.package(new,out/"new",A31)
        for rate in RATES:
            reference={}
            for block in BLOCKS:
                for mix in (0,2,3):
                    c=dict(rate=rate,block=block,mix=mix,status="started");report["cases"].append(c);persist()
                    state=pb.phase(3,mix)
                    def render(bundle,pin):
                        p=chain.prepare(bundle,pin,state,rate,block,True)
                        start=time.perf_counter()
                        x=h.checked(p(score(),duration=1.,sample_rate=rate,num_channels=2,buffer_size=block,reset=False),rate)
                        elapsed=time.perf_counter()-start
                        h.verify_component(p,pin[3],state)
                        return x,elapsed
                    a,t0=render(ob,pb.A3);b,t1=render(nb,A31)
                    c.update(error=compare(a,b,rate),old_wall_seconds=t0,new_wall_seconds=t1,old=h.metrics(a),new=h.metrics(b))
                    again,t2=render(nb,A31);c["repeat_error"]=compare(b,again,rate)
                    if mix in reference:c["partition_error"]=compare(reference[mix],b,rate)
                    else:reference[mix]=b
                    c["status"]="pass";persist()
        report["complete"]=True
    except Exception as exc:
        report["error"]=repr(exc);raise
    finally:persist()


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("old","new","out"):p.add_argument("--"+name,type=Path)
    args=p.parse_args()
    if not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests)).wasSuccessful():raise SystemExit(1)
    if any(vars(args).values()):
        if not all(vars(args).values()):p.error("all three arguments required")
        run(args.old,args.new,args.out)
