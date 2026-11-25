"""Independent finite-state oracle and original synthetic audio, MHAC #424."""
from collections import deque
from hashlib import sha256
from itertools import product
import json
import math
from pathlib import Path
import struct
import wave

HERE = Path(__file__).resolve().parent
ALT = '++++--------+++++++------+++++----+++--+'
ASC = '+-' * 12 + '-' * 8 + '+' * 8


def step(state, d):
    return tuple(tuple(max(0, min(m, x + d)) for x in row)
                 for m, row in enumerate(state, 1))


def full_image(word, R):
    state = tuple(tuple(range(m + 1)) for m in range(1, R + 1))
    for c in word:
        state = step(state, 1 if c == '+' else -1)
    return state


def oracle(R):
    # Full image of every individual starting state; no extrema theorem used.
    start = tuple(tuple(range(m + 1)) for m in range(1, R + 1))
    q = deque([(0, start, 0)])
    seen = {(0, start)}
    found = {}
    visits = 0
    while q and len(found) < 2 ** R:
        s, state, length = q.popleft()
        visits += 1
        if s == 0 and all(len(set(row)) == 1 for row in state):
            found.setdefault(tuple(row[0] for row in state), length)
        for d in (-1, 1):
            pair = (s + d, step(state, d))
            if pair not in seen:
                seen.add(pair)
                q.append((*pair, length + 1))
    assert len(found) == 2 ** R
    expected = {}
    for bits in product((0, 1), repeat=R):
        f = tuple(sum(bits[:i]) for i in range(1, R + 1))
        cost = R + sum(i for i in range(1, R) if bits[i] != bits[i-1])
        cost += f[-1] if bits[-1] else R - f[-1]
        expected[f] = cost
    assert found == expected
    return {'capacity': R, 'profiles': len(found), 'visited': visits,
            'min': min(found.values()), 'max': max(found.values())}


def trajectory(word, initial):
    states = [tuple(initial)]
    for c in word:
        d = 1 if c == '+' else -1
        states.append(tuple(max(0, min(m, x + d))
                            for m, x in enumerate(states[-1], 1)))
    return states


def render(name, left, right):
    rate, ticks, tail = 16000, 1280, 9600
    assert len(left) == len(right) == 41
    frames = bytearray()
    peak = 0
    # Eight original sinusoidal carriers. 10 ms ramps, continuous phase.
    for i in range(40 * ticks + tail):
        k = min(40, i // ticks + 1)
        u = min(1, (i % ticks) / 160) if i < 40*ticks else 1
        envelope = min(1, i / 160, (40*ticks+tail-1-i) / 160)
        pair = []
        for states in (left, right):
            sample = sum(((1-u)*states[k-1][m-1]+u*states[k][m-1])/m
                         * math.sin(2*math.pi*(180+73*m)*i/rate)
                         for m in range(1, 9)) / 10
            pair.append(round(32767 * envelope * sample))
        peak = max(peak, *map(abs, pair))
        frames.extend(struct.pack('<hh', *pair))
    path = HERE / name
    with wave.open(str(path), 'wb') as w:
        w.setparams((2, 2, rate, 0, 'NONE', 'not compressed'))
        w.writeframes(frames)
    assert peak < 32767
    return {'file': name, 'frames': len(frames)//4, 'rate': rate,
            'peak_pcm': peak, 'sha256': sha256(path.read_bytes()).hexdigest()}


def main():
    rows = [oracle(R) for R in range(1, 8)]
    for word in (ASC, ALT):
        assert len(word) == 40 and word.count('+') == word.count('-') == 20
    full = tuple(range(1, 9))
    zeros = (0,) * 8
    mid = tuple(m//2 for m in full)
    a, b = trajectory(ASC, mid), trajectory(ALT, mid)
    low, high = trajectory(ALT, zeros), trajectory(ALT, full)
    assert a[-1] == full and b[-1] == low[-1] == high[-1] == (1,1,2,2,3,3,4,4)
    assert all(len(set(row)) == 1 for row in full_image(ALT, 8))
    first = render('same-input-different-score.wav', a, b)
    second = render('forgetting-in-stereo.wav', low, high)
    assert first == render(first['file'], a, b)
    assert second == render(second['file'], low, high)
    receipt = {'oracle': rows, 'ascending_word': ASC, 'alternating_word': ALT,
               'ascending_final': a[-1], 'alternating_final': b[-1],
               'convergence_tick': next(i for i,(x,y) in enumerate(zip(low,high)) if x==y),
               'audio': [first, second]}
    (HERE / 'independent.synthetic.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
