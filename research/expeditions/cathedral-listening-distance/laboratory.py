"""Finite dyadic audition and original audio score; Python 3.11+ stdlib."""
import argparse
import hashlib
import itertools
import json
import math
import struct
import wave
from collections import Counter
from pathlib import Path


def counts(bits, depth):
    width = len(bits) >> depth
    return tuple(sum(bits[i:i+width]) for i in range(0, len(bits), width))


def ambiguity(n, depth, receipt):
    width = n >> depth
    return math.prod(math.comb(width, k) for k in receipt)


def tour(bits):
    """Root total is given; ask one left-child count per mixed node."""
    queries = []
    def visit(lo, hi, total):
        width = hi-lo
        if total in (0, width):
            return (int(total == width),)*width
        mid = (lo+hi)//2
        left = sum(bits[lo:mid])
        queries.append((lo, hi, left))
        return visit(lo, mid, left) + visit(mid, hi, total-left)
    return visit(0, len(bits), sum(bits)), queries


def census():
    cases = 0
    summary = {}
    for n in (2, 4, 8, 16):
        levels = n.bit_length()-1
        hist = [Counter() for _ in range(levels+1)]
        lo = [n]* (n+1)
        hi = [-1]* (n+1)
        for bits in itertools.product((0, 1), repeat=n):
            cases += 1
            k = sum(bits)
            restored, queries = tour(bits)
            assert restored == bits
            q = len(queries)
            mixed = sum(0 < c < (n >> d) for d in range(levels) for c in counts(bits,d))
            assert q == mixed
            lo[k], hi[k] = min(lo[k], q), max(hi[k], q)
            for d in range(levels+1):
                hist[d][counts(bits,d)] += 1
        for d, h in enumerate(hist):
            assert all(v == ambiguity(n,d,r) for r,v in h.items())
        for k in range(n+1):
            assert lo[k] == sum(k % (n >> d) != 0 for d in range(levels))
            assert hi[k] == sum(min(1 << d,k,n-k) for d in range(levels))
        summary[str(n)] = {"half_count": n//2, "min_queries": lo[n//2], "max_queries": hi[n//2]}
    return {"patterns": cases, "extrema": summary}


RATE = 16000
FRAMES = RATE*4


def render(bits, depth):
    """Fixed four-second count-to-pitch score. Not an auditory decoder."""
    seq = counts(bits, depth)
    width = len(bits) >> depth
    frames = FRAMES//len(seq)
    out = bytearray()
    for k in seq:
        hz = 220 + 440*k/width
        for i in range(frames):
            env = min(1, i/80, (frames-1-i)/80)
            out.extend(struct.pack('<h', round(7000*env*math.sin(2*math.pi*hz*i/RATE))))
    return bytes(out)


def audio(folder):
    folder.mkdir(parents=True, exist_ok=True)
    cluster = (1,)*8+(0,)*8
    spread = (1,0)*8
    shift = (0,1)*8
    results = {}
    for name,bits,d in (("cluster-overview",cluster,0),("spread-overview",spread,0),
                        ("cluster-detail",cluster,4),("spread-detail",spread,4),
                        ("spread-quarter",spread,2),("shift-quarter",shift,2),
                        ("shift-detail",shift,4)):
        pcm = render(bits,d)
        assert pcm == render(bits,d) and len(pcm)==2*FRAMES
        assert max(abs(v[0]) for v in struct.iter_unpack('<h',pcm)) <= 7000
        path = folder/(name+'.wav')
        with wave.open(str(path),'wb') as f:
            f.setparams((1,2,RATE,FRAMES,'NONE','not compressed'))
            f.writeframes(pcm)
        with wave.open(str(path),'rb') as f:
            assert (f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getnframes())==(1,2,RATE,FRAMES)
            assert f.readframes(FRAMES)==pcm
        results[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert results['cluster-overview']==results['spread-overview']
    assert results['spread-quarter']==results['shift-quarter']
    assert len({results[x] for x in ('cluster-detail','spread-detail','shift-detail')})==3
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path('audio'))
    args = parser.parse_args()
    receipt = {'census':census(), 'audio_sha256':audio(args.out)}
    (args.out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
