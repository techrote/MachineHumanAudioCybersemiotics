"""Synthetic casting scores, no human or empirical claims. Python 3.11+."""
from collections import Counter
from itertools import permutations
from pathlib import Path
import hashlib
import json
import math
import struct
import wave


def cycles(p):
    seen = set()
    sizes = []
    for i in range(len(p)):
        if i in seen:
            continue
        j, size = i, 0
        while j not in seen:
            seen.add(j)
            j, size = p[j], size + 1
        sizes.append(size)
    return tuple(sorted(sizes))


def cast(p):
    n = len(p)
    ids = tuple(range(n))
    if sorted(p) != list(ids) or any(i == j for i, j in enumerate(p)):
        raise ValueError('expected a derangement')
    cols = [ids, p]
    while len(cols) < n:
        cols.append(next(q for q in permutations(ids)
                         if all(q[i] not in [c[i] for c in cols] for i in ids)))
    return tuple(zip(*cols))


def validate(rows):
    n = len(rows)
    ids = list(range(n))
    assert all(sorted(r) == ids for r in rows)
    assert all(sorted(c) == ids for c in zip(*rows))


def census():
    counts = {}
    for n in range(2, 8):
        types = Counter()
        for p in permutations(range(n)):
            if any(i == j for i, j in enumerate(p)):
                continue
            rows = cast(p)
            validate(rows)
            assert tuple(r[1] for r in rows) == p
            types[cycles(p)] += 1
        expected = sum((-1)**k * math.factorial(n)//math.factorial(k) for k in range(n+1))
        assert sum(types.values()) == expected
        counts[str(n)] = {str(k): v for k, v in sorted(types.items())}
        # A complete set of n-1 role-balanced blocks covers all ordered pairs.
        pairs = Counter()
        for d in range(1, n):
            offsets = [0, d] + [k for k in range(1, n) if k != d]
            rows = tuple(tuple((i+k)%n for k in offsets) for i in range(n))
            validate(rows)
            pairs.update((r[0], r[1]) for r in rows)
        assert pairs == Counter((i,j) for i in range(n) for j in range(n) if i != j)
    # Independent exhaustive row oracle for four performers.
    ps = tuple(permutations(range(4)))
    hist = Counter()
    for a in ps:
        for b in ps:
            if any(x == y for x,y in zip(a,b)):
                continue
            for c in ps:
                if any(z in (x,y) for x,y,z in zip(a,b,c)):
                    continue
                d = tuple(next(iter(set(range(4))-{x,y,z})) for x,y,z in zip(a,b,c))
                if len(set(d)) != 4:
                    continue
                rows = (a,b,c,d)
                validate(rows)
                p = dict((r[0],r[1]) for r in rows)
                hist[cycles(tuple(p[i] for i in range(4)))] += 1
    assert sum(hist.values()) == 576
    for bad in [(0,1), (1,1), (2,0)]:
        try:
            cast(bad)
        except ValueError:
            continue
        raise AssertionError('invalid cast accepted')
    return counts, {str(k):v for k,v in sorted(hist.items())}


def render(rows, path):
    validate(rows)
    rate, slot = 16000, 3200
    frames = bytearray()
    left = bytearray()
    for row in rows:
        for role, actor in enumerate(row):
            for j in range(slot):
                envelope = math.sin(math.pi*j/(slot-1))**2
                a = round(8000*envelope*math.sin(2*math.pi*(180+90*role)*j/rate))
                b = round(8000*envelope*math.sin(2*math.pi*(240+65*actor)*j/rate))
                frames.extend(struct.pack('<hh', a,b))
                left.extend(struct.pack('<h', a))
    with wave.open(str(path), 'wb') as w:
        w.setparams((2,2,rate,0,'NONE','not compressed'))
        w.writeframes(frames)
    with wave.open(str(path), 'rb') as w:
        assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (2,2,rate,len(rows)**2*slot)
        assert w.readframes(w.getnframes()) == frames
    return hashlib.sha256(path.read_bytes()).hexdigest(), hashlib.sha256(left).hexdigest()


def main():
    counts, hist = census()
    out = Path(__file__).resolve().parent/'audio'
    out.mkdir(exist_ok=True)
    receipt = {'derangements':counts,'four_actor_casts':hist,'editions':{}}
    lefts = set()
    for name, p in [('pairs',(1,0,3,2,5,4)),('triangles',(1,2,0,4,5,3)),('ring',(1,2,3,4,5,0))]:
        rows = cast(p)
        h, left = render(rows, out/(name+'.wav'))
        lefts.add(left)
        receipt['editions'][name] = {'rows':rows,'cycles':cycles(p),'wav_sha256':h,'role_pcm_sha256':left}
    assert len(lefts) == 1
    assert len({v['wav_sha256'] for v in receipt['editions'].values()}) == 3
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(receipt,sort_keys=True))


if __name__ == '__main__':
    main()
