"""Finite reversible-control order auditor and synthetic stereo state score."""
from __future__ import annotations
import argparse
from collections import Counter, deque
import hashlib
from itertools import permutations
import json
from pathlib import Path
import struct
import wave


def validate(a, b, start):
    n = len(a)
    if not n or len(b) != n or sorted(a) != list(range(n)) or sorted(b) != list(range(n)):
        raise ValueError('maps must be permutations on the same nonempty domain')
    if not 0 <= start < n:
        raise ValueError('start outside domain')


def trace(a, b, start, word):
    states = [start]
    for symbol in word:
        states.append({'A': a, 'B': b}[symbol][states[-1]])
    return states


def _search(a, b, start, bad):
    # BFS visits each reachable state once. A/B ordering fixes tie-breaking.
    q = deque([(start, '')])
    seen = {start}
    first = None
    while q:
        s, w = q.popleft()
        if s in bad and first is None:
            first = (s, w)
        for symbol, f in (('A', a), ('B', b)):
            t = f[s]
            if t not in seen:
                seen.add(t)
                q.append((t, w + symbol))
    return first, seen


def audit(a, b, start=0):
    validate(a, b, start)
    bad = {s for s in range(len(a)) if b[a[s]] != a[b[s]]}
    first, seen = _search(a, b, start, bad)
    out = {'a': list(a), 'b': list(b), 'start': start, 'reachable': sorted(seen),
           'global_disagreement': sorted(bad), 'reachable_disagreement': sorted(bad & seen),
           'nominal_equal': start not in bad, 'reachable_equal': first is None,
           'witness': None}
    if first is not None:
        s, w = first
        out['witness'] = {'state': s, 'prefix': w, 'depth': len(w),
                          'AB_trace': trace(a, b, start, w + 'AB'),
                          'BA_trace': trace(a, b, start, w + 'BA')}
    return out


def extremal(n):
    if n < 3:
        raise ValueError('n must be at least 3')
    a = list(range(n)); a[-2], a[-1] = a[-1], a[-2]
    b = list(range(1, n-1)) + [0, n-1]
    return tuple(a), tuple(b)


def survey(n):
    ps = list(permutations(range(n)))
    counts = Counter()
    depths = Counter()
    for a in ps:
        for b in ps:
            bad = {s for s in range(n) if b[a[s]] != a[b[s]]}
            if 0 in bad:
                counts['immediate'] += 1
                depths[0] += 1
                continue
            first, seen = _search(a, b, 0, bad)
            if first is None:
                counts['reachable_equal'] += 1
                if bad:
                    counts['unreachable_disagreement_subset'] += 1
            else:
                counts['hidden'] += 1
                depths[len(first[1])] += 1
                assert len(first[1]) <= len(seen) - 3
    return {'n': n, 'ordered_pairs': len(ps)**2, 'counts': dict(sorted(counts.items())),
            'depth_counts': dict(sorted(depths.items()))}


def sample(state, i, length, rate):
    # Integer triangle oscillator and envelope: identical output bytes across
    # platforms with standard PCM WAV headers; no transcendental math.
    phase = (i * (180 + 40 * state)) % rate
    tri = 4 * phase - rate if phase < rate // 2 else 3 * rate - 4 * phase
    fade = max(1, rate // 100)
    envelope = min(i, length - 1 - i, fade)
    return 7000 * tri * envelope // (rate * fade)


def render(path, left, right):
    if len(left) != len(right):
        raise ValueError('equal-length paths required')
    rate, length, gap = 16000, 2880, 640
    buf = bytearray()
    for l, r in zip(left, right):
        for i in range(length):
            buf.extend(struct.pack('<hh', sample(l, i, length, rate), sample(r, i, length, rate)))
        buf.extend(bytes(4 * gap))
    with wave.open(str(path), 'wb') as f:
        f.setparams((2, 2, rate, 0, 'NONE', 'not compressed'))
        f.writeframes(buf)
    return {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'frames': len(buf)//4,
            'sample_rate': rate, 'channels': 2, 'sample_width': 2}


def run(out, max_n=6):
    out.mkdir(parents=True, exist_ok=True)
    if not 2 <= max_n <= 6:
        raise ValueError('exhaustive bound must be 2..6')
    a, b = extremal(8)
    example = audit(a, b)
    w = example['witness']
    audio = render(out/'sleeping-commutator.wav', w['AB_trace'], w['BA_trace'])
    control = audit(a, tuple(range(8)))
    nominal = render(out/'nominal-control.wav', trace(a,b,0,'AB'), trace(a,b,0,'BA'))
    result = {'classification': 'synthetic finite-state mathematics and artistic mapping',
              'surveys': [survey(n) for n in range(2, max_n+1)],
              'extremal_depths': [{'n': n, 'depth': audit(*extremal(n))['witness']['depth']} for n in range(3,33)],
              'eight_state_example': example, 'commuting_control': control,
              'audio': {'sleeping-commutator.wav': audio, 'nominal-control.wav': nominal}}
    (out/'results.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--max-n', type=int, default=6)
    args = p.parse_args()
    print(json.dumps(run(args.out, args.max_n)['surveys'], indent=2))
