"""Synthetic interval-cut instrument; not a model of a physical Mobius strip."""
from collections import Counter
from itertools import permutations
from math import comb, factorial, sin, pi
from pathlib import Path
import hashlib
import json
import struct
import wave


def trace(n, order):
    intervals = [(0, n)]
    stages = [tuple(intervals)]
    parents = {}
    for k in order:
        matches = [(a, b) for a, b in intervals if a < k < b]
        if len(matches) != 1:
            raise ValueError('cut not interior to exactly one live interval')
        a, b = matches[0]
        intervals.remove((a, b))
        intervals.extend([(a, k), (k, b)])
        intervals.sort()
        parents[k] = (a, b)
        stages.append(tuple(intervals))
    return stages, tuple(sorted(parents.items()))


def genealogy(a, b, order):
    """Independent recursive first-cut oracle and count of compatible orders."""
    if b-a == 1:
        return (), 1
    k = next(k for k in order if a < k < b)
    left, lc = genealogy(a, k, order)
    right, rc = genealogy(k, b, order)
    return tuple(sorted(((k, (a, b)),) + left + right)), comb(b-a-2, k-a-1)*lc*rc


def qualify():
    records = []
    for n in range(2, 10):
        counts, predicted = Counter(), {}
        for order in permutations(range(1, n)):
            stages, g = trace(n, order)
            oracle, ways = genealogy(0, n, order)
            assert g == oracle
            assert stages[-1] == tuple((i, i+1) for i in range(n))
            for stage in stages:
                assert stage[0][0] == 0 and stage[-1][1] == n
                assert all(a < b for a, b in stage)
                assert all(x[1] == y[0] for x, y in zip(stage, stage[1:]))
            counts[g] += 1
            predicted[g] = ways
        assert counts == predicted
        assert sum(counts.values()) == factorial(n-1)
        assert len(counts) == comb(2*(n-1), n-1)//n
        records.append(dict(cells=n, histories=sum(counts.values()), trees=len(counts),
                            largest_fibre=max(counts.values()), singleton_trees=sum(v==1 for v in counts.values())))
    for bad in ((0,), (8,), (4,4)):
        try:
            trace(8, bad)
        except ValueError:
            continue
        raise AssertionError('illegal cut accepted')
    return records


RATE, FRAMES = 16000, 8000
SCORES = {'left-first': (4,2,6,1,3,5,7), 'right-first': (4,6,2,7,5,3,1),
          'comb': (1,2,3,4,5,6,7)}


def render(order):
    stages, g = trace(8, order)
    parents = dict(g)
    blocks = []
    for j, stage in enumerate(stages):
        block = bytearray()
        for i in range(FRAMES):
            t = i/RATE
            env = min(1, i/160, (FRAMES-1-i)/160)
            # All extant pieces sound; pitch reflects length and position.
            left = 2200*env*sum(sin(2*pi*(100+21*(b-a)+7*(a+b))*t) for a,b in stage)
            right = 0
            if j:
                a,b = parents[order[j-1]]
                right = 5000*env*max(0,1-t/.18)**3*sin(2*pi*(170+53*(b-a))*t)
            pair = (round(left), round(right))
            assert all(-32768 <= v <= 32767 for v in pair)
            block.extend(struct.pack('<hh', *pair))
        blocks.append(bytes(block))
    return blocks


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    records = qualify()
    blocks = {name: render(order) for name,order in SCORES.items()}
    assert trace(8,SCORES['left-first'])[1] == trace(8,SCORES['right-first'])[1]
    assert trace(8,SCORES['comb'])[1] != trace(8,SCORES['left-first'])[1]
    assert len({b''.join(b) for b in blocks.values()}) == 3
    assert len({b[-1][::1] for b in blocks.values()}) == 1  # last parent length also equal
    receipt = {'census': records, 'files': {}, 'negative_cut_cases': 3,
               'model': 'synthetic; stage-reset phase; no human data'}
    for name, b in blocks.items():
        path = out/(name+'.wav')
        pcm = b''.join(b)
        with wave.open(str(path),'wb') as w:
            w.setparams((2,2,RATE,0,'NONE','not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path),'rb') as w:
            assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (2,2,RATE,8*FRAMES)
            assert w.readframes(w.getnframes()) == pcm
        receipt['files'][path.name] = {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                                       'cuts':SCORES[name], 'seconds':4}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    import sys
    main(Path(sys.argv[1] if len(sys.argv)>1 else 'audio'))
