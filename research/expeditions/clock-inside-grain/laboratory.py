"""Original synthetic timing art; standard library only, no human evidence."""
from functools import lru_cache
from itertools import accumulate, product
from pathlib import Path
import hashlib
import json
import math
import struct
import sys
import wave


def balanced(w):
    if len(w) == 1:
        return True
    h = len(w) // 2
    return abs(sum(w[:h]) - sum(w[h:])) <= 1 and balanced(w[:h]) and balanced(w[h:])


def rounded(n, m):
    # Round all ideal boundaries half-up, then difference them.
    b = [(2 * i * n + m) // (2 * m) for i in range(m + 1)]
    return tuple(y - x for x, y in zip(b, b[1:]))


@lru_cache(None)
def count(n, m):
    if m == 1:
        return 1
    return sum(count(k, m // 2) * count(n - k, m // 2)
               for k in {n // 2, (n + 1) // 2})


def errors(w):
    m, n = len(w), sum(w)
    return tuple(m * s - i * n for i, s in enumerate(accumulate(w), 1))


def qualify():
    rows = []
    witness = None
    for d in range(1, 5):
        m = 2 ** d
        groups = {n: [] for n in range(m, 2 * m + 1)}
        for w in product((1, 2), repeat=m):
            if balanced(w):
                groups[sum(w)].append(w)
        for n, words in groups.items():
            assert len(words) == count(n, m)
            g = rounded(n, m)
            assert g in words and max(map(abs, errors(g))) * 2 <= m
            assert max(map(abs, errors(g))) == min(max(map(abs, errors(w))) for w in words)
        w = max((w for words in groups.values() for w in words), key=lambda w: max(errors(w)))
        rows.append(dict(depth=d, screened=2 ** m, balanced=sum(map(len, groups.values())),
                         max_error_numerator=max(errors(w)), denominator=m, total=sum(w)))
        if d == 4:
            witness = w
    assert witness is not None
    assert not balanced((2, 2, 1, 1))
    assert sum(witness) in (21, 27) and max(errors(witness)) == 23
    return rows, witness


def render(out, w, name, reference):
    rate, tick, repeats = 16000, 640, 4
    pitches = (220, 330, 277, 392, 247, 370, 294, 440)
    def channel(word):
        pcm = []
        for _ in range(repeats):
            for i, length in enumerate(word):
                frames = length * tick
                for j in range(frames):
                    env = min(1, j / 48, (frames - 1 - j) / 48)
                    pcm.append(round(7000 * env * math.sin(2 * math.pi * pitches[i % len(pitches)] * j / rate)))
        return pcm
    left, right = channel(reference), channel(w)
    assert len(left) == len(right) and max(map(abs, left + right)) <= 7000
    payload = struct.pack('<' + 'h' * (2 * len(left)), *(v for pair in zip(left, right) for v in pair))
    path = out / (name + '.wav')
    with wave.open(str(path), 'wb') as f:
        f.setparams((2, 2, rate, len(left), 'NONE', 'not compressed'))
        f.writeframes(payload)
    with wave.open(str(path), 'rb') as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes()) == (2, 2, rate, len(left))
        assert f.readframes(len(left)) == payload
    return dict(word=w, error_numerator=errors(w), frames=len(left),
                left_sha256=hashlib.sha256(struct.pack('<'+'h'*len(left), *left)).hexdigest(),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('audio')
    out.mkdir(parents=True, exist_ok=True)
    census, w = qualify()
    g = rounded(sum(w), len(w))
    studies = {name: render(out, word, name, g) for name, word in
               [('global', g), ('local', w), ('reflected', w[::-1])]}
    assert len({s['left_sha256'] for s in studies.values()}) == 1
    assert len({s['sha256'] for s in studies.values()}) == 3
    receipt = dict(status='PASS', scope='synthetic only', python=sys.version.split()[0],
                   census=census, studies=studies, tick_ms=40)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
