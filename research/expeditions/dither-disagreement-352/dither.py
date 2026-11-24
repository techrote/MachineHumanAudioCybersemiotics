"""Exact fractional satisfaction compiler for half-LSB signed graph rounding."""
from fractions import Fraction as F
from itertools import combinations, product
from math import lcm


def validate(n, edges):
    edges = tuple(edges)
    if type(n) is not int or not 2 <= n <= 8 or not edges:
        raise ValueError('require 2..8 vertices and nonempty edges')
    seen = set()
    for u,v,p in edges:
        if any(type(x) is not int for x in (u,v,p)) or not 0 <= u < v < n or p not in (0,1) or (u,v) in seen:
            raise ValueError('invalid or duplicate signed edge')
        seen.add((u,v))
    return edges


def satisfaction(n, edges):
    # One representative per complementary pair (bit zero fixed to zero).
    return [[int(((mask >> u) ^ (mask >> v)) & 1 == p) for u,v,p in edges]
            for mask in range(0, 1 << n, 2)]


def solve(n, edges):
    """Return exact optimal distribution and edge-weight certificate.

    Solve max sum(w), A w <= 1, w >= 0 by rational simplex with Bland's rule.
    Dual cover weights are read from objective slack columns.
    """
    edges = validate(n, edges)
    a = satisfaction(n, edges)
    k,m = len(a),len(edges)
    tab = [[F(x) for x in row + [int(i == j) for j in range(k)] + [1]]
           for i,row in enumerate(a)]
    tab.append([F(-1)]*m + [F(0)]*(k+1))
    basis = list(range(m,m+k))
    pivots = 0
    while True:
        col = next((j for j,x in enumerate(tab[-1][:-1]) if x < 0),None)
        if col is None:
            break
        candidates = [(tab[i][-1]/tab[i][col],basis[i],i) for i in range(k) if tab[i][col] > 0]
        if not candidates:
            raise ArithmeticError('unexpected unbounded LP')
        _,_,i = min(candidates)
        row = [x/tab[i][col] for x in tab[i]]
        tab[i] = row
        for j in range(k+1):
            if j != i and tab[j][col]:
                factor = tab[j][col]
                tab[j] = [x-factor*y for x,y in zip(tab[j],row)]
        basis[i] = col
        pivots += 1
        if pivots > 100000:
            raise RuntimeError('pivot budget exhausted; no optimality claim')
    w = [F(0)]*m
    for i,j in enumerate(basis):
        if j < m:
            w[j] = tab[i][-1]
    cover = tab[-1][m:m+k]
    total = tab[-1][-1]
    prob = {2*i:x/total for i,x in enumerate(cover) if x}
    weight = [x/total for x in w]
    success = 1/total
    verify(n,edges,success,prob,weight)
    return success,prob,weight,pivots


def verify(n,edges,success,prob,weight):
    """Exact weak-duality certificate; independent of tableau operations."""
    edges = validate(n,edges)
    if (len(weight) != len(edges) or not 0 <= success <= 1 or
        any(x < 0 for x in weight) or sum(weight) != 1 or
        any(type(s) is not int or s < 0 or s >= 1 << n or s%2 or x < 0 for s,x in prob.items()) or sum(prob.values()) != 1):
        raise ValueError('invalid probability certificate')
    a = satisfaction(n,edges)
    if any(sum(prob.get(2*i,0)*row[j] for i,row in enumerate(a)) < success for j in range(len(edges))):
        raise ValueError('primal lower bound failed')
    if any(sum(x*y for x,y in zip(row,weight)) > success for row in a):
        raise ValueError('dual upper bound failed')


def balanced_period(n,prob,limit=100000):
    """Complement-paired realization; not claimed minimum for general graphs."""
    d = lcm(*(x.denominator for x in prob.values()))
    if 2*d > limit:
        raise ValueError('period budget exceeded')
    full = (1 << n)-1
    return [s for mask,p in sorted(prob.items()) for _ in range(int(d*p)) for s in (mask,mask^full)]


def cycle_edges(parity):
    n = len(parity)
    if n < 3 or any(p not in (0,1) for p in parity) or sum(parity)%2 != 1:
        raise ValueError('require frustrated simple cycle')
    return [(i,i+1,parity[i]) for i in range(n-1)] + [(0,n-1,parity[-1])]


def moving_defect(parity):
    """Shortest balanced optimal period on a frustrated cycle, one flip/frame."""
    cycle_edges(parity)
    n = len(parity)
    mask = bit = 0
    for i,p in enumerate(parity[:-1]):
        bit ^= p
        mask |= bit << (i+1)
    states = []
    for i in range(2*n):
        states.append(mask)
        mask ^= 1 << (i%n)
    return states


def metrics(n,edges,states):
    t = len(states)
    if not t:
        raise ValueError('empty schedule')
    ones = [sum(s >> i & 1 for s in states) for i in range(n)]
    fails = [sum((((s>>u)^(s>>v))&1) != p for s in states) for u,v,p in edges]
    switches = [(a^b).bit_count() for a,b in zip(states,states[1:]+states[:1])]
    return dict(period=t,ones=ones,failures=fails,switches=sum(switches),peak_switch=max(switches))


def census():
    hist = {}
    count = pivots = 0
    for n in range(2,5):
        pairs = list(combinations(range(n),2))
        for labels in product((-1,0,1),repeat=len(pairs)):
            edges = [(u,v,p) for (u,v),p in zip(pairs,labels) if p != -1]
            if not edges:
                continue
            success,prob,weight,it = solve(n,edges)
            met = metrics(n,edges,balanced_period(n,prob))
            assert all(2*x == met['period'] for x in met['ones'])
            assert F(max(met['failures']),met['period']) == 1-success
            key = str(1-success)
            hist[key] = hist.get(key,0)+1
            count += 1
            pivots += it
    return dict(configurations=count,defect_histogram=hist,pivots=pivots)


if __name__ == '__main__':
    import json
    print(json.dumps(census(),sort_keys=True))
