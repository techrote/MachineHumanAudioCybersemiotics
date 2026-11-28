"""Independent host implementation smoke and real-module cross-plugin render.
The official SDK validator/probes are separate per-plugin Windows jobs.
"""
import argparse, hashlib, json, math, time, wave
from pathlib import Path
import numpy as np
import pedalboard as pb
from pedalboard import load_plugin
MIDI=[(bytes([0x90,48,84]),0.0),(bytes([0x90,55,72]),0.24),(bytes([0x80,48,0]),0.80),(bytes([0x90,60,76]),0.92),(bytes([0x80,55,0]),1.05),(bytes([0x80,60,0]),1.64)]
def require(x,msg):
    if not x: raise RuntimeError(msg)
def wav(path,arr,rate):
    path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),"wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(np.rint(np.clip(arr.T,-1,1)*32767).astype("<i2").tobytes())
def bounded(x,rate):
    require(x.shape==(2,rate*3) and np.isfinite(x).all(),"invalid stereo frames/nonfinite")
    require(float(np.max(np.abs(x)))<=8.0,"unbounded output")
    return x
def load(root,row):
    bundle=root/"VST3"/row["kind"]/row["bundle"]; inner=bundle/"Contents/x86_64-win"/bundle.name
    require(hashlib.sha256(inner.read_bytes()).hexdigest()==row["binary_sha256"],"host binary identity")
    try: p=load_plugin(str(bundle)); method="bundle"
    except Exception: p=load_plugin(str(inner)); method="inner-module"
    require(bool(p.is_instrument)==(row["kind"]=="Instruments"),"plugin category")
    return p,method
def prepare(p,instrument,rate,block):
    if instrument: p([],sample_rate=rate,duration=0.05,num_channels=2,buffer_size=block,reset=True)
    else: p(np.zeros((2,block),dtype=np.float32),sample_rate=rate,buffer_size=block,reset=True)
def render(p,inst,rate,block,signal):
    t=time.perf_counter()
    if inst: y=p(MIDI,sample_rate=rate,duration=3.0,num_channels=2,buffer_size=block,reset=False)
    else: y=p(signal,sample_rate=rate,buffer_size=block,reset=False)
    return bounded(np.asarray(y),rate),time.perf_counter()-t
def gain(x):
    return x*min(1.0,0.22/max(1e-9,float(np.max(np.abs(x)))))
def main(root):
    catalog=json.loads((root/"Catalogue/catalogue.json").read_text(encoding="utf-8")); rows={x["bundle"][:-5]:x for x in catalog["plugins"]}
    q=root/"Qualification"; report={"status":"running","source":catalog["source"],"host":"Pedalboard "+pb.__version__,"scope":"fresh default-state stereo rendering, restore and block comparison; not full DAW/automation/auxiliary-bus qualification","modules":[],"chains":[]}
    def flush(): (q/"combined-host.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    flush()
    try:
        for rate in (44100,48000,96000):
            t=np.arange(3*rate,dtype=np.float64)/rate
            sig=np.stack([0.12*np.sin(2*np.pi*220*t),0.10*np.sin(2*np.pi*317*t)]).astype(np.float32); sig[:,int(1.5*rate):]=0
            for name,row in rows.items():
                inst=row["kind"]=="Instruments"; outputs=[]
                for block in (127,1024):
                    p,method=load(root,row); prepare(p,inst,rate,block); state=p.preset_data
                    y,elapsed=render(p,inst,rate,block,sig)
                    require(float(np.max(np.abs(y)))>1e-7,"silent default: "+name)
                    new,_=load(root,row); prepare(new,inst,rate,block); new.preset_data=state
                    y2,_=render(new,inst,rate,block,sig)
                    err=float(np.max(np.abs(y-y2))); require(err<=2e-5,"fresh restore mismatch "+name+" "+str(err))
                    report["modules"].append({"bundle":name,"binary_sha256":row["binary_sha256"],"rate":rate,"block":block,"load":method,"restore_max_error":err,"peak":float(np.max(np.abs(y))),"offline_seconds":elapsed})
                    outputs.append(y); flush()
                err=float(np.max(np.abs(outputs[0]-outputs[1])))
                report["modules"][-1]["partition_max_error"]=err; flush()
                require(err<=2e-4,"partition mismatch "+name+" "+str(err))
        rate=48000; block=127
        chains=[
            ("golden-freeze-receipt",["MHACGoldenReceipt"],["MHACFreezeSocket","MHACReceiptFold"]),
            ("orbit-counterfactual",["MHACOrbitLantern"],["MHACCounterfactualResonator"]),
            ("winters-afterimage-memory",["MHACThreeWinters","MHACAfterimage"],["MHACHarmonicMemoryBank"]),
            ("offcut-erasure-xl",["MHACOffcutLoom"],["MHACErasureLoom","MHACErasureLoomXL"]),
            ("guest-clock-shuttle",["MHACGuestOrgan"],["MHACClockFold","MHACPalimpsestShuttle"])]
        for label,instruments,effects in chains:
            folder=root/"Sessions"/"Stems"/label; stems=[]
            for name in instruments:
                p,_=load(root,rows[name]); prepare(p,True,rate,block); y,_=render(p,True,rate,block,None)
                stems.append(gain(y)); wav(folder/(name+".wav"),stems[-1],rate)
            dry=gain(sum(stems)); wav(folder/"dry.wav",dry,rate)
            y=dry
            for name in effects:
                p,_=load(root,rows[name]); prepare(p,False,rate,block); y,_=render(p,False,rate,block,y); y=gain(y)
                wav(folder/(name+".wav"),y,rate)
            require(float(np.max(np.abs(y)))>1e-7,"silent chain "+label)
            report["chains"].append({"name":label,"instruments":instruments,"effects":effects,"frames":len(y[0]),"rate":rate,"input_peak":float(np.max(np.abs(dry))),"output_peak":float(np.max(np.abs(y))),"routing":"serial effects, summed instrument stems, explicit peak cap 0.22 FS; frame aligned, no claim of latency compensation"})
        midi=root/"Sessions"/"MIDI"; midi.mkdir(parents=True,exist_ok=True)
        (midi/"events.json").write_text(json.dumps([{"seconds":t,"bytes":list(b)} for b,t in MIDI],indent=2))
        report["status"]="pass"
    except Exception as exc:
        report["status"]="fail"; report["error"]=str(exc); raise
    finally: flush()
if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("root",type=Path); main(a.parse_args().root)
