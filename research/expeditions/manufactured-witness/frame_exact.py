"""Exact eight-frame search after a forced uniform three-bit projection.
Dense consecutive grids only, n>=5. Each column encoded as an 8-bit truth table.
"""
from itertools import combinations

def masks(n):
    groups={}
    for i in range(n):
        for j in range(i,n): groups.setdefault(i+j,[]).append((1<<i)^(1<<j))
    return sorted({a^b for g in groups.values() for a,b in combinations(g,2)})

def search(n,budget=10_000_000):
    if not 5<=n<=16:raise ValueError('n')
    m=masks(n); basis=[5,10,17]
    assert all((basis[0] if k&1 else 0)^(basis[1] if k&2 else 0)^(basis[2] if k&4 else 0) in m for k in range(1,8))
    # Fix row ordering by the three forced bits; per-frame global flip makes x0=0.
    # Per-column flips fix row0=0. Then x2=A, x3=x1 xor B, x4=C.
    A,B,C=0xaa,0xcc,0xf0
    groups=[[] for _ in range(n)]
    for mask in m: groups[mask.bit_length()-1].append([j for j in range(n) if mask>>j&1])
    cols=[0]*n; visits=0
    def check(k):
        for g in groups[k]:
            v=0
            for j in g:v^=cols[j]
            if v.bit_count()!=4:return False
        return True
    def walk(k):
        nonlocal visits
        if k==n:return True
        opts=([A] if k==2 else [cols[1]^B] if k==3 else [C] if k==4 else range(0,256,2))
        for v in opts:
            if visits>=budget:return None
            visits+=1;cols[k]=v
            if not check(k):continue
            a=walk(k+1)
            if a is not False:return a
        return False
    ans=walk(1)
    return dict(n=n,frames=8,visited=visits,status='FEASIBLE' if ans else 'INFEASIBLE' if ans is False else 'BUDGET_EXHAUSTED',columns=cols.copy() if ans else None)
if __name__=='__main__':
    import json
    for n in range(5,11):print(json.dumps(search(n)),flush=True)
