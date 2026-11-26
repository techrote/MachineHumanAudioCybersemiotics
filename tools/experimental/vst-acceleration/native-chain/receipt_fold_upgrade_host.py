"""Independent RF01/RF02 migration and RF03 settled-transfer Windows host gate.
Host-independent oracle tests run without a plugin. Actual VST execution needs
both pinned Windows archives and Pedalboard; no listening or automation claim.
"""
import argparse
import json
import math
from pathlib import Path
import struct
import unittest

import numpy as np

NEW = ("MHACReceiptFold", "320e1cdf6594be64177e0702ee6786f250b42b0a",
       "1c0d8c892ac4dad47a3c54ca68f26145ef6f26c37ab1e5baa741674e592f62a6",
       "302FA8177F104E13BFC8A3EF4356888E", "0.2.0")
PAIRS = [(a, b) for a in range(8) for b in range(a+1, 8)]
EPS = 2e-6


def rf03(pair=(2,4), mode=0, bypass=False, bits=3, budget=1,
         a=32, b=192, fine=False, wet=.625):
    if (pair not in PAIRS or mode not in range(4) or bits not in range(3,9)
            or budget not in range(9) or a not in range(256) or b not in range(256)
            or bypass not in (False,True) or fine not in (False,True)
            or not math.isfinite(wet) or not 0 <= wet <= 1):
        raise ValueError("invalid RF03 control")
    word = (PAIRS.index(pair) | mode<<5 | int(bypass)<<7 | (bits-3)<<8
            | budget<<11 | a<<15 | b<<23 | int(fine)<<31)
    return b"RF03" + struct.pack("<Id",word,wet)


def rf02(bits, lo, hi, mode, budget, bypass=False, wet=.625):
    if not (3 <= bits <= 8 and 0 <= lo < hi < (1<<bits) and 0 <= budget <= bits
            and mode in range(4) and bypass in (False,True) and 0 <= wet <= 1):
        raise ValueError("invalid RF02 control")
    return b"RF02"+struct.pack("<8Bd",bits,lo,hi,mode,budget,int(bypass),0,0,wet)


def rf01(mode, bypass=False):
    return b"RF01"+struct.pack("<4Bd",2,4,mode,int(bypass),.625)


def unpack(state):
    if len(state)!=16 or state[:4]!=b"RF03":
        raise ValueError("not RF03")
    w,wet=struct.unpack("<Id",state[4:])
    rank=w&31
    if rank>=len(PAIRS):
        raise ValueError("rank")
    d=dict(pair=PAIRS[rank],mode=(w>>5)&3,bypass=bool(w&128),bits=3+((w>>8)&7),
           budget=(w>>11)&15,a=(w>>15)&255,b=(w>>23)&255,fine=bool(w>>31),wet=wet)
    if rf03(**d)!=state:
        raise ValueError("noncanonical RF03")
    return d


def effective(d):
    bits=d["bits"]
    if d["fine"]:
        lo,hi=sorted((d["a"]>>(8-bits),d["b"]>>(8-bits)))
        if lo==hi:
            if hi+1 < 1<<bits: hi+=1
            else: lo-=1
    else:
        lo,hi=(x<<(bits-3) for x in d["pair"])
    return lo,hi,min(d["budget"],bits)


def oracle(x,state):
    d=unpack(state)
    if d["bypass"] or d["wet"]==0: return x.copy()
    lo,hi,budget=effective(d)
    n=1<<d["bits"]
    q=np.clip(np.floor((x.astype(np.float64)+1)*n/2),0,n-1).astype(np.int32)
    # Recover the upper index only if its retained receipt differs from the lower.
    mask=(0,(1<<budget)-1,(lo^hi)&-(lo^hi),n-1)[d["mode"]]
    if (lo&mask)==(hi&mask): q=np.where(q==hi,lo,q)
    y=x.astype(np.float64)*(1-d["wet"])+((q+.5)/n-.5)*d["wet"]
    return np.where(x==0,0,y).astype(np.float32)


