"""Independent small-hyperperiod oracle and original pulse sonification."""
from collections import Counter
from itertools import combinations_with_replacement, combinations, product
from math import gcd, lcm, ceil, sin, pi
from pathlib import Path
from fractions import Fraction
import hashlib, json, struct, wave

ROOT = Path(__file__).resolve().parent


def oracle(periods):
    h = lcm(*periods)
    masks = [[sum(1 << t for t in range(r, h, p)) for r in range(p)] for p in periods]
    best = len(periods)
    for tail in product(*masks[1:]):
        layers = [0] * len(periods)
        for mask in (masks[0][0], *tail):
            for i in range(len(layers)-1, 0, -1):
                layers[i] |= layers[i-1] & mask
            layers[0] |= mask
        best = min(best, sum(bool(x) for x in layers))
    return best


def family_formula(periods):
    counts = Counter(periods)
    distinct = sorted(counts)
    common = {gcd(a, b) for a, b in combinations(distinct, 2)}
    if len(common) > 1:
        return None
    g = next(iter(common), distinct[0])
    return ceil(Fraction(sum(ceil(Fraction(m, p//g)) for p, m in counts.items()), g))


def timeline(periods, offsets):
    return [tuple(i for i, (p, r) in enumerate(zip(periods, offsets)) if t % p == r)
            for t in range(lcm(*periods))]


def render(periods, left, right, name, ticks, tick_samples=800):
    rate = 16000
    channels = []
    stats = []
    for offsets in (left, right):
        peaks = [sum(t % p == r for p, r in zip(periods, offsets)) for t in range(ticks)]
        samples = []
        for t in range(ticks):
            active = [i for i,(p,r) in enumerate(zip(periods, offsets)) if t%p==r]
            for j in range(tick_samples):
                # Each tick contains a short, independently pitched raised-cosine pulse.
                env = sin(pi*j/(tick_samples-1))**2
                samples.append(round(26000/len(periods)*env*sum(sin(2*pi*(300+100*i)*j/rate) for i in active)))
        channels.append(samples)
        stats.append(dict(peak_concurrency=max(peaks), events=sum(peaks), max_abs_pcm=max(map(abs,samples)), histogram=dict(sorted(Counter(peaks).items()))))
    path = ROOT/name
    with wave.open(str(path), 'wb') as f:
        f.setparams((2,2,rate,0,'NONE','not compressed'))
        f.writeframes(b''.join(struct.pack('<hh',a,b) for a,b in zip(*channels)))
    return dict(file=name, seconds=ticks*tick_samples/rate, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), channels=stats)


def main():
    hist=Counter(); cases=0; outside=0
    for n in range(1,6):
        for periods in combinations_with_replacement(range(1,8),n):
            expected=family_formula(periods)
            if expected is None:
                outside+=1; continue
            actual=oracle(periods)
            assert actual==expected,(periods,actual,expected)
            cases+=1; hist[actual]+=1
    assert cases==497 and outside==294
    assert dict(sorted(hist.items()))=={1:42,2:154,3:178,4:95,5:28}
    # Nonconstant pairwise gcd: global gcd 1 does NOT imply peak 3.
    assert family_formula((6,10,15)) is None
    assert max(map(len,timeline((6,10,15),(0,1,2))))==1
    assert oracle((6,10,15))==1
    # Pairwise feasible, collectively impossible at capacity 1.
    assert all(oracle(pair)==1 for pair in combinations((6,10,14),2))
    assert oracle((6,10,14))==2
    # Finite prefix: 0 mod 101 and 1 mod 103 first meet at 5151.
    assert [t for t in range(10403) if t%101==0 and t%103==1]==[5151]
    # Multiplicity groups require ceil(m_i/a_i) chunks, not one per voice.
    p=(4,4,4,4,4,6,6,6,6)
    offsets=(0,2,1,3,0,1,3,5,0)
    # Here optimum = ceil((ceil(5/2)+ceil(4/3))/2)=3.
    assert family_formula(p)==3
    assert max(map(len,timeline(p,offsets)))==3
    audio=[render((6,10,14),(0,0,0),(0,1,0),'rigid-voices.wav',210),
           render((6,10,15),(0,0,0),(0,1,2),'gcd-geometry.wav',60)]
    receipt=dict(cases=cases,outside=outside,histogram=dict(sorted(hist.items())),audio=audio)
    (ROOT/'independent.synthetic.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': main()
