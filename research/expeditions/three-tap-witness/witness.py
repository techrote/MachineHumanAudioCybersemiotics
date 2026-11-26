"""Exact parity-balanced sparse FIR receipts. Python 3.11+, standard library."""
import hashlib
import itertools
import json
import math
import struct
import wave
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def signal(p, a, s):
    return [(-1)**(t % 2)*sum(si*ai*(pi-1 if t % pi == 0 else -1)
                             for pi, ai, si in zip(p, a, s))
            for t in range(2*math.prod(p))]


def filt(x, delays, weights):
    # Signed parity compensation; forward cyclic convention.
    h = [w*(-1)**(d % 2) for d, w in zip(delays, weights)]
    return [sum(w*x[(t+d) % len(x)] for d, w in zip(delays, h))
            for t in range(len(x))]


def energy(y):
    return Fraction(sum(v**6 for v in y), len(y))


def pair_probe(p, i, j, dc=False):
    d = math.prod(q for k, q in enumerate(p) if k not in (i, j))
    if dc:
        d *= 2
    return [0, d, 2*d], [1, 1, -2]


def calibration(p, a, i, j):
    q, r, A, B = p[i], p[j], a[i], a[j]
    k = 66*(q**5*A**6+r**5*B**6)+1620*(q**3*r*A**4*B**2+q*r**3*A**2*B**4)
    g = 720*q*q*r*r*A**3*B**3
    return k, g


def histogram(p, a, s, delays, weights):
    # Independent residue-bucket formulation, no cyclic signal construction.
    hist = Counter({0: 1})
    for q, A, sign in zip(p, a, s):
        buckets = [0]*q
        for d, w in zip(delays, weights):
            buckets[-d % q] += w
        h = Counter(sign*A*q*w for w in buckets)
        out = Counter()
        for u, n in hist.items():
            for v, m in h.items():
                out[u+v] += n*m
        hist = out
    out = Counter()
    for v, n in hist.items():
        out[v] += n
        out[-v] += n
    return out


def shortest(p, i, j):
    bound = pair_probe(p,i,j)[0][-1]
    for e in range(2,bound+1):
        for d in range(1,e):
            active = {k for k,q in enumerate(p) if d%q and e%q and (e-d)%q}
            if active == {i,j}:
                return [0,d,e]
    raise AssertionError("isolating probe must exist")


def general_calibration(p,a,ds,ws):
    moments=[]
    for q,A in zip(p,a):
        b=[0]*q
        for d,w in zip(ds,ws):
            b[-d%q]+=w
        moments.append({k:Fraction(sum((q*A*v)**k for v in b),q) for k in (2,3,4,6)})
    K=sum(v[6] for v in moments)
    for u,v in itertools.combinations(moments,2):
        K+=15*(u[4]*v[2]+u[2]*v[4])
    for u,v,w in itertools.combinations(moments,3):
        K+=90*u[2]*v[2]*w[2]
    return K,[v[3] for v in moments]


