"""Exact source-side mask laboratory; Python 3.11+, standard library only."""
from fractions import Fraction as F
from itertools import product, combinations
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import random
import struct
import wave


def trim(x):
    x = list(x)
    while x and x[-1] == 0:
        x.pop()
    return tuple(x)


def at(x, i):
    return x[i] if 0 <= i < len(x) else 0


def onset(x):
    return next(i for i, a in enumerate(x) if a)


def conv(x, h):
    y = [0] * (len(x) + len(h) - 1)
    for i, a in enumerate(x):
        for j, b in enumerate(h):
            y[i + j] += a * b
    return trim(y)


def masked(x, h, d):
    return conv([a * d[i] for i, a in enumerate(x)], h)


def canon(x, h):
    a = F(x[onset(x)])
    return trim(F(v) / a for v in x), trim(F(v) * a for v in h)


def quotient(u, v, size):
    assert v[0]
    out = []
    for i in range(size):
        out.append((F(at(u, i)) - sum(at(v, j) * out[i-j] for j in range(1, i+1))) / v[0])
    return out


def recover(y, masks, records, n):
    """Return source normalized at onset, and compensating filter; reject inconsistency."""
    ell = onset(y)
    u = y[ell:]
    signature = tuple(F(at(z, ell)) / u[0] for z in records)
    possible = [p for p in range(min(n, ell+1)) if tuple(d[p] for d in masks) == signature]
    if len(possible) != 1:
        raise ValueError('nonunique or absent onset')
    p = possible[0]
    rs = [quotient(z[ell:], u, n-p) for z in records]
    f = [F(1)]
    for k in range(1, n-p):
        row = next((i for i, d in enumerate(masks) if d[p+k] != d[p]), None)
        if row is None:
            raise ValueError('unseparated coefficient')
        d, r = masks[row], rs[row]
        f.append(sum(f[j] * r[k-j] for j in range(k)) / (d[p+k] - d[p]))
    x = trim([F(0)] * p + f)
    h = trim([F(0)] * (ell-p) + quotient(u, f, len(u)))
    if conv(x, h) != y or any(masked(x, h, d) != z for d, z in zip(masks, records)):
        raise ValueError('inconsistent complete record')
    return x, h


def distance_decode(y, masks, records, n, t):
    good = [i for i, z in enumerate(records) if z is not None]
    candidates = set()
    for inds in combinations(good, len(good)-t):
        try:
            x, h = recover(y, [masks[i] for i in inds], [records[i] for i in inds], n)
        except ValueError:
            continue
        if sum(masked(x, h, masks[i]) != records[i] for i in good) <= t:
            candidates.add((x, h))
    if len(candidates) != 1:
        raise ValueError('not uniquely correctable')
    return candidates.pop()


