"""Synthetic shared-gesture reachability and original stereo score. Standard library."""
from collections import deque
from hashlib import sha256
from math import gcd, lcm, sin, pi
from pathlib import Path
import json
import struct
import sys
import wave


def orbit(m, n, offset=0):
    return [(t % m, (t + offset) % n) for t in range(lcm(m, n))]


def distance(m, n, offset):
    # Independent oracle: 0-1 BFS; common steps cost zero, B-only trim costs one.
    start = (0, offset % n)
    dist = {start: 0}
    queue = deque([start])
    while queue:
        a, b = queue.popleft()
        for da, db, cost in ((1, 1, 0), (-1, -1, 0), (0, 1, 1), (0, -1, 1)):
            v = ((a + da) % m, (b + db) % n)
            candidate = dist[a, b] + cost
            if candidate < dist.get(v, float('inf')):
                dist[v] = candidate
                (queue.append if cost else queue.appendleft)(v)
    return dist


def qualify():
    cases = targets = 0
    for m in range(2, 13):
        for n in range(2, 13):
            d = gcd(m, n)
            classes = [set(orbit(m, n, s)) for s in range(d)]
            assert all(len(c) == lcm(m, n) for c in classes)
            assert len(set.union(*classes)) == m * n
            for s, c in enumerate(classes):
                oracle = distance(m, n, s)
                assert len(oracle) == m * n
                for (a, b), actual in oracle.items():
                    r = (b - a - s) % d
                    assert actual == min(r, d-r)
                    assert ((a, b) in c) == (r == 0)
                    targets += 1
                cases += 1
    assert (0, 1) not in orbit(4, 6)
    assert distance(8, 12, 0)[0, 2] == 2
    return {'offset_cases': cases, 'target_comparisons': targets}


RATE, SLOT = 16000, 4000
PITCH = [196, 220, 261.6256, 293.6648]


def pcm(score):
    result = bytearray()
    for a, b in score:
        for i in range(SLOT):
            t = i / RATE
            env = min(1, i / 240, (SLOT - 1 - i) / 400)
            left = .27 * env * sin(2*pi*PITCH[a]*t)
            right = .27 * env * sin(2*pi*392*t) * (.65 + .35*sin(2*pi*(3+3*b)*t))
            result.extend(struct.pack('<hh', round(32767*left), round(32767*right)))
    return bytes(result)


def render(out):
    out.mkdir(parents=True, exist_ok=True)
    even, odd = orbit(4, 6), orbit(4, 6, 1)
    scores = {'even': even*2, 'odd': odd*2, 'release': even+odd}
    assert len(set(scores['even'])) == len(set(scores['odd'])) == 12
    assert len(set(scores['release'])) == 24
    data = {name: pcm(score) for name, score in scores.items()}
    assert len(set(data.values())) == 3
    assert len({b''.join(p[i:i+2] for i in range(0, len(p), 4)) for p in data.values()}) == 1
    report = {}
    for name, payload in data.items():
        assert payload == pcm(scores[name])
        assert max(abs(s[0]) for s in struct.iter_unpack('<h', payload)) <= 9000
        path = out / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((2, 2, RATE, len(scores[name])*SLOT, 'NONE', 'not compressed'))
            w.writeframes(payload)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2, 2, RATE, 96000)
            assert w.readframes(w.getnframes()) == payload
        report[name] = {'unique_pairs': len(set(scores[name])), 'sha256': sha256(path.read_bytes()).hexdigest()}
    return report


if __name__ == '__main__':
    print(json.dumps({'math': qualify(), 'audio': render(Path(sys.argv[1]) if len(sys.argv)>1 else Path('audio'))}, indent=2))
