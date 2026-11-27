"""Independent modular rank cross-check from literal periodic contrasts.

Python standard library only. Does not use the recurrence coefficients.
A full-rank modular minor certifies full rank over the rationals; a zero
modular minor alone is not proof of a rational dependence.
"""
import itertools as it
import json
from fractions import Fraction as F

P = (5, 7, 11, 13, 17)
D = sum(p - 1 for p in P)
MOD = 1000000007


def design(t):
    return [int(t % p == r) - int(t % p == p-1)
            for p in P for r in range(p-1)]


def inverse(a, field=None):
    n = len(a)
    conv = (lambda x: x % field) if field else F
    b = [[conv(x) for x in row + [int(i == j) for j in range(n)]]
         for i, row in enumerate(a)]
    for j in range(n):
        k = next(i for i in range(j, n) if b[i][j])
        b[j], b[k] = b[k], b[j]
        scale = pow(b[j][j], -1, field) if field else 1 / b[j][j]
        b[j] = [conv(x * scale) for x in b[j]]
        for i in range(n):
            if i != j and b[i][j]:
                aij = b[i][j]
                b[i] = [conv(x - aij*y) for x, y in zip(b[i], b[j])]
    return [row[n:] for row in b]


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def systematic(r, inv):
    rows = []
    for j in range(r):
        a = design(D+j)
        rows.append([(-dot(a, col)) % MOD for col in zip(*inv)]
                    + [int(i == j) for i in range(r)])
    for row in rows:
        assert all(dot(row, c) % MOD == 0
                   for c in zip(*(design(t) for t in range(D+r))))
    return list(zip(*rows))


def determinant(columns):
    a = [list(row) for row in zip(*columns)]
    n, sign = len(a), 1
    for j in range(n):
        k = next((i for i in range(j,n) if a[i][j]), None)
        if k is None:
            return 0
        if k != j:
            a[k], a[j] = a[j], a[k]
            sign = -sign
        p = a[j][j]
        for i in range(j+1,n):
            x = a[i][j]
            a[i] = [(p*u - x*v) % MOD for u,v in zip(a[i],a[j])]
    # Only zero/nonzero is needed: elimination scales rows by nonzero pivots.
    return sign


def run():
    a = [design(t) for t in range(D)]
    inv = inverse(a, MOD)
    exact_inv = inverse(a)
    profiles = []
    for r in (1,2,3,4):
        h = systematic(r, inv)
        bad, checked = [], 0
        for I in it.combinations(range(D+r), r):
            checked += 1
            if not determinant([h[i] for i in I]):
                bad.append(list(I))
        profiles.append(dict(rows=r, checked=checked, zero_modular_minors=bad))
    expected = [[1,4,5,6],[2,4,5,9],[42,46,47,49],[45,46,47,50]]
    assert all(not p['zero_modular_minors'] for p in profiles[:3])
    assert profiles[3]['zero_modular_minors'] == expected
    h5 = systematic(5, inv)
    for I in expected:
        assert any(determinant([[h5[i][j] for j in J] for i in I])
                   for J in it.combinations(range(5),4))
    specs = [(47,[47],[1]),(48,[0],[1]),(49,[0,1],[5,-1]),
             (50,[0,1,2],[10,-5,1]),(52,expected[0],[-5,7,-7,2])]
    exact = []
    for L,I,v in specs:
        h = [0]*max(D,L)
        for i,x in zip(I,v):
            h[i] = x
        coeff = [dot(row,h[:D]) for row in exact_inv]
        assert all(dot(design(t),coeff) == x for t,x in enumerate(h))
        # Integrate each zero-sum periodic contrast separately, yielding a
        # rational/integer periodic primitive with the prescribed difference.
        tables, start = [], 0
        for p in P:
            g = coeff[start:start+p-1]
            g = g + [-sum(g)]
            f = [F(0)]
            for x in g[:-1]:
                f.append(f[-1]+x)
            assert f[0]-f[-1] == g[-1]
            tables.append(f)
            start += p-1
        y = lambda t: sum(f[t % len(f)] for f in tables)
        assert all(y(t+1)-y(t) == x for t,x in enumerate(h))
        exact.append(dict(separation=L, primitive_tables=[[str(x) for x in f] for f in tables]))
    return dict(dimension=D, field=MOD, profiles=profiles,
                exceptional_supports_repaired_at_53=4, exact_periodic_primitives=exact,
                assertions='pass')


if __name__ == '__main__':
    print(json.dumps(run(),indent=2))
