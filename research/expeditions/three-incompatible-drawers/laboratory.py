"""Synthetic atlas; Python standard library only. Run: python laboratory.py OUTDIR."""
from collections import Counter
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib
import json
import math
import struct
import sys
import wave

POINTS = tuple(product(range(2), repeat=3))
FULL = (1 << len(POINTS)) - 1
RATE, FRAMES = 16000, 12000


@lru_cache(None)
def constant(mask):
    return tuple(len({p[a] for i, p in enumerate(POINTS) if mask >> i & 1}) == 1
                 for a in range(3))


def splits(mask):
    anchor = mask & -mask
    sub = (mask - 1) & mask
    while sub:
        if sub & anchor:
            yield sub, mask ^ sub
        sub = (sub - 1) & mask


@lru_cache(None)
def histogram(mask):
    if mask.bit_count() == 1:
        return Counter({(1, 1, 1): 1})
    out = Counter()
    for a, b in splits(mask):
        for v, c in histogram(a).items():
            for w, d in histogram(b).items():
                key = tuple(1 if mono else v[i] + w[i]
                            for i, mono in enumerate(constant(mask)))
                out[key] += c * d
    return out


@lru_cache(None)
def trees(mask):
    # Each tree is represented by its internal clusters; children unordered.
    if mask.bit_count() == 1:
        return ((),)
    return tuple((mask,) + left + right for a, b in splits(mask)
                 for left in trees(a) for right in trees(b))


def clip(p):
    direction, pulse, rich = p
    start, end = (180, 360) if direction == 0 else (360, 180)
    values = []
    for i in range(FRAMES):
        t = i / RATE
        u = i / (FRAMES - 1)
        phase = 2 * math.pi * (start * t + (end-start) * t*t / 1.5)
        envelope = math.sin(math.pi * u)**2
        if pulse:
            envelope *= math.sin(3 * math.pi * u)**2
        carrier = math.sin(phase)
        if rich:
            carrier = (carrier + .5*math.sin(2*phase) + .25*math.sin(3*phase))/1.75
        values.append(round(12000 * envelope * carrier))
    assert max(map(abs, values)) <= 12000
    return struct.pack('<' + 'h'*FRAMES, *values)


def write_wav(path, data):
    with wave.open(str(path), 'wb') as f:
        f.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        f.writeframes(data)
    with wave.open(str(path), 'rb') as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == (1, 2, RATE)
        assert f.getnframes() == len(data)//2 and f.readframes(f.getnframes()) == data
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    h = histogram(FULL)
    # Independent cover computation: each homogeneous internal merge removes
    # one maximal monochromatic subtree from the all-leaf partition.
    brute = Counter(tuple(8-sum(constant(m)[a] for m in tree) for a in range(3))
                    for tree in trees(FULL))
    assert h == brute and sum(h.values()) == 135135 and len(h) == 183
    assert min(map(sum, h)) == 14 and min(map(max, h)) == 6
    assert h[(2, 6, 6)] == 2 and h[(2, 4, 8)] == 1
    assert not any(max(k) <= 5 for k in h)  # impossible balance control
    assert histogram(1) == Counter({(1, 1, 1): 1})
    assert len({tuple(sorted(t)) for t in trees(FULL)}) == 135135
    pcm = {p: clip(p) for p in POINTS}
    assert len(set(pcm.values())) == 8 and all(clip(p) == data for p, data in pcm.items())
    hashes = {}
    for p, data in pcm.items():
        name = 'tile-' + ''.join(map(str, p)) + '.wav'
        hashes[name] = write_wav(out / name, data)
    orders = {}
    for a, label in enumerate(('contour', 'pulse', 'texture')):
        order = sorted(POINTS, key=lambda p: (p[a], p))
        orders[label] = [''.join(map(str, p)) for p in order]
        data = b''.join(pcm[p] for p in order)
        assert Counter(data[i:i+2*FRAMES] for i in range(0, len(data), 2*FRAMES)) == Counter(pcm.values())
        hashes[label+'.wav'] = write_wav(out / (label+'.wav'), data)
    assert len({hashes[x+'.wav'] for x in orders}) == 3
    receipt = dict(python=sys.version, trees=sum(h.values()), cost_vectors=len(h),
                   min_total=min(map(sum,h)), min_worst=min(map(max,h)),
                   total_optima=sum(v for k,v in h.items() if sum(k)==14),
                   balanced_total_optima=sum(v for k,v in h.items() if sum(k)==14 and max(k)==6),
                   histogram={','.join(map(str,k)):v for k,v in sorted(h.items())},
                   orders=orders, wav_sha256=hashes, rate=RATE, frames_per_tile=FRAMES,
                   source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print({k:v for k,v in receipt.items() if k not in ('histogram','wav_sha256')})


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path('atlas-output'))
