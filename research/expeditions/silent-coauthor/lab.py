"""Original finite coalition-gate score; Python standard library only."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path
import argparse
import hashlib
import json
import struct
import wave

N = 4
PAIRS = tuple(sum(1 << i for i in p) for p in combinations(range(N), 2))
FULL = (1 << N) - 1
STAR = 0b000111  # AB, AC, AD
TRIANGLE = 0b111000  # BC, BD, CD


def value(graph, coalition):
    if not 0 <= graph < 64 or not 0 <= coalition <= FULL:
        raise ValueError('out of range')
    k = coalition.bit_count()
    if k < 2:
        return 0
    if k > 2:
        return 1
    return (graph >> PAIRS.index(coalition)) & 1


def credit(graph):
    counts = [0] * N
    for order in permutations(range(N)):
        s = 0
        for i in order:
            t = s | (1 << i)
            counts[i] += value(graph, t) - value(graph, s)
            s = t
    return tuple(Fraction(c, 24) for c in counts)


def degree_credit(graph):
    edges = [p for j, p in enumerate(PAIRS) if graph & (1 << j)]
    return tuple(Fraction(3 + 2 * sum(bool(e & (1 << i)) for e in edges)
                          - len(edges), 12) for i in range(N))


def pcm(graph, coalitions):
    # A fixed original square pulse, not an additive stem. The controls gate it.
    frames = []
    for s in coalitions:
        on = value(graph, s)
        for t in range(4000):
            envelope = min(t, 3999 - t, 160)
            frames.append(on * envelope * 40 * (1 if (t // 20) % 2 == 0 else -1))
        frames.extend([0] * 800)
    return struct.pack('<' + 'h' * len(frames), *frames)


def experiment(out):
    out.mkdir(parents=True, exist_ok=True)
    fixed = (0, 1, 2, 4, 8, 7, 11, 13, 14, 15)
    files = {}
    for name, graph in [('star', STAR), ('triangle', TRIANGLE)]:
        for kind, masks in [('routine', fixed), ('pairs', PAIRS)]:
            path = out / f'{name}-{kind}.wav'
            with wave.open(str(path), 'wb') as w:
                w.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
                w.writeframes(pcm(graph, masks))
            files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    classes = Counter(credit(g) for g in range(64))
    report = {
        'games': 64, 'distinct_credit_vectors': len(classes),
        'credit_class_size_histogram': dict(sorted(Counter(classes.values()).items())),
        'min_max_A': [str(min(c[0] for c in classes)), str(max(c[0] for c in classes))],
        'star': list(map(str, credit(STAR))), 'triangle': list(map(str, credit(TRIANGLE))),
        'equal_credit_games': sorted(g for g in range(64) if credit(g) == (Fraction(1,4),)*4),
        'routine_masks': fixed, 'pair_masks': PAIRS, 'wav_sha256': files,
    }
    (out / 'results.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    return report


def verify():
    checks = 0
    for g in range(64):
        c = credit(g)
        assert c == degree_credit(g) and sum(c) == 1
        checks += 2
        for i in range(N):
            assert 0 <= c[i] <= Fraction(1,2)
            checks += 1
        for s in range(16):
            for t in range(16):
                if s & t == s:
                    assert value(g, s) <= value(g, t)
                    checks += 1
            if s.bit_count() != 2:
                assert value(g, s) == value(0, s)
                checks += 1
        for j in range(6):
            h = g ^ (1 << j)
            assert credit(h) != c
            checks += 1
            for s in range(16):
                assert (value(g, s) != value(h, s)) == (s == PAIRS[j])
                checks += 1
    assert credit(STAR) == (Fraction(1,2),) + (Fraction(1,6),)*3
    assert credit(TRIANGLE) == (Fraction(0),) + (Fraction(1,3),)*3
    assert credit(0) == credit(63) == (Fraction(1,4),)*4
    assert pcm(STAR, (0,1,2,4,8,7,11,13,14,15)) == pcm(TRIANGLE, (0,1,2,4,8,7,11,13,14,15))
    assert pcm(STAR, PAIRS) != pcm(TRIANGLE, PAIRS)
    return checks + 5


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    print('assertions:', verify())
    if a.out:
        print(json.dumps(experiment(a.out), indent=2))
