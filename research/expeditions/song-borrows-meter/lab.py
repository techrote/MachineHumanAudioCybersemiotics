"""Original synthetic score, not a transcription or model of oral tradition."""
from collections import deque
from itertools import combinations
from pathlib import Path
import hashlib
import math
import struct
import wave

A = (1, 1, 1, 1, 0, 0, 0, 0)
B = (0, 0, 0, 0, 1, 1, 1, 1)
PITCH = (220, 294, 247, 330, 262, 392, 349, 220)
RATE, TICK = 16000, 4480


def distance(a, b):
    assert len(a) == len(b) and sum(a) == sum(b)
    debt = cost = 0
    for x, y in zip(a, b):
        debt += x - y
        cost += abs(debt)
    return cost


def neighbours(a):
    for i in range(len(a) - 1):
        if a[i] != a[i+1]:
            yield a[:i] + (a[i+1], a[i]) + a[i+2:]


def shortest(a, b):
    path = [a]
    while a != b:
        a = next(c for c in neighbours(a) if distance(c, b) == distance(a, b)-1)
        path.append(a)
    return path


def verify():
    pairs = 0
    for n in range(1, 9):
        for k in range(n+1):
            words = [tuple(int(i in ix) for i in range(n)) for ix in combinations(range(n), k)]
            diameter = 0
            for a in words:
                seen = {a: 0}
                queue = deque([a])
                while queue:
                    u = queue.popleft()
                    for v in neighbours(u):
                        if v not in seen:
                            seen[v] = seen[u]+1
                            queue.append(v)
                assert len(seen) == len(words)
                for b in words:
                    d = distance(a, b)
                    assert seen[b] == d
                    diameter = max(diameter, d)
                    pairs += 1
            assert diameter == k*(n-k)
    route = shortest(A, B)
    assert len(route) == 17 and route[-1] == B
    return pairs, route


def tone(f, gain):
    return [round(32767*gain*math.sin(math.pi*i/(TICK-1))**2 *
                  (math.sin(2*math.pi*f*i/RATE)+0.18*math.sin(4*math.pi*f*i/RATE)))
            for i in range(TICK)]


def phrase(mask):
    result = []
    for f, long in zip(PITCH, mask):
        result.extend(tone(f, 0.18))
        if long:
            result.extend(tone(f*1.125, 0.10))
    return result


def stereo(left, right):
    assert len(left) == len(right)
    return b''.join(struct.pack('<hh', a, b) for a, b in zip(left, right))


def render(out, route):
    out.mkdir(parents=True, exist_ok=True)
    a, b = phrase(A), phrase(B)
    assert len(a) == len(b) == 12*TICK and a != b
    assert all(len(phrase(mask)) == len(a) for mask in route)
    pieces = {'01-first-dialect': stereo(a, a), '02-second-dialect': stereo(b, b),
              '03-counterpoint': stereo(a, b),
              '04-sixteen-transfers': b''.join(stereo(a, phrase(mask)) for mask in route)}
    hashes = {}
    for name, data in pieces.items():
        p = out/(name+'.wav')
        with wave.open(str(p), 'wb') as w:
            w.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(data)
        with wave.open(str(p), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (2, 2, RATE)
            assert w.readframes(w.getnframes()) == data
        hashes[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes


if __name__ == '__main__':
    pairs, route = verify()
    print('BFS-verified ordered pairs:', pairs)
    print('Route:', [''.join(map(str, a)) for a in route])
    out = Path(__file__).parent/'audio'
    first = render(out, route)
    assert first == render(out, route)
    for name, digest in first.items():
        print(digest, name+'.wav')
