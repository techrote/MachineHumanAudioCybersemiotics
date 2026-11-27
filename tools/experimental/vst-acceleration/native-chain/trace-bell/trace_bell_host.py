"""First Trace Bell Windows host smoke; inner module load, not DAW scanning."""
import argparse, json, pathlib, wave
import numpy as np
from pedalboard import load_plugin

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--module", required=True)
    p.add_argument("--out", required=True)
    args=p.parse_args()
    out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for rate in (44100,48000,96000):
        t=np.arange(rate*2,dtype=np.float64)/rate
        envelope=np.where(t<.8,np.exp(-3*t),0.)
        dry=np.stack([.07*np.sin(2*np.pi*220*t)*envelope,
                      .05*np.sin(2*np.pi*330*t)*envelope]).astype(np.float32)
        results=[]
        for size in (127,1024):
            plugin=load_plugin(args.module)
            wet=plugin.process(dry.copy(),rate,buffer_size=size,reset=True)
            assert wet.shape==dry.shape and np.isfinite(wet).all()
            assert np.max(np.abs(wet))<=1 and np.max(np.abs(wet-dry))>1e-4
            results.append(wet)
        error=float(np.max(np.abs(results[0]-results[1])))
        assert error<1e-5, error
        rows.append(dict(rate=rate,partition_max_error=error,peak=float(np.max(np.abs(results[0])))))
        if rate==48000:
            for name,s in (("dry",dry),("wet",results[0])):
                with wave.open(str(out/(name+".wav")),"wb") as w:
                    w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate)
                    w.writeframes(np.rint(np.clip(s.T*.5,-1,1)*32767).astype("<i2").tobytes())
    (out/"host-receipt.json").write_text(json.dumps(rows,indent=2))
if __name__=="__main__":main()
