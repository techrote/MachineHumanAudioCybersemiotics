"""ACCEL-025: three-plugin group routing, pinned Windows host renders.
The pure routing tests run without plugins; no DAW scan or listening claim.
"""
import argparse
import json
from pathlib import Path
import unittest
import numpy as np

RATES = (44100, 48000, 96000)
BLOCKS = (257, 1024)
EPS = 2e-6
DURATION = 3


def require(ok, message):
    if not ok:
        raise ValueError(message)


def checked(x, rate):
    require(x.shape == (2, DURATION*rate) and np.isfinite(x).all(), "shape/finite")
    require(np.max(np.abs(x)) <= 1, "overload")
    require(np.max(np.abs(x[:, :rate//10])) < EPS, "leading silence")
    require(np.max(np.abs(x[:, -rate//10:])) < EPS, "release silence")
    require(np.max(np.abs(x)) > .001, "silent track")
    return x


def place(x, rate, start):
    require(x.ndim == 2 and x.shape[0] == 2 and np.isfinite(x).all(), "invalid stem")
    require(0 <= start <= DURATION*rate-x.shape[1], "stem extent")
    out = np.zeros((2, DURATION*rate), np.float32)
    out[:, start:start+x.shape[1]] = x
    return out


def route(a, lanes, rate):
    require(len(lanes) == 3, "three winter lanes required")
    a = checked(a, rate)
    w = np.zeros_like(a)
    for lane in lanes:
        w += checked(lane, rate)*np.float32(.125)
    return checked(a*np.float32(.5) + w, rate)


def compare(a, b):
    require(a.shape == b.shape and np.isfinite(a).all() and np.isfinite(b).all(), "comparison shape/finite")
    error = float(np.max(np.abs(a-b)))
    require(error < EPS, f"waveform mismatch {error}")
    return error


class Tests(unittest.TestCase):
    def test_routing(self):
        for rate in RATES:
            stem = np.zeros((2,rate), np.float32)
            stem[0,rate//4:rate//2] = .125
            stem[1,rate//4:rate//2] = -.25
            x = place(stem,rate,rate//5)
            y = route(x,[x,x,x],rate)
            np.testing.assert_array_equal(y,x*np.float32(.875))
            for bad in (x*0,x*np.nan,x*16,x[:,:-1],x+.01):
                with self.assertRaises(ValueError): route(x,[x,bad,x],rate)
            with self.assertRaises(ValueError): place(stem,rate,3*rate)
            with self.assertRaises(ValueError): route(x,[x,x],rate)
            self.assertEqual(compare(y,y.copy()),0)
            with self.assertRaises(ValueError): compare(y,y+.01)


def run(afterimage, winters, receipt, out):
    import afterimage_receipt_host as chain
    import afterimage_depth_host as ac
    import phase_balanced_host as pb
    import receipt_fold_upgrade_host as rf
    import rotation_host as rotation
    import winters_host as winter
    import host_audition as h
    out.mkdir(parents=True,exist_ok=True)
    report = {"scope":__doc__, "cases":[]}
    def persist():
        (out/"three-plugin.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    try:
        ab,report["afterimage"] = chain.package(afterimage,out/"afterimage",rotation.A31)
        wb,report["winters"] = winter.extract(winters,out/"winters")
        fb,report["receipt"] = chain.package(receipt,out/"receipt",pb.F3)
        require(report["afterimage"]["binary_sha256"] == "87774d7877810de06d0abb7ecdaff9bd290829c86ebc0cf8639fc5bef62dc089", "Afterimage binary pin")
        require(report["receipt"]["binary_sha256"] == "c13a44cfd6bf0a6979b362a8dd057bd7c309e95a467a8f2558c340404b320776", "Receipt binary pin")
        base = rf.rf03(bits=4,budget=0,a=112,b=128,fine=True,mode=1,wet=.625)
        bypass = rf.rf03(bits=4,bypass=True,wet=.625)
        modes = [("legacy",pb.balanced(base)), ("balanced",pb.balanced(base,True,25,7)), ("bypass",pb.balanced(bypass,True,25,7))]
        for rate in RATES:
            reference = {}
            for block in BLOCKS:
                s = pb.phase(3,3)
                p = chain.prepare(ab,rotation.A31,s,rate,block,True)
                events = [(msg,t+.2) for msg,t in ac.events(ac.HISTORIES[0])]
                a = checked(p(events,duration=3.,sample_rate=rate,num_channels=2,buffer_size=block,reset=False),rate)
                h.verify_component(p,rotation.A31[3],s)
                lanes = [place(winter.perform(wb,rate,block,lane)[0],rate,rate//2) for lane in range(3)]
                dry = route(a,lanes,rate)
                outputs = {}
                for name,state in modes:
                    c = dict(rate=rate,block=block,mode=name,status="started",dry=h.metrics(dry))
                    report["cases"].append(c);persist()
                    def render(saved=None):
                        f = chain.prepare(fb,pb.F3,state,rate,block,False,saved)
                        y = checked(f(dry.copy(),rate,buffer_size=block,reset=False),rate)
                        h.verify_component(f,pb.F3[3],state)
                        return y,f.preset_data
                    y,saved = render()
                    c["restore_error"] = compare(y,render(saved)[0])
                    if name == "legacy": c["oracle_error"] = compare(y,rf.oracle(dry,base))
                    if name == "bypass": c["bypass_error"] = compare(y,dry)
                    if name == "balanced":
                        c["contrast"] = float(np.max(np.abs(y-outputs["legacy"])))
                        require(c["contrast"] > 1e-4,"missing balanced contrast")
                    if name in reference: c["partition_error"] = compare(y,reference[name])
                    else: reference[name] = y.copy()
                    outputs[name] = y
                    c["output"] = h.metrics(y);c["status"]="pass";persist()
                if rate == 48000 and block == 257:
                    h.wav(out/"dry-group.wav",dry)
                    h.wav(out/"legacy-group.wav",outputs["legacy"])
                    h.wav(out/"balanced-group.wav",outputs["balanced"])
        report["complete"] = True
    except Exception as exc:
        report["error"] = repr(exc);raise
    finally: persist()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("afterimage","winters","receipt","out"):
        p.add_argument("--"+name,type=Path)
    args = p.parse_args()
    if not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests)).wasSuccessful():
        raise SystemExit(1)
    if any(vars(args).values()):
        if not all(vars(args).values()): p.error("all four arguments required")
        run(args.afterimage,args.winters,args.receipt,args.out)
