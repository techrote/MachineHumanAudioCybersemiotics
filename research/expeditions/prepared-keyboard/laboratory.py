"""Synthetic prepared keyboard: matching census and original PCM studies."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import wave


def subsets(n):
    return [tuple(i for i in range(n) if mask >> i & 1) for mask in range(1 << n)]


def rank(rows, chord, ports):
    # Independent assignment enumeration; -1 means unallocated.
    return max(sum(p >= 0 for p in a) for a in itertools.product(range(-1, ports), repeat=len(chord))
               if len({p for p in a if p >= 0}) == sum(p >= 0 for p in a)
               and all(p < 0 or rows[i] >> p & 1 for i, p in zip(chord, a)))


def deficit(rows, chord):
    worst = 0
    for positions in subsets(len(chord)):
        union = 0
        for j in positions:
            union |= rows[chord[j]]
        worst = max(worst, len(positions) - union.bit_count())
    return worst


def census():
    results = []
    for n, m in [(3, 3), (4, 3)]:
        chords = subsets(n)
        pair_ok = hidden = 0
        for rows in itertools.product(range(1 << m), repeat=n):
            ds = [deficit(rows, c) for c in chords]
            assert all(rank(rows, c, m) == len(c)-d for c, d in zip(chords, ds))
            if all(d == 0 for c, d in zip(chords, ds) if len(c) <= 2):
                pair_ok += 1
                hidden += any(d > 0 for c, d in zip(chords, ds) if len(c) == 3)
        results.append(dict(notes=n, ports=m, graphs=2**(n*m), chord_cases=2**(n*m+n),
                            all_pairs_feasible=pair_ok, hidden_triple_obstruction=hidden))
    return results


RATE = 16000
FREQS = (220, 277, 330, 440)
LIMITED = (3, 3, 3, 12)
EXPANDED = (3, 3, 7, 12)


def render(path, rows, score):
    pcm = bytearray()
    for chord in score:
        assert deficit(rows, chord) == 0, ('unplayable request', chord)
        for i in range(RATE//2):
            env = math.sin(math.pi*i/(RATE//2-1))**2
            x = sum(math.sin(2*math.pi*f*i/RATE) + .18*math.sin(2*math.pi*2*f*i/RATE)
                    for f in (FREQS[j] for j in chord))
            pcm.extend(round(3000*env*x).to_bytes(2, 'little', signed=True))
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        w.writeframes(pcm)
    with wave.open(str(path), 'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, RATE)
        assert w.getnframes() == len(score)*RATE//2 and w.readframes(w.getnframes()) == pcm
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(__file__).resolve().parent/'audio'
    out.mkdir(exist_ok=True)
    pairs = list(itertools.combinations(range(4), 2))
    assert all(deficit(LIMITED, c) == 0 for c in pairs)
    assert deficit(LIMITED, (0, 1, 2)) == 1
    assert deficit(EXPANDED, (0, 1, 2, 3)) == 0
    editions = {'duets-limited': (LIMITED, pairs), 'duets-expanded': (EXPANDED, pairs),
                'trio-refused': (LIMITED, [(3,), (), (), (3,)]),
                'trio-serialized': (LIMITED, [(3,), (0, 1), (2,), (3,)]),
                'trio-expanded': (EXPANDED, [(3,), (0, 1, 2), (), (3,)])}
    try:
        render(out/'invalid.wav', LIMITED, [(0, 1, 2)])
    except AssertionError:
        assert not (out/'invalid.wav').exists()
    else:
        raise AssertionError('invalid chord was accepted')
    hashes = {name: render(out/(name+'.wav'), rows, score) for name, (rows, score) in editions.items()}
    assert hashes['duets-limited'] == hashes['duets-expanded'] and len(set(hashes.values())) == 4
    report = {'census': census(), 'sha256': hashes, 'qualification': 'PASS',
              'scope': 'synthetic graph and deterministic PCM; no human or hardware test'}
    (out/'receipt.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
