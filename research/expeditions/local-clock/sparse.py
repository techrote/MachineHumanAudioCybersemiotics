"""Exact two-residual phase certificate; standard library only."""
from fractions import Fraction as F
from itertools import combinations
from random import Random
import json
P=(5,7,11,13)
Q=17

def conv(a,b):
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]+=x*y
    return c

def R(t,r): return Q*int(t%Q==r)-1

def dot(a,b): return sum(x*y for x,y in zip(a,b))

def det(v,w): return v[0]*w[1]-v[1]*w[0]

def run(nuisance):
    L=[1]
    for p in P: L=conv(L,[1]*p)
    if nuisance: L=conv(L,[-1,0,1])
    d=len(L)-1
    V=[tuple(dot(L,[R(j+t,r) for j in range(d+1)]) for t in (0,1)) for r in range(Q)]
    ds=[abs(det(v,w)) for v,w in combinations(V,2)]
    assert min(ds)>0
    rng=Random(20261127); checks=0
    for r in range(Q):
        for gain in (-3,-1,F(1,3),2):
            C=[]
            for p in P:
                a=[rng.randrange(-9,10) for _ in range(p-1)]; C.append(a+[-sum(a)])
            y=[sum(c[t%p] for p,c in zip(P,C))+gain*R(t,r)+(4-7*(-1)**t if nuisance else 0) for t in range(d+2)]
            v=tuple(dot(L,y[t:t+d+1]) for t in (0,1))
            matches=[i for i,w in enumerate(V) if det(v,w)==0]
            assert matches==[r]
            j=0 if V[r][0] else 1
            assert F(v[j],V[r][j])==gain
            checks+=1
    # One residual cannot identify the line: choose distinct phases with nonzero first coordinate.
    a,b=[r for r,v in enumerate(V) if v[0]][:2]
    ga,gb=V[b][0],V[a][0]
    difference=[ga*R(t,a)-gb*R(t,b) for t in range(d+1)]
    assert dot(L,difference)==0 and ga and gb and a!=b
    # This finite difference belongs to the restriction of the relaxed nuisance space:
    # first d samples determine its unique recurrence continuation, including sample d.
    assert -dot(L[:-1],difference[:-1])//L[-1]==difference[-1]
    return dict(nuisance=nuisance,degree=d,samples=d+2,filter_l1=sum(map(abs,L)),
                signatures=V,determinants_checked=len(ds),min_abs_determinant=min(ds),
                exact_decode_checks=checks,one_short_collision=dict(phases=[a,b],gains=[ga,gb]))

if __name__=='__main__': print(json.dumps([run(False),run(True)],indent=2))
