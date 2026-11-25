"""Original periodic-motif study; no human or device data. Python 3.11+ stdlib."""
import argparse
import hashlib
import itertools
import math
from pathlib import Path
import struct
import wave

FS = 32768
RATES = (1, 2, 4, 8, 16, 32, 64, 128)
STAGE = 2 * FS
FIXED = FS // 64
FADE = FS // 100


def centered_sums(x, w):
    """Return exact numerators P*sum(window)-w*sum(cycle)."""
    p = len(x)
    assert p and w > 0
    total = sum(x)
    q, r = divmod(w, p)
    s = q * total + sum(x[-j % p] for j in range(r))
    out = []
    for i in range(p):
        out.append(p * s - w * total)
        s += x[(i + 1) % p] - x[(i + 1 - w) % p]
    return out


def motif(p):
    assert p % 64 == 0
    x = [0] * p
    for start, amp in ((0, 4), (p // 4, 2), (5 * p // 8, 1)):
        x[start:start + p // 32] = [amp] * (p // 32)
    return x


def check():
    cases = 0
    for p in range(1, 7):
        for x in itertools.product(range(3), repeat=p):
            d = next(k for k in range(1, p + 1)
                     if all(x[i] == x[(i - k) % p] for i in range(p)))
            for w in range(1, 2 * p + 1):
                actual = centered_sums(x, w)
                direct = [p * sum(x[(i - j) % p] for j in range(w))
                          - w * sum(x) for i in range(p)]
                assert actual == direct
                assert sum(actual) == 0
                assert (not any(actual)) == (w % d == 0)
                cases += 1
    return cases


def stage(rate, relative):
    p = FS // rate
    w = p // 64 if relative else FIXED
    v = centered_sums(motif(p), w)
    # Absolute common gain; deliberately no per-stage normalization.
    scale = 0.18 * 32767 / (4 * p * w)
    samples = [round(v[i % p] * scale * min(1, i / FADE,
               (STAGE - 1 - i) / FADE)) for i in range(STAGE)]
    assert max(map(abs, samples)) <= 5899
    return samples


def encode(samples, channels):
    return struct.pack('<' + 'h' * len(samples), *samples)


def write_wav(path, samples, channels):
    payload = encode(samples, channels)
    with wave.open(str(path), 'wb') as f:
        f.setparams((channels, 2, FS, 0, 'NONE', 'not compressed'))
        f.writeframes(payload)
    with wave.open(str(path), 'rb') as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == (channels, 2, FS)
        assert f.getnframes() == len(samples) // channels
        assert f.readframes(f.getnframes()) == payload
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(out):
    out.mkdir(parents=True, exist_ok=True)
    relative, fixed = [], []
    print('rate_hz,phase_rms_pcm,fixed_rms_pcm')
    for rate in RATES:
        a, b = stage(rate, True), stage(rate, False)
        assert a == stage(rate, True) and b == stage(rate, False)
        assert any(a)
        assert (not any(b)) == (rate >= 64)
        if rate == 1:
            assert a == b
        rms = lambda x: math.sqrt(sum(y*y for y in x) / len(x))
        print(f'{rate},{rms(a):.3f},{rms(b):.3f}')
        relative.extend(a)
        fixed.extend(b)
    stereo = [v for pair in zip(relative, fixed) for v in pair]
    for name, data, channels in [('phase-relative.wav', relative, 1),
                                 ('absolute-time.wav', fixed, 1),
                                 ('parallel-microscopes.wav', stereo, 2)]:
        print(name, write_wav(out / name, data, channels))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('aperture-audio'))
    args = parser.parse_args()
    print('Exact window cases passed:', check())
    render(args.out)
