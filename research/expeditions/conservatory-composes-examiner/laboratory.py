"""Original synthetic score/selection fixture. No listener or device data."""
import hashlib
import itertools
import json
import math
import platform
import struct
import wave
from collections import Counter
from fractions import Fraction
from pathlib import Path

WEIGHTS = {'R': 9, 'A': 9, 'F': 2}
POINTS = {'R': 0, 'A': 2, 'F': 3}
N = 12
RATE = 16000
CELL = RATE // 4


def histogram(n, points):
    h = Counter()
    for word in itertools.product(WEIGHTS, repeat=n):
        h[sum(points[x] for x in word), word.count('A')] += math.prod(WEIGHTS[x] for x in word)
    return h


def multinomial(n, points):
    h = Counter()
    for a in range(n + 1):
        for f in range(n - a + 1):
            r = n - a - f
            h[a * points['A'] + f * points['F'], a] += math.comb(n, a) * math.comb(n - a, f) * 9**(r + a) * 2**f
    return h


def maximum(h, n, pool):
    # First maximum in an iid ordered pool; its conditional anchor distribution
    # is the same as an arbitrary single draw at that proxy score.
    mass, anchors = Counter(), Counter()
    for (p, a), w in h.items():
        mass[p] += w
        anchors[p] += a * w
    c = 0
    exact = pool <= 16
    ep = ea = Fraction(0) if exact else 0.0
    den = (20**n)**pool if exact else 20**n
    for p, w in sorted(mass.items()):
        win = (Fraction((c + w)**pool - c**pool, den) if exact
               else ((c+w)/den)**pool - (c/den)**pool)
        ep += p * win
        ea += (Fraction(anchors[p], w) if exact else anchors[p]/w) * win
        c += w
    assert c == 20**n
    return ep, ea


def render(word):
    data = []
    for x in word:
        k = POINTS[x]
        for i in range(CELL):
            if k == 0:
                data.append(0)
                continue
            j = i * k // CELL
            u = (i * k / CELL) - j
            f = (220, 330)[j] if x == 'A' else (660, 880, 550)[j]
            # Reset phase per event; envelope goes to zero at each boundary.
            data.append(round(8000 * math.sin(2 * math.pi * f * u * CELL / (RATE * k)) * math.sin(math.pi * u)**2))
    return struct.pack('<' + 'h' * len(data), *data)


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    h = histogram(N, POINTS)
    assert h == multinomial(N, POINTS)
    assert sum(h.values()) == 20**N
    # Independent exhaustive ordered two-candidate experiment, including ties.
    small = list(itertools.product(WEIGHTS, repeat=3))
    sum_p = sum_a = 0
    for x, y in itertools.product(small, repeat=2):
        p, q = (sum(POINTS[v] for v in z) for z in (x, y))
        w = math.prod(WEIGHTS[v] for v in x + y)
        sum_p += max(p, q) * w
        sum_a += (x if p >= q else y).count('A') * w
    assert maximum(histogram(3, POINTS), 3, 2) == (Fraction(sum_p, 20**6), Fraction(sum_a, 20**6))
    assert maximum(h, N, 1) == (Fraction(72, 5), Fraction(27, 5))
    pools = [1, 2, 4, 16, 64, 256, 1024, 16384, 1000000, 100000000]
    rows = []
    for m in pools:
        p, a = maximum(h, N, m)
        rows.append({'pool': m, 'expected_proxy': float(p), 'expected_anchors': float(a)})
    assert all(x['expected_proxy'] < y['expected_proxy'] for x, y in zip(rows, rows[1:]))
    assert rows[2]['expected_anchors'] > rows[0]['expected_anchors'] > rows[-1]['expected_anchors']
    # Direct extremal checks and a positive control: proxy identical to goal.
    assert max(p for p, a in h) == 36 and {a for p, a in h if p == 36} == {0}
    assert max(p for p, a in h if a >= 6) == 30
    direct = multinomial(N, {'R': 0, 'A': 1, 'F': 0})
    for m in pools:
        p, a = maximum(direct, N, m)
        assert abs(p - a) < 1e-12
    assert maximum(direct, N, pools[-1])[1] > maximum(direct, N, 1)[1]
    scores = {'rehearsal': 'ARFAARARARAR', 'structural': 'A'*N,
              'prize': 'F'*N, 'contract': 'AF'*6}
    audio = {}
    for name, word in scores.items():
        assert len(word) == N and set(word) <= set(WEIGHTS)
        pcm = render(word)
        assert pcm == render(word) and len(pcm) == 2 * N * CELL
        assert max(map(abs, struct.unpack('<'+'h'*(len(pcm)//2), pcm))) <= 8000
        path = out / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, RATE, N*CELL)
            assert w.readframes(N*CELL) == pcm
        audio[name] = {'word': word, 'proxy': sum(POINTS[x] for x in word), 'anchors': word.count('A'), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    assert len({x['sha256'] for x in audio.values()}) == len(audio)
    receipt = {'python': platform.python_version(), 'candidate_words': 3**N, 'ordered_small_pools': len(small)**2,
               'pool_results': rows, 'audio': audio, 'status': 'PASS'}
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    import sys
    run(Path(sys.argv[1]) if len(sys.argv) > 1 else Path('examiner-output'))
