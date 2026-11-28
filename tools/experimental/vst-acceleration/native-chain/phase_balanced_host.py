"""ACCEL-020: AC03 and RF04 state, host contrasts and migration (Windows)."""
import argparse
import json
from pathlib import Path
import struct
import unittest
import numpy as np
import afterimage_depth_host as ac
import receipt_fold_upgrade_host as rf

A3 = ("MHACAfterimage", "9b717745daaf04b4e42bd462412947634e98671c",
      "7e6c907967e752afb2933d3523509d4b50623aefb8230803f17272b5c5465910",
      ac.NEW[3], "0.3.0")
F3 = ("MHACReceiptFold", "2cee431826772547699f43bf4d4e598cfbe7162e",
      "74ff70c9c5704fe13a1a0ee88ceaada4cc3e7076fa14e9e6d57e1da6ffabca94",
      rf.NEW[3], "0.3.0")
EPS = 2e-6


def phase(depth, mix):
    if mix not in range(4):
        raise ValueError("phase mix")
    state = ac.state(depth)
    if not mix:
        return state
    word, = struct.unpack("<I", state[4:])
    return b"AC03" + struct.pack("<I", word | mix << 30)


def balanced(base, enabled=False, epoch=25, seed=0):
    rf.unpack(base)
    if enabled not in (False, True) or epoch not in range(5, 1001) or seed not in range(65536):
        raise ValueError("balanced control")
    word, wet = struct.unpack("<Id", base[4:])
    return b"RF04" + struct.pack("<Qd", word | int(enabled)<<32 | epoch<<33 | seed<<43, wet)


def effect_states():
    base = rf.rf03(bits=4, budget=0, a=112, b=128, fine=True, mode=1)
    yield "legacy", base, balanced(base), True
    yield "short", base, balanced(base, True, 25, 7), False
    yield "long", base, balanced(base, True, 100, 7), False
    yield "seed", base, balanced(base, True, 25, 193), False
    full = rf.rf03(bits=4, budget=4, a=112, b=128, fine=True, mode=3)
    yield "full", full, balanced(full, True, 25, 7), True
    bypass = rf.rf03(bits=4, budget=0, a=112, b=128, fine=True, bypass=True)
    yield "bypass", bypass, balanced(bypass, True, 25, 7), True


class Tests(unittest.TestCase):
    def test_codec(self):
        for depth in range(1, 4):
            for mix in range(4):
                s = phase(depth, mix)
                w, = struct.unpack("<I", s[4:])
                self.assertEqual(w >> 30, mix)
                self.assertEqual((w >> 28) & 3, depth-1)
                self.assertEqual(s[:4], b"AC03" if mix else ac.state(depth)[:4])
        for _, base, s, _ in effect_states():
            w, wet = struct.unpack("<Qd", s[4:])
            self.assertEqual(s[:4], b"RF04")
            self.assertEqual(b"RF03" + struct.pack("<Id", w & 0xffffffff, wet), base)
            self.assertEqual(w >> 59, 0)
        for e in (5, 25, 1000):
            for seed in (0, 7, 65535):
                w, _ = struct.unpack("<Qd", balanced(rf.rf03(), True, e, seed)[4:])
                self.assertEqual(((w>>32)&1, (w>>33)&1023, (w>>43)&65535), (1,e,seed))
        for args in ((True,4,0), (True,1001,0), (True,25,65536), (True,25,-1)):
            with self.assertRaises(ValueError): balanced(rf.rf03(), *args)
        for mix in (-1,4):
            with self.assertRaises(ValueError): phase(3,mix)


