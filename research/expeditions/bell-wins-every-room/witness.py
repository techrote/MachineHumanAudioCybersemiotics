"""Exact independent-method checks of the context audit; original synthetic score renderer."""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import json, math, wave, struct, hashlib

ROOT = Path(__file__).resolve().parent

def compositions(n,k):
    for cuts in combinations(range(1,n),k-1):
        yield tuple(b-a for a,b in zip((0,)+cuts,cuts+(n,)))

def partitions(n):
    if n==0:
        yield ()
    else:
        for rest in partitions(n-1):
            for i in range(len(rest)):
                yield rest[:i]+(rest[i]+(n-1,),)+rest[i+1:]
            yield rest+((n-1,),)

def profile(p,q,groups):
    return sorted((F(sum(p[i] for i in g),sum(q[i] for i in g)),sum(q[i] for i in g)) for g in groups)

def knots(rows):
    x=y=0
    out=[(x,F(y))]
    for r,w in rows:
        x+=w; y+=w*r; out.append((x,y))
    return out

def at(pts,x):
    for (a,b),(c,d) in zip(pts,pts[1:]):
        if a<=x<=c:return b+(d-b)*F(x-a,c-a)
    raise ValueError(x)

def gap(f,c):
    return max(at(c,x)-at(f,x) for x in {a for a,_ in f+c})

def strict_counterexample():
    attempts=0
    for N in range(5,13):
        # Four contexts are enough; only strictly increasing ratios.
        n=4; parts=list(partitions(n)); comp=list(compositions(N,n))
        for p in comp:
            for q in comp:
                r=tuple(F(a,b) for a,b in zip(p,q))
                if any(a>=b for a,b in zip(r,r[1:])):continue
                attempts+=1
                f=knots(profile(p,q,[(i,) for i in range(n)]))
                for k in (2,3):
                    options=[(gap(f,knots(profile(p,q,g))),g) for g in parts if len(g)==k]
                    best=min(options)
                    cont=min((v,g) for v,g in options if all(max(s)-min(s)+1==len(s) for s in g))
                    if best[0]<cont[0]:
                        return dict(N=N,p=p,q=q,ratios=list(map(str,r)),k=k,arbitrary=str(best[0]/N),contiguous=str(cont[0]/N),arbitrary_groups=best[1],contiguous_groups=cont[1],strict_profiles_examined=attempts)
    return dict(strict_profiles_examined=attempts,found=False)

def exact_checks():
    p=[F(1,10),F(2,10),F(3,10),F(4,10)];q=[F(1,4)]*4;delta=F(1,10)
    b=[F(9,10),0,0,0];a=[v+delta for v in b]
    A=sum(x*y for x,y in zip(p,a)); B=sum(x*y for x,y in zip(q,b))
    assert A==F(19,100) and B==F(9,40) and A-B==F(-7,200)
    # Check TV bound by literal vertex enumeration, plus heterogeneous margins.
    checks=0
    for n in range(2,5):
        for P in compositions(6,n):
            for Q in compositions(6,n):
                ps=[F(x,6) for x in P];qs=[F(x,6) for x in Q]
                for d in (F(0),F(1,3),F(2,3),F(1)):
                    vals=[]
                    for z in product((0,1),repeat=n):
                        b=[(1-d)*v for v in z];a=[d+v for v in b]
                        vals.append(sum(x*y for x,y in zip(ps,a))-sum(x*y for x,y in zip(qs,b)));checks+=1
                    tv=sum(abs(x-y) for x,y in zip(ps,qs))/2
                    assert min(vals)==d-(1-d)*tv and max(vals)==d+(1-d)*tv
    return dict(vertex_checks=checks,strict_partition_counterexample=strict_counterexample(),witness=dict(A=str(A),B=str(B),gap=str(A-B)))

def render():
    # 40 trials per policy, equal-duration symbols; counts are exact synthetic fixture.
    # 2-context example: A succeeds 9/10 in easy and 6/30 in hard; B 24/30 and 1/10.
    # A beats B in each by 0.1, yet aggregate 15/40 < 25/40.
    # Here two sets of 40 trials are encoded as 40-slot scores. Each slot has a context cue
    # (300 or 600 Hz), then an outcome cue (400 or 800 Hz). Untagged variant omits context.
    out={};rate=8000;slot=1200
    def tone(freq, length=slot//2):
        return [round(1800*math.sin(2*math.pi*freq*i/rate)*math.sin(math.pi*i/(length-1))**2) for i in range(length)]
    for name,counts in [('a',[(10,9),(30,6)]),('b',[(30,24),(10,1)])]:
        for tagged in (False,True):
            samples=[]
            for j,(total,success) in enumerate(counts):
                for i in range(total):
                    samples.extend(tone(300+300*j) if tagged else [0]*(slot//2))
                    samples.extend(tone(800 if i<success else 400))
            assert len(samples)==48000
            path=ROOT/(name+('-tagged' if tagged else '-untagged')+'.wav')
            with wave.open(str(path),'wb') as f:
                f.setparams((1,2,rate,len(samples),'NONE','not compressed'))
                f.writeframes(struct.pack('<'+'h'*len(samples),*samples))
            out[path.name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'samples':len(samples),'successes':sum(s for _,s in counts),'trials':sum(t for t,_ in counts)}
    return out

if __name__=='__main__':
    result=exact_checks();result['audio']=render();print(json.dumps(result,indent=2,sort_keys=True))
