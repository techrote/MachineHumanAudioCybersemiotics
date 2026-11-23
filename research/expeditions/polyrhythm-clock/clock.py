"""Synthetic cyclic pulse scheduling; Python 3.11+, standard library."""
from itertools import combinations
from math import gcd, sin, pi
from pathlib import Path
import argparse, json, struct, wave


def mechanical(q, p, phase=0):
    if not 0 <= p <= q or q < 1:
        raise ValueError('require 0 <= p <= q and q >= 1')
    return tuple(((i+1)*p+phase)//q-(i*p+phase)//q for i in range(q))


def discrepancy(word):
    """q times maximum absolute error over every cyclic interval."""
    q, p = len(word), sum(word)
    if not q or any(x not in (0, 1) for x in word):
        raise ValueError('nonempty binary word required')
    e = lo = hi = 0
    for x in word:
        e += q*x-p
        lo, hi = min(lo, e), max(hi, e)
    return hi-lo


def words(q, p):
    for indices in combinations(range(q), p):
        mask = sum(1 << i for i in indices)
        word = tuple((mask >> i)&1 for i in range(q))
        yield mask, word, discrepancy(word)


def solve(q, p, r):
    """Exact joint Pareto front: (overlap, excess_A, excess_B).

    Exhaustive search, limited to small periods. Excess is measured in units
    of 1/q of a pulse relative to the individual optimal discrepancy.
    """
    if not 1 <= p <= r or p+r > q or q > 12:
        raise ValueError('require 1 <= p <= r, p+r <= q <= 12')
    bases = (q-gcd(q,p), q-gcd(q,r))
    a, b = list(words(q,p)), list(words(q,r))
    points = {}
    for am, aw, ad in a:
        for bm, bw, bd in b:
            key = ((am&bm).bit_count(), ad-bases[0], bd-bases[1])
            points.setdefault(key, (aw,bw))
    front = [k for k in sorted(points) if not any(
        h != k and all(x <= y for x,y in zip(h,k)) for h in points)]
    best = min((k for k in points if k[0]==0),
               key=lambda k:(max(k[1:]),sum(k[1:]),k))
    return {'q':q,'p':p,'r':r,'individual_bounds':bases,
            'pairs_examined':len(a)*len(b),
            'min_overlap_at_individual_optima':min(k[0] for k in points if k[1:]==(0,0)),
            'best_disjoint':{'point':best,'words':points[best]},
            'front':[{'point':k,'words':points[k]} for k in front]}


def census(max_q=10):
    return [solve(q,p,r) for q in range(2,max_q+1)
            for p in range(1,q//2+1) for r in range(p,q-p+1)]


def render(path, left, right, repeats=6, rate=22050):
    """Original stereo pulse score; fixed 120 ms slot, 70 ms decaying sine."""
    slot = rate*120//1000
    decay = rate*70//1000
    frames = bytearray()
    for a,b in zip(left*repeats,right*repeats):
        for n in range(slot):
            env = (1-n/decay)**2 if n<decay else 0
            l = round(9000*a*env*sin(2*pi*440*n/rate))
            r = round(9000*b*env*sin(2*pi*660*n/rate))
            frames.extend(struct.pack('<hh',l,r))
    with wave.open(str(path),'wb') as w:
        w.setparams((2,2,rate,0,'NONE','not compressed'))
        w.writeframes(frames)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path('clock-output'))
    parser.add_argument('--max-q',type=int,default=10,choices=range(2,11))
    args=parser.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    rows=census(args.max_q)
    witness=solve(6,2,3)
    original=next(x for x in witness['front'] if x['point'][1:]==(0,0))
    render(args.out/'independently-even.wav',*original['words'])
    render(args.out/'collision-free.wav',*witness['best_disjoint']['words'])
    result={'schema':'synthetic-clock-v1','cases':rows,'witness':witness,
            'summary':{'cases':len(rows),'pairs':sum(x['pairs_examined'] for x in rows),
            'obstructed':sum(x['min_overlap_at_individual_optima']>0 for x in rows)}}
    (args.out/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result['summary'],sort_keys=True))
    print(json.dumps(witness,sort_keys=True))

if __name__=='__main__':
    main()
