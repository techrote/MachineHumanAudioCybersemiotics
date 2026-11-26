"""Exact witness checks, independent labelled-cube LP, deterministic audio."""
from fractions import Fraction as F
from itertools import combinations, product
from collections import Counter
from pathlib import Path
import hashlib, json, math, random, sys, wave, struct
import numpy as np
from scipy.optimize import linprog
import scipy

ROOT=Path(__file__).resolve().parent

def bounds(n,k):
    if k==3:
        u=F(1,n-2 if n%2 else n-1)
        return -u,u
    squares=sorted({s*s for s in range(-n,n+1,2)})
    a=max(x for x in squares if x<=n); b=min(x for x in squares if x>=n)
    return F((a+b)*n-a*b-3*n*n+2*n,n*(n-1)*(n-2)*(n-3)), F(1,n-2 if n%2 else n-3)

def law(n,k,upper):
    if k==3:
        d={-1:F(n,n+1),n:F(1,n+1)} if n%2 else {-2:F(n,2*(n+2)),0:F(1,2),n:F(1,n+2)}
        return d if upper else {-s:p for s,p in d.items()}
    squares=sorted({s*s for s in range(-n,n+1,2)})
    if upper: a,b=squares[0],squares[-1]
    else: a=max(x for x in squares if x<=n); b=min(x for x in squares if x>=n)
    sq={a:F(1)} if a==b else {a:F(b-n,b-a),b:F(n-a,b-a)}
    d={}
    for v,p in sq.items():
        s=math.isqrt(v)
        if s: d[s]=d[-s]=p/2
        else: d[0]=p
    return d

def marginal(n,d,k):
    out={}
    for x in product((-1,1),repeat=k):
        j=x.count(1); prob=F(0)
        for s,p in d.items():
            m=(n+s)//2
            prob+=p*F(math.comb(m,j)*math.comb(n-m,k-j),math.comb(n,k)*math.comb(k,j))
        out[x]=prob
    return out

def encode(name,frames,n):
    fs=8000; length=640; freqs=[250+50*i for i in range(n)]
    templates=[[math.sin(2*math.pi*f*t/fs) for t in range(length)] for f in freqs]
    # integer number of cycles; use fixed per-voice level, no frame normalization
    samples=[round(3500*sum(templates[i][t] for i,v in enumerate(x) if v==1)) for x in frames for t in range(length)]
    path=ROOT/(name+'.wav')
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(fs)
        w.writeframes(struct.pack('<'+'h'*len(samples),*samples))
    with wave.open(str(path),'rb') as w:
        raw=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float).reshape(-1,length)
    amps=raw@np.array(templates).T/(length/2)
    recovered=[tuple(1 if v>1750 else -1 for v in row) for row in amps]
    assert recovered==frames
    return {'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'frames':len(frames),'decoded_bits':len(frames)*n,'max_amplitude_error':float(np.max(np.abs(amps-np.array([[3500 if v==1 else 0 for v in x] for x in frames]))))}

def run():
    cells=0; witnesses=0; lp=0; maxerr=0.
    for n in range(3,65):
        for k in (3,4):
            if n<k: continue
            lo,hi=bounds(n,k)
            for upper,c in ((False,lo),(True,hi)):
                d=law(n,k,upper)
                assert min(d.values())>=0 and sum(d.values())==1
                out=marginal(n,d,k)
                for x,p in out.items():
                    assert p==F(1,2**k)*(1+c*math.prod(x)); cells+=1
                witnesses+=1
    # No count-law symmetry imposed: constraints for every labelled subset.
    for n in range(3,11):
        bits=np.array(list(product((-1,1),repeat=n)),dtype=float)
        for k in (3,4):
            if n<k: continue
            A=np.array([np.ones(len(bits))]+[np.prod(bits[:,idx],axis=1) for j in range(1,k) for idx in combinations(range(n),j)])
            b=np.array([1]+[0]*(len(A)-1))
            obj=np.mean([np.prod(bits[:,idx],axis=1) for idx in combinations(range(n),k)],axis=0)
            # Objective is the average k-way product, so permutation averaging gives exchangeable laws.
            for sign,target in ((1,bounds(n,k)[0]),(-1,bounds(n,k)[1])):
                fit=linprog(sign*obj,A_eq=A,b_eq=b,bounds=(0,None),method='highs')
                assert fit.success
                err=abs(sign*fit.fun-float(target)); assert err<1e-8
                maxerr=max(maxerr,err); lp+=1
    # Exact 5-voice witness for c3=1/3; two copies of each 2-plus word and four all-plus words.
    ext=[x for x in product((-1,1),repeat=5) if x.count(1)==2]*2+[(1,)*5]*4
    random.Random(658).shuffle(ext)
    projected=[x[:3] for x in ext]
    iid=list(product((-1,1),repeat=3))*3; random.Random(658).shuffle(iid)
    for idx in combinations(range(5),3):
        assert Counter(tuple(x[i] for i in idx) for x in ext)==Counter({x:4 if math.prod(x)==1 else 2 for x in product((-1,1),repeat=3)})
    assert all(Counter(tuple(x[i] for i in idx) for x in ext)==Counter({x:6 for x in product((-1,1),repeat=2)}) for idx in combinations(range(5),2))
    audio=[encode('five-voice-extension',ext,5),encode('three-voice-projection',projected,3),encode('three-voice-iid',iid,3)]
    return {'python':sys.version.split()[0],'scipy':scipy.__version__,'numpy':np.__version__,'exact_endpoint_witnesses':witnesses,'exact_marginal_cells':cells,'labelled_cube_linear_programs':lp,'max_lp_error':maxerr,'audio':audio,'assertion_failures':0}

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
