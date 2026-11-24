"""Deterministic synthetic sonification, not participant evidence (stdlib)."""
import hashlib, json, math, struct, wave
from pathlib import Path

RATE = 16000
STRIDE = 240
A = 0.875
D = 8
N = RATE * 4


def allpass(x, a=A, stride=STRIDE):
    y = [0.0] * len(x)
    for t, v in enumerate(x):
        y[t] = -a * v + (x[t-stride] + a*y[t-stride] if t >= stride else 0)
    return y


def equalize(y, a=A, d=D, stride=STRIDE):
    # G(w)=(1-aw) sum_{i=0}^{d-1} a^(d-1-i) w^i
    if d == 0:
        return [0.0]*len(y)
    q = [sum(a**(d-1-i)*y[t-i*stride] for i in range(d) if t >= i*stride)
         for t in range(len(y))]
    return [v-(a*q[t-stride] if t >= stride else 0) for t,v in enumerate(q)]


def make(out):
    out.mkdir(parents=True, exist_ok=True)
    x = [0.0]*N
    for start, f in [(1600, 187), (11300, 293), (21000, 431), (32000, 239)]:
        for j in range(900):
            u=j/900
            x[start+j] = .36*math.sin(math.pi*u)**2*math.sin(2*math.pi*f*j/RATE)
    y=allpass(x)
    target=[0.0]*(D*STRIDE)+x[:N-D*STRIDE]
    rec=equalize(y)
    residual=[v-r for v,r in zip(target,rec)]
    max_error=max(abs(e-A**D*v) for e,v in zip(residual,x))
    assert max_error < 1e-12
    # Finite rendering truncates the IIR tail. Report actual energy ratio.
    ratio=sum(v*v for v in y)/sum(v*v for v in x)
    assert abs(ratio-1)<1e-10
    manifest={"sample_rate":RATE,"stride_samples":STRIDE,"delay_steps":D,
              "a":A,"frames":N,"max_residual_identity_error":max_error,
              "finite_window_energy_ratio":ratio,"theoretical_error_gain":A**D,"files":{}}
    for name,l,r in [("same-magnitude.wav",x,y),("preview-recovery.wav",target,rec),("recovery-residual.wav",x,residual)]:
        peak=max(max(map(abs,l)),max(map(abs,r)))
        assert peak < 1
        p=out/name
        with wave.open(str(p),'wb') as w:
            w.setparams((2,2,RATE,0,'NONE','not compressed'))
            w.writeframes(b''.join(struct.pack('<hh',round(u*32767),round(v*32767)) for u,v in zip(l,r)))
        manifest['files'][name]={"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"peak":peak}
    (out/'audio-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

if __name__=='__main__':
    import sys
    print(json.dumps(make(Path(sys.argv[1]) if len(sys.argv)>1 else Path('run')),indent=2))
