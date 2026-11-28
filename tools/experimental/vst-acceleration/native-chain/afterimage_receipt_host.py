"""ACCEL-016: exact Windows Afterimage -> Receipt Fold host chain.
Separate preset import, host load, audio, restore and block-size gates.
No listener, DAW GUI, SDK validator rerun or sample-offset automation claim.
"""
import argparse
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import unittest
import zipfile

import numpy as np
import host_audition as h
import preset_bank as bank

A = ("MHACAfterimage", "ab8d5005a3c1c1aac8e2e30ccf4b609f0a3688c3",
     "406f23908d5581b18eb7cb9b8314c82ffd88d8419aed28fda8fe37226f602886",
     "BD0B8CB3B82E43EB9613F0C9A37FBA83", "0.1.1")
F = ("MHACReceiptFold", "c1b8586258946de0669b3f6eec9b79ec05ce2b91",
     "df93330ddc26f799b993677e56a83175172906e3ec417a5e09ebf19f9c0b534d",
     "302FA8177F104E13BFC8A3EF4356888E", "0.1.0")
RATES = (44100, 48000, 96000)
BLOCKS = (257, 1024)
# Exact score of the native chain, using MIDI velocity 102/127.
EVENTS = [(bytes((0x90 if on else 0x80, note, 102 if on else 0)), t/10)
          for t, on, note in ((1,1,62),(8,0,62),(10,1,60),(17,0,60),
                              (19,1,60),(19,1,64),(19,1,67),
                              (26,0,60),(26,0,64),(26,0,67))]
EPS = 2e-5

def package(path, dest, pin):
    name, source, digest, cid, version = pin
    raw = path.read_bytes()
    h.require(h.sha(raw)==digest, "outer artifact hash")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        innername = name+"-Windows-x64.zip"
        h.require(z.testzip() is None and z.namelist()==[innername], "outer ZIP")
        inner = z.read(innername)
    root = name+".vst3"
    with zipfile.ZipFile(io.BytesIO(inner)) as z:
        h.require(z.testzip() is None, "inner CRC")
        receipt = z.read("BUILD-SOURCE.txt").decode("utf-8-sig").splitlines()
        h.require("source="+source in receipt and "sdk="+h.SDK in receipt, "source/SDK")
        v = z.read("validator.txt").decode("utf-8-sig")
        h.require("Result: 47 tests passed, 0 tests failed" in v and
                  not re.search(r"^\s*ERROR\b", v, re.M|re.I), "archived validator")
        info = json.loads(re.sub(r",(\s*[}\]])",r"\1",
                         z.read(root+"/Contents/Resources/moduleinfo.json").decode("utf-8-sig")))
        processors = [c for c in info["Classes"] if c["Category"]=="Audio Module Class"]
        h.require(len(processors)==1 and processors[0]["CID"]==cid and
                  processors[0]["Version"]==version and processors[0]["SDKVersion"]=="VST 3.8.0",
                  "processor identity")
        seen = set()
        for item in z.infolist():
            p = PurePosixPath(item.filename)
            h.require(not p.is_absolute() and ".." not in p.parts and "\\" not in item.filename
                and ":" not in item.filename and all(x.rstrip(" .")==x for x in p.parts)
                and not stat.S_ISLNK(item.external_attr>>16), "archive path")
            h.require(str(p).casefold() not in seen, "duplicate archive path")
            seen.add(str(p).casefold())
            if p.parts[0]!=root or item.is_dir():
                continue
            target = dest.joinpath(*p.parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(item))
    bundle = (dest/root).resolve(strict=True)
    binary = (bundle/"Contents"/"x86_64-win"/root).read_bytes()
    off = struct.unpack_from("<I",binary,60)[0]
    h.require(binary[:2]==b"MZ" and binary[off:off+6]==b"PE\0\0\x64\x86", "PE AMD64")
    return bundle, dict(source=source, sdk=h.SDK, outer_sha256=digest,
                        inner_sha256=h.sha(inner), binary_sha256=h.sha(binary), cid=cid)

