"""Copia: exact symbolic scheduling and original PCM, no human evidence."""
from itertools import permutations
from pathlib import Path
import hashlib
import json
import math
import struct
import sys
import wave

ANCHORS = 'ABCD'
COMMENTS = 'abcd'
DEADLINES = (1, 2, 4, 5)  # completed tile indices, one-based
RATE = 16000
TILE = 4000


def valid(s):
    return (len(s) == 8 and set(s) == set(ANCHORS + COMMENTS)
            and ''.join(c for c in s if c.isupper()) == ANCHORS
            and all(s.index(a) < s.index(a.lower()) for a in ANCHORS))


def on_time(s, deadlines):
    return all(s.index(a) + 1 <= d for a, d in zip(ANCHORS, deadlines))


def distance(s):
    return sum(s.index(a.lower()) - s.index(a) - 1 for a in ANCHORS)


def enumerate_recursive(prefix=''):
    if len(prefix) == 8:
        yield prefix
        return
    a = next((a for a in ANCHORS if a not in prefix), None)
    available = ([a] if a else []) + [a.lower() for a in ANCHORS
                                     if a in prefix and a.lower() not in prefix]
    for c in available:
        yield from enumerate_recursive(prefix + c)


def tile(c):
    f = (196, 247, 294, 392)[ANCHORS.index(c.upper())]
    out = []
    for n in range(TILE):
        t = n / RATE
        env = math.sin(math.pi * n / (TILE - 1)) ** 2
        if c.isupper():
            v = .32 * math.sin(2 * math.pi * f * t)
        else:
            v = .18 * math.sin(2 * math.pi * 2 * f * t) + .10 * math.sin(2 * math.pi * 3 * f * t)
        out.append(round(32767 * env * v))
    return struct.pack('<' + 'h' * TILE, *out)


def render(path, score):
    assert valid(score)
    pcm = b''.join(tile(c) for c in score)
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        w.writeframes(pcm)
    with wave.open(str(path), 'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, RATE, 8 * TILE)
        assert w.readframes(8 * TILE) == pcm
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(out):
    brute = {''.join(p) for p in permutations(ANCHORS + COMMENTS) if valid(''.join(p))}
    recursive = list(enumerate_recursive())
    assert len(recursive) == len(set(recursive)) == len(brute) == 105
    assert set(recursive) == brute
    feasible = sorted(s for s in brute if on_time(s, DEADLINES))
    best = min(map(distance, feasible))
    best_scores = [s for s in feasible if distance(s) == best]
    assert valid('AaBbCcDd') and not on_time('AaBbCcDd', DEADLINES)
    assert on_time('ABCDabcd', DEADLINES)
    assert distance('AaBbCcDd') == 0 and distance('ABCDabcd') == 12
    # Exhaustively compare two generation methods for every deadline vector.
    from itertools import product
    checked = 0
    for deadlines in product(range(1, 9), repeat=4):
        a = {s for s in brute if on_time(s, deadlines)}
        b = {s for s in recursive if all(s.index(k) < d for k, d in zip(ANCHORS, deadlines))}
        assert a == b
        # Earliest possible anchors are at 1,2,3,4. All comments can follow.
        assert bool(a) == all(d >= i for i, d in enumerate(deadlines, 1))
        checked += 1
    out.mkdir(parents=True, exist_ok=True)
    pieces = {'local': 'AaBbCcDd', 'bulletin': 'ABCDabcd', 'negotiated': best_scores[0]}
    files = {}
    for name, s in pieces.items():
        p = out / (name + '.wav')
        digest = render(p, s)
        assert render(p, s) == digest
        files[name] = {'score': s, 'anchor_slots': [s.index(a)+1 for a in ANCHORS],
                       'on_time': on_time(s, DEADLINES), 'comment_distance': distance(s), 'sha256': digest}
    assert len({v['sha256'] for v in files.values()}) == 3
    receipt = {'status': 'PASS', 'python': sys.version.split()[0], 'permutations_examined': math.factorial(8),
               'valid_scores': len(brute), 'deadline_vectors': checked, 'deadline_feasible': len(feasible),
               'minimum_comment_distance': best, 'minimizers': best_scores, 'deadline_slots': DEADLINES,
               'tiles': 8, 'sample_rate': RATE, 'tile_frames': TILE, 'files': files}
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    run(Path(sys.argv[1]) if len(sys.argv) > 1 else Path('audio'))
