"""Full labelled-state LP cross-check and deterministic original PCM score."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, product
from math import comb, cos, pi, sin
from pathlib import Path
import hashlib, json, random, struct, wave
import numpy as np
import scipy
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parent

def corners(n, k):
    cap = F(1, n + n % 2)
    if n == 2:
        return [(F(1, 4), F(1, 4))]
    if n == 3:
        return [(0, cap), (cap, 0)] if k == 2 else [(cap/2, cap/2)]
    c = (F(1, n+1 if n%2 else n+2) if k == 2 else
         F(n-2, 2*(n-1)*(n+1)) if n%2 else F(n-4, 2*(n-1)*(n-2)))
    return [(0, 0), (cap/2, cap/2), (c, 0), (0, c)]

def lp_checks():
    checks = 0
    error = 0.0
    for n in range(2, 9):
        words = list(product((0, 1), repeat=n))
        for k in range(2, min(3, n)+1):
            subsets = [s for j in range(k+1) for s in combinations(range(n), j)]
            A = np.array([[int(all(w[i] for i in s)) for w in words] for s in subsets])
            rhs = [2.0**(-len(s)) for s in subsets]
            for a, b in product(range(-2, 3), repeat=2):
                if not (a or b):
                    continue
                c = np.zeros(len(words)); c[0] = -a; c[-1] = -b
                res = linprog(c, A_eq=A, b_eq=rhs, bounds=(0, None), method='highs')
                assert res.success, res.message
                expected = max(a*x+b*y for x,y in corners(n,k))
                diff = abs(-res.fun-float(expected))
                assert diff < 1e-8, (n,k,a,b,diff)
                error = max(error, diff); checks += 1
    return checks, error

def score(mass):
    frames = []
    for w in product((0, 1), repeat=6):
        count = 120*mass.get(sum(w), F(0))/comb(6,sum(w))
        assert count.denominator == 1
        frames.extend([w]*int(count))
    assert len(frames)==120
    random.Random(420).shuffle(frames)
    return frames

def audit(frames, k):
    count = 0
    for j in range(1,k+1):
        for s in combinations(range(6),j):
            hist = Counter(tuple(w[i] for i in s) for w in frames)
            assert hist == {w:120//(2**j) for w in product((0,1), repeat=j)}
            count += 2**j
    return count

def render(name, frames):
    path = ROOT / (name+'.wav')
    n = 640; sr = 8000
    bank = [[sin(pi*t/(n-1))**2*cos(2*pi*f*t/sr) for t in range(n)]
            for f in (250,350,450,550,650,750)]
    data = b''.join(struct.pack('<h', round(4000*sum(bank[i][t] for i in range(6) if w[i])))
                    for w in frames for t in range(n))
    with wave.open(str(path), 'wb') as f:
        f.setparams((1,2,sr,0,'NONE','not compressed')); f.writeframes(data)
    return {'count_histogram': dict(sorted(Counter(map(sum,frames)).items())),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'frames':len(frames)}

def main():
    checks, err = lp_checks()
    a = score({2:F(3,8),3:F(1,2),6:F(1,8)})
    b = score({1:F(1,5),3:F(1,2),4:F(1,4),6:F(1,20)})
    c = [tuple(1-x for x in w) for w in b]
    d = score({0:F(1,12),3:F(5,6),6:F(1,12)})
    n = sum(audit(w,k) for w,k in [(a,2),(b,3),(c,3),(d,3)])
    result = {'python': __import__('sys').version.split()[0], 'scipy':scipy.__version__,
              'labelled_lp_checks':checks, 'max_abs_error':err, 'literal_marginal_cells':n,
              'audio':{name:render(name,w) for name,w in [('pairwise-tutti',a),('triple-tutti',b),('triple-silence',c),('triple-balanced',d)]}}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
