"""Same-agent numerical LP cross-check of polynomial nuisance certificates."""
import itertools
import json
import random
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog
import scipy


def certificate(z, p, I):
    best = Fraction(0)
    for J in itertools.combinations(I, p+2):
        weights = [Fraction(1, __import__('math').prod(i-j for j in J if j != i))
                   for i in J]
        best = max(best, abs(sum(w*z[i] for i,w in zip(J,weights))) /
                   sum(map(abs,weights)))
    return best


def oracle(z, p, I):
    if len(I) <= p+1:
        return 0.0
    scale = max(1, max(I))
    A = np.array([[(i/scale)**k for k in range(p+1)] for i in I])
    col = -np.ones((len(I), 1))
    vals = np.array([z[i] for i in I])
    res = linprog([0]*(p+1)+[1], A_ub=np.vstack((np.hstack((A,col)),
                  np.hstack((-A,col)))), b_ub=np.concatenate((vals,-vals)),
                  bounds=[(None,None)]*(p+1)+[(0,None)], method='highs')
    assert res.success, res.message
    return res.fun


def main():
    rng = random.Random(404)
    counts = {str(p): 0 for p in range(4)}
    max_error = 0.0
    for p in range(4):
        for _ in range(120):
            n = rng.randint(p+2, 11)
            z = [rng.randint(-9,9) for _ in range(n)]
            I = sorted(rng.sample(range(n), rng.randint(p+2,n)))
            err = abs(float(certificate(z,p,I))-oracle(z,p,I))
            assert err < 1e-8, (p,z,I,err)
            max_error = max(max_error,err)
            counts[str(p)] += 1
    print(json.dumps({'seed':404,'scipy':scipy.__version__,'comparisons_by_degree':counts,
                      'max_absolute_error':max_error,'assertion_failures':0},indent=2))


if __name__ == '__main__':
    main()
