"""Original quiet six-note studies; no listener data or perceptual claims."""
import hashlib
import math
import struct
import wave
from pathlib import Path

RATE = 24000
SLOT = RATE // 4
FREQ = (220, 329.6276, 246.9417, 392, 293.6648, 440)
P = (1, 0, 3, 2, 5, 4)
Q = (5, 2, 1, 4, 3, 0)
X = (1, 0, 0, 0, 0, 0)


def mean(x, p):
    return tuple((v + x[p[i]]) / 2 for i, v in enumerate(x))


def pcm(gains):
    out = bytearray()
    for _ in range(8):
        for f, gain in zip(FREQ, gains):
            for j in range(SLOT):
                t = j / RATE
                env = min(1, j / 240, (SLOT - 1 - j) / 480)
                tone = math.sin(2 * math.pi * f * t) + .2 * math.sin(4 * math.pi * f * t)
                out.extend(struct.pack('<h', round(32767 * (.08 + .24 * gain) * env * tone)))
    return bytes(out)


def main():
    a, b = mean(mean(X, P), Q), mean(mean(X, Q), P)
    assert a == (.25, .25, .25, 0, 0, .25)
    assert b == (.25, .25, 0, 0, .25, .25)
    assert sum(a) == sum(b) == sum(X)
    root = Path(__file__).parent / 'audio'
    root.mkdir(exist_ok=True)
    results = []
    for name, g in [('01-original', X), ('02-P-then-Q', a), ('03-Q-then-P', b)]:
        data = pcm(g)
        assert data == pcm(g)
        assert len(data) == 2 * RATE * 12
        assert max(abs(v[0]) for v in struct.iter_unpack('<h', data)) < 13000
        path = root / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(data)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, RATE, RATE * 12)
            assert w.readframes(w.getnframes()) == data
        results.append(data)
        print(hashlib.sha256(path.read_bytes()).hexdigest(), path.name)
    assert results[1] != results[2]
    for i in (0, 1, 3, 5):
        assert results[1][2*i*SLOT:2*(i+1)*SLOT] == results[2][2*i*SLOT:2*(i+1)*SLOT]
    for i in (2, 4):
        assert results[1][2*i*SLOT:2*(i+1)*SLOT] != results[2][2*i*SLOT:2*(i+1)*SLOT]
    print('PCM checks PASS')


if __name__ == '__main__':
    main()
