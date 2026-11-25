"""Direct legal-firing oracle and original matched-count stereo sonification."""
import argparse
import hashlib
import json
import struct
import wave
from pathlib import Path
from math import gcd
from avalanche import receipt, count, candidates, collision_pairs, plan


def simulate(n, i, h, reverse=False):
    x = [1] * n
    if h:
        x[h-1] = 0
    return fire(x, i, reverse)


def fire(x, i, reverse=False):
    x = x.copy()
    n = len(x)
    x[i-1] += 1
    u = [0] * n
    events = []
    order = range(n-1, -1, -1) if reverse else range(n)
    while True:
        j = next((k for k in order if x[k] >= 2), None)
        if j is None:
            break
        x[j] -= 2
        u[j] += 1
        events.append(j+1)
        if j:
            x[j-1] += 1
        if j+1 < n:
            x[j+1] += 1
    holes = [j+1 for j, v in enumerate(x) if v == 0]
    return {'next': holes[0] if len(holes) == 1 else 0 if not holes else None, 'odometer': u,
            'count': len(events), 'left': u[0], 'right': u[-1]}, events


def census():
    states = schedules = probes = collisions = centred = 0
    for n in range(1, 29):
        for i in range(1, n+1):
            groups = {}
            for h in range(n+1):
                exact = receipt(n, i, h)
                for reverse in (False, True):
                    actual, _ = simulate(n, i, h, reverse)
                    assert actual == exact
                    schedules += 1
                assert count(n, i, h) == exact['count']
                groups.setdefault(exact['count'], []).append(h)
                # One side bit, not both, suffices.
                for side in ('left', 'right'):
                    assert candidates(n, i, exact['count'], **{side: exact[side]}) == [h]
                states += 1
            pairs = sorted(tuple(v) for v in groups.values() if len(v) > 1)
            assert all(len(v) <= 2 for v in groups.values())
            assert pairs == sorted(collision_pairs(n, i))
            assert len(pairs) == gcd(n+1, i)-1
            for total, hs in groups.items():
                assert candidates(n, i, total) == hs
                p = plan(n, i, total)
                if len(hs) == 2:
                    nexts = [(h-i) % (n+1) for h in hs]
                    j = p['next_site']
                    observations = [simulate(n, j, h)[0]['count'] for h in nexts]
                    assert observations[0] != observations[1]
                    collisions += 1
                    if 2*i == n+1:
                        # Centre reflection survives any number of repeated centre injections.
                        a, b = nexts
                        assert a+b == n+1 and count(n, i, a) == count(n, i, b)
                        centred += 1
                    for h, obs in zip(hs, observations):
                        assert candidates(n, i, total, second=obs, second_site=j) == [h]
                else:
                    assert p['next_site'] is None
                probes += 1
    assert candidates(11, 4, 999) == []
    # Outside-model witness: both receipts identical, different final states.
    a, _ = fire([0, 0, 1], 1)
    b, _ = fire([0, 1, 1], 1)
    assert a['count'] == b['count'] == a['left'] == b['left'] == a['right'] == b['right'] == 0
    assert a['next'] == 2 and b['next'] == 0
    for args in ((0, 1, 0), (3, 0, 0), (3, 1, 4), (3, 1, True), (3, 1, None)):
        try:
            receipt(*args)
        except ValueError:
            pass
        else:
            raise AssertionError(args)
    return dict(states=states, legal_schedules=schedules, count_classes=probes,
                collision_pairs=collisions, persistent_centre_pairs=centred)


def render(path, cases):
    sequences = [simulate(*c)[1] for c in cases]
    assert len(sequences[0]) == len(sequences[1])
    frames = bytearray()
    rate, slot = 16000, 1200
    for a, b in zip(*sequences):
        for t in range(slot):
            env = min(t, slot-1-t, 100)
            def sample(j):
                period = 100-4*j
                triangle = 4*abs(t % period-period//2)-period
                return 7000*triangle*env//(period*100)
            frames.extend(struct.pack('<hh', sample(a), sample(b)))
    with wave.open(str(path), 'wb') as f:
        f.setparams((2, 2, rate, 0, 'NONE', 'not compressed'))
        f.writeframes(frames)
    peaks = [max(abs(v[j]) for v in struct.iter_unpack('<hh', frames)) for j in (0, 1)]
    return dict(cases=cases, events=sequences, seconds=len(frames)/(4*rate),
                peaks=peaks, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, default=Path('build/path-avalanche'))
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    result = census()
    cases = [(11, 4, 2), (11, 4, 8)]
    f = args.out/'same-count.wav'
    result['audio'] = render(f, cases)
    assert result['audio'] == render(f, cases)
    result['example'] = [receipt(*c) for c in cases]
    result['second_counts'] = [count(n, i, (h-i) % (n+1)) for n, i, h in cases]
    (args.out/'results.synthetic.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
