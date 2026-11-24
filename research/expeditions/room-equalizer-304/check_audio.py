"""Refs #304: independent integer hull census and synthetic PCM rendering."""
import hashlib
import itertools
import json
import math
import struct
import sys
import wave
from pathlib import Path


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def hull(points):
    p = sorted(set(points))
    if len(p) <= 1:
        return p
    def half(seq):
        h = []
        for x in seq:
            while len(h) >= 2 and cross(h[-2], h[-1], x) <= 0:
                h.pop()
            h.append(x)
        return h
    return half(p)[:-1] + half(reversed(p))[:-1]


def blocked(points):
    h = hull(points)
    if len(h) == 1:
        return h[0] == (0, 0)
    if len(h) == 2:
        a, b = h
        return cross(a, b, (0, 0)) == 0 and sum(x*y for x, y in zip(a, b)) <= 0
    return all(cross(a, b, (0, 0)) >= 0 for a, b in zip(h, h[1:] + h[:1]))


def census():
    grid = [(x, y) for x in range(-2, 3) for y in range(-2, 3) if x or y]
    result = {}
    for n in (3, 4):
        s = dict(total=0, obstructed=0, pairwise_only=0, all_improve=0, antipodal=0)
        for p in itertools.combinations(grid, n):
            s['total'] += 1
            if blocked(p):
                s['obstructed'] += 1
                if any(blocked(pair) for pair in itertools.combinations(p, 2)):
                    s['antipodal'] += 1
                else:
                    s['pairwise_only'] += 1
            else:
                s['all_improve'] += 1
        result[str(n)] = s
    sums = {k: sum(s[k] for s in result.values()) for k in result['3']}
    assert sums == dict(total=12650, obstructed=7810, pairwise_only=3264,
                        all_improve=4840, antipodal=4546), sums
    return result


def render(out):
    out.mkdir(parents=True, exist_ok=True)
    h = [1+0j, complex(-.5, math.sqrt(3)/2), complex(-.5, -math.sqrt(3)/2)]
    pair_gain = (h[0].conjugate() + h[2].conjugate()) / 2
    gains = [pair_gain, h[1].conjugate(), pair_gain]
    corrected = [a*b for a, b in zip(h, gains)]
    residual = [1-z for z in corrected]
    assert max(map(abs, residual)) <= math.sqrt(3)/2 + 1e-14
    assert abs(residual[1]) <= 1e-14
    assert max(abs(1-z) for z in h) > 1
    fs, block = 16000, 9600
    manifest = dict(sample_rate=fs, block_samples=block, receiver_order=[0, 1, 2],
                    carrier_hz=[300, 400, 500], pcm_gain=10000,
                    channels={}, split_gain=[[z.real, z.imag] for z in gains],
                    split_residual_magnitudes=list(map(abs, residual)))
    for name, left, right in (
        ('same-magnitude.wav', [1+0j]*3, h),
        ('split-residual.wav', [1+0j]*3, residual),
    ):
        buf = bytearray()
        peak = 0
        for i, (l, r) in enumerate(zip(left, right)):
            for t in range(block):
                phase = 2*math.pi*(300+100*i)*t/fs
                carrier = complex(math.cos(phase), math.sin(phase))
                # Smooth 20 ms attack/release; common gain, never normalize per channel.
                edge = min(1, t/320, (block-1-t)/320)
                env = math.sin(math.pi*edge/2)**2
                a, b = (round(10000*env*(carrier*z).real) for z in (l, r))
                peak = max(peak, abs(a), abs(b))
                assert -32768 <= a <= 32767 and -32768 <= b <= 32767
                buf.extend(struct.pack('<hh', a, b))
        path = out/name
        with wave.open(str(path), 'wb') as w:
            w.setparams((2, 2, fs, 0, 'NONE', 'not compressed'))
            w.writeframes(buf)
        with wave.open(str(path), 'rb') as w:
            assert w.getnframes() == 3*block
            pcm = list(struct.iter_unpack('<hh', w.readframes(w.getnframes())))
        if name == 'same-magnitude.wav':
            assert all(a == b for a, b in pcm[:block])
            assert any(a != b for a, b in pcm[block:])
        else:
            assert all(b == 0 for _, b in pcm[block:2*block])
            assert any(b != 0 for _, b in pcm[:block])
        manifest['channels'][name] = dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                          frames=len(pcm), peak=peak)
    return manifest


if __name__ == '__main__':
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('run')
    receipt = dict(census=census(), audio=render(out))
    (out/'verification.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))
