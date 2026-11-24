"""Independent exact integer checks and original PCM sonification (Python 3)."""
from itertools import product
from pathlib import Path
from math import comb, sin, pi
import hashlib
import json
import struct
import wave


def quotient(s, r):
    # Explicit polynomial deconvolution via binomial convolution, not prefix passes.
    q = []
    for i in range(len(s)):
        q.append(s[i] - sum((-1)**k * comb(r, k) * q[i-k]
                            for k in range(1, min(i, r)+1)))
    assert not any(q[-r:])
    return q[:-r]


def cost(s, r):
    return (sum(a != b for a, b in zip(s, s[1:])),
            max(abs(sum(s[:i])) for i in range(1, len(s)+1)),
            sum(map(abs, quotient(s, r))))


def dominates(a, b):
    return all(x <= y for x, y in zip(a, b))


def census(n, r):
    values = []
    for tail in product((-1, 1), repeat=n-1):
        s = (1,) + tail
        if all(sum(x*i**k for i,x in enumerate(s)) == 0 for k in range(r)):
            values.append(cost(s, r))
    distinct = set(values)
    return len(values), sorted(v for v in distinct if not any(
        w != v and dominates(w, v) for w in distinct))


def render(out):
    # Two second-order null blocks with n=16, same total amplitude and order.
    words = ['++++--------++++', '+--++--++--++--+']
    s = [tuple(1 if c == '+' else -1 for c in w) for w in words]
    q = [quotient(v, 2) for v in s]
    assert [cost(v, 2) for v in s] == [(2, 4, 128), (8, 1, 8)]
    # Shared adversarial drift: second finite difference is +1 throughout.
    x = [comb(i, 2) for i in range(16)]
    assert [sum(a*b for a,b in zip(v,x)) for v in s] == [128, 8]
    sr, cell = 16000, 1600
    # Artistic mapping: +/- phase on a common 250 Hz carrier, followed by
    # second-integral coefficients mapped onto a shared amplitude scale.
    output = {}
    for name, streams, scale in [('bipolar-words.wav', s, 1),
                                  ('integral-debt.wav', [v+[0,0] for v in q], max(map(abs,q[0])))]:
        data = bytearray()
        for l,r in zip(*streams):
            for t in range(cell):
                env = sin(pi*t/(cell-1))**2
                carrier = sin(2*pi*250*t/sr)*env*0.65*32767/scale
                data.extend(struct.pack('<hh', round(l*carrier), round(r*carrier)))
        p = out/name
        with wave.open(str(p), 'wb') as f:
            f.setparams((2,2,sr,0,'NONE','not compressed'))
            f.writeframes(data)
        output[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return {'words':words,'quotients':q,'costs':[cost(v,2) for v in s],
            'shared_drift':x,'shared_drift_responses':[128,8],
            'sample_rate':sr,'samples_per_cell':cell,'sha256':output}


def main():
    out = Path(__file__).parent/'run'
    out.mkdir(exist_ok=True)
    cases = [(4,1),(4,2),(4,3),(8,2),(8,3),(8,4),(12,2),(12,3),
             (16,2),(16,3),(16,4),(16,5)]
    rows = [{'n':n,'r':r,'count':c,'frontier':f}
            for n,r in cases for c,f in [census(n,r)]]
    for m in range(1,65):
        a = [1]*m+[-1]*(2*m)+[1]*m
        b = [1,-1,-1,1]*m
        assert cost(a,2) == (2,m,2*m**3)
        assert cost(b,2) == (2*m,1,2*m)
    result = {'rows':rows,'family_checks':128,'audio':render(out)}
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
