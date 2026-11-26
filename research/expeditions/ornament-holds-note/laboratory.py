"""Original steady-state resonator score, not a real-time physical solver."""
import argparse
import cmath
import hashlib
import io
import json
import math
import struct
import wave
from pathlib import Path

RATE = 16000
GAMMA = 0.25
TUNED = ((0.25, 1.0, 0.0), (0.25, 1.5, 0.0))
DETUNED = ((0.25, 1.1, 0.0), (0.25, 1.6, 0.0))
DAMPED = tuple((m, f, 0.05) for m, f, _ in TUNED)
SCORE = (160, 200, 240, 300, 340)

def terms(r, branches):
    if r <= 0 or any(m <= 0 or f <= 0 or c < 0 for m, f, c in branches):
        raise ValueError("invalid model")
    d = 1-r*r+1j*GAMMA*r
    k = [m*f*f+1j*c*r for m, f, c in branches]
    a = [v-m*r*r for v, (m, _, _) in zip(k, branches)]
    return d, k, a

def response(r, branches):
    d, k, a = terms(r, branches)
    zeros = [i for i, v in enumerate(a) if v == 0]
    if len(zeros) > 1:
        raise ValueError("coincident undamped branch singularity")
    if zeros:
        y = [0j]*len(a)
        y[zeros[0]] = -1/k[zeros[0]]
        return [0j]+y
    x = 1/(d+sum(v-v*v/w for v, w in zip(k, a)))
    return [x]+[v*x/w for v, w in zip(k, a)]

def direct(r, branches):
    d, k, a = terms(r, branches)
    n = 1+len(k)
    rows = [[0j]*(n+1) for _ in range(n)]
    rows[0][0] = d+sum(k)
    rows[0][-1] = 1
    for i, (v, w) in enumerate(zip(k, a), 1):
        rows[0][i] = rows[i][0] = -v
        rows[i][i] = w
    for j in range(n):
        pivot = max(range(j,n),key=lambda i: abs(rows[i][j]))
        rows[j],rows[pivot] = rows[pivot],rows[j]
        v = rows[j][j]
        if abs(v) < 1e-14:
            raise ValueError("singular")
        rows[j] = [q/v for q in rows[j]]
        for i in range(n):
            if i != j:
                v = rows[i][j]
                rows[i] = [u-v*w for u,w in zip(rows[i],rows[j])]
    return [row[-1] for row in rows]

def qualify():
    cases = 0
    maxerr = 0.0
    for branches in ((), TUNED, DETUNED, DAMPED, TUNED[:1]):
        for i in range(50, 251):
            r = i/100
            x, y = response(r,branches),direct(r,branches)
            err = max(abs(u-v) for u,v in zip(x,y))
            assert err < 1e-9
            maxerr = max(maxerr,err)
            cases += 1
    for i, r in enumerate((1.0,1.5)):
        x = response(r,TUNED)
        assert x[0] == 0 and x[i+1] != 0 and x[2-i] == 0
        assert abs(response(r,())[0]) > 0
        assert abs(response(r,DAMPED)[0]) > 0
        assert abs(response(r,DETUNED)[0]) > 0
    for bad in (0, -1):
        try:
            response(bad,TUNED)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid frequency accepted")
    try:
        response(1.0,(TUNED[0],TUNED[0]))
    except ValueError:
        pass
    else:
        raise AssertionError("singular duplicate accepted")
    return dict(grid_cases=cases,max_complex_error=maxerr,
                exact_zero_targets=2,negative_controls=3)

def render():
    # Shared gain across every recording; no per-file normalization.
    scenes = {"bare": (), "coupled": TUNED, "detuned": DETUNED,
              "lossy": DAMPED}
    ph = {name:[response(f/200,branches) for f in SCORE]
          for name,branches in scenes.items()}
    scale = 0.65/max(abs(v) for seq in ph.values() for z in seq
                     for v in (z[0],sum(z[1:])))
    n = RATE//2
    def wav(name, diagnostic=False):
        buf = io.BytesIO()
        with wave.open(buf,"wb") as w:
            w.setnchannels(2 if diagnostic else 1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            data = bytearray()
            for f,z in zip(SCORE,ph[name]):
                for i in range(n):
                    env = min(1,i/320,(n-1-i)/320)
                    osc = cmath.exp(2j*math.pi*f*i/RATE)
                    vals = [z[0],sum(z[1:])] if diagnostic else [z[0]]
                    for v in vals:
                        a = round(32767*scale*env*(v*osc).real)
                        assert abs(a) <= 32767
                        data.extend(struct.pack("<h",a))
            w.writeframes(data)
        return buf.getvalue()
    files = {name+".wav":wav(name) for name in scenes}
    files["witness.wav"] = wav("coupled",True)
    return files,scale

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,default=Path("audio"))
    args=p.parse_args()
    result=qualify()
    files,scale=render()
    assert files == render()[0]
    args.out.mkdir(parents=True,exist_ok=True)
    result["common_gain"]=scale
    result["wav"]={}
    for name,data in files.items():
        with wave.open(io.BytesIO(data),"rb") as w:
            assert (w.getframerate(),w.getsampwidth(),w.getnframes()) == (RATE,2,40000)
            ch=w.getnchannels()
            assert ch == (2 if name=="witness.wav" else 1)
            pcm=list(struct.unpack("<"+"h"*(40000*ch),w.readframes(40000)))
        if name=="coupled.wav":
            for slot in (1,3):
                assert not any(pcm[slot*8000:(slot+1)*8000])
        if name=="witness.wav":
            for slot in (1,3):
                segment=pcm[slot*16000:(slot+1)*16000]
                assert not any(segment[::2]) and any(segment[1::2])
        (args.out/name).write_bytes(data)
        result["wav"][name]=dict(sha256=hashlib.sha256(data).hexdigest(),
                                 peak=max(map(abs,pcm)),frames=40000,channels=ch)
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