def render(directory, stem, coeffs):
    # Same fixed gain for all histories; deterministic integer pulse basis.
    pcm = [0] * 4000
    pulse = [0, 1000, 0, -1000] * 100
    for j, a in enumerate(coeffs):
        for i, v in enumerate(pulse):
            pcm[j*800+i] = int(a*v)
    data = struct.pack('<' + 'h'*len(pcm), *pcm)
    path = directory / (stem + '.wav')
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
        w.writeframes(data)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(directory):
    n = 3
    masks = list(product((F(1,2), F(1)), repeat=n))
    seq = sorted({trim(x) for x in product(range(3), repeat=n) if any(x)})
    histories = sorted({canon(x,h) for x in seq for h in seq})
    groups = defaultdict(list)
    for x,h in histories:
        groups[conv(x,h)].append(tuple(masked(x,h,d) for d in masks))
    differing = set()
    comparisons = 0
    for records in groups.values():
        for a,b in combinations(records,2):
            differing.add(sum((x != y) << i for i,(x,y) in enumerate(zip(a,b))))
            comparisons += 1
    census = defaultdict(int)
    for dictionary in range(1 << len(masks)):
        empirical = min((dictionary & k).bit_count() for k in differing)
        predicted = min(sum(bool(dictionary & (1<<i)) and d[p] != d[q]
                            for i,d in enumerate(masks))
                        for p,q in combinations(range(n),2))
        assert empirical == predicted, (dictionary, empirical, predicted)
        census[empirical] += 1
    ramp = [(F(1,2),F(3,4),F(1))]
    for x,h in histories:
        assert recover(conv(x,h), ramp, [masked(x,h,ramp[0])], n) == (x,h)
    rng = random.Random(570)
    signed = 0
    corrected = 0
    words = ['000000','111100','110011','001111']
    code = [tuple(F(1,2) if w[j]=='0' else F(1) for w in words) for j in range(6)]
    for _ in range(200):
        n = rng.randrange(2,10)
        x = tuple(rng.randrange(-3,4) for _ in range(n))
        h = tuple(rng.randrange(-3,4) for _ in range(rng.randrange(1,9)))
        if not any(x) or not any(h):
            continue
        x,h = canon(x,h)
        ramp = [tuple(F(1,2)+F(i,2*(n-1)) for i in range(n))]
        assert recover(conv(x,h), ramp, [masked(x,h,ramp[0])],n) == (x,h)
        signed += 1
    for _ in range(40):
        x = tuple(rng.randrange(-2,3) for _ in range(4))
        h = tuple(rng.randrange(-2,3) for _ in range(4))
        if not any(x) or not any(h):
            continue
        x,h = canon(x,h)
        y = conv(x,h)
        rows = [masked(x,h,d) for d in code]
        for err,era in product(range(6), repeat=2):
            if err == era:
                continue
            bad = rows.copy()
            bad[err] = (F(999),)
            bad[era] = None
            assert distance_decode(y,code,bad,4,1) == (x,h)
            corrected += 1
    # Shared polynomial factor survives geometric tilt, but the linked pair identifies it.
    x,h = canon((1,3,2),(1,3))
    d = (F(1,4),F(1,2),F(1))
    assert conv(x,h) == (1,6,11,6)
    assert recover(conv(x,h),[d],[masked(x,h,d)],3) == (x,h)
    # Gain-blind pure-delay ambiguity, even with every strictly positive mask.
    for d in masks:
        a = masked((0,1),(1,),d)
        b = masked((1,),(0,1),d)
        assert tuple(F(v)/a[onset(a)] for v in a) == tuple(F(v)/b[onset(b)] for v in b)
    # A crop before the second tap erases an otherwise identifiable distinction.
    assert conv((1,1),(1,))[:1] == conv((1,),(1,1))[:1]
    crop_mask = (F(1,2),F(1))
    assert masked((1,1),(1,),crop_mask)[:1] == masked((1,),(1,1),crop_mask)[:1]
    assert masked((1,1),(1,),crop_mask) != masked((1,),(1,1),crop_mask)
    # Sharp fault-distance failure: two plausible histories, not malformed receipts.
    short = [(F(1,2),F(1,2)),(F(1,2),F(1)),(F(1,2),F(1))]
    a, b = ((1,), (0,1)), ((0,1),(1,))
    y = conv(*a)
    assert y == conv(*b)
    ra = [masked(*a,d) for d in short]
    rb = [masked(*b,d) for d in short]
    hybrid = [ra[0],ra[1],rb[2]]
    assert sum(u != v for u,v in zip(ra,hybrid)) == 1
    assert sum(u != v for u,v in zip(rb,hybrid)) == 1
    try:
        distance_decode(y,short,hybrid,2,1)
    except ValueError:
        pass
    else:
        raise AssertionError('ambiguous hybrid incorrectly accepted')
    # Audio is sonification of exact coefficient vectors, not room measurement.
    xa,ha = (1,2,1),(1,1)
    xb,hb = ha,xa
    d = (1,F(1,2),F(1,4))
    vectors = {'raw-a':conv(xa,ha),'raw-b':conv(xb,hb),
               'masked-a':masked(xa,ha,d),'masked-b':masked(xb,hb,d)}
    assert vectors['raw-a'] == vectors['raw-b']
    assert vectors['masked-a'] != vectors['masked-b']
    hashes = {name:render(directory,name,v) for name,v in vectors.items()}
    assert (directory/'raw-a.wav').read_bytes() == (directory/'raw-b.wav').read_bytes()
    assert (directory/'masked-a.wav').read_bytes() != (directory/'masked-b.wav').read_bytes()
    return {'histories':len(histories),'baseline_fibres':len(groups),'same_baseline_pairs':comparisons,
            'distinct_row_difference_masks':len(differing),'mask_dictionaries':256,
            'dictionary_distance_histogram':dict(sorted(census.items())),
            'ramp_recoveries':len(histories),'signed_recoveries':signed,
            'one_error_one_erasure_decodes':corrected,
            'audio_coefficients':{k:[str(a) for a in v] for k,v in vectors.items()},
            'audio_sha256':hashes}


if __name__ == '__main__':
    directory = Path(__file__).resolve().parent
    print(json.dumps(run(directory),indent=2,sort_keys=True))
