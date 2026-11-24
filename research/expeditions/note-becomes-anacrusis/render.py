"""Original synthetic accent studies. Python 3, standard library only."""
import hashlib
import math
import struct
import wave
from pathlib import Path

RATE, SLOT, COUNT = 24000, 6000, 24

def render(period, phase, count=COUNT):
    out = bytearray()
    for t in range(count):
        accent = t % period == phase
        for j in range(SLOT):
            s = j / RATE
            env = min(1, j / 120, (SLOT - 1 - j) / 120) * math.exp(-s * 21)
            base = .14 * math.sin(2 * math.pi * 440 * s)
            marker = .16 * math.sin(2 * math.pi * 220 * s) if accent else 0
            out.extend(struct.pack('<h', round(32767 * env * (base + marker))))
    return bytes(out)

def main():
    folder = Path(__file__).resolve().parent / 'audio'
    folder.mkdir(exist_ok=True)
    a, b = render(4, 3), render(5, 3)
    prefix = 7 * SLOT * 2
    assert a[:prefix] == b[:prefix]
    assert a[prefix:prefix+SLOT*2] != b[prefix:prefix+SLOT*2]
    cases = {'01-undecided': render(4, 3, 7), '02-four': a, '03-five': b}
    receipts = []
    for name, pcm in cases.items():
        p = folder / (name + '.wav')
        with wave.open(str(p), 'wb') as w:
            w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(pcm)
        with wave.open(str(p), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, RATE)
            assert w.readframes(w.getnframes()) == pcm
        assert max(abs(x[0]) for x in struct.iter_unpack('<h', pcm)) < 10000
        receipts.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  audio/{p.name}')
    assert a == render(4, 3) and b == render(5, 3)
    (folder.parent / 'SHA256SUMS.txt').write_text('\n'.join(receipts)+'\n', encoding='utf-8')
    print('PASS: shared 42000-sample prefix, slot 8 divergence, 3 WAV payloads, bounds, repeated render')

if __name__ == '__main__':
    main()