def run(a2, f2, a3, f3, out):
    import afterimage_receipt_host as chain
    import host_audition as h
    out.mkdir(parents=True, exist_ok=True)
    report = {"scope":"exact 0.3.0 Windows binaries; state, contrast, legacy and partition", "cases":[]}
    def persist():
        (out/"phase-balanced.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    def err(x,y):
        value=chain.error(x,y)
        h.require(value<EPS,"restore/partition/legacy mismatch")
        return value
    def instrument(bundle,pin,state,rate,block,saved=None):
        p=chain.prepare(bundle,pin,state,rate,block,True,saved)
        x=h.checked(p(ac.events(ac.HISTORIES[0]),duration=2.,sample_rate=rate,
                      num_channels=2,buffer_size=block,reset=False),2*rate)
        h.verify_component(p,pin[3],state)
        h.require(np.max(np.abs(x))>.01 and np.max(np.abs(x[:,-rate//10:]))<2e-5,"instrument activity/release")
        return x,p.preset_data
    def effect(bundle,pin,imported,expected,x,rate,block,saved=None):
        p=h.open_plugin(bundle)
        h.require(p.is_effect,"effect category")
        p(np.zeros((2,rate//20),np.float32),rate,buffer_size=block)
        p.preset_data=chain.preset(pin[3],imported) if saved is None else saved
        h.verify_component(p,pin[3],expected)
        y=h.checked(p(x.copy(),rate,buffer_size=block,reset=False),x.shape[1])
        h.verify_component(p,pin[3],expected)
        return y,p.preset_data
    try:
        bundles=[]
        for path,pin,label in ((a2,ac.NEW,"a2"),(f2,rf.NEW,"f2"),(a3,A3,"a3"),(f3,F3,"f3")):
            bundle,report[label]=chain.package(path,out/label,pin);bundles.append(bundle)
        olda,oldf,newa,newf=bundles
        for rate in ac.RATES:
            reference={}
            for block in ac.BLOCKS:
                outputs={}
                for mix in range(4):
                    s=phase(3,mix)
                    c=dict(kind="phase",rate=rate,block=block,mix=mix,status="started")
                    report["cases"].append(c);persist()
                    y,saved=instrument(newa,A3,s,rate,block)
                    c["restore_error"]=err(y,instrument(newa,A3,s,rate,block,saved)[0])
                    if mix==0: c["legacy_error"]=err(y,instrument(olda,ac.NEW,s,rate,block)[0])
                    else:
                        c["contrast"]=chain.error(y,outputs[0]);h.require(c["contrast"]>1e-4,"missing phase contrast")
                    outputs[mix]=y
                    key=("phase",mix)
                    if block==ac.BLOCKS[0]: reference[key]=y
                    else: c["partition_error"]=err(y,reference[key])
                    c["output"]=h.metrics(y);c["status"]="pass";persist()
                # Persistent endpoint-bin centres ensure receipt draws are audible in the numerical test.
                t=np.arange(rate,dtype=np.int64)
                x=np.stack([np.where(t%64<32,-.0625,.0625),np.where(t%64<32,.0625,-.0625)]).astype(np.float32)
                results={}
                for name,base,s,legacy in effect_states():
                    c=dict(kind="balanced",rate=rate,block=block,mode=name,status="started")
                    report["cases"].append(c);persist()
                    y,saved=effect(newf,F3,base if name=="legacy" else s,s,x,rate,block)
                    c["restore_error"]=err(y,effect(newf,F3,s,s,x,rate,block,saved)[0])
                    if legacy: c["legacy_error"]=err(y,effect(oldf,rf.NEW,base,base,x,rate,block)[0])
                    else:
                        c["contrast"]=chain.error(y,results["legacy"]);h.require(c["contrast"]>1e-4,"missing balanced contrast")
                    if name in ("long","seed"):
                        c["clock_contrast"]=chain.error(y,results["short"]);h.require(c["clock_contrast"]>1e-4,"missing clock/seed contrast")
                    results[name]=y;key=("balanced",name)
                    if block==ac.BLOCKS[0]:reference[key]=y
                    else:c["partition_error"]=err(y,reference[key])
                    c["output"]=h.metrics(y);c["status"]="pass";persist()
        report["complete"]=True
    except Exception as exc:
        report["error"]=repr(exc);raise
    finally: persist()


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("a2","f2","a3","f3","out"):p.add_argument("--"+name,type=Path)
    args=p.parse_args()
    if not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests)).wasSuccessful():raise SystemExit(1)
    if any(vars(args).values()):
        if not all(vars(args).values()):p.error("all five arguments required")
        run(args.a2,args.f2,args.a3,args.f3,args.out)