def ac_state(mode):
    h.require(mode in (1,2), "AC receipt")
    return b"AC01"+struct.pack("<I",16|(mode<<5)|(80<<7)|(800<<18))

def rf_state(mode):
    h.require(mode in range(5), "RF receipt")
    # Pair 2/4; .625 is exactly representable in binary32 and binary64.
    return b"RF01"+struct.pack("<BBBBd",2,4,mode%4,int(mode==4),.625)

def preset(cid, state):
    return (bank.HEADER.pack(b"VST3",1,cid.encode("ascii"),bank.HEADER.size+len(state))
        +state+bank.LIST.pack(b"List",1)+bank.ENTRY.pack(b"Comp",bank.HEADER.size,len(state)))

def prepare(bundle, pin, state, rate, block, instrument, saved=None):
    p = h.open_plugin(bundle)
    h.require(p.is_instrument if instrument else p.is_effect, "category")
    if instrument:
        h.prepare_instrument(p,rate,block)
    else:
        h.require(np.max(np.abs(p(np.zeros((2,rate//20),dtype=np.float32),rate,
                                 buffer_size=block)))<1e-7,"effect preparation not silent")
    p.preset_data = preset(pin[3],state) if saved is None else saved
    h.verify_component(p,pin[3],state)
    return p

def dry_render(p, rate, block, state):
    x = h.checked(p(EVENTS,duration=3.,sample_rate=rate,num_channels=2,
                    buffer_size=block,reset=False),3*rate)
    h.verify_component(p,A[3],state)
    signal_gate(x,rate)
    return x

def wet_render(p, x, rate, block, state):
    y = h.checked(p(x.copy(),rate,buffer_size=block,reset=False),3*rate)
    h.verify_component(p,F[3],state)
    signal_gate(y,rate)
    return y

def signal_gate(x,rate):
    h.checked(x,3*rate)
    h.require(np.max(np.abs(x[0]-x[1]))<EPS,"stereo coherence")
    h.require(np.max(np.abs(x[:,:rate//20]))<EPS,"pre-note silence")
    h.require(np.max(np.abs(x[:,-rate//10:]))<EPS,"release silence")
    h.require(h.metrics(x)["rms"]>1e-5,"silent performance")

def error(x,y):
    return float(np.max(np.abs(x-y)))

def equivalence(outputs,dry):
    h.require(len(outputs)==5,"missing receipt outputs")
    report = dict(absent_fixed=error(outputs[0],outputs[1]),
                  preview_full=error(outputs[2],outputs[3]),
                  bypass=error(outputs[4],dry),
                  recovery_contrast=error(outputs[0],outputs[2]),
                  processing_contrast=error(outputs[2],dry))
    h.require(max(report[k] for k in ("absent_fixed","preview_full","bypass"))<EPS,
              "receipt equivalence or bypass")
    h.require(min(report[k] for k in ("recovery_contrast","processing_contrast"))>1e-4,
              "missing receipt/effect contrast")
    return report

def run(a, f, out):
    out.mkdir(parents=True,exist_ok=True)
    report = dict(scope="Windows Pedalboard chain, component-only preset import, continuous render",
                  instruments=[], effects=[], comparisons=[])
    def persist():
        (out/"afterimage-receipt-host.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    persist()
    try:
        ab, report["instrument_package"] = package(a,out/"instrument",A)
        fb, report["effect_package"] = package(f,out/"effect",F)
        for rate in RATES:
            reference = {}
            for block in BLOCKS:
                memories = []
                for memory in (1,2):
                    state = ac_state(memory)
                    c = dict(rate=rate,block=block,memory=memory,status="started")
                    report["instruments"].append(c); persist()
                    p = prepare(ab,A,state,rate,block,True)
                    dry = dry_render(p,rate,block,state)
                    saved = p.preset_data
                    fresh = prepare(ab,A,state,rate,block,True,saved)
                    c["restore_error"] = error(dry,dry_render(fresh,rate,block,state))
                    c["output"] = h.metrics(dry)
                    h.require(c["restore_error"]<EPS,"instrument restore")
                    key=(memory,-1)
                    if block==BLOCKS[0]: reference[key]=dry
                    else:
                        c["partition_error"]=error(reference[key],dry)
                        h.require(c["partition_error"]<EPS,"instrument partition")
                    c["status"]="pass";persist()
                    memories.append(dry)
                    outputs=[]
                    for mode in range(5):
                        state=rf_state(mode)
                        c=dict(rate=rate,block=block,memory=memory,mode=mode,status="started")
                        report["effects"].append(c);persist()
                        p=prepare(fb,F,state,rate,block,False)
                        wet=wet_render(p,dry,rate,block,state)
                        fresh=prepare(fb,F,state,rate,block,False,p.preset_data)
                        c["restore_error"]=error(wet,wet_render(fresh,dry,rate,block,state))
                        c["output"]=h.metrics(wet)
                        c["active_mean"]=float(np.mean(wet[:,rate//10:rate*27//10],dtype=np.float64))
                        h.require(c["restore_error"]<EPS,"effect restore")
                        key=(memory,mode)
                        if block==BLOCKS[0]: reference[key]=wet
                        else:
                            c["partition_error"]=error(reference[key],wet)
                            h.require(c["partition_error"]<EPS,"effect partition")
                        c["status"]="pass";outputs.append(wet);persist()
                    report["comparisons"].append(dict(rate=rate,block=block,memory=memory,
                                                     **equivalence(outputs,dry)))
                    persist()
                # Prior note should match before its first release; subsequent notes diverge.
                h.require(error(memories[0][:,:rate*8//10],memories[1][:,:rate*8//10])<EPS,
                          "unexpected pre-history difference")
                h.require(error(memories[0][:,rate:rate*17//10],memories[1][:,rate:rate*17//10])>1e-4,
                          "missing history contrast")
        report["complete"]=True
    except Exception as exc:
        report["error"]=repr(exc)
        raise
    finally:
        persist()

class OracleTests(unittest.TestCase):
    def test_states(self):
        for pin,states in ((A,[ac_state(i) for i in (1,2)]),
                           (F,[rf_state(i) for i in range(5)])):
            for state in states:
                self.assertEqual(h.component(preset(pin[3],state)),
                                 dict(class_id=pin[3],chunks={"Comp":state.hex()}))
        self.assertEqual(struct.unpack("<I",ac_state(1)[4:])[0]&31,16)
        self.assertEqual(struct.unpack("<BBBBd",rf_state(4)[4:]),(2,4,0,1,.625))
        with self.assertRaises(ValueError): ac_state(0)
        with self.assertRaises(ValueError): rf_state(5)
    def test_oracle(self):
        for rate in RATES:
            d=np.zeros((2,3*rate),dtype=np.float32)
            d[:,rate//10:2*rate]=.05
            signal_gate(d,rate)
            expected=[d*.5,d*.5,d*.75,d*.75,d]
            equivalence(expected,d)
            for bad in (np.zeros_like(d),d*np.nan,np.ones_like(d)):
                with self.assertRaises(ValueError): signal_gate(bad,rate)
            for i in range(5):
                wrong=expected.copy();wrong[i]=d*.9
                with self.assertRaises(ValueError): equivalence(wrong,d)

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instrument",type=Path)
    parser.add_argument("--effect",type=Path)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    h.require(unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(OracleTests)).wasSuccessful(),"oracle tests")
    if any((args.instrument,args.effect,args.out)):
        h.require(all((args.instrument,args.effect,args.out)),"all three arguments required")
        run(args.instrument,args.effect,args.out)
