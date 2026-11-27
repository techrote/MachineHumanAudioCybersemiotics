"""Synthetic direct-arrival score, not room acoustics or perception."""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math
import struct
import wave
import sys


def arrival(x, t, p):
    return t + abs(p - x)


def crossing(x, t, y, u):
    if not x < y or abs(u-t) >= y-x:
        raise ValueError('no unique interior reversal')
    return F(x+y+u-t, 2)


def boundaries(xs, ts):
    return {(i,j): crossing(xs[i],ts[i],xs[j],ts[j])
            for i,j in combinations(range(len(xs)),2)}


def order(xs, ts, p):
    return tuple(sorted(range(len(xs)), key=lambda i: (arrival(xs[i],ts[i],p),i)))


def qualify():
    cases = comparisons = 0
    census = {}
    for b,c in combinations(range(1,9),2):
        xs = (0,b,c)
        for u,v in product(range(-8,9),repeat=2):
            ts = (0,u,v)
            if any(abs(ts[j]-ts[i]) >= xs[j]-xs[i] for i,j in combinations(range(3),2)):
                continue
            z = boundaries(xs,ts)
            assert z[0,1]+z[1,2]-z[0,2] == b
            cuts = [-1,*sorted(set(z.values())),c+1]
            orders = set()
            for left,right in zip(cuts,cuts[1:]):
                p = (F(left)+right)/2
                orders.add(order(xs,ts,p))
                for (i,j),q in z.items():
                    assert (arrival(xs[i],ts[i],p) < arrival(xs[j],ts[j],p)) == (p<q)
                    comparisons += 1
            for (i,j),q in z.items():
                assert xs[i]<q<xs[j]
                assert arrival(xs[i],ts[i],q)==arrival(xs[j],ts[j],q)
            assert len(orders)==len(set(z.values()))+1
            census[len(orders)] = census.get(len(orders),0)+1
            cases += 1
    # A simultaneous-emission family realizes all pair crossings distinctly.
    for n in range(2,9):
        xs = tuple(2**i for i in range(n))
        ts = (0,)*n
        cuts = [F(0),*sorted(set(boundaries(xs,ts).values())),F(xs[-1]+1)]
        assert len(cuts)-1 == n*(n-1)//2+1
        assert len({order(xs,ts,(a+b)/2) for a,b in zip(cuts,cuts[1:])}) == len(cuts)-1
    # Equality is a plateau, not an interior reversal; beyond it, no tie.
    for delta in (-5,-4,4,5):
        try:
            crossing(0,0,4,delta)
        except ValueError:
            pass
        else:
            raise AssertionError('degenerate crossing accepted')
    assert arrival(0,0,9)==arrival(4,4,9)
    assert F(4)+F(24)-F(17)!=12  # impossible requested triple
    return {'triples':cases,'strict_pair_comparisons':comparisons,'order_census':census}


RATE=16000
TICK=160  # 10 ms; spatial coordinate is expressed in propagation-time ticks
XS=(0,12,31)
TS=(3,0,5)
FREQ=(220,330,495)


def render(path,p):
    starts=[arrival(x,t,p)*TICK for x,t in zip(XS,TS)]
    assert all(F(s).denominator==1 for s in starts)
    starts=list(map(int,starts))
    # Four repetitions; identical emission schedule at every virtual seat.
    data=[0]*(RATE*3)
    length=RATE*7//100
    for rep in range(4):
        for i,start in enumerate(starts):
            for k in range(length):
                t=k/RATE
                sample=round(4200*math.sin(2*math.pi*FREQ[i]*t)*math.sin(math.pi*k/(length-1))**2)
                data[rep*RATE*7//10+start+k]+=sample
    assert max(map(abs,data))<=12600
    pcm=struct.pack('<'+'h'*len(data),*data)
    with wave.open(str(path),'wb') as w:
        w.setparams((1,2,RATE,0,'NONE','not compressed'))
        w.writeframes(pcm)
    with wave.open(str(path),'rb') as w:
        assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,RATE,len(data))
        assert w.readframes(len(data))==pcm
    return {'position':str(p),'starts_samples':starts,'order':''.join('ABC'[i] for i in order(XS,TS,p)),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    out=Path(sys.argv[1] if len(sys.argv)>1 else 'audio')
    out.mkdir(parents=True,exist_ok=True)
    results=qualify()
    scores={name:render(out/(name+'.wav'),p) for name,p in
            [('west',0),('west-middle',10),('east-middle',20),('east',31),('ab-tie',F(9,2))]}
    assert [scores[n]['order'] for n in ('west','west-middle','east-middle','east')]==['ABC','BAC','BCA','CBA']
    assert scores['ab-tie']['starts_samples'][0]==scores['ab-tie']['starts_samples'][1]
    assert len({s['sha256'] for s in scores.values()})==5
    receipt={'python':sys.version.split()[0],**results,'scores':scores,'qualification':'PASS'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(receipt,sort_keys=True))


if __name__=='__main__':
    main()
