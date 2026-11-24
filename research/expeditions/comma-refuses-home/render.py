"""Original synthetic score; no perceptual claims. Python 3 standard library."""
from fractions import Fraction as F
from pathlib import Path
import math, struct, wave, hashlib

BASE = 264
RATE = 16000
FRAMES = 2400
Q = F(81, 80)
FORWARD = (F(3, 2), F(3, 4), F(3, 2), F(3, 4), F(4, 5))
REVERSE = tuple(1 / x for x in reversed(FORWARD))
SIGNS = (-1, -1, -1, 1, 1, 1, 1)


def score(resets):
    x = 0
    pitches = []
    ends = []
    for i, d in enumerate(SIGNS):
        if i in resets:
            x = 0
        f = BASE * Q ** x
        pitches.append(f)
        for ratio in FORWARD if d == 1 else REVERSE:
            f *= ratio
            pitches.append(f)
        x += d
        assert f == BASE * Q ** x
        ends.append(x)
    return pitches, ends


def render(path, pitches):
    with wave.open(str(path), 'wb') as w:
        w.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
        pcm = bytearray()
        for f in pitches:
            for i in range(FRAMES):
                env = min(1, i / 160, (FRAMES - 1 - i) / 160)
                a = round(6500 * env * math.sin(2 * math.pi * float(f) * i / RATE))
                b = round(6500 * env * math.sin(2 * math.pi * BASE * i / RATE))
                pcm.extend(struct.pack('<hh', a, b))
        w.writeframes(pcm)
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == '__main__':
    out = Path(__file__).resolve().parent
    assert math.prod(FORWARD) == Q
    assert math.prod(REVERSE) == 1 / Q
    for name, resets in [('unbounded', ()), ('reactive', (2, 6)), ('anticipatory', (1,))]:
        p, ends = score(resets)
        assert len(p) == 42
        if name != 'unbounded':
            assert max(map(abs, ends)) <= 2
        path = out / (name + '.wav')
        digest = render(path, p)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2, 2, RATE, 42 * FRAMES)
        print(name, ends, digest)
