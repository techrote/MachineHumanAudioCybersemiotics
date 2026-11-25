"""Original synthetic boundary counterpoint; no listener data."""
import hashlib
import json
import math
from pathlib import Path
import struct
import wave

RATE = 16000
PULSE = 4000
CYCLES = 3
N = 8
NOTES = (0, 2, 5, 7, 4, 9, 5, 2)


def carrier():
    result = []
    for i in range(N * CYCLES):
        f = 220 * 2 ** (NOTES[i % N] / 12)
        for j in range(PULSE):
            t = j / RATE
            env = min(1, j / 160, (PULSE - 1 - j) / 240)
            result.append(round(5500 * env * math.sin(2 * math.pi * f * t)))
    return result


def marker(cuts, frequency):
    result = [0] * (N * PULSE * CYCLES)
    for i in range(N * CYCLES):
        if i % N not in cuts:
            continue
        for j in range(1600):
            t = j / RATE
            env = min(1, j / 80, (1599 - j) / 160) * math.exp(-25 * t)
            result[i * PULSE + j] = round(3800 * env * math.sin(2 * math.pi * frequency * t))
    return result


def write(path, values, channels=1):
    assert max(map(abs, values)) < 32768
    raw = struct.pack('<' + 'h' * len(values), *values)
    with wave.open(str(path), 'wb') as f:
        f.setparams((channels, 2, RATE, 0, 'NONE', 'not compressed'))
        f.writeframes(raw)
    with wave.open(str(path), 'rb') as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == (channels, 2, RATE)
        assert f.getnframes() == N * PULSE * CYCLES
        assert f.readframes(f.getnframes()) == raw
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(__file__).parent / 'audio'
    out.mkdir(exist_ok=True)
    base = carrier()
    a = marker({0, 4}, 880)
    hashes = {'carrier.wav': write(out / 'carrier.wav', base)}
    for x in range(4):
        b = marker({x, x + 4}, 1320)
        stereo = [v for c, p, q in zip(base, a, b) for v in (c + p, c + q)]
        assert all(stereo[2 * j] - a[j] == base[j] == stereo[2 * j + 1] - b[j] for j in range(len(base)))
        name = f'offset-{x}.wav'
        hashes[name] = write(out / name, stereo, 2)
        # Re-render identical source arrays and compare byte hashes.
        second = [v for c, p, q in zip(carrier(), marker({0, 4}, 880), marker({x, x + 4}, 1320)) for v in (c + p, c + q)]
        assert second == stereo
        assert write(out / name, second, 2) == hashes[name]
    assert len(set(hashes.values())) == 5
    receipt = {'rate': RATE, 'frames_per_file': len(base), 'files': hashes,
               'status': 'PASS: exact carrier recovery, bounds, headers, payload, repeated rendering; no listening trial'}
    (out.parent / 'audio-receipt.txt').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
