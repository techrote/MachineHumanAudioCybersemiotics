"""Synthetic montage experiment; Python 3.11+, standard library only."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product, permutations
from math import sin, pi, factorial
from pathlib import Path
import json
import struct
import sys
import wave


def grams(s, k):
    return tuple(sorted(Counter(s[i:i+k] for i in range(len(s)-k+1)).items()))


def census():
    rows = []
    for n in range(1, 10):
        groups = defaultdict(list)
        for p in product('ABX', repeat=n):
            s = ''.join(p)
            groups[(s[0], s[-1], grams(s, 2))].append(s)
        ambiguous = 0
        affected = 0
        for group in groups.values():
            assert len({grams(s, 1) for s in group}) == 1
            if len({grams(s, 3) for s in group}) > 1:
                ambiguous += 1
                affected += len(group)
        rows.append(dict(length=n, scores=3**n, receipts=len(groups),
                         triple_ambiguous_receipts=ambiguous, affected_scores=affected,
                         largest_class=max(map(len, groups.values()))))
    return rows


def family(k, p):
    spacer = 'X' * (k-1)
    return spacer + spacer.join(p) + spacer


def qualify_family():
    cases = 0
    for k in range(2, 6):
        for m in range(2, 7):
            scores = [family(k, p) for p in permutations('ABCDEF'[:m])]
            for j in range(1, k+1):
                assert len({grams(s, j) for s in scores}) == 1
            assert len({grams(s, k+1) for s in scores}) == factorial(m)
            assert all(s.startswith('X'*(k-1)) and s.endswith('X'*(k-1)) for s in scores)
            cases += len(scores)
    return cases


RATE = 16000
FRAMES = 4800
FREQ = dict(A=196, B=523, C=247, X=330)


def tile(key):
    f = FREQ[key]
    return tuple(round(6000*sin(pi*i/(FRAMES-1))**2 *
                       (sin(2*pi*f*i/RATE)+0.25*sin(4*pi*f*i/RATE)))
                 for i in range(FRAMES))


def render(score, path):
    tiles = {k: tile(k) for k in set(score)}
    pcm = tuple(v for k in score for v in tiles[k])
    assert max(map(abs, pcm)) <= 7500
    raw = struct.pack('<'+'h'*len(pcm), *pcm)
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, RATE, len(pcm), 'NONE', 'not compressed'))
        w.writeframes(raw)
    with wave.open(str(path), 'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, RATE, len(pcm))
        assert w.readframes(len(pcm)) == raw
    for i, k in enumerate(score):
        assert pcm[i*FRAMES:(i+1)*FRAMES] == tile(k)
    return dict(score=score, frames=len(pcm), sha256=sha256(path.read_bytes()).hexdigest())


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    a, b = 'AXAXBXB', 'AXBXAXB'
    assert a != b and grams(a, 2) == grams(b, 2)
    assert a[0] == b[0] and a[-1] == b[-1]
    assert grams(a, 3) != grams(b, 3)
    assert grams(a, 2) != grams(a[::-1], 2)  # directed negative control
    rows = census()
    cases = qualify_family()
    scores = dict(clustered=a, alternating=b, third_order_i=family(3, 'ABC'),
                  third_order_ii=family(3, 'CAB'), isolated_x='X')
    audio = {name: render(s, out/(name+'.wav')) for name, s in scores.items()}
    assert len({r['sha256'] for r in audio.values()}) == len(audio)
    receipt = dict(python=sys.version.split()[0], census=rows, family_cases=cases,
                   audio=audio, result='PASS', human_listening=False)
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path('montage-audio'))
