"""Independent numerical LP and exact rational syndrome check for MHAC #759."""
from itertools import combinations
import json
import numpy as np
import scipy
from scipy.optimize import linprog
import sympy as sp

T = [1,2,9,11,22,25,26,27,33,47,52,56,63,64,70,72,76,80,83,94,95,98]
H = [1,-1,0,-1,-1,-1,-1,1,0,1,0,0,0]

def design(ts):
    return np.array([[1]+[int(t%p==r) for p in (3,5,7) for r in range(1,p)] for t in ts], dtype=np.int64)

def run():
    results = []
    for k in (1,2,3):
        ts = T+[t+105*j for j in range(1,k) for t in T if t!=76]
        a = design(ts)
        v = a@H
        z = np.where(v==2,2,0)
        n,d = a.shape
        m = sp.Matrix(a.tolist())
        f = sp.Matrix.hstack(*m.T.nullspace()).T
        assert f*m == sp.zeros(n-d,d)
        # Exact syndrome enumeration: all supports up to the declared error budget.
        # The distance proof guarantees every such column set is independent.
        s = f*sp.Matrix(z.tolist())
        hits = []
        checked = 0
        for support in combinations(range(n),k):
            fs = f[:,list(support)]
            # Exact rational normal equations; fs has full column rank.
            candidate = (fs.T*fs).inv() * fs.T*s
            checked += 1
            if fs*candidate == s:
                hits.append((list(support),list(candidate)))
        assert len(hits)==1 and hits[0][0]==np.flatnonzero(z).tolist() and all(x==2 for x in hits[0][1])
        # Solve the actual unit-weight LAD problem, not merely compare two candidates.
        lp = linprog(np.r_[np.zeros(d),np.ones(n)], A_ub=np.block([[a,-np.eye(n)],[-a,-np.eye(n)]]), b_ub=np.r_[z,-z], bounds=[(None,None)]*d+[(0,None)]*n, method='highs')
        assert lp.success and lp.fun <= k+1+1e-8
        if k>1:
            assert lp.fun < 2*k-1e-8
        results.append(dict(k=k,observations=n,syndrome_supports=checked,unique_support=hits[0][0],lad_optimum=round(float(lp.fun),9),truth_cost=2*k,witness_cost=k+1))
    return dict(numpy=np.__version__,scipy=scipy.__version__,sympy=sp.__version__,profiles=results,assertion_failures=0)

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
