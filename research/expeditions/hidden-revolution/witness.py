"""Independent matrix-exponential check and coupled synthetic acoustic traces."""
import hashlib
import json
import math
import random
import struct
import wave
from pathlib import Path
import numpy as np
import scipy
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parent
D = 4 * math.pi / math.sqrt(3)

def generator(s, d):
    a, b = (s+d)/2, (s-d)/2
    return np.array([[-s,a,b],[b,-s,a],[a,b,-s]])

def row_formula(s,d,t):
    return np.array([(1+2*math.exp(-1.5*s*t)*math.cos(math.sqrt(3)*d*t/2-2*math.pi*j/3))/3 for j in range(3)])

def bridge(rng, start, end, s, d):
    """Rejection sampling of a unit-duration CTMC path given its endpoint."""
    for tries in range(1,10001):
        x, t, events = start, 0., [(0.,start)]
        while True:
            t += rng.expovariate(s)
            if t>=1: break
            x = (x+(1 if rng.random()<(s+d)/(2*s) else -1))%3
            events.append((t,x))
        if x==end: return events, tries
    raise RuntimeError('bridge acceptance budget exhausted')

def at(events,t):
    return next(x for stamp,x in reversed(events) if stamp<=t)

def render(name, states):
    sr, N = 8000, 320
    templates = [[round(7000*math.sin(2*math.pi*f*j/sr)*math.sin(math.pi*j/N)**2) for j in range(N)] for f in (300,500,700)]
    path=ROOT/name
    with wave.open(str(path),'wb') as w:
        w.setparams((1,2,sr,0,'NONE','not compressed'))
        w.writeframes(struct.pack('<'+'h'*(N*len(states)),*(v for x in states for v in templates[x])))
    with wave.open(str(path),'rb') as w:
        data=struct.unpack('<'+'h'*(N*len(states)),w.readframes(N*len(states)))
    decoded=[max(range(3),key=lambda x:sum(a*b for a,b in zip(data[i:i+N],templates[x]))) for i in range(0,len(data),N)]
    assert decoded==states
    return {'frames':len(states),'decoded':len(decoded),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    checks=0; maxerr=0.
    for m in range(1,13):
        s=m*D/2+.1
        matrices=[generator(s,-m*D/2+j*D) for j in range(m+1)]
        ref=expm(matrices[0]); c=1.5*s; tstar=math.atan(math.pi/c)/math.pi
        mode=[]
        for j,Q in enumerate(matrices):
            d=-m*D/2+j*D
            for t in (0.,.01,.09,.37,1.,2.):
                P=expm(t*Q); err=float(np.max(np.abs(P[0]-row_formula(s,d,t))))
                maxerr=max(maxerr,err); assert err<1e-12; checks+=1
            assert np.max(np.abs(expm(Q)-ref))<1e-12; checks+=1
            p=expm(tstar*Q)[0]
            mode.append(sum(p[k]*np.exp(2j*np.pi*k/3) for k in range(3)))
        measured=min(abs(x-y) for i,x in enumerate(mode) for y in mode[i+1:])
        assert abs(measured-2*math.exp(-c*tstar)*math.sin(math.pi*tstar))<1e-12; checks+=1
    s=D+.1; rng=random.Random(670); skeleton=[rng.randrange(3)]
    p=row_formula(s,0,1)
    for _ in range(24):
        skeleton.append((skeleton[-1]+rng.choices(range(3),weights=p,k=1)[0])%3)
    audio={}; detail=[]; trials=[]; jumps=[]
    for name,d in [('reversible',0.),('circulating',D)]:
        frames=[]; attempts=0; num_jumps=0
        for start,end in zip(skeleton,skeleton[1:]):
            events, n=bridge(rng,start,end,s,d); attempts+=n; num_jumps+=len(events)-1
            assert at(events,1)==end
            frames.extend(at(events,k/10) for k in range(10))
        frames.append(skeleton[-1]); assert frames[::10]==skeleton
        detail.append(frames); trials.append(attempts); jumps.append(num_jumps)
        audio[name+'-coarse.wav']=render(name+'-coarse.wav',skeleton)
        audio[name+'-detail.wav']=render(name+'-detail.wav',frames)
    assert audio['reversible-coarse.wav']['sha256']==audio['circulating-coarse.wav']['sha256']
    disagreement=sum(x!=y for x,y in zip(*detail)); assert disagreement>0
    receipt={'classification':'synthetic, same-agent cross-check; conditional bridge coupling not independent trajectories', 'numpy':np.__version__,'scipy':scipy.__version__,'matrix_checks':checks,'max_matrix_row_error':maxerr,'coarse_identical':True,'detail_disagreements':disagreement,'bridge_attempts':trials,'accepted_path_jumps':jumps,'skeleton':skeleton,'audio':audio}
    (ROOT/'native-execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': main()
