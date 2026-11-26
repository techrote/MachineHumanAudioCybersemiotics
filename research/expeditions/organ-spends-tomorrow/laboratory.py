"""Synthetic restoration/drive-budget oracle and original sound score.
Run: python laboratory.py [output-directory]. No dependencies beyond stdlib.
"""
from itertools import product
from pathlib import Path
import hashlib, json, math, struct, sys, wave

AGED = (1, 2, 3, 4)
FRESH = 4
TARGET = 12
FREQ = (220, 440, 660, 880)
RATE = 16000


def efficiencies(mask):
    return tuple(FRESH if mask & (1 << i) else e for i, e in enumerate(AGED))


def optimum(es, target, cap):
    """DP keyed by exact drive spent; minimize squared coefficient error."""
    if target < 0 or cap < 0 or not es or any(e <= 0 for e in es):
        raise ValueError('invalid model')
    states = {0: (0, ())}
    for e in es:
        nxt = {}
        for spent, (err, us) in states.items():
            for u in range(min(cap - spent, (target + e - 1) // e) + 1):
                k = spent + u
                v = (err + (e * u - target) ** 2, us + (u,))
                if k not in nxt or v < nxt[k]:
                    nxt[k] = v
        states = nxt
    err, spent, us = min((err, spent, us) for spent, (err, us) in states.items())
    return err, spent, us


def exhaustive(es, target, maxcap):
    """Independent enumeration includes overshoot, bounded only by total cap."""
    bins = [None] * (maxcap + 1)
    count = 0
    for us in product(range(maxcap + 1), repeat=len(es)):
        spent = sum(us)
        if spent > maxcap:
            continue
        count += 1
        v = (sum((e * u - target) ** 2 for e, u in zip(es, us)), spent, us)
        if bins[spent] is None or v < bins[spent]:
            bins[spent] = v
    return [min(v for v in bins[:cap+1] if v is not None) for cap in range(maxcap+1)], count


def pcm(coeffs):
    """One second; normalized coefficient mapping, common gain, fixed phases."""
    assert len(coeffs) == len(FREQ) and all(0 <= c <= 28 for c in coeffs)
    return b''.join(struct.pack('<h', round(32767 * 0.8 / 112 *
        math.sin(math.pi * i / (RATE - 1)) ** 2 *
        sum(c * math.sin(2 * math.pi * f * i / RATE) for c, f in zip(coeffs, FREQ))))
        for i in range(RATE))


def render(out, name, first, second):
    raw = pcm(first) + pcm(second)
    assert raw == pcm(first) + pcm(second)
    assert max(abs(v[0]) for v in struct.iter_unpack('<h', raw)) <= 32767
    path = out / (name + '.wav')
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        w.writeframes(raw)
    with wave.open(str(path), 'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, RATE, 2*RATE)
        assert w.readframes(2*RATE) == raw
    return raw, {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'coefficients': [first, second]}


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    checks = candidates = 0
    for mask in range(16):
        es = efficiencies(mask)
        for target in (0, 6, 12, 24):
            oracle, n = exhaustive(es, target, 25)
            candidates += n
            for cap, expected in enumerate(oracle):
                assert optimum(es, target, cap) == expected
                checks += 1
    for args in [(AGED, -1, 25), (AGED, 12, -1), ((0,), 12, 25)]:
        try:
            optimum(*args)
        except ValueError:
            pass
        else:
            raise AssertionError('bad input admitted')
    # At most r replacements, budget cap. Avoid replacing already-fresh parts in ties.
    table = []
    for r in range(4):
        row = []
        for cap in (12, 16, 20, 25):
            err, used, mask, us = min((*optimum(efficiencies(m), TARGET, cap)[:2], m,
                optimum(efficiencies(m), TARGET, cap)[2]) for m in range(16) if m.bit_count() <= r)
            row.append({'cap': cap, 'error': err, 'drive': used, 'mask': mask, 'settings': us})
        table.append(row)
    policies = {'reference': (4, 4, 4, 4), 'retained': AGED, 'one-replacement': efficiencies(1)}
    scores = {}
    signals = {}
    for name, es in policies.items():
        states = [optimum(es, t, 25) for t in (12, 24)]
        coeffs = [tuple(e*u for e, u in zip(es, s[2])) for s in states]
        signals[name], rec = render(out, name, *coeffs)
        scores[name] = {**rec, 'efficiencies': es, 'states': states}
    signals['unadjusted'], scores['unadjusted'] = render(out, 'unadjusted',
        tuple(e*3 for e in AGED), tuple(e*6 for e in AGED))
    assert len(set(signals.values())) == 4
    assert signals['reference'][:2*RATE] == signals['retained'][:2*RATE] == signals['one-replacement'][:2*RATE]
    assert scores['reference']['states'][1][0] == 0
    assert scores['retained']['states'][1][0] > 0
    assert scores['one-replacement']['states'][1][0] > 0
    receipt = {'python': sys.version.split()[0], 'candidate_vectors': candidates, 'dp_comparisons': checks,
        'invalid_controls': 3, 'table': table, 'recordings': scores, 'common_prefix_frames': RATE}
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1] if len(sys.argv) > 1 else 'audio'))
