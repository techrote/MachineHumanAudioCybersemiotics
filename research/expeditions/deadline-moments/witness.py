"""Synthetic moment archive, direct LP cross-check, original stereo pulse score."""
from fractions import Fraction as F
from itertools import combinations
from math import prod, sin, pi
from pathlib import Path
import collections, hashlib, json, random, struct, wave, sys
import numpy as np
from scipy.optimize import linprog
import scipy

HERE = Path(__file__).resolve().parent

def weights(xs):
    w = [F(1, prod(x-y for y in xs if y != x)) for x in xs]
    m = sum(v for v in w if v > 0)
    return [v/m for v in w]

def exact_gap(xs, k, threshold):
    if k >= len(xs)-1:
        return F(0)
    return max(abs(sum(w for x,w in zip(s,weights(s)) if x<=threshold))
               for s in combinations(xs,k+2))

def lp_gap(xs,k,t):
    n=len(xs); x=np.array(xs,dtype=float); x=(x-x.min())/(x.max()-x.min())*2-1
    V=np.array([x**j for j in range(1,k+1)]).reshape(k,n)
    A=np.vstack([np.r_[np.ones(n),np.zeros(n)],np.r_[np.zeros(n),np.ones(n)],np.c_[V,-V]])
    f=np.array([int(v<=t) for v in xs]); b=np.r_[1.,1.,np.zeros(k)]
    fit=linprog(np.r_[-f,f], A_eq=A,b_eq=b,bounds=(0,None),method='highs')
    assert fit.success,fit.message
    return -fit.fun

def main():
    checks=0; err=0.
    for xs in [list(range(n)) for n in range(3,10)]+[[-10,-7,-3,2,6,9],[-9,-4,-1,1,4,9]]:
        for k in range(min(6,len(xs)-1)+1):
            for t in xs[:-1]:
                d=abs(lp_gap(xs,k,t)-float(exact_gap(xs,k,t))); err=max(err,d); assert d<1e-7,(xs,k,t,d); checks+=1
    # 63 equal-duration episodes: each list is an exact weighted inventory.
    inventories={'early':[1]*30+[7]*33,'late':[3]*55+[12]*8}
    rate=8000; slot=80; episode=14*slot; pulse=40
    audio={}; decoded_moments=[]
    for name,events in inventories.items():
        random.Random(676).shuffle(events)
        path=HERE/(name+'.wav'); samples=[]
        for t in events:
            for i in range(episode):
                j=i-t*slot
                L=round(10000*sin(2*pi*400*i/rate)*sin(pi*i/pulse)**2) if i<pulse else 0
                R=round(10000*sin(2*pi*800*j/rate)*sin(pi*j/pulse)**2) if 0<=j<pulse else 0
                samples.append((L,R))
        with wave.open(str(path),'wb') as f:
            f.setparams((2,2,rate,0,'NONE','not compressed')); f.writeframes(b''.join(struct.pack('<hh',*s) for s in samples))
        with wave.open(str(path),'rb') as f: data=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,episode,2).astype(np.int64)
        energy=(data[:,:,1]**2).reshape(-1,14,slot).sum(axis=2)
        got=energy.argmax(axis=1).tolist(); assert got==events
        assert np.all((energy>0).sum(axis=1)==1)
        left=(data[:,:,0]**2).reshape(-1,14,slot).sum(axis=2); assert np.all(left.argmax(axis=1)==0) and np.all((left>0).sum(axis=1)==1)
        moments=[str(F(sum(t**k for t in got),len(got))) for k in (1,2)]
        decoded_moments.append(moments)
        audio[name]={'frames':len(got),'histogram':dict(sorted(collections.Counter(got).items())),'deadline_slot':2,'success':str(F(sum(t<=2 for t in got),len(got))),'moments':moments,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    assert decoded_moments[0]==decoded_moments[1]
    receipt={'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'lp_checks':checks,'max_lp_error':err,'decoded_episodes':126,'audio':audio,'assertion_failures':0}
    (HERE/'native-execution.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,indent=2,sort_keys=True))
if __name__=='__main__': main()
