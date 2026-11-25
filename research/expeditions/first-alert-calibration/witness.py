"""Synthetic first-alert calibration witness; standard library only."""
from fractions import Fraction as F
from pathlib import Path
from itertools import product
import hashlib, json, math, struct, wave

ROOT = Path(__file__).resolve().parent

def population(rotating):
    return [(y, tuple(int(j < 3) if y else int(j == (t if rotating else 0))
                      for t in range(4))) for y in (1, 0) for j in range(4)]

def inspect(pop):
    snap = []
    first = []
    posterior = []
    for t in range(4):
        high = [y for y, p in pop if p[t]]
        low = [y for y, p in pop if not p[t]]
        assert F(sum(high), len(high)) == F(3, 4)
        assert F(sum(low), len(low)) == F(1, 4)
        snap.append([len(high), sum(high)])
        alerts = [y for y, p in pop if p[t] and not any(p[:t])]
        first.append([len(alerts), sum(alerts)])
        for prefix in sorted({p[:t+1] for _, p in pop}):
            ys = [y for y, p in pop if p[:t+1] == prefix]
            posterior.append([list(prefix), str(F(sum(ys), len(ys)))])
    count, true = map(sum, zip(*first))
    return dict(snapshot=snap, first=first, precision=str(F(true, count)),
                history_posteriors=posterior)

def render(pop, first_only, name):
    # Eight worlds in fixed order, four equal slots per world, then a pause.
    # 500 Hz high, 250 Hz low; a first-only non-alert is silent.
    rate, size = 8000, 1200
    samples = []
    for _, p in pop:
        for t, bit in enumerate(p):
            active = not first_only or (bit and not any(p[:t]))
            freq = 500 if bit else 250
            for j in range(size):
                taper = math.sin(math.pi*j/(size-1))**2
                samples.append(round(3500*taper*math.sin(2*math.pi*freq*j/rate)) if active else 0)
        samples.extend([0]*size)
    path = ROOT / name
    with wave.open(str(path), 'wb') as f:
        f.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        f.writeframes(struct.pack('<'+'h'*len(samples), *samples))
    return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(), samples=len(samples), energy=sum(v*v for v in samples))

def main():
    a, b = population(False), population(True)
    ia, ib = inspect(a), inspect(b)
    assert ia['snapshot'] == ib['snapshot']
    assert ia['precision'] == '3/4' and ib['precision'] == '3/7'
    assert ib['first'] == [[4, 3], [1, 0], [1, 0], [1, 0]]
    # Independent enumeration of 4 labelled worlds, 3 ticks: group by marginals.
    groups = {}
    for rows in product(product((0, 1), repeat=3), repeat=4):
        marg = tuple(map(sum, zip(*rows)))
        groups.setdefault(marg, set()).add(sum(any(row) for row in rows))
    assert all(us == set(range(max(m), min(4, sum(m))+1)) for m, us in groups.items())
    audio = {}
    for name, pop in [('nested', a), ('rotating', b)]:
        for first in (False, True):
            key = name + ('-first.wav' if first else '-raw.wav')
            audio[key] = render(pop, first, key)
    assert audio['nested-raw.wav']['energy'] == audio['rotating-raw.wav']['energy']
    receipt = dict(status='PASS', schedules=8**4, profiles=len(groups), nested=ia, rotating=ib, audio=audio)
    (ROOT/'witness.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','schedules','profiles','audio')}, indent=2))

if __name__ == '__main__':
    main()
