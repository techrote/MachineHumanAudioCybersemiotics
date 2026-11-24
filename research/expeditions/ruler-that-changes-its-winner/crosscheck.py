#!/usr/bin/env python3
"""Independent implementation of the three-alternative census; Python standard library.
Run with python3 crosscheck.py. No source data or human outcomes are used.
"""
from itertools import permutations
from collections import Counter
from fractions import Fraction
import json

BALLOTS = list(permutations(range(3)))

def compositions(n, k):
    if k == 1:
        yield (n,)
        return
    for i in range(n + 1):
        for tail in compositions(n - i, k - 1):
            yield (i,) + tail

def run():
    rows = []
    first = None
    for n in range(1, 12):
        row = Counter(profiles=0, borda_excess=0)
        for c in compositions(n, 6):
            R = [(sum(c[k] for k, b in enumerate(BALLOTS) if b[0] == i),
                  n - sum(c[k] for k, b in enumerate(BALLOTS) if b[-1] == i))
                 for i in range(3)]
            M = [max(r[k] for r in R) for k in (0, 1)]
            L = [tuple(M[k] - r[k] for k in (0, 1)) for r in R]
            p = min(map(max, L))
            bs = [sum(r) for r in R]
            borda = [i for i in range(3) if bs[i] == max(bs)]
            row['profiles'] += 1
            if all(max(L[i]) > p for i in borda):
                row['borda_excess'] += 1
                if first is None:
                    first = dict(n=n, counts=c, R=R, L=L, pure=p, borda=borda)
            if n <= 10:
                row['no_robust_winner'] += bool(p)
                # Dual: uppermost point of the lower envelope of candidate lines.
                ts = {Fraction(0), Fraction(1)}
                for a in L:
                    for b in L:
                        den = a[0] - a[1] - b[0] + b[1]
                        if den:
                            t = Fraction(b[1] - a[1], den)
                            if 0 <= t <= 1:
                                ts.add(t)
                v = max(min(t * a + (1 - t) * b for a, b in L) for t in ts)
                assert v <= p <= 2 * v
                row['mixed_strictly_better'] += v < p
                row['sharp_factor_two'] += p > 0 and 2 * v == p
        rows.append(dict(voters=n, **row))
    total = Counter()
    for row in rows[:10]:
        total.update({k: v for k, v in row.items() if k != 'voters'})
    assert dict(total) == dict(profiles=8007, borda_excess=0, no_robust_winner=2700,
                               mixed_strictly_better=2670, sharp_factor_two=528)
    assert rows[-1]['profiles'] == 4368 and rows[-1]['borda_excess'] == 6
    assert first == dict(n=11, counts=(0,1,4,2,4,0), R=[(1,9),(6,6),(4,7)],
                         L=[(5,0),(0,3),(2,2)], pure=2, borda=[1])
    return dict(rows=rows, totals_through_ten=dict(total), first_borda_excess=first)

if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
