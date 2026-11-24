"""Independent native Python check of the finite relay expedition (synthetic)."""
import hashlib
import itertools
import json
import math
import pathlib
import struct
import sys
import wave


def staircase_census():
    records = []
    for m in range(2, 7):
        permutations = list(itertools.permutations(range(1, m + 1)))
        best = [0] * (m + 1)
        checked = 0
        shapes = 0
        for increasing in itertools.combinations_with_replacement(range(m + 1), m):
            widths = increasing[::-1]
            r = len(set(widths) - {0})
            values = [sum(j <= w for j, w in zip(p, widths)) for p in permutations]
            gap = max(values) - min(values)
            assert gap * (r + 1) <= r * m
            best[r] = max(best[r], gap)
            shapes += 1
            checked += len(permutations)
        for r in range(1, m):
            assert best[r] == m * r // (r + 1)
        records.append(dict(m=m, shapes=shapes, permutations=len(permutations),
                            evaluations=checked, best_gap_numerators=best))
    return records


def witness(m):
    a = [(m + i, m - i) for i in range(1, m)] + [(2*m, m)]
    b = [(m + i, m + 1 - i) for i in range(1, m + 1)]
    return a, b


def replay(relays, trace):
    # Independently model each direction crossing as a separate event.
    on = set()
    counts = []
    last = 0
    for x in trace:
        if x > last:
            on.update(k for k, (hi, lo) in enumerate(relays) if last < hi <= x)
        elif x < last:
            on.difference_update(k for k, (hi, lo) in enumerate(relays) if x < lo <= last)
        counts.append(len(on))
        last = x
    return counts


def pcm(path, counts, total):
    samples = []
    for value in counts:
        for k in range(640):
            tri = 16 - 2 * abs(k % 32 - 16)
            env = min(k, 639 - k, 32)
            # Integer equivalent of JS Math.round, including negative ties.
            numerator = 12000 * value * tri * env
            denom = total * 16 * 32
            samples.append((2 * numerator + denom) // (2 * denom))
    with wave.open(str(path), 'wb') as f:
        f.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
        f.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
    data = path.read_bytes()
    fnv = 2166136261
    for byte in data:
        fnv = ((fnv ^ byte) * 16777619) & 0xffffffff
    return dict(bytes=len(data), fnv1a32=f'{fnv:08x}', sha256=hashlib.sha256(data).hexdigest())


def main(destination):
    destination.mkdir(parents=True, exist_ok=True)
    m = 8
    a, b = witness(m)
    major = list(range(2*m + 1)) + list(range(2*m - 1, -1, -1))
    nested = [0] + [x for i in range(1, m) for x in (2*m-i, i)]
    recordings = {}
    for name, trace in [('major', major), ('nested', nested)]:
        for label, model in [('a', a), ('b', b)]:
            path = destination / f'{name}-{label}.wav'
            recordings[path.name] = pcm(path, replay(model, trace), m)
    assert (destination/'major-a.wav').read_bytes() == (destination/'major-b.wav').read_bytes()
    assert (destination/'nested-a.wav').read_bytes() != (destination/'nested-b.wav').read_bytes()
    assert replay(a, nested)[-1] == 7 and replay(b, nested)[-1] == 0
    expected = ['4478b173', '4478b173', '7ec5470b', '33646de5']
    assert [x['fnv1a32'] for x in recordings.values()] == expected
    return dict(model='synthetic, same-agent independent implementation',
                python=sys.version.split()[0], census=staircase_census(), recordings=recordings,
                assertions='pass')


if __name__ == '__main__':
    print(json.dumps(main(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'results')), indent=2))
