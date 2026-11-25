"""Exact size-chain cross-check and original PCM scores for MHAC #480."""
from fractions import Fraction as F
from math import comb, sin, pi
from itertools import combinations
from pathlib import Path
import hashlib
import json
import struct
import wave


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def profiles(m, d):
    if m == 0:
        yield (d,)
    else:
        for k in range(d+1):
            for rest in profiles(m-1, d-k):
                yield (k,) + rest


def advance(dist, w):
    m, d = len(w)-1, sum(w)
    return [sum((dist[s]*F(w[k]*choose(s,j)*choose(m-s,k-j), d*comb(m,k))
                 for s in range(m+1) for k in range(m+1) if w[k]), F(0))
            for j in range(m+1)]


def inversion(w, t):
    m, d = len(w)-1, sum(w)
    p = [sum((F(w[k]*choose(k,j), d*comb(m,j)) for k in range(m+1)), F(0))
         for j in range(m+1)]
    return [comb(m,l)*sum(((-1)**(j-l)*comb(m-l,j-l)*p[j]**t
                           for j in range(l,m+1)), F(0)) for l in range(m+1)]


def stoploss(dist, z):
    return sum(v*max(j-z,0) for j,v in enumerate(dist))


def verify():
    checks = dict(histograms=0, convex=0, parity=0)
    for m in range(1,6):
        for w in profiles(m,3):
            d = sum(w)
            q = sum(k*v for k,v in enumerate(w))
            b, e = [0]*(m+1), [0]*(m+1)
            lo, rem = divmod(q,d)
            b[lo] = d-rem
            if rem:
                b[lo+1] = rem
            e[0], e[m] = m*d-q, q
            a = x = y = [F(0)]*m+[F(1)]
            for t in range(1,5):
                a,x,y = advance(a,w),advance(x,b),advance(y,e)
                assert a == inversion(w,t)
                checks['histograms'] += 1
                for z in range(m+1):
                    assert stoploss(x,z) <= stoploss(a,z) <= stoploss(y,z)
                    checks['convex'] += 2
    # All proper-support inclusion moments coincide, even after independent draws.
    for m in range(2,9):
        a = [comb(m,k) if (m-k)%2==0 else 0 for k in range(m+1)]
        b = [comb(m,k) if (m-k)%2==1 else 0 for k in range(m+1)]
        A = 2**(m-1)
        for t in range(1,7):
            x,y = inversion(a,t), inversion(b,t)
            for l in range(m+1):
                assert x[l]-y[l] == F((-1)**(m-l)*comb(m,l),A**t)
                checks['parity'] += 1
    # Fano-plane nonexchangeable counterexample to balanced extremality.
    lines = {frozenset((a,b,a^b)) for a,b in combinations(range(1,8),2)}
    assert len(lines)==7 and all(sum(i in s for s in lines)==3 for i in range(1,8))
    assert all(a & b for a in lines for b in lines)
    assert inversion([0,0,0,1,0,0,0,0],2)[0] == F(4,35)
    return checks


def render(out):
    scores = {
        'burst': [(0,), (0,1,2,3,4), (0,), (0,1,2,3,4)],
        'balanced': [(0,1,2), (0,1,3), (0,3,4), (0,2,4)],
        'replay': [(0,1,2)]*4,
    }
    result = {}
    for name, score in scores.items():
        remaining = set(range(5))
        trail = []
        pcm = []
        for chord in score:
            remaining.intersection_update(chord)
            trail.append(sorted(remaining))
            for j in range(2400):
                envelope = sin(pi*j/2399)**2
                sample = sum(sin(2*pi*(200+100*k)*j/8000) for k in chord)
                pcm.append(round(4000*envelope*sample))
            pcm.extend([0]*800)
        path = out/(name+'.wav')
        with wave.open(str(path),'wb') as f:
            f.setparams((1,2,8000,0,'NONE','not compressed'))
            f.writeframes(struct.pack('<'+'h'*len(pcm),*pcm))
        result[name] = {'report_sets':score, 'intersection_trail':trail,
                        'counts':[sum(k in c for c in score) for k in range(5)],
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    assert result['burst']['counts']==result['balanced']['counts']==[4,2,2,2,2]
    return result


if __name__ == '__main__':
    import sys
    out = Path(sys.argv[1] if len(sys.argv)>1 else 'results')
    out.mkdir(parents=True,exist_ok=True)
    print(json.dumps({'checks':verify(),'audio':render(out),'status':'PASS'},indent=2))
