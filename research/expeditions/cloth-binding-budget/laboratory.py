"""Synthetic cyclic weaving / musical exposure oracle; not textile mechanics."""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math
import struct
import sys
import wave


def switches(w):
    return sum(a != b for a, b in zip(w, w[1:] + w[:1]))


def longest(w):
    # Rotate to a genuine boundary, so a wrapped run is counted once.
    if not switches(w):
        return len(w)
    i = next(i for i in range(len(w)) if w[i] != w[i-1])
    run = maximum = 1
    rotated = w[i:] + w[:i]
    for a, b in zip(rotated, rotated[1:]):
        run = run + 1 if a == b else 1
        maximum = max(maximum, run)
    return maximum


def independent_longest(w):
    return max(k for k in range(1, len(w)+1)
               if any(len(set((w+w)[i:i+k])) == 1 for i in range(len(w))))


def construct(n, cap):
    if n < 2 or n % 2 or not 1 <= cap <= n//2:
        raise ValueError('require even n >= 2 and 1 <= cap <= n/2')
    m = n//2
    r = (m+cap-1)//cap
    lengths = [min(cap, m-i*cap) for i in range(r)]
    return tuple(b for length in lengths for b in [1]*length+[0]*length)


def draft(w):
    n = len(w)
    return tuple(tuple(w[(i+j)%n] for j in range(n)) for i in range(n))


def lines(g):
    return tuple(g) + tuple(zip(*g))


def qualify():
    words = checks = 0
    for n in range(2, 15, 2):
        m = n//2
        histogram = Counter()
        for ones in combinations(range(n), m):
            w = tuple(int(i in ones) for i in range(n))
            f, s = longest(w), switches(w)
            assert f == independent_longest(w)
            histogram[f, s] += 1
            words += 1
        for cap in range(1, m+1):
            expected = 2*((m+cap-1)//cap)
            assert min(s for f, s in histogram if f <= cap) == expected
            g = draft(construct(n, cap))
            assert all(sum(w) == m and longest(w) <= cap for w in lines(g))
            assert sum(map(switches, lines(g))) == 2*n*expected
            checks += 1
    counts = Counter()
    for bits in product((0, 1), repeat=16):
        g = tuple(bits[i:i+4] for i in range(0, 16, 4))
        ls = lines(g)
        if all(sum(w) == 2 for w in ls):
            assert all(longest(w) == independent_longest(w) for w in ls)
            counts[max(map(longest, ls)), sum(map(switches, ls))] += 1
    assert sum(counts.values()) == 90
    assert min(s for f, s in counts if f <= 1) == 32
    assert min(s for f, s in counts if f <= 2) == 16
    for args in [(3, 1), (8, 0), (8, 5)]:
        try:
            construct(*args)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid parameters accepted')
    return dict(words=words, sharp_caps=checks, binary_matrices=65536,
                balanced_matrices=90,
                matrix_histogram={f'{f}/{s}': c for (f, s), c in sorted(counts.items())})


def render(g):
    n, rate, slot, cycles = len(g), 16000, 2240, 4
    voices = (196, 220, 247, 262, 294, 330, 349, 392)
    tracks = (g, tuple(tuple(1-b for b in w) for w in zip(*g)))
    frames = bytearray()
    total = n*slot*cycles
    for t in range(total):
        step, offset = divmod(t, slot)
        out = []
        for track in tracks:
            value = 0.0
            for f, w in zip(voices, track):
                i = step % n
                if w[i]:
                    env = 1.0
                    if step == 0 or not w[(i-1)%n]:
                        env = min(env, offset/160)
                    if step == n*cycles-1 or not w[(i+1)%n]:
                        env = min(env, (slot-1-offset)/160)
                    value += env*math.sin(2*math.pi*f*t/rate)
            out.append(round(6500*value))
        assert all(abs(v) <= 26000 for v in out)
        frames.extend(struct.pack('<hh', *out))
    return bytes(frames), rate, total


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    receipt = qualify()
    audio = {}
    for cap in (1, 2, 3, 4):
        g = draft(construct(8, cap))
        pcm, rate, total = render(g)
        path = out/f'cap-{cap}.wav'
        with wave.open(str(path), 'wb') as w:
            w.setparams((2, 2, rate, total, 'NONE', 'not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2, 2, rate, total)
            assert w.readframes(total) == pcm
        audio[path.name] = dict(word=''.join(map(str, g[0])), frames=total,
                                max_run=max(map(longest, lines(g))),
                                switches=sum(map(switches, lines(g))),
                                sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    assert len({a['sha256'] for a in audio.values()}) == 4
    receipt['audio'] = audio
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path('audio'))
