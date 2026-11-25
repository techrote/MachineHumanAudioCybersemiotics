"""Synthetic winner-only layer compositor; no external data or dependencies."""
from itertools import permutations, combinations
from collections import Counter
from pathlib import Path
import hashlib, json, math, struct, wave


def winner(order, mask):
    return next((x for x in order if mask & (1 << x)), -1)


def signature(order, masks):
    return tuple(winner(order, m) for m in masks)


def certified(order, masks):
    # Each consecutive pair must be exposed with the earlier layer winning.
    return all(any(winner(order, m) == a and m & (1 << b)
                   for m in masks) for a, b in zip(order, order[1:]))


def peel(order):
    m = (1 << len(order)) - 1
    out = []
    while m.bit_count() > 1:
        w = winner(order, m)
        out.append(w)
        m ^= 1 << w
    return tuple(out + [winner(order, m)])


def qualify():
    results = []
    for n in range(2, 5):
        orders = list(permutations(range(n)))
        masks = [m for m in range(1, 1 << n) if m.bit_count() >= 2]
        pairs = {m for m in masks if m.bit_count() == 2}
        families = universal = local = 0
        fibres = Counter()
        for f in range(1 << len(masks)):
            probes = [m for i, m in enumerate(masks) if f & (1 << i)]
            sigs = [signature(o, probes) for o in orders]
            counts = Counter(sigs)
            unique = len(counts) == len(orders)
            assert unique == pairs.issubset(probes)
            universal += unique
            families += 1
            for o, s in zip(orders, sigs):
                assert (counts[s] == 1) == certified(o, probes)
                if counts[s] == 1:
                    assert len(probes) >= n - 1
                    local += 1
                fibres[counts[s]] += 1
        for o in orders:
            assert peel(o) == o
        results.append(dict(n=n, families=families, orders=len(orders),
                            instances=families*len(orders), universal=universal,
                            unique_instances=local, fibre_histogram=dict(sorted(fibres.items()))))
    a, b = (0, 1, 2, 3), (0, 1, 3, 2)
    masks = (15, 14, 7, 11, 3, 14)
    assert signature(a, masks) == signature(b, masks)
    assert signature(a, (12,)) != signature(b, (12,))
    assert winner(a, 0) == -1
    assert not certified(a, masks)
    return results


RATE = 24000
SLOT = RATE // 2
FREQ = (196, 293.66, 440, 587.33)


def render(ids):
    samples = []
    for k, v in enumerate(ids):
        for i in range(SLOT):
            t = i / RATE
            env = math.sin(math.pi * i / (SLOT - 1)) ** 2
            if v < 0:
                value = 0
            else:
                f = FREQ[v]
                value = env * (0.22 * math.sin(2*math.pi*f*t) +
                               0.07 * math.sin(2*math.pi*f*(v+2)*t))
            samples.append(round(32767 * value))
    assert max(map(abs, samples), default=0) <= 32767
    return struct.pack('<' + 'h'*len(samples), *samples)


def main():
    results = qualify()
    out = Path(__file__).parent / 'audio'
    out.mkdir(exist_ok=True)
    a, b = (0, 1, 2, 3), (0, 1, 3, 2)
    masks = (15, 14, 7, 11, 3, 14)
    scenes = {'surface-a': signature(a, masks), 'surface-b': signature(b, masks),
              'peel-a': peel(a), 'peel-b': peel(b),
              'bottom-a': signature(a, (12,)), 'bottom-b': signature(b, (12,))}
    receipts = {}
    for name, ids in scenes.items():
        raw = render(ids)
        assert raw == render(ids)
        path = out / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(raw)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, RATE)
            assert w.getnframes() == SLOT*len(ids) and w.readframes(w.getnframes()) == raw
        receipts[name] = dict(ids=ids, frames=SLOT*len(ids), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    assert receipts['surface-a']['sha256'] == receipts['surface-b']['sha256']
    assert receipts['peel-a']['sha256'] != receipts['peel-b']['sha256']
    assert receipts['bottom-a']['sha256'] != receipts['bottom-b']['sha256']
    print(json.dumps(dict(result='PASS', exhaustive=results, audio=receipts), indent=2))


if __name__ == '__main__':
    main()