def stimulus(rate):
    # Exactly representable centres of the finest alphabet; no boundary ambiguity.
    v=(np.arange(256,dtype=np.float32)+.5)/128-1
    active=np.tile(np.stack([v,v[::-1]]),(1,8))
    zero=np.zeros((2,rate//50),dtype=np.float32)
    return np.concatenate((zero,active,zero),axis=1)


def cases():
    for m in range(5):
        yield f"legacy-{m}",rf01(m%4,m==4),rf03(mode=m%4,bypass=m==4),True
    for bits in range(3,9):
        for tag,mode,budget,bypass in (("absent",0,1,False),("fixed-low",1,bits-2,False),
                 ("fixed-high",1,bits-1,False),("preview",2,1,False),
                 ("full",3,1,False),("bypass",0,1,True)):
            s=rf03(bits=bits,mode=mode,budget=budget,bypass=bypass,a=96,b=160,fine=True)
            yield f"{bits}-{tag}",s,s,False
        # RF02 migration at the exact same effective fine endpoints.
        lo,hi=96>>(8-bits),160>>(8-bits)
        s=rf03(pair=(lo,hi) if bits==3 else (1,6),bits=bits,mode=1,budget=bits-1,
               a=96,b=160,fine=bits!=3)
        yield f"{bits}-rf02",rf02(bits,lo,hi,1,bits-1),s,False


class OracleTests(unittest.TestCase):
    def test_codec(self):
        self.assertEqual(len(list(cases())),47)
        for _,_,s,_ in cases(): self.assertEqual(rf03(**unpack(s)),s)
        for pair in PAIRS:
            for bits in range(3,9):
                for b in range(9):
                    s=rf03(pair=pair,bits=bits,budget=b,a=255,b=255,fine=True)
                    self.assertEqual(effective(unpack(s)),((1<<bits)-2,(1<<bits)-1,min(b,bits)))
        for kw in ({"bits":9},{"budget":9},{"pair":(4,2)},{"wet":float("nan")},{"a":256}):
            with self.assertRaises(ValueError): rf03(**kw)
        for w in (31,6<<8,15<<11):
            with self.assertRaises(ValueError): unpack(b"RF03"+struct.pack("<Id",w,.625))
    def test_transfer(self):
        x=stimulus(48000)
        for bits in range(3,9):
            def y(mode,budget): return oracle(x,rf03(bits=bits,mode=mode,budget=budget,a=96,b=160,fine=True))
            self.assertTrue(np.array_equal(y(0,1),y(1,bits-2)))
            self.assertTrue(np.array_equal(y(2,1),y(3,1)))
            self.assertTrue(np.array_equal(y(2,1),y(1,bits-1)))
            self.assertGreater(float(np.max(np.abs(y(0,1)-y(2,1)))),.1)
            self.assertTrue(np.array_equal(oracle(x,rf03(bits=bits,bypass=True)),x))
        for _,_,state,_ in cases():
            out=oracle(x,state)
            self.assertTrue(np.isfinite(out).all())
            self.assertLessEqual(float(np.max(np.abs(out))),1.)
            self.assertEqual(float(np.max(np.abs(out[:,:960]))),0.)


def run(old,new,out):
    import afterimage_receipt_host as ar
    import host_audition as h
    out.mkdir(parents=True,exist_ok=True)
    report=dict(scope="RF01/RF02 migration, RF03 transfer and state; Windows Pedalboard",cases=[])
    def persist():
        (out/"receipt-upgrade.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    persist()
    def render(bundle,pin,imported,expected,x,rate,block,saved=None):
        p=h.open_plugin(bundle)
        h.require(p.is_effect,"not effect")
        silent=p(np.zeros((2,rate//20),dtype=np.float32),rate,buffer_size=block)
        h.require(np.isfinite(silent).all() and np.max(np.abs(silent))<1e-7,"prepare silence")
        p.preset_data=ar.preset(pin[3],imported) if saved is None else saved
        h.verify_component(p,pin[3],expected)
        y=h.checked(p(x.copy(),rate,buffer_size=block,reset=False),x.shape[1])
        h.verify_component(p,pin[3],expected)
        return y,p.preset_data
    try:
        ob,report["old_package"]=ar.package(old,out/"old",ar.F)
        nb,report["new_package"]=ar.package(new,out/"new",NEW)
        for rate in ar.RATES:
            x=stimulus(rate); reference={}
            for block in ar.BLOCKS:
                for name,imported,expected,legacy in cases():
                    c=dict(rate=rate,block=block,name=name,status="started")
                    report["cases"].append(c); persist()
                    y,saved=render(nb,NEW,imported,expected,x,rate,block)
                    c["oracle_error"]=ar.error(y,oracle(x,expected))
                    h.require(c["oracle_error"]<EPS,"settled transfer mismatch")
                    restored,_=render(nb,NEW,expected,expected,x,rate,block,saved)
                    c["restore_error"]=ar.error(y,restored)
                    h.require(c["restore_error"]<EPS,"RF03 restore mismatch")
                    if legacy:
                        original,_=render(ob,ar.F,imported,imported,x,rate,block)
                        c["legacy_error"]=ar.error(y,original)
                        h.require(c["legacy_error"]<EPS,"RF01 old/new audio mismatch")
                    if block==ar.BLOCKS[0]: reference[name]=y
                    else:
                        c["partition_error"]=ar.error(y,reference[name])
                        h.require(c["partition_error"]<EPS,"partition mismatch")
                    c["output"]=h.metrics(y); c["status"]="pass"; persist()
        report["complete"]=True
    except Exception as exc:
        report["error"]=repr(exc); raise
    finally: persist()


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--old",type=Path); p.add_argument("--new",type=Path); p.add_argument("--out",type=Path)
    a=p.parse_args()
    if not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OracleTests)).wasSuccessful():
        raise SystemExit(1)
    if any((a.old,a.new,a.out)):
        if not all((a.old,a.new,a.out)): p.error("all three arguments required")
        run(a.old,a.new,a.out)
