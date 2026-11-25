"""Independent literal-table census and synthetic PCM receipt renderer."""
import hashlib
import itertools as it
import json
import math
from pathlib import Path
import struct
import wave


def tables(rows, m, r):
    out = []
    for d in range(1, r + 1):
        for fields in it.combinations(range(m), d):
            hist = [0] * (1 << d)
            for row in rows:
                cell = sum(((row >> j) & 1) << i for i, j in enumerate(fields))
                hist[cell] += 1
            out.extend(hist)
    return tuple(out)


def census():
    results = []
    for m, r, k, simple in [(3, 2, 3, False), (3, 2, 4, False),
                             (4, 2, 3, False), (4, 2, 4, False),
                             (5, 2, 3, False), (5, 2, 4, False),
                             (4, 3, 8, True)]:
        source = it.combinations if simple else it.combinations_with_replacement
        counts = {}
        n = 0
        for rows in source(range(1 << m), k):
            sig = tables(rows, m, r)
            counts[sig] = counts.get(sig, 0) + 1
            n += 1
        ambiguous = sum(v > 1 for v in counts.values())
        assert max(counts.values()) <= (1 if k < 2**r else 2)
        results.append(dict(m=m, r=r, k=k, simple=simple, multisets=n,
                            fibres=len(counts), ambiguous=ambiguous,
                            max_fibre=max(counts.values())))
    return results


def render(rows, masks, path):
    # Equal integer pulse contributions, same phase for every sender.
    rate, size = 8000, 1600
    pulse = [[round(1800 * math.sin(2 * math.pi * f * i / rate)
                    * math.sin(math.pi * i / (size - 1))**2)
              for i in range(size)] for f in (250, 500)]
    samples = []
    counts = []
    for mask in masks:
        ones = sum((row & mask).bit_count() % 2 for row in rows)
        counts.append(ones)
        samples.extend((len(rows) - ones) * a + ones * b
                       for a, b in zip(*pulse))
    assert max(map(abs, samples)) < 32768
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        w.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
    return dict(counts=counts, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    output = Path(__file__).resolve().parent / 'results'
    output.mkdir(exist_ok=True)
    legs = [[x for x in range(8) if x.bit_count() % 2 == p] for p in (0, 1)]
    masks = [1, 2, 4, 3, 5, 6]
    audio = {}
    for name, rows in zip(('even', 'odd'), legs):
        for mode, queries in [('raw', masks), ('repaired', masks + [7])]:
            key = name + '-' + mode
            audio[key] = render(rows, queries, output / (key + '.wav'))
    assert audio['even-raw']['sha256'] == audio['odd-raw']['sha256']
    assert audio['even-repaired']['sha256'] != audio['odd-repaired']['sha256']
    assert audio['even-repaired']['counts'][-1] == 0
    assert audio['odd-repaired']['counts'][-1] == 4
    print(json.dumps(dict(profiles=census(), audio=audio, status='pass'), indent=2))


if __name__ == '__main__':
    main()
