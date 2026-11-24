"""Bounded binary ornament channels; deterministic original PCM score."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import struct
import wave


def far_masks(n, t):
    return [sum(1 << y for y in range(1 << n)
                if (x ^ y).bit_count() > 2 * t) for x in range(1 << n)]


def vertices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def frontier(n, t):
    """Max size B for each nonempty size A with cross-distance > 2t.

    Translate an element of A to zero; permute a chosen B element to
    the low w bits. Enumerate all subsets of its far set containing 0.
    """
    if not (1 <= n <= 6 and 0 <= t <= n):
        raise ValueError('outside supported cube')
    if n >= 5 and t == 0:
        return {k: (1 << n) - k for k in range(1, 1 << n)}, 0
    if n == 6 and t == 1:
        raise ValueError('unqualified enumeration size')
    far = far_masks(n, t)
    out = {}
    visited = 0
    for w in range(2 * t + 1, n + 1):
        b = (1 << w) - 1
        choices = far[b] & ~1
        s = choices
        while True:
            common = far[0]
            for x in vertices(s):
                common &= far[x]
            k, j = 1 + s.bit_count(), common.bit_count()
            if j:
                out[k] = max(out.get(k, 0), j)
            visited += 1
            if not s:
                break
            s = (s - 1) & choices
    return dict(sorted(out.items())), visited


def full_word_capacity(n, t):
    """Maximum mutually separated words, by exhaustive clique search.

    A maximum nonempty code can be translated to contain zero.
    """
    far = far_masks(n, t)
    def visit(pool):
        best = 0
        while pool:
            bit = pool & -pool
            pool ^= bit
            best = max(best, 1 + visit(pool & far[bit.bit_length() - 1]))
        return best
    return 1 + visit(far[0])


def codebook(n=5):
    return {0: tuple(x for x in range(1 << n) if x.bit_count() <= 1),
            1: tuple(x for x in range(1 << n) if x.bit_count() >= n - 1)}


def candidates(received, code, t=1):
    return [(label, x) for label, words in code.items() for x in words
            if (received ^ x).bit_count() <= t]


def score_words(words, path):
    """Five-slot phrase: zero=200 Hz, one=400 Hz; no silence-as-zero.

    8 kHz, mono 16-bit, 0.12 s per slot, 0.08 s interphrase gap.
    Integer square oscillator with a short integer ramp; no samples reused.
    """
    samples = []
    for x in words:
        for i in range(4, -1, -1):
            period = 20 if x & (1 << i) else 40
            for k in range(960):
                amplitude = 1800 * min(k, 959 - k, 80) // 80
                samples.append(amplitude if k % period < period // 2 else -amplitude)
        samples.extend([0] * 640)
    with wave.open(str(path), 'wb') as handle:
        handle.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
        handle.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report(output):
    output.mkdir(parents=True, exist_ok=True)
    cases = {}
    for n, t in [(3, 0), (3, 1), (4, 1), (5, 1), (5, 2), (6, 2)]:
        f, visited = frontier(n, t)
        cases[f'{n},{t}'] = {'frontier': f, 'balanced': max((min(a, b) for a, b in f.items()), default=0),
                              'enumerated': visited}
    code = codebook()
    ambiguity = {format(y, '05b'): [[m, format(x, '05b')] for m, x in candidates(y, code)]
                 for y in range(32)}
    # A transmitted intentional one, and a corrupted zero word, arrive identically.
    sequences = {'licensed_variants': list(code[0]) + list(code[1]),
                 'intentional': [0, 1, 0, 2, 0, 4],
                 'corrupted': [0, 1, 0, 2, 0, 4],
                 'canonicalized': [0] * 6}
    hashes = {name: score_words(words, output / (name + '.wav'))
              for name, words in sequences.items()}
    result = {'cases': cases, 'full_word_capacity_5_1': full_word_capacity(5, 1),
              'codebook': code, 'ambiguity': ambiguity,
              'uniform_exact_word_optimum': {'numerator': 32, 'denominator': 72},
              'sound_sequences': sequences, 'wav_sha256': hashes,
              'sound_history': {'intentional_sent': sequences['intentional'],
                                'corrupted_sent': [0] * 6,
                                'corrupted_masks': sequences['corrupted']}}
    (output / 'results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = report(args.output)
    print(json.dumps({k: v for k, v in result.items() if k != 'ambiguity'}, sort_keys=True))
