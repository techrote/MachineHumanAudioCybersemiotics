"""Synthetic auditions; no perceptual, occupational or safety measurement."""
import hashlib
import json
import math
from pathlib import Path
import struct
import wave

RATE = 16000
FRAMES = 6 * RATE


def stems():
    a, b = [], []
    for i in range(FRAMES):
        t = i / RATE
        edge = min(1, i / 320, (FRAMES - 1 - i) / 320)
        # Continuous invented mechanical bed; no field recording.
        motor = (0.55 + 0.20 * math.sin(2 * math.pi * 0.7 * t)) * (
            math.sin(2 * math.pi * 97 * t) + 0.35 * math.sin(2 * math.pi * 194 * t)
            + 0.18 * math.sin(2 * math.pi * 291 * t))
        # Independent invented resonant gestures; not real alarms.
        u = t % 0.75
        bell = min(1, u / 0.012) * math.exp(-7 * u) * (
            math.sin(2 * math.pi * 430 * t) + 0.45 * math.sin(2 * math.pi * 713 * t))
        a.append(8 * round(900 * edge * motor))
        b.append(8 * round(900 * edge * bell))
    return a, b


def sse(x, y):
    return sum((u - v) ** 2 for u, v in zip(x, y, strict=True))


def mix(a, b, p, q):
    return [(p * x + q * y) // 8 for x, y in zip(a, b, strict=True)]


def render(path, samples):
    assert len(samples) == FRAMES and max(map(abs, samples)) < 32768
    pcm = struct.pack(f'<{len(samples)}h', *samples)
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, RATE, FRAMES, 'NONE', 'not compressed'))
        w.writeframes(pcm)
    with wave.open(str(path), 'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, RATE, FRAMES)
        assert w.readframes(FRAMES) == pcm
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    a, b = stems()
    d = sse(a, b)
    assert d > 0 and all(v % 8 == 0 for v in a + b)
    mid = mix(a, b, 4, 4)
    assert 4 * sse(mid, a) == 4 * sse(mid, b) == d
    rows = []
    for p in range(9):
        for q in range(9):
            y = mix(a, b, p, q)
            ea, eb = sse(y, a), sse(y, b)
            assert 2 * (ea + eb) == 4 * sse(y, mid) + d
            assert 4 * max(ea, eb) >= d
            if p + q == 8:
                assert 64 * ea == q*q*d and 64 * eb == p*p*d
            rows.append((max(ea, eb), p, q))
    assert min(rows) == (d // 4, 4, 4)
    assert sum(r[0] == d // 4 for r in rows) == 1
    out = Path(__file__).resolve().parent / 'audio'
    out.mkdir(exist_ok=True)
    scores = {'motor': (8, 0), 'bell': (0, 8), 'motor-priority': (6, 2),
              'shared-midpoint': (4, 4), 'bell-priority': (2, 6), 'full-mixture': (8, 8)}
    hashes = {name: render(out / (name + '.wav'), mix(a, b, *gains))
              for name, gains in scores.items()}
    assert len(set(hashes.values())) == len(scores)
    receipt = {'kind': 'synthetic_artistic_mixer', 'frames_per_file': FRAMES,
               'sample_rate': RATE, 'gain_grid_cases': len(rows),
               'target_distance_squared': d, 'minimax_error_squared': d // 4,
               'unique_grid_minimizer': [4, 4], 'gains_in_eighths': scores,
               'wav_sha256': hashes, 'human_listening_test': False}
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
