"""Exhaustive strict monotone product orders, exact certificates after LP discovery.
Run: python laboratory.py > execution.json (requires scipy and numpy).
All examples synthetic. No human data.
"""
from itertools import combinations
from fractions import Fraction
from functools import lru_cache
from collections import Counter
import json, math
import numpy as np
from scipy.optimize import linprog


def orders(m,n):
    def rec(lengths, order):
        if len(order)==m*n:
            yield tuple(order); return
        for i,j in enumerate(lengths):
            if j<n and (i==0 or lengths[i-1]>j):
                z=list(lengths); z[i]+=1
                yield from rec(z,order+[(i,j)])
    yield from rec([0]*m,[])


def features(cell,m,n):
    i,j=cell
    return tuple(int(k==i) for k in range(1,m))+tuple(int(k==j) for k in range(1,n))


def rows(order,m,n):
    f=[features(c,m,n) for c in order]
    return [tuple(b-a for a,b in zip(u,v)) for u,v in zip(f,f[1:])]


def rational(values):
    q=[Fraction(float(v)).limit_denominator(100000) for v in values]
    d=math.lcm(*(v.denominator for v in q))
    return [int(v*d) for v in q]


@lru_cache(None)
def certify(order,m,n):
    A=rows(order,m,n); d=m+n-2; k=len(A)
    # Strict inequalities are equivalent to unit margins by common scaling.
    x=linprog(np.zeros(d),A_ub=-np.array(A),b_ub=-np.ones(k),bounds=[(None,None)]*d,method='highs')
    if x.success:
        w=rational(x.x)
        assert all(sum(a*b for a,b in zip(r,w))>0 for r in A)
        return True, w
    assert x.status==2, x.message
    y=linprog(np.zeros(k),A_eq=np.vstack([np.array(A).T,np.ones(k)]),b_eq=[0]*d+[1],bounds=(0,None),method='highs')
    assert y.success,y.message
    w=rational(y.x)
    assert min(w)>=0 and sum(w)>0
    assert all(sum(w[i]*A[i][j] for i in range(k))==0 for j in range(d))
    return False,w


def sub(order,rr,cc):
    return tuple((rr.index(i),cc.index(j)) for i,j in order if i in rr and j in cc)


def local(order,m,n,r,c):
    return all(certify(sub(order,rr,cc),r,c)[0] for rr in combinations(range(m),r) for cc in combinations(range(n),c))


def matrix(order,m,n):
    return [[order.index((i,j))+1 for j in range(n)] for i in range(m)]


def witness(order,m,n,weights):
    # Cancel a weighted list of comparisons, retaining the literal endpoint cells.
    return dict(ranks=matrix(order,m,n), comparisons=[dict(low=order[i],high=order[i+1],multiplicity=w) for i,w in enumerate(weights) if w])


def interaction(order,m,n):
    A=np.array(rows(order,m,n)); N=len(order); d=m+n-2
    B=np.diff(np.eye(N),axis=0)
    result=linprog([0]*(d+N)+[1],A_ub=np.vstack([
        np.column_stack([-A,-B,np.zeros(N-1)]),
        np.column_stack([np.zeros((N,d)),np.eye(N),-np.ones(N)]),
        np.column_stack([np.zeros((N,d)),-np.eye(N),-np.ones(N)])]),
        b_ub=[-1]*(N-1)+[0]*(2*N),bounds=[(None,None)]*(d+N)+[(0,None)],method='highs')
    assert result.success
    v=[Fraction(float(x)).limit_denominator(100000) for x in result.x]
    w,e,eps=v[:d],v[d:d+N],v[-1]
    assert eps>=0 and max(map(abs,e))<=eps
    assert all(sum(a*b for a,b in zip(r,w))+e[i+1]-e[i]>=1 for i,r in enumerate(A.tolist()))
    lam=rational(-result.ineqlin.marginals[:N-1])
    assert min(lam)>=0 and sum(lam)>0
    assert all(sum(lam[i]*int(A[i,j]) for i in range(N-1))==0 for j in range(d))
    coeff=[-lam[0]]+[a-b for a,b in zip(lam,lam[1:])]+[lam[-1]]
    assert Fraction(sum(lam),sum(map(abs,coeff)))==eps
    return str(eps)


def census(m,n):
    total=good=local3=proper=0; first=None; firstproper=None; costs=Counter()
    for order in orders(m,n):
        total+=1; ok,w=certify(order,m,n)
        good+=ok
        if not ok and (m,n) in ((3,3),(3,4)): costs[interaction(order,m,n)]+=1
        if not ok and m>=3 and n>=3 and local(order,m,n,3,3):
            local3+=1
            if first is None: first=witness(order,m,n,w)
        if not ok and m>=3 and n>=3 and local(order,m,n,m-1,n) and local(order,m,n,m,n-1):
            proper+=1
            if firstproper is None: firstproper=witness(order,m,n,w)
    hook=math.prod(m+n-i-j-1 for i in range(m) for j in range(n))
    assert total==math.factorial(m*n)//hook
    return dict(m=m,n=n,orders=total,additive=good,nonadditive=total-good,nonadditive_passing_all_3x3=local3 if m>=3 and n>=3 else None,nonadditive_passing_all_proper_rectangles=proper if m>=3 and n>=3 else None,first_local3_witness=first,first_proper_witness=firstproper,interaction_cost_counts=dict(sorted(costs.items())))


if __name__=='__main__':
    out=[]
    for m,n in [(2,2),(2,3),(2,4),(2,5),(2,6),(3,3),(3,4),(3,5)]:
        out.append(census(m,n))
    print(json.dumps(out,indent=2))
