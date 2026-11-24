"""Independent numerical LP, exhaustive short-period oracle and original PCM."""
import argparse
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import wave
import struct
from dither import solve, cycle_edges, moving_defect, metrics, balanced_period, census


def oracle(n, edges):
    # Primal probability LP, not the dual cover simplex used by dither.py.
    from scipy.optimize import linprog
    words = list(product((0,1),repeat=n))
    a = [[int((word[u]^word[v]) == p) for word in words] for u,v,p in edges]
    k = len(words)
    res = linprog([0]*k+[-1], A_ub=[[-x for x in row]+[1] for row in a],
                  b_ub=[0]*len(edges), A_eq=[[1]*k+[0]],b_eq=[1],bounds=(0,None),method='highs')
    if not res.success:
        raise RuntimeError(res.message)
    return res.x[-1]


def short_period_exists(parity,t):
    # Each column is an exactly half-one bitword over time. Work along cycle.
    n = len(parity)
    cols = [sum(1<<i for i in c) for c in combinations(range(t),t//2)]
    def good(a,b,p):
        h = (a^b).bit_count()
        return n*(t-h if p else h) <= t
    # By frame permutation we may fix the first column to the first balanced word.
    def walk(path):
        if len(path) == n:
            return good(path[-1],path[0],parity[-1])
        return any(walk(path+[c]) for c in cols if good(path[-1],c,parity[len(path)-1]))
    return walk([cols[0]])


def audio(out):
    rate,block,n = 16000,1600,7
    edges = cycle_edges([1]*n)
    moving = moving_defect([1]*n)
    full = (1<<n)-1
    fixed = [moving[0]^(full if i%2 else 0) for i in range(2*n)]
    def write(name,edge_ids):
        # x_u+x_v-1 is exactly the sum residual of rounding two half-LSBs.
        frames = bytearray()
        nonzero = [0,0]
        for a,b in zip(fixed,moving):
            for j in range(block):
                samples = []
                for ch,s in enumerate((a,b)):
                    value = 0
                    for e in edge_ids:
                        u,v,_ = edges[e]
                        error = (s>>u&1)+(s>>v&1)-1
                        # Distinct integer triangular carriers; common taper.
                        period = [80,64,50,40,32,25,20][e]
                        phase = j%period
                        carrier = period-4*min(phase,period-phase)
                        value += error*carrier*10000//period
                    value = value*min(j,block-1-j,80)//80
                    assert -32768 <= value <= 32767
                    nonzero[ch] += value != 0
                    samples.append(value)
                frames.extend(struct.pack('<hh',*samples))
        path = out/name
        with wave.open(str(path),'wb') as w:
            w.setparams((2,2,rate,0,'NONE','not compressed'))
            w.writeframes(frames)
        return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),nonzero_samples=nonzero,frames=len(frames)//4)
    return dict(target_edge=write('target-edge.wav',[n-1]),edge_bank=write('walking-defect.wav',list(range(n))),fixed=metrics(n,edges,fixed),moving=metrics(n,edges,moving))


def main(out):
    out.mkdir(parents=True,exist_ok=True)
    result = census()
    max_gap = 0.0
    count = 0
    for n in range(2,6):
        pairs = list(combinations(range(n),2))
        # All signed simple graphs through 4; all unsigned simple graphs at 5.
        for labels in product((-1,0,1) if n<5 else (-1,1),repeat=len(pairs)):
            edges = [(u,v,p) for (u,v),p in zip(pairs,labels) if p!=-1]
            if not edges:
                continue
            success,prob,_,_ = solve(n,edges)
            gap = abs(float(success)-oracle(n,edges))
            assert gap < 1e-8
            max_gap = max(max_gap,gap)
            count += 1
    result.update(lp_checks=count,max_lp_gap=max_gap)
    cycles = 0
    for n in range(3,11):
        for parity in product((0,1),repeat=n):
            if sum(parity)%2 == 0:
                continue
            edges = cycle_edges(parity)
            s = moving_defect(parity)
            met = metrics(n,edges,s)
            assert met == dict(period=2*n,ones=[n]*n,failures=[2]*n,switches=2*n,peak_switch=1)
            cycles += 1
    result['moving_cycle_checks'] = cycles
    short = 0
    for n in (3,4):
        for parity in product((0,1),repeat=n):
            if sum(parity)%2 == 0:
                continue
            for t in range(2,2*n+1,2):
                assert short_period_exists(parity,t) == (t==2*n)
                short += 1
    result['short_period_checks'] = short
    # Weighted-average success and worst-edge success disagree on triangle + leaves.
    edges = [(0,1,1),(0,2,1),(1,2,1)]+[(0,i,1) for i in range(3,8)]
    success,prob,weight,_ = solve(8,edges)
    assert success==F(2,3)
    result['triangle_with_leaves'] = dict(fair_defect=str(1-success),min_aggregate_defect='1/8')
    result['audio'] = audio(out)
    (out/'results.synthetic.txt').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=Path('run'))
    main(parser.parse_args().out)
