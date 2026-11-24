"""Exact regression, optional independent LP, and original circular-block WAVs."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import wave
from fractions import Fraction as F
from repair import conv, norm, delta, plan


def sub(a,b):
    return tuple(x-y for x,y in zip(a,b))


def lp(h, budget):
    import numpy as np
    from scipy.optimize import linprog
    n = len(h)
    H = np.column_stack([np.roll(np.array(h,float), j) for j in range(n)])
    A = np.block([[H,-H,np.eye(n),-np.eye(n)],
                  [np.ones((1,n)),-np.ones((1,n)),np.zeros((1,2*n))]])
    u = np.r_[np.zeros(n),np.ones(n),np.zeros(2*n)][None,:]
    z = linprog(np.r_[np.zeros(2*n),np.ones(2*n)], A_ub=u,
                b_ub=[float(budget)], A_eq=A, b_eq=np.r_[np.eye(n)[0],1],
                bounds=(0,None), method='highs')
    if not z.success:
        raise RuntimeError(z.message)
    return z.fun


def verify(use_lp):
    exact=oracles=0
    maxerr=0.0
    for n in range(2,17):
        for q in sorted({F(k,m) for m in range(2,13) for k in range(m//2+1)}):
            initial=plan(n,q,0)
            need=initial['required']
            budgets=[F(0),F(1,10),F(1),F(4)] if need is None else [need*i/4 for i in range(6)]
            for v in budgets:
                z=plan(n,q,v); h,g,b,t=(z[k] for k in ('h','g','inverse','dual'))
                assert sum(g)==1 and (norm(g)-1)/2 <= v
                assert norm(sub(conv(h,g),delta(n)))==z['residual']
                if t is not None:
                    assert conv(h,b)==delta(n)
                    assert max(t)==t[0] and min(t)==t[1]
                    assert t[0]-t[1]==(norm(b)-1)/q
                    bound=max(F(0),2*(norm(b)-1-2*v)/(max(t)-min(t)))
                    assert bound==z['residual']
                elif b is None:
                    assert sum((-1)**j*h[j] for j in range(n))==0 and z['residual']==1
                exact+=1
                if use_lp and n<=10 and q.denominator<=8:
                    err=abs(lp(h,v)-float(z['residual']))
                    assert err<1e-7,(n,q,v,err)
                    maxerr=max(maxerr,err); oracles+=1
    h=(F(1,2),F(3,10),F(1,5)); b=(F(19,7),F(-11,7),F(-1,7))
    g=(F(13,7),F(-6,7),F(0)); v=F(6,7)
    assert conv(h,b)==delta(3) and (norm(g)-1)/2==v==(norm(b)-1)/4
    assert norm(sub(conv(h,g),delta(3)))==F(17,35)<F(1,2)
    if use_lp:
        assert abs(lp(h,v)-17/35)<1e-8
    for n,q,v in [(1,F(1,4),0),(4,F(3,4),0),(4,F(1,4),-1)]:
        try: plan(n,q,v)
        except ValueError: pass
        else: raise AssertionError('invalid argument accepted')
    return dict(exact_cases=exact, lp_cases=oracles, max_lp_error=maxerr,
                multitap_counterexample={'budget':'6/7','chord':'1/2','witness':'17/35'}, invalid_cases=3)


def render(out):
    n=8; q=F(2,5); d=delta(n)
    z=plan(n,q,0); h=z['h']; y=conv(h,d)
    half=plan(n,q,1)['g']; full=plan(n,q,2)['g']
    noise=tuple(F((-1)**i,25) for i in range(n))
    noisy=tuple(a+b for a,b in zip(y,noise))
    cases={'clean-repair':(y,conv(full,y)), 'noise-debt':(conv(half,noisy),conv(full,noisy))}
    data={}
    for name,(left,right) in cases.items():
        path=out/(name+'.wav'); payload=bytearray()
        for i in range(8*800*5):
            k=(i//800)%n; t=i%800
            carrier=math.sin(2*math.pi*400*t/16000)*math.sin(math.pi*t/800)**2
            payload.extend(struct.pack('<hh',round(20000*float(left[k])*carrier),round(20000*float(right[k])*carrier)))
        with wave.open(str(path),'wb') as f:
            f.setparams((2,2,16000,0,'NONE','not compressed')); f.writeframes(payload)
        data[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                    'left':list(map(str,left)), 'right':list(map(str,right)), 'frames':len(payload)//4}
    assert conv(full,y)==d
    assert norm(full)==5 and norm(half)==3
    assert max(map(abs,conv(full,noise)))==F(1,5)
    assert max(map(abs,conv(half,noise)))==F(3,25)
    return data


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--lp',action='store_true'); p.add_argument('--out',type=Path,default=Path('run'))
    a=p.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    receipt={'verification':verify(a.lp),'audio':render(a.out)}
    print(json.dumps(receipt,sort_keys=True,indent=2))
