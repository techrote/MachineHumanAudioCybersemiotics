"""Synthetic score translation, not a physical model of hands or guitars."""
from itertools import product
from pathlib import Path
import hashlib
import json
import math
import struct
import sys
import wave

OLD = (0, 3, 6)
NEW = (0, 4, 6)
CELLS = tuple(product(range(3), range(5)))
SCORE = ((0, 4), (1, 3)) * 3
RATE = 16000
FRAMES = 4000


def pitches(tuning, path):
    return tuple(tuning[s] + f for s, f in path)


def distance(a, b):
    return 2 * abs(a[0] - b[0]) + abs(a[1] - b[1])


def motion(path):
    return sum(distance(a, b) for a, b in zip(path, path[1:]))


def choices(pitch, tuning):
    return tuple(a for a in CELLS if tuning[a[0]] + a[1] == pitch)


def frontier(table):
    return {e: v for e, v in sorted(table.items())
            if all(other >= e or w[0] > v[0] for other, w in table.items())}


def translate(original, source=OLD, target=NEW):
    """Minimize motion at each exact edit count, then remove dominated pairs."""
    states = {(None, 0): (0, ())}
    for old, p in zip(original, pitches(source, original)):
        next_states = {}
        for (last, edits), (cost, path) in states.items():
            for a in choices(p, target):
                key = (a, edits + (old != a))
                value = (cost + (distance(last, a) if last is not None else 0), path + (a,))
                if key not in next_states or value < next_states[key]:
                    next_states[key] = value
        states = next_states
    table = {}
    for (_, edits), v in states.items():
        if edits not in table or v < table[edits]:
            table[edits] = v
    return frontier(table)


def brute(original, source=OLD, target=NEW):
    table = {}
    count = 0
    for path in product(*(choices(p, target) for p in pitches(source, original))):
        count += 1
        edits = sum(a != b for a, b in zip(original, path))
        value = (motion(path), path)
        if edits not in table or value < table[edits]:
            table[edits] = value
    return frontier(table), count


def render(tuning, path):
    """Left: pitch-only oscillator. Right: invented coordinate sonification."""
    payload = bytearray()
    for s, f in path:
        hz = 220 * 2 ** ((tuning[s] + f) / 12)
        cue = 500 + 180 * s + 35 * f
        for j in range(FRAMES):
            env = math.sin(math.pi * j / (FRAMES - 1)) ** 2
            left = round(11000 * env * math.sin(2 * math.pi * hz * j / RATE))
            right = round(7000 * env * math.sin(2 * math.pi * cue * j / RATE))
            payload.extend(struct.pack('<hh', left, right))
    return bytes(payload)


def channel(payload, index):
    return tuple(v[index] for v in struct.iter_unpack('<hh', payload))


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    examined = candidates = 0
    for n in range(4):
        for original in product(CELLS, repeat=n):
            expected, count = brute(original)
            assert translate(original) == expected
            examined += 1
            candidates += count
    solutions = translate(SCORE)
    expected, count = brute(SCORE)
    assert solutions == expected
    assert [(e, c) for e, (c, _) in solutions.items()] == [(3, 20), (4, 16), (5, 12), (6, 10)]
    assert translate(((0, 0),), target=(1, 4, 6)) == {}
    assert translate((), target=NEW) == {0: (0, ())}
    assert translate(SCORE, target=OLD)[0] == (motion(SCORE), SCORE)
    scenes = {'original': (OLD, SCORE), 'literal-retune': (NEW, SCORE)}
    scenes.update({f'edit-{e}': (NEW, path) for e, (_, path) in solutions.items()})
    results = {}
    buffers = {}
    for name, (tuning, path) in scenes.items():
        pcm = render(tuning, path)
        assert pcm == render(tuning, path)
        assert max(map(abs, channel(pcm, 0))) <= 11000
        assert max(map(abs, channel(pcm, 1))) <= 7000
        dest = out / (name + '.wav')
        with wave.open(str(dest), 'wb') as w:
            w.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(pcm)
        with wave.open(str(dest), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2, 2, RATE, len(path) * FRAMES)
            assert w.readframes(w.getnframes()) == pcm
        buffers[name] = pcm
        results[name] = {'pitches': pitches(tuning, path), 'actions': path,
                         'motion': motion(path), 'edits': sum(a != b for a, b in zip(SCORE, path)),
                         'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()}
    assert channel(buffers['original'], 0) != channel(buffers['literal-retune'], 0)
    assert channel(buffers['original'], 1) == channel(buffers['literal-retune'], 1)
    for e in solutions:
        assert channel(buffers['original'], 0) == channel(buffers[f'edit-{e}'], 0)
    assert len(set(buffers.values())) == len(scenes)
    receipt = {'python': sys.version.split()[0], 'short_scores': examined,
               'short_candidate_paths': candidates, 'exemplar_candidate_paths': count,
               'frontier': [[e, c] for e, (c, _) in solutions.items()], 'scenes': results,
               'result': 'PASS', 'limits': 'Synthetic grid, no ergonomic or listening validation.'}
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    run(Path(sys.argv[1]) if len(sys.argv) > 1 else Path('audio'))
