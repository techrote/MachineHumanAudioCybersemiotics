"""Independent matrix oracle: no import of fingerprint.py."""
from itertools import permutations
import numpy as np

n=8
# Enumerate all pairings through permutation quotient rather than recursion.
ms=sorted({tuple(sorted(tuple(sorted(p[i:i+2])) for i in range(0,n,2)))
           for p in permutations(range(n))})
def matrix(m,skip=-1):
    a=np.zeros((n,n),dtype=np.int64)
    for j,(i,k) in enumerate(m):
        a[i,i]=a[k,k]=2 if j==skip else 1
        if j!=skip: a[i,k]=a[k,i]=1
    return a
first=tuple((i,i+1) for i in range(0,n,2)); A=matrix(first)
allm=[matrix(m) for m in ms]
count=checks=0
for j,B in enumerate(allm):
    for k,C in enumerate(allm):
        if not np.all(C@B@A==1): continue
        count+=1
        mats=[A,B,C]; rounds=[first,ms[j],ms[k]]
        for stage in range(3):
            for gate in range(4):
                d=mats.copy(); d[stage]=matrix(rounds[stage],gate)
                E=d[2]@d[1]@d[0]-1
                assert np.sum(E*E)==16 and np.max(np.abs(E))==1
                assert np.count_nonzero(np.any(E,axis=0))==2**(stage+1)
                assert np.count_nonzero(np.any(E,axis=1))==2**(3-stage)
                assert np.linalg.matrix_rank(E)==1
                checks+=1
print(f'pairings={len(ms)} candidate_triples={len(ms)**2} exact={count} single_fault_checks={checks} numpy={np.__version__}')
