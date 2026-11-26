"""ACCEL-008: isolated Three Winters 0.2.0 pitch/timbre host witness.
Boundary edits on a continuous MIDI stream; not sample-offset queue injection.
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

SOURCE = "91dc53aca2076665693cbef9f0c61fd913b28745"
DIGEST = "a694d73fa2080685984e43d3fcaa3245744d9ae7fd0e210b3bbef3f0abe1a97d"
CID = "D1195E6E292C442CB550AE834977E4CD"
NAME = "MHACThreeWinters"
EXPECTED = ((0, .25, .25, .25, .5),
            (0, .25, .875, .875, .875),
            (0, .25, .875, .75, .5))
TRANSIENT = (4,5,15,16)

def extract(path, dest):
    raw = path.read_bytes()
    h.require(h.sha(raw)==DIGEST,"Three Winters outer digest")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        h.require(z.testzip() is None and len(z.namelist())==1,"outer CRC")
        inner = z.read(NAME+"-Windows-x64.zip")
    root = NAME+".vst3"
    with zipfile.ZipFile(io.BytesIO(inner)) as z:
        h.require(z.testzip() is None,"inner CRC")
        receipt = z.read("BUILD-SOURCE.txt").decode("utf-8-sig").splitlines()
        h.require("source="+SOURCE in receipt and "sdk="+h.SDK in receipt,"exact source/SDK")
        info = json.loads(re.sub(r",(\s*[}\]])",r"\1",
                    z.read(root+"/Contents/Resources/moduleinfo.json").decode("utf-8-sig")))
        classes = [c for c in info["Classes"] if c["Category"]=="Audio Module Class"]
        h.require(len(classes)==1 and classes[0]["CID"]==CID and
                  classes[0]["Version"]=="0.2.0" and classes[0]["SDKVersion"]=="VST 3.8.0",
                  "module identity")
        seen=set()
        for item in z.infolist():
            p=PurePosixPath(item.filename)
            h.require(not p.is_absolute() and ".." not in p.parts and "\\" not in item.filename
                and ":" not in item.filename and all(x.rstrip(" .")==x for x in p.parts)
                and not stat.S_ISLNK(item.external_attr>>16),"unsafe archive path")
            h.require(str(p).casefold() not in seen,"duplicate archive path")
            seen.add(str(p).casefold())
            if p.parts[0]!=root or item.is_dir(): continue
            target=dest.joinpath(*p.parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(item))
    bundle=(dest/root).resolve(strict=True)
    binary=bundle/"Contents"/"x86_64-win"/root
    return bundle,dict(source=SOURCE,sdk=h.SDK,outer_sha256=DIGEST,
        inner_sha256=h.sha(inner),binary_sha256=h.sha(binary.read_bytes()),processor_cid=CID)

def initial(lane):
    # Fixed unison pitch bank, manual clocks, one monitor lane at a time.
    v=[0.,0.,0.,0.,0.,0.,0.,.25,0.,0.,0.,0.,.25,.75,1.,0.,0.,0.,.25]
    v[8+lane]=1.
    return v

def state(v):
    h.require(len(v)==19 and all(np.isfinite(x) and 0<=x<=1 for x in v),"invalid state")
    return b"TW02"+struct.pack("<19f",*(0 if i in TRANSIENT else x for i,x in enumerate(v)))

def preset(v):
    body=state(v)
    return (bank.HEADER.pack(b"VST3",1,CID.encode("ascii"),bank.HEADER.size+len(body))
        +body+bank.LIST.pack(b"List",1)+bank.ENTRY.pack(b"Comp",bank.HEADER.size,len(body)))

def mixture(x, rate):
    # Last 100ms of settled tone: 44/88 exact cycles at all tested rates.
    t=np.arange(len(x),dtype=np.float64)/rate
    a,b=[abs(2*np.mean(x*np.exp(-2j*np.pi*f*t))) for f in (440,880)]
    h.require(a+b>1e-4,"silent or wrong-pitch harmonic witness")
    residual=x.copy().astype(np.float64)
    for f in (440,880):
        c=2*np.mean(x*np.exp(-2j*np.pi*f*t))
        residual-=np.real(c*np.exp(2j*np.pi*f*t))
    h.require(np.sqrt(np.mean(residual**2))<2e-4,"nonstationary or wrong-pitch tone")
    return float(b/(a+b))

def check_piece(x,rate,lane,expected):
    h.checked(x,rate//5)
    if lane==1:
        h.require(np.max(np.abs(x[0]-x[1]))<2e-6,"pause monitor channels differ")
    else:
        h.require(np.max(np.abs(x[1 if lane==0 else 0]))<2e-6,"inactive lane audible")
    measured=mixture(x[1 if lane==2 else 0,-rate//10:],rate)
    h.require(abs(measured-expected)<.003,
              f"harmonic mixture expected {expected}, measured {measured}")
    return measured

def key_for(p,prefix):
    keys=[k for k in p.parameters if k==prefix or k.startswith(prefix+"_")]
    h.require(len(keys)==1,"missing/ambiguous parameter "+prefix+": "+repr(list(p.parameters)))
    return keys[0]

def perform(bundle,rate,block,lane,saved=None):
    p=h.open_plugin(bundle)
    h.require(p.is_instrument,"not an instrument")
    h.prepare_instrument(p,rate,block)
    v=initial(lane)
    p.preset_data=preset(v) if saved is None else saved
    h.verify_component(p,CID,state(v))
    initial_export=p.preset_data
    pieces=[]
    measured=[]
    def render(events,expected):
        x=h.checked(p(events,duration=.2,sample_rate=rate,num_channels=2,
                       buffer_size=block,reset=False),rate//5)
        pieces.append(x)
        measured.append(check_piece(x,rate,lane,expected))
    def edit(prefix,i,value):
        key=key_for(p,prefix)
        p.parameters[key].raw_value=value
        h.require(abs(p.parameters[key].raw_value-value)<1e-6,"controller readback")
        v[i]=value
    def tick():
        edit("timbre_tick",16,0.)
        # The zero must reach the processor in a separate processing call
        # before another rising edge. First tick starts from preset zero.
        edit("timbre_tick",16,1.)
    render([(bytes((0x90,69,100)),0.)],EXPECTED[lane][0])
    tick()
    render([],EXPECTED[lane][1])
    edit("timbre_hold",15,1.)
    edit("timbre_tick",16,0.)
    edit("timbre_slot_2",12,.875)
    edit("timbre_slot_3",13,.5)
    render([],EXPECTED[lane][2])
    tick()
    render([],EXPECTED[lane][3])
    edit("timbre_hold",15,0.)
    edit("timbre_tick",16,0.)
    render([],EXPECTED[lane][4])
    release=h.checked(p([(bytes((0x80,69,0)),0.)],duration=.2,sample_rate=rate,
                         num_channels=2,buffer_size=block,reset=False),rate//5)
    h.require(np.max(np.abs(release[:,-rate//10:]))<1e-6,"note release failed")
    pieces.append(release)
    h.verify_component(p,CID,state(v))
    return np.concatenate(pieces,axis=1),measured,initial_export

def run(archive,out):
    out.mkdir(parents=True,exist_ok=True)
    report=dict(scope="Three Winters isolated main monitor lanes; continuous MIDI, boundary edits; not sample-offset queues or auxiliary bus qualification",cases=[])
    def persist():
        (out/"winters-receipt.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    persist()
    bundle,report["package"]=extract(archive,out/"plugin")
    persist()
    for rate in (44100,48000,96000):
        for lane in range(3):
            baseline=None
            for block in (257,1024):
                case=dict(rate=rate,lane=lane,block=block,status="started")
                report["cases"].append(case)
                persist()
                try:
                    x,m,saved=perform(bundle,rate,block,lane)
                    y,_,_=perform(bundle,rate,block,lane,saved)
                    case["restore_max_error"]=float(np.max(np.abs(x-y)))
                    h.require(case["restore_max_error"]<2e-5,"host-export restore mismatch")
                    if baseline is None: baseline=x.copy()
                    else:
                        case["block_max_error"]=float(np.max(np.abs(x-baseline)))
                        h.require(case["block_max_error"]<2e-5,"block-dependent signal")
                    case["harmonic_mixture"]=m
                    case["output"]=h.metrics(x)
                    if rate==48000 and block==257:
                        h.wav(out/("winters-lane-"+str(lane)+".wav"),x)
                        (out/("winters-lane-"+str(lane)+".vstpreset")).write_bytes(preset(initial(lane)))
                    case["status"]="pass"
                except Exception as exc:
                    case["status"]="fail"
                    case["error"]=repr(exc)
                    raise
                finally:
                    persist()
                    print("WINTERS HOST:",json.dumps(case),flush=True)
    report["complete"]=True
    persist()

class Tests(unittest.TestCase):
    def test_oracle(self):
        for rate in (44100,48000,96000):
            t=np.arange(rate//5)/rate
            for lane,values in enumerate(EXPECTED):
                for amount in values:
                    tone=.08*((1-amount)*np.sin(2*np.pi*440*t+.23)+amount*np.sin(2*np.pi*880*t+.46))
                    x=np.stack((tone if lane!=2 else tone*0,tone if lane!=0 else tone*0))
                    self.assertAlmostEqual(check_piece(x,rate,lane,amount),amount,places=6)
                    with self.assertRaises(ValueError): check_piece(x,rate,lane,1-amount if amount!=.5 else .25)
                    with self.assertRaises(ValueError): check_piece(x*0,rate,lane,amount)
    def test_state(self):
        for lane in range(3):
            v=initial(lane)
            v[15]=1
            raw=preset(v)
            self.assertEqual(len(state(v)),80)
            self.assertEqual(h.component(raw)["chunks"]["Comp"],state(v).hex())
            self.assertEqual(struct.unpack("<19f",state(v)[4:])[15],0)
            with self.assertRaises(ValueError): state(v[:-1])
            with self.assertRaises(ValueError): state([float("nan")]+v[1:])

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive",type=Path)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    tests=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    h.require(tests.wasSuccessful(),"oracle self-tests")
    if args.archive:
        h.require(args.out is not None,"missing output directory")
        run(args.archive,args.out)
