#!/usr/bin/env python3
"""Exact rational posterior-path witnesses; optional PCM sonification. No dependencies."""
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from math import lcm, sin, pi
import json, random, struct, wave, hashlib


def cohort_paths(n, tau, delta, prior, rotating):
    a, b = tau-delta, tau+(n-1)*delta
    assert 0 < a < tau < b < 1 and 0 < prior <= tau
    r = min(a/b, (1-b)/(1-a))
    c = prior/tau
    paths = defaultdict(F)
    paths[(F(0),)*n] += 1-c
    for j in range(n):
        p = tuple(b if j == (t if rotating else 0) else a for t in range(n))
        weight = c/n
        for t in range(1,n):
            one = p[t-1]-r*p[t]
            zero = 1-r-one
            assert min(one,zero) >= 0
            paths[p[:t]+(F(1),)*(n-t)] += weight*one
            paths[p[:t]+(F(0),)*(n-t)] += weight*zero
            weight *= r
        paths[p] += weight
    return {p:w for p,w in paths.items() if w}, r


def audit(paths, tau, prior):
    n = len(next(iter(paths)))
    assert sum(paths.values()) == 1
    mass, truth = defaultdict(F), defaultdict(F)
    marginal = [defaultdict(F) for _ in range(n)]
    hit = true_hit = first_weighted = F(0)
    first_times = [F(0)]*n
    for p,w in paths.items():
        for t,x in enumerate(p):
            prefix=p[:t+1]
            mass[prefix]+=w
            truth[prefix]+=w*p[-1]
            marginal[t][(x,1)]+=w*p[-1]
            marginal[t][(x,0)]+=w*(1-p[-1])
        assert all(0<=x<=1 for x in p) and w>0
        k=next((t for t,x in enumerate(p) if x>=tau),None)
        if k is not None:
            hit+=w; true_hit+=w*p[-1]; first_weighted+=w*p[k]; first_times[k]+=w
    assert all(truth[p]==p[-1]*w for p,w in mass.items())
    assert sum(w*p[-1] for p,w in paths.items())==prior
    assert true_hit==first_weighted and true_hit>=tau*hit
    return marginal,hit,true_hit,first_times,len(mass)


def sharp_two_tick(m):
    a,b=F(m-1,2*m),F(m+1,2*m)
    e=F(1,m+1); v=F(1,2)-e
    ys=[F(0),a,b,F(1)]; cols=[e,v,v,e]
    low_a=[e-a*e,v,F(0),a*e]; low_b=[e,F(0),v,F(0)]
    def law(row):
        return {(x,y):w for x,rr in [(a,row),(b,[z-u for z,u in zip(cols,row)])] for y,w in zip(ys,rr) if w}
    return a,b,ys,cols,law(low_a),law(low_b)


def row_vertices(ys, cols, mass, moment):
    """Exact vertex oracle for a capped row with two equality constraints."""
    n=len(ys)
    for i,j in combinations(range(n),2):
        fixed=[k for k in range(n) if k not in (i,j)]
        for bits in product((0,1),repeat=n-2):
            x=[F(0)]*n
            for k,bit in zip(fixed,bits): x[k]=cols[k]*bit
            s=mass-sum(x); t=moment-sum(y*v for y,v in zip(ys,x))
            x[j]=(t-ys[i]*s)/(ys[j]-ys[i]); x[i]=s-x[j]
            if all(0<=v<=u for v,u in zip(x,cols)): yield x


def render(paths, filename, a, b):
    # Exact rational inventory, shuffled only to avoid sorted blocks. Four tones.
    den=lcm(90,*(w.denominator for w in paths.values()))
    seq=[p for p,w in sorted(paths.items()) for _ in range(int(w*den))]
    random.Random(682).shuffle(seq)
    fs=8000; L=400; freqs={F(0):300,a:500,b:700,F(1):900}
    template={x:[round(12000*sin(2*pi*f*k/fs)) for k in range(L)] for x,f in freqs.items()}
    with wave.open(str(filename),'wb') as out:
        out.setparams((1,2,fs,0,'NONE','not compressed'))
        out.writeframes(b''.join(struct.pack('<'+'h'*L,*template[x]) for p in seq for x in p))
    with wave.open(str(filename),'rb') as inp:
        data=struct.unpack('<'+'h'*(inp.getnframes()),inp.readframes(inp.getnframes()))
    for i,x in enumerate(x for p in seq for x in p):
        block=data[i*L:(i+1)*L]
        got=max(template,key=lambda z:sum(a*b for a,b in zip(block,template[z])))
        assert got==x
    return {'episodes':len(seq),'decoded_frames':len(seq)*2,'sha256':hashlib.sha256(filename.read_bytes()).hexdigest()}


def main():
    profiles=prefixes=vertices=0; examples=[]
    for n in range(2,13):
        for tau in (F(1,4),F(1,2),F(3,4)):
            for c in (F(1,3),F(1)):
                for d in (10,100,10000):
                    delta=min(tau,1-tau)/((n-1)*d); prior=c*tau
                    p,r=cohort_paths(n,tau,delta,prior,False)
                    q,s=cohort_paths(n,tau,delta,prior,True)
                    A,B=audit(p,tau,prior),audit(q,tau,prior)
                    assert A[0]==B[0] and r==s
                    a=tau-delta
                    assert A[1]==c/n+c*(n-1)/n*a*(1-r**(n-1))
                    assert B[1]>=c*r**(n-1)
                    assert abs(A[1]-B[1])<=c*F(n-1,n)
                    for t in range(n):
                        expected=c*r**t/n+c*tau*(1-r**t)
                        assert sum(w for (x,y),w in A[0][t].items() if x>=tau)==expected
                    profiles+=1; prefixes+=A[4]+B[4]
                    if tau==F(1,2) and c==1 and d==10000 and n in (2,4,8,12):
                        examples.append({'ticks':n,'stable':float(A[1]),'rotating':float(B[1]),'gap':float(B[1]-A[1]),'supremum':float(F(n-1,n))})
    for m in range(2,101):
        a,b,ys,cols,p,q=sharp_two_tick(m)
        A,B=audit(p,F(1,2),F(1,2)),audit(q,F(1,2),F(1,2))
        assert A[0]==B[0]
        h=[]
        for x in row_vertices(ys,cols,F(1,2),a/2):
            h.append(sum(x[2:])); vertices+=1
        assert min(h)==a*cols[0] and max(h)==a/(2*b)
        assert A[1]==F(1,2)+min(h) and B[1]==F(1,2)+max(h)
        assert B[1]-A[1]==F((m-1)**2,2*m*(m+1))
        prefixes+=A[4]+B[4]
    a,b,ys,cols,p,q=sharp_two_tick(9)
    root=Path(__file__).resolve().parent
    audio={name:render(law,root/(name+'.wav'),a,b) for name,law in [('stable',p),('crossing',q)]}
    receipt={'cohort_profiles':profiles,'exact_prefix_checks':prefixes,'two_tick_profiles':99,'vertex_instances':vertices,'examples':examples,'audio':audio,'assertions':'PASS'}
    (root/'execution.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2,sort_keys=True))

if __name__=='__main__': main()
