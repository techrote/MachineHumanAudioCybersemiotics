"""Original synthetic accent-budget laboratory. Python 3.11+, standard library."""
import hashlib
import itertools
import json
import math
import struct
import sys
import wave
from pathlib import Path

RATE = 16000
CELL = 4000
PITCHES = (220, 275, 330, 294, 247, 220)
GROUPS = ({0, 3}, {1, 4}, {2, 5})


def masks(n, b):
    return map(frozenset, itertools.combinations(range(n), b))


def qualify():
    count = cases = 0
    for r in range(2, 5):
        for s in range(1, 4):
            groups = [set(range(i*s, (i+1)*s)) for i in range(r)]
            for b in range(r*s + 1):
                scores = [min(len(a & g) for g in groups) for a in masks(r*s, b)]
                count += len(scores)
                cases += 1
                assert max(scores) == b // r
    pair_counts = []
    for g, h in itertools.combinations(GROUPS, 2):
        pair_counts.append(sum(bool(a & g) and bool(a & h) for a in masks(6, 2)))
    assert pair_counts == [4, 4, 4]
    assert not any(all(a & g for g in GROUPS) for a in masks(6, 2))
    assert sum(all(a & g for g in GROUPS) for a in masks(6, 3)) == 8
    return dict(candidate_masks=count, budget_cases=cases, pair_counts=pair_counts,
                triple_budget2=0, triple_budget3=8)


def render(accent):
    if not set(accent) <= set(range(6)):
        raise ValueError('accent outside score')
    out = []
    for i, f in enumerate(PITCHES):
        gain = 0.55 if i in accent else 0.20
        for j in range(CELL):
            t = j / RATE
            env = math.sin(math.pi*j/(CELL-1))**2
            out.append(round(32767*gain*env*(0.8*math.sin(2*math.pi*f*t)
                       + 0.2*math.sin(4*math.pi*f*t))))
    assert max(map(abs, out)) < 32767
    return struct.pack('<' + 'h'*len(out), *out)


def main(directory):
    result = qualify()
    directory.mkdir(parents=True, exist_ok=True)
    scores = {'keeper': GROUPS[0], 'locked': GROUPS[1], 'unlocked': GROUPS[1],
              'light': GROUPS[2], 'pair': {0, 1}, 'three': {0, 1, 2}}
    receipt = {}
    for name, a in scores.items():
        pcm = render(a)
        assert pcm == render(a)
        path = directory / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, RATE, 6*CELL)
            assert w.readframes(6*CELL) == pcm
        receipt[name] = dict(accents=sorted(a), hits=[len(a & g) for g in GROUPS],
                             sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    assert receipt['locked']['sha256'] == receipt['unlocked']['sha256']
    assert len({v['sha256'] for v in receipt.values()}) == 5
    try:
        render({6})
    except ValueError:
        pass
    else:
        raise AssertionError('invalid accent accepted')
    result.update(recordings=receipt, frames=6*CELL, sample_rate=RATE,
                  python=sys.version.split()[0], result='PASS')
    (directory / 'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path('contrafactum-audio'))
