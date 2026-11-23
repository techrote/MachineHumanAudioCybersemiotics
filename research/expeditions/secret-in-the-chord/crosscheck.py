#!/usr/bin/env python3
"""Independent finite enumeration cross-check; Python standard library."""
from collections import defaultdict, Counter
from itertools import product, combinations
from fractions import Fraction

def check():
    pairs=groups=projections=0
    for n in range(1,13):
        buckets=defaultdict(list)
        for x in product(range(n+1),repeat=3):
            d=n-sum(x)
            if d<0:
                continue
            p=(*x,d)
            buckets[p[2]+p[3],p[1]+p[3]].append(p)
        for (a,b),tables in buckets.items():
            bound=Fraction(2*min(a,b,n-a,n-b),n)
            tv=[sum(Fraction(abs(i-j),2*n) for i,j in zip(x,y))
                for x in tables for y in tables]
            if max(tv)!=bound:
                raise AssertionError((n,a,b,max(tv),bound))
            pairs+=len(tv)
            groups+=1
    for n in range(2,9):
        for k in range(n+1):
            for idx in combinations(range(n),k):
                counts=[Counter(tuple(v[i] for i in idx)
                                for v in product((0,1),repeat=n)
                                if sum(v)%2==s) for s in (0,1)]
                if (counts[0]==counts[1])!=(k<n):
                    raise AssertionError((n,idx))
                if k==n and counts[0].keys()&counts[1].keys():
                    raise AssertionError("full support overlaps")
                projections+=1
    return dict(groups=groups,table_pairs=pairs,projection_checks=projections)

if __name__=="__main__":
    print(check())
