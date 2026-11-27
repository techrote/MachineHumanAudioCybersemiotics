"""Exploratory certificate laboratory. LP discovers candidates; Fraction checks them."""
from fractions import Fraction as F
from itertools import combinations
from math import prod
import json
import numpy as np
import sympy as sp
from scipy.optimize import linprog


def matrix(ps, n):
    return [[1]+[int(t%p==j) for p in ps for j in range(1,p)] for t in range(n)]


def polynomial(ps):
    a = [-1, 1]
    for p in ps:
        b = [0]*(len(a)+p-1)
        for i,v in enumerate(a):
            for j in range(p):
                b[i+j] += v
        a = b
    return a


def syndrome(columns, y):
    return tuple(sum(c[j]*v for c,v in zip(columns,y)) for j in range(2))


def decode(columns, y):
    s = syndrome(columns,y)
    if s == (0,0):
        return list(y), None
    candidates=[]
    for i,c in enumerate(columns):
        j=0 if c[0] else 1
        a=F(s[j],c[j])
        if tuple(a*v for v in c)==s:
            candidates.append((i,a))
    if len(candidates)!=1:
        raise ValueError('not a unique single-error syndrome')
    i,a=candidates[0]
    out=list(y);out[i]-=a
    assert syndrome(columns,out)==(0,0)
    return out,i


def rational(v):
    return F(float(v)).limit_denominator(1000000)


def dual_profile(ps,n):
    rows=matrix(ps,n); A=np.asarray(rows,dtype=float)
    vals=[]
    for i in range(n):
        objective=np.zeros(n);objective[i]=-1
        r=linprog(objective,A_eq=A.T,b_eq=np.zeros(A.shape[1]),
                  bounds=[(0,None) if j==i else (-1,1) for j in range(n)],method='highs')
        assert r.success
        c=list(map(rational,r.x))
        def valid(c):
            return all(sum(c[t]*rows[t][j] for t in range(n))==0 for j in range(len(rows[0])))
        if not valid(c):
            P=polynomial(ps); D=len(P)-1
            H=sp.Matrix([[P[t-k] if 0<=t-k<=D else 0 for k in range(n-D)] for t in range(n)])
            active=[j for j in range(n) if j!=i and abs(abs(r.x[j])-1)<1e-7]
            coeff,params=H[active,:].gauss_jordan_solve(sp.Matrix([1 if r.x[j]>0 else -1 for j in active]))
            assert not params.rows
            c=[F(v) for v in H*coeff]
        assert valid(c)
        assert all(abs(c[j])<=1 for j in range(n) if j!=i)
        vals.append(c[i])
    return min(vals),vals.index(min(vals))


def primal(ps,n,i):
    rows=matrix(ps,n); A=np.asarray(rows,dtype=float); D=A.shape[1]
    r=linprog(np.r_[np.zeros(D),np.ones(n)],
              A_ub=np.vstack([np.c_[A,-np.eye(n)],np.c_[-A,-np.eye(n)]]),b_ub=np.zeros(2*n),
              A_eq=np.array([np.r_[A[i],np.zeros(n)]]),b_eq=[1],
              bounds=[(None,None)]*D+[(0,None)]*n,method='highs')
    assert r.success
    numeric=A@r.x[:D]; support=[j for j in range(n) if abs(numeric[j])>1e-7]
    P=polynomial(ps)
    H=sp.Matrix([[P[t-k] if 0<=t-k<=D else 0 for t in support] for k in range(n-D)]+[[int(t==i) for t in support]])
    coeff,params=H.gauss_jordan_solve(sp.Matrix([0]*(n-D)+[1]))
    assert not params.rows
    h=[F(0)]*n
    for j,v in zip(support,coeff):h[j]=F(v)
    assert h[i]==1
    assert all(sum(P[j]*h[k+j] for j in range(D+1))==0 for k in range(n-D))
    return sum(map(abs,h)),h


def main():
    ps=(5,7,11,13,17); P=polynomial(ps);D=len(P)-1
    H=list(zip(P+[0],[0]+P)); assert D==49 and len(H)==51
    rows=matrix(ps,51)
    assert all(sum(c[k]*r[j] for c,r in zip(H,rows))==0 for k in range(2) for j in range(D))
    determinants=[abs(a[0]*b[1]-a[1]*b[0]) for a,b in combinations(H,2)]
    assert min(determinants)>0
    trials=0
    for seed in range(8):
        theta=[(seed*29+j*17)%41-20 for j in range(D)]
        clean=[sum(a*b for a,b in zip(r,theta)) for r in rows]
        assert decode(H,clean)==(clean,None)
        for i in range(51):
            for error in (-10001,7,123456):
                y=clean.copy();y[i]+=error
                assert decode(H,y)==(clean,i);trials+=1
    false_error=[F(0)]*51;false_error[25]=false_error[26]=F(-1,127)
    received=[1]+[0]*50
    assert syndrome(H,false_error)==syndrome(H,received)
    assert sum(map(abs,false_error))==F(2,127)
    # The false signal is in ker H; rank follows from distinct Fourier roots.
    profiles=[]
    for periods,n,target in [((3,5,7),21,2),((3,5,7),35,4),(ps,57,F(1)),(ps,85,4)]:
        margin,i=dual_profile(periods,n)
        assert margin>=target and (n!=57 or margin>target)
        profiles.append(dict(periods=periods,n=n,dual_min=str(margin),index=i))
    # Prove 56 fails by an actual rational admissible waveform, not a dual search failure.
    mass,h=primal(ps,56,3)
    assert mass<2
    print(json.dumps(dict(polynomial=P,pair_determinants=len(determinants),min_abs_determinant=min(determinants),
        single_error_trials=trials,zero_error_trials=8,short_false_residual_cost='2/127',
        profiles=profiles,at_56=dict(index=3,mass=str(mass),false_cost=str(mass-1),nonzero=[(i,str(v)) for i,v in enumerate(h) if v])),indent=2))

if __name__=='__main__':main()