def audio(name, values, scale, rate):
    samples = [scale*v for v in values]
    assert max(map(abs, samples)) <= 32767
    raw = struct.pack('<'+'h'*len(samples), *samples)
    path = ROOT / (name+'.wav')
    with wave.open(str(path), 'wb') as f:
        f.setparams((1, 2, rate, len(samples), 'NONE', 'not compressed'))
        f.writeframes(raw)
    with wave.open(str(path), 'rb') as f:
        assert f.readframes(f.getnframes()) == raw
    return {'frames': len(samples), 'peak': max(map(abs, samples)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    counts = Counter()
    for p, a in [((3,5),(1,2)), ((5,7,11),(1,1,1)), ((3,5,7),(2,1,3))]:
        signs = [(1,)+s for s in itertools.product((1,-1), repeat=len(p)-1)]
        xs = [signal(p,a,s) for s in signs]
        for d in range(len(xs[0])):
            hs = [Counter(filt(x,[0,d],[1,-1])) for x in xs]
            assert all(h==hs[0] for h in hs)
            counts['two_tap_histogram_profiles'] += 1
        for i,j in itertools.combinations(range(len(p)),2):
            k,g = calibration(p,a,i,j)
            for dc in (False, True):
                ds,ws = pair_probe(p,i,j,dc)
                for s,x in zip(signs,xs):
                    y = filt(x,ds,ws)
                    assert energy(y)==k+g*s[i]*s[j]
                    assert Counter(y)==histogram(p,a,s,ds,ws)
                    counts['pair_probe_checks'] += 1
        # arbitrary balanced three-tap probes, with deliberate residue collisions
        for d,e in itertools.product(range(1,9),repeat=2):
            for s,x in zip(signs,xs):
                ds,ws=[0,d,e],[2,1,-3]
                assert Counter(filt(x,ds,ws))==histogram(p,a,s,ds,ws)
                counts['general_histogram_checks'] += 1
    p=(5,7,11,13,17); a=(1,)*5
    s=(1,1,1,-1,1); t=(1,1,1,-1,-1)
    x,z=signal(p,a,s),signal(p,a,t)
    assert energy(x)==energy(z)
    ds,ws=pair_probe(p,0,4)
    k,g=calibration(p,a,0,4)
    assert energy(filt(x,ds,ws))==k+g
    assert energy(filt(z,ds,ws))==k-g
    collision={'raw_moment':str(energy(x)), 'delay_span':ds[-1],
               'pair_energy':[k+g,k-g], 'period':len(x)}
    spans=[]
    for i,j in itertools.combinations(range(len(p)),2):
        short=shortest(p,i,j)
        K,G=general_calibration(p,a,short,ws)
        assert {k for k,v in enumerate(G) if v}=={i,j}
        for tail in itertools.product((1,-1),repeat=4):
            signs=(1,)+tail
            h=histogram(p,a,signs,short,ws)
            E=Fraction(sum(n*v**6 for v,n in h.items()),sum(h.values()))
            assert E==K+20*G[i]*G[j]*signs[i]*signs[j]
            counts['short_probe_class_checks']+=1
        spans.append({'pair':[p[i],p[j]],'delays':short,
                      'isolating_span':pair_probe(p,i,j)[0][-1]})
    short=shortest(p,0,4)
    K,G=general_calibration(p,a,short,ws)
    E=[energy(filt(v,short,ws)) for v in (x,z)]
    assert E==[K+20*G[0]*G[4],K-20*G[0]*G[4]]
    collision['short_delays']=short
    collision['short_energy']=[int(v) for v in E]
    # Exhaustive spanning-tree enumeration on the five-component fixture.
    trees=[]
    for edges in itertools.combinations(spans,4):
        reached={p[0]}
        for _ in p:
            for edge in edges:
                if reached.intersection(edge['pair']): reached.update(edge['pair'])
        if len(reached)==len(p):
            trees.append((sum(e['delays'][-1] for e in edges),[e['pair'] for e in edges]))
    assert len(trees)==125
    tree=min(trees)
    assert tree[0]==87
    # Small audible witness: only the p=5 and p=7 components survive.
    p=(5,7,11); a=(1,1,1); ds,ws=pair_probe(p,0,1)
    k,g=calibration(p,a,0,1)
    records={}
    for label,s in [('plus',(1,1,1)),('minus',(1,-1,1))]:
        x=signal(p,a,s); y=filt(x,ds,ws)
        records['raw-'+label]=audio('raw-'+label,x*20,1000,15400)
        records['cubic-'+label]=audio('cubic-'+label,[v**3 for v in y]*20,1,15400)
    result={'counts':dict(counts),'collision':collision,'audio':records,
            'small_pair':{'delays':ds,'baseline':k,'half_gap':g,'energy':[k+g,k-g]},
            'short_spans':spans,'short_tree':tree,'trees_checked':len(trees),
            'status':'PASS','assertion_failures':0}
    (ROOT/'native-execution.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':
    run()
