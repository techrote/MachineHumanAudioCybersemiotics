"""Finite authored stopping frontiers and original PCM studies; no human data."""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib
import json
import math
import struct
import sys
import wave


@lru_cache(None)
def frontiers(d):
    if not d:
        return (('',),)
    return (('',),) + tuple(tuple('0'+p for p in a)+tuple('1'+p for p in b)
                           for a in frontiers(d-1) for b in frontiers(d-1))


def leaves(d):
    return tuple(''.join(p) for p in product('01', repeat=d))


def partitions(d):
    # Independent exhaustive decision masks over every internal node.
    nodes = tuple(p for j in range(d) for p in leaves(j))
    index = {p:i for i,p in enumerate(nodes)}
    result = set()
    for mask in range(1 << len(nodes)):
        cut = set()
        for w in leaves(d):
            p = next((w[:j] for j in range(d) if not mask & (1 << index[w[:j]])), w)
            cut.add(p)
        result.add(tuple(sorted(cut)))
    return result


def metrics(f, d):
    counts = Counter()
    for w in leaves(d):
        hits = [p for p in f if w.startswith(p)]
        assert len(hits) == 1
        counts[hits[0]] += 1
    assert counts == {p:2**(d-len(p)) for p in f}
    mean = sum(Fraction(len(p)*c, 2**d) for p,c in counts.items())
    remaining = sum(Fraction((d-len(p))*c, 2**d) for p,c in counts.items())
    assert mean + remaining == d
    assert sum(Fraction(1, 2**len(p)) for p in f) == 1
    return mean, max(counts.values())


def qualify():
    rows = []
    for d in range(5):
        fs = frontiers(d)
        assert len(fs) == len(set(fs))
        assert set(fs) == partitions(d)
        by_k = defaultdict(list)
        for f in fs:
            by_k[len(f)].append(metrics(f,d))
        for k, vals in by_k.items():
            h = k.bit_length()-1
            assert max(v[0] for v in vals) == h + Fraction(k-2**h,2**h)
            assert min(v[1] for v in vals) == 2**(d-h)
        rows.append({'depth':d,'frontiers':len(fs),'terminal_counts':len(by_k),
                     'decision_masks':2**(2**d-1)})
    flat = leaves(2)
    uneven = ('0','100','101','110','111')
    assert metrics(flat,4) == (2,4)
    assert metrics(uneven,4) == (2,8)
    return rows


RATE, CELL = 16000, 2400


def tile(prefix):
    # A node has a persistent pitch; envelopes are fully contained in its cell.
    freq = 175 + 47*len(prefix) + 29*int(prefix,2)
    return tuple(round(11000*math.sin(2*math.pi*freq*i/RATE)*math.sin(math.pi*i/(CELL-1))**2)
                 for i in range(CELL))


def render(frontier):
    main, ghost = [], []
    for w in leaves(4):
        cut = next(p for p in frontier if w.startswith(p))
        for j in range(1,5):
            t = tile(w[:j])
            z = (0,)*CELL
            main.extend(t if j <= len(cut) else z)
            ghost.extend(z if j <= len(cut) else t)
        main.extend((0,)*CELL)
        ghost.extend((0,)*CELL)
    return main, ghost


def write(path, data):
    assert max(map(abs,data)) <= 11000
    payload = struct.pack('<'+'h'*len(data), *data)
    with wave.open(str(path),'wb') as w:
        w.setparams((1,2,RATE,len(data),'NONE','not compressed'))
        w.writeframes(payload)
    with wave.open(str(path),'rb') as w:
        assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (1,2,RATE,len(data))
        assert w.readframes(len(data)) == payload
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(sys.argv[1] if len(sys.argv)>1 else 'audio')
    out.mkdir(parents=True,exist_ok=True)
    rows = qualify()
    full, silence = render(leaves(4))
    a, ag = render(leaves(2))
    b, bg = render(('0','100','101','110','111'))
    assert not any(silence)
    assert [x+y for x,y in zip(a,ag)] == full == [x+y for x,y in zip(b,bg)]
    assert sum(v != 0 for v in a) > 0 and a != b
    recordings = {'complete':full,'even-cut':a,'uneven-cut':b,'even-ghost':ag,'uneven-ghost':bg}
    hashes = {name:write(out/(name+'.wav'),data) for name,data in recordings.items()}
    assert len(set(hashes.values())) == 5
    assert hashes == {name:write(out/(name+'.wav'),data) for name,data in recordings.items()}
    receipt = {'status':'PASS','python':sys.version.split()[0], 'census':rows,
               'frontiers_total':sum(r['frontiers'] for r in rows),
               'masks_total':sum(r['decision_masks'] for r in rows),
               'recordings':hashes,'frames_per_recording':len(full),'sample_rate':RATE,
               'scheduled_tiles':{'complete':64,'even-cut':32,'uneven-cut':32,'even-ghost':32,'uneven-ghost':32}}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
