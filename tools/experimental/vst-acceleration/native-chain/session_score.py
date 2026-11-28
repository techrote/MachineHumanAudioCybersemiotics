"""ACCEL-026: original four-track score and portable three-plugin session.
Self-tests are host-independent. --afterimage/--winters/--receipt runs real VST3 hosting.
"""
import argparse
import json
from pathlib import Path
import struct
import tempfile
import unittest
import wave

import numpy as np

RATE, PPQ, TEMPO, SECONDS = 48000, 480, 500000, 12
FRAMES = RATE * SECONDS
BLOCKS = (257, 1024)
NAMES = ("Afterimage", "Winter-Latch", "Winter-Pause", "Winter-Snapshot")
GAINS = (.5, .125, .125, .125)
# Start, duration (in eighth notes), pitch, velocity. Each track is monophonic.
SCORE = (
    ((1,1,57,84),(3,1,60,90),(5,1,64,96),(7,3,48,104),
     (12,1,55,86),(14,1,59,92),(16,1,62,97),(18,3,50,103),
     (24,1,53,85),(26,1,57,92),(28,1,65,98),(30,5,48,105),
     (37,1,60,91),(39,1,64,96),(41,4,48,98)),
    ((2,5,48,93),(9,5,50,89),(16,5,53,95),(23,5,48,90),
     (30,5,55,92),(38,6,48,86)),
    ((4,3,60,87),(10,3,62,90),(14,3,65,88),(20,3,64,94),
     (26,3,62,87),(32,3,65,92),(40,4,60,82)),
    ((6,2,67,82),(11,2,69,86),(18,2,72,90),(25,2,67,84),
     (29,2,69,88),(34,2,76,91),(39,2,72,87),(43,2,67,80)),
)


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def midi_events(notes):
    end = 0
    events = []
    for start, duration, pitch, velocity in notes:
        require(start >= end and start >= 1 and duration > 0, "note overlap or extent")
        require(0 <= pitch <= 127 and 1 <= velocity <= 127, "MIDI range")
        end = start + duration
        require(end <= 45, "insufficient release tail")
        events.extend(((start * PPQ//2, bytes((0x90,pitch,velocity))),
                       (end * PPQ//2, bytes((0x80,pitch,0)))))
    return events


def vlq(value):
    require(0 <= value < 0x10000000, "MIDI delta range")
    result = [value & 127]
    while value > 127:
        value >>= 7
        result.append((value & 127) | 128)
    return bytes(reversed(result))


def midi_file(notes, name):
    label = name.encode("ascii")
    data = b"\0\xff\x03" + vlq(len(label)) + label
    data += b"\0\xff\x51\x03" + TEMPO.to_bytes(3,"big")
    last = 0
    for tick, msg in midi_events(notes):
        data += vlq(tick-last) + msg
        last = tick
    data += vlq(SECONDS*2*PPQ-last) + b"\xff\x2f\0"
    return b"MThd"+struct.pack(">IHHH",6,0,1,PPQ)+b"MTrk"+struct.pack(">I",len(data))+data


def host_events(notes):
    return [(msg, tick*TEMPO/(PPQ*1e6)) for tick,msg in midi_events(notes)]


def checked(x, peak=1.):
    require(x.shape == (2,FRAMES) and np.isfinite(x).all(), "shape/finite")
    require(.0001 < np.max(np.abs(x)) <= peak, "silence/overload")
    require(np.max(np.abs(x[:, :RATE//10])) < 2e-6, "leading silence")
    require(np.max(np.abs(x[:, -RATE//4:])) < 2e-6, "release tail")
    return x


def mix(stems):
    require(len(stems)==4,"four stems required")
    weighted = [checked(x)*np.float32(g) for x,g in zip(stems,GAINS)]
    dry = np.zeros_like(weighted[0])
    for x in weighted:
        dry += x
    return weighted, checked(dry)


def pcm(x):
    checked(x,.25)
    return np.rint(x.T*32767).astype("<i2")


def write_wav(path,x):
    data=pcm(x)
    with wave.open(str(path),"wb") as w:
        w.setparams((2,2,RATE,0,"NONE","not compressed"))
        w.writeframes(data.tobytes())
    with wave.open(str(path),"rb") as w:
        require((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (2,2,RATE,FRAMES),"WAV header")
        require(w.readframes(FRAMES)==data.tobytes(),"WAV round trip")
    return data.astype(np.int32)


def compare(a,b):
    checked(a);checked(b)
    error=float(np.max(np.abs(a-b)))
    require(error<2e-6,"partition/restore error: "+str(error))
    return error


def export_score(out):
    out.mkdir(parents=True,exist_ok=True)
    for name,notes in zip(NAMES,SCORE):
        (out/(name+".mid")).write_bytes(midi_file(notes,name))


class Tests(unittest.TestCase):
    def test_score(self):
        for name,notes in zip(NAMES,SCORE):
            raw=midi_file(notes,name)
            self.assertEqual(struct.unpack(">IHHH",raw[4:14]),(6,0,1,PPQ))
            self.assertEqual(struct.unpack(">I",raw[18:22])[0],len(raw)-22)
            self.assertEqual(len(host_events(notes)),2*len(notes))
            self.assertEqual(raw,midi_file(notes,name))
        for bad in (((1,2,128,90),),((1,2,60,0),),((1,4,60,90),(3,1,61,90)),((44,2,60,90),)):
            with self.assertRaises(ValueError): midi_events(bad)

    def test_mix(self):
        stems=[]
        for i in range(4):
            x=np.zeros((2,FRAMES),np.float32)
            x[:,RATE:2*RATE]=(.01+i*.02)
            stems.append(x)
        weighted,dry=mix(stems)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"dry.wav"
            got=write_wav(path,dry)
            error=int(np.max(np.abs(sum(pcm(x).astype(np.int32) for x in weighted)-got)))
            self.assertLessEqual(error,3)
        self.assertEqual(compare(dry,dry.copy()),0.)
        for bad in (dry*0,dry*np.nan,dry*100,dry[:,:-1],dry+.01):
            with self.assertRaises(ValueError): checked(bad)
        with self.assertRaises(ValueError): compare(dry,dry*2)


def render(afterimage,winters,receipt,out):
    import afterimage_receipt_host as chain
    import phase_balanced_host as pb
    import receipt_fold_upgrade_host as rf
    import rotation_host as rotation
    import winters_host as winter
    import host_audition as h
    export_score(out/"MIDI")
    for name in ("Presets","Stems","Comparisons"):
        (out/name).mkdir(exist_ok=True)
    report={"scope":__doc__,"rate":RATE,"seconds":SECONDS,"gains":GAINS,"cases":[]}
    def persist():
        (out/"session.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    try:
        ab,report["afterimage"]=chain.package(afterimage,out/"afterimage",rotation.A31)
        wb,report["winters"]=winter.extract(winters,out/"winters")
        fb,report["receipt"]=chain.package(receipt,out/"receipt",pb.F3)
        require(report["afterimage"]["binary_sha256"]=="87774d7877810de06d0abb7ecdaff9bd290829c86ebc0cf8639fc5bef62dc089","Afterimage pin")
        require(report["receipt"]["binary_sha256"]=="c13a44cfd6bf0a6979b362a8dd057bd7c309e95a467a8f2558c340404b320776","Receipt pin")
        states=[pb.phase(3,3)]
        for lane in range(3):
            v=winter.initial(lane)
            v[11:15]=[0.,.25,.75,1.]
            v[17]=1.;v[18]=(.25,.5,.75)[lane]
            states.append(winter.state(v))
        winter_pin=(winter.NAME,winter.SOURCE,winter.DIGEST,winter.CID,"0.2.1")
        pins=[rotation.A31]+[winter_pin]*3
        base=rf.rf03(bits=4,budget=0,a=112,b=128,fine=True,mode=1,wet=.625)
        effects={"Legacy":pb.balanced(base),"Balanced":pb.balanced(base,True,25,7),
                 "Bypass":pb.balanced(rf.rf03(bits=4,bypass=True,wet=.625),True,25,7)}
        reference={}
        for block in BLOCKS:
            stems=[]
            for name,notes,state,pin,bundle in zip(NAMES,SCORE,states,pins,[ab,wb,wb,wb]):
                p=chain.prepare(bundle,pin,state,RATE,block,True)
                saved=p.preset_data
                def take(p):
                    x=checked(p(host_events(notes),duration=SECONDS,sample_rate=RATE,num_channels=2,buffer_size=block,reset=False))
                    h.verify_component(p,pin[3],state)
                    return x
                x=take(p)
                c=dict(name=name,block=block,output=h.metrics(x),restore_error=compare(x,take(chain.prepare(bundle,pin,state,RATE,block,True,saved))))
                if name in reference:c["partition_error"]=compare(x,reference[name])
                else:reference[name]=x.copy()
                report["cases"].append(c);persist();stems.append(x)
                if block==BLOCKS[0]: (out/"Presets"/(name+".vstpreset")).write_bytes(chain.preset(pin[3],state))
            weighted,dry=mix(stems)
            outputs={}
            for name,state in effects.items():
                p=chain.prepare(fb,pb.F3,state,RATE,block,False)
                saved=p.preset_data
                def take(p):
                    x=checked(p(dry.copy(),RATE,buffer_size=block,reset=False))
                    h.verify_component(p,pb.F3[3],state)
                    return x
                y=take(p)
                c=dict(name=name,block=block,output=h.metrics(y),restore_error=compare(y,take(chain.prepare(fb,pb.F3,state,RATE,block,False,saved))))
                if name=="Legacy":c["oracle_error"]=compare(y,rf.oracle(dry,base))
                if name=="Bypass":c["bypass_error"]=compare(y,dry)
                if name=="Balanced":
                    c["contrast"]=float(np.max(np.abs(y-outputs["Legacy"])))
                    require(c["contrast"]>1e-4,"missing balanced contrast")
                if name in reference:c["partition_error"]=compare(y,reference[name])
                else:reference[name]=y.copy()
                report["cases"].append(c);persist();outputs[name]=y
                if block==BLOCKS[0]: (out/"Presets"/(name+".vstpreset")).write_bytes(chain.preset(pb.F3[3],state))
            if block==BLOCKS[0]:
                parts=[write_wav(out/"Stems"/(name+".wav"),x) for name,x in zip(NAMES,weighted)]
                target=write_wav(out/"Comparisons"/"Dry.wav",dry)
                report["stem_sum_lsb_error"]=int(np.max(np.abs(sum(parts)-target)))
                require(report["stem_sum_lsb_error"]<=3,"stem sum quantization")
                for name in ("Legacy","Balanced"):
                    write_wav(out/"Comparisons"/(name+".wav"),outputs[name])
        report["complete"]=True
    except Exception as exc:
        report["error"]=repr(exc);raise
    finally:persist()


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for n in ("afterimage","winters","receipt","out","score-only"):
        p.add_argument("--"+n,type=Path)
    a=p.parse_args()
    require(unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests)).wasSuccessful(),"self-tests")
    if a.score_only: export_score(a.score_only)
    if any((a.afterimage,a.winters,a.receipt,a.out)):
        require(all((a.afterimage,a.winters,a.receipt,a.out)),"all four host arguments required")
        render(a.afterimage,a.winters,a.receipt,a.out)
