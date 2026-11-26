"""Synthetic singleton/dimer boundary testimony; no speech or human data."""
import hashlib
import json
import math
import struct
import sys
import wave
from pathlib import Path


def tilings(n):
    return [m for m in range(1 << (n - 1)) if not m & (m << 1)]


def certificate(n, d):
    # Bit i is a gap with NO boundary (a dimer crossing it).
    all_gaps = (1 << (n - 1)) - 1
    return d | (all_gaps & ~(d | (d << 1) | (d >> 1)))


def run_checks():
    cases = subsets = unique = 0
    counts = []
    for n in range(1, 11):
        ts = tilings(n)
        counts.append(len(ts))
        for d in ts:
            c = certificate(n, d)
            # Independently enumerate all sets of signed assertions.
            differences = [d ^ other for other in ts if other != d]
            admissible = []
            for s in range(1 << (n - 1)):
                subsets += 1
                if all(s & x for x in differences):
                    admissible.append(s)
            assert admissible
            minimum = min(s.bit_count() for s in admissible)
            assert [s for s in admissible if s.bit_count() == minimum] == [c]
            assert all((s & c) == c for s in admissible)
            assert all(s in admissible for s in range(1 << (n - 1)) if s & c == c)
            # Positive-only boundary evidence always permits all singletons.
            positive = ((1 << (n - 1)) - 1) ^ d
            assert (0 in [x for x in ts if not (x ^ d) & positive])
            assert (len([x for x in ts if not (x ^ d) & positive]) == 1) == (d == 0)
            cases += 1
            unique += len(admissible)
    assert counts[:3] == [1, 2, 3]
    assert all(counts[i] == counts[i-1] + counts[i-2] for i in range(2, len(counts)))
    return dict(target_tilings=cases, marker_subsets=subsets, sufficient_subsets=unique, tilings_by_length=counts)


def render(out):
    rate, cell, n = 16000, 4000, 8
    target = (1 << 1) | (1 << 4)
    c = certificate(n, target)
    all_gaps = (1 << (n - 1)) - 1
    variants = [('carrier', target, 0), ('positive-only', target, all_gaps ^ target),
                ('minimal', target, c), ('full', target, all_gaps),
                ('all-singletons', 0, all_gaps)]
    out.mkdir(parents=True, exist_ok=True)
    carriers, records = [], []
    for name, d, s in variants:
        frames = []
        for k in range(n * cell):
            i, j = divmod(k, cell)
            f = (220, 275, 330, 247, 294, 220, 330, 275)[i]
            left = round(10000 * math.sin(math.pi*j/cell)**2 * math.sin(2*math.pi*f*j/rate))
            # A short marker near the end of the preceding cell. High = boundary,
            # low = explicit continuation; absence = no assertion.
            q = j - 3000
            right = 0
            if i < n-1 and s & (1 << i) and 0 <= q < 800:
                g = 330 if d & (1 << i) else 990
                right = round(6500 * math.sin(math.pi*q/800)**2 * math.sin(2*math.pi*g*q/rate))
            frames.append((left, right))
        payload = b''.join(struct.pack('<hh', *x) for x in frames)
        path = out / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((2, 2, rate, len(frames), 'NONE', 'not compressed'))
            w.writeframes(payload)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2, 2, rate, len(frames))
            assert w.readframes(len(frames)) == payload
        assert max(abs(v) for pair in frames for v in pair) <= 10000
        carriers.append(payload[0::4] + payload[1::4])
        possible = [x for x in tilings(n) if not (x ^ d) & s]
        records.append(dict(name=name, no_boundary_mask=d, assertion_mask=s, possible_parses=len(possible), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    assert all(x == carriers[0] for x in carriers)
    assert len({r['sha256'] for r in records}) == len(records)
    assert [r['possible_parses'] for r in records] == [34, 4, 1, 1, 1]
    return records


if __name__ == '__main__':
    out = Path(sys.argv[1]) if len(sys.argv) == 2 else Path('audio')
    report = dict(status='PASS', python=sys.version.split()[0], checks=run_checks(), audio=render(out), human_trials=0)
    (out / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
