"""Original synthetic constitutional-score audio, standard library only."""
import hashlib
import math
import struct
import wave
from pathlib import Path

RATE = 16000
SLOT = RATE // 2
FREQ = (196, 247, 294, 370)
A = (1, 0, 2, 3)
B = (1, 0, 3, 2)
C = (1, 2, 3, 0)


def orbit(table, start, length=8):
    notes = []
    for _ in range(length):
        notes.append((start,))
        start = table[start]
    return notes


def render(slots):
    samples = []
    for pitches in slots:
        for i in range(SLOT):
            envelope = max(0, min(1, i / 160, (SLOT - 1 - i) / 480))
            value = sum(math.sin(math.tau * FREQ[p] * i / RATE) for p in pitches)
            samples.append(round(5500 * envelope * value / max(1, len(pitches))))
    assert all(abs(v) <= 5500 for v in samples)
    return struct.pack('<' + 'h' * len(samples), *samples)


def main():
    root = Path(__file__).resolve().parent / 'audio'
    root.mkdir(exist_ok=True)
    scores = {
        'prospective-cycle': orbit(C, 0),
        'law-a-start-0': orbit(A, 0),
        'law-b-start-0': orbit(B, 0),
        'law-a-start-2': orbit(A, 2),
        'law-b-start-2': orbit(B, 2),
        'audition-a': [tuple(i for i, v in enumerate(A) if i == v)] * 8,
        'audition-b-empty': [tuple(i for i, v in enumerate(B) if i == v)] * 8,
    }
    payloads = {}
    for name, slots in scores.items():
        pcm = render(slots)
        assert pcm == render(slots)
        path = root / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, RATE, 8 * SLOT)
            assert w.readframes(8 * SLOT) == pcm
        payloads[name] = path.read_bytes()
        print(name, hashlib.sha256(payloads[name]).hexdigest())
    assert payloads['law-a-start-0'] == payloads['law-b-start-0']
    assert payloads['law-a-start-2'] != payloads['law-b-start-2']
    assert render(scores['audition-b-empty']) == bytes(8 * SLOT * 2)
    print('PASS: seven WAVs, exact same-start equality, intervention difference, empty audition')


if __name__ == '__main__':
    main()
